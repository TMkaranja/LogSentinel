# Qt / PySide6 corresponding-source register — trimmed Windows onedir package

**Assessment date:** 2026-11-09  
**Status:** **PARTIAL SOURCE-IDENTITY EVIDENCE; CORRESPONDING SOURCE NOT ESTABLISHED.** This is a read-only engineering source register, not legal advice, a compliance conclusion, or a release approval. A public source repository or same-version archive is only a candidate until matched to the shipped binaries and their build inputs.

## 1. Executive summary

The reference artifact is `dist/gui-ondir-trim-test/LogSentinel-GUI/`, not the earlier 185-file package described in some historical records. It contains 182 files / 80,058,228 bytes. Qt/PySide files are in `_internal/PySide6/` and `_internal/shiboken6/`; `Qt6Pdf.dll`, `qpdf.dll`, and `opengl32sw.dll` are absent.

New read-only checks strengthen one part of the source trail:

- Every one of the **140 files** under the package's `_internal/PySide6/` and `_internal/shiboken6/` trees is byte-identical (SHA-256) to the same relative file in the existing `.venv-build-gui/Lib/site-packages/` installation.
- **132 of 140** also have matching SHA-256 entries in local installed wheel `RECORD` files: 130 entries attributed by local metadata to `pyside6_essentials-6.12.0.dist-info` and two to `shiboken6-6.12.0.dist-info`. The other eight are VC++ runtime DLL copies without explicit matching `RECORD` hashes. The local PySide6/Shiboken distribution metadata reports version 6.12.0 and the inspected package binaries/plugins with Windows version resources report Qt 6.12.0.0.
- This proves package-to-local-install equality and checks those 132 files against the installed manifests. It does **not** independently identify the downloaded wheel files, their URLs or archive hashes, prove the installed `RECORD` was not altered, or connect any binary to a particular upstream source revision, license election, compiler configuration, patch set, SBOM, or build.

Official Qt 6.12.0 source archives and version tags, and the Qt for Python 6.12.0 source archive and tag, are publicly identified. They were **not downloaded or added** in this read-only task. Their public availability is not proof those sources generated these Qt/PySide/Shiboken files. The repository contains licensing and attribution evidence but no corresponding Qt/PySide source trees, wheel archives, matched build manifests, exact source-to-binary records, or reproduction package. Therefore the repository currently contains **insufficient corresponding-source materials** for the exact trimmed package.

## 2. Scope, identity and method

### Artifact identity

- Package: `dist/gui-ondir-trim-test/LogSentinel-GUI/`
- Files / total size: **182 / 80,058,228 bytes**.
- `LogSentinel-GUI.exe`: 2,386,859 bytes; SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- Package file-type summary: 42 DLLs, 16 PYDs, 99 QM translations, 22 SVGs, one ZIP, one ICO, one EXE.
- Qt/PySide directories contain 135 files in `PySide6/` and five in `shiboken6/` (140 total).
- The package itself has no `.txt`, `.md`, or `.rst` license/source notice files.

### Read-only checks performed

1. Enumerated the actual package's PySide6 and Shiboken6 files and read PE version resources for Qt DLLs/plugins and the VC++ DLLs; read local wheel metadata/`RECORD` files in the already-existing build virtual environment.
2. Compared each of the 140 packaged Qt/PySide/Shiboken tree files byte-for-byte with its same-relative-path local site-packages file.
3. Checked each package file against the hash entry in the applicable local distribution `RECORD` when such an entry exists.
4. Consulted the official source archive indexes, release tags and build/licensing documentation listed below on **2026-11-09**. No source archive or binary was downloaded, extracted, replaced or rebuilt.

These checks do not verify wheel origin or source provenance. Installed metadata/RECORD can support an evidence chain but is not a signed attestation of the wheel's upstream origin or build.

## 3. Exact package component inventory

All paths below are relative to `dist/gui-ondir-trim-test/LogSentinel-GUI/_internal/`. Qt version resources were reported as 6.12.0.0 on the five module DLLs and 20 plugin DLLs. Python extension modules and `pyside6.abi3.dll` do not expose a comparable Qt file-version resource; local distribution metadata reports PySide6/Shiboken6 6.12.0.

### 3.1 Qt shared libraries

| Package path | Package fact / candidate source project | Source status |
|---|---|---|
| `PySide6/Qt6Core.dll` | Qt Core; Qt 6.12.0.0. Candidate source: `qt/qtbase`, tag/source archive 6.12.0. | Version and local wheel-record bytes supported; binary-to-source/build mapping open. |
| `PySide6/Qt6Gui.dll` | Qt Gui; Qt 6.12.0.0. Candidate: `qt/qtbase`, including any statically incorporated components. | Same. |
| `PySide6/Qt6Network.dll` | Qt Network; Qt 6.12.0.0. Candidate: `qt/qtbase`. | Same. |
| `PySide6/Qt6Widgets.dll` | Qt Widgets; Qt 6.12.0.0. Candidate: `qt/qtbase`. | Same. |
| `PySide6/Qt6Svg.dll` | Qt Svg; Qt 6.12.0.0. Candidate: `qt/qtsvg`. | Same. |

The local package also includes static/linked third-party code evidenced in the existing audit: e.g. FreeType, HarfBuzz, libpng, PCRE2/SLJIT and zlib-compatible code in Qt modules, and image-codec code in plugins. These are **not resolved by the Qt module source archives alone** until the precise source revisions, configuration, bundled/system choice, patches and applicable license materials are matched. See §6 and the final audit/trimmed notice map.

