# Qt / PySide6 / Shiboken6 LGPL Gap-Closure Plan — Trimmed Windows Package

**Assessment date:** 2026-11-27  
**Artifact assessed:** `dist/gui-ondir-trim-test/LogSentinel-GUI/`  
**Disposition:** **HOLD — NOT CLEARED FOR DISTRIBUTION.**  
**Purpose:** evidence-based release planning for the named package. This document is not legal advice, a legal opinion, a compliance finding, or authorization to distribute.

## 1. Executive assessment

The trimmed package contains Qt 6.12.0 libraries, Qt plugins, PySide6 bindings, Shiboken6 components, and 99 Qt translation catalogs. It is an onedir package with separate runtime files. Its identity is **182 regular files / 80,058,228 bytes**; `LogSentinel-GUI.exe` is 2,386,859 bytes with SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`. No `.txt`, `.md`, or `.rst` notice document is in the package. Repository license texts and notices are not thereby delivered with it.

The evidence supports several important but limited conclusions:

- All 140 files in the package's `_internal/PySide6/` and `_internal/shiboken6/` trees match their same-path files in the existing installed distributions. The cached PySide6 Essentials and Shiboken6 Windows wheels have exact sizes and SHA-256 digests matching Qt's published values. **All 140 tree files, including all eight nested VC++ runtime DLLs, are present byte-for-byte in the matching wheel payloads and validate against the wheels' `RECORD` entries.** This corrects earlier case-sensitive path-comparison findings; see §3.2.
- This wheel-to-package identity does not establish the source revisions, patches, generated inputs, toolchain, build configuration, component SBOM, or license election for the Qt/PySide/Shiboken binaries. Nor does it establish a Qt license grant, a Microsoft redistribution grant for the VC++ files, or the applicable downstream rights.
- If Qt/PySide components are conveyed under LGPLv3 as a Combined Work, LGPLv3 §4 raises the notice, license-text, any applicable runtime-copyright-notice, §4(d) route, and no-effective-restrictions issues described below. Installation Information under §4(e) is conditional on the GPLv3 §6 trigger. **Whether LGPLv3 is the applicable basis for each binary and whether this package is being conveyed are not established.** These are conditional issues, not findings that an obligation has been triggered or breached.
- Neither LGPLv3 §4(d)(0) (source/relinking route) nor §4(d)(1) (suitable shared-library mechanism) is demonstrated for this exact package. The onedir layout is a useful engineering characteristic, not proof of legal sufficiency. No exact-artifact recipient-controlled replacement test or matching source/relink package exists in the evidence reviewed.

The project should not distribute this artifact until it identifies the intended distribution and applicable rights, receives qualified legal review, chooses and substantiates a route where required, prepares the matching end-user materials, and reviews the authorized final artifact. No legal clearance is claimed here.

## 2. Scope, evidence method, and status vocabulary

### 2.1 Scope

This plan consolidates these project records against the trimmed package, using each report's stated scope and limitations:

- `QT-PYSIDE-LGPL-DISTRIBUTION-ASSESSMENT.md`
- `QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md`
- `QT-PYSIDE-BINARY-PROVENANCE-REPORT.md`
- `QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md`
- `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`
- `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`
- `FINAL-LICENSING-AUDIT.md`
- `TRIMMED-PACKAGE-NOTICE-MAP.md`
- `RUNTIME-LICENSING-EVIDENCE.md`
- `RELEASE-PREPARATION-CHECKLIST.md`

Relevant local license materials reviewed include `licenses/LGPL-3.0.txt`, `licenses/GPL-3.0.txt`, the Qt 6.12 licensing/LGPL HTML, the Qt for Python commercial-use HTML, and `licenses/third-party/notices/MANIFEST.md`. The applicable legal interpretation and the complete agreements, if any, remain matters for qualified counsel and the rights holders.

The exact scope is the named 182-file artifact, not older 185-file package inventories. Qt PDF (`Qt6Pdf.dll`, `qpdf.dll`) and Mesa software rendering (`opengl32sw.dll`) are absent according to the package records; they are not included here as shipped components. Re-inventory if the artifact changes.

### 2.2 Meaning of status terms

- **Observed package fact:** directly inventoried, hashed, or otherwise recorded for this artifact.
- **Upstream statement / source candidate:** a public vendor or project statement, release, source tree, or digest. It is not automatically a binary-specific election, source-to-binary attestation, or permission.
- **Conditional issue:** potentially relevant if the applicable grant, conveyance, work relationship, or product facts trigger it; legal applicability is not decided here.
- **Open / not demonstrated:** the inspected evidence does not establish the fact or route.
- **HOLD:** release disposition remains pending. It is not a finding of infringement or noncompliance.

### 2.3 Read-only work and integrity

The package was inventoried and hashed read-only. No package file was executed, replaced, rebuilt, or modified for this plan; no archive or installer was downloaded; no existing report, source, specification, test result, or release artifact was changed. The only intended repository change is this new plan. No commit or push was made. Integrity and worktree verification after writing are recorded in §11.

## 3. Evidence summary and provenance boundaries

### 3.1 What is present

The reports identify Qt 6.12.0.0 Core, Gui, Network, Svg, and Widgets DLLs; PySide6 extension modules and `pyside6.abi3.dll`; Shiboken files; Qt plugins, including platform, image, SVG, network, style and TLS plugins; and 99 `.qm` catalogs. The installed distribution metadata identifies PySide6 and Shiboken6 as 6.12.0. The package contains Python code objects for PySide6/Shiboken support in the frozen executable as well as native extensions. The reports do not establish a binary-specific licensing election for these files.

### 3.2 Corrected wheel-content evidence — read this over superseded statements

The existing pip-cache wheel bodies were hashed and compared with Qt's published wheel digests:

| Wheel | Size | SHA-256 |
|---|---:|---|
| `pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl` | 82,153,795 bytes | `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42` |
| `shiboken6-6.12.0-cp310-abi3-win_amd64.whl` | 1,265,476 bytes | `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e` |

The cached wheel archive sizes and digests match Qt's published mirrorlist values. The payload comparison used case-insensitive Windows path matching; every one of the 140 package files under the two trees has a matching wheel entry, identical bytes, and a valid matching wheel `RECORD` hash and size. This includes five files under `PySide6/` and three under `shiboken6/` named as VC++ runtime DLLs.

This **supersedes earlier case-sensitive assertions** that the eight runtime files were absent from the wheels or lacked matching `RECORD` hashes. The correction is documented in `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`; it should be used when reconciling the older statements in `QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md`, `QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md`, and `QT-PYSIDE-BINARY-PROVENANCE-REPORT.md`. Those earlier reports have not been rewritten. The corrected evidence establishes wheel delivery of the exact bytes, **not** Microsoft source identity, Qt's supplier rights, a downstream redistribution grant, or a source/build-to-binary link.

The native Qt DLLs/plugins are Qt-signed and carry Qt 6.12.0 version resources; the PySide/Shiboken files are also in the digest-matched wheels. Signatures, PE metadata, PDB paths, local `RECORD`, and wheel archive identity have different evidentiary purposes. None alone proves exact source commits, patches, build options, license election, or the complete correspondence-source set.

### 3.3 Source and build provenance that remains open

Official Qt 6.12.0 source archives and the Qt for Python `pyside-setup` 6.12.0 source archive/tag are identified in the source register. Qt source archives' published hashes were not verified against locally acquired archives in these investigations; the archives were not downloaded. The exact Qt online-installer component archives were not compared against the packaged Qt DLL/plugin hashes. The matching PySide/Shiboken wheel hashes now establish the wheel archive contents, but not which source tree or build process produced those contents.

Not established for this artifact:

- source revisions/tree hashes and any downstream patches for each Qt library, plugin, PySide6 binding and Shiboken component;
- Qt and Qt for Python CI/build IDs, signed per-file provenance, matching SBOMs, dependency snapshots, generated sources, Qt/Python headers, Shiboken typesystem/generator inputs and commands;
- full compiler/linker/Windows SDK versions, Qt configure options, feature choices, CRT/build modes, and the precise build environment;
- all statically incorporated Qt third-party source snapshots and applicable file-level license elections/notices;
- source `.ts` mapping, contributor/license notices and `lrelease` build details for the 99 catalogs; and
- source-to-binary correspondence for the frozen Python code objects.

Same-version public source candidates are leads, not corresponding source until matched to the actual shipped builds and necessary build materials. See the source register and binary provenance report for per-file candidate mappings and their limitations.

## 4. LGPL obligations matrix — conditional analysis, not a compliance verdict

The matrix assumes **only for analysis** that (a) a relevant Qt/PySide component is actually available to this distributor under LGPLv3, (b) the relevant work is conveyed, and (c) LGPLv3 §4's Combined Work conditions apply. These premises are **not established** for every package component. The final grant and treatment of the application/bindings must be determined from actual source-file licenses, Qt's written confirmation or commercial agreements, the distribution facts, and counsel's advice. A factual package observation is not itself a finding that a legal condition has been triggered or satisfied.

| Topic | Relevant conditional issue | Evidence for this package | Status / closure evidence |
|---|---|---|---|
| Applicable license and component scope | Determine the actual license grant/election for every conveyed Qt library, plugin, PySide6/Shiboken file and associated third-party code; distinguish LGPL, GPL-only/source-file terms and commercial rights. | Qt 6.12.0 runtime, plugins and PySide/Shiboken 6.12.0 files are present; wheel digests/payloads are identified. PySide metadata lists `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; Qt for Python public language does not resolve the GPLv2 discrepancy. No package-specific election or commercial entitlement is evidenced. | **Open.** Obtain Qt's written, version/file-specific license basis and a reviewed component map; check any commercial agreement. Do not infer an election from the wheel metadata or signature. |
| LGPL §4(a): prominent use/license notice | If the combined-work route under LGPLv3 applies, provide a prominent notice with each conveyed copy that the Library is used and its use is covered by LGPL. | Package inventory finds no `.txt`, `.md` or `.rst` notice document. The application UI/runtime copyright-notice behavior was not audited to decide what §4(c) would additionally require. | **Conditional / not demonstrated.** Counsel should review a proposed prominent notice in the actual delivery and any interface presentation. A repository document is not delivery with the package. |
| LGPL §4(b): GPL and LGPL texts | Under the §4 combined-work conditions, accompany the combined work with copies of both GNU GPL and LGPL license documents. | `licenses/GPL-3.0.txt` and `licenses/LGPL-3.0.txt` exist in the repository, but neither is present in the inspected package. | **Conditional / not demonstrated in package.** Include and validate the correct copies in the authorized recipient distribution if this route applies. |
| LGPL §4(c): execution-time copyright notice | Applies to a Combined Work that displays copyright notices during execution; the Library copyright notice and a reference to the license copies must be included among them. | Runtime display behavior was not assessed for this issue. | **Conditional / open.** Inspect every relevant notice/about screen and have counsel determine applicability and wording. |
| LGPL §4(d)(0): source/relink route | Convey Minimal Corresponding Source under LGPL and Corresponding Application Code in a suitable form and on terms permitting recombination/relinking with a modified Linked Version, using GPLv3 §6's source-conveyance method. | No package-matched Minimal Corresponding Source/application-code bundle or recipient procedure has been assembled or tested. Existing application repository, specs, wheel identity and public source candidates are not by themselves such a bundle. | **Conditional / not demonstrated.** Select only after counsel's review; obtain matching library sources, patches/build materials, application code, reproducible instructions and permissive terms, then test the user workflow. |
| LGPL §4(d)(1): suitable shared-library mechanism | Use a suitable mechanism which at runtime uses a Library copy present on the user's system and works properly with an interface-compatible modified Linked Version. | The onedir package stores many Qt DLLs separately under `_internal/PySide6/` with related plugins and bindings. This is a layout observation only. | **Conditional / not demonstrated.** No exact-package recipient-controlled modified-library test exists. Establish actual load/search paths, compatibility and user control; test a coherent set where necessary. |
| Modification and reverse-engineering restrictions | Terms taken together must not effectively restrict modification of the Library portions or reverse engineering for debugging those modifications. | Final EULA, installer/update terms, signing/anti-tamper behavior and recipient restrictions are not identified in the assessment. | **Conditional / open.** Review proposed distribution terms and mechanisms against the exact route; remove/adjust conflicting restrictions only with legal/owner approval. |
| LGPL §4(e): Installation Information | Required only if GPLv3 §6 would otherwise require it, and only to the extent needed to install/execute the modified combined work. | Intended device/product, conveyance transaction, retained installation capability, signing and technical controls are unspecified. | **Conditional / unresolved trigger.** Counsel should determine if the trigger applies; do not assume either that it always applies or is categorically irrelevant. |
| LGPL §3: material from Library headers | Separate analysis may be needed if the Application object code incorporates material from Library header files beyond §3's specified categories. | The evidence reviewed does not establish the exact PySide/application header-derived material and its scope. | **Conditional / unassessed.** Ask counsel and Qt/build provenance providers to identify relevant incorporated material and any resulting notice/text conditions. |
| Corresponding-source identity and source access | Establish exact corresponding source and convey it or use a permitted source-access/offer method for the chosen route, consistent with the actual conveyance. | Matching wheel bytes are established; source-to-build linkage, build materials, source package and reviewed source-access mechanism are not. | **Conditional / not demonstrated.** Determine the legally applicable source scope/method; make it version-pinned, complete, accessible for the required period, and tied to the final binaries. |
| Translation catalogs | Determine file-specific source/license/notice treatment; ordinary `qttranslations` `.ts` classification is separate from Qt LGPL library binaries. | 99 `.qm` files present and wheel-matched. QUIP 18 identifies the usual translation `.ts` category as `LicenseRef-Qt-Commercial OR BSD-3-Clause`; `.qm` source mapping and contributor notices are not established. | **Present / unresolved.** Map each `.qm` to `.ts`, file metadata and applicable notice; do not simply classify all catalogs as LGPL libraries. |
| Embedded third-party code | Independent licenses/notices and source requirements may apply; fulfilling Qt LGPL conditions does not replace them. | Binary evidence and Qt 6.12 attributions suggest components including FreeType, HarfBuzz, libpng, PCRE2/SLJIT, codecs, C++/WinRT and zlib-compatible code; build-matched SBOM/source mappings and some elections remain open. | **Present / incomplete.** Obtain matching SBOM/build records; resolve FreeType election, codecs, zlib identity, and exact notices/patents before preparing release materials. |
| Eight nested VC++ DLLs | Separate Microsoft runtime provenance/redistribution issue; not resolved by LGPL compliance. | All eight are in the hash-matched Qt wheels, match wheel `RECORD`, report 14.44.35211.0 and carry valid Qt Company signatures. Qt's written supplier/redistribution basis, Microsoft source mapping and downstream eligibility remain unresolved. | **Present / independent open gate.** Obtain Qt's written basis and counsel's review of exact Microsoft terms/files; do not infer permission from Qt's signature or wheel inclusion. |
| Package and release disposition | Review the exact recipient artifact and actual conveyance before a release decision. | Current package has no license-text files; no complete end-user bundle or §4(d) route is demonstrated. | **HOLD.** This plan makes no conclusion that a conveyance occurred, a legal violation exists, or a legal condition is satisfied. |

