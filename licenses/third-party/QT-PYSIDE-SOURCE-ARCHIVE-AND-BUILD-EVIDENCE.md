# Qt / PySide6 / Shiboken6 source archives and build-evidence assessment

**Investigation date:** 2026-11-26  
**Scope:** Read-only examination of public Qt release metadata and the existing local package/cache. No Qt, PySide6, or Shiboken6 source archive, wheel, or Qt binary component archive was downloaded during this investigation.  
**Disposition:** **Official same-version source candidates are available. The existing pip cache now provides a strong, hash-verified link from the official PySide6 Essentials and Shiboken6 wheels to the corresponding packaged files. Exact source-to-build provenance for those binaries, and upstream Qt installer-component matches, remain unestablished. This is an evidence record, not legal advice or release clearance.**

## 1. Executive findings

1. Qt publishes Qt **6.12.0** source archives for the relevant Qt modules; Qt for Python publishes the `pyside-setup` **6.12.0** source archive containing PySide6 and Shiboken sources. Public release tags and archive indexes provide versioned candidates and advertised archive digests. These sources were not acquired or checked out here.
2. Read-only examination of the pre-existing pip HTTP cache found the full Windows AMD64 wheels for `pyside6_essentials==6.12.0` and `shiboken6==6.12.0`. Each cached wheel body has the exact byte count and SHA-256 published by Qt's official wheel mirrorlist. The cache response metadata identifies each as a PyPI binary wheel for the corresponding project and version. This is materially stronger than installed `RECORD` metadata alone: the cached wheel bytes themselves were compared with Qt's published archive digests.
3. The package's 130 files under `_internal/PySide6/` that are present in the Essentials wheel match that wheel's file payload byte-for-byte and match the wheel's embedded `RECORD` entries. The two packaged files under `_internal/shiboken6/` that are present in the Shiboken wheel likewise match its payload and `RECORD`. All wheel `RECORD` entries for included files were verified against the archive content; there were no mismatches.
4. The five VC++ DLLs packaged under `_internal/PySide6/` and three under `_internal/shiboken6/` are not entries in those respective wheels. Their origin and redistribution basis remain separate unresolved issues; do not infer that the wheel hash verifies those files.
5. This establishes an archive-hash and archive-payload link for the files actually included in the two wheels. It does **not** establish which upstream source revision, patches, generated inputs, compiler, SDK, Qt build, build configuration, third-party source revisions, CI job, or license election generated those wheel binaries. It also does not match the Qt binaries against Qt's separate online-installer component archives.
6. A controlled source/build investigation is technically feasible: retrieve the published source candidates and matching upstream build records, preserve and hash the inputs, map source paths and dependency snapshots to each file, and compare the relevant build outputs/IDs. The source tarballs alone are not a sufficient build record and may not permit reproduction without Qt's binary-build configuration and dependencies. Requesting Qt's per-build SBOM, source commit/tree, patches, build-job details and attestations is the most direct next step.

## 2. Artifact scope and local checks

The reference artifact remains the trimmed package described in the prior reports:

- Package: `dist/gui-ondir-trim-test/LogSentinel-GUI/`
- Inventory rechecked for this task: **182 files**, **80,058,228 bytes**.
- `LogSentinel-GUI.exe`: **2,386,859 bytes**, SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- The relevant packaged trees contain 135 files under `_internal/PySide6/` and five under `_internal/shiboken6/`. Of these, 130 and two respectively are in the corresponding official wheel payloads; the remaining five and three are the VC++ DLL copies described above.

Read-only local checks included: enumerating existing pip cache entries; reading CacheControl response metadata and cached bodies; calculating SHA-256 hashes; opening the existing wheel ZIP bodies without extracting them; validating wheel `RECORD` hashes and sizes against archive entries; comparing packaged paths/bytes to the wheel entries; checking package inventory and executable hash; and inspecting the existing git status and release-artifact baseline. No existing source, spec, report, package, build output, test result or release artifact was intentionally changed.

### Evidence distinction

