"""Headless analysis adapter for the optional LogSentinel GUI.

This module is the single bridge between the desktop interface and the
existing production pipeline. It deliberately mirrors the orchestration in
``cli._run`` while reusing every existing primitive unchanged:

    discovery -> per-file streaming parse with RunStorage transactions ->
    SQL cross-file deduplication -> incremental detectors ->
    statistics and error summary.

No parsing, detection, deduplication, validation, redaction, or reporting
logic is reimplemented here. The adapter only adds the two things a GUI
needs that the CLI does not expose: a structured result object and progress
and cancellation hooks.

Security and compatibility rules preserved by this adapter:

- strict mode aborts on the first recorded error, with the same sanitized
  diagnostic and exception type mapping as the CLI;
- only the first ``MAX_REPORTED_ERRORS_STORAGE`` errors plus the exact total
  are returned, matching the existing storage/report contract;
- report rendering is delegated to ``report.render_json`` and
  ``report.render_console``, preserving credential redaction, evidence
  truncation and source-path redaction;
- ``RunStorage`` remains the only staging mechanism and is always cleaned
  up through its context manager;
- no report files are written during analysis; rendering produces strings
  only, and exports remain the caller's responsibility;
- no network access, shell execution, or dynamic code execution.

Wall-clock usage follows the CLI's AR-010 pattern: :meth:`AnalysisRequest.
from_paths` reads the clock exactly once, and both ``reference_now`` and
``generated_at`` come from that same instant. The parser, detectors, and
report renderers never read the clock.
"""

from __future__ import annotations

import os
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone

from ..config import AppConfig
from ..detectors import (
    HTTP4xxAbuseDetector,
    PortScanDetector,
    SSHBruteForceDetector,
)
from ..events import ErrorEntry, Finding, SecurityEvent
from ..exceptions import (
    ConfigError,
    InputPathError,
    LogSentinelError,
    ParseError,
    ReportError,
)
from ..inputs import LogFile, discover_inputs
from ..parsers import stream_parse_file
from ..report import (
    RunStatistics,
    _REDACTED_PATH,
    _sanitize,
    render_console as _render_console,
    render_json as _render_json,
)
from ..storage import RunStorage

__all__ = [
    "AnalysisCancelled",
    "AnalysisRequest",
    "AnalysisResult",
    "ProgressEvent",
    "run_analysis",
]

#: Strict-mode error kind -> exception type mapping, matching the CLI
#: (FR-150/FR-152). Kept local so the GUI has no dependency on cli.py.
_EXCEPTION_BY_KIND: dict[str, type[Exception]] = {
    "config": ConfigError,
    "input": InputPathError,
    "parse": ParseError,
    "report": ReportError,
}


