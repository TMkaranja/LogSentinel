# VC++ runtime DLL provenance and redistribution evidence — eight packaged files

**Investigation date:** 2026-11-26  
**Scope:** The eight VC++-named files under `_internal/PySide6/` and `_internal/shiboken6/` in the verified trimmed package. Read-only examination of the package, existing cached Qt wheels, local PySide/Shiboken installations, local Visual Studio 2022 redistribution files, prior official Microsoft installer evidence, and public Microsoft/Qt documentation. No installer or DLL was downloaded, extracted, replaced, removed, or executed.  
**Disposition:** **The earlier premise that these eight DLLs were absent from the cached wheels is incorrect. All eight are present in the hash-matched official PySide6 Essentials/Shiboken6 wheel payloads and match their wheel `RECORD` entries. Their exact delivery origin and Qt signing are established; underlying Microsoft source lineage and redistribution eligibility for these Qt-signed copies are not established. Do not treat version, signature, or wheel provenance as legal authorization. Release remains on HOLD.**

## 1. Executive summary

- The exact eight files were derived from the existing trimmed package inventory: five in `_internal/PySide6/` and three in `_internal/shiboken6/`. All report file and product version **14.44.35211.0** and AMD64 PE architecture.
- **Correction to the prior source-archive/build report:** the statement in `QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md` that the eight files were not in the wheels resulted from case-sensitive matching of ZIP entry names. The Windows package paths use names such as `MSVCP140.dll`; the wheel stores the basename as `msvcp140.dll`. Comparing normalized, case-insensitive paths shows that all eight entries are present. No prior report was overwritten or edited as part of this task; this new report records the correction.
- The pre-existing cached wheel bodies have the exact sizes and SHA-256 values published by Qt's official mirrorlists: Essentials `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42`; Shiboken `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e`. Each of the five and three packaged files matches the corresponding wheel payload byte-for-byte and verifies against that wheel's embedded `RECORD` hash and size.
- All eight package DLLs have `Get-AuthenticodeSignature` status **Valid**. The signing subject is **The QT Company Oy** for all eight (certificate thumbprint `3D89F77A33C5AD89F45F681848958E755B727C5A`). The observed timestamp responder certificate is **DigiCert SHA256 RSA4096 Timestamp Responder 2026 1** (thumbprint `51D9ABDA034973D84F4266ACA48248E6B369C439`). This identifies the signer of the packaged bytes; it does not identify their build inputs or confer Microsoft redistribution rights.
- Microsoft documents version 14.44.35211 as the Visual Studio 2022 v17.14 final runtime and publishes redistribution conditions. The installed local VS 2022 `VC\Redist` directory contains Microsoft-signed x64 runtime candidates with the same file/product version and names, but their sizes and SHA-256 hashes differ from the Qt-signed wheel copies. Thus no exact, unmodified Microsoft REDIST-file match was found in the inspected local source. Previously captured Microsoft installer evidence also verified the official installer itself, but its payload DLLs were not extracted or compared.
- Qt for Python release notes say that MSVC runtime libraries are bundled in Windows wheels and were updated in a previous release; the 6.12.0 wheel bytes confirm their inclusion here. Qt's Windows deployment documentation also says compiler runtime DLLs found on a developer machine are not intended/licensed for redistribution and recommends the official Redistributable package. The relationship between this general deployment guidance, the Qt-signed copies in these official wheels, Qt's rights to distribute them, and the rights of downstream redistributors needs **written Qt clarification and qualified legal review**.
- **No conclusion of compliance, authorization, or infringement is made.** The eight files are traceable to the official Qt wheel contents, but Microsoft-source derivation, Qt's redistribution basis, applicable license terms, downstream eligibility, and any consequences of Qt signing remain open.

## 2. Artifact and scope

- Verified package: `dist/gui-ondir-trim-test/LogSentinel-GUI/`
- Package identity at this task's baseline: **182 regular files**, **80,058,228 bytes**.
- Executable: `LogSentinel-GUI.exe`, **2,386,859 bytes**, SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- Scope is the eight DLLs in the two package subdirectories; the two root 14.51.36247.0 DLLs are outside the requested eight-file inventory. They remain separately described by `MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`.
- Read-only methods: enumerate the package DLL paths; calculate SHA-256; read PE machine and version resources; inspect Authenticode signer/timestamp certificates; compare normalized ZIP member names, archive bytes and `RECORD` entries against the cached official wheels; compare with installed site-packages and local Microsoft VS 2022 redistribution files; review previously recorded Microsoft installer evidence and public Microsoft/Qt documentation.

