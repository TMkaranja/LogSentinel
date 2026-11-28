# Runtime Licensing Evidence: Trimmed GUI Package

Status: evidence record only. This is not a legal opinion, a compliance determination, or a release approval.

Scope: `dist/gui-ondir-trim-test/LogSentinel-GUI/` (182 files, 80,058,228 B), built from the trimmed exact-path spec (`packaging/LogSentinel-GUI-Onedir.spec`). Three runtime components: (1) Microsoft Visual C++ runtime, (2) OpenSSL 3.5.9, (3) PyInstaller 6.22.3 bootloader and runtime hooks.

Method: read-only inspection of the package, the installed build environment (`.venv-build-gui`), the bundled CPython 3.14.10 install (`C:\Python314`), PyInstaller build artifacts (`build/gui-ondir-trim-work/`), and official upstream sources. No rebuild, no source/test/dependency/packaging/notice/binary changes. Temporary files are under `C:/Users/DELL/AppData/Local/Temp/ls-step9318-*` and `logsentinel-step-9-3-18-*`.

Evidence labels: **Fact** = directly observed or hashed. **Source** = upstream text read. **Interpretation** = reasoning from facts; labeled as such. **Open** = not resolved by this evidence.

---

## 1. Summary

| Component | Packaged evidence | Upstream evidence | Status |
|---|---|---|---|
| Microsoft VC++ runtime | 10 copies (2 at root, 5 under `PySide6/`, 3 under `shiboken6/`) in two versions: 14.51.36247.0 and 14.44.35211.0 | Microsoft redistribution pages; Visual Studio license terms page unusable (stub) | Present — version/source unresolved for the 14.44 copies; Microsoft terms not fully retrieved |
| OpenSSL 3.5.9 | `libcrypto-3.dll` and `libssl-3.dll`, byte-identical to `C:\Python314\DLLs` copies; build string `OpenSSL 3.5.9 29 Sep 2026` | Official 3.5.9 release archive (SHA-256 verified against the published digest); top-level `LICENSE.txt` and `ACKNOWLEDGEMENTS.md` | Present — notice evidence adequate for further review; no NOTICE file was found in the inspected 3.5.9 archive; exact packaged-DLL source archive remains unverified |
| PyInstaller 6.22.3 bootloader | `LogSentinel-GUI.exe` section-identical to installed `runw.exe` except a 4-byte `.rdata` difference (uninterpreted) plus `.rsrc` and overlay | `COPYING.txt` in the installed dist-info and the official sdist are byte-identical | Present — notice mapping adequate for further review; per-file licensing differs (see §4) |

---

## 2. Microsoft Visual C++ Runtime

### 2.1 Packaged copies (Fact)

All copies were hashed, version-read, and checked with `Get-AuthenticodeSignature` (all status `Valid`).

| Package path | Bytes | FileVersion | SHA-256 | Signer |
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

Byte-level provenance (Fact):
- The two root copies are byte-identical to `C:\Python314\vcruntime140.dll` and `vcruntime140_1.dll` and to the `C:\Windows\System32` 14.51.36247.0 copies.
- The PySide6 and shiboken6 copies match the copies in the installed venv wheels (`.venv-build-gui/Lib/site-packages/PySide6` and `shiboken6`).
- Within each 14.44 pair, the copies differ only in the PE checksum and Authenticode certificate-table bytes: `PySide6/VCRUNTIME140.dll` vs `shiboken6/VCRUNTIME140.dll` (5,752 bytes differ; 2 outside the certificate table, offsets 336–337); `VCRUNTIME140_1.dll` pair (566 bytes differ; 2 outside the certificate table); `MSVCP140.dll` pair (5,754 bytes differ; 3 outside the certificate table, offsets 328–330). This is a byte fact only; it does not establish functional equivalence.

Not in the package: `msvcp140_codecvt_ids.dll` is present in the venv `PySide6/` and `shiboken6/` folders but was not collected into the trimmed package (Fact, from directory listing and the 10-copy scan). It was not analyzed.

### 2.2 Why the copies are collected (Fact, source-verified)

