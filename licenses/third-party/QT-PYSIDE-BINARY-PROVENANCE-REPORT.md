# Qt / PySide6 / Shiboken6 binary provenance report — trimmed Windows onedir package

**Investigation date:** 2026-11-26  
**Disposition:** **No verified upstream binary match.** The inspected evidence supports a probable Qt-produced build for the Qt DLLs/plugins and probable Qt for Python distribution origin for the PySide6/Shiboken6 binaries, but does not establish which exact upstream binary archives supplied them or connect them reproducibly to a source revision, build job, configuration, or patch set. This is a read-only engineering evidence report, not legal advice, a compliance finding, or release approval.

## 1. Executive summary

The artifact inspected was `dist/gui-ondir-trim-test/LogSentinel-GUI/`, the current trimmed package described in the prior audits—not the historical 185-file package in `qt/INVENTORY.md`. It contains 41 relevant native PE files under `_internal/PySide6/` and `_internal/shiboken6/`: five Qt module DLLs, 20 Qt plugins, six PySide6 native modules, two Shiboken6 native modules, and eight VC++ runtime DLL copies stored inside those two package trees.

### Findings in brief

- All 41 files are AMD64 (`IMAGE_FILE_MACHINE_AMD64`, `0x8664`) PE files. Windows file-version resources identify the five Qt libraries and 20 plugins as Qt **6.12.0.0**; the eight nested VC++ runtime copies report **14.44.35211.0**. The PySide6/Shiboken6 extension files have no corresponding PE file-version resource; installed Python metadata identifies the distributions as **6.12.0** and their wheel tag as `cp310-abi3-win_amd64`.
- Authenticode verification on this machine reports **Valid** for all 41 files. All use the same signer certificate subject, **The QT Company Oy**, thumbprint `3D89F77A33C5AD89F45F681848958E755B727C5A`, and each has a timestamp. This is strong signer-integrity evidence, not proof of the specific source or archive from which each file was built, nor a redistribution determination.
- Every one of the 140 files in the packaged `PySide6/` and `shiboken6/` trees—not only the native files—matches its relative path in the existing `.venv-build-gui` installation byte-for-byte. Of those 140, **130** match SHA-256 entries in the local `pyside6_essentials-6.12.0.dist-info/RECORD`, **two** match the local `shiboken6-6.12.0.dist-info/RECORD`, and **eight VC++ DLLs have no hash entry** in those records. The wheel records and metadata are local installed files, not signed provenance attestations.
- The Qt DLLs/plugins contain CodeView RSDS records with PDB paths under `C:\Users\qt\work\qt\{qtbase_build,qtsvg_build,qtimageformats_build}`; their embedded linker version is **14.44**. These paths and versions are consistent with a Qt Windows build environment and the Qt module split. They are useful provenance clues, but PDB path strings and linker version do not identify the exact source checkout or prove the referenced PDB belonged to the binary.
- Public official Qt 6.12.0 source releases, Qt MSVC2022_64 component archives, and Qt for Python 6.12.0 source and wheel releases are listed with public digests. No source archive, wheel, or candidate Qt binary archive was downloaded or compared with this package. Consequently, **no binary hash was matched to an official upstream binary release artifact**.
- There is no evidence sufficient to determine whether the Qt files came from the Qt installer component archives, a Qt for Python wheel, another vendor build channel, or another distribution. Local `pip` metadata says pip installed the packages, but no package index, original wheel archive, wheel URL, install log, wheel hash, or `direct_url.json` was found.
- The exact compiler family is supported by the PE linker version; an exact compiler build, Windows SDK, Qt configure options, Python version used to compile PySide, debug/release configuration, source patches, and source-to-binary reproducibility are **not established**.

**Classification summary:** no `Verified upstream binary match`; Qt binaries are **probable Qt-produced origin with supporting evidence**, PySide/Shiboken modules are **local installation match plus probable Qt for Python package origin**, and nested VC++ files are **local installation match only / unverified exact supplier artifact**. The public source releases are **verified as published source candidates only; binary match unverified**. See §7 for the component-by-component matrix.

## 2. Scope, artifact identity, and method

### 2.1 Artifact and scope

- Package: `dist/gui-ondir-trim-test/LogSentinel-GUI/`
- Package identity baseline: **182 regular files / 80,058,228 bytes**.
- Executable: `LogSentinel-GUI.exe`, 2,386,859 bytes; SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- This report’s exact native inventory is the 41 DLL/PYD files beneath `_internal/PySide6/` and `_internal/shiboken6/`. The 99 `.qm` catalogs and four frozen Python code objects (`PySide6`, `PySide6.support`, `PySide6.support.deprecated`, `shiboken6`) are not PE binaries; they are noted where relevant and covered in more detail in `QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md`.
- The two package-root VC++ DLLs (`_internal/MSVCP140.dll`, `_internal/VCRUNTIME140.dll`) are outside this report’s Qt/PySide/Shiboken-tree inventory. They remain in the broader package and are covered by `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`.
- The trimmed package does not contain `PySide6/Qt6Pdf.dll`, `PySide6/plugins/imageformats/qpdf.dll`, or `PySide6/opengl32sw.dll`.

### 2.2 Checks performed

Read-only checks included: direct package inventory, SHA-256 hashing, PE machine/file-version/COFF/linker/CodeView inspection, Windows `Get-AuthenticodeSignature`, local Python distribution metadata and RECORD inspection, package-to-local-install byte comparison, review of the existing PyInstaller `Analysis-00.toc`/`COLLECT-00.toc` for source paths, and official upstream release-index/source/build-documentation searches. No source, wheel, or Qt binary archive was downloaded. No binary, package, build, spec, existing report, or release artifact was written or altered; no build, installation, or replacement test was performed.

The final package inventory and hash checks in §2.1 are repeated after report creation. Official server-index and mirrorlist hashes below were transcribed from the public listings; they were **not locally verified against downloaded artifacts**.

## 3. Exact native binary inventory

