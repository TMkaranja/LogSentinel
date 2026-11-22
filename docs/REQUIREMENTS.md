# LogSentinel — Requirements Specification

- **Document:** REQUIREMENTS.md
- **Phase:** 2 (Requirements & Technical Specification); implemented through Phase 5
- **Status:** Approved requirements blueprint — this document reflects the verified
  implementation through Phase 5; historical addenda (§20) are retained unchanged
- **Scope:** Functional and non-functional requirements for LogSentinel v0.1.0

---

## 1. Project Overview

LogSentinel is a defensive, file-based cybersecurity log analysis application written in
Python (minimum supported version 3.12; development and CI target 3.14) using only
the standard library at runtime. It reads supplied log files in
batch, extracts structured security events, groups activity by source IP address, applies
predefined detection rules, and produces both human-readable (console) and machine-readable
(JSON) reports.

The application is strictly an **offline analysis tool**: it operates only on log files the
user supplies and never connects to, probes, or interacts with the systems whose logs it
analyses. It is a passive audit aid, not an active security control.

## 2. Problem Statement

Security practitioners frequently need to answer simple questions from log files that are
too large to read manually:

- Is one source IP repeatedly failing SSH authentication (possible brute-force attempt)?
- Is one source IP touching many distinct destination ports (possible port scan)?
- Is one source IP generating an abnormal volume of HTTP 4xx responses (possible
  scanning or abuse of a web application)?

Existing SIEM platforms are heavyweight, network-connected, and often unavailable for
quick offline triage, air-gapped environments, forensic review of exported logs, or CI
pipelines. LogSentinel fills that gap: a small, dependency-free, auditable CLI tool that
answers these three questions from plain log files and emits evidence-backed findings.

**Important:** LogSentinel detects *patterns that merit review*. A finding is an
investigative lead, not proof of malicious intent (see §18 and DETECTION_RULES.md).

## 3. Project Objectives

| ID | Objective |
|----|-----------|
| OBJ-01 | Parse common textual SSH, firewall, and HTTP access logs into structured events. |
| OBJ-02 | Group events by source IP address for per-host analysis. |
| OBJ-03 | Detect SSH brute-force, port-scan, and HTTP 4xx abuse patterns with configurable thresholds. |
| OBJ-04 | Produce console and JSON reports containing findings and processing statistics. |
| OBJ-05 | Fail safely: malformed input must never crash the run or corrupt the report. |
| OBJ-06 | Remain dependency-free (standard library only) and cross-platform where practical. |
| OBJ-07 | Keep detection logic independent of presentation so rules can be tested and extended in isolation. |

## 4. Intended Users

- **System administrators** triaging auth, firewall, and web logs on servers they operate.
- **SOC analysts / incident responders** performing first-pass offline review of exported logs.
- **Students and educators** studying defensive log analysis with a readable codebase.
- **CI pipelines** that gate on findings (non-zero exit code when findings exist).

Users are assumed able to obtain log files legitimately. LogSentinel performs **no log
collection**; acquisition is out of scope.

## 5. Functional Requirements

### 5.1 Input (FR-0xx)

| ID | Requirement |
|----|-------------|
| FR-001 | The CLI shall accept one or more file paths and/or directory paths as positional arguments. |
| FR-002 | When a directory is supplied, the tool shall recursively discover files within it with recognized log extensions (`.log`, `.txt`) and non-hidden names. |
| FR-003 | The tool shall read files as UTF-8 with permissive fallback (UTF-8, then Latin-1) and treat undecodable content as data errors, not crashes (see FR-100). |
| FR-004 | Duplicate input paths (including overlapping directory expansions) shall be de-duplicated before processing, by exact path-string identity only: case variants, aliases, and symbolic links are not normalized, so different path strings referring to the same underlying file may be ingested separately (see FR-016 for content deduplication). |
| FR-005 | The tool shall accept an optional JSON configuration file (see §13, FR-060). |

### 5.2 Parsing and events (FR-0xx)

