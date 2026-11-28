# Qt / PySide6 Phase 1 Release-Route Decision

**Scope:** existing trimmed Windows onedir GUI candidate, `dist/gui-ondir-trim-test/LogSentinel-GUI/`
**Decision:** **HOLD — NOT CLEARED FOR DISTRIBUTION**
**Purpose:** engineering route recommendation and evidence request. This is not legal advice, a compliance opinion, or distribution authorization.

## Executive decision

The most practical *candidate* route, if qualified counsel confirms LGPLv3 applies and Qt confirms the relevant license grants, is **LGPLv3 §4(d)(0): provide the exact corresponding source/build materials and Corresponding Application Code with clear relinking/recombination instructions**, rather than relying on the current onedir layout as §4(d)(1) replaceability. Prefer source materials supplied alongside the authorized binary package; use a written-offer mechanism only if counsel confirms the exact conveyance method is one permitted by LGPLv3 §4(d)(0)'s GPLv3 §6 cross-reference and the offer meets its requirements.

That route is **not currently implementable for this exact candidate** from the repository alone: matching wheel bytes are established, but exact source-to-build correspondence, vendor patches, generated inputs, build configuration and the package-scoped source map are not. Versioned upstream source archives are public candidates, not proof of correspondence. The 6.12.0 Qt for Python release announcement specifically says its SBOM documents were not yet ready. Request the missing records from Qt before treating the source route as available. If Qt cannot substantiate source correspondence and license scope, remain on hold; obtain an applicable Qt commercial agreement or authorize a product/package change (potentially CLI-only) and re-audit. Neither alternative automatically clears the other bundled components or Microsoft runtime.

## 1. Verified position for the candidate

### Artifact and versions

| Scope | Evidence-supported position |
|---|---|
| Candidate identity | 182 files / 80,058,228 bytes. Root executable 2,386,859 bytes; SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`. Package tree was re-inventoried read-only for this task. |
| Qt shared libraries | Five Qt 6.12.0.0 AMD64 DLLs: Core, Gui, Network, Svg and Widgets. |
| Qt plugins | 20 Qt 6.12.0.0 AMD64 plugins: `qtuiotouchplugin`; `qsvgicon`; image formats `qgif`, `qicns`, `qico`, `qjpeg`, `qsvg`, `qtga`, `qtiff`, `qwbmp`, `qwebp`; `qnetworklistmanager`; platforms `qdirect2d`, `qminimal`, `qoffscreen`, `qwindows`; `qmodernwindowsstyle`; TLS backends `qcertonlybackend`, `qopensslbackend`, `qschannelbackend`. |
| PySide6 | Distribution metadata identifies PySide6 6.12.0; `QtCore.pyd`, `QtGui.pyd`, `QtNetwork.pyd`, `QtSvg.pyd`, `QtWidgets.pyd`, and `pyside6.abi3.dll` are included. Their version is metadata-based, not a PE version resource. |
| Shiboken6 | Distribution metadata identifies Shiboken6 6.12.0; `Shiboken.pyd` and `shiboken6.abi3.dll` are included. |
| Translations | 99 `.qm` catalogs are present. Their source-catalog, contributor and per-file license mapping is unresolved and must be treated separately from Qt library licensing. |
| Exclusions | `Qt6Pdf.dll`, `qpdf.dll` and `opengl32sw.dll` are absent from this trimmed candidate. Do not count Qt PDF/PDFium or Mesa/LLVM as shipped on this evidence. |

### Delivery identity is not source provenance

The cached PySide6 Essentials 6.12.0 Windows AMD64 wheel body has SHA-256 `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42`; the Shiboken6 wheel body has SHA-256 `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e`. These match Qt-published wheel digests. All 140 files in the package's `PySide6/` and `shiboken6/` trees match their entries in those wheels and their `RECORD` hashes, including the eight nested VC++ DLLs. This is strong archive/payload identity evidence. It does **not** show which source commits, patches, generated code, dependency snapshots, build options, CI job, or license election generated those files.

Qt DLL version resources, Qt Authenticode signatures, PDB path strings, local distribution metadata and wheel hashes corroborate identity/origin in different ways; none is a source-to-binary attestation. The corresponding-source register and source/build report explicitly leave that link open. The older source/build report also contains a case-sensitive comparison that treated eight nested VC++ DLLs as absent from the wheels; the later `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md` corrected this by case-insensitive path matching and confirmed all eight wheel entries and `RECORD` hashes. The correction changes wheel-delivery identity only, not source provenance or redistribution rights; the older report was not modified.

### Licensing position

- Public Qt materials describe license choices for eligible components, not the binary-specific license election for this package. PySide/Shiboken metadata contains `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; Qt for Python public language describes Community Edition as LGPLv3/GPLv3. The GPLv2 discrepancy is unresolved.
- The package has no `.txt`, `.md` or `.rst` notice/license documents. Repository copies of LGPL/GPL texts are not delivered with the candidate.
- Neither LGPLv3 §4(d)(0) nor §4(d)(1) is demonstrated for this exact candidate. Whether the relevant license and conveyance facts trigger LGPLv3 §4 is a legal question, not presumed here.
- The 20 plugins, 99 translation catalogs and third-party code linked into Qt/PySide require file/component-level scope and notice review. Qt's LGPL terms would not replace independent third-party conditions.
- The eight nested Qt-signed VC++ runtime DLLs match Qt wheel payloads, but their Microsoft-source lineage and redistribution basis remain unresolved. Two additional root VC++ files have separate open questions.