## 5. DLL replacement and relinking feasibility

### 5.1 Technical starting point

The onedir layout has separately stored Qt shared libraries rather than placing the entire runtime inside a single-file executable. This is more inspectable and potentially more amenable to replacement than a monolithic embedded runtime. It does not alone show that a recipient can replace the relevant Library, that the application will load that replacement, or that the arrangement meets LGPLv3 §4(d)(1).

The runtime is not just one interchangeable DLL. The package includes Qt DLLs, PySide `.pyd` modules, `pyside6.abi3.dll`, Shiboken extensions/support DLLs, and Qt platform/image/TLS/other plugins. Their ABI, dependency versions, plugin discovery, loader search paths, and signatures/installation constraints may interact. A one-DLL substitution or a successful launch with a different package does not demonstrate that a suitable modified library set works in this artifact.

### 5.2 Exact-artifact evidence gap

No recipient-controlled, modified-library replacement test has been demonstrated against a copy of the exact 182-file package identified in this plan. The earlier replacement probe/test evidence is described in the reports as another package/test arrangement, including ambiguous or failed probes; it is not proof for this package. No source-plus-application-code relinking/recombination package or reproducible recipient process has been assembled.

### 5.3 Safe future test plan, if authorized

Do not test by modifying the preserved baseline. After a rights holder/counsel and release owner approve a test protocol:

1. Make a separately identified test copy of the exact package and record its complete file manifest, hashes, executable hash and copy provenance.
2. Identify with Qt the interface-compatible replacement build and the correct linked versions. Determine whether one library or a coherent set of libraries/plugins/bindings must change; do not substitute random or merely same-version files.
3. Record exact paths, hashes, signatures and search/load behavior before and after substitution. Use a clean recipient-like Windows account/system and capture full-path DLL loading.
4. Exercise startup, all GUI pages, representative analysis/report/export, settings, relevant Qt plugins, error/shutdown paths and any other supported workflow. Verify that the altered compatible library is actually loaded and that the application operates properly.
5. Preserve the protocol, tool/environment versions, logs, failures, hashes and test copy separately from the audit baseline. A technical pass supports feasibility only; counsel must separately decide whether the mechanism and terms satisfy §4(d)(1).

For §4(d)(0), a separate source route must identify the Linked Version and supply the required library source, modifications, build/relink scripts/materials and Corresponding Application Code in a form and under terms that permit recombination. A successful build by the project team alone does not establish that a recipient has the same materials, rights, instructions or practical capability. Counsel should review the exact source set and conveyance method.

## 6. Distribution paths for a future authorized release

None of these options is approved by this assessment. They require a component-specific license basis, review of all independent third-party and Microsoft terms, and a decision by the release owner.

