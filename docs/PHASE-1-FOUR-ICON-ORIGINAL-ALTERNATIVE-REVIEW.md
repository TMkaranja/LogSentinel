# LogSentinel Phase 1 — Four-Icon Original Alternative Review

**Mode:** read-only investigation. This review file is the only permitted creation. No live asset, Lucide proposal, application source, test, packaging file, license record, or release artifact was changed. No icon was integrated. This review does not infer the historical origin or ownership of the existing GUI artwork from geometry, technical similarity, matching hashes, or fallback paths.

## Conclusion

Four independently designed 24×24 SVG icons are a **practical engineering alternative** to the isolated Lucide proposals. Their functions are simple, conventional UI actions; current controls already provide text/tooltips; all are rendered as monochrome strokes using a caller-provided theme color. Independent designs can retain the existing filenames, viewBox, control labels, icon names, and loader interface while avoiding Lucide/Feather SVG paths and artwork.

This is a design-feasibility conclusion, not a legal clearance or guarantee of uniqueness. An implementer should draw new path geometry from the functional briefs below—not trace, edit, or use the Lucide proposal paths as source. Authorship and design provenance should be recorded contemporaneously and reviewed before integration.

**Important completeness condition:** `src/logsentinel/gui/icons.py` embeds fallback geometry for all four names, and its module comment calls those paths “Lucide-style.” A replacement limited to standalone SVG files would leave fallback artwork in the application when an asset is missing. A complete independent-artwork implementation should update the four fallback drawings in the same approved change (or deliberately change the fallback contract), preserve missing-asset behavior, and remove/update source provenance wording that would inaccurately characterize newly authored paths. No such changes are made here.

## Scope and evidence reviewed

Reviewed the current live SVGs and all four corrected isolated proposals; `src/logsentinel/gui/icons.py`, `src/logsentinel/gui/icon_widgets.py`, theme definitions and direct GUI consumers; `tests/test_gui_themes.py`; and the Phase 1 GUI asset reports covering provenance, publication resolution, replacement, correction, eligibility, licensing/attribution, and independent design proposals. The publication-scope review, source-publication review, blocker register, and manifest were also checked for implications to assets, tests, packaging, and disclosure.

The reports consistently distinguish the exact pinned Lucide source of the **proposals** from the unresolved history of the original LogSentinel SVGs. The four Lucide proposals remain unintegrated and all four eligibility decisions remain **INSUFFICIENT EVIDENCE** owing to unresolved per-icon Feather notice scope. This review does not alter that record or clear either the original artwork or the Lucide proposals.

## Current loader and theme contract

- `icons.icon_svg(name, color)` reads `gui/assets/icons/{name}.svg`; if unavailable it composes SVG from `_ICON_PATHS` in `icons.py`. `_with_color()` replaces the literal `CURRENT_COLOR` token with the requested color. `icon_pixmap()` renders through Qt `QSvgRenderer`; `icon()` creates a multi-size `QIcon` (16, 20, 24, 32 px by default).
- `ThemeIconButton` sets its icon from the current semantic theme role and refreshes after theme changes and enabled-state changes. Disabled buttons use `theme.disabled_text`; enabled buttons use the selected role. `ThemeIconLabel` renders a role-colored icon, but none of these four icons is currently used as a standalone icon label.
- The theme system defines four appearances (dark, light, purple, teal) with hex-string semantic colors. New SVGs can use the existing `stroke="CURRENT_COLOR"` convention and avoid fixed stroke colors/fills. Existing target icons use 24×24 viewBoxes, `fill="none"`, rounded caps/joins, and `stroke-width="1.8"`.
- The corrected Lucide proposals use the same color token, a 24×24 viewBox and round caps/joins, with 2px stroke. Their stroke token is therefore technically compatible with the icon color substitution. Their artwork/source/licensing question is separate from rendering compatibility.
- The specs are documented to bundle the GUI SVG assets. The source loader’s embedded fallbacks are used if SVG files cannot be read, so maintaining visual and theme parity between asset and fallback matters for wheel/source deployments and test scenarios.

## Per-icon purpose, exact uses, and independent design brief

