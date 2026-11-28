# LogSentinel GUI — Release Licensing Checklist

**Current disposition: HOLD — NOT CLEARED FOR DISTRIBUTION.** This checklist is an internal release-control aid, not an end-user notice, legal advice, or a compliance determination. Do not place this file in a user-facing package as a substitute for license notices.

## Package under review

- Trimmed onedir: `dist/gui-ondir-trim-test/LogSentinel-GUI/`
- 182 files; 80,058,228 bytes.
- `LogSentinel-GUI.exe` SHA-256: `3f5e10bb1511125b4768cb3388b02565a603a3fc21d9dd527f47785fe101be01`.
- Current package has no license/notice documents. This fingerprint is an audit reference, not a release artifact approval.

## Do not release until these are closed

- [ ] **Legal review:** obtain qualified counsel's review of the actual Qt/PySide6 license basis, LGPLv3 obligations and chosen distribution/relinking model, Microsoft VC++ redistribution terms, and intended end-user restrictions/channel.
- [ ] **Qt confirmation:** resolve PySide6/Shiboken wheel metadata versus Qt public licensing language, and obtain written basis for the Microsoft runtime DLLs in the Qt wheels.
- [ ] **Runtime eligibility:** establish permitted provenance and unmodified status for every included VC++ DLL; decide central versus application-local deployment and document servicing ownership.
- [ ] **Component/source map:** match shipped Qt 6.12.0 Windows binaries/plugins and CPython native modules to source revisions, build options/patches, and applicable notices. Resolve FreeType/Zstandard alternatives and zlib/liblzma identity; map libtiff/libwebp and patent materials; address CPython's Microsoft Distributable Code section.
- [ ] **Corresponding source:** identify the exact source and build/configuration material required for each applicable license route; make it available or prepare the reviewed offer/process selected by counsel.
- [ ] **Notice bundle:** prepare license texts, copyright/attribution notices, Qt/PySide user notices, and any source/relink instructions from the resolved component map. Do not copy the current evidence directory wholesale: it contains alternatives, candidates and historical/removed-component materials.
- [ ] **PyInstaller mapping:** verify each embedded loader/runtime file against the exact build inputs; keep GPL/Bootloader Exception terms distinct from Apache-2.0 runtime-hook/module terms; resolve the unmodified-status question.
- [ ] **Final-artifact validation:** add the reviewed materials to the authorized release layout, regenerate file/hash inventory, check that all required text is present and correct, and test replacement/relinking if that is the chosen route.
- [ ] **Compatibility:** complete the documented RDP, GPU-less/software-rendering and high-DPI tests on supported Windows targets; verify ICU/host dependencies and rerun GUI workflows after any release-layout changes.

## Evidence references

- Consolidated findings and open questions: [`FINAL-LICENSING-AUDIT.md`](FINAL-LICENSING-AUDIT.md).
- Package-specific component/notice map: [`TRIMMED-PACKAGE-NOTICE-MAP.md`](TRIMMED-PACKAGE-NOTICE-MAP.md).
- Microsoft DLL evidence: [`MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md`](MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md).
- Runtime provenance evidence: [`RUNTIME-LICENSING-EVIDENCE.md`](RUNTIME-LICENSING-EVIDENCE.md).
- Collected source material and file hashes: [`notices/MANIFEST.md`](notices/MANIFEST.md) and [`notices/README.md`](notices/README.md).

**Release owner sign-off:** do not change this disposition to approved based only on passing functional tests, valid signatures, upstream attribution pages, or the presence of license files in the repository. Approval requires reviewing the exact final package and the terms applicable to its actual distribution.
