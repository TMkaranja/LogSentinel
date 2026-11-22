"""Unit tests for the LogSentinel event model (Phase 3 matrix TC-E01..TC-E03)."""

import dataclasses
import unittest
from dataclasses import FrozenInstanceError

from logsentinel.events import (
    ErrorEntry,
    FileStats,
    Finding,
    FirewallEvent,
    HTTPRequestEvent,
    SSHAuthEvent,
    SyslogEvent,
    dedup_cross_file,
    events_by_src_ip,
    fingerprint,
)


def ssh(ts=100, ip="192.0.2.7", user="admin", ok=False, line="line",
        source_file="f"):
    return SSHAuthEvent(timestamp=ts, raw_timestamp="raw", raw_line=line,
                        source_file=source_file, src_ip=ip, username=user,
                        success=ok)


def fw(ts=100, ip="192.0.2.7", port=22, dst="203.0.113.10", proto="TCP",
       line="line", source_file="f"):
    return FirewallEvent(timestamp=ts, raw_timestamp="raw", raw_line=line,
                         source_file=source_file, src_ip=ip, dst_ip=dst,
                         dst_port=port, protocol=proto)


def web(ts=100, ip="192.0.2.7", status=404, path="/a", method="GET", line="line"):
    return HTTPRequestEvent(timestamp=ts, raw_timestamp="raw", raw_line=line,
                            source_file="f", src_ip=ip, method=method,
                            path=path, status_code=status)


class TestEventConstruction(unittest.TestCase):
    """TC-E01: construction of every event kind and its invariants."""

    def test_ssh_kind_vocabulary(self):
        self.assertEqual(ssh(ok=False).kind, "authfail")
        self.assertEqual(ssh(ok=True).kind, "authok")

    def test_firewall_and_web_kinds(self):
        self.assertEqual(fw().kind, "fwconn")
        self.assertEqual(web().kind, "web")
        self.assertEqual(SyslogEvent(
            timestamp=1, raw_timestamp="r", raw_line="l", source_file="f"
        ).kind, "othersyslog")

    def test_events_are_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            ssh().timestamp = 5
        with self.assertRaises(FrozenInstanceError):
            web().src_ip = "192.0.2.9"

    def test_raw_line_trailing_crlf_normalized(self):
        event = ssh(line="a line\r\n")
        self.assertEqual(event.raw_line, "a line")

    def test_finding_severities_is_class_variable(self):
        """Regression: _SEVERITIES must not be an instance field (Phase 4.1)."""
        names = [f.name for f in dataclasses.fields(Finding)]
        self.assertNotIn("_SEVERITIES", names)
        with self.assertRaises(TypeError):
            Finding("LS-RULE-001", "high", "192.0.2.7", 1, 2, (), {},
                    frozenset({"low"}))

    def test_finding_invariants(self):
        f = Finding(rule_id="LS-RULE-001", severity="high", src_ip="192.0.2.7",
                    first_seen=10, last_seen=20, evidence=("a",),
                    summary={"failed_count": 1})
        self.assertEqual(f.rule_id, "LS-RULE-001")
        with self.assertRaises(ValueError):
            Finding("LS-RULE-009", "high", "192.0.2.7", 1, 0)
        with self.assertRaises(ValueError):
            Finding("LS-RULE-001", "critical", "192.0.2.7", 1, 2)
        with self.assertRaises(ValueError):
            Finding("LS-RULE-001", "high", "not-an-ip", 1, 2)


class TestEventValidation(unittest.TestCase):
    """TC-E02: invalid fields are rejected at construction (FR-114)."""

    def test_invalid_source_ip(self):
        for bad in ("999.1.1.1", "not-an-ip", "2001:db8::1", "", "01.2.3.4"):
            with self.assertRaises(ValueError):
                ssh(ip=bad)

    def test_invalid_destination_port(self):
        for bad in (0, -1, 65536, 70000):
            with self.assertRaises(ValueError):
                fw(port=bad)

    def test_invalid_status_code(self):
        for bad in (99, 600, 999):
            with self.assertRaises(ValueError):
                web(status=bad)

    def test_invalid_timestamp(self):
        for bad in (-1, 1.5, "10", True):
            with self.assertRaises(ValueError):
                ssh(ts=bad)

    def test_invalid_method_and_path(self):
        with self.assertRaises(ValueError):
            web(method="get")
        with self.assertRaises(ValueError):
            web(method="GET2")
        with self.assertRaises(ValueError):
            web(path="")


