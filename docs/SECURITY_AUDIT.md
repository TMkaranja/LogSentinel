# LogSentinel — Security Audit and Remediation Record

- **Document:** SECURITY_AUDIT.md
- **Status:** findings R1–R5 recorded; R2 remediation verified and committed
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
| **R1** | Sensitive raw lines in temporary SQLite staging | Raw log lines — which can contain credentials — are stored verbatim in the temporary SQLite staging database during processing (needed for evidence reconstruction). The database is deleted when the run ends, but secrets exist in plaintext on disk for the run's duration. | **OPEN** |
| **R2** | Strict-mode stderr leakage | Strict-mode abort messages could expose sensitive tokens embedded in parser diagnostic reasons (e.g. invalid-IP validation errors echo the offending token from the log line). The message is now sanitized before being returned and printed. | **RESOLVED for the identified path** (see §3) |
| **R3** | Unexpected exception output | The unexpected-failure diagnostic (exit code 3) prints the exception text to stderr; that text is not sanitized and could expose sensitive information in arbitrary failure cases. | **OPEN** |
| **R4** | Source-path redaction | `source_file` values are length-capped in reports but are not comprehensively redacted; a credential-shaped path name could survive into the report (truncated). | **OPEN** |
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

- **R1 (OPEN):** while a run is active, raw lines containing credentials sit in
  the temporary staging database in plaintext. Storing raw lines is a current
  design requirement (evidence reconstruction), so resolving R1 requires an
  explicit decision: accept and document the temporary-storage exposure, or
  redesign evidence handling. Until then, processed logs with secrets leave
  readable traces in the system temporary directory for the duration of a run.
- **R3 (OPEN):** unexpected-failure stderr output is unsanitized by design
  (short diagnostics for exit code 3). A failure whose exception text contains
  log-derived content could expose it. Bounding or sanitizing this output
  changes the FR-153 diagnostic contract and requires authorization.
- **R4 (OPEN):** source paths are truncated but not redacted; a path containing
  credential-shaped text can appear (truncated) in reports.
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
  documented gaps (R1, R3, R4, R5) remain unresolved. The accurate public
  position — already stated in docs/USAGE.md §8.4 and docs/ARCHITECTURE.md §5 —
  is that redaction is best-effort and users should not feed secret-bearing
  logs to tools they do not trust.
- Findings R1, R3, R4, and R5 remain open for future remediation decisions.
