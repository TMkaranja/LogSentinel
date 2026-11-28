# LogSentinel

**LogSentinel Phase 1** provides a defensive, file-based log analysis CLI and an
optional PySide6 desktop GUI for offline review of SSH, firewall, and web access
logs. A Windows onedir GUI candidate exists locally; it is not an installer or a
claim of broad Windows support or production readiness, and it remains **HOLD —
NOT CLEARED FOR DISTRIBUTION**.

Both interfaces read log files you supply, extract structured security events,
group activity by source IP address, apply three configurable detection rules,
and produce reports. LogSentinel does not acquire logs from other systems. Findings
are review leads for a human analyst, not assertions of malicious intent.

For installation, first launch, the GUI pages, privacy limitations, and complete
Phase 1 user instructions, see the [LogSentinel User Guide](docs/USER_GUIDE.md).
For detailed CLI commands and configuration, see the
[CLI Usage Guide](docs/USAGE.md).

**Release licensing review:** the inspected Windows GUI candidate is **not cleared
for distribution**. Third-party notice and distribution-status materials prepared for review are
incomplete proposals, not final recipient notices or legal clearance.

Legitimate monitoring tools, scanners, and broken integrations can produce the
same patterns, so review findings in context rather than treating them as proof.

- CLI requires Python **3.12 or newer** and has no third-party runtime
  dependencies; the optional GUI source requires PySide6, which is not declared
  in `pyproject.toml`.
- Batch analysis of files · streaming pipeline · SQLite-staged with multiplicity-aware dedup
- Console and JSON reports · deterministic output · atomic file writes

## Detection rules

| Rule | Detects | Default | Window | Severity |
|------|---------|---------|--------|----------|
| `LS-RULE-001` | SSH authentication failures per source IP | ≥ 8 failures | sliding 300 s, half-open `(t−w, t]` | high |
| `LS-RULE-002` | Distinct destination ports per source IP | ≥ 10 ports | whole run | medium |
| `LS-RULE-003` | HTTP client errors (400–499) per source IP | ≥ 8 responses | whole run | medium |

All three thresholds and the SSH window are configurable via CLI options or a JSON
configuration file (precedence: CLI > config file > built-in defaults). Full logic,
worked examples, false-positive guidance, and edge cases:
[`docs/DETECTION_RULES.md`](docs/DETECTION_RULES.md).

## How it works

One streaming run, with no full-file or full-run buffering of parsed events:

1. **Discovery** — CLI paths are resolved deterministically; directories are
   recursed for non-hidden `*.log`/`*.txt` files; explicit files bypass the
   extension filter; paths are de-duplicated by exact string; oversized files
   (default cap 512 MB) are skipped with a recorded error.
2. **Streaming parse** — each file is read line by line (`stream_parse_file`);
   SSH/firewall/Apache-combined lines become validated, frozen dataclass events;
   unrecognized lines with valid timestamps become context-only `othersyslog`
   events; anything unparseable is counted as malformed.
3. **SQLite staging** — events, errors, and per-file statistics are staged into a
   temporary SQLite database (system temp dir, removed when the run ends), one
   transaction per file attempt. UTF-8 decoding failure rolls back the attempt
   and retries the file as Latin-1.
4. **Cross-file deduplication** — a single SQL pass collapses re-ingested
   duplicates across files, multiplicity-aware: per fingerprint
   `(kind, timestamp, raw_line)`, occurrences are capped at the maximum
   single-file count, earliest-ingested occurrences are retained, and the excess
   is reported as `cross_file_duplicates`. Identical repeats *within* one file
   are preserved and counted individually.
5. **Incremental detection** — detectors consume staged events in ingestion
   order via `observe()`, aggregating per source IP; no complete event list is
   ever built. Memory grows with per-IP activity — constant memory is not
   claimed.
6. **Reporting** — all requested reports are rendered before any file is
   written; JSON and text reports are written atomically.

**Error behaviour:** in normal mode, recoverable input and parsing errors are
recorded as error entries and the run continues. In `--strict` mode, the first
recorded error aborts the run with exit code 2. Unexpected runtime failures can
still terminate execution (exit code 3, no partial report) — malformed log lines
do not make a run crash-proof against software faults.