Paths are relative to the package root. All rows are PE machine `0x8664` (AMD64). The signature column is abbreviated because the observation is common to every row: Windows reports **Valid**, signer **The QT Company Oy**, signer certificate thumbprint `3D89F77A33C5AD89F45F681848958E755B727C5A`; timestamp present. Version source is stated per row; a distribution version is not being presented as a PE resource when none exists.

### 3.1 Qt module DLLs and plugins

All 25 listed Qt DLLs report file and product version `6.12.0.0` in Windows version resources.

| Package-relative path | Component | File version | Bytes | SHA-256 | Signature |
|---|---|---:|---:|---|---|
| `_internal/PySide6/Qt6Core.dll` | Qt Core | 6.12.0.0 | 10,472,760 | `f57ed38afd95d0306cca9d88d997f639f70c7628a4f1f064eae291d579487121` | Valid — Qt Company |
| `_internal/PySide6/Qt6Gui.dll` | Qt Gui | 6.12.0.0 | 9,683,256 | `abd20026e190e8cc69667d1bea042db05cd353cc05e7da74b063c20b7da3f6cd` | Valid — Qt Company |
| `_internal/PySide6/Qt6Network.dll` | Qt Network | 6.12.0.0 | 1,780,536 | `1c7c393b264ae78f4dee211656377a086c4be714bf768d3135f94f11c1d0be61` | Valid — Qt Company |
| `_internal/PySide6/Qt6Svg.dll` | Qt Svg | 6.12.0.0 | 608,056 | `8f1de5b28aab1eedb415c751c81f9cfaa2804242868c0ceea5f3fdb4b2babca4` | Valid — Qt Company |
| `_internal/PySide6/Qt6Widgets.dll` | Qt Widgets | 6.12.0.0 | 6,520,120 | `2f62cbe2869fff4e20df7369c2786e1ec7ec290d5a63d1371b7f70cf06909c3f` | Valid — Qt Company |
| `_internal/PySide6/plugins/generic/qtuiotouchplugin.dll` | Qt generic plugin | 6.12.0.0 | 102,712 | `8565656807db29cfb6170e6803181f24e0bed3aa1b14684d29694e375cc5ee96` | Valid — Qt Company |
| `_internal/PySide6/plugins/iconengines/qsvgicon.dll` | Qt SVG icon-engine plugin | 6.12.0.0 | 72,504 | `f9e21af351bd5d5629bc00e8e3796b552eca92d1a9645438c865b9c53af1714f` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qgif.dll` | Qt image-format plugin | 6.12.0.0 | 48,440 | `77782de4aa4f7b75a7cc4d3f24aee49da935c312ea13d25f4cda3a98d180145c` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qicns.dll` | Qt image-format plugin | 6.12.0.0 | 56,632 | `93e2e588cd1036af3c6300b539d648b3825625788e59a3f0f1863d9901c9759f` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qico.dll` | Qt image-format plugin | 6.12.0.0 | 47,416 | `a0e4d0d0319e075f6cc5f774084bf390f7af83600f38685c6bc9c407681cc22c` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qjpeg.dll` | Qt image-format plugin | 6.12.0.0 | 592,696 | `dd42bdcd229744a9515db82ba9a802c74b6589cc508c3e85fb30f06ba24b9da6` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qsvg.dll` | Qt SVG image-format plugin | 6.12.0.0 | 40,248 | `b63f97ed0ae60aa5bc332c37e429c1f31154e1eee358352b2c49598c5269843b` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qtga.dll` | Qt image-format plugin | 6.12.0.0 | 39,224 | `ce95aa019d940533341b4f08a10ddd3b0393162678c47904251da77aeadfd34e` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qtiff.dll` | Qt image-format plugin | 6.12.0.0 | 991,032 | `ce696a2dd2e57b8852f7d01834725f54a4d0be66c3d2c491df60fd907fece907` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qwbmp.dll` | Qt image-format plugin | 6.12.0.0 | 36,664 | `e118243bd3528aa5fe6378a8839abe0efc200e891af06ee369b97b2ff239b89c` | Valid — Qt Company |
| `_internal/PySide6/plugins/imageformats/qwebp.dll` | Qt image-format plugin | 6.12.0.0 | 566,072 | `02ae5555b688f78aade5cedcd66c646b73d519460c008c23e75ad408bd152668` | Valid — Qt Company |
| `_internal/PySide6/plugins/networkinformation/qnetworklistmanager.dll` | Qt network-information plugin | 6.12.0.0 | 79,160 | `2bd047476183c76004221fb44adb7ada9b4b6ce5c2929d63ff67a5305b430f1a` | Valid — Qt Company |
| `_internal/PySide6/plugins/platforms/qdirect2d.dll` | Qt platform plugin | 6.12.0.0 | 1,082,168 | `18213464be5a5a1d39af6a2c876ce21a6bb6a634c814651d09f0ef7e4719edc2` | Valid — Qt Company |
| `_internal/PySide6/plugins/platforms/qminimal.dll` | Qt platform plugin | 6.12.0.0 | 62,264 | `c9025bc5f4653c5aadac87f06ab391763e82adf792f6759c6027a78a5efcaf5c` | Valid — Qt Company |
| `_internal/PySide6/plugins/platforms/qoffscreen.dll` | Qt platform plugin | 6.12.0.0 | 111,928 | `d24ef380ab0882d39f21539dcf57ab4213875a6fc658a53012f2d2fd275c6f69` | Valid — Qt Company |
| `_internal/PySide6/plugins/platforms/qwindows.dll` | Qt Windows platform plugin | 6.12.0.0 | 1,001,784 | `ddd5cf6a96f058cfafcbc901ddeb5df010d755f0716beacfb557f8b27b733afe` | Valid — Qt Company |
| `_internal/PySide6/plugins/styles/qmodernwindowsstyle.dll` | Qt style plugin | 6.12.0.0 | 241,464 | `74d4c47b56a942afb3723bb105900501bb8f91a46a8b592fa722cc4fdb2ce9bf` | Valid — Qt Company |
| `_internal/PySide6/plugins/tls/qcertonlybackend.dll` | Qt TLS backend plugin | 6.12.0.0 | 105,784 | `87574d467b6f9640a15e37bf4183179c6a7cefc4dc84346b8f4cffb989cf1e12` | Valid — Qt Company |
| `_internal/PySide6/plugins/tls/qopensslbackend.dll` | Qt TLS backend plugin | 6.12.0.0 | 317,752 | `94b3492bc4087da2818e2749a5a03f7d810611b2e3648bd8d580ad087363046f` | Valid — Qt Company |
| `_internal/PySide6/plugins/tls/qschannelbackend.dll` | Qt TLS backend plugin | 6.12.0.0 | 249,144 | `2915a86a2531e65fd4905f0cc1c8dc353772a4f52aeda5100725dd9249db54d1` | Valid — Qt Company |

