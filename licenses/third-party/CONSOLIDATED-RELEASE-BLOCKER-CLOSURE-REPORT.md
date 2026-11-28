# Consolidated Release-Blocker Closure Report

**Assessment date:** 2026-11-27  
**Artifact in scope:** `dist/gui-ondir-trim-test/LogSentinel-GUI/` (verified trimmed Windows onedir test package)  
**Disposition:** **HOLD — NOT CLEARED FOR DISTRIBUTION.**  

This report consolidates engineering evidence and release gates. It is not legal advice, a legal opinion, a compliance determination, or permission to distribute. It distinguishes facts about the named package from public upstream statements, candidates, assumptions, and unresolved legal questions. No conclusion is made that an obligation has been triggered, satisfied, or breached without the necessary grant and conveyance facts.

## 1. Executive decision

Do not distribute the identified package on the present record. The package identity is established, and several formerly uncertain binary-delivery questions have been narrowed, but material rights, license-scope, source, notice, and release-channel questions remain unresolved. In particular:

1. No binary-specific Qt/PySide6/Shiboken license election or commercial entitlement is established. If an LGPLv3 route applies to conveyed components, neither LGPLv3 §4(d) route has been demonstrated for this exact package, and the distribution has no end-user notice/license documents.
2. Microsoft runtime files are present. Eight nested 14.44.35211.0 files are proven to be wheel payloads signed by Qt; this does not establish Microsoft-source identity, Qt's rights chain, or downstream redistribution eligibility. The two root 14.51.36247.0 files have separate provenance/terms questions.
3. The notice collection is an evidence repository, not a release bundle. It contains alternative, candidate, and historical materials. It cannot be copied wholesale or represented as complete for the package.
4. Source-to-binary/build provenance remains incomplete for Qt components and other embedded dependencies. The hash-verified Qt wheel evidence establishes delivery identity for the PySide6/Shiboken6 wheel payload, not which source, patches, configuration, or build produced those binaries.
5. The final distribution channel, recipient terms, installer/update/signing restrictions, and applicable rights review have not been specified or approved.

No release gate is closed by functional testing, upstream version labels, Authenticode signatures, a local `RECORD`, an available license text, or the existence of a same-version source archive. Qualified counsel and the release owner must review the actual intended conveyance and exact final artifact before any release decision.

## 2. Scope, artifact identity, and method limits

### 2.1 Audited artifact

- Directory: `dist/gui-ondir-trim-test/LogSentinel-GUI/`
- **182 regular files; 80,058,228 bytes** total.
- Root executable: `LogSentinel-GUI.exe`, **2,386,859 bytes**, SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- Inventory summary: 42 DLLs, 16 PYDs, 99 Qt `.qm` catalogs, 22 SVGs, one ZIP, one ICO, one EXE.
- The package has no `.txt`, `.md`, or `.rst` license/notice file.
- Exact excluded paths: `_internal/PySide6/Qt6Pdf.dll`, `_internal/PySide6/plugins/imageformats/qpdf.dll`, and `_internal/PySide6/opengl32sw.dll` are absent. Qt PDF/PDFium and Mesa/LLVM materials in older inventories are not automatically in scope for this artifact.
- The 22 SVGs and ICO are LogSentinel GUI assets; existing scans did not identify third-party code or external resource links in them.

This is the 182-file trimmed package, not the historical 185-file package described in `OTHER-COMPONENTS-INVENTORY.md`, `ATTRIBUTION-SOURCE-REGISTER.md`, `qt/INVENTORY.md`, and older notice documentation. Present-but-not-loaded files remain part of a distribution inventory. A host Windows DLL or dependency resolved from Windows System32 is not a bundled file on the evidence reviewed; host compatibility remains a separate issue.

### 2.2 Evidence labels

- **Package fact:** observed path, file, hash, version marker, or recorded test for this named artifact.
- **Strong delivery identity:** package bytes are matched to an archive payload whose archive digest matches the official published digest. This does not prove source/build provenance or licensing rights.
- **Upstream statement/candidate:** a public source, license page, release, or attribution. It does not alone prove that the shipped binary came from it.
- **Possible / unresolved:** markers, generic symbols, or vendor attributions suggest a component, but exact identity/version or package mapping is not established.
- **Conditional legal issue:** relevance depends on the applicable grant, work relationship, conveyance, and distribution terms; no legal trigger is presumed here.
- **Open blocker:** evidence or decision needed before release review can be completed. “Blocker” is a release-control classification, not a finding of infringement or noncompliance.

### 2.3 Source reports reconciled

This report gives precedence to the package-specific and later corrective evidence in:

