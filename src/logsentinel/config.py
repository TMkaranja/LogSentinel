"""Application configuration for LogSentinel (Phase 4.2).

Implements docs/ARCHITECTURE.md section 10 (AR-008) and docs/REQUIREMENTS.md
FR-060/FR-061/FR-140/FR-141/FR-142:

- ``DEFAULTS`` is the single source of truth for built-in values.
- Precedence: built-in defaults < JSON configuration file < CLI overrides.
- Only non-``None`` CLI override values replace lower-precedence values.
- Invalid configuration raises :class:`ConfigError` with a useful diagnostic;
  raw JSON-decoding and filesystem exceptions are never leaked (FR-150).

Deterministic and side-effect free apart from reading the requested JSON
file. This module imports only the exception hierarchy (leaf behaviour).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .exceptions import ConfigError

__all__ = ["DEFAULTS", "CONFIG_KEYS", "AppConfig", "load_config"]

#: Supported configuration keys (FR-060). Order is documentation only.
CONFIG_KEYS: tuple[str, ...] = (
    "ssh_threshold",
    "ssh_window_seconds",
    "portscan_threshold",
    "http_4xx_threshold",
    "strict",
    "max_line_length",
    "max_file_mb",
)

#: Built-in defaults (FR-140) - the single source of truth.
DEFAULTS: dict[str, object] = {
    "ssh_threshold": 8,
    "ssh_window_seconds": 300,
    "portscan_threshold": 10,
    "http_4xx_threshold": 8,
    "strict": False,
    "max_line_length": 8192,
    "max_file_mb": 512,
}

#: Keys that must be strictly positive integers (booleans rejected).
_INT_KEYS: frozenset[str] = frozenset(CONFIG_KEYS) - {"strict"}


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Validated, immutable application configuration (AR-008)."""

    ssh_threshold: int = DEFAULTS["ssh_threshold"]
    ssh_window_seconds: int = DEFAULTS["ssh_window_seconds"]
    portscan_threshold: int = DEFAULTS["portscan_threshold"]
    http_4xx_threshold: int = DEFAULTS["http_4xx_threshold"]
    strict: bool = DEFAULTS["strict"]
    max_line_length: int = DEFAULTS["max_line_length"]
    max_file_mb: int = DEFAULTS["max_file_mb"]

    def __post_init__(self) -> None:
        # Defense in depth: direct construction is validated with the same
        # rules as load_config (bools are never valid integers - FR-061).
        for key in _INT_KEYS:
            value = getattr(self, key)
            if type(value) is not int or value <= 0:
                raise ConfigError(
                    f"invalid configuration: {key!r} must be a positive "
                    f"integer, got {value!r}")
        if type(self.strict) is not bool:
            raise ConfigError(
                f"invalid configuration: 'strict' must be a boolean, "
                f"got {type(self.strict).__name__}")


def _validated_value(key: str, value: object, source: str) -> object:
    """Validate one configuration value; raise ConfigError when invalid."""
    if key == "strict":
        if type(value) is not bool:
            raise ConfigError(
                f"{source}: 'strict' must be a boolean, "
                f"got {type(value).__name__}")
        return value
    if key in _INT_KEYS:
        # type() (not isinstance) rejects booleans: bool is a subclass of
        # int, but a boolean is never a valid integer setting (FR-061).
        if type(value) is not int:
            raise ConfigError(
                f"{source}: {key!r} must be a positive integer, "
                f"got {type(value).__name__}")
        if value <= 0:
            raise ConfigError(
                f"{source}: {key!r} must be a positive integer, got {value}")
        return value
    raise ConfigError(f"{source}: unknown configuration key {key!r}")


def _load_json_config(config_path: str | None) -> dict[str, object]:
    """Load and validate a JSON configuration file (FR-060)."""
    if config_path is None:
        return {}
    path = Path(config_path)
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        # A configuration file must be valid UTF-8 text (Phase 4.2 review
        # correction); the raw decoding exception is never leaked.
        raise ConfigError(
            f"configuration file {path!s} is not valid UTF-8 text "
            f"(at byte offset {exc.start})") from None
    except OSError as exc:
        raise ConfigError(
            f"cannot read configuration file {path!s}: "
            f"{exc.__class__.__name__}: {exc.strerror or exc}") from None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"invalid JSON in configuration file {path!s}: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})") from None
    if not isinstance(data, dict):
        raise ConfigError(
            f"configuration root must be a JSON object, "
            f"got {type(data).__name__}")
    unknown = sorted(str(key) for key in data if key not in CONFIG_KEYS)
    if unknown:
        raise ConfigError(
            f"unknown configuration key(s) in {path!s}: {', '.join(unknown)}")
    return {
        str(key): _validated_value(str(key), value, f"configuration file {path!s}")
        for key, value in data.items()
    }


def _validated_overrides(overrides: dict[str, object] | None) -> dict[str, object]:
    """Validate CLI overrides; only non-None values are applied (AR-008)."""
    if overrides is None:
        return {}
    if not isinstance(overrides, dict):
        raise ConfigError("CLI overrides must be a mapping")
    unknown = sorted(str(key) for key in overrides if key not in CONFIG_KEYS)
    if unknown:
        raise ConfigError(f"unknown CLI override key(s): {', '.join(unknown)}")
    return {
        str(key): _validated_value(str(key), value, "CLI overrides")
        for key, value in overrides.items()
        if value is not None
    }


def load_config(
    cli_overrides: dict[str, object] | None,
    config_path: str | None,
) -> AppConfig:
    """Build the effective configuration.

    Precedence (AR-008): built-in defaults < JSON configuration file <
    CLI overrides. Only non-``None`` CLI override values replace
    lower-precedence values. Raises :class:`ConfigError` for any invalid
    input (FR-061).
    """
    merged: dict[str, object] = dict(DEFAULTS)
    merged.update(_load_json_config(config_path))
    merged.update(_validated_overrides(cli_overrides))
    return AppConfig(**{key: merged[key] for key in CONFIG_KEYS})
