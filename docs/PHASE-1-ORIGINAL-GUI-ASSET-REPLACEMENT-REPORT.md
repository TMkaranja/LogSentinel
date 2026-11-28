# LogSentinel Phase 1 — Original GUI Asset Replacement Proposals

**Status:** isolated design proposals only. These files have **not** replaced live GUI assets and are not approved for integration or publication. The Windows executable and ZIP remain **HOLD — NOT CLEARED FOR DISTRIBUTION**.

**Scope:** prepare fresh alternatives for the 19 original GUI assets classified as unknown-provenance in `docs/PHASE-1-GUI-ASSET-PROVENANCE-REPORT.md`: 18 SVGs and one Windows ICO. Keep each proposal under `licenses/third-party/asset-remediation/original-proposals/`; do not change application references, tests, packaging recipes, dependencies, existing release artifacts, or other work.

## 1. Outcome

The isolated directory contains 18 newly authored SVG proposals, a PNG-backed Windows ICO assembled from the proposed app icon, and a self-contained HTML contact sheet. The SVGs preserve the original files’ viewBoxes and names under the proposal tree. No proposed file is referenced by application source, tests, or packaging. The originals remain in place.

The proposals are fresh drawings created for this task; no external artwork file or icon package was used as source material. Familiar functional symbols (documents, search, warning, controls, shield, etc.) are conventional concepts. This statement records the drawing process, **not** a legal opinion, uniqueness search, ownership determination, or assurance that a design cannot resemble other artwork. The old assets’ historical origin and rights remain unresolved.

## 2. Design and implementation notes

- **Small icons:** fresh 24×24 SVG paths, with consistent `stroke-width="2"`, round caps/joins, and `CURRENT_COLOR` for the existing theme-color substitution path. Names match the 14 original icon files in scope. The new detections icon uses a crosshair/inspection motif; warning, file-plus, file-text, log-search, dashboard tiles, palette, play, report/chart, search, slider settings, shield-check, stop, and trash icons are newly composed for their respective functions.
- **Brand artwork:** four replacement SVGs use a new shield-and-log-lines glyph on a green-to-blue rounded tile. App icon and mark share the 64×64 composition. The horizontal and sidebar wordmarks keep the original 320×64 and 240×56 canvases; their text remains live SVG `<text>` using `Inter, Segoe UI, Arial, sans-serif` fallbacks, not embedded font data. Font appearance can therefore vary by platform.
- **ICO:** generated from the proposed 64×64 app-icon SVG using PySide6/Qt SVG rendering and PNG encoding; includes seven 32-bit PNG-backed frames at 16, 24, 32, 48, 64, 128 and 256 pixels. It is a proposed raster derivative of the proposed SVG only; it does not establish the source or rights of the original ICO.
- **Contact sheet:** `licenses/third-party/asset-remediation/original-proposals/contact-sheet.html` embeds the SVG proposals and the largest ICO PNG frame. Theme tokens are filled with a dark-SOC preview palette for visual review; this is not a runtime integration or a claim of full light/dark-theme approval. The reviewed sheet showed all 18 SVGs and the ICO frame.
- **Reference use:** existing GUI loaders, names, viewBoxes, color-token substitution, and Lucide-like stroke conventions were inspected for compatibility. No Lucide/Feather SVG geometry was used as the drawing source for these proposals. That design choice does not itself establish legal uniqueness or clear any original asset.

## 3. Original-to-proposal inventory and SHA-256

“Original dimensions” for SVGs are the viewBox dimensions. “Original bytes/hash” are the live working-tree values verified against the inventory in the provenance report immediately before and after proposal generation. “Proposed bytes/hash” identify the staged proposal bytes. Hashes identify byte sequences; they do not establish authorship, source, license, or rights.

