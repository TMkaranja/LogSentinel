"""SQLite-backed staging for streaming log processing (Phase 5, NFR-004).

The streaming CLI (cli.py) stages parsed items here instead of accumulating
them in memory:

- events are persisted with every field needed to reconstruct the original
  validated event objects (spec 3.3) plus a monotonic ingestion sequence;
- parser/input errors are staged with their original ordering (spec 3.9);
- per-file statistics rows are staged and summed via SQL (spec 3.7);
- exact cross-file deduplication (Phase 4.1 semantics, spec 3.4) runs as a
  single SQL statement over the staged rows.

Storage design:
- The database file is created in the system temporary directory (or a
  caller-supplied directory for tests) and is never a project artifact; it
  is closed and deleted by :meth:`close`, which ``__exit__`` always calls.
- Transactions are explicit (``isolation_level=None``): the orchestrator
  wraps each file attempt in ``begin()``/``commit()`` and uses
  ``rollback()`` to discard a failed UTF-8 attempt before the Latin-1
  retry (FR-003).
- Deduplication identity is the exact fingerprint triple
  ``(kind, timestamp, raw_line)`` - never a hash alone (spec 3.4).
- Retrieval order is deterministic via the ingestion sequence (FR-111);
  SQLite's implicit row ordering is never relied upon.

This module is leaf-safe: it imports only the standard library and the
event model (events.py). It never parses, detects, or reports.
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
from collections.abc import Iterator
from typing import Any

from .events import (
    ErrorEntry,
    FileStats,
    FirewallEvent,
    HTTPRequestEvent,
    SSHAuthEvent,
    SecurityEvent,
    SyslogEvent,
)

__all__ = ["RunStorage", "MAX_REPORTED_ERRORS_STORAGE"]

#: The streaming CLI reports at most this many staged error entries.
MAX_REPORTED_ERRORS_STORAGE = 100

_SCHEMA = """
CREATE TABLE events (
    seq          INTEGER PRIMARY KEY AUTOINCREMENT,
    kind         TEXT    NOT NULL,
    timestamp    INTEGER NOT NULL,
    raw_timestamp TEXT   NOT NULL,
    raw_line     TEXT    NOT NULL,
    source_file  TEXT    NOT NULL,
    src_ip       TEXT,
    username     TEXT,
    success      INTEGER,
    dst_ip       TEXT,
    dst_port     INTEGER,
    protocol     TEXT,
    method       TEXT,
    path         TEXT,
    status_code  INTEGER
);
CREATE INDEX idx_events_ip ON events (src_ip, timestamp, kind, seq);
CREATE INDEX idx_events_fp ON events (kind, timestamp, raw_line);

CREATE TABLE errors (
    seq          INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file  TEXT    NOT NULL,
    line_number  INTEGER,
    reason       TEXT    NOT NULL,
    kind         TEXT    NOT NULL DEFAULT 'parse'
);

