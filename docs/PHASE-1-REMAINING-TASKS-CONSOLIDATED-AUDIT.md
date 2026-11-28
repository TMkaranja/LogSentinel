# LogSentinel Phase 1 — Remaining Tasks Consolidated Audit

**Audit date:** 2026-12-02
**Scope:** non-publishing source-preparation workflow in this checkout. This report is not authorization to stage, commit, push, tag, release, publish, distribute, or claim legal clearance.

## 1. Executive decision

- **GUI/CLI technical validation:** passed for the current worktree. Focused GUI discovery ran **140 tests: 140 passed, 0 failures/errors/skips**. Full discovery ran **556 tests: 546 passed, 0 failures/errors, 10 skipped**. Python AST parsing and CLI smoke checks passed (details in §3).
- **Source-only GitHub publication:** **NOT READY TO STAGE**. A provisional 61-path INCLUDE list exists in the source-publication manifest (59 tracked + `docs/USER_GUIDE.md` + the manifest itself), but it is not an approved index. All 23 live GUI artwork assets are still HOLD pending item-specific origin/rights evidence; the stale `PROJECTMAP.md` and packaging-spec review remain open; the manifest’s old worktree counts are no longer current. No stage/commit/push was performed.
- **Windows GUI binary distribution:** **HOLD — NOT CLEARED FOR DISTRIBUTION**. The preserved EXE and ZIP hashes match their recorded baseline. This engineering audit is not a rights determination, notice review, release approval, or distribution authorization.
- **Remaining task groups:** **14** (8 source-publication gates and 6 separate binary-release gates; see §9). These are grouped decision/work items, not a legal checklist or proof that any gate is closed.

## 2. Repository snapshot and preservation

Read-only Git snapshot at audit time:

| Item | Result |
|---|---|
| Branch / HEAD | `main` / `3229b17f9f0ae4fefc48e58f7a688f9250e1a117` |
| `origin/main` | `e5bcfd0d78cdb520025ff2cc2398aaaedb1fada0` |
| Branch relation | local `main` ahead by one commit |
| Tracked paths | 87 |
| Modified tracked paths | 11 |
| Non-ignored untracked paths | 116 at the initial snapshot (19 under `docs/`, 96 under `licenses/`, plus special `NUL`); 117 after this new audit file was created (20 under `docs/`) |
| Staged paths | 0 |
| Ignored paths/files reported by Git | 13,116; regular-file bytes summed: 1,176,061,081 |

Modified tracked files: `.gitignore`, `README.md`, `docs/USAGE.md`, `packaging/LogSentinel-GUI-Onedir.spec`, the four integrated SVGs `check.svg`, `download.svg`, `folder_open.svg`, `x.svg`, `src/logsentinel/gui/icons.py`, `tests/test_gui_panels.py`, and `tests/test_gui_themes.py`. These existing changes were preserved. `README.md` was updated in this workflow only to correct the previously stale local suite count, from 554 to the observed 556; no other file was edited during this audit.

The untracked root entry named `NUL` is a Windows character-device/reserved-name object (not a regular file; zero-byte `Path.stat`, mode type character device), not an ordinary document. It is classified **EXCLUDE from any staging proposal**, left untouched, and not opened. All other untracked content is classified in §5. No dependency was installed, no packaging spec or release artifact was modified, and no staging/commit/push/tag/release/publication action occurred.

### Commands used to inspect the repository

```text
git status -sb
git status --short --ignored -uno
git ls-files
git ls-files --others --exclude-standard
git ls-files --others --ignored --exclude-standard
git diff --name-only
git diff --stat
git diff --check
git diff --cached --check
git diff --cached --name-only
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git rev-parse origin/main
git check-ignore -v release/LogSentinel-Windows-v0.1.0/LogSentinel.exe release/LogSentinel-Windows-v0.1.0.zip test-results.txt test-results-local.txt .venv-build/python.exe
```

Results: all expected ignore matches were found (`/release/`, both test-result captures, and `/.venv-build/`); staged-name output was empty. `git diff --check` and `git diff --cached --check` had no whitespace errors. Git emitted existing LF/CRLF conversion warnings only.

## 3. Verification commands and results

### Test suites

The checkout uses a `src/` layout. Both runs inserted `src` into `sys.path` before standard-library `unittest` discovery; Python was CPython **3.14.10** on Windows, with the existing PySide6 environment. No dependencies were installed.

```text
python -B -  [script: sys.path.insert(0, 'src'); unittest discovery tests/test_gui*.py]
Result: Ran 140 tests; OK. Focused GUI total: 140 passed, 0 failures, 0 errors, 0 skipped.

python -B -  [script: sys.path.insert(0, 'src'); unittest discovery tests]
Result: Ran 556 tests; OK (skipped=10). Full suite: 546 passed, 0 failures, 0 errors, 10 skipped.
```

The shell wrapper printed an unrelated `:PYTHONDONTWRITEBYTECODE=1: command not found` because a PowerShell-style environment assignment was forwarded to bash. The Python test commands nevertheless ran with `-B` and completed successfully. The run totals above are from the actual unittest result objects, not the wrapper message. A hosted Actions run for this checkout was **not** verified or claimed.

### CLI smoke checks

Executed with `PYTHONPATH=src` using `python -B -m logsentinel` and a disposable system-temp directory (removed on script exit):

| Command/scenario | Result |
|---|---|
| `--help` | exit 0; usage/options displayed |
| `--version` | exit 0; `logsentinel 0.1.0` |
| analyze shipped `samples/` with `--quiet --json <temp>` | exit 1 as expected for findings; parsed JSON asserted 3 files scanned, 3 findings, 1 malformed line |
| missing input path | exit 2, diagnostic “no input files discovered” |
| malformed one-line file with `--strict --quiet` | exit 2, strict parse-abort diagnostic |
| Assertions | PASS for help/version/sample JSON/missing input/strict malformed input |

