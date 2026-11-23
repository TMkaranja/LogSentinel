"""Theme engine, typography, and application chrome for LogSentinel.

The original shell used a single dark stylesheet. This module keeps that
infrastructure but makes every semantic colour token theme-driven:

    Theme definitions (Qt-free) -> Qt palette + stylesheet + local SVG icons

Four themes are supported: Dark SOC (default), Light Professional, Midnight,
and Cyber Teal. All widgets use the same semantic tokens; no page maintains a
private colour palette. PySide6 remains isolated inside the GUI package.
"""

from __future__ import annotations

import re

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

from .icons import brand_icon
from .themes import (
    DEFAULT_THEME_KEY,
    THEME_KEYS,
    THEME_LABELS,
    THEMES,
    Theme,
    get_theme,
    theme_label,
)

APP_NAME = "LogSentinel"
APP_TAGLINE = "DEFENSIVE LOG INTELLIGENCE"
APP_ORGANIZATION = "LogSentinel"
APP_WINDOW_TITLE = f"{APP_NAME} — Defensive Log Analysis"

FONT_SANS_FAMILIES = (
    "Inter",
    "Segoe UI",
    "Noto Sans",
    "Helvetica Neue",
    "Arial",
    "sans-serif",
)
FONT_MONO_FAMILIES = (
    "JetBrains Mono",
    "Cascadia Mono",
    "Consolas",
    "SFMono-Regular",
    "Menlo",
    "Liberation Mono",
    "Courier New",
    "monospace",
)
FONT_SANS_CSS = ", ".join(f'"{name}"' if " " in name else name
                          for name in FONT_SANS_FAMILIES)
FONT_MONO_CSS = ", ".join(f'"{name}"' if " " in name else name
                          for name in FONT_MONO_FAMILIES)

#: Default dark aliases kept for embedding/tests and older callers.
COLOR_BACKGROUND = THEMES[DEFAULT_THEME_KEY].background
COLOR_SIDEBAR = THEMES[DEFAULT_THEME_KEY].sidebar
COLOR_SURFACE = THEMES[DEFAULT_THEME_KEY].surface
COLOR_SURFACE_RAISED = THEMES[DEFAULT_THEME_KEY].surface_raised
COLOR_BORDER = THEMES[DEFAULT_THEME_KEY].border
COLOR_BORDER_STRONG = THEMES[DEFAULT_THEME_KEY].border_strong
COLOR_TEXT = THEMES[DEFAULT_THEME_KEY].text
COLOR_TEXT_MUTED = THEMES[DEFAULT_THEME_KEY].text_muted
COLOR_TEXT_DIM = THEMES[DEFAULT_THEME_KEY].text_dim
COLOR_ACCENT = THEMES[DEFAULT_THEME_KEY].accent
COLOR_ACCENT_STRONG = THEMES[DEFAULT_THEME_KEY].accent_strong
COLOR_BLUE = THEMES[DEFAULT_THEME_KEY].blue
COLOR_SUCCESS = THEMES[DEFAULT_THEME_KEY].success
COLOR_WARNING = THEMES[DEFAULT_THEME_KEY].warning
COLOR_DANGER = THEMES[DEFAULT_THEME_KEY].danger

#: Compatibility default; live widgets use severity_colors() so the
#: calibrated per-theme values stay readable in all four appearances.
SEVERITY_COLORS: dict[str, str] = dict(
    THEMES[DEFAULT_THEME_KEY].severity_colors)


class ThemeManager(QObject):
    """Small application-wide notifier for icon and severity refreshes."""

    changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._key = DEFAULT_THEME_KEY

    @property
    def key(self) -> str:
        return self._key

    def set_theme(self, key: str) -> None:
        theme = get_theme(key)
        if theme.key == self._key:
            return
        self._key = theme.key
        self.changed.emit(theme.key)


theme_manager = ThemeManager()


def current_theme() -> Theme:
    return get_theme(theme_manager.key)


def severity_colors() -> dict[str, str]:
    return current_theme().severity_colors


