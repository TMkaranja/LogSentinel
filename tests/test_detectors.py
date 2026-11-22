"""Unit tests for the LogSentinel detection engine (Phase 4.3).

Covers docs/DETECTION_RULES.md rules LS-RULE-001/002/003 and the Phase 3
testing matrix (TC-D01..TC-D06). All timestamps are fixed integers; no
sleeps, wall-clock reads, or nondeterministic data.
"""

import unittest

from logsentinel.config import AppConfig
from logsentinel.detectors import (
    BaseDetector,
    HTTP4xxAbuseDetector,
    PortScanDetector,
    SSHBruteForceDetector,
    run_all_detectors,
)
from logsentinel.events import (
    FirewallEvent,
    HTTPRequestEvent,
    SSHAuthEvent,
    SyslogEvent,
)


def ssh(ts, ip="192.0.2.7", user="admin", ok=False):
    tag = "accepted" if ok else "failed"
    line = f"{tag} {user} from {ip} at {ts}"
    return SSHAuthEvent(timestamp=ts, raw_timestamp="t", raw_line=line,
                        source_file="f", src_ip=ip, username=user,
                        success=ok)


def fw(ts, ip, port, dst="203.0.113.10", proto="TCP", line=None):
    if line is None:
        line = f"drop {ip} dpt={port} {proto} at {ts}"
    return FirewallEvent(timestamp=ts, raw_timestamp="t", raw_line=line,
                         source_file="f", src_ip=ip, dst_ip=dst,
                         dst_port=port, protocol=proto)


def web(ts, ip, status, path="/a", line=None):
    if line is None:
        line = f'{ip} "GET {path}" {status} at {ts}'
    return HTTPRequestEvent(timestamp=ts, raw_timestamp="t", raw_line=line,
                            source_file="f", src_ip=ip, method="GET",
                            path=path, status_code=status)


def failure_burst(ip, count, start, step=40, user="admin"):
    return [ssh(start + i * step, ip=ip, user=user) for i in range(count)]