PyInstaller 6.22.3 `PyInstaller/depend/dylib.py` contains a Visual Studio 2015–2022 (VC14) block at lines 152–168. That block sits inside `_win_includes` (which begins at line 54 and whose header comment states it is a list of regex includes that override excludes), not inside `_excludes`. The VC14 entries include `vcruntime140\.dll`, `vcruntime140_1\.dll`, `msvcp140\.dll`, `msvcp140_1\.dll`, and `msvcp140_2\.dll`. Calling the installed `include_library('VCRUNTIME140_1.dll')` returns `True` (include match), so the copies are collected by design on Windows.

This corrects an earlier working assumption that the VC14 names were in `_excludes`. The root `_internal/VCRUNTIME140_1.dll` is therefore not an anomaly: the build's `COLLECT-00.toc` records it as sourced from `C:\Python314\VCRUNTIME140_1.dll`, consistent with this include rule. (Interpretation: PyInstaller's include list explains collection; it does not say which PySide6/shiboken6 copy a given loader will choose.)

The PySide6 and shiboken6 copies are collected from the wheel directories through the PySide6/shiboken6 binary dependency scan (Fact: `Analysis-00.toc` lists `PySide6\VCRUNTIME140_1.dll` and the `C:\Python314` entries). No hook source in `PyInstaller/hooks/` or the PySide6 package adds VC++ names explicitly (Fact: grep over `PyInstaller/` and `PySide6/*.py`, `shiboken6/*.py`).

### 2.3 Runtime loading (Fact, one isolated run)

Isolated profile run of the trimmed `LogSentinel-GUI.exe` with module enumeration (`ls-step9318-modules.ps1`; output `logsentinel-step-9-3-18-modules.txt`; `TOTAL_MODULES=102`; exit recorded). VC++/UCRT-named modules observed loaded, each once by basename:

| Loaded module (process path) | Version |
|---|---|
| `_internal\VCRUNTIME140.dll` | 14.51.36247.0 |
| `_internal\shiboken6\VCRUNTIME140_1.dll` | 14.44.35211.0 |
| `_internal\shiboken6\MSVCP140.dll` | 14.44.35211.0 |
| `_internal\PySide6\MSVCP140_1.dll` | 14.44.35211.0 |
| `_internal\PySide6\MSVCP140_2.dll` | 14.44.35211.0 |
| `C:\Windows\System32\msvcp_win.dll` (Windows, not package) | 651,752 | 10.0.19041.7802 | `1AE6811D068116AC90EF8EA7132C41BC415071E9B714EEB935B7D79D76EEEC3A` | Microsoft Windows (Valid signature) |
| `C:\Windows\System32\ucrtbase.dll` (Windows, not package) | 1,065,512 | 10.0.19041.7802 | `E6C3D2B25104FA81CD12383CBC4B9FBF7EBF4734A2BD0B163F644DC8D468A1ED` | Microsoft Windows (Valid signature) |

The e2e log (`logsentinel-ondir-trim-e2e-run10.log`, basenames only) lists `VCRUNTIME140.dll` and `VCRUNTIME140_1.dll` once each among 150 loaded modules; it does not give paths.

Interpretation (not proven):
- Within this process, the 14.51 root `VCRUNTIME140.dll` and the 14.44 `MSVCP140*`/`VCRUNTIME140_1.dll` copies coexist. The two versions are loaded under different basenames, so no duplicate-basename instance was observed.
- Not observed: `PySide6/VCRUNTIME140.dll` (14.44), `shiboken6/VCRUNTIME140.dll` (14.44), `PySide6/VCRUNTIME140_1.dll` (14.44), `PySide6/MSVCP140.dll` (14.44), and the root `_internal/VCRUNTIME140_1.dll` (14.51) were not in the module list. The loaded `VCRUNTIME140_1.dll` and `MSVCP140.dll` came from `shiboken6/`. Which copy Windows selects for each dependency is determined by search order and is not established by an import table alone.
- One run covers startup and the workflow path captured by the script; this is not proof for every code path, and it was not tested on other machines (see §6).

PE import scan (Fact, `logsentinel-step-9-3-18-imports.txt`): root binaries (`_bz2`, `_decimal`, `_ssl`, `_sqlite3`, `python314.dll`, `libcrypto-3`, `libssl-3`, and others) import `VCRUNTIME140.dll`; PySide6 binaries (`Qt6Core.dll`, `Qt6Gui.dll`, `Qt6Widgets.dll`, `QtCore.pyd`, `QtGui.pyd`, `pyside6.abi3.dll`, `qwindows.dll`, `MSVCP140.dll`) import `MSVCP140.dll` and/or `VCRUNTIME140_1.dll`. The root `_internal/VCRUNTIME140_1.dll` is imported by no other scanned root binary.