| ID | Requirement |
|----|-------------|
| FR-010 | The parser shall recognize three event families: SSH authentication events (`ssh_auth`), firewall connection events (`firewall_conn`), and HTTP request events (`http_request`). |
| FR-011 | The parser shall support classic syslog-style timestamp headers (`Mmm dd hh:mm:ss`, e.g. `Mar 10 11:22:33`) and ISO-8601 timestamps. |
| FR-012 | Syslog timestamps that omit a year shall be resolved to a full UTC date per rule AR-004 (ARCHITECTURE.md §7). |
| FR-013 | All events shall be represented as typed dataclass instances (AR-001), never as loose dictionaries, in all module interfaces. |
| FR-014 | Every event shall carry a canonical integer Unix timestamp (seconds, UTC) plus the original raw timestamp string for evidence. |
| FR-015 | Lines that cannot be parsed into a known event shape shall be skipped and counted; they shall not abort processing (AR-003). |
| FR-016 | Duplicate ingestion shall not inflate detection counts. Deduplication is content-addressed (AR-005) and scoped to cross-file re-ingestion: identical fingerprints `(kind, canonical timestamp, normalized raw line)` from *different* input files collapse; byte-identical lines within one file are preserved as legitimate events. An identical fingerprint across files is not absolute proof of duplicate ingestion - collapses are treated as re-ingestion for counting and are counted in run statistics (accepted limitation: docs/PHASE3_VALIDATION.md section 15.2). |
| FR-017 | An `ssh_auth` event shall expose: timestamp, source IP, username, and authentication result (success/failure). |
| FR-018 | A `firewall_conn` event shall expose: timestamp, source IP, destination IP, destination port (1-65535), and protocol. |
| FR-019 | An `http_request` event shall expose: timestamp, source IP, HTTP method, request path, and response status code. |
| FR-020 | Source IP values shall be validated as IPv4 via the `ipaddress` module; an invalid IP marks the line malformed (see §9). |
| FR-021 | Lines with a valid timestamp shape but an unrecognized message body shall be materialized as `othersyslog` events: retained for statistics and evidence, excluded from all detection rules. (First recorded in the Phase 3 corrections addendum, §20.) |

### 5.3 Detection (FR-0xx)

| ID | Requirement |
|----|-------------|
| FR-030 | The tool shall implement detection rule **LS-RULE-001 (SSH brute-force)**: raise a finding when a single source IP accumulates >= N failed `ssh_auth` events within a sliding time window (defaults: N=8, window=300 s; both configurable). |
| FR-031 | The tool shall implement detection rule **LS-RULE-002 (port scan)**: raise a finding when a single source IP connects to >= M distinct destination ports across `firewall_conn` events (default: M=10; configurable). |
| FR-032 | The tool shall implement detection rule **LS-RULE-003 (HTTP 4xx abuse)**: raise a finding when a single source IP receives >= K HTTP responses with status 400-499 (default: K=8; configurable). |
| FR-033 | Successful SSH authentications shall be retained as evidence context and shall never satisfy the failure threshold of LS-RULE-001 (see DETECTION_RULES.md, Rule 1). |
| FR-034 | Detection shall group events by validated source IP; events without a valid source IP shall not contribute to any rule. |
| FR-035 | Detector output shall be `Finding` dataclass instances carrying rule ID, source IP, severity, first/last seen timestamps, evidence references, and summary counts. Detectors shall not format output. |
| FR-036 | All three thresholds and the SSH window shall be overridable via CLI options or a JSON config file; precedence: CLI > config file > built-in defaults. |

### 5.4 Reporting (FR-0xx)

| ID | Requirement |
|----|-------------|
| FR-040 | The tool shall print a human-readable summary to stdout: per-rule findings with severity and evidence counts, plus processing statistics (files scanned, lines read, events parsed, malformed lines, duplicates, findings). |
| FR-041 | The tool shall optionally write a JSON report (`--json PATH`) with a stable schema: `report_version`, `generated_at`, `config_used`, `statistics`, `findings[]`, `errors[]`. |
| FR-042 | The JSON report shall be deterministic for identical inputs and configuration, except for `generated_at`. |
| FR-043 | JSON output shall use the standard `json` module with `ensure_ascii=False` and UTF-8 encoding; findings shall include evidence excerpts (raw lines) capped at a maximum length. |
| FR-044 | The process exit code shall encode the outcome (see §14, FR-090). |

