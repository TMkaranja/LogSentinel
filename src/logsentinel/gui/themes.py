"""Qt-free theme definitions for the LogSentinel desktop application.

Keeping the colour tokens here means the settings layer can validate theme
keys without importing PySide6, while :mod:`logsentinel.gui.theme` remains the
single place that turns a theme into a Qt palette and stylesheet.

The four themes share one semantic token vocabulary. Severity colours are
calibrated per theme but retain the same meaning (red/amber/blue) so findings
remain consistent and readable in every appearance.
"""

from __future__ import annotations

from dataclasses import dataclass, fields

__all__ = [
    "DEFAULT_THEME_KEY",
    "THEMES",
    "THEME_KEYS",
    "THEME_LABELS",
    "Theme",
    "get_theme",
    "theme_label",
]

DEFAULT_THEME_KEY = "dark"


@dataclass(frozen=True, slots=True)
class Theme:
    """One complete application theme."""

    key: str
    name: str
    description: str
    dark: bool

    background: str
    sidebar: str
    header: str
    surface: str
    surface_raised: str
    surface_alt: str
    input: str
    border: str
    border_strong: str
    control_border: str
    text: str
    text_muted: str
    text_soft: str
    text_dim: str

    accent: str
    accent_strong: str
    accent_soft: str
    accent_border: str
    accent_text: str
    blue: str
    success: str
    warning: str
    danger: str
    warning_soft: str
    warning_border: str

    hover: str
    pressed: str
    selection: str
    selection_text: str
    grid: str
    row_border: str
    code_bg: str
    tooltip_bg: str
    tooltip_text: str
    scroll: str
    scroll_hover: str
    disabled_bg: str
    disabled_text: str
    shadow: str

    hero_start: str
    hero_mid: str
    hero_end: str
    run_start: str
    empty_border: str
    logo_start: str
    logo_end: str
    logo_foreground: str
    logo_border: str

    severity_critical: str
    severity_high: str
    severity_medium: str
    severity_low: str

    def __post_init__(self) -> None:
        if not self.key or not self.name:
            raise ValueError("theme key and name must be non-empty")
        for field in fields(self):
            if field.name in {"key", "name", "description", "dark"}:
                continue
            value = getattr(self, field.name)
            if not isinstance(value, str) or not value.startswith("#"):
                raise ValueError(
                    f"theme {self.key!r} token {field.name!r} must be a "
                    f"colour string")

    @property
    def severity_colors(self) -> dict[str, str]:
        return {
            "critical": self.severity_critical,
            "high": self.severity_high,
            "medium": self.severity_medium,
            "low": self.severity_low,
        }

    @property
    def preview_colors(self) -> tuple[str, str, str, str]:
        """Background, surface, accent, and text swatches for selectors."""
        return (self.background, self.surface, self.accent, self.text)