class TestCrossFileDeduplication(unittest.TestCase):
    """AR-005 final / Phase 4.1: cross-file-only deduplication."""

    def test_intra_file_repeats_preserved(self):
        """Identical events repeated within one file are never collapsed."""
        events = [ssh(line="Mar 10 11:20:01 sshd: Failed password for admin",
                      source_file="a"),
                  ssh(line="Mar 10 11:20:01 sshd: Failed password for admin",
                      source_file="a")]
        kept, cross = dedup_cross_file(events)
        self.assertEqual((len(kept), cross), (2, 0))
        self.assertEqual([e.source_file for e in kept], ["a", "a"])

    def test_identical_events_across_two_files_collapse(self):
        events = [ssh(line="same record", source_file="a"),
                  ssh(line="same record", source_file="b")]
        kept, cross = dedup_cross_file(events)
        self.assertEqual((len(kept), cross), (1, 1))
        self.assertEqual(kept[0].source_file, "a")  # first occurrence wins

    def test_identical_events_across_three_files_consistent(self):
        """Events in 3+ files collapse consistently (multiplicity-aware).

        Occurrences: a=2, b=1, c=1 -> cap = max(2, 1, 1) = 2; the first two
        occurrences in input order are retained (a, b), the rest removed.
        """
        events = [ssh(line="same record", source_file="a"),
                  ssh(line="same record", source_file="b"),
                  ssh(line="same record", source_file="c"),
                  ssh(line="same record", source_file="a")]  # intra repeat
        kept, removed = dedup_cross_file(events)
        self.assertEqual((len(kept), removed), (2, 2))
        self.assertEqual([e.source_file for e in kept], ["a", "b"])

    def test_different_events_sharing_timestamp_kept(self):
        """Different raw lines at the same second are distinct events."""
        events = [ssh(ts=5, line="failed attempt one"),
                  fw(ts=5, line="dropped packet"),
                  web(ts=5, line="GET /admin 403")]
        kept, cross = dedup_cross_file(events)
        self.assertEqual((len(kept), cross), (3, 0))
        self.assertEqual([e.kind for e in kept],
                         ["authfail", "fwconn", "web"])

    def test_ordering_preserved_after_dedup(self):
        events = [ssh(ts=3, line="c"),
                  ssh(ts=1, line="a"),
                  ssh(ts=2, line="b"),
                  ssh(ts=3, line="c", source_file="other")]
        kept, cross = dedup_cross_file(events)
        self.assertEqual([e.raw_line for e in kept], ["c", "a", "b"])
        self.assertEqual(cross, 1)

    def test_statistics_without_double_counting(self):
        """Intra-file repeats are kept (not counted as cross-file collapses)."""
        events = [ssh(line="x", source_file="a"),
                  ssh(line="x", source_file="a"),
                  ssh(line="x", source_file="a"),
                  ssh(line="x", source_file="b")]
        kept, cross = dedup_cross_file(events)
        self.assertEqual((len(kept), cross), (3, 1))

    def test_reversed_file_order_keeps_that_files_record(self):
        """Determinism: the first file in input order becomes the origin."""
        events = [ssh(line="same", source_file="b"),
                  ssh(line="same", source_file="a")]
        kept, cross = dedup_cross_file(events)
        self.assertEqual(kept[0].source_file, "b")
        self.assertEqual(cross, 1)


