# LogSentinel Phase 1 — Lucide Proposal Integration Eligibility Review

**Mode:** read-only review; the only file created is this requested report. The four corrected SVGs remain isolated and are **not integrated**. This review does not establish the historical source or ownership of the original GUI artwork, make a legal determination, approve publication, or clear a Windows binary.

## Decision summary

| Decision | Count | Meaning for this review |
|---|---:|---|
| **ELIGIBLE** | 0 | Complete source, rights/notice, corrected-file record, and technical basis are established sufficiently to recommend integration. |
| **NOT ELIGIBLE** | 0 | A known unresolved technical or rights defect affirmatively prevents integration. |
| **INSUFFICIENT EVIDENCE** | 4 | The technical corrections are evidenced, but one or more material provenance/license/notice records are incomplete or conflicting, so integration eligibility cannot be concluded. |
| **Total** | **4** | No proposal is cleared for integration. |

All four are **INSUFFICIENT EVIDENCE**—not a conclusion that the assets are impermissible. The remaining blocker is unresolved version-specific Feather notice scope: the pinned license snapshot has only a general Feather-derived-portions statement, while a later Lucide license lists `check`, `download`, and `x` but omits `folder-open`. The stale proposal filename/hash fields in the replacement report and staging `ATTRIBUTION.md` have since been reconciled to distinguish corrected proposal bytes from restored pinned-source bytes; this metadata correction does not resolve historical per-icon license applicability. The corrected color rendering and folder target-name issues are addressed by the correction report.

## 1. Scope and evidence reviewed

Reviewed the requested records:

1. `docs/PHASE-1-LUCIDE-ASSET-REPLACEMENT-REPORT.md`
2. `docs/PHASE-1-LUCIDE-ASSET-CORRECTION-REPORT.md`
3. `docs/PHASE-1-GUI-ASSET-PROVENANCE-REPORT.md`
4. `docs/PHASE-1-GUI-ASSET-PUBLICATION-RESOLUTION.md`
5. `licenses/third-party/asset-remediation/proposed-lucide-replacements/ATTRIBUTION.md` and the three bundled Lucide/Feather license files
6. `check.svg`, `download.svg`, `folder_open.svg`, and `x.svg` in `licenses/third-party/asset-remediation/proposed-lucide-replacements/`

The pinned upstream commits and paths, original source-byte digests, Git blob SHA-1 values, and path-geometry comparisons are documented in the original replacement report. The correction report documents the single `currentColor` → `CURRENT_COLOR` change, corrected destination basename for `folder-open`, corrected SHA-256 values, restoration checks against the prior source-byte SHA-256/Git blob SHA-1, and tests through the actual GUI color-token transformation and Qt renderer. Those are repository records reviewed here, not a new upstream retrieval or independent legal/source-history investigation.

## 2. Per-proposal decisions

### `check.svg` → `src/logsentinel/gui/assets/icons/check.svg`

**Decision: INSUFFICIENT EVIDENCE**

- **Exact source/revision:** Documented as Lucide `icons/check.svg` at commit `66cfe527b3d19ce03cdf3de704dfbd80d796ec0f`. The replacement report provides the pinned source URL, Git blob SHA-1, source-byte SHA-256/size, and target mapping. The correction report says restoring the single color-token change reproduces that source SHA-256 and Git blob SHA-1.
- **License:** Lucide ISC terms are present at the pinned source commits. The pinned 880-byte Lucide license also says portions are held by Cole Bemis as part of Feather (MIT), but it does not enumerate which icons are Feather-derived or include the full separate Feather MIT text. A later Lucide license snapshot lists `check` as Feather-derived. This supports a concrete possible ISC + Feather MIT notice route, but the reports do not establish that later per-icon classification as the exact scope at the pinned source revision.
- **Attribution/notice:** The reconciled `ATTRIBUTION.md` now records the corrected proposal hash and the pinned-source hash separately, including the `CURRENT_COLOR` token substitution. The staging area contains Lucide ISC and Feather MIT reference texts. However, version-specific per-icon Feather applicability and the required notice placement remain unconfirmed; see `docs/PHASE-1-LUCIDE-LICENCE-ATTRIBUTION-RECONCILIATION.md`.
- **Corrected hash/name:** Corrected proposal is `check.svg`, exact target basename. SHA-256: `ce862ced28c4f3163e6258b83a8a7231166149242e094a460449fbd5230c48cc` (240 bytes). The replacement report and staging attribution record now identify the corrected hash separately from the pinned raw-source hash.
- **Technical blockers:** Correction report documents that `CURRENT_COLOR` is processed by the GUI loader and validates two requested colors through `icons.icon_svg()` and Qt rendering. It also confirms path geometry restoration. No known token or filename blocker remains. Full live-GUI integration, packaging, and regression tests have not been run.
- **Remaining blocker:** Confirm and document the Feather scope/notice basis applicable to this pinned source and update the authoritative attribution record to the corrected file/hash and modification.

