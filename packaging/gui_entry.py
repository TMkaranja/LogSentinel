"""Dedicated PyInstaller entry point for the LogSentinel GUI."""

from logsentinel.gui.app import main


if __name__ == "__main__":
    raise SystemExit(main())