**Exit codes:** `0` clean · `1` findings · `2` usage/config/input/report errors
or strict-mode abort · `3` unexpected failure.

## Requirements & installation

- Requires Python **3.12 or newer** (`requires-python = ">=3.12"`). The CLI has
  no third-party runtime dependencies. Local verification for this source state
  used CPython 3.14.10 on Windows. The GitHub Actions workflow is configured for
  Python 3.14 on both Ubuntu and Windows for pushes and pull requests; a hosted
  run for the current source state is not claimed here. macOS has not been
  validated.

```bash
# from a checkout, without installing (Linux/macOS bash):
PYTHONPATH=src python -m logsentinel --help
```

```powershell
# Windows PowerShell:
$env:PYTHONPATH = "$PWD\src"
python -m logsentinel --help
```

```bash
# or install the CLI package and console script:
python -m pip install .
```

The CLI has no third-party runtime dependencies. Building/installing the project
from `pyproject.toml` uses its declared `setuptools>=68` build requirement; this
is separate from the installed CLI's runtime dependencies. The optional GUI
source requires PySide6 in the Python environment and is not installed by
`pip install .`.

## Quick start

```bash
# analyze the shipped synthetic samples (directory discovery):
logsentinel samples/ --json report.json

# explicit files:
logsentinel samples/auth.log samples/access.log samples/firewall.log --json report.json

# tune thresholds:
logsentinel samples/ --ssh-threshold 5 --ssh-window 120 \
    --portscan-threshold 12 --http-4xx-threshold 10

# strict mode (abort on first recorded error) and quiet mode:
logsentinel logs/ --config logsentinel.json --strict --quiet
```

## Sample dataset & expected results

The three files under [`samples/`](samples/) are synthetic demonstrations:

- All **valid** IP addresses in the samples belong to RFC 5737 documentation
  ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) — no real hosts.
- `samples/auth.log` additionally contains one **intentionally invalid** address
  (`999.1.1.1`). It is malformed-input **test data** demonstrating how invalid
  lines are counted and reported — it is not a real or routable host.

| File | Demonstrates |
|------|--------------|
| `samples/auth.log` | 8 SSH failures from one IP inside 300 s → `LS-RULE-001` (plus sub-threshold and window-boundary cases, a success context line, an `othersyslog` line, and the intentionally invalid address line) |
| `samples/firewall.log` | 12 distinct destination ports from one IP → `LS-RULE-002` (plus a byte-identical intra-file repeat and normal ACCEPT traffic) |
| `samples/access.log` | 10 HTTP 4xx responses from one IP → `LS-RULE-003` (plus 2xx/5xx lines the rule ignores) |

A default run exits with **code 1** and reports **exactly three findings**:

```
LS-RULE-001  high    192.0.2.7     failed_count=8, distinct_usernames=2, successful_followups=1
LS-RULE-002  medium  198.51.100.23 distinct_ports=12, protocols=['TCP']
LS-RULE-003  medium  203.0.113.50  http_4xx_count=10, status_histogram={'401': 2, '403': 2, '404': 6}
```

Statistics: `files_scanned=3, lines_read=44, events_parsed=43, malformed=1,
duplicates=1, othersyslog=2, othersyslog_dropped=0, cross_file_duplicates=0`.
The malformed line is recorded as a parse error entry in the report.

## Report information

- **JSON** (`--json PATH`): stable schema (`report_version`, `generated_at`,
  `config_used`, `statistics`, `findings[]`, `errors[]`). When the run produces
  more than 100 error entries, the report additionally contains an
  `errors_overflow` object (`{"shown": 100, "total": N}`). Deterministic except
  `generated_at`. Findings include rule ID, severity, source IP, first/last
  seen, summary counters, and evidence excerpts (capped at 256 characters).
- **Text** (`--text PATH`) and **console** (unless `--quiet`): findings grouped
  by rule, then severity, then source IP, followed by the statistics block.
- **Redaction is best-effort:** credential-shaped key/value pairs (password,
  token, api key, secret, authorization) are replaced before truncation, but
  redaction cannot catch every secret format, and the 256-character length cap
  is **not** a guarantee against secret leakage. Do not feed secret-bearing
  logs to tools you do not trust.

## Testing

```bash
python -m unittest discover
```

