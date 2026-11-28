# LogSentinel Phase 1 — GUI Artwork Provenance Evidence Requests

**Purpose:** request and record item-specific evidence needed to evaluate the source-publication status of every live GUI artwork file.

**Disposition:** all 23 files remain **HOLD**. This document does not identify a creator, grant permission, elect a license, make a legal determination, or authorize staging/publication or binary distribution.

**Audit baseline:** `main` at `3229b17f9f0ae4fefc48e58f7a688f9250e1a117`; 23 current files (22 SVGs and one ICO). Refer to the companion asset resolution/provenance reports for observed file sizes, hashes, and technical use. Recompute hashes against the final candidate before any later decision.

## Instructions for the evidence provider

For each entry, provide the actual known facts and attach or identify contemporaneous evidence where available. If an answer is unknown, say **unknown** rather than infer it from a filename, visual style, Git commit author, embedded fallback, or present-day upstream license page. Evidence should identify the specific file/revision and its chain into the current worktree.

For each asset, request as applicable:

1. Original creator(s), employer/commissioner if relevant, and current rightsholder or authorized decision-maker.
2. Original editable source/design file, asset-library record, or other contemporaneous source record; creation date or best-supported date range and revision history.
3. Upstream project, URL, package/version and exact commit/tag if derived from third-party work; identify the precise upstream file/path.
4. Changes made locally: conversion, redraw, path simplification, recoloring, cropping, composition, line/stroke changes, export/rasterization, or other modifications.
5. Fonts/typefaces, templates, stock libraries, component icons, source images, scripts, generators, and design tools used, including relevant versions and licenses.
6. Applicable license or written permission covering modification and public source redistribution; any scope, attribution, notice, territory, or other conditions.
7. Required attribution/notice wording and the exact file/location where it must appear. Do not submit a proposed notice as a completed rights decision.

A response that only says “original,” “Lucide-style,” “made for the project,” or “available online” is not enough by itself to resolve a file unless it identifies the creator/rightsholder, the specific asset, and a sufficient rights basis. Git history and SHA-256 are useful identifiers but are not authorship or permission evidence.

## Per-file requests

### 1. `src/logsentinel/gui/assets/brand/logsentinel-appicon.svg` — HOLD

- **Known from inspection:** 64×64 vector tile/eye motif with theme-color placeholders. It is byte-identical to `brand/logsentinel-mark.svg`; duplication does not establish who created the design.
- **Request:** identify the creator/rightsholder, creation date or range, original editable design/source file and revision history. Identify any source artwork, templates, fonts, libraries, or generator used and their versions/terms. Describe modifications/export steps that produced this SVG. Provide the license or written permission for public source redistribution and exact required attribution/notice. Confirm whether this and `logsentinel-mark.svg` intentionally represent the same design and identify the canonical source.

### 2. `src/logsentinel/gui/assets/brand/logsentinel-logo.svg` — HOLD

- **Known from inspection:** 320×64 eye mark, wordmark and tagline; lettering is encoded as paths, with no live text/font metadata. Path conversion does not identify a typeface or its source.
- **Request:** identify creator/rightsholder separately for the mark, wordmark and tagline if they differ. Provide original design files, date/range and revisions. Identify every font/typeface (family/version/source/license), template, library, stock element, or external artwork used and how text was converted to paths. Describe all modifications. Provide applicable license/written permission for redistribution and required attribution/notice.

### 3. `src/logsentinel/gui/assets/brand/logsentinel-mark.svg` — HOLD

- **Known from inspection:** same bytes as `brand/logsentinel-appicon.svg`; fallback geometry also exists in Python source. Neither copy nor fallback proves origin.
- **Request:** identify the original creator/rightsholder and the original source file/revision and creation date/range; reconcile with the app-icon record. Identify any templates, fonts, libraries, generation tools, source components, modifications, and third-party sources. Provide redistribution permission/license and required attribution/notice, and explain the intended distinct use of the two files if both are retained.

