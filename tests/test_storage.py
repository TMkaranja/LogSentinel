"""Unit and integration tests for SQLite-backed staging (Phase 5, spec 3.11)."""

import hashlib
import hmac
import os
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

from logsentinel.events import (
    ErrorEntry,
    FileStats,
    FirewallEvent,
    HTTPRequestEvent,
    SSHAuthEvent,
    SyslogEvent,
    _sanitize,
)
from logsentinel.storage import (
    MAX_REPORTED_ERRORS_STORAGE,
    RunStorage,
    _event_fingerprint,
)


def ssh(ts=100, line="ssh-line-a", source="a.log", ip="192.0.2.7",
        user="root", success=False):
    return SSHAuthEvent(timestamp=ts, raw_timestamp="Mar 10 11:20:01",
                        raw_line=line, source_file=source, src_ip=ip,
                        username=user, success=success)


def fw(ts=200, line="fw-line", source="b.log", ip="198.51.100.23",
       dport=22, proto="TCP"):
    return FirewallEvent(timestamp=ts, raw_timestamp="Mar 10 09:00:01",
                         raw_line=line, source_file=source, src_ip=ip,
                         dst_ip="203.0.113.10", dst_port=dport,
                         protocol=proto)


def http(ts=300, line="http-line", source="c.log", ip="203.0.113.50",
         path="/x", status=404):
    return HTTPRequestEvent(timestamp=ts, raw_timestamp="ts", raw_line=line,
                            source_file=source, src_ip=ip, method="GET",
                            path=path, status_code=status)


def syslog(ts=400, line="syslog-line", source="d.log"):
    return SyslogEvent(timestamp=ts, raw_timestamp="Mar 10 10:00:00",
                       raw_line=line, source_file=source)


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def storage(self):
        return RunStorage(directory=str(self.tmp))


class TestLifecycle(StorageTestCase):
    def test_database_lives_outside_project_tree(self):
        with self.storage() as store:
            self.assertNotIn(os.getcwd(), store.path)
            self.assertTrue(os.path.exists(store.path))
        self.assertFalse(os.path.exists(store.path))

    def test_cleanup_after_success(self):
        with self.storage() as store:
            store.stage_event(ssh())
            store.begin()
            store.commit()
            path = store.path
        self.assertFalse(os.path.exists(path))

    def test_cleanup_after_exception(self):
        store_ref = None
        with self.assertRaises(RuntimeError):
            with self.storage() as store:
                store_ref = store
                store.stage_event(ssh())
                raise RuntimeError("boom")
        self.assertIsNotNone(store_ref)
        self.assertFalse(os.path.exists(store_ref.path))

    def test_cleanup_after_sqlite_exception(self):
        store_ref = None
        with self.assertRaises(Exception):
            with self.storage() as store:
                store_ref = store
                store.begin()
                store.begin()  # nested BEGIN -> sqlite3.OperationalError
        self.assertFalse(os.path.exists(store_ref.path))


class TestEventSerialization(StorageTestCase):
    def test_roundtrip_all_event_types(self):
        expected = [ssh(), ssh(ts=101, success=True, user="deploy"),
                    fw(), fw(ts=201, dport=8080, proto="UDP"),
                    http(), http(ts=301, path="/admin", status=403),
                    syslog()]
        with self.storage() as store:
            for event in expected:
                store.stage_event(event)
            got = list(store.iter_events())
        self.assertEqual(got, expected)

    def test_unsupported_event_kind_rejected(self):
        with self.storage() as store:
            with self.assertRaises((ValueError, AttributeError)):
                store.stage_event(object())  # type: ignore[arg-type]


class TestTransactions(StorageTestCase):
    def test_rollback_discards_staged_rows(self):
        with self.storage() as store:
            store.begin()
            store.stage_event(ssh())
            store.rollback()
            self.assertEqual(list(store.iter_events()), [])

    def test_commit_persists_staged_rows(self):
        with self.storage() as store:
            store.begin()
            store.stage_event(ssh())
            store.commit()
            self.assertEqual(len(list(store.iter_events())), 1)

    def test_staging_outside_transaction_autocommits(self):
        with self.storage() as store:
            store.stage_event(ssh())
            store.begin()
            store.commit()
            self.assertEqual(len(list(store.iter_events())), 1)


