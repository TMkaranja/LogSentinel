"""Tests for GUI JSON/HTML report rendering, export, and latest-result state."""

import json
import os
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from logsentinel.config import load_config
from logsentinel.events import ErrorEntry, Finding
from logsentinel.exceptions import ReportError
from logsentinel.gui.backend import AnalysisRequest, AnalysisResult, run_analysis
from logsentinel.gui.reporting import (
    HTML_FORMAT,
    JSON_FORMAT,
    default_report_filename,
    ensure_export_extension,
    export_report,
    format_generated_at,
    render_html_report,
    report_filter,
    suggested_export_path,
)
from logsentinel.report import RunStatistics, _REDACTED_PATH

try:
    from PySide6.QtWidgets import QApplication

    from logsentinel.gui.app import create_application
    from logsentinel.gui.main_window import MainWindow
    from logsentinel.gui.reports_view import ReportsView

    PYSIDE_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without PySide6
    PYSIDE_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = PROJECT_ROOT / "samples"


def _finding(
    rule_id="LS-RULE-001",
    severity="high",
    src_ip="192.0.2.7",
    first_seen=0,
    last_seen=1,
    *,
    evidence=(),
    summary=None,
):
    return Finding(
        rule_id=rule_id,
        severity=severity,
        src_ip=src_ip,
        first_seen=first_seen,
        last_seen=last_seen,
        evidence=tuple(evidence),
        summary={} if summary is None else summary,
    )


def _result(
    findings=(),
    statistics=None,
    errors=(),
    errors_total=None,
    *,
    generated_at="2026-03-10T12:00:00Z",
    exit_code=None,
    elapsed_seconds=1.25,
):
    return AnalysisResult(
        findings=tuple(findings),
        statistics=statistics or RunStatistics(),
        errors=tuple(errors),
        errors_total=(
            len(errors) if errors_total is None else errors_total),
        config=load_config(None, None),
        generated_at=generated_at,
        exit_code=(1 if findings else 0) if exit_code is None else exit_code,
        files=(),
        elapsed_seconds=elapsed_seconds,
    )


class ReportPureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = run_analysis(
            AnalysisRequest.from_paths([SAMPLES], load_config(None, None)))

    def test_json_export_is_valid_and_uses_existing_renderer(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            export_report(self.sample, JSON_FORMAT, str(path))

            content = path.read_text(encoding="utf-8")
            payload = json.loads(content)
            self.assertEqual(content, self.sample.render_json())
            self.assertEqual(payload["report_version"], 1)
            self.assertEqual(payload["generated_at"], self.sample.generated_at)
            self.assertEqual(len(payload["findings"]), 3)
            self.assertEqual(payload["statistics"]["events_parsed"], 43)
            self.assertEqual(payload["statistics"]["findings"], 3)
            self.assertEqual(len(payload["errors"]), 1)
            self.assertIn("config_used", payload)

    def test_html_report_is_standalone_and_contains_run_metadata(self):
        rendered = render_html_report(self.sample)
        self.assertTrue(rendered.startswith("<!DOCTYPE html>"))
        self.assertIn("LogSentinel Security Analysis Report", rendered)
        self.assertIn("LS-RULE-001", rendered)
        self.assertIn("Scan statistics", rendered)
        self.assertIn("Configuration used", rendered)
        self.assertIn("Generated at", rendered)
        self.assertIn("43", rendered)
        self.assertNotIn("<script", rendered)
        self.assertNotIn("http://", rendered)
        self.assertNotIn("https://", rendered)

    def test_html_escapes_and_sanitizes_evidence_errors_and_summary(self):
        result = _result(
            findings=(
                _finding(
                    evidence=(
                        "<img src=x onerror=alert(1)>",
                        "password=hunter2",
                    ),
                    summary={
                        "note": "<script>alert('summary')</script>",
                        "password": "hunter2",
                        "nested": {"password": "hunter2"},
                    },
                ),
            ),
            errors=(
                ErrorEntry(
                    source_file=r"C:\private\auth.log",
                    line_number=3,
                    reason="<script>bad</script> password=hunter2",
                    kind="parse",
                ),
            ),
            errors_total=1,
            statistics=RunStatistics(
                files_scanned=1, lines_read=2, events_parsed=1, malformed=1),
        )
        rendered = render_html_report(result)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;img", rendered)
        self.assertNotIn("<script", rendered)
        self.assertNotIn("<img", rendered)
        self.assertNotIn("hunter2", rendered)
        self.assertIn(_REDACTED_PATH, rendered)
        self.assertIn("&lt;REDACTED&gt;", rendered)

    def test_html_shows_error_overflow(self):
        errors = tuple(
            ErrorEntry(
                source_file=f"/private/{index}.log",
                line_number=index,
                reason=f"reason {index}",
                kind="parse",
            )
            for index in range(1, 151))
        rendered = render_html_report(_result(
            errors=errors, errors_total=150))
        self.assertIn("Showing 100 of 150 recoverable errors", rendered)
        self.assertIn("50 omitted", rendered)

    def test_extension_and_default_path_handling(self):
        self.assertEqual(
            format_generated_at("2026-03-10T12:00:00Z"),
            "2026-03-10 12:00:00 UTC")
        self.assertEqual(
            format_generated_at("2026-03-10T12:00:00+00:00"),
            "2026-03-10 12:00:00 UTC")
        self.assertEqual(
            ensure_export_extension("report", JSON_FORMAT), "report.json")
        self.assertEqual(
            ensure_export_extension("report.txt", HTML_FORMAT),
            "report.txt.html")
        self.assertEqual(
            ensure_export_extension("report.HTML", HTML_FORMAT),
            "report.HTML")
        with self.assertRaises(ValueError):
            ensure_export_extension("report", "pdf")

        fixed = _result(generated_at="2026-03-10T12:00:00Z")
        self.assertEqual(
            default_report_filename(fixed, JSON_FORMAT),
            "logsentinel-report-20260310-120000.json")
        self.assertEqual(
            default_report_filename(fixed, HTML_FORMAT),
            "logsentinel-report-20260310-120000.html")
        with TemporaryDirectory() as directory:
            self.assertEqual(
                Path(suggested_export_path(fixed, JSON_FORMAT, directory)),
                Path(directory) / "logsentinel-report-20260310-120000.json")
        self.assertIn("JSON report", report_filter(JSON_FORMAT))
        self.assertIn("HTML report", report_filter(HTML_FORMAT))

    def test_unsupported_format_and_write_failure_are_reported(self):
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                export_report(self.sample, "pdf", str(Path(directory) / "x"))
        missing = Path("C:/this/path/should/not/exist") / "report.json"
        with self.assertRaises(ReportError):
            export_report(self.sample, JSON_FORMAT, str(missing))


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class ReportsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-report-view-tests"])
        cls.app.setQuitOnLastWindowClosed(False)
        cls.sample = run_analysis(
            AnalysisRequest.from_paths([SAMPLES], load_config(None, None)))

    def setUp(self):
        self.view = ReportsView()
        self.view.show()
        self.app.processEvents()

    def tearDown(self):
        self.view.close()
        self.view.deleteLater()
        self.app.processEvents()

    def test_export_is_disabled_before_analysis(self):
        self.assertFalse(self.view.is_export_enabled)
        self.assertEqual(self.view.stack.currentIndex(), 0)
        self.assertEqual(
            self.view.empty_state.title_text, "No completed analysis")
        self.assertFalse(self.view.request_export(JSON_FORMAT))
        self.assertIn("No completed analysis", self.view.feedback_text)

    def test_result_enables_exports_and_clear_disables_them(self):
        self.view.set_result(self.sample)
        self.assertTrue(self.view.is_export_enabled)
        self.assertEqual(self.view.stack.currentIndex(), 1)
        self.assertEqual(self.view.result, self.sample)
        self.assertIn("latest completed", self.view.feedback_text)

        self.view.clear("Analysis cancelled", "No reports for this run.")
        self.assertFalse(self.view.is_export_enabled)
        self.assertIsNone(self.view.result)
        self.assertEqual(self.view.stack.currentIndex(), 0)
        self.assertEqual(
            self.view.empty_state.title_text, "Analysis cancelled")

    def test_busy_state_disables_both_buttons(self):
        self.view.set_result(self.sample)
        self.view.set_exporting(True)
        self.assertFalse(self.view.is_export_enabled)
        self.assertTrue(self.view.is_exporting)
        self.assertFalse(self.view.request_export(HTML_FORMAT))
        self.assertIn("already in progress", self.view.feedback_text)
        self.view.set_exporting(False)
        self.assertTrue(self.view.is_export_enabled)

    def test_cancelled_save_dialog_does_not_emit(self):
        self.view.set_result(self.sample)
        emitted = []
        self.view.export_requested.connect(
            lambda kind, path: emitted.append((kind, path)))
        with mock.patch(
            "logsentinel.gui.reports_view.QFileDialog.getSaveFileName",
            return_value=("", ""),
        ):
            self.assertFalse(self.view.request_export(JSON_FORMAT))
        self.assertEqual(emitted, [])
        self.assertEqual(self.view.feedback_text, "Export cancelled.")
        self.assertTrue(self.view.is_export_enabled)

    def test_save_dialog_path_gets_expected_extension(self):
        self.view.set_result(self.sample)
        emitted = []
        self.view.export_requested.connect(
            lambda kind, path: emitted.append((kind, path)))
        with TemporaryDirectory() as directory:
            selected = str(Path(directory) / "analyst-report")
            with mock.patch(
                "logsentinel.gui.reports_view.QFileDialog.getSaveFileName",
                return_value=(selected, "JSON report (*.json)"),
            ):
                self.assertTrue(self.view.request_export(JSON_FORMAT))
        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0][0], JSON_FORMAT)
        self.assertTrue(emitted[0][1].endswith(".json"))

    def test_success_and_failure_feedback_are_clear(self):
        self.view.show_success(JSON_FORMAT, r"C:\reports\review.json")
        self.assertIn("JSON report saved", self.view.feedback_text)
        self.view.show_failure("password=hunter2 at C:\\private\\x")
        self.assertIn("Export failed", self.view.feedback_text)
        self.assertIn("<REDACTED>", self.view.feedback_text)
        self.assertNotIn("hunter2", self.view.feedback_text)


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class MainWindowExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-report-window-tests"])
        cls.app.setQuitOnLastWindowClosed(False)
        cls.sample = run_analysis(
            AnalysisRequest.from_paths([SAMPLES], load_config(None, None)))

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def wait_until(self, predicate, timeout=10.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.app.processEvents()
            if predicate():
                return True
            time.sleep(0.01)
        self.app.processEvents()
        return predicate()

    def export_with_dialog(self, selected, kind):
        with mock.patch(
            "logsentinel.gui.reports_view.QFileDialog.getSaveFileName",
            return_value=(selected, ""),
        ):
            return self.window.reports_view.request_export(kind)

    def test_successful_json_export_from_latest_result(self):
        self.window._on_analysis_completed(self.sample)
        with TemporaryDirectory() as directory:
            selected = str(Path(directory) / "latest-report")
            self.assertTrue(self.export_with_dialog(selected, JSON_FORMAT))
            self.assertTrue(self.wait_until(
                lambda: self.window._export_thread is None))
            target = Path(directory) / "latest-report.json"
            self.assertTrue(target.is_file())
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                self.sample.render_json())
            self.assertIn("JSON report saved", self.window.reports_view.feedback_text)
            self.assertTrue(self.window.reports_view.is_export_enabled)

    def test_failed_export_reports_safe_feedback(self):
        self.window._on_analysis_completed(self.sample)
        selected = "C:/this/path/should/not/exist/report.json"
        self.assertTrue(self.export_with_dialog(selected, JSON_FORMAT))
        self.assertTrue(self.wait_until(
            lambda: self.window._export_thread is None))
        self.assertIn("Export failed", self.window.reports_view.feedback_text)
        self.assertIn(
            "could not be saved", self.window.reports_view.feedback_text)
        self.assertNotIn("hunter2", self.window.reports_view.feedback_text)
        self.assertTrue(self.window.reports_view.is_export_enabled)

    def test_latest_result_replaces_previous_export_state(self):
        first = self.sample
        second = _result(
            findings=(first.findings[0],),
            statistics=first.statistics,
            generated_at="2026-03-10T13:00:00Z",
        )
        self.window._on_analysis_completed(first)
        self.window._on_analysis_completed(second)
        self.assertIs(self.window.reports_view.result, second)
        with TemporaryDirectory() as directory:
            selected = str(Path(directory) / "second-report.html")
            self.assertTrue(self.export_with_dialog(selected, HTML_FORMAT))
            self.assertTrue(self.wait_until(
                lambda: self.window._export_thread is None))
            rendered = Path(selected).read_text(encoding="utf-8")
            self.assertIn("LS-RULE-001", rendered)
            self.assertIn("1 high · 0 medium · 0 low", rendered)

    def test_cancelled_or_failed_analysis_clears_export_state(self):
        self.window._on_analysis_completed(self.sample)
        self.assertTrue(self.window.reports_view.is_export_enabled)
        self.window._on_analysis_cancelled()
        self.assertFalse(self.window.reports_view.is_export_enabled)
        self.assertIsNone(self.window.last_result)
        self.assertEqual(
            self.window.reports_view.empty_state.title_text,
            "Analysis cancelled")

        self.window._on_analysis_completed(self.sample)
        self.window._on_analysis_failed("password=hunter2")
        self.assertFalse(self.window.reports_view.is_export_enabled)
        self.assertIsNone(self.window.last_result)
        self.assertEqual(
            self.window.reports_view.empty_state.title_text,
            "Analysis failed")
