# LogSentinel Phase 1 — Original Four-Icon Proposal Report

**Status:** four original SVG alternatives and matching fallback path data are isolated proposals. They are **not integrated**. This task modified no live GUI asset, live `icons.py`, test, packaging file, license file, or release artifact. The report and proposal files do not establish historical ownership or source of the existing LogSentinel artwork, clear any asset for publication, or authorize binary distribution.

## 1. Result

Created new 24×24 line-art candidates for `check`, `download`, `folder_open`, and `x` under `licenses/third-party/asset-remediation/original-four-icon-proposals/`. Each SVG uses the current `CURRENT_COLOR` substitution token, `stroke-width="1.8"`, round caps/joins, and the existing 24×24 viewBox. Matching path strings are provided in an isolated Python fallback module in the same proposal directory; the live fallback map was not changed.

The designs were drafted from the functional briefs in `PHASE-1-FOUR-ICON-ORIGINAL-ALTERNATIVE-REVIEW.md`. They use conventional symbolic concepts and the existing LogSentinel outline/color conventions; they do not introduce a new palette or brand mark. The independent alternatives are not a recreation of the old GUI icons and make no claim about their original authorship.

## 2. Design rationale and semantic descriptions

The icons are decorative on the inspected controls: existing buttons supply visible text and tooltips. Accessible wording below is documented separately from the SVG artwork; no `<title>`, `<desc>`, `aria-label`, button accessible name, or tooltip was added or changed by this isolated proposal task.

| Name / proposal | Design rationale | Current control wording/context | Suggested accessible name and description |
|---|---|---|---|
| `check.svg` (`check`) | A single broad, slightly asymmetric rising check stroke, with a low entry, short lower turn, and longer rising arm. The rebalanced proportions distinguish the proposal’s new path from the source paths while staying immediately recognizable at small size. | `src/logsentinel/gui/panels.py:763–764`: **Apply**; tooltip says “Validate the combined configuration”. | Name: **Apply**. Description: **Validate and apply the configuration.** Keep the visible text; do not communicate success by green color alone. |
| `download.svg` (`download`) | A centered downward shaft and short two-arm point terminate above a separate shallow tray. The intentional gap keeps the transfer direction legible at 16 px without a filled arrow or tiny detail. | `src/logsentinel/gui/reports_view.py:252–256`: report export buttons; visible label is `Export {format}`; tooltip at lines 243–244 identifies choosing a destination. | Name: **Export {format}**. Description: **Choose a destination for the {format} report.** Resolve `{format}` to the button’s actual format label. |
| `folder_open.svg` (`folder_open`) | A compact rear tab and upper back edge sit behind a broad, lifted front lip. The interior stays open; no filename or small detail marks compete at 16 px. | `src/logsentinel/gui/panels.py:377–379`: **Add Folder**; `panels.py:704–705`: **Browse** for JSON configuration. The contextual text/tooltips distinguish the two uses. | For Add Folder: name **Add Folder**, description **Add a directory for recursive log discovery.** For Browse: name **Browse configuration file**, description **Validate and load a JSON configuration file.** |
| `x.svg` (`x`) | Two rounded diagonal strokes cross near center with deliberately offset endpoints and unequal slope. It remains a simple clear/cancel sign, without a ring or warning metaphor. The symbol is conventional; changed coordinates alone are not a uniqueness claim. | `src/logsentinel/gui/panels.py:409–411`: **Clear All**; `panels.py:707–709`: **Clear**; `panels.py:760–762`: **Reset Overrides**. Existing tooltips describe each distinct action. | Preserve each control label as its name: **Clear All**, **Clear**, or **Reset Overrides**. Descriptions should remain action-specific: remove selected input paths; return configuration to built-in defaults; or discard edits and restore loaded values. |

## 3. Proposal file sizes and hashes

Sizes are exact current file bytes; hashes are SHA-256 over those bytes.

