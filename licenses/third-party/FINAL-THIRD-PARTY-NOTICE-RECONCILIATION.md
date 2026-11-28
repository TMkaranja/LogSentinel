# Final Third-Party Notice Reconciliation — Verified Trimmed Windows Package

**Assessment date:** 2026-11-27  
**Package:** `dist/gui-ondir-trim-test/LogSentinel-GUI/`  
**Disposition:** **HOLD — NOT CLEARED FOR DISTRIBUTION.** This is a package-specific engineering evidence reconciliation, not legal advice, a legal opinion, a compliance determination, or release approval.

## 1. Executive summary

A read-only inventory and hash pass of the named trimmed onedir package confirms **182 regular files / 80,058,228 bytes** and executable SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`. The inventory contains Qt 6.12.0 libraries and 20 plugins, PySide6 and Shiboken6 bindings, 99 translation catalogs, CPython 3.14.10 runtime/standard-library code and native extensions, OpenSSL 3.5.9, SQLite 3.50.4, PyInstaller 6.22.3 runtime/bootloader code, and 10 Microsoft VC++ runtime DLLs. The three previously identified removals—Qt PDF, qpdf, and Mesa software OpenGL—are absent. The package itself contains **no** `.txt`, `.md`, or `.rst` license/notice files.

The existing notice collection is a useful research set, not an end-user notice bundle. Hash review found **34 manifest-listed files with recorded sizes and hashes, all matching**. The notices directory has **35 files total** when `MANIFEST.md` is counted; the manifest does not contain its own size/hash row, so its own integrity cannot be described as verified against a recorded value. It was readable during this review. The collection includes useful versioned or source-attributed materials, but many are candidates, alternatives, internal notes, or attribution pages—not validated notices for these exact binaries.

Principal reconciliation findings:

- **Available and useful, but not release-ready:** CPython PSF license and attribution material, Unicode License V3 and UCD readme, OpenSSL Apache-2.0 text and acknowledgements, PyInstaller's combined `COPYING.txt`, bzip2 license, mpdecimal copyright/license terms, Zstandard's two alternative licenses, FreeType's two alternative texts, HarfBuzz `COPYING`, libpng license, libjpeg-turbo license and `README.ijg`, PCRE2 license and Qt attribution pages, C++/WinRT MIT text, and SQLite public-domain statement.
- **Important missing notice/source items:** no validated Qt/PySide/Shiboken recipient notice bundle; no exact mapped Qt source/component SBOM; no elected FreeType or Zstandard branch; no exact zlib-compatible or liblzma/XZ source/license mapping; no version-matched libtiff/libwebp license and patent materials; no per-catalog attribution map for 99 `.qm` files; no package-delivered notices or GPL/LGPL license texts; and no completed Qt/PySide corresponding-source/relinking or replacement route.
- **Historical scope must not be mistaken for current scope:** `ATTRIBUTION-SOURCE-REGISTER.md`, `OTHER-COMPONENTS-INVENTORY.md`, `qt/INVENTORY.md`, `notices/README.md`, and the notice manifest declare an older **185-file** baseline. Their evidence is contextual only unless reconciled to this 182-file package. In particular, Qt PDF/PDFium and Mesa/LLVM notice materials relate to components removed from this package and are not automatically applicable.
- **Correction:** the eight nested VC++ DLLs are present in the hash-matched Qt Essentials/Shiboken wheel payloads and match their wheel `RECORD` hashes, notwithstanding old case-sensitive “absent” statements. This proves wheel-content delivery, not Microsoft source identity or redistribution authorization.
- **Separate runtime risk:** the package also has two root VC++ 14.51 files with Microsoft signatures and eight nested 14.44 files with Qt signatures. Redistribution eligibility, exact source chain, applicable Microsoft terms and servicing model remain open.

No legal clearance or compliance conclusion is made. Distribution remains on hold pending rights-holder evidence, qualified legal review, corrected component/notice mapping, a selected applicable source/replacement route where required, and validation of a specifically authorized final package.

## 2. Package identity and method

### 2.1 Direct package facts

| Check | Observed result |
|---|---|
| Regular files / total bytes | **182 / 80,058,228** |
| Top-level layout | One root file (`LogSentinel-GUI.exe`); 181 files below `_internal/` |
| Executable | 2,386,859 bytes; SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01` |
| File-type counts | 42 DLL, 16 PYD, 99 QM, 22 SVG, 1 ZIP, 1 ICO, 1 EXE |
| Notice-text suffixes in package | No `.txt`, `.md`, or `.rst` files |
| Excluded payloads | `_internal/PySide6/Qt6Pdf.dll`, `_internal/PySide6/plugins/imageformats/qpdf.dll`, `_internal/PySide6/opengl32sw.dll` absent |
| Hashing | All 182 files were read and SHA-256 hashed during this reconciliation; key runtime/package hashes are repeated below and in the cited prior evidence. No package file was written. |

The **22 SVG files and one ICO** are project GUI assets under `_internal/logsentinel/gui/assets/`. The SVGs are local resources and a read-only scan found no external `http(s)` or protocol-relative image/source references. They are not identified as third-party code by the inspected evidence. 

### 2.2 Read-only method and evidence limits

Methods: recursively enumerated and hashed the package; counted file types and directory groupings; opened `base_library.zip` for its entry list; used the installed PyInstaller archive-viewer module to list the frozen executable's CArchive/PYZ names; compared the resulting paths and facts with the requested reports; parsed `notices/MANIFEST.md` size/hash rows and recomputed each file; and recorded pre-write worktree and release-baseline state. No downloads, archive extraction, installer execution, package replacement, rebuild, notice edit, source edit, spec edit, commit or push occurred.

A package binary marker, installed wheel `RECORD`, version resource, valid signature, vendor attribution page or matching wheel archive has a specific evidentiary scope. These do not alone prove a binary's source revision, license election, complete notice scope, rights chain or legal sufficiency. Components not loaded at runtime are still included in the distributed artifact. The inventory is based on actual present paths plus the existing binary/component evidence—not solely on historical inventories.

## 3. Complete shipped-component inventory

### 3.1 Qt, PySide6, Shiboken6 and translations

