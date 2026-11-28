# Microsoft VC++ Runtime Redistribution Review

**Status:** engineering evidence for further review. This is not legal advice, a compliance determination, or release approval.

**Scope:** the ten VC++ runtime DLL files in `dist/gui-ondir-trim-test/LogSentinel-GUI/_internal/` (the trimmed onedir package), one isolated GUI-session module enumeration, the PyInstaller collection record, official Microsoft documentation and versioned Microsoft redistributable download paths. The DLLs were not changed. The two installer EXEs fetched for version identification were saved only under `C:/Users/DELL/AppData/Local/Temp/`; neither was executed.

Evidence labels: **Verified fact** is directly observed or hash/signature checked; **Microsoft source** is a statement or source published by Microsoft; **Assessment** is an interpretation, not a license conclusion; **Open** is unresolved.

## Executive findings

1. The package contains **10 files** bearing VC++ runtime DLL names: 2 root copies, 5 in `PySide6/`, and 3 in `shiboken6/`. File versions are 14.51.36247.0 and 14.44.35211.0. Their exact package paths and SHA-256 hashes are listed in §1.
2. In the captured isolated GUI process, **5 of the 10 package copies** were loaded: root `VCRUNTIME140.dll` 14.51, Shiboken `VCRUNTIME140_1.dll` and `MSVCP140.dll` 14.44, and PySide `MSVCP140_1.dll` and `MSVCP140_2.dll` 14.44. Two Windows system runtime DLLs (`msvcp_win.dll`, `ucrtbase.dll`) were also loaded. The other five packaged copies were not in that module snapshot.
3. Microsoft’s lifecycle FAQ identifies **14.44.35211** as the VS 2022 v17.14 final runtime. Microsoft’s troubleshooting page documents a versioned download route for versions 14.30–14.44. For **14.51.36247**, that page documents the VS 18 route for 14.50 and later; the exact route resolved to a Microsoft-hosted, Microsoft-signed x64 installer whose version metadata is 14.51.36247.0.
4. Those official installers establish that the **versioned Redistributable packages** are Microsoft releases. They do **not** establish that the package’s Qt-signed 14.44 DLL copies are byte-identical to Microsoft installer payloads, came from a specific Microsoft package, or are themselves eligible for redistribution under the applicable grant. The package’s root 14.51 pair is byte-identical to the local CPython and Windows System32 files; no provenance trail from the official installer to those copies was established in this step.
5. The package has same-basename duplicates on disk, but the one observed process loaded only one path for each runtime basename. This is not proof that every code path or environment will resolve the same files. No DLL was deleted or replaced.
6. Microsoft recommends central deployment with the redistributable package for servicing; it discourages application-local DLL deployment because the publisher must maintain updates. Whether to use central deployment or retain local files is an application/release decision, and the license terms and exact eligible file provenance still need review.

---

## 1. Packaged DLL inventory

All package DLLs below were version-read, SHA-256 hashed, and verified with `Get-AuthenticodeSignature` as `Valid`. The 14.44 DLLs are signed by **The QT Company Oy**; the root 14.51 DLLs are signed by **Microsoft Windows Software Compatibility Publisher**.

