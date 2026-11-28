"""Tests for the GUI input and configuration panels.

Offscreen smoke tests verify input discovery, duplicate prevention, removal,
JSON configuration loading, validation, and the "only edited fields override"
precedence rule. No analysis, worker, or detector path is exercised here.
"""

import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QListWidget,
        QPushButton,
        QSpinBox,
    )

    from logsentinel.config import AppConfig, load_config
    from logsentinel.gui.app import create_application
    from logsentinel.gui.icons import icon_pixmap
    from logsentinel.gui.main_window import MainWindow
    from logsentinel.gui.panels import ConfigPanel, InputPanel
    from logsentinel.gui.theme import current_theme

    PYSIDE_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without PySide6
    PYSIDE_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _norm(path):
    return os.path.normcase(os.path.abspath(os.fspath(path)))


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class PanelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-panel-tests"])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.temp = TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.auth = self.root / "auth.log"
        self.access = self.root / "access.txt"
        self.ignored = self.root / "notes.md"
        self.subdir = self.root / "nested"
        self.subdir.mkdir()
        self.nested_log = self.subdir / "nested.log"
        self.nested_txt = self.subdir / "extra.txt"
        self.auth.write_text(
            "Mar 10 11:20:01 h sshd[1]: Failed password for admin "
            "from 192.0.2.7 port 51001 ssh2\n", encoding="utf-8")
        self.access.write_text(
            "203.0.113.50 - - [10/Mar/2026:11:00:01 +0000] "
            '"GET /admin HTTP/1.1" 403 199\n', encoding="utf-8")
        self.ignored.write_text("not a log\n", encoding="utf-8")
        self.nested_log.write_text(
            "Mar 10 11:21:01 h sshd[2]: Failed password for root "
            "from 192.0.2.8 port 52001 ssh2\n", encoding="utf-8")
        self.nested_txt.write_text(
            "198.51.100.10 - - [10/Mar/2026:11:01:01 +0000] "
            '"GET / HTTP/1.1" 200 12\n', encoding="utf-8")

        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()
        self.inputs: InputPanel = self.window.input_panel
        self.config: ConfigPanel = self.window.config_panel

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def write_json(self, name, payload):
        path = self.root / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path