## 3. Exact eight-file inventory and signatures

All eight entries are AMD64 (`IMAGE_FILE_MACHINE_AMD64`, PE machine `0x8664`). For every file below, **file version = product version = 14.44.35211.0**, `OriginalFilename` matches the basename, and Authenticode status is **Valid**.

| Package path | Bytes | SHA-256 | Architecture | Original filename | Authenticode signer / certificate thumbprint |
|---|---:|---|---|---|---|
| `_internal/PySide6/MSVCP140.dll` | 549,176 | `f6f1d55bfd64027820ddce48f9cd8cf46d53bfa34047e6acf4ef348d492a05cb` | AMD64 | `msvcp140.dll` | The QT Company Oy / `3D89F77A33C5AD89F45F681848958E755B727C5A` |
| `_internal/PySide6/MSVCP140_1.dll` | 27,448 | `2be87527c41e1ba8aff48e326e0adcd4743516e0bbcc9304986c726e27de6aca` | AMD64 | `msvcp140_1.dll` | The QT Company Oy / `3D89F77A33C5AD89F45F681848958E755B727C5A` |
| `_internal/PySide6/MSVCP140_2.dll` | 271,672 | `6a72ed8a87eae1671640bd1ca98eccb989f1772ae46ab84594e385bf6d4ac4fb` | AMD64 | `msvcp140_2.dll` | The QT Company Oy / `3D89F77A33C5AD89F45F681848958E755B727C5A` |
| `_internal/PySide6/VCRUNTIME140.dll` | 116,024 | `a36e0cb185eb89533ed96d4568138f86a1315756a8b2644c5963a8ce23e32101` | AMD64 | `vcruntime140.dll` | The QT Company Oy / `3D89F77A33C5AD89F45F681848958E755B727C5A` |
| `_internal/PySide6/VCRUNTIME140_1.dll` | 41,272 | `302b1e160e858602490a55e32ae2e29ddfc0bec2a188e19550cb655cdaa58f9c` | AMD64 | `vcruntime140_1.dll` | The QT Company Oy / `3D89F77A33C5AD89F45F681848958E755B727C5A` |
| `_internal/shiboken6/MSVCP140.dll` | 549,176 | `1ba4d7c0a95d375da138a057a57593b33510ad5bda6c5e2686afd68faa5b4231` | AMD64 | `msvcp140.dll` | The QT Company Oy / `3D89F77A33C5AD89F45F681848958E755B727C5A` |
| `_internal/shiboken6/VCRUNTIME140.dll` | 116,024 | `e7be9112ee9a5b9f44b44bff24cb761cca9b1ed7550b612f77b70edfcf5fdabf` | AMD64 | `vcruntime140.dll` | The QT Company Oy / `3D89F77A33C5AD89F45F681848958E755B727C5A` |
| `_internal/shiboken6/VCRUNTIME140_1.dll` | 41,272 | `f02cd4a862b85a9a3153d27e15e5a213f5df8e3d77004ed2e87b8a7e8873d97c` | AMD64 | `vcruntime140_1.dll` | The QT Company Oy / `3D89F77A33C5AD89F45F681848958E755B727C5A` |

Common signature detail: the signing certificate issuer is `CN=DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1, O="DigiCert, Inc.", C=US`; the timestamp responder subject/thumbprint is `CN=DigiCert SHA256 RSA4096 Timestamp Responder 2026 1` / `51D9ABDA034973D84F4266ACA48248E6B369C439`. This report records Windows Authenticode validation at the time of investigation; it does not independently revalidate the certificate chain at future dates.

## 4. Wheel provenance: correction and verification

### 4.1 Cached archive identity

The pre-existing pip HTTP cache under `C:/Users/DELL/AppData/Local/pip/Cache/http-v2/` contains:

| Wheel | Cached body size | Cached body SHA-256 | Qt-published official SHA-256 |
|---|---:|---|---|
| `pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl` | 82,153,795 | `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42` | `c9a95102aa23c1f86516a30d5a9be37552d324eee7e567eb7508973f1218cb42` |
| `shiboken6-6.12.0-cp310-abi3-win_amd64.whl` | 1,265,476 | `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e` | `a1906cb8116869178c64b6bab52623bbc8b4ceed7b30bfc3c9aa0f6e67f6438e` |

