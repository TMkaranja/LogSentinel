# -*- mode: python ; coding: utf-8 -*-
"""One-directory, windowed PyInstaller specification for the LogSentinel GUI.

This is the one-directory counterpart of packaging/LogSentinel-GUI.spec. The
only structural difference is the packaging mode: EXE receives no binaries or
data and sets exclude_binaries=True, and a COLLECT step writes the runtime tree
(_internal/) next to the executable. Everything else - entry point, icon,
assets, dependency collection, hooks and the Qt Virtual Keyboard exclusion with
its guards - is intentionally identical to the one-file specification.
"""

from pathlib import Path


# PyInstaller defines SPECPATH while evaluating a spec file. Resolve every
# input from the project root, rather than relying on the caller's cwd.
PROJECT_ROOT = Path(SPECPATH).resolve().parent
SOURCE_ROOT = PROJECT_ROOT / "src"
ENTRY_POINT = PROJECT_ROOT / "packaging" / "gui_entry.py"
ASSET_ROOT = SOURCE_ROOT / "logsentinel" / "gui" / "assets"
WINDOWS_ICON = ASSET_ROOT / "logsentinel.ico"

if not ENTRY_POINT.is_file():
    raise FileNotFoundError(f"GUI entry point not found: {ENTRY_POINT}")
if not WINDOWS_ICON.is_file():
    raise FileNotFoundError(f"Windows application icon not found: {WINDOWS_ICON}")

# Keep paths relative to the package asset root so icons.py can find files at
# logsentinel/gui/assets/{icons,brand} in both source and frozen execution.
asset_files = sorted(
    path for path in ASSET_ROOT.rglob("*")
    if path.is_file() and path.suffix.lower() in {".svg", ".ico"}
)
svg_files = [path for path in asset_files if path.suffix.lower() == ".svg"]
if len(svg_files) != 22:
    raise RuntimeError(
        f"Expected 22 GUI SVG assets under {ASSET_ROOT}, found {len(svg_files)}")

asset_datas = [
    (
        str(path),
        (Path("logsentinel") / "gui" / "assets"
         / path.relative_to(ASSET_ROOT).parent).as_posix(),
    )
    for path in asset_files
]

