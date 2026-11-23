"""Report rendering and export helpers for the LogSentinel GUI.

This module is intentionally free of Qt imports so report generation can be
tested and used independently of the desktop shell. It delegates structured
report rendering to the existing :meth:`AnalysisResult.render_json` path and
adds only a standalone HTML presentation layer.

Security properties:

- JSON output is produced by the existing report renderer, preserving its
  evidence redaction, source-path redaction, error cap, and schema.
- HTML output is derived from that JSON payload and HTML-escapes every value
  before insertion. Summary values, evidence, and error reasons are also
  passed through the existing sanitizer as defense in depth.
- HTML is a single self-contained document with no scripts or remote assets.
"""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path

from ..report import _REDACTED_PATH, _sanitize, write_report
from .backend import AnalysisResult

__all__ = [
    "HTML_FORMAT",
    "JSON_FORMAT",
    "default_report_filename",
    "ensure_export_extension",
    "export_dialog_title",
    "export_report",
    "format_generated_at",
    "render_html_report",
    "report_filter",
    "suggested_export_path",
]

JSON_FORMAT = "json"
HTML_FORMAT = "html"
_SUPPORTED_FORMATS = (JSON_FORMAT, HTML_FORMAT)
_EXTENSIONS = {JSON_FORMAT: ".json", HTML_FORMAT: ".html"}
_FILTERS = {
    JSON_FORMAT: "JSON report (*.json);;All files (*)",
    HTML_FORMAT: "HTML report (*.html);;All files (*)",
}
_TITLES = {
    JSON_FORMAT: "Export JSON report",
    HTML_FORMAT: "Export HTML report",
}

_STAT_LABELS = (
    ("files_scanned", "Files scanned"),
    ("lines_read", "Lines read"),
    ("events_parsed", "Events parsed"),
    ("malformed", "Malformed lines"),
    ("duplicates", "Intra-file duplicates"),
    ("othersyslog", "Other syslog lines"),
    ("othersyslog_dropped", "Other syslog dropped"),
    ("cross_file_duplicates", "Cross-file duplicates"),
    ("findings", "Findings"),
)
_CONFIG_LABELS = (
    ("ssh_threshold", "SSH failure threshold"),
    ("ssh_window_seconds", "SSH detection window (seconds)"),
    ("portscan_threshold", "Port-scan threshold"),
    ("http_4xx_threshold", "HTTP 4xx threshold"),
    ("strict", "Strict mode"),
    ("max_line_length", "Maximum line length"),
    ("max_file_mb", "Maximum file size (MB)"),
)