class TestSSHBruteForce(unittest.TestCase):
    """LS-RULE-001: threshold and sliding-window behaviour."""

    def test_threshold_minus_one_no_finding(self):
        events = failure_burst("192.0.2.7", 7, 0)  # 7 x 40s = all in window
        self.assertEqual(SSHBruteForceDetector(8, 300).detect(events), [])

    def test_exact_threshold_one_finding(self):
        events = failure_burst("192.0.2.7", 8, 0)
        findings = SSHBruteForceDetector(8, 300).detect(events)
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f.rule_id, "LS-RULE-001")
        self.assertEqual(f.severity, "high")
        self.assertEqual(f.src_ip, "192.0.2.7")
        self.assertEqual(f.summary["failed_count"], 8)
        self.assertEqual(f.first_seen, 0)
        self.assertEqual(f.last_seen, 280)

    def test_threshold_plus_one(self):
        events = failure_burst("192.0.2.7", 9, 0)
        findings = SSHBruteForceDetector(8, 300).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["failed_count"], 9)

    def test_lower_window_boundary_excluded(self):
        # (t_latest - 300, t_latest]: an event exactly 300s earlier is out.
        events = [ssh(200), ssh(500)]
        self.assertEqual(SSHBruteForceDetector(2, 300).detect(events), [])

    def test_event_just_inside_lower_boundary_included(self):
        events = [ssh(201), ssh(500)]
        findings = SSHBruteForceDetector(2, 300).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["failed_count"], 2)

    def test_upper_boundary_same_timestamp_included(self):
        events = [ssh(500), ssh(500)]
        findings = SSHBruteForceDetector(2, 300).detect(events)
        self.assertEqual(len(findings), 1)

    def test_two_sub_threshold_bursts_do_not_trigger(self):
        events = [ssh(0), ssh(60), ssh(1000), ssh(1060)]
        self.assertEqual(SSHBruteForceDetector(3, 300).detect(events), [])

    def test_overlapping_windows_aggregate_into_one_finding(self):
        events = failure_burst("192.0.2.7", 10, 0, step=100)  # 0..900
        findings = SSHBruteForceDetector(3, 300).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["failed_count"], 10)
        self.assertEqual(len(findings[0].evidence), 10)

    def test_fifteen_failures_overlapping_windows(self):
        events = failure_burst("192.0.2.7", 15, 0, step=25)  # 0..350
        findings = SSHBruteForceDetector(8, 300).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["failed_count"], 15)
        self.assertEqual(findings[0].first_seen, 0)
        self.assertEqual(findings[0].last_seen, 350)

    def test_successes_never_count_or_reset_window(self):
        events = failure_burst("192.0.2.7", 8, 0)  # 0..280, all in window
        events.insert(4, ssh(160, ok=True))        # interleave a success
        events.append(ssh(300, ok=True))           # success after the window
        findings = SSHBruteForceDetector(8, 300).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["failed_count"], 8)

    def test_successful_followups_counted_across_whole_run(self):
        events = [ssh(0, ok=True)]                          # before failures
        events += failure_burst("192.0.2.7", 8, 100)        # 100..380
        events.append(ssh(140, ok=True))                    # between failures
        events.append(ssh(999, ok=True))                    # after everything
        findings = SSHBruteForceDetector(8, 300).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["successful_followups"], 3)

    def test_successes_attached_as_contextual_evidence(self):
        events = failure_burst("192.0.2.7", 8, 0)
        events.append(ssh(999, ok=True))
        evidence = SSHBruteForceDetector(8, 300).detect(events)[0].evidence
        self.assertEqual(len(evidence), 9)
        self.assertIn("accepted admin from 192.0.2.7 at 999", evidence)
        self.assertTrue(all("failed" in line for line in evidence[:8]))

    def test_distinct_usernames(self):
        events = (failure_burst("192.0.2.7", 3, 0, user="admin")
                  + failure_burst("192.0.2.7", 3, 120, user="root")
                  + failure_burst("192.0.2.7", 2, 240, user="svc"))
        summary = SSHBruteForceDetector(8, 300).detect(events)[0].summary
        self.assertEqual(summary["distinct_usernames"], 3)

    def test_failures_spread_wider_than_window_do_not_trigger(self):
        events = failure_burst("192.0.2.7", 8, 0, step=100)  # 0..700
        self.assertEqual(SSHBruteForceDetector(8, 300).detect(events), [])

    def test_multiple_source_ips_independent(self):
        events = (failure_burst("192.0.2.7", 8, 0)
                  + failure_burst("192.0.2.9", 8, 0))
        findings = SSHBruteForceDetector(8, 300).detect(events)
        self.assertEqual([f.src_ip for f in findings], ["192.0.2.7", "192.0.2.9"])

    def test_success_for_other_ip_not_attached(self):
        events = failure_burst("192.0.2.7", 8, 0)
        events.append(ssh(999, ip="192.0.2.9", ok=True))
        finding = SSHBruteForceDetector(8, 300).detect(events)[0]
        self.assertEqual(finding.summary["successful_followups"], 0)
        self.assertEqual(len(finding.evidence), 8)


