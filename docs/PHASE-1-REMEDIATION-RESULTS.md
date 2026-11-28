# LogSentinel Phase 1 — Remediation Results and Open Gates

**Mode:** controlled documentation and repository-audit work only.

**Disposition:** source publication is **NOT READY TO STAGE**. Windows GUI binary distribution remains **HOLD — NOT CLEARED FOR DISTRIBUTION**. This report is not owner approval, legal advice, rights clearance, or authorization to stage, commit, push, tag, release, or publish.

**Evidence basis:** the latest read-only disposition and checks against the current repository tree. Local workspace changes and checkpoint refs are preserved.

## Verified repository snapshot

### Audit baseline before this documentation task

| Item | Verified baseline |
|---|---|
| Branch | `main` |
| HEAD | `3229b17f9f0ae4fefc48e58f7a688f9250e1a117` |
| `origin/main` | `e5bcfd0d78cdb520025ff2cc2398aaaedb1fada0` |
| Branch relation | Local `main` is one commit ahead of `origin/main` (`git rev-list --left-right --count origin/main...main` = `0 1`). |
| Tracked paths | 87 |
| Modified tracked paths | 11 |
| Staged paths | 0 |
| Non-ignored untracked entries | 117: 20 under `docs/`, 96 under `licenses/`, and the reserved `NUL` entry. |

### After this documentation task

| Item | Verified result |
|---|---|
| Branch / HEAD | `main` / `3229b17f9f0ae4fefc48e58f7a688f9250e1a117` (unchanged) |
| `origin/main` | `e5bcfd0d78cdb520025ff2cc2398aaaedb1fada0` (unchanged); local branch remains one commit ahead |
| Tracked paths | 87 |
| Modified tracked paths | 13 (the 11 pre-existing changes plus `PROJECTMAP.md` and `docs/ARCHITECTURE.md`; README was already modified) |
| Non-ignored untracked entries | 120: 23 under `docs/`, 96 under `licenses/`, and the preserved reserved `NUL` entry |
| Staged paths | 0 |

No staging index was created or changed; the Git index remains untouched.

## Verified technical results and limitations

- **Full local suite:** 556 tests discovered; **546 passed, 10 skipped**, no failures/errors, as recorded for this audited worktree using the existing environment. No dependency installation was performed for this documentation task.
- **Focused GUI suite:** **140 passed**, no failures/errors/skips, as recorded for the same local worktree.
- **Hosted Actions:** no matching hosted Actions run was found for the exact audited HEAD `3229b17f9f0ae4fefc48e58f7a688f9250e1a117`. Configured Ubuntu/Windows workflow jobs and local test passes are not hosted CI evidence.
- **Packaging:** no clean packaging build or binary smoke validation was performed or authorized in this task. The existing onedir-spec worktree change was preserved.
- **Limits:** local tests establish only the behavior covered by those test runs. They do not establish authorship, rights, legal originality, license scope, source-publication approval, or binary distribution permission.

## Source-publication proposal status

The older 61-path candidate in `PHASE-1-GITHUB-SOURCE-PUBLICATION-MANIFEST.md` was insufficient for the intended complete CLI-plus-GUI source scope. It omitted `PROJECTMAP.md`, `tests/test_gui_themes.py`, both GUI PyInstaller specifications, and `packaging/gui_entry.py`; it also left all 23 GUI assets out. The 61-path list is not owner-approved, not a final index, and not ready to stage.

The refreshed path-by-path proposal in [`PHASE-1-FINAL-SOURCE-PUBLICATION-MANIFEST.md`](PHASE-1-FINAL-SOURCE-PUBLICATION-MANIFEST.md) enumerates 207 current non-ignored entries (including the reserved `NUL` row and the manifest itself): 62 PROPOSED INCLUDE, 144 HOLD, and 1 EXCLUDE. The target remains a complete CLI-plus-GUI source tree. Source paths needed for the GUI are proposed for inclusion only subject to review; all 23 artwork files remain HOLD pending external evidence. `tests/test_gui_themes.py` is PROPOSED INCLUDE for the complete GUI source set, conditional on resolving and including its required artwork; the three packaging paths remain HOLD pending recipe review and separately authorized validation. No source-scope downgrade to CLI-only is made.