| # | Original path | Original dimensions; bytes; SHA-256 | Proposal path | Proposed bytes; SHA-256 |
|---:|---|---|---|---|
| 1 | `src/logsentinel/gui/assets/brand/logsentinel-appicon.svg` | SVG 64×64; 920; `bb28859d520c23a76493efba923b3adfa8cba6aa873090a29e501362e2f25a61` | `licenses/third-party/asset-remediation/original-proposals/brand/logsentinel-appicon.svg` | 963; `a7bca559a31e3641fe8e501ed314e1192fec79199e7c05cecb17e5a77780091f` |
| 2 | `src/logsentinel/gui/assets/brand/logsentinel-logo.svg` | SVG 320×64; 10,340; `9c30d78911c0fff3a641b1820e139370a0991806dcd0523b207df1e305773fa9` | `licenses/third-party/asset-remediation/original-proposals/brand/logsentinel-logo.svg` | 1,355; `b98c79e6d2fa248b53f5f925df504f5c518baa1ffe64353faaac00966df6e62a` |
| 3 | `src/logsentinel/gui/assets/brand/logsentinel-mark.svg` | SVG 64×64; 920; `bb28859d520c23a76493efba923b3adfa8cba6aa873090a29e501362e2f25a61` | `licenses/third-party/asset-remediation/original-proposals/brand/logsentinel-mark.svg` | 963; `a7bca559a31e3641fe8e501ed314e1192fec79199e7c05cecb17e5a77780091f` |
| 4 | `src/logsentinel/gui/assets/brand/logsentinel-sidebar.svg` | SVG 240×56; 10,083; `eb0d3e0874a3877b79503be7128d10a512dd8205fabae60fee319a34b4dfc62f` | `licenses/third-party/asset-remediation/original-proposals/brand/logsentinel-sidebar.svg` | 1,355; `811ee9a4e4f26ff70546459443a4675b2e7b6f597ef59726deaca7683611f80c` |
| 5 | `src/logsentinel/gui/assets/icons/alert.svg` | SVG 24×24; 292; `191a66cf92f42cdd1bf7375d7b0c94f5f53bac44730201e65a2b284b770c3989` | `licenses/third-party/asset-remediation/original-proposals/icons/alert.svg` | 349; `1a95661e6c827b029e75612ebbe968032f46a73a63704409c9592b0fbde94a5f` |
| 6 | `src/logsentinel/gui/assets/icons/detections.svg` | SVG 24×24; 368; `672cd521c8a8ea7355bdbd4f0de78addd014a4e9725f8e74343a9600a453668a` | `licenses/third-party/asset-remediation/original-proposals/icons/detections.svg` | 405; `c529f4447d7d17237be283ca6981058f421307e30a6ba274add4468ca294e98f` |
| 7 | `src/logsentinel/gui/assets/icons/file_plus.svg` | SVG 24×24; 299; `d0357c44c6c1e429614609657a8af64f8f6edb9780924dd09f2f7206b936f8f8` | `licenses/third-party/asset-remediation/original-proposals/icons/file_plus.svg` | 372; `31cb2a96e7faa859aaabbd6d458e9f08cadef88b04aab5ec86b85389193f1c39` |
| 8 | `src/logsentinel/gui/assets/icons/file_text.svg` | SVG 24×24; 298; `a37006fe9dcf14f1d2758761051f5c4ae169d57512c12e62ce9280d8d945f501` | `licenses/third-party/asset-remediation/original-proposals/icons/file_text.svg` | 456; `507192763e5ba2d7c299af35ba38910347027840f5ba18a206ada5c513059a2f` |
| 9 | `src/logsentinel/gui/assets/icons/log_explorer.svg` | SVG 24×24; 317; `3008d40feac72acb9588ac87193c61e9917f5f5bc72665f5e880a520a06f516f` | `licenses/third-party/asset-remediation/original-proposals/icons/log_explorer.svg` | 391; `e97dcff84d31f64d48bd42eb0a2adce3265ede99b93a946660155b1e40420627` |
| 10 | `src/logsentinel/gui/assets/icons/overview.svg` | SVG 24×24; 368; `379fe603df3afc8b80a178b83bbc649d594a74772e984b3c18c5d6ab152336dd` | `licenses/third-party/asset-remediation/original-proposals/icons/overview.svg` | 468; `7788f2e243065ecb6e737aa822088c4c872b3965929441702faa483830580323` |
| 11 | `src/logsentinel/gui/assets/icons/palette.svg` | SVG 24×24; 444; `629e32b419d0adf0b054a4cb87d52d8dd934a0847b58a06ca7f574d200f353b5` | `licenses/third-party/asset-remediation/original-proposals/icons/palette.svg` | 561; `c4f385ce1cf70c9620c08d0a6b7c18482a65e178cd1d2982f712157d83cbfb52` |
| 12 | `src/logsentinel/gui/assets/icons/play.svg` | SVG 24×24; 198; `4d8390b96e111470d6d397540610b6209cd1f16df089fdbd802f4bb70cc946cd` | `licenses/third-party/asset-remediation/original-proposals/icons/play.svg` | 328; `02f0cf55af4200f47e4ba6614b8c5ee82d502cc1e8e623fa1c3a2298ecedd5cc` |
| 13 | `src/logsentinel/gui/assets/icons/reports.svg` | SVG 24×24; 322; `65eeb087b42d52b53721b9202be45487504ca3d253ae92b07ef0154cb7e841f4` | `licenses/third-party/asset-remediation/original-proposals/icons/reports.svg` | 370; `91d4372092e09a0020903246554a0c373c21305d9a55541e47938f4070780a1e` |
| 14 | `src/logsentinel/gui/assets/icons/search.svg` | SVG 24×24; 226; `5c916fe41833f69421452f6198eb24ce7463b8875c38b25c391f75d1a6ce7b63` | `licenses/third-party/asset-remediation/original-proposals/icons/search.svg` | 392; `0d472c24a97ea1544a153dd9adae45ef7d21224dc37bbf97a873eccd4315aae7` |
| 15 | `src/logsentinel/gui/assets/icons/settings.svg` | SVG 24×24; 778; `df60f7fce3362af3958dc54e389389f399ad346b9519f2ffe25734c842d9199b` | `licenses/third-party/asset-remediation/original-proposals/icons/settings.svg` | 375; `d32fe6fec48ab0275b73b03951ced12eb466bab98ddbf3957d2d5ee2c31e5d50` |
| 16 | `src/logsentinel/gui/assets/icons/shield_check.svg` | SVG 24×24; 352; `4b67896a203ea68f791703a20533765a66f53ccbb84fe6292293604b402a1244` | `licenses/third-party/asset-remediation/original-proposals/icons/shield_check.svg` | 335; `adea7228f573f1e5023af3ffc3045769d81410b71adda6f58fe6e310dc6a6001` |
| 17 | `src/logsentinel/gui/assets/icons/stop.svg` | SVG 24×24; 220; `07817d961981a2b1a7206436ad5c49c571b9c07d670e87945bef9216d9d22ffb` | `licenses/third-party/asset-remediation/original-proposals/icons/stop.svg` | 305; `9eef1f945bcc0cd942b6ee9905ec2b94eb3b0c35e74a80ba7479609b264edbe2` |
| 18 | `src/logsentinel/gui/assets/icons/trash.svg` | SVG 24×24; 335; `56da0d4c3ba1b515cb1eceb530a9c99d9353b8e3335256e2b80f153bf4c7edaf` | `licenses/third-party/asset-remediation/original-proposals/icons/trash.svg` | 376; `ff2f35d8515f6f2089fddda9ad7bcb235a8e932b3eb7e77627dd2ad7fe96a7b4` |
| 19 | `src/logsentinel/gui/assets/logsentinel.ico` | ICO 16×16, 24×24, 32×32, 48×48, 64×64, 128×128, 256×256; 28,829; `000dbee98ff64b8c31074c0e346c3322f2213f0e6c99d2c84a937821b6e275e6` | `licenses/third-party/asset-remediation/original-proposals/logsentinel.ico` | 33,417; `6f9948530dfbc3ba8c596d9975ce2a00ff638e54a6afb484b1f29dc6919fe472` |