_STYLE = """
:root {
    color-scheme: dark;
    --bg: #070c16;
    --surface: #0e1727;
    --raised: #121e33;
    --border: #243653;
    --text: #e8f0ff;
    --muted: #8ca1c1;
    --dim: #637896;
    --accent: #22d3ee;
    --high: #ef4444;
    --medium: #f59e0b;
    --low: #38bdf8;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
    background: var(--bg);
    color: var(--text);
    font-family: "Segoe UI", "Inter", "Noto Sans", Arial, sans-serif;
    font-size: 14px;
    line-height: 1.5;
}
.wrap { max-width: 1120px; margin: 0 auto; padding: 32px; }
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    gap: 18px; padding-bottom: 20px; border-bottom: 1px solid var(--border);
}
.brand { display: flex; align-items: center; gap: 12px; }
.mark {
    width: 44px; height: 44px; border-radius: 12px;
    display: grid; place-items: center; font-weight: 800; color: #06111f;
    background: linear-gradient(135deg, #22d3ee, #2563eb);
    border: 1px solid #67e8f9;
}
h1, h2, h3, p { margin: 0; }
h1 { font-size: 20px; letter-spacing: .2px; }
.brand p { color: var(--muted); font-size: 10px; font-weight: 700; letter-spacing: .7px; }
.stamp { color: var(--muted); font-size: 11px; text-align: right; }
.hero {
    display: flex; align-items: flex-start; justify-content: space-between;
    gap: 24px; margin: 28px 0 22px;
}
.eyebrow { color: #67e8f9; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
.hero h2 { font-size: 29px; line-height: 1.15; margin: 5px 0 8px; }
.muted { color: var(--muted); }
.dim { color: var(--dim); }
.badge {
    display: inline-block; border: 1px solid var(--border); border-radius: 999px;
    padding: 5px 11px; color: var(--accent); background: #0b2b36;
    font-size: 10px; font-weight: 800; white-space: nowrap;
}
.cards {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px; margin: 0 0 20px;
}
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 16px 18px;
}
.card-label { color: var(--muted); font-size: 10px; font-weight: 800; letter-spacing: .6px; }
.card-value { font-size: 28px; font-weight: 800; margin-top: 3px; }
.card-note { color: var(--dim); font-size: 11px; margin-top: 2px; }
.grid-two { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 20px; }
.panel {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 18px;
}
.panel h3, .section-title {
    color: #dce8fa; font-size: 14px; font-weight: 800; margin-bottom: 12px;
}
.meta { width: 100%; border-collapse: collapse; }
.meta td { padding: 5px 0; border-bottom: 1px solid #172640; vertical-align: top; }
.meta tr:last-child td { border-bottom: none; }
.meta .k { color: var(--muted); width: 52%; }
.meta .v { text-align: right; font-weight: 600; }
.findings { display: grid; gap: 14px; }
.finding {
    background: var(--surface); border: 1px solid var(--border);
    border-left: 4px solid var(--low); border-radius: 12px; padding: 18px;
}
.finding.high { border-left-color: var(--high); }
.finding.medium { border-left-color: var(--medium); }
.finding.low { border-left-color: var(--low); }
.finding-head { display: flex; align-items: flex-start; gap: 12px; }
.severity {
    display: inline-block; border-radius: 999px; padding: 3px 9px;
    font-size: 9px; font-weight: 800; letter-spacing: .5px;
}
.severity.high { background: #3a1218; color: #fca5a5; border: 1px solid #7f1d1d; }
.severity.medium { background: #35250b; color: #fcd34d; border: 1px solid #784b0e; }
.severity.low { background: #0b2b36; color: #67e8f9; border: 1px solid #155e6b; }
.rule { color: #67e8f9; font-size: 11px; font-weight: 800; }
.ip { font-size: 19px; font-weight: 800; margin-top: 2px; }
.times { color: var(--muted); font-size: 11px; margin: 12px 0 14px; }
.times b { color: #c8d8ee; font-weight: 600; }
.finding-grid { display: grid; grid-template-columns: 1.05fr 1.6fr; gap: 18px; }
.finding h3 { color: var(--muted); font-size: 10px; letter-spacing: .6px; margin-bottom: 6px; }
.kv { display: grid; grid-template-columns: minmax(90px, .8fr) 1.4fr; gap: 10px; padding: 4px 0; border-bottom: 1px solid #172640; }
.kv:last-child { border-bottom: none; }
.kv .k { color: var(--muted); }
.kv .v { color: #c8d8ee; overflow-wrap: anywhere; }
.evidence { margin: 0; padding-left: 18px; color: #c8d8ee; }
.evidence li { margin: 0 0 5px; overflow-wrap: anywhere; }
.notice {
    background: #17200f; border: 1px solid #3f5f1d; border-radius: 8px;
    color: #bef264; padding: 8px 10px; font-size: 11px; margin: 0 0 12px;
}
.errors { width: 100%; border-collapse: collapse; font-size: 12px; }
.errors th {
    color: var(--muted); text-align: left; font-size: 10px; letter-spacing: .4px;
    border-bottom: 1px solid var(--border); padding: 8px 8px 8px 0;
}
.errors td { border-bottom: 1px solid #172640; padding: 8px 8px 8px 0; vertical-align: top; }
.errors tr:last-child td { border-bottom: none; }
.errors .reason { overflow-wrap: anywhere; }
.footer { color: var(--dim); font-size: 11px; border-top: 1px solid var(--border); margin-top: 24px; padding-top: 14px; }
@media (max-width: 780px) {
    .wrap { padding: 18px; }
    .hero { display: block; }
    .badge { margin-top: 12px; }
    .grid-two, .finding-grid { grid-template-columns: 1fr; }
}
@media print {
    :root { color-scheme: light; }
    body { background: #fff; color: #111; }
    .card, .panel, .finding { background: #fff; border-color: #bbb; }
    .muted, .dim, .card-label, .meta .k, .times, .finding h3, .stamp { color: #555; }
    .badge { background: #eef6ff; color: #075985; }
    .severity.high { background: #fee2e2; color: #991b1b; }
    .severity.medium { background: #fef3c7; color: #92400e; }
    .severity.low { background: #e0f2fe; color: #075985; }
    .errors th, .errors td, .meta td, .kv { border-color: #ddd; }
}
"""


