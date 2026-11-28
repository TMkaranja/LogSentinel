# Phase 1 — Three-Icon Original Proposal Redesign Report

**Status:** redesigned `download`, `check`, and `x` candidates and their matching isolated fallback geometry. All proposals remain isolated and **not integrated**. `folder_open.svg` remains unchanged and retains its prior **APPROVED FOR INTEGRATION REVIEW** decision. This report does not grant publication clearance or establish legal originality, authorship, or rights.

## Summary and design rationale

| Key / filename | New visual concept | Intended semantics and accessibility | Distinction from prior proposal |
|---|---|---|---|
| `download.svg` → `download` | **File receiving a downward arrow:** compact document outline with folded upper corner and an arrow directed into the document interior. | Download/export a report. Existing buttons retain visible `Export {format}` text and destination tooltip; suggested accessible name is `Export {format}` with a format-specific destination description. Keep the icon decorative alongside the labeled control. | Replaces the arrow-above-horizontal-tray arrangement entirely. No separate tray or tray-like baseline is used. The inward arrow and recognizable page silhouette remain legible as a file-download metaphor at small sizes. |
| `check.svg` → `check` | **Confirmation seal with a central four-point spark:** circular outline contains a centered diamond-like glint; there is no checkmark stroke. | Confirmation/apply state. Existing **Apply** text and validation tooltip continue to identify the action. Suggested name/description: **Apply** — “Validate and apply the configuration.” Do not communicate success through color alone. | Replaces the single conventional checkmark with a round seal/spark composition rather than adjusting checkmark coordinates. This is a confirmation cue, not a claim that validation succeeded unless the surrounding control/state says so. |
| `x.svg` → `x` | **Tilted eraser:** angled, two-part outlined eraser with a short grounded baseline. No pair of crossing diagonal strokes. | Clear/reset actions in the inspected uses. Preserve action-specific control names (**Clear All**, **Clear**, **Reset Overrides**) and their existing descriptions/tooltips. The SVG remains decorative. | Replaces the crossed X with an eraser metaphor; this better matches the current clear/reset actions. It is not a general-purpose close symbol and should not be used to dismiss a window/dialog without a separately reviewed metaphor. |

The geometry is newly drafted for these functional briefs, using the existing 24×24 outline convention and theme token. No third-party icon artwork was intentionally copied or traced as construction input. The changed concept and path data do not prove authorship, uniqueness, non-infringement, or absence of influence; this assistant-generated provenance statement has not been independently corroborated.

## File hashes and mapping

SHA-256 values below cover exact UTF-8 file bytes. Fallback fragment values cover just the corresponding `ICON_PATHS` string, not the full Python module. Wrapping each fragment in `SVG_HEADER + fragment + SVG_FOOTER` yields byte-for-byte the associated SVG file.

| File / mapping | Bytes | SHA-256 |
|---|---:|---|
| `licenses/third-party/asset-remediation/original-four-icon-proposals/download.svg` (`download.svg` → `download`) | 363 | `7e86a3790b6391e40e3f39712270ebd248c95586f6db02ee56a23dcc96339244` |
| `licenses/third-party/asset-remediation/original-four-icon-proposals/check.svg` (`check.svg` → `check`) | 274 | `fcef03681b865729223add19063265b82730b18f723ea8b42529ba1ab2a5a03e` |
| `licenses/third-party/asset-remediation/original-four-icon-proposals/x.svg` (`x.svg` → `x`) | 371 | `05ea73de346c5f881b2bde865c04a50f582350856c82ec606941e72532bb92d6` |
| `licenses/third-party/asset-remediation/original-four-icon-proposals/fallback_icons.py` | 1,612 | `6da4502f20cfe0365c67545409988f35cabcb8cdebdc94a3e4a4853de6bd82b0` |
| Unmodified `folder_open.svg` | 372 | `9693d483e481b8d4e568ba1d6ff3cd34e2c6a926332427144b5612b20c9d28f9` |

The fallback module remains isolated and is not imported by the live application. The unchanged `folder_open` fragment is 205 bytes, SHA-256 `88a6558c17291ac3e1ee3ad5c930f0b911b9e545a410906b0be6cb6258043ab8`.

## Technical validation

**Result: PASS** for all requested proposal checks. The existing production loader source was imported and exercised without edits. The test temporarily supplied proposal SVG bytes through the loader’s `_read_asset` seam; to exercise fallback mode, it temporarily returned “missing” for that asset and supplied the isolated fallback path string in memory. The module state was restored after the check. The fallback module was read/compiled as isolated test data, not imported by the application.