All paths below are repository-relative; line numbers are the inspected current-source locations. The designs are **text-only briefs** in this review, not SVG code or approved final art. The implementation should make fresh path choices and avoid copying path coordinates or serialization from either the Lucide proposals or old assets.

| Icon | Purpose and visual requirements | Exact current application use | Original design brief (24×24) |
|---|---|---|---|
| `check.svg` / `check` | Communicate successful confirmation/application. Must read clearly at 16 px on primary and ordinary controls, with no fill or reliance on green alone. | `src/logsentinel/gui/panels.py:763`: `Apply` configuration button (`ThemeIconButton`, role `accent_text`); tooltip at line 764 explains validation. Also fallback name `check` in `src/logsentinel/gui/icons.py:122`. | Draw a new, simple confirmation mark using a hand-designed, slightly asymmetric continuous check stroke with deliberate spacing from the 24px canvas edge. Avoid reusing the existing or Lucide check coordinates. Keep it one clear stroke with round ends; no tiny secondary details. The text label “Apply” carries the action if the image is visually ambiguous. |
| `download.svg` / `download` | Indicate exporting/saving a report. Must remain recognizable at 16 px and work in the button’s foreground/accent text color. | `src/logsentinel/gui/reports_view.py:252–256`: every report-format export button gets `icon("download", current_theme().accent_text)` at 16×16. The visible control text begins “Export …”; tooltip at lines 243–244 identifies the report destination action. Also fallback name `download` in `icons.py:78–82`. | Design a new downward transfer motif: a compact arrow with distinct shaft/head ending at a separate shallow receiving baseline or tray. Choose original proportions and path joins, not Lucide’s arrow/tray paths or their coordinates. Keep a visible gap between arrow and tray so the meaning survives at 16px. Do not use a filled arrow that changes the outline family. |
| `folder_open.svg` / `folder_open` | Communicate selecting a directory or browsing for a file. The icon serves both folder selection and configuration-file browsing, so text labels/tooltips—not the glyph alone—must distinguish them. | `src/logsentinel/gui/panels.py:377–379`: `Add Folder`, tooltip “Add a directory for recursive log discovery”; `panels.py:704–705`: `Browse`, tooltip “Validate and load a JSON configuration file”. Also fallback name `folder_open` in `icons.py:87–91`. | Draw an original open-container/folder symbol using a clearly visible rear tab and front lip, plus a lifted/open upper edge that is distinct from the known Lucide folder contour. Keep the interior largely empty and avoid small file/detail marks that collapse at 16px. Use fresh geometry and proportions. The adjacent “Add Folder” and “Browse” labels provide specific task context. |
| `x.svg` / `x` | Mark clear, close/remove, or reset actions. It is not a success/failure status on its own; preserve labeled controls. | `src/logsentinel/gui/panels.py:409–411`: `Clear All` selected input paths; `panels.py:707–709`: `Clear` configuration file; `panels.py:760–762`: `Reset Overrides`. Each has visible text and a task-specific tooltip. Also fallback name `x` in `icons.py:128`. | Draw a fresh, balanced cancellation/clear cross with two rounded diagonal strokes, but select original endpoints, crossing placement, and line rhythm rather than reusing existing/Lucide coordinates. Avoid adding a ring or warning shape, which would change a simple clear action into a stronger destructive/error metaphor. Since “x” is inherently conventional, the authorship record should be especially explicit about drawing process; do not claim visual uniqueness based on a changed angle alone. |

The icon names remain stable because they are part of current call sites and the loader/fallback map. That compatibility does not require retaining the same artwork. No use-site change is needed merely to substitute an original SVG; broader icon-name cleanup is not part of this route.

## Theme-colour, rendering, and consistency assessment

**Mechanism: compatible by design.** Each future original SVG should retain a simple root SVG with `viewBox="0 0 24 24"`, `fill="none"`, stroke set to the literal `CURRENT_COLOR` placeholder, and no hard-coded color. The existing loader substitutes the exact hex value passed by each widget before Qt parses/renders the SVG. Use a coherent stroke weight and rounded caps/joins consistent with the rest of the icon family. A 1.8px stroke matches current live originals; the 2px weight in the corrected Lucide proposals is also technically renderable but should not be adopted by habit if consistency with live originals is the goal.