class TestMultiplicityAwareDeduplication(unittest.TestCase):
    """Phase 4.1 review: retain max single-file multiplicity per fingerprint."""

    def test_file_a_one_file_b_two_retains_two_removes_one(self):
        events = [ssh(line="r", source_file="a"),
                  ssh(line="r", source_file="b"),
                  ssh(line="r", source_file="b")]
        kept, removed = dedup_cross_file(events)
        self.assertEqual((len(kept), removed), (2, 1))
        self.assertEqual([e.source_file for e in kept], ["a", "b"])

    def test_file_a_two_file_b_one_retains_two_removes_one(self):
        events = [ssh(line="r", source_file="a"),
                  ssh(line="r", source_file="a"),
                  ssh(line="r", source_file="b")]
        kept, removed = dedup_cross_file(events)
        self.assertEqual((len(kept), removed), (2, 1))
        self.assertEqual([e.source_file for e in kept], ["a", "a"])

    def test_three_files_with_different_counts(self):
        """a=1, b=2, c=3 -> cap 3; first three occurrences kept, three removed."""
        events = [ssh(line="r", source_file="a"),
                  ssh(line="r", source_file="b"),
                  ssh(line="r", source_file="b"),
                  ssh(line="r", source_file="c"),
                  ssh(line="r", source_file="c"),
                  ssh(line="r", source_file="c")]
        kept, removed = dedup_cross_file(events)
        self.assertEqual((len(kept), removed), (3, 3))
        self.assertEqual([e.source_file for e in kept], ["a", "b", "b"])

    def test_interleaved_records_from_multiple_files(self):
        """Interleaving does not change the deterministic outcome."""
        events = [ssh(line="r", source_file="a"),
                  ssh(line="r", source_file="b"),
                  ssh(line="r", source_file="b"),
                  ssh(line="r", source_file="a"),
                  ssh(line="r", source_file="c"),
                  ssh(line="r", source_file="c"),
                  ssh(line="r", source_file="c")]
        kept, removed = dedup_cross_file(events)
        self.assertEqual((len(kept), removed), (3, 4))
        self.assertEqual([e.source_file for e in kept], ["a", "b", "b"])

    def test_different_fingerprints_remain_independent(self):
        events = [ssh(ts=1, line="alpha", source_file="a"),
                  ssh(ts=1, line="beta", source_file="b"),
                  ssh(ts=2, line="alpha", source_file="a"),
                  fw(ts=3, line="alpha", source_file="c")]
        kept, removed = dedup_cross_file(events)
        self.assertEqual((len(kept), removed), (4, 0))

    def test_removal_count_is_exact(self):
        """Six distinct files, one occurrence each -> cap 1 -> five removals."""
        events = [ssh(line="r", source_file="a")]
        events += [ssh(line="r", source_file=f)
                   for f in ("b", "c", "d", "e", "f")]
        kept, removed = dedup_cross_file(events)
        self.assertEqual((len(kept), removed), (1, 5))
        self.assertEqual(kept[0].source_file, "a")
        self.assertEqual(len(events), len(kept) + removed)


class TestGrouping(unittest.TestCase):
    """TC-D05 support: events_by_src_ip contract (FR-034, FR-111)."""

    def test_group_and_sort(self):
        events = [ssh(ts=20), fw(ts=10), web(ts=20),
                  SyslogEvent(timestamp=1, raw_timestamp="", raw_line="x",
                              source_file="f")]
        groups = events_by_src_ip(events)
        self.assertEqual(list(groups), ["192.0.2.7"])
        # Contract: stable sort by (timestamp, kind) -- FR-111.
        kinds = [(e.timestamp, e.kind) for e in groups["192.0.2.7"]]
        self.assertEqual(kinds, [(10, "fwconn"), (20, "authfail"), (20, "web")])

    def test_empty_input(self):
        self.assertEqual(events_by_src_ip([]), {})


class TestBookkeepingStructures(unittest.TestCase):
    def test_error_entry_defaults(self):
        e = ErrorEntry(source_file="f", line_number=3, reason="boom")
        self.assertEqual(e.kind, "parse")

    def test_file_stats_defaults(self):
        s = FileStats()
        self.assertEqual((s.lines_read, s.events_parsed, s.malformed,
                          s.duplicates, s.othersyslog, s.othersyslog_dropped),
                         (0, 0, 0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
