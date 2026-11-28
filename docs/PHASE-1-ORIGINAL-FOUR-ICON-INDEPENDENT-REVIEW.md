# LogSentinel Phase 1 — Original Four-Icon Independent Review

**Mode:** read-only proposal review. The isolated proposals and live GUI assets were not modified. This review creates no integration approval, authorship certification, rights grant, or distribution clearance. The original GUI artwork’s historical source and ownership remain unresolved.

## Decision summary

| Proposal | Decision | Main basis |
|---|---|---|
| `check.svg` | **INSUFFICIENT EVIDENCE** | Valid and consistent technically, but the silhouette is the same conventional single-stroke check seen in the mapped Lucide candidate; its small proportion changes are not visually distinguishable enough to independently substantiate the stated design separation. |
| `download.svg` | **REQUIRES CORRECTION** | Valid and consistent technically, but the centered down-arrow over a separate tray retains essentially the same recognizable composition and line arrangement as the mapped Lucide download icon. Redesign to be more visually distinct from that reference before reconsidering. |
| `folder_open.svg` | **APPROVED FOR INTEGRATION REVIEW** | Valid, consistent, readable, and visually differentiated from the mapped Lucide folder composition by its two-layer/back-tab structure and broader lifted front lip. This is a review-stage technical/design recommendation only, not approval to integrate. |
| `x.svg` | **INSUFFICIENT EVIDENCE** | Valid and consistent technically, but it remains a conventional crossing X with only modest endpoint/slope changes relative to the mapped Lucide X. Those changes cannot establish independent provenance or meaningful visual distinction. |

**Overall:** the proposal set is not uniformly ready for integration review. Only the folder icon receives **APPROVED FOR INTEGRATION REVIEW**. Redesign `download`; obtain stronger provenance/design-process evidence or a more clearly distinct design for `check` and `x`. Even the folder proposal requires the usual owner, rights, accessibility, application and integration checks. No proposal is integrated or cleared for publication.

## Scope and method

Reviewed the required original proposal report; every current file in `licenses/third-party/asset-remediation/original-four-icon-proposals/`; the four live SVG targets; the current `icons.py` loader and `icon_widgets.py`; theme definitions; relevant control call sites/tooltips; the pinned Lucide proposal report and licence reconciliation; and prior GUI provenance/remediation records. The five-file isolated proposal directory contains `check.svg`, `download.svg`, `folder_open.svg`, `x.svg`, and `fallback_icons.py`.

Checks included raw-byte SHA-256 and size recomputation, XML parsing and SVG attribute/path inspection, loading fallback strings from the isolated module without importing it as application code, and a visual side-by-side raster comparison of live originals, Lucide proposals, and original proposals. A second Qt check exercised the actual production `icon_svg()`/`icon_pixmap()` path with proposal content supplied in memory and the matching proposal fallback path injected only for that check. No source file or asset was edited to perform the checks.

The production loader normally reads `icons/{name}.svg`; these files are at the proposal directory root, so the proposal SVGs were returned through the loader’s existing `_read_asset` seam in memory. For fallback checks, the seam returned “missing” and only the corresponding isolated proposal path string was temporarily supplied in memory as the map value. This proves compatibility of the proposal wrappers/fragments with the loader, not integration or packaging behavior.

## Per-icon findings

### `check.svg` → `check`

**Decision: INSUFFICIENT EVIDENCE**