class TestPortScan(unittest.TestCase):
    """LS-RULE-002: distinct destination ports per source IP."""

    def ports(self, ip="198.51.100.23", start=22, count=10, step=1,
              repeats=0, dst="203.0.113.10"):
        events = [fw(100 + i, ip, start + i * step, dst=dst)
                  for i in range(count)]
        for i in range(repeats):
            events.append(fw(500 + i, ip, start, dst=dst))  # repeat first port
        return events

    def test_threshold_minus_one_no_finding(self):
        self.assertEqual(PortScanDetector(10).detect(self.ports(count=9)), [])

    def test_exact_threshold_one_finding(self):
        findings = PortScanDetector(10).detect(self.ports(count=10))
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f.rule_id, "LS-RULE-002")
        self.assertEqual(f.severity, "medium")
        self.assertEqual(f.summary["distinct_ports"], 10)
        self.assertEqual(f.first_seen, 100)
        self.assertEqual(f.last_seen, 109)

    def test_repeated_same_port_counts_once(self):
        findings = PortScanDetector(10).detect(self.ports(count=10, repeats=5))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["distinct_ports"], 10)

    def test_same_port_different_destination_counts_once(self):
        events = self.ports(count=10)
        events.append(fw(600, "198.51.100.23", 22, dst="203.0.113.99"))
        findings = PortScanDetector(10).detect(events)
        self.assertEqual(findings[0].summary["distinct_ports"], 10)

    def test_protocols_do_not_make_port_distinct(self):
        events = self.ports(count=10)
        events.append(fw(600, "198.51.100.23", 22, proto="UDP"))
        findings = PortScanDetector(10).detect(events)
        self.assertEqual(findings[0].summary["distinct_ports"], 10)
        self.assertEqual(findings[0].summary["protocols"], ["TCP", "UDP"])

    def test_evidence_one_first_seen_line_per_port(self):
        events = [fw(100 + i, "198.51.100.23", port=22 + i,
                     line=f"first-seen dpt={22 + i} marker{i}")
                  for i in range(10)]
        events.append(fw(400, "198.51.100.23", 22,
                         line="later repeat dpt=22"))
        finding = PortScanDetector(10).detect(events)[0]
        self.assertEqual(len(finding.evidence), 10)
        self.assertIn("first-seen dpt=22 marker0", finding.evidence)
        self.assertNotIn("later repeat dpt=22", finding.evidence)

    def test_ports_sample_sorted_and_capped_at_twenty(self):
        events = self.ports(start=1000, count=25)
        finding = PortScanDetector(10).detect(events)[0]
        sample = finding.summary["ports_sample"]
        self.assertEqual(len(sample), 20)
        self.assertEqual(sample, sorted(sample))
        self.assertEqual(sample, list(range(1000, 1020)))
        self.assertEqual(finding.summary["distinct_ports"], 25)

    def test_no_time_window_spread_events_still_trigger(self):
        events = [fw(ts, "198.51.100.23", 22 + i)
                  for i, ts in enumerate(range(100, 100000, 10000))]
        findings = PortScanDetector(10).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].last_seen, 90100)

    def test_multiple_source_ips_independent(self):
        events = self.ports(ip="198.51.100.23") + self.ports(ip="198.51.100.99")
        findings = PortScanDetector(10).detect(events)
        self.assertEqual([f.src_ip for f in findings],
                         ["198.51.100.23", "198.51.100.99"])