- `FINAL-LICENSING-AUDIT.md`, `FINAL-THIRD-PARTY-NOTICE-RECONCILIATION.md`, and `RELEASE-PREPARATION-CHECKLIST.md`;
- `QT-PYSIDE-LGPL-DISTRIBUTION-ASSESSMENT.md` and `QT-PYSIDE-LGPL-GAP-CLOSURE-PLAN.md`;
- `QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md`, `QT-PYSIDE-BINARY-PROVENANCE-REPORT.md`, `QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md`, and `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`;
- `TRIMMED-PACKAGE-NOTICE-MAP.md`, `RUNTIME-LICENSING-EVIDENCE.md`, `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`, and relevant upstream texts in `notices/`.

Where an older document conflicts with a later correction, the conflict and the controlling evidence are stated in §4. This report does not overwrite or amend those source records.

## 3. Component-by-component shipped-component matrix

The matrix covers every third-party component or code family supported by current package evidence. It separates an available candidate text from a confirmed applicable notice. A “candidate in repository” is not authorization to ship that file or proof that it covers the exact binary.

| Shipped component / package evidence | Published license/notice evidence and local materials | Status and release closure required |
|---|---|---|
| **Qt 6.12.0 Core, Gui, Network, Widgets, Svg** (`Qt6*.dll`) | Qt publishes LGPL/GPL and commercial options with file/module-specific scope. `licenses/LGPL-3.0.txt`, `licenses/GPL-3.0.txt`, and Qt vendor HTML exist in the repository, not in the package. Wheel metadata for PySide6/Shiboken6 says `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; public Qt for Python language does not resolve the GPLv2 discrepancy. | **Present; license basis/election and rights open.** Obtain written, binary/version-specific Qt confirmation, component map, and any commercial entitlement evidence. Counsel must determine the applicable grant and conveyance conditions. |
| **Qt plugins (20)**: platform, image formats, SVG/icon, network-information, TLS, style, generic | Qt per-file/module terms and independent code embedded in plugins may apply. Qt 6.12.0 version resources, Qt signatures, PDB path clues, and wheel payload evidence identify the family; exact source/build/SBOM map is absent. | **Present; source, license-file scope, and notices incomplete.** Obtain plugin-to-source/build and third-party component records, including any file-specific GPL-only terms, and prepare only matched notices. |
| **PySide6 bindings**: five `.pyd` modules and `pyside6.abi3.dll`; embedded PySide Python code objects | Qt for Python publishes license alternatives and third-party notices; the local Qt for Python distribution metadata is useful but is not a binary-specific election/build attestation. | **Present; exact applicable terms and source/build scope open.** Get Qt's written response for the identified wheel hash and code scope; map copied/generated materials and notices. |
| **Shiboken6**: `Shiboken.pyd`, `shiboken6.abi3.dll`, embedded helper module | Qt for Python/Shiboken public licensing and third-party materials are candidates; no complete per-file source/copy map or election is established. | **Present; terms and notices incomplete.** Obtain Shiboken-specific source, copied/adapted code, license and build mapping. |
| **Qt translations: 99 `.qm` files** | QUIP 18 describes usual translation `.ts` files as `LicenseRef-Qt-Commercial OR BSD-3-Clause`; individual files may differ. The actual `.qm` files match the Qt wheel payload, but source catalog/contributor map is absent. | **Present; independent license/attribution scope unresolved.** Map every catalog to source, copyright/contributor/license and `lrelease` inputs. Do not automatically classify all catalogs as LGPL libraries. |
| **FreeType in QtGui** | `FT_*`/font-engine markers and Qt 6.12 attribution suggest FreeType 2.14.3. FTL and GPLv2 are alternative grants; both texts and Qt attribution are collected, neither selected. | **Present; version/election/source map open.** Obtain exact Qt build mapping and rights decision; counsel/vendor must resolve applicable branch before a notice can be prepared. |
| **HarfBuzz in QtGui** | HarfBuzz symbols and Qt attribution indicate 14.5.0; `COPYING.txt` and Qt attribution are collected. Exact embedded files and exceptions are not matched. | **Present; notice mapping incomplete.** Match source files/version and applicable exceptions against Qt build/SBOM. |
| **libpng in QtGui** | Package marker reports 1.6.58; upstream license and Qt attribution candidates are available. | **Present; version evidence comparatively strong, build/source match open.** Confirm Qt snapshot and include exact license/attribution in a curated bundle if applicable. |
| **PCRE2 and SLJIT in QtCore** | PCRE2 evidence in QtCore; Qt 6.12 attribution identifies PCRE2 10.48 and separately attributes SLJIT. PCRE2 license and both Qt attribution pages are collected. | **Present; exact version and object/SLJIT mapping open.** Verify exact linked source and preserve the distinct applicable notices/exceptions. |
| **libjpeg-turbo in `qjpeg.dll` and `qtiff.dll`** | Both plugins report libjpeg-turbo 3.2.0. Versioned license and `README.ijg` materials are collected; applicable APIs/subcomponents determine exact terms. | **Present; composition and notices incomplete.** Map plugin code/API usage and required IJG/BSD/subcomponent wording; do not reuse the superseded 3.2.1 assumption. |
| **libtiff in `qtiff.dll`** | `LIBTIFF_*` and “Since libtiff 4.5.1” markers establish presence/lower-bound only. Qt later-patch attribution gives 4.7.2 as a candidate, not a match for this Qt 6.12.0 package. Exact versioned notice not in collection. | **Present; exact version and notice set unresolved.** Obtain the Qt 6.12.0 build snapshot and corresponding license/component notices. |
| **libwebp in `qwebp.dll`** | WebP code/format evidence; Qt later-patch attribution suggests libwebp 1.6.0, not proof for the shipped plugin. BSD text and patent scope are not validated in the collection. | **Present; exact version, notices, and patent materials open.** Obtain matching source/build attribution and review relevant patent grant materials. |
| **C++/WinRT in QtCore** | Version string `2.0.250303.1`; MIT license candidate collected. | **Present; version marker supported, source commit/build match open.** Confirm included source and use exact copyright/permission text. |
| **zlib-compatible code in QtCore** | zlib-family symbols/messages; Qt attribution says zlib, but the binary evidence does not distinguish zlib, zlib-ng, or another compatible implementation. | **Possible/present family; exact implementation, version, and notice unresolved.** Obtain Qt source/SBOM; do not assert zlib-ng or apply the zlib-ng 2.2.4 candidate by inference. |
| **CPython 3.14.10 runtime, standard library and frozen stdlib modules** | PSF license and README/copyright materials are collected. The package version is identified; exact Windows source/build provenance is not matched. Python does not subsume independently licensed embedded dependencies below. | **Present; core text available, file/build and embedded-code mapping incomplete.** Match the Windows distribution/build and distinguish third-party extensions. |
| **CPython “Microsoft Distributable Code” terms** (local `C:/Python314/LICENSE.txt`) | Local interpreter license is 35,407 bytes/676 lines and includes that section. Collected CPython `LICENSE.txt` is 13,804 bytes/277 lines and lacks it. | **Open independent rights/terms issue.** Determine exact applicability to shipped CPython files/build and downstream rights with evidence and counsel; do not assume the shorter collected text closes it. |
| **Unicode Character Database 16.0.0** in `unicodedata.pyd` | Package version evidence; Unicode License V3 and UCD ReadMe are collected and hash-verified against the local manifest. Exact CPython build-input mapping remains open. | **Present; candidate text available, source-input match open.** Tie the data and applicable notice to the exact CPython build. |
| **bzip2 1.0.8** in `_bz2.pyd` | Version marker and upstream bzip2 1.0.8 license collected. Exact embedded source/patch identity is not established. | **Present; versioned license candidate available.** Confirm build input and prepare required notice/disclaimer if applicable. |
| **Zstandard 1.5.7** in `_zstd.pyd` / `compression.zstd` | Version evidence; upstream BSD-style and GPLv2 texts are both collected as alternatives. Downstream election is not recorded. | **Present; election open.** Determine and document the applicable option, then include only the reviewed applicable material; alternatives are not cumulative. |
| **mpdecimal 4.0.0** in `_decimal.pyd` | CPython build-path evidence and source archive-derived copyright material; exact embedded source/patch match remains open. | **Present; candidate notice available, source match partial.** Confirm the CPython build input and exact notice. |
| **SQLite 3.50.4** (`sqlite3.dll`, `_sqlite3.pyd`) | Version/source-ID evidence; SQLite states its implementation is public domain. Local page is courtesy information, not a required license. | **Present; public-domain statement/version supported.** No separate license text required on current evidence; retain precise, non-misleading optional attribution if used. |
| **liblzma / XZ-derived code** in `_lzma.pyd` | Presence established; exact version and license vintage unknown. No version-matched text is collected. XZ Utils contains different license scopes; do not infer tools' terms or modern liblzma terms. | **Present; version/license unresolved.** Obtain exact CPython build source and file-level license; no candidate election by assumption. |
| **zlib-compatible code in CPython** (`python314.dll`) | `zlib-ng` and `1.3.1` strings; the number may be zlib API compatibility, not a zlib-ng release. zlib-ng 2.2.4 text is only a candidate. | **Present/possible; exact identity/version and notice unresolved.** Match exact CPython source/build input before selecting text. |
| **OpenSSL 3.5.9** (`libcrypto-3.dll`, `libssl-3.dll`) | Build string and byte-equality to local CPython DLL copies; official 3.5.9 source archive digest was verified in the prior audit. Apache-2.0 license and `ACKNOWLEDGEMENTS.md` are collected; no `NOTICE` file was found in the inspected archive. Packaged DLL build from that archive is not established. | **Present; license candidate available, build provenance/complete notices open.** Tie DLLs to CPython build inputs and review Apache obligations. Do not relabel acknowledgements or invent a NOTICE; the NOTICE-file issue remains conditional. |
| **PyInstaller bootloader and loader/bootstrap code** in executable | Build metadata says 6.22.3. `COPYING.txt` distinguishes GPL-2.0-or-later with Bootloader Exception for bootloader/loader from other code. Executable sections match installed `runw.exe` except four uninterpreted `.rdata` bytes, plus expected resources/archive. | **Present; license mapping known in principle, pristine/modification status and source map open.** Do not claim unmodified. Validate exact CArchive/bootloader entries, exception scope, GPL-2 text/source implications with counsel. |
| **PyInstaller runtime hooks and `_pyi_rth_utils`** | Embedded runtime hooks/modules map under PyInstaller's `COPYING.txt` to Apache-2.0; `hook-PySide6.QtSvg.py` has a different GPL/Bootloader Exception header and is a build-time hook. | **Present; file scopes must remain distinct.** Verify exact payload mapping and curate appropriate terms; do not label all PyInstaller entries Apache or all GPL. |
| **Microsoft VC++ runtime, 14.51.36247.0 (2 root copies)** | Microsoft-signed; byte-identical to local CPython/System32 copies. Official Microsoft versioned installer evidence establishes a versioned release but payload-to-package and eligibility chain are not established. | **Present; Microsoft terms and exact redistribution basis open.** Obtain applicable terms and rights/eligibility for these copies; decide serviced deployment path. |
| **Microsoft VC++ runtime, 14.44.35211.0 (8 nested copies)** | Five PySide6 and three Shiboken6 DLLs. Each matches the case-normalized entry and `RECORD` in cached Essentials/Shiboken wheels whose archive hashes/sizes match Qt's published digests. All eight are signed by The Qt Company. Same-version local Microsoft REDIST candidates are not byte-identical. | **Wheel delivery identity established; Microsoft origin, Qt supplier rights, and downstream eligibility open.** Obtain written Qt provenance/redistribution basis, exact Microsoft file/source chain, applicable terms and counsel review. Do not infer authorization from wheel inclusion, version, signature, or `RECORD`. |

### Components not treated as shipped third-party libraries

- **Windows ICU/system libraries, SChannel, UCRT, and OS APIs:** no separate bundled ICU DLL was found; prior runtime observations reported ICU resolving from Windows System32 on the test host. These are host dependencies, not package contents on current evidence. Validate supported Windows targets independently.
- **LogSentinel SVG/ICO assets:** project assets, not identified as third-party.
- **Qt PDF/PDFium, qpdf, Mesa/LLVM:** excluded paths absent in this artifact. Their historical notice texts are not included automatically.
- **TinyCBOR, MD4C, double-conversion, libpsl/PSL, Brotli code, and other speculative strings/helpers:** no affirmative component-to-binary evidence in the reviewed trimmed inventory. Do not assert present or absent from isolated strings alone; request Qt SBOM if appropriate.
- **`pyinstaller-hooks-contrib`:** build-time dependency, not identified in the frozen runtime payload; no end-user runtime notice is attributed from current evidence.

## 4. Reconciliation of contradictions and evidence hierarchy

| Older or conflicting statement | Corrected consolidated result | Basis and limit |
|---|---|---|
| Historical reports inventory 185 files, with Qt PDF/PDFium and Mesa/LLVM. | Current artifact is 182 files; Qt6Pdf, qpdf, and opengl32sw are absent. | Current path/hash inventory and trimmed-package reports control. Older reports remain useful historical evidence only. |
| Earlier source evidence said eight nested VC++ DLLs were absent from wheels or had no RECORD hash. | All eight are present in corresponding case-normalized PySide6 Essentials/Shiboken wheel payloads and match their internal RECORD hashes/sizes. | Corrected comparison in `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`; cached wheel archive sizes and SHA-256s match Qt-published values. This proves wheel payload delivery, not Microsoft origin or redistribution rights. |
| Earlier Qt/PySide provenance report said no verified upstream binary/wheel match. | For wheel-contained PySide6/Shiboken6 files, archive identity is now strongly established, including Qt DLL/plugin files present in the Essentials wheel. | Later cache-body SHA-256 and wheel-entry comparisons supersede the older “wheel match unverified” conclusion for those files. They do not establish source-to-build provenance, and do not match separate Qt installer-component archives. |
| Older local installed RECORD analysis counted only 132 of 140 matching files. | Subsequent archive/member comparison validates all 140 PySide6/Shiboken tree files against cached wheels and `RECORD`. | Earlier path comparison was case-sensitive for DLL names. The evidence hierarchy is cached archive digest + normalized wheel entry + RECORD, while preserving the missing source/build/rights edges. |
| Qt 6.12 attributions may list later patch versions, e.g. libtiff/libwebp, as though they were the shipped 6.12.0 versions. | Those pages are vendor candidates/context, not proof of the exact Qt 6.12.0 binary snapshot. | No package-matched Qt SBOM/build record is established. Keep exact version and notice rows unresolved. |
| An earlier CPython inventory treated a generic PSF text as all applicable runtime terms. | The local Python 3.14.10 license contains a “Microsoft Distributable Code” section absent from the collected shorter CPython license text. | Exact affected files, distribution scope and terms require file/build-specific evidence and legal review. |
| Earlier OpenSSL wording implied an obligatory NOTICE based on project name/acknowledgements. | Inspected OpenSSL 3.5.9 archive had `ACKNOWLEDGEMENTS.md` but no file named `NOTICE`; no NOTICE is invented. | Apache NOTICE handling is conditional on the Work including such a file, and the packaged DLL build is not conclusively matched to that archive. |
| Prior summaries sometimes treat package load snapshots as showing a single uniform runtime set or that files are unnecessary. | Ten VC++ DLL copies are distributed (two 14.51 root and eight 14.44 Qt-signed nested). A captured run loaded only five; this does not prove other copies are unnecessary or establish loader behavior on every target. | Package presence is controlling for redistribution scope; do not delete/replace files on the basis of one run. |
| Any claim that PyInstaller is uniformly GPL or Apache. | Bootloader/loader: GPL-2.0-or-later with Bootloader Exception; runtime hooks and `_pyi_rth_utils`: Apache-2.0; `hook-PySide6.QtSvg.py` is a build-time hook with GPL/exception header. | File-specific scope in PyInstaller 6.22.3 `COPYING.txt` and source headers. Bootloader modification status remains open. |

**Evidence hierarchy for this report:** actual current package paths and cryptographic hashes → later corrected archive/payload comparisons → versioned upstream texts and component markers → generic vendor pages and historical package inventories. Lower-level evidence is not promoted to a stronger claim than it supports.

## 5. Classified release blockers and risks

### 5.1 Release-blocking evidence/decision gates

**B1 — Intended distribution and rights basis not defined (critical).** Recipient groups, territories, distribution channel, installer, EULA, update/signing/anti-tamper policy, and any commercial Qt agreement are not established. No legal analysis can close the gates without those facts.

**B2 — Qt/PySide/Shiboken terms and license scope (critical).** No written binary-specific license election or complete component map; PySide metadata/public-description GPLv2 discrepancy unresolved; Shiboken-specific copied-code scope open. The existence of public LGPL/GPL/commercial options does not establish which one applies to the exact package.

**B3 — Conditional LGPL/GPL conveyance route (critical if applicable).** If covered Qt/PySide libraries are conveyed under LGPLv3 as a Combined Work, the relevant §4 notice/text, one §4(d) route, and no-effective-restrictions conditions require counsel review. Neither §4(d)(0) source/relink/application-code route nor §4(d)(1) suitable shared-library mechanism is demonstrated for this exact artifact. §4(c), §4(e), and LGPL §3/header-material issues are conditional and unresolved, not assumed triggered.

**B4 — Microsoft runtime redistribution basis (critical).** The ten runtime files are present. Their source chain and eligibility under the actual Microsoft terms are not established for the intended distributor/channel. In particular, Qt-signed nested DLLs matching a Qt wheel are not thereby shown to be Microsoft unmodified REDIST files or licensed downstream copies. The root Microsoft-signed files also require an applicable terms/source trail.

**B5 — Package-matched recipient notices and source access (critical).** No license/notice text exists in the package. The local 35-file notice collection has 34 manifest rows verified, but it is not a curated distribution payload: it contains alternatives, candidates, local notes, and historical/removed-component material. A reviewed notice set and applicable corresponding-source/offer/relink plan are not established.

**B6 — Embedded component and source/notice mapping (high).** Qt static components/codecs, translation catalogs, CPython build inputs, liblzma, zlib-compatible implementations, FreeType/Zstandard elections, libtiff/libwebp notices and patent materials, and some PyInstaller mapping remain unresolved. The extant notice texts alone do not close these rows.

**B7 — CPython Microsoft Distributable Code scope (high).** The local interpreter license contains the clause, unlike the collected CPython text. Exact scope, affected package files, applicable terms, and downstream permissions need evidence and counsel review.

**B8 — PyInstaller GPL/exception and bootloader modification/source status (high).** The license family split is identified, but source-entry mapping and the four-byte `.rdata` difference are not resolved. Do not claim an unmodified bootloader or assume the consolidated COPYING alone answers all source/text duties.

### 5.2 Non-licensing release risks (not legal clearance gates by themselves)

- RDP, GPU-less/software-rendering, and high-DPI compatibility are not fully tested. The standard desktop workflow passed with PDF/Mesa exclusions; the compatibility report rates current exclusions provisionally and requires target tests before broad support claims.
- Qt's ICU imports were observed resolving from Windows System32 on one host. Minimum supported Windows/host dependency remains open.
- Local application copies of VC++ runtime raise duplicate-path and servicing concerns. A single load snapshot is not a complete trace; central versus app-local deployment needs technical and legal review.

These risks should be closed as release readiness issues but must not be used to imply or deny any license obligation.

## 6. Distribution options for decision and legal review

No option below is approved by this engineering report.

1. **Remain on HOLD / do not convey this artifact.** This is the present recommendation until rights and release gates are reviewed. Internal possession or testing should not be used to infer permission for public or customer distribution.
2. **Potential LGPLv3 distribution path, if available and applicable.** Counsel and Qt must establish the grant/scope and intended conveyance, then select and substantiate §4(d)(0) or §4(d)(1), prepare applicable notices/texts/source materials, and assess §3, §4(c), §4(e), installation and recipient terms. The existing onedir layout is only a technical starting point; no replacement/relink route is proven.
3. **Potential GPL path, only if the exact components offer it and the combined work/channel can satisfy its terms.** This is not a shortcut around source obligations, exact component scope, third-party terms, or the PySide metadata discrepancy. The resulting implications for the whole work must be reviewed by counsel.
4. **Potential commercial Qt/Qt for Python rights.** This could provide a route for covered Qt components if an applicable agreement exists and covers the product/channel. No agreement is evidenced. Commercial Qt rights do not automatically resolve Microsoft runtime, CPython, PyInstaller, translation, or embedded third-party terms.
5. **Change package/product scope or technology.** If required rights/source/notice conditions cannot be established, the release owner may authorize removing/replacing affected components or choosing another GUI path. That is a separate engineering/product decision requiring a new package audit; no code, spec, or binary change is made here.
6. **Microsoft runtime deployment alternative.** Evaluate centrally installing an official Microsoft Redistributable as a future packaging strategy with counsel, Qt, and the release owner. This is not a present authorization to delete or replace wheel-supplied DLLs. It requires license review, a documented servicing owner, loader tests and a fresh package validation.

A notice-only patch, signature, version match, or copy of repository source material is not a substitute for the relevant rights or a substantiated route.

## 7. Prioritized closure roadmap

### P0 — Freeze scope and maintain HOLD (release owner)

Record intended recipients, territories, channel, installer/portable layout, EULA, updates/signing/anti-tamper controls, whether any conveyance is planned or has occurred, supported Windows targets, and exact artifact identity. Preserve the package and existing evidence; make no source/spec/binary/notice edits under this report.

**Exit evidence:** written release-scope statement and exact candidate/channel for counsel. Disposition remains HOLD until all required gates close.

### P1 — Obtain qualified legal review and rights-holder responses (release owner + counsel + Qt)

Ask counsel to review exact grants, conveyance facts, LGPLv3 §§3–4 (including conditional §4(c)/(e)), GPLv3 §6 where relevant, PyInstaller file scopes/exception, Microsoft runtime terms and eligibility, CPython clause, end-user restrictions, and the proposed installer/update model. Ask Qt for written answers tied to the exact wheel digests and package component set.

**Exit evidence:** documented counsel advice/decision and rights basis for each distribution route, or an explicit decision to remain on hold/change scope.

### P1 — Close Qt license and VC++ supplier/rights questions

Request Qt's license elections/options for exact Qt/PySide6/Shiboken6 distribution hashes; resolve the GPLv2 metadata discrepancy and Shiboken scope; obtain exact source/build records, third-party SBOM, translation mapping, and written sourcing, signing/transformation, and downstream rights basis for all eight Qt-signed VC++ hashes. Obtain Microsoft's applicable complete terms and determine the distributor's eligibility for all ten copies.

**Exit evidence:** authenticated or otherwise reviewable, artifact-specific vendor records and counsel's assessment. Silence, signature, wheel `RECORD`, and matching version are not substitutes.

### P2 — Establish source/build/notice traceability

Create a per-file mapping for the exact package: package path/hash → wheel/archive hash and entry (where applicable) → upstream source path/commit → patches/generated inputs → build job/configuration/toolchain/dependencies → license/copyright/notice evidence. Obtain Qt/PySide wheel-scoped SBOMs and source/build records. Match CPython, OpenSSL, PyInstaller and native extension inputs. Resolve the 99 `.qm` files individually. Keep exact-version unknowns explicit.

**Exit evidence:** complete traceability matrix or clearly enumerated unresolved rows accepted by counsel as a reason to change distribution route; applicable corresponding source/build materials identified.

### P2 — Select and validate an LGPL route if triggered

If counsel determines LGPLv3 §4 applies, choose one route:
- For **§4(d)(1)**, run a recipient-controlled replacement test on a separate copy of this exact package, including coherent compatible library/plugin/binding sets, loader paths, permissions, launch and workflows; review legal/technical restrictions.
- For **§4(d)(0)**, assemble the required Minimal Corresponding Source and Corresponding Application Code, exact build/configuration materials and permitted relink/recombine instructions; test from a clean recipient environment.

Counsel must assess applicable text, any source-offer/conveyance method, §4(c), §4(e), §3, installer/EULA and signing restrictions. A technically successful test is not legal clearance.

**Exit evidence:** counsel-reviewed path, tested artifact-matched procedure/materials, and documented user rights/availability.

### P3 — Resolve individual component notice choices

Resolve FreeType election; Zstandard option; zlib-compatible source identity; liblzma/XZ vintage; libtiff/libwebp version, notices and patent scope; PCRE2/SLJIT object map; libjpeg-turbo APIs/subcomponents; C++/WinRT and other confirmed Qt third-party code; CPython Microsoft Distributable Code scope; OpenSSL source/build and NOTICE-file question; PyInstaller bootloader status and GPL-2/exception needs. Select only applicable materials—no speculative or historical notices.

**Exit evidence:** version/file-matched notice/attribution set approved by counsel/rights holders where necessary.

### P3 — Close technical compatibility and servicing

Complete RDP, GPU-less/software-rendering, high-DPI and clean-target Windows testing for the declared supported environment; assess ICU/system dependencies. Decide central vs app-local VC++ servicing and identify an owner for security updates. Any deployment change requires separate authorization and re-inventory.

**Exit evidence:** supported-platform evidence and an operational runtime servicing plan.

### P4 — Build a reviewed end-user set and revalidate final candidate

Only after rights and scope are established, assemble a concise, version-pinned user-facing notice/license/source set. Do not ship internal audit reports, candidate alternatives, local status notes, or the complete notices folder wholesale. Add materials only to an authorized candidate, then re-inventory/hash it, verify all texts and source instructions, rerun tests, and obtain release-owner/counsel approval for the exact artifact and channel.

**Exit evidence:** written approval tied to final artifact hashes and distribution terms. Any change reopens the applicable review.

## 8. Questions requiring external confirmation or legal counsel

### Questions for Qt / Qt for Python

1. Which exact license grant/election applies to each Qt 6.12.0 module/plugin, PySide6 Essentials and Shiboken6 file and wheel hash? How should the PySide metadata's GPL-2.0-only alternative be reconciled with Qt for Python's public description?
2. What source commits/tree hashes, downstream patches, generated sources/typesystems, compiler/SDK/configuration, CI job/build IDs, and exact third-party SBOM correspond to the cached Essentials wheel hash `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42` and Shiboken wheel hash `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e`?
3. Which exact source snapshots and license/notice scopes are embedded in each Qt library/plugin, especially FreeType, HarfBuzz, PCRE2/SLJIT, zlib-compatible code, image codecs, translations and copied Shiboken code?
4. Which `.ts` sources and per-file contributors/licenses correspond to each of the 99 `.qm` catalogs, and what `lrelease` version/options produced them?
5. For the eight nested VC++ file hashes, what Microsoft payload/source hashes were used? Were files transformed or re-signed? What written supplier rights and downstream redistribution basis support these exact wheel entries, and how does this reconcile with Qt's Windows deployment guidance?
6. Can Qt provide a package-matched corresponding-source/relinking or replacement route and tell the distributor what source/build materials and user notices apply?

### Questions for Microsoft / distributor's licensing channel

1. Which complete Microsoft Visual Studio/Visual C++ Runtime license terms apply to the distributor, edition, package channel, and each of the ten runtime copies?
2. Do the terms permit downstream redistribution of the exact Qt-signed 14.44 files, and what evidence establishes their origin and unmodified status? How do Qt's signature and any binary differences from Microsoft REDIST candidates affect the conditions?
3. What authorization covers the root 14.51 files, and does the distributor meet all eligibility, permitted-purpose, downstream-terms and notice conditions?
4. Would a centrally installed official Redistributable be an eligible and operationally acceptable alternative for this product/channel, and what servicing/update process is required?

### Questions for qualified counsel

1. Which components, files and source-level materials are covered by the grants the distributor proposes to rely on? Are there any undisclosed commercial terms or recipient/channel limits?
2. On the actual product and conveyance facts, does LGPLv3 §4 apply to any combined work? Which §4(d) route is legally available, what is the required source/application-code scope, and what user notices/texts must accompany each copy?
3. Does LGPLv3 §3 matter for header-derived PySide/application material? Does §4(c) apply to runtime copyright display? Does §4(e) trigger Installation Information under the actual product, device, transaction, signing and installation facts?
4. Do the installer, EULA, updater, code signing, anti-tamper controls or other terms effectively restrict modification or reverse engineering for debugging covered library changes?
5. What exact source/offer/relink availability period and recipient instructions are required for the selected conveyance method?
6. What separate obligations attach to the PyInstaller bootloader/loader and exception, Apache-licensed hooks, CPython/Microsoft clause, OpenSSL, translations and other embedded code?
7. What Microsoft rights chain covers each runtime file, and are the exact Qt-signed DLLs eligible for downstream distribution under the applicable terms?
8. Which distribution option (LGPL, GPL if available, commercial, product-scope change, or no conveyance) is supportable for this exact artifact and channel?

## 9. Evidence references and record hierarchy

Primary project records are listed in §2.3. Additional pinned upstream references and retrieval dates are in those source reports and `licenses/third-party/notices/MANIFEST.md`. Key source references include:

- Qt 6.12 licensing/LGPL/SBOM/third-party docs: `doc.qt.io/qt-6.12/{licensing,lgpl,sbom,licenses-used-in-qt}.html` and the Qt for Python license/build documentation.
- Qt source candidates and Qt for Python `pyside-setup` 6.12.0 source candidates recorded in `QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md` and `QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md`. Same-version source availability does not establish source-to-binary correspondence.
- GNU LGPLv3/GPLv3 full texts under `licenses/`; consult legal counsel on actual application.
- Microsoft redistribution/Visual Studio terms and versioned runtime evidence listed in `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md` and `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`.
- Component-specific upstream material and SHA-256/size records in `notices/MANIFEST.md`. Its 34 listed files have a recorded baseline; the manifest file itself has no self-hash row.

The report's factual base is the actual trimmed package plus later corrective evidence. Historical 185-file inventories and unverified vendor candidates are retained only as context and are not promoted to current-package facts.

## 10. Release recommendation

**HOLD — NOT CLEARED FOR DISTRIBUTION.** Maintain the hold until the release owner defines the actual distribution model, Qt and Microsoft rights questions are supported with artifact-specific evidence, qualified counsel reviews the applicable grants and conditions, package-matched notices/source materials and any required LGPL route are completed, and the authorized final artifact is re-inventoried and approved. This recommendation is a release-control conclusion based on missing evidence and decisions; it is not a legal finding of compliance, infringement, or breach.

## 11. Final verification record

The separate completion response records the generated report's exact size and SHA-256. Verification requirements for this task are:

- **Package identity:** 182 regular files / 80,058,228 bytes; executable SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- **Release baseline:** all six entries recorded in `C:/Users/DELL/AppData/Local/Temp/logsentinel-final-audit-release-before.txt` must retain their recorded sizes and SHA-256 values.
- **Notice materials:** all 34 rows in `licenses/third-party/notices/MANIFEST.md` must retain their recorded sizes and SHA-256 hashes. The 35th file, `MANIFEST.md`, has no self-hash baseline, so it cannot be compared to a recorded expected value.
- **Worktree:** preserve all pre-existing entries; this report should be the only new entry. No source, spec, binary, notice, prior report, or release artifact should be changed by this task.

No commit or push is made. No rebuild, download, package change, replacement test, source change, specification change, notice change, or release-artifact change is authorized by this report.