class TestInputSelection(PanelTestCase):
    def test_files_and_directory_are_added_and_previewed(self):
        outcome = self.inputs.add_paths(
            [self.auth, self.access, self.subdir])

        self.assertEqual(len(outcome.accepted), 3)
        self.assertEqual(outcome.duplicates, ())
        self.assertEqual(outcome.rejected, ())
        self.assertEqual(len(self.inputs.selected_paths), 3)
        self.assertEqual(
            {_norm(path) for path in self.inputs.selected_paths},
            {_norm(self.auth), _norm(self.access), _norm(self.subdir)},
        )
        # Explicit files are accepted regardless of extension; directory
        # discovery applies the existing .log/.txt filter.
        self.assertEqual(len(self.inputs.discovered_files), 4)
        self.assertIn("3 sources", self.inputs.summary_text)
        self.assertIn("4 log files", self.inputs.summary_text)

    def test_single_path_argument_is_not_split(self):
        outcome = self.inputs.add_paths(self.auth)
        self.assertEqual(len(outcome.accepted), 1)
        self.assertEqual(len(self.inputs.selected_paths), 1)

    def test_duplicate_entries_are_skipped(self):
        self.inputs.add_paths([self.auth])

        duplicate_forms = [
            self.auth,
            str(self.auth),  # same absolute path
            os.path.join(str(self.root), ".", self.auth.name),
        ]
        outcome = self.inputs.add_paths(duplicate_forms)

        self.assertEqual(len(self.inputs.selected_paths), 1)
        self.assertEqual(len(outcome.duplicates), 3)
        self.assertEqual(outcome.accepted, ())
        self.assertIn("duplicate", self.inputs.feedback_text.lower())

    def test_invalid_input_is_rejected_with_feedback(self):
        missing = self.root / "missing.log"
        outcome = self.inputs.add_paths([missing])

        self.assertEqual(self.inputs.selected_paths, ())
        self.assertEqual(outcome.accepted, ())
        self.assertEqual(len(outcome.rejected), 1)
        self.assertIn("rejected", self.inputs.feedback_text.lower())
        self.assertIn("does not exist", outcome.rejected[0][1])

    def test_remove_selected_and_clear_all(self):
        self.inputs.add_paths([self.auth, self.access])
        list_widget = self.inputs.findChild(QListWidget, "InputList")
        self.assertIsNotNone(list_widget)
        list_widget.setCurrentRow(0)
        self.app.processEvents()

        removed = self.inputs.remove_selected()
        self.assertEqual(len(removed), 1)
        self.assertEqual(len(self.inputs.selected_paths), 1)

        self.inputs.clear()
        self.assertEqual(self.inputs.selected_paths, ())
        self.assertEqual(self.inputs.discovered_files, ())
        self.assertIn("cleared", self.inputs.feedback_text.lower())

    def test_main_window_embeds_panels(self):
        self.assertIsInstance(self.window.input_panel, InputPanel)
        self.assertIsInstance(self.window.config_panel, ConfigPanel)

    def test_icon_actions_keep_clear_reset_and_remove_semantics(self):
        input_buttons = {
            button.text(): button
            for button in self.inputs.findChildren(QPushButton)
        }
        config_buttons = {
            button.text(): button
            for button in self.config.findChildren(QPushButton)
        }
        theme = current_theme()

        for text, tooltip in (
            ("Clear All", "Remove every selected input path"),
        ):
            button = input_buttons[text]
            self.assertEqual(button.toolTip(), tooltip)
            self.assertEqual(
                button.icon().pixmap(16, 16).toImage(),
                icon_pixmap("x", 16, theme.text_muted).toImage())

        remove = input_buttons["Remove Selected"]
        self.assertEqual(remove.toolTip(), "Remove the selected input paths")
        self.assertEqual(
            remove.icon().pixmap(16, 16).toImage(),
            icon_pixmap("trash", 16, theme.text_muted).toImage())

        folder_button = input_buttons["Add Folder"]
        self.assertEqual(
            folder_button.toolTip(),
            "Add a directory for recursive log discovery")
        browse_button = config_buttons["Browse"]
        self.assertEqual(
            browse_button.toolTip(),
            "Validate and load a JSON configuration file")

        clear_config = config_buttons["Clear"]
        reset = config_buttons["Reset Overrides"]
        for button, tooltip in (
            (clear_config, "Return to built-in defaults"),
            (reset, "Discard field edits and restore the loaded values"),
        ):
            self.assertEqual(button.toolTip(), tooltip)
            self.assertEqual(
                button.icon().pixmap(16, 16).toImage(),
                icon_pixmap("x", 16, theme.text_muted).toImage())

        apply = config_buttons["Apply"]
        self.assertEqual(apply.toolTip(), "Validate the combined configuration")
        self.assertEqual(
            apply.icon().pixmap(16, 16).toImage(),
            icon_pixmap("check", 16, theme.accent_text).toImage())
        self.assertEqual(folder_button.text(), "Add Folder")
        self.assertEqual(browse_button.text(), "Browse")


