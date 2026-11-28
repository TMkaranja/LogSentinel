# Final Release Readiness Report — LogSentinel Windows GUI Onedir Candidate

**Assessment date:** 2026-11-27  
**Artifact:** `dist/gui-ondir-trim-test/LogSentinel-GUI/`  
**Decision:** **HOLD — NOT CLEARED FOR DISTRIBUTION**

This is a technical release-readiness and evidence report, not legal advice, a compliance opinion, security certification, or authorization to release. It records the exact candidate inspected, documentation gaps, prior test evidence and unresolved legal/vendor questions. The end of the planned audit sequence does not itself close any release gate.

## 1. Executive summary

The existing trimmed Windows onedir test package was independently inventoried and every current regular file was SHA-256 hashed. The observed package contains **182 files / 80,058,228 bytes**. Its root executable is **2,386,859 bytes**, SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`, matching the expected executable hash. Required application/Qt runtime files are present; the three specified exclusions (`Qt6Pdf.dll`, `qpdf.dll`, and `opengl32sw.dll`) remain absent. No package file with an audit/test-document suffix or name was found; the apparent `reports.svg` hit is a GUI icon asset. No structural anomaly was observed in file types or root layout.

The candidate has prior recorded standard-desktop end-to-end success for page navigation, sample-log analysis, expected detection, JSON/HTML export, settings persistence and clean shutdown. This is evidence from the recorded run, not a test rerun in this documentation step or broad Windows compatibility. Remote Desktop, GPU-less/software-rendering, high-DPI and clean-target Windows compatibility remain unverified.

The repository and old release README/documentation are CLI-oriented; they are not a GUI installation/usage guide. The GUI provides in-app Settings and privacy/security descriptions, and source code documents settings storage and input/report handling, but there is no package-specific user guide or package-delivered third-party notice/source set. The notice collection is internal evidence, not a ready-to-ship bundle.

Major release blockers remain: Qt/PySide/Shiboken license scope and election; conditional LGPL/GPL conveyance terms and neither §4(d) route being demonstrated for this exact artifact; Qt and Microsoft runtime redistribution rights; package-matched notices and source materials; Python's Microsoft Distributable Code scope; component/source mappings; PyInstaller bootloader status; actual distribution channel and user terms; and qualified legal review. The release remains on **HOLD**.

## 2. Release candidate identity

| Identity field | Expected/reference | Independently observed |
|---|---|---|
| Candidate path | `dist/gui-ondir-trim-test/LogSentinel-GUI/` | Same directory inspected read-only |
| Regular-file count | 182 | **182** |
| Aggregate file size | 80,058,228 bytes | **80,058,228 bytes** |
| Executable path | `LogSentinel-GUI.exe` at package root | Present at package root |
| Executable size | 2,386,859 bytes | **2,386,859 bytes** |
| Executable SHA-256 | `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01` | **Same; match** |
| Package layout | Onedir; executable outside `_internal/` | Only root file is the executable; 181 files under `_internal/` |

A complete path/size/SHA-256 inventory of all 182 files is included in **Appendix A**. That is a reproducible fingerprint of the package as inspected for this report. It does not establish provenance or that every non-executable file matches an earlier complete hash baseline: no earlier full 182-file expected-hash manifest was identified in the reviewed records. The expected total size and executable hash are useful checks, but they cannot alone rule out a same-size change to another package file.

## 3. Package integrity verification

### 3.1 Current-tree checks

- Enumerated all descendants of the package directory, verified there are **no symlinks or non-regular files**, and hashed every regular file with SHA-256; Appendix A records each relative path, byte count and digest.
- Current extension set is limited to `.dll`, `.exe`, `.ico`, `.pyd`, `.qm`, `.svg`, and `.zip`, consistent with the known inventory.
- Confirmed the only file outside `_internal/` is `LogSentinel-GUI.exe`.
- Confirmed required runtime and application entries exist: CPython runtime, `base_library.zip`, Qt Core/Gui/Network/Svg/Widgets, corresponding PySide bindings, Shiboken extensions, Windows platform and style plugins, and GUI icon resource.
- Confirmed excluded paths are absent: `_internal/PySide6/Qt6Pdf.dll`, `_internal/PySide6/plugins/imageformats/qpdf.dll`, and `_internal/PySide6/opengl32sw.dll`.
- A name/content-type screen found no `.txt`, `.md`, or `.rst` file, no audit/checklist/test-results file, and no internal licensing report in the package. The sole filename substring match for “report” is `_internal/logsentinel/gui/assets/icons/reports.svg`, an expected UI icon, not an audit report.

### 3.2 Integrity interpretation and limitation

The directly measured package count, total bytes and executable digest match the stated reference values. Required files and exclusions also match the stated package composition. All current-file hashes are captured in Appendix A. **No unexpected package modification can be ruled out relative to a prior full-file baseline**, because the reviewed records do not provide an earlier complete set of 182 expected file hashes. The old 185-file package and its inventories are not a valid baseline for this trimmed artifact. Do not describe the entire directory as unchanged relative to history based only on count, aggregate size, and EXE hash.

The package is a test candidate under `dist/gui-ondir-trim-test`, not a user-approved distribution artifact. No copy, build, archive, installer, replacement, or package modification was performed in this task.

## 4. Functional verification evidence and limitations

### Recorded evidence (not rerun here)

The recorded trimmed-package test `C:/Users/DELL/AppData/Local/Temp/logsentinel-ondir-trim-e2e-run10.log` reports:

- Successful launch on the recorded Windows 10 build 19045 host and traversal of Overview, Detections, Log Explorer, Reports and Settings.
- Selection and analysis of `samples/auth.log`; completion with 14 parsed events, one expected `LS-RULE-001` finding for documentation IP `192.0.2.7`, and one malformed-line error.
- Successful JSON export and validation of the finding/counters. Successful standalone HTML export with expected content and **zero `<script>` tags**.
- Settings persistence/restoration across relaunch and clean process shutdown; no remaining process.
- Package count/size unchanged during that recorded workflow (182 files / 80,058,228 bytes).
- The excluded Qt PDF/qpdf/Mesa modules not loaded in that recorded workflow; no Qt plugin diagnostics were captured in the test log.

This report independently rechecked package files but did **not** relaunch the GUI or reproduce the functional test. The older smoke log mentions the earlier untrimmed `dist/gui-ondir-test` package and is not used to claim trimmed-package behavior. A previous run on another package/layout is not proof of the current artifact's LGPL replaceability.

### Compatibility limitations

- The recorded E2E run covers one standard desktop session only.
- RDP, GPU-less or software-rendering hosts, inherited `QT_OPENGL`/`QT_OPENGL_DLL` settings, high-DPI scaling and mixed-DPI movement have not been tested.
- A prior inventory observed Qt ICU imports resolving from Windows System32 on the test host; minimum supported Windows version/host dependency has not been established.
- Compatibility exclusions are provisional for the current feature set. Reassess if PDF, printing, OpenGL, Qt Quick/QML or QRhi functionality is introduced.

Do not make broad supported-Windows claims until the release owner defines targets and the relevant compatibility tests pass.

## 5. User-facing documentation status

The reviewed root README and `release/LogSentinel-Windows-v0.1.0/README.md` describe the **CLI** and an older one-file CLI artifact. Their Python installation commands, CLI options, and license summary do not instruct a user how to install or operate this PySide6 onedir GUI. The existing `docs/USAGE.md`, `docs/REQUIREMENTS.md`, architecture and security documentation are also predominantly CLI-focused; `REQUIREMENTS.md` still lists a GUI as out of scope. The existing `release/` archive is a protected historical CLI artifact and was not edited or treated as the GUI release.

The GUI source/in-app UI does establish some useful facts: launch is by the GUI executable; the UI has five named pages; analysis accepts selected files/folders and JSON config; JSON/HTML reports are user-selected exports; saved preferences are stored under `%APPDATA%\LogSentinel\settings.json` on Windows; settings do not model log paths, credentials, findings or raw content; and the application code marks inputs read-only and uses a temporary SQLite staging database. The GUI Settings page includes privacy/security text. These facts are not a substitute for a complete, reviewed user document, nor a certification that every host environment behaves identically. The UI's redaction wording should be aligned with the CLI documentation's **best-effort, not universal** limitation.

| User-facing documentation need | Current status | Objective criterion before GUI distribution |
|---|---|---|
| Installation / unpacking | **Incomplete.** No GUI-specific packaged instructions; no installer is in scope. | State exact authorized delivery format, unpack/run steps, permissions, supported location, and any prerequisites; verify against the final release layout. |
| System requirements | **Incomplete.** Current evidence is one Windows 10 build 19045 host; no minimum Windows version established, ICU/host dependency unresolved. | Identify supported Windows versions/architectures and prerequisites from vendor/build evidence; validate on each declared minimum target. |
| First launch | **Incomplete.** GUI E2E demonstrates launching the EXE, but there is no user-facing guide. | Document startup, first input selection, analysis start, result review and export from the actual final UI; verify every control/label against release. |
| Usage guide | **Incomplete for GUI.** Existing full guide is CLI-only. | Add/review a GUI workflow guide covering pages, file/folder input, configuration, run/cancel, results and JSON/HTML export; test documented steps. |
| Troubleshooting | **Incomplete for GUI.** Existing CLI troubleshooting does not cover Qt/Windows dialogs or startup. | Document validated GUI-specific recovery steps and stable error messages; verify on supported Windows targets. |
| Configuration and data storage | **Partially documented in UI/source; no full user guide.** Windows preference path is `%APPDATA%\LogSentinel\settings.json`; saved state includes UI preferences and analysis defaults. | Document exact preference location/schema scope, precedence, export destinations and reset/removal behavior; verify from the built app and avoid promising secrecy/protection beyond evidence. |
| Security and privacy | **Partial.** UI describes offline/local analysis, redaction, path redaction and read-only input; repository docs qualify redaction as best-effort. | Reconcile user-facing language; document data processed, local settings/temp database/report behavior and limitations. Validate claims by code review and test; no absolute security/privacy guarantee. |
| License and third-party notices | **Not complete.** No notice/license text in package; repository evidence collection is not curated or legal-approved. | Provide a counsel-reviewed, version-matched end-user notice set and applicable license texts with final package; manifest-to-package verification must pass. |
| Corresponding source / written offer / relinking instructions | **Not established; conditional on applicable license/conveyance route.** | Counsel identifies applicable route and exact source scope; deliver/test matched source or approved offer/relink instructions, or substantiate the chosen shared-library route. |
| Uninstallation | **Incomplete.** No GUI uninstallation guide or installer is in scope. | Document removal of the exact onedir files and separately explain optional per-user settings at the verified location; verify there are no additional managed services/shortcuts/installer entries. |
| Version/support channel | **Incomplete.** GUI displays application version, but no GUI release/support channel documentation is established. | Identify final version, support contact/channel and update mechanism—or state none—then verify against actual build and release process. |

No new user-facing usage guide was invented in this report: an accurate full guide depends on the actual approved distribution layout, supported systems, documentation channel and legal/notices decision. This report is the internal readiness record only.

## 6. Licensing and notice status

**Evidence base:** `CONSOLIDATED-RELEASE-BLOCKER-CLOSURE-REPORT.md`, `FINAL-LICENSING-AUDIT.md`, `RELEASE-PREPARATION-CHECKLIST.md`, `FINAL-THIRD-PARTY-NOTICE-RECONCILIATION.md`, `QT-PYSIDE-LGPL-GAP-CLOSURE-PLAN.md`, `TRIMMED-PACKAGE-NOTICE-MAP.md`, `RUNTIME-LICENSING-EVIDENCE.md`, `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`, `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`, and `notices/MANIFEST.md`.

- The package distributes Qt 6.12.0/PySide6/Shiboken6, plugins, 99 translation catalogs, CPython 3.14.10 and native extensions, OpenSSL 3.5.9, SQLite 3.50.4, PyInstaller 6.22.3 payload, and ten VC++ runtime DLL copies, among other embedded components. File presence, not observed load count, defines this package inventory.
- Eight nested VC++ 14.44.35211.0 DLLs match entries and `RECORD` hashes in the digest-matched Qt Essentials/Shiboken wheels. That proves delivery via those wheel payloads; it does not establish Microsoft source identity, Qt's supplier rights or downstream redistribution eligibility. The two root 14.51 files are a separate rights/provenance issue.
- Qt/PySide/Shiboken binary-specific license election, source/build provenance, complete component SBOM, translation source/license map, Qt's written runtime-DLL basis, and the PySide GPLv2 metadata/public-language discrepancy remain open.
- If an LGPLv3 conveyance route applies, no exact-candidate §4(d)(0) source/relink/application-code route or §4(d)(1) shared-library replacement route is demonstrated. §3, §4(c), and §4(e) applicability are conditional questions for counsel, not assumed triggered.
- Component-specific gaps include FreeType and Zstandard license elections, Qt zlib-compatible code identity, CPython zlib/liblzma source/license scope, libtiff/libwebp notices and patent material, Qt third-party mappings, and CPython's Microsoft Distributable Code section.
- PyInstaller's file-specific distinction remains important: bootloader/loader GPL-2.0-or-later with Bootloader Exception; runtime hooks and `_pyi_rth_utils` Apache-2.0; build-time `hook-PySide6.QtSvg.py` has a GPL/exception header. Bootloader modification/source mapping remains open; a four-byte `.rdata` difference is unexplained.
- OpenSSL 3.5.9 Apache-2.0 text and acknowledgements are collected. The inspected archive had no file named `NOTICE`; do not fabricate or rename one. Exact packaged build provenance remains open.
- The notices folder contains 35 files, but only 34 have manifest-listed expected hashes/sizes. All 34 listed files have been rechecked and match. `MANIFEST.md` has no self-hash baseline. It contains alternatives, candidates, internal notes and historical Mesa/LLVM material; it is not an end-user bundle. No report claims legal clearance.

## 7. Outstanding blockers

### Critical — must close before any distribution decision

1. Define actual recipients, territories, delivery channel, installer/portable format, EULA/recipient terms, update/signing/anti-tamper restrictions, and whether copies have or will be conveyed.
2. Obtain Qt/Qt for Python's written, exact-version/file/wheel license basis and rights; resolve the metadata discrepancy and Shiboken/translation scope.
3. Obtain qualified counsel's review of the actual grants and conveyance, including conditional LGPL/GPL duties, §4(d) route, source/relinking requirements and any §3/§4(c)/§4(e) questions.
4. Establish Qt's supplier/redistribution basis for eight Qt-signed VC++ DLL hashes and applicable Microsoft terms/eligibility for all ten package copies; identify a servicing/deployment model.
5. Produce a package-matched notice/source plan and include legally reviewed end-user materials in an authorized final candidate.

### High — technical/source and documentation closure

6. Obtain Qt/PySide build provenance, component SBOM, source revisions/patches/toolchain and license/notice map; resolve the 99 translation catalogs.
7. Resolve exact source/license/election for FreeType, Zstandard, zlib-compatible code, liblzma/XZ, libtiff, libwebp/patent materials, PCRE2/SLJIT and other supported embedded dependencies.
8. Determine CPython Microsoft Distributable Code applicability and affected files from exact distribution/build records.
9. Validate PyInstaller source-entry mapping, bootloader modification status, and applicable GPL-2.0/exception and Apache materials.
10. Complete GUI documentation (installation, system requirements, first launch, usage, troubleshooting, data storage/privacy, notices/source and uninstallation) for the approved final delivery layout.
11. Run declared-target compatibility tests for RDP, GPU-less/software rendering, high-DPI/mixed-DPI and clean Windows targets; resolve the observed host ICU dependency and document the support matrix.

### Evidence limitation

The current package has a freshly captured full-file SHA-256 manifest in Appendix A, but there is no prior full-file hash manifest for the 182-file trimmed artifact in the reviewed baseline. A future approved release process should use this manifest as a candidate identity reference or generate a new release manifest from the authorized final artifact. The current report cannot retroactively prove all package files were unchanged from an earlier build.

## 8. Final release checklist with objective completion criteria

Each item is a release gate. A checked item records only the stated technical observation; it does not imply legal clearance.

### Technically verified

- [x] **Candidate inventory captured.** Criterion: enumerate all package regular files; current result is 182 files / 80,058,228 bytes; Appendix A contains 182 path/size/SHA-256 rows.
- [x] **Expected executable identity.** Criterion: SHA-256 of root EXE equals the reference digest; result `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01` (2,386,859 bytes).
- [x] **Required runtime and app files present.** Criterion: the listed Python runtime, Qt modules/bindings, Shiboken extensions, QWindows/platform/style plugins, base library archive and application icon exist in the current inventory.
- [x] **Target exclusions present.** Criterion: `Qt6Pdf.dll`, `qpdf.dll`, and `opengl32sw.dll` exact paths are absent.
- [x] **No apparent internal documents in payload.** Criterion: package contains no `.txt`, `.md`, `.rst`, no file names indicating test/audit/checklist, and no reports other than the expected `reports.svg` UI icon match.
- [x] **Recorded standard desktop E2E evidence reviewed.** Criterion: `logsentinel-ondir-trim-e2e-run10.log` records the five pages, expected sample detection, JSON/HTML export, settings persistence and clean shutdown.
- [ ] **Full-package historical baseline comparison.** Criterion: obtain an authorized, trusted expected hash/size list for the exact 182-file candidate and compare every Appendix A row; no earlier full-file baseline is currently available.
- [ ] **Supported Windows matrix verified.** Criterion: documented clean-target test results for each declared minimum/target Windows version, RDP, GPU-less/software-rendering and DPI configurations, with outcomes and loaded-module/diagnostic evidence.

### Documentation complete

- [ ] **GUI install/first-launch/usage/troubleshooting guide.** Criterion: guide matches exact final package layout and every documented workflow is reproduced on the release candidate.
- [ ] **GUI system requirements and uninstall procedure.** Criterion: minimum OS/runtime prerequisites and residual settings cleanup are validated and documented for the chosen distribution format.
- [ ] **Configuration/storage/privacy language reconciled.** Criterion: document `%APPDATA%\LogSentinel\settings.json`, user-selected report paths, temporary-storage behavior, and redaction limitations; verify against final build/code and eliminate absolute unsupported guarantees.
- [ ] **Package-matched third-party notices/source instructions.** Criterion: legal-reviewed manifest lists only applicable texts, all are included in the approved delivery, and hashes/content are checked against the final package and source/offer arrangement.

### Awaiting external evidence

- [ ] **Qt/PySide/Shiboken source/build map and SBOM.** Criterion: obtain artifact-specific source revisions, patches/generated inputs, build configuration and component/notice map tied to the exact wheel and packaged hashes.
- [ ] **Qt translation map.** Criterion: map all 99 `.qm` files to source catalogs, contributor/license notices and generation tool/options.
- [ ] **Qt third-party component records.** Criterion: exact version/source/license and notices established for all confirmed embedded components and plugins; unresolved items explicitly dispositioned.
- [ ] **Qt VC++ DLL sourcing/rights response.** Criterion: written Qt documentation identifies source hashes/transforms/signing and redistribution basis for each of the eight nested files.
- [ ] **CPython distribution/build terms.** Criterion: obtain exact Windows distribution/build license materials and a file-level determination for Microsoft Distributable Code scope.

### Awaiting legal review

- [ ] **Distribution facts and Qt license route.** Criterion: counsel's written decision covers intended channel/recipients, exact component grants/elections, metadata discrepancy and any commercial agreement.
- [ ] **LGPL/GPL scope and route, if applicable.** Criterion: counsel determines the applicable scope and whether §4(d)(0) or §4(d)(1) is relied upon, required source/materials, §3/§4(c)/§4(e) issues, and user/installer restrictions.
- [ ] **PyInstaller scope.** Criterion: counsel reviews bootloader/loader GPL-2.0-or-later exception and Apache runtime scope against final entry map and modification evidence.
- [ ] **Third-party notice/source obligations.** Criterion: counsel reviews the final source/version-matched notice manifest and any open component-specific terms.

### Awaiting redistribution authorization

- [ ] **All ten Microsoft runtime files.** Criterion: applicable complete terms and distributor eligibility are established per file/path; Qt's written basis covers the eight Qt-signed nested hashes; authorized deployment and servicing model is documented.
- [ ] **Qt/PySide commercial or open-source rights.** Criterion: retain written vendor grant/election or applicable executed agreement covering this exact version, use and channel.
- [ ] **Final recipient package.** Criterion: release owner authorizes the exact final hashes and terms after legal review; no inferred permission from signatures, version strings or wheel records.

### Blocked from distribution

- [x] **Current decision is HOLD.** Criterion to remove hold: all critical checklist items are completed with retained evidence, applicable source/notice/replacement conditions are validated, technical target tests pass, and qualified counsel plus the release owner approve the exact final artifact and channel in writing.
- [ ] **Final post-assembly audit.** Criterion: recompute all file hashes after adding authorized docs/notices; verify the package/source/notice manifest; retest install, usage, export, uninstall and supported platforms; record sign-off.

## 9. Distribution decision

**HOLD — NOT CLEARED FOR DISTRIBUTION.** The package is technically fingerprinted and has useful recorded standard-desktop functional evidence, but it is not a release-cleared GUI distribution. Applicable Qt/PySide and Microsoft runtime rights are unresolved; corresponding-source/replacement/relinking requirements are not demonstrated where applicable; package-matched notices and user documentation are incomplete; and qualified legal review and release-owner authorization are absent. Do not publish, upload, or distribute this candidate on the basis of this report.

This is a release-control disposition based on incomplete evidence and decisions. It is not a legal finding of infringement, violation, or noncompliance.

## 10. Exact next actions before public distribution

1. Release owner records recipients, territories, channel, installer/portable layout, EULA, update/signature controls, supported Windows targets and any prior conveyance.
2. Send Qt the exact wheel hashes and per-file package hashes; request binary-specific license/election, source/build/SBOM/translation records, copied-code notices and written rights for the eight nested VC++ files.
3. Obtain complete applicable Microsoft runtime terms and the distributor's license/eligibility evidence for all ten runtime copies; have counsel assess exact files, Qt signing and deployment model.
4. Retain qualified counsel to assess the exact conveyance, Qt/PySide/Shiboken and embedded component licenses, LGPL/GPL alternatives, source/notice requirements, §4(d) route, conditional §3/§4(c)/§4(e), PyInstaller terms, CPython Microsoft clause, and the Microsoft runtime grant.
5. Close source/notice mapping for Qt plugins and static dependencies, all 99 translations, CPython extensions, OpenSSL, PyInstaller entries, and any other confirmed component. Resolve FreeType/Zstandard alternatives, zlib/liblzma identity, libtiff/libwebp and patent materials.
6. Choose and test the legally reviewed replacement/shared-library or corresponding-source/relink process if required; test on a separate copy, never the preserved audit candidate.
7. Complete the GUI user guide and system/installation/uninstallation documentation against the actual authorized delivery; reconcile in-app security/privacy wording with best-effort limitations.
8. Complete Windows compatibility and runtime servicing tests for the support matrix. If packaging or deployment changes, repeat component/source/legal review as appropriate.
9. Assemble only the curated, reviewed end-user license/notice/source materials. Do not copy internal audit reports or the entire notice evidence directory into the package.
10. Re-inventory and hash the authorized final artifact, test it, verify documentation/notice hashes and corresponding-source access, and obtain written release-owner and counsel approval before distribution.

## 11. Verification record and change control

Verification completed after report assembly (report self-hash is provided separately in the completion response):

- **Package:** 182 regular files; 80,058,228 bytes. Root EXE: 2,386,859 bytes; SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`. Result: PASS.
- **Per-file integrity:** freshly computed path/size/SHA-256 inventory contains 182 rows and matches the read-only inventory snapshot taken before report creation. Appendix A is the full current file list.
- **Required content / exclusions:** required application and Qt files are present; Qt PDF, qpdf, and Mesa software OpenGL exact paths are absent.
- **Unexpected payload screening:** unexpected file suffixes: none; no audit, checklist, test-results, or internal report documents were found. The only filename substring match for “report” is `_internal/logsentinel/gui/assets/icons/reports.svg`, an expected GUI icon. No symlinks or non-regular package files observed.
- **Six historical release-baseline artifacts:** 6/6 match their recorded sizes and SHA-256 hashes. These are the existing CLI release artifacts, not this GUI candidate.
- **Notice manifest:** 34/34 manifest-listed files match recorded sizes and SHA-256 hashes. `MANIFEST.md` is a 35th directory file without a self-hash row; observed size **13,184 bytes**, SHA-256 `28951f87cb012f372ef30972c32adf0bafbf57f5443de96ac523906c3f0660b3`; no expected self-hash is recorded for comparison.
- **Worktree:** 68 pre-existing status entries were captured before this report was created. Added status entries: `?? licenses/third-party/FINAL-RELEASE-READINESS-REPORT.md`; removed entries: `none`. The requested report is the only added worktree entry; all pre-existing status entries remain listed.
- **Actions:** no source, spec, package, notice, old report, or release artifact was modified; no rebuild, archive/installer creation, upload, distribution, commit, or push occurred during this step.