### 2.4 Microsoft redistribution terms (Source)

Retrieved during this step; an authoritative retrieval timestamp was not preserved in the source notes.
- `https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files`: the VC++ runtime files are distributed with Visual Studio; distribution is limited to licensed Visual Studio users under the Software License Terms; central (system-wide) deployment is recommended over application-local copies.
- `https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist`: exposes only `aka.ms/vc14/vc_redist.{x86,x64,arm64}.exe`; the mapping from these installers to the 14.44 or 14.51 file versions was **not** verified.
- `https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution`: REDIST terms (line 65); a permission to copy unmodified REDIST files for licensed users (line 185); download pointers (line 134).
- `https://visualstudio.microsoft.com/license-terms/vs2022-ga-community/`: returned a 2,466-byte stub (`ls-step9318-61926e13.txt`); not usable as evidence. `.../releases/2022/redistribution-files` and `.../license-terms/mlt553496/` returned 404.

Interpretation: these are documented constraints on redistribution and deployment of the runtime files. They are not a compliance conclusion for this package.

### 2.5 CPython notice (Fact)

`C:\Python314\LICENSE.txt` (676 lines) contains a "Microsoft Distributable Code" section at lines 284–312, which restricts that code (embedded in `.exe`, `.dll`, `.pyd` files) and not Python itself. The bundled `licenses/third-party/notices/cpython/COPYRIGHT-AND-ATTRIBUTION.txt` contains no "Microsoft" text (grep count 0). **Gap:** the Microsoft clause is not in the notice materials. Not changed here (read-only task).

---

## 3. OpenSSL 3.5.9

### 3.1 Packaged binaries (Fact)

| Package path | Bytes | SHA-256 | Python 3.14 copy |
|---|---:|---|---|
| `_internal/libcrypto-3.dll` | 6,021,880 | `75495fe0e079ab00d49be740d3c710a0b94e3f74f9648cb7cc9f768fc7f52319` | byte-identical (`C:\Python314\DLLs\libcrypto-3.dll`) |
| `_internal/libssl-3.dll` | 1,308,920 | `8957182a9c385bfd9f3f790921de2ddc614cf91f99edbed4e9e5446a46504e32` | byte-identical (`C:\Python314\DLLs\libssl-3.dll`) |

Build strings in `libcrypto-3.dll` (Fact): `OpenSSL 3.5.9 29 Sep 2026`, platform `VC-WIN64A-masm`. Imports (Fact): `libcrypto-3.dll` imports `VCRUNTIME140.dll`; `libssl-3.dll` imports `libcrypto-3.dll` and `VCRUNTIME140.dll`.

Interpretation: the DLLs are the CPython-shipped builds of OpenSSL 3.5.9. The build configuration and whether they were built from the upstream tarball below are not verified; `C:\Python314` has no OpenSSL-specific licence or notice file, and its `LICENSE.txt` has no OpenSSL section.

### 3.2 Upstream archive (Source, retrieved during this step)

- Tag: `https://github.com/openssl/openssl/releases/tag/openssl-3.5.9` (not a prerelease; published 2026-09-29 per GitHub).
- Archive: `https://github.com/openssl/openssl/releases/download/openssl-3.5.9/openssl-3.5.9.tar.gz`
  - 53,279,637 bytes; SHA-256 `603f5602e2eef00d77fbd429d34dcd5822bb301757a1bc9cdb24c670f1eb859a`.
  - Matches the published `.sha256` asset and GitHub API digest.
- The GitHub tag page alone contains only `ACKNOWLEDGEMENTS.md`; the tarball is the complete source for the check below.
- Archive top-level licence material (Fact): `LICENSE.txt` (10,175 B; SHA-256 `7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a`, Apache License 2.0 text) and `ACKNOWLEDGEMENTS.md` (159 B; SHA-256 `58dee45791f007ced048114717f86672778fe75c551827c57e760861446ce3c3`).
- **No file named `NOTICE` (or `NOTICE.*`) was found in the inspected archive** (Fact; only `usernotice`-named source/test paths). This is a finding about this archive, not proof that the packaged DLL source build has no additional notice material.