analysis = Analysis(
    [str(ENTRY_POINT)],
    pathex=[str(SOURCE_ROOT)],
    binaries=[],
    datas=asset_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Qt Virtual Keyboard is GPLv3-only and unused by LogSentinel. PyInstaller's
# QtGui hook copies the whole "platforminputcontexts" plugin category, which
# contains only qtvirtualkeyboardplugin.dll; binary dependency analysis then
# pulls in Qt6VirtualKeyboard.dll and, through it, the QML/Quick/OpenGL stack.
# LogSentinel imports none of them, ships no QML payload, and never selects the
# virtual keyboard input method. PyInstaller 6.22.3 exposes no hooksconfig switch
# for Qt plugin categories, so the entries are removed from the final TOCs here.
# Only components whose *sole* importer is this stack are listed; every bundled
# native module's import table was inspected to confirm that (Step 9.3.2).
EXCLUDED_PLUGIN_CATEGORIES = ("plugins/platforminputcontexts/",)
EXCLUDED_BINARIES = {
    "pyside6/qt6virtualkeyboard.dll",
    "pyside6/qt6qml.dll",
    "pyside6/qt6quick.dll",
    "pyside6/qt6qmlmeta.dll",
    "pyside6/qt6qmlmodels.dll",
    "pyside6/qt6qmlworkerscript.dll",
    "pyside6/qt6opengl.dll",
}


def _is_excluded(dest, typecode):
    normalized = str(dest).replace("\\", "/").lower()
    if any(category in normalized for category in EXCLUDED_PLUGIN_CATEGORIES):
        return True
    return typecode in {"BINARY", "EXTENSION"} and normalized in EXCLUDED_BINARIES


def _without_virtual_keyboard(entries):
    kept = []
    removed = []
    for entry in entries:
        dest, source, typecode = entry[0], entry[1], entry[2]
        if _is_excluded(dest, typecode):
            removed.append(dest)
        else:
            kept.append(entry)
    return kept, removed


remaining_binaries, removed_binaries = _without_virtual_keyboard(analysis.binaries)
remaining_datas, removed_datas = _without_virtual_keyboard(analysis.datas)

# The exclusion must actually take effect: 1 plugin + 7 Qt libraries are expected,
# and nothing excluded may survive in the TOC that EXE and COLLECT receive.
if len(removed_binaries) != len(EXCLUDED_BINARIES) + 1:
    raise RuntimeError(
        "Expected to exclude 8 Qt Virtual Keyboard components, removed "
        f"{len(removed_binaries)}: {sorted(removed_binaries)}")
for entry in remaining_binaries + remaining_datas:
    if _is_excluded(entry[0], entry[2]):
        raise RuntimeError(f"Excluded Qt Virtual Keyboard component survived: {entry[0]}")

for dest in sorted(removed_binaries + removed_datas):
    print(f"[LogSentinel] excluded Qt Virtual Keyboard component: {dest}")

# QtGui's hook collects every imageformats plugin, including qpdf.dll; its
# import then pulls in Qt6Pdf.dll. PyInstaller also adds opengl32sw.dll as an
# optional Windows Qt binary. LogSentinel has no PDF or OpenGL/Qt Quick UI.
# Keep this to exact destination paths: the rest of imageformats includes the
# required ICO/SVG handlers. Mesa's software OpenGL fallback is intentionally
# excluded; revisit this if future features use OpenGL, Qt Quick, or QRhi.
EXCLUDED_UNUSED_QT_BINARIES = {
    "pyside6/qt6pdf.dll",
    "pyside6/plugins/imageformats/qpdf.dll",
    "pyside6/opengl32sw.dll",
}


def _without_unused_qt_binaries(entries):
    kept = []
    removed = []
    for entry in entries:
        dest, source, typecode = entry[0], entry[1], entry[2]
        normalized = str(dest).replace("\\", "/").lower()
        if typecode == "BINARY" and normalized in EXCLUDED_UNUSED_QT_BINARIES:
            removed.append(normalized)
        else:
            kept.append(entry)
    return kept, removed


remaining_binaries, removed_unused_qt = _without_unused_qt_binaries(remaining_binaries)
if set(removed_unused_qt) != EXCLUDED_UNUSED_QT_BINARIES or len(removed_unused_qt) != 3:
    raise RuntimeError(
        "Expected to exclude exactly Qt6Pdf.dll, qpdf.dll, and opengl32sw.dll; "
        f"removed {sorted(removed_unused_qt)}")
for entry in remaining_binaries + remaining_datas:
    normalized = str(entry[0]).replace("\\", "/").lower()
    if entry[2] == "BINARY" and normalized in EXCLUDED_UNUSED_QT_BINARIES:
        raise RuntimeError(f"Excluded unused Qt binary survived: {entry[0]}")

# Guard the image handlers, Windows platform backends, and primary widgets stack
# against accidental broadening of the exact-path filter above.
REQUIRED_QT_DESTINATIONS = {
    "pyside6/qt6core.dll",
    "pyside6/qt6gui.dll",
    "pyside6/qt6svg.dll",
    "pyside6/qt6widgets.dll",
    "pyside6/plugins/imageformats/qico.dll",
    "pyside6/plugins/imageformats/qsvg.dll",
    "pyside6/plugins/iconengines/qsvgicon.dll",
    "pyside6/plugins/platforms/qwindows.dll",
    "pyside6/plugins/platforms/qdirect2d.dll",
    "pyside6/plugins/platforms/qminimal.dll",
    "pyside6/plugins/platforms/qoffscreen.dll",
    "pyside6/plugins/styles/qmodernwindowsstyle.dll",
}
remaining_destinations = {
    str(entry[0]).replace("\\", "/").lower()
    for entry in remaining_binaries
}
missing_required_qt = REQUIRED_QT_DESTINATIONS - remaining_destinations
if missing_required_qt:
    raise RuntimeError(
        f"Required Qt binaries/plugins missing after exclusions: {sorted(missing_required_qt)}")

for dest in sorted(removed_unused_qt):
    print(f"[LogSentinel] excluded unused Qt binary: {dest}")

analysis.binaries = remaining_binaries
analysis.datas = remaining_datas

pyz = PYZ(analysis.pure)

# One-directory mode: the executable carries only the bootloader and the Python
# archive; libraries, plugins, translations and assets are collected by COLLECT
# into the _internal directory that sits next to the executable.
exe = EXE(
    pyz,
    analysis.scripts,
    [],
    [],
    exclude_binaries=True,
    name="LogSentinel-GUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(WINDOWS_ICON)],
)

coll = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="LogSentinel-GUI",
)
