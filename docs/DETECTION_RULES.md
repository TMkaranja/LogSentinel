# LogSentinel — Detection Rules Specification

- **Document:** DETECTION_RULES.md
- **Phase:** 2 (Requirements & Technical Specification); implemented and verified in
  Phases 4.3/4.5 (batch detection engine, input discovery) and Phase 5
  (SQLite-backed streaming architecture)
- **Status:** Implemented — this document reflects the shipped behaviour

This document specifies the three detection engines of LogSentinel v0.1.0. Each rule is
described with its logic, required fields, configuration, worked example, expected
finding, false-positive considerations, edge cases, and acceptance criteria.

**Standing terminology rule:** all findings describe *suspicious patterns that merit human
review*. LogSentinel cannot observe intent, attribution, or impact; the word "attack" must
never appear in generated findings or reports. See "Detection vs. proof" at the end.

Shared semantics (defined in ARCHITECTURE.md, referenced by ID):

- Events are frozen dataclasses; canonical time is integer Unix epoch seconds UTC (AR-002).
- Timestamps are validated at construction; invalid fields mark the line malformed (AR-001).
- Cross-file duplicate handling is performed by SQLite staging (Phase 5): occurrences of a
  fingerprint `(kind, canonical timestamp, raw_line)` are counted separately per source
  file, the retention cap is the **maximum single-file occurrence count**, and only
  occurrences beyond that cap are removed (counted as `cross_file_duplicates`). Identical
  repeated events **within the same file are preserved** and count individually.
  **Detectors themselves never deduplicate** (AR-005 final; docs/PHASE3_VALIDATION.md
  section 15.2).
- The SSH sliding window is half-open `(t_latest - window, t_latest]` (AR-006).
- Detectors are pure functions of (events, thresholds); the clock is injected (AR-010).

All sample addresses below are RFC 5737 documentation addresses (`192.0.2.0/24`,
`198.51.100.0/24`, `203.0.113.0/24`) and RFC 2606 example hostnames.

---

## RULE 1 — LS-RULE-001: SSH Brute-Force Detection

**Intent:** flag source IPs whose failed SSH authentication attempts are dense enough in
time to indicate a credential-guessing pattern.

### 1.1 Detection logic

1. Consider only `ssh_auth` events with `success == False`, grouped by `src_ip`
   (FR-030, FR-034).
2. Sort the group's failure events ascending by `(timestamp, kind)` — a stable sort that
   preserves original ingestion order for equal timestamps (FR-111).
3. For each failure index `i`, the window `(t_i - window, t_i]` is *qualifying* when it
   contains at least `threshold` failures (half-open window, AR-006; two-pointer scan,
   O(n)).
4. All qualifying windows are **merged into a union of qualifying index ranges**:
   overlapping or adjacent ranges unite, and `failed_count` equals the size of that union
   — the number of failures that belong to at least one qualifying window (FR-122).
5. If the union is non-empty, raise **one** finding per source IP with:
   - `first_seen` / `last_seen` = min/max timestamps of the qualifying union,
   - evidence = the raw lines of the qualifying failures first, followed by the raw lines
     of all *successful* authentications from the same source IP observed across the
     whole run (context, see §1.5),
   - summary = `{"failed_count": n, "distinct_usernames": u, "window_seconds": w,
     "successful_followups": s}` where `n` is the union size, `u` the number of distinct
     usernames among the qualifying failures, and `s` the run-wide count of successful
     authentications from that source IP.
6. If no window reaches the threshold, no finding.

### 1.2 Required event fields

| Field | Type | Constraint |
|-------|------|------------|
| `timestamp` | int (epoch s, UTC) | required |
| `src_ip` | str (IPv4) | must parse as IPv4 |
| `success` | bool | `False` for counting; `True` events are context only |
| `username` | str | reported in summary; may be empty string |
| `raw_line`, `source_file` | str | evidence |

### 1.3 Threshold configuration

| Setting | Default | CLI override | Config file key |
|---------|---------|--------------|-----------------|
| Failure threshold | 8 | `--ssh-threshold N` | `ssh_threshold` |
| Sliding window (seconds) | 300 | `--ssh-window N` | `ssh_window_seconds` |

