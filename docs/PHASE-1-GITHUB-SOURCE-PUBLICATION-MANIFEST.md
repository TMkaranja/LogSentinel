# LogSentinel Phase 1 — GitHub Source Publication Manifest

**Purpose:** define an evidence-based candidate file set for a source-only GitHub repository publication. This is a manifest and review aid, **not** an authorization to stage, commit, push, publish, distribute binaries, or a legal opinion.

> **Superseded proposal:** this earlier 61-path candidate is retained as a historical review record only. The intended target is now a complete CLI-plus-GUI source set. Use [`PHASE-1-FINAL-SOURCE-PUBLICATION-MANIFEST.md`](PHASE-1-FINAL-SOURCE-PUBLICATION-MANIFEST.md) for the current path-by-path proposal. Neither document is owner-approved or ready to stage.

**Binary status:** the Windows GUI candidate remains **HOLD — NOT CLEARED FOR DISTRIBUTION**. No executable, installer, ZIP, generated package, or binary release asset is included or approved by this manifest. The root MIT `LICENSE` applies to LogSentinel project material as stated in that file; it does not establish third-party rights or clearance for a compiled GUI package.

**Snapshot:** local branch `main`, HEAD `3229b17`; `origin/main` at `e5bcfd0`; local `main` is one commit ahead. At inventory time there were **87 tracked paths**, **66 non-ignored untracked paths**, and no staged paths. Four tracked files were modified (`.gitignore`, `README.md`, `docs/USAGE.md`, `packaging/LogSentinel-GUI-Onedir.spec`). The User Guide and two publication-review documents were untracked. Ignored local outputs and checkpoint refs also exist and are accounted for below.

## 1. Intended scope and disposition

The intended public repository is the **LogSentinel Phase 1 source project**, including the defensive CLI, its shared analysis code and tests, the optional GUI Python implementation, current user documentation, root MIT license, package metadata, and the configured test workflow. This is a source repository only. It is not a release repository for frozen Windows binaries.

This is a **candidate allowlist, not a ready-to-push index**. Include paths below only after the remaining checks in §8. Files marked HOLD are not part of the present candidate set. A later decision may include, exclude, or revise them. EXCLUDE paths are local/generated/unrelated files and are not part of this source-publication candidate. Where the README names a held file or directory, the discrepancy must be resolved before staging; the candidate list does not silently override the published README.

### INCLUDE — exact candidate paths

The following **59 currently tracked paths** are candidates for the source repository. The two untracked product/manifest paths included in the same list bring the intended set to **61 paths**.

```text
.github/workflows/tests.yml
.gitignore
LICENSE
README.md
pyproject.toml

docs/ARCHITECTURE.md
docs/DETECTION_RULES.md
docs/PHASE3_VALIDATION.md
docs/REQUIREMENTS.md
docs/SECURITY_AUDIT.md
docs/USAGE.md
docs/USER_GUIDE.md                 [currently untracked; README.md links here]
docs/PHASE-1-GITHUB-SOURCE-PUBLICATION-MANIFEST.md [this file; after review]

samples/                           [README.md directory link; all contents listed]
samples/access.log
samples/auth.log
samples/firewall.log

src/logsentinel/__init__.py
src/logsentinel/__main__.py
src/logsentinel/cli.py
src/logsentinel/config.py
src/logsentinel/detectors.py
src/logsentinel/events.py
src/logsentinel/exceptions.py
src/logsentinel/inputs.py
src/logsentinel/parsers.py
src/logsentinel/report.py
src/logsentinel/storage.py
src/logsentinel/gui/__init__.py
src/logsentinel/gui/__main__.py
src/logsentinel/gui/app.py
src/logsentinel/gui/app_settings.py
src/logsentinel/gui/backend.py
src/logsentinel/gui/icon_widgets.py
src/logsentinel/gui/icons.py
src/logsentinel/gui/main_window.py
src/logsentinel/gui/models.py
src/logsentinel/gui/panels.py
src/logsentinel/gui/reporting.py
src/logsentinel/gui/reports_view.py
src/logsentinel/gui/settings_view.py
src/logsentinel/gui/theme.py
src/logsentinel/gui/themes.py
src/logsentinel/gui/views.py
src/logsentinel/gui/worker.py
src/logsentinel/gui/assets/__init__.py

tests/__init__.py
tests/test_cli.py
tests/test_config.py
tests/test_detectors.py
tests/test_events.py
tests/test_gui_backend.py
tests/test_gui_dashboard.py
tests/test_gui_panels.py
tests/test_gui_reports.py
tests/test_gui_settings.py
tests/test_gui_shell.py
tests/test_gui_worker.py
tests/test_inputs.py
tests/test_parsers.py
tests/test_report.py
tests/test_storage.py

```

