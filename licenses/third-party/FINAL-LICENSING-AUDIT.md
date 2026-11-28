# Final Licensing Audit — Verified Trimmed Windows GUI Package

**Status: NOT CLEARED FOR DISTRIBUTION.** This is a consolidated engineering and source-evidence audit, not legal advice, a compliance opinion, or a release approval. It records what was observed in the named package, what official upstream documentation says, and what remains unverified. It does not establish that any license grant applies to LogSentinel's particular build or distribution model.

## 1. Executive conclusion

The trimmed onedir GUI package was functionally exercised and its identity rechecked. It contains Qt/PySide6, CPython and its native modules, OpenSSL, PyInstaller bootloader/runtime code, image-codec implementations, and ten Microsoft Visual C++ runtime DLL files. Some shipped components have associated license texts or attribution sources in this repository, but those materials are a **source collection for review, not a complete, package-matched release notice set**. The package itself contains no license/notice documents.

Distribution should remain on hold until, at minimum:

1. Qualified counsel reviews the Qt/PySide6 license basis and the intended LGPLv3 distribution model, including replaceability, notices, and corresponding-source/relinking questions.
2. Qt confirms the licensing/provenance basis for the Microsoft runtime DLLs carried in the PySide6/Shiboken wheels, and the project establishes eligibility for all ten VC++ DLL copies under the applicable Microsoft terms.
3. A source/build-to-binary evidence package is assembled for bundled dependencies, particularly Qt's static components, CPython-linked zlib/liblzma/Zstandard code, and the applicable CPython Microsoft Distributable Code terms.
4. A reviewed, version-pinned notice bundle and source/corresponding-source access plan are prepared against the exact release candidate, then validated after packaging.

The earlier GUI test, a valid code signature, an upstream version match, or the technical ability to replace a Qt DLL is not by itself evidence of legal compliance or permission to redistribute.

## 2. Scope and verified artifact

### Audited package

- Directory: `dist/gui-ondir-trim-test/LogSentinel-GUI/`
- Inventory: **182 regular files**, **80,058,228 bytes**.
- Executable: `LogSentinel-GUI.exe`, **2,386,859 bytes**, SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- Package file types: 42 DLLs, 16 PYDs, 99 Qt `.qm` translations, 22 SVGs, one ZIP, one ICO, and one EXE.
- The package contains no `.txt`, `.md`, or `.rst` notice document.
- `PySide6/Qt6Pdf.dll`, `PySide6/plugins/imageformats/qpdf.dll`, and `PySide6/opengl32sw.dll` are absent. Qt PDF/PDFium and Mesa/LLVM materials from earlier package inventories therefore do not automatically describe this trimmed artifact. The compatibility report documents the exact exclusions and their still-untested RDP, GPU-less/software-rendering, and high-DPI cases.
- Selected package hashes: `_internal/libcrypto-3.dll` (6,021,880 bytes) SHA-256 `75495fe0e079ab00d49be740d3c710a0b94e3f74f9648cb7cc9f768fc7f52319`; `_internal/libssl-3.dll` (1,308,920 bytes) SHA-256 `8957182a9c385bfd9f3f790921de2ddc614cf91f99edbed4e9e5446a46504e32`.

The 182-file inventory and byte total were checked before and after the isolated end-to-end workflow; the package remained unchanged. Ten runtime DLL paths, versions, sizes, hashes, and signatures are recorded in `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`. The test covered five GUI pages, selection and analysis of `samples/auth.log`, JSON/HTML exports, settings persistence after relaunch, and clean shutdown. This is product-function evidence for one environment, not a licensing test or broad compatibility claim.

### Scope boundary and preservation

This audit reconciles evidence to the trimmed 182-file package, not to the older 185-file `dist/gui-ondir-test/LogSentinel-GUI/` builds described by `OTHER-COMPONENTS-INVENTORY.md`, `ATTRIBUTION-SOURCE-REGISTER.md`, and `qt/INVENTORY.md`. Those older reports remain historical source records and must not be cited as though their complete package inventories match the trimmed package. The trimmed-package map is `TRIMMED-PACKAGE-NOTICE-MAP.md`.