- **Official release metadata:** Qt's official server lists a named artifact, release/version, size and advertised hash. That is a candidate and integrity reference, not local evidence that the file was acquired.
- **Cached wheel digest match:** a pre-existing HTTP-cache body has the exact digest and size published for the official Qt wheel. Matching a strong digest establishes byte identity to the published wheel archive, subject to the trustworthiness of the official digest source. The cache metadata is supporting context, not a signed acquisition receipt.
- **Wheel-payload match:** the exact packaged path bytes are found inside that hash-matched wheel and agree with its internal `RECORD`. This directly links those package files to that wheel archive's contents.
- **Source/build provenance:** none of the above establishes the source tree, build recipe, dependency inputs or build process that produced the wheel. It needs separate source/build evidence.

## 3. Cached official wheel evidence

The cache is the pre-existing pip HTTP cache under `C:/Users/DELL/AppData/Local/pip/Cache/http-v2/`. Bodies and cache metadata were read in place; nothing was copied out or installed. Cache-Control metadata contains the response headers, including PyPI's project/version/package-type headers, content length, server `Last-Modified`, ETag and a cached response date. It does not retain a sufficient original request URL, pip command, index configuration or acquisition transcript to identify the configured index conclusively.

| Distribution | Existing cached response body (relative to `http-v2/`) | Bytes | Cached body SHA-256 | Qt official mirrorlist SHA-256 | Result |
|---|---|---:|---|---|---|
| `pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl` | `0/5/3/8/0/05380cdc5a596078979626b6ab0dcd3fcf6363bb08bf21720b9ec421.body` | 82,153,795 | `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42` | `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42` | Exact digest and size match |
| `shiboken6-6.12.0-cp310-abi3-win_amd64.whl` | `f/2/3/8/4/f23847844ba4cc588be9792a855eafd5ff87ca8153edaf766dc78ef3.body` | 1,265,476 | `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e` | `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e` | Exact digest and size match |

For these responses, the cached metadata reports `x-pypi-file-project` as `pyside6-essentials` / `shiboken6`, `x-pypi-file-version: 6.12.0`, and `x-pypi-file-package-type: bdist_wheel`. The corresponding Qt official mirrorlist pages publish the same filenames, byte counts and SHA-256 values (URLs in §8). The response headers identify the PyPI file-serving infrastructure but do not by themselves prove which index URL pip used or how the body entered the cache. The archive digest correspondence is the substantive identity evidence.

### Archive and payload validation

| Check | Essentials | Shiboken |
|---|---:|---:|
| ZIP file entries | 2,483 | 73 |
| Embedded `RECORD` rows | 2,483 | 73 |
| `RECORD` entries with hash/size mismatches against archive bytes | 0 | 0 |
| Packaged tree files with an exact same-path wheel entry | 130 of 135 | 2 of 5 |
| Exact wheel-payload matches among packaged entries | 130 | 2 |
| Packaged files that are absent from that wheel | 5 | 3 |

The `RECORD` row for `RECORD` itself has no hash, as expected; all hashed entries were checked. The packaged files absent from the relevant wheel entries are:

- Essentials: `_internal/PySide6/MSVCP140.dll`, `MSVCP140_1.dll`, `MSVCP140_2.dll`, `VCRUNTIME140.dll`, and `VCRUNTIME140_1.dll`.
- Shiboken: `_internal/shiboken6/MSVCP140.dll`, `VCRUNTIME140.dll`, and `VCRUNTIME140_1.dll`.

This check also confirms that the earlier local installation/RECORD observations are consistent with the cached official wheel bytes: the 130 Essentials package files and two Shiboken package files match both the cached archive payload and the wheel's embedded manifest. It does not answer where the eight extra runtime DLL files came from. See `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md` and `QT-PYSIDE-BINARY-PROVENANCE-REPORT.md` for the separate runtime/signature findings.

## 4. Official source archives and release identifiers

All dates below were queried on **2026-11-26**. Qt's official source archive mirrorlists publish SHA-256 values. The values below are copied from those official pages and were **not** recomputed against local archive bytes, because the archives were not downloaded.

