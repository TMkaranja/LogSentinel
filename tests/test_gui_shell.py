"""Offscreen smoke tests for the LogSentinel desktop shell.

The tests set ``QT_QPA_PLATFORM=offscreen`` before importing PySide6 so they
run on headless CI hosts. They are skipped cleanly when the optional GUI
dependency is not installed.

No analysis functionality is exercised here: Step 2 is the application
shell and dark theme only.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:  # Optional GUI dependency; the CLI itself never imports PySide6.
    from PySide6.QtGui import QColor, QPalette
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QPushButton,
        QStackedWidget,
        QStatusBar,
    )

    from logsentinel.gui.app import create_application, main
    from logsentinel.gui.main_window import MainWindow
    from logsentinel.gui.theme import (
        APP_NAME,
        COLOR_BACKGROUND,
        STYLESHEET,
        dark_palette,
    )

    PYSIDE_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only without PySide6
    PYSIDE_AVAILABLE = False


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class GuiShellTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_application(["logsentinel-gui-tests"])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def _nav_button(self, label):
        for button in self.window.findChildren(QPushButton, "NavButton"):
            if label in button.text():
                return button
        self.fail(f"navigation button not found: {label}")

    def test_application_and_window_launch(self):
        self.assertIsInstance(self.app, QApplication)
        self.assertEqual(self.app.applicationName(), APP_NAME)
        self.assertIn("LogSentinel", self.window.windowTitle())
        self.assertTrue(self.window.isVisible())
        self.assertGreaterEqual(self.window.width(), 1080)
        self.assertGreaterEqual(self.window.height(), 680)

    def test_branding_and_status_bar_are_present(self):
        brand_names = [
            label.text()
            for label in self.window.findChildren(QLabel, "BrandName")
        ]
        self.assertIn("LogSentinel", brand_names)
        status_bar = self.window.findChild(QStatusBar, "AppStatusBar")
        self.assertIsNotNone(status_bar)
        self.assertIn("ready", status_bar.currentMessage().lower())
        self.assertGreaterEqual(
            len(status_bar.findChildren(QLabel)), 2)

    def test_sidebar_has_all_required_pages(self):
        expected = (
            "overview",
            "detections",
            "log_explorer",
            "reports",
            "settings",
        )
        self.assertEqual(self.window.navigation_keys, expected)
        self.assertEqual(self.window.workspace_stack.count(), len(expected))
        labels = (
            "Overview", "Detections", "Log Explorer", "Reports", "Settings")
        for label in labels:
            button = self._nav_button(label)
            self.assertTrue(button.isCheckable())
        self.assertEqual(len(labels), self.window.workspace_stack.count())

    def test_navigation_updates_page_header_and_stack(self):
        stack = self.window.findChild(QStackedWidget, "WorkspaceStack")
        title = self.window.findChild(QLabel, "PageTitle")
        subtitle = self.window.findChild(QLabel, "PageSubtitle")
        self.assertIsNotNone(stack)
        self.assertIsNotNone(title)
        self.assertIsNotNone(subtitle)
        self.assertEqual(self.window.current_page_key, "overview")
        self.assertEqual(title.text(), "Overview")

        button = self._nav_button("Settings")
        button.click()
        self.app.processEvents()
        self.assertEqual(self.window.current_page_key, "settings")
        self.assertEqual(stack.currentIndex(), 4)
        self.assertEqual(title.text(), "Settings")
        self.assertIn("threshold", subtitle.text().lower())
        self.assertTrue(button.isChecked())

        labels = {
            "overview": "Overview",
            "detections": "Detections",
            "log_explorer": "Log Explorer",
            "reports": "Reports",
            "settings": "Settings",
        }
        for index, key in enumerate(self.window.navigation_keys):
            self.window.navigate_to(key)
            self.app.processEvents()
            self.assertEqual(self.window.current_page_key, key)
            self.assertEqual(self.window.workspace_stack.currentIndex(), index)
            self.assertTrue(self._nav_button(labels[key]).isChecked())

    def test_theme_is_dark_and_applied(self):
        self.assertIn(COLOR_BACKGROUND, STYLESHEET)
        self.assertTrue(self.app.styleSheet())
        palette = dark_palette()
        window_color = palette.color(QPalette.ColorRole.Window)
        self.assertIsInstance(window_color, QColor)
        self.assertLess(window_color.lightness(), 80)
        self.assertEqual(
            self.app.palette().color(QPalette.ColorRole.Window),
            QColor(COLOR_BACKGROUND),
        )

    def test_window_resizes_responsively(self):
        self.window.resize(1280, 800)
        self.app.processEvents()
        self.assertEqual(self.window.width(), 1280)
        self.assertEqual(self.window.height(), 800)
        self.assertIsNotNone(
            self.window.findChild(QStackedWidget, "WorkspaceStack"))

    def test_main_enters_and_leaves_event_loop_cleanly(self):
        with mock.patch.object(QApplication, "exec", return_value=0) as exec_spy:
            exit_code = main(["logsentinel-gui-tests"])
        self.assertEqual(exit_code, 0)
        exec_spy.assert_called_once()
        self.app.processEvents()


@unittest.skipUnless(PYSIDE_AVAILABLE, "PySide6 is not installed")
class GuiImportIsolationTestCase(unittest.TestCase):
    def test_cli_does_not_import_pyside6(self):
        env = os.environ.copy()
        source = str(PROJECT_ROOT / "src")
        env["PYTHONPATH"] = (
            source
            if not env.get("PYTHONPATH")
            else source + os.pathsep + env["PYTHONPATH"]
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sys; import logsentinel.cli; "
                "assert 'PySide6' not in sys.modules, 'CLI imported PySide6'; "
                "print('cli-import-ok')",
            ],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("cli-import-ok", result.stdout)


if __name__ == "__main__":  # pragma: no cover - unittest discovery entry
    unittest.main()
