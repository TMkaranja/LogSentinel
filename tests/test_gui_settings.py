"""Tests for persistent GUI settings, window state, and Settings page behavior.

Settings persistence uses only the existing analysis-config validation layer;
these tests cover the defaults/JSON/override precedence and safe loading of
missing, malformed, and inaccessible settings files.
"""

import json
import os
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from logsentinel.config import DEFAULTS, load_config
from logsentinel.gui.app_settings import (
    AppSettings,
    SettingsError,
    SettingsStore,
    default_settings_path,
)
from logsentinel.gui.themes import (
    DEFAULT_THEME_KEY,
    THEMES,
    THEME_KEYS,
    get_theme,
)

try:
    from PySide6.QtCore import QEvent
    from PySide6.QtWidgets import QMessageBox

    from logsentinel.gui.app import create_application
    from logsentinel.gui.theme import (
        apply_theme,
        build_stylesheet,
        current_theme,
    )
    from logsentinel.gui.main_window import MainWindow
    from logsentinel.gui.panels import ConfigPanel
    from logsentinel.gui.settings_view import SettingsView

    PYSIDE_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without PySide6
    PYSIDE_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES = PROJECT_ROOT / "samples"


def _flush_deferred_deletes(app) -> None:
    """Destroy closed test windows before the next stylesheet application.

    Qt defers deleteLater() until the event loop runs; processing it here
    prevents closed windows from accumulating and makes theme changes in the
    suite as fast as they are in the real application.
    """
    app.processEvents()
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()