### Syntax, links, diff, and tooling

- `ast.parse` over all `*.py` in `src/`, `tests/`, and `packaging/`: **47 files parsed, PASS**.
- Markdown links in `README.md`, `docs/USAGE.md`, and `docs/USER_GUIDE.md`: **17 relative references inspected; 0 missing targets** (16 resolve to local files/directories, one is an in-page anchor). External links and every internal audit/licensing report were not exhaustively link-validated.
- `git diff --check` and `git diff --cached --check`: PASS, with only line-ending warnings.
- Python package/tool availability: Python 3.14.10; pytest, ruff, mypy, and PyInstaller executables/modules unavailable in the active interpreter. The project’s configured `unittest` suite ran successfully; no external lint/static analyzer or clean GUI build was attempted. The `build` module is available but no package build was requested or run.

## 4. Release artifact verification (preserved; not approved)

| Local artifact | Bytes | SHA-256 | Verification |
|---|---:|---|---|
| `release/LogSentinel-Windows-v0.1.0/LogSentinel.exe` | 9,922,891 | `d1bda55a555f6e1a6a433eae89d648079f7eeeb869bd9ee3da487cde36d52b04` | Matches recorded baseline |
| `release/LogSentinel-Windows-v0.1.0.zip` | 9,733,515 | `00b13f0dbf7db61a838be8979f92e4ab761d098b44c071d2b365916fb77cf53a` | Matches recorded baseline; `ZipFile.testzip()` returned `None` |
| `release/LogSentinel-Windows-v0.1.0/SHA256SUMS.txt` | 91 | `2f7fbd2f44d5e094c9e7596ebb8006ee610ee34623fe641f0c878643a03baee2` | Recorded EXE digest agrees |

The ZIP has four members: `LICENSE` (1,075 bytes), `LogSentinel.exe` (9,922,891), `README.md` (10,916), and `SHA256SUMS.txt` (91). No rebuild, extraction-to-deliverable, or modification occurred. The separate anomalous `from pyzbar import pyzbar.py` worktree file was not part of the ZIP; its source/provenance/personal-data-shaped values remain unresolved and it is excluded from proposed source scope. Hash verification identifies files only; it is not endorsement or release clearance.

## 5. Complete worktree disposition

### Provisional INCLUDE — exact 61-path candidate

The exact provisional allowlist is the path list in [`PHASE-1-GITHUB-SOURCE-PUBLICATION-MANIFEST.md`](PHASE-1-GITHUB-SOURCE-PUBLICATION-MANIFEST.md), §1. It was mechanically reconciled: **61 unique, existing regular files** (59 tracked candidates, plus untracked `docs/USER_GUIDE.md` and the manifest itself). Their current aggregate size is **1,009,203 bytes**. The exact path/size/SHA-256 manifest follows; this is a candidate only, not a ready-to-stage index, and remains conditional on scope decisions and rights review.