**Count note:** the 59 tracked INCLUDE entries consist of 5 root/workflow files, 6 tracked docs, 3 samples, 29 Python source files (including `gui/assets/__init__.py`), and 16 test files. The two additional included docs are the untracked `docs/USER_GUIDE.md` and this manifest. Counts describe this checkout snapshot, not an instruction to add files automatically.

### HOLD — exact paths and reasons

These paths must not enter the candidate index until the clarification/review is complete.

**Tracked paths (28):**

```text
PROJECTMAP.md
tests/test_gui_themes.py
packaging/LogSentinel-GUI-Onedir.spec
packaging/LogSentinel-GUI.spec
packaging/gui_entry.py
src/logsentinel/gui/assets/brand/logsentinel-appicon.svg
src/logsentinel/gui/assets/brand/logsentinel-logo.svg
src/logsentinel/gui/assets/brand/logsentinel-mark.svg
src/logsentinel/gui/assets/brand/logsentinel-sidebar.svg
src/logsentinel/gui/assets/icons/alert.svg
src/logsentinel/gui/assets/icons/check.svg
src/logsentinel/gui/assets/icons/detections.svg
src/logsentinel/gui/assets/icons/download.svg
src/logsentinel/gui/assets/icons/file_plus.svg
src/logsentinel/gui/assets/icons/file_text.svg
src/logsentinel/gui/assets/icons/folder_open.svg
src/logsentinel/gui/assets/icons/log_explorer.svg
src/logsentinel/gui/assets/icons/overview.svg
src/logsentinel/gui/assets/icons/palette.svg
src/logsentinel/gui/assets/icons/play.svg
src/logsentinel/gui/assets/icons/reports.svg
src/logsentinel/gui/assets/icons/search.svg
src/logsentinel/gui/assets/icons/settings.svg
src/logsentinel/gui/assets/icons/shield_check.svg
src/logsentinel/gui/assets/icons/stop.svg
src/logsentinel/gui/assets/icons/trash.svg
src/logsentinel/gui/assets/icons/x.svg
src/logsentinel/gui/assets/logsentinel.ico
```

- `PROJECTMAP.md`: its directory tree and module counts describe an earlier CLI-only state and do not represent the current GUI-inclusive source tree. Refresh it or explicitly decide to omit it before publication. The README tree names `PROJECTMAP.md`, so that tree entry must be reconciled if this path remains on HOLD.
- Both GUI PyInstaller specs and `packaging/gui_entry.py`: these are build recipes/entry-point source, not binaries, but public inclusion is optional and should be decided with the GUI-source scope. The onedir spec has a substantial pre-existing uncommitted change that removes three Qt payload paths and adds required-payload guards; review that exact diff and its technical rationale before including it. The specs depend on GUI assets held below; publishing the entry point alone would not provide a complete packaging workflow. Publishing any spec does **not** clear its output for distribution.
- All 23 GUI image/icon assets: source history in this snapshot does not establish authorship, origin, or applicable rights for each SVG/ICO file. Review provenance and rights before publishing these items. `src/logsentinel/gui/assets/__init__.py` remains an included Python module. Holding the assets affects GUI appearance and packaging, and the included `tests/test_gui_themes.py` explicitly expects those files. That test is held too; omitting it means the full discovered test suite is not represented. The `icons.py` source contains fallbacks for missing SVG artwork, but that is not a substitute for asset review and does not satisfy the asset-presence tests.

**Untracked internal publication assessments (2):**

```text
docs/PHASE-1-GITHUB-SOURCE-PUBLICATION-REVIEW.md
docs/PHASE-1-GITHUB-PUBLICATION-BLOCKER-REGISTER.md
```

These are working review/control records, not product documentation. Hold pending an explicit public-disclosure decision; they include detailed local inventory, operational and licensing analysis, and historical evidence. Their presence in the worktree does not make them publication files.

**Untracked licensing proposals, evidence, and notice corpus (63):**

