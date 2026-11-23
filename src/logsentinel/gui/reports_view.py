"""Reports page and background report-export worker for the GUI.

The page only manages presentation, save-dialog selection, and export state.
Formatting and writing are delegated to :mod:`logsentinel.gui.reporting` and
the existing report writer.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, QSize, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..exceptions import ReportError
from ..report import _sanitize
from .backend import AnalysisResult
from .icons import icon
from .reporting import (
    HTML_FORMAT,
    JSON_FORMAT,
    ensure_export_extension,
    export_dialog_title,
    export_report,
    format_generated_at,
    report_filter,
    suggested_export_path,
)
from .theme import current_theme, theme_manager
from .views import EmptyState

__all__ = ["ExportWorker", "ReportsView"]

_FORMAT_LABELS = {JSON_FORMAT: "JSON", HTML_FORMAT: "HTML"}


def _label(text: str, object_name: str, *, wrap: bool = False) -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    if wrap:
        label.setWordWrap(True)
    return label


class ExportWorker(QObject):
    """Render and atomically write one report outside the GUI thread."""

    completed = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        result: AnalysisResult,
        kind: str,
        path: str,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._result = result
        self._kind = kind
        self._path = path

    @Slot()
    def run(self) -> None:
        try:
            export_report(self._result, self._kind, self._path)
        except ReportError:
            self.failed.emit(
                "The report could not be saved. Check the destination "
                "path and permissions.")
        except Exception:
            # Do not echo renderer or filesystem details that could contain
            # sensitive paths or values. The page reports a stable message.
            self.failed.emit("The report could not be generated.")
        else:
            self.completed.emit(self._path)
        finally:
            self.finished.emit()


class ReportsView(QWidget):
    """Latest-result report export panel for the Reports page."""

    export_requested = Signal(str, str)  # (format, path)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        preferred_format: str = JSON_FORMAT,
    ) -> None:
        super().__init__(parent)
        self._result: AnalysisResult | None = None
        self._busy = False
        self._preferred_format = preferred_format
        self._preferred_chips: dict[str, QLabel] = {}
        self._export_buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        header.addWidget(_label("Reports", "SectionHeading"))
        self._status = _label("WAITING", "Chip")
        header.addWidget(self._status)
        header.addStretch(1)
        self._header_hint = _label(
            "Exports use the latest completed analysis", "PanelHint")
        header.addWidget(self._header_hint)
        layout.addLayout(header)

        self._stack = QStackedWidget()
        self._empty = EmptyState(
            "reports",
            "No completed analysis",
            "Run an analysis to enable JSON and HTML report exports. "
            "Cancelled or failed runs are never exported.",
            min_height=260,
        )
        self._stack.addWidget(self._empty)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        meta = QFrame()
        meta.setObjectName("Card")
        meta_layout = QVBoxLayout(meta)
        meta_layout.setContentsMargins(18, 15, 18, 15)
        meta_layout.setSpacing(10)

        meta_header = QHBoxLayout()
        meta_header.setContentsMargins(0, 0, 0, 0)
        meta_header.setSpacing(8)
        meta_header.addWidget(_label(
            "Latest completed analysis", "SectionHeading"))
        meta_header.addStretch(1)
        self._ready = _label("READY TO EXPORT", "ChipAccent")
        meta_header.addWidget(self._ready)
        meta_layout.addLayout(meta_header)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(4)
        self._meta_values: dict[str, QLabel] = {}
        for column, (key, title) in enumerate((
            ("generated", "Generated"),
            ("findings", "Findings"),
            ("files", "Files scanned"),
            ("errors", "Errors"),
        )):
            grid.addWidget(_label(title, "FieldLabel"), 0, column)
            value = _label("—", "StatValue")
            value.setAlignment(
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter)
            self._meta_values[key] = value
            grid.addWidget(value, 1, column)
        meta_layout.addLayout(grid)
        meta_layout.addWidget(_label(
            "Exports always use this result. Starting, cancelling, or failing "
            "another analysis clears the export state.",
            "PanelHint",
            wrap=True,
        ))
        content_layout.addWidget(meta)

        export_row = QHBoxLayout()
        export_row.setContentsMargins(0, 0, 0, 0)
        export_row.setSpacing(14)
        self._json_button = self._build_format_card(
            export_row, JSON_FORMAT, "JSON report", "STRUCTURED",
            "Machine-readable findings, statistics, errors, configuration, "
            "and run metadata. Written with the existing JSON renderer.")
        self._html_button = self._build_format_card(
            export_row, HTML_FORMAT, "HTML report", "STANDALONE",
            "A self-contained, browser-ready security report with escaped "
            "evidence, severity breakdown, statistics, and error summary.")
        content_layout.addLayout(export_row)

        self._feedback = _label(
            "No report exported yet.", "PanelHint", wrap=True)
        self._feedback.setTextFormat(Qt.TextFormat.PlainText)
        self._feedback.setMinimumHeight(22)
        content_layout.addWidget(self._feedback)
        content_layout.addStretch(1)
        self._stack.addWidget(content)
        layout.addWidget(self._stack, 1)

        self._set_export_enabled(False)
        self.set_preferred_format(preferred_format)
        theme_manager.changed.connect(self._refresh_icons)
        self._refresh_icons()

    def _build_format_card(
        self,
        row: QHBoxLayout,
        kind: str,
        title: str,
        badge: str,
        description: str,
    ) -> QPushButton:
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(8)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        top.addWidget(_label(title.upper(), "CardTitle"))
        top.addStretch(1)
        top.addWidget(_label(badge, "Chip"))
        preferred = _label("PREFERRED", "ChipAccent")
        preferred.setVisible(False)
        top.addWidget(preferred)
        self._preferred_chips[kind] = preferred
        card_layout.addLayout(top)
        card_layout.addWidget(_label(title, "SectionHeading"))
        body = _label(description, "BodyText", wrap=True)
        card_layout.addWidget(body)
        card_layout.addStretch(1)

        button = QPushButton(f"Export {_FORMAT_LABELS[kind]}…")
        button.setObjectName("PrimaryButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(36)
        button.setToolTip(f"Choose a destination for the {title.lower()}")
        button.clicked.connect(
            lambda _checked=False, report_kind=kind:
            self.request_export(report_kind))
        self._export_buttons[kind] = button
        card_layout.addWidget(button)
        row.addWidget(card, 1)
        return button

    def _refresh_icons(self, *_args) -> None:
        color = current_theme().accent_text
        for button in self._export_buttons.values():
            button.setIcon(icon("download", color))
            button.setIconSize(QSize(16, 16))

    # -- result and export state ------------------------------------------

    def set_result(self, result: AnalysisResult) -> None:
        self._result = result
        self._busy = False
        generated = format_generated_at(result.generated_at)
        self._meta_values["generated"].setText(generated)
        self._meta_values["findings"].setText(f"{len(result.findings):,}")
        self._meta_values["files"].setText(
            f"{result.statistics.files_scanned:,}")
        self._meta_values["errors"].setText(f"{result.errors_total:,}")
        self._status.setText("READY")
        self._header_hint.setText(
            "Exports use the latest completed analysis")
        self._set_feedback(
            "Ready to export the latest completed analysis.", "PanelHint")
        self._set_export_enabled(True)
        self._stack.setCurrentIndex(1)

    def clear(
        self,
        title: str = "No completed analysis",
        detail: str = (
            "Run an analysis to enable JSON and HTML report exports. "
            "Cancelled or failed runs are never exported."
        ),
    ) -> None:
        self._result = None
        self._busy = False
        self._stack.setCurrentIndex(0)
        self._empty.set_message("reports", title, detail)
        self._status.setText("WAITING")
        self._header_hint.setText(
            "Exports use the latest completed analysis")
        self._set_feedback("No report exported yet.", "PanelHint")
        self._feedback.setToolTip("")
        for value in self._meta_values.values():
            value.setText("—")
        self._set_export_enabled(False)

    def set_preferred_format(self, kind: str) -> None:
        if kind not in _FORMAT_LABELS:
            raise ValueError(f"unsupported report format: {kind!r}")
        self._preferred_format = kind
        for report_kind, chip in self._preferred_chips.items():
            chip.setVisible(report_kind == kind)

    def set_exporting(self, exporting: bool) -> None:
        self._busy = exporting
        self._set_export_enabled(self._result is not None and not exporting)
        if exporting:
            self._set_feedback("Preparing report…", "PanelHint")

    def show_success(self, kind: str, path: str) -> None:
        label = _FORMAT_LABELS.get(kind, kind.upper())
        self._set_feedback(
            f"{label} report saved to {path}", "PanelSuccess")
        self._feedback.setToolTip(path)

    def show_failure(self, message: str) -> None:
        safe = _sanitize(message) or "The report export failed."
        self._set_feedback(f"Export failed: {safe}", "PanelError")

    def request_export(self, kind: str) -> bool:
        if kind not in _FORMAT_LABELS:
            self.show_failure("Unsupported report format.")
            return False
        if self._result is None:
            self._set_feedback(
                "No completed analysis is available for export.", "PanelHint")
            return False
        if self._busy:
            self._set_feedback(
                "Another report export is already in progress.", "PanelHint")
            return False

        try:
            selected, _selected_filter = QFileDialog.getSaveFileName(
                self,
                export_dialog_title(kind),
                suggested_export_path(self._result, kind),
                report_filter(kind),
            )
        except Exception:
            self.show_failure("The save dialog could not be opened.")
            return False
        if not selected:
            self._set_feedback("Export cancelled.", "PanelHint")
            return False
        try:
            path = ensure_export_extension(selected, kind)
        except ValueError:
            self.show_failure("The selected export path is invalid.")
            return False
        self.export_requested.emit(kind, path)
        return True

    def _set_export_enabled(self, enabled: bool) -> None:
        self._json_button.setEnabled(enabled)
        self._html_button.setEnabled(enabled)

    def _set_feedback(self, text: str, object_name: str) -> None:
        self._feedback.setText(text)
        self._feedback.setObjectName(object_name)
        style = self._feedback.style()
        style.unpolish(self._feedback)
        style.polish(self._feedback)
        self._feedback.update()

    # -- public state for tests and embedding ------------------------------

    @property
    def result(self) -> AnalysisResult | None:
        return self._result

    @property
    def is_export_enabled(self) -> bool:
        return self._json_button.isEnabled() and self._html_button.isEnabled()

    @property
    def is_exporting(self) -> bool:
        return self._busy

    @property
    def preferred_format(self) -> str:
        return self._preferred_format

    @property
    def feedback_text(self) -> str:
        return self._feedback.text()

    @property
    def stack(self) -> QStackedWidget:
        return self._stack

    @property
    def empty_state(self) -> EmptyState:
        return self._empty

    @property
    def json_button(self) -> QPushButton:
        return self._json_button

    @property
    def html_button(self) -> QPushButton:
        return self._html_button
