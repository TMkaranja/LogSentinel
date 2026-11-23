"""Tests for the GUI results dashboard, table models, and detail views.

These tests are presentation-only: they use a real backend result for the
sample logs plus small synthetic findings/errors for sorting, sanitization,
selection, overflow, and empty-state behavior.
"""

import os
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import Qt

    from logsentinel.config import load_config
    from logsentinel.events import ErrorEntry, Finding
    from logsentinel.gui.app import create_application
    from logsentinel.gui.backend import AnalysisRequest, AnalysisResult, run_analysis
    from logsentinel.gui.main_window import MainWindow
    from logsentinel.gui.models import (
        ErrorTableModel,
        FindingTableModel,
        SORT_ROLE,
        format_epoch_short,
        format_epoch_utc,
        format_finding_summary,
    )
    from logsentinel.gui.views import (
        DetectionDetail,
        DetectionsView,
        LogExplorerView,
        OverviewDashboard,
    )
    from logsentinel.report import (
        MAX_REPORTED_ERRORS,
        RunStatistics,
        _REDACTED_PATH,
        _sanitize,
    )

    PYSIDE_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without PySide6
    PYSIDE_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = PROJECT_ROOT / "samples"


def _finding(
    rule_id,
    severity,
    src_ip,
    first_seen=1_773_000_000,
    last_seen=1_773_000_060,
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
):
    return AnalysisResult(
        findings=tuple(findings),
        statistics=statistics or RunStatistics(),
        errors=tuple(errors),
        errors_total=(
            len(errors) if errors_total is None else errors_total),
        config=load_config(None, None),
        generated_at="2026-03-10T12:00:00Z",
        exit_code=1 if findings else 0,
        files=(),
        elapsed_seconds=0.1,
    )


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class ModelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-dashboard-model-tests"])
        cls.app.setQuitOnLastWindowClosed(False)


class TestFormatting(ModelTestCase):
    def test_epoch_formatters(self):
        self.assertEqual(format_epoch_utc(0), "1970-01-01 00:00:00 UTC")
        self.assertEqual(format_epoch_short(0), "1970-01-01 00:00:00")

    def test_summary_is_deterministic_and_sanitized(self):
        summary = format_finding_summary({"b": 2, "a": 1})
        self.assertEqual(summary, "a=1, b=2")
        self.assertEqual(format_finding_summary({}), "—")

        secret = format_finding_summary({"password": "hunter2"})
        self.assertIn("<REDACTED>", secret)
        self.assertNotIn("hunter2", secret)


