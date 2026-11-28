# LogSentinel Phase 1 — User Guide

**Applies to:** LogSentinel 0.1.0 CLI and Windows GUI release candidate

**Status:** Phase 1 documentation for implemented features; not a production-readiness or distribution approval statement. The inspected Windows GUI candidate is **HOLD — NOT CLEARED FOR DISTRIBUTION**. Source publication is a separate decision and is **NOT READY TO STAGE**: item-specific evidence for the GUI artwork and review of the GUI packaging recipes remain open. Third-party notice and distribution-status materials prepared for review are incomplete proposals, not final recipient notices or legal clearance.

LogSentinel analyzes log files that you provide and reports patterns for a person to review. Findings are not proof of an attack, compromise, or intent. The current Windows GUI onedir build is a release candidate, not an installer or generally cleared distribution. Use a GUI package only if you have obtained it through an authorized channel.

## 1. Product overview and Phase 1 scope

LogSentinel has two ways to run the same batch-analysis pipeline:

- **Windows desktop GUI:** select log files or folders, adjust analysis settings, run an analysis, review results, and export JSON or HTML reports.
- **Command-line interface (CLI):** analyze file and folder paths from PowerShell or another terminal; print a text summary and optionally save JSON and/or text reports.

The current built-in detectors look for three statistical patterns: repeated SSH authentication failures, breadth of destination ports in firewall events, and HTTP client-error (4xx) responses. The program does not collect logs from other systems, monitor continuously, block traffic, send alerts, or contact a SIEM. You supply the files. Human review and external context are needed to interpret a finding.