- **Qt shared libraries (5):** `PySide6/Qt6Core.dll`, `Qt6Gui.dll`, `Qt6Network.dll`, `Qt6Svg.dll`, `Qt6Widgets.dll` (Qt file-version resources 6.12.0.0).
- **Qt plugins (20):** `plugins/generic/qtuiotouchplugin.dll`; `plugins/iconengines/qsvgicon.dll`; nine image-format plugins `qgif.dll`, `qicns.dll`, `qico.dll`, `qjpeg.dll`, `qsvg.dll`, `qtga.dll`, `qtiff.dll`, `qwbmp.dll`, `qwebp.dll`; `plugins/networkinformation/qnetworklistmanager.dll`; four platform plugins `qdirect2d.dll`, `qminimal.dll`, `qoffscreen.dll`, `qwindows.dll`; `plugins/styles/qmodernwindowsstyle.dll`; and three TLS plugins `qcertonlybackend.dll`, `qopensslbackend.dll`, `qschannelbackend.dll`.
- **PySide6 native files (6):** `QtCore.pyd`, `QtGui.pyd`, `QtNetwork.pyd`, `QtSvg.pyd`, `QtWidgets.pyd`, `pyside6.abi3.dll`.
- **Shiboken native files (2):** `shiboken6/Shiboken.pyd`, `shiboken6/shiboken6.abi3.dll`.
- **Qt translations (99):** files under `PySide6/translations/`; the source report groups them as 37 `qt_*.qm` excluding help, 29 `qt_help_*.qm`, and 33 `qtbase_*.qm`. All are present; `.qm` → `.ts` source/contributor/license mapping is open.
- **Nested VC++ DLLs (8):** five under `PySide6/` and three under `shiboken6/`; all are in the Qt wheel payloads and match wheel `RECORD` per `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`.

**Qt/PySide/Shiboken binary identity evidence:** the Qt DLLs/plugins report Qt 6.12.0 resources and Qt Company Authenticode signatures; cached Qt PySide6 Essentials and Shiboken6 wheels match official published size/SHA-256 values. All 140 files in the PySide6/Shiboken6 package trees, including the eight nested VC++ files, match the appropriate wheel entry and `RECORD`. Wheel identity is not a source/build attestation or legal election. Exact source/build provenance and written Qt license scope remain unverified.

### 3.2 CPython, standard library and other Python code

- **CPython runtime DLLs:** `_internal/python314.dll` (reported Python 3.14.10) and `_internal/python3.dll`.
- **Embedded standard library:** `_internal/base_library.zip` (155 entries, primarily Python standard-library modules); the frozen executable PYZ additionally contains standard-library modules. PyInstaller archive inspection confirmed module names including `bz2`, `compression.zstd`, `hashlib`, `lzma`, `sqlite3`, `ssl`, plus many standard-library modules, and the LogSentinel application modules.
- **CPython extension modules (10):** `_bz2.pyd`, `_decimal.pyd`, `_hashlib.pyd`, `_lzma.pyd`, `_socket.pyd`, `_sqlite3.pyd`, `_ssl.pyd`, `_zstd.pyd`, `select.pyd`, `unicodedata.pyd`.
- **Application code/resources:** frozen LogSentinel modules and 23 project-owned GUI assets (22 SVG icons/brand graphics plus `logsentinel.ico`); these are not identified as third-party components in the evidence reviewed. No external resource links were found in the SVGs.
- **Other bundled Python packages:** PySide6 and Shiboken6 are listed above; PyInstaller runtime code is listed below. No other separately identified third-party Python distribution payload was found in the current package inventory.

The Python license bundle is not a universal license for every extension's embedded library. bzip2, Zstandard, Unicode data, OpenSSL, SQLite, mpdecimal and liblzma need their own rows below. No `_ctypes.pyd`/libffi, Tcl/Tk, or expat payload is evidenced in the current package. Host Windows libraries are not bundled redistributable files; ICU was reported as a host-resolved Qt dependency in prior observations, not as a package file. The actual minimum-Windows/host dependency should be verified separately. The existing `.venv-build-gui` license file is 35,407 bytes / 676 lines and contains a “Microsoft Distributable Code” section; the collected `notices/cpython/LICENSE.txt` is a different 13,804-byte / 277-line upstream text and does not contain that section. The exact applicable Python-distribution terms, affected files and redistribution conditions therefore require a file/build-specific review; do not treat the collected PSF text as resolving this separate Microsoft issue.

### 3.3 Other native files

- **OpenSSL:** `_internal/libcrypto-3.dll` (6,021,880 bytes; SHA-256 `75495fe0e079ab00d49be740d3c710a0b94e3f74f9648cb7cc9f768fc7f52319`) and `_internal/libssl-3.dll` (1,308,920 bytes; SHA-256 `8957182a9c385bfd9f3f790921de2ddc614cf91f99edbed4e9e5446a46504e32`); `libcrypto` reports OpenSSL 3.5.9. The DLLs match local CPython copies; exact source/build matching remains unverified.
- **SQLite:** `_internal/sqlite3.dll` and `_internal/_sqlite3.pyd`; version/source-ID evidence reports SQLite 3.50.4.
- **PyInstaller:** the frozen executable CArchive directly lists `struct`, `pyimod01_archive`, `pyimod02_importers`, `pyimod03_ctypes`, `pyimod04_pywin32`, `pyiboot01_bootstrap`, runtime hooks `pyi_rth_inspect` and `pyi_rth_pyside6`, and `PYZ.pyz`. The PYZ contains `_pyi_rth_utils` and `_pyi_rth_utils.qt`, PySide6/Shiboken helper modules, standard library and application modules. Build/environment evidence identifies PyInstaller 6.22.3. `COPYING.txt` is available locally and documents distinct GPL/Bootloader Exception and Apache-2.0 scopes. Bootloader modification status is not resolved; there is a four-byte `.rdata` difference against the local `runw.exe` reference in prior evidence.
- **Microsoft VC++ runtime (10 DLLs):** 2 root files (`VCRUNTIME140.dll`, `VCRUNTIME140_1.dll`, version 14.51.36247.0, Microsoft-signed); 5 files under `PySide6/` and 3 under `shiboken6/` (14.44.35211.0, Qt-signed). Hashes and source limits are in `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md` and `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md`. Exact Microsoft source payload and redistribution eligibility for the Qt-signed files, as well as the root copies' rights chain, remain open.

No Qt PDF, qpdf/PDFium, Mesa/LLVM software-renderer binary, or other separate Qt third-party DLL was found beyond the inventory above. Third-party code statically incorporated into Qt DLLs/plugins remains in scope where binary markers and Qt attributions support it.