## 2. Source and build materials: availability assessment

### Public source candidates exist

The existing reports identify official versioned source candidates for the relevant Qt modules and Qt for Python:

- Qt 6.12.0 `qtbase` (Core, Gui, Network, Widgets), `qtsvg`, `qtimageformats`, `qttranslations` and `qttools` archives/tags.
- Qt for Python `pyside-setup` 6.12.0 archive/tag, containing PySide6 and Shiboken source/build code.
- Qt's versioned Windows build instructions and Qt SBOM documentation.

Qt's official indexes publish digests for these archives. Prior reports transcribed those digests but did not acquire the archives or compare source files/build records with this package. The archive can be obtained from an authoritative source in a separately authorized step; that would establish archive integrity against its published digest, **not** that the exact signed wheel binaries were built from it.

### Exact corresponding source and build recipe are not established as publicly available

The reviewed reports do not contain or establish:

- source commit/tree identifiers and complete patch sets for the packaged Qt DLLs/plugins and PySide6/Shiboken binaries;
- generated source, bindings/typesystem inputs, generator/tool versions, or copied/adapted Shiboken source mapping;
- exact Qt SDK/component archives used for the wheel build, dependency/source snapshots, feature choices or a wheel-scoped SBOM;
- build job IDs, signed per-file attestations, complete CMake/configure cache or commands, compiler/linker servicing builds, Windows SDK, CRT and link options;
- exact PDBs mapped by GUID/age to the packaged Qt DLLs and then to source/build jobs;
- the 99 `.qm` to `.ts` mapping, catalog-level notices, and exact `lrelease` version/options; or
- source-to-binary reproducibility or other artifact-specific evidence tying an authoritative source tree to these binaries.

Qt 6.12 documentation says Qt builds can generate configuration-specific SBOMs, including via `-sbom`, and installed Qt SBOMs may be in the installation's `sbom` directory. This describes a capability and location, not evidence that a matching SBOM exists for the Qt binaries inside these wheels. Qt for Python's 6.12 release announcement says SBOM documents were not ready and would be added in future releases. Therefore a matching Qt for Python 6.12.0 SBOM cannot be assumed obtainable from the public documentation reviewed; request it, and ask Qt to state explicitly if it does not exist.

### Practical outcome

- **Can obtain:** public, versioned source archive candidates and their published archive digests; Qt's general build documentation and license texts.
- **Not established as publicly obtainable:** exact wheel-to-source/patch/build mapping and corresponding build materials for the signed Qt/PySide/Shiboken binaries. These must be requested from Qt/the Qt for Python release maintainers or generated by a future controlled source build.
- **Cannot substitute:** local wheel `RECORD`, binary version, signature, a same-version tag/archive, or a new independently built binary for proof of what produced this candidate.

## 3. Route comparison

