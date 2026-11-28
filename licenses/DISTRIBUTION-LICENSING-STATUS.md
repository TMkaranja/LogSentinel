# LogSentinel Distribution Licensing Status — Proposal

**Status: NOT CLEARED FOR DISTRIBUTION**

> This is a proposed release-control record for the inspected Phase 1 Windows onedir candidate. It is not legal advice, a compliance determination, redistribution authorization, or an offer of source. No project or third-party license text, wheel metadata, version, signature, hash, or test result alone proves that the candidate may be distributed.

## 1. Artifact and project-license scope

The engineering evidence concerns `dist/gui-ondir-trim-test/LogSentinel-GUI/`: **182 files / 80,058,228 bytes**. The root `LogSentinel-GUI.exe` is 2,386,859 bytes, SHA-256 `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`. This is a test candidate, not a finalized recipient package. It contains no `.txt`, `.md`, or `.rst` license or notice document.

The repository's root `LICENSE` declares **MIT** for LogSentinel itself, with copyright attributed to Moses Karanja Thuo (2026). `pyproject.toml` does not declare a license field. The project's MIT license does not replace or grant rights to the bundled Qt/PySide/Shiboken, CPython, native libraries, PyInstaller payload, Qt-linked components, translations, or Microsoft runtime DLLs. The separate root `licenses/LGPL-3.0.txt` and `licenses/GPL-3.0.txt` are full text materials in the repository; their presence there does not mean they are present in the inspected package or establish which license option applies to any binary.

## 2. Current disposition

**HOLD — NOT CLEARED FOR DISTRIBUTION.** Do not release, publish, provide, or treat this candidate as approved for recipient use on the basis of this status proposal. The package's rights, notice/source set and distribution conditions have not been fully established. No finding is made that a license was breached or that a legal obligation has been triggered; those questions depend on actual grants, conveyance facts, recipient terms and qualified legal review.

This disposition applies to the described candidate and does not determine rights to use the source repository under its own license. It is not an authorization to modify the source, package or build specification.

## 3. Summary of unresolved release requirements

### Qt, PySide6, Shiboken6, plugins and translations

- No binary-specific license election or commercial entitlement is established for Qt 6.12.0, PySide6/Shiboken6 6.12.0, their plugins, or the included code.
- PySide wheel metadata states `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`, while Qt for Python public wording describes Community Edition as LGPLv3/GPLv3. The GPLv2 difference remains unresolved; do not assert either interpretation as settled.
- Source/build provenance, matched SBOM, per-file license/copyright map, and complete component notices are not established. The 99 `.qm` catalogs require an individual source/contributor/license map; they must not automatically be characterized as LGPL library files.
- If an LGPLv3 route applies to a conveyed combined work, the applicable prominent notice, license texts and any runtime notice requirements must be reviewed. Neither §4(d)(0) source/relinking nor §4(d)(1) suitable shared-library mechanism is demonstrated for this exact package. The onedir layout is not proof of replaceability. No exact-package, recipient-controlled modified-library replacement test or corresponding-source/relink package exists in the reviewed evidence.
- Any §4(e) Installation Information question is conditional on the actual conveyance/product facts and requires counsel's determination. Installer/EULA, update/signing and anti-tamper restrictions are not defined for a release.
- Existing technical probe evidence from another package/layout does not establish replacement for this candidate. No written offer or recipient instructions have been validated or prepared.

### Third-party component notice/source mapping

- The internal `licenses/third-party/notices/` collection is evidence material, not an end-user release bundle. Its 34 manifest-listed files match their expected hashes; the manifest has no self-hash row. It contains alternatives, candidates, local notes and historical component material and should not be copied wholesale.
- FreeType's FTL/GPLv2 alternative is not elected. Zstandard's BSD/GPLv2 alternative is not elected. Exact zlib-compatible and liblzma/XZ source/license mappings, Qt codec/source mappings, libtiff and libwebp notices (and potential patent material), and Qt translation mapping remain incomplete.
- HarfBuzz, libpng, PCRE2/possible SLJIT, libjpeg-turbo, C++/WinRT, bzip2, Unicode, mpdecimal, SQLite and OpenSSL have candidate notice materials with varying source-match limitations; each must be matched to the exact shipped source/build and reviewed before a recipient notice is finalized.
- OpenSSL's Apache-2.0 text and acknowledgements are collected. `ACKNOWLEDGEMENTS.md` is not renamed or treated as a `NOTICE`; the inspected 3.5.9 tag/archive evidence did not show a file named `NOTICE`. Actual binary/build provenance still requires confirmation.
- PyInstaller 6.22.3's combined `COPYING.txt` distinguishes GPL/Bootloader Exception from Apache-licensed runtime hooks/modules. Payload-to-source mapping and bootloader modification status remain open; do not claim an unmodified bootloader. The correct full license texts and any source duties require review.
- CPython's exact Windows build materials and the separate “Microsoft Distributable Code” section in the local interpreter license require review for scope and downstream conditions.
- Qt PDF/qpdf and Mesa software OpenGL payloads are absent from this trimmed candidate; their historical notices are not listed as shipped components here. Reassess if package scope changes.

### Microsoft runtime rights and provenance

