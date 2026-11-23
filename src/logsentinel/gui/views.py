"""Results and event-summary widgets for the LogSentinel desktop GUI.

The dashboard and summary views consume the existing ``AnalysisResult``
unchanged. It performs
no detection, parsing, or reporting work: it presents findings, run
statistics, and the capped error summary through reusable Qt models.

Security rules are preserved at the presentation boundary:

- evidence is passed through the existing report sanitizer before display;
- summaries use the existing sanitizer;
- error reasons are already sanitized by ``ErrorEntry`` and are re-sanitized;
- error source paths are replaced with the existing neutral redaction marker;
- the error table shows only the capped entries supplied by the backend and
  displays the exact total separately.
"""

from __future__ import annotations

from PySide6.QtCore import QRect, QSize, QSortFilterProxyModel, Qt
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from ..events import Finding
from ..report import MAX_REPORTED_ERRORS, RunStatistics, _sanitize
from .backend import AnalysisResult
from .models import (
    ErrorTableModel,
    FindingTableModel,
    SORT_ROLE,
    format_epoch_utc,
    format_finding_summary,
)
from .icon_widgets import ThemeIconLabel
from .theme import FONT_MONO_FAMILIES, severity_colors

__all__ = [
    "DetectionDetail",
    "DetectionsView",
    "EmptyState",
    "ErrorsView",
    "KpiCard",
    "LogExplorerView",
    "OverviewDashboard",
    "SeverityBreakdown",
    "StatisticsPanel",
]


def _label(text: str, object_name: str, *, wrap: bool = False) -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    if wrap:
        label.setWordWrap(True)
    return label