| Route | Practical fit for Phase 1 | Evidence/prerequisites | Main risk/impact |
|---|---|---|---|
| **Provide corresponding source and notices (preferred conditional path)** | Best fit if Qt provides the missing source/build records and counsel confirms §4(d)(0) applies. Can preserve an onedir binary delivery while making matching source materials available alongside it. | Exact Qt/PySide/Shiboken source and modifications; generated inputs and scripts/materials within required source scope; Qt/third-party component and translation mapping; Corresponding Application Code and data/tools needed to reproduce/relink; required notices/texts; source-to-final-binary manifest; counsel-reviewed terms and recipient instructions. | High evidence/vendor dependency now; medium-to-high release-engineering effort to curate, version, host and maintain source. A same-version source archive alone is insufficient. Must avoid implying that furnishing source automatically satisfies every LGPL condition. |
| **Written offer instead of immediate source delivery** | Potential distribution mechanism, not a separate way to avoid source work. Could be practical where counsel confirms the actual conveyance facts and GPLv3 §6 permits that method. | Same exact corresponding source must exist, be complete and retrievable. Offer wording, recipients, term/duration, cost/access method and fulfillment process must be reviewed against the precise LGPL/GPL text and channel. | High legal and operational risk if a generic web link or offer is used without confirming eligibility and duration. It does not cure missing source, provenance, notices or rights. No offer should be drafted as operative until counsel reviews it. |
| **LGPL §4(d)(1) shared-library replacement** | Technically attractive because Qt DLLs are separate in onedir; currently less practical than §4(d)(0). | Need recipient-controlled test on a separate copy proving a compatible modified Qt library/set is actually loaded and works with PySide `.pyd` modules, Shiboken, plugins and supported workflows; verify paths/permissions and absence of effective restrictions. Counsel decides legal sufficiency. | No exact-candidate test. A single-DLL swap is not enough; the linked set and Python extension ABI/plugin behavior matter. May require loader/package changes and compatibility work (not authorized now). Onedir layout alone is not sufficient. |
| **Rebuild Qt/PySide from source and adopt a documented §4(d)(0) route** | Viable fallback if Qt cannot supply adequate provenance for the current binaries but the public source and build inputs permit a controlled build. Best foundation for future releases, not a fix to the existing candidate. | Authorized source/build work; all Qt/PySide/third-party inputs and licenses; compatible Windows toolchain/SDK, Qt and Python headers, libclang/typesystems, generated files, configuration, patches and reproducible build records; new package audit and tests. | High effort and schedule risk. New binaries mean a new package identity, functional/compatibility testing, licensing and notice review. Does not resolve Microsoft runtime rights, CPython terms, PyInstaller or independent third-party terms by itself. |
| **Qt commercial licensing** | Potentially lowest implementation impact if Qt offers terms covering these exact modules, PySide/Shiboken, use and distribution channel. | Written executed agreement or vendor-confirmed license scope, sublicensing/distribution rights, versions, recipients, updates and support. Still need third-party, translation, runtime, CPython and PyInstaller review. | Cost/contract terms unknown. No commercial entitlement is evidenced. Does not automatically clear bundled third-party components or Microsoft runtime copies. |
| **Remove/reduce Qt components or discontinue GUI** | Removing unused plugins/catalogs may reduce notice/source scope after product testing, but it does not clear core Qt/PySide. Switching GUI technology or shipping only the CLI is a viable product alternative if Qt rights/source cannot be closed. | Release-owner decision; authorized future source/spec/package changes; new dependency/licensing audit; complete functional and Windows compatibility tests. | Plugin/catalog pruning has modest-to-medium impact but does not solve core LGPL/source obligations. Replacing the GUI framework is high development/test impact. CLI-only is the lowest Qt exposure but changes the Phase 1 product scope and leaves other packaged/runtime questions if the old GUI package is still conveyed. No change is made here. |

## 4. Recommendation and estimated implementation impact

### Recommended route

**Keep HOLD. In parallel, request a Qt-supported source/provenance and license package for the exact wheel hashes, and prepare for a future §4(d)(0) source/relink distribution with complete source delivered alongside an authorized build. Do not rely on §4(d)(1) or a written offer as the primary plan at this time.**

Why:

1. It has a concrete technical and evidentiary finish line: a file-to-source/build/notice map and a source package matched to the exact linked versions.
2. It does not depend on proving that every nested DLL, binding, plugin and Qt loader path accepts a coordinated replacement set at runtime. That route remains technically untested.
3. Directly furnishing source materials alongside the package is operationally easier to evidence than maintaining an offer/fulfillment obligation, subject to counsel's review and the applicable license terms.
4. The official source archives provide a starting point, but Qt must resolve the exact binary/source link and supply or identify non-public build inputs. If it cannot, a controlled source rebuild is the practical technical fallback, but it creates a new candidate and substantial work.

### Impact estimate (planning only)

- **Vendor request and license-scope response:** low engineering effort; schedule depends on Qt response and may be indeterminate. No provider contact is made by this task.
- **Source/SBOM/notice reconciliation once records arrive:** medium-to-high effort because 25 Qt DLLs/plugins, PySide/Shiboken bindings, copied code, 99 catalogs and third-party components need mapping and review.
- **Prepare and verify the §4(d)(0) materials/instructions:** medium-to-high effort, plus qualified legal review. The actual scope and instructions depend on counsel's decision and Qt's source/build records.
- **Rebuild all Qt/PySide from source if vendor records are unavailable:** high engineering/build effort and likely a materially different candidate. Preserve build scripts/toolchain/dependencies, validate a Qt/PySide-compatible Windows build, re-run full GUI and compatibility tests, and repeat the artifact-wide licensing review.
- **Implement/test §4(d)(1) as an alternative:** medium-to-high and uncertain; could require packaging/loader changes, which would need separate authorization and rebuild. This investigation did not run replacement tests.
- **Replace GUI framework or revert to CLI-only:** high product/UX impact if replacing; comparatively low Qt-specific legal exposure only if Qt is actually removed from the conveyed artifact. All remaining bundled components still need review.

These are qualitative estimates, not commitments or license conclusions.

## 5. Exact requirements still outstanding

### Obtain from The Qt Company / Qt for Python maintainers

For the Essentials wheel SHA-256 `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42`, Shiboken wheel SHA-256 `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e`, and attached package-file hash manifest, request:

1. **License basis:** written per-distribution/component confirmation of available license options and conditions for the exact Qt 6.12.0 libraries/plugins, PySide6 Essentials and Shiboken6 wheel contents; resolve the GPL-2.0-only metadata vs public LGPLv3/GPLv3 wording; identify Shiboken-specific terms, third-party code and any commercial option. Clarify that this is license-scope information, not a claim that Qt can give legal advice for the distributor.
2. **Source-to-binary map:** for each Qt DLL/plugin and each PySide/Shiboken native and frozen helper module, identify upstream repository/path, immutable commit/tree hash, exact release branch, generated inputs and all downstream patches/cherry-picks; map each binary hash (or wheel path/hash) to the build output/job.
3. **Build records:** build/CI IDs and attestations; Qt installer/component archive identities used by the wheel builder; compiler/linker servicing versions, Windows SDK, CRT, Qt configure/CMake options, Python headers/ABI, Qt headers/libs, Shiboken generator/typesystem, libclang, build scripts and relevant environment/dependency manifests. Include source-generation and packaging/post-processing steps and signing relationship.
4. **SBOM and third-party notices:** wheel-scoped Qt and Qt for Python SBOMs (CycloneDX/SPDX or native format), exact dependency/source versions, file-level copyrights/licenses, linked/static components and applicable notices. If no 6.12.0 wheel-scoped SBOM exists, say so and provide an equivalent authenticated component/notice manifest or explain what is unavailable.
5. **Translations:** map all 99 `.qm` hashes to exact `.ts` source paths/commits and file-level contributor/license notices; identify Qt Linguist `lrelease` version, options and transformations.
6. **Corresponding source:** confirm which official archives are the actual source for these binaries; provide or identify all source modifications, build scripts/configuration and additional materials needed to rebuild/modify/relink the exact linked versions. State any unavailable proprietary/generated inputs and whether the published archives alone are insufficient.
7. **VC++ copies:** for each of the eight nested DLL hashes, identify Microsoft source payload/file hash, any modifications/re-signing, Qt's supplier rights and written basis for downstream redistribution; distinguish these from LGPL source duties.
8. **Replacement guidance:** identify the coherent interface-compatible Qt/PySide library set and supported replacement procedure for the exact distribution, if Qt has tested one. Vendor guidance is evidence for engineering, not counsel's final §4(d)(1) determination.