Cache response metadata identifies project, version 6.12.0 and binary-wheel type. These exact archive digests match the values in the Qt official wheel mirrorlists listed in §8. The cached response does not preserve a complete original pip request URL/index configuration or an installation transcript.

### 4.2 Per-file wheel and `RECORD` match

Member names were compared using Windows-style case-insensitive path semantics. Each package file was then byte-compared with its same normalized wheel member; the wheel's embedded `RECORD` hash and size were independently checked against the wheel bytes. All results passed.

| Package path | Wheel member path | Wheel `RECORD` SHA-256 (URL-safe base64) | RECORD size | Package bytes equal wheel member | RECORD validated |
|---|---|---|---:|---|---|
| `_internal/PySide6/MSVCP140.dll` | `PySide6/msvcp140.dll` | `9vHVW_1kAngg3c5I-c2M9G1Tv6NAR-as9O80jUkqBcs` | 549,176 | Yes | Yes |
| `_internal/PySide6/MSVCP140_1.dll` | `PySide6/msvcp140_1.dll` | `K-h1J8QeG6iv9I4ybgrc1HQ1FuC7zJMEmGxybifeaso` | 27,448 | Yes | Yes |
| `_internal/PySide6/MSVCP140_2.dll` | `PySide6/msvcp140_2.dll` | `anLtiofq4WcWQL0cqY7MuYnxdyrkarhFlOOFv21KxPs` | 271,672 | Yes | Yes |
| `_internal/PySide6/VCRUNTIME140.dll` | `PySide6/vcruntime140.dll` | `o24MsYXriVM-2W1FaBOPhqExV1aosmRMWWOoziPjIQE` | 116,024 | Yes | Yes |
| `_internal/PySide6/VCRUNTIME140_1.dll` | `PySide6/vcruntime140_1.dll` | `MCseFg6FhgJJClXjKuLind_AvsKhiOGVUMtlXNqlj5w` | 41,272 | Yes | Yes |
| `_internal/shiboken6/MSVCP140.dll` | `shiboken6/msvcp140.dll` | `G6TXwKldN12hOKBXpXWTszUQrVvabF4mhq_Wj6pbQjE` | 549,176 | Yes | Yes |
| `_internal/shiboken6/VCRUNTIME140.dll` | `shiboken6/vcruntime140.dll` | `576REu6aW59EtEv_JMt2HMqbHtdVC2Evd7cO389f2r8` | 116,024 | Yes | Yes |
| `_internal/shiboken6/VCRUNTIME140_1.dll` | `shiboken6/vcruntime140_1.dll` | `8CzUqGK4WpoxU9J-FeWiE_Xfjj13AE7S6HuKfohz2Xw` | 41,272 | Yes | Yes |

**Correction detail:** The Essentials and Shiboken wheel files and their internal `RECORD` rows use lowercase DLL basenames. Windows package paths have uppercase basenames. The previous investigation used case-sensitive ZIP member lookup and incorrectly counted the eight DLLs as absent. The normalized comparison above establishes the exact members and byte/manifest matches. The prior report remains unchanged per the no-overwrite constraint; this report should be read as the corrected result.

### 4.3 What this establishes about the source

- **Verified:** these exact package bytes are content of the cached wheel archives whose sizes and SHA-256 digests match Qt's published official wheel metadata.
- **Verified:** those wheel entries are listed and hashed in their embedded `RECORD`; the wheel-content hashes and sizes validate.
- **Verified:** all eight DLLs carry valid signatures from The QT Company Oy.
- **Strong attribution:** the files were delivered as part of Qt's signed PySide6 Essentials and Shiboken6 6.12.0 wheel contents. Qt for Python release notes say that MSVC runtime libraries are bundled in Windows wheels, which is consistent with this exact archive evidence.
- **Not established:** whether Qt copied, modified, re-signed, or otherwise derived each binary from a particular Microsoft REDIST payload; whether Qt's upstream rights cover Qt's signing and distribution of these files; and whether the exact Qt-signed wheel files are eligible for downstream redistribution under the applicable Microsoft terms.

## 5. Local installation and Microsoft source comparisons

### 5.1 Installed copies

Each package DLL matches byte-for-byte the corresponding file under the existing `.venv-build-gui/Lib/site-packages/PySide6/` or `.../shiboken6/` tree. The local installed distribution `RECORD` files have matching hash and size rows for every one of the eight DLLs. This confirms package-to-installed-wheel-tree consistency but, by itself, would not prove upstream origin. The new cached wheel archive match in §4 provides the separate archive-level evidence.

