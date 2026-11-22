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
- Deduplication identity is the exact fingerprint triple ``(kind,
  timestamp, raw_line)``. Since the M1 security change (security audit
  finding R1) the persisted representation of that triple is a per-run
  keyed digest: each ``RunStorage`` instance generates one random
  HMAC-SHA256 key (``secrets.token_bytes(32)``), held only in memory for
  the instance's lifetime, and stores HMAC digests instead of plaintext
  raw lines in the database. The digest is computed from the exact
  original identity; SQLite never retains the raw line itself (staged
  evidence is sanitized; see ``evidence_line`` below). The in-memory
  event model (events.py) is unchanged.
- The digest message uses a fixed domain prefix and length-prefixed
  fields (``_event_fingerprint``), so concatenation of colliding field
  values cannot produce the same digest.
- Retrieval order is deterministic via the ingestion sequence (FR-111);
  SQLite's implicit row ordering is never relied upon.
- Cleanup coordination (R1 step): a persistent global cleanup lock file in
  the system temporary directory serializes teardown of LogSentinel-owned
  run directories (acquired before creating an owned run directory and
  during teardown, never held during scanning — concurrent runs remain
  possible), and each owned run directory contains a per-run lock held for
  the run's entire lifetime. Locking uses the standard library: ``msvcrt``
  on Windows and ``fcntl.flock`` on POSIX. Caller-supplied directories are
  caller-owned: no lock file is created in them and they are never removed.
- Stale-directory sweeping (R1 step): ``sweep_stale_run_directories``
  removes LogSentinel-owned ``logsentinel-run-*`` directories strictly
  older than 24 hours (mtime basis) that can be proven abandoned:
  recognized artifact content only, ``run.lock`` acquirable
  non-blockingly (an active run keeps its lock and is never touched),
  symlinks and foreign/malformed content skipped. Sweeping, directory
  creation, and teardown all serialize on the global cleanup lock; owned
  ``RunStorage`` construction sweeps while it already holds that lock
  (no re-acquisition). Sweep failures are returned, never raised.

This module is leaf-safe: it imports only the standard library and the
event model (events.py). It never parses, detects, or reports.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import stat
import struct
import tempfile
import time
from collections.abc import Iterator
from typing import Any

try:  # Cross-platform advisory locking (R1 step: cleanup coordination).
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None
try:
    import msvcrt
except ImportError:  # pragma: no cover - POSIX
    msvcrt = None

from .events import (
    ErrorEntry,
    FileStats,
    FirewallEvent,
    HTTPRequestEvent,
    SSHAuthEvent,
    SecurityEvent,
    SyslogEvent,
    _redact,
    _sanitize,
)

__all__ = ["RunStorage", "MAX_REPORTED_ERRORS_STORAGE"]

#: The streaming CLI reports at most this many staged error entries.
MAX_REPORTED_ERRORS_STORAGE = 100

#: Persistent global cleanup lock (never removed) in the system temp dir.
_GLOBAL_LOCK_FILENAME = "logsentinel-cleanup.lock"
#: Per-run lock file inside each LogSentinel-owned temporary directory.
_RUN_LOCK_FILENAME = "run.lock"


def _global_cleanup_lock_path() -> str:
    """Path of the persistent global cleanup lock file."""
    return os.path.join(tempfile.gettempdir(), _GLOBAL_LOCK_FILENAME)