Phase 1 describes these implemented capabilities only. It is not a promise of planned work. See [Known limitations and possible future work](#14-known-limitations-and-possible-future-work) for features that are not present.

## 2. Windows system requirements

### Windows GUI package

- The inspected onedir candidate is **64-bit Windows/AMD64** and includes its Python and Qt runtime files. Keep the complete extracted folder together; the executable is not a standalone file.
- The recorded end-to-end GUI test ran on one Windows 10 build 19045 desktop. This is the environment tested, **not a declared minimum Windows version or a complete support matrix**. Other Windows versions, including Windows 11, have not been established as supported by that test evidence.
- The application window has a minimum size of 1080 × 680 pixels. High-DPI/mixed-DPI, Remote Desktop, GPU-less/software rendering, and clean-target compatibility have not been verified across a support matrix.
- No GUI installer is provided by this project configuration. The current candidate is an onedir folder.

Do not infer that a Windows version is supported merely because it can start the executable. If you are evaluating a candidate, use the exact package and host details supplied with that authorized build.

### CLI

- Python **3.12 or newer** is required for the source/package installation. The project has been locally tested on CPython 3.14; the shipped CLI uses only the Python standard library at runtime.
- The GUI package bundles a Python runtime, so a separate Python installation is not part of the normal onedir launch steps. The source-launched GUI requires PySide6 in the Python environment; PySide6 is optional and is **not** declared as a project dependency in `pyproject.toml`.
- The CLI code is designed to be cross-platform, but a platform's practical support depends on its Python installation and has not been validated by this Windows GUI candidate test.

## 3. Windows GUI installation and first launch

There is no installer, Start Menu shortcut, service, or automatic updater documented for this build. The onedir format consists of an executable and its `_internal` folder.

1. Obtain the complete onedir folder from an authorized source. Do not use a copied EXE by itself.
2. Extract/copy the complete folder to a location where your Windows account can read and run its contents. Do not rename, delete, or separate `_internal` files.
3. Open the folder and double-click `LogSentinel-GUI.exe`.
4. On first launch, the GUI opens on its configured startup page (Overview by default). No log file is selected automatically.
5. Add one or more log files or a folder, review the effective configuration, and select **Analyze**.
6. When the analysis finishes, review the results. Use **Reports** to save JSON or HTML if needed.

If Windows or endpoint protection displays a warning, do not bypass it automatically. Confirm that the file came from the source you trust and follow your organization's software-handling policy. This guide does not attest to a signature or authorize distribution.

### Launching the GUI from source (developer setup)

The GUI entry point is `python -m logsentinel.gui`, but it needs PySide6 installed in that Python environment and the project source available to Python. PySide6 is optional and is not installed by `pip install .` from the project's declared dependencies. No supported end-user source-install recipe for the GUI is provided here; the onedir package is the intended GUI launch shape when an authorized package is available.

## 4. GUI navigation and five pages

The left sidebar contains five pages. Keyboard shortcuts **Ctrl+1** through **Ctrl+5** select the pages in the same order:

1. **Overview** — the main workspace. Add input files/folders, inspect the current run configuration, and start or cancel analysis. After a completed run, the dashboard shows event and finding counts, severity counts, run statistics, and a capped list of sanitized errors.
2. **Detections** — a sortable findings table. Select a row to see its rule ID, severity, source IP, first/last-seen times, summary, and sanitized evidence excerpts. A completed run with no findings displays an empty-results message.
3. **Log Explorer** — despite its name, this page is **not a raw-line log viewer**. It shows event-processing statistics for the latest completed analysis and directs you to Detections and Reports for evidence and exports.
4. **Reports** — export the latest completed analysis to JSON or HTML. Exports are unavailable before a successful completion, after cancellation/failure, or while the result has been cleared by a new run.
5. **Settings** — save persistent application preferences, choose a theme and startup behavior, set analysis defaults, and choose the preferred export format.

The run controls and input/configuration panels are on Overview. Starting a new run clears the prior result and report-export state. Cancel requests cooperative cancellation; cancelled runs do not show results and cannot be exported.

## 5. Selecting log files and running analysis

### In the GUI

1. On **Overview**, choose **Add Files** to select one or more files, or **Add Folder** to select a directory.
2. The input panel shows selected sources and a discovery summary. Use **Remove Selected** or **Clear All** to change the list.
3. Directory discovery is recursive and includes non-hidden `.log` and `.txt` files. Explicitly selected files are not restricted to those extensions, but the content should still be a supported text log format.
4. Review **Analysis settings**. Load an optional JSON configuration file with **Browse**, adjust individual thresholds, or use **Reset Overrides** to discard temporary field edits. Use **Apply** to validate the effective settings.
5. Select **Analyze**. The GUI processes the files in a background worker and shows coarse progress. Select **Cancel** to request a stop; cleanup may finish before the UI returns to idle.

A file that is missing, unreadable, too large, or otherwise invalid can produce a diagnostic. In normal mode, recoverable errors are reported while processing continues. With strict mode enabled, the first recorded error aborts the run. The default maximum file size is 512 MiB and the default maximum line length is 8,192 characters; both can be changed through Settings or JSON configuration. A line exceeding the limit is treated as malformed.

### Supported input families

The built-in parsers recognize common textual forms of:

- SSH authentication messages in syslog-style logs;
- key/value firewall records containing source/destination addresses, protocol, and destination port; and
- Apache/Nginx common or combined HTTP access logs.

This is not a universal log parser. Lines that do not match a known event format may be counted as malformed; timestamped, unrecognized syslog-style lines can be retained as context-only `othersyslog` events and are not evaluated by the three detection rules. Binary logs and Windows Event Log `.evtx` files are not supported.

## 6. Analysis results, findings, and severity

Each finding is an evidence-backed lead for human review, not a verdict. The current rules use fixed severities; users can tune thresholds but cannot set a custom severity or confidence score.

| Rule | Pattern | Built-in default | Current severity |
|---|---|---:|---|
| `LS-RULE-001` | SSH authentication failures from one source IP within a sliding window | 8 failures in 300 seconds | High |
| `LS-RULE-002` | Distinct destination ports associated with one source IP across the run | 10 ports | Medium |
| `LS-RULE-003` | HTTP responses with status 400–499 from one source IP across the run | 8 responses | Medium |

The SSH window is half-open: an event exactly at the lower boundary is excluded; events through the latest timestamp are included. The port and HTTP rules have no time window in the current implementation. Repeated hits on one destination port do not increase the port count. 2xx/3xx/5xx HTTP statuses do not count toward the 4xx rule.

Findings include summary values and evidence excerpts. The Overview and Log Explorer also show scan statistics such as files scanned, lines read, events parsed, malformed lines, repeated events, and context-only syslog counts. Recoverable error rows are capped at the first 100 entries in displays/reports; the exact total is shown separately when more exist.

Severity describes the rule's fixed category, not certainty, impact, or priority for a particular environment. Legitimate administrators, monitoring tools, scanners, NAT gateways, crawlers, or broken integrations can produce the same patterns. Verify source ownership, operational context, and the original log records before drawing conclusions.

## 7. Exporting JSON and HTML reports

1. Wait for an analysis to complete.
2. Open **Reports** and choose **Export JSON…** or **Export HTML…**.
3. Choose a destination and filename in the save dialog. The application proposes a timestamped `logsentinel-report-…` name and adds the expected `.json` or `.html` extension when needed.
4. Wait for the success message before opening or sharing the saved file.

Both formats describe the latest completed run and include run metadata, configuration, statistics, findings, and a capped error summary. JSON is structured for other tools. HTML is a standalone document intended to open in a browser; it uses embedded styles and does not require a remote asset. Treat either report as sensitive because it contains log-derived summaries and evidence.

Reports are written to the user-selected path. The application does not automatically upload, email, or publish them. A failed save may indicate an invalid destination, missing parent folder, or insufficient write permission; choose a writable path and try again.

## 8. Configuration and settings persistence

### Analysis configuration

Built-in CLI and GUI defaults are:

```text
ssh_threshold        = 8
ssh_window_seconds   = 300
portscan_threshold   = 10
http_4xx_threshold   = 8
strict               = false
max_line_length      = 8192
max_file_mb          = 512
```

All integer values must be positive. A JSON configuration file may contain any of these seven keys and must be valid UTF-8 JSON. Unknown keys or invalid values are rejected. Example:

```json
{
  "ssh_threshold": 8,
  "ssh_window_seconds": 300,
  "portscan_threshold": 10,
  "http_4xx_threshold": 8,
  "strict": false,
  "max_line_length": 8192,
  "max_file_mb": 512
}
```

CLI precedence is **built-in defaults < JSON configuration < explicitly supplied CLI options**. GUI precedence is **built-in defaults < saved application defaults < selected JSON configuration < edited per-analysis fields**. Unedited fields inherit from the lower layer. Loading an invalid JSON file leaves the current valid configuration unchanged.

### Persistent GUI preferences

On Windows, the GUI stores settings in:

```text
%APPDATA%\LogSentinel\settings.json
```

The settings file holds interface preferences (theme, startup/last page, window position/state), analysis defaults, and preferred report format. The available themes are Dark SOC, Light Professional, Midnight, and Cyber Teal. It does not intentionally store selected log paths, raw log content, findings, or credentials. Use **Save Settings** to persist changes. The **Reset to Defaults** action resets application preferences; it does not delete exported reports or original input logs. The theme preview applies immediately, but save it to retain it across launches.

Selected input paths and a loaded JSON config-file path are run/workspace choices, not persistent settings. Exact persistence behavior can vary if the file is missing, malformed, or not writable; the GUI reports that defaults are being used or that saving failed.

## 9. CLI installation and usage

The CLI is independent of the optional GUI. It can be run from a source checkout or installed into a Python environment. The following commands are for **Windows PowerShell**.

### Install in a virtual environment

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\logsentinel.exe --help
```

If the Python launcher command `py -3.12` is unavailable, install Python 3.12+ and use its `python` executable to create the environment. The CLI has no third-party runtime dependencies. `pyproject.toml` declares `setuptools>=68` as a build requirement, so package installation may need that build backend. `pip install .` installs the CLI package and console command into the selected environment; it does not install PySide6. The environment must be activated or its `Scripts` paths used explicitly to run the command.

### Run directly from the checkout

No package installation is required for a source checkout:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m logsentinel --help
python -m logsentinel .\samples\ --json .\report.json --text .\report.txt
$LASTEXITCODE
```

The sample command normally returns exit code **1** because the sample set intentionally triggers findings. Exit code 1 means analysis completed with findings, not that the command failed to run.

### Common CLI examples

```powershell
# Analyze the three shipped sample logs through directory discovery.
python -m logsentinel .\samples\

# Analyze explicit files and save JSON.
python -m logsentinel .\samples\auth.log .\samples\access.log --json .\report.json

# Tune thresholds for this run.
python -m logsentinel .\samples\ --ssh-threshold 5 --ssh-window 120 `
  --portscan-threshold 12 --http-4xx-threshold 10

# Use a JSON config file; stop on the first recorded error and suppress console output.
python -m logsentinel .\logs\ --config .\logsentinel.json --strict --quiet --json .\report.json
```

Useful options include `--config PATH`, `--ssh-threshold N`, `--ssh-window SECONDS`, `--portscan-threshold N`, `--http-4xx-threshold N`, `--json PATH`, `--text PATH`, `--strict`, `--quiet`, `--version`, and `--help`. At least one input path is required. Explicit file paths are processed regardless of filename extension; directory discovery scans non-hidden `.log` and `.txt` files recursively.

### CLI exit codes

| Code | Meaning |
|---:|---|
| 0 | Run completed with no findings. If no files were discovered and there were no discovery errors, the CLI warns that there was nothing to analyze. |
| 1 | Run completed and one or more findings were produced. |
| 2 | Usage, configuration, report-writing, or input failure that prevented analysis; also the result of strict-mode abort. |
| 3 | Unexpected runtime failure. The CLI prints a short diagnostic; no partial report is promised. |

Normal mode records recoverable input and parsing problems and continues where possible. Strict mode aborts on the first recorded error. `--quiet` suppresses the console report; requested report files are still written.

## 10. Samples and examples

The repository's `samples/` directory contains synthetic demonstration inputs:

| File | Demonstrates |
|---|---|
| `samples/auth.log` | SSH failures sufficient for `LS-RULE-001`, plus context, boundary, and malformed-input examples. |
| `samples/firewall.log` | Multiple destination ports sufficient for `LS-RULE-002`, including an identical repeated line. |
| `samples/access.log` | HTTP 4xx activity sufficient for `LS-RULE-003`, alongside statuses that do not count for that rule. |

The valid sample IP addresses are documentation-range addresses; `auth.log` also contains an intentionally invalid IP as malformed test data. A default analysis of all three samples is expected to produce three findings: one high-severity SSH finding and two medium-severity findings. The sample data is for learning and smoke checks, not a representative production baseline.

## 11. Troubleshooting

| Symptom | What to check |
|---|---|
| GUI executable does not start or reports a missing DLL/plugin | Confirm you extracted the entire onedir folder and kept `_internal` alongside the EXE. Do not copy or rename the EXE alone. The tested candidate does not establish compatibility on every Windows configuration. |
| GUI has no input sources or Analyze is disabled | Add at least one readable file/folder and resolve any configuration validation message. Directory discovery only includes non-hidden `.log`/`.txt` files. |
| Folder is added but no log files are found | Check the chosen directory and its descendants for non-hidden `.log` or `.txt` files. Explicitly add a file if it has another extension. |
| A file is rejected or skipped | Check it exists, is readable text, is not larger than the configured size cap, and is not a directory symlink. Review the run's sanitized diagnostics. |
| Most lines are malformed | The parser recognizes only the documented SSH, firewall key/value, and Apache/Nginx access-log patterns. Confirm timestamp and field layout; binary and `.evtx` inputs are unsupported. |
| No finding appears | Check that events parsed into the expected family and source IP, thresholds, and SSH window. Port and HTTP rules have no time window. A finding is not produced for every unusual line. |
| Strict mode stops the run | Strict mode intentionally aborts on the first recorded input or parse error. Correct the input/configuration or turn strict mode off for a best-effort batch. |
| JSON configuration is rejected | Ensure it is UTF-8 JSON, uses only the seven documented keys, has positive integer limits/thresholds, and uses a JSON boolean (`true`/`false`) for `strict`. |
| Report export fails | Choose a writable destination with an existing parent folder and enough available disk space. Confirm the destination is not locked by another application. |
| `No module named logsentinel` in source mode | Run from the repository root with `$env:PYTHONPATH = "$PWD\src"`, or install the package into the active Python environment. |
| `No module named PySide6` when launching source GUI | The source GUI requires optional PySide6 in that interpreter. It is not included in the project's declared runtime dependencies; use a properly prepared environment or authorized onedir package. |
| PowerShell command finds no `logsentinel` command | Activate the virtual environment or invoke `\.venv\Scripts\logsentinel.exe` (or the environment's equivalent path). |
| Windows console shows incorrect non-ASCII characters | Try a terminal configured for UTF-8, for example `chcp 65001`, or set `$env:PYTHONIOENCODING = "utf-8"` for that PowerShell session. |

## 12. Data handling, privacy, and security limitations

- LogSentinel is designed for local/offline analysis and does not intentionally make network connections, upload logs, or send telemetry. It does not acquire logs from other systems. This is a description of the implemented application path, not a security certification of the host, Python environment, or surrounding software.
- Input files are opened read-only by the analysis pipeline; LogSentinel does not intentionally modify the source logs. The CLI writes only report paths requested by the user. The GUI writes exported reports only after the user chooses a destination.
- Analysis uses temporary SQLite staging under the operating system's temporary directory. Normal completion/cancellation cleans up staging, but an abnormal termination or filesystem failure can leave temporary data behind. A later application initialization may clean eligible abandoned run data; cleanup cannot be guaranteed in every failure scenario.
- Reports and on-screen evidence contain sanitized log-derived data. Recognized credential-shaped values and source paths are redacted by the existing report pipeline, and evidence excerpts are limited in length. **Redaction is pattern-based and best-effort, not universal secret detection.** Unknown field names, unkeyed secrets, unusual encodings, multiline values, or other unrecognized forms can remain in reports or temporary processing data.
- Do not use LogSentinel on secret-bearing logs unless you have assessed that risk and trust the machine, account, storage, and report destination. Restrict access to input, temporary, settings, and report files according to your own requirements. Review exported content before sharing it.
- GUI settings are preferences, not a secure secret store. The settings file is not designed to contain credentials or logs. Deleting it removes saved preferences but does not remove reports or inputs.
- Findings are not security alerts or automated responses. LogSentinel does not block, quarantine, attribute, or confirm malicious activity.

## 13. Uninstallation and cleanup

### GUI onedir folder

Close LogSentinel, then delete the complete extracted application folder. There is no GUI uninstaller in this build. If you also want to remove saved GUI preferences, delete:

```powershell
Remove-Item -LiteralPath "$env:APPDATA\LogSentinel\settings.json" -Force -ErrorAction SilentlyContinue
```

This command does not delete exported reports, original logs, or possible temporary data left by an abnormal termination. Review and remove those separately only if appropriate. Do not remove files from unrelated application folders.

### CLI virtual environment

If the CLI was installed into the dedicated `.venv` shown above, close shells using it and remove that environment from the repository root:

```powershell
Remove-Item -LiteralPath .\.venv -Recurse -Force
```

This deletes packages in that virtual environment. If installed into a shared environment instead, activate that same environment and run `python -m pip uninstall logsentinel`; do not remove a shared environment wholesale. CLI operation does not create the GUI settings file.

## 14. Known limitations and possible future work

Current limitations include:

- batch file analysis only; no live tailing, collection/agents, scheduled scans, alerts, blocking, or incident response;
- only the three built-in SSH, firewall-port, and HTTP 4xx statistical rules; no custom rules engine, ML/anomaly scoring, confidence score, or severity tuning;
- IPv4 only; no Windows Event Log/`.evtx`, cloud-log ingestion, compressed archive, SIEM, CEF/LEEF/OTLP, or external enrichment support;
- parser coverage is limited to supported textual formats and variants; malformed and unrecognized records may be omitted from detection;
- port breadth and HTTP 4xx counts span the whole run without a time window; SSH is the only rule with a sliding window;
- path deduplication and cross-file content deduplication have documented limits; separate aliases or mirrored legitimate records can affect counts;
- memory use can grow with activity attributed to a source IP and retained evidence; streaming does not mean constant memory;
- secret redaction is best-effort; inspect reports and protect temporary/report files;
- the GUI's tested Windows host and workflow do not establish a broad supported Windows matrix, installer, upgrade mechanism, or general production readiness.

Future enhancements such as more parsers, additional rules, richer platform testing, installers, and operational integrations are not part of the current Phase 1 behavior and should not be assumed to exist.

## Further reading

- [CLI usage and configuration reference](USAGE.md)
- [Detection rule details and false-positive guidance](DETECTION_RULES.md)