### `download.svg` → `src/logsentinel/gui/assets/icons/download.svg`

**Decision: INSUFFICIENT EVIDENCE**

- **Exact source/revision:** Documented as Lucide `icons/download.svg` at commit `09841dd72126a65b39f7c6ebd38dc3664299d756`, including pinned URL, Git blob SHA-1, source-byte hash/size, and intended target. Correction report records restoration to the pinned bytes and confirms path geometry.
- **License:** The pinned Lucide source license provides ISC terms and the general Feather-derived portions statement. A later Lucide license snapshot lists `download` among Feather-derived icons; the full Feather MIT v4.29.1 text is included as a reference. The exact Feather lineage/version and notice scope at this pinned Lucide source commit are not established by the records, so a definitive per-file ISC/MIT notice selection is not evidenced.
- **Attribution/notice:** The reconciled `ATTRIBUTION.md` now records the corrected proposal hash and `CURRENT_COLOR` transformation separately from the pinned source identity. The license bundle contains Lucide ISC and Feather MIT reference texts; per-icon Feather applicability at this pinned revision and notice placement remain unconfirmed.
- **Corrected hash/name:** Corrected proposal is `download.svg`, exact target basename. SHA-256: `6f70003d0f4ade05e8bb586a4d89a551058d5682b3141e9452d2ef593713442e` (319 bytes). The replacement report and staging attribution record now identify the corrected hash separately from the pinned raw-source hash.
- **Technical blockers:** The correction report documents loader-token substitution, two color renders, Qt parsing/rendering, and geometry verification. No known color or filename defect remains. Integration/build tests remain unperformed.
- **Remaining blocker:** Establish version-specific Feather notice scope, and update the per-file attribution/notice record to describe the corrected file and its source modification.

### `folder_open.svg` → `src/logsentinel/gui/assets/icons/folder_open.svg`

**Decision: INSUFFICIENT EVIDENCE**

- **Exact source/revision:** Documented as Lucide `icons/folder-open.svg` at commit `81e44bdc40d21d64881a858c188f391bca75eb0f`. The original replacement report identifies the upstream hyphenated source path and target underscore path; correction report documents the corrected target-relative proposal basename. Restoring the color token yields the recorded source SHA-256/Git blob SHA-1, with matching path geometry.
- **License:** Lucide ISC text is included and the current Lucide snapshot does not list `folder-open` in its Feather-derived list. The pinned historical license still contains a general statement that portions are Feather-derived without identifying those portions. This points toward Lucide ISC but does not establish, from the pinned license text alone, that this particular icon is outside the Feather portion at that revision. Do not treat the newer list as historical evidence without an explicit basis.
- **Attribution/notice:** The reconciled `ATTRIBUTION.md` identifies `folder_open.svg` as the corrected proposal filename, records the target mapping and corrected hash, and preserves the upstream source path `icons/folder-open.svg` separately. The per-icon license-scope gap remains unresolved.
- **Corrected hash/name:** Corrected proposal is `folder_open.svg`, matching the exact GUI target basename; `folder-open.svg` is absent. SHA-256: `b6d39a234cab41b365fc696f3fff3f38525cef6120d952e5651762e64119b09c` (402 bytes). The replacement report and staging attribution record now distinguish corrected proposal filename/hash from upstream source path/hash.
- **Technical blockers:** Correction report documents `CURRENT_COLOR` processing and successful two-color Qt renders. The path lookup mismatch identified in the prior review is corrected in the proposal directory. No known token or destination-name defect remains; integration packaging/tests remain unrun.
- **Remaining blocker:** Confirm the exact license/Feather scope at this pinned source and reconcile the stale attribution path/hash with the corrected destination file.

### `x.svg` → `src/logsentinel/gui/assets/icons/x.svg`

**Decision: INSUFFICIENT EVIDENCE**

- **Exact source/revision:** Documented as Lucide `icons/x.svg` at commit `70be55b78f9043bd8c37200164370a8e8d02d38b`, with pinned URL, blob SHA-1, source-byte SHA-256/size, and mapped target. Correction report validates restored source-byte and blob identities and unchanged path geometry.
- **License:** Pinned Lucide license supplies ISC terms and the general statement concerning Feather portions. The newer Lucide license snapshot lists `x` as Feather-derived and supplies a Feather MIT text; that newer classification does not establish historical per-icon notice scope at the pinned source revision. Exact version-specific license applicability remains unresolved.
- **Attribution/notice:** The reconciled attribution record now describes the one-token change and gives corrected proposal and pinned source hashes separately. The pinned revision’s per-icon Feather scope and notice placement remain unresolved.
- **Corrected hash/name:** Corrected proposal is `x.svg`, matching the target basename. SHA-256: `eebd33f4843cc6a8bccfee89ff350cfcaeca9fbbe5076823742c32896e54b49a` (261 bytes). The replacement report and staging attribution record now identify the corrected proposal hash separately from the pinned source-byte hash.
- **Technical blockers:** Correction report documents correct loader color substitution and valid Qt rendering at two colors; path geometry restores to pinned source. No known color or filename defect remains. End-to-end GUI/package checks have not been performed.
- **Remaining blocker:** Resolve the pinned-version Feather MIT notice basis and refresh the authoritative attribution/notice record for the modified proposal bytes.