## 4. Component-to-license and notice reconciliation matrix

**Status labels:** **Verified and present** means an applicable candidate text/notice is in the local collection and directly relevant version/source evidence is comparatively strong; it does not mean release sufficiency. **Present but provenance unverified** means a candidate exists but exact shipped-source linkage is open. **Incomplete** means material is absent, alternatives are unresolved, or mapping is partial. **Missing** means no applicable candidate text/notice has been collected in the inspected set. **Not applicable** is limited to items not found in this artifact or public-domain/host-supplied scope with explanation. **Requires legal review** identifies a legal/rights or scope question, not a finding of breach.

| Shipped component / paths | Candidate license and attribution | Existing local material and integrity status | Reconciliation status; exact closure evidence |
|---|---|---|---|
| Qt Core, Gui, Network, Svg, Widgets; PySide6 native bindings; Shiboken6 native bindings and frozen helper modules | Qt/PySide/Shiboken license alternatives are not binary-specifically elected. Public Qt pages describe LGPLv3/GPLv3 and commercial paths; wheel metadata reports `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`, leaving GPLv2 discrepancy unresolved. Qt notice identifies Qt Toolkit copyright © 2018 The Qt Company Ltd. and other contributors. Shiboken-specific copied/adapted source may have its own notices. | `licenses/LGPL-3.0.txt`, `licenses/GPL-3.0.txt`, `qt/qt-lgpl.html`, `qt/qt-licensing.html`, `qt/qtforpython-commercial.html`, and `qt/LicenseRef-Qt-Commercial.txt` exist. These are outside `notices/`; the HTML pages are vendor documentation, and the 470-byte `LicenseRef` is a commercial pointer, not an LGPL/GPL election. No user bundle is in package. | **Incomplete; requires legal review.** Obtain written Qt scope/election for exact wheel hashes and components; validate Qt/PySide/Shiboken notice/copyright set. If LGPLv3 applies and is conveyed, prepare appropriate prominent notice and GPL/LGPL texts and select a §4(d) route; establish whether §4(c) applies and review §4(e) trigger. Resolve any commercial agreement claims. |
| Qt plugins (20), including image/codecs, SVG, platform, network, TLS and style | Plugin-specific Qt license/file terms, plus separately licensed statically linked code where present. Qt release/source attributions are leads; each component has to match actual build. | Qt vendor HTML and `notices` component materials below; no per-plugin source file manifest/SBOM. | **Incomplete; requires legal review.** Obtain wheel-scoped SBOM and per-plugin source/build/copyright map; ensure no GPL-only/source-file exception or independent code is overlooked. Distributed plugins count even if not loaded in the observed test. |
| 99 Qt `.qm` translations | Separate translation scope; usual Qt `.ts` sources are classified in QUIP 18 as `LicenseRef-Qt-Commercial OR BSD-3-Clause`; individual catalogs can differ. | No translation-specific notice in `notices/`; general Qt docs and QUIP citations in LGPL report. | **Missing / upstream verification required.** Map each catalog to `.ts`, copyright/contributor/file-license metadata and `lrelease` inputs. Add only matched per-catalog notices and relevant BSD text; do not label all `.qm` files LGPL libraries by default. |
| CPython runtime, standard library and frozen standard modules | Python Software Foundation License v2; PSF notice “Copyright (c) 2001 Python Software Foundation; All Rights Reserved”; incorporated libraries have independent terms. | `notices/cpython/LICENSE.txt` (13,804 B), full `README.rst` (8,897 B), and copyright excerpt (821 B); all hash/size rows pass. The `LICENSE.txt` copy contains PSF terms/notice. The excerpt is not the complete license. | **Present but provenance unverified; incomplete for embedded-code mapping.** Version evidence is Python 3.14.10; exact Windows source/build hash not matched. Map separately licensed embedded libraries. The existing local interpreter license (35,407 B / 676 lines) contains “Microsoft Distributable Code,” while the collected upstream `LICENSE.txt` (13,804 B / 277 lines) does not and is not byte-identical. Obtain and assess the exact interpreter distribution terms, identify whether any included package file falls within that section, and have counsel review any Microsoft conditions. |
| Unicode Character Database in `unicodedata.pyd` | Unicode License V3; retain Unicode copyright/permission notice in copies or associated documentation. | `notices/unicode/UNICODE-LICENSE-V3.txt` (1,995 B) and `UCD-16.0.0-ReadMe.txt` (693 B); both pass manifest hash/size checks. | **Present but provenance unverified.** Package reports UCD 16.0.0, but exact CPython build inputs are not matched. Tie UCD files and license version to the shipped extension. |
| OpenSSL 3.5.9, `libcrypto-3.dll` / `libssl-3.dll` | Apache License 2.0; per-file copyright/attribution and modification notices where applicable. Apache §4(d) NOTICE handling is conditional on the Work including a NOTICE text file. | `notices/openssl/LICENSE-APACHE-2.0.txt` and `TAG-ACKNOWLEDGEMENTS.md` pass hashes; `NOTICE-STATUS.md` is a local note, not upstream notice. Prior release archive review found `ACKNOWLEDGEMENTS.md` but no file named `NOTICE` in the inspected 3.5.9 archive. | **Present but provenance unverified.** Binary version and CPython-copy equality support identity, not exact source build. No upstream NOTICE was identified in that archive; do not invent one or rename acknowledgements. Obtain exact CPython/OpenSSL build/source record and confirm applicable Apache obligations; if a source build includes NOTICE text, reproduce its relevant notices. |
| SQLite (`sqlite3.dll`, `_sqlite3.pyd`) | SQLite deliverable code is dedicated to public domain; no OSS license text requirement for the code is identified. Courtesy attribution is optional, not a required license notice. | `notices/sqlite/copyright.html` hash/size pass; it is a public-domain statement, not a license. | **Not applicable to mandatory license notice on available evidence; courtesy material present.** Version 3.50.4 evidence is recorded; exact source hash/build mapping remains unverified. Do not call the courtesy HTML a required license. |
| bzip2 1.0.8 in `_bz2.pyd` | bzip2 1.0.8 license and copyright of Julian R. Seward; preserve terms/disclaimer and applicable source-origin/altered-source/no-endorsement conditions. | `notices/bzip2/LICENSE.txt` passes manifest hash/size. | **Present but provenance unverified.** Version marker supports 1.0.8; exact CPython source/patch link remains open. Match exact CPython build and include the full applicable text in future notices if counsel confirms conveyance requirements. |
| Zstandard 1.5.7 in `_zstd.pyd`, `compression.zstd` | BSD-style license **or** GPLv2 at upstream option; alternatives are mutually exclusive. BSD option has copyright/conditions/disclaimer/no-endorsement terms. | `notices/zstandard/alternatives/BSD-LICENSE.txt`, `GPLv2-COPYING.txt`, local alternatives `README.md`; all manifest-listed hashes pass. Neither election is documented. | **Incomplete; requires legal review.** Determine actual license election for CPython's embedded copy from build/vendor evidence and distributor rights. Include only elected license and relevant notices; do not ship/describe both as cumulative or silently pick BSD. |
| mpdecimal 4.0.0 in `_decimal.pyd` | Simplified BSD-style terms; copyright Stefan Krah, 2008–2024; accompanying `COPYRIGHT.txt` contains terms/disclaimer. | `notices/mpdecimal/COPYRIGHT.txt` passes manifest hash/size; extracted from source archive with checksum evidence in manifest. | **Present but provenance unverified.** Reported build path points to 4.0.0; exact embedded source/patch hash is open. Tie the file to the CPython build before final notice decision. |
| liblzma/XZ-derived code in `_lzma.pyd` | Exact liblzma version/license vintage unknown; modern 0BSD cannot be presumed for unidentified snapshot; distinguish library from unrelated XZ tools. | **No version-matched liblzma/XZ license or notice** in collection. | **Missing; upstream verification required.** Obtain CPython source/build and exact embedded liblzma revision/file license. Do not apply GPL/LGPL for unrelated XZ tools or assume 0BSD. |
| zlib-compatible code in `python314.dll` and Qt Core | CPython marker `zlib-ng`/`1.3.1` may be compatibility metadata; Qt Core shows zlib-like code but implementation identity (zlib/zlib-ng/other) and exact versions are open. | `notices/zlib-ng/LICENSE.md` is zlib-ng 2.2.4 candidate only; manifest hash passes. No exact zlib license/source map. | **Incomplete / candidate only.** Obtain CPython and Qt build manifests, actual source version, copyright and license. Do not apply the 2.2.4 candidate based on strings. Consider each separate copy independently. |
| FreeType embedded in Qt Gui | FreeType Project License (FTL) **or** GPLv2; mutually exclusive. FTL has project-attribution requirement; exact source/election unverified. | `notices/freetype/LICENSE.TXT`, `alternatives/FTL.TXT`, `alternatives/GPLv2.TXT`, local `alternatives/README.md`, and Qt attribution HTML; all manifest-listed hashes pass. Neither branch is elected. | **Incomplete; requires legal review.** Obtain Qt wheel/build file-level source and license-election confirmation. If FTL, use the exact FTL-required attribution; if GPLv2, assess resulting distribution obligations. Do not choose based on convenience. |
| HarfBuzz embedded in Qt Gui | Old MIT license for cited HarfBuzz source, subject to file-level exceptions/subdirectories; multiple authors/copyright ranges. | `notices/harfbuzz/COPYING.txt` and Qt attribution HTML pass manifest hash/size. | **Present but provenance unverified.** Exact embedded 14.5.0 files/patches and per-file terms need Qt SBOM/source mapping. Keep complete applicable source copyright attribution rather than inventing one line. |
| libpng 1.6.58 embedded in Qt Gui | PNG Reference Library License v2; notice includes PNG Reference Library Authors and other copyright holders. | `notices/libpng/LICENSE.txt` passes; Qt binary marker/version recorded. | **Present but provenance unverified.** Version evidence is strong but source/build exactness is open. Confirm linked snapshot and preserve complete notice. |
| PCRE2 and possible SLJIT in Qt Core | PCRE2 BSD-3-Clause with PCRE2 exception; SLJIT/JIT is separately BSD-2-Clause if present. | `notices/pcre2/LICENCE.md` and two Qt attribution HTML files pass hashes. | **Incomplete.** Match exact PCRE2 version, JIT/SLJIT inclusion and files to Qt build. Ensure both the PCRE2 exception and distinct SLJIT notice are handled where applicable. |
| libjpeg-turbo in qjpeg and qtiff plugins | Version marker 3.2.0. IJG notice applies to libjpeg API; Modified BSD has narrower API/program scope per upstream guide. Product documentation needs the IJG statement for binary distribution; do not apply BSD license indiscriminately without API/source map. | `notices/libjpeg-turbo/LICENSE.md` and `README.ijg` pass hashes; they are source texts, not integrated product documentation. | **Incomplete; provenance/API scope open.** Qt plugin mappings must establish actual code/API composition and applicable notices. Confirm future recipient materials include required IJG statement and any applicable BSD text. |
| libtiff in qtiff plugin | libtiff BSD-like terms and any snapshot-specific third-party notices; observed string only establishes a lower-bound clue ("Since 4.5.1"), not exact version. | **No libtiff-specific license/notice** in current collection. | **Missing; upstream verification required.** Obtain exact Qt plugin source snapshot/SBOM and collect applicable versioned license plus dependencies/notices. Do not use Qt 6.12.1 attribution as proof of this 6.12.0 plugin. |
| libwebp in qwebp plugin | BSD-3-Clause and separate upstream patent grant candidate; exact source/version and patent scope unresolved. | **No libwebp COPYING/BSD notice or patent file** in collection. | **Missing; upstream verification and legal review required.** Obtain exact Qt plugin SBOM/source revision and relevant license/patent material. Do not substitute later patch-level Qt attribution. |
| C++/WinRT 2.0.250303.1 in Qt Core | MIT license; Microsoft copyright/permission notice. | `notices/cppwinrt/LICENSE.txt` passes manifest hash/size. | **Present but provenance unverified.** Embedded version marker matches the collected upstream version; verify source/patch mapping and include the full MIT text if confirmed in the delivered component. |
| Qt image formats and other plugin-specific code | Qt plugin source-file terms plus any embedded libraries, as identified by actual build. `qgif`, qicns, ico, TGA, WBMP, SVG and plugins may have distinct source terms; not all are separate third-party projects. | Qt licensing docs and partial component notices; no complete per-plugin source/attribution matrix. | **Incomplete; upstream verification required.** Qt-supplied per-plugin SBOM/source/file-license manifest needed. Do not infer every plugin has an identical license from the module DLL. |
| PyInstaller bootloader + loader/bootstrap entries | GPL-2.0-or-later with Bootloader Exception for bootloader/`PyInstaller/loader` material; exception does not erase all GPL conditions. | `notices/pyinstaller/COPYING.txt` (32,604 B) passes hash/size and contains GPL/exception/Apache texts. CArchive entries directly verified. | **Present but provenance/modification status unverified; requires legal review.** Map entries to exact PyInstaller 6.22.3 paths, investigate 4-byte `.rdata` difference, and determine source/modified status and any GPL/source conditions. Do not claim unmodified bootloader. |
| PyInstaller runtime hooks and `_pyi_rth_utils` | Apache-2.0, distinct from bootloader exception. | Same combined `COPYING.txt` contains Apache license and distinguishes runtime hooks/modules. CArchive/PYZ names verified. | **Present but provenance unverified.** Map exact hook/module source and retain Apache terms/notices; don't label these as covered by the bootloader exception. Build-time `hook-PySide6.QtSvg.py` is not shown as shipped runtime code. |
| Two root Microsoft VC++ 14.51 DLLs | Microsoft runtime/distributable terms; exact source/eligibility and distributor's license basis need review. | No Microsoft terms or rights documents in notice collection; package files are Microsoft-signed and match local CPython/System32 copies per prior report. | **Missing; requires legal review.** Establish exact origin, applicable EULA/license eligibility, permitted form and servicing model. A signature/version is not redistribution authority. |
| Eight Qt-signed nested VC++ 14.44 DLLs | Microsoft runtime rights/terms apply independently of Qt OSS licenses; Qt wheel provenance is established, Microsoft lineage/Qt supplier authorization/downstream eligibility are not. | No Microsoft terms/rights evidence in notice collection. All eight match digest-verified Qt wheel entries and wheel `RECORD`; five Essentials, three Shiboken. | **Missing; requires Qt and legal review.** Obtain written Qt sourcing/rights basis for exact hashes and counsel's review of applicable Microsoft terms. Do not infer permission from Qt signing or wheel inclusion. |
| ICU, Windows SChannel, UCRT/system libraries | Host OS components reported in runtime evidence; not bundled as package DLLs. `qschannelbackend.dll` is a Qt plugin; Windows system APIs and certificate store are not separately copied. | No host component license notice in package collection. | **Not applicable as bundled third-party notice on available evidence.** Record host dependencies/platform requirements separately; validate clean Windows targets. Reassess if ICU or other OS DLLs are bundled later. |
| Qt PDF / PDFium / qpdf; Mesa llvmpipe / LLVM; Pixman; Qt PDF transitive code | Not present in current package: exact Qt PDF/qpdf/Mesa paths absent; previous markers absent. Older 185-file register statements concern another artifact. | Related historical files: `notices/mesa-llvm/LLVM-3.6.2-LICENSE.TXT`, two Qt attribution pages; Qt PDF HTML is under `qt/`, not the notices folder. | **Not applicable to this package on present path/hash evidence.** Do not include these materials automatically. Re-inventory if the modules/renderers are restored; don't infer PDF transitive code from historical inventory alone. |
| TinyCBOR, MD4C, double-conversion, libpsl/PSL, Brotli code | Presence not established by evidence inspected; isolated strings/provider names are not proof. | No specific notice should be selected based on this evidence. | **Not applicable as an asserted shipped component; presence remains uncertain.** Request Qt SBOM/source mapping if relevant; don't include speculative attributions as established facts. |
| GUI SVG/icon resources and application modules | Project-owned by current source inventory; no upstream third-party markers/references observed. | No third-party notice identified. | **Not applicable as third-party notice on evidence reviewed.** Confirm project copyright/licensing separately; no claim about third-party font or build assets beyond inspected package paths. |