class TestFindingTableModel(ModelTestCase):
    def setUp(self):
        self.findings = (
            _finding(
                "LS-RULE-003", "low", "203.0.113.50",
                first_seen=1_773_000_100,
                last_seen=1_773_000_100,
                evidence=("one",),
                summary={"paths": 9}),
            _finding(
                "LS-RULE-001", "high", "192.0.2.7",
                first_seen=1_773_000_000,
                last_seen=1_773_000_060,
                evidence=("one", "two"),
                summary={"failed_count": 8}),
            _finding(
                "LS-RULE-002", "medium", "198.51.100.23",
                first_seen=1_773_000_020,
                last_seen=1_773_000_030,
                evidence=("one", "two", "three"),
                summary={"ports": 12}),
        )
        self.model = FindingTableModel(self.findings)

    def test_shape_headers_and_display(self):
        self.assertEqual(self.model.rowCount(), 3)
        self.assertEqual(self.model.columnCount(), 7)
        self.assertEqual(
            self.model.headerData(0, Qt.Orientation.Horizontal), "Severity")
        self.assertEqual(
            self.model.headerData(3, Qt.Orientation.Horizontal),
            "First seen (UTC)")
        self.assertEqual(
            self.model.data(self.model.index(1, 0)), "High")
        self.assertEqual(
            self.model.data(self.model.index(1, 1)), "LS-RULE-001")
        self.assertEqual(
            self.model.data(self.model.index(1, 2)), "192.0.2.7")
        self.assertEqual(
            self.model.data(self.model.index(1, 3)),
            format_epoch_short(1_773_000_000))
        self.assertEqual(
            self.model.data(self.model.index(1, 6)), "2 lines")

    def test_sort_roles_are_semantic(self):
        self.assertEqual(self.model.data(self.model.index(1, 0), SORT_ROLE), 0)
        self.assertEqual(self.model.data(self.model.index(2, 0), SORT_ROLE), 1)
        self.assertEqual(self.model.data(self.model.index(0, 0), SORT_ROLE), 2)
        self.assertEqual(
            self.model.data(self.model.index(1, 3), SORT_ROLE), 1_773_000_000)
        self.assertEqual(self.model.data(self.model.index(1, 6), SORT_ROLE), 2)

    def test_tooltip_and_summary_sanitization(self):
        index = self.model.index(1, 3)
        self.assertEqual(
            self.model.data(index, Qt.ItemDataRole.ToolTipRole),
            format_epoch_utc(1_773_000_000))
        self.assertEqual(
            self.model.data(self.model.index(1, 6), Qt.ItemDataRole.ToolTipRole),
            "Select the row to view sanitized evidence.")

        secret_finding = _finding(
            "LS-RULE-004", "high", "192.0.2.9",
            summary={"password": "hunter2"})
        self.model.set_findings((secret_finding,))
        self.assertIn(
            "<REDACTED>", self.model.data(self.model.index(0, 5)))
        self.assertNotIn(
            "hunter2", self.model.data(self.model.index(0, 5)))

    def test_set_findings_and_bounds(self):
        self.model.set_findings(())
        self.assertEqual(self.model.rowCount(), 0)
        self.assertIsNone(self.model.finding_at(0))

        self.model.set_findings(self.findings[:1])
        self.assertEqual(self.model.rowCount(), 1)
        self.assertEqual(self.model.finding_at(0).rule_id, "LS-RULE-003")
        self.assertIsNone(self.model.finding_at(-1))
        self.assertIsNone(self.model.finding_at(1))


class TestErrorTableModel(ModelTestCase):
    def setUp(self):
        self.errors = (
            ErrorEntry(
                source_file=r"C:\sensitive\auth.log",
                line_number=6,
                reason="bad token password=hunter2",
                kind="parse"),
            ErrorEntry(
                source_file="/srv/private/access.log",
                line_number=None,
                reason="input problem",
                kind="input"),
        )
        self.model = ErrorTableModel(self.errors)

    def test_display_and_source_redaction(self):
        self.assertEqual(self.model.rowCount(), 2)
        self.assertEqual(self.model.columnCount(), 4)
        self.assertEqual(
            self.model.data(self.model.index(0, 0)), "parse")
        self.assertEqual(self.model.data(self.model.index(0, 1)), "6")
        self.assertEqual(
            self.model.data(self.model.index(1, 1)), "—")
        self.assertIn(
            "<REDACTED>", self.model.data(self.model.index(0, 2)))
        self.assertNotIn(
            "hunter2", self.model.data(self.model.index(0, 2)))
        self.assertEqual(
            self.model.data(self.model.index(0, 3)), _REDACTED_PATH)
        self.assertEqual(
            self.model.data(self.model.index(1, 3)), _REDACTED_PATH)

    def test_sort_roles_and_bounds(self):
        self.assertEqual(self.model.data(self.model.index(0, 3), SORT_ROLE),
                         _REDACTED_PATH)
        self.assertEqual(self.model.data(self.model.index(0, 1), SORT_ROLE), 6)
        self.assertEqual(self.model.data(self.model.index(1, 1), SORT_ROLE), -1)
        self.assertIsNone(self.model.error_at(9))
        self.model.set_errors(self.errors[:1])
        self.assertEqual(self.model.rowCount(), 1)
        self.assertEqual(self.model.error_at(0).kind, "parse")


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class ViewTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-dashboard-view-tests"])
        cls.app.setQuitOnLastWindowClosed(False)
        cls.sample_result = run_analysis(
            AnalysisRequest.from_paths([SAMPLES], load_config(None, None)))

    def setUp(self):
        self.widgets = []

    def tearDown(self):
        for widget in self.widgets:
            widget.close()
            widget.deleteLater()
        self.app.processEvents()

    def track(self, widget):
        self.widgets.append(widget)
        widget.show()
        self.app.processEvents()
        return widget


