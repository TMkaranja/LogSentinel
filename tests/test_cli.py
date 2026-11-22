"""Integration and unit tests for the CLI orchestrator (Phase 4.6)."""

import contextlib
from dataclasses import asdict
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from logsentinel import __version__, cli
from logsentinel import parsers as lsentinel_parsers
from logsentinel.storage import RunStorage
from logsentinel.config import DEFAULTS
from logsentinel.events import ErrorEntry
from logsentinel.exceptions import (
    ConfigError,
    InputPathError,
    ParseError,
    ReportError,
)

REF_YEAR = 2026  # syslog year inference target


def auth_line(ts: str, ip: str = "192.0.2.7", port: int = 51001) -> str:
    return (f"Mar 10 {ts} host sshd[1001]: Failed password for admin "
            f"from {ip} port {port} ssh2")


def fw_line(dpt: int, ip: str = "198.51.100.23") -> str:
    return (f"Mar 10 09:00:01 fw kernel: DROP IN=eth0 OUT= SRC={ip} "
            f"DST=203.0.113.10 PROTO=TCP SPT=40001 DPT={dpt}")


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.stdout, self.stderr = io.StringIO(), io.StringIO()

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, text):
        path = self.tmp / name
        path.write_text(text, encoding="utf-8", newline="")
        return path

    def run_cli(self, argv, cwd=None):
        """Run main() capturing stdout/stderr; returns (exit_code, out, err)."""
        code = None
        with contextlib.redirect_stdout(self.stdout), \
                contextlib.redirect_stderr(self.stderr):
            code = cli.main(argv)
        return code, self.stdout.getvalue(), self.stderr.getvalue()

    def read_json(self, name="report.json"):
        return json.loads((self.tmp / name).read_text(encoding="utf-8"))

    def statistics_payload(self, argv):
        """Run with --json and return (exit_code, parsed payload)."""
        code, _, _ = self.run_cli(
            list(argv) + ["--json", str(self.tmp / "r.json")])
        return code, self.read_json("r.json")


