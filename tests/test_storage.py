"""Unit and integration tests for SQLite-backed staging (Phase 5, spec 3.11)."""

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
)
from logsentinel.storage import MAX_REPORTED_ERRORS_STORAGE, RunStorage


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


if __name__ == "__main__":
    unittest.main()
