"""Typed event model for LogSentinel.

Implements docs/ARCHITECTURE.md sections 5 and 8 and
docs/PHASE3_VALIDATION.md section 4:

- Frozen, slotted dataclasses for events and findings (AR-001).
- Canonical time as integer Unix epoch seconds in UTC (AR-002).
- Content-addressed deduplication fingerprints (AR-005, revised Phase 3).
- Construction-time field validation (FR-114); violations raise ValueError.

Canonical event-kind vocabulary (Phase 3 correction F-01):
    authok, authfail, fwconn, web, othersyslog

This module is an I/O-free leaf: it imports only the exception hierarchy.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass, field
from typing import ClassVar

__all__ = [
    "ErrorEntry",
    "FileStats",
    "Finding",
    "SecurityEvent",
    "SSHAuthEvent",
    "FirewallEvent",
    "HTTPRequestEvent",
    "SyslogEvent",
    "fingerprint",
    "dedup_cross_file",
    "events_by_src_ip",
]


# --------------------------------------------------------------------------
# Bookkeeping / reporting structures (Phase 3 section 3 contracts)
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ErrorEntry:
    """A recoverable problem recorded as data (AR-012), never raised per line."""

    source_file: str
    line_number: int | None
    reason: str
    kind: str = "parse"  # one of: config | input | parse | report


@dataclass(frozen=True, slots=True)
class FileStats:
    """Per-file processing statistics (FR-113, Phase 4.1 semantics).

    Invariant: malformed + events_parsed + othersyslog_dropped == lines_read.
    ``events_parsed`` counts every retained parsed event, including retained
    ``othersyslog`` events and intra-file byte-identical repeats;
    ``duplicates`` counts those intra-file repeats (a subset of
    ``events_parsed``, informational only - they are never dropped);
    ``othersyslog`` counts every othersyslog line encountered (retained or
    dropped under the retention cap).
    """

    lines_read: int = 0
    events_parsed: int = 0
    malformed: int = 0
    duplicates: int = 0
    othersyslog: int = 0
    othersyslog_dropped: int = 0


@dataclass(frozen=True, slots=True)
class Finding:
    """A detection result (AR-007). At most one per (rule_id, src_ip) per run."""

    rule_id: str
    severity: str
    src_ip: str
    first_seen: int
    last_seen: int
    evidence: tuple[str, ...] = ()
    summary: dict[str, object] = field(default_factory=dict)

    _SEVERITIES: ClassVar[frozenset[str]] = frozenset({"low", "medium", "high"})

    def __post_init__(self) -> None:
        if not self.rule_id.startswith("LS-RULE-"):
            raise ValueError("rule_id must start with 'LS-RULE-'")
        if self.severity not in self._SEVERITIES:
            raise ValueError(f"invalid severity: {self.severity!r}")
        _validated_ipv4(self.src_ip)
        if type(self.first_seen) is not int or type(self.last_seen) is not int:
            raise ValueError("first_seen/last_seen must be integers")
        if self.first_seen > self.last_seen:
            raise ValueError("first_seen must not be greater than last_seen")
        if not isinstance(self.evidence, tuple):
            raise ValueError("evidence must be a tuple of raw lines")


# --------------------------------------------------------------------------
# Event model
# --------------------------------------------------------------------------

def _validated_ipv4(value: str) -> str:
    """Validate a dotted-quad IPv4 address; raises ValueError otherwise (AR-009)."""
    if not isinstance(value, str):
        raise ValueError(f"IP address must be a string, got {type(value).__name__}")
    ipaddress.IPv4Address(value)  # raises AddressValueError (a ValueError)
    return value


def _validated_port(value: int) -> int:
    """Validate a destination port in 1-65535 (FR-125; 0 is invalid)."""
    if type(value) is not int or not 1 <= value <= 65535:
        raise ValueError(f"invalid destination port: {value!r}")
    return value


def _validated_status(value: int) -> int:
    """Validate an HTTP response status code in 100-599 (FR-114)."""
    if type(value) is not int or not 100 <= value <= 599:
        raise ValueError(f"invalid HTTP status code: {value!r}")
    return value


def _validated_method(value: str) -> str:
    """Validate an HTTP method token (uppercase alphabetic)."""
    if not isinstance(value, str) or not value or not (value.isalpha() and value.isupper()):
        raise ValueError(f"invalid HTTP method: {value!r}")
    return value


@dataclass(frozen=True, slots=True)
class SecurityEvent:
    """Common base for all parsed security events (Phase 3 section 4.2).

    Sub-second timestamp precision is truncated (floored) to whole seconds by
    the parser before construction (AR-002).
    """

    timestamp: int
    raw_timestamp: str
    raw_line: str
    source_file: str

    @property
    def kind(self) -> str:  # pragma: no cover - overridden by every subclass
        raise NotImplementedError

    def __post_init__(self) -> None:
        if type(self.timestamp) is not int or self.timestamp < 0:
            raise ValueError(f"invalid timestamp: {self.timestamp!r}")
        if not isinstance(self.raw_timestamp, str):
            raise ValueError("raw_timestamp must be a string")
        if not isinstance(self.raw_line, str):
            raise ValueError("raw_line must be a string")
        # Normalization: strip trailing CR/LF only (Phase 3 section 4.2).
        line = self.raw_line
        while line.endswith("\n") or line.endswith("\r"):
            line = line[:-1]
        object.__setattr__(self, "raw_line", line)
        if not isinstance(self.source_file, str):
            raise ValueError("source_file must be a string")


@dataclass(frozen=True, slots=True)
class SSHAuthEvent(SecurityEvent):
    """SSH authentication event (FR-017).

    ``kind`` is ``authfail`` when ``success`` is False, ``authok`` otherwise.
    ``username`` is never None; ``invalid user X`` lines map to ``username=X``.
    """

    src_ip: str
    username: str
    success: bool

    @property
    def kind(self) -> str:
        return "authfail" if not self.success else "authok"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validated_ipv4(self.src_ip)
        if not isinstance(self.username, str):
            raise ValueError("username must be a string")
        if type(self.success) is not bool:
            raise ValueError("success must be a boolean")


@dataclass(frozen=True, slots=True)
class FirewallEvent(SecurityEvent):
    """Firewall connection event (FR-018); ``kind`` is ``fwconn``."""

    src_ip: str
    dst_ip: str
    dst_port: int
    protocol: str

    @property
    def kind(self) -> str:
        return "fwconn"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validated_ipv4(self.src_ip)
        _validated_ipv4(self.dst_ip)
        _validated_port(self.dst_port)
        if not isinstance(self.protocol, str) or not self.protocol:
            raise ValueError("protocol must be a non-empty string")


@dataclass(frozen=True, slots=True)
class HTTPRequestEvent(SecurityEvent):
    """HTTP access event (FR-019); ``kind`` is ``web``."""

    src_ip: str
    method: str
    path: str
    status_code: int

    @property
    def kind(self) -> str:
        return "web"

    def __post_init__(self) -> None:
        super().__post_init__()
        _validated_ipv4(self.src_ip)
        _validated_method(self.method)
        if not isinstance(self.path, str) or not self.path:
            raise ValueError("path must be a non-empty string")
        _validated_status(self.status_code)


@dataclass(frozen=True, slots=True)
class SyslogEvent(SecurityEvent):
    """Pass-through syslog event (FR-021); ``kind`` is ``othersyslog``.

    Well-formed timestamp header with an unrecognized message body.
    Context/evidence only: never consumed by detectors.
    """

    @property
    def kind(self) -> str:
        return "othersyslog"


# --------------------------------------------------------------------------
# Fingerprinting, deduplication, grouping
# --------------------------------------------------------------------------

def fingerprint(event: SecurityEvent) -> tuple[str, int, str]:
    """Content-addressed fingerprint (AR-005, revised Phase 3).

    Two events are duplicates iff they derive from the same normalized line of
    text at the same canonical timestamp -- i.e. the record was re-ingested.
    Distinct genuine repeats (different raw text) always keep distinct
    fingerprints and are preserved (docs/PHASE3_VALIDATION.md section 7).
    """
    return (event.kind, event.timestamp, event.raw_line)


def dedup_cross_file(
    events: list[SecurityEvent],
) -> tuple[list[SecurityEvent], int]:
    """Multiplicity-aware cross-file deduplication (FR-016; AR-005 final;
    Phase 4.1 review correction).

    Policy:
    - Fingerprint: ``(kind, canonical timestamp, raw_line)`` (unchanged).
    - For each fingerprint, the number of retained occurrences equals the
      **maximum occurrence count observed in any single source file** --
      occurrences are never summed across files.
    - Repeated occurrences within one file are preserved up to that
      multiplicity cap; only the excess -- occurrences beyond the cap in
      deterministic first-occurrence order -- is removed as cross-file
      duplicate ingestion.
    - Events appearing in three or more files are handled consistently: the
      cap is per fingerprint, independent of how many files contributed.
    - Deterministic first-occurrence ordering is preserved: the retained
      occurrences of each fingerprint are its earliest occurrences in input
      order.
    - Returns ``(kept_events, removed_cross_file_duplicate_count)``; the
      removal count is exact (``len(events) - len(kept)``).

    Accepted design limitation (docs/PHASE3_VALIDATION.md section 15.2):
    cross-file fingerprint matching is not absolute proof of duplicate
    ingestion - genuinely separate events with identical fingerprints in
    different files may be removed. Removals are always counted so they
    remain visible in run statistics.
    """
    # Pass 1: occurrence multiplicity of each fingerprint per source file.
    per_file: dict[tuple[str, int, str], dict[str, int]] = {}
    for event in events:
        fp = fingerprint(event)
        files = per_file.setdefault(fp, {})
        files[event.source_file] = files.get(event.source_file, 0) + 1
    # Pass 2: retention budget per fingerprint = max single-file multiplicity.
    remaining = {fp: max(files.values()) for fp, files in per_file.items()}
    kept: list[SecurityEvent] = []
    removed = 0
    for event in events:
        fp = fingerprint(event)
        if remaining[fp] > 0:
            remaining[fp] -= 1
            kept.append(event)
        else:
            removed += 1
    return kept, removed


def events_by_src_ip(events: list[SecurityEvent]) -> dict[str, list[SecurityEvent]]:
    """Group events by validated source IP (FR-034).

    ``SyslogEvent`` instances carry no ``src_ip`` and are excluded. Each group
    is sorted by ``(timestamp, kind)`` with a stable sort, preserving input
    order for ties (FR-111).
    """
    groups: dict[str, list[SecurityEvent]] = {}
    for event in events:
        ip = getattr(event, "src_ip", None)
        if ip is None:
            continue
        groups.setdefault(ip, []).append(event)
    for group in groups.values():
        group.sort(key=lambda e: (e.timestamp, e.kind))
    return groups
