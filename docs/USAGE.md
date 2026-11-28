# LogSentinel — CLI Usage Reference

- **Document:** USAGE.md
- **Phase:** Phase 1 user documentation (CLI reference)
- **Status:** Commands below describe the current CLI; platform behavior depends on the installed Python environment.

This document focuses on the command-line interface. For user-facing coverage of the Windows GUI, first launch, settings, report exports, data handling, and product limitations, see the [Phase 1 User Guide](USER_GUIDE.md).

LogSentinel is a defensive, file-based log analysis CLI. Findings are review
leads for a human analyst — not assertions of malicious intent.

## 1. Prerequisites

- **Python 3.12 or newer** (standard library only — no third-party packages
  required at runtime). Development target and configured GitHub Actions Python
  version: 3.14.
- Read access to the log files you want to analyse.
- The CLI is implemented with cross-platform Python APIs. It has been locally
  tested on Windows; GitHub Actions is configured for Python 3.14 on Ubuntu and
  Windows, but this guide does not claim a hosted result for the current source
  state. macOS and a complete operating-system support matrix are not
  established here.

## 2. Installation

The CLI has no third-party **runtime** dependencies. The package build declares
`setuptools>=68` as a build requirement in `pyproject.toml`; an installer may
need to make that build backend available. Two ways to run the CLI are:

1. **From a checkout (no project install):** from the project root, run the CLI via
   the interpreter's module switch. Because the project uses a `src/`
   layout, add `src` to `PYTHONPATH` when the package is not installed:

   ```bash
   # Linux / macOS (bash):
   PYTHONPATH=src python -m logsentinel --help

   # Windows (PowerShell):
   $env:PYTHONPATH = "$PWD\src"
   python -m logsentinel --help

   # Windows (cmd.exe):
   set PYTHONPATH=src && python -m logsentinel --help
   ```

2. **Install the CLI package from the repository root:**

   ```bash
   python -m pip install .
   ```

   This installs the package into the environment and provides the
   `logsentinel` console script (`logsentinel = "logsentinel.cli:main"`).
   On Windows the script is `logsentinel.exe` inside the environment's
   `Scripts` directory (activate the venv to put it on `PATH`).

## 3. Virtual environment setup

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (cmd.exe):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate
```

A venv is recommended for development even though LogSentinel has no
runtime dependencies (it keeps your global interpreter clean and isolates
dev tooling). Python 3.12 is the minimum version; 3.14 is the development
and CI target.

## 4. CLI invocation examples

```bash
# Analyse single files:
logsentinel samples/auth.log samples/firewall.log
# (without installation: PYTHONPATH=src python -m logsentinel ... )

# Analyse a directory (recursive discovery of non-hidden *.log / *.txt):
logsentinel samples/

# Write a JSON report:
logsentinel samples/ --json report.json

# Also write a human-readable text report to a file:
logsentinel samples/ --text report.txt

# Custom thresholds:
logsentinel samples/ --ssh-threshold 5 --ssh-window 120 \
    --portscan-threshold 12 --http-4xx-threshold 10

