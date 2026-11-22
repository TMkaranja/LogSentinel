# LogSentinel — Security Audit and Remediation Record

- **Document:** SECURITY_AUDIT.md
- **Status:** findings R1–R5 recorded; R2, M6, and M1 remediations verified and committed; FR-162 staged-path remediation verified and committed
- **Related requirements:** FR-162 and NFR-009 (docs/REQUIREMENTS.md §14/§15)

## 1. Audit Scope and Context

This record documents a read-only security-redaction review of LogSentinel's
handling of potentially sensitive log content — where raw log lines can enter the
application, what is stored during processing, and what can reach reports or
standard error. The relevant requirements are **FR-162** (credential-bearing
fields shall never be extracted, stored, or echoed even if present in raw lines)
and **NFR-009** (reports shall avoid emitting secrets found in logs).

This document records security findings and their remediation status. It is **not
a replacement for the requirements**: FR-162 and NFR-009 remain the approved
requirements, and the open findings below mean neither requirement may be
described as fully satisfied.

Terminology note: the finding IDs **R1–R5** in this document are the security
review's own numbering. They are unrelated to the Phase 3 design risks
`R-01`–`R-08` recorded in docs/PHASE3_VALIDATION.md §12, and unrelated to the
detection rule `LS-RULE-002` (port-scan detection).

## 2. Findings Register

| ID | Finding | Impact | Status |
|----|---------|--------|--------|
| **R1** | Sensitive raw lines in temporary SQLite staging | *Historical (resolved for the identified path):* raw log lines — which could contain credentials — were once stored verbatim in the temporary SQLite staging database during processing, leaving plaintext secrets on disk for the run's duration. Commit `37d19de` (M1) replaced this with sanitized evidence lines and per-run keyed HMAC fingerprints; the database now contains no raw-line column or raw-line index. | **RESOLVED for the identified path** (residual risks remain — see §4) |
| **R2** | Strict-mode stderr leakage | Strict-mode abort messages could expose sensitive tokens embedded in parser diagnostic reasons (e.g. invalid-IP validation errors echo the offending token from the log line). The message is now sanitized before being returned and printed. | **RESOLVED for the identified path** (see §3) |
| **R3** | Unexpected exception output | The unexpected-failure diagnostic (exit code 3) printed the raw exception message to stderr; that text could expose log-derived content in arbitrary failure cases. The message is now sanitized (best-effort, single shared sanitizer) before printing; the exception class name, short-diagnostic behaviour and exit code 3 are unchanged. | **RESOLVED for the identified output path** (best-effort limitations apply — see §4) |
| **R4** | Source-path redaction | Source paths appeared in externally visible error outputs (JSON error entries length-capped but not redacted; strict-mode abort diagnostics echoed the full uncapped path); a credential-shaped path name or OS username could survive into the output. Output paths are now replaced with the neutral marker `[REDACTED_PATH]`. | **RESOLVED for externally visible outputs** (source paths remain internally and in temporary storage — see §4) |
| **R5** | Redaction bypass limitations | The redaction is best-effort: it matches credential-shaped key/value pairs and credential-bearing headers only. Two narrow authorized vocabulary extensions added the explicit key families `access_key`, `private_key`, `session_key`, `credential`/`credentials`, and — second extension (commit `0280615`) — `sess`/`session`/`sessionid`/`session_id`, `passphrase`, `pass_word`/`pass-word`, and `signature`, plus whole-remainder redaction for the credential-bearing headers `Cookie`, `Set-Cookie`, and `Proxy-Authentication` (hyphen and underscore forms); it cannot guarantee detection of every secret format or encoding (bare tokens, unrecognized key names, generic `key`/`pin`, unkeyed JWT material, bare Basic-auth/base64 credentials outside a recognized header, separator variations, multi-line secrets, non-percent encodings). This is a documented design limitation, not a defect introduced by the R2 fix. | **OPEN** (vocabulary gap for the added families resolved; broader limitations remain) |