| Package path | Bytes | File version | SHA-256 | Signer |
|---|---:|---|---|---|
| `_internal/VCRUNTIME140.dll` | 178,616 | 14.51.36247.0 | `D1F4225DF2CD877DBF130D5668A021DCE3F94118455FF5EC952061C30AFC9CE7` | Microsoft Windows Software Compatibility Publisher |
| `_internal/VCRUNTIME140_1.dll` | 50,112 | 14.51.36247.0 | `A7146C08F89FE5B04541AB507CDB59FF7B44534D4BA3C668A426C6450A03434E` | Microsoft Windows Software Compatibility Publisher |
| `_internal/PySide6/MSVCP140.dll` | 549,176 | 14.44.35211.0 | `F6F1D55BFD64027820DDCE48F9CD8CF46D53BFA34047E6ACF4EF348D492A05CB` | The QT Company Oy |
| `_internal/PySide6/MSVCP140_1.dll` | 27,448 | 14.44.35211.0 | `2BE87527C41E1BA8AFF48E326E0ADCD4743516E0BBCC9304986C726E27DE6ACA` | The QT Company Oy |
| `_internal/PySide6/MSVCP140_2.dll` | 271,672 | 14.44.35211.0 | `6A72ED8A87EAE1671640BD1CA98ECCB989F1772AE46AB84594E385BF6D4AC4FB` | The QT Company Oy |
| `_internal/PySide6/VCRUNTIME140.dll` | 116,024 | 14.44.35211.0 | `A36E0CB185EB89533ED96D4568138F86A1315756A8B2644C5963A8CE23E32101` | The QT Company Oy |
| `_internal/PySide6/VCRUNTIME140_1.dll` | 41,272 | 14.44.35211.0 | `302B1E160E858602490A55E32AE2E29DDFC0BEC2A188E19550CB655CDAA58F9C` | The QT Company Oy |
| `_internal/shiboken6/MSVCP140.dll` | 549,176 | 14.44.35211.0 | `1BA4D7C0A95D375DA138A057A57593B33510AD5BDA6C5E2686AFD68FAA5B4231` | The QT Company Oy |
| `_internal/shiboken6/VCRUNTIME140.dll` | 116,024 | 14.44.35211.0 | `E7BE9112EE9A5B9F44B44BFF24CB761CCA9B1ED7550B612F77B70EDFCF5FDABF` | The QT Company Oy |
| `_internal/shiboken6/VCRUNTIME140_1.dll` | 41,272 | 14.44.35211.0 | `F02CD4A862B85A9A3153D27E15E5A213F5DF8E3D77004ED2E87B8A7E8873D97C` | The QT Company Oy |

The two root DLLs byte-match `C:\Python314\VCRUNTIME140.dll`, `C:\Python314\VCRUNTIME140_1.dll` and their Windows System32 copies (14.51.36247.0). The eight PySide6/Shiboken DLLs byte-match the DLLs in the installed PySide6 6.12.0 and shiboken6 6.12.0 package directories. This is file provenance within the local build environment, not proof of the vendors’ upstream acquisition or the scope of any redistribution grant.

For duplicate 14.44 filenames, corresponding PySide6 and Shiboken files differ in PE checksum and Authenticode certificate-table bytes; a few byte differences outside the certificate table were also recorded in the prior evidence report. These byte comparisons do not prove functional equivalence. `msvcp140_codecvt_ids.dll` is in the venv package directories but is not in the trimmed package’s 10-file runtime inventory.

---

## 2. Loaded versus merely packaged

**Observed source:** the prior isolated-profile module enumeration, `C:/Users/DELL/AppData/Local/Temp/logsentinel-step-9-3-18-modules.txt`, captured 102 process modules and a clean exit. The separate trimmed E2E log lists loaded module basenames but does not include paths. The full paths and versions below are from the module enumeration.

| Runtime basename | Package copy loaded in captured session | Other package copies not observed loaded |
|---|---|---|
| `VCRUNTIME140.dll` | `_internal/VCRUNTIME140.dll` — 14.51.36247.0 | `_internal/PySide6/VCRUNTIME140.dll` and `_internal/shiboken6/VCRUNTIME140.dll` — both 14.44.35211.0 |
| `VCRUNTIME140_1.dll` | `_internal/shiboken6/VCRUNTIME140_1.dll` — 14.44.35211.0 | `_internal/VCRUNTIME140_1.dll` — 14.51.36247.0; `_internal/PySide6/VCRUNTIME140_1.dll` — 14.44.35211.0 |
| `MSVCP140.dll` | `_internal/shiboken6/MSVCP140.dll` — 14.44.35211.0 | `_internal/PySide6/MSVCP140.dll` — 14.44.35211.0 |
| `MSVCP140_1.dll` | `_internal/PySide6/MSVCP140_1.dll` — 14.44.35211.0 | None; one packaged copy |
| `MSVCP140_2.dll` | `_internal/PySide6/MSVCP140_2.dll` — 14.44.35211.0 | None; one packaged copy |