### 4. `src/logsentinel/gui/assets/brand/logsentinel-sidebar.svg` — HOLD

- **Known from inspection:** 240×56 tile with wordmark/tagline encoded as vector paths. Relationship to the logo is visual; the design/source history and typeface are not recorded.
- **Request:** identify creator/rightsholder, source/design file, creation date/range and revision history for the tile, mark and lettering. State whether it was derived from the main logo and document the exact steps and changes. Identify any fonts, templates, libraries, tools or external artwork and terms. Provide the rights basis for public source redistribution and required attribution/notice.

### 5. `src/logsentinel/gui/assets/icons/alert.svg` — HOLD

- **Known from inspection:** 24×24 warning triangle/exclamation. A familiar shape or Lucide-style fallback is not source evidence; no historical origin is established.
- **Request:** identify creator/rightsholder, original vector/design source, date/range and revisions. If from an icon library, provide its URL, exact icon name, package/version and commit/tag and the source file; identify modifications or component composition. Identify tools/templates/libraries and applicable terms. Provide redistribution permission/license and exact attribution/notice requirements.

### 6. `src/logsentinel/gui/assets/icons/check.svg` — HOLD; Lucide geometry match lead

- **Known from inspection:** local path geometry matches Lucide `check` at commit `66cfe527b3d19ce03cdf3de704dfbd80d796ec0f`; local SVG wrapper/stroke styling differs. This is a geometry comparison only. **It does not establish historical copying, authorship, licence scope, or permission.**
- **Request:** confirm or rebut derivation from Lucide, Feather, another source, or independent creation. Identify the actual original creator/rightsholder, exact upstream file/package/version/commit if applicable, creation date/range, original local design file and history, and all modifications. Identify authoring/conversion tools and any templates/libraries. Supply the license/permission applicable to this exact source and version and required ISC/MIT or other attribution/notice wording as applicable. Do not infer historical source solely from the match.

### 7. `src/logsentinel/gui/assets/icons/detections.svg` — HOLD

- **Known from inspection:** shield/exclamation composition; no item-specific author or complete component-source record is present.
- **Request:** identify the creator/rightsholder of the complete composition and each component if sourced separately. Provide editable source/design file, date/range, revision history, upstream URLs and exact versions/commits where relevant, and all local modifications. Identify tools, templates, component libraries and license terms. Provide written redistribution rights and required attribution/notice.

### 8. `src/logsentinel/gui/assets/icons/download.svg` — HOLD; Lucide geometry match lead

- **Known from inspection:** path geometry matches Lucide `download` at commit `09841dd72126a65b39f7c6ebd38dc3664299d756`; local ordering/wrapper/stroke differs. This is a geometry comparison only. **It does not establish historical copying, authorship, licence scope, or permission.**
- **Request:** confirm or rebut Lucide/Feather derivation or independent creation. Identify creator/rightsholder, exact original source file, package/version/commit, creation date/range, original editable file/history and modifications. Identify tools/templates/libraries. Supply the applicable license or written permission for this precise source/version and exact required attribution/notices (including any relevant Lucide and Feather terms). A current license page alone does not establish which terms govern this local file.

### 9. `src/logsentinel/gui/assets/icons/file_plus.svg` — HOLD

- **Known from inspection:** document/plus design. A current semantic comparison did not establish an exact upstream match; that does not prove independent creation.
- **Request:** identify creator/rightsholder, original design/source file, creation date/range and revisions. State whether the document and plus are a local composition or derived from another icon; for each component, identify source URL/file/version/commit and modifications. Identify tools/templates/libraries and terms. Provide redistribution permission/license and required notices.

### 10. `src/logsentinel/gui/assets/icons/file_text.svg` — HOLD

- **Known from inspection:** document with text-line geometry; no exact provenance record is available.
- **Request:** identify creator/rightsholder, source/design file, date/range and revision history. Identify any icon-library source, exact version/commit/file, modifications, fonts/templates/libraries/tools and their terms. Provide the license or written permission for redistribution and exact attribution/notice requirements.

