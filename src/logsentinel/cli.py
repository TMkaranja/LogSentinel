"""Command-line interface and application orchestration (Phase 4.6, Phase 5).

Implements docs/REQUIREMENTS.md FR-070/FR-071/FR-072 (CLI), FR-090 (exit
codes), FR-100/FR-151/FR-152 (normal vs strict error handling), FR-153
(unexpected failures), FR-110/NFR-004 (streaming pipeline) and
docs/ARCHITECTURE.md AR-010 (the CLI is the only module that reads the wall
clock) and AR-012 (cli.py translates exceptions into exit codes).

Orchestration sequence (single run, Phase 5 streaming architecture):
    argparse -> load_config -> discover_inputs -> stream_parse_file (per
    file, incrementally, one shared reference_now) -> RunStorage staging
    (events, errors, and per-file statistics in a temporary SQLite
    database; intra-file fingerprint checks run in SQLite inside each
    file's transaction) -> SQL cross-file deduplication -> detectors fed
    from staged storage via observe/results -> RunStatistics -> render
    (all reports, in memory) -> write/print -> exit code.

Normal mode records recoverable problems as ErrorEntry data in staging and
continues; strict mode aborts on the first recorded error with the matching
exception type and exit code 2. Exit codes: 0 clean, 1 findings, 2 usage/
config/input-path/report/strict abort, 3 unexpected failure (FR-090,
FR-153).

NFR-004 is addressed by the streaming implementation: no full-run event or
error list is built, per-file parsing is incremental, and per-file
fingerprint tracking lives in SQLite. Memory still grows with the
explicitly permitted per-IP detector aggregation and final evidence
materialization - constant memory is NOT claimed.

Patching surface for tests: module-level names (``stream_parse_file``,
``discover_inputs``, ``load_config``, ``render_console``, ``render_json``,
``write_report``, ``datetime``, and the detector classes
``SSHBruteForceDetector``/``PortScanDetector``/``HTTP4xxAbuseDetector``)
can be patched via ``unittest.mock.patch("logsentinel.cli.<name>", ...)``;
``RunStorage.fingerprint_seen`` is patched at the storage class for
duplicate-tracking spies.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from typing import Sequence

from . import __version__
from .config import load_config
from .detectors import (
    HTTP4xxAbuseDetector,
    PortScanDetector,
    SSHBruteForceDetector,
)
from .events import ErrorEntry, Finding, SecurityEvent
from .exceptions import (
    ConfigError,
    InputPathError,
    LogSentinelError,
    ParseError,
    ReportError,
)
from .inputs import discover_inputs
from .parsers import stream_parse_file
from .report import (
    RunStatistics,
    _REDACTED_PATH,
    _sanitize,
    render_console,
    render_json,
    write_report,
)
from .storage import RunStorage

__all__ = ["main", "build_parser"]

#: Strict-mode error kind -> exception type mapping (FR-150/FR-152).
_EXCEPTION_BY_KIND: dict[str, type[Exception]] = {
    "config": ConfigError,
    "input": InputPathError,
    "parse": ParseError,
    "report": ReportError,
}


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser (FR-071/FR-072).

    Zero positional inputs are rejected by ``nargs="+"`` with argparse's
    usage error and exit code 2. No configuration defaults are duplicated
    here: every optional value defaults to ``None`` and only non-``None``
    values are forwarded to ``load_config`` as overrides (AR-008).
    """
    parser = argparse.ArgumentParser(
        prog="logsentinel",
        description=(
            "Defensive, file-based log analysis. Findings are review leads "
            "for a human analyst - not assertions of malicious intent."))
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--config", metavar="PATH", default=None,
        help="optional JSON configuration file")
    parser.add_argument(
        "--ssh-threshold", metavar="N", type=int, default=None,
        help="SSH failure threshold (default from built-in config)")
    parser.add_argument(
        "--ssh-window", metavar="SECONDS", type=int, default=None,
        dest="ssh_window_seconds",
        help="SSH detection window in seconds")
    parser.add_argument(
        "--portscan-threshold", metavar="N", type=int, default=None,
        help="port-scan threshold")
    parser.add_argument(
        "--http-4xx-threshold", metavar="N", type=int, default=None,
        help="HTTP 4xx abuse threshold")
    parser.add_argument(
        "--json", metavar="PATH", default=None, dest="json_path",
        help="write a JSON report to PATH (atomically)")
    parser.add_argument(
        "--text", metavar="PATH", default=None, dest="text_path",
        help="write a human-readable report to PATH (atomically)")
    parser.add_argument(
        "--strict", action="store_true", default=None,
        help="abort with exit code 2 on the first recorded error")
    parser.add_argument(
        "--quiet", action="store_true",
        help="suppress the console report (report files are still written)")
    parser.add_argument(
        "paths", nargs="+", metavar="PATH",
        help="log files or directories to analyse")
    return parser