def _safe(value) -> str:
    """Return an HTML-escaped display string."""
    return html.escape("" if value is None else str(value), quote=True)


def _safe_text(value) -> str:
    """Sanitize then HTML-escape a potentially sensitive display value."""
    return html.escape(_safe_display_text(value), quote=True)


def _safe_display_text(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return _sanitize_report_text(str(value))


def _sanitize_report_text(text: str) -> str:
    # Reuse the single existing report sanitizer; never reimplement it here.
    return _sanitize(text)


def format_generated_at(value: object) -> str:
    """Format the caller-supplied run timestamp for human display in UTC."""
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return str(value or "—")
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _format_epoch(value) -> str:
    try:
        moment = datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (OverflowError, OSError, TypeError, ValueError):
        return _safe(value)
    return moment.strftime("%Y-%m-%d %H:%M:%S UTC")


def _outcome(result: AnalysisResult) -> str:
    return {
        0: "Clean run",
        1: "Findings detected",
        2: "Input problem",
    }.get(result.exit_code, "Analysis complete")


def _summary_html(summary) -> str:
    if not isinstance(summary, dict) or not summary:
        return '<p class="muted">No summary fields.</p>'
    rows = []
    for key in sorted(summary, key=str):
        value = summary[key]
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value, ensure_ascii=False, sort_keys=True)
        # Sanitize the key/value pair together so a secret-bearing key such as
        # ``password`` still redacts its value, then split the rendered pair
        # back into the key and value cells for presentation.
        key_text = _sanitize(str(key))
        pair_text = _sanitize(f"{key}={value}")
        prefix = f"{key_text}="
        value_text = (pair_text[len(prefix):]
                      if pair_text.startswith(prefix) else pair_text)
        rows.append(
            '<div class="kv"><span class="k">'
            f"{html.escape(key_text, quote=True)}</span>"
            '<span class="v">'
            f"{html.escape(value_text, quote=True)}</span></div>")
    return "".join(rows)


def _evidence_html(evidence) -> str:
    if not evidence:
        return '<p class="muted">No evidence excerpts.</p>'
    items = "".join(
        f"<li>{_safe_text(line)}</li>" for line in evidence)
    return f'<ul class="evidence">{items}</ul>'


def _finding_html(finding: dict) -> str:
    severity = str(finding.get("severity", "low")).lower()
    if severity not in {"high", "medium", "low"}:
        severity = "low"
    rule = _safe_text(finding.get("rule_id", "Unknown rule"))
    source = _safe_text(finding.get("src_ip", "Unknown source"))
    first_seen = _format_epoch(finding.get("first_seen"))
    last_seen = _format_epoch(finding.get("last_seen"))
    summary = _summary_html(finding.get("summary"))
    evidence = _evidence_html(finding.get("evidence"))
    return f"""
    <article class="finding {severity}">
      <div class="finding-head">
        <span class="severity {severity}">{severity.upper()}</span>
        <div><div class="rule">{rule}</div><div class="ip">{source}</div></div>
      </div>
      <div class="times">First seen <b>{first_seen}</b> &nbsp;·&nbsp; Last seen <b>{last_seen}</b></div>
      <div class="finding-grid">
        <div><h3>SUMMARY</h3>{summary}</div>
        <div><h3>EVIDENCE</h3>{evidence}</div>
      </div>
    </article>
    """


