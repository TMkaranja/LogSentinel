"""Functional Settings centre for the LogSentinel desktop GUI.

The view edits persistent application preferences and the supported analysis
defaults. Analysis values are validated by the existing configuration layer
when collected; the view itself does not implement a second validator.
"""

from __future__ import annotations

from dataclasses import replace

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..config import DEFAULTS, load_config
from ..report import _sanitize
from .app_settings import (
    DEFAULT_EXPORT_FORMAT,
    EXPORT_FORMATS,
    PAGE_LABELS,
    AppSettings,
)
from .icon_widgets import BrandWordmarkLabel
from .icons import theme_preview_pixmap
from .themes import DEFAULT_THEME_KEY, THEMES

__all__ = ["SettingsView"]

_FIELD_LABELS = {
    "ssh_threshold": "SSH failure threshold",
    "ssh_window_seconds": "SSH detection window (seconds)",
    "portscan_threshold": "Port-scan threshold",
    "http_4xx_threshold": "HTTP 4xx threshold",
    "max_line_length": "Maximum log-line length",
    "max_file_mb": "Maximum input file size (MB)",
}
_FIELD_ORDER = tuple(_FIELD_LABELS)
_EXPORT_LABELS = {"json": "JSON (structured)", "html": "HTML (standalone)"}


def _label(text: str, object_name: str, *, wrap: bool = False) -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    if wrap:
        label.setWordWrap(True)
    return label


def _field_label(text: str) -> QLabel:
    label = _label(text, "FieldLabel")
    return label


def _bullet(text: str) -> QLabel:
    return _label(f"•  {text}", "BodyText", wrap=True)


def _set_state(label: QLabel, object_name: str) -> None:
    if label.objectName() == object_name:
        return
    label.setObjectName(object_name)
    style = label.style()
    style.unpolish(label)
    style.polish(label)
    label.update()