Both values are independent and configurable (FR-036, FR-140); precedence CLI > config
file > defaults (AR-008).

### 1.4 Timestamp handling

- Canonical epoch seconds (AR-002). Yearless syslog prefixes are resolved per AR-004
  (injected `reference_now`, current year, >24h-future rollover).
- Events whose timestamps cannot be validated never enter the group (FR-114).
- Window math is exact integer comparison: `t_latest - window < t_j <= t_latest`.

### 1.5 Treatment of successful authentications

- `success == True` events are **never counted** toward the threshold (FR-033).
- They are **not** a reset condition either: failures before and after a success remain in
  their own windows. Rationale: attackers commonly interleave successes after cracking a
  weak account; resetting on success would let an attacker suppress future findings by
  succeeding occasionally. Successes are attached to the finding (if any) as context:
  `successful_followups` counts successes from the same source IP across the whole run
  (independent of windows), to help analysts spot probable compromise. The successful
  authentication raw lines are appended to the finding's evidence after the qualifying
  failure lines.
- A success after a raised finding therefore never cancels the finding — findings are
  review leads, not verdicts.

### 1.6 Duplicate and malformed event handling

- **Duplicates (final, Phase 3 remediation; Phase 5 storage):** cross-file duplicate
  handling is performed by SQLite staging, not by the detectors. Occurrences of each
  fingerprint `(kind, canonical timestamp, raw_line)` are tracked separately per source
  file; the retention cap is the **maximum single-file occurrence count**; the
  earliest-ingested occurrences are retained and only the excess is removed (counted as
  `cross_file_duplicates`). Byte-identical lines within the **same file are preserved**
  and count individually — legitimate sources can emit identical lines for distinct
  events. Input discovery removes duplicate path strings (exact-string path
  dedup, FR-004), so the same file cannot be ingested twice via an identical
  path spelling; however, different path aliases, case variants, or symbolic
  links can still refer to the same underlying file, and such aliasing is not
  detected or normalized — deduplication identity remains the exact supplied
  path string.
  An identical fingerprint across files is **not absolute proof of duplicate ingestion**:
  a genuine event mirrored into two collected files may collapse although genuine — an
  accepted, conservative limitation (docs/PHASE3_VALIDATION.md section 15.2).
- **Malformed lines** (bad timestamp, invalid IP, unparseable shape) are counted as
  malformed, excluded from analysis, and never partially contribute (FR-015, FR-114).
- Note the deliberate asymmetry: identical repeats within one file are preserved and all
  count individually, while cross-file re-ingestion collapses beyond the per-file
  multiplicity cap.

### 1.7 Example input (synthetic)

```text
Mar 10 11:20:01 sshd[1001]: Failed password for admin from 192.0.2.7 port 51001 ssh2
Mar 10 11:20:05 sshd[1001]: Failed password for admin from 192.0.2.7 port 51002 ssh2
... (6 more failures at 11:20:09 .. 11:20:59 from 192.0.2.7) ...
Mar 10 11:20:59 sshd[1001]: Failed password for invalid user root from 192.0.2.7 port 51008 ssh2
```

### 1.8 Expected finding

```json
{
  "rule_id": "LS-RULE-001",
  "severity": "high",
  "src_ip": "192.0.2.7",
  "first_seen": 1741605601,
  "last_seen": 1741605659,
  "summary": {"failed_count": 8, "distinct_usernames": 2, "window_seconds": 300,
              "successful_followups": 0},
  "evidence": ["<raw lines of the qualifying failures, then successful-login context>"]
}
```

Severity is `high` by default (see §4.1 Severity table). The serialized finding carries
`rule_id`, `severity`, `src_ip`, `first_seen`, `last_seen`, `summary`, and `evidence`
(the report renderer does not emit a separate `rule_name` field).

### 1.9 False-positive considerations