**Upstream license-family statements (not a package license election):** Qt 6.12.0 module pages identify Core, Widgets and SVG as commercial or LGPLv3/GPLv2. The reviewed Qt Gui, Qt Network and Qt Image Formats pages resolve to Qt 6.12.1 and identify the same license family; they are supporting context, not exact 6.12.0 package proof. QUIP 18 describes module/plugin implementation files as either `LicenseRef-Qt-Commercial OR LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`, or GPL-only as `LicenseRef-Qt-Commercial OR GPL-3.0-only`; exact source-file expressions and module-page terms govern. These public statements establish upstream source terms, not that the package came from those sources or which option is being relied upon.

### 3.2 Qt plugins

The package includes these 20 plugin DLLs, all reporting Qt 6.12.0.0. Source project mapping below is a likely source area based on Qt's module layout and public documentation, not binary provenance. A Qt SBOM/build manifest or binary-to-build record is still required for each plugin and embedded codec.

| Package path(s) | Candidate official source project(s) | Main source/build gap |
|---|---|---|
| `PySide6/plugins/generic/qtuiotouchplugin.dll` | `qt/qtbase` | Exact source target, build flags and patches. |
| `PySide6/plugins/iconengines/qsvgicon.dll`; `PySide6/plugins/imageformats/qsvg.dll` | `qt/qtsvg` and/or `qt/qtbase` plugin integration | Verify actual repository/source target for each packaged plugin and any QtSvg dependencies. |
| `PySide6/plugins/imageformats/qgif.dll`; `qico.dll`; `qjpeg.dll` | `qt/qtbase` likely; codec sources may be in its `src/3rdparty` | Confirm exact plugin source and codec revision/selection; qjpeg's libjpeg-turbo mapping is not source-hash verified. |
| `PySide6/plugins/imageformats/qicns.dll`; `qtga.dll`; `qtiff.dll`; `qwbmp.dll`; `qwebp.dll` | `qt/qtimageformats` likely | Confirm exact release/source target and codec snapshot/patches. libtiff/libwebp versions and notices remain unresolved in the package audit. |
| `PySide6/plugins/networkinformation/qnetworklistmanager.dll` | `qt/qtbase` | Exact source target, Windows APIs/SDK and build options. |
| `PySide6/plugins/platforms/qdirect2d.dll`; `qminimal.dll`; `qoffscreen.dll`; `qwindows.dll` | `qt/qtbase` | Exact source target, compiler/SDK, build options and patch state. |
| `PySide6/plugins/styles/qmodernwindowsstyle.dll` | `qt/qtbase` likely | Confirm exact source target/terms and build inputs. |
| `PySide6/plugins/tls/qcertonlybackend.dll`; `qopensslbackend.dll`; `qschannelbackend.dll` | `qt/qtbase` | Map plugin source and configuration. `qopensslbackend` is a plugin; the separate bundled OpenSSL DLLs are an external dependency addressed separately in the final audit. |

**Not present in this package:** `PySide6/Qt6Pdf.dll`, `PySide6/plugins/imageformats/qpdf.dll`, `PySide6/opengl32sw.dll`. Do not include Qt PDF/PDFium or Mesa/LLVM as package components based only on older inventory documents.

### 3.3 PySide6 binding files

| Exact package paths | Local version evidence | Candidate official source | Status |
|---|---|---|---|
| `PySide6/QtCore.pyd`, `QtGui.pyd`, `QtNetwork.pyd`, `QtSvg.pyd`, `QtWidgets.pyd` | Local `pyside6_essentials` metadata reports 6.12.0; each file matches the installed `RECORD` hash. | `pyside/pyside-setup`, release tag/source archive `v6.12.0`, primarily `sources/pyside6`. | Package-to-local-wheel-manifest evidence verified; exact wheel artifact, source commit/build output, generated files and patch state open. |
| `PySide6/pyside6.abi3.dll` | Same local `pyside6_essentials` manifest match; distribution 6.12.0. | `pyside/pyside-setup`, `sources/pyside6` and build/package scripts. | Same. |
| Embedded PYZ code objects `PySide6`, `PySide6.support`, `PySide6.support.deprecated` | Present in the frozen executable archive; local source files exist in the installed PySide6 distribution. | `pyside/pyside-setup`, `sources/pyside6/PySide6/`. | Frozen bytecode mapping/source commit and compiled settings are not verified; package source files are not shipped as source. |
| Embedded PYZ code object `shiboken6` | Present in the frozen executable archive; local source file exists in installed Shiboken6 distribution. | `pyside/pyside-setup`, `sources/shiboken6/`. | Frozen bytecode mapping/source commit/build settings not verified. |

The aggregate `PySide6` wheel is documented as an alias/metapackage depending on `PySide6_Essentials` and `PySide6_Addons`. The files in the trimmed package are drawn from installed distribution content; local RECORD hash matches were found for 130 package files in the essentials manifest and two in Shiboken's manifest. The frozen PYZ also contains four PySide/Shiboken Python package modules: `PySide6`, `PySide6.support`, `PySide6.support.deprecated`, and `shiboken6`. Their local source counterparts and installed metadata are present in `.venv-build-gui`, but their frozen code-object bytes are not source files and were not matched/reproduced from source. The wrapper/generated C++ source, typesystem inputs, generator version, Qt headers and exact wheel inputs are not included in this project repository.