| Possible path | What it would require | Important limitation |
|---|---|---|
| **LGPL-based Qt/PySide distribution** | Written confirmation of which exact components are eligible and under what LGPL terms; resolve PySide metadata/vendor-description issue; satisfy applicable notices/texts, chosen §4(d) route, no-restriction terms, any triggered §4(e) information, source/notice duties for embedded components and translations; counsel review. | Current artifact has neither package-matched notices nor a demonstrated §4(d) route. Onedir layout alone is insufficient. |
| **GPL-based distribution, if actually available for each component** | Verify the exact GPL alternative and compatibility for every library/binding/plugin; identify the combined-work/source obligations and notices for the actual license; provide required source/access and recipient rights; obtain counsel review. | PySide metadata's GPL-2.0-only alternative is not reconciled with Qt for Python's public LGPLv3/GPLv3 wording. GPL is not a shortcut around source or notice duties, and cannot be assumed to cover every component. |
| **Qt/Qt for Python commercial licensing** | Obtain and document an agreement covering the exact Qt/PySide/Shiboken versions, uses, recipients and distribution model; review sublicensing/deployment and any contractual obligations. | A Qt commercial arrangement does not automatically clear third-party code, Microsoft runtimes, CPython, OpenSSL, PyInstaller or other independent terms. No commercial entitlement is evidenced here. |
| **Change/remove Qt or change the distribution model** | Make an explicitly authorized engineering/product decision, then perform a new inventory, source/license review, compatibility and package verification. A different delivery model must still be analyzed on its own facts. | No change is made by this plan. Merely moving dependencies or relying on a system Qt install does not itself determine or eliminate applicable duties. |
| **Do not convey / keep on hold** | Do not make copies available to recipients until the rights and release gates are reviewed. Confirm no other planned conveyance route is in scope. | This is the current release disposition; it is not a permanent product decision or legal conclusion. |