### 11. `src/logsentinel/gui/assets/icons/folder_open.svg` — HOLD; Lucide geometry match lead

- **Known from inspection:** path geometry matches Lucide `folder-open` at commit `81e44bdc40d21d64881a858c188f391bca75eb0f`; wrapper and stroke styling differ. This is a geometry comparison only. **It does not establish historical copying, authorship, licence scope, or permission.**
- **Request:** confirm or rebut Lucide derivation or independent creation. Identify creator/rightsholder, exact upstream file/package/version/commit, creation date/range, original source file/revision and modifications. Identify tools/templates/libraries. Supply the license/permission applicable to the actual source vintage and required notice wording. Do not infer historical source or license from current Lucide terms alone.

### 12. `src/logsentinel/gui/assets/icons/log_explorer.svg` — HOLD

- **Known from inspection:** document/search-lens composition; no exact source or component history is recorded.
- **Request:** identify creator/rightsholder of the complete design and each component, original source/design file, date/range and revisions. If elements derive from icon sets or other artwork, provide exact URLs/files/versions/commits and describe modifications. Identify tools/templates/libraries and terms. Provide redistribution rights and required attribution/notices.

### 13. `src/logsentinel/gui/assets/icons/overview.svg` — HOLD

- **Known from inspection:** viewfinder/corner frame with central circle and diagonal; no item-specific source record is available.
- **Request:** identify creator/rightsholder, source/design file, date/range and revision history; document whether the composition is original or uses components from an icon set/template/library. Identify tools and versions, modifications, applicable license/permission and exact required attribution/notice.

### 14. `src/logsentinel/gui/assets/icons/palette.svg` — HOLD

- **Known from inspection:** palette outline with small circles; no item-specific origin or rights record is available.
- **Request:** identify creator/rightsholder, editable source/design file, creation date/range and revisions. Identify icon-library or stock source, exact version/commit/file, modifications, tools/templates/libraries and terms. Provide redistribution license/permission and exact attribution/notice if required.

### 15. `src/logsentinel/gui/assets/icons/play.svg` — HOLD

- **Known from inspection:** play triangle; common geometry and non-matching current comparisons do not establish source or original authorship.
- **Request:** identify creator/rightsholder, original source/design file, date/range and revision history. If derived, identify upstream project/icon/version/commit and modifications. Identify templates, fonts (if any), libraries and generation/design tools and terms. Provide license/written permission and required notice/attribution.

### 16. `src/logsentinel/gui/assets/icons/reports.svg` — HOLD

- **Known from inspection:** document/chart composition; no complete component mapping or origin record is available.
- **Request:** identify creator/rightsholder for the full design and any separate document/chart components; provide source/design file, creation date/range and revisions. Identify upstream sources and exact versions/commits, modifications, fonts/templates/libraries/tools and terms. Provide public redistribution permission/license and exact notice requirements.

### 17. `src/logsentinel/gui/assets/icons/search.svg` — HOLD

- **Known from inspection:** magnifying glass; its geometry differs from the current Lucide comparison, but this does not identify an alternative source or prove independent creation.
- **Request:** identify creator/rightsholder, source/design file, date/range and revisions. Identify any icon-set source and exact file/version/commit, modifications and tools/templates/libraries. Provide applicable redistribution license/permission and required attribution/notice.

### 18. `src/logsentinel/gui/assets/icons/settings.svg` — HOLD

- **Known from inspection:** gear/circle design; it does not match the current Lucide `settings` path compared in prior review, but its origin remains unknown.
- **Request:** identify creator/rightsholder, original design/source file, date/range and revision history. Identify any upstream icon/library/template, exact version/commit, path components and modifications; identify tools and terms. Provide public source redistribution permission/license and any required notice.

### 19. `src/logsentinel/gui/assets/icons/shield_check.svg` — HOLD

