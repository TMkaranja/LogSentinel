"""Application bootstrap for the optional LogSentinel PySide6 GUI.

Launch with either of:

    python -m logsentinel.gui
    logsentinel-gui            (when a GUI entry point is packaged)

This module is imported only by the GUI package. The CLI and the headless
analysis backend never import PySide6, so they continue to work without Qt.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtWidgets import QApplication

from .. import __version__
from .app_settings import SettingsStore
from .themes import DEFAULT_THEME_KEY
from .main_window import MainWindow
from .theme import (
    APP_NAME,
    APP_ORGANIZATION,
    apply_theme,
    create_app_icon,
)

__all__ = ["create_application", "main"]


def create_application(argv: Sequence[str] | None = None) -> QApplication:
    """Create or reuse the QApplication and apply the LogSentinel theme."""
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        app = existing
    else:
        arguments = list(argv) if argv is not None else list(sys.argv)
        app = QApplication(arguments)

    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(__version__)
    app.setOrganizationName(APP_ORGANIZATION)
    app.setWindowIcon(create_app_icon())
    apply_theme(app, DEFAULT_THEME_KEY)
    return app


def main(argv: Sequence[str] | None = None) -> int:
    """Launch the LogSentinel desktop shell and enter the Qt event loop."""
    app = create_application(argv)
    window = MainWindow(settings_store=SettingsStore())
    window.show()
    return app.exec()


if __name__ == "__main__":  # pragma: no cover - module execution guard
    raise SystemExit(main())