## 5. Notice collection integrity and applicability

### 5.1 Hash and size verification result

`notices/MANIFEST.md` contains 34 asset rows with a path, byte count and SHA-256. All 34 recomputed hashes and sizes match. The directory contains 35 files total including `MANIFEST.md`; the manifest itself has no self-entry, so there is **no recorded expected hash/size for the 35th file**. Its observed size is 13,184 bytes and SHA-256 is `28951f87cb012f372ef30972c32adf0bafbf57f5443de96ac523906c3f0660b3`, but no earlier expected value exists for comparison. Therefore the evidence-supported statement is **34/34 manifest rows pass; the manifest was fingerprinted but not baseline-verified**, not “35 of 35 manifest hashes passed.” No missing or extra file was found among the 34 listed assets.

The manifest's rows comprise upstream notices/attributions and local notes. Not every listed file is applicable to the current 182-file package, and hash integrity proves only that the local files match the manifest—not that their license/source/version applies to a shipped binary.

### 5.2 Applicability classes

**Potentially applicable; only after exact version/source/legal checks:**

- CPython: `cpython/LICENSE.txt`, `cpython/README.rst`, and `cpython/COPYRIGHT-AND-ATTRIBUTION.txt`.
- Unicode: `unicode/UNICODE-LICENSE-V3.txt`, `unicode/UCD-16.0.0-ReadMe.txt`.
- OpenSSL: `openssl/LICENSE-APACHE-2.0.txt`, `openssl/TAG-ACKNOWLEDGEMENTS.md`; `NOTICE-STATUS.md` is internal context, not upstream notice text.
- PyInstaller: `pyinstaller/COPYING.txt` (contains distinct GPL/Bootloader Exception and Apache sections).
- bzip2: `bzip2/LICENSE.txt`.
- mpdecimal: `mpdecimal/COPYRIGHT.txt`.
- Zstandard: both files under `zstandard/alternatives/`; one is selected only after upstream/election confirmation.
- FreeType: overview, FTL, GPLv2 alternatives, Qt attribution page; not an election.
- HarfBuzz: `COPYING.txt` and Qt attribution HTML.
- libpng: `LICENSE.txt`.
- libjpeg-turbo: `LICENSE.md`, `README.ijg`.
- PCRE2/SLJIT: `LICENCE.md` and two Qt attribution HTML pages.
- C++/WinRT: `LICENSE.txt`.
- SQLite: courtesy public-domain page; no license text required on the reported public-domain basis.