```text
licenses/DISTRIBUTION-LICENSING-STATUS.md
licenses/GPL-3.0.txt
licenses/LGPL-3.0.txt
licenses/THIRD-PARTY-NOTICES.md
licenses/third-party/ATTRIBUTION-SOURCE-REGISTER.md
licenses/third-party/COMPATIBILITY-RISK-ASSESSMENT.md
licenses/third-party/CONSOLIDATED-RELEASE-BLOCKER-CLOSURE-REPORT.md
licenses/third-party/FINAL-LICENSING-AUDIT.md
licenses/third-party/FINAL-RELEASE-READINESS-REPORT.md
licenses/third-party/FINAL-THIRD-PARTY-NOTICE-RECONCILIATION.md
licenses/third-party/MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md
licenses/third-party/OTHER-COMPONENTS-INVENTORY.md
licenses/third-party/QT-PYSIDE-BINARY-PROVENANCE-REPORT.md
licenses/third-party/QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md
licenses/third-party/QT-PYSIDE-LGPL-DISTRIBUTION-ASSESSMENT.md
licenses/third-party/QT-PYSIDE-LGPL-GAP-CLOSURE-PLAN.md
licenses/third-party/QT-PYSIDE-PHASE-1-RELEASE-ROUTE-DECISION.md
licenses/third-party/QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md
licenses/third-party/RELEASE-PREPARATION-CHECKLIST.md
licenses/third-party/RUNTIME-LICENSING-EVIDENCE.md
licenses/third-party/TRIMMED-PACKAGE-NOTICE-MAP.md
licenses/third-party/VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md
licenses/third-party/notices/MANIFEST.md
licenses/third-party/notices/README.md
licenses/third-party/notices/bzip2/LICENSE.txt
licenses/third-party/notices/cppwinrt/LICENSE.txt
licenses/third-party/notices/cpython/COPYRIGHT-AND-ATTRIBUTION.txt
licenses/third-party/notices/cpython/LICENSE.txt
licenses/third-party/notices/cpython/README.rst
licenses/third-party/notices/freetype/LICENSE.TXT
licenses/third-party/notices/freetype/alternatives/FTL.TXT
licenses/third-party/notices/freetype/alternatives/GPLv2.TXT
licenses/third-party/notices/freetype/alternatives/README.md
licenses/third-party/notices/freetype/qt-attribution-freetype.html
licenses/third-party/notices/harfbuzz/COPYING.txt
licenses/third-party/notices/harfbuzz/qt-attribution-harfbuzz-ng.html
licenses/third-party/notices/libjpeg-turbo/LICENSE.md
licenses/third-party/notices/libjpeg-turbo/README.ijg
licenses/third-party/notices/libpng/LICENSE.txt
licenses/third-party/notices/mesa-llvm/LLVM-3.6.2-LICENSE.TXT
licenses/third-party/notices/mesa-llvm/qt-attribution-llvm.html
licenses/third-party/notices/mesa-llvm/qt-attribution-llvmpipe.html
licenses/third-party/notices/mpdecimal/COPYRIGHT.txt
licenses/third-party/notices/openssl/LICENSE-APACHE-2.0.txt
licenses/third-party/notices/openssl/NOTICE-STATUS.md
licenses/third-party/notices/openssl/TAG-ACKNOWLEDGEMENTS.md
licenses/third-party/notices/pcre2/LICENCE.md
licenses/third-party/notices/pcre2/qt-attribution-pcre2-sljit.html
licenses/third-party/notices/pcre2/qt-attribution-pcre2.html
licenses/third-party/notices/pyinstaller/COPYING.txt
licenses/third-party/notices/sqlite/copyright.html
licenses/third-party/notices/unicode/UCD-16.0.0-ReadMe.txt
licenses/third-party/notices/unicode/UNICODE-LICENSE-V3.txt
licenses/third-party/notices/zlib-ng/LICENSE.md
licenses/third-party/notices/zstandard/alternatives/BSD-LICENSE.txt
licenses/third-party/notices/zstandard/alternatives/GPLv2-COPYING.txt
licenses/third-party/notices/zstandard/alternatives/README.md
licenses/third-party/qt/INVENTORY.md
licenses/third-party/qt/LicenseRef-Qt-Commercial.txt
licenses/third-party/qt/qt-lgpl.html
licenses/third-party/qt/qt-licensing.html
licenses/third-party/qt/qtforpython-commercial.html
licenses/third-party/qt/qtpdf-licensing.html
```