### 3.2 PySide6, Shiboken6, and nested VC++ runtime files

PE version resources are absent on the PySide6 and Shiboken6 binding modules, so their version column shows the installed distribution metadata, not an embedded PE version. The VC++ file versions below are from PE version resources.

| Package-relative path | Component | Version evidence | Bytes | SHA-256 | Signature |
|---|---|---|---:|---|---|
| `_internal/PySide6/QtCore.pyd` | PySide6 QtCore extension | PySide6 6.12.0 metadata | 3,521,336 | `6486f6f0a2fec42fc8c652c0b76bb3ad0d44eaccad9c72e577116a075681eebb` | Valid — Qt Company |
| `_internal/PySide6/QtGui.pyd` | PySide6 QtGui extension | PySide6 6.12.0 metadata | 3,936,056 | `9ac544d1bcf8a26c408c63090d05506f8382d5378ee3a204e29a3ac5449c5b2b` | Valid — Qt Company |
| `_internal/PySide6/QtNetwork.pyd` | PySide6 QtNetwork extension | PySide6 6.12.0 metadata | 1,039,672 | `22bffdb2a431b5a986de255f7eb0fcd1fd7d9e85c53967978e2ab479b33a13c5` | Valid — Qt Company |
| `_internal/PySide6/QtSvg.pyd` | PySide6 QtSvg extension | PySide6 6.12.0 metadata | 116,536 | `c9bdacf14ce30f4de75179f999ff20d7a8856126dbebd3a518a5e1c2916a3a6d` | Valid — Qt Company |
| `_internal/PySide6/QtWidgets.pyd` | PySide6 QtWidgets extension | PySide6 6.12.0 metadata | 4,911,416 | `a8e323e56a93c1a8a70981c36a409c0a2546e7a08da5be8ca4e03dfd27febc2a` | Valid — Qt Company |
| `_internal/PySide6/pyside6.abi3.dll` | PySide6 support DLL | PySide6 6.12.0 metadata | 262,968 | `d5b87ccb0a7c305854bd120242b0a75002d0b50a35532d0f6171e4ed0f3cc82a` | Valid — Qt Company |
| `_internal/shiboken6/Shiboken.pyd` | Shiboken6 extension | Shiboken6 6.12.0 metadata | 33,080 | `8ccf415b2cefb5b6462504581ab1993fb41afe04e415931d8a72049f1c79b267` | Valid — Qt Company |
| `_internal/shiboken6/shiboken6.abi3.dll` | Shiboken6 support DLL | Shiboken6 6.12.0 metadata | 399,672 | `07c318c02be5a3a9f1475f5a2d0cd438f4d4ea3288c28e2e10bc5ebbbec8de86` | Valid — Qt Company |
| `_internal/PySide6/MSVCP140.dll` | VC++ runtime copy | 14.44.35211.0 | 549,176 | `f6f1d55bfd64027820ddce48f9cd8cf46d53bfa34047e6acf4ef348d492a05cb` | Valid — Qt Company |
| `_internal/PySide6/MSVCP140_1.dll` | VC++ runtime copy | 14.44.35211.0 | 27,448 | `2be87527c41e1ba8aff48e326e0adcd4743516e0bbcc9304986c726e27de6aca` | Valid — Qt Company |
| `_internal/PySide6/MSVCP140_2.dll` | VC++ runtime copy | 14.44.35211.0 | 271,672 | `6a72ed8a87eae1671640bd1ca98eccb989f1772ae46ab84594e385bf6d4ac4fb` | Valid — Qt Company |
| `_internal/PySide6/VCRUNTIME140.dll` | VC++ runtime copy | 14.44.35211.0 | 116,024 | `a36e0cb185eb89533ed96d4568138f86a1315756a8b2644c5963a8ce23e32101` | Valid — Qt Company |
| `_internal/PySide6/VCRUNTIME140_1.dll` | VC++ runtime copy | 14.44.35211.0 | 41,272 | `302b1e160e858602490a55e32ae2e29ddfc0bec2a188e19550cb655cdaa58f9c` | Valid — Qt Company |
| `_internal/shiboken6/MSVCP140.dll` | VC++ runtime copy | 14.44.35211.0 | 549,176 | `1ba4d7c0a95d375da138a057a57593b33510ad5bda6c5e2686afd68faa5b4231` | Valid — Qt Company |
| `_internal/shiboken6/VCRUNTIME140.dll` | VC++ runtime copy | 14.44.35211.0 | 116,024 | `e7be9112ee9a5b9f44b44bff24cb761cca9b1ed7550b612f77b70edfcf5fdabf` | Valid — Qt Company |
| `_internal/shiboken6/VCRUNTIME140_1.dll` | VC++ runtime copy | 14.44.35211.0 | 41,272 | `f02cd4a862b85a9a3153d27e15e5a213f5df8e3d77004ed2e87b8a7e8873d97c` | Valid — Qt Company |

## 4. Qt binary provenance findings

### 4.1 Direct observations

- Qt Core, Gui, Network, Svg, Widgets and all 20 plugins expose file/product version `6.12.0.0`, Qt framework description/company metadata, AMD64 machine type, and Authenticode verification as described above.
- Each of the 25 Qt files has a CodeView RSDS reference and linker version `14.44`. Exact PE timestamp and RSDS identifiers/paths are:

| File (beneath `_internal/PySide6/`) | COFF timestamp (UTC) | PDB GUID / age | Embedded PDB path |
|---|---|---|---|
| `plugins/generic/qtuiotouchplugin.dll` | 2026-09-26 04:55:28 | `2abac441-9991-495f-9a45-2141f51edba1 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\generic\qtuiotouchplugin.pdb` |
| `plugins/iconengines/qsvgicon.dll` | 2026-09-26 10:15:59 | `7154b64c-47a2-49a3-90b0-2b216312aee3 / 1` | `C:\Users\qt\work\qt\qtsvg_build\plugins\iconengines\qsvgicon.pdb` |
| `plugins/imageformats/qgif.dll` | 2026-09-26 04:55:27 | `c5dbe8fc-5a16-4cbc-b44d-d00f2719aa5c / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\imageformats\qgif.pdb` |
| `plugins/imageformats/qicns.dll` | 2026-09-26 10:17:00 | `1b4d18b2-7d98-42f1-949f-f456b3ef5de1 / 1` | `C:\Users\qt\work\qt\qtimageformats_build\plugins\imageformats\qicns.pdb` |
| `plugins/imageformats/qico.dll` | 2026-09-26 04:54:16 | `efec4dd9-478b-4cce-b24e-d8f5f468d499 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\imageformats\qico.pdb` |
| `plugins/imageformats/qjpeg.dll` | 2026-09-26 04:55:26 | `a9609055-434d-43ec-8540-d12ac249e925 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\imageformats\qjpeg.pdb` |
| `plugins/imageformats/qsvg.dll` | 2026-09-26 10:15:59 | `eb47c30c-f1fc-4c15-aa3f-8b39b2f508ca / 1` | `C:\Users\qt\work\qt\qtsvg_build\plugins\imageformats\qsvg.pdb` |
| `plugins/imageformats/qtga.dll` | 2026-09-26 10:16:21 | `80136a4b-5e15-4e8e-901d-b34652018c2e / 1` | `C:\Users\qt\work\qt\qtimageformats_build\plugins\imageformats\qtga.pdb` |
| `plugins/imageformats/qtiff.dll` | 2026-09-26 10:16:24 | `27e21650-b976-4ae1-9f54-ddfb9f67e451 / 1` | `C:\Users\qt\work\qt\qtimageformats_build\plugins\imageformats\qtiff.pdb` |
| `plugins/imageformats/qwbmp.dll` | 2026-09-26 10:16:08 | `3e722abd-8262-42b1-a31f-8b35ca64c6cf / 1` | `C:\Users\qt\work\qt\qtimageformats_build\plugins\imageformats\qwbmp.pdb` |
| `plugins/imageformats/qwebp.dll` | 2026-09-26 10:16:47 | `4bb6aec1-495b-4f26-a807-e20137dbe830 / 1` | `C:\Users\qt\work\qt\qtimageformats_build\plugins\imageformats\qwebp.pdb` |
| `plugins/networkinformation/qnetworklistmanager.dll` | 2026-09-26 04:55:34 | `bd7e5d3c-acef-411d-9b6b-6e9fc07447f6 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\networkinformation\qnetworklistmanager.pdb` |
| `plugins/platforms/qdirect2d.dll` | 2026-09-26 04:55:13 | `5c5a4173-986c-488e-a087-f7d8f74af281 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\platforms\qdirect2d.pdb` |
| `plugins/platforms/qminimal.dll` | 2026-09-26 04:54:15 | `9ef25d98-9224-4fe2-9cf1-3d407b7cb099 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\platforms\qminimal.pdb` |
| `plugins/platforms/qoffscreen.dll` | 2026-09-26 04:54:15 | `539c8544-cc46-4ebb-ba8f-54e2d4958d2d / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\platforms\qoffscreen.pdb` |
| `plugins/platforms/qwindows.dll` | 2026-09-26 04:54:46 | `e1ea6e84-e0cd-4e50-8074-72d6247bddb5 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\platforms\qwindows.pdb` |
| `plugins/styles/qmodernwindowsstyle.dll` | 2026-09-26 04:55:43 | `2ca85132-1341-4f96-9a80-e1739feab648 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\styles\qmodernwindowsstyle.pdb` |
| `plugins/tls/qcertonlybackend.dll` | 2026-09-26 04:55:42 | `3d5d3b75-9219-4dae-8239-4217a71ba7e2 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\tls\qcertonlybackend.pdb` |
| `plugins/tls/qopensslbackend.dll` | 2026-09-26 04:55:34 | `49d6f29f-9899-489b-a1f2-530e5bcf538b / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\tls\qopensslbackend.pdb` |
| `plugins/tls/qschannelbackend.dll` | 2026-09-26 04:55:38 | `6a5ae844-0a5d-4e2f-ade8-d3ab2897caa8 / 1` | `C:\Users\qt\work\qt\qtbase_build\plugins\tls\qschannelbackend.pdb` |
| `Qt6Core.dll` | 2026-09-26 04:49:33 | `57cb85ac-6360-4f46-b2ad-0a5815c3565b / 1` | `C:\Users\qt\work\qt\qtbase_build\bin\Qt6Core.pdb` |
| `Qt6Gui.dll` | 2026-09-26 04:52:18 | `5630957c-212a-4ce1-bd47-629647e5c1a1 / 1` | `C:\Users\qt\work\qt\qtbase_build\bin\Qt6Gui.pdb` |
| `Qt6Network.dll` | 2026-09-26 04:50:49 | `cdd72cad-1b5c-4b29-a382-13f0573ae95e / 1` | `C:\Users\qt\work\qt\qtbase_build\bin\Qt6Network.pdb` |
| `Qt6Svg.dll` | 2026-09-26 10:15:48 | `a108be2e-2595-49b2-a7ee-c6d195722804 / 1` | `C:\Users\qt\work\qt\qtsvg_build\bin\Qt6Svg.pdb` |
| `Qt6Widgets.dll` | 2026-09-26 04:54:08 | `7611761c-6d45-4bae-9354-3792862acced / 1` | `C:\Users\qt\work\qt\qtbase_build\bin\Qt6Widgets.pdb` |

