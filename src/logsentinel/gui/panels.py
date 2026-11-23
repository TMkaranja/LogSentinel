"""Input selection and configuration panels for the LogSentinel GUI.

This module provides the setup surface: selecting log sources and editing
detection settings. Analysis execution, worker lifecycle, report export, and
detector wiring are owned by the other GUI modules.

Configuration semantics deliberately preserve the existing precedence chain
(explicit overrides > JSON file > persistent application defaults > built-in
defaults):

- the panel tracks which fields the user has actually edited;
- only edited fields become overrides;
- loading a JSON file validates it with ``config.load_config`` and displays
  the effective values, clearing all override state;
- untouched fields continue to inherit the JSON file, saved application
  defaults, or built-in defaults.

Input selection delegates filesystem validation and discovery to
``inputs.discover_inputs``. The panel stores the user-selected paths (not the
expanded file list), so a later analysis step can pass exactly those paths to
the existing pipeline.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..config import CONFIG_KEYS, DEFAULTS, AppConfig, load_config
from ..events import ErrorEntry
from ..exceptions import ConfigError
from ..inputs import LogFile, discover_inputs
from ..report import _sanitize
from .icon_widgets import ThemeIconButton

__all__ = [
    "ConfigPanel",
    "InputAddOutcome",
    "InputPanel",
]


@dataclass(frozen=True, slots=True)
class InputAddOutcome:
    """Result of one programmatic input-add operation."""

    accepted: tuple[str, ...] = ()
    duplicates: tuple[str, ...] = ()
    rejected: tuple[tuple[str, str], ...] = ()


def _normalise_path(raw: str | os.PathLike[str]) -> str:
    """Return an absolute, normalised path string, never resolving symlinks."""
    if isinstance(raw, bytes):
        raise ValueError("bytes paths are not supported")
    try:
        value = os.fspath(raw)
    except TypeError as exc:
        raise ValueError(f"unsupported path type: {type(raw).__name__}") from exc
    if not isinstance(value, str) or not value.strip():
        raise ValueError("path must be a non-empty string")
    expanded = os.path.expanduser(value.strip())
    return os.path.abspath(os.path.normpath(expanded))


def _path_key(path: str) -> str:
    """Deduplication key: case-normalised on Windows, exact on POSIX."""
    return os.path.normcase(path)


def _field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("FieldLabel")
    return label


def _hint(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("FieldHint")
    label.setWordWrap(True)
    return label


def _button(
    text: str,
    *,
    primary: bool = False,
    icon_name: str | None = None,
    role: str = "muted",
) -> QPushButton:
    if icon_name is None:
        button: QPushButton = QPushButton(text)
    else:
        button = ThemeIconButton(text, icon_name, role=role)
    button.setObjectName("PrimaryButton" if primary else "GhostButton")
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setMinimumHeight(36)
    return button


class InputPanel(QFrame):
    """Card for adding, listing, and removing log sources."""

    inputs_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumWidth(380)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._paths: list[str] = []
        self._keys: set[str] = set()
        self._discovered: tuple[LogFile, ...] = ()
        self._discovery_errors: tuple[ErrorEntry, ...] = ()
        self._last_outcome = InputAddOutcome()
        self._max_file_mb = int(DEFAULTS["max_file_mb"])

        self._build_ui()
        self._update_empty_state()

    # -- public API --------------------------------------------------------

    @property
    def selected_paths(self) -> tuple[str, ...]:
        """Selected source paths in insertion order (directories unexpanded)."""
        return tuple(self._paths)

    @property
    def discovered_files(self) -> tuple[LogFile, ...]:
        """Files returned by the most recent ``discover_inputs`` preview."""
        return self._discovered

    @property
    def discovery_errors(self) -> tuple[ErrorEntry, ...]:
        """Discovery problems from the most recent preview, as data."""
        return self._discovery_errors

    @property
    def last_outcome(self) -> InputAddOutcome:
        """Outcome of the most recent ``add_paths`` call."""
        return self._last_outcome

    @property
    def max_file_mb(self) -> int:
        """Effective discovery size cap supplied by the configuration panel."""
        return self._max_file_mb

    def set_max_file_mb(self, value: int) -> None:
        """Update the discovery size cap and refresh the preview if needed."""
        if type(value) is not int or value <= 0:
            raise ValueError("max_file_mb must be a positive integer")
        if value == self._max_file_mb:
            return
        self._max_file_mb = value
        if self._paths:
            self.refresh_preview()

    @property
    def feedback_text(self) -> str:
        return self._feedback.text()

    @property
    def summary_text(self) -> str:
        return self._summary.text()

    def add_paths(
        self, paths: Iterable[str | os.PathLike[str]]
    ) -> InputAddOutcome:
        """Add paths, rejecting invalid inputs and exact duplicates."""
        if isinstance(paths, (str, bytes, os.PathLike)):
            paths = [paths]
        accepted: list[str] = []
        duplicates: list[str] = []
        rejected: list[tuple[str, str]] = []

        for raw in paths:
            try:
                candidate = _normalise_path(raw)
            except (OSError, TypeError, ValueError) as exc:
                rejected.append((str(raw), f"invalid path: {exc}"))
                continue
            key = _path_key(candidate)
            if key in self._keys:
                duplicates.append(candidate)
                continue

            result = discover_inputs(
                [candidate], max_file_mb=self._max_file_mb)
            if result.errors and not result.files:
                rejected.append((candidate, result.errors[0].reason))
                continue

            self._keys.add(key)
            self._paths.append(candidate)
            accepted.append(candidate)

        self._last_outcome = InputAddOutcome(
            accepted=tuple(accepted),
            duplicates=tuple(duplicates),
            rejected=tuple(rejected),
        )

        if accepted:
            self._reload_list()
            self.refresh_preview()
            self._update_empty_state()
            self.inputs_changed.emit()

        self._set_outcome_feedback(
            accepted=len(accepted),
            duplicates=len(duplicates),
            rejected=rejected,
        )
        return self._last_outcome

    def remove_selected(self) -> tuple[str, ...]:
        """Remove currently selected list entries."""
        selected = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self._list.selectedItems()
        ]
        return self.remove_paths(selected)

    def remove_paths(
        self, paths: Iterable[str | os.PathLike[str]]
    ) -> tuple[str, ...]:
        """Remove paths by value; returns the paths actually removed."""
        if isinstance(paths, (str, bytes, os.PathLike)):
            paths = [paths]
        keys: set[str] = set()
        for raw in paths:
            try:
                keys.add(_path_key(_normalise_path(raw)))
            except (OSError, TypeError, ValueError):
                continue
        if not keys:
            return ()

        kept_paths: list[str] = []
        kept_keys: set[str] = set()
        removed: list[str] = []
        for path in self._paths:
            if _path_key(path) in keys:
                removed.append(path)
            else:
                kept_paths.append(path)
                kept_keys.add(_path_key(path))
        if not removed:
            return ()

        self._paths = kept_paths
        self._keys = kept_keys
        self._reload_list()
        self.refresh_preview()
        self._update_empty_state()
        self._set_feedback(
            f"Removed {len(removed)} input source"
            f"{'' if len(removed) == 1 else 's'}.", "muted")
        self.inputs_changed.emit()
        return tuple(removed)

    def clear(self) -> None:
        """Remove every selected source."""
        had_paths = bool(self._paths)
        self._paths.clear()
        self._keys.clear()
        self._discovered = ()
        self._discovery_errors = ()
        self._last_outcome = InputAddOutcome()
        self._reload_list()
        self.refresh_preview()
        self._update_empty_state()
        self._set_feedback(
            "All inputs cleared." if had_paths else "No inputs selected.",
            "muted")
        if had_paths:
            self.inputs_changed.emit()

    def refresh_preview(self) -> None:
        """Re-run discovery over the selected paths and update the summary."""
        if not self._paths:
            self._discovered = ()
            self._discovery_errors = ()
            self._summary.setText("No input sources selected")
            return
        result = discover_inputs(
            self._paths, max_file_mb=self._max_file_mb)
        self._discovered = tuple(result.files)
        self._discovery_errors = tuple(result.errors)
        source_count = len(self._paths)
        file_count = len(result.files)
        summary = (
            f"{source_count} source{'' if source_count == 1 else 's'} · "
            f"{file_count} log file{'' if file_count == 1 else 's'}"
        )
        if result.errors:
            summary += (
                f" · {len(result.errors)} discovery "
                f"issue{'' if len(result.errors) == 1 else 's'}")
        self._summary.setText(summary)

    def browse_files(self) -> None:
        """Open a multi-file picker and add the chosen files."""
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Add log files",
            "",
            "Log files (*.log *.txt);;All files (*)",
        )
        if paths:
            self.add_paths(paths)

    def browse_directory(self) -> None:
        """Open a directory picker and add the chosen directory."""
        path = QFileDialog.getExistingDirectory(
            self, "Add a log directory", "")
        if path:
            self.add_paths([path])

    # -- UI ----------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        eyebrow = QLabel("INPUT SOURCES")
        eyebrow.setObjectName("CardTitle")
        header.addWidget(eyebrow)
        header.addStretch(1)
        chip = QLabel("READ-ONLY")
        chip.setObjectName("ChipAccent")
        header.addWidget(chip)
        layout.addLayout(header)

        title = QLabel("Log files and folders")
        title.setObjectName("SectionHeading")
        layout.addWidget(title)
        description = QLabel(
            "Add specific log files or a directory. Directories are scanned "
            "for non-hidden .log and .txt files using the existing rules.")
        description.setObjectName("PanelHint")
        description.setWordWrap(True)
        layout.addWidget(description)

        add_row = QHBoxLayout()
        add_row.setContentsMargins(0, 2, 0, 0)
        add_row.setSpacing(8)
        add_files = _button("Add Files", primary=True, icon_name="file_plus", role="accent_text")
        add_files.setToolTip("Add one or more explicit log files")
        add_files.clicked.connect(self.browse_files)
        add_folder = _button("Add Folder", icon_name="folder_open", role="text")
        add_folder.setToolTip("Add a directory for recursive log discovery")
        add_folder.clicked.connect(self.browse_directory)
        add_row.addWidget(add_files)
        add_row.addWidget(add_folder)
        add_row.addStretch(1)
        layout.addLayout(add_row)

        self._list = QListWidget()
        self._list.setObjectName("InputList")
        self._list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection)
        self._list.setMinimumHeight(170)
        self._list.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self._list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self._list, 1)

        self._empty = QLabel(
            "No inputs selected.\nAdd log files or a folder to begin.")
        self._empty.setObjectName("PanelEmpty")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setWordWrap(True)
        self._empty.setMinimumHeight(170)
        layout.addWidget(self._empty, 1)

        remove_row = QHBoxLayout()
        remove_row.setContentsMargins(0, 0, 0, 0)
        remove_row.setSpacing(8)
        remove = _button("Remove Selected", icon_name="trash")
        remove.setToolTip("Remove the selected input paths")
        remove.clicked.connect(self.remove_selected)
        clear = _button("Clear All", icon_name="x")
        clear.setToolTip("Remove every selected input path")
        clear.clicked.connect(self.clear)
        remove_row.addWidget(remove)
        remove_row.addWidget(clear)
        remove_row.addStretch(1)
        layout.addLayout(remove_row)

        self._summary = QLabel("No input sources selected")
        self._summary.setObjectName("PanelHint")
        layout.addWidget(self._summary)

        self._feedback = QLabel("")
        self._feedback.setObjectName("PanelHint")
        self._feedback.setWordWrap(True)
        layout.addWidget(self._feedback)

    def _reload_list(self) -> None:
        self._list.clear()
        for path in self._paths:
            item = QListWidgetItem(path)
            item.setData(Qt.ItemDataRole.UserRole, path)
            item.setToolTip(path)
            self._list.addItem(item)

    def _update_empty_state(self) -> None:
        has_paths = bool(self._paths)
        self._list.setVisible(has_paths)
        self._empty.setVisible(not has_paths)

    def _set_outcome_feedback(
        self,
        *,
        accepted: int,
        duplicates: int,
        rejected: list[tuple[str, str]],
    ) -> None:
        if rejected:
            reason = rejected[0][1]
            extra = (
                f" and {len(rejected) - 1} more"
                if len(rejected) > 1 else "")
            self._set_feedback(
                f"Input rejected{extra}: {_sanitize(reason)}", "error")
            return
        if accepted and duplicates:
            self._set_feedback(
                f"Added {accepted}; skipped {duplicates} duplicate"
                f"{'' if duplicates == 1 else 's'}.", "success")
            return
        if accepted:
            self._set_feedback(
                f"Added {accepted} input source"
                f"{'' if accepted == 1 else 's'}.", "success")
            return
        if duplicates:
            self._set_feedback(
                f"Already selected: {duplicates} duplicate"
                f"{'' if duplicates == 1 else 's'} skipped.", "muted")
            return
        self._set_feedback("No paths were added.", "muted")

    def _set_feedback(self, text: str, kind: str) -> None:
        names = {
            "muted": "PanelHint",
            "success": "PanelSuccess",
            "error": "PanelError",
        }
        object_name = names[kind]
        if self._feedback.objectName() != object_name:
            self._feedback.setObjectName(object_name)
            self._feedback.style().unpolish(self._feedback)
            self._feedback.style().polish(self._feedback)
        self._feedback.setText(text)


class ConfigPanel(QFrame):
    """Card for detection thresholds and JSON configuration loading."""

    configuration_changed = Signal()

    _FIELD_ORDER = (
        "ssh_threshold",
        "ssh_window_seconds",
        "portscan_threshold",
        "http_4xx_threshold",
    )

    _FIELD_LABELS = {
        "ssh_threshold": "SSH failure threshold",
        "ssh_window_seconds": "SSH detection window (s)",
        "portscan_threshold": "Port-scan threshold",
        "http_4xx_threshold": "HTTP 4xx threshold",
    }

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        analysis_defaults: dict[str, object] | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumWidth(330)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._config_path: str | None = None
        self._analysis_defaults = dict(analysis_defaults or {})
        self._effective_config = load_config(
            None, None, defaults=self._analysis_defaults)
        self._dirty: set[str] = set()
        self._updating = False
        self._spins: dict[str, QSpinBox] = {}

        self._build_ui()
        self._apply_effective(self._effective_config)
        self._set_feedback(self._defaults_feedback_text(), "muted")

    # -- public API --------------------------------------------------------

    @property
    def config_path(self) -> str | None:
        return self._config_path

    @property
    def dirty_keys(self) -> tuple[str, ...]:
        return tuple(key for key in CONFIG_KEYS if key in self._dirty)

    @property
    def analysis_defaults(self) -> dict[str, object]:
        return dict(self._analysis_defaults)

    @property
    def feedback_text(self) -> str:
        return self._feedback.text()

    def overrides(self) -> dict[str, object]:
        """Only user-edited fields, suitable for ``load_config`` overrides."""
        result: dict[str, object] = {}
        for key in self._FIELD_ORDER:
            if key in self._dirty:
                result[key] = self._spins[key].value()
        if "strict" in self._dirty:
            result["strict"] = self._strict.isChecked()
        return result

    def effective_config(self) -> AppConfig:
        """Validate and return the combined configuration.

        Raises ``ConfigError`` if the selected JSON file is no longer valid
        or an override is invalid. Untouched fields inherit the JSON file or
        built-in defaults because they are absent from ``overrides``.
        """
        return load_config(
            self.overrides(), self._config_path,
            defaults=self._analysis_defaults)

    def apply_configuration(self) -> AppConfig | None:
        """Validate the effective configuration and report the result."""
        try:
            config = self.effective_config()
        except ConfigError as exc:
            self._set_feedback(_sanitize(str(exc)), "error")
            return None
        self._effective_config = config
        self._set_feedback("Configuration valid.", "success")
        self.configuration_changed.emit()
        return config

    def load_config_file(self, path: str | os.PathLike[str]) -> bool:
        """Validate and load a JSON configuration file.

        The file is accepted only after ``load_config`` succeeds. On failure
        the current configuration and field values stay unchanged.
        """
        candidate = str(path).strip()
        if not candidate:
            self.clear_config_file()
            return True
        try:
            effective = load_config(
                {}, candidate, defaults=self._analysis_defaults)
        except ConfigError as exc:
            self._set_feedback(_sanitize(str(exc)), "error")
            return False

        self._config_path = candidate
        self._config_edit.setText(candidate)
        self._apply_effective(effective)
        name = Path(candidate).name or candidate
        self._set_feedback(
            f"Loaded {name}. Only edited fields will override it.", "success")
        self.configuration_changed.emit()
        return True

    def clear_config_file(self) -> None:
        """Remove the JSON file and restore built-in defaults."""
        self._config_path = None
        self._config_edit.clear()
        self._apply_effective(load_config(
            None, None, defaults=self._analysis_defaults))
        self._set_feedback(self._defaults_feedback_text(), "muted")
        self.configuration_changed.emit()

    def reset_overrides(self) -> bool:
        """Discard local edits and reload the selected JSON/default state."""
        try:
            effective = load_config(
                {}, self._config_path, defaults=self._analysis_defaults)
        except ConfigError as exc:
            self._set_feedback(_sanitize(str(exc)), "error")
            return False
        self._apply_effective(effective)
        self._set_feedback("Overrides cleared.", "muted")
        self.configuration_changed.emit()
        return True

    def set_analysis_defaults(
        self, analysis_defaults: dict[str, object] | None
    ) -> bool:
        """Replace persistent defaults used as the base config layer.

        Existing per-analysis field edits remain explicit overrides. The
        settings are applied to future analyses; an already-running worker
        owns an immutable request snapshot.
        """
        previous = self._analysis_defaults
        self._analysis_defaults = dict(analysis_defaults or {})
        try:
            effective = self.effective_config()
        except ConfigError as exc:
            self._analysis_defaults = previous
            self._set_feedback(_sanitize(str(exc)), "error")
            return False
        self._apply_effective(effective, clear_dirty=False)
        self._set_feedback("Application defaults updated.", "muted")
        self.configuration_changed.emit()
        return True

    def set_override(self, key: str, value: object) -> None:
        """Set one field and mark it as an explicit override (tests/API)."""
        if key == "strict":
            if type(value) is not bool:
                raise ValueError("strict must be a boolean")
            self._strict.setChecked(value)
        elif key in self._spins:
            if type(value) is not int or value <= 0:
                raise ValueError(f"{key} must be a positive integer")
            self._spins[key].setValue(value)
        else:
            raise ValueError(f"unsupported configuration field: {key!r}")
        self._mark_dirty(key)

    # -- UI ----------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        eyebrow = QLabel("DETECTION CONFIGURATION")
        eyebrow.setObjectName("CardTitle")
        header.addWidget(eyebrow)
        header.addStretch(1)
        chip = QLabel("VALIDATED")
        chip.setObjectName("ChipAccent")
        header.addWidget(chip)
        layout.addLayout(header)

        title = QLabel("Analysis settings")
        title.setObjectName("SectionHeading")
        layout.addWidget(title)
        description = QLabel(
            "Only fields you edit override the loaded JSON file. Untouched "
            "fields keep their JSON or built-in values.")
        description.setObjectName("PanelHint")
        description.setWordWrap(True)
        layout.addWidget(description)

        config_label = _field_label("JSON configuration")
        layout.addWidget(config_label)
        config_row = QHBoxLayout()
        config_row.setContentsMargins(0, 0, 0, 0)
        config_row.setSpacing(8)
        self._config_edit = QLineEdit()
        self._config_edit.setObjectName("ConfigPathEdit")
        self._config_edit.setPlaceholderText("Path")
        self._config_edit.setToolTip(
            "Optional JSON configuration file; leave empty for built-ins")
        self._config_edit.editingFinished.connect(
            self._on_config_edit_finished)
        browse = _button("Browse", icon_name="folder_open")
        browse.setToolTip("Validate and load a JSON configuration file")
        browse.clicked.connect(self._browse_config)
        clear = _button("Clear", icon_name="x")
        clear.setToolTip("Return to built-in defaults")
        clear.clicked.connect(self.clear_config_file)
        config_row.addWidget(self._config_edit, 1)
        config_row.addWidget(browse)
        config_row.addWidget(clear)
        layout.addLayout(config_row)

        form = QFormLayout()
        form.setContentsMargins(0, 4, 0, 0)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(9)
        form.setLabelAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        for key in self._FIELD_ORDER:
            spin = QSpinBox()
            spin.setObjectName(f"{key}_spin")
            spin.setRange(1, 2_147_483_647)
            spin.setAccelerated(True)
            spin.setKeyboardTracking(False)
            spin.valueChanged.connect(
                lambda _value, field=key: self._mark_dirty(field))
            self._spins[key] = spin
            label = _field_label(self._FIELD_LABELS[key])
            form.addRow(label, spin)

        self._strict = QCheckBox("Abort on first error")
        self._strict.setObjectName("StrictModeCheck")
        self._strict.setToolTip(
            "Strict mode: abort on the first recorded input or parse error")
        self._strict.toggled.connect(
            lambda _checked: self._mark_dirty("strict"))
        strict_label = _field_label("Strict mode")
        form.addRow(strict_label, self._strict)
        layout.addLayout(form)

        note = QLabel(
            "Configuration is validated with the same rules as the CLI. "
            "Apply updates the next analysis; a running analysis keeps its "
            "immutable request snapshot.")
        note.setObjectName("PanelHint")
        note.setWordWrap(True)
        layout.addWidget(note)

        self._feedback = QLabel("")
        self._feedback.setObjectName("PanelHint")
        self._feedback.setWordWrap(True)
        layout.addWidget(self._feedback)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(8)
        reset = _button("Reset Overrides", icon_name="x")
        reset.setToolTip("Discard field edits and restore the loaded values")
        reset.clicked.connect(self.reset_overrides)
        apply_button = _button("Apply", primary=True, icon_name="check", role="accent_text")
        apply_button.setToolTip("Validate the combined configuration")
        apply_button.clicked.connect(self.apply_configuration)
        action_row.addWidget(reset)
        action_row.addStretch(1)
        action_row.addWidget(apply_button)
        layout.addLayout(action_row)

    def _on_config_edit_finished(self) -> None:
        text = self._config_edit.text().strip()
        if not text:
            if self._config_path is not None:
                self.clear_config_file()
            return
        if text == self._config_path:
            return
        if not self.load_config_file(text):
            self._config_edit.setText(self._config_path or "")

    def _browse_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load JSON configuration",
            "",
            "JSON configuration (*.json);;All files (*)",
        )
        if path and not self.load_config_file(path):
            self._config_edit.setText(self._config_path or "")

    def _apply_effective(
        self, config: AppConfig, *, clear_dirty: bool = True
    ) -> None:
        self._updating = True
        try:
            for key in self._FIELD_ORDER:
                self._spins[key].setValue(getattr(config, key))
            self._strict.setChecked(config.strict)
        finally:
            self._updating = False
        if clear_dirty:
            self._dirty.clear()
        self._effective_config = config

    def _defaults_feedback_text(self) -> str:
        if self._analysis_defaults:
            return "Using application defaults."
        return "Using built-in defaults."

    def _mark_dirty(self, key: str) -> None:
        if self._updating:
            return
        self._dirty.add(key)
        self._set_feedback(
            "Field override pending. Click Apply to validate.", "muted")
        self.configuration_changed.emit()

    def _set_feedback(self, text: str, kind: str) -> None:
        names = {
            "muted": "PanelHint",
            "success": "PanelSuccess",
            "error": "PanelError",
        }
        object_name = names[kind]
        if self._feedback.objectName() != object_name:
            self._feedback.setObjectName(object_name)
            self._feedback.style().unpolish(self._feedback)
            self._feedback.style().polish(self._feedback)
        self._feedback.setText(text)