class AnalysisCancelled(RuntimeError):
    """Raised cooperatively when the caller requests cancellation.

    Cancellation is never treated as an analysis failure: the worker layer
    is expected to distinguish it from ``LogSentinelError`` and unexpected
    exceptions. ``RunStorage`` cleanup still runs through its context
    manager, so no staging database is left behind.
    """


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    """One coarse-grained progress notification emitted by a GUI run.

    Messages are static or count-based and never contain log content or
    parser diagnostics. ``files_done`` and ``files_total`` describe the
    current file stage; ``events_seen`` counts streamed events observed so
    far across the run.
    """

    phase: str
    files_done: int = 0
    files_total: int = 0
    events_seen: int = 0
    message: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.phase, str) or not self.phase:
            raise ValueError("phase must be a non-empty string")
        for name in ("files_done", "files_total", "events_seen"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(
                    f"{name} must be a non-negative integer, got {value!r}")
        if self.files_done > self.files_total:
            raise ValueError("files_done must not exceed files_total")
        if not isinstance(self.message, str):
            raise ValueError("message must be a string")


@dataclass(frozen=True, slots=True)
class AnalysisRequest:
    """Inputs for one GUI analysis run.

    ``paths`` are the user-selected files and/or directories, in the order
    the GUI presents them. Discovery still applies every existing rule
    (directory recursion, extension filtering, exact-string de-duplication,
    size caps, and errors-as-data).

    Use :meth:`from_paths` in the application layer so the run clock is read
    exactly once. Direct construction is supported for deterministic tests
    and for callers that already captured the run instant.
    """

    paths: tuple[str | os.PathLike[str], ...]
    config: AppConfig
    generated_at: str
    reference_now: int

    def __post_init__(self) -> None:
        raw_paths = self.paths
        if isinstance(raw_paths, (str, bytes, os.PathLike)):
            normalized: tuple[object, ...] = (raw_paths,)
        else:
            normalized = tuple(raw_paths)
        object.__setattr__(self, "paths", normalized)
        if not isinstance(self.config, AppConfig):
            raise TypeError("config must be an AppConfig instance")
        if not isinstance(self.generated_at, str) or not self.generated_at:
            raise ValueError("generated_at must be a non-empty string")
        if type(self.reference_now) is not int or self.reference_now < 0:
            raise ValueError("reference_now must be a non-negative integer")

    @classmethod
    def from_paths(
        cls,
        paths: Sequence[str | os.PathLike[str]] | str | os.PathLike[str],
        config: AppConfig,
        *,
        now: datetime | None = None,
    ) -> "AnalysisRequest":
        """Build a request and capture one run instant (AR-010 pattern).

        A supplied naive ``now`` is treated as UTC. The same instant supplies
        both ``reference_now`` (integer epoch seconds) and ``generated_at``
        (ISO-8601 UTC) so report timestamps and year inference cannot drift
        apart within one run.
        """
        if isinstance(paths, (str, bytes, os.PathLike)):
            items: tuple[object, ...] = (paths,)
        else:
            items = tuple(paths)
        if now is None:
            now = datetime.now(timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        return cls(
            paths=items,  # type: ignore[arg-type]
            config=config,
            generated_at=now.isoformat(),
            reference_now=int(now.timestamp()),
        )


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Structured outcome of a completed GUI analysis run.

    The object contains the same data the CLI sends to its renderers:
    findings, run statistics, the first capped error entries plus the exact
    error total, and the effective configuration. ``exit_code`` mirrors the
    CLI's outcome mapping (0 clean, 1 findings, 2 input problems with
    nothing scanned). Strict aborts and unexpected failures raise instead of
    returning a result.

    ``render_json`` and ``render_text`` delegate to the existing report
    layer, so exports are byte-compatible with the CLI and keep all
    redaction and truncation rules.
    """

    findings: tuple[Finding, ...]
    statistics: RunStatistics
    errors: tuple[ErrorEntry, ...]
    errors_total: int
    config: AppConfig
    generated_at: str
    exit_code: int
    files: tuple[LogFile, ...]
    elapsed_seconds: float
    cleanup_errors: tuple[str, ...] = ()

    def render_json(self) -> str:
        """Render the machine-readable report using the existing renderer."""
        return _render_json(
            self.findings,
            self.statistics,
            self.config,
            self.generated_at,
            errors=self.errors,
            errors_total=self.errors_total,
        )

    def render_text(self) -> str:
        """Render the human-readable report using the existing renderer."""
        return _render_console(
            self.findings,
            self.statistics,
            self.config,
            errors=self.errors,
            errors_total=self.errors_total,
        )


def _check_cancel(cancel_event: threading.Event | None) -> None:
    if cancel_event is not None and cancel_event.is_set():
        raise AnalysisCancelled("analysis cancelled by user")


def _emit(
    callback: Callable[[ProgressEvent], None] | None,
    event: ProgressEvent,
) -> None:
    if callback is not None:
        callback(event)


def _strict_abort(entry: ErrorEntry) -> Exception:
    """Build the strict-mode abort exception for an error entry.

    Mirrors ``cli._strict_abort`` exactly: the reason is sanitized before it
    can reach a UI message, the source path is replaced with the neutral
    redaction marker, and the line number and kind are preserved.
    """
    exception_type = _EXCEPTION_BY_KIND.get(entry.kind, InputPathError)
    location = f"in {_REDACTED_PATH}"
    if entry.line_number is not None:
        location += f" at line {entry.line_number}"
    return exception_type(
        f"strict mode abort: {_sanitize(entry.reason)} ({location}, "
        f"kind={entry.kind!r})")


def run_analysis(
    request: AnalysisRequest,
    *,
    progress: Callable[[ProgressEvent], None] | None = None,
    cancel_event: threading.Event | None = None,
) -> AnalysisResult:
    """Run one analysis and return structured results.

    Raises ``AnalysisCancelled`` when cancellation is requested,
    ``LogSentinelError`` subclasses for strict aborts, and unexpected
    exceptions unchanged. The existing report writers are never called.
    """
    if not isinstance(request, AnalysisRequest):
        raise TypeError("request must be an AnalysisRequest instance")
    if progress is not None and not callable(progress):
        raise TypeError("progress must be callable or None")
    if cancel_event is not None and not isinstance(cancel_event, threading.Event):
        raise TypeError("cancel_event must be a threading.Event or None")

    started = time.monotonic()
    config = request.config
    _check_cancel(cancel_event)
    _emit(progress, ProgressEvent(
        phase="discovery", message="Discovering input files"))

    discovery = discover_inputs(
        list(request.paths), max_file_mb=config.max_file_mb)
    _check_cancel(cancel_event)

    with RunStorage() as storage:
        # Discovery errors are staged first, preserving original error
        # ordering exactly as the CLI does.
        for entry in discovery.errors:
            storage.stage_error(entry)
        if config.strict and discovery.errors:
            raise _strict_abort(discovery.errors[0])

        files = discovery.files
        files_total = len(files)
        detectors = (
            SSHBruteForceDetector(
                config.ssh_threshold, config.ssh_window_seconds),
            PortScanDetector(config.portscan_threshold),
            HTTP4xxAbuseDetector(config.http_4xx_threshold),
        )

        events_seen = 0
        for index, log_file in enumerate(files, start=1):
            _check_cancel(cancel_event)
            _emit(progress, ProgressEvent(
                phase="reading",
                files_done=index - 1,
                files_total=files_total,
                events_seen=events_seen,
                message=f"Reading file {index} of {files_total}",
            ))
            _check_cancel(cancel_event)
            events_seen += _process_file(
                storage, log_file, config, request.reference_now,
                cancel_event)
            _emit(progress, ProgressEvent(
                phase="reading",
                files_done=index,
                files_total=files_total,
                events_seen=events_seen,
                message=f"Read file {index} of {files_total}",
            ))

        _check_cancel(cancel_event)
        _emit(progress, ProgressEvent(
            phase="deduplicating",
            files_done=files_total,
            files_total=files_total,
            events_seen=events_seen,
            message="Deduplicating staged events",
        ))
        cross_file_duplicates = storage.dedup_cross_file()

        _check_cancel(cancel_event)
        _emit(progress, ProgressEvent(
            phase="detecting",
            files_done=files_total,
            files_total=files_total,
            events_seen=events_seen,
            message="Applying detection rules",
        ))
        # Feed detectors from staged storage in ingestion order. No complete
        # event list is ever constructed.
        for event in storage.iter_events():
            _check_cancel(cancel_event)
            for detector in detectors:
                detector.observe(event)

        findings: list[Finding] = []
        for detector in detectors:  # deterministic rule order (FR-036)
            findings.extend(detector.results())

        _check_cancel(cancel_event)
        _emit(progress, ProgressEvent(
            phase="finalizing",
            files_done=files_total,
            files_total=files_total,
            events_seen=events_seen,
            message="Collecting statistics",
        ))

        sums = storage.statistics_sums()
        statistics = RunStatistics(
            files_scanned=sums["files_scanned"],
            lines_read=sums["lines_read"],
            events_parsed=sums["events_parsed"],
            malformed=sums["malformed"],
            duplicates=sums["duplicates"],
            othersyslog=sums["othersyslog"],
            othersyslog_dropped=sums["othersyslog_dropped"],
            cross_file_duplicates=cross_file_duplicates,
        )

        # Same capped contract as the CLI: first 100 entries plus exact total.
        staged_errors, errors_total = storage.error_summary()

        exit_code = 1 if findings else 0
        if sums["files_scanned"] == 0 and errors_total > 0:
            exit_code = 2

    cleanup_errors = tuple(storage.cleanup_errors)
    _check_cancel(cancel_event)
    _emit(progress, ProgressEvent(
        phase="complete",
        files_done=len(files),
        files_total=len(files),
        events_seen=events_seen,
        message="Analysis complete",
    ))

    return AnalysisResult(
        findings=tuple(findings),
        statistics=statistics,
        errors=tuple(staged_errors),
        errors_total=errors_total,
        config=config,
        generated_at=request.generated_at,
        exit_code=exit_code,
        files=tuple(files),
        elapsed_seconds=time.monotonic() - started,
        cleanup_errors=cleanup_errors,
    )


def _process_file(
    storage: RunStorage,
    log_file: LogFile,
    config: AppConfig,
    reference_now: int,
    cancel_event: threading.Event | None,
) -> int:
    """Stream one file into storage; return the retained event count.

    Mirrors ``cli._process_file``: one transaction per encoding attempt,
    rollback on the UTF-8/Latin-1 fallback, strict abort after the successful
    attempt is committed, and recoverable filesystem races staged as input
    errors in normal mode. Cancellation propagates; the caller's
    ``RunStorage`` context manager handles cleanup and rollback.
    """
    first_error: ErrorEntry | None = None
    events_staged = 0
    try:
        _check_cancel(cancel_event)
        storage.begin()

        def duplicate_check(event: SecurityEvent) -> bool:
            _check_cancel(cancel_event)
            return storage.fingerprint_seen(event)

        for tag, item in stream_parse_file(
            log_file.path,
            reference_now,
            max_line_length=config.max_line_length,
            duplicate_check=duplicate_check,
        ):
            _check_cancel(cancel_event)
            if tag == "rollback":
                storage.rollback()
                storage.begin()
                first_error = None
                events_staged = 0
            elif tag == "event":
                storage.stage_event(item)
                events_staged += 1
            elif tag == "error":
                storage.stage_error(item)
                if first_error is None:
                    first_error = item
            elif tag == "stats":
                storage.stage_file_stats(str(log_file.path), item)
                storage.commit()
                if config.strict and first_error is not None:
                    raise _strict_abort(first_error)
                return events_staged
        storage.commit()  # pragma: no cover - the stream always yields stats
        return events_staged  # pragma: no cover
    except OSError as exc:
        entry = ErrorEntry(
            source_file=str(log_file.path),
            line_number=None,
            reason=(
                f"cannot read file: {exc.__class__.__name__}: "
                f"{exc.strerror or exc}"
            ),
            kind="input",
        )
        if config.strict:
            raise _strict_abort(entry)
        storage.rollback()
        storage.stage_error(entry)
        return 0