- **Visual/function:** a clean, easily recognized single check stroke. The broad sweep is legible at 16 px and the 24×24 composition fits the neighboring outline family. The visible control label **Apply** and its tooltip provide the actual action/accessible name, so the glyph does not need to carry the entire meaning.
- **Independence comparison:** the new path coordinates differ from the live original and pinned Lucide proposal. In a side-by-side view, however, all three appear as the same conventional check silhouette; at ordinary icon size the minor proportion differences are not a reliable visible distinction. A check is a highly conventional symbol, so resemblance alone neither proves copying nor proves independent authorship. The proposal report’s declaration that the path was newly drafted is useful provenance documentation but is authored by the generating assistant and was not independently corroborated.
- **SVG/fallback:** valid SVG root, 24×24 viewBox, no fill, `stroke="CURRENT_COLOR"`, 1.8 stroke, round caps/joins, one path. `fallback_icons.py` contains the same single path-data string. Composing the fallback wrapper gives exactly the proposal SVG string.
- **Theme/rendering:** token is supported by the production literal replacement. It rendered successfully in all four themes using the existing roles. Technical rendering does not resolve visual-source ambiguity.
- **Accessibility:** retain the control’s visible **Apply** name and tooltip. Do not use green as the sole confirmation cue. Suggested accessible description in the proposal report is semantically suitable; no explicit ARIA/name metadata is embedded in the decorative SVG.
- **Remaining limitations:** no independent human authorship confirmation, source-history corroboration, exhaustive similarity search, rights/licence decision, live GUI or screen-reader testing. The visual and provenance record is insufficient for this review to distinguish the mark from the mapped conventional Lucide design.

### `download.svg` → `download`

**Decision: REQUIRES CORRECTION**

- **Visual/function:** the downward shaft, two-arm arrowhead, and separate tray communicate downloading/export. The visible export-button text and tooltip make the purpose clear. The deliberate gap remains visible at the tested small size, though it is only a few rendered pixels at 16 px.
- **Independence comparison:** although endpoints, proportions and serialization differ, the visual arrangement remains essentially the familiar Lucide-style centered downward arrow over a horizontal receiving tray. The side-by-side raster comparison does not show a substantial silhouette change from the mapped Lucide proposal. The task specifically requires a design that does not visibly reproduce the mapped design; path-coordinate changes and the proposal report’s own authorship statement do not cure this visual concern. Redesign from a more distinct export concept (for example, a document/output cue or another clearly differentiated but still conventional export metaphor), without tracing the mapped paths.
- **SVG/fallback:** valid 24×24 SVG; no fill; `CURRENT_COLOR`; 1.8 stroke; round caps/joins; three path elements. The isolated fallback contains the same ordered path data and composes byte-for-byte to the SVG proposal.
- **Theme/rendering:** actual loader substitution and Qt rendering passed for all four themes, semantic roles and tested sizes. Color is supplied by the caller, not fixed in the file.
- **Accessibility:** visible `Export {format}` button label and destination tooltip identify purpose. Suggested accessible name/description is contextually suitable if format text is resolved to the actual format. The icon itself should remain decorative and must not replace the button text.
- **Remaining limitations:** same provenance, rights, author corroboration, uniqueness-search, GUI integration, and accessibility-test limitations as the other candidates. The immediate correction is a visual redesign, not a token/render fix.

### `folder_open.svg` → `folder_open`

**Decision: APPROVED FOR INTEGRATION REVIEW**

- **Visual/function:** the rear tab/back edge and broad lifted front lip read as an open folder, appropriate to both **Add Folder** and configuration **Browse**. The design is compact and readable at 16 px, with the labels/tooltips distinguishing the two actions.
- **Independence comparison:** the proposed shape uses a separated back/top edge and a more visibly lifted front lip, whereas the mapped Lucide proposal is a single, more continuous folder contour. This produces a meaningfully different composition in the comparison while preserving the general folder concept. This is a limited visual observation, not proof of independent authorship, legal originality, or non-infringement.
- **SVG/fallback:** valid 24×24 SVG; no fill; `CURRENT_COLOR`; 1.8 stroke; round caps/joins; two paths. The isolated fallback contains the same ordered path strings and wrapper, yielding exact serialized parity.
- **Theme/rendering:** token and color replacement function with the current loader. Qt rendering succeeds in all four themes, roles and requested sizes. The visible open interior remains clear at 16 px; optical centering still merits a live-widget review.
- **Accessibility:** preserve **Add Folder** or **Browse** text and task-specific tooltip. The proposal’s suggested contextual names/descriptions are suitable; the icon is decorative and should not be the only accessible label.
- **Remaining limitations:** assistant-authored independence statement is not external corroboration; no exhaustive artwork/mark similarity search or legal review was done. Rights, licence scope, original GUI art provenance, live app behavior, screen-reader behavior and package integration remain open. “Approved for integration review” is only a recommendation to include this candidate in a later, separately authorized integration evaluation.

