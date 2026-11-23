"""``python -m logsentinel.gui`` entry point for the desktop application."""

from __future__ import annotations

from .app import main

__all__ = ["main"]


if __name__ == "__main__":
    raise SystemExit(main())