| Source scope | Official archive/repository candidate | Published identity evidence | Relationship to package |
|---|---|---|---|
| Qt Base (Core, Gui, Network, Widgets and associated source) | `qtbase-everywhere-src-6.12.0.tar.xz`; repository tag `qt/qtbase` `v6.12.0` | Archive size 51,220,268 bytes; advertised SHA-256 `a951bd163c7b80fc6b8c88d7668fb56abf91c152373e13c10666763238131307`. Tag commit prefix `025bdad1`. | Version/source candidate for `Qt6Core.dll`, `Qt6Gui.dll`, `Qt6Network.dll`, `Qt6Widgets.dll` and Qt Base plugins. No source-to-file/build link yet. |
| Qt SVG | `qtsvg-everywhere-src-6.12.0.tar.xz`; `qt/qtsvg` tag `v6.12.0` | Advertised SHA-256 `e4ab39534ec97987b1b9b60ef7f4d3253d5912a69f8c713a01753174a4029331`. | Candidate for `Qt6Svg.dll` and SVG-related plugins. Exact source/build link not established. |
| Qt Image Formats | `qtimageformats-everywhere-src-6.12.0.tar.xz`; official 6.12.0 release archive | Advertised SHA-256 `0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762`. | Candidate for image-format plugins, with per-codec sources, configuration and attribution still requiring mapping. |
| Qt translations | `qttranslations-everywhere-src-6.12.0.tar.xz`; `qt/qttranslations` tag `v6.12.0`, commit prefix `2811457c` | Advertised SHA-256 `85929c0c30d6f273f23bd879bb69803ea17b010ab73cab2f8abf95357f6f6bbb`. | Candidate for 99 packaged `.qm` catalogs. Exact catalog-to-source mapping, license classification per source and `lrelease` generation evidence are open. |
| Qt Linguist/build tools | `qttools-everywhere-src-6.12.0.tar.xz` | Advertised SHA-256 `8dab8f3611496486a470ad5f115ceea584f36bc22a2b8b6f6ebdbafbb8160693`. | Source candidate for tooling such as `lrelease`; it does not establish which tool binary/options generated each packaged catalog. |
| Qt for Python, PySide6 and Shiboken6 | `pyside-setup-everywhere-src-6.12.0.tar.xz`; repository tag `pyside/pyside-setup` `v6.12.0` | Archive size 18,211,772 bytes; advertised SHA-256 `099c1a597cf33c1b000e11cf68a0b82d216fb802bf81726efc720394f10c7751`. Release tag commit prefix `f50facb8`. | Candidate source for bindings, `pyside6.abi3.dll`, Shiboken runtime/generator sources and build scripts. Neither source archive nor build inputs were compared with the wheel binaries. |
| Combined Qt source tree | `qt-everywhere-src-6.12.0.tar.xz` | Official single-source archive index lists the 6.12.0 combined source tree; its mirrorlist advertises SHA-256 `98ff4f44bac6ec3e1e62ee2a4316ae0e3d15badb015d753cc0268a20db52f165`. | Convenient source-candidate path, not a Windows binary build record or proof of exact source linkage. |

The Qt release source index also lists the separate module archives and their companion ZIP alternatives. Prefer the specific module archives when building a narrow file-to-source map; the combined archive may be useful for an authorized broader review. The source archive tags and version labels are consistent with the version resources in the package, but the package's Qt version resources are not proof that those exact tagged source trees generated the binaries.

### Source archive integrity and provenance caveats

- Official Qt server mirrorlists advertise SHA-256; these should be verified after any authorized retrieval. Qt's Qt 6.12.0 submodule index also has an `md5sums.txt` file; MD5 is weaker and should not replace the published SHA-256 check.
- A matching archive hash verifies the acquired archive against the server's published digest. It does not prove that the Qt wheel/installer binary was built from that archive, was unmodified after build, or has the same license election.
- Git tags/short commit IDs identify upstream repository points; a source archive's content should be tied to the tag/tree and any generated or vendored inputs. A tag alone is not a binary build attestation.
- Qt's official online MSVC2022 x64 installer component archives are separate binary candidates, including qtbase, qtsvg and qtimageformats packages. Their existence, version metadata, Qt signatures, and matching PDB path clues are recorded in `QT-PYSIDE-BINARY-PROVENANCE-REPORT.md`. The candidate archives were not acquired or compared in this task. The wheel match established here does not separately identify those installer packages as the source of the wheel's Qt DLLs.