### 3.3 Bundled notice comparison (Fact)

`licenses/third-party/notices/openssl/`:
- `LICENSE-APACHE-2.0.txt` is identical to the upstream `LICENSE.txt`.
- `TAG-ACKNOWLEDGEMENTS.md` is identical to the upstream `ACKNOWLEDGEMENTS.md`.
- `NOTICE-STATUS.md` (772 B; SHA-256 `a395a737303aa66e51330ff063672faa4c8527f8e66c7c71bc07fd01a38fb7ff`) is a project-written status file, not an upstream notice.

### 3.4 Apache-2.0 §4(d) (Interpretation, for legal review)

Apache-2.0 §4(d) requires a copy of any NOTICE text file the Work includes, when redistributing, provided such a file exists. Evidence found: no NOTICE file in the 3.5.9 source archive, none in the packaged DLLs or the `C:\Python314` install. Therefore no §4(d) NOTICE-reproduction obligation was identified from the inspected upstream 3.5.9 archive. This does not establish that the packaged DLLs were built from that archive or exclude additional notices in an unverified CPython build input. No NOTICE text has been created or attributed to OpenSSL. Other Apache-2.0 §4 obligations (copy of the licence, modification notices) are not evaluated here.

Open: whether the CPython-distributed OpenSSL build carries any additional notice text not in the source archive; the `.asc` signature of the 3.5.9 archive was not verified.

---

## 4. PyInstaller 6.22.3 Bootloader and Runtime Hooks

### 4.1 Bootloader comparison (Fact)