## 7. Prioritized gap-closure actions and exit criteria

The ordering reflects release gating. Evidence collection must preserve the current package and records; no source or packaging change is authorized by this plan.

### P0 — Keep distribution on hold and define the facts (release owner)

- Record the intended recipient groups, territories, channel, installer/portable format, terms/EULA, update/signing/anti-tamper behavior, and whether any copies are already or will be conveyed.
- Freeze the exact candidate identity and maintain a read-only hash manifest. Do not modify, rebuild, replace DLLs, or publish this trimmed artifact as a release based on this plan.
- **Exit evidence:** signed release-owner scope statement and a precisely identified artifact/channel for legal review. Until then disposition stays HOLD.

### P1 — Obtain Qt's written component, licensing and runtime answers (vendor liaison)

Request Qt confirmation tied to the exact Essentials and Shiboken wheel hashes and the exact Qt/PySide/Shiboken component set. Ask for:

- the license basis/options applicable to the actual shipped modules, plugins, bindings, Shiboken and translations, including the PySide GPLv2 metadata discrepancy and any commercial entitlement;
- the Qt/Qt for Python binary-to-source mapping: source commits/tree hashes, downstream patches, generated sources/typesystems, relevant Qt build identity/configuration, compiler/SDK, build job IDs and package-matched SBOMs/attributions;
- component-specific copyright and notice requirements, including third-party source/versions and file-level license choices; and
- for all eight nested VC++ DLL hashes, the Microsoft payload/source file hashes, transformations/re-signing/build chain, supplier authorization and Qt's written downstream redistribution basis, reconciling Qt wheel packaging with its Windows deployment guidance.

**Exit evidence:** written, artifact-specific response and retained provenance/rights documents, or an explicit unresolved status accepted by counsel as a reason to choose another distribution path. Silence, version labels, signatures and public metadata are not substitutes.

### P1 — Qualified legal review and path decision (counsel + release owner)

Ask qualified counsel to review the actual grants/agreements and conveyance facts; Qt/PySide/Shiboken license alternatives; LGPLv3 §3, §4(a)–(e), including §4(d)(0)/(1) and §4(e)'s trigger; GPLv3 §6 where incorporated by the chosen route; end-user restrictions; and the separate Microsoft runtime terms. Ask counsel to decide which route is legally available and what source, texts, notices and evidence are required. Do not ask this engineering plan to decide legal applicability.