### `x.svg` → `x`

**Decision: INSUFFICIENT EVIDENCE**

- **Visual/function:** two rounded crossing strokes form a clear close/clear mark. It is legible at 16 px and uses no ring or color-only warning. The glyph is used for **Clear All**, **Clear**, and **Reset Overrides**, each of which has visible text and a specific tooltip.
- **Independence comparison:** endpoint positions and diagonal angles differ slightly from the mapped Lucide proposal and live original, but a side-by-side view still reads as the same conventional X silhouette. Because this is a minimal common symbol, those subtle changes are not enough to independently establish a distinct design. The assistant’s declaration records intent but is not an independent provenance check; similarity cannot establish either copying or originality.
- **SVG/fallback:** valid 24×24 SVG; no fill; `CURRENT_COLOR`; 1.8 stroke; round caps/joins; two paths. The isolated fallback uses identical path data and wrapper, with exact serialized parity.
- **Theme/rendering:** production loader replaces `CURRENT_COLOR`; rendering passed through the tested themes, roles and sizes.
- **Accessibility:** preserve each control’s action-specific text and tooltip. The suggested accessible name should match the control (`Clear All`, `Clear`, `Reset Overrides`) and any description must describe that distinct action, not a generic “close”.
- **Remaining limitations:** no external authorship confirmation, broader similarity search or rights decision; no live GUI/screen-reader testing. Maintain the conventional X semantics, but gather stronger independent design provenance or reconsider how to document/review this standard glyph before relying on it as a provenance-clearing replacement.

## Technical verification, hashes and mapping

All four standalone SVG files parse as XML. Each root is SVG with the expected 24×24 viewBox, `fill="none"`, `stroke="CURRENT_COLOR"`, `stroke-width="1.8"`, and round line caps/joins. There are no scripts, embedded images, remote references, or fixed palette colors in the proposals. The fallback fragments are valid inside the isolated module’s shared SVG header/footer.

| Icon | Exact proposal filename → loader key | Proposal bytes / SHA-256 | Fallback fragment bytes / SHA-256 | SVG/fallback result |
|---|---|---|---|---|
| Check | `check.svg` → `check` | 206 / `2ade700f50424ee0b66d406c9cb405de728aa64274f72cf92118c4aa24e503c5` | 39 / `8927a53e0b1e383881e5a0640692f022666b4fe640fd72584c1a277c8b5343b2` | Exact path and serialized-SVG match |
| Download | `download.svg` → `download` | 302 / `649f151b818d83d1daf5637a161a85190a18e9ca30c26de8ed18afe9fcd8cd14` | 135 / `386ad7ed896bac9935a5952b9bbb532802f866268118cf7921686a7a9ac2915c` | Exact ordered paths and serialized-SVG match |
| Folder open | `folder_open.svg` → `folder_open` | 372 / `9693d483e481b8d4e568ba1d6ff3cd34e2c6a926332427144b5612b20c9d28f9` | 205 / `88a6558c17291ac3e1ee3ad5c930f0b911b9e545a410906b0be6cb6258043ab8` | Exact ordered paths and serialized-SVG match |
| X | `x.svg` → `x` | 227 / `5431c0a386982a0585853b9b1d0805438cdc58450446798c82fa00dd07a7c7cc` | 60 / `3aff92e2642156543f55706bf2c25a20e447be403b130198bdaf9ad5535cdef4` | Exact ordered paths and serialized-SVG match |