CREATE TABLE file_stats (
    seq                 INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file         TEXT    NOT NULL,
    lines_read          INTEGER NOT NULL,
    events_parsed       INTEGER NOT NULL,
    malformed           INTEGER NOT NULL,
    duplicates          INTEGER NOT NULL,
    othersyslog         INTEGER NOT NULL,
    othersyslog_dropped INTEGER NOT NULL
);
"""


class RunStorage:
    """Temporary SQLite staging database for one CLI run.

    Use as a context manager; :meth:`__exit__` always closes the connection
    and deletes the database file (success, exception, and abort paths -
    spec 3.8). The file lives in the system temporary directory unless a
    ``directory`` is supplied (tests); it is never created inside the
    project tree.
    """

    def __init__(self, directory: str | None = None) -> None:
        self._owns_dir = directory is None
        self._dir = directory or tempfile.mkdtemp(prefix="logsentinel-run-")
        self._path = os.path.join(self._dir, "staging.sqlite3")
        #: Descriptions of cleanup steps that failed (never raised): leaks
        #: stay observable instead of being silently swallowed, while the
        #: original application exception is preserved.
        self.cleanup_errors: list[str] = []
        self._conn: sqlite3.Connection | None = None
        self._closed = False
        try:
            # Explicit transaction control: BEGIN/COMMIT/ROLLBACK by the
            # caller.
            self._conn = sqlite3.connect(self._path, isolation_level=None)
            # Durability is irrelevant for a run-scoped staging file that is
            # deleted afterwards: keep the rollback journal in RAM (ROLLBACK
            # still works for the UTF-8 retry) and skip disk syncs entirely.
            self._conn.execute("PRAGMA journal_mode=MEMORY")
            self._conn.execute("PRAGMA synchronous=OFF")
            self._conn.executescript(_SCHEMA)
        except BaseException:
            # Constructor failure after temp-dir creation (connect, PRAGMA,
            # or schema failure): dispose of every partially created
            # resource, record any removal failure, and re-raise the
            # original exception (spec 3 of the Phase 5 corrections).
            self.cleanup_errors.extend(self._dispose())
            raise

    # -- lifecycle ---------------------------------------------------------

    @property
    def path(self) -> str:
        """Filesystem path of the temporary database (test observability)."""
        return self._path

    def _dispose(self) -> list[str]:
        """Close the connection and remove owned artifacts.

        Returns human-readable descriptions of every removal step that
        failed; never raises (cleanup failures must not mask the original
        application exception). Removal targets only this instance's own
        database file and, when owned, its temporary directory.
        """
        failures: list[str] = []
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception as exc:  # sqlite3.Error and defensive others
                failures.append(f"connection close: {exc}")
            self._conn = None
        try:
            os.remove(self._path)
        except FileNotFoundError:
            pass
        except OSError as exc:
            failures.append(f"database removal {self._path}: {exc}")
        if self._owns_dir:
            try:
                os.rmdir(self._dir)
            except OSError as exc:
                failures.append(f"directory removal {self._dir}: {exc}")
        return failures

    def close(self) -> None:
        """Close the connection and delete the database file.

        Removal failures are recorded in ``cleanup_errors`` for
        observability; they never mask the flow's own outcome.
        """
        if self._closed:
            return
        self._closed = True
        self.cleanup_errors.extend(self._dispose())

    def __enter__(self) -> "RunStorage":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # -- transactions --------------------------------------------------------

    def begin(self) -> None:
        self._conn.execute("BEGIN")

    def commit(self) -> None:
        self._conn.execute("COMMIT")

    def rollback(self) -> None:
        self._conn.execute("ROLLBACK")

    # -- staging -------------------------------------------------------------

    def stage_event(self, event: SecurityEvent) -> None:
        """Persist one validated event with full reconstruction data."""
        kind = event.kind
        row: list[Any] = [
            kind, event.timestamp, event.raw_timestamp, event.raw_line,
            event.source_file,
            getattr(event, "src_ip", None),
            None, None, None, None, None, None, None, None,
        ]
        if isinstance(event, SSHAuthEvent):
            row[6] = event.username
            row[7] = 1 if event.success else 0
        elif isinstance(event, FirewallEvent):
            row[8] = event.dst_ip
            row[9] = event.dst_port
            row[10] = event.protocol
        elif isinstance(event, HTTPRequestEvent):
            row[11] = event.method
            row[12] = event.path
            row[13] = event.status_code
        elif not isinstance(event, SyslogEvent):  # pragma: no cover - guard
            raise ValueError(f"unsupported event kind: {kind!r}")
        self._conn.execute(
            "INSERT INTO events (kind, timestamp, raw_timestamp, raw_line,"
            " source_file, src_ip, username, success, dst_ip, dst_port,"
            " protocol, method, path, status_code)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)

    def fingerprint_seen(self, event: SecurityEvent) -> bool:
        """Exact intra-file duplicate check (Phase 5 correction).

        The staged rows themselves are the fingerprint records: the check
        asks whether the exact triple ``(event.kind, event.timestamp,
        event.raw_line)`` has already been staged for ``event.source_file``
        within the current transaction. Comparisons are exact values - no
        hash-only identity is used. Because the query runs inside the same
        per-file transaction as the staging itself, a rolled-back UTF-8
        attempt automatically discards both its events and the duplicate
        knowledge they carried; the Latin-1 retry starts clean.

        Callers must invoke this BEFORE staging the event it is asked
        about (the streaming parser does: the check precedes the yield,
        staging happens after).
        """
        row = self._conn.execute(
            "SELECT 1 FROM events WHERE kind = ? AND timestamp = ?"
            " AND raw_line = ? AND source_file = ? LIMIT 1",
            (event.kind, event.timestamp, event.raw_line,
             event.source_file)).fetchone()
        return row is not None

    def stage_error(self, entry: ErrorEntry) -> None:
        """Persist one recoverable error entry in arrival order."""
        self._conn.execute(
            "INSERT INTO errors (source_file, line_number, reason, kind)"
            " VALUES (?, ?, ?, ?)",
            (entry.source_file, entry.line_number, entry.reason, entry.kind))

    def stage_file_stats(self, source_file: str, stats: FileStats) -> None:
        """Persist one file's final statistics (successful attempts only)."""
        self._conn.execute(
            "INSERT INTO file_stats (source_file, lines_read, events_parsed,"
            " malformed, duplicates, othersyslog, othersyslog_dropped)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (source_file, stats.lines_read, stats.events_parsed,
             stats.malformed, stats.duplicates, stats.othersyslog,
             stats.othersyslog_dropped))

    # -- retrieval -----------------------------------------------------------

    def iter_events(self) -> Iterator[SecurityEvent]:
        """Yield reconstructed events in ingestion sequence order.

        Deterministic first-occurrence order (FR-111): detectors receive
        exactly the ingestion order; their per-IP stable ``(timestamp,
        kind)`` sorting reproduces the batch API's ordering exactly.
        """
        cursor = self._conn.execute(
            "SELECT seq, kind, timestamp, raw_timestamp, raw_line,"
            " source_file, src_ip, username, success, dst_ip, dst_port,"
            " protocol, method, path, status_code FROM events ORDER BY seq")
        for row in cursor:
            yield _row_to_event(row)

    def error_summary(self) -> tuple[list[ErrorEntry], int]:
        """First staged errors in original order plus the exact total."""
        total = self._conn.execute(
            "SELECT COUNT(*) FROM errors").fetchone()[0]
        entries = [
            ErrorEntry(source_file=row[0], line_number=row[1], reason=row[2],
                       kind=row[3])
            for row in self._conn.execute(
                "SELECT source_file, line_number, reason, kind FROM errors"
                " ORDER BY seq LIMIT ?", (MAX_REPORTED_ERRORS_STORAGE,))
        ]
        return entries, total

    def statistics_sums(self) -> dict[str, int]:
        """SQL aggregate of every staged per-file statistics row.

        ``files_scanned`` is the number of successfully parsed files (the
        orchestrator stages one row per successful file attempt); the six
        counters are exact sums (spec 3.7); ``cross_file_duplicates`` is
        supplied separately by :meth:`dedup_cross_file`.
        """
        row = self._conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(lines_read), 0),"
            " COALESCE(SUM(events_parsed), 0), COALESCE(SUM(malformed), 0),"
            " COALESCE(SUM(duplicates), 0), COALESCE(SUM(othersyslog), 0),"
            " COALESCE(SUM(othersyslog_dropped), 0) FROM file_stats"
        ).fetchone()
        return {
            "files_scanned": row[0],
            "lines_read": row[1],
            "events_parsed": row[2],
            "malformed": row[3],
            "duplicates": row[4],
            "othersyslog": row[5],
            "othersyslog_dropped": row[6],
        }

    # -- deduplication ---------------------------------------------------------

    def dedup_cross_file(self) -> int:
        """Exact cross-file deduplication (Phase 4.1 semantics, spec 3.4).

        For every fingerprint ``(kind, timestamp, raw_line)``:

        - the occurrence count is tracked separately per ``source_file``;
        - the retention cap is the maximum single-file occurrence count
          (counts are never summed across files);
        - the earliest occurrences in ingestion order are retained; only
          occurrences beyond the cap are deleted;
        - same-file repeats are preserved up to the cap; three or more
          files are handled per fingerprint (spec 3.4 examples).

        Returns the exact number of removed occurrences. Implemented as one
        SQL statement; no Python-side event collections are built.
        """
        before = self._conn.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        self._conn.execute(
            """
            DELETE FROM events WHERE seq IN (
                SELECT seq FROM (
                    SELECT e.seq AS seq,
                           c.cap AS cap,
                           ROW_NUMBER() OVER (
                               PARTITION BY e.kind, e.timestamp, e.raw_line
                               ORDER BY e.seq) AS rn
                    FROM events e
                    JOIN (
                        SELECT kind, timestamp, raw_line, MAX(cnt) AS cap
                        FROM (
                            SELECT kind, timestamp, raw_line, source_file,
                                   COUNT(*) AS cnt
                            FROM events
                            GROUP BY kind, timestamp, raw_line, source_file
                        )
                        GROUP BY kind, timestamp, raw_line
                    ) c
                      ON e.kind = c.kind
                     AND e.timestamp = c.timestamp
                     AND e.raw_line = c.raw_line
                )
                WHERE rn > cap
            )
            """)
        after = self._conn.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        return before - after