| Proposed path | Bytes | SHA-256 |
|---|---:|---|
| `.github/workflows/tests.yml` | 1,220 | `5fc2b5447e3986b74ca787645bfb09b02e4372bf6ce670252555cac445700fd0` |
| `.gitignore` | 453 | `c5ed230a6d41b7465ace78d3d769e0814b80c626351c96d39225c2293fd52a7c` |
| `LICENSE` | 1,075 | `2303a4d4953cc673cbd314782cf05346901c40323d0d4426d758a6d96e4ea3f1` |
| `README.md` | 13,290 | `4f323af64e213752618caa9c5894959b2793f7524fd0f250ba604b9a66dc5553` |
| `pyproject.toml` | 417 | `9cfb01ce7a284544d34a0b7ae50c5afb7f7267b6c0b3fb0e94106b4b00b4c72d` |
| `docs/ARCHITECTURE.md` | 42,623 | `fb7ba46dcfa6d3976083eb84a7f4298950ae0a2f6365d48943483bdcc519ba51` |
| `docs/DETECTION_RULES.md` | 24,509 | `c038c008473e48e95d2e94aeca883f56ee927ef9ccfb0eeb6c77fb5bfa2bd53c` |
| `docs/PHASE3_VALIDATION.md` | 52,594 | `7ccff201c60f92f2f2ff1b602dec9825598fa1f8097a53989f45cc9a14ad37b7` |
| `docs/REQUIREMENTS.md` | 25,363 | `31cec250c3db3a572942febeb03acf884b5a3bd31366e299013028d4e2ba82d6` |
| `docs/SECURITY_AUDIT.md` | 21,304 | `58a10986e6c7448a672adeff13e42e5f742df616e1cc5f817276878cc44f1682` |
| `docs/USAGE.md` | 16,876 | `c892da7761ef8730f86072082bbed169ea3c667afdc165227e9570d75fccfcf0` |
| `docs/USER_GUIDE.md` | 25,015 | `0f0b5e2adb099174dcc003372921e5918b801a10b6f7d5f4d8cc5a8f5608d1c7` |
| `docs/PHASE-1-GITHUB-SOURCE-PUBLICATION-MANIFEST.md` | 25,626 | `38d24f416513e36ac8ef74a18e1d0984ce9dada71a30ba349dc41cd2f4a105c3` |
| `samples/access.log` | 1,037 | `17a64e446a2bfc927ef7e99bfcd97a1f1b91415fba2f07a5e2e33e4cf0762740` |
| `samples/auth.log` | 1,406 | `092cdfddfc05672b0f3328ed2efdb69e487a7223baaf41f22f18c15623f38f4c` |
| `samples/firewall.log` | 1,629 | `5cdcef8e5088d8f96821e98edb8c76fcdc5dfd102fff426d8a0ca47ff05aaa2a` |
| `src/logsentinel/__init__.py` | 214 | `5a1fe1391f1ebe61a528ac95096d60d6e10ed0faecc8112b8a88d8169f980593` |
| `src/logsentinel/__main__.py` | 134 | `d0d4159b980a40754d3e2c567b68d12145f81f54f7b4960f487be72d0887eaf3` |
| `src/logsentinel/cli.py` | 16,062 | `886cb5718ebf7f8ad553ea901dd95c5364853ec34b26d7ad484c658f68133785` |
| `src/logsentinel/config.py` | 7,115 | `83a297d4d37c02a77e5aabb1ddb6df74aaffdf45914995926a2b29a1b9e5a9a5` |
| `src/logsentinel/detectors.py` | 14,572 | `cd03fbfb803a7c1f8ffac6b4794670341964e43b6bb44fd2e9630e4cf48c6778` |
| `src/logsentinel/events.py` | 15,374 | `302218e1808f03cf7dfdef8b32e542cb7ee445ca2f418e21c4f6e3cc7c4437c5` |
| `src/logsentinel/exceptions.py` | 949 | `fddc779c65616e5879507c87865da0672c8a4406a8a9fc0325b0ea661111f6d9` |
| `src/logsentinel/inputs.py` | 10,539 | `5ac0bdc96078f1646fb2c6d023c16e8a65c1254ae3b2f36cb09d712487ab7440` |
| `src/logsentinel/parsers.py` | 19,238 | `f3beb1445445d742acbe7fa810271c67e84eca5488bce7ec0dff6cf81487a78d` |
| `src/logsentinel/report.py` | 9,657 | `214481bd9e51d7c6336e196f73a8a639b4262e743d5dd7b3943b934e21c0d8ad` |
| `src/logsentinel/storage.py` | 39,786 | `fb90b9b140364f47d7154e62c22b1596024a004917b6d9305c887a0d2d680a68` |
| `src/logsentinel/gui/__init__.py` | 410 | `440befaafd0e6d9396721662355ec7b8b6f09768b2f929836e9fac76f06eeede` |
| `src/logsentinel/gui/__main__.py` | 214 | `c55a492987f6d0a884e4489c986241b0386d5707a11cb171c3db09058bba6b40` |
| `src/logsentinel/gui/app.py` | 1,823 | `126c12148f7135e322a002823daf03126d4bf4342de2257af34b7c7300d2a72d` |
| `src/logsentinel/gui/app_settings.py` | 10,186 | `aa9e78d979f3d94db5e7bd2c32848c836bd494645bfe91e80a3c8dbfa253394d` |
| `src/logsentinel/gui/backend.py` | 17,483 | `380a1d5076d50970787896762e603e3bed16484f13796aa61014cd0dd170abe7` |
| `src/logsentinel/gui/icon_widgets.py` | 4,590 | `047b9beb0d13f2650d3b60e04257f742dcc801e1203154868839c45ab1bc371b` |
| `src/logsentinel/gui/icons.py` | 22,355 | `8e680a426e33672eb3a7e896477e53259bfa936b392b9e83ef2f6f3e3f7ea67f` |
| `src/logsentinel/gui/main_window.py` | 43,112 | `d3f02245e354512f92b9fae45665302329fd066298d2457ebb73494611e35c1f` |
| `src/logsentinel/gui/models.py` | 10,283 | `82f539438311913a56d8c668b1eb3df9a5d8d0706701a2c5426e945aa2e3f134` |
| `src/logsentinel/gui/panels.py` | 30,540 | `b686ee42578e3b7e64602563c0a040295f0a80b38e73675a97c25bc46554819a` |
| `src/logsentinel/gui/reporting.py` | 21,299 | `12c327c481ce2afa4d0e327453a436202888f3b34a583f610c7ed47f717b8a1c` |
| `src/logsentinel/gui/reports_view.py` | 14,320 | `5d5406fda21a4e7d35fe33f79681bec5d41666ca0adf7445ec135dbae5488394` |
| `src/logsentinel/gui/settings_view.py` | 24,540 | `2950011d83a8f375676c6b2145e86e5be89cc1fa8e9c0648f93c7b52e6748700` |
| `src/logsentinel/gui/theme.py` | 23,584 | `5e8452d35d125d07b693507e3a0a5a5f4feca7bcb5c9a8a03ec7d98ed3ce335a` |
| `src/logsentinel/gui/themes.py` | 10,242 | `f519ef7a11f7e62bdf15278547a8d52051484bebb5c636de737cca8c3d37399a` |
| `src/logsentinel/gui/views.py` | 36,710 | `146e8269f07120ed5dec827467f96164d59189b41a39a5c4077d26e95685e21c` |
| `src/logsentinel/gui/worker.py` | 3,988 | `3dac28e086cbb4a0c59d1c5dec1d8e48f45d4bfc41dad29ed6ee717c09563a4e` |
| `src/logsentinel/gui/assets/__init__.py` | 57 | `51f903f643c849d079e612b646a649c23ce56774b3ec30c7da251842c297f36f` |
| `tests/__init__.py` | 336 | `c4d2ed97c1135c413df92dc19d993c1a64e79749a3f38dced779859d2d19ed43` |
| `tests/test_cli.py` | 46,587 | `ffebd0d1a613c587e04dfed6e5738eeb62114b2eed3e1eceea0f2b58f87fd1f4` |
| `tests/test_config.py` | 9,992 | `d3fd0cbe3000adb35e4d46051c63bb7bb0e50a7d42565fb6d595f67d49628b4a` |
| `tests/test_detectors.py` | 24,136 | `c0e710dc4cc65e44ad566764229edcaf541ed371d6048323ccb20a39b4ae5464` |
| `tests/test_events.py` | 13,755 | `f40ccccf5a13c83fe88c487d1cb4a3f334ec050cdca9a96d154292f169e4ca91` |
| `tests/test_gui_backend.py` | 12,097 | `fdde74d7def1dc95491f586fbaf169f4a5aac032b361cd8a5bf263b2a7cf1a87` |
| `tests/test_gui_dashboard.py` | 21,768 | `f9ab8b1edeec36d5bd2e263aa9336284749c6d297581a1610563ddbba0611df5` |
| `tests/test_gui_panels.py` | 14,347 | `6c2f589a96246f2406403da19631b291fcc5b8043207a833300a5cf73c6fced4` |
| `tests/test_gui_reports.py` | 16,110 | `edb5eccf44c47b87b9f97c336e1946e873fb4ae7a38524313b87ee7b44bdc9f0` |
| `tests/test_gui_settings.py` | 30,423 | `6b3a8e22db5143128d47faedcb3019ea6e15945e06e255170582dc791abd9d54` |
| `tests/test_gui_shell.py` | 7,071 | `4c986846e109e9cbdfe4c8509b70395395ca07cc50c8ed878183e75179fa7888` |
| `tests/test_gui_worker.py` | 13,927 | `3b17d1dd8f753c7d09e49f66e3fcc8aad6f9d1a1a8766759dd746e18428d21d9` |
| `tests/test_inputs.py` | 21,159 | `190588d699ef151941f33e911e576cd4f407efb1648e124f1ef73dc76ebee141` |
| `tests/test_parsers.py` | 26,066 | `00f98342fe1cfb66e2f061098be124b9071c6c19a50de62a94684797de06bee4` |
| `tests/test_report.py` | 25,632 | `f886a5385cbdc112bb83c85dff484e8305ff4d670bdc3931683b663c951190cc` |
| `tests/test_storage.py` | 61,984 | `aec91bc12ec730d6687fd897aa80eb97533d6f68655471397ad7b1fca8a54634` |

