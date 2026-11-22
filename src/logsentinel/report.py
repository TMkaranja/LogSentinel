"""Reporting engine for LogSentinel (Phase 4.4).

Implements the approved reporting contract:

- Console (FR-040, FR-130) and JSON (FR-041/FR-042/FR-043) rendering.
- Evidence is redacted before truncation (FR-162, NFR-009): credential
  bearing values are replaced with a fixed marker and never echoed. Regex
  redaction is conservative and best-effort - it does not claim to detect
  every possible secret; the length cap is the backstop.
- Errors are capped (FR-154) with a structured, separate overflow object.
- ``write_report`` is atomic (FR-132) and translates expected write
  failures into ReportError (FR-150).
- Renderers are pure: they never mutate inputs, never read the clock
  (``generated_at`` is caller-supplied, AR-010) and never perform detection.

Note: cross_file_duplicates is accepted explicitly (Phase 4.1 policy); it
is never derived from other counters.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, fields
from pathlib import Path

from .events import ErrorEntry, Finding, SecurityEvent
from .exceptions import ReportError

__all__ = [
    "REPORT_VERSION",
    "MAX_EVIDENCE_LENGTH",
    "MAX_REPORTED_ERRORS",
    "RunStatistics",
    "render_console",
    "render_json",
    "write_report",
]

#: Version of the JSON report schema (FR-041; matches the documented example).
REPORT_VERSION = 1

#: Maximum rendered length of evidence excerpts and error text (FR-043/FR-162).
#: Owned by the leaf event module (shared with ErrorEntry construction-time
#: sanitization, M6); re-exported here for the public reporting contract.
from .events import (  # noqa: F401 - re-exported contract symbols
    MAX_EVIDENCE_LENGTH,
    _cap,
    _redact,
    _REDACTED_PATH,
    _sanitize,
)

#: Maximum number of error entries rendered (FR-154).
MAX_REPORTED_ERRORS = 100

_SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}
_STAT_ORDER = (
    "files_scanned", "lines_read", "events_parsed", "malformed",
    "duplicates", "othersyslog", "othersyslog_dropped",
    "cross_file_duplicates",
)


@dataclass(frozen=True, slots=True)
class RunStatistics:
    """Run-level statistics supplied by the orchestrator (FR-040/FR-041).

    Every counter is provided explicitly by Phase 5; nothing is derived
    from unrelated values. All fields are non-negative integers.
    """

    files_scanned: int = 0
    lines_read: int = 0
    events_parsed: int = 0
    malformed: int = 0
    duplicates: int = 0
    othersyslog: int = 0
    othersyslog_dropped: int = 0
    cross_file_duplicates: int = 0

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is not int or value < 0:
                raise ValueError(
                    f"invalid statistic {field.name!r}: "
                    f"expected a non-negative integer, got {value!r}")


# _redact/_cap/_sanitize are imported from .events above (M6: the single
# sanitizer implementation is shared with ErrorEntry construction-time
# sanitization).


def _finding_sort_key(finding: Finding) -> tuple[str, int, str]:
    return (finding.rule_id,
            _SEVERITY_RANK.get(finding.severity, len(_SEVERITY_RANK)),
            finding.src_ip)


def _render_evidence(lines) -> tuple[str, ...]:
    return tuple(_sanitize(line) for line in lines)


def _check_statistics(statistics: RunStatistics) -> RunStatistics:
    if not isinstance(statistics, RunStatistics):
        raise TypeError("statistics must be a RunStatistics instance")
    return statistics


def render_console(
    findings, statistics: RunStatistics, config, *, errors=None,
    errors_total: int | None = None,
) -> str:
    """Render the human-readable report (FR-040, FR-130).

    Findings are grouped by rule (rule order) and sorted by severity then
    source IP for display only - the input objects are never mutated.

    ``errors_total`` (Phase 5): when the caller streams errors from storage
    it supplies only the first ``MAX_REPORTED_ERRORS`` entries plus the
    exact total; the overflow line is computed from the difference. When
    ``None`` (default) the total is derived from ``errors`` as before.
    """
    _check_statistics(statistics)
    ordered = sorted(findings, key=_finding_sort_key)
    lines = [f"LogSentinel report (version {REPORT_VERSION})"]
    if not ordered:
        lines.append("No findings.")
    else:
        lines.append("Findings:")
        current_rule: str | None = None
        for finding in ordered:
            if finding.rule_id != current_rule:
                current_rule = finding.rule_id
                lines.append(f"  {finding.rule_id}:")
            lines.append(
                f"    [{finding.severity}] {finding.src_ip} "
                f"first={finding.first_seen} last={finding.last_seen}")
            summary_text = ", ".join(
                f"{key}={value}" for key, value in sorted(finding.summary.items()))
            lines.append(f"      {summary_text}")
            for excerpt in _render_evidence(finding.evidence):
                lines.append(f"      evidence: {excerpt}")
    lines.append("Statistics:")
    for key in _STAT_ORDER:
        lines.append(f"  {key}: {getattr(statistics, key)}")
    lines.append(f"  findings: {len(ordered)}")
    shown_errors = list(errors)[:MAX_REPORTED_ERRORS] if errors is not None else []
    total_errors = (errors_total if errors_total is not None
                    else len(list(errors)) if errors is not None else 0)
    if total_errors > MAX_REPORTED_ERRORS:
        omitted = total_errors - len(shown_errors)
        lines.append(
            f"errors: {len(shown_errors)} of {total_errors} shown "
            f"({omitted} omitted)")
    return chr(10).join(lines)


def _finding_to_json(finding: Finding) -> dict[str, object]:
    return {
        "rule_id": finding.rule_id,
        "severity": finding.severity,
        "src_ip": finding.src_ip,
        "first_seen": finding.first_seen,
        "last_seen": finding.last_seen,
        "evidence": _render_evidence(finding.evidence),
        "summary": dict(finding.summary),
    }


def _error_to_json(entry: ErrorEntry) -> dict[str, object]:
    return {
        "source_file": _REDACTED_PATH,  # R4: paths never echoed externally
        "line_number": entry.line_number,
        "reason": _sanitize(entry.reason),
        "kind": entry.kind,
    }


def render_json(
    findings, statistics: RunStatistics, config, generated_at: str,
    *, errors=None, errors_total: int | None = None,
) -> str:
    """Render the machine-readable report (FR-041/FR-042/FR-043).

    Deterministic for identical inputs and configuration except for
    ``generated_at`` (which is caller-supplied). ``errors_overflow`` is
    emitted only when truncation occurs (FR-154). Key order in the output
    is canonical (sorted) via ``sort_keys=True``.

    ``errors_total`` (Phase 5): when provided, ``errors`` contains only the
    first ``MAX_REPORTED_ERRORS`` entries and ``errors_total`` is the exact
    run total; the overflow marker uses the difference. No new JSON fields;
    report version unchanged.
    """
    _check_statistics(statistics)
    ordered = sorted(findings, key=_finding_sort_key)
    all_errors = list(errors) if errors is not None else []
    total_errors = (errors_total if errors_total is not None
                    else len(all_errors))
    shown_errors = all_errors[:MAX_REPORTED_ERRORS]
    payload: dict[str, object] = {
        "report_version": REPORT_VERSION,
        "generated_at": generated_at,
        "config_used": {
            "ssh_threshold": config.ssh_threshold,
            "ssh_window_seconds": config.ssh_window_seconds,
            "portscan_threshold": config.portscan_threshold,
            "http_4xx_threshold": config.http_4xx_threshold,
            "strict": config.strict,
            "max_line_length": config.max_line_length,
            "max_file_mb": config.max_file_mb,
        },
        "statistics": {**{key: getattr(statistics, key) for key in _STAT_ORDER},
                       "findings": len(ordered)},
        "findings": [_finding_to_json(f) for f in ordered],
        "errors": [_error_to_json(entry) for entry in shown_errors],
    }
    if total_errors > MAX_REPORTED_ERRORS:
        payload["errors_overflow"] = {
            "shown": len(shown_errors), "total": total_errors}
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def write_report(path: str, content: str) -> None:
    """Write a report atomically (FR-132).

    Content is written to a temporary file in the target directory and then
    atomically replaced onto the target. Expected write failures (missing
    directory, permission problems, directory targets, disk errors) are
    translated into ReportError (FR-150); the temporary file is always
    cleaned up.
    """
    target = Path(path)
    directory = target.parent if str(target.parent) else Path(".")
    tmp_name: str | None = None
    try:
        handle_fd, tmp_name = tempfile.mkstemp(
            prefix=".logsentinel-report-", suffix=".tmp", dir=str(directory))
        with os.fdopen(handle_fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.replace(tmp_name, target)
        tmp_name = None
    except OSError as exc:
        raise ReportError(
            f"cannot write report to {path!s}: "
            f"{exc.__class__.__name__}: {exc.strerror or exc}") from None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
