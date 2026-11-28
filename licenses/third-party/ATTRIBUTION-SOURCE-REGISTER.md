# Third-party attribution and source register

Read-only source register for the components identified in [`OTHER-COMPONENTS-INVENTORY.md`](OTHER-COMPONENTS-INVENTORY.md). Package evidence refers to that inventory's **185-file, 105,363,740-byte `dist/gui-ondir-test/LogSentinel-GUI/` build**, not the later trimmed test package. This register records source evidence and open questions; it is **not legal advice, a notice payload, or a compliance finding**.

## How to read the statuses

- **Verified** — the inventory reports direct package/version evidence and an official upstream source for the version or its applicable licensing terms. This does not mean a release notice set has been assembled or legally reviewed.
- **Partially Verified** — component presence or its upstream terms are supported, but the exact embedded version, per-file scope, or package-to-vendor-document match is not established.
- **Unresolved** — presence, version, applicable license/notice set, or another essential attribution detail is not established well enough to prepare a specific notice.

“Copyright attribution” below means the attribution material identified by the cited source. For components containing many separately copyrighted files, it is not a substitute for checking the complete upstream notice text. “Required notice” describes the source terms at a high level, not a conclusion about LogSentinel's legal obligations.

## Priority components

### OpenSSL

- **Detected version / package evidence:** 3.5.9, read from the bundled `libcrypto-3.dll` and `libssl-3.dll` according to the inventory.
- **License alternatives:** Apache License 2.0 for OpenSSL 3.0 and later; the older OpenSSL/SSLeay terms are not the applicable alternative for this reported version. No election between alternatives is indicated for 3.5.9.
- **Copyright attribution:** OpenSSL source files have file-specific notices. Do not infer a single project-wide copyright line from an arbitrary header; inspect the actual source/version notices if preparing an attribution.
- **Required notice / redistribution conditions:** Include a copy of Apache-2.0; preserve applicable notices and mark modified files where required. Apache-2.0 §4(d)'s `NOTICE`-file condition applies **only if** the Work includes a NOTICE text file. The `openssl-3.5.9` source-tree entry `ACKNOWLEDGEMENTS.md` is not itself evidence of an Apache `NOTICE` file. The exact official release-tarball contents and notices applicable to these Windows binaries have not been independently inventoried here. Do not assert that a separate OpenSSL NOTICE is required or that §4(d) is satisfied until that is checked. Avoid implying OpenSSL endorsement or using its marks.
- **Official sources:** [OpenSSL license policy](https://www.openssl.org/source/license.html); [3.5.9 tagged source](https://github.com/openssl/openssl/tree/openssl-3.5.9); [Apache-2.0 text in the tag](https://github.com/openssl/openssl/blob/openssl-3.5.9/LICENSE.txt); [3.5.9 release](https://github.com/openssl/openssl/releases/tag/openssl-3.5.9).
- **Version match:** Direct package version string and a corresponding upstream release tag; exact build provenance/source archive hash not recorded in the inventory.
- **Uncertainty:** Exact source archive used and its file list; whether an applicable upstream NOTICE file accompanied it; which file-level attribution notices apply to the bundled object-form binaries.
- **Status:** **Partially Verified**.

### PyInstaller, bootloader, loader modules, and runtime hooks

- **Detected version / package evidence:** 6.22.3 in the build log and installed distribution metadata; the executable itself does not expose a PyInstaller version string. Inventory reports the bootloader and loader/bootstrap payload embedded in the GUI executable, plus runtime hooks.
- **License alternatives:** PyInstaller's bootloader/related files are GPL-2.0-or-later with the **Bootloader Exception**. The exception allows compiled bootloader and related files to be embedded in combinations with other programs; it does not erase the GPL in other respects. PyInstaller runtime hooks are separately Apache-2.0-licensed. The local 6.22.3 `COPYING.txt` identifies loader files in `PyInstaller/loader` as bootloader-related; classify each embedded file by its upstream path rather than applying one label to every CArchive entry.
- **Copyright attribution:** PyInstaller licensing text lists PyInstaller Development Team (2010–2023), Giovanni Bajo (2005–2009), and prior McMillan Enterprises work (2002); runtime hooks may have their own authors/notices.
- **Required notice / redistribution conditions:** Retain the applicable GPL text and the Bootloader Exception text for covered embedded bootloader/loader files. Preserve Apache-2.0 terms and applicable notices for the shipped runtime hooks. The exception explicitly does not remove GPL restrictions on modification or distribution of the covered files outside a combined executable. The inventory does not establish source-by-source modification status; do not state that the bootloader is unmodified without confirming it.
- **Official sources:** [PyInstaller 6.22.3 licensing documentation](https://pyinstaller.org/en/v6.22.3/license.html); [versioned COPYING.txt](https://github.com/pyinstaller/pyinstaller/blob/v6.22.3/COPYING.txt); [GPL-2.0 text](https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt); [Apache-2.0 text](https://www.apache.org/licenses/LICENSE-2.0.txt).
- **Version match:** 6.22.3 is evidenced by build log/local package metadata and a matching upstream versioned source page, but not by a self-identifying version string in the frozen executable.
- **Uncertainty:** Per-entry file-to-license mapping and whether the bootloader/loader files were modified. Runtime hooks must not be described as covered by the bootloader exception.
- **Status:** **Partially Verified**.

### CPython runtime and standard library

- **Detected version / package evidence:** CPython 3.14.10, reported from the bundled Python DLL resource; standard library files are included in the frozen package.
- **License alternatives:** Python Software Foundation License Version 2 (PSF-2.0) for CPython. Python's license documentation notes that some incorporated software has different licenses; this row does not replace their individual entries below.
- **Copyright attribution:** The Python 3.14 source README identifies PSF (2001), BeOpen.com (2000), CNRI (1995–2001), and Stichting Mathematisch Centrum (1991–1995). The PSF-2.0 text specifically requires retaining “Copyright (c) 2001 Python Software Foundation; All Rights Reserved”. Use the version-specific distribution's actual license/notice rather than silently substituting a current-year range.
- **Required notice / redistribution conditions:** Include the PSF license and retain the PSF copyright notice in Python or a derivative version. Separately account for incorporated code under other licenses (including Unicode data and compression libraries listed here).
- **Official sources:** [Python 3.14.10 release](https://www.python.org/downloads/release/python-31410/); [CPython 3.14 license](https://github.com/python/cpython/blob/3.14/LICENSE); [CPython 3.14 README and copyright information](https://github.com/python/cpython/blob/3.14/README.rst); [Python licensing documentation](https://docs.python.org/3.14/license.html).
- **Version match:** Package resource evidence and the official 3.14.10 release agree; the exact Windows build/source archive hash is not recorded.
- **Uncertainty:** Inventory does not map every standard-library module to its included third-party code. Do not treat PSF-2.0 as covering separately licensed incorporated components.
- **Status:** **Verified** for the runtime version and PSF terms; incorporated-code inventory remains separate work.

### Unicode Character Database

- **Detected version / package evidence:** Unicode 16.0.0 reported from bundled `unicodedata.pyd`.
- **License alternatives:** Unicode License Version 3 for Unicode data/software, unless a particular data file states otherwise; no alternative is indicated for this UCD entry.
- **Copyright attribution:** Unicode, Inc.; the Unicode License text carries the copyright and permission notice. The current general license page may update its copyright year; use the notice applicable to the Unicode 16.0.0 data/source distribution rather than copying a later year's notice without checking.
- **Required notice / redistribution conditions:** The Unicode License requires its copyright and permission notice with copies of the data/software or in associated documentation.
- **Official sources:** [Unicode License](https://www.unicode.org/license.txt); [Unicode 16.0.0 UCD](https://www.unicode.org/Public/16.0.0/ucd/); [Unicode licensing policy](https://www.unicode.org/policies/licensing_policy.html).
- **Version match:** Package-reported 16.0.0 matches the official Unicode 16.0.0 data release.
- **Uncertainty:** The inventory identifies the version but does not identify the exact UCD input files or reproduce a version-specific license notice from the Python source distribution.
- **Status:** **Partially Verified**.

## Compression, database, and numerical libraries

### zlib-ng / zlib-compatible code in CPython

- **Detected version / package evidence:** Presence and strings `zlib-ng` / `1.3.1` are reported inside `python314.dll`. `1.3.1` may identify zlib-compatible API/version data, **not** the zlib-ng upstream release number; the exact zlib-ng release is not recoverable from the listed evidence.
- **License alternatives:** zlib License; no alternative identified for the relevant code.
- **Copyright attribution:** Jean-loup Gailly and Mark Adler in the zlib-ng license/header, subject to the actual source revision's notices.
- **Required notice / redistribution conditions:** Preserve the zlib copyright/license notice and conditions; do not misrepresent origin, mark altered source versions, and do not remove/alter the notice from source distributions. The zlib license says product-documentation acknowledgement is appreciated but not required.
- **Official sources:** [zlib-ng license](https://github.com/zlib-ng/zlib-ng/blob/develop/LICENSE.md); [zlib-ng project](https://github.com/zlib-ng/zlib-ng).
- **Version match:** Presence is package-evidenced; upstream release/version is not matched.
- **Uncertainty:** Exact zlib-ng release/commit and whether the `1.3.1` string denotes compatibility with zlib rather than the zlib-ng version.
- **Status:** **Partially Verified**.

### zlib-family code in Qt Core

- **Detected version / package evidence:** zlib-like routines/symbols and a zlib decompression message are reported in `Qt6Core.dll`. The inventory labels this copy zlib-ng, but the listed evidence does not prove that implementation identity. Qt's attribution documentation calls its component “zlib”; the current Qt 6.12 attribution/change pages include a later Qt 6.12.1 update, and should not be used as proof of the exact 6.12.0 payload.
- **License alternatives:** zlib License for the upstream zlib component. Whether this is zlib-ng or another zlib-compatible implementation remains unresolved.
- **Copyright attribution:** If the upstream component is zlib, its notice names Jean-loup Gailly and Mark Adler; confirm the actual code before using that attribution.
- **Required notice / redistribution conditions:** Preserve the actual component's copyright/license conditions and accurately mark changes where applicable. Do not prepare a zlib-ng-specific notice from symbol strings alone.
- **Official sources:** [Qt 6.12 third-party code index](https://doc.qt.io/qt-6.12/licenses-used-in-qt.html); [Qt zlib attribution page](https://doc.qt.io/qt-6/qtcore-attribution-zlib.html); [zlib-ng license](https://github.com/zlib-ng/zlib-ng/blob/develop/LICENSE.md).
- **Version match:** Qt binary version is reported as 6.12.0; the vendor attribution page currently resolves to a later 6.12 patch and does not establish the exact implementation/version bundled in this binary.
- **Uncertainty:** Component identity and version; exact 6.12.0 Qt source/attribution snapshot.
- **Status:** **Unresolved**.

### bzip2 / libbzip2

- **Detected version / package evidence:** 1.0.8 string and date reported in `_bz2.pyd`.
- **License alternatives:** bzip2 1.0.8 license; no alternative identified.
- **Copyright attribution:** Julian R. Seward, copyright 1996–2019.
- **Required notice / redistribution conditions:** Reproduce the copyright notice, conditions and disclaimer for binary redistribution; source distribution also has origin/altered-source terms and a no-endorsement condition.
- **Official sources:** [bzip2 1.0.8 manual and license](https://sourceware.org/bzip2/manual/manual.html); [bzip2 project](https://sourceware.org/bzip2/); [1.0.8 license copy](https://github.com/libarchive/bzip2/blob/bzip2-1.0.8/LICENSE).
- **Version match:** Package version string and upstream 1.0.8 release/license agree.
- **Uncertainty:** No substantial version uncertainty noted; inventory does not identify source archive hash.
- **Status:** **Verified**.

### liblzma (XZ Utils)

- **Detected version / package evidence:** Presence in `_lzma.pyd`; exact version not recoverable in the inventory.
- **License alternatives:** liblzma in modern XZ Utils is 0BSD; this cannot be assumed for an unidentified older snapshot. XZ Utils contains files under multiple licenses, and the command-line tools' licenses must not be applied indiscriminately to liblzma.
- **Copyright attribution:** XZ Utils authors and contributors, with upstream-derived code also credited to its authors; 0BSD permits distribution without a notice, but an acknowledgement may be used.
- **Required notice / redistribution conditions:** Under 0BSD no conditions are imposed; verify the applicable license for the exact bundled revision before relying on this. Do not import GPL/LGPL obligations applicable to unrelated XZ Utils files into the library without evidence.
- **Official sources:** [XZ Utils licensing files](https://github.com/tukaani-project/xz/tree/master); [liblzma API and license description](https://tukaani.org/xz/liblzma-api/index.html).
- **Version match:** Presence only; source version and license revision not matched.
- **Uncertainty:** Exact liblzma version/license vintage. XZ Utils states core components moved to 0BSD starting with 5.5.2beta; the inventory provides no bundled version to establish that threshold.
- **Status:** **Unresolved**.

### Zstandard

- **Detected version / package evidence:** 1.5.7 reported from `_zstd.pyd`.
- **License alternatives:** BSD-style license **or** GPLv2, at the user's option for the C library. The alternatives are not cumulative; do not describe the component as GPL-only. No election is evidenced by the binary.
- **Copyright attribution:** Meta Platforms, Inc. and affiliates.
- **Required notice / redistribution conditions:** If using the BSD option, reproduce its copyright notice, conditions and disclaimer in binary-distribution materials and observe the no-endorsement term. If relying on GPLv2, assess and satisfy that license instead. This register does not make the election.
- **Official sources:** [Zstandard 1.5.7 license](https://github.com/facebook/zstd/blob/v1.5.7/LICENSE); [1.5.7 public header/license statement](https://github.com/facebook/zstd/blob/v1.5.7/lib/zstd.h); [upstream license explanation](https://github.com/facebook/zstd#license).
- **Version match:** Package string and upstream v1.5.7 source tag agree.
- **Uncertainty:** License branch selected for redistribution is not recorded.
- **Status:** **Partially Verified**.

### mpdecimal

- **Detected version / package evidence:** 4.0.0 indicated by the CPython build path reported in the inventory.
- **License alternatives:** Simplified BSD / 2-clause BSD for the upstream 4.0.0 distribution; no alternative identified.
- **Copyright attribution:** Stefan Krah; the 4.0.0 `COPYRIGHT.txt` notice reports 2008–2024.
- **Required notice / redistribution conditions:** Preserve copyright/license notice and disclaimer in source; binary distributions reproduce the notice and disclaimer in documentation or accompanying materials.
- **Official sources:** [mpdecimal downloads and license](https://www.bytereef.org/mpdecimal/download.html); [mpdecimal 4.0.0 source archive](https://www.bytereef.org/software/mpdecimal/releases/mpdecimal-4.0.0.tar.gz).
- **Version match:** Build path reports the version; exact upstream source archive/hash used for the embedded copy is not recorded.
- **Uncertainty:** Whether the embedded code is identical to the 4.0.0 upstream release or locally modified.
- **Status:** **Partially Verified**.

### SQLite

- **Detected version / package evidence:** 3.50.4 from `sqlite3.dll` version resource and source ID, according to the inventory.
- **License alternatives:** SQLite implementation code is public domain; no alternate license is required for that code. SQLite separately notes that some build scripts may have different terms, but those are not part of the shipped library according to the project's statement.
- **Copyright attribution:** Contributors have dedicated the SQLite code to the public domain; a courtesy statement that SQLite is public domain is conventional, not a required copyright notice.
- **Required notice / redistribution conditions:** No license notice is required for the public-domain SQLite deliverable. A courtesy credit may be included, without suggesting it is legally required.
- **Official sources:** [SQLite 3.50.4 release record](https://sqlite.org/releaselog/3_50_4.html); [SQLite copyright/public-domain statement](https://sqlite.org/copyright.html).
- **Version match:** Package version/source ID matches the official release record.
- **Uncertainty:** None material in the inventory for the library version/public-domain statement.
- **Status:** **Verified**.

## Qt-bundled graphics, text, image, and document libraries

Qt documentation is useful evidence of what a particular Qt release may contain, but does not prove a library is present in this exact Windows binary unless paired with package evidence. The binary inventory reports Qt 6.12.0; use version-pinned Qt 6.12.0 attributions where available and treat later patch-level pages as supporting context only.

### FreeType

- **Detected version / package evidence:** `FT_*` / `QFontEngineFT` evidence in `Qt6Gui.dll`; no embedded version string recovered. Qt's Qt 6.12.0 attribution page lists FreeType 2.14.3.
- **License alternatives:** FreeType Project License (FTL) **or** GNU GPL-2.0-only. They are mutually exclusive choices; the package inventory records no choice.
- **Copyright attribution:** The complete Qt attribution includes multiple contributors; the FTL's recommended credit is “Portions of this software are copyright © The FreeType Project (www.freetype.org). All rights reserved.”
- **Required notice / redistribution conditions:** If the FTL branch is selected, reproduce its required terms/credit in product documentation. The GPLv2-only branch has different consequences and must not be silently inferred. Preserve the relevant version-specific copyright notices.
- **Official sources:** [Qt 6.12.0 FreeType attribution](https://doc.qt.io/qt-6.12/qtgui-attribution-freetype.html); [FreeType license alternatives](https://freetype.org/license.html); [Qt 6.12 third-party index](https://doc.qt.io/qt-6.12/licenses-used-in-qt.html).
- **Version match:** Qt 6.12.0 attribution identifies upstream 2.14.3; binary evidence confirms FreeType presence but not its exact version.
- **Uncertainty:** Exact embedded version and documented license election.
- **Status:** **Partially Verified**.

### HarfBuzz

- **Detected version / package evidence:** HarfBuzz symbols in `Qt6Gui.dll`; no binary version string recovered. Qt 6.12.0 attribution identifies HarfBuzz-NG 14.5.0.
- **License alternatives:** Old MIT license for the listed upstream component; individual subdirectories/files may carry other terms.
- **Copyright attribution:** Qt's versioned attribution lists Google, Ebrahim Byagowi, Facebook, Mozilla, Codethink, Nokia, Keith Stribley, SIL, Chris Wilson, Behdad Esfahbod, Red Hat, David Turner, Werner Lemberg, Igalia, Matthias Clasen, Khaled Hosny, Adobe, and Alexei Podtelezhnikov, with year ranges in the source.
- **Required notice / redistribution conditions:** Include the applicable copyright and Old MIT permission/disclaimer text; check individual-file exceptions rather than assuming every HarfBuzz file has identical terms.
- **Official sources:** [Qt 6.12.0 HarfBuzz attribution](https://doc.qt.io/qt-6.12/qtgui-attribution-harfbuzz-ng.html); [HarfBuzz upstream COPYING](https://github.com/harfbuzz/harfbuzz/blob/main/COPYING).
- **Version match:** Vendor Qt 6.12.0 attribution identifies 14.5.0; binary confirms presence but not version.
- **Uncertainty:** Exact embedded version and per-file license exceptions.
- **Status:** **Partially Verified**.

### libpng

- **Detected version / package evidence:** 1.6.58 string and PNG symbols in `Qt6Gui.dll`.
- **License alternatives:** PNG Reference Library License version 2 (libpng license); no alternative identified for the reported release.
- **Copyright attribution:** The 1.6.58 source header identifies the PNG Reference Library Authors, Cosmin Truta, Glenn Randers-Pehrson, Andreas Dilger, and Guy Eric Schalnat, with the versioned year ranges in the source.
- **Required notice / redistribution conditions:** Include the full version-appropriate copyright, disclaimer and license text; preserve the origin/altered-source conditions.
- **Official sources:** [libpng v1.6.58 source header](https://github.com/pnggroup/libpng/blob/v1.6.58/png.h); [libpng v1.6.58 announcement/source files](https://github.com/pnggroup/libpng/tree/v1.6.58); [official license text](https://libpng.org/pub/png/src/libpng-LICENSE.txt).
- **Version match:** Package string reports 1.6.58 and the official upstream release has that version; source hash/build provenance is not recorded.
- **Uncertainty:** Exact Qt-vendored source revision is not identified, though version and license family are supported.
- **Status:** **Verified**.

### PCRE2 and SLJIT

- **Detected version / package evidence:** PCRE2 strings in `Qt6Core.dll`; no binary version string recovered. Qt 6.12.0 attribution lists PCRE2 10.48 and its stack-less JIT component.
- **License alternatives:** PCRE2 basic library: BSD 3-Clause with the PCRE2 binary-like packages exception; SLJIT/JIT code: separately BSD 2-Clause. No evidence of a different license election.
- **Copyright attribution:** The Qt attribution lists University of Cambridge, Philip Hazel, and Zoltan Herczeg for the basic library; consult the versioned SLJIT attribution for its own notice.
- **Required notice / redistribution conditions:** Reproduce applicable BSD notices, conditions, disclaimers and the PCRE2 exception. Include the distinct SLJIT license notice if that code is present (the Qt attribution identifies it as a separate component).
- **Official sources:** [Qt 6.12.0 PCRE2 attribution](https://doc.qt.io/qt-6.12/qtcore-attribution-pcre2.html); [Qt 6.12.0 PCRE2 SLJIT attribution](https://doc.qt.io/qt-6.12/qtcore-attribution-pcre2-sljit.html); [PCRE2 10.48 upstream license](https://github.com/PCRE2Project/pcre2/blob/pcre2-10.48/LICENCE).
- **Version match:** Qt 6.12.0 attribution identifies 10.48; package evidence confirms PCRE2 presence but not version.
- **Uncertainty:** Exact embedded version and confirmation of which PCRE2/SLJIT objects are linked into this build.
- **Status:** **Partially Verified**.

### libjpeg-turbo

- **Detected version / package evidence:** 3.2.0 string in `qjpeg.dll` and `qtiff.dll`.
- **License alternatives:** The upstream project describes compatible IJG and modified 3-clause BSD licenses. Applicable license depends on the code/API; do not treat every file as carrying three independent whole-project licenses. The source also documents less restrictive component licenses/subcomponents.
- **Copyright attribution:** IJG and libjpeg-turbo file notices, including the copyright lines in the versioned `README.ijg` / source files; use the complete 3.2.0 license bundle rather than inventing a single blanket copyright line.
- **Required notice / redistribution conditions:** Reproduce the applicable IJG/BSD copyright notices, conditions and disclaimers; preserve relevant bundled-component notices and the no-endorsement condition. Confirm the precise code composition of Qt's two plugins before finalizing the notice.
- **Official sources:** [libjpeg-turbo 3.2.0 license](https://github.com/libjpeg-turbo/libjpeg-turbo/blob/3.2.0/LICENSE.md); [3.2.0 release](https://github.com/libjpeg-turbo/libjpeg-turbo/releases/tag/3.2.0); [upstream licensing overview](https://libjpeg-turbo.org/About/License).
- **Version match:** Package-reported version 3.2.0 matches the upstream version tag, correcting the earlier 3.2.1 assumption.
- **Uncertainty:** Which library interfaces/subcomponents are linked into each Qt plugin and whether vendor patches affect attribution.
- **Status:** **Partially Verified**.

### libtiff

- **Detected version / package evidence:** `LIBTIFF_*` symbols and a “Since libtiff 4.5.1” string in `qtiff.dll`; no exact version. Qt's later Qt 6.12.1 change record lists an update to 4.7.2, which does not prove the Qt 6.12.0 package's version.
- **License alternatives:** The upstream libtiff license is permissive/BSD-like, with additional component notices (including LZW-derived code in current source); exact applicable files depend on the embedded snapshot.
- **Copyright attribution:** Sam Leffler, Silicon Graphics, Inc., and any third-party code authors named by the exact version's license file.
- **Required notice / redistribution conditions:** Preserve the relevant copyright and permission notices, disclaimer and advertising/no-endorsement restrictions; include separate notices for included third-party components.
- **Official sources:** [LibTIFF 4.7.2 license documentation](https://libtiff.gitlab.io/libtiff/project/license.html); [4.7.2 versioned license file](https://gitlab.com/libtiff/libtiff/-/blob/v4.7.2/LICENSE.md); [Qt 6.12 license changes](https://doc.qt.io/qt-6/license-changes.html).
- **Version match:** Presence is supported; “Since 4.5.1” supplies only a lower bound. Later Qt documentation cannot establish the exact 6.12.0 binary version.
- **Uncertainty:** Exact release and full version-specific notice set.
- **Status:** **Unresolved**.

### libwebp

- **Detected version / package evidence:** WebP code/signatures in `qwebp.dll`; inventory did not recover an embedded version. Qt's later Qt 6.12.1 attribution lists libwebp 1.6.0, not proof of the earlier 6.12.0 binary.
- **License alternatives:** BSD 3-Clause for the source identified; the project also publishes a separate patent grant (`PATENTS`).
- **Copyright attribution:** Google Inc. (2010) in `COPYING`, plus upstream contributor notices as applicable.
- **Required notice / redistribution conditions:** Reproduce the BSD copyright, conditions and disclaimer, including the no-endorsement clause; review/include the relevant patent grant if applicable to the code distributed.
- **Official sources:** [libwebp 1.6.0 tagged source](https://chromium.googlesource.com/webm/libwebp/+/refs/tags/v1.6.0/); [tagged COPYING](https://chromium.googlesource.com/webm/libwebp/+/refs/tags/v1.6.0/COPYING); [Qt libwebp attribution](https://doc.qt.io/qt-6/qtimageformats-attribution-libwebp.html).
- **Version match:** Presence is package-evidenced; the vendor page is a later Qt 6.12 patch and the binary version remains unknown.
- **Uncertainty:** Exact source/version and relevant patent-grant scope.
- **Status:** **Unresolved**.

### C++/WinRT

- **Detected version / package evidence:** 2.0.250303.1 string in `Qt6Core.dll`.
- **License alternatives:** MIT License.
- **Copyright attribution:** Microsoft Corporation.
- **Required notice / redistribution conditions:** Include copyright and permission notice in copies or substantial portions and retain the disclaimer.
- **Official sources:** [C++/WinRT 2.0.250303.1 release](https://github.com/microsoft/cppwinrt/releases/tag/2.0.250303.1); [upstream MIT license](https://github.com/microsoft/cppwinrt/blob/master/LICENSE).
- **Version match:** Exact version string reported in the package and matching upstream release.
- **Uncertainty:** Exact source commit/hash embedded is not recorded.
- **Status:** **Verified**.

## Mesa, LLVM, and PDFium

### Mesa llvmpipe / software rasterizer

- **Detected version / package evidence:** Mesa 11.2.2 in `opengl32sw.dll`; inventory says it was bundled but not loaded during the observed run.
- **License alternatives:** Mesa is a collection with differing component/file licenses; the Qt llvmpipe attribution contains multiple notices. Do not summarize the complete DLL as a single MIT-licensed work without checking that attribution.
- **Copyright attribution:** Includes Brian Paul and Mesa contributors, plus third-party/component authors named in Qt's llvmpipe attribution.
- **Required notice / redistribution conditions:** Preserve the relevant notices and license texts from the version-matched Qt/Mesa attribution; binary inclusion means not-loaded status does not remove the attribution question.
- **Official sources:** [Qt 6.12 llvmpipe attribution](https://doc.qt.io/qt-6.12/qt-attribution-llvmpipe.html); [Mesa licensing overview](https://docs.mesa3d.org/license.html); [Mesa 11.2.2 source](https://gitlab.freedesktop.org/mesa/mesa/-/tree/mesa-11.2.2).
- **Version match:** Binary version string identifies 11.2.2; Qt's attribution is a Qt 6.12 page, but the inventory has not matched the exact DLL build/constituent files to the full notice set.
- **Uncertainty:** Full component-by-component licenses and exact build provenance of the binary.
- **Status:** **Partially Verified**.

### LLVM inside Mesa

- **Detected version / package evidence:** `llvm-mc (based on LLVM 3.6.2)` string in `opengl32sw.dll`.
- **License alternatives:** University of Illinois/NCSA Open Source License applies to LLVM releases before 8.0; do not apply current LLVM Apache-2.0 with LLVM Exceptions to this 3.6.2 component. Check Mesa's other contents separately.
- **Copyright attribution:** University of Illinois at Urbana-Champaign, copyright 2003–2014 in the official 3.6.2 license.
- **Required notice / redistribution conditions:** Retain the copyright/license/disclaimer in source distributions and reproduce them in documentation or other distribution materials for binary distributions; no endorsement using contributor/institution names.
- **Official sources:** [LLVM 3.6.2 LICENSE.TXT](https://releases.llvm.org/3.6.2/LICENSE.TXT); [LLVM release licensing history](https://releases.llvm.org/).
- **Version match:** Version string and official 3.6.2 license correspond.
- **Uncertainty:** Exact LLVM-derived code subset and any Qt/Mesa patches, rather than the license family/version.
- **Status:** **Verified**.

### PDFium and Qt PDF's transitive components

- **Detected version / package evidence:** PDFium-related string and PDF decoder handlers reported inside `Qt6Pdf.dll`; Qt PDF and `qpdf.dll` were bundled in the inventory baseline, though not loaded in the observed workflow. Exact PDFium snapshot/version is not established.
- **License alternatives:** PDFium's upstream tree contains BSD-style terms and Qt's PDF attribution material may include additional third-party terms (including Apache-2.0-licensed material). The applicable set is snapshot/build-specific; do not label the whole Qt PDF payload BSD-3-Clause based on PDFium's top-level license alone.
- **Copyright attribution:** PDFium Authors plus all third-party authors enumerated by the precise Qt/PDFium snapshot attribution. The inventory reports Chromium/Abseil/AGG/lcms/ICU/fast_float strings were not found; absence of strings is not proof those dependencies are absent.
- **Required notice / redistribution conditions:** Reproduce PDFium's applicable BSD notices and the exact Qt PDF third-party license/attribution set, with per-component terms. Obtain the Qt 6.12.0 module-specific attribution/SBOM and match it to the packaged DLL before writing a final payload.
- **Official sources:** [PDFium upstream license](https://pdfium.googlesource.com/pdfium/+/main/LICENSE); [Qt 6.12 PDF licensing](https://doc.qt.io/qt-6.12/qtpdf-licensing.html); [Qt PDF third-party PDFium attribution](https://doc.qt.io/qt-6.12/qtpdf-3rdparty-pdfium.html); [Qt SBOM documentation](https://doc.qt.io/qt-6.12/sbom.html).
- **Version match:** Presence is supported; neither PDFium snapshot nor transitive attribution set is matched to the packaged Qt 6.12.0 binaries.
- **Uncertainty:** Exact snapshot, transitive component contents, license alternatives/elections, and complete notices. The fact the DLL was not loaded does not resolve the distribution question.
- **Status:** **Unresolved**.

## Other candidates and build/host components from the inventory

The components below were listed as unproven, string-only, build-time, or host-provided in the inventory. An upstream project license is not evidence that the component is present in this package.

| Component | Version and package match | License alternatives; copyright attribution | Notice / attribution evidence | Official source | Uncertainty and status |
|---|---|---|---|---|---|
| TinyCBOR | Not evidenced in package; `qt_cbor_*` helpers alone were attributed by the inventory to Qt. | If independently present, upstream MIT; Intel and contributors. | MIT copyright/permission notice would apply only if actual TinyCBOR code is identified. | [TinyCBOR upstream](https://github.com/intel/tinycbor) | Presence/version unresolved — **Unresolved**. |
| MD4C | Not evidenced; file-extension string is insufficient. | If present, MIT; copyright attribution must come from the exact source. | Include upstream MIT notice only if code is established. | [MD4C upstream](https://github.com/mity/md4c) | Presence/version unresolved — **Unresolved**. |
| double-conversion | Not evidenced by the inventory's binary-string checks. | If present, BSD-3-Clause; Google/contributor notices per source. | Include exact upstream BSD notice only if code is established. | [double-conversion upstream](https://github.com/google/double-conversion) | Presence/version unresolved — **Unresolved**. |
| libpsl / Public Suffix List | Not evidenced in `Qt6Network.dll`; Qt Network was also not loaded in the observed session. | If present, libpsl uses MIT-style terms; PSL data may have distinct source/licensing details. | Do not infer library/data notices without identifying the payload. | [libpsl upstream](https://github.com/rockdaboot/libpsl) | Presence, version and data provenance unresolved — **Unresolved**. |
| Brotli | No Brotli code evidenced; name appears only among OpenSSL provider-name strings, which is not proof of bundled codec code. | If present, MIT; Google/contributor copyright notices per source. | No Brotli notice established for this build. | [Brotli upstream](https://github.com/google/brotli) | Presence/version unresolved — **Unresolved**. |
| Chromium, Abseil, AGG, lcms, fast_float, ICU within Qt PDF | Not evidenced by the inventory's string scan; that scan cannot exclude stripped/renamed code. | Each has its own license and authors; no single combined license or attribution should be inferred. | Qt PDF's exact 6.12.0 SBOM/third-party attribution and build/source records are needed before listing specific required notices. | [Qt 6.12 PDF licensing](https://doc.qt.io/qt-6.12/qtpdf-licensing.html); [Qt SBOM documentation](https://doc.qt.io/qt-6.12/sbom.html) | Presence and per-component versions/licenses unresolved — **Unresolved**. |
| OpenSSL provider strings `zlib`, `brotli`, `zstd` | Strings in `libcrypto-3.dll`; no separate imported codec library or codec-code evidence in the inventory. | No standalone component license can be attributed from strings alone. | Do not add codec notices solely because provider names appear. | [OpenSSL 3.5.9 source](https://github.com/openssl/openssl/tree/openssl-3.5.9) | Whether codec code is compiled in is unresolved — **Unresolved**. |
| ICU from Windows System32 | Host ICU 64.2 reported at runtime; not bundled in the audited package. | System/OS-provided component; not a LogSentinel redistribution license election. | No bundled ICU notice established. Do not claim the package redistributes ICU; record the host dependency separately. | [ICU project](https://icu.unicode.org/); host evidence is the inventory's runtime observation. | Host version/signing evidence reported; no redistribution component match — **Verified** as not bundled in the audited package. |
| Microsoft Visual C++ runtime | Two reported generations: 14.51.36247.0 and 14.44.35211.0, in different package folders. | Microsoft Redistributable terms, not an OSS license alternative; Microsoft copyright. | Redistribution depends on Microsoft's applicable Visual Studio/VC++ terms and package eligibility; no standalone notice text or normalized runtime set was established. | [Microsoft Visual C++ Redistributable latest supported downloads](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) | Versions are package-evidenced, but the applicable grant/version skew requires review — **Partially Verified**. |
| pyinstaller-hooks-contrib | Build-time package 2026.10 per inventory; no bundled runtime component identified. | Apache-2.0 for the build-time project. | No notice attributed to the GUI binary from the inventory's runtime-hook provenance check. If build scripts/package are redistributed separately, assess their own terms. | [pyinstaller-hooks-contrib upstream](https://github.com/pyinstaller/pyinstaller-hooks-contrib) | Inventory reports no shipped artifact — **Verified** as not a bundled runtime component. |
| Pixman | Inventory reports not present in the Windows Qt build. | Not applicable if absent. | No package notice indicated. | [Pixman upstream](https://www.pixman.org/) | Inventory's absence finding — **Verified** as absent from audited package. |

## Source and package evidence gaps to close before preparing notices

1. Obtain and preserve the exact upstream source/build manifests (or Qt 6.12.0 SBOMs) matching each statically linked library in `Qt6Core.dll`, `Qt6Gui.dll`, `qjpeg.dll`, `qtiff.dll`, and `qwebp.dll`.
2. Resolve PyInstaller's exact embedded-file license mapping, including the Apache-2.0 runtime hooks, and verify whether the bootloader/loader files are modified before describing them.
3. Resolve OpenSSL's exact source archive and inspect its actual release file list. Apache §4(d) is conditional; the tag's `ACKNOWLEDGEMENTS.md` is not proof of an Apache `NOTICE` file.
4. Record the FreeType license election, Zstandard license election, and exact liblzma revision before assembling notices.
5. Match PDFium and every Qt PDF transitive component to the exact Qt 6.12.0 build; a current documentation page or an unsuccessful binary string search is not sufficient.
6. Collect version-appropriate notice texts and re-check the final package inventory after any build change. This register alone is not a third-party notice payload and does not establish legal compliance.