Release baseline rows:

| Artifact | Bytes | SHA-256 | Result |
|---|---:|---|---|
| `LogSentinel-Windows-v0.1.0/from pyzbar import pyzbar.py` | 583 | `3b61a54ceb89d0635ae42e36e9d1c00facedd7de6db08e2a3acbbdf237202279` | PASS |
| `LogSentinel-Windows-v0.1.0/LICENSE` | 1075 | `2303a4d4953cc673cbd314782cf05346901c40323d0d4426d758a6d96e4ea3f1` | PASS |
| `LogSentinel-Windows-v0.1.0/LogSentinel.exe` | 9922891 | `d1bda55a555f6e1a6a433eae89d648079f7eeeb869bd9ee3da487cde36d52b04` | PASS |
| `LogSentinel-Windows-v0.1.0/README.md` | 10916 | `0a3417209068d877c3c3533eb0446549d77e5e2852924b063f3ed049899944bd` | PASS |
| `LogSentinel-Windows-v0.1.0/SHA256SUMS.txt` | 91 | `2f7fbd2f44d5e094c9e7596ebb8006ee610ee34623fe641f0c878643a03baee2` | PASS |
| `LogSentinel-Windows-v0.1.0.zip` | 9733515 | `00b13f0dbf7db61a838be8979f92e4ab761d098b44c071d2b365916fb77cf53a` | PASS |