The ICO frame list above is also its proposed frame list: 16×16, 24×24, 32×32, 48×48, 64×64, 128×128 and 256×256, each 32-bit PNG-backed. Proposal file SHA-256 values were recomputed after final visual refinements; the inventory table reflects that final snapshot.

## 4. GUI usage inspected

- `src/logsentinel/gui/icons.py` reads `assets/icons/{name}.svg`, substitutes `CURRENT_COLOR`, and renders brand mark/logo/sidebar after substituting theme tokens. Its embedded path fallbacks are used if an asset cannot be read.
- `src/logsentinel/gui/icon_widgets.py` defines theme-aware `ThemeIconLabel`, `ThemeIconButton`, `BrandMarkLabel` and `BrandWordmarkLabel` wrappers. Navigation specs in `main_window.py` use overview, detections, log-explorer, reports and settings names. Other direct consumers include `file_plus` in `panels.py`, search in `views.py`, play/stop in `main_window.py`, and download in `reports_view.py`. Additional filenames are available through the common named-icon loader and package asset glob; not every icon has a direct static call.
- `app.py` and `main_window.py` create the runtime window icon through `brand_icon()`, which renders the brand-mark SVG at 16, 24, 32, 48, 64, 128 and 256 px. The live ICO is used by the two PyInstaller spec files as the executable icon, not as the runtime theme icon.
- `tests/test_gui_themes.py` checks the expected asset names and theme/render behavior. Its assertions and the GUI/package recipes were left unchanged. The proposed files are not in application asset roots.