| Proposal | Bytes | SHA-256 |
|---|---:|---|
| `licenses/third-party/asset-remediation/original-four-icon-proposals/check.svg` | 206 | `2ade700f50424ee0b66d406c9cb405de728aa64274f72cf92118c4aa24e503c5` |
| `licenses/third-party/asset-remediation/original-four-icon-proposals/download.svg` | 302 | `649f151b818d83d1daf5637a161a85190a18e9ca30c26de8ed18afe9fcd8cd14` |
| `licenses/third-party/asset-remediation/original-four-icon-proposals/folder_open.svg` | 372 | `9693d483e481b8d4e568ba1d6ff3cd34e2c6a926332427144b5612b20c9d28f9` |
| `licenses/third-party/asset-remediation/original-four-icon-proposals/x.svg` | 227 | `5431c0a386982a0585853b9b1d0805438cdc58450446798c82fa00dd07a7c7cc` |
| `licenses/third-party/asset-remediation/original-four-icon-proposals/fallback_icons.py` | 1,290 | `b26fa17e10bf0cf37abd7b019a736e69589223e4e689510bd737b04272e700cb` |

The isolated fallback module has four path-data strings. Their UTF-8 fragment sizes/hashes are:

| Fallback key | Fragment bytes | SHA-256 |
|---|---:|---|
| `check` | 39 | `8927a53e0b1e383881e5a0640692f022666b4fe640fd72584c1a277c8b5343b2` |
| `download` | 135 | `386ad7ed896bac9935a5952b9bbb532802f866268118cf7921686a7a9ac2915c` |
| `folder_open` | 205 | `88a6558c17291ac3e1ee3ad5c930f0b911b9e545a410906b0be6cb6258043ab8` |
| `x` | 60 | `3aff92e2642156543f55706bf2c25a20e447be403b130198bdaf9ad5535cdef4` |

For each icon, composing `SVG_HEADER + ICON_PATHS[name] + SVG_FOOTER` produces byte-for-byte the same UTF-8 SVG text as its corresponding proposal file (no trailing newline). Therefore the SVG file SHA-256 above also identifies the fallback-composed SVG content. The Python module includes only the four isolated fallback fragments and the existing-compatible wrapper/token format; it is not imported by the application.

## 4. Provenance and independence statement

These path geometries were newly drafted for this task from the stated functional purposes and shared display conventions. No Lucide/Feather SVG path data was traced, pasted, transformed, or used as the construction input; the corrected Lucide proposals and the old GUI asset files were not used as tracing/editing material. No external vector art, icon package, font, template, embedded image, or generator was imported into the proposal files. The only external/contextual basis was the written design brief, current application naming/color/rendering contract, and the general functional concepts (confirmation, export/download, folder browsing, clear/reset).

This report records how this assistant generated the candidate geometry; it is not a human creator certification, proof of legal originality/uniqueness, or rights grant. Check and cross marks, arrows, folder shapes, and X marks are conventional visual concepts, and possible similarity to unrelated artwork has not been exhaustively searched. A project owner/rightsholder should review the new assets, confirm the intended license/permission and attribution status, and preserve the authoring record before public source inclusion. This statement applies only to these newly created candidate files; it does not alter the unresolved provenance or rights status of the existing GUI originals or the separate Lucide proposals.

## 5. Validation method and results

Validation used the installed PySide6 6.12.0/Qt SVG stack with `QT_QPA_PLATFORM=offscreen` and `PYTHONPATH=src`. The test harness imported the actual `logsentinel.gui.icons` module and used its `icon_svg()` and `icon_pixmap()` implementations. Since the candidate filenames are at the proposal root rather than `icons/<name>.svg`, the loader’s `_read_asset` seam was temporarily patched in memory to return the isolated proposal content for each matching request. The production source tree was not altered.

For fallback cases, the harness simulated a missing asset by returning `None` from `_read_asset`, injected the matching isolated path fragment into `icons._ICON_PATHS` only for the duration of the check, and called the actual `icon_svg()`/`icon_pixmap()` loader functions. This verifies the production wrapper/color substitution and rendering path with the proposed fallback fragments without importing the proposal module into application code or changing the live fallback map.