Core candidate groups: workflow, `.gitignore`, root `LICENSE`, `README.md`, `pyproject.toml`; six existing documentation files plus `docs/USER_GUIDE.md` and the manifest; all three synthetic `samples/*.log`; 29 CLI/GUI Python source paths (including the GUI asset package `__init__.py`); and 16 test files. It deliberately omits `PROJECTMAP.md`, the GUI artwork, GUI packaging specs/entry point, internal review records, and licensing corpus. The README’s now-verified 556 test count has been corrected in this worktree.

**Important dependency:** this candidate is not yet a fully coherent GUI source-publication set because the complete theme-asset test is held along with all 23 artwork assets. Thus source publication may be considered only after the owner resolves GUI scope/assets and finalizes the allowlist; no automatic inclusion is authorized.

### HOLD — tracked paths (28)

These 27 tracked paths are not in the provisional 61-path candidate:

```text
PROJECTMAP.md
tests/test_gui_themes.py
packaging/LogSentinel-GUI-Onedir.spec
packaging/LogSentinel-GUI.spec
packaging/gui_entry.py
src/logsentinel/gui/assets/brand/logsentinel-appicon.svg
src/logsentinel/gui/assets/brand/logsentinel-logo.svg
src/logsentinel/gui/assets/brand/logsentinel-mark.svg
src/logsentinel/gui/assets/brand/logsentinel-sidebar.svg
src/logsentinel/gui/assets/icons/alert.svg
src/logsentinel/gui/assets/icons/check.svg
src/logsentinel/gui/assets/icons/detections.svg
src/logsentinel/gui/assets/icons/download.svg
src/logsentinel/gui/assets/icons/file_plus.svg
src/logsentinel/gui/assets/icons/file_text.svg
src/logsentinel/gui/assets/icons/folder_open.svg
src/logsentinel/gui/assets/icons/log_explorer.svg
src/logsentinel/gui/assets/icons/overview.svg
src/logsentinel/gui/assets/icons/palette.svg
src/logsentinel/gui/assets/icons/play.svg
src/logsentinel/gui/assets/icons/reports.svg
src/logsentinel/gui/assets/icons/search.svg
src/logsentinel/gui/assets/icons/settings.svg
src/logsentinel/gui/assets/icons/shield_check.svg
src/logsentinel/gui/assets/icons/stop.svg
src/logsentinel/gui/assets/icons/trash.svg
src/logsentinel/gui/assets/icons/x.svg
src/logsentinel/gui/assets/logsentinel.ico
```

`tests/test_gui_themes.py` and 23 image resources are held because local records still show **23/23 assets without verified historical origin and rights basis**; four assets have exact Lucide geometry matches but historical copying/rights are not established. The test must stay coherent with the assets if GUI source is published. `PROJECTMAP.md` is stale versus the GUI-inclusive current tree. Both `.spec` recipes and `gui_entry.py` are optional source build recipes, but the existing 64-line onedir diff is unreviewed for publication/build purposes and the one-file/on-dir differences require a recorded decision. No build was run.

Current live asset size/hash inventory (newly integrated four; the remaining 19 entries unchanged from the provenance report):