Hold the full collection for item-by-item source-publication disclosure and provenance review. It includes incomplete proposals, alternative license texts, inventories, source/provenance and release-readiness evidence, and candidate notices. It is not a curated end-user notice bundle, is not an authorization to publish these records, and must not be copied into a GUI package as if it established legal compliance. Root `LICENSE` is treated separately and is included as the project license.

### EXCLUDE — local, generated, binary, or unrelated paths

These are not part of the source-publication candidate. Preserve them locally; this decision does not authorize deletion or movement.

**Entire ignored local output directories:**

```text
.venv-build/                  local Python/build environment (4,319 files)
.venv-build-gui/              local Python/GUI build environment (8,239 files)
build/                        generated build output (104 files)
dist/                         generated binaries/reports (372 files)
release/                      local release payloads (6 files)
src/logsentinel.egg-info/     generated package metadata
audit-*/                      local audit fixtures/configs/reports
**/__pycache__/               generated Python bytecode/cache files
```

**Root generated logs/reports (exact observed files):**

```text
test-results.txt
test-results-local.txt
report.json
report.txt
report-explicit.json
audit-config.json
audit-dedup-a.log
audit-dedup-b.log
audit-dedup-report.json
audit-empty-report.json
audit-empty-report.txt
audit-http-7.log
audit-http-8-report.json
audit-http-8.log
audit-malformed-report.json
audit-malformed.log
audit-portscan-10-report.json
audit-portscan-10.log
audit-portscan-9.log
audit-quiet-report.json
audit-ssh-7.log
audit-ssh-8-report.json
audit-ssh-8.log
audit-ssh-success-report.json
audit-ssh-success.log
```

The test-result captures are stale, conflicting local output and are not canonical test evidence. Reports and audit fixtures are generated/local materials; do not publish them as current test results or demonstration data.

**Entire local release directory (six exact paths):**

```text
release/LogSentinel-Windows-v0.1.0/LICENSE
release/LogSentinel-Windows-v0.1.0/LogSentinel.exe
release/LogSentinel-Windows-v0.1.0/README.md
release/LogSentinel-Windows-v0.1.0/SHA256SUMS.txt
release/LogSentinel-Windows-v0.1.0/from pyzbar import pyzbar.py
release/LogSentinel-Windows-v0.1.0.zip
```

The EXE and ZIP are local binaries, explicitly not GitHub source-publication assets. The sibling `from pyzbar import pyzbar.py` is unrelated to LogSentinel: it imports pyzbar/OpenCV and contains driver-license-shaped sample fields. Its author, origin, license, and whether its personal-data-shaped values are fabricated are unknown. Exclude it and the entire release directory. Do not copy it into application source or the source archive.

## 2. Tracked and untracked inventory reconciliation

- `git ls-files`: 87 tracked paths, all classified above: 59 INCLUDE and 28 HOLD.
- `git ls-files --others --exclude-standard`: 66 pre-manifest non-ignored untracked paths: `docs/USER_GUIDE.md` INCLUDE; the two publication assessments and 63 licensing/provenance files HOLD. After creating this manifest, the non-ignored untracked count is 67.
- The new manifest adds one untracked candidate path, bringing the candidate INCLUDE set to 61. No files were staged during this task.
- `.gitignore` currently root-anchors exclusions for `/release/`, `/test-results.txt`, `/test-results-local.txt`, `/build/`, `/dist/`, and root virtual environments. It also excludes reports/audit outputs, `*.egg-info/`, and Python caches. Verified examples are ignored, but ignore rules are not a substitute for explicit staging review or protection against force-adds.

## 3. Publication links and workflow impact

### Internal Markdown links

Checked the internal relative links and anchors in the intended public documentation set: `README.md`, `docs/USAGE.md`, and `docs/USER_GUIDE.md`. All 17 local link/anchor references resolve to included files or the included `samples/` directory, whose three files are listed in §1: `docs/USER_GUIDE.md`, `docs/USAGE.md`, `docs/DETECTION_RULES.md`, `docs/ARCHITECTURE.md`, `docs/REQUIREMENTS.md`, `docs/PHASE3_VALIDATION.md`, `docs/SECURITY_AUDIT.md`, `samples/`, and root `LICENSE`. The guide’s in-page anchor resolves within the included guide. No public-document link targets the held licensing proposals or publication-review records.