def _cli_overrides(args: argparse.Namespace) -> dict[str, object]:
    """Map parsed options onto configuration override keys (None = unset)."""
    return {
        "ssh_threshold": args.ssh_threshold,
        "ssh_window_seconds": args.ssh_window_seconds,
        "portscan_threshold": args.portscan_threshold,
        "http_4xx_threshold": args.http_4xx_threshold,
        "strict": args.strict,
    }


def _strict_abort(entry: ErrorEntry) -> Exception:
    """Build the strict-mode abort exception for an error entry (FR-152).

    The reason is sanitized before the message is composed: parser
    exception reasons can embed raw log-line tokens (e.g. invalid-IP
    diagnostics echo the offending token), and this message reaches
    stderr in strict mode. Reuses the report layer's single redaction
    implementation - no second, inconsistent sanitizer.
    """
    exception_type = _EXCEPTION_BY_KIND.get(entry.kind, InputPathError)
    # R4: the strict-abort diagnostic is externally visible (stderr), so the
    # source path is replaced with the neutral marker; the line number and
    # kind are not path information and are preserved.
    location = f"in {_REDACTED_PATH}"
    if entry.line_number is not None:
        location += f" at line {entry.line_number}"
    return exception_type(
        f"strict mode abort: {_sanitize(entry.reason)} ({location}, "
        f"kind={entry.kind!r})")


def _run(
    args: argparse.Namespace,
    config: object,
    reference_now: int,
    generated_at: str,
) -> int:
    """Execute one streaming analysis run (Phase 5, NFR-004/FR-110).

    Returns 0 (clean) or 1 (findings); input problems with zero scanned
    files return 2 (FR-090). Raises LogSentinelError subclasses for strict
    aborts and report-write failures; unexpected exceptions propagate to
    the boundary in ``main`` (which also cleans up the staging database).

    No full-run event list and no full-run error list exist anywhere in
    this path: parsed items and errors are staged into the temporary SQLite
    database as they stream, cross-file deduplication runs as SQL over the
    staged rows, and detectors consume staged events through bounded
    per-IP aggregation (spec 3.10).
    """
    discovery = discover_inputs(args.paths, max_file_mb=config.max_file_mb)

    with RunStorage() as storage:
        # Discovery errors are staged first: original error ordering starts
        # with them (spec 3.9).
        for entry in discovery.errors:
            storage.stage_error(entry)
        # Strict mode checks discovery errors before any parsing (FR-152);
        # the staging database is cleaned up by the context manager.
        if config.strict and discovery.errors:
            raise _strict_abort(discovery.errors[0])

        files = discovery.files
        if not files:
            print(
                "logsentinel: warning: no input files discovered; "
                "nothing to analyse", file=sys.stderr)

        detectors = (
            SSHBruteForceDetector(
                config.ssh_threshold, config.ssh_window_seconds),
            PortScanDetector(config.portscan_threshold),
            HTTP4xxAbuseDetector(config.http_4xx_threshold),
        )

        for log_file in files:
            _process_file(storage, log_file, config, reference_now)

        cross_file_duplicates = storage.dedup_cross_file()

        # Feed the detectors from staged storage in ingestion order; each
        # detector applies its own stable (timestamp, kind) per-IP ordering
        # (FR-111). No complete event list is ever constructed.
        for event in storage.iter_events():
            for detector in detectors:
                detector.observe(event)
        findings: list[Finding] = []
        for detector in detectors:  # deterministic rule order (FR-036)
            findings.extend(detector.results())

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

        # Only the first staged errors are fetched; the exact total comes
        # from storage (spec 3.9 - no full-run error list).
        staged_errors, errors_total = storage.error_summary()

        exit_code = 1 if findings else 0
        if sums["files_scanned"] == 0 and errors_total > 0:
            # FR-090: input problems with nothing analysed -> 2. Ordinary
            # parser errors never trigger this rule: they only exist for
            # successfully scanned files.
            exit_code = 2

        # Render every requested report fully in memory BEFORE writing any
        # file: a rendering failure must not leave half-delivered reports
        # behind. Individual writes stay atomic via write_report(); no
        # cross-file rollback is claimed.
        json_content: str | None = None
        text_content: str | None = None
        if args.json_path:
            json_content = render_json(
                findings, statistics, config, generated_at,
                errors=staged_errors, errors_total=errors_total)
        if args.text_path or not args.quiet:
            # One render serves both the --text file and stdout.
            text_content = render_console(
                findings, statistics, config,
                errors=staged_errors, errors_total=errors_total)

        if json_content is not None:
            write_report(args.json_path, json_content)
        if args.text_path and text_content is not None:
            write_report(args.text_path, text_content)
        if not args.quiet and text_content is not None:
            print(text_content)

        return exit_code