| Path (all under `src/logsentinel/gui/assets/`) | Bytes | SHA-256 | Status |
|---|---:|---|---|
| `brand/logsentinel-appicon.svg` | 920 | `bb28859d520c23a76493efba923b3adfa8cba6aa873090a29e501362e2f25a61` | HOLD |
| `brand/logsentinel-logo.svg` | 10,340 | `9c30d78911c0fff3a641b1820e139370a0991806dcd0523b207df1e305773fa9` | HOLD |
| `brand/logsentinel-mark.svg` | 920 | `bb28859d520c23a76493efba923b3adfa8cba6aa873090a29e501362e2f25a61` | HOLD |
| `brand/logsentinel-sidebar.svg` | 10,083 | `eb0d3e0874a3877b79503be7128d10a512dd8205fabae60fee319a34b4dfc62f` | HOLD |
| `icons/alert.svg` | 292 | `191a66cf92f42cdd1bf7375d7b0c94f5f53bac44730201e65a2b284b770c3989` | HOLD |
| `icons/check.svg` | 274 | `fcef03681b865729223add19063265b82730b18f723ea8b42529ba1ab2a5a03e` | HOLD; new proposal, not rights evidence |
| `icons/detections.svg` | 368 | `672cd521c8a8ea7355bdbd4f0de78addd014a4e9725f8e74343a9600a453668a` | HOLD |
| `icons/download.svg` | 363 | `7e86a3790b6391e40e3f39712270ebd248c95586f6db02ee56a23dcc96339244` | HOLD; new proposal, not rights evidence |
| `icons/file_plus.svg` | 299 | `d0357c44c6c1e429614609657a8af64f8f6edb9780924dd09f2f7206b936f8f8` | HOLD |
| `icons/file_text.svg` | 298 | `a37006fe9dcf14f1d2758761051f5c4ae169d57512c12e62ce9280d8d945f501` | HOLD |
| `icons/folder_open.svg` | 372 | `9693d483e481b8d4e568ba1d6ff3cd34e2c6a926332427144b5612b20c9d28f9` | HOLD; new proposal, not rights evidence |
| `icons/log_explorer.svg` | 317 | `3008d40feac72acb9588ac87193c61e9917f5f5bc72665f5e880a520a06f516f` | HOLD |
| `icons/overview.svg` | 368 | `379fe603df3afc8b80a178b83bbc649d594a74772e984b3c18c5d6ab152336dd` | HOLD |
| `icons/palette.svg` | 444 | `629e32b419d0adf0b054a4cb87d52d8dd934a0847b58a06ca7f574d200f353b5` | HOLD |
| `icons/play.svg` | 198 | `4d8390b96e111470d6d397540610b6209cd1f16df089fdbd802f4bb70cc946cd` | HOLD |
| `icons/reports.svg` | 322 | `65eeb087b42d52b53721b9202be45487504ca3d253ae92b07ef0154cb7e841f4` | HOLD |
| `icons/search.svg` | 226 | `5c916fe41833f69421452f6198eb24ce7463b8875c38b25c391f75d1a6ce7b63` | HOLD |
| `icons/settings.svg` | 778 | `df60f7fce3362af3958dc54e389389f399ad346b9519f2ffe25734c842d9199b` | HOLD |
| `icons/shield_check.svg` | 352 | `4b67896a203ea68f791703a20533765a66f53ccbb84fe6292293604b402a1244` | HOLD |
| `icons/stop.svg` | 220 | `07817d961981a2b1a7206436ad5c49c571b9c07d670e87945bef9216d9d22ffb` | HOLD |
| `icons/trash.svg` | 335 | `56da0d4c3ba1b515cb1eceb530a9c99d9353b8e3335256e2b80f153bf4c7edaf` | HOLD |
| `icons/x.svg` | 371 | `05ea73de346c5f881b2bde865c04a50f582350856c82ec606941e72532bb92d6` | HOLD; new proposal, not rights evidence |
| `logsentinel.ico` | 28,829 | `000dbee98ff64b8c31074c0e346c3322f2213f0e6c99d2c84a937821b6e275e6` | HOLD |

The four approved designs have integrated tests and matching fallback data; technical acceptance does not establish authorship, rights, license, or distribution clearance. The semantic regression asserts preserve **Apply** text, limit the eraser to clear/reset uses, and retain `trash` for **Remove Selected**.

### HOLD — untracked documentation and licensing material

- **17 untracked Phase 1 review/control documents:** `docs/PHASE-1-COMPLETE-GUI-ASSET-REPLACEMENT-REVIEW.md`, `docs/PHASE-1-COMPLETE-PUBLICATION-SCOPE-REVIEW.md`, `docs/PHASE-1-FOUR-ICON-INTEGRATION-REPORT.md`, `docs/PHASE-1-FOUR-ICON-ORIGINAL-ALTERNATIVE-REVIEW.md`, `docs/PHASE-1-GITHUB-PUBLICATION-BLOCKER-REGISTER.md`, `docs/PHASE-1-GITHUB-SOURCE-PUBLICATION-REVIEW.md`, `docs/PHASE-1-GUI-ASSET-PROVENANCE-REPORT.md`, `docs/PHASE-1-GUI-ASSET-PUBLICATION-RESOLUTION.md`, `docs/PHASE-1-LUCIDE-ASSET-CORRECTION-REPORT.md`, `docs/PHASE-1-LUCIDE-ASSET-REPLACEMENT-REPORT.md`, `docs/PHASE-1-LUCIDE-INTEGRATION-ELIGIBILITY-REVIEW.md`, `docs/PHASE-1-LUCIDE-LICENCE-ATTRIBUTION-RECONCILIATION.md`, `docs/PHASE-1-ORIGINAL-FOUR-ICON-INDEPENDENT-REVIEW.md`, `docs/PHASE-1-ORIGINAL-FOUR-ICON-PROPOSAL-REPORT.md`, `docs/PHASE-1-ORIGINAL-GUI-ASSET-REPLACEMENT-REPORT.md`, `docs/PHASE-1-REDESIGNED-ICON-INDEPENDENT-REVIEW.md`, and `docs/PHASE-1-THREE-ICON-REDESIGN-REPORT.md`. They are review/evidence records, not automatically product docs. Public disclosure is undecided. The source-publication manifest is listed separately in the candidate allowlist; this audit is newly created, excluded from that candidate, and not included in this 17-file inventory.
- **All 96 files under `licenses/` are HOLD as an uncurated collection**, including the following exact current paths:

```text
licenses/DISTRIBUTION-LICENSING-STATUS.md
licenses/GPL-3.0.txt
licenses/LGPL-3.0.txt
licenses/THIRD-PARTY-NOTICES.md
licenses/third-party/ATTRIBUTION-SOURCE-REGISTER.md
licenses/third-party/COMPATIBILITY-RISK-ASSESSMENT.md
licenses/third-party/CONSOLIDATED-RELEASE-BLOCKER-CLOSURE-REPORT.md
licenses/third-party/FINAL-LICENSING-AUDIT.md
licenses/third-party/FINAL-RELEASE-READINESS-REPORT.md
licenses/third-party/FINAL-THIRD-PARTY-NOTICE-RECONCILIATION.md
licenses/third-party/MSVC-RUNTIME-REDISTRIBUTION-REVIEW.md
licenses/third-party/OTHER-COMPONENTS-INVENTORY.md
licenses/third-party/QT-PYSIDE-BINARY-PROVENANCE-REPORT.md
licenses/third-party/QT-PYSIDE-CORRESPONDING-SOURCE-REGISTER.md
licenses/third-party/QT-PYSIDE-LGPL-DISTRIBUTION-ASSESSMENT.md
licenses/third-party/QT-PYSIDE-LGPL-GAP-CLOSURE-PLAN.md
licenses/third-party/QT-PYSIDE-PHASE-1-RELEASE-ROUTE-DECISION.md
licenses/third-party/QT-PYSIDE-SOURCE-ARCHIVE-AND-BUILD-EVIDENCE.md
licenses/third-party/RELEASE-PREPARATION-CHECKLIST.md
licenses/third-party/RUNTIME-LICENSING-EVIDENCE.md
licenses/third-party/TRIMMED-PACKAGE-NOTICE-MAP.md
licenses/third-party/VC-RUNTIME-EIGHT-DLL-PROVENANCE-REPORT.md
licenses/third-party/asset-remediation/original-four-icon-proposals/check.svg
licenses/third-party/asset-remediation/original-four-icon-proposals/download.svg
licenses/third-party/asset-remediation/original-four-icon-proposals/fallback_icons.py
licenses/third-party/asset-remediation/original-four-icon-proposals/folder_open.svg
licenses/third-party/asset-remediation/original-four-icon-proposals/x.svg
licenses/third-party/asset-remediation/original-proposals/brand/logsentinel-appicon.svg
licenses/third-party/asset-remediation/original-proposals/brand/logsentinel-logo.svg
licenses/third-party/asset-remediation/original-proposals/brand/logsentinel-mark.svg
licenses/third-party/asset-remediation/original-proposals/brand/logsentinel-sidebar.svg
licenses/third-party/asset-remediation/original-proposals/contact-sheet.html
licenses/third-party/asset-remediation/original-proposals/icons/alert.svg
licenses/third-party/asset-remediation/original-proposals/icons/detections.svg
licenses/third-party/asset-remediation/original-proposals/icons/file_plus.svg
licenses/third-party/asset-remediation/original-proposals/icons/file_text.svg
licenses/third-party/asset-remediation/original-proposals/icons/log_explorer.svg
licenses/third-party/asset-remediation/original-proposals/icons/overview.svg
licenses/third-party/asset-remediation/original-proposals/icons/palette.svg
licenses/third-party/asset-remediation/original-proposals/icons/play.svg
licenses/third-party/asset-remediation/original-proposals/icons/reports.svg
licenses/third-party/asset-remediation/original-proposals/icons/search.svg
licenses/third-party/asset-remediation/original-proposals/icons/settings.svg
licenses/third-party/asset-remediation/original-proposals/icons/shield_check.svg
licenses/third-party/asset-remediation/original-proposals/icons/stop.svg
licenses/third-party/asset-remediation/original-proposals/icons/trash.svg
licenses/third-party/asset-remediation/original-proposals/logsentinel.ico
licenses/third-party/asset-remediation/proposed-lucide-replacements/ATTRIBUTION.md
licenses/third-party/asset-remediation/proposed-lucide-replacements/LICENSE-FEATHER-MIT-v4.29.1.txt
licenses/third-party/asset-remediation/proposed-lucide-replacements/LICENSE-LUCIDE-AT-PINNED-SOURCE-COMMITS.txt
licenses/third-party/asset-remediation/proposed-lucide-replacements/LICENSE-LUCIDE-CURRENT-SNAPSHOT.txt
licenses/third-party/asset-remediation/proposed-lucide-replacements/check.svg
licenses/third-party/asset-remediation/proposed-lucide-replacements/download.svg
licenses/third-party/asset-remediation/proposed-lucide-replacements/folder_open.svg
licenses/third-party/asset-remediation/proposed-lucide-replacements/x.svg
licenses/third-party/notices/MANIFEST.md
licenses/third-party/notices/README.md
licenses/third-party/notices/bzip2/LICENSE.txt
licenses/third-party/notices/cppwinrt/LICENSE.txt
licenses/third-party/notices/cpython/COPYRIGHT-AND-ATTRIBUTION.txt
licenses/third-party/notices/cpython/LICENSE.txt
licenses/third-party/notices/cpython/README.rst
licenses/third-party/notices/freetype/LICENSE.TXT
licenses/third-party/notices/freetype/alternatives/FTL.TXT
licenses/third-party/notices/freetype/alternatives/GPLv2.TXT
licenses/third-party/notices/freetype/alternatives/README.md
licenses/third-party/notices/freetype/qt-attribution-freetype.html
licenses/third-party/notices/harfbuzz/COPYING.txt
licenses/third-party/notices/harfbuzz/qt-attribution-harfbuzz-ng.html
licenses/third-party/notices/libjpeg-turbo/LICENSE.md
licenses/third-party/notices/libjpeg-turbo/README.ijg
licenses/third-party/notices/libpng/LICENSE.txt
licenses/third-party/notices/mesa-llvm/LLVM-3.6.2-LICENSE.TXT
licenses/third-party/notices/mesa-llvm/qt-attribution-llvm.html
licenses/third-party/notices/mesa-llvm/qt-attribution-llvmpipe.html
licenses/third-party/notices/mpdecimal/COPYRIGHT.txt
licenses/third-party/notices/openssl/LICENSE-APACHE-2.0.txt
licenses/third-party/notices/openssl/NOTICE-STATUS.md
licenses/third-party/notices/openssl/TAG-ACKNOWLEDGEMENTS.md
licenses/third-party/notices/pcre2/LICENCE.md
licenses/third-party/notices/pcre2/qt-attribution-pcre2-sljit.html
licenses/third-party/notices/pcre2/qt-attribution-pcre2.html
licenses/third-party/notices/pyinstaller/COPYING.txt
licenses/third-party/notices/sqlite/copyright.html
licenses/third-party/notices/unicode/UCD-16.0.0-ReadMe.txt
licenses/third-party/notices/unicode/UNICODE-LICENSE-V3.txt
licenses/third-party/notices/zlib-ng/LICENSE.md
licenses/third-party/notices/zstandard/alternatives/BSD-LICENSE.txt
licenses/third-party/notices/zstandard/alternatives/GPLv2-COPYING.txt
licenses/third-party/notices/zstandard/alternatives/README.md
licenses/third-party/qt/INVENTORY.md
licenses/third-party/qt/LicenseRef-Qt-Commercial.txt
licenses/third-party/qt/qt-lgpl.html
licenses/third-party/qt/qt-licensing.html
licenses/third-party/qt/qtforpython-commercial.html
licenses/third-party/qt/qtpdf-licensing.html
```

