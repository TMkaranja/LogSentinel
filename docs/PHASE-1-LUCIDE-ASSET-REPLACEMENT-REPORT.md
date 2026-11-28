# LogSentinel Phase 1 — Lucide Asset Replacement Preparation

**Purpose:** prepare exact, upstream-sourced Lucide SVG alternatives for the four probable matches identified in the GUI asset publication resolution and provenance reports.

**Status:** proposal staging only. Nothing here replaces or clears the existing GUI artwork, proves how the original files were created, or authorizes integration or publication. The original LogSentinel SVGs remain unchanged in `src/logsentinel/gui/assets/icons/`. The four proposed SVGs are isolated in `licenses/third-party/asset-remediation/proposed-lucide-replacements/` and are not referenced by GUI code, tests, or packaging specifications. The Windows GUI EXE and ZIP remain **HOLD — NOT CLEARED FOR DISTRIBUTION**.

## 1. Scope and source selection

The four candidate mappings are those recorded in `docs/PHASE-1-GUI-ASSET-PUBLICATION-RESOLUTION.md`. The corrected proposal filenames/hashes and license reconciliation in this report supersede the original proposal metadata below where noted; the live GUI originals remain unchanged.

| Lucide icon | Exact pinned upstream path | Existing LogSentinel target (unchanged) | Corrected isolated proposal path | Pinned Lucide source commit |
|---|---|---|---|---|
| `check` | `icons/check.svg` | `src/logsentinel/gui/assets/icons/check.svg` | `licenses/third-party/asset-remediation/proposed-lucide-replacements/check.svg` | `66cfe527b3d19ce03cdf3de704dfbd80d796ec0f` |
| `download` | `icons/download.svg` | `src/logsentinel/gui/assets/icons/download.svg` | `licenses/third-party/asset-remediation/proposed-lucide-replacements/download.svg` | `09841dd72126a65b39f7c6ebd38dc3664299d756` |
| `folder-open` | `icons/folder-open.svg` | `src/logsentinel/gui/assets/icons/folder_open.svg` | `licenses/third-party/asset-remediation/proposed-lucide-replacements/folder_open.svg` | `81e44bdc40d21d64881a858c188f391bca75eb0f` |
| `x` | `icons/x.svg` | `src/logsentinel/gui/assets/icons/x.svg` | `licenses/third-party/asset-remediation/proposed-lucide-replacements/x.svg` | `70be55b78f9043bd8c37200164370a8e8d02d38b` |

These exact upstream revisions were selected because the prior resolution report identified matching Lucide path geometry at these commits. The original downloaded source bytes are not the current proposal bytes: Task 3.10.4 changed only the SVG stroke token from `currentColor` to `CURRENT_COLOR`, which the existing GUI loader replaces, and renamed the folder proposal to the exact target basename `folder_open.svg`. No proposal was copied into the active asset tree. Restoring the token reproduces the pinned source-byte hashes and Git blob SHA-1 values listed below.

## 2. Hashes and comparison results

SHA-256 values below were computed over raw file bytes. Original values match the existing asset inventory in `docs/PHASE-1-GUI-ASSET-PROVENANCE-REPORT.md`. Proposed values identify the staged upstream bytes.