The base interpreter's root `C:/Python314/VCRUNTIME140.dll` and `VCRUNTIME140_1.dll` are 14.51.36247.0 files and are not hash matches for these eight 14.44.35211.0 Qt-signed copies. No exact copy of the eight SHA-256 values was found among the checked base Python root, Windows System32, or other local candidate paths beyond the matching PySide/Shiboken installations and package copies.

### 5.2 Existing local Microsoft VS 2022 REDIST candidates

A read-only scan found Microsoft-signed x64 files in the existing VS 2022 Community installation at:

`C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Redist/MSVC/14.44.35112/x64/Microsoft.VC143.CRT/`

All five distinct names there have version/product version **14.44.35211.0**, AMD64 architecture and valid Authenticode signatures from **Microsoft Windows Software Compatibility Publisher**. Their sizes and SHA-256 values differ from the corresponding Qt-signed package files. The same corresponding Microsoft candidate applies to both copies where the filename is duplicated.

| Runtime basename | Microsoft-signed local VS REDIST candidate bytes | Microsoft candidate SHA-256 | Packaged Qt-signed bytes | Packaged path(s) | Exact byte/hash match? |
|---|---:|---|---:|---|---|
| `MSVCP140.dll` | 557,728 | `0f885b509a685d2bbfa652fed26b5fb31d88fbdab0a978c641d1c7b8aa460aa9` | 549,176 | PySide6 and Shiboken6 | No |
| `MSVCP140_1.dll` | 35,952 | `bfad5aef4c63a669e3c140655cdfdf395b6c979b400a447bd5dcb65ed8826c3d` | 27,448 | PySide6 | No |
| `MSVCP140_2.dll` | 280,200 | `3ea06f0ee098b4823cb79599df3780e7f23cce52c19aac31d2a0d47efe33a5e9` | 271,672 | PySide6 | No |
| `VCRUNTIME140.dll` | 124,544 | `d5e4d9a3e835fa679450145d6a7d94e36573a509317111904d9b3712c30d9066` | 116,024 | PySide6 and Shiboken6 | No |
| `VCRUNTIME140_1.dll` | 49,792 | `1f2d41c4aa5db0bc33ebf7b66d72943a817d7ce6cbe880502a9403823633093f` | 41,272 | PySide6 and Shiboken6 | No |

The Microsoft candidate files' identical version resources and official Microsoft signatures establish that the local installation contains Microsoft-signed 14.44.35211.0 x64 REDIST candidates. They are comparison evidence, not proof that the Qt-signed copies were generated from these exact files or that the local VS installation/edition is the acquisition source for Qt's wheel build. Different sizes and hashes rule out byte-for-byte identity with the inspected candidate files.

### 5.3 Previously recorded Microsoft installer evidence

`MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md` records a previously retrieved, Microsoft-signed installer from:

`https://aka.ms/vs/17/release/14.44.35211/VC_redist.x64.exe`

The prior report gives installer size 25,635,768 bytes and SHA-256 `CC0FF0EB1DC3F5188AE6300FAEF32BF5BEEBA4BDD6E8E445A9184072096B713B`, with file/product version 14.44.35211.0 and a valid Microsoft signature. It states that installer was inspected but not executed and its embedded DLLs were not extracted or compared. No installer was downloaded during this task. Therefore the prior installer identity supports an official release path for that runtime version but supplies no direct file-hash match for these eight packaged DLLs.

### 5.4 Provenance classification by candidate source

| Candidate origin | Finding for these eight files |
|---|---|
| Microsoft Visual C++ runtime family | **Version/family attribution established:** file resources say 14.44.35211.0; Microsoft identifies this as VS 2022 v17.14 final runtime; same-version Microsoft-signed REDIST files and a versioned Microsoft installer are documented. **Exact Microsoft binary origin not established:** inspected local Microsoft candidate DLLs differ in bytes, and installer payload comparison was not performed. |
| Qt-signed distribution | **Established:** all eight package bytes are Authenticode-valid under The QT Company Oy; all eight exact bytes are in the official-digest-matched Qt wheels. The evidence supports Qt distribution/signing of these copies. It does not show Qt created the underlying implementation or establish Qt's rights to redistribute it. |
| PySide6/Shiboken wheel | **Established:** five exact files are in the matching Essentials wheel and three in the matching Shiboken wheel; per-file payload, size, and `RECORD` hash all match. |
| Python installation | **Partial/local only:** wheel files also reside in the local Python environment's site-packages. The Python base interpreter's root runtime DLLs are the separate 14.51 copies and do not match these eight files. The exact origin of the site-packages entries is traced to the wheel archives above, not to CPython's root runtime distribution. |
| Another identifiable source | **Not identified.** The inspected Visual Studio candidate is same version/name but not an exact binary match. No other exact external source candidate was verified. |

