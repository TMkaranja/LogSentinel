# LogSentinel — Project Map

- **Version:** 0.1.0 | **Status:** Implementation and validation complete;
  documentation and release preparation underway.
- **Language:** Python (minimum 3.12 declared; development and testing performed on
  CPython 3.14.10) | **Runtime dependencies:** none (standard library only)

## 1. Project Description

LogSentinel is a defensive, file-based cybersecurity log analysis CLI. It reads supplied
log files (SSH auth, firewall, HTTP access), parses them into structured events, groups
activity by source IP address, applies three configurable detection rules, and reports
findings to the console and as JSON. It runs fully offline and performs no log
acquisition — a passive audit aid whose findings are review leads, never proof of intent.

## 2. Directory Tree (verified current)

```text
LogSentinel/
├── .github/workflows/tests.yml   CI: full unittest suite on push/PR (configured)
├── .gitignore                    populated (caches, venvs, reports, audit-*, OS files)
├── LICENSE                       MIT License, Copyright (c) 2026 Moses Karanja Thuo
├── PROJECTMAP.md                 this document
├── README.md                     current user-facing overview
├── pyproject.toml                packaging: logsentinel 0.1.0, >=3.12, deps=[],
│                                 console script logsentinel = "logsentinel.cli:main"
├── docs/
│   ├── ARCHITECTURE.md           pipeline design + AR-001..AR-012 decisions
│   ├── DETECTION_RULES.md        full rule specifications (authoritative)
│   ├── PHASE3_VALIDATION.md      validation + remediation record, incl. §16 reconciliation
│   ├── REQUIREMENTS.md           FR/NFR requirements + acceptance criteria
│   ├── SECURITY_AUDIT.md         security audit and remediation record (R1–R5)
│   └── USAGE.md                  user guide (sample-verified)
├── samples/                      synthetic demo logs, RFC 5737 documentation IPs only
│   ├── auth.log  firewall.log  access.log
├── src/logsentinel/              application package (11 modules)
│   ├── __init__.py  __main__.py  cli.py  config.py  inputs.py  parsers.py
│   ├── events.py  detectors.py  storage.py  report.py  exceptions.py
└── tests/                        unittest suite (8 test modules)
    ├── __init__.py  test_cli.py  test_config.py  test_detectors.py  test_events.py
    ├── test_inputs.py  test_parsers.py  test_report.py  test_storage.py
```

Byte-code caches (`__pycache__/`) are build artifacts, not project sources, and are
Git-ignored. Demonstration reports (`report.json`, `report.txt`,
`report-explicit.json`) and the 20 `audit-*` Phase-4-era artifacts are currently
Git-ignored and preserved locally; their deletion remains an open decision.

## 3. Module Responsibilities (verified)