### 5.5 Configuration (FR-0xx)

| ID | Requirement |
|----|-------------|
| FR-060 | An optional JSON config file may set: `ssh_threshold`, `ssh_window_seconds`, `portscan_threshold`, `http_4xx_threshold`, `strict`, `max_line_length`, `max_file_mb`. Unknown keys shall be rejected with a configuration error. |
| FR-061 | Threshold values shall be validated (positive integers; window > 0); invalid configuration shall abort before any processing with exit code 2. |

### 5.6 CLI (FR-0xx)

| ID | Requirement |
|----|-------------|
| FR-070 | The tool shall be invokable as `python -m logsentinel` and (after packaging) as the `logsentinel` console script. |
| FR-071 | The CLI shall provide `--help`, `--version`, and options for: config file, per-rule thresholds, SSH window, JSON output path, text report path, `--strict`, and `--quiet`. |
| FR-072 | The CLI shall reject zero positional inputs with a usage error and exit code 2. |

## 6. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-001 | Runtime shall depend only on the Python standard library. Minimum supported interpreter: 3.12; development and CI target: 3.14 (NFR-011). Testing shall use the stdlib `unittest`. |
| NFR-002 | Modular architecture: each module has a single responsibility; no circular imports; dependencies flow one way and form an acyclic graph: `cli` depends on `config`, `inputs`, `parsers`, `storage`, `events`, `detectors`, `report`, and `exceptions`; `inputs` on `events`; `parsers` on `events` and `exceptions`; `storage` on `events`; `detectors` on `events`; `report` on `events` and `exceptions`. (Full graph: ARCHITECTURE.md §4.) |
| NFR-003 | Malformed input shall never raise an unhandled exception during a normal batch run (fail-safe parsing). |
| NFR-004 | Batch processing shall handle files of at least 100k lines by streaming line-by-line and aggregating incrementally (no full-file buffering of parsed events beyond per-IP aggregation). |
| NFR-005 | All timestamps shall be handled in UTC internally; local timezone shall never change analysis results. |
| NFR-006 | All documented default behaviour (thresholds, window, dedup, boundary handling) shall be deterministic and covered by unit tests using fixed reference times. |
| NFR-007 | The codebase shall use type hints throughout and pass `python -m unittest discover` cleanly across the supported interpreter range (3.12+, CI runs on 3.14). |
| NFR-008 | Cross-platform where practical: pure-Python path handling (`pathlib`), no shell-out, LF/CRLF-tolerant reading. |
| NFR-009 | Reports shall avoid emitting secrets found in logs (passwords, tokens) — evidence lines are trimmed and no credential fields are extracted or echoed. |
| NFR-010 | Analysis of the three shipped sample files (each < 1 MB) shall complete in under 5 seconds on commodity hardware. |
| NFR-011 | The project shall support Python 3.12 as the minimum interpreter version, with 3.14 as the development and CI target. All runtime and test code shall avoid features unavailable in 3.12. (Introduced in the final Phase 3 corrections; resolves the former 3.14-only phrasing of NFR-001/NFR-007/AC-008.) |

## 7. Supported Log Sources

| ID | Source | Example origin | Format in scope |
|----|--------|----------------|-----------------|
| SRC-01 | SSH authentication logs | OpenSSH via syslog/auth.log | syslog-style lines with `Failed password` / `Accepted password` / `Accepted publickey` |
| SRC-02 | Firewall logs | Common Linux firewall dump styles (e.g. netfilter `DROP`/`ACCEPT` lines) | key=value fields such as `PROTO=TCP SPT=... DPT=...` |
| SRC-03 | HTTP access logs | Apache/Nginx *combined/common* access log format | `"GET /path HTTP/1.1" 404 size` |

Log **acquisition** (SSHing to hosts, agents, syslog receivers, Windows Event Log) is out
of scope; the user supplies files.

## 8. Supported Log Formats

