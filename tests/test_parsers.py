"""Unit tests for LogSentinel parsing (Phase 3 matrix TC-P01..TC-P04, TC-T01..TC-T03)."""

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from logsentinel.events import (
    FirewallEvent,
    HTTPRequestEvent,
    SSHAuthEvent,
    SyslogEvent,
    dedup_cross_file,
)
from logsentinel.exceptions import ParseError
from logsentinel.parsers import ParseResult, parse_file, stream_parse_file


REF_NOW = int(datetime(2026, 3, 10, 12, 0, 0, tzinfo=UTC).timestamp())


def epoch(y, mo, d, h, mi, s):
    return int(datetime(y, mo, d, h, mi, s, tzinfo=UTC).timestamp())


class ParserTestCase(unittest.TestCase):
    def parse(self, text, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.log"
            path.write_text(text, encoding="utf-8", newline="")
            return parse_file(path, kwargs.pop("reference_now", REF_NOW), **kwargs)


class TestSSHParsing(ParserTestCase):
    """TC-P01/TC-P02: SSH auth lines -> authfail/authok (FR-017)."""

    def test_failed_password_line(self):
        result = self.parse(
            "Mar 10 11:20:01 host sshd[1001]: Failed password for admin "
            "from 192.0.2.7 port 51001 ssh2\n"
        )
        self.assertEqual(result.stats.malformed, 0)
        self.assertEqual(len(result.events), 1)
        event = result.events[0]
        self.assertIsInstance(event, SSHAuthEvent)
        self.assertEqual(event.kind, "authfail")
        self.assertEqual(event.src_ip, "192.0.2.7")
        self.assertEqual(event.username, "admin")
        self.assertIs(event.success, False)
        self.assertEqual(event.timestamp, epoch(2026, 3, 10, 11, 20, 1))

    def test_invalid_user_variant(self):
        result = self.parse(
            "Mar 10 11:20:02 host sshd: Failed password for invalid user root "
            "from 192.0.2.8 port 51002 ssh2\n"
        )
        event = result.events[0]
        self.assertEqual(event.username, "root")
        self.assertEqual(event.kind, "authfail")

    def test_accepted_publickey_line(self):
        result = self.parse(
            "Mar 10 11:20:03 host sshd[7]: Accepted publickey for deploy "
            "from 192.0.2.9 port 51003 ssh2\n"
        )
        event = result.events[0]
        self.assertEqual(event.kind, "authok")
        self.assertIs(event.success, True)

    def test_ssh_line_without_ip_is_othersyslog(self):
        # A-03: header valid, body not an auth event -> othersyslog.
        result = self.parse(
            "Mar 10 11:20:04 host sshd[9]: Connection closed by 192.0.2.7\n"
        )
        self.assertEqual(result.events[0].kind, "othersyslog")


class TestTimestampHandling(ParserTestCase):
    """TC-T01/TC-T02: year inference, rollover, UTC normalization (AR-003/004)."""

    def test_year_inference_same_year(self):
        result = self.parse(
            "Jan 05 08:00:00 h sshd[1]: Failed password for a from 192.0.2.7 port 1\n"
        )
        self.assertEqual(result.events[0].timestamp, epoch(2026, 1, 5, 8, 0, 0))

    def test_year_rollover_dec_to_jan(self):
        ref = int(datetime(2027, 1, 2, 9, 0, 0, tzinfo=UTC).timestamp())
        result = self.parse(
            "Dec 31 23:59:59 h sshd[1]: Failed password for a from 192.0.2.7 port 1\n",
            reference_now=ref,
        )
        self.assertEqual(result.events[0].timestamp, epoch(2026, 12, 31, 23, 59, 59))

    def test_iso_offset_converted_to_utc(self):
        result = self.parse(
            "2026-03-10T13:20:01+02:00 sshd[1]: Failed password for a "
            "from 192.0.2.7 port 2\n"
        )
        self.assertEqual(result.events[0].timestamp, epoch(2026, 3, 10, 11, 20, 1))

    def test_iso_naive_assumed_utc(self):
        result = self.parse(
            "2026-03-10 11:20:02 sshd[1]: Failed password for a "
            "from 192.0.2.7 port 3\n"
        )
        self.assertEqual(result.events[0].timestamp, epoch(2026, 3, 10, 11, 20, 2))

    def test_subsecond_truncated_floor(self):
        result = self.parse(
            "2026-03-10T11:20:03.912Z sshd[1]: Failed password for a "
            "from 192.0.2.7 port 4\n"
        )
        self.assertEqual(result.events[0].timestamp, epoch(2026, 3, 10, 11, 20, 3))

    def test_impossible_date_is_malformed(self):
        result = self.parse("Feb 30 10:00:00 h sshd[1]: Failed password for a "
                            "from 192.0.2.7 port 5\n")
        self.assertEqual(result.stats.malformed, 1)
        self.assertEqual(len(result.events), 0)


class TestFirewallParsing(ParserTestCase):
    """TC-P01/TC-P02: firewall lines -> fwconn (FR-018, FR-125)."""

    def test_drop_line_tcp(self):
        result = self.parse(
            "Mar 10 09:00:01 fw kernel: DROP IN=eth0 OUT= SRC=198.51.100.23 "
            "DST=203.0.113.10 PROTO=TCP SPT=40001 DPT=22\n"
        )
        event = result.events[0]
        self.assertIsInstance(event, FirewallEvent)
        self.assertEqual(event.kind, "fwconn")
        self.assertEqual(event.src_ip, "198.51.100.23")
        self.assertEqual(event.dst_port, 22)
        self.assertEqual(event.protocol, "TCP")
        self.assertEqual(event.timestamp, epoch(2026, 3, 10, 9, 0, 1))

    def test_icmp_becomes_othersyslog(self):
        result = self.parse(
            "Mar 10 09:00:02 fw kernel: DROP IN=eth0 SRC=198.51.100.23 "
            "DST=203.0.113.10 PROTO=ICMP TYPE=8\n"
        )
        self.assertEqual(result.events[0].kind, "othersyslog")

    def test_invalid_ports_malformed(self):
        for dpt in (0, 70000):
            with self.subTest(dpt=dpt):
                result = self.parse(
                    f"Mar 10 09:00:03 fw kernel: DROP IN=eth0 SRC=198.51.100.23 "
                    f"DST=203.0.113.10 PROTO=TCP SPT=1 DPT={dpt}\n"
                )
                self.assertEqual(result.stats.malformed, 1)
                self.assertEqual(result.events, [])

    def test_invalid_source_ip_malformed(self):
        result = self.parse(
            "Mar 10 09:00:04 fw kernel: DROP IN=eth0 SRC=999.9.9.9 "
            "DST=203.0.113.10 PROTO=TCP SPT=1 DPT=22\n"
        )
        self.assertEqual(result.stats.malformed, 1)


class TestHTTPParsing(ParserTestCase):
    """TC-P01: Apache/Nginx lines -> web (FR-019)."""

    def test_combined_line(self):
        result = self.parse(
            '203.0.113.50 - - [10/Mar/2026:11:00:01 +0000] "GET /admin HTTP/1.1" '
            "403 199 \"-\" \"Mozilla/5.0\"\n"
        )
        event = result.events[0]
        self.assertIsInstance(event, HTTPRequestEvent)
        self.assertEqual(event.kind, "web")
        self.assertEqual(event.status_code, 403)
        self.assertEqual(event.method, "GET")
        self.assertEqual(event.path, "/admin")
        self.assertEqual(event.timestamp, epoch(2026, 3, 10, 11, 0, 1))

    def test_ipv6_source_is_malformed_v1(self):
        result = self.parse(
            '2001:db8::1 - - [10/Mar/2026:11:00:02 +0000] "GET / HTTP/1.1" 200 10\n'
        )
        self.assertEqual(result.stats.malformed, 1)
        self.assertEqual(result.events, [])

    def test_dash_status_is_malformed(self):
        result = self.parse(
            '192.0.2.7 - - [10/Mar/2026:11:00:03 +0000] "GET / HTTP/1.1" - 10\n'
        )
        self.assertEqual(result.stats.malformed, 1)


class TestMalformedAndUnknown(ParserTestCase):
    """TC-P03: malformed/unknown handling (FR-015, FR-021, FR-103)."""

    def test_garbage_line(self):
        result = self.parse("this is not a log line\n")
        self.assertEqual(result.stats.malformed, 1)
        self.assertEqual(result.stats.events_parsed, 0)

    def test_empty_line_counts_malformed(self):
        result = self.parse("\n\n")
        self.assertEqual(result.stats.lines_read, 2)
        self.assertEqual(result.stats.malformed, 2)

    def test_overlong_line(self):
        result = self.parse("x" * 50 + "\n", max_line_length=20)
        self.assertEqual(result.stats.malformed, 1)

    def test_unknown_syslog_body_is_othersyslog(self):
        result = self.parse("Mar 10 11:21:00 host CRON[5]: job started\n")
        self.assertEqual(result.events[0].kind, "othersyslog")
        self.assertEqual(result.stats.othersyslog, 1)

    def test_othersyslog_retention_cap(self):
        text = "".join(
            f"Mar 10 11:21:{s:02d} host TAG[i]: body {s}\n" for s in range(10, 15)
        )
        result = self.parse(text, max_othersyslog_kept=2)
        self.assertEqual(result.stats.othersyslog, 5)
        self.assertEqual(
            sum(1 for e in result.events if e.kind == "othersyslog"), 2)
        self.assertEqual(result.stats.othersyslog_dropped, 3)
        self.assertEqual(result.stats.malformed + result.stats.events_parsed
                         + result.stats.othersyslog_dropped,
                         result.stats.lines_read)

    def test_crlf_normalized(self):
        result = self.parse(
            "Mar 10 11:20:01 h sshd[1]: Failed password for admin "
            "from 192.0.2.7 port 1 ssh2\r\n"
        )
        self.assertEqual(result.stats.malformed, 0)
        self.assertEqual(result.events[0].kind, "authfail")

    def test_intra_file_repeats_preserved_and_counted(self):
        """Phase 4.1: identical records in one file are kept, not dropped."""
        line = ("Mar 10 11:20:01 h sshd[1]: Failed password for a "
                "from 192.0.2.7 port 1\n")
        result = self.parse(line + line + line)
        s = result.stats
        self.assertEqual(s.lines_read, 3)
        self.assertEqual(len(result.events), 3)          # all preserved
        self.assertEqual(s.events_parsed, 3)             # all retained
        self.assertEqual(s.duplicates, 2)                # counted, not dropped
        self.assertEqual(s.malformed, 0)
        self.assertEqual(s.malformed + s.events_parsed
                         + s.othersyslog_dropped, s.lines_read)

    def test_stats_invariant(self):
        text = (
            "Mar 10 11:20:01 h sshd[1]: Failed password for a from 192.0.2.7 port 1\n"
            "garbage\n"
            "\n"
            "Mar 10 11:20:02 h sshd[1]: Failed password for a from 192.0.2.7 port 1\n"
            "Mar 10 11:20:02 h sshd[1]: Failed password for a from 192.0.2.7 port 1\n"
        )
        result = self.parse(text)
        s = result.stats
        self.assertEqual(s.lines_read, 5)
        self.assertEqual(s.malformed, 2)
        self.assertEqual(s.duplicates, 1)                # line 5 repeats line 4
        self.assertEqual(s.events_parsed, 3)             # all three preserved
        self.assertEqual(s.malformed + s.events_parsed
                         + s.othersyslog_dropped, s.lines_read)


class TestEncodingAndDeterminism(ParserTestCase):
    """TC-P04: encoding fallback and determinism (FR-003, NFR-006)."""

    def test_latin1_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "latin.log"
            path.write_bytes(
                b"Mar 10 11:20:01 h sshd[1]: Failed password for caf\xc3\xa9x "
                b"from 192.0.2.7 port 1\n"
                b"Mar 10 11:20:02 h note: caf\xe9 latin\n"
            )
            result = parse_file(path, REF_NOW)
        self.assertEqual(result.stats.malformed, 0)
        kinds = [e.kind for e in result.events]
        self.assertEqual(kinds, ["authfail", "othersyslog"])
        self.assertIn("café", result.events[1].raw_line)

    def test_deterministic_repeats(self):
        text = (
            "Mar 10 11:20:01 h sshd[1]: Failed password for a from 192.0.2.7 port 1\n"
            '203.0.113.50 - - [10/Mar/2026:11:00:01 +0000] "GET /x HTTP/1.1" 404 5\n'
            "Mar 10 09:00:01 fw kernel: DROP SRC=198.51.100.23 DST=203.0.113.10 "
            "PROTO=TCP SPT=1 DPT=80\n"
        )
        r1 = self.parse(text)
        r2 = self.parse(text)
        self.assertEqual(r1.stats, r2.stats)
        self.assertEqual([e.kind for e in r1.events], [e.kind for e in r2.events])
        self.assertEqual([e.timestamp for e in r1.events],
                         [e.timestamp for e in r2.events])
        self.assertEqual([e.raw_line for e in r1.events],
                         [e.raw_line for e in r2.events])

    def test_empty_file(self):
        result = self.parse("")
        self.assertEqual(result, ParseResult())

    def test_invalid_reference_now_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.log"
            path.write_text("x\n")
            with self.assertRaises(Exception):
                parse_file(path, -1)
            with self.assertRaises(Exception):
                parse_file(path, "now")


class TestCrossFileScenario(unittest.TestCase):
    """Phase 4.1: parser preserves everything; dedup across files collapses."""

    LINE = ("Mar 10 11:20:01 h sshd[1]: Failed password for a "
            "from 192.0.2.7 port 1\n")

    def _parse_tmp(self, tmp, name):
        path = Path(tmp) / name
        path.write_text(self.LINE, encoding="utf-8", newline="")
        return parse_file(path, REF_NOW)

    def test_same_line_in_two_files_collapses_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            r1 = self._parse_tmp(tmp, "one.log")
            r2 = self._parse_tmp(tmp, "two.log")
            origin_path = str(Path(tmp) / "one.log")
        # The parser has no cross-file knowledge and keeps its own record.
        self.assertEqual(len(r1.events), 1)
        self.assertEqual(len(r2.events), 1)
        kept, cross = dedup_cross_file(r1.events + r2.events)
        self.assertEqual((len(kept), cross), (1, 1))
        self.assertEqual(kept[0].source_file, origin_path)  # first file wins

    def test_same_line_in_three_files_collapses_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = [self._parse_tmp(tmp, name)
                       for name in ("one.log", "two.log", "three.log")]
            origin_path = str(Path(tmp) / "one.log")
        combined = [e for r in results for e in r.events]
        self.assertEqual(len(combined), 3)
        kept, cross = dedup_cross_file(combined)
        self.assertEqual((len(kept), cross), (1, 2))
        self.assertEqual(kept[0].source_file, origin_path)


class TestStreamingProtocol(unittest.TestCase):
    """Phase 5 spec 3.11: stream_parse_file protocol and semantics."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def stream(self, data, **kwargs):
        path = self.tmp / "stream.log"
        path.write_bytes(data)
        return list(stream_parse_file(
            path, kwargs.pop("reference_now", REF_NOW), **kwargs))

    AUTH = ("Mar 10 11:20:01 h sshd[1]: Failed password for admin "
            "from 192.0.2.7 port 51001 ssh2\n").encode("utf-8")

    def test_successful_stream_single_stats_sentinel(self):
        items = self.stream(self.AUTH)
        tags = [tag for tag, _ in items]
        self.assertEqual(tags, ["event", "stats"])
        stats = items[-1][1]
        self.assertEqual(stats.lines_read, 1)
        self.assertEqual(stats.events_parsed, 1)

    def test_stream_event_fields_and_error_line_numbers(self):
        items = self.stream(self.AUTH + b"garbage\n")
        event = items[0][1]
        self.assertEqual(event.kind, "authfail")
        error = items[1][1]
        self.assertEqual(error.line_number, 2)
        self.assertEqual(error.kind, "parse")
        stats = items[2][1]
        self.assertEqual((stats.lines_read, stats.malformed), (2, 1))
        self.assertEqual(stats.malformed + stats.events_parsed,
                         stats.lines_read)

    def test_stream_error_reasons_pre_sanitized(self):
        """M6: ErrorEntry construction-time sanitization covers the
        streaming production path - yielded reasons are already
        redacted/capped before any caller (CLI staging) sees them.
        """
        bad_ip = b"Mar 10 11:20:01 h sshd[1001]: Failed password for admin " \
                 b"from password=hunter2 port 22 ssh2\n"
        items = self.stream(self.AUTH + bad_ip)
        error = items[1][1]
        self.assertEqual(error.kind, "parse")
        self.assertIn("<REDACTED>", error.reason)
        self.assertNotIn("hunter2", error.reason)

    def test_intra_file_duplicates_preserved_and_counted(self):
        items = self.stream(self.AUTH + self.AUTH)
        events = [item for tag, item in items if tag == "event"]
        self.assertEqual(len(events), 2)          # preserved, not dropped
        stats = items[-1][1]
        self.assertEqual(stats.duplicates, 1)     # second copy counted

    def test_othersyslog_retention_cap_streaming(self):
        body = (b"Mar 10 11:20:01 h unexpected-device-message\n")
        items = self.stream(body * 3, max_othersyslog_kept=2)
        stats = items[-1][1]
        self.assertEqual((stats.othersyslog, stats.othersyslog_dropped),
                         (3, 1))
        events = [item for tag, item in items if tag == "event"]
        self.assertEqual(len(events), 2)          # only the cap retained

    def test_decode_failure_rollback_and_retry_from_beginning(self):
        # Two parseable lines, then invalid UTF-8 on line 3.
        data = self.AUTH + self.AUTH + b"\xff\xfe tail\n"
        items = self.stream(data)
        sequence = [(tag, getattr(item, "raw_line", None))
                    for tag, item in items]
        # Small files decode in one ~8KiB chunk, so the UTF-8 attempt can
        # fail before any item is yielded; the rollback marker always
        # precedes the Latin-1 retry (events are re-emitted from line 1).
        self.assertEqual([tag for tag, _ in sequence[:2]],
                         ["rollback", "error"])   # fallback warning first
        auth_line = self.AUTH.decode("utf-8").rstrip("\n")
        retry_events = [line for tag, line in sequence[2:] if tag == "event"]
        self.assertEqual(retry_events, [auth_line, auth_line])
        stats = items[-1][1]
        self.assertEqual(stats.lines_read, 3)        # retry pass only
        self.assertEqual(stats.events_parsed, 2)
        self.assertEqual(stats.malformed, 1)         # the \xff line
        self.assertEqual(stats.malformed + stats.events_parsed
                         + stats.othersyslog_dropped, stats.lines_read)

    def test_decode_failure_after_streamed_events(self):
        # Multi-chunk file (~12 KiB): the first chunk's lines ARE yielded
        # before the decode failure; the caller must still discard them
        # (exactly one rollback marker, retry re-emits everything).
        data = self.AUTH * 150 + b"\xff tail\n"
        items = self.stream(data)
        tags = [tag for tag, _ in items]
        self.assertEqual(tags.count("rollback"), 1)
        first_rollback = tags.index("rollback")
        # Chunk size is interpreter-dependent; "many" events streamed
        self.assertGreaterEqual(tags[:first_rollback].count("event"), 50)
        events = [item for tag, item in items if tag == "event"]
        # Attempt 1 yielded only its decoded chunk; the retry re-emits all.
        self.assertEqual(len(events),
                         tags[:first_rollback].count("event") + 150)
        stats = items[-1][1]
        self.assertEqual(stats.lines_read, 151)  # successful pass only
        self.assertEqual(stats.events_parsed, 150)
        self.assertEqual(stats.malformed, 1)

    def test_decode_failure_discards_partial_attempt_errors(self):
        # A malformed line BEFORE the decode failure must not survive.
        data = b"garbage\n" + self.AUTH + b"\xff tail\n"
        items = self.stream(data)
        errors = [item for tag, item in items if tag == "error"]
        self.assertEqual(errors[0].reason,
                         "utf-8 decode failed; retried as latin-1")
        self.assertFalse(any(e.reason == "unparseable line" and
                             e.line_number == 1 for e in errors))

    def test_latin1_only_file_needs_no_rollback(self):
        data = self.AUTH + b"caf\xe9 line\n"   # valid latin-1, invalid utf-8
        items = self.stream(data)
        tags = [tag for tag, _ in items]
        self.assertEqual(tags.count("rollback"), 1)  # exactly one retry
        stats = items[-1][1]
        self.assertEqual(stats.lines_read, 2)

    def test_utf8_file_never_rolls_back(self):
        items = self.stream(self.AUTH)
        self.assertNotIn("rollback", [tag for tag, _ in items])

    def test_compat_parse_file_matches_stream(self):
        path = self.tmp / "same.log"
        path.write_bytes(self.AUTH + b"garbage\n")
        compat = parse_file(path, REF_NOW)
        items = list(stream_parse_file(path, REF_NOW))
        stream_events = [i for tag, i in items if tag == "event"]
        stream_errors = [i for tag, i in items if tag == "error"]
        self.assertEqual(compat.events, stream_events)
        self.assertEqual(compat.errors, stream_errors)
        self.assertEqual(compat.stats, items[-1][1])

    def test_invalid_stream_parameters_rejected(self):
        path = self.tmp / "p.log"
        path.write_bytes(self.AUTH)
        with self.assertRaises(ParseError):
            list(stream_parse_file(path, -1))
        with self.assertRaises(ParseError):
            list(stream_parse_file(path, REF_NOW, max_line_length=0))
        with self.assertRaises(ParseError):
            list(stream_parse_file(path, REF_NOW, max_othersyslog_kept=-1))


class TestDuplicateCheckSeam(TestStreamingProtocol):
    """Phase 5 correction: the parser's duplicate policy is injectable.

    ``stream_parse_file(duplicate_check=...)`` lets the CLI supply a
    SQLite-backed exact checker so no unbounded in-memory fingerprint set
    exists in the production path. These tests prove the seam behaviourally:
    the tracker is consulted per event, its answers alone determine the
    duplicate statistics, and dropped othersyslog events never reach it.
    """

    def test_tracker_consulted_per_event_and_drives_statistics(self):
        seen = set()
        calls = []

        def tracker(event):
            calls.append(event.raw_line)
            fp = (event.kind, event.timestamp, event.raw_line)
            if fp in seen:
                return True
            seen.add(fp)
            return False

        data = self.AUTH + self.AUTH + self.AUTH
        items = self.stream(data, duplicate_check=tracker)
        stats = items[-1][1]
        # Three identical lines: tracker answers F, T, T -> duplicates == 2.
        self.assertEqual(len(calls), 3)           # consulted per event
        self.assertEqual(stats.duplicates, 2)
        self.assertEqual(stats.events_parsed, 3)  # repeats preserved

    def test_tracker_answers_are_authoritative(self):
        # If the parser still consulted its own set, the duplicate count
        # would not follow the tracker's answers. A tracker that reports
        # "seen" for everything must push duplicates to events_parsed.
        def always_seen(event):
            return True

        items = self.stream(self.AUTH, duplicate_check=always_seen)
        stats = items[-1][1]
        self.assertEqual(stats.events_parsed, 1)
        self.assertEqual(stats.duplicates, 1)     # tracker's answer used

    def test_no_tracker_matches_legacy_in_memory_path(self):
        data = self.AUTH + self.AUTH
        with_tracker = self.stream(data, duplicate_check=self._exact_tracker())
        without = self.stream(data)
        self.assertEqual(with_tracker[-1][1], without[-1][1])
        self.assertEqual(
            [i for tag, i in with_tracker if tag == "event"],
            [i for tag, i in without if tag == "event"])

    def test_dropped_othersyslog_never_reaches_tracker(self):
        calls = []

        def tracker(event):
            calls.append(event.raw_line)
            return False

        body = b"Mar 10 11:20:01 h unexpected-device-message\n"
        items = self.stream(body * 3, max_othersyslog_kept=1,
                            duplicate_check=tracker)
        stats = items[-1][1]
        self.assertEqual((stats.othersyslog, stats.othersyslog_dropped),
                         (3, 2))
        self.assertEqual(len(calls), 1)   # only the retained event checked

    def test_tracker_knowledge_spans_attempts_unless_caller_rolls_back(self):
        # Documented contract (correction task section 2/7): the parser
        # NEVER rolls back caller-owned tracker state - the caller owns the
        # rollback. With a caller tracker that is not transaction-scoped,
        # the Latin-1 retry's duplicate counts reflect the stale attempt-1
        # knowledge (every re-emitted event is reported "seen"). The CLI's
        # storage-backed tracker is transaction-scoped, so its retry is
        # clean - proven in tests.test_cli.TestSQLiteBackedDuplicates.
        class NotTransactionalTracker:
            def __init__(self):
                self.seen = set()

            def __call__(self, event):
                fp = (event.kind, event.timestamp, event.raw_line)
                if fp in self.seen:
                    return True
                self.seen.add(fp)
                return False

        tracker = NotTransactionalTracker()
        data = self.AUTH * 150 + b"\xff tail\n"   # multi-chunk file
        items = self.stream(data, duplicate_check=tracker)
        stats = items[-1][1]
        self.assertEqual(stats.events_parsed, 150)
        # Stale knowledge inflates the retry's duplicate count to every
        # event - exactly why the CLI tracker must share the transaction.
        self.assertEqual(stats.duplicates, 150)
        self.assertEqual(stats.lines_read, 151)

    @staticmethod
    def _exact_tracker():
        seen = set()

        def tracker(event):
            fp = (event.kind, event.timestamp, event.raw_line)
            if fp in seen:
                return True
            seen.add(fp)
            return False

        return tracker


if __name__ == "__main__":
    unittest.main()