## 3. Cross-cutting findings and limitations

### Source and historical provenance

The pinned Lucide source path/commit and source blob/hash evidence are specific for all four proposals. The corrected report further proves that each corrected file restores byte-for-byte to the reported raw upstream file when replacing only `CURRENT_COLOR` back to `currentColor`; the folder basename change does not affect contents. This is strong evidence for the provenance of the **proposed replacements**. It does not prove that the existing LogSentinel originals were historically copied from Lucide, establish who authored those originals, or convey rights in them. The GUI provenance and publication-resolution reports explicitly leave original historical source/rights unresolved and classify the four as HOLD for publication.

### License and notice basis

The bundle includes the pinned Lucide ISC license text, a later Lucide snapshot with a per-icon Feather-derived list, and the complete Feather v4.29.1 MIT text. Availability and hashes of texts are not the same as a completed, version-specific notice decision. For `check`, `download`, and `x`, later Lucide evidence says Feather-derived; the reviewed pinned license does not identify those icons individually. For `folder-open`, the later list omits Feather, while the pinned license gives only a general Feather-derived portions statement. The reports explicitly warn not to conflate current and historical license texts. Therefore the applicable full notices for these exact pinned SVGs are not unambiguously assigned per item in the integration records.

### Metadata reconciliation status

The replacement report and staging `ATTRIBUTION.md` were reconciled in the documentation-only follow-up `docs/PHASE-1-LUCIDE-LICENCE-ATTRIBUTION-RECONCILIATION.md`. They now distinguish pinned source paths/commits, source-byte SHA-256/Git blob SHA-1, corrected proposal filenames, and corrected proposal hashes. `folder-open` remains the Lucide upstream icon/path name, while `folder_open.svg` is the local proposal basename. The eligibility review originally identified stale metadata; that filename/hash inconsistency is no longer a blocker. This reconciliation does not establish historical per-icon Feather scope or settle notice placement.

### Technical status

No remaining color-token or folder-target-filename defect is reported after Task 3.10.4, and its recorded isolated loader/Qt checks support that correction. The current review did not rerun those tests and did not copy proposals, run the full test suite, integrate into the live asset tree, execute GUI behavior tests, or build either packaging recipe. Therefore end-to-end integration behavior is not newly proven here. No technical blocker is known from the materials examined, but integration test gates remain open.

## 4. Preservation verification

The pre-review state showed existing tracked modifications in `.gitignore`, `README.md`, `docs/USAGE.md`, and `packaging/LogSentinel-GUI-Onedir.spec`; existing untracked Phase 1 documents and `licenses/` work; and no staged paths. This review initially created only the eligibility report. The subsequent documentation-only reconciliation changed the Lucide replacement report and staging `ATTRIBUTION.md`, and created `docs/PHASE-1-LUCIDE-LICENCE-ATTRIBUTION-RECONCILIATION.md`. No proposal SVG, active GUI asset, application source, test, packaging file, or release artifact was changed.

Pre-review corrected proposal hashes and byte sizes:

| File | Bytes | SHA-256 |
|---|---:|---|
| `check.svg` | 240 | `ce862ced28c4f3163e6258b83a8a7231166149242e094a460449fbd5230c48cc` |
| `download.svg` | 319 | `6f70003d0f4ade05e8bb586a4d89a551058d5682b3141e9452d2ef593713442e` |
| `folder_open.svg` | 402 | `b6d39a234cab41b365fc696f3fff3f38525cef6120d952e5651762e64119b09c` |
| `x.svg` | 261 | `eebd33f4843cc6a8bccfee89ff350cfcaeca9fbbe5076823742c32896e54b49a` |

License bundle SHA-256 values before this report: pinned Lucide `1e7290b35280a048667bbf0ebabac1c7fd52a75300e8b2946ac165715997f2bc`; later Lucide snapshot `b495047bd93a9b06913511076f504daba17d5bbeb3e0650f3bb53a4220329c57`; Feather MIT v4.29.1 `308028e93fcf84972523cdf6e616f73168546b4953895f516d01287f16fe7bee`; attribution file `25006276e56bf4c1389be653cfe1a8e9b761d0f9bdce8995e167409ef20ceda2`.

After the reconciliation, verify and report that the four proposal hashes remain exactly those above, the pre-existing worktree/index changes remain preserved, no paths are staged, and the release artifacts remain present. No staging, commit, push, or publication is authorized. The Windows EXE/ZIP stay **HOLD — NOT CLEARED FOR DISTRIBUTION**.

No historical ownership of original artwork is asserted. This report does not elect a license, authorize integration or publication, or clear the Windows distribution hold.