| ID | Format | Timestamp style | Notes |
|----|--------|-----------------|-------|
| FMT-01 | Syslog-style prefix | `Mmm dd hh:mm:ss` (no year) | Year resolved per AR-004; treated as UTC |
| FMT-02 | ISO-8601 | `YYYY-MM-DDTHH:MM:SS[.ffffff][Z or +-HH:MM]` | Offset-aware values converted to UTC; naive treated as UTC |
| FMT-03 | Apache combined | `[dd/Mon/yyyy:hh:mm:ss +-zzzz]` | Used for `http_request` |

Any line that matches none of the configured event shapes is treated as unparsed (FR-015).
Encoding: UTF-8 preferred with Latin-1 fallback; input files are assumed to be text.

## 9. Input Validation Requirements

| ID | Requirement |
|----|-------------|
| FR-100 | A path that does not exist or is not readable shall produce a per-path error entry in the report and be skipped, not crash the run; in `--strict` mode it shall abort with exit code 2. |
| FR-101 | Directories supplied as input shall be recursed per FR-002; empty discovery results shall produce a warning, not an error. |
| FR-102 | Files larger than a configurable safety cap (`max_file_mb`, default 512) shall be skipped with a recorded error entry. |
| FR-103 | Individual lines longer than `max_line_length` (default 8192 chars) shall be treated as malformed and counted. |
| FR-104 | Non-UTF-8 decodable bytes shall follow the encoding fallback in FR-003 (UTF-8 attempt, then a full Latin-1 retry of the file); when the fallback is used, the file receives a warning error entry in the report. Because Latin-1 maps every byte sequence, no post-fallback decoding failure can occur. |

## 10. Event Processing Requirements

| ID | Requirement |
|----|-------------|
| FR-110 | Files shall be processed line-by-line in streaming fashion (NFR-004). |
| FR-111 | Parse order within a file shall follow file order; events shall be ordered for detection by canonical timestamp with kind as tie-breaker — a stable sort by `(timestamp, kind)` that preserves ingestion (file) order for ties (see DETECTION_RULES.md §4.2). |
| FR-112 | Every successfully parsed line shall yield exactly one event, except `othersyslog` lines dropped after the configured retention cap (FR-021): those yield no event and are counted in `othersyslog_dropped` (FR-113); every unparseable line shall increment the per-file malformed counter. |
| FR-113 | Statistics shall be accumulated as follows. Per file (`FileStats`): `lines_read`, `events_parsed`, `malformed`, `duplicates` (intra-file byte-identical repeats, preserved as events per FR-016 and counted here), `othersyslog`, `othersyslog_dropped`. Run-level: `cross_file_duplicates` (collapses attributed during cross-file dedup). Invariant: `malformed + events_parsed + othersyslog_dropped == lines_read` (``duplicates`` counts intra-file byte-identical repeats, which are preserved and are a subset of `events_parsed`; run-level `cross_file_duplicates` is tracked separately - Phase 4.1 semantics). |
| FR-114 | Event construction shall validate types (IP, port, status code, result flag) at construction time; invalid construction attempts are recorded as malformed lines by the parser. |

## 11. Detection Requirements

| ID | Requirement |
|----|-------------|
| FR-120 | Detection shall operate on validated events only, grouped by source IP (FR-034). |
| FR-121 | The SSH sliding window shall be half-open: events with timestamp in `(t_latest - window, t_latest]` count (AR-006). |
| FR-122 | A finding is raised at most once per (rule, source IP) per run; the finding aggregates all qualifying evidence. |
| FR-123 | Distinct ports for LS-RULE-002 are counted after deduplication (FR-016); duplicate connections to the same port do not raise the count. |
| FR-124 | For LS-RULE-003 only statuses 400-499 count; 3xx/5xx and other codes are ignored by the rule but retained in events. |
| FR-125 | Invalid destination ports (outside 1-65535) make the firewall line malformed (FR-020); they are never counted toward port-scan thresholds. |

Full per-rule logic, examples, and edge cases: **DETECTION_RULES.md**.

## 12. Reporting Requirements

| ID | Requirement |
|----|-------------|
| FR-130 | Console output shall list findings grouped by rule, sorted by rule ID first, then severity, then source IP. |
| FR-131 | The JSON report shall include the effective configuration used, enabling reproducible audits (FR-041). |
| FR-132 | Reports shall be written atomically (write to temp file, replace) when a file target is given. |