Windows system runtime modules observed in that session, not bundled in the package:

| System path | Bytes | File version | SHA-256 | Signature |
|---|---:|---|---|---|
| `C:\Windows\System32\msvcp_win.dll` | 651,752 | 10.0.19041.7802 | `1AE6811D068116AC90EF8EA7132C41BC415071E9B714EEB935B7D79D76EEEC3A` | Valid; Microsoft Windows |
| `C:\Windows\System32\ucrtbase.dll` | 1,065,512 | 10.0.19041.7802 | `E6C3D2B25104FA81CD12383CBC4B9FBF7EBF4734A2BD0B163F644DC8D468A1ED` | Valid; Microsoft Windows |

**Interpretation and limits:** the captured process had a loaded 14.51 `VCRUNTIME140.dll` together with loaded 14.44 `VCRUNTIME140_1.dll` and `MSVCP140.dll`/dot libraries. This is coexistence of different runtime DLL basenames and versions in one process, not two loaded copies of the same basename. The process snapshot did not load five other packaged copies. An import scan shows that multiple PySide DLLs import these basenames, but import tables do not specify which file Windows will select. One process snapshot cannot establish every module-load outcome, code path, clean target machine, or Windows loader configuration.

---

## 3. Official Microsoft source evidence

### Redistribution permission and deployment guidance