### Qualified legal review (not decided by engineering or Qt response)

Counsel must review the actual distribution model/recipients/territories/terms; identify which files and grants apply; determine if the Combined Work and LGPLv3 §4 route is triggered; determine §3 header-material issues and conditional §4(c)/(e); select and approve §4(d)(0) or §4(d)(1); define required notices and accompanying texts; decide if a written-offer method is valid for the actual conveyance and specify its exact terms, source access, duration and fulfillment; review GPL alternatives and the metadata discrepancy; assess user restrictions, signing, installer/updater/anti-tamper behavior and replacement/reverse-engineering rights; and review third-party and Microsoft runtime terms. Counsel must also determine whether direct source delivery meets the chosen route's scope and method for this specific distribution.

### Release owner / engineering

Before any release route is implemented: define channel, recipients and territories; decide installer/portable layout and user terms; identify update/support/signing policy and supported Windows versions; preserve the exact candidate; maintain a file-level source/license/notice manifest; prepare and test source/relink instructions or a recipient replacement process only on a separately authorized copy; curate recipient materials; verify final hashes; and obtain written release-owner approval tied to those hashes.

## 6. Draft upstream inquiry — NOT SENT

**To:** The Qt Company, Qt for Python release/build and open-source licensing contacts
**Subject:** Request for Qt/PySide6 6.12.0 Windows wheel source/build records and license scope — LogSentinel Phase 1 candidate
**Status:** Draft for internal review only. Do not send without authorization.

> We are conducting an internal release-readiness review of a Windows AMD64 onedir candidate containing Qt 6.12.0.0 Core, Gui, Network, Svg and Widgets DLLs; 20 Qt 6.12.0.0 plugins; PySide6 6.12.0 bindings; Shiboken6 6.12.0; and 99 Qt `.qm` catalogs. The candidate's Qt/PySide/Shiboken files match entries in the following wheel archives, whose local archive hashes match Qt's published wheel digests:
>
> - `pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl` — SHA-256 `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42`.
> - `shiboken6-6.12.0-cp310-abi3-win_amd64.whl` — SHA-256 `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e`.
>
> These facts establish wheel-content identity only; we are not asserting that the public 6.12.0 source tags or archives produced the binaries. If this draft is later approved for sending, we would include a package path/hash manifest. Could you provide, or identify an authoritative source for, the following materials tied to these exact wheel digests and that manifest?
>
> 1. A per-component/file license-scope statement for the Qt modules/plugins, PySide6 and Shiboken6 in these wheels, including the available grant alternatives, applicable Shiboken terms, third-party source/notice scope, and clarification of the `GPL-2.0-only` wheel metadata expression versus the Qt for Python public description of Community Edition as LGPLv3/GPLv3.
> 2. The exact upstream repositories, commits/tree hashes, source paths, patches/cherry-picks, generated source and build inputs used for each Qt DLL/plugin and PySide/Shiboken binary; corresponding build/CI IDs and any signed build attestations or binary-to-build manifest.
> 3. The Windows build configuration: Qt installer/component archive identities; Qt configure/CMake options; compiler/linker and Windows SDK/CRT versions; Python ABI/headers; Qt headers/libraries; Shiboken generator/typesystems; libclang; build scripts; dependency/source snapshots; and packaging, post-processing and signing steps.
> 4. Wheel-scoped SBOMs and file-level third-party copyright/license/notice data, including statically linked components. If no 6.12.0 Windows-wheel SBOM exists, please confirm that and identify an equivalent component manifest or records that are available.
> 5. A mapping for each of the 99 packaged `.qm` catalogs to its `.ts` source, revision, contributor/copyright/license metadata, and the `lrelease` version/options used to generate it.
> 6. Confirmation of which source archives and modifications constitute the corresponding source for these particular wheel binaries, and the source/build materials and user-facing information Qt identifies for a downstream distributor evaluating an LGPL source/relink or compatible-library-replacement route. Please identify any source or build inputs that cannot be supplied.
> 7. For the eight Qt-signed VC++ runtime DLLs located under the PySide6/Shiboken6 wheel trees, the Microsoft source payload/file hashes, any transformations or re-signing, and Qt's written basis for including and permitting downstream redistribution of those exact bytes. We understand this is a separate Microsoft-rights question and are not treating wheel inclusion or signature as redistribution authorization.
>
> We are requesting technical provenance and published license-scope information for an internal review, not asking Qt to provide legal advice. Please distinguish records that are exact to these wheel hashes from general 6.12.0 documentation, and state explicitly where records do not exist. This inquiry is a draft only and has not been sent.