Notice manifest-listed files: all rows were individually hashed and size-checked; summary above.


No source, packaging specification, binary, notice, old release artifact or existing report was intentionally modified for this task. No package was rebuilt, no archive or installer was created, and nothing was published, uploaded, committed or pushed. Existing worktree changes and all six historical release-baseline files were to be preserved. Appendix A is the current candidate's per-file fingerprint; it is not a newly authorized release artifact.

## Appendix A — Complete current package file inventory

The table lists every regular file observed in the candidate at the time of inspection, relative to the package root. Sizes are bytes; hashes are lowercase SHA-256. This fingerprint is for reproducible comparison, not an upstream provenance or release-authorization statement.

| Path (relative to package root) | Bytes | SHA-256 |
|---|---:|---|
| `_internal/_bz2.pyd` | 87776 | `9590a3f4b7c0801cd379341d40bb89b5dc9a4e232c9498b6f3bc6b5e99d4ae7f` |
| `_internal/_decimal.pyd` | 290016 | `9605f332fb52636d77a3125abc7e42ba22b3838dcf136d81f37fe5875cbd62d6` |
| `_internal/_hashlib.pyd` | 68832 | `9052a85ac9947afbbdfdd62b0cad7501b668e6107832cefaa4b76377d710dae0` |
| `_internal/_lzma.pyd` | 160992 | `9ff9f63ad79f161722106e029b4c3afc6494848fd73f9bcc2ed5434a15c71bde` |
| `_internal/_socket.pyd` | 87776 | `11f2ace2a37e59bf0f2fcfcc2523307408fa2e7f0aec561bc7531a8db130a83c` |
| `_internal/_sqlite3.pyd` | 133344 | `33e91d0de7924180012c86efb17611ec589b93f90b321ed9ec3c2f4c99fae5be` |
| `_internal/_ssl.pyd` | 193248 | `56fdbe70896e4b3c6d4e8897fad1d011129354172566832371289edca0d85a21` |
| `_internal/_zstd.pyd` | 503520 | `7a7b50c580428daf3d43c87b121988d2e8c7af9533fa2195f1aef8652fc2c489` |
| `_internal/base_library.zip` | 1396401 | `6f444d2287976066adf712953b9e8a2234bd5c49769945aa0f155ed218cdc384` |
| `_internal/libcrypto-3.dll` | 6021880 | `75495fe0e079ab00d49be740d3c710a0b94e3f74f9648cb7cc9f768fc7f52319` |
| `_internal/libssl-3.dll` | 1308920 | `8957182a9c385bfd9f3f790921de2ddc614cf91f99edbed4e9e5446a46504e32` |
| `_internal/logsentinel/gui/assets/brand/logsentinel-appicon.svg` | 920 | `bb28859d520c23a76493efba923b3adfa8cba6aa873090a29e501362e2f25a61` |
| `_internal/logsentinel/gui/assets/brand/logsentinel-logo.svg` | 10340 | `9c30d78911c0fff3a641b1820e139370a0991806dcd0523b207df1e305773fa9` |
| `_internal/logsentinel/gui/assets/brand/logsentinel-mark.svg` | 920 | `bb28859d520c23a76493efba923b3adfa8cba6aa873090a29e501362e2f25a61` |
| `_internal/logsentinel/gui/assets/brand/logsentinel-sidebar.svg` | 10083 | `eb0d3e0874a3877b79503be7128d10a512dd8205fabae60fee319a34b4dfc62f` |
| `_internal/logsentinel/gui/assets/icons/alert.svg` | 292 | `191a66cf92f42cdd1bf7375d7b0c94f5f53bac44730201e65a2b284b770c3989` |
| `_internal/logsentinel/gui/assets/icons/check.svg` | 196 | `0f68dcfa6748c435768b27317f89689bc752a27bd63b797737972340ec283c39` |
| `_internal/logsentinel/gui/assets/icons/detections.svg` | 368 | `672cd521c8a8ea7355bdbd4f0de78addd014a4e9725f8e74343a9600a453668a` |
| `_internal/logsentinel/gui/assets/icons/download.svg` | 267 | `fb67a5ce7e49bce1df96910725e71b47820ac5046e91a6ecf85b95b8a0e2da77` |
| `_internal/logsentinel/gui/assets/icons/file_plus.svg` | 299 | `d0357c44c6c1e429614609657a8af64f8f6edb9780924dd09f2f7206b936f8f8` |
| `_internal/logsentinel/gui/assets/icons/file_text.svg` | 298 | `a37006fe9dcf14f1d2758761051f5c4ae169d57512c12e62ce9280d8d945f501` |
| `_internal/logsentinel/gui/assets/icons/folder_open.svg` | 358 | `c7c425bb348b1af16c697be291b12c9e05e87400487a2f8caa017b0f8329b7d0` |
| `_internal/logsentinel/gui/assets/icons/log_explorer.svg` | 317 | `3008d40feac72acb9588ac87193c61e9917f5f5bc72665f5e880a520a06f516f` |
| `_internal/logsentinel/gui/assets/icons/overview.svg` | 368 | `379fe603df3afc8b80a178b83bbc649d594a74772e984b3c18c5d6ab152336dd` |
| `_internal/logsentinel/gui/assets/icons/palette.svg` | 444 | `629e32b419d0adf0b054a4cb87d52d8dd934a0847b58a06ca7f574d200f353b5` |
| `_internal/logsentinel/gui/assets/icons/play.svg` | 198 | `4d8390b96e111470d6d397540610b6209cd1f16df089fdbd802f4bb70cc946cd` |
| `_internal/logsentinel/gui/assets/icons/reports.svg` | 322 | `65eeb087b42d52b53721b9202be45487504ca3d253ae92b07ef0154cb7e841f4` |
| `_internal/logsentinel/gui/assets/icons/search.svg` | 226 | `5c916fe41833f69421452f6198eb24ce7463b8875c38b25c391f75d1a6ce7b63` |
| `_internal/logsentinel/gui/assets/icons/settings.svg` | 778 | `df60f7fce3362af3958dc54e389389f399ad346b9519f2ffe25734c842d9199b` |
| `_internal/logsentinel/gui/assets/icons/shield_check.svg` | 352 | `4b67896a203ea68f791703a20533765a66f53ccbb84fe6292293604b402a1244` |
| `_internal/logsentinel/gui/assets/icons/stop.svg` | 220 | `07817d961981a2b1a7206436ad5c49c571b9c07d670e87945bef9216d9d22ffb` |
| `_internal/logsentinel/gui/assets/icons/trash.svg` | 335 | `56da0d4c3ba1b515cb1eceb530a9c99d9353b8e3335256e2b80f153bf4c7edaf` |
| `_internal/logsentinel/gui/assets/icons/x.svg` | 213 | `8257c7412a3231067454c75cea0d56530ca400c29051fa7a840c8df5790a4edf` |
| `_internal/logsentinel/gui/assets/logsentinel.ico` | 28829 | `000dbee98ff64b8c31074c0e346c3322f2213f0e6c99d2c84a937821b6e275e6` |
| `_internal/PySide6/MSVCP140.dll` | 549176 | `f6f1d55bfd64027820ddce48f9cd8cf46d53bfa34047e6acf4ef348d492a05cb` |
| `_internal/PySide6/MSVCP140_1.dll` | 27448 | `2be87527c41e1ba8aff48e326e0adcd4743516e0bbcc9304986c726e27de6aca` |
| `_internal/PySide6/MSVCP140_2.dll` | 271672 | `6a72ed8a87eae1671640bd1ca98eccb989f1772ae46ab84594e385bf6d4ac4fb` |
| `_internal/PySide6/plugins/generic/qtuiotouchplugin.dll` | 102712 | `8565656807db29cfb6170e6803181f24e0bed3aa1b14684d29694e375cc5ee96` |
| `_internal/PySide6/plugins/iconengines/qsvgicon.dll` | 72504 | `f9e21af351bd5d5629bc00e8e3796b552eca92d1a9645438c865b9c53af1714f` |
| `_internal/PySide6/plugins/imageformats/qgif.dll` | 48440 | `77782de4aa4f7b75a7cc4d3f24aee49da935c312ea13d25f4cda3a98d180145c` |
| `_internal/PySide6/plugins/imageformats/qicns.dll` | 56632 | `93e2e588cd1036af3c6300b539d648b3825625788e59a3f0f1863d9901c9759f` |
| `_internal/PySide6/plugins/imageformats/qico.dll` | 47416 | `a0e4d0d0319e075f6cc5f774084bf390f7af83600f38685c6bc9c407681cc22c` |
| `_internal/PySide6/plugins/imageformats/qjpeg.dll` | 592696 | `dd42bdcd229744a9515db82ba9a802c74b6589cc508c3e85fb30f06ba24b9da6` |
| `_internal/PySide6/plugins/imageformats/qsvg.dll` | 40248 | `b63f97ed0ae60aa5bc332c37e429c1f31154e1eee358352b2c49598c5269843b` |
| `_internal/PySide6/plugins/imageformats/qtga.dll` | 39224 | `ce95aa019d940533341b4f08a10ddd3b0393162678c47904251da77aeadfd34e` |
| `_internal/PySide6/plugins/imageformats/qtiff.dll` | 991032 | `ce696a2dd2e57b8852f7d01834725f54a4d0be66c3d2c491df60fd907fece907` |
| `_internal/PySide6/plugins/imageformats/qwbmp.dll` | 36664 | `e118243bd3528aa5fe6378a8839abe0efc200e891af06ee369b97b2ff239b89c` |
| `_internal/PySide6/plugins/imageformats/qwebp.dll` | 566072 | `02ae5555b688f78aade5cedcd66c646b73d519460c008c23e75ad408bd152668` |
| `_internal/PySide6/plugins/networkinformation/qnetworklistmanager.dll` | 79160 | `2bd047476183c76004221fb44adb7ada9b4b6ce5c2929d63ff67a5305b430f1a` |
| `_internal/PySide6/plugins/platforms/qdirect2d.dll` | 1082168 | `18213464be5a5a1d39af6a2c876ce21a6bb6a634c814651d09f0ef7e4719edc2` |
| `_internal/PySide6/plugins/platforms/qminimal.dll` | 62264 | `c9025bc5f4653c5aadac87f06ab391763e82adf792f6759c6027a78a5efcaf5c` |
| `_internal/PySide6/plugins/platforms/qoffscreen.dll` | 111928 | `d24ef380ab0882d39f21539dcf57ab4213875a6fc658a53012f2d2fd275c6f69` |
| `_internal/PySide6/plugins/platforms/qwindows.dll` | 1001784 | `ddd5cf6a96f058cfafcbc901ddeb5df010d755f0716beacfb557f8b27b733afe` |
| `_internal/PySide6/plugins/styles/qmodernwindowsstyle.dll` | 241464 | `74d4c47b56a942afb3723bb105900501bb8f91a46a8b592fa722cc4fdb2ce9bf` |
| `_internal/PySide6/plugins/tls/qcertonlybackend.dll` | 105784 | `87574d467b6f9640a15e37bf4183179c6a7cefc4dc84346b8f4cffb989cf1e12` |
| `_internal/PySide6/plugins/tls/qopensslbackend.dll` | 317752 | `94b3492bc4087da2818e2749a5a03f7d810611b2e3648bd8d580ad087363046f` |
| `_internal/PySide6/plugins/tls/qschannelbackend.dll` | 249144 | `2915a86a2531e65fd4905f0cc1c8dc353772a4f52aeda5100725dd9249db54d1` |
| `_internal/PySide6/pyside6.abi3.dll` | 262968 | `d5b87ccb0a7c305854bd120242b0a75002d0b50a35532d0f6171e4ed0f3cc82a` |
| `_internal/PySide6/Qt6Core.dll` | 10472760 | `f57ed38afd95d0306cca9d88d997f639f70c7628a4f1f064eae291d579487121` |
| `_internal/PySide6/Qt6Gui.dll` | 9683256 | `abd20026e190e8cc69667d1bea042db05cd353cc05e7da74b063c20b7da3f6cd` |
| `_internal/PySide6/Qt6Network.dll` | 1780536 | `1c7c393b264ae78f4dee211656377a086c4be714bf768d3135f94f11c1d0be61` |
| `_internal/PySide6/Qt6Svg.dll` | 608056 | `8f1de5b28aab1eedb415c751c81f9cfaa2804242868c0ceea5f3fdb4b2babca4` |
| `_internal/PySide6/Qt6Widgets.dll` | 6520120 | `2f62cbe2869fff4e20df7369c2786e1ec7ec290d5a63d1371b7f70cf06909c3f` |
| `_internal/PySide6/QtCore.pyd` | 3521336 | `6486f6f0a2fec42fc8c652c0b76bb3ad0d44eaccad9c72e577116a075681eebb` |
| `_internal/PySide6/QtGui.pyd` | 3936056 | `9ac544d1bcf8a26c408c63090d05506f8382d5378ee3a204e29a3ac5449c5b2b` |
| `_internal/PySide6/QtNetwork.pyd` | 1039672 | `22bffdb2a431b5a986de255f7eb0fcd1fd7d9e85c53967978e2ab479b33a13c5` |
| `_internal/PySide6/QtSvg.pyd` | 116536 | `c9bdacf14ce30f4de75179f999ff20d7a8856126dbebd3a518a5e1c2916a3a6d` |
| `_internal/PySide6/QtWidgets.pyd` | 4911416 | `a8e323e56a93c1a8a70981c36a409c0a2546e7a08da5be8ca4e03dfd27febc2a` |
| `_internal/PySide6/translations/qt_ar.qm` | 104 | `b11333c520ccd8e375cde20985df402d586a1a95e0796313bbeb9f717d4db22e` |
| `_internal/PySide6/translations/qt_bg.qm` | 91 | `1e22ee126ec9f76031d880285a907b3a0c4510392319ff700dcdee964abbb1ad` |
| `_internal/PySide6/translations/qt_ca.qm` | 91 | `17ab2623c7f6e8def44b3dbcb517544185817d65f1298ddb10ef71136f232bdc` |
| `_internal/PySide6/translations/qt_cs.qm` | 95 | `c585918fb1d4821a054ea40bdcf279f275ca76c88a5793f433dac6a611ac7e8f` |
| `_internal/PySide6/translations/qt_da.qm` | 91 | `f6773c672acb73fdef6e092060d69d1e5dfee840012bac912d1e92de28714386` |
| `_internal/PySide6/translations/qt_de.qm` | 91 | `0401c316aa3b50a172eb44a4ff1ec384924073beec7c928ef888ec48e4612688` |
| `_internal/PySide6/translations/qt_en.qm` | 33 | `494ac9a2b2cb2fdeced353f4a9f898ed8dcf616e9bc667438c62681e3f7f79cf` |
| `_internal/PySide6/translations/qt_es.qm` | 91 | `648ed4519bc45d7a4779479a7626ea16cf9aa23e93a0b178546cc47bea0591ab` |
| `_internal/PySide6/translations/qt_fa.qm` | 84 | `3f4c989c6b2990d80cc6299408214b31698923b52f154483b3371875de91f88e` |
| `_internal/PySide6/translations/qt_fi.qm` | 91 | `342d01c7eeb234e431d0506821c4cd03c0433115d8d63fee3357be2331858879` |
| `_internal/PySide6/translations/qt_fr.qm` | 91 | `c896a38892a92346b033793d56440993236b23e47e06f3974afdb0552f628387` |
| `_internal/PySide6/translations/qt_gd.qm` | 70 | `49df855a004a17950338af3146466f6df4d5852410bd0b58ea80e0d0203a9d24` |
| `_internal/PySide6/translations/qt_gl.qm` | 323590 | `204a01ac7deb6b5bae193afecbd1e50d18c73bf7d94badeb2bbfdf6123c4ed93` |
| `_internal/PySide6/translations/qt_he.qm` | 57 | `36f01fff2f25e116d4b7af78097b7e49520fd5b7fb6fb120e40be228c05c045f` |
| `_internal/PySide6/translations/qt_help_ar.qm` | 8743 | `222088c9752d1cc3bab985ef2dc77e5ae78578dce18a61ec15b39f02e588163d` |
| `_internal/PySide6/translations/qt_help_bg.qm` | 10599 | `cbcdd1e0bbae332d80ddb0a286056f17c824fa28d353d7fdf12fc97d9f6fe054` |
| `_internal/PySide6/translations/qt_help_ca.qm` | 7435 | `fe40962c814a9f489e18d033e4aaabe435232c9bcf760830c6165af507cca80e` |
| `_internal/PySide6/translations/qt_help_cs.qm` | 15297 | `4ac56fc63e400943bab13f1d4c418502138908e1d488c24aee6131d3d17552aa` |
| `_internal/PySide6/translations/qt_help_da.qm` | 4795 | `6bb092552a398687119f6d52145f04bf8373977446d8f00c0dcbd56b96829f0f` |
| `_internal/PySide6/translations/qt_help_de.qm` | 7569 | `037bc99abf98571ae9375c2513536c15b571d66406c36c1de447b547ff539c07` |
| `_internal/PySide6/translations/qt_help_en.qm` | 33 | `494ac9a2b2cb2fdeced353f4a9f898ed8dcf616e9bc667438c62681e3f7f79cf` |
| `_internal/PySide6/translations/qt_help_es.qm` | 10704 | `fd16b279f8cf69077f75e94d90c9c07a2afff3948a579e3789f5ffb5e5f4202d` |
| `_internal/PySide6/translations/qt_help_fr.qm` | 3573 | `875ee2dcdc64e3dea888d84048e382d3921a175f12847de2e6b1cb12ad9add50` |
| `_internal/PySide6/translations/qt_help_gl.qm` | 10891 | `7399a248609974773f60866c87b78ea7dfbc4f750313d692f7886cd763883c9f` |
| `_internal/PySide6/translations/qt_help_hr.qm` | 5170 | `8c8cc3c5b1ab2b074f82937001b896603420ef75592b3b78172177360dd7ea61` |
| `_internal/PySide6/translations/qt_help_hu.qm` | 7255 | `7be32e015119c969453abb6e8f3fb377963a69fafb10c27b796737b5eb283eaf` |
| `_internal/PySide6/translations/qt_help_it.qm` | 10612 | `316fe8d0815e2b4b396895beb38ef1a40431915b5e054df80f4c0cd556f26e4b` |
| `_internal/PySide6/translations/qt_help_ja.qm` | 7917 | `ae603b2c0d434d40cde433ffcba65f9ee27978a9e19316007be7fe782a5b8b47` |
| `_internal/PySide6/translations/qt_help_ka.qm` | 7091 | `159c74f94b384b5ee6afdf38b6cfc4806bc99ecf73be02d4a7021d4ceba7ec7e` |
| `_internal/PySide6/translations/qt_help_kk.qm` | 6971 | `de92b7bc46998da4becb07f810e7947f0e22d5f7bf152b8bd7be90375027dfa0` |
| `_internal/PySide6/translations/qt_help_ko.qm` | 5708 | `f11c64694e8e34e1d2c46c1a1d15d6ba9f2db7b61de4fdf54eca5ab977c3e052` |
| `_internal/PySide6/translations/qt_help_nl.qm` | 5087 | `44a8a0daf775d14352180052d13f623814d7bdf98e2c5c80144b7bf74214e3b0` |
| `_internal/PySide6/translations/qt_help_nn.qm` | 6934 | `4c8a7213942078e4f72f5babd26c41b77ace70189714a58b5504a7d5ad0193dc` |
| `_internal/PySide6/translations/qt_help_pl.qm` | 9673 | `cc6cb4d8c54086224672f2e49e623c8cb7c0c1cd65b8d5ecd42fc9ba3a6065bd` |
| `_internal/PySide6/translations/qt_help_pt_BR.qm` | 16030 | `b4015c5d519b4fe93c00bf734d1742e4f0094d89862664d548eb64a46a2feae7` |
| `_internal/PySide6/translations/qt_help_ru.qm` | 7288 | `557b644e6da5f1ec720ef93965617087e4d1f40b2494cc5aa524cf3796108de7` |
| `_internal/PySide6/translations/qt_help_sk.qm` | 10388 | `f41e33e1d790bd0d3eb180f1f875bc191fe74773628f25c2cad95e1402e66867` |
| `_internal/PySide6/translations/qt_help_sl.qm` | 10363 | `2ec955e662407ebcd8dcdae5aaa21e4108e0b5b0aee0e9db712c27072943535f` |
| `_internal/PySide6/translations/qt_help_sv.qm` | 6934 | `95bdb03dbaa6dbdfda46c249e9ccce9a353f71ddb8b112961e8b005b2c60b13c` |
| `_internal/PySide6/translations/qt_help_tr.qm` | 6723 | `81da2f88cd624097581f2d29b10311796bcd9ab289e65883346d276110542d28` |
| `_internal/PySide6/translations/qt_help_uk.qm` | 9750 | `497cfc473684692ee44d7a3795e8fb2270c57069fd9eb98a615dd29ab9be8a7c` |
| `_internal/PySide6/translations/qt_help_zh_CN.qm` | 5115 | `e256d1f6034a5a5521c62f129f91731216e474f71e1d9caea3d3dcb11b670deb` |
| `_internal/PySide6/translations/qt_help_zh_TW.qm` | 5160 | `40112812abb43853d678cc6d97729f21f21b3a7321c827fc9d18f6c936447d1e` |
| `_internal/PySide6/translations/qt_hr.qm` | 102 | `fc9e4146f33be3d09b234be01e56235d3037d8d82d64f0700b4d4a6e253a61a7` |
| `_internal/PySide6/translations/qt_hu.qm` | 84 | `c2fa649f167cdb801d1cc0cb69c1d93594fd5bf8c0b7e79b969935da5c3e19aa` |
| `_internal/PySide6/translations/qt_it.qm` | 91 | `9e7a18bc20ebeec54baaaf41c918a74534511271f796dffffd0f9b9ec31c68d3` |
| `_internal/PySide6/translations/qt_ja.qm` | 84 | `0f5fe50452947d1ee9755249d860354bff6977279b4c496a5bc77e5b89dd745e` |
| `_internal/PySide6/translations/qt_ka.qm` | 94 | `00b67c6dfc255079b5b98a5640f82519c96b2520a028682fba4078b39d743eaa` |
| `_internal/PySide6/translations/qt_kk.qm` | 86 | `23f7ccad75b8b2d70eb0ed0fc910dacc667e9ff65ed1e328c65263ad2d172cda` |
| `_internal/PySide6/translations/qt_ko.qm` | 84 | `1d254b535e1cb35cbcad8210b15b89f4488159826bf35b4504696263dd102fa3` |
| `_internal/PySide6/translations/qt_lg.qm` | 57 | `6ba668501f4c040c66da1bdc022362da3c8cf663da6aa484cbdb599028da98ed` |
| `_internal/PySide6/translations/qt_lt.qm` | 165383 | `47eb5f97467df769261421d54a5bea1131c9fb9b6388791d38bb6574335b64bf` |
| `_internal/PySide6/translations/qt_lv.qm` | 63 | `addeca285282338294f24ca50d37d08a5f68d3785d0a94af86dd4ec8f2a3b449` |
| `_internal/PySide6/translations/qt_nl.qm` | 91 | `39e870cbd25c0f97fa9b1828d5ea1ed9849857a2e26c5321b3f13c76be8f0548` |
| `_internal/PySide6/translations/qt_nn.qm` | 91 | `4e544e23f75eafe1553dc896973db23b5795cd243786d5c653cc0f36a46ca74f` |
| `_internal/PySide6/translations/qt_pl.qm` | 99 | `e6890afa0caf0f6db0248e4c94f6016b8ec8bc266f1e0e9b8f01e8ea912cf968` |
| `_internal/PySide6/translations/qt_pt_BR.qm` | 106 | `0e24c58e35271853f8cdfb3f0f7b0741b5a9a588e43cdec62ae85a3842771e0a` |
| `_internal/PySide6/translations/qt_pt_PT.qm` | 70334 | `2c1e7bbf5168a64b43752dd4c547601c0bde6d610f8671fa3e3af38597e84783` |
| `_internal/PySide6/translations/qt_ru.qm` | 102 | `1b388e2d6d1bd405603e794e498c6d7ec5f5a5ad819243546f6399181da36758` |
| `_internal/PySide6/translations/qt_sk.qm` | 95 | `840c3b01c89df976fc1d2e5bfc6fc84b65666b8a3ceb4cbf5aa0c22af3d2a383` |
| `_internal/PySide6/translations/qt_sl.qm` | 228428 | `c44e0313a9414cc0e490b65b0c036fa11bca959353b228886547bc2c8492034f` |
| `_internal/PySide6/translations/qt_sv.qm` | 91 | `daaae448e0814b469ac3d7a91096fde15491600a6b8bc6c01508425fb5e8b3ec` |
| `_internal/PySide6/translations/qt_tr.qm` | 84 | `59e8a0c411be3b0802a68561b090f182099d6b75c4fe46f398e55f11528e11b9` |
| `_internal/PySide6/translations/qt_uk.qm` | 102 | `053ec1f677c4dba48c6a97eb28f4fc78c1511324d1843d7f4cec2c7c00a66145` |
| `_internal/PySide6/translations/qt_zh_CN.qm` | 99 | `c0e29d32c9540a7e78643b74214e633c56f6ab11f018e516629f2c11b1fb09fc` |
| `_internal/PySide6/translations/qt_zh_TW.qm` | 99 | `24e226954491689549a1a1990db3b8cb78888008d8163b2fd2442b772b6d1b5f` |
| `_internal/PySide6/translations/qtbase_ar.qm` | 160017 | `e03fe68d83201543698fd7fe267dd5dfc5bfd195147e74ff2f19ac3491401263` |
| `_internal/PySide6/translations/qtbase_bg.qm` | 165337 | `e448ac9e3f16c29eb27af3012efe21052daa78fabfb34cd6dff2f69ee3bd3cdb` |
| `_internal/PySide6/translations/qtbase_ca.qm` | 269007 | `5298532fc52ffbc4e2c549f277151a61e741921c834286f7c04d3753677b6b04` |
| `_internal/PySide6/translations/qtbase_cs.qm` | 174701 | `03028b42df5479270371e4c3bdc7df2f56cbbe6dda956a2864ac6f6415861fe8` |
| `_internal/PySide6/translations/qtbase_da.qm` | 181387 | `7d1e5ca3310b54d104c19bf2abd402b38e584e87039a70e153c4a9af74b25c22` |
| `_internal/PySide6/translations/qtbase_de.qm` | 224345 | `a1483bae0385c380edad72b818ce7c2f54ba617ba4c709b2a34a76886d5b5f3d` |
| `_internal/PySide6/translations/qtbase_en.qm` | 33 | `494ac9a2b2cb2fdeced353f4a9f898ed8dcf616e9bc667438c62681e3f7f79cf` |
| `_internal/PySide6/translations/qtbase_es.qm` | 165170 | `4ffda56ba3bb5414ab0482d1dde64a6f226e3488f6b7f3f11a150e01f53fa4c8` |
| `_internal/PySide6/translations/qtbase_fa.qm` | 148156 | `f78e59b5bdd586181a999034ba418868ed17fe9c05707fb65e523f70e92253d2` |
| `_internal/PySide6/translations/qtbase_fi.qm` | 179941 | `e47fe13713e184d07fa4495dde0c589b0e8f562e91574a3558a9363443a4fa72` |
| `_internal/PySide6/translations/qtbase_fr.qm` | 159463 | `314243a55c32679ad473fdfe48dc7d66e973ad0fc8bf2164480c58dddb50c1a7` |
| `_internal/PySide6/translations/qtbase_gd.qm` | 189580 | `63b439dd44139aa3aed54c2ebe03fa9bc77f22c14ed8fba8eff2608445bb233d` |
| `_internal/PySide6/translations/qtbase_he.qm` | 138690 | `e1ebca16afe8994356f81ca007fbdb9ddf865842010fe908923d873b687cad3f` |
| `_internal/PySide6/translations/qtbase_hr.qm` | 149711 | `bb9eec9a9a652c1340dc75eb2e749be50df00f885b3d6900dfc76799c45b244d` |
| `_internal/PySide6/translations/qtbase_hu.qm` | 205885 | `98463295539d769c8645a0b7fb95ad38454cfd0b14f36af485513f036ddbbbc6` |
| `_internal/PySide6/translations/qtbase_it.qm` | 161166 | `7808ed542a7833c4bd94ec8bdfbbca00bb4f2fe15979b9121ce3249323687300` |
| `_internal/PySide6/translations/qtbase_ja.qm` | 129913 | `2b9581c69b975f59be505b127cd3c19d403ef3d12e0e8386fb97238223e9c1df` |
| `_internal/PySide6/translations/qtbase_ka.qm` | 201105 | `e55e4b72fa620bebee5297ca59dfe2f49894a1e544f2b7485b1cfd8829289d6f` |
| `_internal/PySide6/translations/qtbase_kk.qm` | 259281 | `8bab72c453e87489d76cc7efffc57e947cbfa239dee4d6fa113f7b7b8cbd5b86` |
| `_internal/PySide6/translations/qtbase_ko.qm` | 156799 | `0179ed1b136e1cb3f583351eaa2c545ba3d83a6ee3f82c32505926a1a5f5f183` |
| `_internal/PySide6/translations/qtbase_lg.qm` | 315764 | `31c0cc4ce13b1d74fe0c19ed0b47638fb31e20c93ee08092533e884007aebfb5` |
| `_internal/PySide6/translations/qtbase_lv.qm` | 153608 | `846e047573ae40c83671c3ba7f73e27efc24b98c82701da0df9973e574178bb2` |
| `_internal/PySide6/translations/qtbase_nl.qm` | 202861 | `f61513bcdbb6ad800585f9437a95d018aab17fa12ee414aa31462ff279d8240e` |
| `_internal/PySide6/translations/qtbase_nn.qm` | 196411 | `f9f2fb7c60e7fcb38bbd3c1314ef122145594265e20b0659ff00004baab13ac7` |
| `_internal/PySide6/translations/qtbase_pl.qm` | 162962 | `3cf6b5c14d5eb0cf81e9af2066e66b3aa579a6b9b3c323ed670761f6254a8c54` |
| `_internal/PySide6/translations/qtbase_pt_BR.qm` | 290955 | `3475d61604b938d459949801a906dbd34a8ca824ade94120015d676e208da859` |
| `_internal/PySide6/translations/qtbase_ru.qm` | 203767 | `3da6605668f9178d11a838c4515478084dcfb4f9cf22f99d7a92b492db9c224b` |
| `_internal/PySide6/translations/qtbase_sk.qm` | 125763 | `d586ae2c314074cf398417fdecb40709d5478dfeb0a67c2fe60d509ee9b59ed7` |
| `_internal/PySide6/translations/qtbase_sv.qm` | 249963 | `5a2178dd2c03cc4516697f1fb0049649c9ed53f5cde6b937786733dae06aeda8` |
| `_internal/PySide6/translations/qtbase_tr.qm` | 248720 | `353fdfd7165659a49212e7a25bf91c0a71588e52c836f7496640f26782414634` |
| `_internal/PySide6/translations/qtbase_uk.qm` | 158274 | `51b8ff55b37dc5907d637a8ddda12fbe816852b0244c74eb4f0fb84867a786e0` |
| `_internal/PySide6/translations/qtbase_zh_CN.qm` | 147222 | `0481a9b92a6f0578400e960a7d5ee70217a6a450eaf7f98b7d32b8dbd0d58616` |
| `_internal/PySide6/translations/qtbase_zh_TW.qm` | 126185 | `21012b2b427f8d09d31ce9cae582ca27955b478ca3dc2ec18a3068d808638c6a` |
| `_internal/PySide6/VCRUNTIME140.dll` | 116024 | `a36e0cb185eb89533ed96d4568138f86a1315756a8b2644c5963a8ce23e32101` |
| `_internal/PySide6/VCRUNTIME140_1.dll` | 41272 | `302b1e160e858602490a55e32ae2e29ddfc0bec2a188e19550cb655cdaa58f9c` |
| `_internal/python3.dll` | 73952 | `7bb0a7df2d5cb829319dd8d122039843e2a762361bb5a61bb5d24ca34f4040b5` |
| `_internal/python314.dll` | 6816992 | `d8a06cc6ca3348925ea29e343e1c5c5895fe0bb433ff913e1cee44caf358aa6a` |
| `_internal/select.pyd` | 33504 | `0da869c017fd3231cfc1c1e4c4bef1bb7bf5cba38236e6d7bf1630c3507c5a1d` |
| `_internal/shiboken6/MSVCP140.dll` | 549176 | `1ba4d7c0a95d375da138a057a57593b33510ad5bda6c5e2686afd68faa5b4231` |
| `_internal/shiboken6/Shiboken.pyd` | 33080 | `8ccf415b2cefb5b6462504581ab1993fb41afe04e415931d8a72049f1c79b267` |
| `_internal/shiboken6/shiboken6.abi3.dll` | 399672 | `07c318c02be5a3a9f1475f5a2d0cd438f4d4ea3288c28e2e10bc5ebbbec8de86` |
| `_internal/shiboken6/VCRUNTIME140.dll` | 116024 | `e7be9112ee9a5b9f44b44bff24cb761cca9b1ed7550b612f77b70edfcf5fdabf` |
| `_internal/shiboken6/VCRUNTIME140_1.dll` | 41272 | `f02cd4a862b85a9a3153d27e15e5a213f5df8e3d77004ed2e87b8a7e8873d97c` |
| `_internal/sqlite3.dll` | 1584864 | `99c296ca2b4372418edbdcbd923ab0df2cdbcf406782694d7376f2b01e5010c9` |
| `_internal/unicodedata.pyd` | 758496 | `4c4e9f9e71e299a7e0093830e79f955f2b12b4eb0a6bb45003d42256b6e5985d` |
| `_internal/VCRUNTIME140.dll` | 178616 | `d1f4225df2cd877dbf130d5668a021dce3f94118455ff5ec952061c30afc9ce7` |
| `_internal/VCRUNTIME140_1.dll` | 50112 | `a7146c08f89fe5b04541ab507cdb59ff7b44534d4ba3c668a426c6450a03434e` |
| `LogSentinel-GUI.exe` | 2386859 | `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01` |