## 5. Build evidence: what exists and what is missing

### Publicly obtainable or requestable

- **Qt source and build guidance:** Qt 6.12 documentation describes Windows source-build requirements, supported compiler/tool configurations, third-party dependency selection, and SBOM generation. Qt's SBOM documentation says SBOMs can be generated for platform/build configurations and that Online Installer installations place them under an `sbom` directory. This describes a method and expected artifact location; it is not evidence that an SBOM matching this specific 6.12.0 PySide wheel build was available locally.
- **Qt CI/release records:** Qt publishes release tags and CI/release materials. These can help identify source state and release process, but a general CI task or successful module build is not enough; the evidence must identify the exact binary job/artifact and connect it to shipped hashes.
- **PySide/Shiboken source and build guidance:** Qt for Python publishes `pyside-setup` source, Windows and general source-build instructions, and the versioned wheel files. Its instructions identify typical Python, Qt, CMake, Git, libclang and Windows MSVC requirements. They do not record the precise inputs used for these particular official wheel files.
- **PySide SBOM reference:** the Qt for Python 6.12.0 release notes indicate SBOM-related work. A package-matched SBOM, its schema, scope, checksums and relation to the Windows AMD64 release wheel still need to be obtained and validated; the release-note entry alone is not that evidence.
- **Build metadata from existing binaries:** the provenance report records Qt version resources, valid Qt signatures, AMD64 architecture, MSVC linker metadata and Qt CodeView/PDB path strings. These are useful corroborating clues, but not the full compiler version, source revision, build options or build job.

### Not found in the examined local material

- Qt/PySide/Shiboken source archives, checkouts, submodule source trees or source-file manifests.
- Original wheel-to-source build attestation, exact Qt binary SDK/install package identity for the wheel producer, or signed per-file build-provenance statements.
- A Qt or PySide SBOM demonstrably scoped to the exact official Essentials/Shiboken Windows AMD64 wheels and their hashes.
- Source patch lists, generated-source manifests, source tree hashes, build configuration/CMake cache, exact compiler/linker/Windows SDK identifiers, CI job logs and reproducibility results for these files.
- Matching Qt PDB files and signed mapping of each CodeView GUID/age to a specific source commit and build job.
- `.qm` source catalog mapping for the 99 packaged catalogs and the exact `lrelease` tool build/options.
- A complete install/acquisition transcript or original URL/index configuration for the pip cache bodies. Cached metadata gives project/version/type headers, sizes, dates and ETags, but not a conclusive request URL or operator action.
- Provenance evidence for the eight nested VC++ DLLs absent from the two wheels.

The local `.venv-build-gui` `METADATA`, `WHEEL`, `INSTALLER` and `RECORD` files remain useful package consistency evidence. For the included wheel files, the new archive-to-package comparison is stronger than the installed manifest alone. None of those installed files records the producer's source/build configuration or proves that the eight additional VC++ DLLs came from those wheels.

## 6. Traceability and feasibility assessment