## 7. Authoritative references and evidence reviewed

### Existing project evidence (read before this decision)

- `QT-PYSIDE-LGPL-DISTRIBUTION-ASSESSMENT.md`
- `QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md`
- `QT-PYSIDE-BINARY-PROVENANCE-REPORT.md`
- `QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md`
- `QT-PYSIDE-LGPL-GAP-CLOSURE-PLAN.md`
- `CONSOLIDATED-RELEASE-BLOCKER-CLOSURE-REPORT.md`
- `FINAL-RELEASE-READINESS-REPORT.md`
- Supporting correction: `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md` (for the eight nested DLLs' wheel match).

### Upstream references

These are source/license/build references, not proof that the exact binaries were built from them:

- Qt 6.12 LGPL text and guidance: <https://doc.qt.io/qt-6.12/lgpl.html>; Qt licensing: <https://doc.qt.io/qt-6.12/licensing.html>; Qt third-party code: <https://doc.qt.io/qt-6.12/licenses-used-in-qt.html>.
- Qt SBOM behavior and `-sbom` build option: <https://doc.qt.io/qt-6.12/sbom.html>.
- Qt 6.12 Windows source-building instructions: <https://doc.qt.io/qt-6.12/windows-building.html>; Qt configure options: <https://doc.qt.io/qt-6.12/configure-options.html>.
- Qt 6.12.0 source archive index: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/>; `qtbase` digest record: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtbase-everywhere-src-6.12.0.tar.xz.mirrorlist>; `qtsvg`: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtsvg-everywhere-src-6.12.0.tar.xz.mirrorlist>; `qtimageformats`: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtimageformats-everywhere-src-6.12.0.tar.xz.mirrorlist>; Qt translations and tools are listed in the same versioned index.
- Qt for Python 6.12.0 source archive and published digest: <https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/pyside-setup-everywhere-src-6.12.0.tar.xz.mirrorlist>; source/build instructions: <https://doc.qt.io/qtforpython-6/building_from_source/index.html> and <https://doc.qt.io/qtforpython-6/building_from_source/windows.html>.
- Qt for Python 6.12 release announcement, including statement that SBOM documents were not yet ready: <https://www.qt.io/blog/qt-for-python-release-6.12-is-here>.
- Qt's general LGPL obligations guidance: <https://www.qt.io/development/open-source-lgpl-obligations>.
- QUIP 18 source-file licensing/translation distinctions: <https://contribute.qt-project.org/quips/18/>.
- The repository's LGPLv3 and GPLv3 texts: `licenses/LGPL-3.0.txt` and `licenses/GPL-3.0.txt`. Their exact application and conveyance route require counsel.

## 8. Hold criteria and change control

The candidate remains **HOLD — NOT CLEARED FOR DISTRIBUTION** until: (1) the distribution model and applicable rights are established; (2) Qt's exact source/build/license/notice and translation records are obtained or another supportable product route is authorized; (3) qualified counsel determines the applicable LGPL/GPL scope, any source/offer/replacement conditions, notices, recipient terms and conditional §3/§4(c)/(e) issues; (4) independent third-party and Microsoft runtime blockers are separately closed; and (5) the release owner approves an exact final artifact and its hashes after post-assembly verification.

This report and its inquiry are drafts only. No provider was contacted, no email was sent, no application source/specification/package/release artifact was modified, no rebuild/replacement/download was performed, and no commit, push or distribution occurred. Reassess if any package component or release terms change.