class TestCrossFileDedup(StorageTestCase):
    def stage_fingerprints(self, store, plan):
        """plan: list of (file, count, ts) for one shared fingerprint."""
        for file, count, ts in plan:
            for _ in range(count):
                store.stage_event(ssh(ts=ts, line="same raw line",
                                      source=file))

    def test_example_one_three_two_one(self):
        with self.storage() as store:
            self.stage_fingerprints(store, [("A", 3, 10), ("B", 2, 10),
                                            ("C", 1, 10)])
            removed = store.dedup_cross_file()
            kept = list(store.iter_events())
        self.assertEqual(removed, 3)          # spec 3.4 example 1
        self.assertEqual(len(kept), 3)
        self.assertEqual([e.source_file for e in kept],
                         ["A", "A", "A"])     # earliest occurrences first

    def test_example_two_two_three_one(self):
        with self.storage() as store:
            self.stage_fingerprints(store, [("A", 2, 10), ("B", 3, 10),
                                            ("C", 1, 10)])
            removed = store.dedup_cross_file()
            kept = list(store.iter_events())
        self.assertEqual(removed, 3)          # spec 3.4 example 2
        self.assertEqual(len(kept), 3)
        self.assertEqual([e.source_file for e in kept],
                         ["A", "A", "B"])     # earliest in ingestion order

    def test_same_file_repeats_fully_preserved(self):
        with self.storage() as store:
            self.stage_fingerprints(store, [("A", 5, 10)])
            removed = store.dedup_cross_file()
            kept = list(store.iter_events())
        self.assertEqual(removed, 0)
        self.assertEqual(len(kept), 5)

    def test_distinct_fingerprints_never_collapsed(self):
        with self.storage() as store:
            store.stage_event(ssh(ts=10, line="line one", source="A"))
            store.stage_event(ssh(ts=10, line="line two", source="A"))
            store.stage_event(ssh(ts=11, line="line one", source="B"))
            removed = store.dedup_cross_file()
        self.assertEqual(removed, 0)   # fingerprint is exact, never a hash

    def test_dedup_is_idempotent(self):
        with self.storage() as store:
            self.stage_fingerprints(store, [("A", 3, 10), ("B", 2, 10)])
            first = store.dedup_cross_file()
            second = store.dedup_cross_file()
        self.assertEqual((first, second), (2, 0))

    def test_dedup_spans_many_fingerprints_and_files(self):
        with self.storage() as store:
            # fp1: A1 B1 C1 -> cap 1, removed 2; fp2: A2 B1 -> cap 2, removed 0
            store.stage_event(ssh(ts=1, line="fp1", source="A"))
            store.stage_event(ssh(ts=2, line="fp2", source="A"))
            store.stage_event(ssh(ts=3, line="fp2", source="A"))
            store.stage_event(ssh(ts=1, line="fp1", source="B"))
            store.stage_event(ssh(ts=2, line="fp2", source="B"))
            store.stage_event(ssh(ts=1, line="fp1", source="C"))
            removed = store.dedup_cross_file()
            kept = list(store.iter_events())
        self.assertEqual(removed, 3)     # fp1: -2, fp2: -1
        self.assertEqual(len(kept), 3)   # fp1 earliest + fp2 x2 (cap 2)
        self.assertEqual([e.raw_line for e in kept],
                         ["fp1", "fp2", "fp2"])


class TestOrdering(StorageTestCase):
    def test_ingestion_order_preserved(self):
        with self.storage() as store:
            store.stage_event(fw(ts=5, line="early"))
            store.stage_event(ssh(ts=4, line="mid"))
            store.stage_event(syslog(ts=3, line="late"))
            got = [e.raw_line for e in store.iter_events()]
        self.assertEqual(got, ["early", "mid", "late"])  # FR-111 base order

    def test_equal_timestamp_and_kind_stability(self):
        with self.storage() as store:
            for n in range(5):
                store.stage_event(ssh(ts=99, line=f"n{n}", source="A"))
            got = [e.raw_line for e in store.iter_events()]
        self.assertEqual(got, [f"n{n}" for n in range(5)])


