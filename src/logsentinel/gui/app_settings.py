"""Persistent GUI application settings.

This module stores interface preferences and a persistent analysis-default
layer. Analysis values are validated with the existing
:func:`logsentinel.config.load_config` validator; the GUI does not implement
a second configuration format.

Precedence used by the GUI is:

    built-in defaults < saved application defaults < selected JSON config <
    temporary per-analysis field overrides

The CLI keeps its existing three-layer behavior because it never passes the
optional ``defaults`` argument to ``load_config``.

The settings file deliberately contains no log paths, credentials, findings,
or raw log content. Window geometry is stored as opaque base64 text produced
by Qt, and the analysis section contains only the existing supported keys.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from ..config import load_config
from ..exceptions import ConfigError
from .themes import DEFAULT_THEME_KEY, THEME_KEYS

__all__ = [
    "DEFAULT_EXPORT_FORMAT",
    "EXPORT_FORMATS",
    "PAGE_KEYS",
    "PAGE_LABELS",
    "SETTINGS_VERSION",
    "SUPPORTED_THEMES",
    "AppSettings",
    "SettingsError",
    "SettingsLoadResult",
    "SettingsStore",
    "default_settings_path",
]

SETTINGS_VERSION = 1
THEME_DARK = DEFAULT_THEME_KEY
SUPPORTED_THEMES = THEME_KEYS
DEFAULT_EXPORT_FORMAT = "json"
EXPORT_FORMATS = ("json", "html")

PAGE_LABELS: dict[str, str] = {
    "overview": "Overview",
    "detections": "Detections",
    "log_explorer": "Log Explorer",
    "reports": "Reports",
    "settings": "Settings",
}
PAGE_KEYS = tuple(PAGE_LABELS)

_SETTINGS_FILENAME = "settings.json"


class SettingsError(RuntimeError):
    """Raised when settings cannot be persisted safely."""


@dataclass(frozen=True, slots=True)
class SettingsLoadResult:
    """Loaded settings plus an optional user-safe warning."""

    settings: AppSettings
    warning: str | None = None


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Validated persistent application settings."""

    remember_window_state: bool = True
    restore_last_page: bool = True
    startup_page: str = "overview"
    theme: str = DEFAULT_THEME_KEY
    analysis_defaults: dict[str, object] = field(default_factory=dict)
    default_export_format: str = DEFAULT_EXPORT_FORMAT
    window_geometry: str = ""
    window_state: str = ""
    last_page: str = "overview"

    def __post_init__(self) -> None:
        for name in ("remember_window_state", "restore_last_page"):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be a boolean")
        if self.startup_page not in PAGE_KEYS:
            raise ValueError(f"unsupported startup page: {self.startup_page!r}")
        if self.last_page not in PAGE_KEYS:
            raise ValueError(f"unsupported last page: {self.last_page!r}")
        if self.theme not in SUPPORTED_THEMES:
            raise ValueError(f"unsupported theme: {self.theme!r}")
        if self.default_export_format not in EXPORT_FORMATS:
            raise ValueError(
                f"unsupported default export format: "
                f"{self.default_export_format!r}")
        if not isinstance(self.analysis_defaults, dict):
            raise ValueError("analysis_defaults must be a mapping")
        for name in ("window_geometry", "window_state"):
            if not isinstance(getattr(self, name), str):
                raise ValueError(f"{name} must be a string")
        try:
            load_config(dict(self.analysis_defaults), None)
        except ConfigError as exc:
            raise ValueError(str(exc)) from None
        object.__setattr__(
            self, "analysis_defaults", dict(self.analysis_defaults))

    @classmethod
    def defaults(cls) -> "AppSettings":
        """Return built-in application settings (analysis inherits defaults)."""
        return cls()


def default_settings_path() -> Path:
    """Return the platform-appropriate per-user settings file path."""
    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        root = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        config_home = os.environ.get("XDG_CONFIG_HOME")
        root = Path(config_home) if config_home else Path.home() / ".config"
    return root / "LogSentinel" / _SETTINGS_FILENAME