class TestHTTP4xxAbuse(unittest.TestCase):
    """LS-RULE-003: 400-499 inclusive per source IP."""

    def test_threshold_minus_one_no_finding(self):
        events = [web(100 + i, "203.0.113.50", 404) for i in range(7)]
        self.assertEqual(HTTP4xxAbuseDetector(8).detect(events), [])

    def test_exact_threshold_one_finding(self):
        events = [web(100 + i, "203.0.113.50", 404) for i in range(8)]
        findings = HTTP4xxAbuseDetector(8).detect(events)
        self.assertEqual(len(findings), 1)
        f = findings[0]
        self.assertEqual(f.rule_id, "LS-RULE-003")
        self.assertEqual(f.severity, "medium")
        self.assertEqual(f.summary["http_4xx_count"], 8)
        self.assertEqual(f.first_seen, 100)
        self.assertEqual(f.last_seen, 107)

    def test_status_400_and_499_included(self):
        events = [web(100 + i, "203.0.113.50", 404) for i in range(6)]
        events += [web(200, "203.0.113.50", 400),
                   web(201, "203.0.113.50", 499)]
        findings = HTTP4xxAbuseDetector(8).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["http_4xx_count"], 8)

    def test_non_4xx_statuses_excluded(self):
        events = [web(100 + i, "203.0.113.50", 404) for i in range(7)]
        events += [web(500, "203.0.113.50", 399),
                   web(501, "203.0.113.50", 500),
                   web(502, "203.0.113.50", 200),
                   web(503, "203.0.113.50", 301)]
        self.assertEqual(HTTP4xxAbuseDetector(8).detect(events), [])
        # ...even in volume: 5xx never counts toward 4xx abuse.
        events += [web(600 + i, "203.0.113.50", 500) for i in range(10)]
        self.assertEqual(HTTP4xxAbuseDetector(8).detect(events), [])

    def test_histogram_sorted_string_keys(self):
        events = ([web(100 + i, "203.0.113.50", 404, path="/x") for i in range(3)]
                  + [web(200 + i, "203.0.113.50", 403, path="/y") for i in range(2)]
                  + [web(300 + i, "203.0.113.50", 401, path="/z") for i in range(3)])
        summary = HTTP4xxAbuseDetector(8).detect(events)[0].summary
        self.assertEqual(summary["status_histogram"],
                         {"401": 3, "403": 2, "404": 3})

    def test_distinct_paths(self):
        events = ([web(100 + i, "203.0.113.50", 404, path="/dup") for i in range(5)]
                  + [web(200 + i, "203.0.113.50", 403, path="/p%d" % i)
                     for i in range(3)])
        summary = HTTP4xxAbuseDetector(8).detect(events)[0].summary
        self.assertEqual(summary["distinct_paths"], 4)

    def test_timestamps_span_qualifying_only(self):
        events = [web(100 + i, "203.0.113.50", 404) for i in range(8)]
        events.append(web(9999, "203.0.113.50", 500))  # ignored 5xx
        finding = HTTP4xxAbuseDetector(8).detect(events)[0]
        self.assertEqual(finding.last_seen, 107)

    def test_multiple_source_ips_independent(self):
        events = ([web(100 + i, "203.0.113.50", 404) for i in range(8)]
                  + [web(200 + i, "203.0.113.60", 403) for i in range(8)])
        findings = HTTP4xxAbuseDetector(8).detect(events)
        self.assertEqual([f.src_ip for f in findings],
                         ["203.0.113.50", "203.0.113.60"])

