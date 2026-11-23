"""Qt table models for the LogSentinel results dashboard.

The models are presentation-only. They consume the existing frozen
``Finding`` and ``ErrorEntry`` objects from ``AnalysisResult`` and never run
detection logic. Every evidence/summary/error string is displayed through the
existing report sanitizer, and error source paths use the existing neutral
redaction marker.
"""

from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QBrush, QColor, QFont

from ..events import ErrorEntry, Finding
from ..report import _REDACTED_PATH, _sanitize
from .theme import FONT_MONO_FAMILIES, severity_colors

__all__ = [
    "ErrorTableModel",
    "FindingTableModel",
    "SORT_ROLE",
    "format_epoch_short",
    "format_epoch_utc",
    "format_finding_summary",
]

#: Custom role used by QSortFilterProxyModel so sorting follows display-> semantic
#: ordering (severity rank, epoch seconds, evidence count, ...).
SORT_ROLE = int(Qt.ItemDataRole.UserRole) + 1

_SEVERITY_RANK = {"critical": -1, "high": 0, "medium": 1, "low": 2}


def format_epoch_utc(timestamp: int) -> str:
    """Format an epoch-second timestamp for detail display in UTC."""
    try:
        moment = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return str(timestamp)
    return moment.strftime("%Y-%m-%d %H:%M:%S UTC")


def format_epoch_short(timestamp: int) -> str:
    """Format an epoch-second timestamp compactly for table columns."""
    try:
        moment = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return str(timestamp)
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def format_finding_summary(summary: dict[str, object]) -> str:
    """Render a finding summary deterministically and sanitize it for display."""
    if not summary:
        return "—"
    parts: list[str] = []
    for key in sorted(summary):
        value = summary[key]
        if isinstance(value, dict):
            inner = ", ".join(
                f"{inner_key}: {inner_value}"
                for inner_key, inner_value in sorted(
                    value.items(), key=lambda item: str(item[0])))
            text = "{" + inner + "}"
        elif isinstance(value, (list, tuple)):
            text = "[" + ", ".join(str(item) for item in value) + "]"
        else:
            text = str(value)
        parts.append(f"{key}={text}")
    return _sanitize(", ".join(parts))


class FindingTableModel(QAbstractTableModel):
    """Sortable table model for detection findings."""

    HEADERS = (
        "Severity",
        "Rule",
        "Source IP",
        "First seen (UTC)",
        "Last seen (UTC)",
        "Summary",
        "Evidence",
    )

    def __init__(self, findings=(), parent=None) -> None:
        super().__init__(parent)
        self._findings: tuple[Finding, ...] = tuple(findings)

    # -- data management ---------------------------------------------------

    @property
    def findings(self) -> tuple[Finding, ...]:
        return self._findings

    def set_findings(self, findings) -> None:
        self.beginResetModel()
        self._findings = tuple(findings)
        self.endResetModel()

    def finding_at(self, row: int) -> Finding | None:
        if 0 <= row < len(self._findings):
            return self._findings[row]
        return None

    def refresh_theme(self) -> None:
        if self._findings:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(len(self._findings) - 1, 0),
                [Qt.ItemDataRole.ForegroundRole],
            )

    # -- QAbstractTableModel ----------------------------------------------

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._findings)

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (orientation == Qt.Orientation.Horizontal
                and role == Qt.ItemDataRole.DisplayRole
                and 0 <= section < len(self.HEADERS)):
            return self.HEADERS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, column = index.row(), index.column()
        if not 0 <= row < len(self._findings):
            return None
        finding = self._findings[row]
        summary_text = format_finding_summary(finding.summary)
        evidence_count = len(finding.evidence)

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return finding.severity.capitalize()
            if column == 1:
                return finding.rule_id
            if column == 2:
                return finding.src_ip
            if column == 3:
                return format_epoch_short(finding.first_seen)
            if column == 4:
                return format_epoch_short(finding.last_seen)
            if column == 5:
                return summary_text
            if column == 6:
                return f"{evidence_count} line{'' if evidence_count == 1 else 's'}"

        if role == Qt.ItemDataRole.ToolTipRole:
            if column == 3:
                return format_epoch_utc(finding.first_seen)
            if column == 4:
                return format_epoch_utc(finding.last_seen)
            if column == 5:
                return summary_text
            if column == 6:
                return "Select the row to view sanitized evidence."
            return self.data(index, Qt.ItemDataRole.DisplayRole)

        if role == SORT_ROLE:
            if column == 0:
                return _SEVERITY_RANK.get(finding.severity, 99)
            if column == 1:
                return finding.rule_id
            if column == 2:
                return finding.src_ip
            if column == 3:
                return finding.first_seen
            if column == 4:
                return finding.last_seen
            if column == 5:
                return summary_text
            if column == 6:
                return evidence_count

        if role == Qt.ItemDataRole.ForegroundRole and column == 0:
            colors = severity_colors()
            return QBrush(QColor(colors.get(finding.severity, colors["low"])))

        if role == Qt.ItemDataRole.FontRole:
            if column in (2, 3, 4):
                font = QFont()
                font.setFamilies(list(FONT_MONO_FAMILIES))
                font.setPixelSize(12)
                font.setStyleHint(QFont.StyleHint.Monospace)
                return font
            if column == 0:
                font = QFont()
                font.setBold(True)
                return font

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column in (3, 4, 6):
                return int(
                    Qt.AlignmentFlag.AlignRight
                    | Qt.AlignmentFlag.AlignVCenter)
        return None


class ErrorTableModel(QAbstractTableModel):
    """Sortable table model for sanitized error entries."""

    HEADERS = ("Kind", "Line", "Reason", "Source")

    def __init__(self, errors=(), parent=None) -> None:
        super().__init__(parent)
        self._errors: tuple[ErrorEntry, ...] = tuple(errors)

    @property
    def errors(self) -> tuple[ErrorEntry, ...]:
        return self._errors

    def set_errors(self, errors) -> None:
        self.beginResetModel()
        self._errors = tuple(errors)
        self.endResetModel()

    def error_at(self, row: int) -> ErrorEntry | None:
        if 0 <= row < len(self._errors):
            return self._errors[row]
        return None

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._errors)

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (orientation == Qt.Orientation.Horizontal
                and role == Qt.ItemDataRole.DisplayRole
                and 0 <= section < len(self.HEADERS)):
            return self.HEADERS[section]
        return None

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, column = index.row(), index.column()
        if not 0 <= row < len(self._errors):
            return None
        entry = self._errors[row]
        reason = _sanitize(entry.reason)
        line = "—" if entry.line_number is None else str(entry.line_number)

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ToolTipRole):
            if column == 0:
                return entry.kind
            if column == 1:
                return line
            if column == 2:
                return reason
            if column == 3:
                return _REDACTED_PATH

        if role == SORT_ROLE:
            if column == 0:
                return entry.kind
            if column == 1:
                return -1 if entry.line_number is None else entry.line_number
            if column == 2:
                return reason
            if column == 3:
                return _REDACTED_PATH

        if role == Qt.ItemDataRole.FontRole and column in (1, 3):
            font = QFont()
            font.setFamilies(list(FONT_MONO_FAMILIES))
            font.setPixelSize(12)
            font.setStyleHint(QFont.StyleHint.Monospace)
            return font

        if role == Qt.ItemDataRole.TextAlignmentRole and column == 1:
            return int(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return None
