# Compatibility risk assessment: Qt PDF and Mesa exclusions

**Scope:** Read-only assessment of `dist/gui-ondir-trim-test/LogSentinel-GUI/`, the
one-directory GUI package built with exact-path exclusions for
`PySide6/Qt6Pdf.dll`, `PySide6/plugins/imageformats/qpdf.dll`, and
`PySide6/opengl32sw.dll`. The package fingerprint at assessment time is 182 files,
80,058,228 bytes; executable SHA-256 begins `3f5e10bb1511125b…`.

The trimmed package previously passed a full standard-desktop workflow: all five
pages, `samples/auth.log` analysis, JSON/HTML exports, settings persistence across
relaunch, and clean shutdown. No excluded DLL was in the process module list during
those workflows. **This is not evidence of compatibility on RDP, GPU-less systems,
or high-DPI configurations.** No legal compliance conclusion is made.

## Evidence examined

- GUI imports and feature code under `src/logsentinel/gui/`, plus
  `packaging/gui_entry.py`: Qt Core, Gui, Widgets and Svg are used. `icons.py` uses
  `QSvgRenderer`, `QPainter`, `QPixmap` and `QIcon` for SVG icons and theme previews.
  No imports or source references to QtPdf, QtPrintSupport, QtOpenGL,
  QtOpenGLWidgets, QtQuick, QML, `QOpenGLWidget`, `QSurfaceFormat`, or
  `QGraphicsView`; no PDF viewing/export or print action is implemented. Reports
  are JSON and HTML.
- `packaging/LogSentinel-GUI-Onedir.spec`: three exact, case-normalized binary
  destination exclusions with count/survival guards; no `imageformats` category
  exclusion. The spec says Mesa's software-OpenGL fallback is intentionally
  excluded and future OpenGL/Qt Quick/QRhi features must revisit the choice. It
  also guards presence of Qt Core/Gui/Svg/Widgets, qico/qsvg/qsvgicon, Windows
  platform plugins and qmodernwindowsstyle.
- Trimmed package paths: the three named files are absent. `qico.dll`, `qsvg.dll`,
  `qsvgicon.dll`, `qwindows.dll`, `qdirect2d.dll`, `qminimal.dll`, `qoffscreen.dll`
  and `qmodernwindowsstyle.dll` remain. QtOpenGL, QtQuick, QtQml and QtPrintSupport
  are not present.
- Recorded end-to-end evidence in
  `C:\Users\DELL\AppData\Local\Temp\logsentinel-ondir-trim-e2e-run10.log`:
  standard desktop launch, page traversal, analysis, exports, persistence and
  close passed. `Get-Process.Modules` showed Qt6Core/Gui/Svg/Widgets, qwindows and
  qmodernwindowsstyle loaded; no Qt6Pdf, qpdf or opengl32sw. The app's redirected
  stdout/stderr files were empty (0 bytes); this means no warning was captured,
  not that all Qt loader diagnostics are observable in this windowed build.
- Qt plugin/environment references: source and spec do not set or consume
  `QT_OPENGL`, `QT_OPENGL_DLL`, `QT_QPA_PLATFORM`, `QT_SCALE_FACTOR`, or a
  software-OpenGL attribute. Qt's Windows `qwindows.dll` contains dynamic-loader
  references to `opengl32sw.dll`, `QT_OPENGL` and `QT_OPENGL_DLL`; those are Qt
  runtime paths, not application imports. An inherited user/system environment
  setting may therefore affect a future/current GL consumer even though LogSentinel
  itself does not request a GL context.
- The previous packaging audit found no explicit `dpiAware` manifest entry. No
  high-DPI test was run for this assessment.

## Risk table

Risk means compatibility risk **introduced by these exclusions**, not general
product risk. “Untested” is stated separately from the classification.