| Cause | Mitigation / analyst guidance |
|-------|-------------------------------|
| One user mistyping their password repeatedly | 8 failures in 5 min from one IP is possible; check `username` spread and follow-up success |
| Scheduled job with stale credentials (cron, backup agent) | Usually same username, metronomic timing; check `successful_followups` |
| Legitimate vulnerability scanner in a pentest window | Same signature; requires operator context LogSentinel cannot have |
| Mail/monitoring probes hitting SSH by accident | Rarely reaches the failure threshold |

### 1.10 Edge cases

| Case | Behaviour |
|------|-----------|
| 8 failures spread over 1 hour (> window) | No finding (window is essential) |
| Failure exactly `t_latest - 300` | Excluded (half-open window, AR-006) |
| Failure exactly at `t_latest` | Included (same-second events count) |
| Two overlapping qualifying windows | Merged into one union; `failed_count` is the union size, no double counting |
| 8 failures then 1 success at `t_latest` | Finding still raised; success recorded as `successful_followups: 1` and its raw line appended to evidence |
| Same second x10, same IP/user, distinct raw lines (ports/pids) | 10 failures counted (distinct raw lines are distinct fingerprints; only cross-file re-ingestion beyond the cap collapses) |
| Same second x10, byte-identical lines, same file | 10 failures counted (intra-file repeats preserved); `duplicates` statistic = 9 |
| Threshold lowered to 1 by config | Valid; single failure triggers (documented, discouraged) |
| Invalid IP `999.1.1.1` | Line malformed; never counted (FR-020) |

### 1.11 Acceptance criteria

- AC-002 (REQUIREMENTS.md §17): 8 failures/300 s -> exactly one finding; 7 -> none.
- R1-AC-01: two separate bursts, each 7 failures, > 300 s apart -> no finding.
- R1-AC-02: 15 failures across two overlapping windows -> one finding per IP, evidence
  covers the merged qualifying union, `failed_count` = the union size (FR-122).
- R1-AC-03: cross-file duplicate handling verified: the same fingerprint in two files is
  retained up to the maximum single-file occurrence count; intra-file byte-identical
  repeats are preserved and counted individually (10 identical lines in one file ->
  10 counted, `duplicates` statistic = 9).
- R1-AC-04: success events never lower or reset counts (FR-033).

---

## RULE 2 — LS-RULE-002: Network Port-Scan Detection

**Intent:** flag source IPs that contact an unusually wide set of destination ports — the
signature of reconnaissance sweeps.

### 2.1 Detection logic

1. Consider only `firewall_conn` events, grouped by `src_ip` (FR-031, FR-034).
2. Build the set of **distinct** `dst_port` values per source IP (cross-file duplicates
   are already handled by SQLite staging before detection, AR-005; distinctness is by
   port number regardless of protocol and destination IP).
3. If `len(distinct_ports) >= threshold` (default 10), raise **one** finding per source IP
   with:
   - `first_seen` / `last_seen` = min/max timestamps spanning **all** firewall events
     observed for that source IP across the run (not only first-seen port events),
   - evidence = the raw line of the **first event seen to each distinct destination
     port**, ordered by ascending port number — exactly one line per distinct port,
   - summary = `{"distinct_ports": n, "ports_sample": <first 20 sorted>,
     "protocols": [...]}` where `protocols` is the sorted set of distinct protocols.
4. There is **no time window** in v1: the sweep may span the whole run. Rationale: for
   batch log review, a rate-unlimited distinct-port count is the strongest simple signal;
   windowing is a candidate for v1.1 and its absence is documented, not hidden.

### 2.2 Required event fields

| Field | Type | Constraint |
|-------|------|------------|
| `timestamp` | int (epoch s, UTC) | required |
| `src_ip` | str (IPv4) | must parse as IPv4 |
| `dst_port` | int | 1-65535; anything else -> line malformed (FR-125) |
| `dst_ip` | str (IPv4) | must parse as IPv4 (not used in counting; kept for evidence) |
| `protocol` | str | TCP/UDP/ICMP accepted; informational |

### 2.3 Threshold configuration

| Setting | Default | CLI override | Config file key |
|---------|---------|--------------|-----------------|
| Distinct-port threshold | 10 | `--portscan-threshold N` | `portscan_threshold` |