| Icon | Existing GUI target: bytes / SHA-256 | Pinned upstream bytes / SHA-256 | Pinned source Git blob SHA-1 | Corrected proposal path: bytes / SHA-256 |
|---|---|---|---|---|
| `check` | 196 / `0f68dcfa6748c435768b27317f89689bc752a27bd63b797737972340ec283c39` | 239 / `7f33acc9a77a61659531044525fc008edebe215bf4dcf1c789c8674ad3277db0` | `5abe1527434e7b251bde0661f99af96178976d8c` | `check.svg`: 240 / `ce862ced28c4f3163e6258b83a8a7231166149242e094a460449fbd5230c48cc` |
| `download` | 267 / `fb67a5ce7e49bce1df96910725e71b47820ac5046e91a6ecf85b95b8a0e2da77` | 318 / `3daeee13ded5a3afa2198b1bb4e2262d163922f97d96ac6ff9953e8ed4fe039d` | `5c75527bde1fe8259efb72c5b590bedfae28c05e` | `download.svg`: 319 / `6f70003d0f4ade05e8bb586a4d89a551058d5682b3141e9452d2ef593713442e` |
| `folder-open` | 358 / `c7c425bb348b1af16c697be291b12c9e05e87400487a2f8caa017b0f8329b7d0` | 401 / `ee57452b40e71df310214091dd9da1941a397c83197b8ff8d7ae66dd4242578b` | `b01f60fcb51848a9b3a7380d4566c4de7534745c` | `folder_open.svg`: 402 / `b6d39a234cab41b365fc696f3fff3f38525cef6120d952e5651762e64119b09c` |
| `x` | 213 / `8257c7412a3231067454c75cea0d56530ca400c29051fa7a840c8df5790a4edf` | 260 / `4a9cdab38fbb96162e7dace28e33f4ca0e49d8963a6162abc3d4691b7d675117` | `e31794349d3eecea1b3ae8e974b68bb8f4becda7` | `x.svg`: 261 / `eebd33f4843cc6a8bccfee89ff350cfcaeca9fbbe5076823742c32896e54b49a` |

All four corrected proposal documents parse as SVG/XML. Each corrected proposal retains the pinned source path-data multiset exactly; `download` is compared as a multiset because the existing GUI original orders path elements differently from the upstream source. The current proposal changes the pinned SVG’s `stroke="currentColor"` to `stroke="CURRENT_COLOR"` and otherwise preserves markup/geometry and upstream `stroke-width="2"`. The current proposal SHA-256 is distinct from the pinned source-byte SHA-256; source-byte restoration and Git blob SHA-1 verification are recorded in `docs/PHASE-1-LUCIDE-ASSET-CORRECTION-REPORT.md`. Loader-driven Qt render checks for two explicit colors are recorded there as well. The upstream width 2 differs from the existing GUI originals’ 1.8 and remains a visible integration consideration.

### Upstream references