class TestConfiguration(PanelTestCase):
    def test_defaults_have_no_overrides(self):
        self.assertEqual(self.config.overrides(), {})
        self.assertEqual(self.config.effective_config(), load_config(None, None))
        self.assertIn("built-in defaults", self.config.feedback_text.lower())

    def test_json_load_and_only_edited_fields_override(self):
        path = self.write_json("config.json", {
            "ssh_threshold": 5,
            "portscan_threshold": 12,
            "strict": True,
            "max_file_mb": 64,
        })
        self.assertTrue(self.config.load_config_file(path))

        effective = self.config.effective_config()
        self.assertEqual(effective.ssh_threshold, 5)
        self.assertEqual(effective.portscan_threshold, 12)
        self.assertTrue(effective.strict)
        self.assertEqual(effective.max_file_mb, 64)
        self.assertEqual(self.config.overrides(), {})
        # The input panel follows the effective discovery size cap.
        self.assertEqual(self.inputs.max_file_mb, 64)

        spin = self.config.findChild(QSpinBox, "ssh_threshold_spin")
        strict = self.config.findChild(QCheckBox, "StrictModeCheck")
        self.assertEqual(spin.value(), 5)
        self.assertTrue(strict.isChecked())

        self.config.set_override("ssh_threshold", 7)
        self.assertEqual(self.config.overrides(), {"ssh_threshold": 7})
        effective = self.config.effective_config()
        self.assertEqual(effective.ssh_threshold, 7)
        self.assertEqual(effective.portscan_threshold, 12)  # JSON retained
        self.assertTrue(effective.strict)                   # JSON retained
        self.assertEqual(effective.max_file_mb, 64)         # JSON retained

        self.config.set_override("strict", False)
        self.assertEqual(
            self.config.overrides(),
            {"ssh_threshold": 7, "strict": False},
        )
        self.assertFalse(self.config.effective_config().strict)
        self.assertEqual(
            self.config.effective_config().portscan_threshold, 12)

    def test_apply_validates_and_preserves_overrides(self):
        self.config.set_override("ssh_threshold", 6)
        applied = self.config.apply_configuration()

        self.assertIsInstance(applied, AppConfig)
        self.assertEqual(applied.ssh_threshold, 6)
        self.assertEqual(self.config.overrides(), {"ssh_threshold": 6})
        self.assertEqual(
            self.config.effective_config().ssh_threshold, 6)
        self.assertIn("valid", self.config.feedback_text.lower())

    def test_invalid_json_is_rejected_without_changing_state(self):
        good = self.write_json("good.json", {"ssh_threshold": 5})
        self.assertTrue(self.config.load_config_file(good))
        self.assertEqual(self.config.config_path, str(good))

        bad = self.write_json("bad.json", {"ssh_threshold": "not-an-int"})
        self.assertFalse(self.config.load_config_file(bad))

        self.assertEqual(self.config.config_path, str(good))
        self.assertEqual(self.config.effective_config().ssh_threshold, 5)
        self.assertIn("positive integer", self.config.feedback_text.lower())

        unknown = self.write_json("unknown.json", {"mystery": 1})
        self.assertFalse(self.config.load_config_file(unknown))
        self.assertEqual(self.config.config_path, str(good))

    def test_clear_config_restores_defaults(self):
        path = self.write_json("config.json", {
            "ssh_threshold": 5,
            "strict": True,
        })
        self.assertTrue(self.config.load_config_file(path))
        self.config.set_override("portscan_threshold", 14)

        self.config.clear_config_file()

        self.assertIsNone(self.config.config_path)
        self.assertEqual(self.config.overrides(), {})
        self.assertEqual(self.config.effective_config(), load_config(None, None))
        self.assertEqual(self.inputs.max_file_mb, 512)
        self.assertIn("built-in defaults", self.config.feedback_text.lower())

    def test_reset_overrides_reloads_json_values(self):
        path = self.write_json("config.json", {"ssh_threshold": 5})
        self.assertTrue(self.config.load_config_file(path))
        self.config.set_override("ssh_threshold", 9)
        self.assertEqual(self.config.effective_config().ssh_threshold, 9)

        self.assertTrue(self.config.reset_overrides())

        self.assertEqual(self.config.overrides(), {})
        self.assertEqual(self.config.effective_config().ssh_threshold, 5)
        self.assertEqual(
            self.config.findChild(
                QSpinBox, "ssh_threshold_spin").value(), 5)

    def test_loading_a_new_config_discards_previous_overrides(self):
        first = self.write_json("first.json", {"ssh_threshold": 5})
        second = self.write_json("second.json", {"ssh_threshold": 9})
        self.assertTrue(self.config.load_config_file(first))
        self.config.set_override("ssh_threshold", 7)
        self.assertEqual(self.config.overrides(), {"ssh_threshold": 7})

        self.assertTrue(self.config.load_config_file(second))

        self.assertEqual(self.config.overrides(), {})
        self.assertEqual(self.config.effective_config().ssh_threshold, 9)

    def test_overrides_never_include_unedited_json_fields(self):
        path = self.write_json("config.json", {
            "ssh_threshold": 5,
            "ssh_window_seconds": 120,
            "portscan_threshold": 11,
            "http_4xx_threshold": 7,
        })
        self.assertTrue(self.config.load_config_file(path))
        self.config.set_override("http_4xx_threshold", 9)

        self.assertEqual(
            self.config.overrides(), {"http_4xx_threshold": 9})
        effective = self.config.effective_config()
        self.assertEqual(effective.ssh_threshold, 5)
        self.assertEqual(effective.ssh_window_seconds, 120)
        self.assertEqual(effective.portscan_threshold, 11)
        self.assertEqual(effective.http_4xx_threshold, 9)


if __name__ == "__main__":  # pragma: no cover - unittest discovery entry
    unittest.main()
