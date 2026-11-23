"""Tests for the headless GUI analysis adapter.

These tests do not require PySide6. They verify that the GUI adapter:

- produces exactly the same findings, statistics, errors and JSON report as
  the existing CLI when given the same run instant;
- preserves strict-mode abort, cancellation, and storage cleanup;
- keeps report rendering delegated to the existing redaction layer;
- exposes progress without leaking log content, and mirrors CLI exit codes.
"""

import json
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from logsentinel import cli
from logsentinel.config import AppConfig, load_config
from logsentinel.exceptions import ParseError
from logsentinel.gui import backend
from logsentinel.storage import RunStorage

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = PROJECT_ROOT / "samples"


class GuiBackendTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = SAMPLES
        cls.default_config = load_config(None, None)

    def request(self, paths, config=None, now=None):
        return backend.AnalysisRequest.from_paths(
            paths, config or self.default_config, now=now)

    def write_log(self, directory, name, content):
        path = Path(directory) / name
        path.write_text(content, encoding="utf-8")
        return path


class TestRequestAndClock(GuiBackendTestCase):
    def test_from_paths_captures_one_instant_for_both_fields(self):
        now = datetime(2026, 3, 10, 12, 0, 0, tzinfo=timezone.utc)
        request = self.request([self.samples], now=now)
        self.assertEqual(request.generated_at, "2026-03-10T12:00:00+00:00")
        self.assertEqual(request.reference_now, int(now.timestamp()))

    def test_naive_now_is_treated_as_utc(self):
        now = datetime(2026, 3, 10, 12, 0, 0)
        request = self.request([self.samples], now=now)
        self.assertEqual(request.generated_at, "2026-03-10T12:00:00+00:00")

    def test_single_path_is_not_split_into_characters(self):
        request = self.request(self.samples)
        self.assertEqual(request.paths, (self.samples,))


class TestSampleParity(GuiBackendTestCase):
    def test_exact_json_parity_with_cli(self):
        with TemporaryDirectory() as directory:
            report_path = Path(directory) / "cli-report.json"
            exit_code = cli.main([
                str(self.samples), "--quiet", "--json", str(report_path)])
            self.assertEqual(exit_code, 1)
            cli_text = report_path.read_text(encoding="utf-8")
            cli_payload = json.loads(cli_text)

            # Reuse the CLI's own run instant so results are byte-identical.
            generated_at = cli_payload["generated_at"]
            reference_now = int(
                datetime.fromisoformat(generated_at).timestamp())
            request = backend.AnalysisRequest(
                paths=(str(self.samples),),
                config=self.default_config,
                generated_at=generated_at,
                reference_now=reference_now,
            )
            result = backend.run_analysis(request)

        self.assertEqual(result.exit_code, exit_code)
        self.assertEqual(result.render_json(), cli_text)

    def test_structured_sample_results(self):
        result = backend.run_analysis(self.request([self.samples]))

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.statistics.files_scanned, 3)
        self.assertEqual(result.statistics.lines_read, 44)
        self.assertEqual(result.statistics.events_parsed, 43)
        self.assertEqual(result.statistics.malformed, 1)
        self.assertEqual(result.statistics.duplicates, 1)
        self.assertEqual(result.statistics.othersyslog, 2)
        self.assertEqual(result.statistics.othersyslog_dropped, 0)
        self.assertEqual(result.statistics.cross_file_duplicates, 0)
        self.assertEqual(result.errors_total, 1)
        self.assertEqual(len(result.files), 3)
        self.assertEqual(
            [(f.rule_id, f.severity, f.src_ip) for f in result.findings],
            [
                ("LS-RULE-001", "high", "192.0.2.7"),
                ("LS-RULE-002", "medium", "198.51.100.23"),
                ("LS-RULE-003", "medium", "203.0.113.50"),
            ],
        )

    def test_render_methods_do_not_write_report_files(self):
        result = backend.run_analysis(self.request([self.samples]))
        with mock.patch.object(
            backend, "_render_json", wraps=backend._render_json
        ) as render_json_spy, mock.patch.object(
            backend, "_render_console", wraps=backend._render_console
        ) as render_console_spy:
            result.render_json()
            result.render_text()
        self.assertEqual(render_json_spy.call_count, 1)
        self.assertEqual(render_console_spy.call_count, 1)


class TestProgress(GuiBackendTestCase):
    def test_progress_phases_and_monotonic_file_counts(self):
        events = []
        result = backend.run_analysis(
            self.request([self.samples]), progress=events.append)

        phases = [event.phase for event in events]
        self.assertEqual(phases[0], "discovery")
        self.assertIn("reading", phases)
        self.assertIn("deduplicating", phases)
        self.assertIn("detecting", phases)
        self.assertIn("finalizing", phases)
        self.assertEqual(phases[-1], "complete")
        self.assertEqual(events[-1].files_done, 3)
        self.assertEqual(events[-1].files_total, 3)
        self.assertEqual(events[-1].events_seen, result.statistics.events_parsed)

        reading = [event for event in events if event.phase == "reading"]
        done_values = [event.files_done for event in reading]
        self.assertEqual(done_values, sorted(done_values))
        self.assertEqual(done_values[-1], 3)
        # Progress messages are count-based and never contain log content.
        for event in events:
            self.assertNotIn("ssh", event.message.lower())
            self.assertNotIn("hunter2", event.message)