- [`check.svg` at Lucide commit `66cfe527b3d19ce03cdf3de704dfbd80d796ec0f`](https://github.com/lucide-icons/lucide/blob/66cfe527b3d19ce03cdf3de704dfbd80d796ec0f/icons/check.svg)
- [`download.svg` at Lucide commit `09841dd72126a65b39f7c6ebd38dc3664299d756`](https://github.com/lucide-icons/lucide/blob/09841dd72126a65b39f7c6ebd38dc3664299d756/icons/download.svg)
- [`folder-open.svg` at Lucide commit `81e44bdc40d21d64881a858c188f391bca75eb0f`](https://github.com/lucide-icons/lucide/blob/81e44bdc40d21d64881a858c188f391bca75eb0f/icons/folder-open.svg)
- [`x.svg` at Lucide commit `70be55b78f9043bd8c37200164370a8e8d02d38b`](https://github.com/lucide-icons/lucide/blob/70be55b78f9043bd8c37200164370a8e8d02d38b/icons/x.svg)

Each GitHub Contents API response agreed with the requested path, downloaded file size, and Git blob SHA-1 in the table. SHA-256 was computed separately after download. These checks establish that the proposal contains the bytes returned for the pinned upstream paths; they do not establish the original LogSentinel files’ historical source.

## 3. License and attribution evidence

The staging directory includes a proposed attribution record and the complete source license texts used for review:

- `ATTRIBUTION.md` records each corrected proposal filename/hash separately from its pinned upstream source-byte SHA-256 and Git blob SHA-1, with the original GUI target treated as a mapping only. It marks the proposals **not integrated** and disclaims historical-origin, publication, and binary-clearance conclusions. Per-icon Feather scope limits are documented there and in the reconciliation report.
- `LICENSE-LUCIDE-AT-PINNED-SOURCE-COMMITS.txt` is byte-identical at all four pinned source commits. Size: 880 bytes. SHA-256: `1e7290b35280a048667bbf0ebabac1c7fd52a75300e8b2946ac165715997f2bc`. It contains Lucide ISC terms and the then-current general statement that portions are held by Cole Bemis 2013–2022 as part of Feather under MIT. This historical text has no separate per-icon Feather-derived list or full MIT permission text.
- `LICENSE-LUCIDE-CURRENT-SNAPSHOT.txt` is the official Lucide license at commit `4bf621064bed45d114ba31435b85760513830d1c`. Size: 3,208 bytes. SHA-256: `b495047bd93a9b06913511076f504daba17d5bbeb3e0650f3bb53a4220329c57`. This snapshot expressly lists `check`, `download`, and `x` as Feather-derived and contains ISC plus Feather MIT terms. It does not list `folder-open` among those Feather-derived icons. This is current upstream scope evidence, not proof that LogSentinel obtained the files from that revision.
- `LICENSE-FEATHER-MIT-v4.29.1.txt` is the official Feather v4.29.1 MIT license text. Size: 1,082 bytes. SHA-256: `308028e93fcf84972523cdf6e616f73168546b4953895f516d01287f16fe7bee`. It is included as a full MIT reference for the identified Feather lineage, not as a claim that v4.29.1 was the source version for the local originals.

The applicable upstream references are [Lucide’s current pinned license](https://github.com/lucide-icons/lucide/blob/4bf621064bed45d114ba31435b85760513830d1c/LICENSE) and [Feather v4.29.1’s license](https://github.com/feathericons/feather/blob/v4.29.1/LICENSE). Before integrating these assets or publishing notices, confirm the chosen source/version and notice scope with the asset author/project owner and any required legal reviewer. The included license texts are review material, not a legal determination or license election for the original files.

## 4. Proposed files created

All files are under `licenses/third-party/asset-remediation/proposed-lucide-replacements/`:

```text
ATTRIBUTION.md
check.svg
download.svg
folder_open.svg
x.svg
LICENSE-LUCIDE-AT-PINNED-SOURCE-COMMITS.txt
LICENSE-LUCIDE-CURRENT-SNAPSHOT.txt
LICENSE-FEATHER-MIT-v4.29.1.txt
```

No files were written under the active `src/logsentinel/gui/assets/` tree. No source, test, packaging spec, GUI reference, dependency, or release artifact was changed.

## 5. Verification and preservation

- Confirmed the four original SVG sizes and SHA-256 values still match the prior 23-asset provenance inventory.
- Confirmed the four pinned source URLs/commits, source-byte SHA-256 and Git blob SHA-1 through the source-restoration verification recorded in the correction report; the corrected current proposal files have distinct verified SHA-256 values, parse as XML, retain the expected geometry, use the GUI loader’s `CURRENT_COLOR` token, and use the target basename `folder_open.svg`.
- Confirmed the bundled pinned Lucide license text is the recorded common 880-byte snapshot and reviewed the later official Lucide license’s Feather-derived list: `check`, `download`, and `x` are listed; `folder-open` is not. The pinned license text itself contains no per-icon list. This version/scope gap remains unresolved; see `docs/PHASE-1-LUCIDE-LICENCE-ATTRIBUTION-RECONCILIATION.md`.
- Confirmed the original four live assets were not overwritten and no GUI references were changed. No tests or builds were run; proposed files are not integrated and behavior/visual effects have not been evaluated in the application.
- Existing tracked worktree modifications remain `.gitignore`, `README.md`, `docs/USAGE.md`, and `packaging/LogSentinel-GUI-Onedir.spec`. The existing onedir spec diff remains intact. No paths were staged; no commit, push, or publication occurred.
- The ignored `release/` directory and artifacts remain present. EXE SHA-256 remains `d1bda55a555f6e1a6a433eae89d648079f7eeeb869bd9ee3da487cde36d52b04`; ZIP SHA-256 remains `00b13f0dbf7db61a838be8979f92e4ab761d098b44c071d2b365916fb77cf53a`. Both remain **HOLD — NOT CLEARED FOR DISTRIBUTION**.
- Original asset authorship, licensing rights, and historical upstream origin remain unestablished. This replacement preparation does not change the 23-asset publication HOLD or clear the Windows binary.