class TestErrorStaging(StorageTestCase):
    def test_errors_in_original_order_with_exact_total(self):
        with self.storage() as store:
            for n in range(150):
                store.stage_error(ErrorEntry(
                    source_file=f"f{n}.log", line_number=n,
                    reason=f"reason {n}", kind="parse"))
            entries, total = store.error_summary()
        self.assertEqual(total, 150)                       # exact total
        self.assertEqual(len(entries), MAX_REPORTED_ERRORS_STORAGE)
        self.assertEqual(entries[0].reason, "reason 0")    # original order
        self.assertEqual(entries[99].reason, "reason 99")
        self.assertEqual(entries[0].kind, "parse")

    def test_fewer_errors_than_cap(self):
        with self.storage() as store:
            store.stage_error(ErrorEntry("a.log", 3, "r", "input"))
            entries, total = store.error_summary()
        self.assertEqual((total, len(entries)), (1, 1))
        self.assertEqual(entries[0].kind, "input")

    def test_discovery_errors_come_first(self):
        with self.storage() as store:
            store.stage_error(ErrorEntry("input-path", None, "missing",
                                         "input"))
            store.stage_error(ErrorEntry("f.log", 1, "parse", "parse"))
            entries, _ = store.error_summary()
        self.assertEqual(entries[0].kind, "input")   # staged first


class TestStatistics(StorageTestCase):
    def test_statistics_sums_and_files_scanned(self):
        with self.storage() as store:
            store.stage_file_stats("a.log", FileStats(
                lines_read=10, events_parsed=7, malformed=2, duplicates=1,
                othersyslog=1, othersyslog_dropped=1))
            store.stage_file_stats("b.log", FileStats(
                lines_read=5, events_parsed=3, malformed=1, duplicates=0,
                othersyslog=1, othersyslog_dropped=1))
            sums = store.statistics_sums()
        self.assertEqual(sums["files_scanned"], 2)
        self.assertEqual(sums["lines_read"], 15)
        self.assertEqual(sums["events_parsed"], 10)
        self.assertEqual(sums["malformed"], 3)
        self.assertEqual(sums["duplicates"], 1)
        self.assertEqual(sums["othersyslog"], 2)
        self.assertEqual(sums["othersyslog_dropped"], 2)
        # Parser invariant holds per file and in aggregate:
        self.assertEqual(sums["malformed"] + sums["events_parsed"]
                         + sums["othersyslog_dropped"], sums["lines_read"])

    def test_empty_storage_zero_statistics(self):
        with self.storage() as store:
            sums = store.statistics_sums()
        self.assertEqual(sums["files_scanned"], 0)
        self.assertEqual(sums["lines_read"], 0)


class _FakeConnection:
    """Minimal connection double for constructor-failure tests."""

    def __init__(self, fail_on: str, message: str):
        self._fail_on = fail_on
        self._message = message
        self.closed = False

    def execute(self, sql, *args, **kwargs):
        if self._fail_on == "pragma" and "PRAGMA" in sql:
            raise sqlite3.OperationalError(self._message)
        return None

    def executescript(self, script):
        if self._fail_on == "schema":
            raise sqlite3.OperationalError(self._message)

    def close(self):
        self.closed = True


def _failing_storage_module(fail_on: str, message: str):
    """Patch storage's sqlite3 reference with a connect that fails later."""
    fake = SimpleNamespace(
        connect=lambda path, isolation_level=None:
            _FakeConnection(fail_on, message),
        OperationalError=sqlite3.OperationalError)
    return mock.patch("logsentinel.storage.sqlite3", fake)