Ten VC++ runtime DLL copies remain in the candidate. Eight nested 14.44.35211.0 DLLs are contained in digest-matched Qt wheels, match wheel `RECORD` entries and carry Qt Company signatures. These facts establish wheel delivery and signer, not Microsoft source identity, Qt's underlying redistribution rights, or downstream eligibility. Two root 14.51.36247.0 DLLs are a separate set. Applicable Microsoft terms, exact provenance and eligibility remain unresolved for all ten. No Qt written rights basis or counsel approval is documented.

### Release model, notices and approval

- Intended recipients, territories, channel, portable/installer format, user terms, update mechanism and signing/anti-tamper controls have not been specified or reviewed.
- There is no counsel-reviewed notice/license/source package, validated corresponding-source offer, recipient replacement/relink guide, or release-owner approval tied to final hashes.
- Broad Windows compatibility and host dependencies have not been validated across a declared support matrix. A functionality test is not licensing clearance.

## 4. Corresponding source, DLL replacement, instructions and written offers

The evidence establishes Qt wheel-to-package content identity for PySide6/Shiboken trees and for the eight nested runtime DLLs. It does **not** establish corresponding source: exact Qt/PySide/Shiboken revisions, patches, generated inputs, source-to-binary maps, build configuration/toolchain, and package-matched SBOM remain outstanding. Public same-version source archives are only candidates until matched to the actual binaries and relevant build materials.

The separately stored Qt DLLs in the onedir layout are an engineering observation only. No exact-candidate test shows that a recipient can supply and cause the program to load a coherent, interface-compatible modified Qt library set while the application and relevant plugins/bindings operate properly. Nor has a §4(d)(0) source/relink bundle been assembled. Prior tests on another layout/package do not close either gap.

No recipient-facing instructions or written offer have been prepared or verified. A source-access method, offer term, source set or replacement procedure must not be invented here. If a particular license/conveyance requires one, qualified counsel must determine its form and duration; the release team must match the materials to exact shipped versions and test the recipient workflow before any distribution decision.

## 5. Proposed release-directory structure (not created or populated)

The following is a planning sketch for a **future, separately authorized** release. It is not a statement that any listed folder is complete, that all contents are legally required, or that the current package is approved. Use only counsel-reviewed, artifact-matched materials; omit a source or notice item only after its applicability has been reviewed.

```text
LogSentinel-<version>-Windows-x64/
├── LogSentinel-GUI/
│   ├── LogSentinel-GUI.exe
│   └── _internal/                         # Complete final onedir payload
├── LICENSE                               # Reviewed LogSentinel project license
├── THIRD-PARTY-NOTICES.md                 # Final, curated, package-matched notices
├── licenses/
│   ├── GPL-<applicable-version>.txt       # Include only if applicable/required
│   ├── LGPL-<applicable-version>.txt      # Include only if applicable/required
│   └── third-party/                       # Exact, reviewed applicable texts only
├── source/                                # Only if selected route requires/provides it
│   ├── README-SOURCE-AND-OFFERS.txt       # Counsel-reviewed scope, method and duration
│   ├── corresponding-source/              # Exact source/revisions and required patches
│   ├── build-materials/                   # Required scripts/configuration/materials
│   └── application-code/                  # If required for a source/relink route
├── instructions/
│   ├── REPLACEMENT-OR-RELINKING.txt        # Only the validated, applicable procedure
│   └── INSTALLATION-INFORMATION.txt        # Only if counsel determines it is triggered
└── SHA256SUMS.txt                          # Generated for the authorized final tree
```

The current project/repository evidence files, candidate/alternative notice corpus, audit reports, and historical release archives are not a curated distribution payload. This proposal does not create the directory, copy files into it, or recommend that all shown folders be included.

## 6. Release exit criteria

Keep the HOLD until all applicable items below have evidence tied to the exact final artifact and channel:

1. Define recipient, territory, distribution channel, terms, installation format, updates/signing/anti-tamper controls and the exact artifact hashes.
2. Obtain Qt's written, component-specific licensing, source/build/SBOM and translation/notice scope, including resolution of the PySide GPLv2 metadata discrepancy and the eight nested Microsoft runtime DLL rights basis.
3. Establish exact source, build and license/notice mappings for Qt/PySide/Shiboken, CPython, PyInstaller and all embedded components; resolve elections and missing notices.
4. Obtain qualified legal review of applicable grants, conditional LGPL/GPL duties, source/replacement route, Microsoft terms, and the proposed recipient materials.
5. If applicable, select and validate the exact LGPL §4(d) route. For replacement, test a recipient-controlled copy and confirm the modified compatible library set is loaded and works. For source/relinking, assemble and test matching corresponding source, application code, build materials and instructions. Determine §4(e) only from actual facts.
6. Curate final recipient notices, applicable license texts and source/offer/replacement materials; verify all delivered files against a manifest. Do not use internal audit reports or speculative candidates as substitutes.
7. Validate the declared Windows support matrix and documented workflows on the authorized candidate.
8. Have the release owner and qualified counsel approve the final artifact and channel in writing. Recompute the final hashes after all approved materials are assembled.

**Until all applicable gates are closed: NOT CLEARED FOR DISTRIBUTION.**