| Module | Actual responsibility | Streaming vs. compatibility |
|--------|----------------------|------------------------------|
| `__init__.py` | Package marker; `__version__ = "0.1.0"`; review-lead framing | — |
| `__main__.py` | `python -m logsentinel` entry point; delegates to `cli.main()` | — |
| `cli.py` | argparse CLI; streaming orchestration: discovery → per-file streaming parse → SQLite staging (per-file transactions) → SQL cross-file dedup → detectors via `observe()`/`results()` → render-all-before-write → atomic writes → exit codes 0/1/2/3; sole wall-clock reader (AR-010); strict-mode aborts; unexpected-exception boundary (exit 3) | Production path only |
| `config.py` | Sole owner of defaults, validation, precedence: 7 keys (`ssh_threshold`, `ssh_window_seconds`, `portscan_threshold`, `http_4xx_threshold`, `strict`, `max_line_length`, `max_file_mb`); frozen `AppConfig`; `ConfigError` (AR-008, FR-142) | — |
| `inputs.py` | `discover_inputs(paths, *, max_file_mb) -> DiscoverResult(files, errors)`: stat-based predicates, directory recursion (non-hidden `*.log`/`*.txt`), explicit-file filter bypass, exact-string path de-duplication, size caps; errors returned as data | Production path |
| `parsers.py` | `stream_parse_file()`: line-by-line streaming, tagged items (`event`/`error`/`rollback`/`stats`), `duplicate_check` seam (SQLite-backed in production), UTF-8 attempt → rollback → Latin-1 retry, othersyslog retention cap, per-file statistics | Streaming = production; `parse_file()` = compatibility wrapper with identical semantics |
| `events.py` | Frozen slotted dataclasses: `SecurityEvent` base + `SSHAuthEvent` (`authok`/`authfail`), `FirewallEvent` (`fwconn`), `HTTPRequestEvent` (`web`), `SyslogEvent` (`othersyslog`); `ErrorEntry` (M6: `reason` sanitized at construction, best-effort — the single sanitizer implementation lives in this leaf module and is re-exported by `report.py`), `FileStats`, `Finding`; `fingerprint`; batch utilities `dedup_cross_file`/`events_by_src_ip`; stdlib-only leaf | Batch utilities = compatibility; production dedup lives in storage |
| `detectors.py` | LS-RULE-001/002/003 via incremental `observe(event)`/`results()`/`_reset()` with per-IP aggregation; batch `detect(events)` and `run_all_detectors(events, config)` | Incremental = production; batch = compatibility (same algorithm, identical findings) |
| `storage.py` | `RunStorage`: temporary SQLite database (system temp dir, removed at run end); events/errors/file_stats tables + two indexes; explicit `begin()`/`commit()`/`rollback()` per file attempt; `fingerprint_seen()` digest-equality intra-file duplicate check inside the transaction (M1: events are stored as sanitized `evidence_line` plus per-run keyed HMAC `fp_digest` — no raw-line column or raw-line index; the HMAC key lives only in memory for the instance lifetime); `dedup_cross_file()` SQL (multiplicity cap, earliest retained, excess counted); `error_summary()` (first 100 + exact total); `statistics_sums()`; exception-safe lifecycle with observable `cleanup_errors` | Production path only (FR-110/NFR-004) |
| `report.py` | `render_console`/`render_json` (keyword-only `errors`/`errors_total`; `errors_overflow {"shown", "total"}` beyond 100 errors), best-effort credential redaction before 256-character truncation, atomic `write_report` (FR-132/154) | Both report paths production |
| `exceptions.py` | `LogSentinelError` hierarchy: `ConfigError`, `InputPathError`, `ParseError`, `ReportError` (FR-150) | — |

Correction of an earlier claim: `inputs.py` does **not** raise `InputPathError` — it
returns per-path error entries as data, and `cli.py` constructs the strict-mode abort
from the first returned error.

## 4. Architecture (actual pipeline)

One streaming run. The production pipeline does not materialize a complete
parsed-event collection in memory:

1. **Input discovery** — deterministic resolution of CLI paths into an ordered,
   de-duplicated file list (errors as data).
2. **Per-file streaming parsing** — `stream_parse_file()` reads each file line by
   line and yields tagged items; the UTF-8 attempt runs inside its own transaction.
3. **SQLite staging and per-file transactions** — events, errors, and per-file
   statistics are staged as they stream; on decode failure the attempt is rolled
   back and the file is retried as Latin-1 from the beginning; the successful
   attempt (with its warning entry and statistics) is committed.
4. **Cross-file SQL deduplication** — one SQL statement applies the approved
   multiplicity rule per logical fingerprint `(kind, timestamp, raw_line)`, persisted
   as its per-run keyed HMAC-SHA256 digest `(kind, timestamp, fp_digest)` (M1): per-source-file
   occurrence counts, retention cap = maximum single-file count, earliest-ingested
   occurrences retained, excess removed and counted as `cross_file_duplicates`.
   Intra-file identical repeats are preserved and count individually.
5. **Incremental detection** — staged events are streamed to the three detectors
   in ingestion order via `observe()`; each detector aggregates per source IP;
   no complete event list is ever constructed.
6. **Statistics, rendering, and atomic writing** — run statistics are SQL sums over
   staged per-file rows; every requested report is rendered in memory before any
   file is written; JSON/text reports are written atomically; exit code encodes
   the outcome (0/1/2/3).

Import relationships (verified against source): `cli` imports `config`, `inputs`,
`parsers`, `storage`, `events`, `detectors`, `report`, `exceptions`; `inputs` imports
`events`; `parsers` imports `events` and `exceptions`; `storage` imports `events`;
`detectors` imports `events`; `report` imports `events` and `exceptions`. The graph is
acyclic and one-way. Full details: `docs/ARCHITECTURE.md` §3–§5, §14.

## 5. Event Model Summary

