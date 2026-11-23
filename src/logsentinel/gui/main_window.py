"""Main application shell for the LogSentinel desktop GUI.

The window owns navigation, input/configuration panels, analysis and export
worker lifecycles, dashboard/detection views, the reports workspace, and the
Settings centre. Detection and report rendering stay in the existing backend
modules; this module only coordinates them.

PySide6 is optional and is imported only inside the GUI package. The CLI
never imports this module.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from PySide6.QtCore import QByteArray, QSize, Qt, QThread
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..exceptions import ConfigError
from ..report import _sanitize
from .app_settings import AppSettings, SettingsError, SettingsStore
from .backend import AnalysisRequest, AnalysisResult
from .icon_widgets import BrandMarkLabel
from .icons import icon
from .panels import ConfigPanel, InputPanel
from .reports_view import ExportWorker, ReportsView
from .settings_view import SettingsView
from .views import DetectionsView, LogExplorerView, OverviewDashboard
from .worker import AnalysisWorker
from .theme import (
    APP_NAME,
    APP_TAGLINE,
    APP_WINDOW_TITLE,
    apply_theme,
    create_app_icon,
    current_theme,
    theme_label,
    theme_manager,
)


@dataclass(frozen=True, slots=True)
class _PageSpec:
    key: str
    label: str
    icon: str
    title: str
    subtitle: str


_PAGE_SPECS: tuple[_PageSpec, ...] = (
    _PageSpec(
        "overview",
        "Overview",
        "overview",
        "Overview",
        "Security posture at a glance",
    ),
    _PageSpec(
        "detections",
        "Detections",
        "detections",
        "Detections",
        "Review leads grouped by rule, severity, and source",
    ),
    _PageSpec(
        "log_explorer",
        "Log Explorer",
        "log_explorer",
        "Log Explorer",
        "Review streamed event counts and run context",
    ),
    _PageSpec(
        "reports",
        "Reports",
        "reports",
        "Reports",
        "Export analyst-ready JSON and HTML reports",
    ),
    _PageSpec(
        "settings",
        "Settings",
        "settings",
        "Settings",
        "Application defaults, thresholds, and preferences",
    ),
)


class MainWindow(QMainWindow):
    """The LogSentinel desktop shell.

    The window coordinates navigation, input/configuration panels, the
    analysis and export worker lifecycles, result views, and persisted
    application settings.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        settings_store: SettingsStore | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("MainWindow")
        self.setWindowTitle(APP_WINDOW_TITLE)
        self.setWindowIcon(create_app_icon())
        self.setMinimumSize(1080, 680)
        self.resize(1440, 900)

        self._specs_by_key = {spec.key: spec for spec in _PAGE_SPECS}
        self._page_indices = {
            spec.key: index for index, spec in enumerate(_PAGE_SPECS)
        }
        self._nav_buttons: dict[str, QPushButton] = {}
        self._shortcuts: list[QShortcut] = []
        self._current_page_key = ""
        self._stack: QStackedWidget | None = None
        self._page_title: QLabel | None = None
        self._page_subtitle: QLabel | None = None

        self._analysis_thread: QThread | None = None
        self._analysis_worker: AnalysisWorker | None = None
        self._export_thread: QThread | None = None
        self._export_worker: ExportWorker | None = None
        self._export_kind: str | None = None
        self._export_path: str | None = None
        self._last_result: AnalysisResult | None = None
        self._close_pending = False

        # MainWindow() uses an in-memory store so tests and embedders do not
        # write into the user's profile. The production entry point injects
        # the platform settings path.
        self._settings_store = settings_store or SettingsStore(path=None)
        loaded_settings = self._settings_store.load()
        self._settings = loaded_settings.settings
        self._settings_warning = loaded_settings.warning
        application = QApplication.instance()
        if isinstance(application, QApplication):
            apply_theme(application, self._settings.theme)
        self.setWindowIcon(create_app_icon(self._settings.theme))

        self.input_panel = InputPanel()
        self.config_panel = ConfigPanel(
            analysis_defaults=self._settings.analysis_defaults)
        self.dashboard = OverviewDashboard()
        self.detections_view = DetectionsView()
        self.log_explorer_view = LogExplorerView()
        self.reports_view = ReportsView(
            preferred_format=self._settings.default_export_format)
        self.reports_view.export_requested.connect(self._on_export_requested)
        self.settings_view = SettingsView()
        self.settings_view.save_requested.connect(self._save_settings)
        self.settings_view.reset_requested.connect(self._reset_settings)
        self.settings_view.theme_selected.connect(self._on_theme_selected)
        self.input_panel.inputs_changed.connect(self._on_inputs_changed)
        self.config_panel.configuration_changed.connect(
            self._on_configuration_changed)

        self._build_ui()
        theme_manager.changed.connect(self._refresh_theme_visuals)
        self._refresh_icons()
        self.settings_view.set_settings(
            self._settings, warning=self._settings_warning)
        self.input_panel.set_max_file_mb(
            self.config_panel.effective_config().max_file_mb)
        self._restore_window_state()
        self._refresh_analysis_controls()
        self.navigate_to(self._startup_page_key())
        if self._settings_warning:
            self.statusBar().showMessage(self._settings_warning)

        application = QApplication.instance()
        if isinstance(application, QApplication):
            application.aboutToQuit.connect(self._shutdown_analysis)
            application.aboutToQuit.connect(self._shutdown_export)
            application.aboutToQuit.connect(self._persist_window_state)

    # -- public shell API -------------------------------------------------

    @property
    def navigation_keys(self) -> tuple[str, ...]:
        """Ordered page keys exposed by the sidebar."""
        return tuple(self._nav_buttons)

    @property
    def current_page_key(self) -> str:
        """Key of the currently selected page."""
        return self._current_page_key

    @property
    def workspace_stack(self) -> QStackedWidget:
        """The central page stack, exposed for navigation and tests."""
        assert self._stack is not None
        return self._stack

    @property
    def is_analysis_running(self) -> bool:
        """True while an analysis thread is active or finishing."""
        return self._analysis_thread is not None

    @property
    def last_result(self) -> AnalysisResult | None:
        """Most recent successful result, retained for the results dashboard."""
        return self._last_result

    @property
    def app_settings(self) -> AppSettings:
        """Current persistent application settings snapshot."""
        return self._settings

    @property
    def settings_store(self) -> SettingsStore:
        return self._settings_store

    def start_analysis(self) -> bool:
        """Start one background analysis; return False if it cannot start."""
        if self._analysis_thread is not None:
            self.statusBar().showMessage(
                "Analysis already running — cancel or wait for it to finish")
            return False
        if self._export_thread is not None:
            self.statusBar().showMessage(
                "Report export in progress — wait for it to finish")
            return False

        paths = self.input_panel.selected_paths
        if not paths:
            self._set_run_message(
                "No input sources",
                "Add log files or a folder before starting an analysis.")
            return False

        try:
            config = self.config_panel.effective_config()
        except ConfigError as exc:
            self._set_run_message(
                "Configuration error", _sanitize(str(exc)))
            return False

        request = AnalysisRequest.from_paths(paths, config)
        worker = AnalysisWorker(request)
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.started.connect(self._on_analysis_started)
        worker.progress.connect(self._on_analysis_progress)
        worker.completed.connect(self._on_analysis_completed)
        worker.cancelled.connect(self._on_analysis_cancelled)
        worker.failed.connect(self._on_analysis_failed)
        worker.finished.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_analysis_thread_finished)

        self._analysis_worker = worker
        self._analysis_thread = thread
        self._last_result = None
        self.dashboard.clear(
            "Analysis running",
            "KPI cards, severity breakdown, statistics, and errors will "
            "appear when the run completes.")
        self.detections_view.clear(
            "Analysis running",
            "Detection results will appear when the run completes.")
        self.log_explorer_view.clear(
            "Analysis running",
            "Event statistics will appear when the run completes.")
        self.reports_view.clear(
            "Analysis running",
            "Report exports will be enabled when the run completes.")
        self._set_running_ui(True)
        self._run_progress.setRange(0, 0)
        self._run_progress.setValue(0)
        self._run_status.setText("Starting analysis…")
        self._run_detail.setText(
            f"{len(paths)} input source{'' if len(paths) == 1 else 's'}"
        )
        self.statusBar().showMessage("Analysis starting…")
        thread.start()
        return True

    def cancel_analysis(self) -> bool:
        """Request cooperative cancellation of the active run."""
        if self._analysis_worker is None:
            return False
        self._analysis_worker.cancel()
        self.cancel_button.setEnabled(False)
        self._refresh_action_icons()
        self._set_run_message(
            "Cancelling analysis…",
            "Waiting for the current file and staging cleanup to finish.")
        return True

    def closeEvent(self, event: QCloseEvent) -> None:
        """Defer closing until a running worker has stopped."""
        if (self._export_thread is not None
                and self._export_thread.isRunning()):
            self._close_pending = True
            self.statusBar().showMessage(
                "Closing after the report export finishes…")
            event.ignore()
            return
        if (self._analysis_thread is not None
                and self._analysis_thread.isRunning()):
            self._close_pending = True
            self.cancel_analysis()
            self._set_run_message(
                "Closing after cancellation…",
                "The analysis worker is cleaning up before exit.")
            event.ignore()
            return
        self._persist_window_state()
        event.accept()

    def navigate_to(self, key: str) -> None:
        """Select a page by key and synchronise navigation and header state."""
        if key not in self._page_indices:
            raise KeyError(f"unknown GUI page: {key!r}")
        assert self._stack is not None
        assert self._page_title is not None
        assert self._page_subtitle is not None

        spec = self._specs_by_key[key]
        self._stack.setCurrentIndex(self._page_indices[key])
        self._nav_buttons[key].setChecked(True)
        self._page_title.setText(spec.title)
        self._page_subtitle.setText(spec.subtitle)
        self._current_page_key = key
        self.statusBar().showMessage(f"{spec.label} — ready")

    # -- settings and window state ----------------------------------------

    def _startup_page_key(self) -> str:
        if (self._settings.restore_last_page
                and self._settings.last_page in self._page_indices):
            return self._settings.last_page
        return self._settings.startup_page

    def _restore_window_state(self) -> None:
        if not self._settings.remember_window_state:
            return
        geometry = self._settings.window_geometry
        if geometry:
            try:
                restored = QByteArray.fromBase64(geometry.encode("ascii"))
            except (UnicodeError, ValueError):
                restored = QByteArray()
            if not restored.isEmpty():
                self.restoreGeometry(restored)
        state = self._settings.window_state
        if state:
            try:
                restored = QByteArray.fromBase64(state.encode("ascii"))
            except (UnicodeError, ValueError):
                restored = QByteArray()
            if not restored.isEmpty():
                self.restoreState(restored)

    def _persist_window_state(self) -> None:
        """Save geometry/page state without blocking shutdown on failure."""
        last_page = self._current_page_key or self._settings.startup_page
        if self._settings.remember_window_state:
            geometry = bytes(self.saveGeometry().toBase64()).decode("ascii")
            state = bytes(self.saveState().toBase64()).decode("ascii")
        else:
            geometry = ""
            state = ""
        updated = replace(
            self._settings,
            window_geometry=geometry,
            window_state=state,
            last_page=last_page,
        )
        try:
            self._settings_store.save(updated)
        except SettingsError:
            return
        self._settings = updated

    def _apply_persistent_settings(self, settings: AppSettings) -> bool:
        self._settings = settings
        application = QApplication.instance()
        if isinstance(application, QApplication):
            apply_theme(application, settings.theme)
        self.setWindowIcon(create_app_icon(settings.theme))
        self._refresh_theme_visuals()
        applied = self.config_panel.set_analysis_defaults(
            settings.analysis_defaults)
        self.reports_view.set_preferred_format(
            settings.default_export_format)
        return applied

    def _on_theme_selected(self, key: str) -> None:
        """Preview a theme immediately without touching worker state."""
        application = QApplication.instance()
        if isinstance(application, QApplication):
            apply_theme(application, key)
        self.setWindowIcon(create_app_icon(key))
        self._refresh_theme_visuals()
        self.statusBar().showMessage(
            f"{theme_label(key)} theme applied — save Settings to keep it")

    def _refresh_nav_icons(self, *_args) -> None:
        theme = current_theme()
        for key, button in self._nav_buttons.items():
            spec = self._specs_by_key[key]
            color = theme.accent if button.isChecked() else theme.text_muted
            button.setIcon(icon(spec.icon, color))
            button.setIconSize(QSize(18, 18))

    def _refresh_action_icons(self) -> None:
        if not hasattr(self, "analyze_button"):
            return
        theme = current_theme()
        analyze_color = (
            theme.accent_text if self.analyze_button.isEnabled()
            else theme.disabled_text)
        cancel_color = (
            theme.text_muted if self.cancel_button.isEnabled()
            else theme.disabled_text)
        self.analyze_button.setIcon(icon("play", analyze_color))
        self.analyze_button.setIconSize(QSize(15, 15))
        self.cancel_button.setIcon(icon("stop", cancel_color))
        self.cancel_button.setIconSize(QSize(14, 14))

    def _refresh_icons(self, *_args) -> None:
        self._refresh_nav_icons()
        self._refresh_action_icons()

    def _refresh_theme_visuals(self, *_args) -> None:
        self._refresh_icons()
        self.dashboard.refresh_theme()
        self.detections_view.refresh_theme()

    def _save_settings(self) -> bool:
        if self._analysis_thread is not None:
            self.settings_view.show_error(
                "Settings cannot be saved while an analysis is running.")
            return False
        try:
            candidate = self.settings_view.collect_settings(self._settings)
        except (ConfigError, ValueError) as exc:
            self.settings_view.show_error(str(exc))
            return False
        try:
            self._settings_store.save(candidate)
        except SettingsError as exc:
            self.settings_view.show_error(str(exc))
            return False
        applied = self._apply_persistent_settings(candidate)
        self.settings_view.set_settings(candidate)
        if applied:
            self.settings_view.show_saved("Settings saved.")
            self.statusBar().showMessage("Settings saved")
        else:
            self.settings_view.show_warning(
                "Settings saved, but the active analysis configuration "
                "needs attention.")
            self.statusBar().showMessage("Settings saved; configuration needs attention")
        return True

    def _reset_settings(self) -> bool:
        if self._analysis_thread is not None:
            self.settings_view.show_error(
                "Settings cannot be reset while an analysis is running.")
            return False
        defaults = AppSettings.defaults()
        try:
            self._settings_store.save(defaults)
        except SettingsError as exc:
            self.settings_view.show_error(str(exc))
            return False
        applied = self._apply_persistent_settings(defaults)
        self.settings_view.set_settings(defaults)
        if applied:
            self.settings_view.show_saved("Settings reset to defaults.")
            self.statusBar().showMessage("Settings reset to defaults")
        else:
            self.settings_view.show_warning(
                "Defaults restored, but the active configuration needs "
                "attention.")
        return True

    # -- shell construction ------------------------------------------------

    def _build_ui(self) -> None:
        container = QWidget(self)
        container.setObjectName("AppContainer")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_sidebar())
        layout.addWidget(self._build_workspace(), 1)
        self.setCentralWidget(container)

        self._build_status_bar()
        self._install_shortcuts()

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(252)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(18, 22, 18, 18)
        layout.setSpacing(0)

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(0, 0, 0, 0)
        brand_row.setSpacing(12)

        mark = BrandMarkLabel(44)
        brand_row.addWidget(mark)

        brand_text = QVBoxLayout()
        brand_text.setContentsMargins(0, 0, 0, 0)
        brand_text.setSpacing(1)
        name = QLabel(APP_NAME)
        name.setObjectName("BrandName")
        tagline = QLabel(APP_TAGLINE)
        tagline.setObjectName("BrandTagline")
        brand_text.addWidget(name)
        brand_text.addWidget(tagline)
        brand_row.addLayout(brand_text, 1)
        layout.addLayout(brand_row)

        layout.addSpacing(28)
        section = QLabel("WORKSPACE")
        section.setObjectName("SectionLabel")
        layout.addWidget(section)
        layout.addSpacing(9)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        for spec in _PAGE_SPECS:
            button = QPushButton(spec.label)
            button.setObjectName("NavButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setIconSize(QSize(18, 18))
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setToolTip(f"Open {spec.label}")
            button.clicked.connect(
                lambda _checked=False, page_key=spec.key:
                self.navigate_to(page_key))
            button.toggled.connect(self._refresh_nav_icons)
            self._nav_group.addButton(button)
            self._nav_buttons[spec.key] = button
            layout.addWidget(button)
            layout.addSpacing(4)

        layout.addStretch(1)
        layout.addSpacing(12)

        system_label = QLabel("SYSTEM")
        system_label.setObjectName("SectionLabel")
        layout.addWidget(system_label)
        layout.addSpacing(9)
        layout.addWidget(self._build_sidebar_footer())
        return sidebar

    def _build_sidebar_footer(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("SidebarFooter")
        layout = QVBoxLayout(footer)
        layout.setContentsMargins(13, 12, 13, 12)
        layout.setSpacing(6)

        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        status_row.setSpacing(8)
        dot = QLabel()
        dot.setObjectName("StatusDot")
        dot.setFixedSize(8, 8)
        status_row.addWidget(dot)
        title = QLabel("Offline analysis core")
        title.setObjectName("FooterTitle")
        status_row.addWidget(title, 1)
        layout.addLayout(status_row)

        detail = QLabel("No network · Read-only input")
        detail.setObjectName("FooterText")
        detail.setWordWrap(True)
        layout.addWidget(detail)

        version = QLabel(f"LogSentinel v{__version__}")
        version.setObjectName("FooterVersion")
        layout.addWidget(version)
        return footer

    def _build_workspace(self) -> QWidget:
        workspace = QWidget()
        workspace.setObjectName("Workspace")
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._build_header())

        self._stack = QStackedWidget()
        self._stack.setObjectName("WorkspaceStack")
        self._stack.addWidget(self._build_overview_page())
        self._stack.addWidget(self._build_detections_page())
        self._stack.addWidget(self._build_log_explorer_page())
        self._stack.addWidget(self._build_reports_page())
        self._stack.addWidget(self._build_settings_page())
        layout.addWidget(self._stack, 1)
        return workspace

    def _build_header(self) -> QFrame:
        header = QFrame()
        header.setObjectName("HeaderBar")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(16)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(3)
        self._page_title = QLabel()
        self._page_title.setObjectName("PageTitle")
        self._page_subtitle = QLabel()
        self._page_subtitle.setObjectName("PageSubtitle")
        text_column.addWidget(self._page_title)
        text_column.addWidget(self._page_subtitle)
        layout.addLayout(text_column, 1)

        layout.addWidget(self._chip("LOCAL / OFFLINE", accent=True))
        layout.addWidget(self._chip("READ-ONLY INPUT"))
        layout.addWidget(self._chip(f"v{__version__}"))
        return header

    def _build_status_bar(self) -> None:
        bar = QStatusBar(self)
        bar.setObjectName("AppStatusBar")
        bar.setSizeGripEnabled(True)
        self.setStatusBar(bar)
        bar.showMessage("Ready — no analysis running")
        bar.addPermanentWidget(self._status_pill("OFFLINE", accent=True))
        bar.addPermanentWidget(self._status_pill(f"v{__version__}"))

    def _build_run_bar(self) -> QFrame:
        bar = QFrame()
        bar.setObjectName("RunBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(18, 12, 18, 12)
        layout.setSpacing(14)

        text_column = QVBoxLayout()
        text_column.setContentsMargins(0, 0, 0, 0)
        text_column.setSpacing(2)
        self._run_status = QLabel("Ready to analyze")
        self._run_status.setObjectName("RunStatus")
        self._run_detail = QLabel(
            "Add at least one input source to begin.")
        self._run_detail.setObjectName("RunDetail")
        self._run_detail.setWordWrap(True)
        text_column.addWidget(self._run_status)
        text_column.addWidget(self._run_detail)
        layout.addLayout(text_column, 1)

        self._run_progress = QProgressBar()
        self._run_progress.setObjectName("RunProgress")
        self._run_progress.setRange(0, 100)
        self._run_progress.setValue(0)
        self._run_progress.setTextVisible(False)
        self._run_progress.setFixedWidth(220)
        self._run_progress.setVisible(False)
        layout.addWidget(self._run_progress)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("GhostButton")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setMinimumHeight(36)
        self.cancel_button.setToolTip(
            "Stop the active analysis and let staging cleanup finish")
        self.cancel_button.clicked.connect(self.cancel_analysis)
        self.cancel_button.setVisible(False)
        layout.addWidget(self.cancel_button)

        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.setObjectName("PrimaryButton")
        self.analyze_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analyze_button.setMinimumHeight(36)
        self.analyze_button.setToolTip(
            "Run the analysis in a background thread")
        self.analyze_button.clicked.connect(self.start_analysis)
        layout.addWidget(self.analyze_button)
        return bar

    def _install_shortcuts(self) -> None:
        for index, spec in enumerate(_PAGE_SPECS, start=1):
            shortcut = QShortcut(QKeySequence(f"Ctrl+{index}"), self)
            shortcut.activated.connect(
                lambda page_key=spec.key: self.navigate_to(page_key))
            self._shortcuts.append(shortcut)

    # -- workspace pages ---------------------------------------------------

    def _build_overview_page(self) -> QWidget:
        page, layout = self._new_page()

        hero = QFrame()
        hero.setObjectName("HeroCard")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(28, 24, 28, 24)
        hero_layout.setSpacing(10)

        eyebrow = QLabel("DEFENSIVE LOG ANALYSIS")
        eyebrow.setObjectName("HeroEyebrow")
        title = QLabel("Security signal, without the noise.")
        title.setObjectName("HeroTitle")
        body = QLabel(
            "A focused workspace for reviewing SSH, firewall, and web access "
            "log findings. Every result will be presented as an evidence-backed "
            "review lead for a human analyst."
        )
        body.setObjectName("HeroText")
        body.setWordWrap(True)
        hero_layout.addWidget(eyebrow)
        hero_layout.addWidget(title)
        hero_layout.addWidget(body)

        chip_row = QHBoxLayout()
        chip_row.setContentsMargins(0, 8, 0, 0)
        chip_row.setSpacing(8)
        chip_row.addWidget(self._chip("LOCAL ONLY", accent=True))
        chip_row.addWidget(self._chip("EVIDENCE FIRST"))
        chip_row.addWidget(self._chip("DETERMINISTIC"))
        chip_row.addStretch(1)
        hero_layout.addLayout(chip_row)
        layout.addWidget(hero)

        layout.addWidget(self._build_run_bar())

        setup_row = QHBoxLayout()
        setup_row.setContentsMargins(0, 0, 0, 0)
        setup_row.setSpacing(14)
        setup_row.addWidget(self.input_panel, 3)
        setup_row.addWidget(self.config_panel, 2)
        layout.addLayout(setup_row)

        layout.addWidget(self.dashboard)

        note = QLabel(
            "Findings are evidence-backed review leads. Sanitized evidence "
            "and diagnostics are shown in the dashboard and Detections page."
        )
        note.setObjectName("MutedLabel")
        layout.addWidget(note)
        layout.addStretch(1)
        return page

    def _build_detections_page(self) -> QWidget:
        page, layout = self._new_page()
        layout.addWidget(self.detections_view)
        return page

    def _build_log_explorer_page(self) -> QWidget:
        page, layout = self._new_page()
        layout.addWidget(self.log_explorer_view)
        return page

    def _build_reports_page(self) -> QWidget:
        page, layout = self._new_page()
        layout.addWidget(self.reports_view)
        return page

    def _build_settings_page(self) -> QWidget:
        page, layout = self._new_page()
        layout.addWidget(self.settings_view)
        return page

    # -- panel status wiring ----------------------------------------------

    def _on_inputs_changed(self) -> None:
        sources = len(self.input_panel.selected_paths)
        files = len(self.input_panel.discovered_files)
        self.statusBar().showMessage(
            f"{sources} input source{'' if sources == 1 else 's'} · "
            f"{files} log file{'' if files == 1 else 's'} discovered")
        self._refresh_analysis_controls()

    def _on_configuration_changed(self) -> None:
        try:
            effective = self.config_panel.effective_config()
        except ConfigError:
            # The panel already reports validation failures; keep the last
            # known discovery limit rather than blocking input management.
            effective = None
        if effective is not None:
            self.input_panel.set_max_file_mb(effective.max_file_mb)

        overrides = len(self.config_panel.dirty_keys)
        if overrides:
            self.statusBar().showMessage(
                f"Configuration changed · {overrides} override"
                f"{'' if overrides == 1 else 's'}")
        else:
            self.statusBar().showMessage("Configuration reset to inherited values")
        self._refresh_analysis_controls()

    # -- analysis worker wiring -------------------------------------------

    def _set_run_message(self, status: str, detail: str) -> None:
        self._run_status.setText(status)
        self._run_detail.setText(_sanitize(detail))
        self.statusBar().showMessage(_sanitize(status))

    def _refresh_analysis_controls(self, *, update_text: bool = True) -> None:
        """Enable Analyze only when inputs and configuration are valid."""
        if not hasattr(self, "analyze_button"):
            return
        if (self._analysis_thread is not None
                or self._export_thread is not None):
            self.analyze_button.setEnabled(False)
            self._refresh_action_icons()
            return

        sources = len(self.input_panel.selected_paths)
        try:
            self.config_panel.effective_config()
            config_ok = True
        except ConfigError:
            config_ok = False
        self.analyze_button.setEnabled(sources > 0 and config_ok)
        self._refresh_action_icons()

        if not update_text:
            return
        if not sources:
            self._run_status.setText("Ready to analyze")
            self._run_detail.setText(
                "Add at least one input source to begin.")
        elif not config_ok:
            self._run_status.setText("Configuration needs attention")
            self._run_detail.setText(
                "Resolve the configuration error before analyzing.")
        else:
            files = len(self.input_panel.discovered_files)
            self._run_status.setText("Ready to analyze")
            self._run_detail.setText(
                f"{sources} source{'' if sources == 1 else 's'} · "
                f"{files} log file{'' if files == 1 else 's'} ready")

    def _set_running_ui(self, running: bool) -> None:
        if hasattr(self, "settings_view"):
            self.settings_view.set_analysis_running(running)
        self._run_progress.setVisible(True)
        self.cancel_button.setVisible(running)
        self.cancel_button.setEnabled(running)
        self.input_panel.setEnabled(not running)
        self.config_panel.setEnabled(not running)
        if running:
            self.analyze_button.setEnabled(False)
            self._refresh_action_icons()
        else:
            self._refresh_analysis_controls(update_text=False)

    def _on_analysis_started(self) -> None:
        self._run_status.setText("Analysis running")
        self._run_detail.setText("Preparing input discovery…")
        self._run_progress.setRange(0, 0)
        self.statusBar().showMessage("Analysis running…")

    def _on_analysis_progress(self, event: object) -> None:
        message = _sanitize(getattr(event, "message", "Analysis running"))
        self._run_status.setText(message or "Analysis running")
        files_total = getattr(event, "files_total", 0)
        files_done = getattr(event, "files_done", 0)
        events_seen = getattr(event, "events_seen", 0)
        phase = getattr(event, "phase", "")
        if phase == "reading" and files_total > 0:
            self._run_progress.setRange(0, files_total)
            self._run_progress.setValue(min(files_done, files_total))
            detail = (
                f"{files_done}/{files_total} files · "
                f"{events_seen} events seen")
        elif phase == "complete":
            self._run_progress.setRange(0, 100)
            self._run_progress.setValue(100)
            detail = f"{events_seen} events processed"
        else:
            self._run_progress.setRange(0, 0)
            detail = (
                f"{files_total} files queued · {events_seen} events seen")
        self._run_detail.setText(detail)
        self.statusBar().showMessage(message or "Analysis running…")

    def _on_analysis_completed(self, result: AnalysisResult) -> None:
        self._last_result = result
        self.dashboard.set_result(result)
        self.detections_view.set_result(result)
        self.log_explorer_view.set_result(result)
        self.reports_view.set_result(result)
        findings = len(result.findings)
        self._run_status.setText("Analysis complete")
        self._run_detail.setText(
            f"{findings} finding{'' if findings == 1 else 's'} · "
            f"{result.statistics.files_scanned} file"
            f"{'' if result.statistics.files_scanned == 1 else 's'} scanned · "
            f"{result.errors_total} error"
            f"{'' if result.errors_total == 1 else 's'}")
        self._run_progress.setRange(0, 100)
        self._run_progress.setValue(100)
        self.statusBar().showMessage("Analysis complete")

    def _on_analysis_cancelled(self) -> None:
        self._last_result = None
        self.dashboard.clear(
            "Analysis cancelled",
            "No results are displayed for a cancelled run.")
        self.detections_view.clear(
            "Analysis cancelled",
            "No detections are displayed for a cancelled run.")
        self.log_explorer_view.clear(
            "Analysis cancelled",
            "No event statistics are displayed for a cancelled run.")
        self.reports_view.clear(
            "Analysis cancelled",
            "No reports can be exported for a cancelled run.")
        self._run_status.setText("Analysis cancelled")
        self._run_detail.setText(
            "The run was stopped and temporary staging data was cleaned up.")
        self._run_progress.setRange(0, 100)
        self._run_progress.setValue(0)
        self.statusBar().showMessage("Analysis cancelled")

    def _on_analysis_failed(self, message: str) -> None:
        safe_message = _sanitize(message) or "The analysis failed."
        self._last_result = None
        self.dashboard.clear(
            "Analysis failed",
            "No results are displayed for a failed run.")
        self.detections_view.clear(
            "Analysis failed",
            "No detections are displayed for a failed run.")
        self.log_explorer_view.clear(
            "Analysis failed",
            "No event statistics are displayed for a failed run.")
        self.reports_view.clear(
            "Analysis failed",
            "No reports can be exported for a failed run.")
        self._run_status.setText("Analysis failed")
        self._run_detail.setText(safe_message)
        self._run_progress.setRange(0, 100)
        self._run_progress.setValue(0)
        self.statusBar().showMessage("Analysis failed")

    def _on_analysis_thread_finished(self) -> None:
        self._analysis_thread = None
        self._analysis_worker = None
        self._set_running_ui(False)
        if self._close_pending:
            self._close_pending = False
            self.close()

    # -- report export wiring ---------------------------------------------

    def _on_export_requested(self, kind: str, path: str) -> None:
        """Start one background export for the current completed result."""
        if self._analysis_thread is not None:
            self.reports_view.show_failure(
                "Wait for the analysis to finish before exporting.")
            return
        if self._export_thread is not None:
            self.reports_view.show_failure(
                "Another report export is already in progress.")
            return
        result = self._last_result
        if result is None:
            self.reports_view.show_failure(
                "No completed analysis is available for export.")
            return

        worker = ExportWorker(result, kind, path)
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.completed.connect(self._on_export_completed)
        worker.failed.connect(self._on_export_failed)
        worker.finished.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._on_export_thread_finished)

        self._export_worker = worker
        self._export_thread = thread
        self._export_kind = kind
        self._export_path = path
        self.reports_view.set_exporting(True)
        self._refresh_analysis_controls(update_text=False)
        self.statusBar().showMessage(f"Exporting {kind.upper()} report…")
        thread.start()

    def _on_export_completed(self, path: str) -> None:
        kind = self._export_kind or "Report"
        self.reports_view.show_success(kind, path)
        self.statusBar().showMessage(f"{kind.upper()} report exported")

    def _on_export_failed(self, message: str) -> None:
        self.reports_view.show_failure(message)
        self.statusBar().showMessage("Report export failed")

    def _on_export_thread_finished(self) -> None:
        self._export_thread = None
        self._export_worker = None
        self._export_kind = None
        self._export_path = None
        self.reports_view.set_exporting(False)
        self._refresh_analysis_controls(update_text=False)
        if self._close_pending:
            self._close_pending = False
            self.close()

    def _shutdown_export(self) -> None:
        """Wait for a short report write when the application itself quits."""
        thread = self._export_thread
        if thread is not None and thread.isRunning():
            thread.quit()
            thread.wait(5_000)

    def _shutdown_analysis(self) -> None:
        """Cancel and await the worker when the application itself quits."""
        worker = self._analysis_worker
        thread = self._analysis_thread
        if worker is not None:
            worker.cancel()
        if thread is not None and thread.isRunning():
            # quit() is safe from the GUI thread; the worker's cooperative
            # cancellation lets its run() slot return and the event loop exit.
            thread.quit()
            thread.wait(10_000)

    # -- reusable visual components ---------------------------------------

    def _new_page(self) -> tuple[QScrollArea, QVBoxLayout]:
        content = QWidget()
        content.setObjectName("PageContainer")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 26, 30, 30)
        layout.setSpacing(18)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content)
        return scroll, layout

    def _chip(self, text: str, *, accent: bool = False) -> QLabel:
        label = QLabel(text)
        label.setObjectName("ChipAccent" if accent else "Chip")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _status_pill(self, text: str, *, accent: bool = False) -> QLabel:
        label = QLabel(text)
        label.setObjectName("StatusPillAccent" if accent else "StatusPill")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label


def create_main_window() -> MainWindow:
    """Construct the shell and apply the application icon."""
    window = MainWindow()
    app = QApplication.instance()
    if isinstance(app, QApplication):
        window.setWindowIcon(create_app_icon())
    return window