## 6. Digital-signature interpretation

- `Get-AuthenticodeSignature` returned **Valid** for every packaged DLL.
- All eight have the same QT Company signer subject and thumbprint. The timestamp responder certificate is the same DigiCert 2026 responder certificate across the set.
- The corresponding local Microsoft REDIST candidates are separately signed by Microsoft Windows Software Compatibility Publisher and are not byte-identical to the Qt-signed copies.
- A valid signature supports integrity relative to the signer's signed bytes and identifies the signing certificate. It is not a Microsoft license grant, proof of Microsoft's approval of Qt's signing, proof the file is on a Microsoft distributable list, or proof that Qt or LogSentinel has downstream redistribution authorization.
- The Qt certificates do not establish whether Qt re-signed Microsoft-provided binaries under a supplier agreement, used a permitted packaging workflow, or built a compatible runtime. These questions require supplier records, written Qt confirmation, and legal review.

## 7. Applicable Microsoft documentation and terms

Microsoft's official pages make distribution conditional. The relevant statements are not a blanket authorization for any same-version file from any supplier.

1. **Redistribute Visual C++ Files** — <https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files?view=msvc-170>. Microsoft says redistribution of the Visual C++ Redistributable package, merge modules and individual binaries is limited to licensed Visual Studio users and subject to Microsoft Software License Terms. It directs users to the applicable REDIST list and license terms.
2. **Visual Studio 2022 Redistribution / Distributable Code Files** — <https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution>. For a validly licensed VS 2022 copy, the listed Distributable Code may be copied with a program in unmodified form, subject to the relevant license terms. The page identifies the VS 2022 REDIST list and VC143 runtime files. This is the relevant Visual Studio generation candidate for version 14.44; application-specific entitlement and all conditions still require review.
3. **Visual Studio 2026 Redistribution** — <https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution>. It sets out VS 2026-and-later REDIST conditions (including unmodified files), but its VC145 list is not the source identity of the examined 14.44 VC143 files. Do not use it to infer the provenance or license election for these files.
4. **Microsoft Visual Studio license/EULA directory** — <https://visualstudio.microsoft.com/license-terms/>. The directory lists the VS 2022 Community and VS 2022 Enterprise/Professional terms and the separate “Microsoft Visual C++ Runtime 2015-2022 Software” terms. It also lists VS 2026 license products. The appropriate edition and terms must be determined for the actual distributor. The applicable full EULA and eligibility records were not established by this investigation.
5. **Troubleshoot VC Redistributable installation issues** — <https://learn.microsoft.com/en-us/cpp/windows/troubleshoot-vc-redistributable-installation-issues?view=msvc-170>. Microsoft documents versioned installer URL patterns: VS 17 for versions 14.30–14.44 and VS 18 for 14.50 or later, and warns to use Microsoft-signed installers. This supports the historical 14.44 installer candidate, not file-by-file identity of the Qt-signed DLLs.
6. **Visual C++ lifecycle FAQ** — <https://learn.microsoft.com/en-us/lifecycle/faq/visual-c-faq>. The version table identifies V143/14.44.35211 with VS 2022 v17.14 final and gives its lifecycle. Runtime version metadata does not itself prove package source or redistribution rights.
7. **Latest supported VCRedist** — <https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist>. Microsoft documents v14 runtime compatibility/current installer guidance and repeats the licensed-user restriction. It is useful when choosing a future centrally serviced runtime strategy, but does not bless the present Qt-signed copies.
8. **Determine which DLLs to redistribute** — <https://learn.microsoft.com/en-us/cpp/windows/determining-which-dlls-to-redistribute?view=msvc-170>. Microsoft explains how to map DLL dependencies to the applicable REDIST list; the filename alone is not the complete analysis.
9. **Deployment in Microsoft C++** — <https://learn.microsoft.com/en-us/cpp/windows/deployment-in-visual-cpp?view=msvc-170>. Microsoft describes central and app-local deployment, notes that dot libraries such as `msvcp140_1.dll` may be required, and recommends a servicing strategy because app-local DLLs are not automatically updated.