The current call sites supply semantic colors: the Apply button uses `accent_text`; Add Folder uses `text`; Browse, Clear, Clear All, and Reset use the default muted role; report export buttons use `accent_text`; disabled `ThemeIconButton`s switch to `disabled_text`. The color replacement handles all of these the same way and supports each of the four themes. Avoid palette-specific paths or separate light/dark SVG versions.

**Expected format/render path:** simple SVG paths (and, if justified, basic line/shape elements) are appropriate for `QSvgRenderer` and scale to the existing pixmap sizes. Avoid filters, masks, scripts, embedded images, external references, CSS-dependent color, and unnecessary tiny details. The check, download, folder and x designs should use no more geometry than needed. This review checked the current files and loader but did not render any newly proposed original artwork; actual rendering must be verified in the next implementation task.

## Accessibility, visual, and regression concerns

- **Decorative icon semantics:** these four icons accompany visible text on the inspected controls; several also have specific tooltips. The icon itself should not be the only accessible name. Preserve button text, tooltips, keyboard focus, and existing hit areas. If a future use makes any icon-only button, add/verify its accessible name and tooltip at that control rather than relying on a visual glyph.
- **Contrast:** the parent supplies theme colors, but color support does not prove sufficient contrast in every state. Inspect all four designs at their actual 16px button rendering and any 24/32px icon rendering; check muted, accent-text, text, and disabled roles on all four palettes. Disabled-state legibility and any anti-aliased thin strokes deserve particular attention.
- **Small-size legibility:** preserve a simple silhouette, internal negative space, and endpoint separation; avoid thin parallel segments that merge at 16px. The folder’s inside edge and download arrow/tray gap are likely to need pixel-size review. A geometrically correct SVG may still appear optically off-center at 16 px; inspect actual Qt rasterization, not just XML validity.
- **Consistency:** keep 24×24 viewBox, visual bounds, nominal stroke, round caps/joins, and currentColor token aligned across all four and the remaining icon family. The folder path may require an optical rather than numeric center. Avoid introducing filled/colored artwork into the existing outline system.
- **Behavior/cache:** names and colors are cache-key components in `icon_pixmap`; retain expected names and let theme changes obtain the correct rendered color. Keep fallback output behavior synchronized with standalone assets, including valid SVG root and token substitution.
- **Qt/package reliability:** verify both asset-present and missing-asset branches, SVG parse success, non-null/non-empty pixmaps at actual requested sizes, and the packaged filesystem path. No runtime, packaging, regression suite, screen-reader audit, or Windows shell verification was run for this review.

## Independent authorship and provenance record

For each newly designed icon, document the work as a new candidate asset, not as an assertion about the original GUI file. A future asset register/report should record:

1. Exact proposal path/name and semantic purpose/call sites.
2. Designer/author and any tool or AI assistance, creation date, and the author’s confirmation that the final geometry was drawn independently from the functional brief.
3. Source-of-design materials and workflow: state that Lucide/Feather SVG path data, the corrected Lucide proposal files, and the old artwork were not used as tracing/editing inputs, if that is accurate. Distinguish using icon libraries only to understand a generic function from copying their geometry.
4. A content hash (e.g. SHA-256) for the final candidate bytes; record each subsequent edit/hash separately. A hash proves which bytes the record concerns, not authorship by itself.
5. Any external references, fonts, templates, generators, or imported shapes and their licenses/notice obligations; state “none” only after checking and author confirmation.
6. Rights holder and intended project license/permission for the new drawing, plus any required attribution/notice decision, reviewed by the responsible project owner. Do not infer permission from the repository MIT license or a commit author name.
7. Review and validation record: viewBox/token/stroke contract, Qt render sizes and themes, accessibility label context, and the exact Git commit that introduces the proposal.

If AI-assisted, the record should accurately name that assistance and the human direction/review; it should not make an unsupported legal claim that generated output is necessarily unique or copyrightable. Keep this new-art record separate from the unresolved provenance of the originals and the Lucide proposal license issue. Do not retroactively rewrite the original GUI artwork’s source history.