# Configuration file + strict mode + quiet:
logsentinel logs/ --config logsentinel.json --strict --quiet
```

**Expected results with the shipped samples:** a default run over `samples/`
produces three findings — one for each detection rule (SSH authentication
failures, port scanning, and HTTP 4xx activity) — and exits with code 1
because findings were detected. The malformed sample line is recorded as a
parsing error entry in the report.

Full option list (`--help` shows the same):

| Option | Meaning |
|--------|---------|
| `paths ...` | one or more log files and/or directories (required; zero paths is a usage error, exit code 2) |
| `--config PATH` | optional JSON configuration file (§6) |
| `--ssh-threshold N` | LS-RULE-001 failure threshold |
| `--ssh-window SECONDS` | LS-RULE-001 sliding window |
| `--portscan-threshold N` | LS-RULE-002 distinct-port threshold |
| `--http-4xx-threshold N` | LS-RULE-003 HTTP 4xx threshold |
| `--json PATH` | write the JSON report to PATH (atomically) |
| `--text PATH` | write the console-format report to PATH (atomically) |
| `--strict` | abort on the first recorded error (exit code 2) |
| `--quiet` | suppress the console report (report files are still written) |
| `--version` | print `logsentinel 0.1.0` and exit |
| `--help` | show help and exit |

## 5. Supported input paths

| Input | Behaviour |
|-------|-----------|
| File path | Parsed directly, regardless of extension (explicit files bypass the extension/hidden-name filters) |
| Directory | Recursively scanned for non-hidden `*.log` / `*.txt` files (case-insensitive), in sorted order |
| Multiple paths | Combined; de-duplicated by exact path string (first occurrence wins). Case variants, aliases, and symbolic links to the same file are **not** normalized and may be ingested separately |
| Missing/unreadable/invalid path | Recorded as a per-path error entry and skipped (FR-100); aborts in `--strict` mode |
| File > `max_file_mb` (512 MB) | Skipped with a recorded error entry (FR-102) |

Expected formats per file family: `auth.log` (syslog-style SSH),
`firewall.log` (key-value firewall dump), `access.log`
(Apache/Nginx combined). Lines matching no known event shape but carrying a
valid timestamp become `othersyslog` context events (never detected); lines
matching nothing at all are counted as malformed. Neither ever crashes the
run.

If discovery finds nothing at all, the tool prints a warning to stderr and
exits 0 (nothing analysed, no errors). If discovery records errors and no
file could be scanned, the run exits 2.

## 6. Configuration

Defaults (REQUIREMENTS.md FR-140):

```text
ssh_threshold        = 8     ssh_window_seconds  = 300
portscan_threshold   = 10    http_4xx_threshold  = 8
strict = False, max_line_length = 8192, max_file_mb = 512
```

Optional JSON config file (all seven keys are accepted; unknown keys are
rejected, FR-060):

```json
{
  "ssh_threshold": 8,
  "ssh_window_seconds": 300,
  "portscan_threshold": 10,
  "http_4xx_threshold": 8,
  "strict": false,
  "max_line_length": 8192,
  "max_file_mb": 512
}
```

**Precedence:** built-in defaults < JSON config file < CLI options; only
explicitly given (non-`None`) CLI values override. Invalid configuration
aborts with exit code 2 before any file is read.

## 7. Detection threshold examples

| Scenario | Recommended tuning |
|----------|--------------------|
| Small team, low traffic | `--ssh-threshold 5 --ssh-window 600` |
| Busy public web server (legit 404 noise) | `--http-4xx-threshold 25` |
| NAT gateway analysing egress firewall logs | `--portscan-threshold 30` |
| Strict triage pass on exported logs | `--ssh-threshold 3 --strict` |

Rule semantics, windows, and evidence behaviour: `DETECTION_RULES.md`.

## 8. Reading the report

### 8.1 Statistics — three different "dropped/duplicate" counters

The report statistics distinguish three separate phenomena; do not conflate
them:

| Counter | Meaning |
|---------|---------|
| `duplicates` (per file, summed) | Repeated events with the same exact event fingerprint `(kind, timestamp, raw_line)` **within one file**. These events are **retained** and counted individually (they are a subset of `events_parsed`); the counter is informational. |
| `cross_file_duplicates` (run level) | Occurrences removed by cross-file deduplication: events sharing the fingerprint `(kind, timestamp, raw_line)` are grouped by `source_file`; the retention cap is the **maximum occurrence count in any one source file**, the earliest-ingested occurrences are retained, and only the excess is removed and counted here. |
| `othersyslog_dropped` (per file, summed) | Well-formed-timestamp lines with unrecognized bodies beyond the retention cap (1000 per file). These are **not** staged as events at all — they are counted and dropped, and are neither duplicates nor malformed. |

A large `duplicates` value usually means repeated identical lines within one
file (rotation or forwarder overlap). A large `cross_file_duplicates` value
indicates overlapping event fingerprints across distinct source-file
identities; possible causes include overlapping log copies, rotation
overlap, or the same underlying file supplied through different path
strings (see §5).

### 8.2 JSON report

`--json report.json` writes a schema-stable report (FR-041/FR-042). The
example below is an **illustrative schema excerpt**, not a complete literal
report — it shows representative values for every field, including an
overflow object that appears only when the exact error total exceeds 100:

```json
{
  "report_version": 1,
  "generated_at": "2026-11-21T10:00:00+00:00",
  "config_used": {"ssh_threshold": 8, "ssh_window_seconds": 300,
                  "portscan_threshold": 10, "http_4xx_threshold": 8,
                  "strict": false, "max_line_length": 8192,
                  "max_file_mb": 512},
  "statistics": {"files_scanned": 3, "lines_read": 1204,
                 "events_parsed": 981, "malformed": 18, "duplicates": 6,
                 "othersyslog": 12, "othersyslog_dropped": 0,
                 "cross_file_duplicates": 0, "findings": 1},
  "findings": [{"rule_id": "LS-RULE-001", "severity": "high",
                "src_ip": "192.0.2.7", "first_seen": 1763712000,
                "last_seen": 1763712150,
                "evidence": ["raw log line ..."],
                "summary": {"...": "..."}}],
  "errors": [{"source_file": "missing.log", "line_number": null,
              "reason": "...", "kind": "input"}],
  "errors_overflow": {"shown": 100, "total": 143}
}
```

- `findings` are ordered by rule ID, then severity, then source IP.
- `errors` contains at most the first 100 error entries; `errors_overflow`
  appears **only** when the exact run total exceeds 100 and reports
  `{"shown": 100, "total": N}`.
- Deterministic except `generated_at` (FR-042); both report files are
  written atomically (temp file in the target directory, then replace —
  FR-132).
- Consumable by `jq`, CI scripts, and simple dashboards.
- The `generated_at` timestamp is captured once at the start of the run;
  analysis itself never depends on wall-clock time (AR-010).

### 8.3 Console report

Printed to stdout unless `--quiet` is active; the same format is written by
`--text PATH`. It lists findings grouped by rule with severity, first/last
seen, summary counts, and redacted evidence excerpts, followed by the
statistics block. When errors exceed 100 it appends e.g.
`errors: 100 of 143 shown (43 omitted)`.

### 8.4 Redaction and evidence limits (best-effort)

Evidence excerpts and error text are capped at 256 characters (with a
truncation marker). Before truncation, credential-bearing key/value pairs
whose key contains `password`, `passwd`, `pwd`, `token`, `api_key`,
`secret`, `authorization`, `access_key`/`access-key`,
`private_key`/`private-key`, `session_key`/`session-key`, `credential`,
`credentials`, `sess`/`session`/`sessionid`/`session_id`, `passphrase`,
`pass_word`/`pass-word`, or `signature` (case-insensitive,
hyphen/underscore separators and separator-free forms recognized) are
replaced with a fixed marker. Credential-bearing headers — `Authorization`,
`Cookie`, `Set-Cookie`, and `Proxy-Authentication` (hyphen and underscore
forms) — have their entire remainder replaced with the marker, since
header values are opaque (scheme plus credentials or session identifiers).
**This redaction is best-effort, not universal secret detection:**
secrets in formats the matcher does not recognize (e.g. bare tokens without
a `key=value` shape, bare Basic-auth/base64 credentials outside a
recognized header, unkeyed JWT material, generic `key` or `pin` field
names), unknown key names, unusual separators, multiline
material, and other unrecognized encodings are not detected — the length
cap is the backstop. The vocabulary is deliberately narrow: ordinary fields
such as `client_id`, `keyboard`, or `monkey` are never redacted. Do not
feed secret-bearing logs to any tool you do not trust.

## 9. Exit codes

| Code | Meaning |
|------|---------|
| 0 | Run completed; no findings |
| 1 | Run completed; findings present (grep-able signal for CI) |
| 2 | Usage/configuration/input-path/report error; strict-mode abort; also input errors with zero files scanned |
| 3 | Unexpected runtime error (short diagnostic on stderr; no partial report) |

CI gating example (bash):

```bash
logsentinel logs/ --json r.json --quiet
code=$?
if [ "$code" -eq 0 ] || [ "$code" -eq 1 ]; then
  echo "run completed (exit $code)"; else
  echo "run failed (exit $code)"; exit "$code"; fi