(FR-031, FR-036, FR-140; precedence per AR-008.)

### 2.4 Duplicate port handling

- Duplicate connections to the *same* port never increase the distinct count — the
  count is set-based. Cross-file re-ingestion duplicates collapse only via the
  multiplicity rule (AR-005, final: Phase 3 remediation; SQLite staging in Phase 5).
- A connection to the same port on a **different destination IP** still counts once: the
  rule measures port breadth, not host breadth (a v1 limitation, documented).

### 2.5 Treatment of invalid ports

- Values outside 1-65535 (including 0, negative, non-numeric) make the line **malformed**:
  the event is rejected entirely and never counted (FR-125, FR-114).
- Rationale: a "port" that cannot exist indicates a parsing artifact or corrupt line;
  counting it would poison the distinct set. The malformed counter records it.

### 2.6 Example input (synthetic)

```text
Mar 10 09:00:01 fw kernel: DROP IN=eth0 SRC=198.51.100.23 DST=203.0.113.10 PROTO=TCP SPT=40001 DPT=22
Mar 10 09:00:02 fw kernel: DROP IN=eth0 SRC=198.51.100.23 DST=203.0.113.10 PROTO=TCP SPT=40002 DPT=23
... (DPT = 25, 80, 110, 143, 443, 445, 3389, 8080) ...
Mar 10 09:00:11 fw kernel: DROP IN=eth0 SRC=198.51.100.23 DST=203.0.113.10 PROTO=TCP SPT=40011 DPT=9100
```

### 2.7 Expected finding

```json
{
  "rule_id": "LS-RULE-002",
  "severity": "medium",
  "src_ip": "198.51.100.23",
  "first_seen": 1741599601,
  "last_seen": 1741599611,
  "summary": {"distinct_ports": 10, "ports_sample": [22, 23, 25, 80, 110, 143, 443, 445, 3389, 9100],
              "protocols": ["TCP"]},
  "evidence": ["<one first-seen raw line per distinct port, ascending port order>"]
}
```

### 2.8 False-positive considerations

| Cause | Mitigation / analyst guidance |
|-------|-------------------------------|
| Monitoring/NMS probing many ports (e.g. Zabbix, Nessus) | Classic false positive; check whether source is a known scanner |
| P2P or mail servers with many ephemeral *source* ports | Not counted — the rule uses destination ports only |
| Proxy / NAT egress point touching many services | One NAT IP legitimately represents many internal clients |
| DNS/AD/domain controllers (udp/53, ldap, kerberos) | Broad legitimate port use; review protocol mix in summary |

### 2.9 Edge cases

| Case | Behaviour |
|------|-----------|
| 9 distinct ports + repeated hits on the same 9 | No finding (set size unchanged) |
| Same port, different dst_ip x20 | Counts once (port breadth, not host breadth) |
| ICMP event (no port) | Ignored by this rule (no dst_port field) |
| DPT=0 or DPT=70000 | Line malformed; excluded (FR-125) |
| 10 distinct ports across two files | One finding (grouping is per IP across the run) |

### 2.10 Acceptance criteria

- AC-003 (REQUIREMENTS.md §17): 10 distinct ports -> one finding; 9 -> none.
- R2-AC-01: 30 events over 9 ports -> no finding; repeat traffic is reflected in the
  intra-file `duplicates` statistic, not in the distinct count.
- R2-AC-02: invalid port lines counted as malformed and excluded (FR-125).
- R2-AC-03: cross-file duplicate handling verified per fingerprint with per-file
  multiplicity (intra-file repeats preserved).
- R2-AC-04: evidence contains exactly one first-seen raw line per distinct destination
  port, ordered by ascending port number.

---

## RULE 3 — LS-RULE-003: HTTP 4xx Abuse Detection

**Intent:** flag source IPs that elicit an abnormal volume of HTTP client-error responses —
typically content scanning, credential-stuffing against login forms, or forced-browsing.

### 3.1 Detection logic