The embedded PDB paths organize into these Qt source/build areas:
  - `qtbase_build`: Core, Gui, Network, Widgets; `qtuiotouchplugin`; image plugins `qgif`/`qico`/`qjpeg`; network-information `qnetworklistmanager`; platform plugins `qdirect2d`/`qminimal`/`qoffscreen`/`qwindows`; style `qmodernwindowsstyle`; TLS plugins `qcertonlybackend`/`qopensslbackend`/`qschannelbackend`.
  - `qtsvg_build`: `Qt6Svg.dll`, `qsvgicon.dll`, `qsvg.dll`.
  - `qtimageformats_build`: image-format plugins `qicns`, `qtga`, `qtiff`, `qwbmp`, `qwebp`.
- Representative paths embedded in the files are `C:\Users\qt\work\qt\qtbase_build\bin\Qt6Core.pdb`, `C:\Users\qt\work\qt\qtsvg_build\plugins\imageformats\qsvg.pdb`, and `C:\Users\qt\work\qt\qtimageformats_build\plugins\imageformats\qwebp.pdb`. The full inventory is grouped above; RSDS values are debug identifiers, not source hashes.
- The COFF characteristics include `IMAGE_FILE_DEBUG_STRIPPED`; external CodeView references remain. This is consistent with symbols being kept separately. It does **not** establish whether the compiled configuration was optimized Release, Debug, or another configuration.
- All 25 Qt DLLs/plugins match the same-relative-path files in the existing venv and have matching hashes in the local `pyside6_essentials-6.12.0.dist-info/RECORD`.

### 4.2 Official binary and source candidates

The official Qt online SDK repository publicly lists a Qt 6.12.0 `win64_msvc2022_64` component family. Examples include:

- `qtbase`: `6.12.0-0-202609280346qtbase-Windows-Windows_11_24H2-MSVC2022-Windows-Windows_11_24H2-X86_64.7z`, published size 40,184,745 bytes, published SHA-256 `219d1b86def3be418e31d704572bc4acc91b2ec373c65595c9fb12b42bf098dc`.
- `qtsvg`: `6.12.0-0-202609280346qtsvg-Windows-Windows_11_24H2-MSVC2022-Windows-Windows_11_24H2-X86_64.7z`, published size 690,561 bytes, published SHA-256 `dfcad02224b71724e3314d0bc3ffc0b862dfa6e02bc4aadd39f1738f6c364c79`.
- `qtimageformats`: `6.12.0-0-202609280346qtimageformats-Windows-Windows_11_24H2-MSVC2022-Windows-Windows_11_24H2-X86_64.7z`, published size 1,055,799 bytes, published SHA-256 `b5a5729e0dab582a3676bf82ffc77b9de5f95bb9d0a60226f730d97fad2db448`.

The filenames, server metadata and PDB paths are consistent with these candidate official Qt builds, especially the MSVC2022/x64 candidate. **No archive contents or binary hashes were compared**: the archives were not downloaded. The public hashes authenticate only the listed archive bytes when verified against an acquired archive; they do not match an individual installed file by assertion alone.

The official Qt 6.12.0 source projects/releases `qtbase`, `qtsvg`, and `qtimageformats` are identified in §8. Their same-version availability does not identify the source used in these exact PE files. No matching SBOM, build ID, build job provenance, Qt source revision manifest, patch manifest, linker command, Qt configure summary/cache, dependency-source manifest, or PDB files were found in the repository/package evidence examined.

### 4.3 Origin assessment

**Classification: probable Qt-produced origin with supporting evidence; exact upstream binary artifact unverified.** Evidence includes Qt signer, Qt 6.12.0 resource metadata, Qt CI-style PDB paths, MSVC 14.44 linker metadata, matching venv files and local RECORD hashes, and compatible official 6.12.0 Qt binary archive candidates. No evidence establishes whether the bytes were extracted from those Qt installer component archives, from the Qt for Python wheel, or delivered through another channel. No verified upstream binary match is claimed.

## 5. PySide6 provenance findings

### 5.1 Installed distribution and package mapping

The existing `.venv-build-gui/Lib/site-packages/` contains `pyside6-6.12.0.dist-info`, `pyside6_essentials-6.12.0.dist-info`, `pyside6_addons-6.12.0.dist-info`, and other 6.12.0 distribution metadata. The PySide6 aggregate package metadata says version 6.12.0, requires Python `>=3.10,<3.16`, declares `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`, and depends on `PySide6_Essentials==6.12.0` and `PySide6_Addons==6.12.0`. Its WHEEL record is `cp310-abi3-win_amd64`; `INSTALLER` says `pip`.

The six native files in §3.2 match the local site-packages bytes. Their 130 PySide6-tree RECORD matches across all 140 tree files include the five `.pyd` modules, `pyside6.abi3.dll`, the 25 Qt DLLs/plugins, and the packaged catalog set. Thus the records provide a local file-to-installed-manifest consistency check. However:

- no installed `direct_url.json` identifies an index or direct URL;
- `INSTALLER=pip` does not identify the configured index, mirror, downloaded wheel, or who supplied it;
- the original `.whl` file, its SHA-256, pip download/install transcript, and artifact provenance record were not found; and
- a wheel RECORD is an internal manifest, not a signature. Its presence in site-packages does not independently prove it was copied from the official wheel or remained unaltered.

The pre-existing PyInstaller `Analysis-00.toc` and `COLLECT-00.toc` list the local `.venv-build-gui/Lib/site-packages/PySide6/...` paths as packaging sources. This supports the **application packaging** step from that local installation, not the upstream origin of that installation.

### 5.2 Official release candidates and classification

The official Qt download index lists `pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl`, size 82,153,795 bytes, published SHA-256 `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42`. The official source archive and `pyside-setup` tag `v6.12.0` are also listed in §8. These establish published candidates and metadata, not identity with the local distribution.