class SettingsView(QWidget):
    """Settings page with persistent save/reset lifecycle."""

    save_requested = Signal()
    reset_requested = Signal()
    theme_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._settings: AppSettings | None = None
        self._baseline: dict[str, object] | None = None
        self._updating = False
        self._analysis_running = False
        self._analysis_spins: dict[str, QSpinBox] = {}
        self._theme_key = DEFAULT_THEME_KEY
        self._theme_buttons: dict[str, QPushButton] = {}
        self._theme_group = QButtonGroup(self)
        self._theme_group.setExclusive(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        header.addWidget(_label("Settings", "SectionHeading"))
        self._persistent_chip = _label("PERSISTENT", "ChipAccent")
        header.addWidget(self._persistent_chip)
        header.addStretch(1)
        self._dirty_label = _label("All changes saved", "PanelHint")
        header.addWidget(self._dirty_label)
        layout.addLayout(header)

        general_row = QHBoxLayout()
        general_row.setContentsMargins(0, 0, 0, 0)
        general_row.setSpacing(14)
        general_row.addWidget(self._build_general_card(), 1)
        general_row.addWidget(self._build_appearance_card(), 1)
        layout.addLayout(general_row)

        layout.addWidget(self._build_analysis_card())

        lower_row = QHBoxLayout()
        lower_row.setContentsMargins(0, 0, 0, 0)
        lower_row.setSpacing(14)
        lower_row.addWidget(self._build_inputs_card(), 1)
        lower_row.addWidget(self._build_reports_card(), 1)
        layout.addLayout(lower_row)

        security_row = QHBoxLayout()
        security_row.setContentsMargins(0, 0, 0, 0)
        security_row.setSpacing(14)
        security_row.addWidget(self._build_security_card(), 1)
        security_row.addWidget(self._build_about_card(), 1)
        layout.addLayout(security_row)

        self._feedback = _label("Settings loaded.", "PanelHint", wrap=True)
        self._feedback.setTextFormat(Qt.TextFormat.PlainText)
        self._feedback.setMinimumHeight(22)
        layout.addWidget(self._feedback)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)
        self._reset_button = QPushButton("Reset to Defaults")
        self._reset_button.setObjectName("GhostButton")
        self._reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reset_button.setMinimumHeight(36)
        self._reset_button.setToolTip(
            "Restore persistent settings to the built-in defaults")
        self._reset_button.clicked.connect(self.request_reset)
        action_row.addWidget(self._reset_button)
        action_row.addStretch(1)
        self._save_button = QPushButton("Save Settings")
        self._save_button.setObjectName("PrimaryButton")
        self._save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_button.setMinimumHeight(36)
        self._save_button.setToolTip(
            "Validate and save application defaults and interface preferences")
        self._save_button.clicked.connect(self.request_save)
        action_row.addWidget(self._save_button)
        layout.addLayout(action_row)
        layout.addStretch(1)

        self._refresh_state()

    # -- construction ------------------------------------------------------

    @staticmethod
    def _card(title: str, subtitle: str, chip: str | None = None) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        header.addWidget(_label(title, "SectionHeading"))
        header.addStretch(1)
        if chip:
            header.addWidget(_label(chip, "Chip"))
        layout.addLayout(header)
        description = _label(subtitle, "PanelHint", wrap=True)
        layout.addWidget(description)
        return card

    def _build_general_card(self) -> QFrame:
        card = self._card(
            "General",
            "Window and navigation preferences apply on the next launch.")
        layout = card.layout()
        self._remember_window = QCheckBox("Remember window size and position")
        self._remember_window.setObjectName("RememberWindowCheck")
        self._remember_window.setToolTip(
            "Save and restore the LogSentinel window geometry")
        self._remember_window.toggled.connect(self._mark_dirty)
        layout.addWidget(self._remember_window)

        self._restore_last_page = QCheckBox("Restore the last open page")
        self._restore_last_page.setObjectName("RestoreLastPageCheck")
        self._restore_last_page.setToolTip(
            "Open the page that was active when the application last closed")
        self._restore_last_page.toggled.connect(self._mark_dirty)
        layout.addWidget(self._restore_last_page)

        startup_row = QHBoxLayout()
        startup_row.setContentsMargins(0, 2, 0, 0)
        startup_row.setSpacing(8)
        startup_row.addWidget(_field_label("Startup page"))
        self._startup_page = QComboBox()
        self._startup_page.setObjectName("SettingsStartupPage")
        for key, label in PAGE_LABELS.items():
            self._startup_page.addItem(label, key)
        self._startup_page.currentIndexChanged.connect(self._mark_dirty)
        startup_row.addWidget(self._startup_page, 1)
        layout.addLayout(startup_row)
        layout.addStretch(1)
        return card

    def _build_appearance_card(self) -> QFrame:
        card = self._card(
            "Appearance",
            "Select a visual theme. Changes apply immediately; save to keep "
            "them across launches.")
        layout = card.layout()
        grid = QGridLayout()
        grid.setContentsMargins(0, 3, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        for index, (key, theme) in enumerate(THEMES.items()):
            button = QPushButton(theme.name)
            button.setObjectName("ThemeButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setIcon(theme_preview_pixmap(theme))
            button.setIconSize(QSize(54, 32))
            button.setMinimumHeight(58)
            button.setToolTip(f"{theme.name}: {theme.description}")
            button.setAccessibleName(f"{theme.name} theme")
            button.clicked.connect(
                lambda _checked=False, theme_key=key:
                self._select_theme(theme_key))
            self._theme_group.addButton(button, index)
            self._theme_buttons[key] = button
            grid.addWidget(button, index // 2, index % 2)
        layout.addLayout(grid)
        layout.addWidget(_bullet(
            "Each theme includes matching typography, severity colours, "
            "focus states, and control styling."))
        layout.addStretch(1)
        return card

    def _build_analysis_card(self) -> QFrame:
        card = self._card(
            "Analysis defaults",
            "These persistent defaults are validated with the CLI "
            "configuration rules. Temporary per-analysis overrides still "
            "take precedence.")
        layout = card.layout()
        grid = QGridLayout()
        grid.setContentsMargins(0, 4, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(9)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        for index, key in enumerate(_FIELD_ORDER):
            row = index // 2
            column = (index % 2) * 2
            label = _field_label(_FIELD_LABELS[key])
            spin = QSpinBox()
            spin.setObjectName(f"settings_{key}_spin")
            spin.setRange(1, 2_147_483_647)
            spin.setAccelerated(True)
            spin.setKeyboardTracking(False)
            spin.setToolTip(
                "Positive integer validated by the existing configuration layer")
            spin.valueChanged.connect(self._on_analysis_value_changed)
            self._analysis_spins[key] = spin
            grid.addWidget(label, row, column)
            grid.addWidget(spin, row, column + 1)

        strict_row = (len(_FIELD_ORDER) + 1) // 2
        self._strict = QCheckBox("Abort analysis on the first recorded error")
        self._strict.setObjectName("settings_strict_check")
        self._strict.setToolTip(
            "Strict mode preserves the existing abort-on-first-error contract")
        self._strict.toggled.connect(self._mark_dirty)
        grid.addWidget(_field_label("Strict mode"), strict_row, 0)
        grid.addWidget(self._strict, strict_row, 1, 1, 3)
        layout.addLayout(grid)
        layout.addWidget(_label(
            "Saved defaults are the base layer: built-in values are "
            "replaced here, then an optional JSON file and per-analysis edits "
            "can override them.",
            "PanelHint",
            wrap=True,
        ))
        return card

    def _build_inputs_card(self) -> QFrame:
        card = self._card(
            "Input handling",
            "Input discovery remains fixed to the safe existing rules.")
        layout = card.layout()
        for text in (
            "Directories are scanned recursively for non-hidden .log and "
            ".txt files.",
            "Log files are opened read-only; original inputs are never "
            "modified.",
            "Files above the configured size cap are skipped by discovery "
            "with a sanitized diagnostic.",
            "Overlong lines are rejected by the existing parser limit.",
        ):
            layout.addWidget(_bullet(text))
        self._file_cap_label = _label(
            f"Current file-size cap: {DEFAULTS['max_file_mb']} MB", "PanelHint")
        self._line_cap_label = _label(
            f"Current line-length cap: {DEFAULTS['max_line_length']} characters",
            "PanelHint")
        layout.addWidget(self._file_cap_label)
        layout.addWidget(self._line_cap_label)
        layout.addStretch(1)
        return card

    def _build_reports_card(self) -> QFrame:
        card = self._card(
            "Reports",
            "Choose the preferred report format for future export sessions.")
        layout = card.layout()
        report_row = QHBoxLayout()
        report_row.setContentsMargins(0, 0, 0, 0)
        report_row.setSpacing(8)
        report_row.addWidget(_field_label("Preferred export format"))
        self._default_export = QComboBox()
        self._default_export.setObjectName("SettingsDefaultExportFormat")
        for kind in EXPORT_FORMATS:
            self._default_export.addItem(_EXPORT_LABELS[kind], kind)
        self._default_export.currentIndexChanged.connect(self._mark_dirty)
        report_row.addWidget(self._default_export, 1)
        layout.addLayout(report_row)
        layout.addWidget(_label(
            "Default filename pattern: "
            "logsentinel-report-<run-timestamp>.<json|html>",
            "PanelHint",
            wrap=True,
        ))
        layout.addWidget(_bullet(
            "JSON continues to use the existing report renderer."))
        layout.addWidget(_bullet(
            "HTML remains standalone, escaped, and free of external assets."))
        layout.addWidget(_bullet(
            "Credential and source-path redaction remains mandatory for every "
            "export."))
        layout.addStretch(1)
        return card

    def _build_security_card(self) -> QFrame:
        card = self._card(
            "Privacy & security",
            "Mandatory protections are always enabled and are not user "
            "configuration options.")
        layout = card.layout()
        for text in (
            "Credential-bearing values are redacted from evidence and errors.",
            "Source paths are replaced with [REDACTED_PATH] in reports.",
            "Evidence excerpts are redacted, then capped at 256 characters.",
            "Reported errors are sanitized and capped at the first 100 entries.",
            "Analysis is local and offline; no network access is performed.",
        ):
            layout.addWidget(_bullet(text))
        layout.addStretch(1)
        return card

    def _build_about_card(self) -> QFrame:
        card = self._card(
            "About",
            "LogSentinel desktop application information.")
        layout = card.layout()
        layout.addWidget(BrandWordmarkLabel(250, 50))
        layout.addWidget(_label(
            f"Version {__version__}", "BodyText"))
        layout.addWidget(_label(
            "A defensive, offline log-analysis workspace for reviewing "
            "SSH, firewall, and web-access findings as evidence-backed leads.",
            "BodyText",
            wrap=True,
        ))
        layout.addWidget(_label(
            "Local/offline build · Read-only inputs · Deterministic reports",
            "PanelHint",
            wrap=True,
        ))
        layout.addWidget(_label(
            "No public project URL is configured in this build.",
            "PanelHint",
            wrap=True,
        ))
        layout.addStretch(1)
        return card

    # -- public API --------------------------------------------------------

    @property
    def settings(self) -> AppSettings | None:
        return self._settings

    @property
    def is_dirty(self) -> bool:
        return (
            self._settings is not None
            and self._baseline is not None
            and self._current_values() != self._baseline
        )

    @property
    def feedback_text(self) -> str:
        return self._feedback.text()

    @property
    def dirty_text(self) -> str:
        return self._dirty_label.text()

    @property
    def save_button(self) -> QPushButton:
        return self._save_button

    @property
    def reset_button(self) -> QPushButton:
        return self._reset_button

    @property
    def analysis_spins(self) -> dict[str, QSpinBox]:
        return dict(self._analysis_spins)

    @property
    def remember_window_check(self) -> QCheckBox:
        return self._remember_window

    @property
    def restore_last_page_check(self) -> QCheckBox:
        return self._restore_last_page

    @property
    def startup_page_combo(self) -> QComboBox:
        return self._startup_page

    @property
    def default_export_combo(self) -> QComboBox:
        return self._default_export

    @property
    def strict_check(self) -> QCheckBox:
        return self._strict

    @property
    def theme_buttons(self) -> dict[str, QPushButton]:
        return dict(self._theme_buttons)

    @property
    def selected_theme(self) -> str:
        return self._theme_key

    def set_settings(
        self,
        settings: AppSettings,
        *,
        warning: str | None = None,
    ) -> None:
        """Populate the form from validated persistent settings."""
        self._settings = settings
        self._updating = True
        try:
            effective = load_config(
                dict(settings.analysis_defaults), None)
            self._theme_key = settings.theme
            theme_button = self._theme_buttons.get(settings.theme)
            if theme_button is not None:
                theme_button.setChecked(True)
            self._remember_window.setChecked(settings.remember_window_state)
            self._restore_last_page.setChecked(settings.restore_last_page)
            index = self._startup_page.findData(settings.startup_page)
            self._startup_page.setCurrentIndex(max(0, index))
            for key, spin in self._analysis_spins.items():
                spin.setValue(getattr(effective, key))
            self._strict.setChecked(effective.strict)
            index = self._default_export.findData(
                settings.default_export_format)
            self._default_export.setCurrentIndex(max(0, index))
        finally:
            self._updating = False
        self._baseline = self._current_values()
        self._update_cap_labels()
        if warning:
            self.show_warning(warning)
        else:
            self.show_saved("Settings loaded.")
        self._refresh_state()

    def collect_settings(self, base: AppSettings) -> AppSettings:
        """Build a validated candidate, preserving window metadata from base."""
        analysis_defaults = {
            key: spin.value() for key, spin in self._analysis_spins.items()
        }
        analysis_defaults["strict"] = self._strict.isChecked()
        return replace(
            base,
            remember_window_state=self._remember_window.isChecked(),
            restore_last_page=self._restore_last_page.isChecked(),
            startup_page=self._startup_page.currentData() or "overview",
            theme=self._theme_key,
            analysis_defaults=analysis_defaults,
            default_export_format=(
                self._default_export.currentData() or DEFAULT_EXPORT_FORMAT),
        )

    def show_saved(self, message: str = "Settings saved.") -> None:
        if self._settings is not None:
            self._baseline = self._current_values()
        self._set_feedback(message, "PanelSuccess")
        self._refresh_state()

    def show_error(self, message: str) -> None:
        self._set_feedback(
            f"Settings error: {_sanitize(message)}", "PanelError")

    def show_warning(self, message: str) -> None:
        self._set_feedback(
            f"Settings warning: {_sanitize(message)}", "PanelWarning")
        self._refresh_state()

    def set_analysis_running(self, running: bool) -> None:
        self._analysis_running = running
        self._refresh_state()

    def request_save(self) -> None:
        if self._analysis_running:
            self.show_error(
                "Settings cannot be saved while an analysis is running.")
            return
        if not self.is_dirty:
            self._set_feedback("No unsaved settings changes.", "PanelHint")
            return
        self.save_requested.emit()

    def request_reset(self) -> None:
        if self._analysis_running:
            self.show_error(
                "Settings cannot be reset while an analysis is running.")
            return
        answer = QMessageBox.question(
            self,
            "Reset settings",
            "Reset all application settings to their built-in defaults? "
            "This replaces saved window, analysis, and report preferences.",
            QMessageBox.StandardButton.Reset
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Reset:
            self.reset_requested.emit()
        else:
            self._set_feedback("Reset cancelled.", "PanelHint")

    # -- state helpers -----------------------------------------------------

    def _current_values(self) -> dict[str, object]:
        return {
            "remember_window_state": self._remember_window.isChecked(),
            "theme": self._theme_key,
            "restore_last_page": self._restore_last_page.isChecked(),
            "startup_page": self._startup_page.currentData() or "overview",
            "analysis_defaults": {
                key: spin.value()
                for key, spin in self._analysis_spins.items()
            } | {"strict": self._strict.isChecked()},
            "default_export_format": (
                self._default_export.currentData() or DEFAULT_EXPORT_FORMAT),
        }

    def _select_theme(self, key: str) -> None:
        if self._updating or key not in THEMES:
            return
        self._theme_key = key
        button = self._theme_buttons.get(key)
        if button is not None:
            button.setChecked(True)
        self._mark_dirty()
        self.theme_selected.emit(key)

    def _mark_dirty(self, *_args) -> None:
        if self._updating:
            return
        self._refresh_state()

    def _on_analysis_value_changed(self, *_args) -> None:
        self._update_cap_labels()
        self._mark_dirty()

    def _update_cap_labels(self) -> None:
        self._file_cap_label.setText(
            f"Current file-size cap: "
            f"{self._analysis_spins['max_file_mb'].value()} MB")
        self._line_cap_label.setText(
            f"Current line-length cap: "
            f"{self._analysis_spins['max_line_length'].value()} characters")

    def _refresh_state(self) -> None:
        dirty = self.is_dirty
        if self._analysis_running:
            self._dirty_label.setText(
                "Analysis running — save after it finishes"
                if dirty else "Analysis running")
            _set_state(self._dirty_label, "PanelWarning")
        elif dirty:
            self._dirty_label.setText("Unsaved changes")
            _set_state(self._dirty_label, "PanelWarning")
        elif self._settings is not None:
            self._dirty_label.setText("All changes saved")
            _set_state(self._dirty_label, "PanelSuccess")
        else:
            self._dirty_label.setText("All changes saved")
            _set_state(self._dirty_label, "PanelHint")
        enabled = not self._analysis_running and self._settings is not None
        self._save_button.setEnabled(enabled and dirty)
        self._reset_button.setEnabled(enabled)

    def _set_feedback(self, text: str, object_name: str) -> None:
        self._feedback.setText(text)
        _set_state(self._feedback, object_name)