Canonical kind vocabulary: **`authok`, `authfail`, `fwconn`, `web`, `othersyslog`**.

| Type | Role |
|------|------|
| `SSHAuthEvent` | `authok`/`authfail`; timestamp (epoch s UTC), src_ip (IPv4), username, success (bool) |
| `FirewallEvent` | `fwconn`; timestamp, src_ip, dst_ip, dst_port (1–65535), protocol |
| `HTTPRequestEvent` | `web`; timestamp, src_ip, method, path, status_code (100–599) |
| `SyslogEvent` | `othersyslog`: well-formed timestamp header, unrecognized body; context only, never detected; retained up to the per-file cap (1000), excess counted as `othersyslog_dropped` |
| `ErrorEntry` | Recoverable problem record: `source_file`, `line_number` (nullable), `reason` (sanitized at construction — M6, best-effort), `kind` (`config\|input\|parse\|report`) |
| `FileStats` | Per-file: `lines_read`, `events_parsed`, `malformed`, `duplicates`, `othersyslog`, `othersyslog_dropped` |
| `Finding` | Rule result: `rule_id`, `severity`, `src_ip`, `first_seen`/`last_seen`, evidence tuple, summary counters; at most one per (rule, src_ip) per run |

All are frozen slotted dataclasses (AR-001). **Deduplication:** the logical
fingerprints are `(kind, timestamp, raw_line)`; identical repeats within one file are
preserved and
counted individually (per-file `duplicates` counter); cross-file re-ingestion
collapses multiplicity-aware (cap = maximum single-file count, earliest ingested
retained, excess → run-level `cross_file_duplicates`). In SQLite (M1) the persisted
representation of that identity is the per-run keyed HMAC-SHA256 digest
`(kind, timestamp, fp_digest)`; `evidence_line` is stored sanitized and no raw-line
column or index exists. Input-path de-duplication
removes duplicate path strings only (FR-004).

## 6. Detection Rules and Defaults

| Rule | Trigger | Default | Window | Severity |
|------|---------|---------|--------|----------|
| LS-RULE-001 | failed SSH auths per source IP | 8 | 300 s sliding, half-open `(t-w, t]` | high |
| LS-RULE-002 | distinct destination ports per source IP | 10 | none (whole run) | medium |
| LS-RULE-003 | HTTP 400–499 responses per source IP | 8 | none (whole run) | medium |

Implementation notes: Rule 1 aggregates all qualifying windows into one merged union
(`failed_count` = union size); successful authentications from the same source IP
never count toward or reset the window and are attached run-wide as
`successful_followups` plus evidence context. Rule 3 retains every qualifying 4xx raw
line as detection-time evidence in memory (uncapped; report-level truncation happens
later; evidence staged in SQLite is sanitized — M1).
Streaming and batch detector paths share one algorithm, so their findings are
identical by construction. All thresholds and the SSH window are configurable;
precedence CLI > JSON config file > defaults (AR-008). Full logic, examples, false
positives, edge cases: `docs/DETECTION_RULES.md` (authoritative).

## 7. Technical Constraints

- Python ≥3.12 declared (`pyproject.toml`); local development and full-suite testing
  performed on CPython 3.14.10 (Windows). Python 3.12 execution has not been verified;
  macOS compatibility has not been verified.
- CI is configured for Ubuntu and Python 3.14 (`.github/workflows/tests.yml`); the
  first hosted run (`45025411430`) succeeded on push to `main`.
- Standard-library-only runtime; `unittest` for tests.
- Per-IP detection state and some evidence collections can grow with input volume;
  constant-memory operation is **not** claimed. The memory test measures **traced
  Python allocations** (tracemalloc), not total process RAM.
- Input-path de-duplication uses exact path strings, not filesystem identity
  (aliases/symlinks are not normalized).
- Credential redaction in reports is best-effort, not guaranteed secret protection
  (FR-162/NFR-009 remain outstanding in part).
- Out of scope for v1: ML/anomaly scoring, GUI/TUI/web, real-time streaming or
  tailing, SIEM integration, Windows Event Log, cloud log integrations, GeoIP,
  IPv6, active response (blocking/alerting), any log acquisition.

## 8. Development Phases

> **Historical record:** the table below is the *original planned* sequence from the
> Phase 2 specification. It does not reflect current implementation status — see §9.