# Every dark token used by the original stylesheet has one semantic mapping.
# Keeping the base QSS as a single source of truth avoids duplicating complete
# stylesheets for each theme.
_DARK_TO_TOKEN: dict[str, str] = {
    "#03060c": "shadow",
    "#050912": "shadow",
    "#06111f": "logo_foreground",
    "#070c16": "background",
    "#08101d": "code_bg",
    "#08121f": "code_bg",
    "#0a111f": "header",
    "#0a1220": "sidebar",
    "#0b1524": "input",
    "#0b1e2e": "hero_start",
    "#0b2b36": "accent_soft",
    "#0c1524": "surface",
    "#0c1a2b": "run_start",
    "#0d1728": "pressed",
    "#0e1727": "surface",
    "#0e192b": "surface_raised",
    "#0e1a2c": "surface_alt",
    "#0f1b2e": "surface_alt",
    "#101a2d": "hero_end",
    "#101c31": "hover",
    "#10243a": "selection",
    "#121e33": "surface_raised",
    "#12334a": "selection",
    "#155e6b": "accent_border",
    "#16243a": "row_border",
    "#1a2942": "grid",
    "#1a2a3f": "disabled_bg",
    "#1d4e63": "accent_border",
    "#1e2d47": "border",
    "#22c55e": "success",
    "#22d3ee": "accent",
    "#233552": "scroll",
    "#241b0b": "warning_soft",
    "#243653": "control_border",
    "#2563eb": "blue",
    "#263959": "empty_border",
    "#2a3d5c": "border_strong",
    "#2dd4bf": "accent",
    "#2f466b": "scroll_hover",
    "#38bdf8": "accent_strong",
    "#3b82f6": "blue",
    "#4ade80": "success",
    "#4f6483": "text_dim",
    "#5c4415": "warning_border",
    "#5d7394": "disabled_text",
    "#637896": "text_dim",
    "#67e8f9": "accent_strong",
    "#6f84a5": "text_muted",
    "#6f86a8": "text_muted",
    "#7f93b3": "text_muted",
    "#8ca1c1": "text_muted",
    "#9fb2cf": "text_soft",
    "#c8d8ee": "text_soft",
    "#dce8fa": "text",
    "#e8f0ff": "text",
    "#e9f8ff": "text",
    "#ef4444": "danger",
    "#f1f6ff": "text",
    "#f4f9ff": "selection_text",
    "#f59e0b": "warning",
    "#f87171": "danger",
    "#fbbf24": "warning",
}

