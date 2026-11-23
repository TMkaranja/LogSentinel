"""Background analysis worker for the LogSentinel desktop GUI.

The worker owns a ``QThread``-compatible ``run()`` slot that delegates to the
existing headless adapter ``gui.backend.run_analysis``. It adds only:

- Qt signals for progress, completion, cancellation, failure, and finish;
- a thread-safe cancellation event;
- sanitization of every message before it leaves the worker thread.

Parsing, detection, deduplication, validation, redaction, and SQLite staging
remain in the existing backend modules. The worker never reads log content and
never builds progress messages from it: progress messages originate in the
backend and are count-based, and every message is passed through the shared
report sanitizer as defense in depth.

Typical use::

    worker = AnalysisWorker(request)
    thread = QThread(parent)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.progress.connect(window.on_progress)
    worker.completed.connect(window.on_completed)
    worker.finished.connect(thread.quit)
    thread.start()
"""

from __future__ import annotations

import threading

from PySide6.QtCore import QObject, Signal, Slot

from ..exceptions import LogSentinelError
from ..report import _sanitize
from .backend import (
    AnalysisCancelled,
    AnalysisRequest,
    AnalysisResult,
    ProgressEvent,
    run_analysis,
)

__all__ = ["AnalysisWorker"]


class AnalysisWorker(QObject):
    """Run one analysis request on a background Qt thread."""

    started = Signal()
    progress = Signal(object)       # ProgressEvent
    completed = Signal(object)      # AnalysisResult
    cancelled = Signal()
    failed = Signal(str)            # sanitized diagnostic
    finished = Signal()             # always emitted, including failures

    def __init__(
        self, request: AnalysisRequest, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        if not isinstance(request, AnalysisRequest):
            raise TypeError("request must be an AnalysisRequest instance")
        self._request = request
        self._cancel_event = threading.Event()
        self._started = False

    @property
    def request(self) -> AnalysisRequest:
        return self._request

    @property
    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    @Slot()
    def cancel(self) -> None:
        """Request cooperative cancellation; safe from the GUI thread."""
        self._cancel_event.set()

    @Slot()
    def run(self) -> None:
        """Execute the backend and translate its outcome into Qt signals."""
        if self._started:
            return
        self._started = True
        self.started.emit()
        try:
            result = run_analysis(
                self._request,
                progress=self._emit_progress,
                cancel_event=self._cancel_event,
            )
            self.completed.emit(result)
        except AnalysisCancelled:
            self.cancelled.emit()
        except LogSentinelError as exc:
            self.failed.emit(self._sanitised_message(exc))
        except Exception as exc:  # outermost worker boundary
            self.failed.emit(
                f"{exc.__class__.__name__}: "
                f"{self._sanitised_message(exc)}")
        finally:
            self.finished.emit()

    def _emit_progress(self, event: ProgressEvent) -> None:
        """Republish a backend progress event with sanitized text."""
        safe_event = ProgressEvent(
            phase=_sanitize(event.phase),
            files_done=event.files_done,
            files_total=event.files_total,
            events_seen=event.events_seen,
            message=_sanitize(event.message),
        )
        self.progress.emit(safe_event)

    @staticmethod
    def _sanitised_message(exc: BaseException) -> str:
        """Best-effort sanitization; never emit a traceback or raw secret."""
        text = _sanitize(str(exc))
        return text or exc.__class__.__name__