**Historical/removed component material—do not include automatically:**

- `mesa-llvm/LLVM-3.6.2-LICENSE.TXT`, `qt-attribution-llvm.html`, and `qt-attribution-llvmpipe.html` concern `opengl32sw.dll`, absent from the current package.
- `qt/qtpdf-licensing.html` and any PDFium chain belong to Qt PDF, `qpdf.dll`, absent from the current package.
- `qt/INVENTORY.md`, older `ATTRIBUTION-SOURCE-REGISTER.md`, `OTHER-COMPONENTS-INVENTORY.md`, `notices/README.md` and manifest front matter explicitly describe the older 185-file build; do not use that older inventory to assert current presence or quantity.

**Candidate or internal-only content:**

- `zlib-ng/LICENSE.md` is a 2.2.4 candidate, not established for either Qt Core or CPython code.
- `openssl/NOTICE-STATUS.md` and both alternative README files are local working notes; they are not substitute upstream notices and should not be shipped as though they were.
- Qt attribution HTML proves only what the cited vendor page says, not a package-matched binary attribution.

### 5.3 Other license documents outside `notices/`

`licenses/LGPL-3.0.txt` and `licenses/GPL-3.0.txt` exist at repository level; neither is part of the package. Under an LGPLv3 Combined Work path, LGPLv3 §4(b) calls for GPL and LGPL text copies; exact applicability and final delivery must be reviewed by counsel. The Qt HTML pages under `licenses/third-party/qt/` are vendor documentation; they are not automatically end-user notice documents or binary-specific elections. `LicenseRef-Qt-Commercial.txt` is a commercial terms pointer, not evidence of a commercial license held. No Microsoft VC++ runtime license/EULA text or Qt rights statement is in the notice collection.