- Installed bootloader: `.venv-build-gui/Lib/site-packages/PyInstaller/bootloader/Windows-64bit-intel/runw.exe` (SHA-256 `2291f269c3a3804fde1079462239e09a8b32fffbeeaa8f628a531faf5be77d41`).
- Packaged `LogSentinel-GUI.exe` (2,386,859 B; SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`).
- Section-level comparison: `.text`, `.data`, `.pdata`, `.fptable`, `.reloc` are byte-identical to `runw.exe`. `.rdata` differs in 4 bytes at offsets 67252–67255 (`69b7046b` in package vs `d8c4a56a` in `runw.exe`); not interpreted and not claimed functional. The package EXE adds `.rsrc` (30,720 B raw) and a 2,049,451-byte overlay (the PyInstaller archive); `runw.exe` has no overlay.

### 4.2 Archive contents (Fact)

The CArchive (listed with the venv's `pyi-archive_viewer.exe -r -b`) contains the PyInstaller bootstrap entries `pyimod01_archive`, `pyimod02_importers`, `pyimod03_ctypes`, `pyimod04_pywin32`, `pyiboot01_bootstrap`, runtime hooks `pyi_rth_inspect` and `pyi_rth_pyside6`, and `PYZ.pyz` stdlib/app modules including `_pyi_rth_utils` and `_pyi_rth_utils.qt`. The archive is compiled bytecode; source-file headers were checked in the installed PyInstaller tree (below), not inside the archive.

### 4.3 Licence mapping to installed `COPYING.txt` (Fact)

The installed `pyinstaller-6.22.3.dist-info/licenses/COPYING.txt` (SHA-256 `0598064c7d2718e38d7914a7d08343b2fa008e3bea9ebba2aa7a6ffa5900dd64`) is byte-identical to the one in the official sdist `pyinstaller-6.22.3.tar.gz` (4,437,180 B; SHA-256 `05eb2f5615503e72939a7224d68b4aff572c6b0438ee4a17d0a4b481f399362d`; PyPI-listed digest matches). Sources: [PyInstaller v6.22.3 COPYING.txt](https://raw.githubusercontent.com/pyinstaller/pyinstaller/v6.22.3/COPYING.txt), [PyPI 6.22.3 release](https://pypi.org/project/pyinstaller/6.22.3/). PyPI metadata: "GPLv2-or-later with a special exception which allows to use PyInstaller to build and distribute non-free programs (including commercial ones)".

| COPYING.txt section (line) | Scope | Licence stated | Relevant to packaged files? |
|---|---|---|---|
| General (line 11) | PyInstaller as a whole | GPL-2.0-or-later | Build-time tool; not shipped in the package |
| Bootloader Exception (lines 16–25) | `./bootloader/` and `./PyInstaller/loader` (lines 28–35) | GPL-2.0-or-later with Bootloader Exception | Yes: bootloader (`runw.exe` source) and the loader modules `pyimod01_archive`, `pyimod02_importers`, `pyimod03_ctypes`, `pyimod04_pywin32`, `pyiboot01_bootstrap` (headers checked; SPDX GPL-2.0-or-later with Bootloader Exception; copyright 2005–2023) |
| Run-time Hooks (lines 38–47) | `./PyInstaller/hooks/rthooks` | Apache-2.0 | Yes: `pyi_rth_pyside6`, `pyi_rth_inspect` (headers checked; SPDX Apache-2.0; copyright 2021–2023) |
| Additional Run-time Modules (lines 50–59) | `./PyInstaller/fake-modules` (`pyi_splash`, `_pyi_rth_utils`) | Apache-2.0 | Yes: `_pyi_rth_utils` and `_pyi_rth_utils.qt` (header checked; Apache-2.0) |

Per-file exception (Fact): `PyInstaller/hooks/hook-PySide6.QtSvg.py` (a build-time hook, not a runtime hook) has a GPL-2.0-or-later with Bootloader Exception header, not Apache-2.0. Interpretation: the Apache-2.0 terms apply to the runtime hook files, not to every hook-level file; this mapping must be stated per file. Whether any build-time hook source is packaged was not exhaustively checked (the archive is bytecode).

### 4.4 Separation from `pyinstaller-hooks-contrib` (Fact)

`pyinstaller-hooks-contrib` is a build-time dependency for hook discovery; its licence does not change the Apache-2.0 terms of the runtime hooks listed in §4.3. (Interpretation.)

---

## 5. Open Questions

1. **VC++ 14.44 vs 14.51 selection.** Which copy Windows selects for each dependency in each code path is not established by import tables or one module-load run. Confirm with a loader trace (for example, `Process Monitor` or `DLL` load events) on a clean profile, if duplicate-version loading matters for support.
2. **VC++ 14.44 provenance.** The Qt-signed 14.44.35211.0 copies come from the PySide6 and shiboken6 wheels. Confirm the wheel versions and Microsoft redistribution basis; the Microsoft pages did not map 14.44 to an official installer.
3. **VC++ redistribution terms.** The Visual Studio license-terms page used for the Community edition is a stub; the REDIST terms were read from the Visual Studio 2022 redistribution page only. A full review of the applicable Microsoft licence text is needed before shipping application-local copies.
4. **CPython Microsoft clause.** The Microsoft Distributable Code text (`LICENSE.txt` lines 284–312) is not in the bundled CPython notice excerpt. Add or decide in a separate notice task.
5. **OpenSSL build provenance.** Confirm that the CPython-shipped `libcrypto-3.dll`/`libssl-3.dll` were built from `openssl-3.5.9.tar.gz`, and verify the archive's `.asc` signature against the OpenSSL release key.
6. **PyInstaller build-time hook files.** Confirm whether any `hook-*.py` source is included in the package (none identified by the 182-file listing, which lists no `.py` files outside `_internal` bytecode); if any is, state its GPL-2.0-or-later with exception header per file.
7. **`.rdata` 4-byte difference** in `LogSentinel-GUI.exe` vs `runw.exe`: uninterpreted; likely a build-stamp or resource-table artifact, but not verified.

## 6. Next Actions (not performed; require authorization)

- Trace VC++ DLL load order in a clean profile on a standard desktop.
- Obtain Microsoft's full applicable licence text for the packaged VC++ files (through the licensed Visual Studio channel, if available).
- Verify the OpenSSL archive signature and the CPython build configuration.
- Decide whether to add the CPython Microsoft clause and any VC++ notice to `licenses/third-party/notices/` (separate task; not performed here).
- Test on RDP, GPU-less/software-rendering, and high-DPI displays (outside this step).

---

## 7. Verification

- This file was written by the agent in this step. Its size and SHA-256 are recorded in the completion report, not inside this file.
- The trimmed package identity was rechecked after report creation: 182 files / 80,058,228 B; no package files were edited by this step.
- Git status was compared to `C:/Users/DELL/AppData/Local/Temp/logsentinel-step-9-3-18-status-before.txt`; the only new status entry is this report.