The fallback module is 1,290 bytes; its SHA-256 is `b26fa17e10bf0cf37abd7b019a736e69589223e4e689510bd737b04272e700cb`. The full file hash is distinct from the per-fragment hashes above. The current SVG basenames match the local mapping (`folder_open`, not the upstream Lucide filename `folder-open`).

The actual loader/color/fallback render matrix passed **320 paired cases**: four icons × four themes (`dark`, `light`, `midnight`, `cyber_teal`) × four roles (`text_muted`, `text`, `accent_text`, `disabled_text`) × five sizes (16, 20, 24, 32, 40 px). For each pair, the loader-produced SVG strings and Qt-rendered images were identical; all produced visible pixels and opaque core strokes. Maximum opaque RGB-channel rounding error relative to the requested color was one level. This validates technical rendering and fallback equivalence, not full application or accessibility approval.

## GUI/accessibility context and unresolved limitations

`ThemeIconButton` renders a 16px icon, refreshes colors on theme changes, and uses the disabled semantic color when disabled. `ThemeIconLabel` uses caller-selected semantic roles and supports other sizes. Call sites supply text and tooltips:

- `panels.py`: **Apply** (accent text); **Add Folder** (text); **Clear All**, **Browse**, **Clear**, and **Reset Overrides** (default muted role).
- `reports_view.py`: report export button icons at 16 px in `accent_text`, alongside visible `Export …` text and a destination tooltip.

No SVG contains accessibility metadata, which is appropriate for these currently decorative icons only when the parent controls retain accessible names. The inspected usage supports that principle, but no screen reader or Qt accessibility-tree test was run. The proposed accessible wording is advisory and not implemented in code.

The GUI source’s embedded `_ICON_PATHS` still contains its pre-existing Lucide-style geometry and the module comment still describes fallback paths as Lucide-style. These isolated proposals do not replace that live geometry, so using an original SVG while an asset is missing would still invoke the old fallback. A later integration would need a coordinated fallback update and accurate source comment, plus asset-path, tests, and package checks. No such update is authorized here.

The proposal report’s “newly drafted” statement is self-reported assistant provenance. This review confirms the present files and the stated render/geometry consistency, but cannot independently witness their creation or certify that no third-party influence occurred. Common check/X/download/folder concepts are not distinctive authorship evidence. No exhaustive similarity search, human creator confirmation, legal opinion, rights grant, original-asset history determination, full GUI integration test, screen-reader check, or packaging build was performed. The earlier Lucide proposal review remains separate; this report does not change its four **INSUFFICIENT EVIDENCE** decisions or settle its Feather notice question.

## Preservation and changed-file record

**This task’s only created file:** `docs/PHASE-1-ORIGINAL-FOUR-ICON-INDEPENDENT-REVIEW.md`.

The pre-existing worktree changes remain the four tracked modifications (`.gitignore`, `README.md`, `docs/USAGE.md`, `packaging/LogSentinel-GUI-Onedir.spec`) and the pre-existing untracked Phase 1/licensing work. No paths are staged. The four original GUI SVGs and the four corrected Lucide SVGs retain their previously recorded SHA-256 values; this task only read them. No tests or builds were run beyond the described isolated Qt renderer checks. No files were integrated, staged, committed, pushed, or published.

Release artifacts were rechecked and remain present and unchanged:

- `release/LogSentinel-Windows-v0.1.0/LogSentinel.exe`: 9,922,891 bytes; SHA-256 `d1bda55a555f6e1a6a433eae89d648079f7eeeb869bd9ee3da487cde36d52b04`.
- `release/LogSentinel-Windows-v0.1.0.zip`: 9,733,515 bytes; SHA-256 `00b13f0dbf7db61a838be8979f92e4ab761d098b44c071d2b365916fb77cf53a`.

Both remain **HOLD — NOT CLEARED FOR DISTRIBUTION**.