| Evidence link | Status after this investigation | Feasibility / next evidence |
|---|---|---|
| Qt 6.12.0 source release availability | **Publicly established as a candidate** through official versioned archive indexes, tags and advertised SHA-256 values. | High: authorized retrieval and digest verification are straightforward. Establishing that these sources built the shipped binaries requires vendor/build records or a controlled binary comparison. |
| PySide6 Essentials wheel archive to official digest | **Strongly established:** existing cached body size and SHA-256 exactly equal Qt's published official wheel metadata. | High: repeatable locally from the preserved cache body and official mirrorlist digest. Preserve the cache body/metadata under an approved evidence-retention process if the project later authorizes it; no copy was made here. |
| Shiboken6 wheel archive to official digest | **Strongly established:** existing cached body size and SHA-256 exactly equal Qt's published official wheel metadata. | High: same conditions as Essentials. |
| Wheel payload to packaged Qt/PySide/Shiboken files | **Established for 130 Essentials and two Shiboken files:** exact path/content and wheel `RECORD` validation. | High: rerun with a documented script/procedure when preparing a release candidate; retain per-file hashes and wheel archive hashes. |
| Wheel archive acquisition URL, index and installation event | **Partial:** cache response headers indicate PyPI-serving metadata; no complete request URL or pip transcript was found. | Moderate: check retained pip logs, proxy/index logs, shell history, lock files, CI records or package-manager logs, if available. This gap no longer prevents archive-byte identity because the cached digest matches Qt's published official digest, but it matters to acquisition-chain documentation. |
| Qt source tree to Qt DLL/plugin build | **Open:** module/version candidates and binary clues exist; no build mapping. | Low to moderate without Qt cooperation. Request exact component-to-source revisions, patches, Windows build configuration, SBOM, PDBs and per-file build/job attestations. A source-only rebuild could be costly and still fail to reproduce vendor build settings. |
| PySide/Shiboken source to matching official wheel build | **Open:** exact official wheel archive identified, source candidate and release tag publicly listed; no source/build attestation. | Moderate with Qt for Python build artifacts or signed CI attestations. A local rebuild from the tag is useful corroboration but cannot substitute for proof of the vendor wheel's inputs unless its outputs and build environment can be independently matched. |
| Qt third-party source/version/notice mapping | **Partial:** public Qt 6.12 attributions/SBOM documentation and package binary markers are described in prior reports. | Moderate if Qt supplies the wheel-scoped SBOM and third-party component manifest; otherwise requires source-tree inspection, plugin mapping, build-option evidence and component-specific license review. |
| Translation catalog source and licenses | **Open:** 99 `.qm` files are present and match the exact Essentials wheel payload. | Moderate: acquire matching qttranslations source, map catalog bytes/metadata to `.ts` files, identify per-file license/notice and `lrelease` version/invocation. Catalog byte identity to a wheel does not establish source author/license. |
| Eight extra VC++ runtime DLLs | **Not linked to the matching Essentials/Shiboken wheel payloads.** | Requires separate supplier origin records, Microsoft redistribution eligibility review and Qt written explanation; do not attribute these to the wheel on version/signature alone. |

### Overall assessment

**Source archives:** obtainable from official release locations, with versioned source repositories and advertised digests.  
**Wheel binary identity:** now strongly linked to the official published 6.12.0 Essentials and Shiboken wheel archives by exact SHA-256 and package-file comparison.  
**Source-to-binary provenance:** not established. The source archive and wheel archive are both identified, but the evidence connecting source revision/build inputs to the signed wheel binaries is missing.  
**Qt installer binary-source link:** still unverified for specific Qt online component archives; the direct wheel link covers Qt DLLs/plugins that are entries in the matching Essentials wheel, not separate installer packages.  
**Distribution/legal readiness:** unchanged. This report does not clear the release or resolve the licensing and redistribution issues in the final audit.

## 7. Unresolved questions