**Classification: local installation match, with probable Qt for Python distribution origin; exact official wheel match unverified.** All native PySide6 files are validly signed by The QT Company Oy and have local 6.12.0 metadata and RECORD matches. No official wheel was acquired for archive-hash or embedded-RECORD comparison; no build attestation ties the files to a source tag, source hash, patch set, build job, or license selection.

## 6. Shiboken6 provenance findings

The existing venv contains `shiboken6-6.12.0.dist-info`. Its metadata reports version 6.12.0, the same `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only` expression, Python `>=3.10,<3.16`, and WHEEL tag `cp310-abi3-win_amd64`; `INSTALLER` says `pip`. Both packaged Shiboken native files match their same-relative-path site-packages files and the two hash entries in the local `shiboken6-6.12.0.dist-info/RECORD`. The corresponding installed metadata is not a signed provenance statement, and the original wheel, download URL, and install log are absent.

The official Qt download index lists `shiboken6-6.12.0-cp310-abi3-win_amd64.whl`, size 1,265,476 bytes and published SHA-256 `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e`. The official source candidate is the same `pyside-setup` v6.12.0 source archive/tag that contains Shiboken sources. No wheel/source was downloaded or matched.

**Classification: local installation match, with probable Qt for Python distribution origin; exact official wheel and source-build match unverified.** Signature, distribution metadata and manifest matches are corroborating evidence but not a source-to-binary link.

## 7. Build environment evidence and source-to-binary traceability matrix

### 7.1 What build metadata establishes

**Observed locally:**

- `.venv-build-gui/pyvenv.cfg` identifies base interpreter `C:\Python314`, Python 3.14.10. The active interpreter reports `[MSC v.1944 64 bit (AMD64)]`, build tag `b703b2c`, and an October 2026 build date. The development machine used Windows 10 build 19045.
- The installed PySide6 and Shiboken6 WHEEL metadata permits Python 3.10+ via a `cp310-abi3-win_amd64` tag. This is declared ABI compatibility, not proof that Python 3.14 was used to compile these extension modules.
- PE records for all 41 files identify AMD64 and linker version 14.44. The Qt files have Qt build-tree PDB paths; PySide/Shiboken modules have October 5, 2026 COFF header timestamps but no CodeView PDB reference. PE timestamps are metadata fields and are not independently verified wall-clock build records.
- Microsoft’s version mapping identifies MSVC 14.44 / V143 with Visual Studio 2022 version 17.14. This makes a VS 2022 17.14-era toolchain probable. The PE linker field does not provide the compiler’s full servicing build, all compiler flags, or Windows SDK version.
- The Qt and PySide source-build documentation lists typical prerequisites. Qt’s 6.12 Windows build docs list supported MSVC 2022/2026 configurations and build tools; Qt for Python Windows instructions say Qt, Python and PySide should use compatible MSVC and list MSVC 2022 and libclang. These are general requirements, **not records of what generated this package**.
- Qt’s COFF symbols, version resources and signer point to Qt’s producer environment. The packaging TOCs point to local installed wheel paths. No Qt/PySide source checkout, original wheels, PDBs, compiler/linker command transcript, CMake cache, Qt SDK install manifest, Windows SDK identification, build SBOM, patch manifest, or build attestation was found in the inspected repository paths. `cl`, `cmake`, `ninja`, `dumpbin`, `llvm-readobj`, `signtool`, and `qtpaths6` were not on the current PATH at inspection time; this is not evidence that they were unavailable to the upstream producer.

### 7.2 Evidence classification matrix

| Component group | Strongest observed link | Classification | Link still missing |
|---|---|---|---|
| `Qt6Core/Gui/Network/Widgets.dll` | Qt signer; 6.12.0.0 resources; linker 14.44; Qt `qtbase_build` CodeView paths; local essentials RECORD hashes; official Qt 6.12.0 MSVC2022 x64 candidate archive | **Probable Qt-produced origin with supporting evidence**; **not a verified upstream binary match** | Match each SHA-256 to an acquired official archive or signed supplier manifest; source commit, patches, toolchain/config, dependencies, SBOM and build provenance |
| `Qt6Svg.dll` | Qt signer/version; `qtsvg_build` PDB path; local RECORD hash; official qtsvg 6.12.0 MSVC candidate | **Probable Qt-produced origin with supporting evidence**; binary match unverified | Same exact archive/source/build chain |
| 20 Qt plugin DLLs | Qt signer/version; project-specific PDB paths matching qtbase/qtsvg/qtimageformats build-directory names; local RECORD hashes; official component archive candidates | **Probable Qt-produced origin with supporting evidence**; binary match unverified | Per-file archive and source target match, source revisions, dependency/codec map, patches, flags and matching build attestation |
| Five PySide `.pyd` modules + `pyside6.abi3.dll` | Qt signer; same-relative local install equality; essentials RECORD hashes; 6.12.0 metadata; Qt official wheel candidate | **Local installation match plus probable Qt for Python origin**; official wheel match unverified | Original wheel/hash/index/install log, source commit, generated code/typesystems, Python/Qt inputs, build flags and attestation |
| `Shiboken.pyd` + `shiboken6.abi3.dll` | Qt signer; same-relative local install equality; Shiboken RECORD hashes; 6.12.0 metadata; official wheel candidate | **Local installation match plus probable Qt for Python origin**; official wheel match unverified | Original wheel/hash/index/install log, source/generated inputs, patches, build settings and attestation |
| Eight VC++ DLLs under PySide/Shiboken | Qt signer; 14.44.35211.0 version resource; package/local installation equality; matching `COLLECT` paths | **Local installation match only; probable bundled wheel copies** | Exact wheel entry/hash (local RECORD has no hash entries for these eight), Microsoft distributable source/provenance and eligibility, and Qt’s written basis for the copies |
| Official Qt/PySide source releases and online binary packages | Official versioned indexes, source tags, release archives, package names and published digests | **Official release artifacts listed; package-binary match unverified** | Acquire under controlled evidence procedures and compare archive contents/records/hashes; supplier/build provenance is still needed where artifacts are not bit-identical |
| Build configuration / patch state | COFF linker and PDB path strings; installed distribution metadata; packaging TOCs | **Unknown in material respects** | Verified build job records, source commit/tree hash, patchset, compiler and SDK versions, options, dependency manifest, source-to-binary attestations and reproducible build comparison |