class TestConstructorFailure(StorageTestCase):
    """Phase 5 correction: exception-safe initialization and cleanup."""

    def test_connect_failure_after_tempdir_creation_cleans_up(self):
        created_dirs = []
        real_mkdtemp = tempfile.mkdtemp

        def spy_mkdtemp(*args, **kwargs):
            directory = real_mkdtemp(*args, **kwargs)
            created_dirs.append(directory)
            return directory

        with mock.patch("tempfile.mkdtemp", spy_mkdtemp), \
                mock.patch("logsentinel.storage.sqlite3.connect",
                           side_effect=sqlite3.OperationalError(
                               "disk I/O error")):
            with self.assertRaises(sqlite3.OperationalError):
                RunStorage()
        # Original exception preserved; owned temp dir removed.
        self.assertTrue(created_dirs)
        self.assertTrue(all(not os.path.exists(d) for d in created_dirs))

    def test_pragma_failure_cleans_up(self):
        created_dirs = []
        real_mkdtemp = tempfile.mkdtemp

        def spy_mkdtemp(*args, **kwargs):
            directory = real_mkdtemp(*args, **kwargs)
            created_dirs.append(directory)
            return directory

        with mock.patch("tempfile.mkdtemp", spy_mkdtemp), \
                _failing_storage_module("pragma", "pragma rejected"):
            with self.assertRaises(sqlite3.OperationalError):
                RunStorage()
        self.assertTrue(created_dirs)
        self.assertTrue(all(not os.path.exists(d) for d in created_dirs))

    def test_schema_failure_cleans_up(self):
        created_dirs = []
        real_mkdtemp = tempfile.mkdtemp

        def spy_mkdtemp(*args, **kwargs):
            directory = real_mkdtemp(*args, **kwargs)
            created_dirs.append(directory)
            return directory

        with mock.patch("tempfile.mkdtemp", spy_mkdtemp), \
                _failing_storage_module("schema", "schema boom"):
            with self.assertRaises(sqlite3.OperationalError):
                RunStorage()
        self.assertTrue(created_dirs)
        self.assertTrue(all(not os.path.exists(d) for d in created_dirs))

    def test_failure_with_caller_directory_keeps_caller_directory(self):
        staging = self.tmp / "staging"
        staging.mkdir()   # caller-owned directory must pre-exist
        with mock.patch("logsentinel.storage.sqlite3.connect",
                        side_effect=sqlite3.OperationalError("boom")):
            with self.assertRaises(sqlite3.OperationalError):
                RunStorage(directory=str(staging))
        # A caller-supplied directory is never removed by cleanup...
        self.assertTrue(staging.exists())
        # ...but the database file inside it is gone.
        self.assertFalse((staging / "staging.sqlite3").exists())


class TestCleanupObservability(StorageTestCase):
    """Cleanup failures are recorded, never raised, never silent."""

    def test_database_removal_failure_recorded(self):
        staging = self.tmp / "obs"
        staging.mkdir()
        store = RunStorage(directory=str(staging))
        path = store.path
        try:
            with mock.patch("logsentinel.storage.os.remove",
                            side_effect=OSError(13, "Permission denied")):
                store.close()
        finally:
            if os.path.exists(path):
                os.remove(path)
        self.assertTrue(store.cleanup_errors)
        self.assertIn("database removal", store.cleanup_errors[0])
        self.assertTrue(store.cleanup_errors[0].startswith(
            "database removal"))

    def test_directory_removal_failure_recorded(self):
        store = RunStorage()  # owned temp directory
        directory = store._dir
        real_remove = os.remove
        try:
            with mock.patch("logsentinel.storage.os.remove", real_remove), \
                    mock.patch("logsentinel.storage.os.rmdir",
                               side_effect=OSError(13, "Permission denied")):
                store.close()
        finally:
            if os.path.exists(store.path):
                os.remove(store.path)
            if os.path.exists(directory):
                os.rmdir(directory)
        self.assertTrue(store.cleanup_errors)
        self.assertIn("directory removal", store.cleanup_errors[0])

    def test_successful_cleanup_records_no_errors(self):
        with self.storage() as store:
            store.stage_event(ssh())
        self.assertEqual(store.cleanup_errors, [])

    def test_close_is_idempotent(self):
        store = self.storage()
        store.close()
        store.close()   # second close must not raise or duplicate work
        self.assertEqual(store.cleanup_errors, [])


class TestFingerprintSeen(StorageTestCase):
    """Exact, per-file, transaction-bound duplicate tracking."""

    def test_exact_fingerprint_check_per_file(self):
        with self.storage() as store:
            store.stage_event(ssh(ts=10, line="L", source="A"))
            self.assertTrue(store.fingerprint_seen(
                ssh(ts=10, line="L", source="A")))
            # Same triple in a different file: NOT seen (per-file tracking).
            self.assertFalse(store.fingerprint_seen(
                ssh(ts=10, line="L", source="B")))
            # Exact triple identity: timestamp and raw_line both matter.
            self.assertFalse(store.fingerprint_seen(
                ssh(ts=11, line="L", source="A")))
            self.assertFalse(store.fingerprint_seen(
                ssh(ts=10, line="other", source="A")))

    def test_rollback_discards_fingerprint_knowledge(self):
        with self.storage() as store:
            store.begin()
            store.stage_event(ssh(ts=10, line="L", source="A"))
            store.rollback()
            store.begin()
            # The rolled-back attempt's duplicate knowledge is gone.
            self.assertFalse(store.fingerprint_seen(
                ssh(ts=10, line="L", source="A")))
            store.commit()

    def test_uncommitted_transaction_rows_are_visible(self):
        with self.storage() as store:
            store.begin()
            store.stage_event(ssh(ts=10, line="L", source="A"))
            # Inside the same transaction the row is already trackable.
            self.assertTrue(store.fingerprint_seen(
                ssh(ts=10, line="L", source="A")))
            store.rollback()