| Environment / feature area | Risk | Evidence and interpretation | Test status |
|---|---|---|---|
| Standard Windows desktop, current GUI | **Low** | The complete existing workflow passed with all three files absent. Qt widgets, SVG/icon rendering, themes, analysis and both exports worked; required platform/style/image plugins remained. | **Tested** on the current standard desktop session only. |
| Windows Remote Desktop (RDP), current GUI | **Medium** | No app feature requests OpenGL, and standard Windows widget rendering worked without Mesa. RDP can change available display/OpenGL paths; Qt's dynamic loader still knows about the software DLL. No RDP run proves the raster/widgets path stays selected or that no user environment forces software GL. | **Not tested.** |
| GPU-less / software-rendering host, current GUI | **Medium** | The missing Mesa DLL is Qt's fallback software OpenGL renderer, but this application has no OpenGL/Qt Quick feature and standard-session module evidence showed it was not used. A GPU-less host can still expose different Qt platform behavior; a user-set `QT_OPENGL=software`/`QT_OPENGL_DLL` may explicitly request the missing fallback. | **Not tested.** Do not claim compatibility. |
| High-DPI displays / Windows scaling | **Low direct exclusion risk; overall compatibility unverified** | PDF and Mesa are not DPI-scaling components. The app uses Qt Widgets and SVG icons, and the standard session rendered them. Qt 6 normally handles device scaling, but there is no high-DPI run and the earlier audit noted no explicit `dpiAware` manifest entry; any scaling/blur issue may be independent of these exclusions. | **Not tested** at 125/150/200% or across mixed-DPI displays. |
| Current PDF rendering / PDF image loading | **Low** | No PDF UI, `QPdf*` imports or PDF export exists. qpdf was collected as a QtGui `imageformats` plugin, not for a current feature. JSON/HTML are the only report formats. | Current functional workflow tested; PDF-specific paths intentionally not exercised. |
| Current printing | **Low** | No QtPrintSupport import, print action, printer workflow or PrintSupport module in the package. | No print workflow exists to test. |
| Future PDF view/export, PDF image decode, or printing feature | **High** | The excluded `Qt6Pdf.dll`/`qpdf.dll` provide the PDF module and PDF image handler; QtPrintSupport is also absent. Such a feature would fail or be unavailable until dependency collection and packaging are deliberately revisited. | Not applicable until feature work. |
| Future OpenGL / Qt Quick / QML / QRhi feature | **High** | The current package intentionally lacks `opengl32sw.dll` and, due to the existing Virtual Keyboard exclusion, QtOpenGL/QtQuick/QtQml components. The spec explicitly requires revisiting this decision. On systems without usable hardware OpenGL, Mesa removal can remove the fallback. | Not applicable until feature work. |

## Confirmed findings vs. untested assumptions

**Confirmed:** the currently shipped GUI source has no PDF, printing, OpenGL, Qt Quick
or QML feature/import; JSON/HTML are its report formats. The exact excluded files
are absent from the trimmed package while qico, SVG handlers and Windows
platform/style plugins remain. A standard desktop end-to-end run passed, and none
of the excluded module names appeared in the loaded-module list.

**Not established:** whether RDP or a GPU-less host causes Qt to request Mesa for
this widget-only UI; behavior when `QT_OPENGL=software`, `QT_OPENGL_DLL`, or a
custom QPA platform is inherited; high-DPI layout/clarity; and any future PDF,
print or GL feature. Empty stdout/stderr means no diagnostic was captured, not
that Qt could not silently attempt a dynamic load.

## Tests still required before release

1. Run the full GUI workflow on an actual supported Windows Remote Desktop session,
   with the same isolated profile/export safeguards; capture loaded modules and
   Qt/plugin diagnostics.
2. Run on a VM or host with no hardware OpenGL driver (and separately test with
   `QT_OPENGL=software` only if that environment setting is within the supported
   product contract). Record whether startup or widgets attempt to load the absent
   DLL and whether Qt reports errors.
3. Test 125%, 150% and 200% scaling, plus a mixed-DPI monitor move; verify all five
   pages, SVG/icon rendering, themes, dialogs and export layouts. Review manifest
   DPI awareness separately because that concern is not caused by these exclusions.
4. If PDF viewing/decoding, printing, Qt Quick, QML, OpenGL or QRhi is introduced,
   restore/re-evaluate the corresponding Qt modules/plugins and software renderer,
   then repeat packaging and functional tests before shipping.

## Recommendation

**Keep the three exact-path exclusions provisionally in place** for the current
feature set: standard-desktop functional evidence is strong, and no present feature
uses these components. Do not widen the filters. Treat release approval as
conditional on RDP, GPU-less/software-rendering and high-DPI tests, plus an explicit
revisit whenever a listed future feature is added. This is a provisional
compatibility recommendation, not a claim of broad Windows compatibility.