No findings beyond R1–R5 are recorded here, and the open findings have not been
fixed.

## 3. R2 Remediation Evidence

- **Commit:** `9393229` — `Fix strict-mode error message sanitization`.
- **Files changed:** `src/logsentinel/cli.py` and `tests/test_cli.py`.
- **Implementation:** `cli.py` now imports the report layer's existing sanitizer
  (`_sanitize`) and applies it to the error reason when composing the
  strict-mode abort message (`_strict_abort()`): `strict mode abort:
  {_sanitize(entry.reason)} (…)`. The report layer's single redaction
  implementation is reused — no second, inconsistent sanitizer was created.
  Message structure, exception-type mapping, and the strict-mode exit code (2)
  are unchanged; normal-mode reporting and unexpected-exception handling were
  not modified.
- **Regression test:** `tests/test_cli.py` —
  `TestErrorHandling.test_strict_abort_reason_sanitized_on_stderr`. It feeds a
  strict-mode run an SSH line whose invalid "IP" token embeds a
  credential-shaped value (`password=hunter2`), captures stderr, asserts the
  strict abort still exits with code 2, asserts the `<REDACTED>` marker is
  present, asserts the secret value `hunter2` is absent, and asserts the
  diagnostic context (source file name) is preserved. It would fail against the
  pre-fix implementation.
- **Full suite result (verified locally, canonical command
  `python -W error::ResourceWarning -m unittest discover`):** **355 tests, OK,
  9 skipped** — no failures or errors. (The suite grew from 354 to 355 with the
  regression test.)
- **Hosted GitHub Actions run:** `45025411430` — workflow result **Success**,
  triggered by the push of commit `9393229` to `main`, `ubuntu-latest`, Python
  3.14.
- **Scope of resolution:** this evidence resolves **R2's identified
  strict-mode stderr exposure path only**. It does not resolve R1, R3, R4, or
  R5, and does not close the broader credential-exposure concerns described in
  §4.

## 4. Outstanding Risks

