# LogSentinel Phase 1 — Lucide Asset Correction Report

**Status:** the four isolated Lucide SVG proposals are corrected and validated; they remain **not integrated**. No original GUI asset, application source, test, packaging spec, existing report, attribution file, or license file was modified. This report is the authoritative corrected filename/hash/validation addendum to `docs/PHASE-1-LUCIDE-ASSET-REPLACEMENT-REPORT.md`; that earlier report and the attribution record were preserved unchanged, as required by the scope limit. The Windows GUI executable and ZIP remain **HOLD — NOT CLEARED FOR DISTRIBUTION**.

## Corrections and hashes

The existing GUI loader in `src/logsentinel/gui/icons.py` replaces the literal `CURRENT_COLOR` token with the requested theme color. Each staged Lucide SVG’s `stroke="currentColor"` was changed to `stroke="CURRENT_COLOR"`—the only byte-content edit. The folder proposal was renamed from `folder-open.svg` to the live target basename `folder_open.svg`; its SVG content changed only for the same color-token correction. All paths, attributes other than the stroke token, stroke width, viewBox, and SVG geometry were retained.

| Lucide icon | Exact target-relative proposal filename | Pinned source commit | Corrected bytes | Corrected SHA-256 | Original source-byte SHA-256 (before token substitution) |
|---|---|---|---:|---|---|
| `check` | `check.svg` | `66cfe527b3d19ce03cdf3de704dfbd80d796ec0f` | 240 | `ce862ced28c4f3163e6258b83a8a7231166149242e094a460449fbd5230c48cc` | `7f33acc9a77a61659531044525fc008edebe215bf4dcf1c789c8674ad3277db0` |
| `download` | `download.svg` | `09841dd72126a65b39f7c6ebd38dc3664299d756` | 319 | `6f70003d0f4ade05e8bb586a4d89a551058d5682b3141e9452d2ef593713442e` | `3daeee13ded5a3afa2198b1bb4e2262d163922f97d96ac6ff9953e8ed4fe039d` |
| `folder-open` | `folder_open.svg` | `81e44bdc40d21d64881a858c188f391bca75eb0f` | 402 | `b6d39a234cab41b365fc696f3fff3f38525cef6120d952e5651762e64119b09c` | `ee57452b40e71df310214091dd9da1941a397c83197b8ff8d7ae66dd4242578b` |
| `x` | `x.svg` | `70be55b78f9043bd8c37200164370a8e8d02d38b` | 261 | `eebd33f4843cc6a8bccfee89ff350cfcaeca9fbbe5076823742c32896e54b49a` | `4a9cdab38fbb96162e7dace28e33f4ca0e49d8963a6162abc3d4691b7d675117` |

All corrected proposals are under `licenses/third-party/asset-remediation/proposed-lucide-replacements/`. `folder_open.svg` now matches the existing target name `src/logsentinel/gui/assets/icons/folder_open.svg`; the obsolete staged basename `folder-open.svg` is absent. The existing `ATTRIBUTION.md` still records the source icon name and intended target, but its proposal-filename line reflects the earlier hyphenated name; this report supersedes that path record without editing the attribution file, consistent with the strict allowed-file list. Keep that stale filename reference in mind if a later task authorizes updating the attribution record.

## Geometry and pinned-source verification

For each file, I parsed both the corrected SVG and its pre-correction/source-equivalent bytes. The restored-byte check replaces only `CURRENT_COLOR` with the prior raw `currentColor` token and then confirms both the pre-correction SHA-256 and Git blob SHA-1 reported for the pinned upstream file. Results:

| Proposal | Restored source SHA-256 match | Restored Git blob SHA-1 match | Path `d` multiset matches mapped original | ViewBox |
|---|---|---|---|---|
| `check.svg` | PASS | PASS (`5abe1527434e7b251bde0661f99af96178976d8c`) | PASS (1 path) | `0 0 24 24` |
| `download.svg` | PASS | PASS (`5c75527bde1fe8259efb72c5b590bedfae28c05e`) | PASS (3 paths; element order retained from pinned source) | `0 0 24 24` |
| `folder_open.svg` | PASS | PASS (`b01f60fcb51848a9b3a7380d4566c4de7534745c`) | PASS (1 path) | `0 0 24 24` |
| `x.svg` | PASS | PASS (`e31794349d3eecea1b3ae8e974b68bb8f4becda7`) | PASS (2 paths) | `0 0 24 24` |

Thus the color-token correction leaves the source SVG’s original geometry unchanged. Renaming `folder-open.svg` to `folder_open.svg` changes no bytes. This validates correspondence to the pinned-byte claims already recorded in the prior replacement report; it is not a fresh upstream download or a claim about the historical origin of the original LogSentinel artwork.

## Actual GUI-loader color-render checks

A headless PySide6 check imported `logsentinel.gui.icons`, supplied each proposal through the loader’s `_read_asset` seam, and called the actual `icons.icon_svg(name, color)` transformation. For each SVG, the check verified that `CURRENT_COLOR` was replaced with the requested `stroke` value, parsed the transformed document with Qt `QSvgRenderer`, rendered it into a transparent image, and examined opaque pixels. Two colors were tested per file:

- `#8ca1c1` → dominant opaque rendered RGB `(140, 161, 193)`
- `#ef4444` → dominant opaque rendered RGB `(239, 68, 68)`

All eight loader/color renders were valid and non-empty; dominant pixels matched the requested RGB exactly, and curved/diagonal antialias pixels stayed within 3 RGB levels. Therefore the three corrected color-token cases (`check`, `download`, `x`) and the corrected folder proposal all render with the expected theme color through the current loader’s substitution behavior. No GUI source was changed to perform this test.

## Attribution and license preservation

The following files were not edited and their SHA-256 values remain as recorded before the correction:

| Preserved file | SHA-256 |
|---|---|
| `ATTRIBUTION.md` | `25006276e56bf4c1389be653cfe1a8e9b761d0f9bdce8995e167409ef20ceda2` |
| `LICENSE-LUCIDE-AT-PINNED-SOURCE-COMMITS.txt` | `1e7290b35280a048667bbf0ebabac1c7fd52a75300e8b2946ac165715997f2bc` |
| `LICENSE-LUCIDE-CURRENT-SNAPSHOT.txt` | `b495047bd93a9b06913511076f504daba17d5bbeb3e0650f3bb53a4220329c57` |
| `LICENSE-FEATHER-MIT-v4.29.1.txt` | `308028e93fcf84972523cdf6e616f73168546b4953895f516d01287f16fe7bee` |

The prior report’s pinned commits, Lucide ISC text and later Feather-derived icon scope, and Feather MIT reference remain available. This correction changes only a color placeholder and one proposal basename; it does not select a different upstream version, establish the originals’ history, or resolve the final legal notice basis. The source/version/notice limitation from the replacement and provenance reports remains open and must be resolved before integration or publication.

## Preservation and scope confirmation

- Changed exactly the four SVG proposal entries in the isolated Lucide directory: three in-place token substitutions, plus the folder token substitution and basename correction. The three license texts and `ATTRIBUTION.md` were byte-verified unchanged.
- Created this report as the only changed file outside that proposal directory. Did not modify the previous Lucide replacement report, complete GUI review, provenance report, original GUI assets, application source, tests, packaging specifications, or any other worktree files.
- No integration, staging, commit, push, publication, tests, or package builds occurred. The corrected proposals remain outside `src/logsentinel/gui/assets/`.
- Pre-existing worktree changes, untracked documentation/licensing work, and release artifacts were preserved. The release EXE and ZIP remain on distribution hold; their final byte sizes and hashes are reported in the task completion response after verification.

No historical ownership of original artwork is claimed. This correction grants no rights, authorizes no integration/publication, and does not clear the Windows distribution hold.