class TestHmacFingerprints(StorageTestCase):
    """M1: per-run HMAC fingerprints and sanitized evidence at rest."""

    KEY = b"\x01" * 32

    def test_schema_has_evidence_and_digest_no_raw_line(self):
        with self.storage() as store:
            cols = [r[1] for r in store._conn.execute(
                "PRAGMA table_info(events)")]
            self.assertIn("evidence_line", cols)
            self.assertIn("fp_digest", cols)
            self.assertNotIn("raw_line", cols)
            indexes = {r[1]: r[2] for r in store._conn.execute(
                "PRAGMA index_list(events)")}
            self.assertIn("idx_events_fp", indexes)
            sql = store._conn.execute(
                "SELECT sql FROM sqlite_master WHERE name='idx_events_fp'"
            ).fetchone()[0]
            self.assertIn("fp_digest", sql)
            self.assertNotIn("raw_line", sql)

    def test_no_raw_line_column_in_any_statement(self):
        # Every CREATE statement and index is free of a raw_line reference.
        with self.storage() as store:
            for (sql,) in store._conn.execute(
                    "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"):
                self.assertNotIn("raw_line", sql)

    def test_staging_stores_digest_and_sanitized_evidence(self):
        with self.storage() as store:
            event = ssh(ts=10, line="Failed password token=abc123",
                        source="A")
            original_line = event.raw_line
            store.stage_event(event)
            row = store._conn.execute(
                "SELECT evidence_line, fp_digest FROM events").fetchone()
            self.assertIn("<REDACTED>", row[0])
            self.assertNotIn("abc123", row[0])
            self.assertEqual(len(row[1]), 32)
            self.assertIsInstance(row[1], bytes)
            # The caller's event object is not mutated.
            self.assertEqual(event.raw_line, original_line)
            # The original plaintext never reached the database file.
            with open(store.path, "rb") as handle:
                db_bytes = handle.read()
            self.assertNotIn(b"abc123", db_bytes)

    def test_distinct_raw_lines_identical_parsed_fields_distinct(self):
        with self.storage() as store:
            first = ssh(ts=10, line="first attempt", source="A")
            second = ssh(ts=10, line="second attempt", source="A")
            store.stage_event(first)
            store.stage_event(second)
            self.assertFalse(store.fingerprint_seen(
                ssh(ts=10, line="third attempt", source="A")))
            events = list(store.iter_events())
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0].raw_line, "first attempt")
            self.assertEqual(events[1].raw_line, "second attempt")
            digests = store._conn.execute(
                "SELECT fp_digest FROM events ORDER BY seq").fetchall()
            self.assertNotEqual(digests[0][0], digests[1][0])

    def test_unambiguous_encoding_adversarial_strings(self):
        # With length prefixes, these pairs - which collide under naive
        # delimiter-only concatenation - produce distinct digests.
        pairs = [
            # ("web", 12, "a") vs ("web", 1, "2\x1fa"): same joined bytes.
            (("web", 12, "a"), ("web", 1, "2\x1fa")),
            # kind/raw_line boundary shift: ("a\x00b", ...) style.
            (("authfail", 5, "x"), ("authfail\x00", 5, "")),
        ]
        for a, b in pairs:
            da = _event_fingerprint(self.KEY, *a)
            db = _event_fingerprint(self.KEY, *b)
            self.assertNotEqual(da, db, f"collision for {a!r} vs {b!r}")
        # Domain separation: a different domain prefix changes the digest.
        self.assertNotEqual(
            _event_fingerprint(self.KEY, "web", 12, "a"),
            hmac.new(self.KEY, b"other-domain\x00web|12|a",
                     hashlib.sha256).digest())

    def test_fresh_key_per_instance(self):
        event = ssh(ts=10, line="L", source="A")
        with self.storage() as first:
            first.stage_event(event)
            d1 = first._conn.execute(
                "SELECT fp_digest FROM events").fetchone()[0]
        with self.storage() as second:
            # A fresh instance knows nothing of the previous run's events.
            self.assertFalse(second.fingerprint_seen(event))
            second.stage_event(event)
            d2 = second._conn.execute(
                "SELECT fp_digest FROM events").fetchone()[0]
            # Fresh key: the same event digests differently across runs.
            self.assertNotEqual(d1, d2)

    def test_same_key_survives_rollback_and_retry(self):
        event = ssh(ts=10, line="L", source="A")
        with self.storage() as store:
            store.begin()
            store.stage_event(event)
            d1 = store._conn.execute(
                "SELECT fp_digest FROM events").fetchone()[0]
            store.rollback()
            # UTF-8-retry-style re-attempt: same instance, same key.
            store.begin()
            store.stage_event(event)
            d2 = store._conn.execute(
                "SELECT fp_digest FROM events").fetchone()[0]
            store.commit()
            self.assertEqual(d1, d2)
            self.assertTrue(store.fingerprint_seen(event))

    def test_key_not_persisted_or_exposed(self):
        with self.storage() as store:
            key = store._hmac_key
            self.assertEqual(len(key), 32)
            store.stage_event(ssh(ts=10, line="token=abc123", source="A"))
            with open(store.path, "rb") as handle:
                db_bytes = handle.read()
            self.assertNotIn(key, db_bytes)
            # Neither the key nor derived material leaks through observable
            # structures (cleanup errors, module state).
            self.assertEqual(store.cleanup_errors, [])
            self.assertNotIn(repr(key), repr(store))
        # The instance state dies with the instance: no module-level key.
        import logsentinel.storage as storage_module
        module_keys = [v for v in vars(storage_module).values()
                       if isinstance(v, bytes) and len(v) == 32]
        self.assertEqual(module_keys, [])

    def test_reconstructed_events_carry_sanitized_evidence(self):
        with self.storage() as store:
            store.stage_event(ssh(ts=10, line="pwd=hunter2 failed",
                                  source="A"))
            store.stage_event(ssh(ts=11, line="plain failure", source="A"))
            events = list(store.iter_events())
        self.assertEqual(events[0].raw_line, "pwd=<REDACTED> failed")
        self.assertNotIn("hunter2", events[0].raw_line)
        # Non-sensitive evidence passes through unchanged.
        self.assertEqual(events[1].raw_line, "plain failure")

    def test_sanitizer_idempotence_over_corpus(self):
        from tests.test_report import TestRedactionAndCapping
        for fixture in TestRedactionAndCapping.FIXTURES:
            once = _sanitize(fixture)
            self.assertEqual(once, _sanitize(once), f"not idempotent: {fixture!r}")
        # Round-trip through storage: staged evidence re-sanitized is stable.
        with self.storage() as store:
            store.stage_event(ssh(ts=10, line="Authorization: Bearer tok",
                                  source="A"))
            store.stage_event(ssh(ts=11, line="password=p1 secret=s2",
                                  source="A"))
            for event in store.iter_events():
                self.assertEqual(event.raw_line, _sanitize(event.raw_line))

    def test_dedup_uses_digest_partition(self):
        # Cross-file multiplicity semantics preserved under digest identity.
        with self.storage() as store:
            store.stage_event(ssh(ts=10, line="D", source="A"))
            store.stage_event(ssh(ts=10, line="D", source="A"))
            store.stage_event(ssh(ts=10, line="D", source="B"))
            # cap = max single-file count = 2; 3 occurrences -> 1 removed
            # (the beyond-cap B occurrence; earliest retained).
            removed = store.dedup_cross_file()
            self.assertEqual(removed, 1)
            self.assertEqual(store._conn.execute(
                "SELECT COUNT(*) FROM events").fetchone()[0], 2)
        with self.storage() as store:
            store.stage_event(ssh(ts=10, line="D", source="A"))
            store.stage_event(ssh(ts=10, line="E", source="A"))
            store.stage_event(ssh(ts=10, line="D", source="B"))
            store.stage_event(ssh(ts=10, line="E", source="B"))
            # Same parsed fields, different raw lines: distinct identities.
            # Each identity occurs once per file -> cap 1 -> 2 removed
            # (earliest occurrences retained).
            self.assertEqual(store.dedup_cross_file(), 2)
            self.assertEqual(store._conn.execute(
                "SELECT COUNT(*) FROM events").fetchone()[0], 2)


if __name__ == "__main__":
    unittest.main()