`docs/PHASE-1-GITHUB-SOURCE-PUBLICATION-REVIEW.md` and `docs/PHASE-1-GITHUB-PUBLICATION-BLOCKER-REGISTER.md` are held internal working records, not part of the public documentation set; their links are not represented as validated for publication. If either is later approved for publication, re-run link checks against its final allowlist and anchors.

### Installation, test, and development workflows

- The documented CLI source invocation (`PYTHONPATH=src python -m logsentinel`) and package installation (`python -m pip install .`) depend on included `src/logsentinel/` Python modules and `pyproject.toml`; the installed CLI has no third-party runtime dependency. Package building uses the declared `setuptools>=68` backend.
- `python -m unittest discover` depends on included `tests/`, source modules, and samples; the Python 3.14 workflow is included. No workflow configuration or CLI source file is held.
- The optional GUI source Python modules are candidates for inclusion, but the 23 artwork/icon files and `tests/test_gui_themes.py` are on HOLD. The held test explicitly verifies those assets and attempts rendering; omitting it means the full discovered test suite is not represented. Holding the files leaves CLI installation intact but means the GUI cannot reach complete appearance/packaging acceptance until the asset rights review is resolved.
- Holding both PyInstaller specs does not prevent the documented CLI install or test workflow. It does defer publishing the GUI build recipes, and the README/tree wording or scope may need a separate authorized update if the specs remain held.
- There is no supported end-user source-install recipe for the GUI in the User Guide. No Windows GUI executable or ZIP is needed for the documented CLI workflows or GitHub Actions test job.

## 4. Sensitive-data, provenance, and historical-content review

This is a focused screening, not a guarantee that every byte, reachable historical commit, or external origin is clear.

- `samples/*.log` are documented synthetic examples; valid source/destination addresses are RFC 5737 documentation ranges. `samples/auth.log` includes the intentionally invalid `999.1.1.1` test value and synthetic usernames. Keep the sample disclaimer; these are not customer logs.
- `tests/test_report.py` intentionally contains credential-shaped strings (including password/token/secret and a bearer/JWT-shaped fixture) to test redaction. It also uses illustrative paths such as `C:\Users\alice\secret\creds.log` and `/home/bob/.ssh/id_rsa.log`. These are test fixtures, not observed user credentials or actual host paths. Do not remove them without replacing their security-test coverage.
- The root `LICENSE` identifies the project author/copyright holder by name; Git commit metadata also contains author identity. These are attribution/publication information, not a discovered credential, but should be knowingly retained as part of publication. Historical validation/security records and the held licensing corpus may include environment paths, names, emails, or third-party attribution; inspect the exact files before any decision to move them from HOLD to INCLUDE.
- The source-publication review previously recorded pattern scans finding no common private-key, AWS/GitHub token, or database credential shapes in the scanned working tree/history. Pattern scans can miss secrets and personal information; repeat scanning on the exact candidate index and refs immediately before any publication.
- `PROJECTMAP.md` contains stale project-state descriptions (see HOLD above). `docs/PHASE3_VALIDATION.md` is historical and includes an old “ready for implementation” verdict; README labels it historical rather than current release approval. `docs/SECURITY_AUDIT.md` records unresolved best-effort redaction limits; README does not make it a security guarantee. Re-review these caveats against the intended public audience.
- The third-party licensing corpus includes attribution/contact material and technical/environment evidence. Its public-disclosure decision is unresolved; this manifest therefore holds all 63 local files in `licenses/` rather than asserting that they are recipient notices or clearances.
- The anomalous pyzbar/OpenCV file is present under the ignored release directory and in local checkpoint history. Git history inspection found commit `8e183c2` adding it and ten local refs containing it: `refs/t3/orchestration-v2/checkpoints/MDQ1NGVhNzRlZTBjNzNhYzk0NDYxM2E0Zjc0OTc3YmY/ordinal/{18,21}`, `refs/t3/orchestration-v2/checkpoints/OTg2OWE0NDcxNGM2ZWNmN2RkNmJlODk5ZGU4ZDQ0OTY/ordinal/6`, and `refs/t3/orchestration-v2/checkpoints/ZDk4YTk4NzU4ZjhkMzkzNWQwMzlkZmJhYmJjMGIxZTU/ordinal/{8,12,14,16,17,18,22}`. It is absent from the `main` and `origin/main` trees and is not an ancestor of either branch. A `main`-only source publication would not include those local checkpoint refs; do not use a mirror/all-refs push or include checkpoint refs without separately inspecting and deciding their history. Their public status is a separate HOLD until the intended push refspec/refs are confirmed.