def _lock_fd(handle) -> None:
    """Acquire a blocking exclusive advisory lock on ``handle``.

    On Windows the lock region is relative to the current file position
    (``msvcrt.locking`` contract); seek to byte offset zero explicitly so
    the lock byte is consistent across processes regardless of open mode.
    """
    if msvcrt is not None:  # Windows
        handle.seek(0, 0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:  # POSIX
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def _try_lock_fd(handle) -> None:
    """Acquire a NON-blocking exclusive advisory lock on ``handle``.

    Raises ``OSError`` if the lock is already held. The same explicit
    seek-to-zero applies on Windows (LK_NBLCK contract).
    """
    if msvcrt is not None:  # Windows
        handle.seek(0, 0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    else:  # POSIX
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_fd(handle) -> None:
    """Release the advisory lock on ``handle`` (best-effort)."""
    try:
        if msvcrt is not None:  # Windows
            handle.seek(0, 0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:  # POSIX
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError:
        # Closing the handle also releases the lock; never mask cleanup.
        pass


class _FileLock:
    """Cross-platform blocking exclusive advisory file lock.

    Standard library only: ``msvcrt.locking`` on Windows, ``fcntl.flock``
    on POSIX. The lock is held by the open handle; :meth:`release` unlocks
    and closes it. Acquire is idempotent per instance (a held instance does
    not re-lock); release of an unheld instance is a no-op.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._handle = None

    @property
    def path(self) -> str:
        return self._path

    @property
    def locked(self) -> bool:
        return self._handle is not None

    def acquire(self) -> None:
        if self._handle is not None:
            return
        handle = open(self._path, "a+b")
        try:
            _lock_fd(handle)
        except BaseException:
            handle.close()
            raise
        self._handle = handle

    def try_acquire(self) -> bool:
        """Acquire without blocking; ``False`` if the lock is busy.

        On failure the temporary handle is closed so no lock state leaks.
        """
        if self._handle is not None:
            return True  # already held by this instance
        handle = open(self._path, "a+b")
        try:
            _try_lock_fd(handle)
        except OSError:
            handle.close()
            return False
        except BaseException:
            handle.close()
            raise
        self._handle = handle
        return True

    def release(self) -> None:
        if self._handle is None:
            return
        handle, self._handle = self._handle, None
        try:
            _unlock_fd(handle)
        finally:
            handle.close()


#: Recognized artifacts inside an owned run directory (R1 sweeper
#: whitelist). Anything else makes a candidate foreign/malformed and it is
#: skipped, never deleted.
_OWNED_ARTIFACTS = frozenset({"staging.sqlite3", _RUN_LOCK_FILENAME})


def _sweep_skip_reason(path: str, root_abspath: str,
                       cutoff: float) -> str | None:
    """Revalidate one sweep candidate; ``None`` means safe to remove.

    Full identity/safety validation, safe to call both during discovery
    and again **under the global cleanup lock** immediately before
    deletion (defence against the directory being replaced, renamed, made
    recent, or filled with foreign content between the two phases):

    - name must be an exact ``logsentinel-run-*`` candidate;
    - the path's parent must be exactly the validated scan root
      (containment; prevents path substitution);
    - symlinks are rejected via ``os.path.islink`` **and**, on Windows,
      any reparse point (``FILE_ATTRIBUTE_REPARSE_POINT``), which also
      covers junctions that ``islink`` does not report;
    - the entry must be a real directory (``follow_symlinks=False``);
    - it must be strictly older than the age cutoff (recomputed mtime);
    - contents must be a non-empty subset of the recognized artifact
      names, and every entry must be a regular file (no subdirectories,
      no symlinks, nothing unknown). Empty directories are rejected.

    Portable-limitation note: reparse points are detectable only on
    Windows; on POSIX, ``islink`` covers symlinks, but bind mounts over
    the scan root cannot be detected portably - the root-containment and
    content checks are the residual defence.
    """
    name = os.path.basename(path)
    if not name.startswith("logsentinel-run-"):
        return f"sweep skip {path}: unexpected name"
    parent = os.path.normcase(os.path.dirname(os.path.abspath(path)))
    if parent != root_abspath:
        return f"sweep skip {path}: outside scan root"
    if os.path.islink(path):
        return f"sweep skip {path}: symlink"
    try:
        st = os.stat(path, follow_symlinks=False)
    except OSError:
        return f"sweep skip {path}: stat failed"
    reparse = getattr(st, "st_file_attributes", 0)
    if reparse & stat.FILE_ATTRIBUTE_REPARSE_POINT:
        return f"sweep skip {path}: reparse point (junction/symlink)"
    if not stat.S_ISDIR(st.st_mode):
        return f"sweep skip {path}: not a directory"
    if st.st_mtime > cutoff:  # strictly older than the age limit
        return f"sweep skip {path}: no longer stale"
    try:
        entries = os.listdir(path)
    except OSError:
        return f"sweep skip {path}: listdir failed"
    if not entries:
        return f"sweep skip {path}: empty directory"
    for item in entries:
        if item not in _OWNED_ARTIFACTS:
            return f"sweep skip {path}: foreign content {item!r}"
        item_path = os.path.join(path, item)
        if os.path.islink(item_path):
            return f"sweep skip {path}: entry symlink {item!r}"
        try:
            item_st = os.stat(item_path, follow_symlinks=False)
        except OSError:
            return f"sweep skip {path}: entry stat failed {item!r}"
        if not stat.S_ISREG(item_st.st_mode):
            return f"sweep skip {path}: entry not a regular file {item!r}"
    return None


def sweep_stale_run_directories(
        root: str | None = None, *, now: float | None = None,
        max_age_seconds: float = 86400.0,
        assume_global_lock_held: bool = False) -> list[str]:
    """Remove abandoned LogSentinel-owned temporary run directories.

    A candidate is a **direct child** of ``root`` (never recursed) whose
    name starts exactly with ``logsentinel-run-`` and which is a real
    directory (symlinks are rejected). A candidate is removed only when
    ALL of the following hold:

    - it is strictly older than ``max_age_seconds`` (24 hours by default),
      based on ``mtime`` (``now`` is injectable for deterministic tests);
    - its contents are exclusively recognized LogSentinel artifacts
      (``staging.sqlite3`` and/or ``run.lock``) - foreign, malformed, or
      unknown content makes it skipped, never deleted;
    - its ``run.lock`` can be acquired NON-blockingly - an active run
      keeps its lock and is never touched (lock-less stale residue is
      removed, conservatively, only under the content whitelist above).
    - full identity/safety revalidation (name, root containment, symlink
      and reparse-point status, directory type, recalculated age, and
      content whitelist incl. regular-file checks) is repeated **under
      the global cleanup lock** immediately before deletion; empty
      directories are rejected.

    The removal phase runs under the persistent global cleanup lock,
    serializing with directory creation and teardown. When
    ``assume_global_lock_held`` is true (owned ``RunStorage`` construction
    already holds it), the caller's hold is used and no re-acquisition or
    extra release happens - a held ``_FileLock.acquire`` is a no-op, but
    the sweeper must not release a lock it did not take.

    Returns human-readable failure descriptions; never raises. The global
    lock file itself is never removed.
    """
    failures: list[str] = []
    if root is None:
        root = tempfile.gettempdir()
    if now is None:
        now = time.time()
    cutoff = now - max_age_seconds
    try:
        entries = list(os.scandir(root))
    except OSError as exc:
        return [f"sweep scan {root}: {exc}"]
    candidates: list[str] = []
    for entry in entries:
        if not entry.name.startswith("logsentinel-run-"):
            continue
        try:
            if entry.is_symlink():
                continue
            if not entry.is_dir(follow_symlinks=False):
                continue
            mtime = entry.stat(follow_symlinks=False).st_mtime
        except OSError:
            continue  # unreadable entry: skip, never delete
        if mtime > cutoff:  # strictly older than max_age required
            continue
        candidates.append(entry.path)
    if not candidates:
        return failures
    root_abspath = os.path.normcase(os.path.abspath(root))
    sweep_lock = None
    if not assume_global_lock_held:
        sweep_lock = _FileLock(_global_cleanup_lock_path())
        try:
            sweep_lock.acquire()
        except OSError as exc:
            return failures + [f"sweep global lock: {exc}"]
    try:
        for path in candidates:
            # Revalidate EVERYTHING under the global lock: identity, type,
            # symlink/reparse status, root containment, recalculated age,
            # and content whitelist. Replacement, renames, symlink swaps,
            # recentification, or foreign content between discovery and
            # deletion make the candidate skipped, never deleted.
            skip_reason = _sweep_skip_reason(path, root_abspath, cutoff)
            if skip_reason is not None:
                continue
            db_path = os.path.join(path, "staging.sqlite3")
            lock_file = os.path.join(path, _RUN_LOCK_FILENAME)
            run_lock = None
            if os.path.lexists(lock_file):
                run_lock = _FileLock(lock_file)
                try:
                    acquired = run_lock.try_acquire()
                except OSError as exc:
                    # Opening/acquiring the run lock failed (e.g.
                    # PermissionError): the lock state cannot be verified,
                    # so the candidate is NEVER deleted. Preserve the
                    # directory and all contents; report the failure.
                    failures.append(f"sweep run-lock {lock_file}: {exc}")
                    run_lock = None
                    continue
                if not acquired:
                    continue  # active run: never touched
            # NOTE: a missing run.lock is probed by NOT creating it -
            # creating the file here would refresh the directory mtime and
            # defeat the age revalidation below. This is race-free: run
            # creation also holds the global cleanup lock, so no active
            # run can appear between the check and the deletion.
            # Second full revalidation AFTER the per-run lock was taken
            # (when it existed) and BEFORE the first destructive
            # operation: state may have changed while the probe ran. On a
            # skip reason nothing is deleted and any held per-run lock is
            # released immediately.
            skip_reason = _sweep_skip_reason(path, root_abspath, cutoff)
            if skip_reason is not None:
                if run_lock is not None:
                    run_lock.release()
                continue
            try:
                try:
                    os.remove(db_path)
                except FileNotFoundError:
                    pass
                except OSError as exc:
                    failures.append(f"sweep database {db_path}: {exc}")
            finally:
                # Release before removing the lock file: on Windows an
                # open locked handle prevents deletion.
                if run_lock is not None:
                    run_lock.release()
            try:
                os.remove(lock_file)
            except FileNotFoundError:
                pass
            except OSError as exc:
                failures.append(f"sweep run-lock {lock_file}: {exc}")
            try:
                os.rmdir(path)
            except OSError as exc:
                failures.append(f"sweep directory {path}: {exc}")
    finally:
        if sweep_lock is not None:
            sweep_lock.release()
    return failures


#: Domain separation prefix for the per-run fingerprint digest (M1).
_FP_DOMAIN = b"LogSentinel:event-fingerprint:v1\x00"


def _length_prefixed(value: str) -> bytes:
    """Encode ``value`` unambiguously: 4-byte length + UTF-8 bytes."""
    data = value.encode("utf-8")
    return struct.pack(">I", len(data)) + data


def _event_fingerprint(key: bytes, kind: str, timestamp: int,
                       raw_line: str) -> bytes:
    """Per-run keyed HMAC-SHA256 digest of the exact event identity.

    Message layout (unambiguous, length-prefixed):

    - fixed domain prefix ``LogSentinel:event-fingerprint:v1\x00``;
    - ``kind``: 4-byte big-endian length + UTF-8 bytes;
    - ``timestamp``: fixed-width signed 64-bit big-endian;
    - ``raw_line``: 4-byte big-endian length + UTF-8 bytes.

    The digest is computed from the original, unmodified identity before
    any sanitization. Length prefixes make the encoding injective: field
    values cannot bleed into one another (an adversarial delimiter inside
    a value cannot produce a colliding message).
    """
    message = (_FP_DOMAIN
               + _length_prefixed(kind)
               + struct.pack(">q", timestamp)
               + _length_prefixed(raw_line))
    return hmac.new(key, message, hashlib.sha256).digest()


_SCHEMA = """
CREATE TABLE events (
    seq          INTEGER PRIMARY KEY AUTOINCREMENT,
    kind         TEXT    NOT NULL,
    timestamp    INTEGER NOT NULL,
    raw_timestamp TEXT   NOT NULL,
    evidence_line TEXT   NOT NULL,
    fp_digest    BLOB    NOT NULL,
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
CREATE INDEX idx_events_fp ON events (kind, timestamp, fp_digest);

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
        self._dir = None
        self._path = None
        #: Descriptions of cleanup steps that failed (never raised): leaks
        #: stay observable instead of being silently swallowed, while the
        #: original application exception is preserved.
        self.cleanup_errors: list[str] = []
        self._conn: sqlite3.Connection | None = None
        self._closed = False
        # R1 retryability: set once destructive cleanup has been attempted
        # under the global lock; close() marks the instance closed only
        # after this flag is set (a global-lock failure leaves the instance
        # retryable).
        self._cleanup_complete = False
        # M1 (security audit R1): one fresh random key per RunStorage
        # instance, held exclusively in memory for the instance lifetime.
        # Never persisted, logged, reported, or exposed; regenerated by
        # every new instance. The same key is used across transaction
        # rollback and UTF-8 retry (it is not tied to any transaction).
        self._hmac_key = secrets.token_bytes(32)
        # R1 step (cleanup coordination): the persistent global cleanup
        # lock serializes owned-directory creation and teardown. It is NOT
        # held during scanning, so concurrent runs remain possible.
        self._global_lock = _FileLock(_global_cleanup_lock_path())
        self._run_lock: _FileLock | None = None
        try:
            if self._owns_dir:
                # Global lock held only while creating the owned run
                # directory and taking the per-run lock.
                self._global_lock.acquire()
                try:
                    self._dir = tempfile.mkdtemp(prefix="logsentinel-run-")
                    self._run_lock = _FileLock(
                        os.path.join(self._dir, _RUN_LOCK_FILENAME))
                    self._run_lock.acquire()  # held for the entire run
                    # R1 step: sweep abandoned residue while the global
                    # cleanup lock is already held (no re-acquisition); the
                    # fresh run directory is minutes old and its lock is
                    # held, so it can never be a sweep target. Sweeping
                    # never raises; failures are recorded below.
                    self.cleanup_errors.extend(
                        sweep_stale_run_directories(
                            assume_global_lock_held=True))
                finally:
                    self._global_lock.release()
            else:
                # Caller-supplied directories are caller-owned: no lock
                # file is created inside them.
                self._dir = directory
            self._path = os.path.join(self._dir, "staging.sqlite3")
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
            # Constructor failure (owned-directory or lock handling, connect,
            # PRAGMA, or schema failure): dispose of every partially created
            # resource, record any removal failure, and re-raise the
            # original exception (spec 3 of the Phase 5 corrections). A
            # single handler guarantees _dispose() runs exactly once.
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
        database file and, when owned, its temporary directory. Teardown
        runs under the persistent global cleanup lock; the per-run lock is
        released and its lock file removed before the owned directory is
        removed. The global lock file itself is persistent and never
        removed. If the global lock cannot be acquired, **no destructive
        cleanup is performed**: the database, per-run lock, and owned
        directory are preserved (observable via ``cleanup_errors``) so the
        run is never treated as unprotected.
        """
        failures: list[str] = []
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception as exc:  # sqlite3.Error and defensive others
                failures.append(f"connection close: {exc}")
            self._conn = None
        try:
            self._global_lock.acquire()
        except OSError as exc:
            # Without the global cleanup lock, destructive cleanup must NOT
            # proceed: the per-run lock and directory are preserved so the
            # run is not treated as unprotected (and a future stale-directory
            # sweeper does not race a live run). The failure is observable
            # in ``cleanup_errors``; the original application exception (if
            # any) is not masked.
            failures.append(f"global cleanup lock: {exc}")
            return failures
        # From here the destructive cleanup is (being) performed under the
        # global lock: close() may mark the instance closed regardless of
        # individual step failures (they are recorded in cleanup_errors).
        self._cleanup_complete = True
        try:
            if self._path is not None:
                try:
                    os.remove(self._path)
                except FileNotFoundError:
                    pass
                except OSError as exc:
                    failures.append(f"database removal {self._path}: {exc}")
            if self._owns_dir and self._dir is not None:
                if self._run_lock is not None:
                    # Release before removing the lock file: on Windows an
                    # open locked handle prevents deletion.
                    self._run_lock.release()
                lock_file = os.path.join(self._dir, _RUN_LOCK_FILENAME)
                try:
                    os.remove(lock_file)
                except FileNotFoundError:
                    pass
                except OSError as exc:
                    failures.append(
                        f"run-lock removal {self._dir}: {exc}")
                try:
                    os.rmdir(self._dir)
                except OSError as exc:
                    failures.append(f"directory removal {self._dir}: {exc}")
        finally:
            self._global_lock.release()
        self._run_lock = None
        return failures

    def close(self) -> None:
        """Close the connection and delete the database file.

        Removal failures are recorded in ``cleanup_errors`` for
        observability; they never mask the flow's own outcome. If global
        cleanup-lock acquisition fails, destructive cleanup is skipped and
        the instance stays retryable: a later :meth:`close` can complete
        the cleanup once the lock becomes available. After a completed
        cleanup the instance is marked closed and further calls are
        no-ops.
        """
        if self._closed:
            return
        self.cleanup_errors.extend(self._dispose())
        if self._cleanup_complete:
            self._closed = True

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
        """Persist one validated event with full reconstruction data.

        M1: the persisted ``fp_digest`` is the per-run HMAC of the exact
        original identity ``(kind, timestamp, raw_line)``; the persisted
        ``evidence_line`` is the sanitized original line. The original
        line itself is never written to the database, and the caller's
        event object is not mutated.
        """
        kind = event.kind
        row: list[Any] = [
            kind, event.timestamp, event.raw_timestamp,
            _sanitize(event.raw_line),
            self._event_fingerprint(event),
            event.source_file,
            getattr(event, "src_ip", None),
            None, None, None, None, None, None, None, None,
        ]
        if isinstance(event, SSHAuthEvent):
            row[7] = event.username
            row[8] = 1 if event.success else 0
        elif isinstance(event, FirewallEvent):
            row[9] = event.dst_ip
            row[10] = event.dst_port
            row[11] = event.protocol
        elif isinstance(event, HTTPRequestEvent):
            row[12] = event.method
            # FR-162 remediation: the parsed path may itself be
            # credential-bearing (e.g. ``/login?password=secret``). The
            # shared events.py redaction is applied to the persisted
            # column only -- WITHOUT the evidence-length cap (requirement:
            # parsed paths are not capped); the in-memory event used by
            # detectors is untouched.
            row[13] = _redact(event.path)
            row[14] = event.status_code
        elif not isinstance(event, SyslogEvent):  # pragma: no cover - guard
            raise ValueError(f"unsupported event kind: {kind!r}")
        self._conn.execute(
            "INSERT INTO events (kind, timestamp, raw_timestamp,"
            " evidence_line, fp_digest, source_file, src_ip, username,"
            " success, dst_ip, dst_port, protocol, method, path,"
            " status_code)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)

    def _event_fingerprint(self, event: SecurityEvent) -> bytes:
        """Keyed digest of this instance's exact identity for ``event``."""
        return _event_fingerprint(self._hmac_key, event.kind,
                                  event.timestamp, event.raw_line)

    def fingerprint_seen(self, event: SecurityEvent) -> bool:
        """Exact intra-file duplicate check (Phase 5 correction, M1 form).

        The staged rows themselves are the fingerprint records: the check
        asks whether the per-run keyed digest of the exact triple
        ``(event.kind, event.timestamp, event.raw_line)`` has already been
        staged for ``event.source_file`` within the current transaction.
        Comparisons are over the digest of the exact identity - within the
        practical collision resistance of keyed HMAC-SHA256, digest
        equality is exact identity. Because the query runs inside the same
        per-file transaction as the staging itself, a rolled-back UTF-8
        attempt automatically discards both its events and the duplicate
        knowledge they carried; the Latin-1 retry starts clean (with the
        same per-run key).

        Callers must invoke this BEFORE staging the event it is asked
        about (the streaming parser does: the check precedes the yield,
        staging happens after).
        """
        row = self._conn.execute(
            "SELECT 1 FROM events WHERE kind = ? AND timestamp = ?"
            " AND fp_digest = ? AND source_file = ? LIMIT 1",
            (event.kind, event.timestamp, self._event_fingerprint(event),
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
            "SELECT seq, kind, timestamp, raw_timestamp, evidence_line,"
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

        For every fingerprint ``(kind, timestamp, fp_digest)`` - the
        per-run keyed digest of the exact identity triple (M1):

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
                               PARTITION BY e.kind, e.timestamp, e.fp_digest
                               ORDER BY e.seq) AS rn
                    FROM events e
                    JOIN (
                        SELECT kind, timestamp, fp_digest, MAX(cnt) AS cap
                        FROM (
                            SELECT kind, timestamp, fp_digest, source_file,
                                   COUNT(*) AS cnt
                            FROM events
                            GROUP BY kind, timestamp, fp_digest, source_file
                        )
                        GROUP BY kind, timestamp, fp_digest
                    ) c
                      ON e.kind = c.kind
                     AND e.timestamp = c.timestamp
                     AND e.fp_digest = c.fp_digest
                )
                WHERE rn > cap
            )
            """)
        after = self._conn.execute(
            "SELECT COUNT(*) FROM events").fetchone()[0]
        return before - after


def _row_to_event(row: tuple) -> SecurityEvent:
    """Reconstruct the original validated event object from a stored row.

    M1: the stored ``evidence_line`` is the sanitized original line; it is
    mapped into the in-memory ``raw_line`` slot so detectors' evidence
    paths work unchanged. The reconstruction never sees the original
    plaintext line, which was never persisted.
    """
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