1. Can Qt provide a wheel-scoped, signed or otherwise verifiable SBOM for the exact Essentials and Shiboken wheel hashes, with source repository commits/tree hashes, third-party sources/versions/licenses, build configuration and file-level hashes?
2. Which `qtbase`, `qtsvg`, `qtimageformats`, `qttranslations` and `qttools` source revisions and dependency snapshots produced each relevant binary and catalog? Were there downstream cherry-picks, patches, generated inputs or release-branch changes beyond the public tags?
3. Which exact Qt MSVC2022 x64 installer component build/archives, if any, were used to build Qt for Python 6.12.0 Windows wheels? Can Qt map package PE hashes and Qt CodeView GUID/age values to a particular build job, archived PDB set and source tree?
4. What exact compiler/linker servicing build, Visual Studio update, Windows SDK, CRT settings, Qt configure flags, feature selections and build environment were used for the wheel binaries?
5. What PySide/Shiboken generator and typesystem inputs, generated source, Python headers/ABI, Qt headers/libs, libclang version and build options were used? Are per-wheel build attestations or source/build manifests available?
6. Does the official source archive hash match the retrieved bytes when acquired, and does the archive's unpacked Git/tree content correspond to the stated release tag and expected submodule/dependency snapshots?
7. What exact `.ts` source and source license correspond to each of the 99 wheel-matched `.qm` catalogs, and what `lrelease` version/options created them?
8. What supplied the five Essentials and three Shiboken VC++ DLL copies absent from those wheel payloads, and what is Qt's written legal/provenance basis for their distribution?
9. Can the exact wheel builds be reproduced from the published source and documented configuration? If not, can Qt furnish an auditable build record sufficient to establish the applicable corresponding source and binary relationship? A failure to reproduce would not itself show that the source archive is wrong.
10. Does Qt's public or vendor-specific licensing record identify the license election applicable to these exact wheel binaries and relevant Qt/PySide/Shiboken components? The wheel metadata's license expression is not a binary-specific election record.

## 8. Recommended next steps

1. Preserve this finding and the pre-existing pip cache without modifying either. If a formally controlled evidence copy is later authorized, copy the cache bodies and metadata to a separate evidence location, record chain of custody, hash each file, and preserve access controls. No additional archive retrieval is needed to substantiate the wheel SHA-256 match already observed.
2. Ask Qt for the source/build provenance package for the exact Essentials and Shiboken SHA-256 values listed in §3: source commits/tree hashes, patches, generated sources/typesystems, Qt SDK/component archive hashes, compiler/SDK/configuration, SBOM, CI job identifiers, PDBs and signed build attestations.
3. Ask for corresponding Qt records for each packaged Qt DLL/plugin, including exact online component archive identity and a per-file mapping between binary hash, PDB GUID/age, source target/revision and build job.
4. If authorized, acquire only the necessary versioned source archives to a separate evidence area, verify the Qt-published SHA-256 before unpacking, preserve acquisition details, and inspect the relevant per-file license/third-party inputs. Do not write them into the application package or overwrite any prior report.
5. If matching source/build materials are provided, create a file-level traceability matrix for each package path: package hash → wheel/archive entry hash → upstream source path/commit → generated/third-party inputs → build job/configuration → applicable license/notice. Mark every unsupported edge explicitly.
6. Map the 99 `.qm` catalogs independently to `.ts` sources and source-license records; identify the exact compiler tool and invocation where possible.
7. Resolve the eight extra VC++ DLLs through the separate runtime review and vendor/Microsoft evidence. Do not use the wheel digest match as evidence for those files.
8. Continue the release HOLD pending qualified legal review, Qt confirmation, source/notice preparation, corresponding-source and LGPL route decisions, and final artifact-specific review. Do not rebuild, replace, repackage, commit or push without explicit authorization.

## 9. Source and evidence references

### Official Qt sources and release metadata

- Qt 6.12.0 release directory: <https://download.qt.io/official_releases/qt/6.12/6.12.0/>.
- Qt 6.12.0 source module index and `md5sums.txt`: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/>.
- qtbase source archive mirrorlist (size and SHA-256): <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtbase-everywhere-src-6.12.0.tar.xz.mirrorlist>.
- qtsvg source archive mirrorlist: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtsvg-everywhere-src-6.12.0.tar.xz.mirrorlist>.
- qtimageformats source archive mirrorlist: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtimageformats-everywhere-src-6.12.0.tar.xz.mirrorlist>.
- qttranslations source archive mirrorlist: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qttranslations-everywhere-src-6.12.0.tar.xz.mirrorlist>.
- qttools source archive mirrorlist: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qttools-everywhere-src-6.12.0.tar.xz.mirrorlist>.
- Combined Qt 6.12.0 source archive mirrorlist: <https://download.qt.io/official_releases/qt/6.12/6.12.0/single/qt-everywhere-src-6.12.0.tar.xz.mirrorlist>.
- qtbase tag `v6.12.0`: <https://github.com/qt/qtbase/tree/v6.12.0>.
- qtsvg tag `v6.12.0`: <https://code.qt.io/cgit/qt/qtsvg.git/tag/?h=v6.12.0>.
- qttranslations tag `v6.12.0`: <https://invent.kde.org/qt/qt/qttranslations/-/tags/v6.12.0>.
- Qt 6.12.0 Windows build requirements: <https://doc.qt.io/qt-6.12/windows-building.html>.
- Qt third-party dependency/configuration options: <https://doc.qt.io/qt-6.12/configure-options.html>.
- Qt SBOM format and install/build generation description: <https://doc.qt.io/qt-6.12/sbom.html>.
- Qt 6.12 licensing and third-party attributions: <https://doc.qt.io/qt-6.12/licensing.html>, <https://doc.qt.io/qt-6.12/licenses-used-in-qt.html>.

