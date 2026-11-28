# Third-party notice source materials

These materials were prepared from `../ATTRIBUTION-SOURCE-REGISTER.md`, `../OTHER-COMPONENTS-INVENTORY.md`, and `../qt/INVENTORY.md`. They are an evidence collection for review, **not legal advice, a finding of compliance, or a complete release notice set**. The package baseline described in the inventories is the earlier 185-file onedir build; it is not the later trimmed test package.

## How to use this directory

- Files copied from upstream source or vendor pages are preserved as retrieved. See [`MANIFEST.md`](MANIFEST.md) for source URLs, release/version context, retrieval/evidence notes, byte counts, and SHA-256 hashes.
- Some included versions are pinned upstream but are **not proven to be the exact source/build used in the packaged binary**. Do not treat an upstream version match alone as package provenance.
- `freetype/alternatives/` contains the FreeType Project License and GPLv2 texts as mutually exclusive upstream alternatives. Neither has been selected.
- `zstandard/alternatives/` similarly contains the upstream BSD and GPLv2 alternatives. Neither has been selected.
- Qt attribution pages are retained as published HTML in the component folders where useful; they are vendor evidence, not proof that every attribution matches the exact Qt binaries.
- The SQLite page is a public-domain statement, included as courtesy information; it is not a license text.
- A few `.md` files in the alternatives/OpenSSL folders are locally written scope notes, not upstream license or notice text.

## Included materials

Collected source texts and attribution material cover OpenSSL 3.5.9, PyInstaller 6.22.3, CPython 3.14.10, Unicode/UCD 16.0.0, FreeType 2.14.3, bzip2 1.0.8, Zstandard 1.5.7, libpng 1.6.58, libjpeg-turbo 3.2.0, LLVM 3.6.2, HarfBuzz 14.5.0, PCRE2 10.48, C++/WinRT 2.0.250303.1, SQLite, and mpdecimal 4.0.0. Mesa attribution is the Qt 6.12 documentation page; its exact match to the bundled Mesa 11.2.2 DLL is unresolved. PyInstaller's upstream `COPYING.txt` includes its GPL terms, Bootloader Exception, and separate Apache-2.0 statements for runtime hooks/modules.

The existing project-level `licenses/LGPL-3.0.txt` and `licenses/GPL-3.0.txt` were not modified. Qt/PySide license texts and documents remain separate under `../qt/`.

## Not resolved or included as a specific notice

No license election is made for FreeType or Zstandard. No OpenSSL `NOTICE` file is fabricated: the inspected 3.5.9 tag tree contains `ACKNOWLEDGEMENTS.md` and no file named `NOTICE`; Apache-2.0 §4(d)'s NOTICE condition depends on a NOTICE file being included with the Work. The exact OpenSSL release tarball/build provenance remains unverified.

The exact package/source matches or required complete notice sets for zlib-ng, liblzma, libtiff, libwebp, PDFium/Qt PDF and its transitive components, and Microsoft VC++ runtime terms remain unresolved in the cited inventories. They are listed as withheld/unresolved in the manifest rather than guessed. The Qt attribution pages are kept separate from the copied license texts and do not close those evidence gaps.

Before any release use, review the manifest against the final binary/package, resolve the outstanding entries and alternatives, confirm all applicable notices with the corresponding source/build records, and obtain any legal review considered appropriate. No packaging integration or compliance conclusion is implied by this collection.