THEMES: dict[str, Theme] = {
    "dark": Theme(
        key="dark",
        name="Dark SOC",
        description="Dark navy surfaces with green monitoring accents.",
        dark=True,
        background="#070c16",
        sidebar="#0a1220",
        header="#0a111f",
        surface="#0e1727",
        surface_raised="#121e33",
        surface_alt="#0e1a2c",
        input="#0b1524",
        border="#1e2d47",
        border_strong="#2a3d5c",
        control_border="#243653",
        text="#e8f0ff",
        text_muted="#8ca1c1",
        text_soft="#c8d8ee",
        text_dim="#637896",
        accent="#34d399",
        accent_strong="#6ee7b7",
        accent_soft="#0b2b24",
        accent_border="#155e4b",
        accent_text="#042018",
        blue="#38bdf8",
        success="#22c55e",
        warning="#f59e0b",
        danger="#ef4444",
        warning_soft="#241b0b",
        warning_border="#5c4415",
        hover="#101c31",
        pressed="#0d1728",
        selection="#123a35",
        selection_text="#eafff6",
        grid="#1a2942",
        row_border="#16243a",
        code_bg="#08121f",
        tooltip_bg="#101c31",
        tooltip_text="#e8f0ff",
        scroll="#233552",
        scroll_hover="#2f466b",
        disabled_bg="#1a2a3f",
        disabled_text="#5d7394",
        shadow="#03060c",
        hero_start="#0b1e2e",
        hero_mid="#0d1728",
        hero_end="#101a2d",
        run_start="#0c1a2b",
        empty_border="#263959",
        logo_start="#34d399",
        logo_end="#2563eb",
        logo_foreground="#06111f",
        logo_border="#6ee7b7",
        severity_critical="#f43f5e",
        severity_high="#fb7185",
        severity_medium="#fbbf24",
        severity_low="#67e8f9",
    ),
    "light": Theme(
        key="light",
        name="Light Professional",
        description="Clean white surfaces with professional blue accents.",
        dark=False,
        background="#f4f7fb",
        sidebar="#ffffff",
        header="#ffffff",
        surface="#ffffff",
        surface_raised="#f8fafc",
        surface_alt="#f1f5f9",
        input="#ffffff",
        border="#dbe3ee",
        border_strong="#c3cedd",
        control_border="#cbd5e1",
        text="#0f172a",
        text_muted="#52637a",
        text_soft="#334155",
        text_dim="#7b8ba1",
        accent="#2563eb",
        accent_strong="#1d4ed8",
        accent_soft="#e8f0ff",
        accent_border="#93c5fd",
        accent_text="#ffffff",
        blue="#2563eb",
        success="#15803d",
        warning="#b45309",
        danger="#b91c1c",
        warning_soft="#fff7ed",
        warning_border="#fed7aa",
        hover="#eff6ff",
        pressed="#dbeafe",
        selection="#dbeafe",
        selection_text="#0f172a",
        grid="#e2e8f0",
        row_border="#eef2f7",
        code_bg="#f1f5f9",
        tooltip_bg="#0f172a",
        tooltip_text="#f8fafc",
        scroll="#cbd5e1",
        scroll_hover="#94a3b8",
        disabled_bg="#eef2f7",
        disabled_text="#94a3b8",
        shadow="#cbd5e1",
        hero_start="#eef6ff",
        hero_mid="#f8fbff",
        hero_end="#ffffff",
        run_start="#f0f7ff",
        empty_border="#c3cedd",
        logo_start="#2563eb",
        logo_end="#06b6d4",
        logo_foreground="#ffffff",
        logo_border="#93c5fd",
        severity_critical="#b91c1c",
        severity_high="#be123c",
        severity_medium="#b45309",
        severity_low="#0369a1",
    ),
    "midnight": Theme(
        key="midnight",
        name="Midnight",
        description="Near-black surfaces with a restrained violet accent.",
        dark=True,
        background="#04040a",
        sidebar="#08070f",
        header="#07060c",
        surface="#0c0a14",
        surface_raised="#12101d",
        surface_alt="#100d19",
        input="#0a0811",
        border="#241d38",
        border_strong="#3b2d5c",
        control_border="#2e2447",
        text="#f5f1ff",
        text_muted="#b2a5c9",
        text_soft="#d8ceea",
        text_dim="#7e7099",
        accent="#a78bfa",
        accent_strong="#c4b5fd",
        accent_soft="#211735",
        accent_border="#6d28d9",
        accent_text="#12081f",
        blue="#8b5cf6",
        success="#4ade80",
        warning="#fbbf24",
        danger="#fb7185",
        warning_soft="#2a2113",
        warning_border="#7c5a18",
        hover="#1a1428",
        pressed="#211735",
        selection="#2a1d45",
        selection_text="#f5f1ff",
        grid="#2a203e",
        row_border="#1d172c",
        code_bg="#08060e",
        tooltip_bg="#181125",
        tooltip_text="#f5f1ff",
        scroll="#34264d",
        scroll_hover="#4c3a6e",
        disabled_bg="#161222",
        disabled_text="#6f6387",
        shadow="#020106",
        hero_start="#0d0920",
        hero_mid="#0a0813",
        hero_end="#120d24",
        run_start="#0b0817",
        empty_border="#3b2d5c",
        logo_start="#8b5cf6",
        logo_end="#d946ef",
        logo_foreground="#ffffff",
        logo_border="#c4b5fd",
        severity_critical="#fb7185",
        severity_high="#fda4af",
        severity_medium="#fcd34d",
        severity_low="#c4b5fd",
    ),
    "cyber_teal": Theme(
        key="cyber_teal",
        name="Cyber Teal",
        description="Deep teal surfaces with bright turquoise accents.",
        dark=True,
        background="#021314",
        sidebar="#041c1d",
        header="#031819",
        surface="#062426",
        surface_raised="#083033",
        surface_alt="#072a2c",
        input="#052022",
        border="#0d4447",
        border_strong="#126366",
        control_border="#0f4f52",
        text="#e6fffb",
        text_muted="#8ec9c4",
        text_soft="#c8f5ee",
        text_dim="#5e9a96",
        accent="#2dd4bf",
        accent_strong="#5eead4",
        accent_soft="#073b3d",
        accent_border="#0f766e",
        accent_text="#01201f",
        blue="#22d3ee",
        success="#34d399",
        warning="#fbbf24",
        danger="#fb7185",
        warning_soft="#2a2113",
        warning_border="#7c5a18",
        hover="#083638",
        pressed="#0a4143",
        selection="#0d4f50",
        selection_text="#e6fffb",
        grid="#0e3b3d",
        row_border="#0a3032",
        code_bg="#031b1d",
        tooltip_bg="#062426",
        tooltip_text="#e6fffb",
        scroll="#0e4a4c",
        scroll_hover="#176e6e",
        disabled_bg="#073032",
        disabled_text="#4f827f",
        shadow="#010b0c",
        hero_start="#042b2c",
        hero_mid="#052a2b",
        hero_end="#062426",
        run_start="#062a2b",
        empty_border="#126366",
        logo_start="#2dd4bf",
        logo_end="#0f766e",
        logo_foreground="#01201f",
        logo_border="#5eead4",
        severity_critical="#fb7185",
        severity_high="#fda4af",
        severity_medium="#fde68a",
        severity_low="#5eead4",
    ),
}

THEME_KEYS = tuple(THEMES)
THEME_LABELS = {key: theme.name for key, theme in THEMES.items()}


def get_theme(key: str | None) -> Theme:
    """Return a known theme, falling back to Dark SOC for invalid values."""
    if isinstance(key, str) and key in THEMES:
        return THEMES[key]
    return THEMES[DEFAULT_THEME_KEY]


def theme_label(key: str) -> str:
    return get_theme(key).name