### 3.4 Shiboken6 runtime files

| Exact package path | Local version evidence | Candidate official source | Status |
|---|---|---|---|
| `shiboken6/Shiboken.pyd` | Local `shiboken6` metadata 6.12.0 and matching RECORD SHA-256. | `pyside/pyside-setup`, `sources/shiboken6`, particularly libshiboken. | Local distribution manifest match; exact upstream wheel/source/build mapping open. |
| `shiboken6/shiboken6.abi3.dll` | Local metadata 6.12.0 and matching RECORD SHA-256. | `pyside/pyside-setup`, Shiboken source/build scripts. | Same. |

Qt for Python documentation describes Shiboken as both a generator and a Python helper module. Its third-party license listing identifies specific code incorporated into libshiboken and signature support (including Python buffer-related code and copied/adapted signature sources). Therefore source correspondence for the Shiboken runtime must include applicable copied/modified files and their original notices, not only the main Qt libraries. The precise component list and source revision for this built DLL remain unverified.

### 3.5 Translation catalog files

All 99 package files are under `PySide6/translations/` and match the local installed files byte-for-byte. The 130 `pyside6_essentials` RECORD matches include the packaged catalogs. Qt's `qttranslations` release is the principal source candidate; Qt Linguist's `lrelease` source/build tool is in `qt/qttools` and is needed to reproduce `.qm` outputs from `.ts` catalogs.

- **66 files matching `qt_*.qm`:** this wildcard group includes 29 `qt_help_<locale>.qm` files and 37 other `qt_<locale>.qm` files. The 37 non-help locale suffixes are `ar,bg,ca,cs,da,de,en,es,fa,fi,fr,gd,gl,he,hr,hu,it,ja,ka,kk,ko,lg,lt,lv,nl,nn,pl,pt_BR,pt_PT,ru,sk,sl,sv,tr,uk,zh_CN,zh_TW`.
- **29 `qt_help_*.qm`:** `ar,bg,ca,cs,da,de,en,es,fr,gl,hr,hu,it,ja,ka,kk,ko,nl,nn,pl,pt_BR,ru,sk,sl,sv,tr,uk,zh_CN,zh_TW`.
- **33 `qtbase_*.qm`:** `ar,bg,ca,cs,da,de,en,es,fa,fi,fr,gd,he,hr,hu,it,ja,ka,kk,ko,lg,lv,nl,nn,pl,pt_BR,ru,sk,sv,tr,uk,zh_CN,zh_TW`.

The 66 `qt_*.qm` wildcard matches include the 29 `qt_help_*.qm` files, so the disjoint count is 37 `qt_*.qm` excluding `qt_help_*.qm`, plus 29 help files and 33 `qtbase_*.qm` files = 99. Exact source `.ts` association, catalog contributor notices, `lrelease` version/options, generated-file metadata and catalog-specific source mapping remain unverified. QUIP 18 describes usual Qt translation `.ts` files as `LicenseRef-Qt-Commercial OR BSD-3-Clause`; do not automatically classify these catalogs as LGPL module binaries. Use exact source-file notices and counsel's review for the compiled files.

### 3.6 Supporting dependencies in/near the Qt trees

| Files / dependency | Relation to this register | Source / rights evidence |
|---|---|---|
| `_internal/PySide6/MSVCP140.dll`, `MSVCP140_1.dll`, `MSVCP140_2.dll`, `VCRUNTIME140.dll`, `VCRUNTIME140_1.dll`; `_internal/shiboken6/MSVCP140.dll`, `VCRUNTIME140.dll`, `VCRUNTIME140_1.dll` | Eight runtime DLL copies under the PySide6/Shiboken directories. They match local site-packages files but have no explicit matching wheel RECORD SHA-256 entries. | Not Qt/PySide LGPL source. Microsoft's redistribution eligibility, file provenance and terms remain open in `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`; Qt's written wheel-DLL basis is outstanding. Do not infer source or permission from version/signature alone. |
| `_internal/MSVCP140.dll`, `_internal/VCRUNTIME140.dll` | Two additional VC++ runtime files at package internal root (10 copies total in the full package). | Separate Microsoft source/redistribution issue, not Qt/PySide corresponding source; see `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`. |
| `_internal/libcrypto-3.dll`, `_internal/libssl-3.dll` | Separate OpenSSL runtime files used by CPython and potentially by Qt's optional OpenSSL TLS backend. | Not Qt/PySide source. Existing runtime evidence identifies OpenSSL 3.5.9 candidates and archive evidence; build provenance remains open in `RUNTIME-LICENSING-EVIDENCE.md` and `FINAL-LICENSING-AUDIT.md`. |
| `_internal/python314.dll`, `_internal/python3.dll`, Python runtime/extensions | Runtime environment used by PySide/Shiboken extension modules. | Separate CPython source/license scope; exact CPython build inputs and embedded-code correspondence are open in the final audit. |

These supporting files are included here to avoid conflating “Qt source” with dependencies that the Qt/PySide runtime may load. They require their own source/license evidence and are not made part of Qt's corresponding source merely by being stored beside Qt DLLs.

## 4. Version-to-source and official-source register

URLs below were consulted **2026-11-09**. No archive was downloaded. The archive hashes are values advertised by Qt's official mirrorlist/index, not hashes verified against a local file in this investigation.