### Official Qt for Python sources and wheel metadata

- Qt for Python 6.12.0 source archive directory: <https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/>.
- `pyside-setup` source archive mirrorlist (size and SHA-256): <https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/pyside-setup-everywhere-src-6.12.0.tar.xz.mirrorlist>.
- `pyside-setup` tag `v6.12.0`: <https://github.com/pyside/pyside-setup/tree/v6.12.0>.
- Qt official Essentials wheel mirrorlist: <https://download.qt.io/official_releases/QtForPython/pyside6-essentials/pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl.mirrorlist>.
- Qt official Shiboken6 wheel mirrorlist: <https://download.qt.io/official_releases/QtForPython/shiboken6/shiboken6-6.12.0-cp310-abi3-win_amd64.whl.mirrorlist>.
- PySide6 aggregate wheel mirrorlist (metapackage, not the Qt bindings payload): <https://download.qt.io/official_releases/QtForPython/pyside6/pyside6-6.12.0-cp310-abi3-win_amd64.whl.mirrorlist>.
- Qt for Python build-from-source requirements: <https://doc.qt.io/qtforpython-6/building_from_source/index.html> and <https://doc.qt.io/qtforpython-6/building_from_source/windows.html>.
- Qt for Python 6.12 release notes: <https://doc.qt.io/qtforpython-6/release_notes/pyside6_release_notes.html>.
- PyPI metadata (release records; metadata is not a build attestation): <https://pypi.org/project/PySide6-Essentials/6.12.0/>, <https://pypi.org/project/shiboken6/6.12.0/>.

### Existing project evidence

- `licenses/third-party/QT-PYSIDE-BINARY-PROVENANCE-REPORT.md` — package PE inventory, hashes/signatures, PDB clues, Qt installer archive candidates, and prior source/binary gap assessment.
- `licenses/third-party/QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md` — package inventory, local installed `RECORD` checks, relevant source candidates and component/source questions.
- `licenses/third-party/QT-PYSIDE-LGPL-DISTRIBUTION-ASSESSMENT.md` — conditional LGPL routes and evidence needs.
- `licenses/third-party/FINAL-LICENSING-AUDIT.md` and `licenses/third-party/MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md` — overall HOLD disposition and separate runtime provenance/eligibility issues.

## 10. Verification and limitations

- The inspected package identity remained **182 files / 80,058,228 bytes**; the executable SHA-256 remained `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- The two cached wheel bodies match the Qt official published archive sizes and SHA-256 values, and the included package payload files match their corresponding wheel entries and `RECORD` checks as tabulated in §3.
- No Qt/PySide/Shiboken source archive, wheel, Qt installer component archive, new binary, or replacement file was downloaded or installed during this task. The two wheel bodies were already present in the local pip cache before this investigation.
- No source, packaging specification, existing report, verified package file, test-result file, release artifact, or source build output was intentionally modified. No commit or push was made.
- The exact wheel SHA-256 match improves the binary-distribution traceability finding, but does not establish source-to-binary provenance, resolve the extra VC++ DLLs, satisfy licensing requirements, or change the release **HOLD / NOT CLEARED FOR DISTRIBUTION** disposition.