## 13. Configuration Requirements

| ID | Requirement |
|----|-------------|
| FR-140 | Built-in defaults: `ssh_threshold=8`, `ssh_window_seconds=300`, `portscan_threshold=10`, `http_4xx_threshold=8`, `strict=False`, `max_line_length=8192`, `max_file_mb=512`. |
| FR-141 | Precedence: built-in defaults < JSON config file < CLI options (FR-036, FR-060). |
| FR-142 | `config.py` shall own defaults, validation, and precedence; no other module defines thresholds. |

## 14. Error Handling Requirements

| ID | Requirement |
|----|-------------|
| FR-150 | The application shall define its own exception hierarchy in `exceptions.py`: `LogSentinelError` (base), `ConfigError`, `InputPathError`, `ParseError`, `ReportError`. |
| FR-151 | Per-line and per-file problems shall be recorded as error entries (file, line number, reason) in the report, not raised, in normal mode. |
| FR-152 | `--strict` mode converts the first recorded error into an abort with the corresponding exception type. |
| FR-153 | Unhandled unexpected exceptions shall abort with exit code 3 and a short diagnostic on stderr; they shall not produce a partial JSON report. |
| FR-154 | Error entries shall be capped in the report (`max_reported_errors`, default 100) with an overflow marker. |

### Exit codes (FR-090)

| Code | Meaning |
|------|---------|
| 0 | Run completed; no findings. |
| 1 | Run completed; one or more findings. |
| 2 | Usage/configuration/input-path error (nothing analysed, or run aborted in strict mode). |
| 3 | Unexpected runtime error. |

## 15. Security and Privacy Requirements

| ID | Requirement |
|----|-------------|
| FR-160 | The application shall make no network connections of any kind at runtime. |
| FR-161 | The application shall not execute any content from log files (no shell-out, no `eval`, no dynamic imports). |
| FR-162 | Evidence excerpts shall be capped in length; credential-bearing fields (passwords) shall never be extracted, stored, or echoed even if present in raw lines. |
| FR-163 | No telemetry, crash reporting, or update checks. |
| FR-164 | Processed files are opened read-only; the application writes only to paths explicitly given by the user (report targets), except for its own run-scoped temporary SQLite staging database created under the system temporary directory (never inside the project tree), which is removed when the run ends (see ARCHITECTURE.md §14). Processed user input files remain unmodified. |

## 16. Testing Requirements

| ID | Requirement |
|----|-------------|
| FR-170 | Tests shall use the standard library `unittest` framework (`python -m unittest discover` from the project root). |
| FR-171 | Each module shall have a corresponding `tests/test_<module>.py`; the CLI is covered by `tests/test_cli.py`. |
| FR-172 | Detector tests shall use fixed reference timestamps (injected `now`) so results are deterministic (NFR-006). |
| FR-173 | Sample files under `samples/` shall contain only synthetic data with documentation IP ranges (RFC 5737 `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`) and example hostnames — no real client data. |
| FR-174 | Boundary conditions shall be tested explicitly: threshold-1, threshold, threshold+1, window boundary inclusivity (AR-006), duplicate collapse, malformed-line counting. |
| FR-175 | CI shall run the full suite on every push/PR via GitHub Actions (`.github/workflows/tests.yml`). |

## 17. Acceptance Criteria

| ID | Criterion |
|----|-----------|
| AC-001 | `python -m logsentinel samples/ --json report.json` on the shipped synthetic samples completes with exit code 0 or 1 and produces a schema-valid JSON report. |
| AC-002 | A synthetic `auth.log` with 8 failures from `192.0.2.7` within 300 s yields exactly one LS-RULE-001 finding for that IP; 7 failures yields none. |
| AC-003 | A synthetic `firewall.log` with connections to 10 distinct ports from one IP yields one LS-RULE-002 finding; 9 distinct ports yields none. |
| AC-004 | A synthetic `access.log` with 8 x 4xx responses from one IP yields one LS-RULE-003 finding; 7 yields none. |
| AC-005 | A file containing garbage lines yields a report with `malformed` counts and no crash (exit 0/1, not 2/3). |
| AC-006 | Overriding `--ssh-threshold 3` lowers the detection bar accordingly (precedence FR-141). |
| AC-007 | Missing input path -> exit code 2; `--strict` with a malformed file -> exit code 2. |
| AC-008 | `python -m unittest discover` passes with zero failures across the supported interpreter range (3.12+; CI on 3.14). |