_BASE_STYLESHEET = """
/* Typography scale: 14px base, 13px body, 12px metadata, 11px labels.
   Technical values use the mono stack at 12px for comfortable scanning. */
QWidget {
    background: transparent;
    color: #e8f0ff;
    font-family: __FONT_SANS__;
    font-size: 14px;
}

QMainWindow, #AppContainer, #Workspace {
    background-color: #070c16;
}

#Sidebar {
    background-color: #0a1220;
    border-right: 1px solid #1e2d47;
}

#BrandMark {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #22d3ee, stop:1 #2563eb);
    border: 1px solid #67e8f9;
    border-radius: 12px;
    color: #06111f;
    font-size: 17px;
    font-weight: 800;
}

#BrandName {
    color: #f1f6ff;
    font-size: 19px;
    font-weight: 700;
}

#BrandTagline {
    color: #6f86a8;
    font-size: 10px;
    font-weight: 700;
}

#SectionLabel {
    color: #5d7394;
    font-size: 11px;
    font-weight: 700;
}

QPushButton#NavButton {
    background: transparent;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 8px;
    color: #9fb2cf;
    font-size: 14px;
    font-weight: 600;
    min-height: 44px;
    padding: 0 14px;
    text-align: left;
}

QPushButton#NavButton:hover {
    background-color: #101c31;
    color: #e8f0ff;
}

QPushButton#NavButton:pressed {
    background-color: #0d1728;
}

QPushButton#NavButton:checked {
    background-color: #10243a;
    border-left: 3px solid #22d3ee;
    color: #e9f8ff;
}

#SidebarFooter {
    background-color: #0e192b;
    border: 1px solid #1e2d47;
    border-radius: 12px;
}

#StatusDot {
    background-color: #22c55e;
    border-radius: 4px;
    min-width: 8px;
    max-width: 8px;
    min-height: 8px;
    max-height: 8px;
}

#FooterTitle {
    color: #c8d8ee;
    font-size: 12px;
    font-weight: 700;
}

#FooterText {
    color: #6f86a8;
    font-size: 11px;
}

#FooterVersion {
    color: #4f6483;
    font-size: 10px;
    font-weight: 600;
}

#HeaderBar {
    background-color: #0a111f;
    border-bottom: 1px solid #1e2d47;
}

#PageTitle {
    color: #f1f6ff;
    font-size: 28px;
    font-weight: 700;
}

#PageSubtitle {
    color: #8ca1c1;
    font-size: 13px;
}

#Chip, #StatusPill {
    background-color: #0f1b2e;
    border: 1px solid #243653;
    border-radius: 10px;
    color: #9fb2cf;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
}

#ChipAccent, #StatusPillAccent {
    background-color: #0b2b36;
    border: 1px solid #155e6b;
    border-radius: 10px;
    color: #67e8f9;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 10px;
}

#ChipPending {
    background-color: #241b0b;
    border: 1px solid #5c4415;
    border-radius: 9px;
    color: #fbbf24;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
}

#Card {
    background-color: #0e1727;
    border: 1px solid #1e2d47;
    border-radius: 14px;
}

#HeroCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 #0b1e2e, stop:0.58 #0d1728,
                                stop:1 #101a2d);
    border: 1px solid #1d4e63;
    border-radius: 16px;
}

#CardTitle {
    color: #7f93b3;
    font-size: 11px;
    font-weight: 700;
}

#CardValue {
    color: #f1f6ff;
    font-size: 34px;
    font-weight: 700;
}

#CardHint {
    color: #6f84a5;
    font-size: 12px;
}

#HeroEyebrow {
    color: #67e8f9;
    font-size: 11px;
    font-weight: 700;
}

#HeroTitle {
    color: #f4f9ff;
    font-size: 30px;
    font-weight: 700;
}

#HeroText {
    color: #9fb2cf;
    font-size: 14px;
}

#SectionHeading {
    color: #dce8fa;
    font-size: 17px;
    font-weight: 700;
}

#BodyText {
    color: #9fb2cf;
    font-size: 13px;
}

#MutedLabel {
    color: #637896;
    font-size: 12px;
}

#EmptyState {
    background-color: #0c1524;
    border: 1px dashed #263959;
    border-radius: 14px;
}

#EmptyIcon {
    color: #2dd4bf;
    font-size: 34px;
    font-weight: 700;
}

#EmptyTitle {
    color: #e8f0ff;
    font-size: 18px;
    font-weight: 700;
}

#EmptyText {
    color: #7f93b3;
    font-size: 13px;
}

#RuleId {
    color: #67e8f9;
    font-size: 11px;
    font-weight: 700;
}

#RuleTitle {
    color: #e8f0ff;
    font-size: 14px;
    font-weight: 700;
}

#RuleText {
    color: #7f93b3;
    font-size: 12px;
}

#PageContainer {
    background-color: #070c16;
}

QScrollArea {
    background: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background: transparent;
}

QScrollBar:vertical {
    background: #08101d;
    border: none;
    margin: 0;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #233552;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #2f466b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    width: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

QStatusBar {
    background-color: #0a111f;
    border-top: 1px solid #1e2d47;
    color: #7f93b3;
    font-size: 12px;
}

QStatusBar::item {
    border: none;
}

QToolTip {
    background-color: #101c31;
    border: 1px solid #2a3d5c;
    border-radius: 6px;
    color: #e8f0ff;
    font-size: 13px;
    padding: 6px 9px;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #0b1524;
    border: 1px solid #243653;
    border-radius: 8px;
    color: #e8f0ff;
    min-height: 34px;
    padding: 0 11px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #22d3ee;
}

QTableView, QTreeView, QListView {
    background-color: #0b1524;
    alternate-background-color: #0e1a2c;
    border: 1px solid #1e2d47;
    border-radius: 10px;
    color: #dce8fa;
    gridline-color: #1a2942;
    selection-background-color: #12334a;
    selection-color: #f4f9ff;
}

QHeaderView::section {
    background-color: #0e1a2c;
    border: none;
    border-bottom: 1px solid #243653;
    color: #8ca1c1;
    font-size: 11px;
    font-weight: 700;
    padding: 9px 12px;
}

QPushButton#PrimaryButton {
    background-color: #22d3ee;
    border: 1px solid #67e8f9;
    border-radius: 8px;
    color: #06111f;
    font-size: 14px;
    font-weight: 700;
    min-height: 36px;
    padding: 0 17px;
}

QPushButton#PrimaryButton:hover {
    background-color: #67e8f9;
}

QPushButton#PrimaryButton:disabled {
    background-color: #1a2a3f;
    border-color: #243653;
    color: #5d7394;
}

QPushButton#GhostButton {
    background-color: transparent;
    border: 1px solid #2a3d5c;
    border-radius: 8px;
    color: #9fb2cf;
    font-size: 14px;
    font-weight: 600;
    min-height: 36px;
    padding: 0 17px;
}

QPushButton#GhostButton:hover {
    background-color: #101c31;
    color: #e8f0ff;
}

QCheckBox {
    color: #c8d8ee;
    font-size: 13px;
    spacing: 9px;
}

QCheckBox::indicator {
    background-color: #0b1524;
    border: 1px solid #2a3d5c;
    border-radius: 4px;
    width: 17px;
    height: 17px;
}

QCheckBox::indicator:hover {
    border-color: #22d3ee;
}

QCheckBox::indicator:checked {
    background-color: #22d3ee;
    border-color: #67e8f9;
}

#FieldLabel {
    color: #c8d8ee;
    font-size: 13px;
    font-weight: 600;
}

#FieldHint {
    color: #637896;
    font-size: 11px;
}

#InputList {
    background-color: #0b1524;
    border: 1px solid #1e2d47;
    border-radius: 10px;
    padding: 4px;
}

#InputList::item {
    border-radius: 6px;
    color: #c8d8ee;
    min-height: 32px;
    padding: 6px 8px;
}

#InputList::item:hover {
    background-color: #101c31;
}

#InputList::item:selected {
    background-color: #12334a;
    color: #f4f9ff;
}

#PanelHint {
    color: #7f93b3;
    font-size: 12px;
}

#PanelSuccess {
    color: #4ade80;
    font-size: 12px;
    font-weight: 600;
}

#PanelError {
    color: #f87171;
    font-size: 12px;
    font-weight: 600;
}

#PanelWarning {
    color: #fbbf24;
    font-size: 12px;
    font-weight: 600;
}

#PanelEmpty {
    background-color: #0b1524;
    border: 1px dashed #263959;
    border-radius: 10px;
    color: #5d7394;
    font-size: 13px;
}

#RunBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #0c1a2b, stop:1 #0e1727);
    border: 1px solid #1d4e63;
    border-radius: 12px;
}

#RunStatus {
    color: #f1f6ff;
    font-size: 14px;
    font-weight: 700;
}

#RunDetail {
    color: #8ca1c1;
    font-size: 12px;
}

QProgressBar#RunProgress {
    background-color: #08121f;
    border: 1px solid #1e2d47;
    border-radius: 4px;
    min-height: 8px;
    max-height: 8px;
    text-align: center;
}

QProgressBar#RunProgress::chunk {
    background-color: #22d3ee;
    border-radius: 3px;
}

#StatLabel {
    color: #7f93b3;
    font-size: 12px;
}

#StatValue {
    color: #e8f0ff;
    font-size: 14px;
    font-weight: 700;
}

QTableView#DetectionTable, QTableView#ErrorTable {
    background-color: #0b1524;
    border: 1px solid #1e2d47;
    border-radius: 10px;
}

QTableView::item {
    padding: 6px 6px;
}

QSplitter::handle {
    background-color: #1e2d47;
    width: 1px;
}

#EvidenceList {
    background-color: #0b1524;
    border: 1px solid #1e2d47;
    border-radius: 8px;
    padding: 4px;
}

#EvidenceList::item {
    border-bottom: 1px solid #16243a;
    color: #c8d8ee;
    padding: 6px 8px;
}

QProgressBar#SeverityBar {
    background-color: #08121f;
    border: 1px solid #1e2d47;
    border-radius: 3px;
    max-height: 6px;
    min-height: 6px;
}

QProgressBar#SeverityBar::chunk {
    border-radius: 2px;
}

/* Typography: technical values use a local monospace stack. */
QLabel#MonoText {
    font-family: __FONT_MONO__;
    font-size: 12px;
}
QLabel#MonoValue {
    font-family: __FONT_MONO__;
    color: #e8f0ff;
    font-size: 16px;
    font-weight: 700;
}
QLineEdit#ConfigPathEdit,
QListWidget#InputList,
QListWidget#EvidenceList {
    font-family: __FONT_MONO__;
}
QLineEdit#ConfigPathEdit,
QListWidget#InputList {
    font-size: 13px;
}
QListWidget#EvidenceList {
    font-size: 12px;
}
QTableView#DetectionTable,
QTableView#ErrorTable {
    font-size: 13px;
    font-weight: 500;
}

/* Theme selector cards. */
QPushButton#ThemeButton {
    background-color: #0e1727;
    border: 1px solid #1e2d47;
    border-radius: 10px;
    color: #c8d8ee;
    font-size: 13px;
    font-weight: 600;
    min-height: 58px;
    padding: 8px 12px;
    text-align: left;
}
QPushButton#ThemeButton:hover {
    background-color: #101c31;
    border-color: #2a3d5c;
    color: #f1f6ff;
}
QPushButton#ThemeButton:checked {
    background-color: #0b2b36;
    border: 1px solid #155e6b;
    color: #e9f8ff;
}
QPushButton#ThemeButton:focus {
    border: 2px solid #67e8f9;
}
QPushButton#ThemeButton:disabled {
    background-color: #1a2a3f;
    border-color: #243653;
    color: #5d7394;
}

/* Keyboard focus and disabled states. */
QPushButton#PrimaryButton:focus,
QPushButton#GhostButton:focus {
    border: 2px solid #67e8f9;
}
QPushButton#GhostButton:disabled {
    background-color: #1a2a3f;
    border-color: #243653;
    color: #5d7394;
}
QPushButton#NavButton:focus {
    border-left: 3px solid #67e8f9;
}
QPushButton#NavButton:disabled {
    color: #5d7394;
}
QCheckBox:disabled {
    color: #5d7394;
}
QCheckBox::indicator:disabled {
    background-color: #1a2a3f;
    border-color: #243653;
}
QLineEdit:disabled,
QComboBox:disabled,
QSpinBox:disabled,
QDoubleSpinBox:disabled {
    background-color: #1a2a3f;
    border-color: #243653;
    color: #5d7394;
}
QComboBox QAbstractItemView {
    background-color: #0e1727;
    border: 1px solid #243653;
    color: #e8f0ff;
    selection-background-color: #12334a;
    selection-color: #f4f9ff;
}

/* Dialogs inherit the active surface palette instead of the OS default. */
QDialog, QMessageBox {
    background-color: #070c16;
}
QDialog QLabel, QMessageBox QLabel {
    color: #e8f0ff;
    font-size: 14px;
}
"""