def _row_to_event(row: tuple) -> SecurityEvent:
    """Reconstruct the original validated event object from a stored row."""
    (_seq, kind, timestamp, raw_timestamp, raw_line, source_file,
     src_ip, username, success, dst_ip, dst_port, protocol,
     method, path, status_code) = row
    if kind in ("authfail", "authok"):
        return SSHAuthEvent(
            timestamp=timestamp, raw_timestamp=raw_timestamp,
            raw_line=raw_line, source_file=source_file, src_ip=src_ip,
            username=username, success=bool(success))
    if kind == "fwconn":
        return FirewallEvent(
            timestamp=timestamp, raw_timestamp=raw_timestamp,
            raw_line=raw_line, source_file=source_file, src_ip=src_ip,
            dst_ip=dst_ip, dst_port=dst_port, protocol=protocol)
    if kind == "web":
        return HTTPRequestEvent(
            timestamp=timestamp, raw_timestamp=raw_timestamp,
            raw_line=raw_line, source_file=source_file, src_ip=src_ip,
            method=method, path=path, status_code=status_code)
    if kind == "othersyslog":
        return SyslogEvent(
            timestamp=timestamp, raw_timestamp=raw_timestamp,
            raw_line=raw_line, source_file=source_file)
    raise ValueError(f"unsupported stored event kind: {kind!r}")  # pragma: no cover