_DEFAULT_PATH = object()


class SettingsStore:
    """Read and atomically write the GUI settings file.

    ``path=None`` creates an in-memory store, which keeps the existing test
    suite and embedders free of side effects. The production entry point
    passes the default platform path.
    """

    def __init__(
        self,
        path: str | Path | None | object = _DEFAULT_PATH,
    ) -> None:
        if path is _DEFAULT_PATH:
            self._path = default_settings_path()
        elif path is None:
            self._path = None
        else:
            self._path = Path(path).expanduser()
        self._memory: AppSettings | None = None

    @property
    def path(self) -> Path | None:
        return self._path

    def load(self) -> SettingsLoadResult:
        """Load settings, falling back safely on missing or invalid files."""
        if self._path is None:
            return SettingsLoadResult(
                self._memory or AppSettings.defaults())
        path = self._path
        try:
            raw = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return SettingsLoadResult(AppSettings.defaults())
        except (OSError, UnicodeError):
            return SettingsLoadResult(
                AppSettings.defaults(),
                "Settings could not be read; defaults are in use.",
            )
        try:
            payload = json.loads(raw)
            settings = _settings_from_payload(payload)
        except (ConfigError, TypeError, ValueError, KeyError):
            return SettingsLoadResult(
                AppSettings.defaults(),
                "Settings file is malformed; defaults are in use.",
            )
        return SettingsLoadResult(settings)

    def save(self, settings: AppSettings) -> None:
        """Persist settings atomically; raise ``SettingsError`` on failure."""
        if not isinstance(settings, AppSettings):
            raise TypeError("settings must be an AppSettings instance")
        if self._path is None:
            self._memory = settings
            return

        target = self._path
        directory = target.parent
        tmp_name: str | None = None
        try:
            directory.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(
                prefix=".logsentinel-settings-",
                suffix=".tmp",
                dir=str(directory),
            )
            with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
                json.dump(
                    _settings_payload(settings),
                    handle,
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
                handle.write("\n")
            os.replace(tmp_name, target)
            tmp_name = None
            if os.name != "nt":
                try:
                    os.chmod(target, 0o600)
                except OSError:
                    pass
        except OSError:
            raise SettingsError("Settings could not be saved.") from None
        finally:
            if tmp_name is not None:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass


def _settings_payload(settings: AppSettings) -> dict[str, object]:
    return {
        "version": SETTINGS_VERSION,
        "general": {
            "remember_window_state": settings.remember_window_state,
            "restore_last_page": settings.restore_last_page,
            "startup_page": settings.startup_page,
        },
        "appearance": {
            "theme": settings.theme,
        },
        "analysis_defaults": dict(settings.analysis_defaults),
        "reports": {
            "default_export_format": settings.default_export_format,
        },
        "window": {
            "geometry": settings.window_geometry,
            "state": settings.window_state,
            "last_page": settings.last_page,
        },
    }


def _settings_from_payload(payload: object) -> AppSettings:
    if not isinstance(payload, dict):
        raise ValueError("settings root must be a JSON object")
    version = payload.get("version", SETTINGS_VERSION)
    if version != SETTINGS_VERSION:
        raise ValueError("unsupported settings version")
    general = _section(payload, "general")
    appearance = _section(payload, "appearance")
    analysis_defaults = _section(payload, "analysis_defaults")
    reports = _section(payload, "reports")
    window = _section(payload, "window")
    return AppSettings(
        remember_window_state=general.get(
            "remember_window_state", True),
        restore_last_page=general.get("restore_last_page", True),
        startup_page=general.get("startup_page", "overview"),
        theme=appearance.get("theme", DEFAULT_THEME_KEY),
        analysis_defaults=analysis_defaults,
        default_export_format=reports.get(
            "default_export_format", DEFAULT_EXPORT_FORMAT),
        window_geometry=window.get("geometry", ""),
        window_state=window.get("state", ""),
        last_page=window.get("last_page", "overview"),
    )


def _section(payload: dict, name: str) -> dict:
    value = payload.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"settings section {name!r} must be an object")
    return value