**Exit evidence:** documented counsel advice/decision tied to the identified artifact, channel and user terms, plus a recorded distribution-path choice. If any required entitlement cannot be established, remain on hold or have the owner authorize another product path.

### P2 — Establish source-to-binary traceability and corresponding-source scope (Qt/PySide build liaison + engineering)

- Use the exact wheel hashes and package hashes as starting identifiers, not the 6.12.0 version alone.
- Obtain matching source commits, modifications, generated files, build configuration, dependencies, SBOM and build attestations from Qt. Match Qt module/plugin binaries, PySide/Shiboken extensions/support code, embedded Python package code and relevant third-party components.
- Preserve the distinction between the Qt/PySide wheel payload match and the separate source/build relationship. Do not claim a public same-version archive is corresponding source until matched.
- Create a per-file release traceability matrix: package path/hash → wheel entry/archive digest → source path/revision → patches/generated inputs → build job/configuration/dependencies → license and notice source.

**Exit evidence:** per-file records for all in-scope Qt/PySide/Shiboken files, explicit unresolved rows where vendor evidence is unavailable, and counsel's confirmation of source scope/method for the selected licensing path.

### P2 — Decide and validate one §4(d) route if LGPL §4 applies (engineering + counsel)

- For **§4(d)(1)**, design a recipient-controlled replacement test on a separate copy of this exact artifact; confirm compatible linked versions, actual loader behavior, plugin/binding interactions, access to replace, and no effective technical/legal restrictions. Retain reproducible logs and hashes.
- For **§4(d)(0)**, assemble the matching Minimal Corresponding Source and Corresponding Application Code, required configuration/scripts, appropriate terms and clear recipient recombination/relink instructions. Test the supplied process from a clean environment. Determine with counsel whether Installation Information is triggered and, if so, prepare what is necessary.

**Exit evidence:** counsel-reviewed route selection plus the complete, artifact-matched test record or source/relink bundle and recipient instructions. One route's technical success does not prove the legal conditions by itself.

### P3 — Map translations and independent third-party material (engineering + Qt)

- Match all 99 `.qm` files to `.ts` sources and identify each catalog's copyright, contributor and applicable license/notice metadata; record `lrelease` version/options where available. Keep translation treatment separate from the Qt LGPL library rows.
- Match Qt's linked components and plugins to the Windows wheel/build SBOM and resolve FreeType license election, HarfBuzz/PCRE2/SLJIT mapping, libjpeg-turbo interfaces, libtiff/libwebp sources/notices/patent material, C++/WinRT and zlib-compatible code.
- Resolve Shiboken-specific copied/adapted source notices and licenses. Preserve uncertain implementations/elections as open rather than selecting candidates by guess.

**Exit evidence:** version/file-matched component and translation map with correct source notices and unresolved items escalated to counsel. Do not copy the entire evidence-notices folder into a release: it contains alternatives, candidates and removed-component materials.

### P3 — Close VC++ runtime entitlement and servicing separately (vendor liaison + counsel + release owner)

- Use the eight exact package hashes and verified wheel-entry facts from `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`. Ask Qt to identify the Microsoft source payload and rights chain. Obtain the actual applicable Microsoft terms and have counsel assess the exact files, modifications/signatures and distribution model.
- Decide whether an application-local or centrally installed runtime is the authorized and operationally supported route. Include a named servicing/update owner. Any runtime substitution/removal requires separate explicit authorization, a fresh package identity and load/compatibility regression tests; do not infer a file is unnecessary from one process snapshot.

**Exit evidence:** written source/rights analysis for each retained file or an approved alternative deployment decision with documented licensing, loader and servicing evidence.

### P4 — Prepare reviewed recipient materials, then validate the authorized candidate (release engineering + counsel)

- Prepare a version-pinned user notice/license bundle for the selected path, including applicable prominent Qt-use notice, GPL/LGPL copies if required, runtime copyright/reference if triggered, third-party and translation attributions, and the exact source/relink/access instructions. Review any Qt/third-party supplied notices against actual binaries.
- Review installer/EULA/update/signing restrictions for recipient rights and any §4(e) issue. Keep internal audit records distinct from end-user notices.
- Only after explicit authorization, place approved materials into the authorized release layout, inventory and hash the final package, compare it with the reviewed source and notice manifest, run GUI and compatibility tests on supported Windows targets, and re-open legal review if any file/channel/terms changed.

