"""Optional desktop interface package for LogSentinel.

The GUI is an optional layer over the existing analysis pipeline. Importing
this package must never require PySide6: the headless analysis adapter in
:mod:`logsentinel.gui.backend` is standard-library only and is the only part
of the GUI used by backend tests.

Findings remain review leads for a human analyst, never assertions of
malicious intent.
"""