The existing `release/` artifacts, pre-existing source/spec/worktree changes, tests, dependencies, package files, and notice/source documents were not changed by this audit. No package was rebuilt, no DLL was replaced, and nothing was committed or pushed.

## 3. Findings by component family

Evidence terms used below: **Package fact** means inspected in the named package or supported by its recorded hash/module evidence; **upstream disclosure** means a vendor/project source identifies a version or license, but does not alone prove the shipped file came from that source; **open** means the evidence is incomplete.

### 3.1 Qt and PySide6 — primary license/relinking issue

**Package facts:** Qt 6.12.0 Windows binaries and PySide6/Shiboken6 bindings are present. Qt Core, Gui, Widgets, Svg, and Network binaries are shipped; plugins, including image-format plugins, and 99 translations are also present. The application uses Qt shared libraries. Qt PDF and its qpdf plugin are not present in this trimmed package.

**Upstream disclosures:** Qt documents LGPLv3 and commercial licensing for the relevant Qt libraries, with some modules under GPL instead. Qt for Python describes Community Edition as LGPLv3/GPLv3 and commercial alternatives. PySide6 and Shiboken wheel metadata previously inspected declares `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; the GPL-2.0-only metadata option does not align clearly with the vendor page's community-edition description. No option/election, commercial agreement, or written vendor resolution is established here. The present application does not appear to use a GPLv3-only Qt module identified in the reviewed vendor list; nevertheless, each shipped Qt/PySide component and translation set must be mapped to the actual applicable terms.

**Engineering evidence relevant to LGPL:** An earlier audit demonstrated replacing a Qt DLL in an onedir package. This supports that a Qt library file can technically be substituted in that tested package arrangement. It does not establish that recipients have effective modification/reverse-engineering rights, that every relevant shared library/plugin can be replaced, that a replacement will work in every supported environment, or that the LGPL's distribution conditions are met. It also does not establish a complete corresponding-source offer for the exact linked versions and build configuration.

LGPLv3 §4 contains combined-work conditions, including prominent license/use notice, accompanying the GPL and LGPL texts, applicable copyright notices, and a choice of the stated relinking/shared-library routes. The exact terms and their application to this frozen Python/Qt application require legal review. Technically, retain the modular onedir layout, identify the Linked Version for each relevant library, preserve the application code and scripts needed for a permissible relink/recombine route if that route is chosen, and test a recipient-controlled library replacement. Do not present the previous single-DLL substitution as proof of legal sufficiency. Confirm the final installation permits replacement and does not impose effective restrictions on modification or reverse engineering for debugging such modifications.

**Open:** resolve the wheel metadata/vendor documentation discrepancy with Qt; confirm Shiboken's notice/licensing basis; choose and document the applicable Qt/PySide terms; map the 99 translation files and plugins; identify exact source revisions/build options for Qt libraries; prepare corresponding-source and relinking materials; and obtain legal review of the delivery mechanism and user notices. `licenses/LGPL-3.0.txt` and `licenses/GPL-3.0.txt` are present in the repository but not in the application package.

### 3.2 Qt statically included third-party code and image plugins

The trimmed binary review reports evidence of these components in the shipped Qt DLLs/plugins. Qt's **Qt 6.12.0** attribution pages disclose matching version candidates for several: FreeType 2.14.3; HarfBuzz-NG 14.5.0; libpng 1.6.58; PCRE2 10.48 (and a distinct SLJIT attribution); libjpeg-turbo 3.2.0; libtiff 4.7.2; and libwebp 1.6.0. Qt's versioned disclosures are stronger than a generic current page, but absent matching Qt SBOM/build records they remain vendor-attribution evidence rather than a cryptographic source-to-binary match.

| Component evidenced in package | Evidence and upstream license family | Audit disposition |
|---|---|---|
| FreeType in `Qt6Gui.dll` | `FT_*`/font-engine markers; Qt 6.12.0 attribution lists 2.14.3 and offers the FreeType Project License (FTL) or GPL-2.0-only. | Presence supported; exact linked revision and **mutually exclusive license election unresolved**. Do not silently call it FTL-licensed. |
| HarfBuzz in `Qt6Gui.dll` | HarfBuzz symbols; Qt 6.12.0 lists 14.5.0 and publishes attribution/COPYING. | Presence supported; exact linked files, source revision, and any file-specific exceptions not mapped. |
| libpng in `Qt6Gui.dll` | Version string 1.6.58 and PNG symbols; libpng license. | Strong version/license-family evidence; exact Qt source/build provenance not established. |
| PCRE2 in `Qt6Core.dll` | PCRE2 diagnostic strings/symbols; Qt 6.12.0 lists 10.48; PCRE2 has BSD-3-Clause terms with its exception, and Qt separately attributes SLJIT. | Presence supported; exact version and object/SLJIT mapping unresolved. Preserve both applicable notice possibilities pending match. |
| libjpeg-turbo in `qjpeg.dll` and `qtiff.dll` | Both plugins contain `libjpeg-turbo version 3.2.0`; versioned upstream license material exists. | Version supported. Applicable IJG/BSD/subcomponent notices depend on included APIs/files and require Qt/source mapping. |
| libtiff in `qtiff.dll` | `LIBTIFF_*` symbols and documentation marker “Since libtiff 4.5.1”; Qt 6.12.0 attribution lists 4.7.2. | Presence supported; marker is only a lower bound. Vendor attribution offers a version candidate, but exact shipped source and full snapshot notice mapping remain open. |
| libwebp in `qwebp.dll` | WebP code/format markers; Qt 6.12.0 attribution identifies libwebp 1.6.0 and BSD-3-Clause terms. | Presence supported; exact version/source and applicability of upstream patent materials remain open. |
| C++/WinRT in `Qt6Core.dll` | Embedded string `C++/WinRT version:2.0.250303.1`; MIT. | Version marker and matching upstream license are available; source hash/patch state not matched. |
| zlib-compatible code in `Qt6Core.dll` | zlib-family symbols and Qt decompression strings. | Implementation identity (zlib versus zlib-ng or other compatible code), exact version, and applicable notice unresolved. Do not infer zlib-ng from generic symbols. |
| TinyCBOR, MD4C, double-conversion, libpsl/PSL, Brotli code | No affirmative source-to-binary evidence in the reviewed trimmed-package inventory; isolated strings/helpers are insufficient. | Presence remains uncertain; do not assert present or absent solely from a string scan. Do not include speculative attributions as established facts. |

Qt's generic documentation describes an SBOM mechanism starting in Qt 6.8, but no SBOM matching these PySide6 Windows wheel binaries was obtained. Obtain the exact wheel/build SBOM, Qt source revisions, configuration/patch records, and per-component attribution set. Qt PDF/PDFium and Mesa/LLVM are excluded from this trimmed package based on path and marker checks; reassess if package contents change.

### 3.3 CPython, standard library, and native dependencies

**Package facts and source evidence:** CPython 3.14.10 runtime/standard-library material is present. The package contains `_bz2.pyd`, `_lzma.pyd`, `_zstd.pyd`, `_decimal.pyd`, `_sqlite3.pyd`, `unicodedata.pyd`, OpenSSL DLLs, and SQLite. Existing binary/source review reports bzip2 1.0.8, Zstandard 1.5.7, mpdecimal 4.0.0, SQLite 3.50.4, and Unicode Character Database 16.0.0.

- **CPython:** include the applicable PSF license and attribution material; the official 3.14.10 license/README are collected. Exact CPython Windows source archive/build input hash is not matched. CPython's `LICENSE.txt` contains a **Microsoft Distributable Code** section for specified embedded components. The previously collected CPython attribution excerpt does not contain that section. Assess and address it from the exact applicable CPython license/build terms before distribution.
- **Unicode data:** `unicodedata.pyd` carries UCD 16.0.0 evidence. The Unicode License V3 and UCD ReadMe are collected, but the exact CPython input-data mapping remains unverified.
- **bzip2:** `_bz2.pyd` reports 1.0.8; its versioned BSD-like license text is collected. Confirm exact source/patch identity.
- **Zstandard:** `_zstd.pyd` reports 1.5.7. Upstream provides BSD-style and GPLv2 licensing alternatives; the downstream election for this embedded CPython copy is not established. Both upstream texts are in the collection as alternatives, not a decision.
- **mpdecimal:** `_decimal.pyd` build evidence points to mpdecimal 4.0.0. Its copyright material is collected from a source archive whose published checksum was checked, but the binary's precise source/patch identity remains open.
- **SQLite:** `sqlite3.dll` reports 3.50.4/source-ID evidence; SQLite states its implementation is public domain. The collected page is courtesy/public-domain information, not a required license text. Exact source hash is not matched.
- **liblzma/XZ:** `_lzma.pyd` proves code presence, not version or license vintage. XZ Utils contains different license scopes; do not infer the license of the command-line tools or assume a current liblzma license applies to the embedded copy. Exact CPython build source is needed.
- **zlib-ng/zlib-compatible code in CPython:** strings include `zlib-ng` and `1.3.1`, but that number may indicate zlib API compatibility rather than the upstream zlib-ng release. The collected zlib-ng 2.2.4 license is expressly a **candidate only** and is not asserted applicable. Resolve CPython's exact source/build inputs before selecting a notice.

### 3.4 OpenSSL

`libcrypto-3.dll` and `libssl-3.dll` report OpenSSL 3.5.9 and match the local CPython 3.14 DLL copies byte-for-byte. The official OpenSSL 3.5.9 release archive was downloaded and its SHA-256 matched the published digest; its top-level `LICENSE.txt` is Apache-2.0, and the inspected archive includes `ACKNOWLEDGEMENTS.md` but no file named `NOTICE` or `NOTICE.*`. The archived Apache license and acknowledgement file are collected. No OpenSSL `NOTICE` has been invented or relabeled.

This is stronger upstream archive evidence than a tag-tree-only check, but it does not prove the CPython-packaged DLLs were built from that exact archive/configuration or exhaust all notices relevant to those DLLs. The archive's detached signature was not verified, and CPython's build provenance was not established. Apache-2.0 §4(d) refers to a NOTICE file when the Work includes one; the inspected archive contains none. Legal review should confirm the actual source/build distribution and all other Apache obligations, including license delivery and modification notices. No endorsement is implied.

### 3.5 PyInstaller

The frozen EXE contains PyInstaller bootloader and loader/bootstrap payload, runtime hooks, and `_pyi_rth_utils` modules. Build metadata identifies PyInstaller 6.22.3. The installed `COPYING.txt` matches the official 6.22.3 source-distribution copy byte-for-byte and distinguishes:

- bootloader and `PyInstaller/loader` files: GPL-2.0-or-later with the PyInstaller Bootloader Exception;
- runtime hooks and `_pyi_rth_utils`: Apache-2.0; and
- `hook-PySide6.QtSvg.py`: a build-time hook carrying a GPL/Bootloader Exception header, not the Apache runtime-hook terms.

The complete upstream `COPYING.txt` is collected. The EXE's `.text`, `.data`, `.pdata`, `.fptable`, and `.reloc` sections matched the installed `runw.exe`; `.rdata` differed by four uninterpreted bytes, and the package adds resources/archive data. Therefore the report does **not** make an unmodified-bootloader claim. The source-to-CArchive entry mapping is documented for principal entries but should be validated against the exact build inputs. Preserve the separate license treatment and assess whether build-time hook source is present in any distribution. No PyInstaller source/corresponding-source delivery plan is settled.

### 3.6 Microsoft Visual C++ runtime

The package contains **ten** VC++ DLLs: two root files at version 14.51.36247.0 and eight under `PySide6/`/`shiboken6/` at 14.44.35211.0. The eight 14.44 DLLs carry Qt Company signatures and match the local wheel files; the two root 14.51 files carry Microsoft signatures and match local CPython/System32 copies. All ten package file paths and hashes are listed in `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`.

Microsoft's official documentation limits redistribution of Redistributable packages/individual files to eligible licensed Visual Studio users and subjects use to applicable software license terms; it recommends central deployment for servicing. Official versioned Microsoft-signed installer evidence supports that 14.44.35211 and 14.51.36247 are Microsoft runtime releases. It does **not** establish that the package's differently signed/inherited DLL copies are exact installer payload files, unmodified, eligible for redistribution, or covered by a specific grant. The complete applicable license terms were not readable in this environment. Qt's written basis for redistributing/re-signing its wheel DLLs is also absent.

One captured process loaded five of the ten packaged files, including a 14.51 `VCRUNTIME140.dll` and 14.44 `VCRUNTIME140_1.dll`/`MSVCP140*` files. No duplicate path for the same basename was observed in that run; this does not show that five other copies are unnecessary or prove loader selection on all systems/workflows. No runtime DLL was removed/replaced. Establish a legal and operational central-vs-app-local deployment decision, eligibility/provenance for every retained file, and servicing plan before release.

### 3.7 Other platform/build dependencies

- The earlier runtime inventory observed Qt's ICU imports resolving to Windows System32 on the test system, while ICU was not bundled. This indicates a possible host dependency/minimum-Windows compatibility question; no claim is made about all supported Windows versions. Revalidate against the trimmed binary on clean target OS environments.
- No redistribution obligation is inferred from OpenSSL provider-name strings such as `brotli`, `zstd`, or `zlib` alone.
- Qt PDF/PDFium and Mesa/LLVM are not in the named trimmed artifact. Their old notice texts are not automatically applicable solely because they remain in the repository's earlier evidence collection.

## 4. Existing notice/source materials: what they do and do not establish

`licenses/third-party/notices/` contains a hash manifest and collected source texts/attributions for CPython, Unicode, OpenSSL, PyInstaller, bzip2, mpdecimal, SQLite, Zstandard alternatives, FreeType alternatives, HarfBuzz, libpng, libjpeg-turbo, PCRE2/SLJIT, C++/WinRT, and historical Mesa/LLVM material. These files are useful evidence and several have verified upstream hashes. Their presence does not mean each is the correct notice for the exact shipped bytes, that all notices are present, or that they have been integrated into the package.

The following items remain incomplete or candidate-only for a release notice set: applicable Qt/PySide notices and license election; package-matched Qt component records; FreeType and Zstandard elections; exact zlib/liblzma notice bases; libtiff/libwebp snapshot/notice/patent mapping; CPython Microsoft Distributable Code terms; Microsoft runtime redistribution terms and eligibility; PyInstaller payload mapping/modification status; and a reviewed LGPL user notice/source-relinking plan. The existing notice manifest describes source files collected for review and historical builds; it is **not** proof that the trimmed package contains notices (it does not) or that its inventory has been reconciled for redistribution.

No release notice bundle is declared complete by this report. Do not copy every file in `notices/` into a public release blindly: the directory includes alternatives and candidate/historical material, including FreeType FTL/GPLv2 alternatives, Zstandard BSD/GPLv2 alternatives, a zlib-ng candidate license, and removed Mesa/LLVM attribution pages.

## 5. Release gates and required evidence

| Priority | Gate | Evidence needed before approval |
|---|---|---|
| 1 | Qt/PySide licensing and LGPL model | Written license-basis decision (including wheel metadata discrepancy); counsel review of LGPLv3 §4 and delivery terms; exact Qt/PySide/translation component map; conspicuous user notice and license texts; tested user-controlled replacement/relinking route; defined corresponding-source or relink package/source offer as applicable. |
| 2 | Microsoft VC++ runtime | Applicable complete license terms; written Qt confirmation for wheel DLL provenance and redistribution basis; eligible/unmodified source trail for each retained DLL; chosen central/app-local deployment model and servicing plan. |
| 3 | Third-party notice accuracy | Qt 6.12.0 Windows build/wheel SBOM or source/build mapping for QtCore/Gui/plugins; exact CPython inputs for zlib-compatible code and liblzma; FreeType/Zstandard elections; libtiff/libwebp and patent materials; CPython Microsoft clause; package-matched attributions for shipped files. |
| 4 | Source/corresponding-source obligations | Identify versions, patches, build scripts/configuration, and corresponding source for covered components; determine the appropriate source delivery/offer and keep it available for the relevant period; validate availability and version matching. |
| 5 | Frozen executable/bootloader | Final PyInstaller 6.22.3 entry-to-source/license map; resolve the four-byte `.rdata` difference without claiming it is functional; determine modified status and obligations; retain bootloader exception and Apache runtime-hook notices distinctly. |
| 6 | Release packaging and platform support | Include reviewed notices/license copies in the intended end-user distribution, preserve the onedir replacement path if relied upon, verify hashes/inventory post-assembly, and run RDP, GPU-less/software-rendering, high-DPI, and clean-target Windows compatibility tests. |

No single gate alone is a legal clearance decision. Review the exact release artifact and intended distribution channel, including any installer, EULA, update mechanism, or other recipient restrictions.

## 6. Official source register

Primary vendor/project references used or identified in the existing evidence files:

- Qt 6.12 licensing and LGPL: <https://doc.qt.io/qt-6.12/licensing.html>, <https://doc.qt.io/qt-6.12/lgpl.html>, <https://doc.qt.io/qt-6.12/licenses-used-in-qt.html>, <https://doc.qt.io/qt-6.12/sbom.html>.
- Qt/Python licensing: <https://doc.qt.io/qtforpython-6/commercial/index.html>, <https://doc.qt.io/qtforpython-6/overviews/qtdoc-lgpl.html>, <https://doc.qt.io/qtforpython-6/licenses.html>.
- Qt 6.12.0 component attributions: <https://doc.qt.io/qt-6.12/qtgui-attribution-freetype.html>, <https://doc.qt.io/qt-6.12/qtgui-attribution-harfbuzz-ng.html>, <https://doc.qt.io/qt-6.12/qtgui-attribution-libpng.html>, <https://doc.qt.io/qt-6.12/qtcore-attribution-pcre2.html>, <https://doc.qt.io/qt-6.12/qtimageformats-attribution-libtiff.html>, <https://doc.qt.io/qt-6.12/qtimageformats-attribution-libwebp.html>.
- Microsoft VC++ redistribution: <https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files>, <https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist>, <https://learn.microsoft.com/en-us/cpp/windows/troubleshoot-vc-redistributable-installation-issues>, <https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution>, <https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution>, <https://learn.microsoft.com/en-us/lifecycle/faq/visual-c-faq>.
- OpenSSL 3.5.9: <https://github.com/openssl/openssl/releases/tag/openssl-3.5.9>; archive digest and file-list findings are detailed in `RUNTIME-LICENSING-EVIDENCE.md`.
- CPython 3.14: <https://github.com/python/cpython/tree/3.14>, <https://docs.python.org/3.14/license.html>.
- PyInstaller 6.22.3: <https://pyinstaller.org/en/v6.22.3/license.html>, <https://github.com/pyinstaller/pyinstaller/blob/v6.22.3/COPYING.txt>.

Sources establish what the named project/version documents say; they do not, without matching build evidence, prove the provenance or exact license scope of a packaged binary.

## 7. Audit disposition

**Engineering disposition:** evidence-backed, incomplete licensing review. The trimmed package identity is known and remained unchanged during verification. Some removed components and version mismatches have been corrected in scope. The repository's collected texts are not yet a valid, complete release notice package.

**Release disposition:** **HOLD / NOT CLEARED FOR DISTRIBUTION.** Do not describe the software as license-compliant or legally cleared on the basis of this audit. Obtain qualified legal review and close the gates in §5. Any package/source/notice changes require explicit release authorization, a new inventory/hash check, and retesting.