The Microsoft Learn summaries and REDIST lists refer the user to the exact Software License Terms. This investigation did not establish a complete applicable EULA for the distributor's exact Visual Studio edition, license program, and distribution route. A legal decision must examine that text, including all conditions on qualifying application functionality, downstream terms and notices, and restrictions on permitted recipients or purposes where applicable. This report does not interpret the contract or conclude that any condition is met.

## 8. Qt documentation and the open supplier question

- **Qt for Python release notes:** <https://doc.qt.io/qtforpython-6/release_notes/pyside6_release_notes.html>. Release-note entries include updates/fixes concerning MSVC runtime libraries bundled in Windows wheels (including the 6.9.2 runtime update and 6.8.2 bundling fix). This supports the practice of shipping runtime DLLs inside wheels; it does not disclose source hashes, signing/repackaging methods, or a Microsoft redistribution grant for this 6.12.0 payload.
- **Qt for Python Windows build instructions:** <https://doc.qt.io/qtforpython-6/building_from_source/windows.html>. The documentation lists MSVC 2022 for Python 3 on Windows and Qt/Python/PySide compiler compatibility; it does not establish the exact compiler/runtime DLL package used for this wheel build.
- **Qt for Windows deployment (Qt 6.12):** <https://doc.qt.io/qt-6.12/windows-deployment.html>. The documented guidance says that if `windeployqt` cannot find the official Redistributable, it may fall back to developer-machine shared runtime DLLs; it describes those individual DLLs as not intended/licensed for redistribution and recommends the official Microsoft Redistributable package. It is general deployment guidance, not a written statement about the exact Qt-signed DLLs shipped in the PySide6/Shiboken6 wheels. Because the wheel evidence shows those DLLs are included, request Qt's explanation of how its official wheel distribution is reconciled with that guidance and Microsoft's terms.
- **Qt for Python development notes:** <https://wiki.qt.io/Qt_for_Python_Development_Notes_2022> mentions historical CI sourcing of bundled MSVC DLLs and a wheel packaging fix. It is background only; it is not a provenance record for these exact 6.12.0 wheel entries.

## 9. Redistribution eligibility assessment

**Current status: NOT ESTABLISHED for the exact Qt-signed files.** The evidence chain supports the presence of Microsoft v14 runtime code by file names and version data, and the local VS 2022 REDIST candidates have matching version resources. But the exact file hashes differ; none of the eight is a byte-identical match to the inspected Microsoft-signed x64 candidate. The packaged signatures identify Qt, not Microsoft. The prior versioned Microsoft installer was not extracted for a payload comparison. The bundled Qt wheel evidence does not itself convey Microsoft runtime redistribution rights to this project.

Questions that prevent an eligibility conclusion include:

- What exact Microsoft REDIST file/build did Qt use for each wheel DLL? Were these copied, modified, re-signed, or produced by another process? Does Qt have supplier rights to distribute them as wheel contents?
- How does Qt interpret its Windows deployment warning about individual DLLs, given that it distributes them in the official Windows wheels?
- Do the applicable Visual Studio 2022/Visual C++ Runtime Software terms authorize downstream distribution of these exact Qt-signed, non-byte-identical files? Does the relevant license require distribution in unmodified form, and how does Qt signing or any other byte differences affect that condition?
- What Visual Studio license/edition or other authorization basis does the distributor hold? Which conditions attach to the intended redistribution model, recipients, installer, EULA, or end-user terms?
- Is the selected deployment model centrally serviced or application-local, and who maintains security updates? The observed package includes duplicate local copies; a prior load snapshot covered only one execution/workflow and cannot establish that some copies are unnecessary.

This assessment is not a claim that Qt's wheel distribution is unauthorized or that LogSentinel's distribution would necessarily violate terms. It is a record that file origin and authority are distinct: the official Qt wheel link is strong evidence of delivery provenance, but the license chain from Microsoft to Qt and then to LogSentinel remains unverified.

## 10. Per-file practical action matrix

The common action for all eight is to retain their hashes and wheel-entry proof, request Qt's exact package-level provenance and redistribution basis, and obtain qualified review of the relevant Microsoft terms. Do not modify files during this evidence phase.