| Phase | Scope (original plan) | Status at planning time |
|-------|-----------------------|--------------------------|
| 1 | Scaffolding (empty modules, tests, samples, docs, CI, license) | Complete |
| 2 | Requirements & technical specification (5 documents) | Complete (this document set) |
| 3 | Event model + parsing (`events.py`, `parsers.py`) + tests | Planned |
| 4 | Detection engines (`detectors.py`) + tests | Planned |
| 5 | Configuration, inputs, CLI wiring (`config.py`, `inputs.py`, `cli.py`) + tests | Planned |
| 6 | Reporting (`report.py`) + JSON schema + tests | Planned |
| 7 | Synthetic samples, README, CI green, packaging metadata | Planned |

## 9. Current Implementation Status (verified)

- **Implementation:** complete through the Phase 5 streaming architecture — all 11
  modules implemented (2,708 lines of application code), including `storage.py`
  (SQLite staging) and the streaming CLI, plus the compatibility interfaces.
- **Tests:** the canonical command
  `python -W error::ResourceWarning -m unittest discover` reports **372 tests, OK,
  9 skipped** (platform-gated Windows symlink/permission cases) on CPython 3.14.10.
- **Scale validation:** a 105,335-line, three-file streaming test asserts exact
  statistics and findings and proves the compatibility parser is not used at scale.
- **Memory validation:** the streaming test verifies a traced Python memory peak
  below 30 MB (tracemalloc) — a regression bound on Python allocations, not a
  measurement of total process RAM and not a constant-memory claim.
- **Performance:** an authorized one-time measurement of the shipped samples run
  completed end-to-end in 0.396 s (requirement: under 5 s; NFR-010 verified).
- **Samples:** three populated synthetic files (44 lines total) demonstrating all
  three rules plus sub-threshold, boundary, intra-file-duplicate, `othersyslog`,
  and malformed-line behaviour — RFC 5737 documentation addresses only (FR-173
  verified), including one intentionally invalid address (`999.1.1.1`) as
  malformed-input test data.
- **Release documents:** README current (verified facts, MIT-linked); MIT LICENSE
  populated; `.gitignore` populated (caches, venvs, reports, `audit-*`, OS files).
- **CI:** `.github/workflows/tests.yml` authored (push/PR triggers, Ubuntu,
  Python 3.14, `python -m unittest discover`); first hosted run `45025411430`
  succeeded on push to `main`.
- **Git:** initialized with remote `origin` (GitHub); commits through `a59f3f9` are
  published to `origin/main`; M6 (`58d1806`), M1 (`37d19de`), and the two
  security-audit and architecture documentation commits are local, pending push.
- **Outstanding requirement gap:** FR-162/NFR-009 secret protection — report
  redaction is best-effort and cannot guarantee detection of every secret format;
  the requirement is not fully satisfied and must not be described as such.

Distinguish: the facts above are verified from current files and recorded validation
runs; publication of the four local commits is a future action, not completed work.

## 10. Future Scope (post-v1, not committed)

- Windowed variants of LS-RULE-002/003 (rate-limit aware).
- User-agent field parsing for HTTP events; IPv6 support.
- Additional rules (successful-login-after-brute-force correlation, 5xx anomaly).
- Optional SARIF export for security dashboards.
- A small detector registry if the rule count grows (AR-011 revisit).

## 11. Phase 3 Corrections Addendum

> **Historical record:** this section documents earlier project states. It must not
> be read as current implementation status — see §9.

Applied during the Phase 3 technical design validation (docs/PHASE3_VALIDATION.md §13).

- **Event model:** adds `SyslogEvent` (kind `othersyslog`) — well-formed header,
  unrecognized body; context only, never detected. Canonical kind vocabulary:
  `authok`, `authfail`, `fwconn`, `web`, `othersyslog`.
- **Dedup (AR-005, final: Phase 3 remediation):** content-addressed fingerprint
  `(kind, canonical timestamp, normalized raw line)`; scoped to **cross-file
  re-ingestion** — identical lines from different input files collapse;
  byte-identical lines within one file are preserved as legitimate events.
- **Rule corrections:** Rule 1 duplicate-handling and the "same second x10" edge case
  corrected; `successful_followups` scoped to the whole run. Authoritative record:
  docs/PHASE3_VALIDATION.md §6 and §13.

## 12. Phase 4 Implementation Status Addendum