def build_stylesheet(theme: Theme) -> str:
    """Render the shared QSS with one theme's semantic colour values."""
    qss = _BASE_STYLESHEET
    # Resolve context-specific gradients through placeholders first. A single
    # regex pass then maps every original dark token exactly once; sequential
    # string replacement would re-map generated colours that happen to match
    # another dark token.
    qss = qss.replace(
        "stop:0 #0b1e2e, stop:0.58 #0d1728",
        "stop:0 __HERO_START__, stop:0.58 __HERO_MID__",
    )
    qss = qss.replace("stop:1 #101a2d", "stop:1 __HERO_END__")
    qss = qss.replace(
        "stop:0 #22d3ee, stop:1 #2563eb",
        "stop:0 __BRAND_START__, stop:1 __BRAND_END__",
    )

    def replace_token(match: re.Match[str]) -> str:
        source = match.group(0).lower()
        token = _DARK_TO_TOKEN.get(source)
        return getattr(theme, token) if token is not None else match.group(0)

    qss = re.sub(r"#[0-9a-fA-F]{6}", replace_token, qss)
    qss = qss.replace("__HERO_START__", theme.hero_start)
    qss = qss.replace("__HERO_MID__", theme.hero_mid)
    qss = qss.replace("__HERO_END__", theme.hero_end)
    qss = qss.replace("__BRAND_START__", theme.logo_start)
    qss = qss.replace("__BRAND_END__", theme.logo_end)
    qss = qss.replace("__FONT_SANS__", FONT_SANS_CSS)
    qss = qss.replace("__FONT_MONO__", FONT_MONO_CSS)
    return qss