class TestGeneralDetectorBehaviour(unittest.TestCase):
    """Shared requirements: purity, config plumbing, finding shape."""

    def test_empty_input(self):
        self.assertEqual(run_all_detectors([], AppConfig()), [])

    def test_irrelevant_event_types_ignored(self):
        events = [SyslogEvent(timestamp=1, raw_timestamp="t",
                              raw_line="misc message", source_file="f")]
        self.assertEqual(run_all_detectors(events, AppConfig()), [])

    def test_configurable_thresholds_respected(self):
        config = AppConfig(ssh_threshold=2, ssh_window_seconds=60,
                           portscan_threshold=1, http_4xx_threshold=1)
        events = [ssh(0), ssh(10),                          # 2 failures -> hit
                  fw(20, "198.51.100.23", 22),              # 1 port -> hit
                  web(30, "203.0.113.50", 404)]             # 1 x 4xx -> hit
        findings = run_all_detectors(events, config)
        self.assertEqual([f.rule_id for f in findings],
                         ["LS-RULE-001", "LS-RULE-002", "LS-RULE-003"])

    def test_findings_use_config_thresholds_not_hardcoded(self):
        config = AppConfig(ssh_threshold=3, ssh_window_seconds=300)
        events = failure_burst("192.0.2.7", 3, 0)
        self.assertEqual(len(run_all_detectors(events, config)), 1)
        self.assertEqual(len(run_all_detectors(events, AppConfig())), 0)

    def test_one_finding_per_rule_and_source_ip(self):
        events = (failure_burst("192.0.2.7", 8, 0)
                  + [fw(100 + i, "192.0.2.7", 22 + i) for i in range(10)]
                  + [web(200 + i, "192.0.2.7", 404, path="/p%d" % i)
                     for i in range(8)])
        findings = run_all_detectors(events, AppConfig())
        self.assertEqual(len(findings), 3)
        self.assertEqual([f.rule_id for f in findings],
                         ["LS-RULE-001", "LS-RULE-002", "LS-RULE-003"])
        self.assertEqual(len({f.src_ip for f in findings}), 1)

    def test_finding_shape(self):
        events = failure_burst("192.0.2.7", 8, 0)
        finding = run_all_detectors(events, AppConfig())[0]
        self.assertIsInstance(finding.evidence, tuple)
        self.assertTrue(all(isinstance(line, str) for line in finding.evidence))
        self.assertEqual(set(finding.summary),
                         {"failed_count", "distinct_usernames",
                          "window_seconds", "successful_followups"})
        self.assertEqual(finding.summary["window_seconds"], 300)

    def test_input_events_not_mutated(self):
        events = (failure_burst("192.0.2.7", 8, 0)
                  + [fw(100 + i, "198.51.100.23", 22 + i) for i in range(10)]
                  + [web(200 + i, "203.0.113.50", 404) for i in range(8)])
        snapshot = [(type(e).__name__, e.timestamp, e.raw_line) for e in events]
        run_all_detectors(events, AppConfig())
        self.assertEqual(
            [(type(e).__name__, e.timestamp, e.raw_line) for e in events],
            snapshot)

    def test_repeated_identical_events_remain_countable(self):
        """Phase 4.1 policy: detectors never deduplicate (same-file repeats)."""
        line = ("Mar 10 11:20:01 h sshd[1]: Failed password for a "
                "from 192.0.2.7 port 1")
        events = [SSHAuthEvent(timestamp=100, raw_timestamp="t",
                               raw_line=line, source_file="f",
                               src_ip="192.0.2.7", username="a",
                               success=False) for _ in range(8)]
        findings = SSHBruteForceDetector(8, 300).detect(events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["failed_count"], 8)

    def test_base_detector_validates_threshold(self):
        for bad in (0, -1, 2.0, "8", True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    BaseDetector(bad)
        with self.assertRaises(ValueError):
            SSHBruteForceDetector(8, 0)
        with self.assertRaises(NotImplementedError):
            BaseDetector(1).detect([])

    def test_no_wall_clock_or_environment_use(self):
        # Structural purity check: the module must not import time/os/sys.
        import logsentinel.detectors as module
        with open(module.__file__, encoding="utf-8") as source_file:
            source = source_file.read()
        for banned in ("import time", "import os", "import sys",
                       "time.time", "os.environ", "print(", "socket"):
            self.assertNotIn(banned, source)


class TestStreamingEquivalence(unittest.TestCase):
    """Phase 5 spec 3.11: incremental observe/results == batch detect()."""

    def _assert_same(self, detector_factory, events):
        batch = detector_factory().detect(events)
        streaming = detector_factory()
        for event in events:
            streaming.observe(event)
        self.assertEqual(streaming.results(), batch)
        # And re-running batch reproduces identical output (state reset).
        self.assertEqual(detector_factory().detect(events), batch)

    def test_ssh_equivalent_with_overlapping_windows(self):
        # 10 failures; two overlapping qualifying windows merge into one set.
        events = failure_burst("192.0.2.7", 6, 0) \
            + failure_burst("192.0.2.7", 6, 200, step=40, user="root") \
            + [ssh(500, ip="192.0.2.7", ok=True),
               ssh(501, ip="192.0.2.9", ok=True)]
        self._assert_same(
            lambda: SSHBruteForceDetector(8, 300), events)

    def test_ssh_equivalent_with_out_of_order_and_ties(self):
        events = failure_burst("192.0.2.7", 8, 0, step=10)
        shuffled = events[3:] + events[:3]  # out-of-order ingestion
        ties = [ssh(100, ip="192.0.2.7", user="a"),
                ssh(100, ip="192.0.2.7", user="b")]
        self._assert_same(
            lambda: SSHBruteForceDetector(8, 300), shuffled + ties)

    def test_ssh_window_boundary_streaming(self):
        # Failures spread too widely never qualify...
        events = [ssh(i * 100, ip="192.0.2.7") for i in range(8)]
        self.assertEqual(SSHBruteForceDetector(8, 300).detect(events), [])
        # ...and the half-open boundary excludes a failure exactly at a
        # qualifying window's lower bound: with 8 failures at 320..600,
        # the only qualifying window is (300, 600]; a failure at exactly
        # ts=20 (== 320 - 300... and below every window bound) is excluded.
        events = ([ssh(20, ip="192.0.2.7", user="boundary")]
                  + [ssh(320 + i * 40, ip="192.0.2.7") for i in range(8)])
        detector = SSHBruteForceDetector(8, 300)
        for event in events:
            detector.observe(event)
        findings = detector.results()
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["failed_count"], 8)
        self.assertEqual(findings[0].first_seen, 320)
        self.assertEqual(findings[0].last_seen, 600)
        self.assertEqual(len(findings[0].evidence), 8)
        self.assertNotIn(
            "failed boundary from 192.0.2.7 at 20", findings[0].evidence)

    def test_ssh_success_context_never_counts_streaming(self):
        events = failure_burst("192.0.2.7", 8, 0) \
            + [ssh(1, ip="192.0.2.7", ok=True)]
        detector = SSHBruteForceDetector(8, 300)
        for event in events:
            detector.observe(event)
        findings = detector.results()
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].summary["successful_followups"], 1)
        self.assertEqual(findings[0].evidence[-1],
                         "accepted admin from 192.0.2.7 at 1")

    def test_portscan_equivalent_and_first_seen_evidence(self):
        events = ([fw(10 + i, "198.51.100.23", 1000 + i) for i in range(10)]
                  + [fw(500, "198.51.100.23", 1003, proto="UDP")]
                  + [fw(600, "198.51.100.24", 80)])
        self._assert_same(lambda: PortScanDetector(10), events)
        detector = PortScanDetector(10)
        for event in events:
            detector.observe(event)
        finding = detector.results()[0]
        self.assertEqual(finding.summary["distinct_ports"], 10)
        self.assertEqual(finding.summary["ports_sample"], list(range(1000, 1010)))
        self.assertEqual(finding.summary["protocols"], ["TCP", "UDP"])
        self.assertEqual(finding.first_seen, 10)
        self.assertEqual(finding.last_seen, 500)
        self.assertEqual(len(finding.evidence), 10)   # one line per port

    def test_http_equivalent_filtering_and_histogram(self):
        events = ([web(10 + i, "203.0.113.50", 404, path=f"/p{i}")
                   for i in range(8)]
                  + [web(100, "203.0.113.50", 200),       # never contributes
                     web(101, "203.0.113.50", 302),       # never contributes
                     web(102, "203.0.113.50", 500),       # never contributes
                     web(103, "203.0.113.50", 404, path="/p0")]  # dup path
                  + [web(200, "203.0.113.51", 401)])
        self._assert_same(lambda: HTTP4xxAbuseDetector(8), events)
        detector = HTTP4xxAbuseDetector(8)
        for event in events:
            detector.observe(event)
        finding = detector.results()[0]
        self.assertEqual(finding.summary["http_4xx_count"], 9)
        self.assertEqual(finding.summary["status_histogram"], {"404": 9})
        self.assertEqual(finding.summary["distinct_paths"], 8)
        self.assertEqual(len(finding.evidence), 9)   # never capped

    def test_streaming_results_order_matches_batch(self):
        events = (failure_burst("192.0.2.8", 8, 0)
                  + failure_burst("192.0.2.7", 8, 0))
        detector = SSHBruteForceDetector(8, 300)
        for event in events:
            detector.observe(event)
        self.assertEqual([f.src_ip for f in detector.results()],
                         ["192.0.2.7", "192.0.2.8"])   # ascending IP order
        self.assertEqual(detector.results(),
                         SSHBruteForceDetector(8, 300).detect(events))


if __name__ == "__main__":
    unittest.main()