class EmptyState(QFrame):
    """Reusable centered empty-state card."""

    def __init__(
        self,
        icon: str,
        title: str,
        detail: str,
        *,
        min_height: int = 210,
        detail_width: int = 560,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("EmptyState")
        self.setMinimumHeight(min_height)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(8)
        layout.addStretch(1)

        self._icon = ThemeIconLabel(icon, 40, role="accent")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title = _label(title, "EmptyTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail = _label(detail, "EmptyText", wrap=True)
        self._detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._detail.setFixedWidth(detail_width)
        self._detail.setMinimumHeight(40)

        layout.addWidget(self._icon)
        layout.addWidget(self._title, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._detail, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)

    def set_message(self, icon: str, title: str, detail: str) -> None:
        self._icon.set_icon_name(icon)
        self._title.setText(title)
        self._detail.setText(detail)

    @property
    def title_text(self) -> str:
        return self._title.text()

    @property
    def detail_text(self) -> str:
        return self._detail.text()


class KpiCard(QFrame):
    """Compact metric card used by the overview dashboard."""

    def __init__(
        self, title: str, hint: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumHeight(112)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(4)
        self._title = _label(title, "CardTitle")
        self._value = _label("—", "CardValue")
        self._hint = _label(hint, "CardHint", wrap=True)
        layout.addWidget(self._title)
        layout.addWidget(self._value)
        layout.addWidget(self._hint)

    def set_value(self, value) -> None:
        text = f"{value:,}" if type(value) is int else str(value)
        self._value.setText(text)

    def set_hint(self, text: str) -> None:
        self._hint.setText(text)

    @property
    def value_text(self) -> str:
        return self._value.text()

    @property
    def hint_text(self) -> str:
        return self._hint.text()


class SeverityBreakdown(QFrame):
    """High/medium/low count breakdown with compact coloured bars."""

    _ROWS = (
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(10)
        layout.addWidget(_label("Severity breakdown", "SectionHeading"))

        self._counts = {"high": 0, "medium": 0, "low": 0}
        self._count_labels: dict[str, QLabel] = {}
        self._bars: dict[str, QProgressBar] = {}
        self._dots: dict[str, QLabel] = {}

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(7)
        grid.setColumnStretch(3, 1)
        for row, (key, label) in enumerate(self._ROWS):
            dot = QLabel("●")
            self._dots[key] = dot
            grid.addWidget(dot, row, 0)
            grid.addWidget(_label(label, "StatLabel"), row, 1)
            count = _label("0", "StatValue")
            count.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._count_labels[key] = count
            grid.addWidget(count, row, 2)
            bar = QProgressBar()
            bar.setObjectName("SeverityBar")
            bar.setRange(0, 1)
            bar.setValue(0)
            bar.setTextVisible(False)
            self._bars[key] = bar
            grid.addWidget(bar, row, 3)
        layout.addLayout(grid)
        layout.addStretch(1)
        self.refresh_theme()

    def refresh_theme(self) -> None:
        colors = severity_colors()
        for key, _label_text in self._ROWS:
            color = colors.get(key, colors["low"])
            self._dots[key].setStyleSheet(f"color: {color};")
            self._bars[key].setStyleSheet(
                f"QProgressBar#SeverityBar::chunk "
                f"{{ background-color: {color}; border-radius: 2px; }}")

    def set_counts(self, high: int, medium: int, low: int) -> None:
        self._counts = {"high": high, "medium": medium, "low": low}
        total = max(1, high + medium + low)
        for key in ("high", "medium", "low"):
            count = self._counts[key]
            self._count_labels[key].setText(f"{count:,}")
            self._bars[key].setRange(0, total)
            self._bars[key].setValue(count)

    def clear(self) -> None:
        self.set_counts(0, 0, 0)

    @property
    def counts(self) -> dict[str, int]:
        return dict(self._counts)


class StatisticsPanel(QFrame):
    """Detailed scan statistics from the existing ``RunStatistics``."""

    _METRICS = (
        ("files_scanned", "Files scanned"),
        ("lines_read", "Lines read"),
        ("events_parsed", "Events parsed"),
        ("malformed", "Malformed lines"),
        ("duplicates", "Intra-file duplicates"),
        ("othersyslog", "Other syslog lines"),
        ("othersyslog_dropped", "Other syslog dropped"),
        ("cross_file_duplicates", "Cross-file duplicates"),
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(10)
        layout.addWidget(_label("Scan statistics", "SectionHeading"))

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(7)
        self._values: dict[str, QLabel] = {}
        for index, (key, title) in enumerate(self._METRICS):
            row = index // 2
            column = (index % 2) * 2
            grid.addWidget(_label(title, "StatLabel"), row, column)
            value = _label("—", "StatValue")
            value.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._values[key] = value
            grid.addWidget(value, row, column + 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        layout.addLayout(grid)
        layout.addStretch(1)

    def set_statistics(self, statistics: RunStatistics) -> None:
        for key, _title in self._METRICS:
            self._values[key].setText(f"{getattr(statistics, key):,}")

    def clear(self) -> None:
        for value in self._values.values():
            value.setText("—")

    @property
    def values(self) -> dict[str, str]:
        return {key: value.text() for key, value in self._values.items()}


class LogExplorerView(QWidget):
    """Read-only summary of the streamed event pipeline for the latest run.

    The production pipeline intentionally does not retain raw event objects
    after detection. This view therefore presents the existing run
    statistics and points analysts to the sanitized evidence in Detections
    and exported reports instead of implying that a raw event browser exists.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._stack = QStackedWidget()
        self._empty = EmptyState(
            "log_explorer",
            "No parsed event summary yet",
            "Run an analysis to see the streamed event counts and source "
            "context for the latest run.",
            min_height=240,
        )
        self._stack.addWidget(self._empty)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        heading_row = QHBoxLayout()
        heading_row.setContentsMargins(0, 0, 0, 0)
        heading_row.setSpacing(8)
        heading_row.addWidget(_label("Latest completed analysis", "SectionHeading"))
        heading_row.addStretch(1)
        self._status = _label("STREAMED", "ChipAccent")
        heading_row.addWidget(self._status)
        content_layout.addLayout(heading_row)

        self._statistics = StatisticsPanel()
        content_layout.addWidget(self._statistics)

        context = QFrame()
        context.setObjectName("Card")
        context_layout = QVBoxLayout(context)
        context_layout.setContentsMargins(18, 15, 18, 15)
        context_layout.setSpacing(7)
        context_layout.addWidget(_label("Event context", "SectionHeading"))
        self._context = _label(
            "The analysis pipeline streams parsed events into detectors "
            "without retaining the raw event stream. Use Detections for "
            "sanitized evidence and Reports for complete structured exports.",
            "BodyText",
            wrap=True,
        )
        context_layout.addWidget(self._context)
        content_layout.addWidget(context)
        content_layout.addStretch(1)
        self._stack.addWidget(content)
        layout.addWidget(self._stack)

    def set_result(self, result: AnalysisResult) -> None:
        self._statistics.set_statistics(result.statistics)
        self._status.setText("STREAMED · "
                             f"{result.statistics.events_parsed:,} events")
        self._stack.setCurrentIndex(1)

    def clear(self, title: str = "No parsed event summary yet",
              detail: str = "Run an analysis to see the streamed event "
                            "counts and source context for the latest run."
              ) -> None:
        self._statistics.clear()
        self._empty.set_message("log_explorer", title, detail)
        self._stack.setCurrentIndex(0)

    @property
    def stack(self) -> QStackedWidget:
        return self._stack

    @property
    def empty_state(self) -> EmptyState:
        return self._empty

    @property
    def statistics(self) -> StatisticsPanel:
        return self._statistics

    @property
    def context_text(self) -> str:
        return self._context.text()


class ErrorsView(QFrame):
    """Capped, sanitized error table with exact overflow total."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        header.addWidget(_label("Run errors", "SectionHeading"))
        header.addStretch(1)
        self._overflow = _label("No errors recorded", "PanelHint")
        header.addWidget(self._overflow)
        layout.addLayout(header)

        self._model = ErrorTableModel()
        self._proxy = QSortFilterProxyModel(self)
        self._proxy.setSortRole(SORT_ROLE)
        self._proxy.setSourceModel(self._model)
        self._table = QTableView()
        self._table.setObjectName("ErrorTable")
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.setWordWrap(False)
        self._table.verticalHeader().setVisible(False)
        self._table.setMinimumHeight(148)
        self._table.setMaximumHeight(260)
        header_view = self._table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self._table)

        self._empty = _label("No errors to display.", "PanelHint", wrap=True)
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setMinimumHeight(60)
        layout.addWidget(self._empty)

    def set_errors(self, errors, total: int) -> None:
        capped = tuple(errors)[:MAX_REPORTED_ERRORS]
        total = max(total, len(capped))
        self._model.set_errors(capped)
        shown = self._model.rowCount()
        if shown:
            self._table.setFixedHeight(min(260, max(92, 44 + 34 * shown)))
            self._table.show()
            self._empty.hide()
        else:
            self._table.hide()
            self._empty.show()
        if total > shown:
            self._overflow.setText(f"Showing {shown:,} of {total:,} errors")
        elif total:
            self._overflow.setText(
                f"{total:,} error{'' if total == 1 else 's'} recorded")
        else:
            self._overflow.setText("No errors recorded")

    def clear(self) -> None:
        self._model.set_errors(())
        self._table.hide()
        self._empty.show()
        self._empty.setText("No errors to display.")
        self._overflow.setText("No errors recorded")

    @property
    def model(self) -> ErrorTableModel:
        return self._model

    @property
    def proxy(self) -> QSortFilterProxyModel:
        return self._proxy

    @property
    def table(self) -> QTableView:
        return self._table

    @property
    def overflow_text(self) -> str:
        return self._overflow.text()


class EvidenceListWidget(QListWidget):
    """Word-wrapped evidence list with height calculated from real text.

    Qt's default list delegate does not reliably grow rows for wrapped mono
    text after a scrollbar appears. Recomputing each row against the current
    viewport prevents the last words of an evidence line from being clipped.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setUniformItemSizes(False)

    def reflow_items(self) -> None:
        if self.count() == 0:
            return
        metrics_font = QFont()
        metrics_font.setFamilies(list(FONT_MONO_FAMILIES))
        metrics_font.setPixelSize(12)
        metrics = QFontMetrics(metrics_font)
        width = max(120, self.viewport().width() - 24)
        for index in range(self.count()):
            item = self.item(index)
            if item is None:
                continue
            bounds = metrics.boundingRect(
                QRect(0, 0, width, 10_000),
                int(Qt.TextFlag.TextWordWrap),
                item.text(),
            )
            item.setSizeHint(QSize(
                width, max(metrics.height() + 14, bounds.height() + 14)))
        self.doItemsLayout()

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        super().resizeEvent(event)
        self.reflow_items()

    def showEvent(self, event) -> None:  # noqa: N802 - Qt API name
        super().showEvent(event)
        self.reflow_items()


class DetectionDetail(QFrame):
    """Separate panel showing one finding's sanitized details and evidence."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumWidth(300)
        self._current: Finding | None = None
        self._evidence_texts: list[str] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 15, 18, 15)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        header.addWidget(_label("Detection details", "SectionHeading"))
        header.addStretch(1)
        self._severity = _label("", "Chip")
        header.addWidget(self._severity)
        layout.addLayout(header)

        self._stack = QStackedWidget()
        empty = EmptyState(
            "search",
            "Select a detection",
            "Choose a row in the detections table to inspect its summary "
            "and sanitized evidence.",
            min_height=240,
            detail_width=180,
        )
        self._stack.addWidget(empty)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(7)

        self._rule = _label("", "RuleId")
        content_layout.addWidget(self._rule)
        self._source = _label("", "MonoValue")
        content_layout.addWidget(self._source)

        meta = QGridLayout()
        meta.setContentsMargins(0, 0, 0, 0)
        meta.setHorizontalSpacing(12)
        meta.setVerticalSpacing(5)
        self._first_seen = _label("—", "MonoText")
        self._last_seen = _label("—", "MonoText")
        meta.addWidget(_label("First seen", "FieldLabel"), 0, 0)
        meta.addWidget(self._first_seen, 0, 1)
        meta.addWidget(_label("Last seen", "FieldLabel"), 1, 0)
        meta.addWidget(self._last_seen, 1, 1)
        meta.setColumnStretch(1, 1)
        content_layout.addLayout(meta)

        content_layout.addWidget(_label("Summary", "FieldLabel"))
        self._summary = _label("", "BodyText", wrap=True)
        self._summary.setMinimumHeight(38)
        content_layout.addWidget(self._summary)

        evidence_header = QHBoxLayout()
        evidence_header.setContentsMargins(0, 4, 0, 0)
        evidence_header.setSpacing(8)
        evidence_header.addWidget(_label("EVIDENCE", "CardTitle"))
        evidence_header.addStretch(1)
        self._evidence_count = _label("0 lines", "PanelHint")
        evidence_header.addWidget(self._evidence_count)
        content_layout.addLayout(evidence_header)

        self._evidence = EvidenceListWidget()
        self._evidence.setObjectName("EvidenceList")
        self._evidence.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._evidence.setSelectionMode(
            QAbstractItemView.SelectionMode.NoSelection)
        self._evidence.setMinimumHeight(170)
        content_layout.addWidget(self._evidence, 1)
        self._stack.addWidget(content)

        layout.addWidget(self._stack, 1)
        self.clear()

    def show_finding(self, finding: Finding) -> None:
        self._current = finding
        color = severity_colors().get(
            finding.severity, severity_colors()["low"])
        self._severity.setText(finding.severity.upper())
        self._severity.setStyleSheet(
            f"color: {color}; border-color: {color};")
        self._rule.setText(finding.rule_id)
        self._source.setText(finding.src_ip)
        self._first_seen.setText(format_epoch_utc(finding.first_seen))
        self._last_seen.setText(format_epoch_utc(finding.last_seen))
        self._summary.setText(format_finding_summary(finding.summary))

        self._evidence.clear()
        self._evidence_texts = []
        for line in finding.evidence:
            safe_line = _sanitize(line)
            self._evidence_texts.append(safe_line)
            item = QListWidgetItem(safe_line)
            item.setToolTip(safe_line)
            self._evidence.addItem(item)
        self._evidence.reflow_items()
        self._evidence_count.setText(
            f"{len(self._evidence_texts):,} line"
            f"{'' if len(self._evidence_texts) == 1 else 's'}")
        self._stack.setCurrentIndex(1)

    def refresh_theme(self) -> None:
        if self._current is not None:
            self.show_finding(self._current)

    def clear(self) -> None:
        self._current = None
        self._evidence_texts = []
        self._evidence.clear()
        self._evidence_count.setText("0 lines")
        self._severity.setText("")
        self._severity.setStyleSheet("")
        self._rule.clear()
        self._source.clear()
        self._first_seen.setText("—")
        self._last_seen.setText("—")
        self._summary.clear()
        self._stack.setCurrentIndex(0)

    @property
    def current_finding(self) -> Finding | None:
        return self._current

    @property
    def summary_text(self) -> str:
        return self._summary.text()

    @property
    def evidence_count_text(self) -> str:
        return self._evidence_count.text()

    @property
    def evidence_texts(self) -> tuple[str, ...]:
        return tuple(self._evidence_texts)

    @property
    def evidence_widget(self) -> QListWidget:
        return self._evidence


class DetectionsView(QWidget):
    """Sortable findings table plus a separate details/evidence panel."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        header.addWidget(_label("Detections", "SectionHeading"))
        self._count = _label("0 detections", "PanelHint")
        header.addWidget(self._count)
        header.addStretch(1)
        self._hint = _label(
            "Run an analysis to populate detections", "PanelHint")
        header.addWidget(self._hint)
        layout.addLayout(header)

        self._stack = QStackedWidget()
        self._empty = EmptyState(
            "detections",
            "No analysis results yet",
            "Select log sources and run an analysis to populate detections.",
        )
        self._stack.addWidget(self._empty)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._model = FindingTableModel()
        self._proxy = QSortFilterProxyModel(self)
        self._proxy.setSortRole(SORT_ROLE)
        self._proxy.setSourceModel(self._model)

        self._table = QTableView()
        self._table.setObjectName("DetectionTable")
        self._table.setModel(self._proxy)
        self._table.setSortingEnabled(True)
        self._table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.setWordWrap(False)
        self._table.verticalHeader().setVisible(False)
        self._table.verticalHeader().setDefaultSectionSize(30)
        header_view = self._table.horizontalHeader()
        for column, width in (
            (0, 80),
            (1, 98),
            (2, 120),
            (3, 152),
            (4, 152),
            (6, 78),
        ):
            header_view.setSectionResizeMode(column, QHeaderView.ResizeMode.Fixed)
            self._table.setColumnWidth(column, width)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self._table.setMinimumWidth(440)
        self._table.selectionModel().selectionChanged.connect(
            self._on_selection_changed)

        self._detail = DetectionDetail()
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setChildrenCollapsible(False)
        self._splitter.addWidget(self._table)
        self._splitter.addWidget(self._detail)
        self._splitter.setStretchFactor(0, 4)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([808, 320])
        content_layout.addWidget(self._splitter)
        self._stack.addWidget(content)
        layout.addWidget(self._stack, 1)

    def _apply_column_layout(self, vertical: bool) -> None:
        """Prioritize the summary column when the view is narrow.

        The evidence count is repeated in the detail panel, so hiding that
        secondary column frees enough width for a readable summary at the
        minimum supported window size.
        """
        self._table.setColumnHidden(6, vertical)

    def resizeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        super().resizeEvent(event)
        # At the minimum window size a horizontal table/detail split leaves
        # too little room for all fixed finding columns. Stacking the detail
        # panel below the table keeps the table readable at narrow widths.
        vertical = self.width() < 1100
        orientation = (Qt.Orientation.Vertical if vertical
                       else Qt.Orientation.Horizontal)
        self._apply_column_layout(vertical)
        if self._splitter.orientation() == orientation:
            return
        self._splitter.setOrientation(orientation)
        if vertical:
            self._detail.setMinimumWidth(0)
            self._detail.evidence_widget.setMinimumHeight(100)
            self._table.setMinimumHeight(150)
            self._splitter.setStretchFactor(0, 3)
            self._splitter.setStretchFactor(1, 2)
            self._splitter.setSizes([220, 280])
        else:
            self._detail.setMinimumWidth(300)
            self._detail.evidence_widget.setMinimumHeight(170)
            self._table.setMinimumHeight(0)
            self._splitter.setStretchFactor(0, 4)
            self._splitter.setStretchFactor(1, 1)
            self._splitter.setSizes([808, 320])

    def set_result(self, result: AnalysisResult) -> None:
        findings = result.findings
        self._model.set_findings(findings)
        count = len(findings)
        self._count.setText(
            f"{count:,} detection{'' if count == 1 else 's'}")
        if count:
            self._hint.setText("Select a row for sanitized evidence")
            self._stack.setCurrentIndex(1)
            self._table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            self._table.selectRow(0)
            self._on_selection_changed()
        else:
            self._hint.setText("No detections for this run")
            self._detail.clear()
            self._empty.set_message(
                "detections",
                "No detections in this run",
                "The analysis completed without triggering any detection "
                "rules. Review the scan statistics and errors for context.",
            )
            self._stack.setCurrentIndex(0)

    def clear(
        self,
        title: str = "No analysis results yet",
        detail: str = "Select log sources and run an analysis to populate detections.",
    ) -> None:
        self._model.set_findings(())
        self._detail.clear()
        self._count.setText("0 detections")
        self._hint.setText("Run an analysis to populate detections")
        self._empty.set_message("detections", title, detail)
        self._stack.setCurrentIndex(0)

    def refresh_theme(self) -> None:
        self._model.refresh_theme()
        self._detail.refresh_theme()

    def _on_selection_changed(self, *_args) -> None:
        selected = self._table.selectionModel().selectedRows()
        if not selected:
            self._detail.clear()
            return
        proxy_index = selected[0]
        source_index = self._proxy.mapToSource(proxy_index)
        finding = self._model.finding_at(source_index.row())
        if finding is None:
            self._detail.clear()
        else:
            self._detail.show_finding(finding)

    @property
    def model(self) -> FindingTableModel:
        return self._model

    @property
    def proxy(self) -> QSortFilterProxyModel:
        return self._proxy

    @property
    def table(self) -> QTableView:
        return self._table

    @property
    def detail(self) -> DetectionDetail:
        return self._detail

    @property
    def splitter(self) -> QSplitter:
        return self._splitter

    @property
    def count_text(self) -> str:
        return self._count.text()

    @property
    def empty_state(self) -> EmptyState:
        return self._empty

    @property
    def stack(self) -> QStackedWidget:
        return self._stack


class OverviewDashboard(QWidget):
    """KPI, severity, statistics, and error summary for one result."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._has_result = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        self._empty = EmptyState(
            "overview",
            "No analysis results yet",
            "Select log sources and run an analysis. KPI cards, severity "
            "breakdown, scan statistics, and sanitized errors will appear "
            "here.",
        )
        self._stack.addWidget(self._empty)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)

        self.events_card = KpiCard("EVENTS PARSED", "Awaiting analysis")
        self.detections_card = KpiCard("DETECTIONS", "No findings yet")
        self.high_card = KpiCard("HIGH SEVERITY", "No high severity findings")
        self.errors_card = KpiCard("ERRORS", "No errors recorded")
        kpi_row = QHBoxLayout()
        kpi_row.setContentsMargins(0, 0, 0, 0)
        kpi_row.setSpacing(14)
        for card in (
            self.events_card,
            self.detections_card,
            self.high_card,
            self.errors_card,
        ):
            kpi_row.addWidget(card, 1)
        content_layout.addLayout(kpi_row)

        self.severity = SeverityBreakdown()
        self.statistics = StatisticsPanel()
        details_row = QHBoxLayout()
        details_row.setContentsMargins(0, 0, 0, 0)
        details_row.setSpacing(14)
        details_row.addWidget(self.severity, 1)
        details_row.addWidget(self.statistics, 2)
        content_layout.addLayout(details_row)

        self.errors_view = ErrorsView()
        content_layout.addWidget(self.errors_view)
        self._stack.addWidget(content)
        layout.addWidget(self._stack)

    def set_result(self, result: AnalysisResult) -> None:
        findings = result.findings
        high = sum(1 for finding in findings if finding.severity == "high")
        medium = sum(1 for finding in findings if finding.severity == "medium")
        low = sum(1 for finding in findings if finding.severity == "low")
        statistics = result.statistics

        self.events_card.set_value(statistics.events_parsed)
        self.events_card.set_hint(
            f"{statistics.files_scanned:,} file"
            f"{'' if statistics.files_scanned == 1 else 's'} scanned")
        self.detections_card.set_value(len(findings))
        self.detections_card.set_hint(
            f"{medium:,} medium · {low:,} low")
        self.high_card.set_value(high)
        self.high_card.set_hint(
            "High severity findings" if high else "No high severity findings")
        self.errors_card.set_value(result.errors_total)
        self.errors_card.set_hint(
            "Sanitized diagnostics" if result.errors_total
            else "No errors recorded")

        self.severity.set_counts(high, medium, low)
        self.statistics.set_statistics(statistics)
        self.errors_view.set_errors(result.errors, result.errors_total)
        self._has_result = True
        self._stack.setCurrentIndex(1)

    def clear(
        self,
        title: str = "No analysis results yet",
        detail: str = (
            "Select log sources and run an analysis. KPI cards, severity "
            "breakdown, scan statistics, and sanitized errors will appear "
            "here."
        ),
    ) -> None:
        self._has_result = False
        for card in (
            self.events_card,
            self.detections_card,
            self.high_card,
            self.errors_card,
        ):
            card.set_value("—")
        self.events_card.set_hint("Awaiting analysis")
        self.detections_card.set_hint("No findings yet")
        self.high_card.set_hint("No high severity findings")
        self.errors_card.set_hint("No errors recorded")
        self.severity.clear()
        self.statistics.clear()
        self.errors_view.clear()
        self._empty.set_message("overview", title, detail)
        self._stack.setCurrentIndex(0)

    def refresh_theme(self) -> None:
        self.severity.refresh_theme()

    @property
    def has_result(self) -> bool:
        return self._has_result

    @property
    def empty_state(self) -> EmptyState:
        return self._empty

    @property
    def stack(self) -> QStackedWidget:
        return self._stack