## Practical route and next implementation task

**Practical route:** replace the four Lucide candidate designs with independently drawn, simple line-art SVG alternatives under an isolated, clearly marked proposal location. Keep existing targets and source code untouched in that implementation pass unless the separately authorized task explicitly includes them. Do not copy the Lucide proposal files into the new proposal set. Use a design process based on the functional descriptions above and the application’s rendering contract only.

**Next task recommendation — Task 3.10.8, “Create and validate isolated original alternatives for check/download/folder-open/x”:**

1. Create four fresh SVG proposals only, with target-consistent basenames and `CURRENT_COLOR`, and document authorship/source/hash facts in the authorized proposal record.
2. Design matching fresh `_ICON_PATHS` fallback geometry for these four names (or explicitly decide how the fallback is handled), so the independent-artwork route does not silently retain the current Lucide-style geometry when a packaged asset is absent. This code change should be in the following integration task if the implementation scope remains proposal-only.
3. Validate XML and loader color substitution; render asset-present and fallback variants at 16, 20, 24, 32, and any actual 40px context across dark, light, purple, and teal themes, including disabled-state colors.
4. Review side-by-side at actual control sizes, preserve labels/tooltips and icon bounds, and verify small-size legibility and contrast. Add or update focused regression coverage only under the task authorization.
5. Keep proposals unintegrated until an explicit integration decision, author/rights documentation, and required test/package checks are complete. The Lucide eligibility records remain historical records for those proposals; do not mark them cleared based on new designs alone.

After an original-proposal implementation pass, a separate authorized integration task would need to replace active SVGs, synchronously change the four fallback geometries/provenance comment, verify asset packaging and GUI tests, update the source attribution/provenance register, and obtain owner review. That future integration is not approved by this investigation.

## Preservation verification

At the start and final read-only checks, the existing tracked modifications were `.gitignore`, `README.md`, `docs/USAGE.md`, and `packaging/LogSentinel-GUI-Onedir.spec`; other Phase 1 documents and `licenses/` were pre-existing untracked work. No paths were staged. The current live four SVGs and four corrected Lucide proposal files were read only; no app/test/packaging source changed. The release files remain present:

- `release/LogSentinel-Windows-v0.1.0/LogSentinel.exe` — 9,922,891 bytes; SHA-256 `d1bda55a555f6e1a6a433eae89d648079f7eeeb869bd9ee3da487cde36d52b04`.
- `release/LogSentinel-Windows-v0.1.0.zip` — 9,733,515 bytes; SHA-256 `00b13f0dbf7db61a838be8979f92e4ab761d098b44c071d2b365916fb77cf53a`.

Both artifacts remain **HOLD — NOT CLEARED FOR DISTRIBUTION**. The requested report is the only file created by this task. No tests, builds, commits, pushes, or publication actions were performed.

## Related Phase 1 records reviewed

- `docs/PHASE-1-GUI-ASSET-PROVENANCE-REPORT.md`
- `docs/PHASE-1-GUI-ASSET-PUBLICATION-RESOLUTION.md`
- `docs/PHASE-1-LUCIDE-ASSET-REPLACEMENT-REPORT.md`
- `docs/PHASE-1-LUCIDE-ASSET-CORRECTION-REPORT.md`
- `docs/PHASE-1-LUCIDE-INTEGRATION-ELIGIBILITY-REVIEW.md`
- `docs/PHASE-1-LUCIDE-LICENCE-ATTRIBUTION-RECONCILIATION.md`
- `docs/PHASE-1-COMPLETE-GUI-ASSET-REPLACEMENT-REVIEW.md`
- `docs/PHASE-1-ORIGINAL-GUI-ASSET-REPLACEMENT-REPORT.md`
- `docs/PHASE-1-COMPLETE-PUBLICATION-SCOPE-REVIEW.md`
- `docs/PHASE-1-GITHUB-SOURCE-PUBLICATION-REVIEW.md`
- `docs/PHASE-1-GITHUB-PUBLICATION-BLOCKER-REGISTER.md`
- `docs/PHASE-1-GITHUB-SOURCE-PUBLICATION-MANIFEST.md`