## 5. Validation and preservation

### Passed

- All 18 proposed SVGs parse as XML, have the expected root/viewBox, contain no script, `foreignObject`, embedded image, hyperlink or remote URL, and were accepted by Qt `QSvgRenderer` after preview theme tokens were filled.
- The HTML contact sheet rendered at 1360 px width with zero browser console messages; it visually displays all 18 SVGs and the largest proposed ICO frame.
- The proposed ICO directory has seven entries with valid PNG signatures, decodable frame images, matching declared dimensions, and 32-bit entries.
- Each original path’s byte length and SHA-256 still matches the provenance report’s recorded working-tree inventory. Original SVGs and ICO were not overwritten.
- A Git search found no `original-proposals` references in tracked source, tests or packaging. No GUI source, tests, packaging specs, dependency declarations, or live asset references were changed for this task.
- No files were staged or committed. Existing changes in `.gitignore`, `README.md`, `docs/USAGE.md`, `packaging/LogSentinel-GUI-Onedir.spec`, existing untracked documentation/licensing work, and ignored release artifacts were preserved. `git diff --check` and `git diff --cached --check` passed (Git only reported existing line-ending warnings for the four modified tracked files).

### Not performed / limitations

- No application test suite, GUI integration test, package build, installer build, release-artifact rebuild, browser/device font matrix, or light-theme usability test was run for these unintegrated proposals.
- The preview is a design review, not an accessibility evaluation, comprehensive cross-platform rendering review, legal uniqueness search, source-history finding, or rights determination.
- No replacement was integrated or approved. There was no modification to PyInstaller asset enumeration or the two GUI packaging recipes.
- Preparing alternatives does not resolve who created or owns the original 19 assets and does not clear the remaining original GUI assets (including the separate four Lucide-source proposals) for source publication. Nor does it close Qt/PySide, runtime, notices, corresponding-source/relink, compatibility or other Windows binary distribution gates.

## 6. Disposition and follow-up gates

Keep all proposals isolated and all live GUI assets on **HOLD** until an authorized integration decision is made. Before integration, review the appearance and light/dark contrast at actual widget sizes; verify the horizontal/sidebar wordmarks against real layout constraints; render ICO sizes in a Windows shell/taskbar context; run GUI asset/theme tests and both controlled package recipes; and review all changes together with the relevant provenance and notice records. Any integration must preserve the existing fallback behavior and tests and must not imply that historical asset origins have been discovered.

No staging, commit, publication, or binary release authorization is granted by this report.