**Exit evidence:** legal/release owner approval for the exact final hashed artifact and channel; completed package verification and test record. No such approval is established by this plan.

## 8. Missing evidence register

The following evidence remains absent or unverified in the cited material:

1. Qt's written license-election/rights confirmation for exact Qt 6.12.0, PySide6 6.12.0 and Shiboken6 6.12.0 binaries, and resolution of the PySide GPLv2 metadata discrepancy.
2. A matching Qt/Qt for Python SBOM and authenticated source/build attestations tying the exact wheel/package hashes to source commits, patches, generated inputs, build configuration, toolchain and third-party dependencies.
3. A per-file translation `.qm` → `.ts` source/license/copyright map and generation record.
4. Complete source/notice/election evidence for Qt-linked third-party code; unresolved alternatives must not be represented as chosen.
5. A selected and counsel-reviewed §4(d) route; exact-package recipient replacement testing or a corresponding-source/application-code relink package and tested instructions.
6. Final EULA, installer, update/signing/anti-tamper and recipient-control facts for assessing effective restrictions and possible Installation Information.
7. A package-delivered user notice and accompanying license texts; runtime copyright notice behavior has not been assessed for §4(c).
8. Qt's written sourcing and Microsoft redistribution basis for the eight Qt-signed VC++ runtime DLL hashes, Microsoft source-file mapping, the distributor's applicable terms/eligibility analysis, and a servicing decision.
9. Qualified counsel's review and documented disposition for the actual final distribution model.

A known missing document in the current package is not, by itself, a conclusion about the legality of an unmade or differently structured conveyance. Conversely, repository-held evidence is not evidence that recipients receive it.

## 9. Questions for qualified counsel and Qt

### Counsel

- Which precise files and source-level components in this artifact are governed by the grant the distributor proposes to rely on? What evidence establishes that grant, and how should conflicts between PySide wheel metadata and Qt for Python public descriptions be resolved?
- On the actual facts, is the distributed application a Combined Work for LGPLv3 §4, and does §3's incorporated header-material rule require separate treatment? Which recipients, channels, markets, and user terms affect the analysis?
- If §4 applies, which §4(d) route is available and what is the required scope and form of source/application-code delivery? Does the actual relative-path onedir mechanism satisfy §4(d)(1) when a recipient replaces the relevant library set? What tests and records are probative but not determinative?
- What notices/texts and runtime copyright notice are required for this actual package? Does the proposed installer/EULA, updater, code-signing policy or other protection effectively restrict Library modification or reverse engineering to debug those modifications?
- Does §4(e) apply based on the product, conveyance transaction, user's ability to install modified code, and any retained signing/installation control? If it applies, what exact Installation Information is necessary?
- Which exact Qt/PySide/Shiboken, translation, embedded third-party and Microsoft runtime terms apply independently, and what source/notice/patent materials must accompany distribution?
- Do Microsoft's applicable Visual Studio/VC++ terms authorize the exact Qt-signed runtime files and the proposed downstream distribution? What does the unmodified-file condition mean for these exact bytes and signing history?
- Which GPL alternative, if any, is actually available and compatible for every component, and what additional obligations would it impose on the combined distribution?

### Qt / Qt for Python

- Which license alternatives/election apply to each exact package component and wheel hash, including the PySide GPLv2 metadata discrepancy and Shiboken's scope?
- What exact source commits, modifications, generated inputs, toolchain/configuration, Windows build IDs and SBOM correspond to the wheel contents? Which third-party materials and source notices are included in each binary/plugin?
- Which `.ts` sources, per-file notices and `lrelease` inputs correspond to the 99 `.qm` files?
- What Microsoft source payload and transformations/signing process produced the eight runtime DLLs? What written Microsoft authorization/right permits Qt and downstream distributors to ship these exact hashes, and how is that reconciled with Qt's Windows deployment guidance?

## 10. Official references and retrieval dates

Dates below are those recorded in the existing evidence reports or this local read-only review. A public source or licensing page supports the proposition that the source says what it says; it does not establish the package's source, election, permission or compliance. References are preserved here to aid follow-up; re-check current versions and terms during legal review.