class SettingsPersistenceTests(unittest.TestCase):
    def test_defaults_are_valid_and_inherit_builtin_analysis_values(self):
        settings = AppSettings.defaults()
        self.assertTrue(settings.remember_window_state)
        self.assertTrue(settings.restore_last_page)
        self.assertEqual(settings.startup_page, "overview")
        self.assertEqual(settings.theme, DEFAULT_THEME_KEY)
        self.assertEqual(settings.analysis_defaults, {})
        self.assertEqual(settings.default_export_format, "json")
        self.assertEqual(settings.window_geometry, "")
        self.assertEqual(settings.last_page, "overview")
        self.assertEqual(
            load_config(settings.analysis_defaults, None),
            load_config(None, None))

    def test_default_settings_path_is_per_user(self):
        path = default_settings_path()
        self.assertEqual(path.name, "settings.json")
        self.assertEqual(path.parent.name, "LogSentinel")

    def test_save_and_reload_round_trip(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config" / "settings.json"
            store = SettingsStore(path)
            settings = AppSettings(
                remember_window_state=False,
                restore_last_page=False,
                startup_page="reports",
                analysis_defaults={
                    "ssh_threshold": 5,
                    "max_file_mb": 64,
                    "strict": True,
                },
                default_export_format="html",
                window_geometry="Z2VvbWV0cnk=",
                window_state="c3RhdGU=",
                last_page="detections",
            )
            store.save(settings)
            self.assertTrue(path.is_file())
            loaded = store.load()
            self.assertIsNone(loaded.warning)
            self.assertEqual(loaded.settings, settings)
            text = path.read_text(encoding="utf-8")
            payload = json.loads(text)
            self.assertEqual(payload["version"], 1)
            self.assertEqual(payload["general"]["startup_page"], "reports")
            self.assertEqual(
                payload["analysis_defaults"]["ssh_threshold"], 5)
            self.assertEqual(payload["reports"]["default_export_format"], "html")
            self.assertNotIn("password", text)
            if os.name != "nt":
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_missing_file_uses_defaults_without_warning(self):
        with TemporaryDirectory() as directory:
            loaded = SettingsStore(
                Path(directory) / "missing" / "settings.json").load()
        self.assertEqual(loaded.settings, AppSettings.defaults())
        self.assertIsNone(loaded.warning)

    def test_malformed_files_fall_back_safely(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text("{not json", encoding="utf-8")
            loaded = SettingsStore(path).load()
            self.assertEqual(loaded.settings, AppSettings.defaults())
            self.assertIn("malformed", loaded.warning.lower())

            path.write_text(json.dumps({"version": 1, "general": []}),
                            encoding="utf-8")
            loaded = SettingsStore(path).load()
            self.assertIn("malformed", loaded.warning.lower())

            path.write_text(json.dumps({
                "version": 1,
                "analysis_defaults": {"ssh_threshold": 0},
            }), encoding="utf-8")
            loaded = SettingsStore(path).load()
            self.assertIn("malformed", loaded.warning.lower())

    def test_unreadable_path_uses_defaults_with_warning(self):
        with TemporaryDirectory() as directory:
            # A directory target is readable as a path but not as a file.
            loaded = SettingsStore(Path(directory)).load()
        self.assertEqual(loaded.settings, AppSettings.defaults())
        self.assertIn("could not be read", loaded.warning.lower())

    def test_save_failure_is_safe_and_does_not_create_target(self):
        with TemporaryDirectory() as directory:
            blocker = Path(directory) / "blocker"
            blocker.write_text("not a directory", encoding="utf-8")
            store = SettingsStore(blocker / "settings.json")
            with self.assertRaises(SettingsError):
                store.save(AppSettings.defaults())

    def test_in_memory_store_keeps_settings_for_embedding_and_tests(self):
        store = SettingsStore(path=None)
        settings = AppSettings(startup_page="settings")
        store.save(settings)
        self.assertEqual(store.load().settings, settings)
        self.assertIsNone(store.load().warning)

    def test_config_precedence_uses_defaults_then_json_then_overrides(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({
                "ssh_threshold": 8,
                "http_4xx_threshold": 6,
            }), encoding="utf-8")
            effective = load_config(
                {"ssh_threshold": 9},
                str(path),
                defaults={"ssh_threshold": 5, "portscan_threshold": 11},
            )
        self.assertEqual(effective.ssh_threshold, 9)       # explicit override
        self.assertEqual(effective.http_4xx_threshold, 6)  # JSON
        self.assertEqual(effective.portscan_threshold, 11)  # app defaults
        self.assertEqual(effective.ssh_window_seconds,
                         DEFAULTS["ssh_window_seconds"])

    def test_cli_layer_without_defaults_is_unchanged(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({"ssh_threshold": 8}), encoding="utf-8")
            effective = load_config(None, str(path))
        self.assertEqual(effective.ssh_threshold, 8)
        self.assertEqual(effective.portscan_threshold,
                         DEFAULTS["portscan_threshold"])

    def test_invalid_defaults_and_settings_are_rejected(self):
        with self.assertRaises(ValueError):
            AppSettings(analysis_defaults={"ssh_threshold": 0})
        with self.assertRaises(ValueError):
            AppSettings(theme="neon")
        with self.assertRaises(ValueError):
            AppSettings(startup_page="unknown")
        with self.assertRaises(ValueError):
            AppSettings(default_export_format="pdf")


class ThemeDefinitionTests(unittest.TestCase):
    def test_all_four_themes_are_valid_and_ordered(self):
        self.assertEqual(
            THEME_KEYS, ("dark", "light", "midnight", "cyber_teal"))
        names = {THEMES[key].name for key in THEME_KEYS}
        self.assertEqual(
            names,
            {"Dark SOC", "Light Professional", "Midnight", "Cyber Teal"})
        for key in THEME_KEYS:
            self.assertEqual(AppSettings(theme=key).theme, key)
            self.assertEqual(get_theme(key).key, key)

    def test_invalid_theme_lookup_falls_back_to_dark_soc(self):
        self.assertEqual(get_theme("neon").key, DEFAULT_THEME_KEY)
        self.assertEqual(get_theme(None).key, DEFAULT_THEME_KEY)
        with self.assertRaises(ValueError):
            AppSettings(theme="neon")

    def test_theme_settings_round_trip(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            store = SettingsStore(path)
            store.save(AppSettings(theme="midnight"))
            loaded = store.load()
        self.assertEqual(loaded.settings.theme, "midnight")
        self.assertIsNone(loaded.warning)

    def test_malformed_theme_value_falls_back_safely(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "settings.json"
            path.write_text(
                json.dumps({"version": 1, "appearance": {"theme": "neon"}}),
                encoding="utf-8")
            loaded = SettingsStore(path).load()
        self.assertEqual(loaded.settings.theme, DEFAULT_THEME_KEY)
        self.assertIn("malformed", loaded.warning.lower())

    @unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
    def test_all_stylesheets_are_complete_and_distinct(self):
        styles = {key: build_stylesheet(THEMES[key]) for key in THEME_KEYS}
        self.assertEqual(len(set(styles.values())), len(THEME_KEYS))
        for key, qss in styles.items():
            theme = THEMES[key]
            self.assertIn(theme.background, qss)
            self.assertIn(theme.accent, qss)
            self.assertIn(theme.text, qss)
            self.assertNotIn("__FONT_", qss)
            self.assertIn("Inter", qss)
            self.assertIn("Cascadia Mono", qss)

    def test_theme_text_and_severity_contrast(self):
        def luminance(hex_color: str) -> float:
            channels = []
            for index in (1, 3, 5):
                value = int(hex_color[index:index + 2], 16) / 255
                channels.append(
                    value / 12.92 if value <= 0.03928
                    else ((value + 0.055) / 1.055) ** 2.4)
            return (0.2126 * channels[0] + 0.7152 * channels[1]
                    + 0.0722 * channels[2])

        def contrast(a: str, b: str) -> float:
            first, second = sorted((luminance(a), luminance(b)), reverse=True)
            return (first + 0.05) / (second + 0.05)

        for key, theme in THEMES.items():
            self.assertGreaterEqual(
                contrast(theme.text, theme.background), 7.0, key)
            self.assertGreaterEqual(
                contrast(theme.text_muted, theme.background), 3.0, key)
            for severity in ("high", "medium", "low"):
                self.assertGreaterEqual(
                    contrast(theme.severity_colors[severity],
                             theme.background),
                    3.0,
                    f"{key}:{severity}",
                )


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class SettingsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-settings-view-tests"])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.view = SettingsView()
        self.view.set_settings(AppSettings.defaults())
        self.view.show()
        self.app.processEvents()

    def tearDown(self):
        self.view.close()
        self.view.deleteLater()
        apply_theme(self.app, DEFAULT_THEME_KEY)
        _flush_deferred_deletes(self.app)

    def test_theme_selector_has_four_named_visual_previews(self):
        self.assertEqual(
            tuple(self.view.theme_buttons),
            ("dark", "light", "midnight", "cyber_teal"))
        self.assertEqual(self.view.selected_theme, "dark")
        for key, button in self.view.theme_buttons.items():
            self.assertTrue(button.isCheckable())
            self.assertFalse(button.icon().isNull())
            self.assertIn(THEMES[key].name, button.text())
            self.assertTrue(button.toolTip())
        self.assertTrue(self.view.theme_buttons["dark"].isChecked())

    def test_selecting_theme_emits_and_marks_dirty(self):
        selected = []
        self.view.theme_selected.connect(selected.append)
        self.view.theme_buttons["light"].click()
        self.assertEqual(selected, ["light"])
        self.assertEqual(self.view.selected_theme, "light")
        self.assertTrue(self.view.is_dirty)
        self.assertEqual(
            self.view.collect_settings(AppSettings.defaults()).theme, "light")

    def test_set_settings_selects_persisted_theme(self):
        self.view.set_settings(AppSettings(theme="cyber_teal"))
        self.assertEqual(self.view.selected_theme, "cyber_teal")
        self.assertTrue(self.view.theme_buttons["cyber_teal"].isChecked())
        self.assertFalse(self.view.theme_buttons["dark"].isChecked())

    def test_theme_selector_remains_available_during_analysis(self):
        self.view.set_analysis_running(True)
        for button in self.view.theme_buttons.values():
            self.assertTrue(button.isEnabled())
        self.view.theme_buttons["light"].click()
        self.assertEqual(self.view.selected_theme, "light")

    def test_defaults_populate_all_supported_analysis_fields(self):
        values = {
            key: spin.value()
            for key, spin in self.view.analysis_spins.items()
        }
        self.assertEqual(values["ssh_threshold"], DEFAULTS["ssh_threshold"])
        self.assertEqual(values["ssh_window_seconds"],
                         DEFAULTS["ssh_window_seconds"])
        self.assertEqual(values["portscan_threshold"],
                         DEFAULTS["portscan_threshold"])
        self.assertEqual(values["http_4xx_threshold"],
                         DEFAULTS["http_4xx_threshold"])
        self.assertEqual(values["max_line_length"],
                         DEFAULTS["max_line_length"])
        self.assertEqual(values["max_file_mb"], DEFAULTS["max_file_mb"])
        self.assertFalse(self.view.strict_check.isChecked())
        self.assertFalse(self.view.is_dirty)
        self.assertFalse(self.view.save_button.isEnabled())
        self.assertTrue(self.view.reset_button.isEnabled())

    def test_editing_marks_unsaved_and_save_collects_values(self):
        self.view.analysis_spins["ssh_threshold"].setValue(5)
        self.assertEqual(self.view.dirty_text, "Unsaved changes")
        self.assertTrue(self.view.is_dirty)
        self.assertTrue(self.view.save_button.isEnabled())
        candidate = self.view.collect_settings(AppSettings.defaults())
        self.assertEqual(candidate.analysis_defaults["ssh_threshold"], 5)
        self.assertEqual(
            candidate.analysis_defaults["max_file_mb"],
            DEFAULTS["max_file_mb"])

    def test_saving_clears_dirty_state_through_view_api(self):
        self.view.analysis_spins["portscan_threshold"].setValue(12)
        candidate = self.view.collect_settings(AppSettings.defaults())
        self.view.set_settings(candidate)
        self.view.show_saved("Settings saved.")
        self.assertFalse(self.view.is_dirty)
        self.assertIn("Settings saved", self.view.feedback_text)
        self.assertFalse(self.view.save_button.isEnabled())

    def test_analysis_running_disables_save_and_reset(self):
        self.view.set_analysis_running(True)
        self.assertFalse(self.view.save_button.isEnabled())
        self.assertFalse(self.view.reset_button.isEnabled())
        self.view.analysis_spins["ssh_threshold"].setValue(5)
        self.assertIn("Analysis running", self.view.dirty_text)
        self.view.set_analysis_running(False)
        self.assertTrue(self.view.save_button.isEnabled())

    def test_reset_requires_confirmation(self):
        emitted = []
        self.view.reset_requested.connect(lambda: emitted.append(True))
        with mock.patch(
            "logsentinel.gui.settings_view.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Cancel,
        ):
            self.view.request_reset()
        self.assertEqual(emitted, [])
        self.assertIn("cancelled", self.view.feedback_text.lower())

        with mock.patch(
            "logsentinel.gui.settings_view.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Reset,
        ):
            self.view.request_reset()
        self.assertEqual(emitted, [True])

    def test_warning_and_error_feedback_are_sanitized(self):
        self.view.show_warning("settings file is malformed")
        self.assertIn("warning", self.view.feedback_text.lower())
        self.view.show_error("password=hunter2")
        self.assertIn("<REDACTED>", self.view.feedback_text)
        self.assertNotIn("hunter2", self.view.feedback_text)


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class SettingsWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-settings-window-tests"])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.path = Path(self.temp.name) / "settings.json"
        self.store = SettingsStore(self.path)
        self.window = MainWindow(settings_store=self.store)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        apply_theme(self.app, DEFAULT_THEME_KEY)
        _flush_deferred_deletes(self.app)
        self.temp.cleanup()

    def wait_until(self, predicate, timeout=10.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.app.processEvents()
            if predicate():
                return True
            time.sleep(0.01)
        self.app.processEvents()
        return predicate()

    def test_settings_page_navigation_and_defaults(self):
        self.window.navigate_to("settings")
        self.app.processEvents()
        self.assertEqual(self.window.current_page_key, "settings")
        self.assertEqual(self.window.workspace_stack.currentIndex(), 4)
        self.assertFalse(self.window.settings_view.is_dirty)
        self.assertFalse(self.window.settings_view.save_button.isEnabled())

    def test_theme_preview_applies_immediately_and_save_persists(self):
        self.window.settings_view.theme_buttons["midnight"].click()
        self.app.processEvents()
        self.assertEqual(current_theme().key, "midnight")
        self.assertEqual(self.window.app_settings.theme, "dark")
        self.assertTrue(self.window.settings_view.is_dirty)
        self.assertTrue(self.window._save_settings())
        self.app.processEvents()
        self.assertEqual(self.window.app_settings.theme, "midnight")
        self.assertEqual(self.store.load().settings.theme, "midnight")
        self.assertEqual(current_theme().key, "midnight")

    def test_persisted_theme_is_restored_on_next_window(self):
        self.window.settings_view.theme_buttons["light"].click()
        self.assertTrue(self.window._save_settings())
        self.window.close()
        self.app.processEvents()
        second = MainWindow(settings_store=self.store)
        second.show()
        self.app.processEvents()
        self.assertEqual(second.app_settings.theme, "light")
        self.assertEqual(second.settings_view.selected_theme, "light")
        self.assertEqual(current_theme().key, "light")
        second.close()
        second.deleteLater()
        self.app.processEvents()

    def test_reset_restores_dark_soc_theme(self):
        self.window.settings_view.theme_buttons["light"].click()
        self.assertTrue(self.window._save_settings())
        with mock.patch(
            "logsentinel.gui.settings_view.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Reset,
        ):
            self.window.settings_view.request_reset()
        self.app.processEvents()
        self.assertEqual(self.window.app_settings.theme, "dark")
        self.assertEqual(current_theme().key, "dark")
        self.assertTrue(
            self.window.settings_view.theme_buttons["dark"].isChecked())

    def test_theme_can_change_while_analysis_runs(self):
        self.window.input_panel.add_paths([SAMPLES])
        self.assertTrue(self.window.start_analysis())
        self.assertTrue(self.window.is_analysis_running)
        self.window.settings_view.theme_buttons["cyber_teal"].click()
        self.app.processEvents()
        self.assertEqual(current_theme().key, "cyber_teal")
        self.assertTrue(self.window.is_analysis_running)
        self.assertFalse(self.window.settings_view.save_button.isEnabled())
        self.assertTrue(self.wait_until(
            lambda: not self.window.is_analysis_running))
        self.assertEqual(current_theme().key, "cyber_teal")

    def test_theme_switch_does_not_interrupt_report_export(self):
        self.window.reports_view.set_exporting(True)
        self.window.settings_view.theme_buttons["light"].click()
        self.app.processEvents()
        self.assertEqual(current_theme().key, "light")
        self.assertTrue(self.window.reports_view.is_exporting)
        self.assertFalse(self.window.reports_view.is_export_enabled)

    def test_save_updates_config_reports_and_persists(self):
        self.window.navigate_to("settings")
        self.window.settings_view.analysis_spins["ssh_threshold"].setValue(5)
        self.window.settings_view.analysis_spins["max_file_mb"].setValue(64)
        self.window.settings_view.default_export_combo.setCurrentIndex(
            self.window.settings_view.default_export_combo.findData("html"))
        self.assertTrue(self.window._save_settings())
        self.app.processEvents()
        self.assertFalse(self.window.settings_view.is_dirty)
        self.assertEqual(
            self.window.config_panel.effective_config().ssh_threshold, 5)
        self.assertEqual(
            self.window.config_panel.effective_config().max_file_mb, 64)
        self.assertEqual(self.window.reports_view.preferred_format, "html")
        self.assertEqual(self.window.input_panel.max_file_mb, 64)
        reloaded = self.store.load().settings
        self.assertEqual(reloaded.analysis_defaults["ssh_threshold"], 5)
        self.assertEqual(reloaded.default_export_format, "html")

    def test_persistence_between_window_instances(self):
        self.window.settings_view.analysis_spins["ssh_threshold"].setValue(6)
        self.window.settings_view.analysis_spins["max_file_mb"].setValue(64)
        self.assertTrue(self.window._save_settings())
        self.window.close()
        self.app.processEvents()
        second = MainWindow(settings_store=self.store)
        second.show()
        self.app.processEvents()
        self.assertEqual(
            second.config_panel.effective_config().ssh_threshold, 6)
        self.assertEqual(
            second.app_settings.analysis_defaults["ssh_threshold"], 6)
        self.assertEqual(second.input_panel.max_file_mb, 64)
        second.close()
        second.deleteLater()
        self.app.processEvents()

    def test_window_state_and_last_page_persist(self):
        # Offscreen screens are 800x800; use the supported minimum window
        # size so restoreGeometry can be verified without screen clamping.
        self.window.resize(1080, 680)
        self.window.navigate_to("detections")
        self.app.processEvents()
        self.window.close()
        self.app.processEvents()
        loaded = self.store.load().settings
        self.assertTrue(loaded.remember_window_state)
        self.assertTrue(loaded.window_geometry)
        self.assertEqual(loaded.last_page, "detections")

        second = MainWindow(settings_store=self.store)
        second.show()
        self.app.processEvents()
        self.assertEqual(second.current_page_key, "detections")
        self.assertEqual(second.width(), 1080)
        self.assertEqual(second.height(), 680)
        second.close()
        second.deleteLater()
        self.app.processEvents()

    def test_disabling_window_state_stops_geometry_persistence(self):
        self.window.settings_view.remember_window_check.setChecked(False)
        self.assertTrue(self.window._save_settings())
        self.window.close()
        self.app.processEvents()
        loaded = self.store.load().settings
        self.assertFalse(loaded.remember_window_state)
        self.assertEqual(loaded.window_geometry, "")
        self.assertEqual(loaded.window_state, "")

    def test_startup_page_used_when_last_page_restore_is_disabled(self):
        self.window.settings_view.restore_last_page_check.setChecked(False)
        self.window.settings_view.startup_page_combo.setCurrentIndex(
            self.window.settings_view.startup_page_combo.findData("reports"))
        self.assertTrue(self.window._save_settings())
        self.window.close()
        self.app.processEvents()
        second = MainWindow(settings_store=self.store)
        second.show()
        self.app.processEvents()
        self.assertEqual(second.current_page_key, "reports")
        second.close()
        second.deleteLater()
        self.app.processEvents()

    def test_malformed_settings_warns_and_uses_defaults(self):
        self.path.write_text("{malformed", encoding="utf-8")
        broken = MainWindow(settings_store=self.store)
        broken.show()
        self.app.processEvents()
        self.assertIn("warning", broken.settings_view.feedback_text.lower())
        self.assertEqual(broken.app_settings, AppSettings.defaults())
        broken.close()
        broken.deleteLater()
        self.app.processEvents()

    def test_save_failure_keeps_dirty_state(self):
        blocker = Path(self.temp.name) / "blocked"
        blocker.write_text("file", encoding="utf-8")
        store = SettingsStore(blocker / "settings.json")
        window = MainWindow(settings_store=store)
        window.show()
        self.app.processEvents()
        window.settings_view.analysis_spins["ssh_threshold"].setValue(5)
        self.assertFalse(window._save_settings())
        self.assertTrue(window.settings_view.is_dirty)
        self.assertIn("Settings error", window.settings_view.feedback_text)
        window.close()
        window.deleteLater()
        self.app.processEvents()

    def test_reset_via_view_restores_defaults(self):
        self.window.settings_view.analysis_spins["ssh_threshold"].setValue(5)
        self.assertTrue(self.window._save_settings())
        with mock.patch(
            "logsentinel.gui.settings_view.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Reset,
        ):
            self.window.settings_view.request_reset()
        self.app.processEvents()
        self.assertEqual(self.window.app_settings, AppSettings.defaults())
        self.assertEqual(
            self.window.config_panel.effective_config().ssh_threshold,
            DEFAULTS["ssh_threshold"])
        self.assertEqual(self.store.load().settings, AppSettings.defaults())

    def test_settings_are_disabled_while_analysis_is_running(self):
        self.window.settings_view.analysis_spins["ssh_threshold"].setValue(5)
        self.window.input_panel.add_paths([SAMPLES])
        self.assertTrue(self.window.start_analysis())
        self.assertFalse(self.window.settings_view.save_button.isEnabled())
        self.assertFalse(self.window.settings_view.reset_button.isEnabled())
        self.assertFalse(self.window.config_panel.isEnabled())
        self.assertTrue(self.wait_until(
            lambda: not self.window.is_analysis_running))
        self.assertTrue(self.window.settings_view.save_button.isEnabled())

    def test_config_panel_layers_app_defaults_under_json_and_overrides(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({
                "ssh_threshold": 8,
                "http_4xx_threshold": 6,
            }), encoding="utf-8")
            panel = ConfigPanel(analysis_defaults={
                "ssh_threshold": 5,
                "portscan_threshold": 11,
            })
            self.assertEqual(panel.effective_config().ssh_threshold, 5)
            self.assertTrue(panel.load_config_file(path))
            self.assertEqual(panel.effective_config().ssh_threshold, 8)
            self.assertEqual(panel.effective_config().portscan_threshold, 11)
            panel.set_override("ssh_threshold", 9)
            effective = panel.effective_config()
            self.assertEqual(effective.ssh_threshold, 9)
            self.assertEqual(effective.http_4xx_threshold, 6)
            self.assertEqual(effective.portscan_threshold, 11)
            panel.close()
            panel.deleteLater()
            self.app.processEvents()
