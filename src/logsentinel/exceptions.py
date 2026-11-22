"""Application-specific exception hierarchy for LogSentinel.

Contract (docs/REQUIREMENTS.md FR-150, docs/ARCHITECTURE.md section 5):
LogSentinelError is the root; cli.py is the only module that translates these
into exit codes. Per-line/per-file problems are errors-as-data (ErrorEntry),
not exceptions (AR-012).

This module is a leaf: it imports nothing from the application.
"""

from __future__ import annotations


class LogSentinelError(Exception):
    """Base class for all recoverable, anticipated LogSentinel failures."""


class ConfigError(LogSentinelError):
    """Invalid or unknown configuration (FR-060, FR-061)."""


class InputPathError(LogSentinelError):
    """Input path failure in strict mode (FR-100, FR-152)."""


class ParseError(LogSentinelError):
    """Parser-level failure that cannot be recorded as per-line data."""


class ReportError(LogSentinelError):
    """Report target could not be written (FR-041, FR-150)."""