1. Consider only `http_request` events, grouped by `src_ip` (FR-032, FR-034).
2. Filter to events with `400 <= status_code <= 499` (FR-124).
3. If `count(4xx) >= threshold` (default 8), raise **one** finding per source IP with:
   - `first_seen` / `last_seen` = min/max timestamps spanning the **qualifying 4xx events
     only** (non-4xx events never move the window),
   - evidence = the raw lines of **every qualifying 4xx event** — none are dropped at
     detection time (length capping happens later, at report rendering, see §4.4),
   - summary = `{"http_4xx_count": n, "status_histogram": {"404": x, "403": y, ...},
     "distinct_paths": d}` with the histogram sorted by status code.
4. There is **no time window** in v1 (same rationale as LS-RULE-002; documented).

### 3.2 Required event fields

| Field | Type | Constraint |
|-------|------|------------|
| `timestamp` | int (epoch s, UTC) | required |
| `src_ip` | str (IPv4) | must parse as IPv4 |
| `method` | str | informational |
| `path` | str | informational; used for `distinct_paths` |
| `status_code` | int | 100-599; outside range -> line malformed (FR-114) |

### 3.3 Threshold configuration

| Setting | Default | CLI override | Config file key |
|---------|---------|--------------|-----------------|
| 4xx count threshold | 8 | `--http-4xx-threshold N` | `http_4xx_threshold` |

(FR-032, FR-036, FR-140; precedence per AR-008.)

### 3.4 Handling of other status codes

- **1xx/2xx/3xx/5xx are ignored by this rule** but retained on the event and visible in
  the run statistics. Rationale:
  - 3xx redirects and 2xx successes are normal browsing; counting them would flood
    findings.
  - 5xx (server errors) indicate server-side faults, not client abuse; mixing them into a
    4xx count would misattribute outages to clients.
- The *rate* of 5xx from one IP is a plausible secondary signal (e.g. fuzzing causing
  crashes); it is deliberately deferred — do not silently fold it into this rule.
- Statuses outside 100-599 (e.g. 999) mark the line malformed; they are never counted.

### 3.5 Example input (synthetic)

```text
203.0.113.50 - - [10/Mar/2026:11:00:01 +0000] "GET /admin HTTP/1.1" 403 199
203.0.113.50 - - [10/Mar/2026:11:00:02 +0000] "GET /wp-login.php HTTP/1.1" 404 153
... (6 more 4xx at 11:00:03 .. 11:00:15) ...
203.0.113.50 - - [10/Mar/2026:11:00:15 +0000] "GET /.env HTTP/1.1" 404 0
```

### 3.6 Expected finding

```json
{
  "rule_id": "LS-RULE-003",
  "severity": "medium",
  "src_ip": "203.0.113.50",
  "first_seen": 1741605601,
  "last_seen": 1741605615,
  "summary": {"http_4xx_count": 8, "status_histogram": {"404": 7, "403": 1}, "distinct_paths": 8},
  "evidence": ["<raw line of every qualifying 4xx event, chronological>"]
}
```

### 3.7 False-positive considerations

| Cause | Mitigation / analyst guidance |
|-------|-------------------------------|
| Aggressive but legitimate crawlers / feed fetchers | Check user-agent (not parsed in v1 — evidence lines contain it) |
| Link rot: users following stale external links | 404 burst spread across many IPs and paths; single-IP concentration is the discriminator |
| Security scanners running with authorization | Same signature; operator context required |
| API clients in a broken integration loop | Often same path + same status; check `status_histogram` shape |
| Password-spray defenders: 401/403 bursts | This is exactly the intended catch — verify against auth logs |

### 3.8 Edge cases

| Case | Behaviour |
|------|-----------|
| 7 x 4xx + 5 x 200 from one IP | No finding (only 4xx count) |
| 8 x 4xx + 4 x 500 from one IP | One finding; 5xx excluded from count but events retained |
| Status 400 exactly at threshold-1/threshold | Counted (inclusive range 400-499, FR-124) |
| 8 identical 4xx lines in one file | 8 events counted individually (intra-file repeats preserved; `duplicates` statistic = 7); the threshold applies to the count, so the finding is raised exactly as for 8 distinct lines |
| HEAD/POST/OPTIONS methods | Counted — method-agnostic in v1 |
| Query strings in paths | Part of `path`; distinctness includes the full path string |