- **R1 (RESOLVED for the identified path — commit `37d19de`, "Add per-run
  HMAC fingerprints and sanitized staging (M1)"):** raw log lines are no
  longer stored in SQLite. The `events` table now holds `evidence_line
  TEXT` (the sanitized original line) and `fp_digest BLOB` (a per-run
  keyed HMAC-SHA256 digest of the exact identity ``(kind, timestamp,
  raw_line)``); the former `raw_line` column and raw-line index were
  removed. Evidence and error reasons are sanitized before persistence:
  `evidence_line` is sanitized at staging, and error reasons are
  sanitized at `ErrorEntry` construction (commit `58d1806`, M6). The
  HMAC key is 32 bytes from `secrets.token_bytes`, generated once per
  `RunStorage` instance, held only in memory for the instance lifetime,
  and never persisted, logged, or reported; the same key is used across
  transaction rollback and UTF-8 retry, and every new run generates a
  fresh key. Digests are computed from the original identity before
  sanitization, using a domain-separated, length-prefixed encoding
  (`LogSentinel:event-fingerprint:v1\0` plus length-prefixed fields and
  a fixed-width signed 64-bit timestamp).

  The per-run key means fingerprints from one run cannot be matched
  against fingerprints from another run, preventing straightforward
  cross-run fingerprint correlation. Within a single run's database,
  however, repeated identical events still produce identical digests, so
  the fingerprints expose equality patterns (how often each exact event
  identity occurred) to anyone who can read the database file.
  Association with files is available through the separately stored
  `source_file` field.

  Evidence: `tests/test_storage.py::TestHmacFingerprints` (11 tests,
  including no-`raw_line`-in-any-DDL, plaintext-absence from the database
  file at rest, key non-persistence and non-exposure, rollback/retry key
  stability, and adversarial unambiguous encoding); full suite at HEAD
  `37d19de`: 372 tests OK, 9 skipped.

  **R1 residual risks (documented, not eliminated):**
  (a) sanitization is best-effort — unrecognized secret formats may
  remain in `evidence_line`; (b) other parsed fields that are still
  stored — `username`, `method`, `src_ip`, `dst_ip`, and
  `source_file` — may themselves contain sensitive information
  (credential-bearing HTTP paths were the most sensitive of these and
  are now remediated at staging time — see the FR-162 staged-path
  remediation below); (c) abnormal termination (kill, power loss) can leave the temporary
  SQLite file behind, containing sanitized evidence, sanitized error
  reasons, parsed fields, and digests; residue can remain until a later
  application initialization sweeps it (see the lifecycle controls
  below), and cleanup cannot be guaranteed if the application never runs
  again or filesystem/OS failures prevent deletion; (d) HMAC-SHA256
  carries a theoretical collision risk — within practical keyed-collision
  resistance, digest equality stands in for exact identity, and the
  per-run key prevents straightforward fingerprint matching across runs,
  but does not prevent identification through other stored database
  fields or evidence; (e) the sanitizer bypass classes documented
  under R5 apply to staged `evidence_line` exactly as they do to
  reports, so unrecognized secrets can persist there. These residuals
  mean **FR-162 is not fully satisfied**: literal compliance — that
  credential-bearing fields are never stored — is not demonstrated,
  because unrecognized secret formats and other parsed fields can still
  be persisted in sanitized or parsed form.

  **R1 lifecycle controls (implemented after the storage change above; a
  separate, safer lifecycle-coordination step — this is distinct from the
  M1 data change and does not by itself address evidence sanitization):**
  - a **persistent global cleanup lock** (`<system temp
    dir>/logsentinel-cleanup.lock`, never removed) serializes owned
    directory creation, sweeping, and teardown;
  - each owned run directory contains a **per-run lock** (`run.lock`)
    held for the run's entire lifetime, protecting active owned runs;
  - every subsequent owned `RunStorage` initialization **sweeps eligible
    abandoned directories**: candidates are `logsentinel-run-*`
    directories strictly older than **24 hours** (directory mtime basis)
    whose contents are exclusively recognized LogSentinel artifacts;
  - the sweeper uses **non-blocking** run-lock acquisition (an active run
    keeps its lock and is never touched), revalidates each candidate
    under the global lock and again after per-run lock acquisition, and
    removes only directories containing recognized artifacts
    (`staging.sqlite3` and/or `run.lock`);
  - foreign or malformed contents, symlinks, and Windows reparse points
    (junctions) are skipped, never deleted;
  - cleanup failures (including global-lock acquisition failures, which
    skip destructive cleanup and leave the instance retryable) remain
    observable in `cleanup_errors`. Tests: `tests/test_storage.py`
    (`TestCleanupLocks`, `TestStaleSweeper` — locking, contention,
    retryability, sweeper gating and path-safety coverage).
- **R3 (RESOLVED for the identified output path):** the outermost CLI
  exception boundary (`cli.py`, `except Exception` arm) now applies the single
  shared sanitizer (`_sanitize`) to the exception message text before printing
  it to stderr. The exception **class name** is code-side context, not
  log-derived, and is preserved; the diagnostic prefix, stderr destination,
  short-diagnostic behaviour (no traceback, FR-153) and exit code 3 are
  unchanged, and the FR-153 contract text is not modified. Regression test:
  `tests/test_cli.py::TestErrorHandling.test_unexpected_exception_message_sanitized`
  (a detector failure whose message embeds `password=hunter2` produces
  `<REDACTED>` on stderr, with the secret value absent, class name retained,
  exit code 3, and no traceback — it would fail under the previous raw
  `str(exc)` implementation). **Best-effort limitation (R5 applies):** the
  sanitizer recognizes only credential-shaped key/value patterns and
  Authorization headers; unrecognized secret formats in an exception message
  are not detected and could still reach stderr. Unknown future failure modes
  may also produce message shapes the sanitizer handles differently (e.g.
  truncation at 256 characters), which is acceptable for a short diagnostic.
- **R4 (RESOLVED for externally visible outputs):** source paths are replaced
  with the neutral marker `[REDACTED_PATH]` in JSON report error entries and in
  strict-mode abort diagnostics (line number and kind preserved — they are not
  path information). Console reports never rendered paths. The marker is
  defined once in the leaf event module (`events.py`) and applied at both output
  boundaries (`report.py::_error_to_json`, `cli.py::_strict_abort`); internal
  source-path association (storage, staging, event association, reconstruction)
  is unchanged, and the caller's `ErrorEntry` object is not mutated. Regression
  tests assert that Windows and POSIX absolute paths — including usernames,
  directory structure and credential-shaped filenames — never appear in the JSON
  report, that strict-abort messages no longer name the file, and that internal
  association still works (tests would fail under the previous capping-only
  implementation). **Distinction:** this remediates *output* redaction only —
  source paths are still retained internally, staged in the temporary SQLite
  database, and (as with any temporary file) can survive abnormal termination;
  at-rest source-path exposure is not eliminated.
- **R5 (OPEN — narrowed twice, not closed):** the shared `_SECRET_KV` key
  vocabulary was extended (authorized narrow extension) to also recognize the
  explicit key families `access_key`/`access-key`, `private_key`/`private-key`,
  `session_key`/`session-key` (including separator-free forms such as
  `accesskey`), and `credential`/`credentials` — case-insensitive, with the
  same separator and value shapes as before; existing key names are unchanged,
  and ordinary fields sharing word prefixes (`client_id`, `keyboard`,
  `monkey`) are not redacted (regression-tested). A second authorized narrow
  extension (commit `0280615`) added the explicit key families
  `sess`/`session`/`sessionid`/`session_id`, `passphrase`,
  `pass_word`/`pass-word`, and `signature` (still whole-word under the same
  boundary structure, so compounds such as `account_password_reset` and
  `signature_algorithm` are not redacted), and extended the whole-remainder
  header rule beyond `Authorization` to `Cookie`, `Set-Cookie`, and
  `Proxy-Authentication` (hyphen and underscore forms), whose values —
  session identifiers or credentials — are treated as opaque exactly like
  `Authorization`. This resolves the specific
  vocabulary gaps for those families **only**. The broader detection
  limitations remain and R5 stays open: best-effort redaction still misses
  unkeyed/bare secrets, unknown key vocabularies, unusual separators,
  multi-line secrets, and non-percent encodings; no entropy heuristics,
  generic `key` suffix or `pin`, `ssh_key`, `client_id` matching, unkeyed
  JWT detection, bare Basic-auth/base64 detection, or multiline
  PEM detection were added (explicitly out of scope). Closing R5 fully is a
  significant design change; the current behaviour is documented in
  docs/USAGE.md §8.4 and docs/ARCHITECTURE.md §9.
- **FR-162 staged HTTP-path persistence (RESOLVED for recognized
  credential patterns — commit `259ca94`, "Redact credential-bearing
  HTTP paths at staging"):** a confirmed at-rest exposure was
  demonstrated: a parsed HTTP `path` field such as
  `/login?password=hunter2` was persisted verbatim in the `events`
  table while the same row's `evidence_line` was sanitized — the
  credential value remained recoverable from the database.
  Remediation: `RunStorage.stage_event` now applies the shared
  `events.py` redaction (`_redact`, the single existing implementation —
  no second vocabulary) to the persisted `path` column only, so
  credential-bearing values in recognized key families
  (`password=`, `token=`, `api_key=`, `session_id=`, cookie/Authorization
  headers, and the other approved patterns) are replaced with
  `<REDACTED>` before SQLite persistence. The evidence-length cap is
  deliberately NOT applied to parsed paths (redaction only). The
  in-memory event object is never mutated, so detectors observe the
  original path; the per-run HMAC fingerprint continues to be computed
  over the original unsanitized `(kind, timestamp, raw_line)` identity;
  deduplication, UTF-8 rollback/retry, replay reconstruction, and report
  output are unchanged. The SQLite schema and docs/REQUIREMENTS.md were
  not modified. Ordinary paths, query parameters, usernames, IP
  addresses, ports, timestamps, and source-file information are
  preserved byte-identically unless they contain a recognized
  credential-bearing value. Evidence: `tests/test_storage.py`
  (`TestStagedPathRedaction`, 7 regression tests — redaction of
  credential values in staged paths, ordinary-path preservation, no
  evidence cap on parsed paths, in-memory event non-mutation, ordinary
  SSH usernames unchanged, replay round-trip, and dedup/fingerprint
  over the original line); full local suite at the change: **416 tests,
  OK, 10 skipped, zero failures** (canonical command
  `python -W error::ResourceWarning -m unittest discover`); hosted
  GitHub Actions run `45070480433` — Ubuntu/Python 3.14 and
  Windows/Python 3.14 both passed. **Limitations (unchanged):** the
  redaction is pattern-based and recognizes only the approved
  vocabulary; unrecognized secret formats inside a `path` value are
  still persisted, and the remaining stored parsed fields (`username`,
  `source_file`, and address/port fields) are not sanitized. This
  remediation therefore does not claim universal credential protection
  or complete literal compliance with every part of FR-162.
- **R2's resolution is narrow.** It fixes one identified stderr exposure path.
  It does not make redaction universal, does not change what is stored in
  SQLite staging, and does not satisfy FR-162 or NFR-009 in full.

## 5. Overall Security Assessment

- Best-effort redaction is **not a guarantee of complete secret protection**.
  The length cap is a backstop, not a security boundary: a 256-character
  evidence cap does not ensure that secrets cannot leak.
- **R1 at-rest exposure is reduced, not eliminated.** The M1 data change
  (sanitized evidence, per-run HMAC fingerprints) is complemented by R1
  lifecycle controls: a persistent global cleanup lock serializing creation,
  sweeping, and teardown; per-run locks protecting active runs; and automatic
  sweeping of abandoned owned directories older than 24 hours (mtime) during
  subsequent owned initializations. Abnormal-termination residue can still
  persist until a later initialization sweeps it, and cleanup cannot be
  guaranteed if the application never runs again or filesystem/OS failures
  prevent deletion; at-rest parsed fields other than HTTP paths (which are
  now redacted at staging for recognized credential patterns — commit
  `259ca94`) and unrecognized secret formats remain as described in §4.
- **NFR-009 is PARTIALLY SATISFIED.** Reports protect recognized secret
  patterns at every external boundary (sanitized evidence, sanitized error
  reasons, `[REDACTED_PATH]`, count-only summaries), but the protection is
  inherited from the same pattern-based sanitizer: secret formats the matcher
  does not recognize may still reach reports through evidence lines or
  diagnostic text. NFR-009 is therefore not universally satisfied, and the
  same R5 limitations govern both FR-162 and NFR-009.
- **FR-162 and NFR-009 must not be described as fully satisfied** while the
  documented gaps (R5, and R1's residual risks) remain unresolved. The staged
  HTTP-path persistence issue is remediated for recognized credential
  patterns, but redaction is pattern-based: it cannot guarantee detection of
  unknown secret formats, and credential-bearing values in unrecognized
  vocabularies can still be stored in evidence and parsed fields. No claim
  of universal credential protection or complete literal FR-162 compliance
  is made. The accurate public
  position — already stated in docs/USAGE.md §8.4 and docs/ARCHITECTURE.md §5 —
  is that redaction is best-effort and users should not feed secret-bearing
  logs to tools they do not trust.
- Findings R5 remains open for future remediation decisions;
  R1, R2, R3, and R4 are resolved for their identified paths with documented
  residuals (R1: at-rest sensitivity and abnormal-termination residue; R3:
  best-effort sanitizer limitations; R4: at-rest source-path exposure in
  temporary storage).