class TestArgumentHandling(CliTestCase):
    def test_help_exits_zero_and_lists_options(self):
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                cli.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)
        text = out.getvalue()
        for expected in ("--config", "--ssh-threshold", "--ssh-window",
                         "--portscan-threshold", "--http-4xx-threshold",
                         "--json", "--text", "--strict", "--quiet",
                         "--version"):
            self.assertIn(expected, text)

    def test_version_exits_zero(self):
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                cli.main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn(f"logsentinel {__version__}", out.getvalue())

    def test_no_positional_arguments_rejected(self):
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(io.StringIO()) as err:
                cli.main([])
        self.assertEqual(ctx.exception.code, 2)  # FR-072
        self.assertIn("required", err.getvalue())

    def test_all_options_accepted(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        self.write("cfg.json", "{}")     # --config must point at real JSON
        code, _, _ = self.run_cli([
            str(good),
            "--config", str(self.tmp / "cfg.json"),
            "--ssh-threshold", "3",
            "--ssh-window", "120",
            "--portscan-threshold", "5",
            "--http-4xx-threshold", "4",
            "--json", str(self.tmp / "r.json"),
            "--text", str(self.tmp / "r.txt"),
            "--strict", "--quiet",
        ])
        self.assertIn(code, (0, 1))

    def test_cli_overrides_reach_configuration(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        captured = {}
        real = cli.load_config

        def spy(overrides, config_path):
            cfg = real(overrides, config_path)
            captured.update(asdict(cfg))
            return cfg

        with mock.patch.object(cli, "load_config", spy):
            self.run_cli([
                str(good), "--ssh-threshold", "3", "--ssh-window", "60",
                "--portscan-threshold", "5", "--http-4xx-threshold", "4",
                "--strict",
            ])
        self.assertEqual(captured["ssh_threshold"], 3)
        self.assertEqual(captured["ssh_window_seconds"], 60)
        self.assertEqual(captured["portscan_threshold"], 5)
        self.assertEqual(captured["http_4xx_threshold"], 4)
        self.assertTrue(captured["strict"])


class TestConfiguration(CliTestCase):
    def test_defaults_used_when_nothing_supplied(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        captured = {}
        real = cli.load_config

        def spy(overrides, config_path):
            cfg = real(overrides, config_path)
            captured.update(asdict(cfg))
            return cfg

        with mock.patch.object(cli, "load_config", spy):
            self.run_cli([str(good)])
        for key, value in DEFAULTS.items():
            self.assertEqual(captured[key], value)

    def test_json_configuration_applied(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        config_file = self.write("cfg.json", '{"ssh_threshold": 4}')
        captured = {}
        real = cli.load_config

        def spy(overrides, config_path):
            cfg = real(overrides, config_path)
            captured.update(asdict(cfg))
            return cfg

        with mock.patch.object(cli, "load_config", spy):
            self.run_cli([str(good), "--config", str(config_file)])
        self.assertEqual(captured["ssh_threshold"], 4)

    def test_cli_overrides_precede_json_configuration(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        config_file = self.write("cfg.json", '{"ssh_threshold": 4}')
        captured = {}
        real = cli.load_config

        def spy(overrides, config_path):
            cfg = real(overrides, config_path)
            captured.update(asdict(cfg))
            return cfg

        with mock.patch.object(cli, "load_config", spy):
            self.run_cli([str(good), "--config", str(config_file),
                          "--ssh-threshold", "2"])
        self.assertEqual(captured["ssh_threshold"], 2)  # FR-141

    def test_unknown_json_key_aborts_before_processing(self):
        config_file = self.write("cfg.json", '{"bogus_key": 1}')
        with mock.patch.object(cli, "discover_inputs") as discover:
            code, _, err = self.run_cli(
                ["whatever.log", "--config", str(config_file)])
        self.assertEqual(code, 2)
        self.assertIn("configuration error", err)
        discover.assert_not_called()  # FR-061: abort before input processing

    def test_invalid_threshold_aborts_before_processing(self):
        with mock.patch.object(cli, "discover_inputs") as discover:
            code, _, err = self.run_cli(
                ["whatever.log", "--ssh-threshold", "0"])
        self.assertEqual(code, 2)
        self.assertIn("configuration error", err)
        discover.assert_not_called()


class TestInputDiscovery(CliTestCase):
    def test_explicit_files_and_directories(self):
        one = self.write("one.log", auth_line("11:20:01") + "\n")
        two = self.write("two.log", fw_line(22) + "\n")
        directory = self.tmp / "logs"
        directory.mkdir()
        (directory / "three.log").write_text(
            auth_line("11:21:01", port=51002) + "\n", encoding="utf-8")
        code, _, _ = self.run_cli([str(one), str(two), str(directory)])
        self.assertEqual(code, 0)  # 3 distinct events, thresholds unmet

    def test_empty_discovery_warns_but_succeeds(self):
        empty = self.tmp / "empty"
        empty.mkdir()
        code, out, err = self.run_cli([str(empty)])
        self.assertEqual(code, 0)
        self.assertIn("no input files", err)          # warning, not fatal
        self.assertIn("No findings.", out)

    def test_invalid_path_normal_mode_recorded(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        missing = str(self.tmp / "ghost.log")
        code, _, _ = self.run_cli(
            [missing, str(good), "--json", str(self.tmp / "r.json")])
        self.assertEqual(code, 0)  # recoverable; no findings
        payload = self.read_json("r.json")
        self.assertEqual(payload["errors"][0]["kind"], "input")
        self.assertIn("does not exist", payload["errors"][0]["reason"])

    def test_invalid_path_strict_mode_aborts(self):
        missing = str(self.tmp / "ghost.log")
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        code, _, err = self.run_cli([missing, str(good), "--strict"])
        self.assertEqual(code, 2)  # FR-100/FR-152
        self.assertIn("strict mode abort", err)
        # R4: the path is replaced with the neutral marker.
        self.assertIn("[REDACTED_PATH]", err)
        self.assertNotIn("ghost.log", err)

    def test_discovery_order_preserved(self):
        a = self.write("a.log", auth_line("11:20:01") + "\n")
        b = self.write("b.log", auth_line("11:20:02", port=51002) + "\n")
        seen = []
        real = cli.stream_parse_file

        def spy(path, *args, **kwargs):
            seen.append(str(path))
            yield from real(path, *args, **kwargs)

        with mock.patch.object(cli, "stream_parse_file", spy):
            self.run_cli([str(b), str(a)])
        self.assertEqual(seen, [str(b), str(a)])


class TestParsingAndStatistics(CliTestCase):
    def test_shared_reference_now_across_files(self):
        one = self.write("one.log", auth_line("11:20:01") + "\n")
        two = self.write("two.log", auth_line("11:20:02", port=51002) + "\n")
        stamps = []
        real = cli.stream_parse_file

        def spy(path, reference_now, **kwargs):
            stamps.append(reference_now)
            yield from real(path, reference_now, **kwargs)

        with mock.patch.object(cli, "stream_parse_file", spy):
            self.run_cli([str(one), str(two)])
        self.assertEqual(len(stamps), 2)
        self.assertEqual(stamps[0], stamps[1])   # one clock read per run
        self.assertEqual(type(stamps[0]), int)   # integer Unix timestamp

    def test_statistics_aggregation_and_dedup_counts(self):
        event = auth_line("11:20:01")                       # identical event
        first = self.write("first.log", f"{event}\n{event}\n garbage\n")
        second = self.write("second.log", f"{event}\n")
        code, payload = self.statistics_payload([str(first), str(second)])
        self.assertEqual(code, 0)   # one unique authfail; threshold 8 unmet
        stats = payload["statistics"]
        self.assertEqual(stats["files_scanned"], 2)
        self.assertEqual(stats["lines_read"], 4)            # 3 + 1
        self.assertEqual(stats["events_parsed"], 3)         # pre-dedup sum
        self.assertEqual(stats["malformed"], 1)             # ' garbage'
        self.assertEqual(stats["duplicates"], 1)            # intra-file repeat
        self.assertEqual(stats["othersyslog"], 0)
        self.assertEqual(stats["othersyslog_dropped"], 0)
        self.assertEqual(stats["cross_file_duplicates"], 1)  # second copy
        # Invariant: malformed + events_parsed == lines_read here (no drops).
        self.assertEqual(
            stats["malformed"] + stats["events_parsed"]
            + stats["othersyslog_dropped"], stats["lines_read"])

    def test_parser_errors_preserved_in_report(self):
        bad = self.write("bad.log", "totally not a log line\n")
        code, payload = self.statistics_payload([str(bad)])
        self.assertEqual(code, 0)   # normal mode: errors are data
        self.assertEqual(payload["statistics"]["malformed"], 1)
        self.assertEqual(payload["errors"][0]["kind"], "parse")
        self.assertEqual(payload["errors"][0]["line_number"], 1)

    def test_filesystem_race_after_discovery_recovered(self):
        keep = self.write("keep.log", auth_line("11:20:01") + "\n")
        gone = self.write("gone.log", auth_line("11:20:02", port=51002) + "\n")
        real = cli.stream_parse_file

        def flaky(path, *args, **kwargs):
            if "gone.log" in str(path):
                raise OSError(2, "No such file or directory")
            yield from real(path, *args, **kwargs)

        with mock.patch.object(cli, "stream_parse_file", flaky):
            code, payload = self.statistics_payload([str(gone), str(keep)])
        self.assertEqual(code, 0)               # race never crashes the run
        self.assertEqual(payload["statistics"]["files_scanned"], 1)
        self.assertEqual(len(payload["errors"]), 1)
        self.assertEqual(payload["errors"][0]["kind"], "input")
        self.assertIn("cannot read file", payload["errors"][0]["reason"])


class TestDetection(CliTestCase):
    def brute_force_file(self):
        lines = [auth_line(f"11:20:{n:02d}", port=51000 + n)
                 for n in range(8)]
        return self.write("brute.log", "\n".join(lines) + "\n")

    def test_findings_return_exit_code_1(self):
        brute = self.brute_force_file()
        code, payload = self.statistics_payload([str(brute)])
        self.assertEqual(code, 1)  # FR-090: findings -> 1
        self.assertEqual(payload["statistics"]["findings"], 1)
        self.assertEqual(payload["findings"][0]["rule_id"], "LS-RULE-001")
        self.assertEqual(payload["findings"][0]["src_ip"], "192.0.2.7")

    def test_below_threshold_returns_exit_code_0(self):
        lines = [auth_line(f"11:20:{n:02d}", port=51000 + n)
                 for n in range(7)]
        near = self.write("near.log", "\n".join(lines) + "\n")
        code, payload = self.statistics_payload([str(near)])
        self.assertEqual(code, 0)
        self.assertEqual(payload["findings"], [])

    def test_cli_threshold_override_lowers_detection_bar(self):
        lines = [auth_line(f"11:20:{n:02d}", port=51000 + n)
                 for n in range(4)]
        small = self.write("small.log", "\n".join(lines) + "\n")
        code, payload = self.statistics_payload(
            [str(small), "--ssh-threshold", "3"])
        self.assertEqual(code, 1)  # AC-006: override reaches the detector
        self.assertEqual(payload["findings"][0]["rule_id"], "LS-RULE-001")


class TestReporting(CliTestCase):
    def test_console_report_printed_to_stdout(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        code, out, _ = self.run_cli([str(good)])
        self.assertEqual(code, 0)
        self.assertIn("LogSentinel report (version 1)", out)
        self.assertIn("No findings.", out)

    def test_quiet_suppresses_console_but_not_report_files(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        code, out, _ = self.run_cli([
            str(good), "--quiet", "--json", str(self.tmp / "r.json")])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")               # console report suppressed
        self.assertTrue((self.tmp / "r.json").exists())   # JSON still written

    def test_text_report_written_atomically(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        code, _, _ = self.run_cli([str(good), "--text", str(self.tmp / "r.txt")])
        self.assertEqual(code, 0)
        content = (self.tmp / "r.txt").read_text(encoding="utf-8")
        self.assertIn("LogSentinel report (version 1)", content)

    def test_json_report_schema(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        code, _, _ = self.run_cli([str(good), "--json", str(self.tmp / "r.json")])
        self.assertEqual(code, 0)
        payload = self.read_json("r.json")
        self.assertEqual(payload["report_version"], 1)
        self.assertIn("generated_at", payload)
        self.assertIn("config_used", payload)
        self.assertIn("statistics", payload)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["findings"], [])

    def test_errors_included_in_json_report(self):
        missing = str(self.tmp / "ghost.log")
        code, _, _ = self.run_cli([
            missing, "--json", str(self.tmp / "r.json")])
        # Nothing scanned + input errors -> exit 2 (correction 4, FR-090);
        # the requested report is still produced and lists the errors.
        self.assertEqual(code, 2)
        payload = self.read_json("r.json")
        self.assertEqual(payload["errors"][0]["kind"], "input")
        # R4: source paths are never echoed in externally visible reports.
        self.assertEqual(payload["errors"][0]["source_file"],
                         "[REDACTED_PATH]")

    def test_error_overflow_handled_by_report_layer(self):
        garbage = "\n".join(f"junk {n}" for n in range(150)) + "\n"
        bad = self.write("bad.log", garbage)
        code, _, _ = self.run_cli([
            str(bad), "--json", str(self.tmp / "r.json"),
            "--text", str(self.tmp / "r.txt")])
        self.assertEqual(code, 0)  # FR-154: cap lives in the report layer
        payload = self.read_json("r.json")
        self.assertEqual(payload["errors_overflow"], {"shown": 100,
                                                      "total": 150})
        text_report = (self.tmp / "r.txt").read_text(encoding="utf-8")
        self.assertIn("errors: 100 of 150 shown", text_report)

    def test_report_write_failure_returns_exit_code_2(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        target = self.tmp / "missing-dir" / "r.json"
        code, _, err = self.run_cli([str(good), "--json", str(target)])
        self.assertEqual(code, 2)  # ReportError -> 2 (FR-090)
        self.assertIn("cannot write report", err)

    def test_no_report_written_when_analysis_fails(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        target = self.tmp / "r.json"
        with mock.patch.object(cli, "HTTP4xxAbuseDetector", BoomDetector):
            code, _, err = self.run_cli([str(good), "--json", str(target)])
        self.assertEqual(code, 3)
        self.assertFalse(target.exists())   # no partial JSON report (FR-153)


class BoomDetector(cli.HTTP4xxAbuseDetector):
    """Detector whose results() raises - simulates unexpected failures."""

    def results(self):
        raise RuntimeError("boom")


class LeakyBoomDetector(cli.HTTP4xxAbuseDetector):
    """R3: detector whose failure message embeds a keyed log secret."""

    def results(self):
        raise RuntimeError("password=hunter2 leaked into detector state")


class TestErrorHandling(CliTestCase):
    def test_strict_parser_error_aborts_exit_2(self):
        bad = self.write("bad.log", "totally not a log line\n")
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        code, _, err = self.run_cli([str(bad), str(good), "--strict"])
        self.assertEqual(code, 2)  # AC-007
        self.assertIn("strict mode abort", err)
        # R4: the path is never echoed; line number is preserved.
        self.assertIn("[REDACTED_PATH]", err)
        self.assertNotIn("bad.log", err)
        self.assertIn("line 1", err)

    def test_strict_abort_reason_sanitized_on_stderr(self):
        """Regression (security audit R2): parser exception reasons can
        embed raw log-line tokens (an invalid IP echoes the offending
        token), and the strict-mode abort message reaches stderr.
        The abort reason must be sanitized before that happens.
        """
        bad = self.write(
            "secret.log",
            "Mar 10 11:20:01 h sshd[1001]: Failed password for admin "
            "from password=hunter2 port 22 ssh2\n")
        code, _, err = self.run_cli([str(bad), "--strict"])
        self.assertEqual(code, 2)  # strict abort behaviour unchanged
        self.assertIn("strict mode abort", err)
        self.assertIn("<REDACTED>", err)   # marker present
        self.assertNotIn("hunter2", err)   # secret value absent
        # R4: the source path is externally visible, so it is replaced
        # with the neutral marker; the file name must not appear.
        self.assertIn("[REDACTED_PATH]", err)
        self.assertNotIn("secret.log", err)

    def test_strict_abort_exception_mapping(self):
        cases = {
            "config": ConfigError,
            "input": InputPathError,
            "parse": ParseError,
            "report": ReportError,
        }
        for kind, expected_type in cases.items():
            with self.subTest(kind=kind):
                entry = ErrorEntry(source_file="f.log", line_number=3,
                                   reason="whatever", kind=kind)
                exception = cli._strict_abort(entry)
                self.assertIsInstance(exception, expected_type)
                # R4: the path is never echoed; line number is preserved.
                self.assertIn("[REDACTED_PATH]", str(exception))
                self.assertNotIn("f.log", str(exception))
                self.assertIn("line 3", str(exception))

    def test_unexpected_exception_returns_exit_3_with_short_diagnostic(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        with mock.patch.object(cli, "HTTP4xxAbuseDetector", BoomDetector):
            code, out, err = self.run_cli([str(good)])
        self.assertEqual(code, 3)  # FR-153
        self.assertIn("unexpected failure", err)
        self.assertIn("RuntimeError", err)
        self.assertNotIn("Traceback", err)   # no traceback in normal CLI use
        self.assertNotIn("Traceback", out)

    def test_unexpected_exception_message_sanitized(self):
        """Regression (security audit R3): an unexpected exception's message
        can embed log-derived content; it is sanitized (best-effort) before
        reaching stderr. Class name, short-diagnostic behaviour and exit
        code 3 are preserved. Would fail under the previous implementation,
        which printed str(exc) raw.
        """
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        with mock.patch.object(cli, "HTTP4xxAbuseDetector", LeakyBoomDetector):
            code, out, err = self.run_cli([str(good)])
        self.assertEqual(code, 3)                       # exit code unchanged
        self.assertIn("unexpected failure", err)        # diagnostic prefix
        self.assertIn("RuntimeError", err)              # class name preserved
        self.assertIn("<REDACTED>", err)                # keyed secret redacted
        self.assertNotIn("hunter2", err)                # secret absent
        self.assertNotIn("Traceback", err)              # short diagnostic kept
        self.assertNotIn("Traceback", out)

    def test_application_errors_exit_2(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        with mock.patch.object(cli, "stream_parse_file",
                               side_effect=ParseError("synthetic")):
            code, _, err = self.run_cli([str(good)])
        self.assertEqual(code, 2)
        self.assertIn("synthetic", err)


class TestStrictFilesystemRace(CliTestCase):
    """Correction 1: parse-time OSError under normal vs strict mode."""

    def flaky_parser(self, failing_name, record):
        real = cli.stream_parse_file

        def spy(path, *args, **kwargs):
            record.append(str(path))
            if failing_name in str(path):
                raise OSError(13, "Permission denied")
            yield from real(path, *args, **kwargs)

        return spy

    def test_normal_mode_continues_after_race(self):
        keep = self.write("keep.log", auth_line("11:20:01") + "\n")
        gone = self.write("gone.log", auth_line("11:20:02", port=51002) + "\n")
        record = []
        with mock.patch.object(cli, "stream_parse_file",
                               self.flaky_parser("gone.log", record)):
            code, payload = self.statistics_payload([str(gone), str(keep)])
        self.assertEqual(code, 0)                # normal mode: keep going
        self.assertEqual(payload["statistics"]["files_scanned"], 1)
        self.assertEqual(payload["errors"][0]["kind"], "input")
        self.assertIn("cannot read file", payload["errors"][0]["reason"])
        # R4: source paths are never echoed in externally visible reports.
        self.assertEqual(payload["errors"][0]["source_file"],
                         "[REDACTED_PATH]")

    def test_strict_mode_aborts_on_parse_time_race(self):
        keep = self.write("keep.log", auth_line("11:20:01") + "\n")
        gone = self.write("gone.log", auth_line("11:20:02", port=51002) + "\n")
        record = []
        with mock.patch.object(cli, "stream_parse_file",
                               self.flaky_parser("gone.log", record)):
            code, _, err = self.run_cli([str(gone), str(keep), "--strict"])
        self.assertEqual(code, 2)                # strict abort -> exit 2
        self.assertIn("strict mode abort", err)
        # R4: the path is replaced with the neutral marker.
        self.assertIn("[REDACTED_PATH]", err)
        self.assertNotIn("gone.log", err)
        self.assertIn("Permission denied", err)  # filesystem context

    def test_strict_mode_does_not_parse_subsequent_files(self):
        keep = self.write("keep.log", auth_line("11:20:01") + "\n")
        gone = self.write("gone.log", auth_line("11:20:02", port=51002) + "\n")
        record = []
        with mock.patch.object(cli, "stream_parse_file",
                               self.flaky_parser("gone.log", record)):
            self.run_cli([str(gone), str(keep), "--strict"])
        parsed = [name for name in record if "keep.log" in name]
        self.assertEqual(parsed, [])   # subsequent file never parsed


class TestUnexpectedBoundary(CliTestCase):
    """Correction 2: the unexpected-exception boundary covers config+clock."""

    def test_load_config_unexpected_returns_exit_3(self):
        with mock.patch.object(cli, "load_config",
                               side_effect=RuntimeError("cfg boom")):
            code, out, err = self.run_cli(["whatever.log"])
        self.assertEqual(code, 3)
        self.assertIn("unexpected failure", err)
        self.assertIn("cfg boom", err)
        self.assertNotIn("Traceback", err)

    def test_clock_capture_unexpected_returns_exit_3(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        target = self.tmp / "r.json"
        with mock.patch.object(cli, "datetime") as fake_clock:
            fake_clock.now.side_effect = RuntimeError("clock boom")
            code, _, err = self.run_cli(
                [str(good), "--json", str(target)])
        self.assertEqual(code, 3)
        self.assertIn("clock boom", err)
        self.assertNotIn("Traceback", err)
        self.assertFalse(target.exists())   # no partial report (FR-153)


class TestRenderBeforeWrite(CliTestCase):
    """Correction 3: render all reports before writing any of them."""

    def test_text_render_failure_leaves_no_report_files(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        json_target = self.tmp / "r.json"
        text_target = self.tmp / "r.txt"
        with mock.patch.object(cli, "render_console",
                               side_effect=RuntimeError("render boom")):
            code, _, err = self.run_cli([
                str(good), "--json", str(json_target),
                "--text", str(text_target)])
        self.assertEqual(code, 3)   # unexpected rendering failure
        self.assertIn("render boom", err)
        self.assertNotIn("Traceback", err)
        self.assertFalse(json_target.exists())  # JSON was rendered, not written
        self.assertFalse(text_target.exists())

    def test_both_reports_written_when_rendering_succeeds(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        json_target = self.tmp / "r.json"
        text_target = self.tmp / "r.txt"
        code, _, _ = self.run_cli([
            str(good), "--json", str(json_target),
            "--text", str(text_target)])
        self.assertEqual(code, 0)
        self.assertTrue(json_target.exists())
        self.assertTrue(text_target.exists())


class TestNothingScannedExitCodes(CliTestCase):
    """Correction 4: exit 2 when input problems leave nothing scanned."""

    def test_discovery_errors_with_zero_scanned_exit_2(self):
        missing = str(self.tmp / "ghost.log")
        code, _, _ = self.run_cli([missing])
        self.assertEqual(code, 2)   # FR-090: nothing analysed

    def test_all_parse_races_exit_2(self):
        one = self.write("one.log", auth_line("11:20:01") + "\n")
        two = self.write("two.log", auth_line("11:20:02", port=51002) + "\n")
        with mock.patch.object(cli, "stream_parse_file",
                               side_effect=OSError(2, "No such file")):
            code, _, _ = self.run_cli([str(one), str(two)])
        self.assertEqual(code, 2)   # every file failed at parse time

    def test_discovery_error_with_one_scanned_file_exit_0(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        missing = str(self.tmp / "ghost.log")
        code, _, _ = self.run_cli([missing, str(good)])
        self.assertEqual(code, 0)   # something scanned -> normal exit codes

    def test_empty_directory_without_errors_exit_0(self):
        empty = self.tmp / "empty"
        empty.mkdir()
        code, _, err = self.run_cli([str(empty)])
        self.assertEqual(code, 0)   # valid empty discovery, warning only
        self.assertIn("no input files", err)

    def test_parser_errors_on_scanned_file_do_not_exit_2(self):
        bad = self.write("bad.log", "totally not a log line\n")
        code, _, _ = self.run_cli([str(bad)])
        self.assertEqual(code, 0)   # ordinary parse errors are not input-path


class TestEntryPoints(CliTestCase):
    def test_python_dash_m_entry_point(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path("src").resolve())
        proc = subprocess.run(
            [sys.executable, "-m", "logsentinel", "--version"],
            capture_output=True, text=True, env=env, cwd=os.getcwd())
        self.assertEqual(proc.returncode, 0)
        self.assertIn(f"logsentinel {__version__}", proc.stdout)

    def test_version_single_source_of_truth(self):
        self.assertEqual(__version__, "0.1.0")
        self.assertEqual(cli.__version__, __version__)
        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.1.0"', pyproject)

    def test_console_entry_point_declared(self):
        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('logsentinel = "logsentinel.cli:main"', pyproject)


class TestStorageLifecycle(CliTestCase):
    """Phase 5 spec 3.8: staging database cleanup on every failure path."""

    def run_cli_tracking_storage(self, argv):
        """Run main() while recording every staging database path."""
        created = []
        real_init = RunStorage.__init__

        def spy_init(storage_self, directory=None):
            real_init(storage_self, directory)
            created.append(storage_self.path)

        with mock.patch.object(cli.RunStorage, "__init__", spy_init):
            code, out, err = self.run_cli(argv)
        return code, created, err

    def test_cleanup_after_strict_abort(self):
        missing = str(self.tmp / "ghost.log")
        code, created, _ = self.run_cli_tracking_storage([missing, "--strict"])
        self.assertEqual(code, 2)
        self.assertTrue(created)
        self.assertTrue(all(not os.path.exists(path) for path in created))

    def test_cleanup_after_unexpected_exception(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        with mock.patch.object(cli, "HTTP4xxAbuseDetector", BoomDetector):
            code, created, _ = self.run_cli_tracking_storage([str(good)])
        self.assertEqual(code, 3)
        self.assertTrue(created)
        self.assertTrue(all(not os.path.exists(path) for path in created))

    def test_cleanup_after_report_rendering_failure(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        with mock.patch.object(cli, "render_console",
                               side_effect=RuntimeError("render boom")):
            code, created, _ = self.run_cli_tracking_storage(
                [str(good), "--text", str(self.tmp / "r.txt")])
        self.assertEqual(code, 3)
        self.assertTrue(created)
        self.assertTrue(all(not os.path.exists(path) for path in created))

    def test_cleanup_after_report_write_failure(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        target = self.tmp / "missing-dir" / "r.json"
        code, created, _ = self.run_cli_tracking_storage(
            [str(good), "--json", str(target)])
        self.assertEqual(code, 2)
        self.assertTrue(created)
        self.assertTrue(all(not os.path.exists(path) for path in created))

    def test_cleanup_after_parser_parameter_error(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        with mock.patch.object(cli, "stream_parse_file",
                               side_effect=ParseError("synthetic")):
            code, created, _ = self.run_cli_tracking_storage([str(good)])
        self.assertEqual(code, 2)
        self.assertTrue(created)
        self.assertTrue(all(not os.path.exists(path) for path in created))

    def test_cleanup_after_success(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        code, created, _ = self.run_cli_tracking_storage([str(good)])
        self.assertEqual(code, 0)
        self.assertTrue(created)
        self.assertTrue(all(not os.path.exists(path) for path in created))


class TestStreamingWiring(CliTestCase):
    """Phase 5 spec 3.10: the CLI streams; it never builds full lists."""

    def test_cli_never_calls_compatibility_parse_file(self):
        good = self.write("good.log", auth_line("11:20:01") + "\n")
        with mock.patch.object(lsentinel_parsers, "parse_file",
                               side_effect=AssertionError(
                                   "compatibility parser used by CLI")):
            code, _, err = self.run_cli([str(good)])
        self.assertEqual(code, 0)
        self.assertNotIn("compatibility parser", err)

    def test_cli_uses_streaming_parser_per_file(self):
        one = self.write("one.log", auth_line("11:20:01") + "\n")
        two = self.write("two.log", auth_line("11:20:02", port=51002) + "\n")
        real = cli.stream_parse_file
        streamed = []
        original_parse = lsentinel_parsers.parse_file

        def spy(path, *args, **kwargs):
            streamed.append(str(path))
            yield from real(path, *args, **kwargs)

        with mock.patch.object(cli, "stream_parse_file", spy), \
                mock.patch.object(lsentinel_parsers, "parse_file",
                                  side_effect=AssertionError("compat used")):
            code, _, _ = self.run_cli([str(one), str(two)])
        self.assertEqual(code, 0)
        self.assertEqual(streamed, [str(one), str(two)])
        self.assertIsNot(original_parse, None)

    def test_cli_source_has_no_full_run_accumulation(self):
        import inspect
        source = inspect.getsource(cli)
        self.assertNotIn("all_events", source)
        self.assertNotIn("errors.extend", source)
        self.assertNotIn("all_events.extend", source)
        # Deduplication is performed by storage, not on an in-memory list.
        self.assertNotIn("dedup_cross_file(all_events", source)


class TestScaleStreaming(CliTestCase):
    """Phase 5 spec 3.11 scale test: >100k lines, end-to-end incremental.

    Construction (exact expected statistics by design):
    - auth.log:    8 failures/192.0.2.7 (finding), 2 identical failures
                   192.0.2.8 (intra-file dup), 35000 accepted/192.0.2.9
                   (context only), 100 malformed, 3 copies of the shared
                   cross-file line            -> 35113 lines
    - firewall.log: 10 distinct ports/198.51.100.23 (finding), 2 copies of
                   the shared cross-file line, 35000 same-port lines
                   198.51.100.24, 100 malformed -> 35112 lines
    - access.log:  8 x 404 distinct paths/203.0.113.50 (finding), 35000 x
                   200/203.0.113.51, 2 identical 404s/203.0.113.52 (intra-
                   file dup), 100 malformed  -> 35110 lines
    Totals: 105335 lines; 105035 events_parsed; 300 malformed; duplicates
    3 + 1 + 1 = 5 (incl. the 3-copy cross-file line inside auth.log);
    cross-file duplicates removed = 2 (auth 3, firewall 2 -> cap 3).
    """

    @classmethod
    def setUpClass(cls):
        cls._big = tempfile.TemporaryDirectory()
        cls.big = Path(cls._big.name)
        build_scale_corpus(cls.big)
        shared = UNUSED_SENTINEL = None  # noqa: F841 - kept below for docs
        del shared, UNUSED_SENTINEL

    @staticmethod
    def _corpus_lines():
        shared = ("Mar 10 12:00:00 h sshd[1]: Failed password for admin "
                  "from 192.0.2.77 port 1 ssh2")
        auth = [auth_line(f"11:20:{n:02d}", port=51000 + n)
                for n in range(8)]
        auth += [auth_line("11:30:00", ip="192.0.2.8", port=52000)] * 2
        auth += ["Mar 10 13:00:{:02d} h sshd[2]: Accepted publickey for "
                 "deploy from 192.0.2.9 port {} ssh2".format(n % 60, n)
                 for n in range(35000)]
        auth += [f"junk auth {n}" for n in range(100)]
        auth += [shared] * 3
        fw_lines = [fw_line(1000 + n) for n in range(10)]
        fw_lines += [shared] * 2
        fw_lines += ["Mar 10 09:{:02d}:{:02d} fw kernel: DROP IN=eth0 "
                     "OUT= SRC=198.51.100.24 DST=203.0.113.10 PROTO=TCP "
                     "SPT={} DPT=80".format((n // 60) % 60, n % 60, 40000 + n)
                     for n in range(35000)]
        fw_lines += [f"junk fw {n}" for n in range(100)]
        web = ['203.0.113.50 - - [10/Mar/2026:11:00:{:02d} +0000] '
               '"GET /p{} HTTP/1.1" 404 153'.format(n % 60, n)
               for n in range(8)]
        web += ['203.0.113.51 - - [10/Mar/2026:11:{:02d}:{:02d} +0000] '
                '"GET /ok{} HTTP/1.1" 200 10'.format(
                    (n // 60) % 60, n % 60, n)
                for n in range(35000)]
        web += ['203.0.113.52 - - [10/Mar/2026:11:02:00 +0000] '
                '"GET /dup HTTP/1.1" 404 5'] * 2
        web += [f"junk web {n}" for n in range(100)]
        return {"auth.log": auth, "firewall.log": fw_lines,
                "access.log": web}

    @classmethod
    def tearDownClass(cls):
        cls._big.cleanup()

    def test_end_to_end_incremental_scale(self):
        # Prove the CLI never touches the compatibility parser at scale.
        json_target = self.big / "r.json"
        with mock.patch.object(lsentinel_parsers, "parse_file",
                               side_effect=AssertionError("compat used")):
            code, _, err = self.run_cli([
                str(self.big), "--json", str(json_target)])
        self.assertEqual(code, 1)   # three findings
        payload = json.loads(json_target.read_text(encoding="utf-8"))
        stats = payload["statistics"]
        self.assertEqual(stats["files_scanned"], 3)
        self.assertEqual(stats["lines_read"], 105335)
        self.assertEqual(stats["events_parsed"], 105035)
        self.assertEqual(stats["malformed"], 300)
        self.assertEqual(stats["duplicates"], 5)
        self.assertEqual(stats["othersyslog"], 0)
        self.assertEqual(stats["othersyslog_dropped"], 0)
        self.assertEqual(stats["cross_file_duplicates"], 2)
        self.assertEqual(
            stats["malformed"] + stats["events_parsed"]
            + stats["othersyslog_dropped"], stats["lines_read"])
        # Exact overflow through the errors_total streaming path.
        self.assertEqual(payload["errors_overflow"],
                         {"shown": 100, "total": 300})
        # Exactly one finding per rule, for the designed source IPs.
        self.assertEqual(
            [(f["rule_id"], f["src_ip"]) for f in payload["findings"]],
            [("LS-RULE-001", "192.0.2.7"),
             ("LS-RULE-002", "198.51.100.23"),
             ("LS-RULE-003", "203.0.113.50")])
        ssh_finding = payload["findings"][0]
        self.assertEqual(ssh_finding["summary"]["failed_count"], 8)
        self.assertEqual(len(ssh_finding["evidence"]), 8)
        self.assertEqual(ssh_finding["summary"]["successful_followups"], 0)
        # Staging database cleaned up after the run.
        self.assertFalse(any(
            (self.big / name).exists()
            for name in ("staging.sqlite3",)))





def build_scale_corpus(directory):
    """Write the ~105k-line scale corpus (see TestScaleStreaming docs)."""
    corpus = TestScaleStreaming._corpus_lines()
    for name, lines in corpus.items():
        (Path(directory) / name).write_text("\n".join(lines) + "\n",
                                            encoding="utf-8", newline="")

class TestSQLiteBackedDuplicates(CliTestCase):
    """Phase 5 correction: intra-file duplicate tracking lives in SQLite
    in the CLI streaming path - no per-file in-memory fingerprint set."""

    def test_storage_backed_tracker_used_per_event(self):
        one = self.write(
            "one.log",
            auth_line("11:20:01") + "\n" + auth_line("11:20:01") + "\n")
        calls = []
        real = cli.RunStorage.fingerprint_seen

        def spy(storage_self, event):
            result = real(storage_self, event)
            calls.append((event.raw_line, result))
            return result

        with mock.patch.object(cli.RunStorage, "fingerprint_seen", spy):
            code, payload = self.statistics_payload([str(one)])
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 2)            # consulted per event
        self.assertEqual([result for _, result in calls], [False, True])
        self.assertEqual(payload["statistics"]["duplicates"], 1)
        self.assertEqual(payload["statistics"]["events_parsed"], 2)

    def test_tracker_answers_are_authoritative_in_cli(self):
        # If any in-memory fingerprint set still participated in the CLI
        # path, forcing the tracker to answer True would not change the
        # statistics. It does - proving the tracker is the single source.
        one = self.write(
            "one.log",
            auth_line("11:20:01") + "\n"
            + auth_line("11:20:02", port=51002) + "\n")
        with mock.patch.object(cli.RunStorage, "fingerprint_seen",
                               return_value=True):
            code, payload = self.statistics_payload([str(one)])
        self.assertEqual(payload["statistics"]["events_parsed"], 2)
        self.assertEqual(payload["statistics"]["duplicates"], 2)

    def test_same_file_repeats_remain_staged_and_detector_countable(self):
        # 8 byte-identical failures within the window -> failed_count 8:
        # every repeat is staged and every occurrence reaches the detector.
        line = auth_line("11:20:01")
        brute = self.write("brute.log", "\n".join([line] * 8) + "\n")
        code, payload = self.statistics_payload([str(brute)])
        self.assertEqual(code, 1)
        self.assertEqual(payload["statistics"]["duplicates"], 7)
        self.assertEqual(payload["statistics"]["events_parsed"], 8)
        finding = payload["findings"][0]
        self.assertEqual(finding["summary"]["failed_count"], 8)
        self.assertEqual(len(finding["evidence"]), 8)

    def test_rollback_discards_duplicate_knowledge(self):
        # Duplicate knowledge from the rolled-back UTF-8 attempt must not
        # leak into the Latin-1 retry's statistics (shared transaction).
        auth = (auth_line("11:20:01") + "\n") * 2   # intra-file duplicate
        path = self.tmp / "fallback.log"
        path.write_bytes(auth.encode("utf-8") + b"\xff tail\n")
        code, payload = self.statistics_payload([str(path)])
        self.assertEqual(code, 0)
        stats = payload["statistics"]
        self.assertEqual(stats["duplicates"], 1)   # retry pass only
        self.assertEqual(stats["events_parsed"], 2)
        self.assertEqual(stats["lines_read"], 3)

    def test_cross_file_multiplicity_unchanged(self):
        shared = auth_line("11:20:01")
        a = self.write("a.log", "\n".join([shared] * 3) + "\n")
        b = self.write("b.log", "\n".join([shared] * 2) + "\n")
        code, payload = self.statistics_payload([str(a), str(b)])
        self.assertEqual(payload["statistics"]["duplicates"], 3)
        self.assertEqual(payload["statistics"]["cross_file_duplicates"], 2)
        self.assertEqual(payload["statistics"]["events_parsed"], 5)
        self.assertEqual(payload["statistics"]["files_scanned"], 2)


class TestMemoryEnvelope(CliTestCase):
    """Tracemalloc check that the pipeline stays within the per-IP
    aggregation envelope (NFR-004).

    Methodology: ``tracemalloc`` traces Python allocations while the CLI
    processes the ~105k-line scale corpus; the assertion bounds peak traced
    memory. Limitations: tracemalloc measures only traced (Python) memory,
    adds interpreter overhead, and the bound was chosen well above the
    streaming pipeline's measured baseline (~10 MB) while remaining below
    the cost of buffering the full run's event objects (>60 MB). It is a
    regression guard, not a precise memory audit.
    """

    def test_streaming_peak_memory_stays_bounded(self):
        import tracemalloc
        with tempfile.TemporaryDirectory() as corpus_dir:
            build_scale_corpus(corpus_dir)
            tracemalloc.start()
            try:
                code, _, _ = self.run_cli([corpus_dir])
            finally:
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
        self.assertEqual(code, 1)
        self.assertLess(peak, 30 * 1024 * 1024,  # 30 MB regression bound
                        f"peak traced memory {peak / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    unittest.main()