> **Historical record:** this section documents an earlier project state (the
> event-model and parsing phase). It must not be read as current implementation
> status — see §9. Historical test counts and module descriptions are preserved
> verbatim below.

Implementation status of the event model and parsing layer (work already present
in the repository; authored in a separate implementation step in response to the
user's separate Phase 4 authorization instruction - it is not a product of the
Phase 3 validation or remediation, which are documentation-only):

- `src/logsentinel/exceptions.py` - LogSentinelError hierarchy (FR-150).
- `src/logsentinel/events.py` - full event model: SecurityEvent base,
  SSHAuthEvent/FirewallEvent/HTTPRequestEvent/SyslogEvent, Finding, FileStats,
  ErrorEntry, content-addressed `fingerprint`, `dedup_events`, `events_by_src_ip`.
- `src/logsentinel/parsers.py` - `parse_file(path, reference_now, ...)` with
  syslog/ISO/Apache timestamp handling, SSH/firewall/HTTP classifiers,
  othersyslog pass-through with retention cap, UTF-8/Latin-1 fallback.
- `tests/test_events.py`, `tests/test_parsers.py` - 46 tests, all passing
  (`python -m unittest discover`).
- Note: `parse_file` accepts a path (not `LogFile`) so `parsers` never imports
  `inputs` (dependency map); Phase 5 will pass `LogFile.path`.
- Still empty (Phase 5-7): cli.py, config.py, inputs.py, detectors.py, report.py,
  __init__.py, __main__.py, remaining tests, samples, CI workflow.

## 13. Subsequent Implementation and Release-Readiness Record

Evidence-based continuation after §12 (Phases 4.2–4.6, Phase 5, and Phase 6
documentation/release preparation). Authoritative detail lives in the documents
referenced here; this section is a map, not a duplicate.

- **Architecture replaced by streaming + SQLite:** the batch in-memory pipeline was
  replaced by the streaming design — `stream_parse_file()` (tagged items,
  `duplicate_check` seam), `storage.py` (`RunStorage`: temp SQLite DB, per-file
  transactions, `fingerprint_seen` intra-file checks, SQL multiplicity-aware
  cross-file dedup, first-100 + exact-total error summaries, statistics sums,
  exception-safe lifecycle with cleanup failures exposed through `cleanup_errors`). Compatibility interfaces (`parse_file`,
  `dedup_cross_file`, `events_by_src_ip`, `detect`, `run_all_detectors`) are
  preserved with identical semantics. Record: `docs/ARCHITECTURE.md` §3–§5, §13–§14.
- **Incremental detection:** detectors converted to `observe()`/`results()` with
  batch compatibility; streaming and batch findings identical by construction.
- **Security remediations:** M1 (`37d19de`) — sanitized SQLite evidence
  (`evidence_line`) and per-run keyed HMAC fingerprints (`fp_digest`), no raw-line
  column or index; M6 (`58d1806`) — construction-time best-effort error-reason
  sanitization. Full record incl. residual risks: `docs/SECURITY_AUDIT.md`.
- **Validation:** 372 tests OK / 9 platform-gated skips (canonical command,
  CPython 3.14.10, Windows); 105,335-line scale test with exact statistics;
  traced-memory regression bound (< 30 MB tracemalloc peak — Python allocations,
  not process RAM); one-time NFR-010 timing measurement 0.396 s (< 5 s).
- **Samples:** populated with verified synthetic content (FR-173 verified; RFC 5737
  addresses; intentional invalid address as malformed-input test data); two accepted
  end-to-end CLI demonstrations with exact statistics reconciliation.
- **Documentation:** REQUIREMENTS.md, ARCHITECTURE.md, DETECTION_RULES.md, and
  USAGE.md reconciled to the verified implementation; docs/PHASE3_VALIDATION.md §16
  added as the post-Phase-5 reconciliation record.
- **Release preparation:** README written and verified; MIT LICENSE populated;
  `.gitignore` populated; CI workflow authored; first hosted run `45025411430`
  succeeded on push to `main`.
- **Outstanding:** push of the four local commits (`58d1806`, `37d19de`,
  `6c2383e`, `c98c3d0`) to `origin/main`; deletion decision for the Git-ignored
  `audit-*` and demonstration-report artifacts; FR-162/NFR-009 best-effort redaction
  gap; Python 3.12 and macOS verification (declared/expected, not yet executed).