## 6. Missing, incomplete, potentially unnecessary, and ambiguous findings

### Missing or incomplete

1. **Qt/PySide/Shiboken end-user set:** exact applicable license/election, per-component copyright/attribution map, Qt use notice, appropriate license texts, and recipient source/replacement instructions are not present in the package or a reviewed release bundle. The three repository-level Qt HTML/vendor files do not close these items.
2. **LGPL route and corresponding source:** neither §4(d)(0) source/relink route nor §4(d)(1) suitable shared-library mechanism is demonstrated for this package. The onedir layout alone and prior tests on another arrangement are insufficient. No exact package-controlled replacement test or matching source/application-code relink package is available. §4(e) remains a fact-dependent question for counsel.
3. **Translations:** source, per-file contributor/copyright/license mapping and generation details for all 99 `.qm` files are missing. Usual `.ts` classifications should not be casually assigned to compiled `.qm` files without mapping.
4. **Qt third-party map:** no package-matched Qt wheel SBOM, source-build attestation or full plugin/static-component map. FreeType election, HarfBuzz per-file terms, PCRE2/SLJIT objects, codec composition, zlib identity and source versions remain open.
5. **Missing standalone texts:** no version-matched liblzma/XZ license, libtiff notice, libwebp BSD/patent material, or confirmed Qt zlib notice is present. No exact-source-required BSD-3 notice for translations is mapped.
6. **CPython's embedded components:** bzip2/Unicode/Zstandard/mpdecimal have candidate materials, but exact build correspondence is partial. zlib-compatible code and liblzma remain unresolved. The CPython 3.14.10 license copy is versioned but not tied to the exact Windows build; the separate Microsoft Distributable Code clause found in the local Python installation's license needs exact applicability/provenance analysis and is not shown in the collected notice `LICENSE.txt`.
7. **VC++ runtime:** no Microsoft terms, Qt's rights/sourcing confirmation, or distributor eligibility record in notice collection. Eight nested DLLs are wheel-matched, but their precise Microsoft source/authorization is not.
8. **PyInstaller:** a useful combined `COPYING.txt` exists, but source-path mapping and bootloader modification status are incomplete. The four-byte `.rdata` difference is unexplained; do not claim pristine/unmodified bootloader. The collection does not include a separate full GPL-2.0 license text (the combined file states the terms and exception but is not the GPL text); determine with counsel the applicable license-text/source duties and prepare the correct text if required.
9. **OpenSSL:** the Apache-2.0 text and acknowledgements are available, but exact CPython build/source correspondence is unverified. Prior archive inspection found no `NOTICE` file in the inspected OpenSSL 3.5.9 release archive; do not fabricate a NOTICE. Confirm whether the actual work/build includes other NOTICE text.

### Potentially unnecessary for this exact package

- Mesa/LLVM license/attribution pages and Qt PDF/PDFium materials are tied to absent payloads and should not be automatically included. Their source files may remain in the internal evidence store for historical traceability.
- SQLite's page is courtesy information, not a required license text on the evidence reviewed.
- Build-only `pyinstaller-hooks-contrib` is not identified in the frozen runtime; no runtime notice is attributed to that project from the current artifact evidence.
- TinyCBOR, MD4C, double-conversion, libpsl/PSL, Brotli and other speculative candidates have no affirmative package evidence in this reconciliation. Do not add invented notices. Ask Qt for SBOM evidence if the code could be hidden/static.
- Windows/ICU/SChannel host components were not bundled as separate files; do not include their OS notices as though LogSentinel redistributes them. Validate host requirements separately.

### Ambiguous or potentially incorrect older statements

- The old 185-file Qt inventory describes Qt PDF as shipped; current path inventory disproves that for the 182-file artifact.
- The old VC++ wheel-absence assertion is superseded: case-normalized matching proves all eight nested DLLs are in the corresponding cached wheel payloads and `RECORD`s.
- The old CPython inventory says “all license files/no notices” as of a different package baseline. The present collection includes CPython license/README material; that does not settle the separate Microsoft runtime code terms.
- OpenSSL `ACKNOWLEDGEMENTS.md` is not an Apache `NOTICE` file. No separate NOTICE should be invented from it.
- Never transfer old counts, plugin quantity, PDF/Mesa licenses or load observations from the 185-file build onto this artifact.

## 7. Recommended future end-user distribution contents

This is a **conditional planning list**, not an assembled bundle or legal determination. The release owner and counsel must identify actual grants, source scope and channel before choosing files.

### 7.1 License texts and recipient notices to prepare if applicable