### 3.9 Acceptance criteria

- AC-004 (REQUIREMENTS.md §17): 8 x 4xx -> one finding; 7 -> none.
- R3-AC-01: status histogram and `distinct_paths` computed correctly.
- R3-AC-02: 2xx/3xx/5xx never counted (FR-124).
- R3-AC-03: status outside 100-599 -> malformed, excluded.
- R3-AC-04: cross-file duplicate handling verified per fingerprint with per-file
  multiplicity (intra-file repeats preserved and counted individually).

---

## 4. Shared Rule Semantics

### 4.1 Severity table (v1 fixed mapping)

| Rule | Severity | Rationale |
|------|----------|-----------|
| LS-RULE-001 | high | Repeated auth failures are the strongest compromise precursor of the three |
| LS-RULE-002 | medium | Reconnaissance pattern, no direct compromise evidence |
| LS-RULE-003 | medium | Abuse/scanning pattern, context-dependent |

Severity is fixed per rule in v1 (no scoring engine — out of scope, AR-011).

### 4.2 Finding identity and aggregation

- At most one finding per (rule, src_ip) per run (FR-122).
- Rule 1's multiple qualifying windows aggregate into a single merged union.
- Findings are ordered by **rule ID first** (LS-RULE-001/002/003), then **severity rank**
  (high > medium > low), then **source IP** ascending (FR-130). Within one rule there is
  at most one finding per IP, so the rule-then-IP order yields a deterministic report.

### 4.3 Threshold summary

| Rule | Threshold | Default | Window | Configurable |
|------|-----------|---------|--------|--------------|
| LS-RULE-001 | failed SSH auths per IP | 8 | 300 s sliding, half-open (AR-006) | threshold + window (FR-036) |
| LS-RULE-002 | distinct destination ports per IP | 10 | none (whole run) | threshold (FR-036) |
| LS-RULE-003 | 4xx responses per IP | 8 | none (whole run) | threshold (FR-036) |

### 4.4 Incremental detector processing and report sanitization

- Each detector supports **incremental aggregation**: `observe(event)` feeds
  one event into incremental per-IP aggregation state and `results()`
  finalizes the findings in deterministic rule-then-IP order. NFR-004 is
  satisfied by avoiding buffering of an entire file's (or run's) parsed
  events: the pipeline streams events through staging and lets each
  detector aggregate per source IP. Per-IP aggregation is the memory model
  explicitly permitted by NFR-004, but it is not a fixed upper memory bound:
  state and evidence retained per source IP can still grow with the number
  of events attributed to that IP (e.g. HTTP 4xx evidence is intentionally
  uncapped). Memory claims are therefore limited to "no full-file/full-run
  buffering" — constant or bounded per-IP memory is not claimed. The
  streaming CLI drives the three detector instances via
  `observe()`/`results()`; findings are identical by construction to the
  batch path because `detect(events)` is implemented on top of the same
  code path.
- `detect(events)` (and `run_all_detectors(events, config)`, which runs all three rules
  with thresholds from `AppConfig`) is retained as the **batch compatibility interface**
  for existing callers and tests.
- Report-level evidence sanitization (credential redaction) and length truncation
  (`MAX_EVIDENCE_LENGTH`) happen **after detection**, in the report rendering layer
  (FR-043): detectors attach full raw lines, and the renderer applies the evidence
  cap when displaying or serializing them.

## 5. Detection vs. Proof of Malicious Intent

LogSentinel is a **pattern detector, not a judge**. For every rule:

- The signature is purely statistical (counts, windows, distinct sets).
- Every rule has a documented false-positive section above; benign tools (scanners,
  monitors, broken integrations) trigger identical findings.
- Findings therefore use the language "suspicious pattern detected — manual review
  required"; reports never assert compromise, attribution, or intent.
- Evidence (raw lines) is always attached so a human can reach an independent conclusion.
- Any downstream automation that *acts* on LogSentinel findings (blocking, alerting) is
  outside LogSentinel's scope and responsibility (REQUIREMENTS.md §18).
