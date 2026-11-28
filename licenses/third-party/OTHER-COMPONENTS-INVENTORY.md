# Remaining bundled third-party components — audit

Read-only audit of `dist/gui-ondir-test/LogSentinel-GUI/` (one-directory GUI build,
185 files, 105,363,740 B). Qt/PySide6 core licensing is covered separately in
`../qt/INVENTORY.md` and is not repeated here, except where a Qt binary embeds or
requires non-Qt code.

**This document is an engineering inventory, not a legal opinion, and it makes no
compliance claim.** Licence names below are the licences the upstream projects
publish; the licence texts themselves have **not** been collected yet, by design.

## Executive summary

- **No licence or notice material exists anywhere in the package.** A full-tree
  search for `*licen*`, `*copying*`, `*notice*`, `*attribut*`, `*.txt`, `*.md`,
  `*.rst` returned **zero files**. Every obligation listed below is therefore
  currently unmet in the shipped artefact.
- **62 PE binaries** ship; **28 load** in a normal analyst session. The largest
  bundled-and-never-loaded items are Mesa llvmpipe (`opengl32sw.dll`, 20.6 MB) and
  Qt PDF (`Qt6Pdf.dll` + `qpdf.dll`, 4.7 MB).
- **Nine distinct permissively-licensed library families** are statically compiled
  into binaries rather than shipped as separate DLLs: zlib-ng (×2), bzip2, liblzma,
  Zstandard, mpdecimal, libpng, libjpeg-turbo, libtiff, libwebp, plus FreeType,
  HarfBuzz and PCRE2 inside Qt, PDFium inside Qt PDF, and Mesa + LLVM inside
  `opengl32sw.dll`.
- **Three components carry obligations that are easy to miss:**
  1. **OpenSSL 3.5.9** — Apache-2.0, which requires reproducing its `NOTICE` file,
     not just the licence text.
  2. **PyInstaller 6.22.3** — GPL-2.0-or-later **with the bootloader exception**;
     the bootloader and its bootstrap modules are embedded in the `.exe`, and the
     exception's conditions attach to that embedded code.
  3. **CPython 3.14.10** — PSF-2.0 requires the PSF licence *and* the PSF copyright
     notice; the runtime also carries Unicode data under the Unicode licence.
- **Two version mismatches were found in shipped binaries**, contradicting earlier
  documentation-based assumptions: `libjpeg-turbo` reports **3.2.0** (not 3.2.1),
  and the MSVC runtime is present in **two different builds** (14.51 and 14.44),
  with the process loading a mix.
- **One host-OS dependency was discovered:** `Qt6Core.dll` has a hard import on
  `icuuc.dll`, resolved at runtime from `C:\Windows\System32` (Microsoft-signed
  "The ICU Project" build 64.2). ICU is **not** bundled, so there is no ICU
  redistribution obligation — but the package silently requires a Windows build
  that ships system ICU.
- **No copyleft conflict was identified** among the remaining components — the only
  dual-licensed item is FreeType (FTL *or* GPLv2), which must be documented under
  the FTL branch, and LLVM 3.6.2 predates LLVM's Apache switch (NCSA-style terms).

## Evidence standard

| Tag | Meaning |
|---|---|
| **verified** | Version string, PE version resource, or runtime observation read from the shipped artefact or its wheel metadata |
| **probable** | Presence proven in the binary, exact version taken from vendor documentation that has not yet been captured |
| **unresolved** | Component is expected from vendor documentation but could not be evidenced in this build, or its version is not recoverable from the binary |

Every version tagged *probable* or *unresolved* must be pinned when the vendor
attribution pages are captured in the next step. Do not transfer a *probable*
version into a published NOTICE file without that confirmation.

## 1. Python runtime and standard library