```

## 10. Normal mode vs strict mode

- **Normal mode (default):** recoverable input and parsing errors do not
  stop normal-mode processing; unexpected runtime failures can still
  terminate the run. Recoverable problems — missing/unreadable
  paths, oversized files, undecodable-for-UTF-8 content, malformed lines,
  files that vanish between discovery and parsing — are recorded as error
  entries and the run continues.
- **Strict mode (`--strict`):** the first recorded error aborts the run
  with exit code 2. Discovery errors are checked before any parsing; a
  parse error aborts immediately after the file that produced it, and later
  files are not parsed. Report-write failures always exit 2 in both modes.
- Encoding fallback in both modes: files are read as UTF-8; if decoding
  fails, the partial attempt is discarded and the file is retried from the
  beginning as Latin-1, and a warning error entry records that the fallback
  was used. Binary files are not a supported log format; because Latin-1
  can decode arbitrary byte sequences, binary input may instead produce
  malformed lines or `othersyslog` events rather than a decode failure.

## 11. Memory and scalability (NFR-004)

LogSentinel streams every file line by line: events and errors are staged
into a temporary SQLite database as they are parsed, and no full-file or
full-run list of parsed events is ever built. Detection aggregates per
source IP. **NFR-004 does not guarantee constant memory usage:** per-IP
detector state and evidence grow with the event volume attributed to each
source IP (HTTP 4xx evidence is intentionally uncapped), and the findings
list is materialized for rendering. Very lopsided traffic (one IP
generating millions of events) will use proportionally more memory.

## 12. Troubleshooting

| Symptom | Likely cause / action |
|---------|----------------------|
| Exit 2, "no input paths" | Supply at least one file or directory (FR-072) |
| Exit 2, "unknown config key" | Fix the JSON config file (FR-060) |
| Exit 2 with input errors and `files_scanned: 0` | All paths failed discovery (missing, unreadable, oversized); check paths and permissions |
| Exit 2, report not written | Check write permission/target validity; write failures raise `ReportError` and exit 2 in both modes |
| Everything shows as malformed | Check whether the input lines match the supported event formats (§5) |
| No findings although you expect some | Thresholds too high — lower them; or events fell outside the SSH window |
| `duplicates` counter is large | Repeated identical lines within one file (rotation/forwarder overlap) — preserved as events, see §8.1 |
| `cross_file_duplicates` counter is large | Overlapping event fingerprints across different source files — overlapping log copies, rotation overlap, or the same underlying file reached through different path strings (aliases/symlinks are not normalized, §5; repeated identical path strings are already removed during discovery, §5) |
| Lines missing from findings | Check `othersyslog_dropped`: unrecognized-body lines beyond 1000 per file are dropped from staging |
| `ModuleNotFoundError: logsentinel` | Run from the project root with `PYTHONPATH=src`, or `pip install .` (§2) |
| Windows console shows mangled non-ASCII output | The console report is UTF-8 text; a Windows codepage terminal may need `chcp 65001` or `PYTHONIOENCODING=utf-8` |

## 13. Behaviour notes

- Findings never assert malicious intent; each finding carries evidence
  derived from the original log lines, subject to report-level redaction
  (best-effort credential masking, §8.4) and the 256-character truncation
  cap, and points back to the original file for human review.
- The temporary SQLite staging database is created in the system temporary
  directory and removed when the run ends; it is never a project artifact.
- All timestamps are handled in UTC; naive log timestamps are interpreted
  as UTC regardless of the analysis host's timezone.