| Reference | Relevance | Retrieval/view date recorded |
|---|---|---|
| GNU LGPL v3, <https://www.gnu.org/licenses/lgpl-3.0.html>; local full text `licenses/LGPL-3.0.txt` | §§3–4, particularly combined-work notices, texts, alternatives in §4(d), and conditional §4(e). | Local text reviewed 2026-11-27; upstream URL cited by the 2026-11-09 assessment. |
| GNU GPL v3, <https://www.gnu.org/licenses/gpl-3.0.html>; local full text `licenses/GPL-3.0.txt` | GPLv3 §6 source conveyance and §4(d)(0) cross-reference; §4(e) trigger. | Local text reviewed 2026-11-27; upstream URL cited by the 2026-11-09 assessment. |
| Qt 6.12 licensing, <https://doc.qt.io/qt-6.12/licensing.html>; LGPL, <https://doc.qt.io/qt-6.12/lgpl.html>; third-party code, <https://doc.qt.io/qt-6.12/licenses-used-in-qt.html>; SBOM, <https://doc.qt.io/qt-6.12/sbom.html> | Public license choices, LGPL text/vendor statement, independent third-party code and SBOM availability. | Cited/retrieved in licensing/source evidence 2026-11-09 and 2026-11-26; local HTML reviewed 2026-11-27. |
| Qt for Python commercial use, <https://doc.qt.io/qtforpython-6/commercial/index.html>; LGPL overview, <https://doc.qt.io/qtforpython-6/overviews/qtdoc-lgpl.html>; third-party licenses, <https://doc.qt.io/qtforpython-6/licenses.html> | Public Qt for Python licensing description, commercial path and copied/third-party material. | Cited/retrieved in reports 2026-11-09 / 2026-11-26; local commercial page reviewed 2026-11-27. |
| PySide6 6.12.0 project metadata, <https://pypi.org/project/PySide6/6.12.0/>; official Essentials/Shiboken wheel mirrorlists listed in `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md` | Public metadata and archive digest values compared with existing cached wheel bodies. | Wheel digest comparison and official index evidence recorded 2026-11-26. |
| QUIP 18, <https://contribute.qt-project.org/quips/18/>; Qt localization, <https://doc.qt.io/qt-6.12/localization.html> | Qt source-file license classifications, including usual translation source files, and translation context. | Cited/retrieved in licensing assessment 2026-11-09. |
| Qt 6.12 source archive/tag indexes and Qt for Python `pyside-setup` 6.12.0 source archive/tag, links in `QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md` and `QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md` | Versioned source candidates and published source-archive digest claims; archives were not locally acquired/matched in these reviews. | Queried 2026-11-09 and 2026-11-26 as recorded in the source reports. |
| Qt LGPL obligations guidance, <https://www.qt.io/development/open-source-lgpl-obligations> | Vendor's general LGPL guidance, not a replacement for license text or legal advice. | Cited in `QT-PYSIDE-LGPL-DISTRIBUTION-ASSESSMENT.md`, 2026-11-09. |
| Microsoft redistribution and deployment references listed in `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md` and `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md` | Runtime deployment guidance, redistribution conditions and applicable Visual Studio/runtime terms. | Public documentation consulted 2026-11-26 as recorded in the VC runtime reports; exact applicable EULA remains to be obtained/reviewed. |
| Project evidence reports listed in §2.1, and `notices/MANIFEST.md` | Package facts, provenance limits, notices, corrections and missing evidence. | Local files reviewed 2026-11-27; dates internal to each source report are retained in their headers. |

## 11. Verification, change control, and disposition

Verification after creating this plan found:

- **Plan:** byte size and SHA-256 are reported in the task completion response; they are intentionally not embedded in this file's own contents.
- **Trimmed package:** 182 regular files; 80,058,228 bytes; executable 2,386,859 bytes; executable SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- **Eight nested VC++ DLLs:** every SHA-256 remains equal to the hash recorded in `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`.
- **Release baseline:** all six artifacts in `C:/Users/DELL/AppData/Local/Temp/logsentinel-final-audit-release-before.txt` retain the recorded sizes and SHA-256 hashes.
- **Worktree:** the target did not exist before this task. The pre-existing status entries were captured before writing; this plan is the only intended new repository file. Existing specification changes, untracked licensing/release/test-result artifacts and release files were preserved.
- No download, extraction, rebuild, package edit, source/spec edit, commit or push was performed.

**Disposition remains HOLD — NOT CLEARED FOR DISTRIBUTION.** This plan records actions and evidence gaps, not legal conclusions. Reassess against the exact authorized final artifact, source/notice set, user terms and distribution channel; any artifact change requires new package identity verification and the appropriate legal review.