- **Known from inspection:** shield/check composition; no exact upstream source or component-level history is established.
- **Request:** identify the creator/rightsholder for the full composition and each component if assembled from separate sources. Provide design/source file, date/range, revisions, URLs and exact upstream versions/commits, changes, tools/templates/libraries and their terms. Provide applicable permission/license and complete attribution/notice wording.

### 20. `src/logsentinel/gui/assets/icons/stop.svg` — HOLD

- **Known from inspection:** rounded-square stop symbol; simplicity does not establish authorship or rights.
- **Request:** identify creator/rightsholder, source/design file, date/range and revisions; state whether independently drawn, generated, or based on an icon set/template. Identify tools/libraries and versions, modifications, applicable license/permission, and required attribution/notice.

### 21. `src/logsentinel/gui/assets/icons/trash.svg` — HOLD

- **Known from inspection:** trash-can outline; the compared current Lucide/Feather variants differ, which does not prove independent creation.
- **Request:** identify creator/rightsholder, source/design file, date/range and revisions. Identify exact upstream/library source and version/commit if any, all path components and modifications, tools/templates/libraries and terms. Provide rights for source redistribution and exact notice/attribution requirements.

### 22. `src/logsentinel/gui/assets/icons/x.svg` — HOLD; Lucide geometry match lead

- **Known from inspection:** path geometry matches Lucide `x` at commit `70be55b78f9043bd8c37200164370a8e8d02d38b`; local wrapper/stroke styling differs. This is a geometry comparison only. **It does not establish historical copying, authorship, licence scope, or permission.**
- **Request:** confirm or rebut derivation from Lucide, Feather, another source, or independent creation. Identify creator/rightsholder, exact upstream source/file/package/version/commit, creation date/range, original local source and revision history, and modifications. Identify tools/templates/libraries. Supply the license/permission applicable to the actual source version and exact attribution/notices (including relevant Lucide/Feather terms if supported by evidence). A geometric match alone is not permission.

### 23. `src/logsentinel/gui/assets/logsentinel.ico` — HOLD

- **Known from inspection:** Windows ICO with seven PNG-backed sizes (16, 24, 32, 48, 64, 128 and 256 px); no embedded author/source record. A relation to the SVG mark is plausible but not established.
- **Request:** identify creator/rightsholder, original editable source image/design, creation date/range and revision history. Explain the relationship, if any, to `brand/logsentinel-appicon.svg`, `brand/logsentinel-mark.svg`, or another source. Identify the exporter/generator and version, input artwork, tools, templates, fonts, libraries and any third-party terms; describe all rasterization/cropping/retouching per frame. Provide permission/license for every embedded frame and exact required attribution/notice.

## Evidence tracking template

Use one record per file. Attach source files or point to a durable evidence location without exposing unrelated personal or confidential data.

| Field | Response |
|---|---|
| Exact repository path and current SHA-256 | Not supplied — fill after comparing with the requested asset bytes |
| Creator(s) / rightsholder(s) / authorized contact role | Not supplied |
| Creation date or supported date range; revision history | Not supplied |
| Original source/design file or upstream URL + exact revision/version/commit | Not supplied |
| Components, fonts, templates, libraries and tools (with versions) | Not supplied |
| Modifications from source to current file | Not supplied |
| Applicable license or written permission and scope | Not supplied |
| Required attribution, notices, redistribution conditions | Not supplied |
| Evidence reference and verification date | Not supplied |
| Owner disposition | **HOLD — no decision recorded** |

## Status and next action

No per-file external creator/rightsholder evidence is present in this request record. All 23 assets therefore remain **HOLD**. The four Lucide geometry matches are source-investigation leads only and must not be treated as proof of historical copying, authorship, licence scope, or permission. Once evidence is supplied, review each item independently, verify it against the exact current file hash, curate only applicable attribution/license text, and update the separate source-publication proposal after an owner decision. Do not replace, remove, stage, publish, or integrate alternative assets under this request.