- [Redistributing Visual C++ files](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files): Microsoft says distribution of the Visual C++ Redistributable package, merge modules and individual binaries is limited to licensed Visual Studio users and is subject to Microsoft Software License Terms. The page says to consult the applicable license terms. It recommends redistributable-package/central deployment; it also documents app-local individual DLL installation but says that location is not recommended for servicing reasons.
- [Visual Studio 2022 Redistribution](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution): its Visual C++ Runtime Files section permits specified files, unmodified and subject to the software license terms, including files under the Visual Studio `VC\redist` tree. It repeats that the package, merge modules, and individual binaries obtained from the cited download pages are for licensed Visual Studio users and subject to the terms.
- [Visual Studio 2026 Redistribution](https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution): corresponding REDIST/distributable-code list and Visual C++ runtime file section for VS 2026 and later, again subject to the applicable license terms and with unmodified-file conditions.
- [Latest supported Visual C++ Redistributable downloads](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist): documents the rolling x86/x64/ARM64 v14 installer links. Microsoft says the v14 Redistributable is updated frequently and the page does not provide a permanent version-to-file table. It says redistribution is limited to licensed Visual Studio users and recommends the latest supported package for compatible MSVC-built applications.
- [Troubleshoot Visual C++ Redistributable installation issues](https://learn.microsoft.com/en-us/cpp/windows/troubleshoot-vc-redistributable-installation-issues): provides old-version routes and specifically warns to download VC Redist installers from Microsoft and install only packages signed by Microsoft. It documents `https://aka.ms/vs/17/release/<version>/VC_redist.<arch>.exe` for versions 14.30–14.44 and `https://aka.ms/vs/18/release/<version>/VC_redist.<arch>.exe` for 14.50 or later.
- [Microsoft C++ Build Tools, Redistributable, and runtime libraries FAQ](https://learn.microsoft.com/en-us/lifecycle/faq/visual-c-faq): describes v14 runtime cumulative/in-place servicing and binary compatibility. Its version table identifies 14.44.35211 as shipped with VS 2022 v17.14 final, start date May 13, 2025, end date January 13, 2032. It says VS 2015–2022 runtime releases follow fixed lifecycle; starting with VS 2026, 14.50+ follows the Modern Policy separately from the IDE lifecycle.
- [C++ binary compatibility 2015–2026](https://learn.microsoft.com/en-us/cpp/porting/binary-compat-2015-2017): describes binary compatibility across MSVC toolset families v140–v145 and use of current v14 Redistributable, with restrictions. This does not by itself establish which copies a particular application may redistribute.
- [Deployment in Microsoft C++](https://learn.microsoft.com/en-us/cpp/windows/deployment-in-visual-cpp): defines central and local deployment, notes that “dot libraries” (for example `msvcp140_1.dll`) may be required with the main library, and says Microsoft does not automatically update app-local DLLs and does not recommend local deployment without an updater.

### Version-specific official packages checked (x64, not executed)

The versioned URLs below are on Microsoft’s documented old-version patterns. The `aka.ms` paths redirected to Microsoft’s `download.visualstudio.microsoft.com` host. Each resulting installer’s Authenticode signature was `Valid`, signer `CN=Microsoft Corporation`; file and product version metadata matched the requested release. The installer file hash matches the hex digest included in the Microsoft download URL.

| Runtime/package version | Microsoft versioned installer URL | Final Microsoft-hosted URL path/digest | Installer evidence |
|---|---|---|---|
| 14.44.35211.0 | [`https://aka.ms/vs/17/release/14.44.35211/VC_redist.x64.exe`](https://aka.ms/vs/17/release/14.44.35211/VC_redist.x64.exe) | `download.visualstudio.microsoft.com/download/pr/cca52e64-05a7-46cb-9a21-9d30a1609598/CC0FF0EB1DC3F5188AE6300FAEF32BF5BEEBA4BDD6E8E445A9184072096B713B/VC_redist.x64.exe` | 25,635,768 B; SHA-256 `CC0FF0EB1DC3F5188AE6300FAEF32BF5BEEBA4BDD6E8E445A9184072096B713B`; file/product version 14.44.35211.0; Microsoft signature valid |
| 14.51.36247.0 | [`https://aka.ms/vs/18/release/14.51.36247/VC_redist.x64.exe`](https://aka.ms/vs/18/release/14.51.36247/VC_redist.x64.exe) | `download.visualstudio.microsoft.com/download/pr/ebdab8e5-1d7b-4d9f-a11b-cbb1720c3b12/843068991DAAA1F73AD9F6239BCE4D0F6A07A51F18C37EA2A867E9BECA71295C/VC_redist.x64.exe` | 18,731,856 B; SHA-256 `843068991DAAA1F73AD9F6239BCE4D0F6A07A51F18C37EA2A867E9BECA71295C`; file/product version 14.51.36247.0; Microsoft signature valid |

Temporary downloaded installers: `C:/Users/DELL/AppData/Local/Temp/ls-step9319-vc144-x64.exe` and `.../ls-step9319-vc151-x64.exe`. Both were inspected for metadata/signature only, not run. Installer signatures and installer hashes establish the files downloaded from these official URLs; installer payload DLLs were not extracted or compared to the package DLL hashes.

---

## 4. Version-specific findings and packaged-file provenance

### 14.44.35211.0 — Microsoft runtime release, Qt-signed packaged copies

**Microsoft-supported facts:** Microsoft’s FAQ explicitly associates runtime version 14.44.35211 with the VS 2022 v17.14 final release and its lifecycle. The exact official 14.44 x64 Redistributable URL resolves and supplies a Microsoft-signed installer whose metadata reports 14.44.35211.0. Qt’s installed `PySide6` and `shiboken6` versions are 6.12.0; the eight packaged 14.44 DLL files match the respective wheel-directory files and carry valid Qt Company signatures.

**Assessment:** 14.44.35211 is a genuine Microsoft v14 runtime release. The existence of an official, versioned Microsoft installer supports that the version is a legitimate Microsoft Redistributable release; the Qt-signing and wheel provenance do **not** prove that each particular packaged DLL is one of Microsoft’s unmodified distributable files, nor do they establish the license or redistribution permission under which Qt included/signed the copies. No file-by-file hash match against the 14.44 installer contents was made. The applicable VS 2022 license terms remain necessary for a legal assessment.

### 14.51.36247.0 — versioned Microsoft VS 18 runtime package, mixed local provenance

**Microsoft-supported facts:** the official troubleshooting page assigns versions 14.50 or later to the versioned VS 18 URL pattern. The exact 14.51.36247 x64 URL resolves to Microsoft-hosted content; the downloaded installer is Microsoft-signed, and its file/product metadata is 14.51.36247.0. The two packaged root DLLs are Microsoft Windows Software Compatibility Publisher-signed and match local CPython and Windows System32 copies.

**Assessment:** the version is confirmed as a Microsoft v14 Redistributable release via the official package path and signed installer. But the root DLLs’ byte identity to the host CPython/System32 files does not itself establish they were extracted from the 14.51 installer or that their inclusion is authorized by the relevant Visual Studio license terms. The 14.51 lifecycle is under VS 2026’s 14.50+ Modern Policy; the FAQ’s version table observed here names 14.50.35710 but not 14.51.36247, so no version-specific support end date is asserted.

### Source/signature implications

The package contains 14.44 files signed by Qt and 14.51 root DLLs signed by Microsoft. Authenticode validity identifies the signer and signed file state; it is not a license grant. Similarly, a Microsoft signed installer establishes the official installer publisher, not the provenance of already-bundled, differently signed DLL copies. The license pages tie redistribution to an eligible Visual Studio license and unmodified REDIST/distributable files. No conclusion that every packaged DLL satisfies those conditions is made here.

---

## 5. Duplicates and practical assessment

### What is duplicated (verified)

The package repeats basenames at different paths:
- `VCRUNTIME140.dll`: three copies (root 14.51; PySide6 and Shiboken 14.44).
- `VCRUNTIME140_1.dll`: three copies (root 14.51; PySide6 and Shiboken 14.44).
- `MSVCP140.dll`: two copies (PySide6 and Shiboken, both 14.44 but not byte-identical).
- `MSVCP140_1.dll` and `MSVCP140_2.dll`: one copy each, under PySide6.

### Are they necessary or redundant?

- **Necessity is not established for every file.** The captured run did not load five copies, including the root `VCRUNTIME140_1.dll`, PySide6 `VCRUNTIME140.dll`, Shiboken `VCRUNTIME140.dll`, PySide6 `VCRUNTIME140_1.dll`, and PySide6 `MSVCP140.dll`. The root `VCRUNTIME140_1.dll` was also not listed as an import by the scanned package binaries. Those facts suggest candidate redundancy for the tested path, not proof that a copy is unnecessary for other supported paths or loader conditions.
- **Not a same-name double load in the observed process.** The process list had one path per loaded basename; for example, it selected the Shiboken 14.44 `VCRUNTIME140_1.dll`, not the root 14.51 or PySide 14.44 copy. It selected root 14.51 `VCRUNTIME140.dll`, and Shiboken 14.44 `MSVCP140.dll`. Thus different runtime files coexist, but duplicate same-basename copies were not simultaneously observed in the process.
- **Potential technical risks:** different file contents/signers under identical basenames, DLL search-order-dependent selection, servicing/version skew, and changed behavior if a module/code path or packaging layout changes. Microsoft’s own docs describe `msvcp140_1.dll` as a “dot library” that may be required with `msvcp140.dll`; do not remove dot libraries based solely on one process snapshot. The different MSVC 14.44 and 14.51 v14 minor/update generations are within Microsoft’s stated compatibility family, but that does not prove substitutability of these individual files or of Qt/Python binaries.
- **Could one supported runtime deployment reduce duplicates?** Microsoft recommends central deployment with a supported Redistributable package for maintenance; it can let Microsoft service the runtime and avoids the app’s own update burden. Microsoft also documents app-local deployment, but discourages it for servicing reasons. Qt’s [Windows deployment documentation for Qt 6.12](https://doc.qt.io/qt-6.12/windows-deployment.html) says the appropriate VCRedist should be installed on the end-user system and cautions that application compiler/runtime versions must align. This supports evaluating a single centrally deployed runtime strategy; it does not alone determine how the current PySide6 wheel copies may be removed or replaced.

**Recommendation:** make no DLL changes in this evidence-only step. Before any distribution change, choose and document one deployment strategy with legal review. Prefer evaluating a centrally installed, current supported Microsoft x64 v14 Redistributable (using the official Microsoft package and an installer prerequisite) if it fits the product’s deployment model and the applicable license terms. If retaining app-local DLLs, establish eligibility and source for every packaged file, keep files unmodified as required by the applicable grant, and assign a maintenance/update process. Do not replace the Qt-signed files with installer-extracted DLLs or remove “unloaded” copies without a separate dependency/load-path review and full regression test.

---

## 6. Outstanding questions

1. **License terms:** obtain and review the exact Microsoft Visual C++ Runtime license terms applicable to the source/edition used for redistribution (VS 2022 vs VS 2026/runtime package). Microsoft’s directory lists the product license, but the Visual Studio-hosted license pages rendered a page shell/unsupported-device response in this environment, not a readable complete EULA. The Microsoft Learn redistribution pages point to and summarize the grant; they are not a substitute for the complete terms.
2. **14.44 package DLL provenance:** determine whether the Qt-signed DLLs were re-signed by Qt from eligible Microsoft Redistributable DLLs, how that was authorized, and whether the applicable terms’ “unmodified” condition is satisfied. Obtain vendor build/licensing documentation or a written Qt confirmation; hashes of the original wheel DLLs and the Microsoft 14.44 installer payload are needed for precise comparison.
3. **14.51 source chain:** identify the source that supplied the root 14.51 DLLs to `C:\Python314` and confirm the authorized redistribution basis. Their hash match to Windows System32/CPython files is not itself proof of package-source entitlement.
4. **Runtime load coverage:** obtain a DLL-load trace (with full paths) across standard app workflows, optional Qt plugins, clean Windows targets, and the intended package/install layout. The current module snapshot is one run only.
5. **Version alignment:** identify the compiler/runtime used to build the Qt 6.12.0 wheels and CPython 3.14.10 distribution, and determine the specific runtime minima for packaged binaries. Microsoft's general v14 compatibility statement is not an app-specific dependency audit.
6. **Deployment model:** determine whether the GUI is intended to be portable/unpacked or installed. Central package servicing and application-local updates have different operational consequences.

## 7. Recommended next action

Request a Microsoft licensing review (or consult qualified counsel) against the exact Microsoft Visual C++ Runtime/Visual Studio license terms and intended distribution model, and request Qt’s documentation for the Microsoft runtime DLLs included with the PySide6 6.12.0 Windows wheels. In parallel, preserve file hashes and capture a full-path loader trace. Only after those results should the project decide whether to retain wheel-supplied runtime files, ship an official signed x64 Redistributable as an installer prerequisite, or use another documented deployment path. No compliance conclusion is made by this report.

## 8. Evidence records and integrity

- Prior package evidence: `licenses/third-party/RUNTIME-LICENSING-EVIDENCE.md`, sections 2.1–2.4; trimmed package notice map: `licenses/third-party/TRIMMED-PACKAGE-NOTICE-MAP.md`.
- Isolated loaded-module list: `C:/Users/DELL/AppData/Local/Temp/logsentinel-step-9-3-18-modules.txt`; trimmed E2E basename list: `C:/Users/DELL/AppData/Local/Temp/logsentinel-ondir-trim-e2e-run10.log`.
- Installer downloads and signature metadata checks: `C:/Users/DELL/AppData/Local/Temp/ls-step9319-vc144-x64.exe`, `ls-step9319-vc151-x64.exe`; no installers were executed.
- Package files were not changed in this step. Final report size and SHA-256 are in the completion response; the worktree comparison uses `C:/Users/DELL/AppData/Local/Temp/logsentinel-step-9-3-19-status-before.txt`.