def _process_file(
    storage: RunStorage,
    log_file: object,
    config: object,
    reference_now: int,
) -> None:
    """Stream one file into staging under a per-file transaction (spec 3.1).

    - The UTF-8 attempt is staged inside its own transaction; on a decode
      failure the ``("rollback", None)`` item discards the partial attempt
      and the full Latin-1 retry is staged into a fresh transaction; only
      the successful attempt (with its statistics) is committed (FR-003).
    - Strict mode aborts on the first error of the *successful* attempt,
      checked immediately after the file is staged and committed (FR-152) -
      mirroring the batch contract where a discarded attempt's errors never
      become the abort reason. The staging database is cleaned up by the
      ``RunStorage`` context manager.
    - A parse-time filesystem error (file vanished between discovery and
      parsing) is a recoverable input error in normal mode and a strict
      abort otherwise; it never crashes the run.
    """
    first_error: ErrorEntry | None = None
    try:
        storage.begin()

        def duplicate_check(event: SecurityEvent) -> bool:
            # SQLite-backed exact intra-fingerprint check (Phase 5
            # correction): the staged rows are the tracking records; the
            # check shares the file transaction, so a rolled-back UTF-8
            # attempt discards its events and duplicate knowledge together.
            return storage.fingerprint_seen(event)

        for tag, item in stream_parse_file(
            log_file.path, reference_now,
            max_line_length=config.max_line_length,
            duplicate_check=duplicate_check,
        ):
            if tag == "rollback":
                # Discard the failed UTF-8 attempt entirely (spec 3.1).
                storage.rollback()
                storage.begin()
                first_error = None
            elif tag == "event":
                storage.stage_event(item)
            elif tag == "error":
                storage.stage_error(item)
                if first_error is None:
                    first_error = item
            elif tag == "stats":
                storage.stage_file_stats(str(log_file.path), item)
                storage.commit()
                if config.strict and first_error is not None:
                    raise _strict_abort(first_error)
                return
        storage.commit()  # pragma: no cover - stream always yields stats
    except OSError as exc:
        entry = ErrorEntry(
            source_file=str(log_file.path), line_number=None,
            reason=f"cannot read file: {exc.__class__.__name__}: "
                   f"{exc.strerror or exc}",
            kind="input")
        if config.strict:
            # Strict mode aborts on the first error, never continuing to
            # later files (FR-152).
            raise _strict_abort(entry)
        # Normal mode: discover-vs-parse race becomes recoverable data.
        storage.rollback()
        storage.stage_error(entry)


def main(argv: Sequence[str] | None = None) -> int:
    """Application entry point; returns the process exit code (FR-090)."""
    # argparse stays outside the application boundary: --help/--version exit
    # successfully and invalid arguments exit with argparse's code 2.
    args = build_parser().parse_args(argv)

    try:
        # Invalid configuration aborts before any input processing (FR-061);
        # ConfigError keeps its dedicated diagnostic and exit code 2.
        try:
            config = load_config(_cli_overrides(args), args.config)
        except ConfigError as exc:
            print(f"logsentinel: configuration error: {exc}", file=sys.stderr)
            return 2

        # AR-010: the wall clock is read exactly once per run, here.
        run_time = datetime.now(timezone.utc)
        reference_now = int(run_time.timestamp())
        generated_at = run_time.isoformat()  # ISO-8601 UTC, same instant

        return _run(args, config, reference_now, generated_at)
    except LogSentinelError as exc:
        print(f"logsentinel: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # outermost application boundary only (FR-153)
        # R3 (security audit): the message text of an arbitrary unexpected
        # exception can embed log-derived content; sanitize it (best-effort,
        # single shared sanitizer) before it reaches stderr. The exception
        # class name is code-side context, not log-derived, and is
        # preserved; the short-diagnostic behaviour (no traceback) and exit
        # code 3 are unchanged. LogSentinelError handling above is separate.
        print(
            f"logsentinel: unexpected failure: "
            f"{exc.__class__.__name__}: {_sanitize(str(exc))}",
            file=sys.stderr)
        return 3