### Confirmed tracked HOLD discrepancy and artwork inventory

The repository contains **28 tracked HOLD paths** in the earlier manifest’s classification. The earlier audit heading said “28,” while its prose called the set “27”; the exact listed paths reconcile to 28. This refresh changes `PROJECTMAP.md` and `tests/test_gui_themes.py` to PROPOSED INCLUDE (the test remains dependent on the held artwork), leaving 26 of those baseline paths on HOLD (23 artwork files and three packaging paths). That source-map classification is a proposal, not publication approval.

All 23 GUI artwork resources remain **HOLD**, exactly:

- `src/logsentinel/gui/assets/brand/logsentinel-appicon.svg`
- `src/logsentinel/gui/assets/brand/logsentinel-logo.svg`
- `src/logsentinel/gui/assets/brand/logsentinel-mark.svg`
- `src/logsentinel/gui/assets/brand/logsentinel-sidebar.svg`
- `src/logsentinel/gui/assets/icons/alert.svg`
- `src/logsentinel/gui/assets/icons/check.svg`
- `src/logsentinel/gui/assets/icons/detections.svg`
- `src/logsentinel/gui/assets/icons/download.svg`
- `src/logsentinel/gui/assets/icons/file_plus.svg`
- `src/logsentinel/gui/assets/icons/file_text.svg`
- `src/logsentinel/gui/assets/icons/folder_open.svg`
- `src/logsentinel/gui/assets/icons/log_explorer.svg`
- `src/logsentinel/gui/assets/icons/overview.svg`
- `src/logsentinel/gui/assets/icons/palette.svg`
- `src/logsentinel/gui/assets/icons/play.svg`
- `src/logsentinel/gui/assets/icons/reports.svg`
- `src/logsentinel/gui/assets/icons/search.svg`
- `src/logsentinel/gui/assets/icons/settings.svg`
- `src/logsentinel/gui/assets/icons/shield_check.svg`
- `src/logsentinel/gui/assets/icons/stop.svg`
- `src/logsentinel/gui/assets/icons/trash.svg`
- `src/logsentinel/gui/assets/icons/x.svg`
- `src/logsentinel/gui/assets/logsentinel.ico`

Four files (`check.svg`, `download.svg`, `folder_open.svg`, `x.svg`) have identified Lucide geometry matches; those comparisons do not establish historical copying, authorship, license scope, or permission. The separate [`PHASE-1-ARTWORK-PROVENANCE-EVIDENCE-REQUESTS.md`](PHASE-1-ARTWORK-PROVENANCE-EVIDENCE-REQUESTS.md) requests item-specific evidence for each file. No evidence is invented and no held asset was changed, replaced, moved, or integrated.

## Licensing collection and local-history findings

- **Licensing corpus:** 96 files currently exist under `licenses/`. The collection remains uncurated and all files remain HOLD. It mixes internal provenance/release assessments, candidate and alternative license texts, upstream notices, and incomplete package evidence. It is not treated as a complete recipient notice set or blanket rights clearance.
- **Anomalous local file:** the unrelated `release/LogSentinel-Windows-v0.1.0/from pyzbar import pyzbar.py` file is not in the `main` or `origin/main` trees. Read-only tree checks found it in **10 of 31** local `refs/t3/orchestration-v2/checkpoints/*` refs. The file and history were not modified. Its provenance and personal-data-shaped content remain unresolved; it is excluded from source scope.
- **Refs and push configuration:** the inspected Git config has no explicit `remote.origin.push`, `push.default`, or `branch.main.pushRemote`. The intended push refspec and exact refs to send have not been verified. Checkpoint-ref exclusion is not recorded as an owner decision; preserve all refs and obtain explicit review before any later publication action. No all-refs/mirror push is authorized.
- **NUL:** the reserved root `NUL` entry remains untouched and is excluded from any publication proposal.

## Unresolved external evidence and owner decisions

The following cannot be resolved from repository mechanics or test results:

1. Obtain creator/rightsholder, source/design file, date/revision history, upstream version/commit where relevant, modification history, tools/fonts/templates/libraries, and applicable redistribution license or written permission for every GUI artwork path; then record required notices.
2. Decide whether internal Phase 1 assessment/control reports should be disclosed publicly. They remain HOLD in the proposal pending that owner decision.
3. Review the exact existing onedir-spec diff, reconcile one-file/onedir differences, and authorize any clean build/smoke validation separately. Both specs and `packaging/gui_entry.py` remain HOLD pending that review and validation.
4. Decide the exact public refs/refspec and explicitly address checkpoint-ref exclusion; verify hosted CI for the intended source revision if available.
5. Approve the exact final source paths/index separately before any staging. This report and the manifest do not constitute approval.

## Separate Windows binary-release gates (six)

These gates are independent of the source-publication proposal. The local EXE and ZIP remain on distribution HOLD.

1. **Release model:** define recipient, territory, distribution channel, exact package format/scope, end-user terms, update/signing/anti-tamper model, and final artifact set.
2. **Qt/PySide/Shiboken:** resolve the applicable license election and exact binary/source/build/translation mapping, including any applicable source, relink, or replacement route with qualified review.
3. **Microsoft runtime:** establish provenance and redistribution rights/terms for every bundled VC++ runtime copy.
4. **Other components/notices:** complete file-level component, source, license, and recipient-notice mapping for CPython, PyInstaller, Qt-linked/native components and other shipped material; resolve alternatives and gaps.
5. **Support/replacement:** validate the declared Windows support matrix and any applicable recipient replacement/relink workflow against the final artifact; prepare only artifact-matched source/instructions where required.
6. **Approval tied to artifact:** obtain written release-owner and qualified-counsel approval for the final package hash and channel; recompute hashes/checksum manifest after any separately authorized changes.

Hash matching, ZIP integrity, tests, or recipe/build success would not themselves satisfy these release gates or authorize distribution.

## Work completed under this request

- Refreshed `PROJECTMAP.md` to describe the current CLI, optional GUI architecture, test/documentation/packaging layout, and explicit HOLD/readiness boundaries.
- Reconciled README and architecture documentation to the 556/140 local results, exact-HEAD hosted-CI absence, optional GUI status, source-publication hold, and independent binary hold.
- Created this remediation-results record, the item-by-item final source-publication proposal, and the 23-entry artwork evidence-request document.
- Preserved all existing source, assets, licensing material, release artifacts, the `NUL` entry, local checkpoint refs, branch history, remotes, push settings, and the Git index. No dependencies were installed; no packaging build was performed; no staging/publication action occurred.

## Validation performed for this documentation update

- The final proposal contains 207 unique rows and exactly covers the current 87 tracked paths, 120 non-ignored untracked entries, and its own manifest row. It currently has 62 PROPOSED INCLUDE, 144 HOLD, and 1 EXCLUDE. Every listed regular-file size/hash was recomputed against the live file; zero mismatches were found. The manifest excludes a self-hash by design; its final digest is in the completion report.
- Confirmed 23 artwork entries and 96 `licenses/` paths are all HOLD; `tests/test_gui_themes.py` is proposed for inclusion subject to the held artwork; both specs and `packaging/gui_entry.py` remain HOLD.
- Confirmed 23 numbered, path-specific artwork evidence requests. They request creator/source/rights evidence without asserting unknown facts.
- Checked eight maintained/updated Markdown documents, 20 Markdown link references, local target/anchor references, fenced code-block balance, final newlines, heading formatting, and trailing whitespace: **0 detected issues**. This is a lightweight local checker, not a complete CommonMark parser; external URL reachability is **NOT VERIFIED**.
- `git diff --check` and `git diff --cached --check` passed. Git emitted only existing LF/CRLF conversion warnings. No tests were rerun during this documentation-only task; the cited 556/140 results are the verified audit-baseline results above.
- No clean packaging build was run. Intended push refs/refspec and checkpoint-ref exclusion approval remain **NOT VERIFIED**. No dependency was installed, no Git index operation occurred, and no staged path exists.

Exact byte sizes and SHA-256 digests for all new deliverables and updated documentation are reported in the completion response. The manifest’s own digest is reported there because embedding it would change the manifest.