| Package file(s) | Strongest verified source link | Exact Microsoft-source status | Practical resolution |
|---|---|---|---|
| `_internal/PySide6/MSVCP140.dll` | Exact entry in digest-matched Essentials wheel; Qt Authenticode signature; matching local wheel `RECORD`. | Same-version Microsoft VS REDIST filename exists locally, but candidate SHA-256/size differ. | Request Qt's file/build manifest and origin of the wheel's `msvcp140.dll`; compare against Qt's cited original Microsoft payload with hashes and signed provenance. Do not infer that a general 14.44 version match is enough. |
| `_internal/PySide6/MSVCP140_1.dll` | Exact entry in Essentials wheel and `RECORD`; Qt signature. | Local Microsoft same-version candidate differs in size/hash. | Request the same file-level source and signing/redistribution record; legal review whether Qt-signed form is covered by applicable unmodified-file terms. |
| `_internal/PySide6/MSVCP140_2.dll` | Exact entry in Essentials wheel and `RECORD`; Qt signature. | Local Microsoft same-version candidate differs in size/hash. | Request file-specific source, transformations and licensing basis; confirm whether this dot-library is needed under the selected deployment strategy. Do not remove based on one load snapshot. |
| `_internal/PySide6/VCRUNTIME140.dll` | Exact entry in Essentials wheel and `RECORD`; Qt signature. | Local Microsoft same-version candidate differs in size/hash; separate from root CPython 14.51 file. | Request Qt provenance/redistribution confirmation; legal review of this exact local copy. Consider centrally installed official VCRedist only as a separately designed and tested release change. |
| `_internal/PySide6/VCRUNTIME140_1.dll` | Exact entry in Essentials wheel and `RECORD`; Qt signature. | Local Microsoft same-version candidate differs in size/hash. | Request same file-level proof and rights; retain until a separately authorized technical change validates loader behavior and every supported workflow. |
| `_internal/shiboken6/MSVCP140.dll` | Exact entry in digest-matched Shiboken wheel and `RECORD`; Qt signature. | Local Microsoft same-version candidate differs in size/hash; also differs from PySide6 copy despite same basename/version. | Request separate mapping for Shiboken wheel build, source and Qt signing; review copy eligibility individually, not by analogy to the PySide copy. |
| `_internal/shiboken6/VCRUNTIME140.dll` | Exact entry in Shiboken wheel and `RECORD`; Qt signature. | Local Microsoft same-version candidate differs in size/hash. | Request separate per-file Shiboken build and distribution basis; do not equate version/signer with Microsoft's unmodified REDIST file. |
| `_internal/shiboken6/VCRUNTIME140_1.dll` | Exact entry in Shiboken wheel and `RECORD`; Qt signature. | Local Microsoft same-version candidate differs in size/hash; distinct hash from the PySide6 file. | Request separate file mapping and redistribution basis; preserve until a reviewed central/local strategy is tested. |

### Recommended release path

1. Keep the current files and verified package unchanged while evidence is gathered.
2. Ask Qt for a written response for both exact wheel hashes and all eight path/hash values: source of each Microsoft runtime DLL; exact Microsoft package/file hashes; whether any binary was modified/re-signed and how; Microsoft's authorization/terms basis; and how this packaging is reconciled with Qt's Windows deployment documentation.
3. Obtain the distributor's applicable VS 2022/VC++ Runtime Software license terms and have qualified counsel review exact eligibility, app-local delivery, end-user terms and all conditions. Do not rely solely on a Microsoft Q&A interpretation, signing certificate, matching product version, or Qt wheel `RECORD`.
4. Evaluate central installation of the official Microsoft Redistributable as a future option if product deployment supports an installer prerequisite and the license review approves it. Any change would require explicit authorization, a separate package/rebuild decision, fresh DLL-load tracing on clean targets, servicing plan and regression tests. Merely installing the redistributable does not prove bundled copies are harmless or unselected.
5. If Qt and counsel establish an eligible basis for the wheel files, retain the applicable provenance/permission documentation and version-pinned notice/terms with the release record. Keep a runtime servicing and security-update owner.

## 11. Unresolved evidence

- Qt's written sourcing, re-signing/transformations, supplier permission and downstream redistribution explanation for the exact eight DLL hashes.
- Microsoft-origin file-level mapping: exact 14.44 source payload hashes, signing treatment and a comparison to the wheel DLLs. The local VS REDIST candidates and earlier official installer evidence are version-level, not exact binary matches.
- Complete applicable Visual Studio/Visual C++ Runtime license terms and evidence of the distributor's relevant license/eligibility basis; no legal interpretation has been made.
- Whether all conditions and downstream recipient terms can be satisfied for the intended portable onedir distribution.
- Exact dependency/load behavior for each duplicate copy over all GUI paths and clean Windows targets; the prior isolated run is evidence only for one captured run.
- An approved update/servicing strategy if any application-local runtime copies remain.