Existing records explicitly describe incomplete or package-specific evidence. Do not bulk-publish these files as recipient notices or as evidence that rights are cleared. Review every item separately before changing disposition.

`docs/USER_GUIDE.md` is the one untracked documentation file in the candidate; it resolves the README/USAGE links and was link-checked. Candidate path counts must not be confused with all 116 untracked entries.

### EXCLUDE — generated, local, or non-regular content (preserve locally)

Ignored inventory totaled 13,116 entries and 1,176,061,081 regular-file bytes. Key groups: `.venv-build/` (4,319 files; 28,682,313 bytes), `.venv-build-gui/` (8,239; 711,764,710), `build/` (104; 128,222,529), `dist/` (372; 286,119,071), `release/` (6; 19,669,071), `src/logsentinel.egg-info/` (5; 1,758), plus caches/bytecode, root `audit-*`, reports, and stale local test captures. These remain preserved. Exact high-risk files include `release/LogSentinel-Windows-v0.1.0/LogSentinel.exe`, its ZIP, `test-results.txt` (219,812 bytes), `test-results-local.txt` (104,586), `report.json` (5,233), `report.txt` (4,129), and `report-explicit.json` (5,233). `.gitignore` now explicitly covers the local release folder, test captures, build outputs, and build venvs. Ignore status is not staging approval; review any future index explicitly.

The local release EXE/ZIP and all generated trees are **EXCLUDE from source staging** while the binary itself independently remains on distribution HOLD. The reserved `NUL` object is also EXCLUDE. No local/generated item was deleted, moved, or rewritten.

## 6. Modified-file hash record

SHA-256 is over current worktree bytes. HEAD values identify the pre-existing tracked baseline; this audit does not overwrite that work.

| Modified tracked path | HEAD bytes / SHA-256 | Worktree bytes / SHA-256 |
|---|---|---|
| `.gitignore` | 299 / `a8915b554cae45586e23df65badd7c5a9c55cbb46dc61257658977e442079a07` | 453 / `c5ed230a6d41b7465ace78d3d769e0814b80c626351c96d39225c2293fd52a7c` |
| `README.md` | 10,916 / `0a3417209068d877c3c3533eb0446549d77e5e2852924b063f3ed049899944bd` | 13,290 / `4f323af64e213752618caa9c5894959b2793f7524fd0f250ba604b9a66dc5553` |
| `docs/USAGE.md` | 16,132 / `1f6b01f08a2c32288fac16455fbcab9857dba12d1ede5641f03854744e17a4ac` | 16,876 / `c892da7761ef8730f86072082bbed169ea3c667afdc165227e9570d75fccfcf0` |
| `packaging/LogSentinel-GUI-Onedir.spec` | 5,472 / `7942e7cba42aef822716d4abf373997e6f0bd3c1f6599f0d01715e617793904a` | 8,165 / `cb6817361bb32e11c9f20dfb54e6a3cf2274c602d902abba3a38b6063979b2d6` |
| `src/logsentinel/gui/assets/icons/check.svg` | 195 / `c18da1a09272c5824eb1d22e1051fb1e2d7a5d6f0bd5bfa7dcdbf76cff5dbecc` | 274 / `fcef03681b865729223add19063265b82730b18f723ea8b42529ba1ab2a5a03e` |
| `src/logsentinel/gui/assets/icons/download.svg` | 266 / `6768f09973c8cdb8eec192a0e608a706aa67724f3c0c7ae4951ad6cfc6d0fe92` | 363 / `7e86a3790b6391e40e3f39712270ebd248c95586f6db02ee56a23dcc96339244` |
| `src/logsentinel/gui/assets/icons/folder_open.svg` | 357 / `aa984e039550d29933593011ef6bb368f3be237d3ce61fd8a6864020e25c0aa2` | 372 / `9693d483e481b8d4e568ba1d6ff3cd34e2c6a926332427144b5612b20c9d28f9` |
| `src/logsentinel/gui/assets/icons/x.svg` | 212 / `bc94688afb024a859b561e93994c95b724fe690606121a5683447b89e2cd0c4a` | 371 / `05ea73de346c5f881b2bde865c04a50f582350856c82ec606941e72532bb92d6` |
| `src/logsentinel/gui/icons.py` | 21,559 / `a22408ecdb5c68f414c98e61bb72de4c9301dc866a53105f9c26fcb3567bcd04` | 22,355 / `8e680a426e33672eb3a7e896477e53259bfa936b392b9e83ef2f6f3e3f7ea67f` |
| `tests/test_gui_panels.py` | 12,010 / `e0183f9ea915e181de45cb9f0055110e87d7b37c8e88f37b59937dd8cd99b799` | 14,347 / `6c2f589a96246f2406403da19631b291fcc5b8043207a833300a5cf73c6fced4` |
| `tests/test_gui_themes.py` | 6,539 / `8ef60af61545fc4c10678706193d7246007f28b06d051a77ca8acd63a3355b90` | 8,670 / `19d4cdde1fc46ebf0244dd3527a1729a31e18dbb1897eca1709c5399475377b7` |

