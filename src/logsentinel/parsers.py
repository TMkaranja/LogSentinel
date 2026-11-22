"""Line-level log parsing for LogSentinel.

Implements docs/ARCHITECTURE.md sections 3-7 and docs/PHASE3_VALIDATION.md
section 5. One compiled, anchored regex per format; IP/port semantics are
validated by ``events``, never by regex. All behaviour is deterministic given
(file bytes, ``reference_now``, thresholds): no clock reads, no dict-order
nondeterminism.

Strict mode is an orchestrator concern (FR-152): ``parse_file`` records
recoverable problems as ``ErrorEntry`` data and never raises for bad lines;
``ParseError`` is reserved for invalid parser parameters.

Per-file ``duplicates`` statistics count intra-file byte-identical repeats,
which are **preserved** (AR-005, final: cross-file-only dedup; Phase 4.1).
Cross-file collapse is the orchestrator's responsibility via
``events.dedup_cross_file`` (Phase 5); per-file and cross-file counts are
disjoint by construction and are never double-counted.

Note (Phase 4): ``parse_file`` takes a filesystem path; Phase 5 will pass
``LogFile.path`` from ``inputs.discover_inputs`` (``parsers`` must not import
``inputs`` per the dependency map).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from .events import (
    ErrorEntry,
    FileStats,
    FirewallEvent,
    HTTPRequestEvent,
    SSHAuthEvent,
    SyslogEvent,
    fingerprint,
)
from .exceptions import ParseError

__all__ = ["ParseResult", "parse_file", "stream_parse_file"]

DEFAULT_MAX_LINE_LENGTH = 8192       # FR-103
DEFAULT_MAX_OTHERSYSLOG_KEPT = 1000  # Phase 3 risk R-07

# One day in seconds: margin of the syslog year-rollover heuristic (AR-004).
_ROLLOVER_MARGIN_S = 86400

_MONTHS: dict[str, int] = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

# --- format regexes (anchored; bounded quantifiers only; A-07 tolerant) -----

_SYSLOG_HEADER = re.compile(
    r"^(?P<mon>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+"
    r"(?P<day>\d{1,2})\s+(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2})\s+"
    r"(?P<rest>.*)$"
)

_ISO_PREFIX = re.compile(
    r"^(?P<iso>\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}:\d{2}(?:\.\d+)?"
    r"(?:[Zz]|[+-]\d{2}:?\d{2})?)\s+(?P<rest>.*)$"
)

# The hostname between timestamp and tag is optional (A-07 dialect tolerance).
_SSH_FAIL = re.compile(
    r"^(?:\S+\s+)?sshd(?:\[\d+\])?:\s+Failed\s+\S+\s+for\s+"
    r"(?:invalid user\s+)?(?P<user>\S+)\s+from\s+(?P<ip>\S+)\s+port\s+\d+"
)

_SSH_OK = re.compile(
    r"^(?:\S+\s+)?sshd(?:\[\d+\])?:\s+Accepted\s+(?:password|publickey)\s+for\s+"
    r"(?P<user>\S+)\s+from\s+(?P<ip>\S+)\s+port\s+\d+"
)

# Firewall lines are tokenized from KEY=value pairs (A-05/A-07 tolerant);
# the first token (after an optional hostname and "kernel:") is the action.
_FW_ACTION = re.compile(r"^(?:\S+\s+)?(?:kernel:\s+)?(?P<action>DROP|ACCEPT|REJECT)\b")
_FW_KV = re.compile(r"\b([A-Z]{2,6})=(\S+)")

_APACHE = re.compile(
    r"^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<ts>[^\]]+)\]\s+"
    r'"(?P<method>[A-Za-z]+)\s+(?P<path>\S+)(?:\s+HTTP/[\d.]+)?"\s+'
    r"(?P<status>\d{3})\s+(?P<size>\S+)"
)


# --------------------------------------------------------------------------
# Timestamp resolution (AR-002/003/004; Phase 3 section 8)
# --------------------------------------------------------------------------

def _syslog_epoch(
    mon: str, day: str, hour: str, minute: str, second: str, reference_now: int
) -> int:
    """Resolve a yearless syslog timestamp to epoch seconds (AR-004).

    Year = UTC year of ``reference_now``; if the result lies more than 24 h in
    the future, subtract one year (Dec-Jan rollover). Raises ``ValueError`` for
    impossible dates (e.g. Feb 30) -- callers record these as malformed.
    """
    ref = datetime.fromtimestamp(reference_now, tz=UTC)
    year = ref.year
    dt = datetime(year, _MONTHS[mon], int(day), int(hour), int(minute), int(second), tzinfo=UTC)
    if dt.timestamp() > reference_now + _ROLLOVER_MARGIN_S:
        try:
            dt = dt.replace(year=year - 1)
        except ValueError:  # e.g. Feb 29 in a non-leap previous year
            dt = dt.replace(year=year - 1, day=int(day) - 1)
    epoch = int(dt.timestamp())
    if epoch < 0:
        raise ValueError("timestamp before 1970 out of range")
    return epoch


def _iso_epoch(text: str) -> int:
    """Parse an ISO-8601 timestamp; naive values are assumed UTC (AR-003)."""
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    epoch = int(dt.timestamp())  # floor truncation (sub-second dropped)
    if epoch < 0:
        raise ValueError("timestamp before 1970 out of range")
    return epoch


def _apache_epoch(text: str) -> int:
    """Parse an Apache ``[dd/Mon/yyyy:hh:mm:ss +zzzz]`` timestamp to epoch UTC."""
    dt = datetime.strptime(text, "%d/%b/%Y:%H:%M:%S %z")
    epoch = int(dt.timestamp())
    if epoch < 0:
        raise ValueError("timestamp before 1970 out of range")
    return epoch


# --------------------------------------------------------------------------
# Line classification
# --------------------------------------------------------------------------

def _parse_firewall_rest(rest: str) -> tuple[str, dict[str, str]]:
    """Extract action and KEY=value tokens from a firewall message body."""
    action_match = _FW_ACTION.match(rest)
    if action_match is None:
        raise ValueError("not a firewall line")
    pairs = dict(_FW_KV.findall(rest))
    return action_match.group("action"), pairs


def _classify(
    line: str, source_file: str, reference_now: int
) -> tuple[object, str | None]:
    """Classify one normalized line.

    Returns ``(event, None)`` on success or ``(None, error_reason)`` when the
    line is malformed. Pure function; never raises for bad input.
    """
    # 1. Apache/Nginx access lines (own embedded timestamp) -- tried first so
    #    that IP-leading lines are not misread as untimestamped bodies.
    apache = _APACHE.match(line)
    if apache is not None:
        try:
            epoch = _apache_epoch(apache.group("ts"))
        except ValueError as exc:
            return None, f"invalid apache timestamp ({exc})"
        try:
            return (
                HTTPRequestEvent(
                    timestamp=epoch,
                    raw_timestamp=apache.group("ts"),
                    raw_line=line,
                    source_file=source_file,
                    src_ip=apache.group("ip"),
                    method=apache.group("method").upper(),
                    path=apache.group("path"),
                    status_code=int(apache.group("status")),
                ),
                None,
            )
        except ValueError as exc:
            return None, str(exc)

    # 2. Extract a leading timestamp: classic syslog or ISO-8601 prefix.
    syslog = _SYSLOG_HEADER.match(line)
    iso = _ISO_PREFIX.match(line)
    if syslog is not None:
        try:
            epoch = _syslog_epoch(
                syslog.group("mon"),
                syslog.group("day"),
                syslog.group("h"),
                syslog.group("m"),
                syslog.group("s"),
                reference_now,
            )
        except (ValueError, KeyError) as exc:
            return None, f"invalid syslog timestamp ({exc})"
        rest = syslog.group("rest")
        raw_ts = (f"{syslog.group('mon')} {syslog.group('day')} "
                  f"{syslog.group('h')}:{syslog.group('m')}:{syslog.group('s')}")
    elif iso is not None:
        try:
            epoch = _iso_epoch(iso.group("iso"))
        except ValueError as exc:
            return None, f"invalid iso timestamp ({exc})"
        rest = iso.group("rest")
        raw_ts = iso.group("iso")
    else:
        return None, "unrecognized line format"

    # 3. SSH authentication messages (FR-017).
    ssh_fail = _SSH_FAIL.match(rest)
    if ssh_fail is not None:
        try:
            return (
                SSHAuthEvent(
                    timestamp=epoch,
                    raw_timestamp=raw_ts,
                    raw_line=line,
                    source_file=source_file,
                    src_ip=ssh_fail.group("ip"),
                    username=ssh_fail.group("user"),
                    success=False,
                ),
                None,
            )
        except ValueError as exc:
            return None, str(exc)
    ssh_ok = _SSH_OK.match(rest)
    if ssh_ok is not None:
        try:
            return (
                SSHAuthEvent(
                    timestamp=epoch,
                    raw_timestamp=raw_ts,
                    raw_line=line,
                    source_file=source_file,
                    src_ip=ssh_ok.group("ip"),
                    username=ssh_ok.group("user"),
                    success=True,
                ),
                None,
            )
        except ValueError as exc:
            return None, str(exc)

    # 4. Firewall connection messages (FR-018).
    try:
        _action, pairs = _parse_firewall_rest(rest)
    except ValueError:
        pairs = None
    if pairs is not None and "SRC" in pairs and "DST" in pairs and "PROTO" in pairs:
        proto = pairs["PROTO"].upper()
        if proto == "ICMP":
            # ICMP carries no destination port; retained as context only
            # (docs/DETECTION_RULES.md Rule 2 edge cases).
            return (
                SyslogEvent(
                    timestamp=epoch, raw_timestamp=raw_ts, raw_line=line,
                    source_file=source_file,
                ),
                None,
            )
        try:
            dst_port = int(pairs["DPT"])
        except (KeyError, ValueError):
            return None, "invalid destination port"
        try:
            return (
                FirewallEvent(
                    timestamp=epoch,
                    raw_timestamp=raw_ts,
                    raw_line=line,
                    source_file=source_file,
                    src_ip=pairs["SRC"],
                    dst_ip=pairs["DST"],
                    dst_port=dst_port,
                    protocol=proto,
                ),
                None,
            )
        except ValueError as exc:
            return None, str(exc)

    # 5. Well-formed header, unrecognized body -> othersyslog (FR-021, F-03).
    return (
        SyslogEvent(
            timestamp=epoch, raw_timestamp=raw_ts, raw_line=line,
            source_file=source_file,
        ),
        None,
    )


# --------------------------------------------------------------------------
# File driver
# --------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ParseResult:
    """Outcome of parsing one file (FR-112, FR-113)."""

    events: list[object] = field(default_factory=list)
    stats: FileStats = field(default_factory=FileStats)
    errors: list[ErrorEntry] = field(default_factory=list)


def parse_file(
    path: str | Path,
    reference_now: int,
    *,
    max_line_length: int = DEFAULT_MAX_LINE_LENGTH,
    max_othersyslog_kept: int = DEFAULT_MAX_OTHERSYSLOG_KEPT,
) -> ParseResult:
    """Parse one log file into a complete in-memory result (compatibility).

    Phase 5: implemented as a thin consumer of :func:`stream_parse_file`, so
    both APIs share one code path and identical semantics (encoding
    fallback, statistics, error ordering). The streaming CLI does NOT use
    this function; it is intended for callers that genuinely need the whole
    ``ParseResult`` in memory.
    """
    events: list[object] = []
    errors: list[ErrorEntry] = []
    stats: FileStats | None = None
    for tag, item in stream_parse_file(
        path, reference_now,
        max_line_length=max_line_length,
        max_othersyslog_kept=max_othersyslog_kept,
    ):
        if tag == "event":
            events.append(item)
        elif tag == "error":
            errors.append(item)  # type: ignore[arg-type]
        elif tag == "rollback":
            # UTF-8 attempt failed: discard everything staged for it and
            # expect the full Latin-1 retry (FR-003).
            events.clear()
            errors.clear()
        elif tag == "stats":
            stats = item  # type: ignore[assignment]
    if stats is None:  # pragma: no cover - stream always yields stats
        stats = FileStats()
    return ParseResult(events=events, stats=stats, errors=errors)


def stream_parse_file(
    path: str | Path,
    reference_now: int,
    *,
    max_line_length: int = DEFAULT_MAX_LINE_LENGTH,
    max_othersyslog_kept: int = DEFAULT_MAX_OTHERSYSLOG_KEPT,
    duplicate_check=None,
):
    """Stream one log file item by item (FR-110, NFR-004; Phase 5).

    ``duplicate_check`` (Phase 5 correction): optional callable mapping an
    event to ``True`` when its exact fingerprint ``(event.kind,
    event.timestamp, event.raw_line)`` was already recorded for the same
    source file. It is consulted before each event is yielded, so a
    storage-backed checker (the CLI path) observes only previously staged
    rows and shares the file's transaction lifecycle. When ``None``, an
    exact in-memory per-file fingerprint set is used - the compatibility
    path; the streaming CLI MUST supply a checker so that no unbounded
    Python fingerprint collection exists in the production pipeline. The
    parser itself never touches SQLite; the tracker seam keeps the two
    responsibilities separated.

    Yields tagged items:

    - ``("event", SecurityEvent)`` - one validated event at a time;
    - ``("error", ErrorEntry)`` - one recoverable problem at a time;
    - ``("rollback", None)`` - the UTF-8 attempt failed: the caller must
      discard every event/error staged for this file so far and expect a
      complete Latin-1 retry (FR-003). The discarded attempt's events are
      re-emitted from the beginning in the retry.
    - ``("stats", FileStats)`` - final sentinel, exactly once per
      successful stream; reflects ONLY the successful attempt (spec 3.7).

    Encoding: UTF-8 first; if decoding fails anywhere in the file, the
    partial attempt is abandoned (the caller rolls back its staging) and
    the entire file is retried as Latin-1 from the beginning. The fallback
    warning ``ErrorEntry`` is emitted before the retry's own items so the
    error ordering matches ``parse_file``.

    Statistics and semantics are identical to ``parse_file``: line-ending
    removal, overlong/empty-line handling, intra-file duplicate counting
    (repeats preserved), ``othersyslog`` retention cap, ``reference_now``
    year inference. No full-file event or error lists are accumulated.

    Limitation (documented, unchanged from ``parse_file``): the retry opens
    the file a second time; a file that changes between the two attempts
    can produce mixed content. Byte-snapshot consistency is NOT claimed.

    ``OSError`` from opening/reading propagates to the caller.
    """
    if type(reference_now) is not int or reference_now < 0:
        raise ParseError("reference_now must be a non-negative integer")
    if type(max_line_length) is not int or max_line_length <= 0:
        raise ParseError("max_line_length must be a positive integer")
    if type(max_othersyslog_kept) is not int or max_othersyslog_kept < 0:
        raise ParseError("max_othersyslog_kept must be a non-negative integer")

    source = str(path)
    for encoding in ("utf-8", "latin-1"):
        if encoding != "utf-8":
            # FR-003 fallback warning, emitted before the retry's items so
            # error ordering matches the compatibility parse_file.
            yield ("error", ErrorEntry(
                source_file=source, line_number=None,
                reason="utf-8 decode failed; retried as latin-1",
                kind="parse",
            ))
        try:
            yield from _stream_attempt(
                path, encoding, source, reference_now,
                max_line_length, max_othersyslog_kept, duplicate_check)
            return  # successful attempt: stats sentinel already emitted
        except UnicodeDecodeError:
            if encoding != "utf-8":  # pragma: no cover - latin-1 is total
                raise
            yield ("rollback", None)  # caller discards the partial attempt


def _stream_attempt(
    path: str | Path,
    encoding: str,
    source: str,
    reference_now: int,
    max_line_length: int,
    max_othersyslog_kept: int,
    duplicate_check,
):
    """Yield one full pass over ``path``; raises UnicodeDecodeError.

    On success the final item is the ``("stats", FileStats)`` sentinel.
    """
    if duplicate_check is None:
        # Compatibility path: exact in-memory fingerprint set (legacy
        # behaviour, identical duplicate statistics).
        seen: set[tuple[str, int, str]] = set()

        def duplicate_check(event):  # noqa: F811 - deliberate local policy
            fp = fingerprint(event)
            if fp in seen:
                return True
            seen.add(fp)
            return False

    othersyslog_kept = 0
    lines_read = events_parsed = malformed = duplicates = othersyslog = 0
    othersyslog_dropped = 0

    with open(path, "r", encoding=encoding, newline="") as handle:
        for line_number, raw in enumerate(handle, start=1):
            lines_read += 1
            line = raw.rstrip("\r\n")
            if len(line) > max_line_length:
                malformed += 1
                yield ("error", ErrorEntry(
                    source_file=source, line_number=line_number,
                    reason="overlong line", kind="parse",
                ))
                continue
            if not line.strip():
                malformed += 1
                yield ("error", ErrorEntry(
                    source_file=source, line_number=line_number,
                    reason="empty line", kind="parse",
                ))
                continue

            event, error = _classify(line, source, reference_now)
            if event is None:
                malformed += 1
                yield ("error", ErrorEntry(
                    source_file=source, line_number=line_number,
                    reason=error or "unparseable line", kind="parse",
                ))
                continue

            if event.kind == "othersyslog":
                othersyslog += 1
                if othersyslog_kept >= max_othersyslog_kept:
                    # Retention cap (Phase 3 R-07): counted, not retained.
                    othersyslog_dropped += 1
                    continue
                othersyslog_kept += 1

            fp_seen = duplicate_check(event)
            if fp_seen:
                # Intra-file byte-identical repeat: preserved (AR-005, final)
                # and counted for statistics only - never dropped (Phase 4.1).
                duplicates += 1
            yield ("event", event)
            events_parsed += 1

    yield ("stats", FileStats(
        lines_read=lines_read,
        events_parsed=events_parsed,
        malformed=malformed,
        duplicates=duplicates,
        othersyslog=othersyslog,
        othersyslog_dropped=othersyslog_dropped,
    ))
