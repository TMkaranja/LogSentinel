# LogSentinel — Current Project Map

**Version:** 0.1.0
**Scope:** current repository working tree, CLI plus optional PySide6 GUI
**Publication status:** proposed source scope only; not owner-approved and **NOT READY TO STAGE**. The GUI artwork and packaging recipes listed below remain on HOLD.
**Binary status:** Windows GUI EXE/ZIP **HOLD — NOT CLEARED FOR DISTRIBUTION**.

This map describes the present tree, not a clearance decision. It distinguishes the implemented source from files whose publication is held pending evidence or review. The project runs offline on user-supplied log files; results are indicators for human review, not proof of malicious intent.

## Repository layout

```text
LogSentinel/
├── .github/workflows/tests.yml   configured Ubuntu + Windows test jobs (Python 3.14)
├── .gitignore                    generated/local outputs and environments
├── LICENSE                       LogSentinel project MIT license
├── PROJECTMAP.md                 this current tree and status map
├── README.md                     overview and CLI/GUI publication/readiness caveats
├── pyproject.toml                CLI package metadata; no declared GUI dependency
├── samples/                      three synthetic demonstration logs
├── src/logsentinel/              CLI, shared analysis pipeline, and optional GUI
├── tests/                        CLI, core, storage, and GUI unit tests
├── packaging/                    GUI entry point and two PyInstaller recipes — HOLD
├── docs/                         product docs, history, and Phase 1 review records
└── licenses/                     96-file uncurated licensing/provenance collection — HOLD
```

The current product source proposal is CLI-plus-GUI. All 23 live GUI artwork resources are on HOLD, so the GUI source set is not currently complete for publication. The 96 files under `licenses/` are all HOLD; they are an uncurated mix of source/rights investigations, candidate notices, alternatives, and licensing materials, not an approved recipient notice bundle. These holds do not imply infringement or permission.

## Application architecture

### CLI and shared analysis core

The CLI is a standard-library Python `src/` package. Its main pipeline is:

```text
CLI arguments/configuration
  → input discovery
  → streaming parsers
  → temporary SQLite staging
  → cross-file deduplication
  → incremental detection
  → text/JSON reporting
```

- `cli.py` orchestrates the command-line interface and exit codes.
- `config.py`, `inputs.py`, `parsers.py`, `events.py`, `exceptions.py`, and `storage.py` provide configuration, discovery, parsing, typed events/errors, and temporary SQLite staging.
- `detectors.py` implements the three current SSH, firewall-port, and HTTP 4xx rules.
- `report.py` renders reports and provides best-effort redaction; this is not a universal secret-protection guarantee.
- `__main__.py` enables `python -m logsentinel`.

### Optional PySide6 GUI

The optional GUI package is in `src/logsentinel/gui/`; the CLI does not import PySide6. `gui/app.py` bootstraps Qt, `main_window.py` coordinates navigation and worker lifecycles, `backend.py` adapts the shared pipeline, and `worker.py` runs analysis in the background. The remaining modules provide application settings, models, input/configuration panels, icon widgets, theme handling, dashboard/detection/log-explorer views, and JSON/HTML report export. `gui/__main__.py` is the source launch entry point (`python -m logsentinel.gui`). PySide6 is not declared in `pyproject.toml`.

The GUI uses SVG/ICO resources under `src/logsentinel/gui/assets/` and includes fallbacks in Python for selected artwork. **All 23 live artwork files remain HOLD** until item-specific source and rights evidence is supplied and reviewed. Fallback parity, visual review, and tests do not establish authorship, licence scope, or permission.

## Tests and verification snapshot

`tests/` contains the standard-library `unittest` suite for the CLI, configuration, events, parsing, detectors, storage, reporting, and GUI. The recorded local result for the audited worktree is **556 tests: 546 passed, 10 skipped**; focused GUI discovery is **140 passed**. These results were obtained locally on CPython 3.14.10 with the existing GUI test environment. They are not hosted CI results. No matching hosted GitHub Actions run for the audited exact HEAD was found. Workflow configuration for Ubuntu and Windows is not proof of a hosted pass.

## Documentation

- `docs/USER_GUIDE.md` — CLI and Windows GUI release-candidate instructions.
- `docs/USAGE.md` — CLI usage/configuration reference.
- `docs/ARCHITECTURE.md` — shared CLI pipeline and optional GUI architecture.
- `docs/DETECTION_RULES.md`, `docs/REQUIREMENTS.md`, `docs/SECURITY_AUDIT.md` — product specifications and limitations.
- `docs/PHASE3_VALIDATION.md` — historical design-validation record, not a current release approval.
- `docs/PHASE-1-REMEDIATION-RESULTS.md` — current controlled audit summary.
- `docs/PHASE-1-FINAL-SOURCE-PUBLICATION-MANIFEST.md` — path-by-path proposal; not owner-approved or ready to stage.
- `docs/PHASE-1-ARTWORK-PROVENANCE-EVIDENCE-REQUESTS.md` — evidence requests for each held asset.
- Other `docs/PHASE-1-*` review/control records are internal working material and are HOLD pending an owner disclosure decision.

The three new Phase 1 documents are review aids; their presence does not authorize publication. See the manifest for per-path classifications and current hashes.

## Packaging and distribution status

`packaging/gui_entry.py`, `packaging/LogSentinel-GUI.spec`, and `packaging/LogSentinel-GUI-Onedir.spec` are present in the worktree. **All three remain HOLD** pending review of the recipes and existing onedir-spec changes and a separately authorized validation. No clean packaging build was performed for this documentation task. Do not treat the recipes as publication-cleared or as evidence that a build is distributable.

The local Windows EXE and ZIP are generated release artifacts outside the source-publication proposal. They remain **HOLD — NOT CLEARED FOR DISTRIBUTION** pending component/source and notice mapping, Qt/PySide/Shiboken licensing and source/replacement decisions, Microsoft runtime evidence, support/replacement validation, and written owner and qualified-counsel approvals tied to exact final artifact hashes.

## Repository-state baseline

At the audit baseline before these documentation edits: branch `main`; HEAD `3229b17f9f0ae4fefc48e58f7a688f9250e1a117`; `origin/main` at `e5bcfd0d78cdb520025ff2cc2398aaaedb1fada0`; local `main` one commit ahead; 87 tracked paths, 11 modified tracked paths, 117 non-ignored untracked entries, and zero staged paths. The untracked `NUL` entry is preserved and excluded from the source proposal.

The initial audit baseline had 28 tracked HOLD paths: the 23 GUI assets, the GUI theme asset test, `PROJECTMAP.md`, and three packaging paths. This refreshed map and the GUI theme test are now classified PROPOSED INCLUDE; the test remains dependent on resolving and including the held artwork. The 26 remaining paths from that baseline are HOLD (23 artwork files and three packaging paths). The final manifest also classifies the three requested Phase 1 deliverables as HOLD pending a separate public-disclosure decision. Preserve the Git index, all existing changes, and checkpoint refs; staging, commit, push, tag, release, and publication are not authorized by this map.
