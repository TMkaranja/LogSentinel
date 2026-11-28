"""Isolated fallback geometry for the four original icon proposals.

Candidate-only module: it is not imported by LogSentinel. The path data is
newly drawn for the proposal set and is not copied from the live loader.
"""

ICON_PATHS: dict[str, str] = {
    "check": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="m12 7.4 1.2 3.4 3.4 1.2-3.4 1.2-1.2 3.4-1.2-3.4-3.4-1.2 3.4-1.2Z"/>'
    ),
    "download": (
        '<path d="M6.2 20.3V4.1c0-.6.5-1.1 1.1-1.1h6.4l4.8 4.8v12.5'
        'c0 .6-.5 1.1-1.1 1.1H7.3c-.6 0-1.1-.5-1.1-1.1Z"/>'
        '<path d="M13.6 3.2v4.9h4.8"/>'
        '<path d="M12 9.4v6.7"/>'
        '<path d="m9.5 13.6 2.5 2.6 2.5-2.6"/>'
    ),
    "folder_open": (
        '<path d="M3.2 7.2V5.8c0-.9.7-1.6 1.6-1.6h4l2 2.2h8.3'
        'c.9 0 1.6.7 1.6 1.6v1.3"/>'
        '<path d="m4 11.1 1.1 7.1c.1.9.9 1.5 1.8 1.5h11.3'
        'c.8 0 1.5-.5 1.8-1.3l1.5-4.4c.3-.9-.3-1.8-1.2-1.8H9.2'
        'c-.7 0-1.3.3-1.8.8L4 16"/>'
    ),
    "x": (
        '<path d="m4.7 16.1 8.6-9.2 6.1 5.7-8.6 9.2a1.7 1.7 0 0 1-2.4.1l-3.6-3.4a1.7 1.7 0 0 1-.1-2.4Z"/>'
        '<path d="m13.3 6.9 2-2.1a1.7 1.7 0 0 1 2.4-.1l3.6 3.4a1.7 1.7 0 0 1 .1 2.4l-2 2.1"/>'
        '<path d="M5.9 21h13.4"/>'
    ),
}

SVG_HEADER = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="none" stroke="CURRENT_COLOR" stroke-width="1.8" '
    'stroke-linecap="round" stroke-linejoin="round">'
)
SVG_FOOTER = "</svg>"


def icon_svg(name: str) -> str:
    """Compose a proposal fallback SVG using the application conventions."""
    return SVG_HEADER + ICON_PATHS[name] + SVG_FOOTER