def build_palette(theme: Theme) -> QPalette:
    """Build the native Qt palette for a theme."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(theme.background))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(theme.text))
    palette.setColor(QPalette.ColorRole.Base, QColor(theme.input))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme.surface_alt))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme.tooltip_bg))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme.tooltip_text))
    palette.setColor(QPalette.ColorRole.Text, QColor(theme.text))
    palette.setColor(QPalette.ColorRole.Button, QColor(theme.surface))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme.text))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(theme.selection))
    palette.setColor(QPalette.ColorRole.HighlightedText,
                     QColor(theme.selection_text))
    palette.setColor(QPalette.ColorRole.Link, QColor(theme.accent))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(theme.text_dim))
    palette.setColor(QPalette.ColorRole.Light, QColor(theme.border_strong))
    palette.setColor(QPalette.ColorRole.Midlight, QColor(theme.border))
    palette.setColor(QPalette.ColorRole.Mid, QColor(theme.row_border))
    palette.setColor(QPalette.ColorRole.Dark, QColor(theme.shadow))
    palette.setColor(QPalette.ColorRole.Shadow, QColor(theme.shadow))
    for role in (
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.Text,
        QPalette.ColorRole.ButtonText,
    ):
        palette.setColor(
            QPalette.ColorGroup.Disabled, role, QColor(theme.disabled_text))
    return palette


def dark_palette() -> QPalette:
    """Compatibility helper returning the Dark SOC palette."""
    return build_palette(THEMES[DEFAULT_THEME_KEY])


def apply_theme(app: QApplication, theme_key: str | None = None) -> None:
    """Apply a complete theme immediately without touching worker state."""
    theme = get_theme(theme_key if theme_key is not None else theme_manager.key)
    # setStyle() repolishes every existing widget and is expensive. Applying
    # it once per QApplication keeps theme previews instant even with several
    # windows open (the stylesheet itself handles the visible changes).
    if not app.property("_logsentinel_fusion_style"):
        app.setStyle("Fusion")
        app.setProperty("_logsentinel_fusion_style", True)
    app.setPalette(build_palette(theme))
    app.setStyleSheet(build_stylesheet(theme))

    font = QFont()
    font.setFamilies(list(FONT_SANS_FAMILIES))
    font.setPixelSize(14)
    app.setFont(font)
    app.setWindowIcon(create_app_icon(theme.key))
    theme_manager.set_theme(theme.key)


def create_app_icon(theme_key: str | None = None):
    """Return the compact LogSentinel application icon for a theme."""
    return brand_icon(get_theme(theme_key) if theme_key is not None
                      else current_theme())


# Public default stylesheet retained for compatibility and smoke tests.
STYLESHEET = build_stylesheet(THEMES[DEFAULT_THEME_KEY])

__all__ = [
    "APP_NAME",
    "APP_ORGANIZATION",
    "APP_TAGLINE",
    "APP_WINDOW_TITLE",
    "COLOR_ACCENT",
    "COLOR_ACCENT_STRONG",
    "COLOR_BACKGROUND",
    "COLOR_BLUE",
    "COLOR_BORDER",
    "COLOR_BORDER_STRONG",
    "COLOR_DANGER",
    "COLOR_SIDEBAR",
    "COLOR_SUCCESS",
    "COLOR_SURFACE",
    "COLOR_SURFACE_RAISED",
    "COLOR_TEXT",
    "COLOR_TEXT_DIM",
    "COLOR_TEXT_MUTED",
    "COLOR_WARNING",
    "FONT_MONO_FAMILIES",
    "FONT_SANS_FAMILIES",
    "SEVERITY_COLORS",
    "STYLESHEET",
    "THEME_KEYS",
    "THEME_LABELS",
    "THEMES",
    "Theme",
    "apply_theme",
    "build_palette",
    "build_stylesheet",
    "create_app_icon",
    "current_theme",
    "dark_palette",
    "get_theme",
    "severity_colors",
    "theme_label",
    "theme_manager",
]