## 5. Required GitHub repository contents

For the candidate source-only scope, the required content set is the 61 INCLUDE paths in §1, subject to each HOLD being resolved and the final allowlist being approved. At minimum it includes:

- `README.md`, `LICENSE`, `pyproject.toml`, `.gitignore`, and `.github/workflows/tests.yml`;
- `src/logsentinel/` CLI/shared analysis and GUI Python source;
- `tests/` and synthetic `samples/`;
- current CLI/user/rule/architecture/requirements/security documentation plus the historical-validation record;
- No packaging files are currently required in the candidate set. `packaging/gui_entry.py` and the two GUI PyInstaller specs remain held pending asset provenance, intended build-recipe scope, and the onedir-spec diff review;
- this manifest and `docs/USER_GUIDE.md` so the README’s local links resolve.

Do not include license proposals as a substitute for final recipient notices. Do not attach or link a GUI binary release asset. Source repository contents and binary-distribution clearance are separate decisions.

## 6. Readiness assessment

**Source-only publication is not technically ready for staging from the current worktree.** There are no staged changes, but there are modified tracked files, untracked work product, held files and local checkpoint refs. A candidate allowlist is identifiable, and the CLI install/test workflows remain represented, but GUI assets/specifications, `PROJECTMAP.md`, publication-review documents, licensing records, and history/ref scope remain unresolved. This manifest does not authorize publication or make a legal clearance determination.

This does not mean a source-only publication is technically impossible. It means the current candidate requires owner decisions and verification of the exact index/history before staging.

## 7. Explicit EXCLUDE vs HOLD summary

- **EXCLUDE:** local/ignored `.venv-build/`, `.venv-build-gui/`, `build/`, `dist/`, `release/`, root reports/test logs/audit outputs, generated `*.egg-info/` and `__pycache__/`; all exact release files listed in §1; and the unrelated pyzbar/OpenCV file. Excluding these does not break the documented CLI install, tests, or CI workflow.
- **HOLD:** `PROJECTMAP.md`; `tests/test_gui_themes.py`; both GUI PyInstaller specs and `packaging/gui_entry.py`; 23 GUI art/icon assets; two publication assessment records; all 63 licensing/provenance/notice files; and local checkpoint-ref publication scope. Reasons are stated next to each path group in §1 and the checkpoint note in §4. These are undecided, not cleared by exclusion from the candidate.
- **INCLUDE:** the precise candidate allowlist in §1. This includes root MIT `LICENSE`, but that is not a conclusion about third-party code or GUI binaries. The candidate test set is incomplete while `tests/test_gui_themes.py` and its assets are on HOLD.

## 8. Remaining checks before staging

Before any separate staging authorization:

1. Review and resolve each HOLD, especially the current `packaging/LogSentinel-GUI-Onedir.spec` diff, GUI asset provenance, and the stale `PROJECTMAP.md` entry/tree.
2. Decide whether the two publication review reports and all or any licensing materials belong in public source history; do not bulk-add them.
3. Confirm the intended public scope, exact branch/tag refs, and push refspec. Explicitly exclude all `refs/t3/orchestration-v2/checkpoints/*` unless separately approved after history review.
4. Re-run a secret/PII/provenance scan on the **exact proposed paths and all refs to be sent**; manually inspect suspicious matches and binary/asset provenance. Pattern scans alone are insufficient.
5. Create a clean staging allowlist only after approval, then verify `git diff --cached --name-only`, `git diff --cached --check`, file types, ignored outputs, license/content scope, and all internal Markdown links against the staged tree.
6. Run the documented test suite at the exact proposed source revision. Check hosted Actions evidence for that revision separately; configured workflow jobs are not proof of a successful hosted run.
7. Recheck README tree entries and documentation links against the exact staged contents, including any decision to retain `PROJECTMAP.md`, package specs, or assets.
8. Keep the Windows GUI executable and ZIP out of source publication and GitHub release assets. Preserve **HOLD — NOT CLEARED FOR DISTRIBUTION** unless and until the separate licensing/provenance/release gates are closed by the appropriate reviewers.

No files were staged, committed, pushed, tagged, deleted, moved, or published to create this manifest.