- If Qt/PySide components are conveyed under LGPLv3 as the applicable combined-work path, prepare the appropriate prominent Qt-use/LGPL notice and the GPLv3 and LGPLv3 copies called for by the reviewed route; consider an accessible license/about entry and any §4(c) runtime copyright notice if triggered. Resolve component-specific Qt/PySide/Shiboken alternatives before naming them.
- If a GPL option applies to any component (including PyInstaller's covered loader/bootloader code), include the correct GPL version and applicable exception text; retain the Bootloader Exception and do not conflate it with Apache runtime hooks. The collection currently has GPL-3.0 for the Qt/LGPL documentation and PyInstaller's combined `COPYING.txt`, but not a separate full GPL-2.0 text. Counsel should assess whether/how the GPLv2 text and any source duties apply to the conveyed bootloader/loader payload.
- Include the full CPython PSF license and retain the specific PSF copyright notice; use appropriate 3.14.10 attribution material only after build/source review. Independently include the selected version-specific Unicode, bzip2, Zstandard, mpdecimal and other confirmed component notices.
- Include Apache-2.0 for confirmed OpenSSL and Apache-licensed PyInstaller runtime-hook/modules, and preserve actual copyright/attribution and any applicable NOTICE text from the matched source/build. Do not promote the acknowledgements file into a fabricated NOTICE.
- Include confirmed BSD/MIT/permissive component copyrights, conditions and disclaimers for the exact Qt static libraries/plugins (e.g. relevant HarfBuzz, libpng, PCRE2/SLJIT, libjpeg-turbo, codecs, C++/WinRT), with the correct API-specific scope and required IJG documentation statement where applicable.
- Include the exact elected FreeType/Zstandard branch only. Do not bundle both alternatives as though cumulative or make an unrecorded election.
- Include no Qt PDF/PDFium or Mesa/LLVM notice solely because historical files exist in the repository; re-evaluate if those binaries are restored.

### 7.2 Source, offer, and instructions (not interchangeable with a notice file)

- For the applicable Qt/PySide license route, determine whether the recipient needs a corresponding-source offer or the LGPL §4(d)(0) Minimal Corresponding Source plus Corresponding Application Code and relinking instructions, or whether a validated §4(d)(1) shared-library mechanism is chosen. Match any offered sources to the exact linked binaries, patches and build configuration and maintain availability as required by the chosen route and law.
- If §4(e) Installation Information is triggered on actual conveyance/product facts, provide only the information required for installing/executing a modified combined work as counsel directs.
- Provide accurate source URLs/offer instructions and a recipient-controlled replacement/relink guide only after the chosen route is tested and reviewed. The internal evidence reports are not a substitute.
- For independently licensed components, provide any source or modification notices required by their actual license and exact source distribution. Do not offer unverified same-version source archives as corresponding source.

### 7.3 Optional, internal and non-payload material

- Optional courtesy attribution: SQLite public-domain acknowledgement, if desired and not misleading.
- Do not ship internal audit reports, candidate/alternative matrices, raw provenance notes, old-package inventories, failed replacement probes, manifests containing candidate/historical files, or the full `notices/` folder wholesale. They contain internal findings, alternatives and removed-component materials and are not a curated end-user notice bundle.
- Do not include a generic Microsoft runtime notice as a substitute for legal eligibility, exact source provenance or applicable product terms. Microsoft terms/redistribution eligibility should be handled according to counsel's and Microsoft's actual requirements.

## 8. Outstanding provenance and legal questions

### Qt / PySide / Shiboken

1. Which exact license option applies to each Qt 6.12.0 module/plugin, PySide6 and Shiboken6 file? Does Qt confirm the wheel `GPL-2.0-only` metadata option and Shiboken scope?
2. Can Qt provide authenticated source commits, downstream patches, generated inputs, per-file source-to-binary records, build configurations/toolchains, wheel-scoped SBOMs and copyright/license notices for the exact wheel hashes?
3. Which exact Qt third-party source snapshots, feature choices and license elections were linked into each DLL/plugin? What source produced the codec modules?
4. Which `.ts` files and individual notices generated the 99 `.qm` files, and which `lrelease` version/options were used?
5. Does the intended conveyance use an applicable LGPL route? Can the exact package work with recipient-controlled interface-compatible modified libraries, or can source/relink/application code and instructions be delivered? What user restrictions or signing/install controls apply? Does §4(e) trigger?

### CPython, independent native dependencies, and PyInstaller

6. Do the collected CPython 3.14.10 texts and attribution accurately match the exact Windows interpreter and build? What is the exact distribution's Microsoft Distributable Code section/scope and required treatment?
7. What exact CPython builds/inputs produced embedded zlib-compatible code, liblzma, Zstandard, Unicode and other extensions? Which Zstandard option is the distributor relying on?
8. Which exact source paths correspond to frozen PyInstaller entries; why does the packaged executable differ by four `.rdata` bytes from the installed bootloader reference, and what does that imply for modification status? What source/notice duties attach to each included code category?
9. Are the OpenSSL binaries from the exact 3.5.9 archive/build; does the Windows distribution include any additional NOTICE or attribution text not found in the inspected archive?

### VC++ and Microsoft terms

10. What Microsoft payload/build generated the eight Qt-signed nested runtime DLLs? What was copied, altered, or re-signed, and what written rights permit Qt and downstream distribution of these hashes?
11. What applicable Microsoft runtime/Visual Studio terms and eligibility basis cover the root 14.51 DLL copies and the eight nested 14.44 copies? Does any unmodified-file requirement apply, and how is it satisfied for the Qt-signed files?
12. Which local or central runtime deployment will be used, who maintains it, and what loader/clean-target tests cover duplicate paths and supported workflows?

## 9. Prioritized corrective actions

1. **Keep release HOLD and preserve the exact artifact.** Record intended distribution channel, recipients, end-user terms, installer, updates/signing/anti-tamper controls and release owner. Do not modify/rebuild this test artifact or claim release approval.
2. **Obtain Qt written rights/provenance package.** Request binary-specific license alternatives/election, the PySide GPLv2 and Shiboken scope resolution, matching SBOM/source/build manifests, translation notices, per-file copyright map, and written Microsoft runtime sourcing/redistribution basis for all eight exact hashes.
3. **Obtain qualified legal review before selecting a route.** Review actual component grants, conveyance, Qt/PySide obligations, LGPL §§3–4 (including conditional §4(c)/(e)), GPLv3 §6 if relevant, Microsoft runtime terms, distribution restrictions and third-party licenses. Record the decision for the exact artifact/channel.
4. **Complete component/source linkage.** Create a file-level path/hash → wheel/archive → source revision/patches/generated code → build job/configuration/SBOM → license/notice map for Qt, PySide, Shiboken, PyInstaller and CPython. Mark missing rows, don't infer source from versions.
5. **Resolve per-component notice gaps.** Map 99 translation catalogs; decide FreeType/Zstandard election based on rights/source evidence; determine exact liblzma, zlib-compatible, libtiff, libwebp/patent and Qt codec materials; validate PyInstaller entry categories and bootloader status; reconcile OpenSSL notices.
6. **Close VC++ runtime entitlement and servicing.** Review exact Microsoft source/terms and Qt's written authority. Decide local vs central deployment with counsel and a named security-update owner. No DLL replacement/removal is authorized here.
7. **Build a reviewed end-user notice/source set only after closure.** Select only applicable texts, attributions and source instructions. Keep internal reports and alternatives out. Validate package assembly, hashes and any chosen replacement/relink route on the authorized candidate.
8. **Re-inventory and re-review any changed candidate.** Re-run package identity, all component hashes, notice/source checks and Windows workflow tests after any authorized change. Keep disposition HOLD until qualified counsel and release owner approve the exact final artifact.

## 10. Official references and retrieval dates

The dates below are inherited from the existing source records or this local inspection. Links support upstream statements only; they do not prove the contents or license of a particular binary. Recheck documents against the actual proposed release and agreements.

| Reference | Use in reconciliation | Retrieval/view date in evidence |
|---|---|---|
| Qt 6.12 licensing, LGPL, third-party list and SBOM: <https://doc.qt.io/qt-6.12/licensing.html>, <https://doc.qt.io/qt-6.12/lgpl.html>, <https://doc.qt.io/qt-6.12/licenses-used-in-qt.html>, <https://doc.qt.io/qt-6.12/sbom.html> | Qt license choices, separate third-party code and SBOM context | 2026-11-09 / 2026-11-26 per reports; local pages reviewed 2026-11-27 |
| Qt for Python: <https://doc.qt.io/qtforpython-6/commercial/index.html>, <https://doc.qt.io/qtforpython-6/overviews/qtdoc-lgpl.html>, <https://doc.qt.io/qtforpython-6/licenses.html> | Public PySide/Shiboken licensing description and third-party code notes | 2026-11-09 / 2026-11-26 per reports; local commercial-use HTML reviewed 2026-11-27 |
| QUIP 18: <https://contribute.qt-project.org/quips/18/>; Qt localization: <https://doc.qt.io/qt-6.12/localization.html> | Translation/source-file classification and catalog context | 2026-11-09 per LGPL assessment |
| GNU GPL v3: <https://www.gnu.org/licenses/gpl-3.0.html>; GNU LGPL v3: <https://www.gnu.org/licenses/lgpl-3.0.html> | Conditional LGPL route and related source/license text | Local full texts reviewed 2026-11-27; URLs cited 2026-11-09 |
| PySide6 6.12 metadata and official Qt wheel mirrorlists: <https://pypi.org/project/PySide6/6.12.0/> and URLs in `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md` | Wheel metadata and digest values used for package payload identity | Cache/wheel/mirrorlist evidence recorded 2026-11-26 |
| CPython 3.14: <https://docs.python.org/3.14/license.html>, <https://github.com/python/cpython/tree/3.14>; Unicode 16: <https://www.unicode.org/Public/16.0.0/ucd/> and Unicode License V3 | CPython and Unicode public license/data evidence | Report sources 2026-11-26; local notice texts/hash rows checked 2026-11-27 |
| OpenSSL 3.5.9: <https://github.com/openssl/openssl/releases/tag/openssl-3.5.9> and archive evidence in `RUNTIME-LICENSING-EVIDENCE.md` | Apache license, acknowledgements and conditional NOTICE question | Archive investigation recorded 2026-11-26; local texts checked 2026-11-27 |
| PyInstaller 6.22.3: <https://pyinstaller.org/en/v6.22.3/license.html>, <https://github.com/pyinstaller/pyinstaller/blob/v6.22.3/COPYING.txt> | GPL/Bootloader Exception vs Apache runtime hook/module scopes | 2026-11-26 per runtime evidence; local archive list and COPYING inspected 2026-11-27 |
| Microsoft VC++ redistribution and version pages: links in `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md` and `VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md` | Redistribution limits, application-local vs central deployment, applicable terms | 2026-11-26 per reports; exact EULA/eligibility still open |
| Component source references in `notices/MANIFEST.md` | License texts/attributions for bzip2, FreeType, HarfBuzz, libjpeg-turbo, libpng, mpdecimal, PCRE2, SQLite, Unicode, Zstandard, C++/WinRT | Each row gives its pinned source URL/hash and limits; manifest hash rows rechecked 2026-11-27 |
| Requested local reports: attribution register, trimmed notice map, runtime evidence, MSVC review, final audit, release checklist, Qt inventory, notices README/MANIFEST, LGPL gap plan | Package evidence, historical scope caveats and prior findings | Local review on 2026-11-27; dates internal to each report remain as stated |

## 11. Verification, change control, and final disposition

**Final verification recorded after report creation:**

- **New report:** byte size and SHA-256 are provided in the completion response; no self-hash is embedded in the report.
- **Package:** 182 files / 80,058,228 bytes; executable SHA-256 remains `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- **Notice collection:** 34/34 files with recorded manifest hashes/sizes match. `MANIFEST.md` is the 35th file in the directory but has no self-hash/size row in itself; observed size is 13,184 bytes and SHA-256 is `28951f87cb012f372ef30972c32adf0bafbf57f5443de96ac523906c3f0660b3`, with no recorded expected value against which to compare it.
- **Release baseline:** all six artifacts in `C:/Users/DELL/AppData/Local/Temp/logsentinel-final-audit-release-before.txt` remain at their recorded sizes and SHA-256 values.
- **Worktree:** existing status was snapshotted before writing. After writing, no prior entry was removed; this report is the only intended added file. The pre-existing spec modification, licensing materials, release artifacts and test-result files were preserved.
- No package/source/spec/existing notice file was changed; no external download/extraction/rebuild, commit or push occurred.

**Disposition remains HOLD — NOT CLEARED FOR DISTRIBUTION.** This reconciliation identifies present files and evidence gaps; it does not determine that a legal obligation has been triggered or met. Prepare no end-user bundle and make no compliance claim until the actual rights, source and notice scope, distribution channel and exact authorized final artifact have been reviewed.