class TestCancellationAndCleanup(GuiBackendTestCase):
    def test_cancellation_stops_run_and_cleans_storage(self):
        class TrackingStorage(RunStorage):
            instances = []

            def __init__(self, directory=None):
                super().__init__(directory)
                self.was_closed = False
                TrackingStorage.instances.append(self)

            def close(self):
                super().close()
                self.was_closed = True

        cancel = threading.Event()

        def progress(event):
            if event.phase == "reading" and event.files_done == 0:
                cancel.set()

        with mock.patch.object(backend, "RunStorage", TrackingStorage):
            with self.assertRaises(backend.AnalysisCancelled):
                backend.run_analysis(
                    self.request([self.samples]),
                    progress=progress,
                    cancel_event=cancel,
                )

        self.assertTrue(TrackingStorage.instances)
        storage = TrackingStorage.instances[0]
        self.assertTrue(storage.was_closed)
        self.assertFalse(Path(storage.path).exists())

    def test_unexpected_failure_propagates_and_cleans_storage(self):
        class BoomDetector:
            def __init__(self, *args, **kwargs):
                pass

            def observe(self, event):
                pass

            def results(self):
                raise RuntimeError("synthetic detector failure")

        class TrackingStorage(RunStorage):
            instances = []

            def __init__(self, directory=None):
                super().__init__(directory)
                self.was_closed = False
                TrackingStorage.instances.append(self)

            def close(self):
                super().close()
                self.was_closed = True

        with mock.patch.object(
            backend, "HTTP4xxAbuseDetector", BoomDetector
        ), mock.patch.object(backend, "RunStorage", TrackingStorage):
            with self.assertRaises(RuntimeError):
                backend.run_analysis(self.request([self.samples]))

        self.assertTrue(TrackingStorage.instances)
        storage = TrackingStorage.instances[0]
        self.assertTrue(storage.was_closed)
        self.assertFalse(Path(storage.path).exists())


class TestSecurityAndStrictMode(GuiBackendTestCase):
    def test_strict_abort_is_sanitized(self):
        with TemporaryDirectory() as directory:
            bad = self.write_log(
                directory,
                "secret.log",
                "Mar 10 11:20:01 h sshd[1001]: Failed password for admin "
                "from password=hunter2 port 22 ssh2\n",
            )
            config = load_config({"strict": True}, None)
            with self.assertRaises(ParseError) as raised:
                backend.run_analysis(self.request([bad], config=config))

        message = str(raised.exception)
        self.assertIn("strict mode abort", message)
        self.assertIn("<REDACTED>", message)
        self.assertNotIn("hunter2", message)
        self.assertIn("[REDACTED_PATH]", message)
        self.assertNotIn("secret.log", message)
        self.assertIn("line 1", message)

    def test_rendered_reports_redact_evidence_paths_and_errors(self):
        lines = [
            "Mar 10 11:20:01 h sshd[1]: Failed password for invalid user "
            f"password=hunter2 from 192.0.2.7 port {51000 + index} ssh2"
            for index in range(8)
        ]
        lines.append(
            "Mar 10 11:20:02 h sshd[2]: Failed password for admin "
            "from password=hunter2 port 22 ssh2")
        with TemporaryDirectory() as directory:
            log_path = self.write_log(
                directory, "sensitive.log", "\n".join(lines) + "\n")
            result = backend.run_analysis(self.request([log_path]))

        self.assertEqual(result.errors_total, 1)
        self.assertEqual(len(result.findings), 1)
        rendered_json = result.render_json()
        rendered_text = result.render_text()
        for rendered in (rendered_json, rendered_text):
            self.assertIn("<REDACTED>", rendered)
            self.assertNotIn("hunter2", rendered)
            self.assertNotIn("sensitive.log", rendered)
            self.assertNotIn(str(Path(directory)), rendered)
        payload = json.loads(rendered_json)
        self.assertEqual(payload["errors"][0]["source_file"],
                         "[REDACTED_PATH]")


class TestInputOutcomes(GuiBackendTestCase):
    def test_empty_directory_is_a_clean_run(self):
        with TemporaryDirectory() as directory:
            result = backend.run_analysis(self.request([directory]))
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.statistics.files_scanned, 0)
        self.assertEqual(result.findings, ())
        self.assertEqual(result.errors_total, 0)

    def test_missing_input_returns_exit_code_two_and_structured_error(self):
        with TemporaryDirectory() as directory:
            missing = Path(directory) / "ghost.log"
            result = backend.run_analysis(self.request([missing]))

        self.assertEqual(result.exit_code, 2)
        self.assertEqual(result.statistics.files_scanned, 0)
        self.assertEqual(result.errors_total, 1)
        self.assertEqual(result.errors[0].kind, "input")
        payload = json.loads(result.render_json())
        self.assertEqual(payload["errors"][0]["source_file"],
                         "[REDACTED_PATH]")
        self.assertNotIn("ghost.log", result.render_json())

    def test_config_is_preserved_on_result(self):
        config = AppConfig(ssh_threshold=5, ssh_window_seconds=60)
        result = backend.run_analysis(self.request([self.samples], config=config))
        self.assertIs(result.config, config)
        self.assertIn('"ssh_threshold": 5', result.render_json())


if __name__ == "__main__":  # pragma: no cover - unittest discovery entry
    unittest.main()