| Validation | Result |
|---|---|
| XML parse of each standalone SVG and each fallback-composed SVG | **PASS** (8 documents) |
| `QSvgRenderer.isValid()` and non-empty rendering | **PASS** for each icon in both asset and fallback mode |
| Correct filename/key mapping | **PASS**: `check.svg→check`, `download.svg→download`, `folder_open.svg→folder_open`, `x.svg→x` |
| Theme token replacement | **PASS**: `CURRENT_COLOR` was replaced with the requested hex color, with no placeholder remaining |
| Theme/state colors | **PASS** across all four app themes (`dark`, `light`, `midnight`, `cyber_teal`) and four semantic roles (`text_muted`, `text`, `accent_text`, `disabled_text`) |
| Raster sizes | **PASS** at 16, 20, 24, 32, and 40 px |
| Asset/fallback geometry and serialized output | **PASS**: same path-data values and complete loader-produced SVG string for each pair |
| Asset/fallback pixel equality | **PASS** for every combination: 4 icons × 4 themes × 4 color roles × 5 sizes = **320 paired raster cases** |
| Color fidelity | **PASS**: opaque core pixels matched supplied theme color; maximum observed RGB rounding error was 1 channel level |
| Non-empty small-size silhouette | **PASS**: each produced an opaque core and non-empty pixels at 16 px |

Observed 16px alpha-bound boxes on the raster checks were check `(2,4)-(13,11)`, download `(2,1)-(13,14)`, folder-open `(1,2)-(14,13)`, and X `(3,2)-(12,13)`. These confirm that a visible stroke reached the raster, not that optical centering, contrast, or usability has received formal sign-off.

The validation exercised every theme palette, but used each one of four representative semantic role colors rather than every individual widget/state transition in a live GUI. It did not run the GUI, screen reader, test suite, packaging recipes, Windows shell, high-DPI device matrix, or build. The temporary preview image was not retained in the repository.

## 6. Safeguards and limitations

- The live assets `src/logsentinel/gui/assets/icons/{check,download,folder_open,x}.svg` were not modified. Their existing recorded SHA-256 values were rechecked: `check` `0f68dcfa6748c435768b27317f89689bc752a27bd63b797737972340ec283c39`; `download` `fb67a5ce7e49bce1df96910725e71b47820ac5046e91a6ecf85b95b8a0e2da77`; `folder_open` `c7c425bb348b1af16c697be291b12c9e05e87400487a2f8caa017b0f8329b7d0`; `x` `8257c7412a3231067454c75cea0d56530ca400c29051fa7a840c8df5790a4edf`.
- The four corrected Lucide proposals remain unchanged and isolated. Their SHA-256 values are `ce862ced28c4f3163e6258b83a8a7231166149242e094a460449fbd5230c48cc`, `6f70003d0f4ade05e8bb586a4d89a551058d5682b3141e9452d2ef593713442e`, `b6d39a234cab41b365fc696f3fff3f38525cef6120d952e5651762e64119b09c`, and `eebd33f4843cc6a8bccfee89ff350cfcaeca9fbbe5076823742c32896e54b49a` for check, download, folder-open and X respectively.
- The new fallback file is isolated. The live `src/logsentinel/gui/icons.py` still contains its prior Lucide-style fallback paths and wording. Therefore these proposals alone do **not** complete an application-wide switch away from those fallback designs; a later authorized integration must replace the fallback geometry and accurately update that source comment as well as replace active SVGs.
- No integration, code/test/packaging change, release build, license election, or publication occurred. No source provenance for original GUI assets has been inferred. These proposed SVGs include no text/ARIA metadata because current use is decorative alongside labeled controls; any future icon-only use requires explicit accessible naming.
- The user asked to preserve existing worktree changes. The prior tracked modifications remained `.gitignore`, `README.md`, `docs/USAGE.md`, and `packaging/LogSentinel-GUI-Onedir.spec`; prior untracked reports/licensing work was retained. No path was staged. The EXE and ZIP remain on distribution hold.

## 7. Complete changed-file list for this task

Created exactly these six repository files:

1. `licenses/third-party/asset-remediation/original-four-icon-proposals/check.svg`
2. `licenses/third-party/asset-remediation/original-four-icon-proposals/download.svg`
3. `licenses/third-party/asset-remediation/original-four-icon-proposals/folder_open.svg`
4. `licenses/third-party/asset-remediation/original-four-icon-proposals/x.svg`
5. `licenses/third-party/asset-remediation/original-four-icon-proposals/fallback_icons.py`
6. `docs/PHASE-1-ORIGINAL-FOUR-ICON-PROPOSAL-REPORT.md`

No existing file was changed. No file was staged, committed, pushed, or published.