No component in this matrix qualifies as **Verified upstream binary match**. “Unknown provenance” applies specifically to the exact acquisition route for the wheel contents and VC++ copies; “probable” is an evidence-weighted lead, not a finding of verified release identity.

### 7.3 Compiler, ABI, configuration and modifications

- **Compiler:** PE linker metadata says 14.44. Microsoft’s public mapping associates MSVC 14.44 with VS 2022 v17.14. Exact `cl.exe`/`link.exe` versions and build environment are unavailable; calling this a specific full compiler build would overstate the evidence.
- **Architecture/ABI:** AMD64 PE is directly observed. Wheel metadata says `cp310-abi3-win_amd64`; Python 3.14.10 is the local packaging interpreter. Neither establishes the precise Python headers/ABI used to compile PySide or Shiboken.
- **Qt configuration:** module/plugin versions, build roots, signer and compiler family are observed; configure flags, static-vs-dynamic third-party choices, Qt feature selection, debug information policy and target SDK are not established.
- **PySide/Shiboken configuration:** package version, stable-ABI wheel tag, signer and linker family are observed. Generator version/options, exact Qt headers/libs, libclang version, Python headers, build mode and packaging process are unknown.
- **Release/debug:** no conclusion. The `IMAGE_FILE_DEBUG_STRIPPED` flag means debug information is separated/stripped from the image, while CodeView records retain symbol references. That is compatible with separately retained PDBs and does not prove optimized Release configuration. No debug/release build logs or matching PDBs are present.
- **Patches/local changes:** package files match the local installed tree; this proves no byte difference between those copies only. It does not prove upstream source was unmodified before compilation. No upstream source files, patch list, wheel source-build manifest, or reproducibility run exists in the evidence reviewed.

## 8. Official upstream references and retrieval dates

Retrieved or queried **2026-11-26**. Listed archive hashes are transcribed from official Qt server mirrorlist/index pages and were not locally verified against downloaded files.

### Qt sources and binary-package candidates