The full standard-library `unittest` suite was run locally from the repository
root with CPython 3.14.10 on Windows: **556 tests ran; 546 passed and 10 were
skipped**. Focused GUI discovery ran **140 tests; all 140 passed**. The suite
includes a 105,335-line end-to-end streaming test and a `tracemalloc` regression
guard; the latter is not a general memory-usage guarantee. GitHub Actions
(`.github/workflows/tests.yml`) is configured to run `python -m unittest discover`
on pushes and pull requests using Python 3.14 on `ubuntu-latest` and
`windows-latest`. These are local results, not hosted CI results; no matching
hosted Actions run for the audited exact HEAD was found.

## Project structure

The proposed source scope is CLI-plus-GUI and contains application code, tests,
synthetic samples, and product/developer documentation. The GUI artwork remains
on HOLD pending item-specific provenance and rights evidence; the GUI packaging
recipes remain on HOLD pending review and separately authorized validation.
Thus the complete GUI-inclusive source proposal is not ready to stage. Local
virtual environments, `build/`, `dist/`, `release/`, and generated test/report
outputs are not source-publication contents. The Windows executable and ZIP
remain on distribution hold and are not approved as release assets.

```
LogSentinel/
├── src/logsentinel/          CLI and shared analysis code
│   └── gui/                  optional PySide6 GUI source and assets
├── tests/                    CLI, analysis, storage, and GUI tests
├── samples/                  synthetic RFC 5737 demonstration logs
├── docs/                     user guide, CLI/rule/architecture references,
│                              requirements, historical validation, security audit
├── packaging/                GUI PyInstaller recipes/entry point — HOLD pending review
├── .github/workflows/        configured Ubuntu and Windows test jobs
├── LICENSE                   LogSentinel project license
├── PROJECTMAP.md             source and project map
├── pyproject.toml            Python package metadata and CLI entry point
└── .gitignore
```

The Phase 1 product/developer documentation is listed below. Separate
publication-review working records are not product documentation and do not
grant publication or distribution approval. Design rationale is in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) (AR-001…AR-012).

## Limitations & security considerations

- **Analysis only.** No real-time tailing, no alerting, no blocking, no SIEM
  integration, no log acquisition. Out of scope for v1: IPv6, Windows Event
  Log, cloud logs, ML scoring.
- **Evidence, not verdicts.** Every detector reports a statistical pattern;
  human review is required.
- **IPv4 only** for source/destination addresses.
- **Input-path dedup is exact-string:** aliases, case variants, or symlinks to
  the same file are not detected and may be analyzed twice (content dedup still
  collapses identical lines across the copies).
- **Encoding:** files are read as UTF-8 with a full Latin-1 retry; the retry
  reopens the file, so a file changing mid-run could yield mixed content.
  Binary files are not a supported log format.
- **Memory is not bounded:** per-IP aggregation and retained evidence grow with
  the volume attributed to each source IP (HTTP 4xx evidence is intentionally
  uncapped).
- **Files are opened read-only**; the tool writes only to report paths you
  specify (atomically) and to a temporary staging database it removes itself.
  No network connections, no dynamic code execution, no telemetry.
- **Redaction is not complete.** See the best-effort caveat under *Report
  information*; full secret-protection guarantees are not claimed.

## Documentation

- [`PROJECTMAP.md`](PROJECTMAP.md) — current CLI/GUI source map and publication/distribution hold boundaries
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — Phase 1 CLI and Windows GUI release-candidate guide, including workflows, troubleshooting, data handling, and limitations
- [`docs/USAGE.md`](docs/USAGE.md) — CLI installation, commands, configuration, and report reference
- [`docs/DETECTION_RULES.md`](docs/DETECTION_RULES.md) — implemented rule behavior, examples, false positives, and edge cases
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — architecture and design decisions
- [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md) — requirements specification
- [`docs/PHASE3_VALIDATION.md`](docs/PHASE3_VALIDATION.md) — historical design-validation record, not current release approval
- [`docs/SECURITY_AUDIT.md`](docs/SECURITY_AUDIT.md) — security review record; it documents open, best-effort redaction limitations and is not a security guarantee

## License

LogSentinel is licensed under the MIT License. See [LICENSE](LICENSE) for the full license text.