class TestLogExplorerView(ViewTestCase):
    def test_empty_state_before_a_run(self):
        view = self.track(LogExplorerView())
        self.assertEqual(view.stack.currentIndex(), 0)
        self.assertEqual(view.empty_state.title_text,
                         "No parsed event summary yet")

    def test_result_shows_streamed_statistics_without_raw_paths(self):
        view = self.track(LogExplorerView())
        view.set_result(self.sample_result)
        self.assertEqual(view.stack.currentIndex(), 1)
        self.assertEqual(view.statistics.values["events_parsed"], "43")
        self.assertEqual(view.statistics.values["files_scanned"], "3")
        self.assertIn("sanitized evidence", view.context_text)
        self.assertNotIn(str(SAMPLES), view.context_text)

    def test_clear_removes_stale_statistics(self):
        view = self.track(LogExplorerView())
        view.set_result(self.sample_result)
        view.clear("Analysis failed", "No event statistics for a failed run.")
        self.assertEqual(view.stack.currentIndex(), 0)
        self.assertEqual(view.empty_state.title_text, "Analysis failed")
        self.assertEqual(view.statistics.values["events_parsed"], "—")


class TestDetectionsView(ViewTestCase):
    def test_empty_and_populated_states(self):
        view = self.track(DetectionsView())
        self.assertEqual(view.model.rowCount(), 0)
        self.assertEqual(view.stack.currentIndex(), 0)
        self.assertEqual(view.empty_state.title_text, "No analysis results yet")

        view.set_result(self.sample_result)
        self.app.processEvents()
        self.assertEqual(view.model.rowCount(), 3)
        self.assertEqual(view.count_text, "3 detections")
        self.assertEqual(view.stack.currentIndex(), 1)
        self.assertIsNotNone(view.detail.current_finding)
        self.assertEqual(view.detail.current_finding.rule_id, "LS-RULE-001")
        self.assertEqual(len(view.detail.evidence_texts), 9)

    def test_narrow_layout_stacks_detail_below_table(self):
        view = self.track(DetectionsView())
        view.resize(1200, 700)
        self.app.processEvents()
        self.assertEqual(view.splitter.orientation(), Qt.Orientation.Horizontal)
        self.assertGreaterEqual(view.detail.minimumWidth(), 300)
        self.assertFalse(view.table.isColumnHidden(6))

        view.resize(820, 560)
        self.app.processEvents()
        self.assertEqual(view.splitter.orientation(), Qt.Orientation.Vertical)
        self.assertEqual(view.detail.minimumWidth(), 0)
        self.assertTrue(view.table.isColumnHidden(6))

        view.resize(1200, 700)
        self.app.processEvents()
        self.assertEqual(view.splitter.orientation(), Qt.Orientation.Horizontal)
        self.assertGreaterEqual(view.detail.minimumWidth(), 300)
        self.assertFalse(view.table.isColumnHidden(6))

    def test_sorting_and_selection_map_to_details(self):
        findings = (
            _finding("LS-RULE-003", "low", "203.0.113.50"),
            _finding("LS-RULE-001", "high", "192.0.2.7"),
            _finding("LS-RULE-002", "medium", "198.51.100.23"),
        )
        view = self.track(DetectionsView())
        view.set_result(_result(findings=findings))
        self.app.processEvents()

        view.proxy.sort(1, Qt.SortOrder.DescendingOrder)
        self.app.processEvents()
        self.assertEqual(view.proxy.index(0, 1).data(), "LS-RULE-003")
        view.table.selectRow(0)
        self.app.processEvents()
        self.assertEqual(view.detail.current_finding.rule_id, "LS-RULE-003")
        self.assertEqual(
            view.detail.current_finding.src_ip, "203.0.113.50")

        view.proxy.sort(0, Qt.SortOrder.DescendingOrder)
        self.app.processEvents()
        view.table.selectRow(0)
        self.app.processEvents()
        self.assertEqual(view.detail.current_finding.severity, "low")

    def test_clear_removes_stale_detail_and_rows(self):
        view = self.track(DetectionsView())
        view.set_result(self.sample_result)
        self.app.processEvents()
        view.clear("Analysis cancelled", "No detections for this run.")
        self.assertEqual(view.model.rowCount(), 0)
        self.assertEqual(view.count_text, "0 detections")
        self.assertIsNone(view.detail.current_finding)
        self.assertEqual(view.detail.evidence_texts, ())
        self.assertEqual(view.stack.currentIndex(), 0)
        self.assertEqual(view.empty_state.title_text, "Analysis cancelled")

    def test_no_detections_result_shows_dedicated_empty_state(self):
        view = self.track(DetectionsView())
        clean = _result(
            findings=(),
            statistics=RunStatistics(files_scanned=1, lines_read=2),
            errors=(),
            errors_total=0)
        view.set_result(clean)
        self.assertEqual(view.stack.currentIndex(), 0)
        self.assertEqual(view.empty_state.title_text, "No detections in this run")
        self.assertEqual(view.model.rowCount(), 0)

    def test_detail_evidence_and_summary_are_sanitized(self):
        detail = self.track(DetectionDetail())
        finding = _finding(
            "LS-RULE-001", "high", "192.0.2.7",
            evidence=(
                "Authorization: Bearer supersecret",
                "password=hunter2"),
            summary={"password": "hunter2"})
        detail.show_finding(finding)
        self.assertEqual(detail.current_finding, finding)
        self.assertTrue(any("<REDACTED>" in line
                            for line in detail.evidence_texts))
        self.assertFalse(any("hunter2" in line
                             for line in detail.evidence_texts))
        self.assertNotIn("hunter2", detail.summary_text)
        self.assertIn("<REDACTED>", detail.summary_text)
        self.assertEqual(detail.evidence_count_text, "2 lines")

        detail.clear()
        self.assertIsNone(detail.current_finding)
        self.assertEqual(detail.evidence_texts, ())
        self.assertEqual(detail.summary_text, "")