| Component/version observed | Official source repository, release archive/tag candidate | Public license evidence | Provenance conclusion |
|---|---|---|---|
| Qt Core/Gui/Network/Widgets 6.12.0.0 | [qt/qtbase tag v6.12.0](https://github.com/qt/qtbase/tree/v6.12.0); [qtbase 6.12.0 source archive](https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtbase-everywhere-src-6.12.0.tar.xz); official mirrorlist advertises SHA-256 `a951bd163c7b80fc6b8c88d7668fb56abf91c152373e13c10666763238131307`. | Qt's Qt 6.12 LGPL/licensing pages and source-file licensing expressions; source-tree components have file-specific terms. See §5 and attribution register. | Versioned source candidate available. No matching Windows Qt wheel SBOM/build ID, compiler/configure record, patch inventory, or source hash for the package DLLs. |
| Qt Svg 6.12.0.0 and SVG plugin candidates | [qt/qtsvg tag v6.12.0](https://code.qt.io/cgit/qt/qtsvg.git/tag/?h=v6.12.0); [qtsvg 6.12.0 archive](https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtsvg-everywhere-src-6.12.0.tar.xz); advertised SHA-256 `e4ab39534ec97987b1b9b60ef7f4d3253d5912a69f8c713a01753174a4029331`. | Qt module terms plus file-level terms in repository. | Versioned candidate; no DLL/source/build match. |
| Qt image-format plugin candidates 6.12.0.0 | [qt/qtimageformats tag/source project](https://github.com/qt/qtimageformats); [qtimageformats 6.12.0 archive](https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtimageformats-everywhere-src-6.12.0.tar.xz); advertised SHA-256 `0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762`. | Qt module terms plus distinct codec licenses/attributions. Qt 6.12.0 component candidates in the existing audit include libjpeg-turbo 3.2.0, libtiff candidate 4.7.2 and libwebp candidate 1.6.0; exact inclusion/source snapshots remain open. | Versioned source candidate; plugin-by-plugin source attribution, codec source, patches, build options and Qt SBOM needed. |
| Qt translations 6.12.0 catalogs | [qt/qttranslations tag v6.12.0](https://invent.kde.org/qt/qt/qttranslations/-/tags/v6.12.0) (release mirror reports short commit `2811457c`); [archive](https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qttranslations-everywhere-src-6.12.0.tar.xz); advertised SHA-256 `85929c0c30d6f273f23bd879bb69803ea17b010ab73cab2f8abf95357f6f6bbb`. | QUIP 18: usual `translations/*.ts` files are commercial OR BSD-3-Clause; individual files may differ. | Source candidate only; exact 99 QM-to-TS mapping and compiler invocation are absent. |
| Qt Linguist/lrelease source, tools 6.12.0 | [qt/qttools tag/source project](https://github.com/qt/qttools); [archive](https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qttools-everywhere-src-6.12.0.tar.xz); advertised SHA-256 `8dab8f3611496486a470ad5f115ceea584f36bc22a2b8b6f6ebdbafbb8160693`. | File-specific Qt terms; source path for translation compiler tooling. | Build-tool source candidate; no exact `lrelease` executable version/options or catalog-generation record. `lrelease` is not itself present as a package executable. |
| PySide6 6.12.0 bindings and `pyside6.abi3.dll` | [pyside/pyside-setup tag v6.12.0](https://github.com/pyside/pyside-setup/tree/v6.12.0), release commit prefix `f50facb`; [official source archive](https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/pyside-setup-everywhere-src-6.12.0.tar.xz); advertised SHA-256 `099c1a597cf33c1b000e11cf68a0b82d216fb802bf81726efc720394f10c7751`. | PyPI/local metadata expression `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; Qt for Python docs describe LGPLv3/GPLv3 and commercial. Election and GPLv2 discrepancy unresolved. | Official source candidate exists. No source archive downloaded or matched, and no original installed wheel archive/hash/build provenance captured. |
| Shiboken6 6.12.0 (`Shiboken.pyd`, `shiboken6.abi3.dll`) | Same [pyside-setup v6.12.0 source tag](https://github.com/pyside/pyside-setup/tree/v6.12.0) and source archive above; Shiboken code is in `sources/shiboken6` and generator sources. | Same published expression/Qt for Python licensing; separate file-specific third-party notices. | Same source candidate gap. Local RECORD confirms copies but not origin/build or exact third-party copied/adapted code. |
| MSVC DLLs under PySide6/Shiboken | No Qt source archive is applicable to the Microsoft runtime itself. The local package paths are listed in §3.6. | Microsoft runtime license/redistribution terms; not an open-source license election. | File eligibility and origin remain open under the separate MSVC report. |

### Archive/source publication interpretation

Qt's official source download indexes expose `qtbase`, `qtsvg`, `qtimageformats`, `qttranslations` and `qttools` 6.12.0 archives; the Qt for Python site exposes `pyside-setup-everywhere-src-6.12.0`. The corresponding repositories/tags are useful fixed-version references. These establish **official source availability**, not that the artifacts in this package were produced from those sources. The Qt build system's SBOM feature is documented for Qt 6.8+; no SBOM matching this package's Qt/PySide Windows distribution was found in the repository or package.

## 5. License and copyright material mapping

| Source family | Published license basis relevant to source files | Existing repository materials | Source/notice status for this package |
|---|---|---|---|
| Qt modules/plugins | Qt 6.12.0 docs identify Core, Widgets and Svg as commercial or LGPLv3/GPLv2. Reviewed Gui, Network and Image Formats pages resolve to 6.12.1; QUIP 18 defines source-file expressions for LGPL-eligible versus GPL-only module/plugin files. Exact 6.12.0 files and terms require tag-level review. | `licenses/LGPL-3.0.txt`, `licenses/GPL-3.0.txt`, `licenses/third-party/qt/qt-lgpl.html`, `qt-licensing.html`, Qt notice/attribution material. | Qt's published notice identifies Qt Toolkit copyright © 2018 The Qt Company Ltd. and other contributors. Preserve matching source-file copyright headers, file-level license expressions, and `LICENSES/` texts; collect applicable LGPL/GPL copies and mapped third-party notices. The repository has core LGPL/GPL texts and vendor pages, but not the matching source tree, full copyright/file map, selected license basis, or recipient notice bundle. |
| PySide6 / Shiboken6 | Local metadata and PyPI say `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; Qt for Python overview describes LGPLv3/GPLv3 and commercial. | GPL/LGPL texts and Qt for Python licensing HTML/metadata evidence. | PySide/Shiboken source files have their own copyright headers and license expressions. Qt for Python's third-party page identifies copied Python buffer-interface code (`bufferprocs_py37.cpp/.h`) with Python Software Foundation license text and copied/adapted signature-support sources. Exact 6.12.0 files/notices need mapping. The repository has general vendor pages, not the source-file copyright set, complete source code or package-matched copied-source map. |
| PySide/Shiboken third-party/copied source | Qt for Python publishes third-party licenses and identifies code reused in libshiboken/signature support; exact code and file scopes must be followed to source revision. | `licenses/third-party/qt/INVENTORY.md`; general Qt for Python licensing page. | No exact 6.12.0 copied-source inventory, origin notices or match to the built outputs. |
| Qt third-party code | Component-specific licenses (e.g. FreeType alternatives, HarfBuzz, libpng, PCRE2/SLJIT, codecs, C++/WinRT and zlib-like code) independent of Qt's license. | Selected texts/attributions under `licenses/third-party/notices/`; `ATTRIBUTION-SOURCE-REGISTER.md`; `TRIMMED-PACKAGE-NOTICE-MAP.md`. | Partial evidence collection; not package-matched complete source/notices. FreeType election, codec versions/source and several mappings remain open. |
| Qt translation catalogs | QUIP 18 classifies usual `translations/*.ts` as `LicenseRef-Qt-Commercial OR BSD-3-Clause`; individual file headers/REUSE metadata and contributors may vary. | The QUIP and Qt licensing/evidence reports are cited; no complete per-catalog notice payload is present. | Preserve each matched `.ts` file's contributor copyright/source metadata and applicable BSD-3-Clause copyright, conditions and disclaimer; retain `lrelease` source/version/options for reproduction. 99 compiled catalogs are locally matched, but exact source catalogs/copyright mappings are not in the repository. |
| Microsoft VC runtime copies | Separate Microsoft terms and redistribution eligibility, not Qt/PySide LGPL source. | `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`. | Open; Qt written provenance/basis for wheel-copied runtime files and eligibility for each retained DLL required. |

The repository does **not** contain the corresponding Qt/PySide source code, a source archive, a complete Qt/PySide build directory, source patches or a matched SBOM. License texts and attribution HTML are not corresponding source. The local virtual environment has installed package binaries, metadata and RECORD, not the full source or original wheel archive.

## 6. Patch, modification and build-material status

### What can be said

- Qt DLLs and plugin DLLs that expose Windows file/product version resources report 6.12.0.0. Local PySide6/Shiboken distribution metadata reports 6.12.0.
- All 140 packaged PySide6/Shiboken tree files match the existing local site-packages files by SHA-256. Of those, 132 also match local `RECORD` SHA-256 entries; eight VC++ DLLs have no explicit matching RECORD entry.
- Therefore, for the 140-tree-file set, no byte changes between the local site-packages copy and the trimmed-package copy were observed. This says nothing about source patches applied when building the upstream/local wheel.

### What cannot be said

- No evidence establishes whether Qt or PySide source was patched before these binaries were built, whether upstream release source was modified, or whether vendor-specific build patches were applied.
- No exact PySide6/Shiboken wheel URL, downloaded archive hash, installer command/log, Qt binary distribution identifier, Qt compiler/configuration record, Qt SBOM, patch manifest, or release build attestation is present in the evidence inspected.
- No source-to-binary reproducible build or symbol-level proof has been performed. Version resources and local RECORD matches are not source provenance.
- The eight Qt-tree MSVC runtime DLL copies are not covered by the local RECORD hash evidence and have separate legal/provenance concerns.

### Build materials needed to correspond/modify

For a reproducible source package or a user modification path, retain and associate with the exact linked versions:

1. **Qt:** exact source archives/commits for qtbase, qtsvg, qtimageformats and other confirmed modules; source of each shipped plugin; configuration command and CMake cache/build options; patches and generated inputs; exact compiler/linker versions, Windows SDK, CRT selection, build tools; fetched/system/bundled dependency versions and their sources/licenses; and the exact SBOM/component list from the Windows build.
2. **Qt for Python:** exact `pyside-setup` v6.12.0 source archive/commit; PySide6 and Shiboken C++/Python source, generator/typesystem XML, copied/adapted code and notices; exact Qt headers/libraries/`qtpaths6` used; Python version/headers; CMake/Ninja and libclang versions; build options, module subset, patches, generated files, compiler/linker/SDK records and wheel packaging inputs.
3. **Translations:** exact `.ts` sources and per-file notices for each shipped `.qm`; Qt Linguist `lrelease` source/tool version and exact command/options; source catalog revision and any transformation/selection records.
4. **Dependencies:** source/configuration for statically incorporated Qt third-party code; OpenSSL source/build data for the separately shipped TLS dependency; exact CPython source/header/build data used by PySide extension modules; and MSVC DLL provenance/terms separately.
5. **Release mapping:** manifest linking each packaged file hash to its wheel/source archive, source repository path/commit, build job/configuration and applicable license/notice; records showing the precise Linked Version for each covered library. If §4(d)(0) is selected, also preserve the corresponding application code and usable relinking/recombination instructions/terms; this engineering report does not decide which LGPL route is legally sufficient.

Qt 6.12 Windows build documentation identifies a supported compiler/toolchain and build requirements. Current Qt 6.12 docs list CMake 3.25+, Python 3, Ninja as recommended, and Windows MSVC/SDK configurations. Qt for Python's build documentation lists Python 3.10+, Qt, CMake, Git and libclang, and describes its setup.py/CMake build process. These are general prerequisites, not the actual missing build record for the packaged wheel.

## 7. Source availability matrix

Status definitions:
- **Locally verified copy**: package bytes were directly checked against local site-packages and, where indicated, an installed RECORD hash. This is not upstream provenance.
- **Official source candidate**: official project/tag/archive for the displayed version exists, but has not been matched to package bytes/build.
- **Partial**: some identity/source/notice evidence exists, but exact source, patches, build materials or dependencies remain missing.
- **Not available in repository**: corresponding code/build materials are not present in this repository/package evidence collection.
- **Separate issue**: dependency has independent source/redistribution terms outside Qt/PySide source scope.

| Component set | Package identity evidence | Official corresponding-source candidate | Applicable license/copyright materials | Patches/build configuration/additional dependencies | Repository sufficiency / outstanding requirement |
|---|---|---|---|---|---|
| Qt Core, Gui, Network, Widgets DLLs | Qt 6.12.0.0 resource; local file hashes match installed `pyside6_essentials` RECORD. | qtbase v6.12.0 repo and official archive. | Qt module file licenses; Qt third-party components need file/build mapping. | Exact Windows wheel build config, patch set, source commit and SBOM missing; build requires toolchain, SDK and selected dependencies. | **Partial / not available in repository:** source candidate exists upstream, but no matched source or build evidence. |
| Qt Svg DLL | Qt 6.12.0.0 resource; local RECORD match. | qtsvg v6.12.0 repo/archive. | Qt source file terms and any dependencies. | Exact build/patch/source match missing. | **Partial / not available in repository.** |
| 20 Qt plugins | Qt 6.12.0.0 resources; local RECORD matches. | qtbase, qtsvg and qtimageformats 6.12.0 candidates by plugin family. | Qt file terms plus individual codecs/third-party notices. | Exact project/path, build flags, source snapshots, codec selections/patches and SBOM missing. | **Partial / not available in repository.** |
| Five PySide6 `.pyd` modules and `pyside6.abi3.dll` | Local `pyside6_essentials` 6.12.0 manifest; package bytes match RECORD. | pyside-setup v6.12.0 source archive/tag. | PySide license alternatives; copied/third-party source notices. | Qt headers/libs, Python, libclang, generator inputs/options and build attestations absent. | **Partial / not available in repository.** |
| Four embedded Python modules in PYZ (`PySide6`, `PySide6.support`, `PySide6.support.deprecated`, `shiboken6`) | Module names and code-object entries confirmed in executable archive; local installed source counterparts exist. | Same pyside-setup v6.12.0 candidate. | Source file headers/expressions and applicable copied-code notices need matching; archive code objects are not source. | Exact compiled source/options/patch mapping absent. | **Partial / not available in repository.** |
| Shiboken `Shiboken.pyd`, `shiboken6.abi3.dll` | Local `shiboken6` 6.12.0 manifest; package bytes match RECORD. | pyside-setup v6.12.0, Shiboken sources. | Shiboken licensing and copied/adapted third-party/Python code notices. | Exact source map, generator/toolchain inputs, build config/patches absent. | **Partial / not available in repository.** |
| 99 `.qm` translation files | All package/local files match; hashes recorded for catalog set in local essentials `RECORD`. | qttranslations v6.12.0; qttools/lrelease v6.12.0. | Usual `.ts` license category commercial OR BSD-3-Clause; per-file notices unresolved. | Source `.ts`, contributor mapping, lrelease binary version/options and conversion manifest absent. | **Partial / not available in repository.** |
| Qt/PySide statically embedded third-party code | Some package markers/attributions in existing audits; exact module mapping is mixed. | Sources are referenced in Qt release source/attribution/SBOM materials. | Applicable component-specific licenses; FreeType alternative unresolved, codec and component scope incomplete. | Exact source/component version, configuration, patches and Qt Windows SBOM absent. | **Partial / not available in repository as complete matching source.** |
| Eight MSVC DLLs under PySide/Shiboken | Package bytes equal local site-packages but no explicit matching RECORD hashes. | Microsoft runtime source/distribution materials, not Qt source. | Microsoft redistribution terms; separate from OSS license texts. | Qt written basis, binary origin/eligibility and installer payload mapping unresolved. | **Separate issue / insufficient**; see MSVC review. |
| OpenSSL DLLs used by `qopensslbackend` | Separate package binaries identified as OpenSSL 3.5.9 in existing audits. | OpenSSL 3.5.9 release/source archive candidate. | Apache-2.0 and applicable OpenSSL notices. | Exact CPython/wheel build provenance remains separate/open. | **Separate issue / partial**; see runtime audit. |
| Qt PDF/qpdf/PDFium and Mesa/LLVM | Explicit package path inventory says absent. | Historical source exists but not relevant to current artifact on available evidence. | Do not include their licensing rows for this package without new presence evidence. | Reassess if package changes. | **Not in package; excluded from current source scope.** |

## 8. Unresolved provenance questions

1. Which exact PySide6_Essentials and Shiboken6 wheel archives supplied the local site-packages files, where were they obtained, and what were their archive SHA-256 hashes/signatures?
2. Were the local site-packages copied from official Qt/PyPI wheels or created by another installation path? No installer/download log or original wheel archive was identified here.
3. What exact official Qt Windows distribution (archive, build ID, compiler, configuration, patches and third-party source map) supplied the 6.12.0 DLLs/plugins inside the PySide wheel?
4. Can Qt provide the Windows wheel's SBOM and source/build attestation, including statically linked dependencies and the eight redistributable DLLs?
5. What source commit and modified-source set built each Qt DLL/plugin and PySide/Shiboken extension? Do official release tags exactly match those files, or were vendor/local patches applied?
6. Which exact Qt source repositories produce each plugin path (especially qsvgicon/qsvg and image formats), and what codec revisions/options are embedded in qjpeg, qtiff and qwebp?
7. Which exact `.ts` files produced each `.qm`; what contributors/notices apply, and what Qt Linguist `lrelease` version/flags and transformations were used?
8. What PySide/Shiboken copied/adapted source files and per-file licenses are represented by the package extension modules, and what Python/Qt headers/generator inputs produced them?
9. Does Qt for Python's local 6.12.0 package manifest/license expression resolve to the intended license choice? The installed metadata does not record the distributor's election, and the published GPLv2 alternative remains a vendor-confirmation item in the existing inventory.
10. What is the provenance and redistribution basis of the eight unrecorded VC++ runtime DLL files under the PySide/Shiboken directories?
11. What complete source/build materials and recipient-facing method will be provided if the applicable license route requires source, relinking or a source offer? This report does not determine legal compliance or the final mechanism.

## 9. Prioritized recommendations

1. **Preserve and obtain provenance evidence first.** Locate the original Windows wheels/install logs or ask the Qt supplier for exact wheel names, hashes, signatures, build IDs, SBOMs, source commits and patch manifests. Do not infer this from the local version label.
2. **Obtain the vendor source/build record for Qt binaries.** Request Qt 6.12.0 Windows wheel component mapping for all five Qt DLLs and 20 plugin DLLs, including build configuration, compiler/SDK, bundled third-party sources, exact notices, SBOM and any modifications.
3. **Treat PySide and Shiboken as a separate source track.** Obtain the 6.12.0 source archive/tag mapping to wheel builds; request generated-code/typesystem, Shiboken/libshiboken copied-source and notice records, Python/Qt tool inputs, and build scripts/options.
4. **Resolve translation sources individually.** Match the 99 `.qm` files to upstream `.ts` catalogs, file-level copyright/license metadata and the exact `lrelease` version/options; keep the translation license path distinct from the Qt library license path.
5. **Close third-party and supporting dependencies.** Use matching Qt SBOMs/source records to resolve bundled codecs/static components. Close the MSVC runtime source/redistribution question and OpenSSL provenance through their separate reviews.
6. **Create a release-candidate source manifest only after matching.** For each shipped file record package path/hash, distribution/wheel and archive hash, repository path/commit, build job/configuration, modifications, dependency sources and license materials. Mark unresolved rows explicitly rather than treating a public source URL as fulfillment.
7. **Keep the release disposition on hold.** Qualified counsel should review the exact linked versions, source route, user notices, replacement/relinking mechanism and intended distribution model before release claims or assembly.

## 10. Official references consulted (retrieved/viewed 2026-11-09)

These establish upstream public availability and instructions, not package provenance.

### Qt source, tags and build materials

- Qt release source directory: <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/>.
- qtbase tag and archive: <https://github.com/qt/qtbase/tree/v6.12.0>; <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtbase-everywhere-src-6.12.0.tar.xz> (official mirrorlist advertises SHA-256 `a951bd163c7b80fc6b8c88d7668fb56abf91c152373e13c10666763238131307`).
- qtsvg tag and archive: <https://code.qt.io/cgit/qt/qtsvg.git/tag/?h=v6.12.0>; <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtsvg-everywhere-src-6.12.0.tar.xz> (advertised SHA-256 `e4ab39534ec97987b1b9b60ef7f4d3253d5912a69f8c713a01753174a4029331`).
- qtimageformats source project/archive: <https://github.com/qt/qtimageformats>; <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qtimageformats-everywhere-src-6.12.0.tar.xz> (advertised SHA-256 `0943132b5db8de6b6a7f1d162682173e8763c7ed94e80fd39113292845f67762`).
- qttranslations tag/archive: <https://invent.kde.org/qt/qt/qttranslations/-/tags/v6.12.0>; <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qttranslations-everywhere-src-6.12.0.tar.xz> (advertised SHA-256 `85929c0c30d6f273f23bd879bb69803ea17b010ab73cab2f8abf95357f6f6bbb`).
- qttools source/archive for Linguist tooling: <https://github.com/qt/qttools>; <https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/qttools-everywhere-src-6.12.0.tar.xz> (advertised SHA-256 `8dab8f3611496486a470ad5f115ceea584f36bc22a2b8b6f6ebdbafbb8160693`).
- Qt 6.12 Windows source-build prerequisites and supported compilers: <https://doc.qt.io/qt-6.12/windows-building.html>; configure options: <https://doc.qt.io/qt-6.12/configure-options.html>.
- Qt SBOM feature and generation: <https://doc.qt.io/qt-6.12/sbom.html>.
- Qt deployment/plugin paths: <https://doc.qt.io/qt-6.12/windows-deployment.html>; <https://doc.qt.io/qt-6.12/deployment-plugins.html>.
- Qt licensing and third-party code: <https://doc.qt.io/qt-6.12/licensing.html>; <https://doc.qt.io/qt-6.12/lgpl.html>; <https://doc.qt.io/qt-6.12/licenses-used-in-qt.html>.
- Qt source-file license classification including LGPL-eligible/GPL-only module and plugin expressions, statically linked files and translations: <https://contribute.qt-project.org/quips/18/>.
- Versioned module licensing pages: [Qt Core 6.12.0](https://doc.qt.io/qt-6.12/qtcore-index.html), [Qt Widgets 6.12.0](https://doc.qt.io/qt-6.12/qtwidgets-index.html), [Qt SVG 6.12.0](https://doc.qt.io/qt-6.12/qtsvg-index.html), [Qt Gui 6.12 documentation](https://doc.qt.io/qt-6.12/qtgui-index.html), [Qt Network 6.12 documentation](https://doc.qt.io/qt-6.12/qtnetwork-index.html), and [Qt Image Formats 6.12 documentation](https://doc.qt.io/qt-6.12/qtimageformats-index.html). The reviewed Gui, Network and Image Formats pages resolved to 6.12.1; they are later patch-level support only for this 6.12.0 package.

### Qt for Python / PySide6 / Shiboken

- PySide source tag and repository: <https://github.com/pyside/pyside-setup/tree/v6.12.0>; official tag page: <https://github.com/pyside/pyside-setup/tags> (release commit shown with prefix `f50facb`).
- Qt for Python source/build overview and Windows build requirements: <https://doc.qt.io/qtforpython-6/building_from_source/index.html>; <https://doc.qt.io/qtforpython-6/building_from_source/windows.html>. Windows instructions state MSVC must match the Qt library/Python/PySide build; OpenSSL is optional for SSL support, and libclang is a build input.
- Official source archive: <https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/pyside-setup-everywhere-src-6.12.0.tar.xz> (official mirrorlist advertises SHA-256 `099c1a597cf33c1b000e11cf68a0b82d216fb802bf81726efc720394f10c7751`).
- Versioned PySide and Shiboken package metadata: <https://pypi.org/project/PySide6/6.12.0/>; <https://pypi.org/project/shiboken6/6.12.0/>. These describe distributions but do not identify the local installed wheel origin.
- Qt for Python build requirements/process: <https://doc.qt.io/qtforpython-6/building_from_source/index.html>; PySide6 6.12.0 metadata/readme also points to this process and libclang requirements.
- Qt for Python project overview and Shiboken role: <https://doc.qt.io/qtforpython-6/>; third-party/copy notices: <https://doc.qt.io/qtforpython-6/licenses.html>.
- Qt for Python licensing statements: <https://doc.qt.io/qtforpython-6/commercial/index.html>; <https://doc.qt.io/qtforpython-6/overviews/qtdoc-lgpl.html>.

### Related repository evidence

- `QT-PYSIDE-LGPL-DISTRIBUTION-ASSESSMENT.md`
- `FINAL-LICENSING-AUDIT.md`
- `qt/INVENTORY.md` (historical 185-file inventory; do not treat as current package inventory)
- `ATTRIBUTION-SOURCE-REGISTER.md` (historical package scope explicitly stated in that file)
- `TRIMMED-PACKAGE-NOTICE-MAP.md`
- `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`
- `RUNTIME-LICENSING-EVIDENCE.md`
- `notices/MANIFEST.md`

## 11. Conclusion and change control

**Corresponding-source conclusion:** Official same-version source candidates are available upstream, and local package-to-installed-distribution equality is strongly supported for the 140 PySide6/Shiboken files (with 132 local RECORD hash matches). However, the Qt/PySide/Shiboken **source-to-binary provenance, exact build configuration/patch set, complete third-party scope, and corresponding-source delivery materials remain unverified**. The repository is not sufficient to claim that the exact corresponding source for this package has been established or made available.

**No compliance conclusion:** this register does not determine legal compliance, a license election, or whether the current distribution model satisfies any license. The final audit remains **HOLD / NOT CLEARED FOR DISTRIBUTION**.

This task was read-only except for creating this requested report. No source archive was downloaded or added; no code, packaging specification, notice, existing report, release artifact or verified package file was intentionally modified. No build, commit or push was performed. Existing worktree changes and release artifacts are to remain preserved.