Hashes identify exact byte snapshots only; they do not establish authorship or rights.

## 7. Publication and licensing reconciliation

- The current README and User Guide preserve the caveat that the Windows GUI is a release candidate and not cleared for distribution. The root project `LICENSE` is MIT; it does not establish third-party asset rights or binary redistribution clearance.
- The current public-doc links checked resolve, including `docs/USER_GUIDE.md`. The README now documents the 556-test local result and accurately distinguishes configured Ubuntu/Windows jobs from an unverified hosted run for this worktree. `PROJECTMAP.md` still has stale CLI-era trees/counts/history and is held.
- The 23 GUI assets include 22 SVGs and one ICO. Existing provenance reports say 23/23 have no verified historical creator/source/rights record; exact-geometry comparisons and accepted original proposals do not establish authorship, legal originality, ownership, license compatibility, or publication/distribution permission. Keep every one on HOLD. Do not integrate unresolved Lucide candidates or treat proposed notice material as final.
- The `licenses/` collection includes incomplete candidate notices, alternative license texts, internal technical/provenance records, and binary-release assessments. It is not a curated recipient notice package; no item is promoted to a clearance conclusion here.
- Local history has checkpoint refs outside ordinary `main` ancestry and an unrelated pyzbar/OpenCV driver-license-shaped code file in local history/worktree. The source-publication manifest explicitly limits its proposed scope to a reviewed source allowlist; exact intended push refs/refspec and a fresh scan of the refs to be sent remain unverified. No remote GitHub settings were inspected.

## 8. Readiness decisions

### Source-only repository

**Decision: NOT READY TO STAGE.** Engineering tests pass in the current local checkout, but publication scope remains conditional and the current candidate omits held GUI assets/tests/specs and stale project map. Rights/provenance decisions are outstanding for the artwork, some internal evidence docs may expose detailed technical/environment information, and no final approved index/history scan or hosted CI evidence exists. The provisional allowlist in §5 is a review aid only. A clean test result is not a publication or legal approval.

### Windows binary

**Decision: HOLD — NOT CLEARED FOR DISTRIBUTION.** Artifact hashes and ZIP structure were verified; licensing/rights, component/source mapping, recipient notices, Qt/PySide route, Microsoft runtime rights, compatibility/support scope, and release-owner/counsel decisions remain outside this technical test. Do not attach, publish, distribute, or rebuild release binaries under this audit.

## 9. Remaining tasks: 14 grouped work items

### Source-publication gates (8)
1. Obtain and record item-specific creator/source/rights decisions for all 23 GUI assets; keep any unresolved paths on HOLD.
2. Curate applicable source attribution/license material from verified provenance; do not bulk-add the 96-file licensing corpus or use proposed notices as clearance.
3. Decide the intended public source scope and resolve whether to publish the complete GUI set; update the exact allowlist only after decisions, including the held GUI asset test/resources.
4. Refresh stale `PROJECTMAP.md` against the final source tree; reconcile README/project structure, test counts, documentation links, and optional GUI dependency/build descriptions.
5. Review the preserved 64-line onedir-spec diff, decide one-file/onedir differences, and validate any chosen recipes in a separately authorized clean build/smoke workflow. Do not modify packaging or build binaries under this audit.
6. Inspect the exact future staging index and all intended refs/refspec, including checkpoint-ref exclusion; run fresh secret/PII/path/provenance/file-type scans on exactly what will be sent.
7. Verify the intended-source-revision hosted CI evidence (or state its absence) and rerun the exact final test suite after all source/index changes.
8. Obtain repository-owner approval for the final path/ref proposal and staging in a separate authorized task; then re-verify staged paths/hashes. No such authorization or staging occurred here.

### Separate binary-release gates (6)
9. Define recipient, territory, distribution channel, exact package format, end-user terms, update/signing/anti-tamper model, and final artifact scope.
10. Resolve Qt/PySide/Shiboken license election and exact binary/source/build/translation mapping; identify any applicable source/relink/replacement route with qualified review.
11. Resolve Microsoft VC++ runtime redistribution rights/provenance for all bundled copies.
12. Complete file-level source/license/notice mapping for CPython, PyInstaller and all embedded Qt-linked/native components; elect alternatives where appropriate and curate exact recipient notices.
13. Validate the declared Windows support matrix and any applicable recipient replacement/relink workflow against the final artifact; prepare only required, artifact-matched source/instructions.
14. Obtain written release-owner and qualified-counsel approval tied to the final package hash and channel; recompute package/checksum manifest after any separately authorized changes. Until then, keep the binary on HOLD.

## 10. Audit limitations and final integrity

This is a local worktree engineering audit. It does not certify every historical blob/ref, every file in ignored trees, every external URL, platform support, GUI package behavior, copyright ownership, legal originality, licence/permission, or release compliance. The 60-path baseline product candidate plus the manifest itself is not a legally approved public manifest. No remote repository settings, branch protections, collaborator access, secret settings, or hosted workflow execution for the current worktree were verified. All excluded/held files and local binaries remain in place.

Files whose hashes are explicitly recorded above include the four integrated SVGs, matching fallback module, changed GUI tests, candidate release binaries/archive, checksum file, and the 61 candidate paths via the linked manifest’s exact list. The audit report’s own final byte size and SHA-256 are recorded in the completion message after write-time verification; a document cannot contain its own stable digest without changing that digest.