## 12. References and evidence records

### Local project evidence

- `licenses/third-party/QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md` — official wheel digests and prior case-sensitive “absent from wheel” assertion. This report corrects that assertion; it was not modified.
- `licenses/third-party/QT-PYSIDE-BINARY-PROVENANCE-REPORT.md` — native file/version/signature inventory and Qt signing evidence.
- `licenses/third-party/QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md` — local package/site-packages comparison and Qt/PySide source mapping gaps.
- `licenses/third-party/MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md` — ten-file inventory, previously inspected Microsoft installers, local runtime copies and legal/servicing questions.
- `licenses/third-party/RUNTIME-LICENSING-EVIDENCE.md` — trimmed package and VC++ runtime/CPython licensing evidence.
- `licenses/third-party/FINAL-LICENSING-AUDIT.md` — overall release HOLD and unresolved runtime eligibility.
- Existing exact cache bodies and metadata are under `C:/Users/DELL/AppData/Local/pip/Cache/http-v2/`; no copy was made in this task.
- Existing local VS candidate directory: `C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Redist/MSVC/14.44.35112/x64/Microsoft.VC143.CRT/`; files were read/hash-checked but not changed.

### Official Qt references

- Essentials wheel and published SHA-256: <https://download.qt.io/official_releases/QtForPython/pyside6-essentials/pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl.mirrorlist>.
- Shiboken wheel and published SHA-256: <https://download.qt.io/official_releases/QtForPython/shiboken6/shiboken6-6.12.0-cp310-abi3-win_amd64.whl.mirrorlist>.
- Qt for Python release notes: <https://doc.qt.io/qtforpython-6/release_notes/pyside6_release_notes.html>.
- Qt for Python Windows build information: <https://doc.qt.io/qtforpython-6/building_from_source/windows.html>.
- Qt 6.12 Windows deployment: <https://doc.qt.io/qt-6.12/windows-deployment.html>.
- Qt for Python development notes: <https://wiki.qt.io/Qt_for_Python_Development_Notes_2022>.

### Official Microsoft references

- VC++ redistribution overview: <https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files?view=msvc-170>.
- Visual Studio 2022 REDIST list: <https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution>.
- Visual Studio 2026 REDIST list: <https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution>.
- Visual Studio license directory: <https://visualstudio.microsoft.com/license-terms/>.
- Versioned installer troubleshooting/download guidance: <https://learn.microsoft.com/en-us/cpp/windows/troubleshoot-vc-redistributable-installation-issues?view=msvc-170>.
- Visual C++ runtime lifecycle/version FAQ: <https://learn.microsoft.com/en-us/lifecycle/faq/visual-c-faq>.
- Latest supported VCRedist: <https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist>.
- Which DLLs to redistribute: <https://learn.microsoft.com/en-us/cpp/windows/determining-which-dlls-to-redistribute?view=msvc-170>.
- Central/local deployment and servicing: <https://learn.microsoft.com/en-us/cpp/windows/deployment-in-visual-cpp?view=msvc-170>.

## 13. Final disposition and verification

**Provenance:** all eight package DLLs are byte-identical to entries in the official-digest-matched PySide6 Essentials/Shiboken6 wheel archives and match the wheel `RECORD` values. All are validly signed by The QT Company Oy. Their Microsoft runtime version family is strongly supported by version metadata and official Microsoft documentation.

**Microsoft source and redistribution eligibility:** **not established** for the exact Qt-signed wheel files. The local Microsoft-signed same-version REDIST candidates are not byte-identical, and the prior Microsoft installer payload was not extracted/compared. Qt's exact source/rights basis and the distributor's applicable Microsoft license conditions require evidence and review.

**Release disposition:** **HOLD / NOT CLEARED FOR DISTRIBUTION.** This report is not legal advice, does not conclude that redistribution is permitted or prohibited, and does not authorize modifying or replacing the DLLs.

Verification after report creation must confirm: (a) the new report's byte size and SHA-256; (b) trimmed package remains 182 files / 80,058,228 bytes with EXE SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`; (c) each of the eight DLL SHA-256 values above is unchanged; (d) all six existing release-baseline artifacts still match `C:/Users/DELL/AppData/Local/Temp/logsentinel-final-audit-release-before.txt`; and (e) the new report is the only new worktree entry, with all pre-existing worktree entries preserved. No package/spec/source/report other than this new file was intentionally changed. No download, extraction, rebuild, commit or push was performed.
