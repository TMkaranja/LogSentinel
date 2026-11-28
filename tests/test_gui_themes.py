"""Visual identity, typography, and local asset regression tests.

These tests keep the four-theme design system honest: icons are local SVG
assets, the brand mark renders at taskbar sizes, typography has a real
Inter-first fallback stack, and page navigation never falls back to emoji.
"""

import os
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtGui import QIcon

    from logsentinel.gui.app import create_application
    from logsentinel.gui.icons import (
        available_icon_names,
        brand_icon,
        brand_mark_pixmap,
        brand_pixmap,
        icon_pixmap,
        icon_svg,
    )
    from logsentinel.gui.main_window import _PAGE_SPECS
    from logsentinel.gui.theme import (
        FONT_MONO_FAMILIES,
        FONT_SANS_FAMILIES,
        build_stylesheet,
        current_theme,
    )
    from logsentinel.gui.themes import THEMES, THEME_KEYS

    PYSIDE_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without PySide6
    PYSIDE_AVAILABLE = False

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = PROJECT_ROOT / "src" / "logsentinel" / "gui" / "assets"


class AssetPresenceTests(unittest.TestCase):
    def test_required_icon_assets_are_local_svg_files(self):
        required = (
            "overview",
            "detections",
            "log_explorer",
            "reports",
            "settings",
            "play",
            "stop",
            "download",
            "file_plus",
            "folder_open",
            "trash",
            "search",
            "palette",
        )
        for name in required:
            path = ASSET_ROOT / "icons" / f"{name}.svg"
            self.assertTrue(path.is_file(), name)
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.lstrip().startswith("<svg"))
            self.assertNotIn("http://", text.replace(
                "http://www.w3.org/2000/svg", ""))
            self.assertNotIn("https://", text)

    def test_brand_assets_exist_and_use_vector_placeholders(self):
        expected = {
            "logsentinel-logo.svg",
            "logsentinel-mark.svg",
            "logsentinel-sidebar.svg",
            "logsentinel-appicon.svg",
        }
        actual = {
            path.name for path in (ASSET_ROOT / "brand").glob("*.svg")
        }
        self.assertEqual(actual, expected)
        for name in expected:
            text = (ASSET_ROOT / "brand" / name).read_text(encoding="utf-8")
            self.assertIn("CURRENT_", text)
            self.assertNotIn("<image", text)


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class ThemeAssetRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-theme-asset-tests"])
        cls.app.setQuitOnLastWindowClosed(False)

    def test_every_page_uses_a_known_icon_name(self):
        known = set(available_icon_names())
        for spec in _PAGE_SPECS:
            self.assertIn(spec.icon, known)
            self.assertTrue(spec.icon.isascii())

    def test_icons_render_in_every_theme(self):
        for key in THEME_KEYS:
            theme = THEMES[key]
            for name in (
                "overview", "detections", "reports", "settings",
                "check", "download", "folder_open", "x",
            ):
                pixmap = icon_pixmap(name, 20, theme.text_muted)
                self.assertFalse(pixmap.isNull(), f"{key}:{name}")
                self.assertEqual(pixmap.size().width(), 20)

    def test_approved_icon_assets_match_fallbacks_across_theme_roles_sizes(self):
        from unittest.mock import patch

        from logsentinel.gui import icons

        names = ("check", "download", "folder_open", "x")
        roles = ("text_muted", "text", "accent_text", "disabled_text")
        sizes = (16, 20, 24, 32, 40)
        missing = PROJECT_ROOT / "does-not-exist" / "assets"
        try:
            for name in names:
                asset_svg = icon_svg(name, "#123456")
                ET.fromstring(asset_svg)
                self.assertNotIn("CURRENT_COLOR", asset_svg)
                self.assertIn("#123456", asset_svg)

                with patch.object(icons, "ASSET_ROOT", missing):
                    fallback_svg = icon_svg(name, "#123456")
                    ET.fromstring(fallback_svg)
                    self.assertEqual(fallback_svg, asset_svg, name)

                for theme in THEMES.values():
                    for role in roles:
                        color = getattr(theme, role)
                        for size in sizes:
                            icons.icon_pixmap.cache_clear()
                            asset_image = icon_pixmap(name, size, color).toImage()
                            self.assertFalse(asset_image.isNull())
                            with patch.object(icons, "ASSET_ROOT", missing):
                                icons.icon_pixmap.cache_clear()
                                fallback_image = icon_pixmap(
                                    name, size, color).toImage()
                            self.assertEqual(asset_image, fallback_image,
                                             f"{name}:{theme.key}:{role}:{size}")
        finally:
            icons.icon_pixmap.cache_clear()

    def test_brand_mark_and_wordmark_render(self):
        for key in THEME_KEYS:
            theme = THEMES[key]
            mark = brand_mark_pixmap(theme, 64)
            wordmark = brand_pixmap(theme, 320, 64)
            self.assertFalse(mark.isNull(), key)
            self.assertFalse(wordmark.isNull(), key)
        icon = brand_icon(THEMES["dark"])
        self.assertIsInstance(icon, QIcon)
        self.assertTrue(icon.availableSizes())
        sizes = {size.width() for size in icon.availableSizes()}
        self.assertIn(16, sizes)
        self.assertIn(32, sizes)
        self.assertIn(256, sizes)

    def test_embedded_fallbacks_survive_missing_asset_files(self):
        from unittest.mock import patch

        from logsentinel.gui import icons

        missing = PROJECT_ROOT / "does-not-exist" / "assets"
        with patch.object(icons, "ASSET_ROOT", missing):
            icon_svg = icons.icon_svg("overview", "#123456")
            logo_svg = icons.brand_logo_svg(THEMES["dark"])
        for svg in (icon_svg, logo_svg):
            self.assertTrue(svg.startswith("<svg"))
            self.assertTrue(svg.strip().endswith("</svg>"))
            self.assertNotIn("CURRENT_", svg)
        self.assertIn("#123456", icon_svg)

    def test_typography_and_stylesheet_use_professional_stacks(self):
        self.assertEqual(FONT_SANS_FAMILIES[0], "Inter")
        self.assertIn("Segoe UI", FONT_SANS_FAMILIES)
        self.assertIn("Cascadia Mono", FONT_MONO_FAMILIES)
        qss = build_stylesheet(THEMES[current_theme().key])
        self.assertIn("Inter", qss)
        self.assertIn("Cascadia Mono", qss)
        self.assertIn("QLabel#MonoText", qss)

    def test_typography_scale_is_readable_and_hierarchical(self):
        self.assertEqual(self.app.font().pixelSize(), 14)
        qss = build_stylesheet(THEMES["dark"])

        def size(selector: str) -> int:
            match = re.search(
                rf"{re.escape(selector)}\s*\{{[^}}]*?font-size:\s*(\d+)px",
                qss,
            )
            self.assertIsNotNone(match, selector)
            return int(match.group(1))

        self.assertEqual(size("QWidget"), 14)
        self.assertEqual(size("#PageTitle"), 28)
        self.assertEqual(size("#SectionHeading"), 17)
        self.assertEqual(size("#BodyText"), 13)
        self.assertEqual(size("#FieldLabel"), 13)
        self.assertEqual(size("#StatValue"), 14)
        self.assertEqual(size("#MonoText"), 12)
        self.assertEqual(size("#MonoValue"), 16)

    def test_all_themes_share_the_same_type_scale(self):
        scales = {
            key: re.findall(
                r"font-size:\s*(\d+)px",
                build_stylesheet(THEMES[key]),
            )
            for key in THEME_KEYS
        }
        reference = scales["dark"]
        self.assertGreater(len(reference), 20)
        for key, scale in scales.items():
            self.assertEqual(scale, reference, key)


if __name__ == "__main__":  # pragma: no cover - discovery entry
    unittest.main()