- Official Qt 6.12.0 release directory: <https://download.qt.io/official_releases/qt/6.12/6.12.0/>.
- Official online SDK repository, Qt 6.12.0 MSVC2022 64-bit base package: <https://download.qt.io/online/qtsdkrepository/windows_x86/desktop/qt6_6120/qt6_6120_msvc2022_64/qt.qt6.6120.win64_msvc2022_64/>. QtBase candidate archive and published digest detailed in §4.2.
- Official Qt qtsvg MSVC2022 x64 archive mirrorlist: <https://download.qt.io/online/qtsdkrepository/windows_x86/desktop/qt6_6120/qt6_6120_msvc2022_64/qt.qt6.6120.win64_msvc2022_64/6.12.0-0-202609280346qtsvg-Windows-Windows_11_24H2-MSVC2022-Windows-Windows_11_24H2-X86_64.7z.mirrorlist>.
- Official Qt qtimageformats MSVC2022 x64 archive mirrorlist: <https://download.qt.io/online/qtsdkrepository/windows_x86/desktop/qt6_6120/qt6_6120_msvc2022_64/qt.qt6.6120.addons.qtimageformats.win64_msvc2022_64/6.12.0-0-202609280346qtimageformats-Windows-Windows_11_24H2-MSVC2022-Windows-Windows_11_24H2-X86_64.7z.mirrorlist>.
- Qt source tags and releases: [qtbase v6.12.0](https://github.com/qt/qtbase/tree/v6.12.0), [qtsvg v6.12.0](https://code.qt.io/cgit/qt/qtsvg.git/tag/?h=v6.12.0), [Qt Image Formats](https://github.com/qt/qtimageformats); source candidates and published archive digest references are documented in `QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md`.
- Qt 6.12 Windows build and configuration: <https://doc.qt.io/qt-6.12/windows-building.html>, <https://doc.qt.io/qt-6.12/configure-options.html>, and <https://doc.qt.io/qt-6.12/sbom.html>.

### Qt for Python / PySide6 / Shiboken6

- Official PySide6 Essentials 6.12.0 Windows AMD64 wheel mirrorlist and digest: <https://download.qt.io/official_releases/QtForPython/pyside6-essentials/pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl.mirrorlist>.
- Official Shiboken6 6.12.0 Windows AMD64 wheel mirrorlist and digest: <https://download.qt.io/official_releases/QtForPython/shiboken6/shiboken6-6.12.0-cp310-abi3-win_amd64.whl.mirrorlist>.
- Official aggregate PySide6 wheel mirrorlist: <https://download.qt.io/official_releases/QtForPython/pyside6/pyside6-6.12.0-cp310-abi3-win_amd64.whl.mirrorlist>.
- Official Qt for Python 6.12.0 source archive index: <https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/>; PySide source tag: <https://github.com/pyside/pyside-setup/tree/v6.12.0>.
- PySide6/Shiboken Windows build requirements: <https://doc.qt.io/qtforpython-6/building_from_source/windows.html>; general build instructions: <https://doc.qt.io/qtforpython-6/building_from_source/index.html>.
- Distribution metadata pages: <https://pypi.org/project/PySide6/6.12.0/>, <https://pypi.org/project/PySide6-Essentials/6.12.0/>, <https://pypi.org/project/shiboken6/6.12.0/>.

### Toolchain metadata interpretation

- Microsoft MSVC compiler version mapping: <https://learn.microsoft.com/en-us/cpp/overview/compiler-versions?view=msvc-170>.
- Microsoft PE format / COFF characteristics: <https://learn.microsoft.com/en-us/windows/win32/debug/pe-format>.
- Microsoft VC++ runtime/MSVC toolset compatibility information: <https://learn.microsoft.com/en-us/lifecycle/faq/visual-c-faq>.

## 9. Unresolved questions

1. Which precise source delivered the installed `pyside6_essentials` and `shiboken6` distributions: Qt’s official server, PyPI, a proxy/mirror, a local wheelhouse, or another source? What are the original filenames, URLs, archive hashes, and acquisition records?
2. Do the local installed files match the contents and RECORD of the official wheels whose published hashes are listed above? The wheel archives were not downloaded or tested.
3. Did PyInstaller package Qt DLLs/plugins from the PySide6 Essentials wheel, an independently installed Qt SDK, or another local source? The local `Analysis`/`COLLECT` TOCs identify site-packages source paths, but not where those files originated.
4. Are the Qt CodeView GUID/age pairs associated with PDB files from the same official Qt release build? Are those PDBs available from Qt’s debug-symbol archives, and do they verify the exact build IDs/configuration?
5. What exact Qt source commits, generated inputs, patch sets, feature/configuration flags and third-party source revisions produced each Qt module and plugin? Can Qt provide the matching CI job IDs, build attestations and SBOM?
6. Were the modules built from the official Qt installer MSVC2022 x64 build packages, or were they repackaged, relinked, or otherwise altered? Can vendor metadata provide a hash manifest tying each binary to the candidate `.7z` archives?
7. What are the exact compiler and linker versions, Visual Studio edition/update, Windows SDK, CRT mode and linker options? Does 14.44 identify only the linker family or an exact compiler servicing toolset in this build?
8. Which Python headers/interpreter ABI, Qt headers/libraries, Shiboken generator and typesystem inputs, libclang version and build flags produced the PySide6/Shiboken6 extension modules? Was `abi3` built from which Python baseline?
9. Were the files built in Release, Debug, or another mode? The PE debug-stripped flag and PDB references do not answer this.
10. What source modifications, patches, generated-file changes, reproducibility controls and binary post-processing occurred before signing? Did signing occur in the Qt release pipeline, and which signed manifest identifies these files?
11. What is the package-level origin and redistribution basis of the eight Qt-signed VC++ runtime files that lack local RECORD hashes? Do the corresponding wheel files match an official wheel and Microsoft-authorized payload, and what is Qt’s written basis for including them?
12. Does a build SBOM cover all five Qt DLLs, 20 plugins, bundled static third-party code, codecs and VC++ copies in this exact wheel? No package-matched SBOM was located.

## 10. Recommended evidence-collection actions

1. **Preserve acquisition records.** Locate the original wheels, package manager/index configuration, pip logs/cache, requirements/lock data, and any artifact proxy records. Hash the original wheel files without reinstalling. Record the exact URL, filename, repository/index identity, date, TLS/certificate evidence, digest and chain of custody.
2. **Obtain Qt’s source-to-binary package manifest.** Ask Qt for a signed or otherwise authenticated per-file manifest that maps these exact package hashes to the Qt 6.12.0 `qtbase`, `qtsvg`, `qtimageformats`, and other component build IDs, CI jobs, source commits, patches, configure/build flags, compiler/SDK/CRT, dependencies, SBOM and license/notice data.
3. **Compare candidates under controlled authorization.** If authorized to acquire artifacts, download the exact Qt 6.12.0 MSVC2022 x64 installer component archives and official PySide6 Essentials/Shiboken wheels to a separate evidence location, verify their official archive digests, inspect the wheel RECORDs and compare the relevant member hashes to this package. Do not overwrite or replace the preserved package. A comparison that matches a vendor archive would establish archive identity for the matched files, but source/build provenance still requires supplier build records.
4. **Resolve Qt CodeView identifiers.** Obtain the matching PDBs and build provenance from Qt, then validate PDB GUID/age against every Qt DLL/plugin and connect each PDB to source commit, CI job, build options and dependency record. Treat embedded PDB path names alone as clues only.
5. **Request PySide/Shiboken build provenance.** Obtain matching source archive/commit and wheel hashes, Qt binary distribution identity, Python headers/ABI, Shiboken generator/typesystems, libclang version, compiler/SDK, configuration, generated code, patches, packaging logs and the exact per-file manifest. Ask Qt to explain how wheel DLL payloads and vendor signing relate to the public release artifacts.
6. **Resolve compiler/configuration facts.** Obtain authenticated CI logs and tool manifests for full `cl.exe`/`link.exe` versions, Windows SDK, CMake/Ninja, Python and Qt; document Release/Debug flags and PDB retention/stripping. Do not infer these settings from the local PyInstaller venv.
7. **Resolve the VC++ copies separately.** Match all eight nested runtime hashes to official Qt wheel member hashes and Microsoft runtime payload provenance; obtain Qt’s written redistribution basis and the applicable Microsoft terms. Do not infer eligibility from version resources, signer or hash alone.
8. **Create a per-release traceability record.** For each packaged file, record package SHA-256, source wheel/archive and hash, upstream repository path/commit, source patches, compiler/build ID, build job/attestation, signing evidence, dependencies/SBOM, generated source and notices. Preserve it with the final candidate and regenerate it only after an authorized package change.
9. **Keep release decisions separate.** This engineering evidence does not decide license election, notice sufficiency, Microsoft runtime permission, LGPL route, or distribution clearance. Keep the existing `HOLD / NOT CLEARED FOR DISTRIBUTION` disposition until qualified counsel and the release owner assess the exact authorized artifact and distribution model.

## 11. Evidence limitations and change control

This report records binary-level provenance evidence; it does not supersede the broader licensing findings. The matching signer, version resources, PDB paths, installed RECORDs, wheel tags, public archive indexes and same-version source tags are corroborating facts of different strength and must not be collapsed into “verified upstream binary match.” A public digest is only useful for a local identity check after acquiring the corresponding archive and verifying it. A version match is not a build attestation. A valid signature attributes the signed bytes to the signer certificate; it does not provide source lineage or distribution permission. A local RECORD match checks against a local manifest that is not itself a signed supply-chain statement.

The investigation was read-only apart from creating this requested report. No source code, packaging specification, existing report, notice, verified package file, build output, or release artifact was modified intentionally. No source archive, wheel, or replacement binary was downloaded; nothing was installed, rebuilt, committed, or pushed. Existing worktree changes and release artifacts are preserved.