def _stats_rows(statistics: dict) -> str:
    rows = []
    for key, label in _STAT_LABELS:
        if key not in statistics:
            continue
        rows.append(
            f'<tr><td class="k">{_safe(label)}</td>'
            f'<td class="v">{_safe(statistics[key])}</td></tr>')
    return "".join(rows)


def _config_rows(config: dict) -> str:
    rows = []
    for key, label in _CONFIG_LABELS:
        if key not in config:
            continue
        value = config[key]
        if isinstance(value, bool):
            value = "Yes" if value else "No"
        rows.append(
            f'<tr><td class="k">{_safe(label)}</td>'
            f'<td class="v">{_safe(value)}</td></tr>')
    return "".join(rows)


def _errors_html(errors, shown: int, total: int) -> str:
    notice = ""
    if total > shown:
        notice = (
            f'<p class="notice">Showing {shown} of {total} recoverable errors; '
            f'{total - shown} omitted by the reporting limit.</p>')
    if not errors:
        return notice + '<p class="muted">No recoverable errors recorded.</p>'
    rows = []
    for entry in errors:
        line = entry.get("line_number")
        line_text = "—" if line is None else str(line)
        rows.append(
            "<tr>"
            f"<td>{_safe_text(entry.get('kind', 'unknown'))}</td>"
            f"<td>{_safe(line_text)}</td>"
            f'<td class="reason">{_safe_text(entry.get("reason", ""))}</td>'
            f"<td>{_safe_text(_REDACTED_PATH)}</td>"
            "</tr>")
    return notice + (
        '<table class="errors"><thead><tr>'
        "<th>Kind</th><th>Line</th><th>Reason</th><th>Source</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>")


def render_html_report(result: AnalysisResult) -> str:
    """Render a standalone, escaped HTML security analysis report."""
    payload = json.loads(result.render_json())
    findings = payload.get("findings") or []
    statistics = payload.get("statistics") or {}
    config = payload.get("config_used") or {}
    errors = payload.get("errors") or []
    overflow = payload.get("errors_overflow") or {}
    shown_errors = int(overflow.get("shown", len(errors)))
    total_errors = int(overflow.get("total", len(errors)))
    if total_errors > shown_errors:
        error_note = f"{shown_errors} of {total_errors} shown"
    elif total_errors:
        error_note = f"{total_errors} recorded"
    else:
        error_note = "none"
    counts = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        severity = str(finding.get("severity", "low")).lower()
        if severity in counts:
            counts[severity] += 1
    generated_at = _safe_text(format_generated_at(payload.get("generated_at", "")))
    report_version = _safe(payload.get("report_version", ""))
    finding_cards = "".join(_finding_html(item) for item in findings)
    findings_section = (
        '<div class="findings">' + finding_cards + "</div>"
        if findings else
        '<div class="panel"><p class="muted">No findings were reported for '
        "this run.</p></div>")
    stats_rows = _stats_rows(statistics)
    config_rows = _config_rows(config)
    errors_section = _errors_html(errors, shown_errors, total_errors)
    outcome = _safe(_outcome(result))
    elapsed = _safe(f"{result.elapsed_seconds:.2f} s")
    files = _safe(statistics.get("files_scanned", len(result.files)))
    events = _safe(statistics.get("events_parsed", 0))
    finding_count = _safe(statistics.get("findings", len(findings)))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="LogSentinel">