## 18. Explicit Limitations and Out-of-Scope Features

The following are **out of scope for v0.1.0**:

- Machine learning / anomaly scoring.
- GUI, TUI, or web front-end (CLI only).
- Real-time streaming/tailing; batch files only.
- SIEM integration (Splunk/Elastic/etc.), CEF/LEEF/OTLP export.
- Windows Event Log ingestion (`.evtx`).
- Cloud log integrations (AWS CloudTrail, Azure, GCP).
- GeoIP or any enrichment requiring external data or services.
- IPv6 source addresses (records IPv4 only; IPv6 parsing is a documented non-goal for v1).
- Active response: blocking, alerting, notifications — LogSentinel is analysis-only.
- Log acquisition of any kind; encrypted/rotated/compressed archives.

**Fundamental limitation:** every detector reports a *statistical pattern*. A finding does
not prove malicious intent — legitimate tools (monitoring agents, vulnerability scanners,
QA crawlers, fat-fingered operators) produce identical signatures. Human review of the
evidence is always required (DETECTION_RULES.md, "Detection vs. proof").

## 19. Requirement Traceability (summary)

| Concern | Requirements | Design refs |
|---------|--------------|-------------|
| Input handling | FR-001-005, FR-100-104 | inputs.py, AR-012, AR-005 |
| Parsing/events | FR-010-020, FR-110-114 | parsers.py, events.py, AR-001/004/005 |
| Detection | FR-030-036, FR-120-125 | detectors.py, DETECTION_RULES.md |
| Reporting | FR-040-044, FR-130-132 | report.py |
| Configuration | FR-060-061, FR-140-142 | config.py, AR-008 |
| Errors | FR-150-154 | exceptions.py, AR-012 |
| Security | FR-160-164 | Section 15 |
| Testing | FR-170-175, AC-001-008 | tests/, ARCHITECTURE.md |

## 20. Phase 3 Corrections Addendum

Applied during the Phase 3 technical design validation (docs/PHASE3_VALIDATION.md §13).
Entries here supersede the original text of the referenced requirements.

| Ref | Correction |
|-----|------------|
| FR-002 (clarified) | Explicitly supplied file paths are processed regardless of extension (user override); the `.log`/`.txt` extension filter applies only to directory discovery (FR-002 original applies to directory recursion only). |
| FR-010 (superseded) | The parser recognizes three typed event families — `SSHAuthEvent` (kinds `authok`/`authfail`), `FirewallEvent` (kind `fwconn`), `HTTPRequestEvent` (kind `web`) — plus pass-through `SyslogEvent` (kind `othersyslog`, FR-021). Canonical kind vocabulary: **`authok`, `authfail`, `fwconn`, `web`, `othersyslog`**. |
| FR-016 (final, Phase 3 remediation) | Deduplication is **content-addressed** (AR-005) and scoped to **cross-file re-ingestion**: identical fingerprints `(kind, canonical timestamp, normalized raw line)` from *different* input files collapse; byte-identical lines within one file are preserved as legitimate events. Duplicate ingestion of the same file is prevented by input-path de-duplication (FR-004); FR-004 de-duplicates only exact path strings - different path strings referring to the same underlying file, including aliases, case variants, and symbolic links, are not normalized and may therefore be ingested separately. Cross-file collapses are counted and reported. |
| FR-021 (new) | Lines with a valid timestamp shape but an unrecognized message body shall be materialized as `othersyslog` events: retained for statistics and evidence, excluded from all detection rules. |
| FR-033 (clarified) | `successful_followups` in an LS-RULE-001 finding counts successful SSH authentications from the same source IP across the whole run (independent of windows); successes never satisfy or reset the failure threshold. |
