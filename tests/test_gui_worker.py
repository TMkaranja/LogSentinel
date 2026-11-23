"""Tests for the GUI background analysis worker and its window integration.

Coverage:
- successful worker run and structured result delivery;
- sanitized failure reporting;
- progress signal delivery without raw log content;
- cooperative cancellation before and during a run;
- prevention of concurrent runs from the main window;
- deferred window close while the worker cancels and cleans up.
"""

import os
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtCore import QEventLoop, QObject, QThread, QTimer, Slot
    from PySide6.QtGui import QCloseEvent
    from PySide6.QtWidgets import QApplication

    from logsentinel.config import load_config
    from logsentinel.gui.app import create_application
    from logsentinel.gui.backend import (
        AnalysisCancelled,
        AnalysisRequest,
        ProgressEvent,
    )
    from logsentinel.gui.main_window import MainWindow
    from logsentinel.gui.worker import AnalysisWorker

    PYSIDE_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without PySide6
    PYSIDE_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = PROJECT_ROOT / "samples"


class WorkerCapture(QObject):
    """Main-thread receiver that records worker signals."""

    def __init__(self):
        super().__init__()
        self.started_count = 0
        self.progress = []
        self.results = []
        self.cancelled_count = 0
        self.failures = []
        self.finished_count = 0

    @Slot()
    def on_started(self):
        self.started_count += 1

    @Slot(object)
    def on_progress(self, event):
        self.progress.append(event)

    @Slot(object)
    def on_completed(self, result):
        self.results.append(result)

    @Slot()
    def on_cancelled(self):
        self.cancelled_count += 1

    @Slot(str)
    def on_failed(self, message):
        self.failures.append(message)

    @Slot()
    def on_finished(self):
        self.finished_count += 1


class WorkerTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-worker-tests"])
        cls.app.setQuitOnLastWindowClosed(False)

    def request(self, path=None):
        return AnalysisRequest.from_paths(
            [path or SAMPLES], load_config(None, None))

    def run_worker(self, worker, timeout_ms=15000):
        capture = WorkerCapture()
        thread = QThread()
        worker.moveToThread(thread)
        worker.started.connect(capture.on_started)
        worker.progress.connect(capture.on_progress)
        worker.completed.connect(capture.on_completed)
        worker.cancelled.connect(capture.on_cancelled)
        worker.failed.connect(capture.on_failed)
        worker.finished.connect(capture.on_finished)
        worker.finished.connect(thread.quit)
        thread.started.connect(worker.run)

        loop = QEventLoop()
        thread.finished.connect(loop.quit)
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        thread.start()
        timer.start(timeout_ms)
        loop.exec()
        timer.stop()

        if thread.isRunning():
            worker.cancel()
            thread.quit()
            thread.wait(3000)
        self.app.processEvents()
        self.assertFalse(thread.isRunning(), "worker thread did not finish")
        return capture, thread

    def wait_until(self, predicate, timeout=5.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.app.processEvents()
            if predicate():
                return True
            time.sleep(0.01)
        return predicate()


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class GuiWorkerTestCase(WorkerTestBase):
    def test_worker_success_delivers_structured_result(self):
        worker = AnalysisWorker(self.request())
        capture, _thread = self.run_worker(worker)

        self.assertEqual(capture.started_count, 1)
        self.assertEqual(capture.finished_count, 1)
        self.assertEqual(len(capture.results), 1)
        self.assertEqual(capture.failures, [])
        self.assertEqual(capture.cancelled_count, 0)

        result = capture.results[0]
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(len(result.findings), 3)
        self.assertEqual(result.statistics.files_scanned, 3)
        self.assertGreater(len(capture.progress), 0)
        self.assertEqual(capture.progress[-1].phase, "complete")

    def test_progress_signals_are_ordered_and_content_free(self):
        worker = AnalysisWorker(self.request())
        capture, _thread = self.run_worker(worker)

        phases = [event.phase for event in capture.progress]
        self.assertEqual(phases[0], "discovery")
        self.assertIn("reading", phases)
        self.assertIn("deduplicating", phases)
        self.assertIn("detecting", phases)
        self.assertIn("complete", phases)

        reading = [event for event in capture.progress
                   if event.phase == "reading"]
        done_values = [event.files_done for event in reading]
        self.assertEqual(done_values, sorted(done_values))
        self.assertEqual(done_values[-1], 3)

        for event in capture.progress:
            text = event.message.lower()
            self.assertNotIn("failed password", text)
            self.assertNotIn("192.0.2.7", text)
            self.assertNotIn("hunter2", text)

    def test_worker_failure_is_sanitized(self):
        def boom(request, *, progress=None, cancel_event=None):
            raise RuntimeError(
                "password=hunter2 appeared in a Failed password line")

        with mock.patch(
            "logsentinel.gui.worker.run_analysis", new=boom
        ):
            worker = AnalysisWorker(self.request())
            capture, _thread = self.run_worker(worker)

        self.assertEqual(len(capture.failures), 1)
        self.assertEqual(capture.results, [])
        self.assertEqual(capture.cancelled_count, 0)
        self.assertEqual(capture.finished_count, 1)
        message = capture.failures[0]
        self.assertIn("RuntimeError", message)
        self.assertIn("<REDACTED>", message)
        self.assertNotIn("hunter2", message)

    def test_worker_failure_redacts_progress_messages(self):
        def leaky(request, *, progress=None, cancel_event=None):
            progress(ProgressEvent(
                phase="reading", files_done=0, files_total=1,
                events_seen=0, message="password=hunter2"))
            raise AnalysisCancelled("analysis cancelled by user")

        with mock.patch(
            "logsentinel.gui.worker.run_analysis", new=leaky
        ):
            worker = AnalysisWorker(self.request())
            capture, _thread = self.run_worker(worker)

        self.assertEqual(capture.cancelled_count, 1)
        self.assertTrue(capture.progress)
        self.assertIn("<REDACTED>", capture.progress[0].message)
        self.assertNotIn("hunter2", capture.progress[0].message)

    def test_cancellation_before_worker_starts(self):
        worker = AnalysisWorker(self.request())
        worker.cancel()
        capture, _thread = self.run_worker(worker)

        self.assertEqual(capture.cancelled_count, 1)
        self.assertEqual(capture.finished_count, 1)
        self.assertEqual(capture.results, [])
        self.assertEqual(capture.failures, [])

    def test_cancellation_during_run(self):
        def slow_run(request, *, progress=None, cancel_event=None):
            progress(ProgressEvent(
                phase="reading", files_done=0, files_total=1,
                events_seen=0, message="Reading file 1 of 1"))
            while not cancel_event.is_set():
                time.sleep(0.005)
            raise AnalysisCancelled("analysis cancelled by user")

        with mock.patch(
            "logsentinel.gui.worker.run_analysis", new=slow_run
        ):
            worker = AnalysisWorker(self.request())
            QTimer.singleShot(100, worker.cancel)
            capture, _thread = self.run_worker(worker)

        self.assertEqual(capture.cancelled_count, 1)
        self.assertEqual(capture.results, [])
        self.assertEqual(capture.failures, [])
        self.assertTrue(capture.progress)


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class MainWindowWorkerIntegrationTestCase(WorkerTestBase):
    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.cancel_analysis()
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def add_input(self):
        self.window.input_panel.add_paths([SAMPLES / "auth.log"])
        self.app.processEvents()

    def test_analyze_controls_initial_state(self):
        self.assertFalse(self.window.is_analysis_running)
        self.assertFalse(self.window.analyze_button.isEnabled())
        self.assertFalse(self.window.cancel_button.isVisible())

        self.add_input()
        self.assertTrue(self.window.analyze_button.isEnabled())
        self.assertFalse(self.window.cancel_button.isVisible())

    def test_analyze_button_runs_worker_and_completes(self):
        self.add_input()
        self.assertTrue(self.window.start_analysis())
        self.assertTrue(self.window.cancel_button.isVisible())
        self.assertFalse(self.window.analyze_button.isEnabled())

        self.assertTrue(self.wait_until(
            lambda: not self.window.is_analysis_running))
        self.app.processEvents()

        self.assertIsNotNone(self.window.last_result)
        self.assertGreaterEqual(len(self.window.last_result.findings), 1)
        self.assertEqual(self.window._run_status.text(), "Analysis complete")
        self.assertEqual(self.window.log_explorer_view.stack.currentIndex(), 1)
        self.assertNotEqual(
            self.window.log_explorer_view.statistics.values["events_parsed"],
            "—")
        self.assertTrue(self.window.analyze_button.isEnabled())
        self.assertFalse(self.window.cancel_button.isVisible())

    def test_concurrent_start_is_rejected(self):
        self.add_input()
        started = threading.Event()

        def slow_run(request, *, progress=None, cancel_event=None):
            started.set()
            while not cancel_event.is_set():
                time.sleep(0.005)
            raise AnalysisCancelled("analysis cancelled by user")

        with mock.patch("logsentinel.gui.worker.run_analysis", new=slow_run):
            self.assertTrue(self.window.start_analysis())
            self.assertTrue(started.wait(3.0))
            self.assertFalse(self.window.start_analysis())
            self.assertTrue(self.window.is_analysis_running)
            self.assertTrue(self.window.cancel_analysis())
            self.assertTrue(self.wait_until(
                lambda: not self.window.is_analysis_running))

        self.assertFalse(self.window.is_analysis_running)
        self.assertTrue(self.window.analyze_button.isEnabled())
        self.assertEqual(self.window._run_status.text(), "Analysis cancelled")
        self.assertEqual(self.window.log_explorer_view.stack.currentIndex(), 0)
        self.assertEqual(self.window.log_explorer_view.empty_state.title_text,
                         "Analysis cancelled")

    def test_failed_run_is_reported_and_controls_recover(self):
        self.add_input()

        def boom(request, *, progress=None, cancel_event=None):
            raise RuntimeError("password=hunter2 in a raw log line")

        with mock.patch("logsentinel.gui.worker.run_analysis", new=boom):
            self.assertTrue(self.window.start_analysis())
            self.assertTrue(self.wait_until(
                lambda: not self.window.is_analysis_running))
            self.app.processEvents()

        self.assertEqual(self.window._run_status.text(), "Analysis failed")
        self.assertIn("<REDACTED>", self.window._run_detail.text())
        self.assertNotIn("hunter2", self.window._run_detail.text())
        self.assertTrue(self.window.analyze_button.isEnabled())
        self.assertFalse(self.window.cancel_button.isVisible())
        self.assertEqual(self.window.log_explorer_view.stack.currentIndex(), 0)
        self.assertEqual(self.window.log_explorer_view.empty_state.title_text,
                         "Analysis failed")

    def test_window_close_defers_until_worker_stops(self):
        self.add_input()
        started = threading.Event()

        def slow_run(request, *, progress=None, cancel_event=None):
            started.set()
            while not cancel_event.is_set():
                time.sleep(0.005)
            raise AnalysisCancelled("analysis cancelled by user")

        with mock.patch("logsentinel.gui.worker.run_analysis", new=slow_run):
            self.assertTrue(self.window.start_analysis())
            self.assertTrue(started.wait(3.0))

            event = QCloseEvent()
            self.window.closeEvent(event)
            self.assertFalse(event.isAccepted())

            self.assertTrue(self.wait_until(
                lambda: not self.window.is_analysis_running))
            self.app.processEvents()

        self.assertFalse(self.window.is_analysis_running)
        self.assertFalse(self.window.isVisible())


if __name__ == "__main__":  # pragma: no cover - unittest discovery entry
    unittest.main()