class TestOverviewDashboard(ViewTestCase):
    def test_empty_then_populated(self):
        dashboard = self.track(OverviewDashboard())
        self.assertFalse(dashboard.has_result)
        self.assertEqual(dashboard.stack.currentIndex(), 0)
        self.assertEqual(
            dashboard.empty_state.title_text, "No analysis results yet")

        dashboard.set_result(self.sample_result)
        self.assertTrue(dashboard.has_result)
        self.assertEqual(dashboard.stack.currentIndex(), 1)
        self.assertEqual(dashboard.events_card.value_text, "43")
        self.assertEqual(dashboard.detections_card.value_text, "3")
        self.assertEqual(dashboard.high_card.value_text, "1")
        self.assertEqual(dashboard.errors_card.value_text, "1")
        self.assertEqual(
            dashboard.severity.counts,
            {"high": 1, "medium": 2, "low": 0})
        self.assertEqual(dashboard.statistics.values["files_scanned"], "3")
        self.assertEqual(dashboard.statistics.values["lines_read"], "44")
        self.assertEqual(dashboard.statistics.values["malformed"], "1")
        self.assertEqual(dashboard.errors_view.model.rowCount(), 1)
        self.assertIn("1 error", dashboard.errors_view.overflow_text)

    def test_clear_resets_all_panels(self):
        dashboard = self.track(OverviewDashboard())
        dashboard.set_result(self.sample_result)
        dashboard.clear("Analysis failed", "No results for this run.")
        self.assertFalse(dashboard.has_result)
        self.assertEqual(dashboard.events_card.value_text, "—")
        self.assertEqual(dashboard.detections_card.value_text, "—")
        self.assertEqual(dashboard.high_card.value_text, "—")
        self.assertEqual(dashboard.errors_card.value_text, "—")
        self.assertEqual(
            dashboard.severity.counts,
            {"high": 0, "medium": 0, "low": 0})
        self.assertTrue(
            all(value == "—" for value in dashboard.statistics.values.values()))
        self.assertEqual(dashboard.errors_view.model.rowCount(), 0)
        self.assertEqual(dashboard.errors_view.overflow_text,
                         "No errors recorded")
        self.assertEqual(dashboard.empty_state.title_text, "Analysis failed")

    def test_zero_findings_and_zero_errors_are_explicit(self):
        dashboard = self.track(OverviewDashboard())
        clean = _result(
            findings=(),
            statistics=RunStatistics(
                files_scanned=1, lines_read=5, events_parsed=4,
                malformed=1),
            errors=(),
            errors_total=0)
        dashboard.set_result(clean)
        self.assertEqual(dashboard.events_card.value_text, "4")
        self.assertEqual(dashboard.detections_card.value_text, "0")
        self.assertEqual(dashboard.high_card.value_text, "0")
        self.assertEqual(dashboard.errors_card.value_text, "0")
        self.assertEqual(
            dashboard.severity.counts,
            {"high": 0, "medium": 0, "low": 0})
        self.assertEqual(dashboard.errors_view.model.rowCount(), 0)
        self.assertEqual(dashboard.errors_view.overflow_text,
                         "No errors recorded")

    def test_error_display_is_capped_and_reports_exact_total(self):
        dashboard = self.track(OverviewDashboard())
        errors = tuple(
            ErrorEntry(
                source_file=f"/private/source-{index}.log",
                line_number=index,
                reason=f"reason password=secret-{index}",
                kind="parse")
            for index in range(1, 151))
        dashboard.set_result(_result(
            errors=errors, errors_total=150))
        self.assertEqual(
            dashboard.errors_view.model.rowCount(), MAX_REPORTED_ERRORS)
        self.assertEqual(
            dashboard.errors_view.overflow_text, "Showing 100 of 150 errors")
        self.assertEqual(
            dashboard.errors_view.model.data(
                dashboard.errors_view.model.index(0, 3)), _REDACTED_PATH)
        self.assertNotIn(
            "secret-1",
            dashboard.errors_view.model.data(
                dashboard.errors_view.model.index(0, 2)))


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class TestDashboardIntegration(ViewTestCase):
    def test_window_populates_dashboard_and_detections(self):
        window = self.track(MainWindow())
        self.assertFalse(window.dashboard.has_result)
        self.assertEqual(window.detections_view.model.rowCount(), 0)

        window._on_analysis_completed(self.sample_result)
        self.app.processEvents()
        self.assertTrue(window.dashboard.has_result)
        self.assertEqual(window.dashboard.detections_card.value_text, "3")
        self.assertEqual(window.detections_view.model.rowCount(), 3)
        self.assertEqual(window.detections_view.count_text, "3 detections")
        self.assertIs(window.last_result, self.sample_result)

    def test_cancelled_and_failed_runs_clear_stale_results(self):
        window = self.track(MainWindow())
        window._on_analysis_completed(self.sample_result)
        window._on_analysis_cancelled()
        self.app.processEvents()
        self.assertIsNone(window.last_result)
        self.assertFalse(window.dashboard.has_result)
        self.assertEqual(window.detections_view.model.rowCount(), 0)
        self.assertEqual(
            window.dashboard.empty_state.title_text, "Analysis cancelled")
        self.assertEqual(
            window.detections_view.empty_state.title_text, "Analysis cancelled")

        window._on_analysis_completed(self.sample_result)
        window._on_analysis_failed("failure at C:\\private\\auth.log")
        self.app.processEvents()
        self.assertIsNone(window.last_result)
        self.assertFalse(window.dashboard.has_result)
        self.assertEqual(window.detections_view.model.rowCount(), 0)
        self.assertEqual(
            window.dashboard.empty_state.title_text, "Analysis failed")
        self.assertIn("failure at", window._run_detail.text())