<title>LogSentinel Security Analysis Report</title>
<style>{_STYLE}</style>
</head>
<body>
<div class="wrap">
  <header class="topbar">
    <div class="brand">
      <div class="mark">LS</div>
      <div><h1>LogSentinel</h1><p>DEFENSIVE LOG INTELLIGENCE</p></div>
    </div>
    <div class="stamp">Offline analysis<br>Report version {report_version}</div>
  </header>

  <section class="hero">
    <div>
      <p class="eyebrow">SECURITY ANALYSIS REPORT</p>
      <h2>Evidence-backed review leads.</h2>
      <p class="muted">Generated at {generated_at}</p>
    </div>
    <span class="badge">{outcome}</span>
  </section>

  <section class="cards">
    <div class="card"><div class="card-label">FINDINGS</div>
      <div class="card-value">{finding_count}</div>
      <div class="card-note">{counts['high']} high · {counts['medium']} medium · {counts['low']} low</div></div>
    <div class="card"><div class="card-label">EVENTS PARSED</div>
      <div class="card-value">{events}</div>
      <div class="card-note">across {files} file(s)</div></div>
    <div class="card"><div class="card-label">RECOVERABLE ERRORS</div>
      <div class="card-value">{_safe(total_errors)}</div>
      <div class="card-note">{_safe(error_note)}</div></div>
    <div class="card"><div class="card-label">ELAPSED</div>
      <div class="card-value">{elapsed}</div>
      <div class="card-note">run duration</div></div>
  </section>

  <section class="grid-two">
    <div class="panel"><h3>Run metadata</h3>
      <table class="meta">
        <tr><td class="k">Generated at</td><td class="v">{generated_at}</td></tr>
        <tr><td class="k">Report version</td><td class="v">{report_version}</td></tr>
        <tr><td class="k">Outcome</td><td class="v">{outcome}</td></tr>
        <tr><td class="k">Elapsed</td><td class="v">{elapsed}</td></tr>
      </table>
    </div>
    <div class="panel"><h3>Configuration used</h3>
      <table class="meta">{config_rows}</table>
    </div>
  </section>

  <section class="panel" style="margin-bottom:20px;"><h3>Scan statistics</h3>
    <table class="meta">{stats_rows}</table>
  </section>

  <h2 class="section-title">Findings</h2>
  {findings_section}

  <h2 class="section-title" style="margin-top:24px;">Recoverable errors</h2>
  <div class="panel">{errors_section}</div>

  <p class="footer">Generated locally by LogSentinel. Findings are evidence-backed review leads for a human analyst, not verdicts. Source paths and credential-bearing values are redacted by the report pipeline.</p>
</div>
</body>
</html>
"""


def render_report_content(result: AnalysisResult, kind: str) -> str:
    """Render one supported export format without writing it."""
    if kind == JSON_FORMAT:
        return result.render_json()
    if kind == HTML_FORMAT:
        return render_html_report(result)
    raise ValueError(f"unsupported report format: {kind!r}")


def export_report(result: AnalysisResult, kind: str, path: str) -> None:
    """Atomically write a JSON or HTML report to ``path``."""
    write_report(path, render_report_content(result, kind))


def ensure_export_extension(path: str, kind: str) -> str:
    """Append the expected extension unless the path already has it."""
    if kind not in _SUPPORTED_FORMATS:
        raise ValueError(f"unsupported report format: {kind!r}")
    if not path:
        raise ValueError("report path must not be empty")
    expected = _EXTENSIONS[kind]
    target = Path(path)
    if target.suffix.lower() == expected:
        return str(target)
    return str(target.with_name(target.name + expected))


def report_filter(kind: str) -> str:
    """Return the save-dialog filter for a report format."""
    try:
        return _FILTERS[kind]
    except KeyError:
        raise ValueError(f"unsupported report format: {kind!r}") from None


def _report_stamp(generated_at: object) -> str:
    text = str(generated_at or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        moment = datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y%m%d-%H%M%S")


def default_report_filename(result: AnalysisResult, kind: str) -> str:
    """Build a deterministic default report filename from the run timestamp."""
    if kind not in _SUPPORTED_FORMATS:
        raise ValueError(f"unsupported report format: {kind!r}")
    return f"logsentinel-report-{_report_stamp(result.generated_at)}" \
           f"{_EXTENSIONS[kind]}"


def suggested_export_path(
    result: AnalysisResult,
    kind: str,
    directory: str | Path | None = None,
) -> str:
    """Suggest a save path, preferring the user's Documents folder."""
    base = Path(directory) if directory is not None else Path.home() / "Documents"
    if not base.is_dir():
        base = Path.cwd()
    return str(base / default_report_filename(result, kind))


def export_dialog_title(kind: str) -> str:
    """Return the save-dialog title for a report format."""
    try:
        return _TITLES[kind]
    except KeyError:
        raise ValueError(f"unsupported report format: {kind!r}") from None