| Check | Result |
|---|---|
| XML parsing of the three standalone SVGs and fallback-composed documents | **PASS** (6 documents) |
| XML parsing of loader-colored SVG outputs | **PASS** |
| SVG root/viewBox and convention: 24×24, `fill="none"`, `stroke="CURRENT_COLOR"`, `stroke-width="1.8"`, rounded caps/joins | **PASS** |
| Filename-to-loader-key mapping: `download.svg` → `download`, `check.svg` → `check`, `x.svg` → `x` | **PASS** |
| Exact serialized SVG/fallback-wrapper parity | **PASS** for all three |
| Production `icon_svg()` token replacement and production `icon_pixmap()` rendering | **PASS**; no unresolved `CURRENT_COLOR`, no null/blank pixmaps |
| Themes | **PASS** for `dark`, `light`, `midnight`, `cyber_teal` |
| Semantic color roles | **PASS** for `text_muted`, `text`, `accent_text`, `disabled_text` |
| Requested sizes | **PASS** at 16, 20, 24, 32, and 40 px |
| Asset/fallback raster equality | **PASS** in all 240 pairs: 3 icons × 4 themes × 4 roles × 5 sizes |
| Unchanged folder file hash | **PASS** against the previous value |

The rendering matrix establishes loader/token compatibility and exact fallback output for these isolated shapes. It is not a live-widget, screen-reader, packaging, DPI, or legal originality test. Visual review was limited to the proposal preview and tested raster sizes; formal usability testing has not been done.

## Scope, preservation, and limitations

This task changed exactly the following existing proposal files and created the report:

1. `licenses/third-party/asset-remediation/original-four-icon-proposals/download.svg`
2. `licenses/third-party/asset-remediation/original-four-icon-proposals/check.svg`
3. `licenses/third-party/asset-remediation/original-four-icon-proposals/x.svg`
4. `licenses/third-party/asset-remediation/original-four-icon-proposals/fallback_icons.py`
5. `docs/PHASE-1-THREE-ICON-REDESIGN-REPORT.md`

`folder_open.svg` was not modified. Live GUI SVGs, `src/logsentinel/gui/icons.py`, tests, packaging configuration, release artifacts, and other pre-existing worktree files were not modified by this task. The live icon loader still has its existing fallback geometry; this isolated proposal module does not change that. No proposal was integrated. Nothing was staged, committed, pushed, or published.

Preservation check hashes (the same values recorded before the redesign) confirm the live SVGs remain unchanged:

- `src/logsentinel/gui/assets/icons/check.svg`: 196 bytes; `0f68dcfa6748c435768b27317f89689bc752a27bd63b797737972340ec283c39`
- `src/logsentinel/gui/assets/icons/download.svg`: 267 bytes; `fb67a5ce7e49bce1df96910725e71b47820ac5046e91a6ecf85b95b8a0e2da77`
- `src/logsentinel/gui/assets/icons/folder_open.svg`: 358 bytes; `c7c425bb348b1af16c697be291b12c9e05e87400487a2f8caa017b0f8329b7d0`
- `src/logsentinel/gui/assets/icons/x.svg`: 213 bytes; `8257c7412a3231067454c75cea0d56530ca400c29051fa7a840c8df5790a4edf`

The separate corrected Lucide proposal SVGs were also read-only and retain their recorded hashes: check `ce862ced28c4f3163e6258b83a8a7231166149242e094a460449fbd5230c48cc`; download `6f70003d0f4ade05e8bb586a4d89a551058d5682b3141e9452d2ef593713442e`; folder-open `b6d39a234cab41b365fc696f3fff3f38525cef6120d952e5651762e64119b09c`; X `eebd33f4843cc6a8bccfee89ff350cfcaeca9fbbe5076823742c32896e54b49a`.

Release artifacts remain present and unchanged:

- `release/LogSentinel-Windows-v0.1.0/LogSentinel.exe`: 9,922,891 bytes; SHA-256 `d1bda55a555f6e1a6a433eae89d648079f7eeeb869bd9ee3da487cde36d52b04`.
- `release/LogSentinel-Windows-v0.1.0.zip`: 9,733,515 bytes; SHA-256 `00b13f0dbf7db61a838be8979f92e4ab761d098b44c071d2b365916fb77cf53a`.

Both remain **HOLD — NOT CLEARED FOR DISTRIBUTION**. Remaining limitations include assistant-only provenance, no independent creator/rightsholder confirmation, no exhaustive similarity search or legal review, no grant/selection of intended licensing, no live application integration, no screen-reader/accessibility-tree test, and no package/release test. The eraser X substitute is semantically scoped to clear/reset; reconsider if a true dismiss/close action is expected. The prior folder proposal’s review-stage approval is unchanged and is not integration or distribution authorization.