| Component | Version | Bundled at | Licence | Obligation | Source | Confidence |
|---|---|---|---|---|---|---|
| CPython runtime | 3.14.10 (PE resource) | `_internal/python314.dll` 6,816,992 B, `_internal/python3.dll` 73,952 B | PSF-2.0 | Reproduce PSF licence **and** PSF copyright notice ("Copyright © 2001-2026 Python Software Foundation") | <https://docs.python.org/3/license.html> | verified |
| CPython standard library | 3.14.10 | `_internal/base_library.zip` 1,396,401 B, 155 entries (`encodings/`, `re/`, `collections/`, plus `hashlib`, `sqlite3`, `bz2`, `lzma`, `compression.zstd`, `ssl` in the embedded PYZ) | PSF-2.0 | covered by CPython notice; no separate notice | as above | verified |
| Unicode Character Database | 16.0.0 | inside `_internal/unicodedata.pyd` 758,496 B | Unicode licence (Unicode-3.0-style) | Attribution/"Unicode Data Files" notice | <https://www.unicode.org/license.txt> | verified version, licence text to collect |
| zlib-ng | version not recoverable | statically inside `_internal/python314.dll` (strings `1.3.1`, `zlib-ng`) | zlib licence | Retain copyright + licence notice in binary distribution | <https://github.com/zlib-ng/zlib-ng> | presence verified, version **probable** |
| bzip2 | **1.0.8** ("1.0.8, 13-Jul-2019") | statically inside `_internal/_bz2.pyd` 87,776 B | bzip2-1.0.6 licence (BSD-like, 4 clauses incl. "origin must not be misrepresented", "altered versions must be plainly marked") | Reproduce licence; mark modifications if patched | <https://sourceware.org/bzip2/> | verified |
| liblzma (XZ Utils) | not recoverable | statically inside `_internal/_lzma.pyd` 160,992 B | public domain / 0BSD per XZ Utils (liblzma only; the XZ *tools* are GPL) | None if 0BSD; confirm which applies to this copy | <https://tukaani.org/xz/> | presence verified, licence **probable** |
| Zstandard | **1.5.7** | statically inside `_internal/_zstd.pyd` 503,520 B | BSD-3-Clause (or GPLv2 at the user's option) | Reproduce BSD notice | <https://github.com/facebook/zstd> | verified |
| mpdecimal | **4.0.0** (build path `externals\mpdecimal-4.0.0`) | statically inside `_internal/_decimal.pyd` 290,016 B | MIT-style mpdecimal licence | Reproduce copyright + licence | <https://www.bytereef.org/mpdecimal/> | verified |
| libffi | — | **not bundled** (no `_ctypes.pyd` in package) | — | none | — | verified absent |
| expat / Tcl-Tk / multiprocessing | — | **not bundled** | — | none | — | verified absent |

Note: `unicodedata.pyd` and `_decimal.pyd` are bundled but were **not loaded** in the
observed session.

## 2. Cryptography and networking

| Component | Version | Bundled at | Licence | Obligation | Source | Confidence |
|---|---|---|---|---|---|---|
| OpenSSL | **3.5.9** ("OpenSSL 3.5.9 29 Sep 2026", built Tue 29 Sep 2026, platform `VC-WIN64A-masm`, compiler `cl ... /MD /O2`) | `_internal/libcrypto-3.dll` 6,021,880 B, `_internal/libssl-3.dll` 1,308,920 B | Apache-2.0 | Reproduce the Apache-2.0 licence **and OpenSSL's `NOTICE` file**; state any modifications; no trademark use | <https://www.openssl.org/source/license.html> | verified |
| Windows SChannel TLS backend | OS component | `plugins/tls/qschannelbackend.dll` (imports `ncrypt.dll`) | Windows OS | none | — | verified |
| Qt TLS plugins | 6.12.0.0 | `qopensslbackend.dll`, `qcertonlybackend.dll` (bundled, **not loaded**) | LGPLv3/commercial | covered by Qt notice | see `../qt/INVENTORY.md` | verified |
| ICU | **not bundled** — loaded from `C:\Windows\System32\icuuc.dll`, `icuin.dll`, `icu.dll` (v64.2.0.0, signer `CN=Microsoft Windows`) | host OS | Microsoft/ICU (OS component) | none for redistribution; but a **host requirement** | — | verified at runtime |
| CA certificate store | **none bundled** (`OPENSSLDIR: "C:\Program Files\Common Files\SSL"`) | — | — | none; no TLS is performed by the GUI | — | verified |

`libssl-3.dll` was **not loaded** in the observed session; `libcrypto-3.dll` was
(imported by `_hashlib.pyd` for hashing, not for TLS).

## 3. Database

| Component | Version | Bundled at | Licence | Obligation | Source | Confidence |
|---|---|---|---|---|---|---|
| SQLite | **3.50.4** (`sqlite3.dll` version resource 3.50.4.0, CompanyName "SQLite3"; FTS5 source id `2025-07-30 19:33:53 4d8adfb3…`; 287 exports incl. `sqlite3_rtree_*`) | `_internal/sqlite3.dll` 1,584,864 B, imported by `_internal/_sqlite3.pyd` | Public domain | None legally; a courtesy credit is conventional ("SQLite is in the public domain") | <https://www.sqlite.org/copyright.html> | verified |

Loaded at runtime: both `_sqlite3.pyd` and `sqlite3.dll`.

## 4. Compression and numerics

| Component | Version | Bundled at | Licence | Obligation | Confidence |
|---|---|---|---|---|---|
| zlib-ng (Qt copy) | not recoverable (`z_deflate`, `z_inflateCodesUsed`, `z_deflateUsed`, `z_crc32_combine_gen64` symbols; "QResource: error decompressing zlib content") | statically inside `_internal/PySide6/Qt6Core.dll` | zlib licence | Retain notice | presence verified, version **probable** (Qt 6.12 attribution page needed) |
| zlib-ng (CPython copy) | "1.3.1 / zlib-ng" | statically inside `_internal/python314.dll` | zlib licence | Retain notice | presence verified, version **probable** |
| bzip2 | 1.0.8 | `_internal/_bz2.pyd` | bzip2 licence | see §1 | verified |
| liblzma | unresolved | `_internal/_lzma.pyd` | 0BSD/public domain | see §1 | presence verified |
| Zstandard | 1.5.7 | `_internal/_zstd.pyd` | BSD-3-Clause | see §1 | verified |
| mpdecimal | 4.0.0 | `_internal/_decimal.pyd` | MIT-style | see §1 | verified |
| "zlib", "brotli", "zstd" (OpenSSL provider names) | n/a | strings inside `libcrypto-3.dll` only; **no codec library is bundled or imported** | — | none unless the codecs are actually linked; **unresolved** whether any codec code is compiled in | strings only |

## 5. Graphics, text rendering, and document support

| Component | Version | Bundled at | Licence | Obligation | Source | Confidence |
|---|---|---|---|---|---|---|
| FreeType | unresolved (no version string; `FT_*` symbols and `QFontEngineFT` strings present) | statically inside `_internal/PySide6/Qt6Gui.dll` | **FTL or GPLv2** (dual) | Must be documented under the FTL branch; the FTL requires attribution ("Portions of this software are copyright © The FreeType Project") | <https://freetype.org/license.html> | presence verified, dual-licence choice **must be recorded** |
| HarfBuzz | unresolved (`hb_font`, `hb_blob`, `hb_shape_plan_create2` symbols) | statically inside `Qt6Gui.dll` | MIT (old-style) | Reproduce copyright + licence | <https://github.com/harfbuzz/harfbuzz> | presence verified, version **probable** |
| libpng | **1.6.58** (string `1.6.58`, `png_read_update_info`, `png_write_info`, "libpng warning: %s") | statically inside `Qt6Gui.dll` | libpng-2.0 | Reproduce copyright + licence | <http://www.libpng.org/pub/png/src/libpng-LICENSE.txt> | verified |
| PCRE2 | unresolved (`PCRE2` error strings ×19, e.g. "this version of PCRE2 does not have Unicode support") | statically inside `Qt6Core.dll` | BSD-3-Clause | Reproduce copyright + licence | <https://github.com/PCRE2Project/pcre2> | presence verified, version **probable** |
| C++/WinRT | **2.0.250303.1** (`C++/WinRT version:2.0.250303.1`) | statically compiled into `Qt6Core.dll` | MIT | Reproduce copyright + licence | <https://github.com/microsoft/cppwinrt> | verified |
| libjpeg-turbo | **3.2.0** (`libjpeg-turbo version 3.2.0 (build )`; copyright `1991-2026`) | statically inside `plugins/imageformats/qjpeg.dll` 592,696 B **and** `qtiff.dll` 991,032 B | BSD-3-Clause + IJG + zlib | Reproduce all three notices | <https://github.com/libjpeg-turbo/libjpeg-turbo> | verified (**corrects the earlier 3.2.1 assumption**) |
| libtiff | unresolved; binary only shows "Since libtiff 4.5.1…" doc string and `LIBTIFF_*` symbols | statically inside `plugins/imageformats/qtiff.dll` | libtiff licence (BSD-like) | Reproduce copyright + licence | <https://gitlab.com/libtiff/libtiff> | presence verified (≥4.5.1), version **unresolved** |
| libwebp | unresolved (`VP8X`, `WEBP` fourccs; no version string) | statically inside `plugins/imageformats/qwebp.dll` 566,072 B | BSD-3-Clause | Reproduce copyright + licence | <https://chromium.googlesource.com/webm/libwebp> | presence verified, version **probable** |
| Mesa (llvmpipe software rasteriser) | **11.2.2** (`Mesa 11.2.2`) | `_internal/PySide6/opengl32sw.dll` 20,639,544 B (**never loaded** in observed session) | MIT (Mesa) | Reproduce copyright + licence + Qt's llvmpipe attribution page | <https://docs.mesa3d.org/license.html>, <https://doc.qt.io/qt-6/qt-attribution-llvmpipe.html> | verified |
| LLVM | **3.6.2** (`llvm-mc (based on LLVM 3.6.2)`) | statically inside `opengl32sw.dll` | **NCSA/UIUC** (LLVM predates its 2019 Apache-2.0 switch) | Reproduce NCSA notice; do not describe as Apache-2.0 | <https://llvm.org/releases/3.6.2/LICENSE.TXT> | version verified, licence text to collect |
| PDFium | unresolved (single string `PDFIUM_HasGeneratedAP`; `JBIG2Decode`, `JPXDecode` handlers) | statically inside `_internal/PySide6/Qt6Pdf.dll` 4,623,672 B (**never loaded**) | BSD-3-Clause (Chromium-style) | Reproduce copyright + licence + per-snapshot third-party attributions | <https://pdfium.googlesource.com/pdfium/+/refs/heads/main/LICENSE> | presence verified, version **unresolved** |
| Chromium / Abseil / AGG / lcms / fast_float / ICU inside Qt PDF | **not evidenced** in this build (no `Chromium`, `absl`, `lcms`, `ICU`/`icudt` strings) | — | (would be BSD/MIT/Apache/LGPL if present) | **unresolved** — Qt's PDF docs describe PDFium as a Chromium snapshot; the shipped binary does not surface them | <https://doc.qt.io/qtpdf/qtpdf-licensing.html> | unresolved |
| TinyCBOR | not evidenced (`qt_cbor_*` symbols are Qt's own helpers) | — | (MIT if present) | unresolved | <https://github.com/intel/tinycbor> | unresolved |
| MD4C (Markdown) | not evidenced (only the `.markdown` file extension string) | — | (MIT if present) | unresolved | <https://github.com/mity/md4c> | unresolved |
| double-conversion | not evidenced (no `DoubleToStringConverter`, no `double_conversion` strings) | — | (BSD-3 if present) | unresolved | <https://github.com/google/double-conversion> | unresolved |
| libpsl / Public Suffix List | not evidenced in `Qt6Network.dll` | — | (MIT if present) | unresolved | <https://github.com/rockdaboot/libpsl> | unresolved |
| Pixman | **not present** (expected: Windows Qt builds do not use it) | — | — | none | — | verified absent |
| Brotli | not evidenced as code; name appears only in OpenSSL provider lists | — | (MIT if present) | unresolved | <https://github.com/google/brotli> | unresolved |

Qt's image-format plugins `qico`, `qgif`, `qicns`, `qtga`, `qwbmp`, `qsvg` and the
icon engine `qsvgicon` import no external codec DLLs; any inlined codec code is
covered by the Qt notice except where noted above.

## 6. Build and packaging toolchain

| Component | Version | Embedding | Licence | Obligation | Confidence |
|---|---|---|---|---|---|
| PyInstaller bootloader | 6.22.3 (build log; no version string in the `.exe`) | statically linked into `LogSentinel-GUI.exe` 2,386,859 B (PE subsystem 2, no `RT_VERSION`) | GPL-2.0-or-later **with the bootloader exception** | Reproduce the GPLv2 text **and** the exception text; the exception's conditions (notably: do not ship a modified bootloader, and the exception applies only to programs distributed under terms compatible with it) attach to this embedded code | version verified from build log |
| PyInstaller Python runtime modules | 6.22.3 | embedded in the `.exe` CArchive: `pyiboot01_bootstrap`, `pyimod01_archive`, `pyimod02_importers`, `pyimod03_ctypes`, `pyimod04_pywin32`, `pyi_rth_inspect`, `pyi_rth_pyside6`, plus the `gui_entry` script and `struct` | as above | same | verified |
| pyinstaller-hooks-contrib | 2026.10 | **build-time only** — no shipped artefact; its hooks directory contains **0** runtime hooks and neither shipped rthook originates from it | Apache-2.0 | none for the binary; applicable only to build scripts if redistributed | verified |
| Microsoft Visual C++ runtime | **14.51.36247.0** (`_internal/VCRUNTIME140.dll`, `VCRUNTIME140_1.dll`) **and 14.44.35211.0** (`PySide6/`, `shiboken6/` copies of `VCRUNTIME140`, `MSVCP140`, `MSVCP140_1`, `MSVCP140_2`) | `_internal/` ×2 + `PySide6/` ×5 + `shiboken6/` ×3 = 10 files, 1,940,792 B | Microsoft Visual Studio redistributable terms | Distribute only under Microsoft's redistributable grant; do not modify; see §9 item 2 | versions verified |
| MSVC toolchain (build-time) | 14.44.35211.0 / 14.41 Python toolset | build only | Microsoft | none for the binary beyond the runtime grant | probable |

## 7. Loaded versus merely bundled

Runtime observation (isolated `USERPROFILE`, window title
`LogSentinel - Defensive Log Analysis - LogSentinel`, 102 modules, clean close,
0 `_MEI` residue):

- **Loaded (28 of 62 PEs):** the exe, `python314`, `python3`, `VCRUNTIME140` (14.51),
  `shiboken6/VCRUNTIME140_1` + `shiboken6/MSVCP140`, `shiboken6.abi3.dll`,
  `Shiboken.pyd`, `pyside6.abi3.dll`, `QtCore/QtGui/QtSvg/QtWidgets.pyd`,
  `Qt6Core`, `Qt6Gui`, `Qt6Svg`, `Qt6Widgets`, `qwindows.dll`,
  `qmodernwindowsstyle.dll`, `_hashlib`, `_sqlite3`, `sqlite3.dll`, `libcrypto-3`,
  `_bz2`, `_lzma`, `_zstd`.
- **Bundled but never loaded:** `opengl32sw.dll` (Mesa+LLVM, 20.6 MB), `Qt6Pdf.dll` +
  `qpdf.dll` (4.7 MB), `Qt6Network`/`QtNetwork.pyd`, `libssl-3.dll`, `_ssl`, `_socket`,
  `select`, `_decimal`, `unicodedata`, 20 of 21 plugins (all image formats, the other
  three platform plugins, TLS backends, UI Touch), and 7 of 10 MSVC runtime copies.
- Consequence for notices: obligations follow **what is distributed**, not what is
  loaded. Mesa/LLVM, PDFium and the image-format codec notices are required because
  the files ship, even though this workflow never touches them.

## 8. Obligation summary by licence family

| Licence family | Components | Typical requirement | Collected? |
|---|---|---|---|
| PSF-2.0 | CPython, stdlib | licence text + PSF copyright notice | no |
| Apache-2.0 | OpenSSL 3.5.9 (also pyinstaller-hooks-contrib, build-time) | licence text + reproduce `NOTICE`; state modifications | no |
| GPL-2.0-or-later + bootloader exception | PyInstaller | licence text + exception text; no modified bootloader | no |
| MIT / MIT-style | mpdecimal, HarfBuzz, C++/WinRT, Mesa, TinyCBOR(?), MD4C(?) | copyright + permission notice | no |
| BSD-3-Clause | Zstandard, libjpeg-turbo, PCRE2, libwebp, PDFium | copyright + 3 clauses + no-endorsement | no |
| BSD-like (zlib) | zlib-ng (×2) | copyright + "altered source versions must be marked" | no |
| BSD-like (bzip2, libtiff, libpng) | bzip2 1.0.8, libtiff, libpng 1.6.58 | copyright + origin/marking clauses | no |
| NCSA/UIUC | LLVM 3.6.2 | copyright + 3 clauses | no |
| FTL or GPLv2 | FreeType | elect FTL and reproduce its attribution | no |
| Public domain / 0BSD | SQLite 3.50.4, liblzma | none / attribution optional | no |
| Unicode | UCD 16.0.0 | Unicode licence notice | no |
| Microsoft redistributable | VC++ runtime 14.51 / 14.44 | Microsoft's redistributable terms | no |

The only reciprocal (copyleft) exposure in this set is **PyInstaller's GPLv2 with the
bootloader exception** and **FreeType's optional GPLv2 branch**. Everything else is
permissive. That does not by itself make the distribution compliant — no notice
payload exists yet.

## 9. Ambiguities, mismatches and unresolved items

1. **No notice payload at all.** Zero licence files ship. This is the single largest
   gap and affects every row above.
2. **MSVC runtime version skew.** Root `VCRUNTIME140.dll` is 14.51.36247.0 while
   `PySide6/` and `shiboken6/` carry 14.44.35211.0 copies of `VCRUNTIME140`,
   `MSVCP140`, `MSVCP140_1`, `MSVCP140_2`. The observed process loaded **both**
   generations (`_internal\VCRUNTIME140.dll` 14.51 **and**
   `shiboken6\VCRUNTIME140_1.dll` + `shiboken6\MSVCP140.dll` 14.44). Microsoft's
   redistribution terms expect a single redistributable version, and mixing
   `MSVCP140` with a newer `VCRUNTIME140` is not a supported configuration even
   though it worked here. This is a packaging-hygiene issue with licensing
   consequences, not a proven defect.
3. **Host ICU dependency.** `Qt6Core.dll` imports `icuuc.dll`; the package does not
   carry it, so it resolves from `System32`. On a Windows build without system ICU
   the application would fail to start. No redistribution obligation, but a
   minimum-OS constraint that must be stated or eliminated.
4. **Qt PDF composition unverified.** The binary evidences PDFium (`PDFIUM_*`
   symbol) but not Chromium, Abseil, AGG, lcms, ICU or fast_float, all of which Qt's
   documentation attributes to the PDF module. Either the shipped Qt PDF is built
   with fewer bundled dependencies than the documentation implies, or the strings
   were stripped. Needs Qt's per-module attribution page before any notice text is
   written.
5. **Version drift against earlier assumptions.** libjpeg-turbo is **3.2.0**, not
   3.2.1. Several versions (zlib-ng, FreeType, HarfBuzz, libtiff, libwebp, liblzma,
   PDFium) are not recoverable from the binary and must be taken from vendor
   attribution documents, not from memory.
6. **Quantities do not match the Qt PDF licensing model.** Qt PDF is bundled but
   never imported; Mesa llvmpipe is bundled but never selected. Both are removable
   by packaging decision, and removing them removes the largest attribution
   surface (the llvmpipe attribution page and the whole Qt PDF/PDFium chain).
7. **OS-provided ICU is Microsoft-branded but ICU-licensed** ("CompanyName: The ICU
   Project", version 64.2.0.0). Any statement about ICU must say it is exercised
   through the operating system, not redistributed by LogSentinel.
8. **No SBOM exists.** There is no machine-readable component list in the repo, so
   this report is the only inventory; it should become the basis of one.

## 10. Potential distribution blockers

| # | Blocker | Impact |
|---|---|---|
| 1 | Zero licence/notice files in the package while the package ships PSF, Apache-2.0, GPLv2-with-exception, BSD, MIT, FTL, Unicode and Microsoft-redistributable code | Blocks any public release |
| 2 | OpenSSL `NOTICE` file reproduction (Apache-2.0 §4(d)) not prepared | Blocks any public release |
| 3 | PyInstaller bootloader exception text not prepared, and no statement that the bootloader is unmodified | Blocks any public release |
| 4 | MSVC runtime duplication/version skew unresolved | Blocks a defensible "uses the Microsoft redistributable" statement |
| 5 | FreeType dual-licence branch not recorded (FTL vs GPLv2) | Blocks an accurate notice; choosing GPLv2 would change the licence posture of the whole bundle |
| 6 | Undetermined PDFium/Chromium/LLVM/Mesa attribution sets | Blocks completeness of the third-party notice for two large bundled blobs |
| 7 | Undetermined minimum Windows version (system ICU) | Blocks a supported-platform statement |
| 8 | Unpinned versions for 7+ components | Blocks an accurate NOTICE/source list |

## 11. Recommended order for the next licence-preparation steps

1. **Freeze the inventory.** Record the package definition (185 files,
   105,363,740 B, exe `86517ebc…`) in the report and treat this file list as the
   release baseline; re-hash after any packaging change.
2. **Collect vendor attribution pages first** (they resolve the version gaps):
   Qt `licenses-used-in-qt.html` for the shipped modules, `qt-attribution-llvmpipe.html`
   and `qt-attribution-llvm.html` for `opengl32sw.dll`, and the Qt PDF licensing page
   for PDFium.
3. **Collect the Qt-bundled third-party texts**: zlib-ng, PCRE2, FreeType (FTL),
   HarfBuzz, libpng, libjpeg-turbo, libtiff, libwebp, C++/WinRT, PDFium.
4. **Collect the standalone component texts**: CPython PSF-2.0 + PSF notice,
   OpenSSL Apache-2.0 + `NOTICE`, SQLite public-domain statement, Zstandard, mpdecimal,
   bzip2, liblzma, Unicode licence, Mesa MIT, LLVM 3.6.2 NCSA, libjpeg-turbo IJG/zlib.
5. **Collect PyInstaller's GPLv2 text and bootloader exception** and record that the
   bootloader is used unmodified.
6. **Obtain the Microsoft redistributable terms** and decide whether to normalise
   the runtime to one VC++ redistributable version; do not write the notice until
   that decision is made.
7. **Resolve the FreeType branch** (FTL) in writing, and the Qt PDF / llvmpipe
   keep-or-drop decision, since both shrink or expand the notice set.
8. **Assemble** a single `THIRD-PARTY-NOTICES` set plus a package-level
   `LICENSES/` directory, then re-verify that every row in §8 has a collected file.
9. **Only after 1–8**, revisit the LGPLv3 §4(d)(1)/§4(d)(0) packaging decision and
   produce the release archive.

## Appendix A — evidence highlights

| Evidence | Where |
|---|---|
| `OpenSSL 3.5.9 29 Sep 2026` / `built on: Tue Sep 29 15:10:02 2026 UTC` / `platform: VC-WIN64A-masm` | `libcrypto-3.dll` |
| `3.50.4` + FTS5 source id `2025-07-30 19:33:53 4d8adfb3…` + 287 exports | `sqlite3.dll` |
| `1.0.8, 13-Jul-2019` | `_bz2.pyd` |
| `1.5.7` | `_zstd.pyd` |
| `externals\mpdecimal-4.0.0\libmpdec\typearith.h` | `_decimal.pyd` |
| `16.0.0` | `unicodedata.pyd` |
| `Mesa 11.2.2`, `llvm-mc (based on LLVM 3.6.2)` | `opengl32sw.dll` |
| `libjpeg-turbo version 3.2.0 (build )` | `qjpeg.dll`, `qtiff.dll` |
| `LIBTIFF_*` symbols, `Since libtiff 4.5.1…` | `qtiff.dll` |
| `libpng warning: %s`, `1.6.58` | `Qt6Gui.dll` |
| `this version of PCRE2 does not have Unicode support` | `Qt6Core.dll` |
| `C++/WinRT version:2.0.250303.1` | `Qt6Core.dll` |
| `Qt 6.12.0 (x86_64-little_endian-llp64 shared (dynamic) release build; by MSVC 2022)` | `Qt6Core.dll` |
| `PDFIUM_HasGeneratedAP` | `Qt6Pdf.dll` |
| `pyi_rth_pyside6`, `pyi_rth_inspect`, `pyimod01..04`, `pyiboot01_bootstrap` | CArchive of `LogSentinel-GUI.exe` (10 entries) |
| `icuuc.dll`, `icu.DLL` loaded from `System32` | runtime module list |

## Appendix B — files inspected

- `dist/gui-ondir-test/LogSentinel-GUI/` — all 185 files (sizes, PE resources,
  import/delay-import tables, export tables, embedded strings, CArchive/PYZ TOCs,
  `base_library.zip` TOC).
- Build environment: `.venv-build-gui/Lib/site-packages/*.dist-info/METADATA`
  (licence declarations), `PyInstaller/hooks/rthooks/` (origin of shipped rthooks),
  `_pyinstaller_hooks_contrib/stdhooks/` (0 runtime hooks).
- Runtime: one isolated launch, 102 loaded modules, clean close, 0 residue.
- Prior findings reused: `../qt/INVENTORY.md`, the virtual-keyboard exclusion audit,
  and the licensing investigation in the release-readiness audit.

No file in the package, the build environment, or the source tree was modified;
nothing was committed or pushed.
