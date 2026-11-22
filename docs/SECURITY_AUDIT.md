# LogSentinel — Security Audit and Remediation Record

- **Document:** SECURITY_AUDIT.md
- **Status:** findings R1–R5 recorded; R2, M6, and M1 remediations verified and committed
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
| **R3** | Unexpected exception output | The unexpected-failure diagnostic (exit code 3) prints the exception text to stderr; that text is not sanitized and could expose sensitive information in arbitrary failure cases. | **OPEN** |
| **R4** | Source-path redaction | Source paths appeared in externally visible error outputs (JSON error entries length-capped but not redacted; strict-mode abort diagnostics echoed the full uncapped path); a credential-shaped path name or OS username could survive into the output. Output paths are now replaced with the neutral marker `[REDACTED_PATH]`. | **RESOLVED for externally visible outputs** (source paths remain internally and in temporary storage — see §4) |
| **R5** | Redaction bypass limitations | The existing redaction is best-effort: it matches credential-shaped key/value pairs and Authorization headers only. It cannot guarantee detection of every secret format or encoding (bare tokens, unrecognized key names, separator variations, multi-line secrets, non-percent encodings). This is a documented design limitation, not a defect introduced by the R2 fix. | **OPEN** |

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
  stored — `username`, `path`, `method`, `src_ip`, `dst_ip`, and
  `source_file` — may themselves contain sensitive information;
  (c) abnormal termination (kill, power loss) can leave the temporary
  SQLite file behind, containing sanitized evidence, sanitized error
  reasons, parsed fields, and digests; (d) HMAC-SHA256 carries a
  theoretical collision risk — within practical keyed-collision
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
- **R3 (OPEN):** unexpected-failure stderr output is unsanitized by design
  (short diagnostics for exit code 3). A failure whose exception text contains
  log-derived content could expose it. Bounding or sanitizing this output
  changes the FR-153 diagnostic contract and requires authorization.
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
- **R5 (OPEN):** best-effort redaction misses unkeyed secrets, unknown key
  vocabularies, unusual separators, multi-line secrets, and non-percent
  encodings. Closing R5 fully is a significant design change; the current
  behaviour is documented in docs/USAGE.md §8.4 and docs/ARCHITECTURE.md §5.
- **R2's resolution is narrow.** It fixes one identified stderr exposure path.
  It does not make redaction universal, does not change what is stored in
  SQLite staging, and does not satisfy FR-162 or NFR-009 in full.

## 5. Overall Security Assessment

- Best-effort redaction is **not a guarantee of complete secret protection**.
  The length cap is a backstop, not a security boundary: a 256-character
  evidence cap does not ensure that secrets cannot leak.
- **FR-162 and NFR-009 must not be described as fully satisfied** while the
  documented gaps (R3, R5, and R1's residual risks) remain unresolved. The accurate public
  position — already stated in docs/USAGE.md §8.4 and docs/ARCHITECTURE.md §5 —
  is that redaction is best-effort and users should not feed secret-bearing
  logs to tools they do not trust.
- Findings R3, R4, and R5 remain open for future remediation decisions;
  R1 and R2 are resolved for their identified paths with documented residuals.
  (R4's residual: at-rest source-path exposure in temporary storage.)
