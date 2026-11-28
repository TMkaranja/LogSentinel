# LogSentinel Third-Party Notices — Proposal Only

> **DRAFT — NOT A FINAL RELEASE NOTICE OR DISTRIBUTION AUTHORIZATION.** This proposal is based on the inspected Phase 1 Windows onedir candidate only. Its component mappings and license scope are incomplete. Do not place it in a distributed package or rely on it as evidence that redistribution is permitted. The current candidate remains **NOT CLEARED FOR DISTRIBUTION**.

## Scope of this proposal

Inspected artifact: `dist/gui-ondir-trim-test/LogSentinel-GUI/` — 182 files / 80,058,228 bytes. The root executable SHA-256 is `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.

This package contains no `.txt`, `.md`, or `.rst` license/notice document. The findings below describe files and component evidence in this exact candidate; a version string, wheel entry, signature, or upstream notice does not by itself establish source identity, license election, permission, or that a notice is sufficient. The repository's collected license texts are review material and are not currently included in the candidate package.

## LogSentinel

The repository's root `LICENSE` identifies LogSentinel as MIT-licensed and attributes it to Moses Karanja Thuo (2026). That is the project's own license, not a license for bundled third-party software. The GUI package inventory identifies the application modules and its GUI assets; the project license does not resolve third-party terms below.

```text
MIT License

Copyright (c) 2026 Moses Karanja Thuo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Components observed in the candidate

The table is an **engineering evidence summary, not a statement that the listed text is the applicable or elected license**. “Local review material” names repository files only; it does not mean that a final distribution must use these exact files or that they are already delivered to recipients.

| Component / package evidence | License or attribution material identified for review | Current limitation |
|---|---|---|
| **Qt 6.12.0, PySide6 6.12.0, Shiboken6 6.12.0** — Qt Core, Gui, Network, Svg, Widgets, bindings, support files, plugins and 99 `.qm` catalogs | Qt/PySide materials and the repository's `licenses/LGPL-3.0.txt`, `licenses/GPL-3.0.txt`; Qt use/copyright notice appears in collected vendor material | No per-binary license election or commercial entitlement is established. PySide metadata and public Qt for Python wording differ on a GPLv2 alternative. Shiboken-specific scope and catalog-by-catalog source, contributor and license mapping remain open. The catalogs are a separate scope and are not presumed to be LGPL libraries. |
| **CPython 3.14.10** — runtime, standard-library code and extensions | Candidate PSF License Version 2 text and attribution in `licenses/third-party/notices/cpython/LICENSE.txt`, `COPYRIGHT-AND-ATTRIBUTION.txt`, and `README.rst` | Runtime version is reported, but the exact Windows source/build inputs are not matched. Embedded libraries have their own terms. A separate Microsoft Distributable Code section in the local interpreter license requires review for applicability and affected files. |
| **Unicode Character Database 16.0.0** — `unicodedata.pyd` evidence | Unicode License V3 and UCD readme in `licenses/third-party/notices/unicode/` | Version evidence exists; exact CPython build-input mapping remains unverified. |
| **OpenSSL 3.5.9** — `libcrypto-3.dll`, `libssl-3.dll` | Apache License 2.0 text and tag acknowledgements in `licenses/third-party/notices/openssl/` | Exact DLL source/build match is open. The inspected tag/archive evidence did not identify a file named `NOTICE`; acknowledgements are not relabeled as a NOTICE. |
| **SQLite 3.50.4** — `sqlite3.dll`, `_sqlite3.pyd` | SQLite public-domain/copyright page in `licenses/third-party/notices/sqlite/copyright.html` | The upstream page describes a public-domain dedication; it is courtesy attribution, not a license text. Exact build-source hash is not established. |
| **bzip2 1.0.8** — `_bz2.pyd` | Version-tagged bzip2 license in `licenses/third-party/notices/bzip2/LICENSE.txt` | Version evidence agrees; exact embedded source and patch state are not matched. |
| **Zstandard 1.5.7** — `_zstd.pyd` and Python `compression.zstd` | BSD-style and GPLv2 alternatives are in `licenses/third-party/notices/zstandard/alternatives/` | The alternatives are not cumulative; no downstream license choice is recorded. Neither may be presented here as the elected license. |
| **mpdecimal 4.0.0** — `_decimal.pyd` | Copyright and terms in `licenses/third-party/notices/mpdecimal/COPYRIGHT.txt` | Version/build-path evidence exists, but exact embedded source and patch state are not matched. |
| **PyInstaller 6.22.3** — frozen bootloader, loader, hooks and helper modules | Combined `licenses/third-party/notices/pyinstaller/COPYING.txt` contains distinct GPL/Bootloader Exception and Apache-2.0 scopes | Frozen entries are observed, but entry-to-source mapping and bootloader modification status are unresolved. The Bootloader Exception does not cover every runtime hook/module. |
| **Microsoft Visual C++ runtime** — ten DLL copies: two root copies reported as 14.51.36247.0 and eight Qt-wheel copies reported as 14.44.35211.0 | No Microsoft redistribution terms or rights document is established in the notice collection | The eight nested files match Qt wheel payloads and `RECORD` hashes and are Qt-signed. That does not establish Microsoft source lineage, Qt's supplier rights, or downstream redistribution eligibility. All ten remain an independent release blocker. |

### Additional Qt-linked code and plugin candidates

Package and binary evidence also identifies or supports the presence of FreeType, HarfBuzz, libpng, PCRE2/possible SLJIT, libjpeg-turbo, libtiff, libwebp, C++/WinRT and zlib-compatible code within Qt libraries/plugins. Their exact source snapshots, file-level terms, license elections, complete attributions, and (for libwebp) patent materials are not all established for these binaries. Collected materials—including both alternative FreeType texts—are candidates for technical/legal review, not a completed notice set. Exact zlib-compatible implementation is unresolved. No notice or license is invented here for liblzma/XZ-derived code, libtiff, libwebp, or any other unresolved component.

## Components not listed as shipped

The inspected trimmed package does **not** contain Qt PDF (`Qt6Pdf.dll`), the qpdf image plugin (`qpdf.dll`), or Mesa software OpenGL (`opengl32sw.dll`). PDFium/Qt PDF and Mesa/LLVM notices from historical inventories are therefore not included as shipped-component attributions in this proposal. Re-inventory if a later package restores any such payload.

## Before this can become a recipient notice

A release owner and qualified counsel must first establish the exact distribution model and rights, match source/build and file-level license records to the final package, resolve license elections and missing attributions, select any required source/relinking or other compliance route, and curate the corresponding license texts and instructions. Then this draft must be revised against the final artifact and placed in the authorized delivery with an updated hash manifest. Until those steps are complete, this file is **proposal material only**.
