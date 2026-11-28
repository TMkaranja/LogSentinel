# LogSentinel Phase 1 — Lucide Licence and Attribution Reconciliation

**Status:** documentation-only reconciliation of four isolated corrected Lucide icon proposals. No proposal has been integrated. The four original GUI artwork files remain untouched; this report does not infer their historical source or ownership from geometry, hashes, or technical similarity. It makes no legal determination, publication authorization, or Windows release clearance.

## Scope and sources reviewed

This reconciliation covers the exact upstream Lucide proposals mapped to the existing GUI targets:

| Icon | Pinned Lucide source path and revision | Existing target (unchanged) | Isolated corrected proposal |
|---|---|---|---|
| `check` | [`icons/check.svg`, `66cfe527b3d19ce03cdf3de704dfbd80d796ec0f`](https://github.com/lucide-icons/lucide/blob/66cfe527b3d19ce03cdf3de704dfbd80d796ec0f/icons/check.svg) | `src/logsentinel/gui/assets/icons/check.svg` | `licenses/third-party/asset-remediation/proposed-lucide-replacements/check.svg` |
| `download` | [`icons/download.svg`, `09841dd72126a65b39f7c6ebd38dc3664299d756`](https://github.com/lucide-icons/lucide/blob/09841dd72126a65b39f7c6ebd38dc3664299d756/icons/download.svg) | `src/logsentinel/gui/assets/icons/download.svg` | `licenses/third-party/asset-remediation/proposed-lucide-replacements/download.svg` |
| `folder-open` | [`icons/folder-open.svg`, `81e44bdc40d21d64881a858c188f391bca75eb0f`](https://github.com/lucide-icons/lucide/blob/81e44bdc40d21d64881a858c188f391bca75eb0f/icons/folder-open.svg) | `src/logsentinel/gui/assets/icons/folder_open.svg` | `licenses/third-party/asset-remediation/proposed-lucide-replacements/folder_open.svg` |
| `x` | [`icons/x.svg`, `70be55b78f9043bd8c37200164370a8e8d02d38b`](https://github.com/lucide-icons/lucide/blob/70be55b78f9043bd8c37200164370a8e8d02d38b/icons/x.svg) | `src/logsentinel/gui/assets/icons/x.svg` | `licenses/third-party/asset-remediation/proposed-lucide-replacements/x.svg` |

Reviewed the three bundled license texts, staging attribution record, pinned source metadata, correction report, and eligibility review. External primary-source references checked include the [Lucide merged license-text change #3530](https://github.com/lucide-icons/lucide/pull/3530), which merged on 2025-08-09 as commit `867c0581af76d38ce1da2940fa5d5e182bf1883f`, and the later official [Lucide license snapshot at commit `4bf621064bed45d114ba31435b85760513830d1c`](https://github.com/lucide-icons/lucide/blob/4bf621064bed45d114ba31435b85760513830d1c/LICENSE). PR #3530 describes adding the full Feather license copied from Feather's license; that history establishes when the separate text was added to Lucide, not the per-icon scope at the four older pinned commits.

## Licence evidence and applicability

### Evidence actually in hand

1. `LICENSE-LUCIDE-AT-PINNED-SOURCE-COMMITS.txt` is the common 880-byte Lucide license text recorded at the four pinned commits (SHA-256 `1e7290b35280a048667bbf0ebabac1c7fd52a75300e8b2946ac165715997f2bc`). It contains the ISC license and the general statement that portions of Lucide are held by Cole Bemis 2013–2022 as part of Feather under MIT. It does **not** enumerate icon names or include the full separate Feather MIT text.
2. `LICENSE-LUCIDE-CURRENT-SNAPSHOT.txt` is the official later Lucide license at commit `4bf621064bed45d114ba31435b85760513830d1c` (3,208 bytes; SHA-256 `b495047bd93a9b06913511076f504daba17d5bbeb3e0650f3bb53a4220329c57`). Its Feather-derived list includes `check`, `download`, and `x`, and omits `folder-open`. Its copyright years and classification belong to that later snapshot; they are not silently applied as proof of historical per-icon scope at the four pinned revisions.
3. `LICENSE-FEATHER-MIT-v4.29.1.txt` is the official Feather v4.29.1 MIT license (1,082 bytes; SHA-256 `308028e93fcf84972523cdf6e616f73168546b4953895f516d01287f16fe7bee`). It is available as reference notice text. No evidence here establishes v4.29.1 as the exact Feather source version for any of the four pinned Lucide paths.
4. Lucide's [#3530 merged change](https://github.com/lucide-icons/lucide/pull/3530) documents addition of the full Feather license text on 2025-08-09. The change does not by itself prove that every icon subject to the old general Feather statement was identified in exactly the later list, nor does it retrospectively settle the four pinned revisions' per-icon classification.

### Per-proposal coverage assessment

| Proposal | Pinned Lucide ISC text | Individual Feather evidence | Reconciliation status |
|---|---|---|---|
| `check.svg` | Present in the recorded pinned license snapshot. | Later Lucide snapshot lists `check`; pinned license contains no per-icon list. | Lucide ISC notice text is identified; whether Feather MIT attribution applies to this pinned icon and what notice must accompany distribution remains unconfirmed. |
| `download.svg` | Present in the recorded pinned license snapshot. | Later Lucide snapshot lists `download`; pinned license contains no per-icon list. | Lucide ISC notice text is identified; whether Feather MIT attribution applies to this pinned icon and what notice must accompany distribution remains unconfirmed. |
| `folder_open.svg` (`folder-open`) | Present in the recorded pinned license snapshot. | Later snapshot omits `folder-open`; pinned license still has a general Feather-derived-portions statement and no per-icon list. | Absence from the later list is not proof of historical non-derivation at the pinned revision. Individual Feather scope and distribution notice handling remain unconfirmed. |
| `x.svg` | Present in the recorded pinned license snapshot. | Later Lucide snapshot lists `x`; pinned license contains no per-icon list. | Lucide ISC notice text is identified; whether Feather MIT attribution applies to this pinned icon and what notice must accompany distribution remains unconfirmed. |

### Practical conclusion, not legal advice

The records support citing the pinned Lucide source, its ISC text, and the existence of a Feather-related MIT component in Lucide's historical license statement. For the later Lucide snapshot, there is positive per-icon Feather attribution for `check`, `download`, and `x`; `folder-open` is not listed there. These facts do not answer the exact Feather-derived scope at the four older pinned commits. The staging directory contains both Lucide and Feather texts, but presence alone does not decide whether both are required for each icon, whether the bundled terms cover the corrected proposal as distributed, or how notices should be placed. An owner/legal reviewer should confirm the pinned-version notice basis before any integration/publication. This is an evidence limitation, not a conclusion that any proposal is impermissible.

## Corrected source-to-proposal and attribution record

The proposal bytes are not described as raw upstream files. The correction report records one SVG-content transformation only: `stroke="currentColor"` became `stroke="CURRENT_COLOR"` to work with the existing GUI loader. `folder-open.svg` was renamed to target basename `folder_open.svg`; its upstream source remains `icons/folder-open.svg`. The source restoration checks replace only the token back and reproduce the pinned source SHA-256 and Git blob SHA-1. They validate proposed-source correspondence only, not the provenance or ownership of the existing GUI art.

| Icon | Corrected proposal bytes / SHA-256 | Restored pinned source SHA-256 | Pinned source Git blob SHA-1 |
|---|---|---|---|
| `check.svg` | 240 / `ce862ced28c4f3163e6258b83a8a7231166149242e094a460449fbd5230c48cc` | `7f33acc9a77a61659531044525fc008edebe215bf4dcf1c789c8674ad3277db0` | `5abe1527434e7b251bde0661f99af96178976d8c` |
| `download.svg` | 319 / `6f70003d0f4ade05e8bb586a4d89a551058d5682b3141e9452d2ef593713442e` | `3daeee13ded5a3afa2198b1bb4e2262d163922f97d96ac6ff9953e8ed4fe039d` | `5c75527bde1fe8259efb72c5b590bedfae28c05e` |
| `folder_open.svg` | 402 / `b6d39a234cab41b365fc696f3fff3f38525cef6120d952e5651762e64119b09c` | `ee57452b40e71df310214091dd9da1941a397c83197b8ff8d7ae66dd4242578b` | `b01f60fcb51848a9b3a7380d4566c4de7534745c` |
| `x.svg` | 261 / `eebd33f4843cc6a8bccfee89ff350cfcaeca9fbbe5076823742c32896e54b49a` | `4a9cdab38fbb96162e7dace28e33f4ca0e49d8963a6162abc3d4691b7d675117` | `e31794349d3eecea1b3ae8e974b68bb8f4becda7` |

The staging `licenses/third-party/asset-remediation/proposed-lucide-replacements/ATTRIBUTION.md` was reconciled to show the corrected proposal filename and SHA-256 separately from the pinned source SHA-256/blob ID, with the loader token change and source-versus-proposal distinction stated. The replacement report was updated to the corrected filename/hash facts and cross-references this reconciliation. These metadata changes describe candidate replacements only. The live GUI originals remain unchanged, and no inference is made that their geometric resemblance establishes historical Lucide origin, ownership, or license.

## Eligibility and unresolved blockers

`docs/PHASE-1-LUCIDE-INTEGRATION-ELIGIBILITY-REVIEW.md` currently records **INSUFFICIENT EVIDENCE for all four proposals** (0 eligible, 0 not eligible, 4 insufficient). Corrected path/hash discrepancies in the staging attribution and replacement report are reconciled by these documentation changes; this does not close the licence-scope evidence gap. Eligibility remains unchanged pending an authoritative determination/documentation of whether the Feather MIT component applies per pinned icon, and the required bundled notice placement. No rights/ownership conclusion about original LogSentinel GUI art is part of that later decision.

## Changed and created documentation

The following documentation/attribution records were edited/created for this reconciliation:

- Modified `docs/PHASE-1-LUCIDE-ASSET-REPLACEMENT-REPORT.md` to distinguish original pinned source bytes from corrected proposal bytes, fix the target basename/current hashes, and cite the unresolved per-icon license scope.
- Modified `licenses/third-party/asset-remediation/proposed-lucide-replacements/ATTRIBUTION.md` to use corrected basenames and hashes and distinguish source identity from modified proposal identity.
- Modified `docs/PHASE-1-LUCIDE-INTEGRATION-ELIGIBILITY-REVIEW.md` to remove stale-metadata blockers while retaining the insufficient-evidence decisions and license-scope blocker.
- Created this reconciliation report.

No SVG, original GUI asset, application source, test, packaging file, license text, release artifact, or eligibility decision was modified. No files were staged, integrated, committed, pushed, or published. The release EXE/ZIP remain on distribution hold.
