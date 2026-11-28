"""Local vector icon and brand-asset support for the LogSentinel GUI.

The application ships SVG assets under ``gui/assets``. If a wheel/build omits
those data files, matching local path data is embedded here as a fallback so
the interface never falls back to remote assets or emoji glyphs.

SVG placeholders are replaced at render time, which keeps every icon and
brand mark consistent with the active theme without maintaining four copies
of each file.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .themes import Theme

__all__ = [
    "brand_icon",
    "brand_pixmap",
    "icon",
    "icon_pixmap",
    "theme_preview_pixmap",
    "available_icon_names",
]

ASSET_ROOT = Path(__file__).resolve().parent / "assets"

_ICON_PATHS: dict[str, str] = {
    "overview": (
        '<path d="M3 7V5a2 2 0 0 1 2-2h2"/>'
        '<path d="M17 3h2a2 2 0 0 1 2 2v2"/>'
        '<path d="M21 17v2a2 2 0 0 1-2 2h-2"/>'
        '<path d="M7 21H5a2 2 0 0 1-2-2v-2"/>'
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="m16 16-1.9-1.9"/>'
    ),
    "detections": (
        '<path d="M20 13c0 5-3.5 7.5-7.7 8.9a1 1 0 0 1-.6 0'
        'C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.2-2.7'
        'a1 1 0 0 1 1.6 0C14.5 3.8 17 5 19 5a1 1 0 0 1 1 1z"/>'
        '<path d="M12 8v4"/><path d="M12 16h.01"/>'
    ),
    "log_explorer": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12'
        'a2 2 0 0 0 2-2V8Z"/>'
        '<path d="M14 2v6h6"/><circle cx="11" cy="14" r="3"/>'
        '<path d="m16 19-1.8-1.8"/>'
    ),
    "reports": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12'
        'a2 2 0 0 0 2-2V8Z"/>'
        '<path d="M14 2v6h6"/><path d="M8 18v-2"/>'
        '<path d="M12 18v-4"/><path d="M16 18v-6"/>'
    ),
    "settings": (
        '<path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73'
        'l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38'
        'a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 '
        '1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73'
        'l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 '
        '2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 '
        '1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73'
        'l-.15-.09a2 2 0 0 1-1-1.74v-.51a2 2 0 0 1 1-1.74l.15-.09a2 '
        '2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 '
        '0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>'
        '<circle cx="12" cy="12" r="3"/>'
    ),
    "play": '<path d="m5 3 14 9-14 9V3Z"/>',
    "stop": '<rect x="6" y="6" width="12" height="12" rx="1.5"/>',
    "download": (
        '<path d="M6.2 20.3V4.1c0-.6.5-1.1 1.1-1.1h6.4l4.8 4.8v12.5'
        'c0 .6-.5 1.1-1.1 1.1H7.3c-.6 0-1.1-.5-1.1-1.1Z"/>'
        '<path d="M13.6 3.2v4.9h4.8"/>'
        '<path d="M12 9.4v6.7"/>'
        '<path d="m9.5 13.6 2.5 2.6 2.5-2.6"/>'
    ),
    "file_plus": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12'
        'a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/>'
        '<path d="M12 12v6"/><path d="M9 15h6"/>'
    ),
    "folder_open": (
        '<path d="M3.2 7.2V5.8c0-.9.7-1.6 1.6-1.6h4l2 2.2h8.3'
        'c.9 0 1.6.7 1.6 1.6v1.3"/>'
        '<path d="m4 11.1 1.1 7.1c.1.9.9 1.5 1.8 1.5h11.3'
        'c.8 0 1.5-.5 1.8-1.3l1.5-4.4c.3-.9-.3-1.8-1.2-1.8H9.2'
        'c-.7 0-1.3.3-1.8.8L4 16"/>'
    ),
    "trash": (
        '<path d="M3 6h18"/><path d="M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 '
        '1 1v2"/><path d="M19 6l-1 15a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>'
        '<path d="M10 11v5"/><path d="M14 11v5"/>'
    ),
    "search": (
        '<circle cx="11" cy="11" r="8"/>'
        '<path d="m21 21-4.3-4.3"/>'
    ),
    "shield_check": (
        '<path d="M20 13c0 5-3.5 7.5-7.7 8.9a1 1 0 0 1-.6 0'
        'C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.2-2.7'
        'a1 1 0 0 1 1.6 0C14.5 3.8 17 5 19 5a1 1 0 0 1 1 1z"/>'
        '<path d="m9 12 2 2 4-4"/>'
    ),
    "file_text": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12'
        'a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/>'
        '<path d="M8 13h8"/><path d="M8 17h8"/>'
    ),
    "palette": (
        '<circle cx="13.5" cy="6.5" r=".5"/>'
        '<circle cx="17.5" cy="10.5" r=".5"/>'
        '<circle cx="8.5" cy="7.5" r=".5"/>'
        '<circle cx="6.5" cy="12.5" r=".5"/>'
        '<path d="M12 2a10 10 0 0 0 0 20c1.1 0 2-.9 2-2'
        ' 0-.5-.2-1-.5-1.4-.3-.4-.5-.8-.5-1.3 0-1.1.9-2 2-2h1.5'
        'a4 4 0 0 0 4-4A10 10 0 0 0 12 2Z"/>'
    ),
    "check": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="m12 7.4 1.2 3.4 3.4 1.2-3.4 1.2-1.2 3.4-1.2-3.4-3.4-1.2 3.4-1.2Z"/>'
    ),
    "alert": (
        '<path d="m21.7 18-8-14a2 2 0 0 0-3.4 0l-8 14'
        'A2 2 0 0 0 4 22h16a2 2 0 0 0 1.7-4Z"/>'
        '<path d="M12 9v4"/><path d="M12 17h.01"/>'
    ),
    "x": (
        '<path d="m4.7 16.1 8.6-9.2 6.1 5.7-8.6 9.2a1.7 1.7 0 0 1-2.4.1l-3.6-3.4a1.7 1.7 0 0 1-.1-2.4Z"/>'
        '<path d="m13.3 6.9 2-2.1a1.7 1.7 0 0 1 2.4-.1l3.6 3.4a1.7 1.7 0 0 1 .1 2.4l-2 2.1"/>'
        '<path d="M5.9 21h13.4"/>'
    ),
}

_ICON_HEADER = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'fill="none" stroke="CURRENT_COLOR" stroke-width="1.8" '
    'stroke-linecap="round" stroke-linejoin="round">'
)
_ICON_FOOTER = "</svg>"

_BRAND_MARK_FALLBACK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<defs>
  <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="CURRENT_START"/>
    <stop offset="1" stop-color="CURRENT_END"/>
  </linearGradient>
</defs>
<rect x="3" y="3" width="58" height="58" rx="15" fill="url(#tile)"
      stroke="CURRENT_BORDER" stroke-width="1.2"/>
<path d="M15 33c4-9 13-14 17-14s13 5 17 14c-4 9-13 14-17 14S19 42 15 33Z"
      fill="CURRENT_FOREGROUND" opacity="0.96"/>
<circle cx="32" cy="33" r="6" fill="CURRENT_PUPIL"/>
<circle cx="34" cy="31" r="1.6" fill="CURRENT_FOREGROUND" opacity="0.8"/>
<path d="M32 11v5M32 47v5M11 33h5M48 33h5"
      stroke="CURRENT_FOREGROUND" stroke-width="2" stroke-linecap="round"
      opacity="0.55"/>
<path d="M20 51c4 2 20 2 24 0" fill="none" stroke="CURRENT_FOREGROUND"
      stroke-width="1.6" stroke-linecap="round" opacity="0.4"/>
</svg>
"""

_BRAND_LOGO_FALLBACK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 64">
<defs>
  <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="CURRENT_START"/>
    <stop offset="1" stop-color="CURRENT_END"/>
  </linearGradient>
</defs>
<g transform="translate(2 2) scale(0.9375)">
  <rect x="3" y="3" width="58" height="58" rx="15" fill="url(#tile)" stroke="CURRENT_BORDER" stroke-width="1.2"/>
  <path d="M15 33c4-9 13-14 17-14s13 5 17 14c-4 9-13 14-17 14S19 42 15 33Z" fill="CURRENT_FOREGROUND" opacity="0.96"/>
  <circle cx="32" cy="33" r="6" fill="CURRENT_PUPIL"/>
  <circle cx="34" cy="31" r="1.6" fill="CURRENT_FOREGROUND" opacity="0.8"/>
  <path d="M32 11v5M32 47v5M11 33h5M48 33h5" stroke="CURRENT_FOREGROUND" stroke-width="2" stroke-linecap="round" opacity="0.55"/>
  <path d="M20 51c4 2 20 2 24 0" fill="none" stroke="CURRENT_FOREGROUND" stroke-width="1.6" stroke-linecap="round" opacity="0.4"/>
</g>
<path d="M 83.93 36.00 L 73.92 36.00 L 73.92 19.20 L 77.71 19.20 L 77.71 32.93 L 83.93 32.93 L 83.93 36.00 Z M 91.28 36.29 L 88.60 35.87 L 86.56 34.61 L 85.27 32.63 L 84.84 30.05 L 85.29 27.39 L 86.62 25.39 L 88.72 24.13 L 91.44 23.71 L 94.11 24.13 L 96.13 25.39 L 97.40 27.34 L 97.83 29.84 L 97.39 32.51 L 96.08 34.56 L 94.00 35.86 L 91.28 36.29 Z M 91.37 26.54 L 90.21 26.77 L 89.33 27.45 L 88.61 30.00 L 89.30 32.59 L 90.17 33.24 L 91.39 33.46 L 92.56 33.24 L 93.39 32.57 L 94.05 29.91 L 93.38 27.38 L 92.55 26.75 L 91.37 26.54 Z M 112.32 34.63 L 111.84 37.59 L 110.39 39.80 L 108.02 41.18 L 104.79 41.64 L 100.95 40.95 L 100.95 37.83 L 102.81 38.64 L 104.68 38.91 L 106.35 38.66 L 107.59 37.92 L 108.36 36.75 L 108.62 35.23 L 108.62 34.28 L 108.57 34.28 L 107.01 35.79 L 104.84 36.29 L 102.78 35.89 L 101.19 34.68 L 100.18 32.78 L 99.84 30.34 L 100.22 27.61 L 101.34 25.50 L 103.08 24.16 L 105.29 23.71 L 107.21 24.13 L 108.57 25.39 L 108.62 25.39 L 108.62 24.00 L 112.32 24.00 L 112.32 34.63 Z M 108.67 30.23 L 108.67 29.29 L 107.99 27.35 L 106.24 26.54 L 105.14 26.78 L 104.31 27.50 L 103.61 30.21 L 104.27 32.58 L 106.10 33.46 L 107.96 32.57 L 108.67 30.23 Z" fill="CURRENT_TEXT"/>
<path d="M 115.15 35.36 L 115.15 31.61 L 117.36 32.89 L 119.78 33.32 L 121.03 33.19 L 121.92 32.83 L 122.45 32.29 L 122.58 31.97 L 122.62 31.62 L 122.34 30.74 L 121.58 30.02 L 120.42 29.39 L 118.98 28.77 L 116.04 26.77 L 115.32 25.46 L 115.08 23.91 L 115.61 21.65 L 117.04 20.10 L 119.14 19.20 L 121.68 18.91 L 124.00 19.07 L 125.87 19.56 L 125.87 23.06 L 124.95 22.55 L 123.93 22.18 L 122.88 21.96 L 121.89 21.89 L 120.71 22.01 L 119.82 22.36 L 119.26 22.89 L 119.11 23.22 L 119.06 23.59 L 119.12 23.99 L 119.19 24.17 L 119.29 24.35 L 119.92 24.98 L 120.91 25.56 L 122.24 26.16 L 124.05 27.05 L 125.43 28.12 L 126.30 29.49 L 126.61 31.28 L 126.08 33.64 L 124.63 35.19 L 122.50 36.04 L 119.94 36.29 L 117.31 36.06 L 115.15 35.36 Z M 139.34 31.05 L 131.51 31.05 L 132.43 33.01 L 134.80 33.67 L 136.67 33.43 L 138.29 32.73 L 138.29 35.40 L 136.37 36.07 L 133.96 36.29 L 131.38 35.89 L 129.45 34.68 L 128.25 32.75 L 127.84 30.19 L 128.28 27.51 L 129.58 25.45 L 131.51 24.14 L 133.84 23.71 L 136.17 24.10 L 137.90 25.27 L 138.98 27.10 L 139.34 29.50 L 139.34 31.05 Z M 135.91 28.78 L 135.38 26.85 L 133.82 26.20 L 132.28 26.94 L 131.49 28.78 L 135.91 28.78 Z M 153.15 36.00 L 149.46 36.00 L 149.46 29.33 L 148.96 27.24 L 147.46 26.54 L 145.88 27.28 L 145.26 29.16 L 145.26 36.00 L 141.56 36.00 L 141.56 24.00 L 145.26 24.00 L 145.26 25.90 L 145.31 25.90 L 146.93 24.25 L 149.16 23.71 L 150.91 24.02 L 152.15 24.94 L 152.90 26.49 L 153.15 28.65 L 153.15 36.00 Z M 163.81 35.86 L 161.34 36.29 L 159.63 36.04 L 158.40 35.28 L 157.67 34.01 L 157.43 32.23 L 157.43 26.73 L 155.48 26.73 L 155.48 24.00 L 157.43 24.00 L 157.43 21.41 L 161.12 20.36 L 161.12 24.00 L 163.81 24.00 L 163.81 26.73 L 161.12 26.73 L 161.12 31.58 L 161.49 32.99 L 162.61 33.46 L 163.81 33.12 L 163.81 35.86 Z M 167.43 22.10 L 165.90 21.54 L 165.30 20.18 L 165.90 18.82 L 167.43 18.29 L 168.97 18.82 L 169.57 20.18 L 168.97 21.56 L 167.43 22.10 Z M 169.26 36.00 L 165.56 36.00 L 165.56 24.00 L 169.26 24.00 L 169.26 36.00 Z M 184.15 36.00 L 180.46 36.00 L 180.46 29.33 L 179.96 27.24 L 178.46 26.54 L 176.88 27.28 L 176.26 29.16 L 176.26 36.00 L 172.56 36.00 L 172.56 24.00 L 176.26 24.00 L 176.26 25.90 L 176.31 25.90 L 177.93 24.25 L 180.16 23.71 L 181.91 24.02 L 183.15 24.94 L 183.90 26.49 L 184.15 28.65 L 184.15 36.00 Z M 198.34 31.05 L 190.51 31.05 L 191.43 33.01 L 193.80 33.67 L 195.67 33.43 L 197.29 32.73 L 197.29 35.40 L 195.37 36.07 L 192.96 36.29 L 190.38 35.89 L 188.45 34.68 L 187.25 32.75 L 186.84 30.19 L 187.28 27.51 L 188.58 25.45 L 190.51 24.14 L 192.84 23.71 L 195.17 24.10 L 196.90 25.27 L 197.98 27.10 L 198.34 29.50 L 198.34 31.05 Z M 194.91 28.78 L 194.38 26.85 L 192.82 26.20 L 191.28 26.94 L 190.49 28.78 L 194.91 28.78 Z M 204.26 36.00 L 200.56 36.00 L 200.56 18.23 L 204.26 18.23 L 204.26 36.00 Z" fill="CURRENT_ACCENT"/>
<path d="M 73.56 50.00 L 73.56 45.10 L 75.30 45.10 L 77.26 45.70 L 77.91 47.49 L 77.20 49.32 L 75.30 50.00 L 73.56 50.00 Z M 74.66 46.00 L 74.66 49.10 L 75.21 49.10 L 76.34 48.67 L 76.75 47.50 L 76.34 46.40 L 75.20 46.00 L 74.66 46.00 Z M 82.75 50.00 L 79.81 50.00 L 79.81 45.10 L 82.64 45.10 L 82.64 46.00 L 80.91 46.00 L 80.91 47.09 L 82.52 47.09 L 82.52 47.98 L 80.91 47.98 L 80.91 49.10 L 82.75 49.10 L 82.75 50.00 Z M 87.89 46.00 L 86.16 46.00 L 86.16 47.20 L 87.75 47.20 L 87.75 48.10 L 86.16 48.10 L 86.16 50.00 L 85.06 50.00 L 85.06 45.10 L 87.89 45.10 L 87.89 46.00 Z M 93.25 50.00 L 90.31 50.00 L 90.31 45.10 L 93.14 45.10 L 93.14 46.00 L 91.41 46.00 L 91.41 47.09 L 93.02 47.09 L 93.02 47.98 L 91.41 47.98 L 91.41 49.10 L 93.25 49.10 L 93.25 50.00 Z M 99.97 50.00 L 98.86 50.00 L 96.84 46.92 L 96.69 46.68 L 96.59 46.51 L 96.58 46.51 L 96.60 46.84 L 96.60 47.31 L 96.60 50.00 L 95.56 50.00 L 95.56 45.10 L 96.75 45.10 L 98.69 48.08 L 98.82 48.28 L 98.94 48.48 L 98.95 48.48 L 98.93 47.81 L 98.93 45.10 L 99.97 45.10 L 99.97 50.00 Z M 102.58 49.81 L 102.58 48.72 L 103.23 49.09 L 103.58 49.19 L 103.94 49.22 L 104.30 49.18 L 104.56 49.08 L 104.71 48.92 L 104.77 48.72 L 104.68 48.47 L 104.46 48.26 L 104.12 48.07 L 103.92 47.98 L 103.70 47.89 L 102.85 47.31 L 102.56 46.47 L 102.60 46.12 L 102.72 45.81 L 102.90 45.56 L 103.14 45.36 L 103.42 45.21 L 103.75 45.10 L 104.11 45.04 L 104.49 45.02 L 104.85 45.03 L 105.17 45.06 L 105.45 45.12 L 105.71 45.20 L 105.71 46.23 L 105.44 46.08 L 105.15 45.97 L 104.84 45.91 L 104.55 45.88 L 104.21 45.92 L 103.95 46.02 L 103.78 46.18 L 103.73 46.38 L 103.79 46.60 L 103.98 46.79 L 104.27 46.96 L 104.45 47.04 L 104.65 47.13 L 104.93 47.26 L 105.18 47.39 L 105.40 47.54 L 105.58 47.70 L 105.73 47.89 L 105.84 48.10 L 105.91 48.34 L 105.93 48.62 L 105.89 49.00 L 105.77 49.31 L 105.59 49.56 L 105.35 49.76 L 105.06 49.91 L 104.73 50.01 L 104.37 50.07 L 103.98 50.09 L 103.59 50.07 L 103.22 50.02 L 102.88 49.93 L 102.58 49.81 Z M 109.16 50.00 L 108.06 50.00 L 108.06 45.10 L 109.16 45.10 L 109.16 50.00 Z M 115.39 45.10 L 113.70 50.00 L 112.45 50.00 L 110.78 45.10 L 111.97 45.10 L 113.00 48.51 L 113.06 48.77 L 113.09 49.00 L 113.12 49.00 L 113.15 48.76 L 113.22 48.50 L 114.24 45.10 L 115.39 45.10 Z M 120.50 50.00 L 117.56 50.00 L 117.56 45.10 L 120.39 45.10 L 120.39 46.00 L 118.66 46.00 L 118.66 47.09 L 120.27 47.09 L 120.27 47.98 L 118.66 47.98 L 118.66 49.10 L 120.50 49.10 L 120.50 50.00 Z M 128.98 50.00 L 126.06 50.00 L 126.06 45.10 L 127.16 45.10 L 127.16 49.10 L 128.98 49.10 L 128.98 50.00 Z M 132.38 50.09 L 130.67 49.40 L 130.00 47.61 L 130.68 45.73 L 132.46 45.02 L 134.16 45.70 L 134.81 47.52 L 134.13 49.38 L 132.38 50.09 Z M 132.43 45.97 L 131.51 46.40 L 131.17 47.56 L 131.51 48.71 L 132.40 49.13 L 133.31 48.72 L 133.64 47.58 L 133.32 46.39 L 132.43 45.97 Z M 140.58 49.67 L 138.80 50.09 L 136.93 49.43 L 136.25 47.63 L 137.00 45.74 L 138.98 45.02 L 140.35 45.23 L 140.35 46.27 L 138.97 45.94 L 137.85 46.39 L 137.42 47.58 L 137.80 48.75 L 138.85 49.16 L 139.21 49.13 L 139.48 49.05 L 139.48 48.09 L 138.50 48.09 L 138.50 47.21 L 140.58 47.21 L 140.58 49.67 Z M 147.16 50.00 L 146.06 50.00 L 146.06 45.10 L 147.16 45.10 L 147.16 50.00 Z M 153.72 50.00 L 152.61 50.00 L 150.59 46.92 L 150.44 46.68 L 150.34 46.51 L 150.33 46.51 L 150.35 46.84 L 150.35 47.31 L 150.35 50.00 L 149.31 50.00 L 149.31 45.10 L 150.50 45.10 L 152.44 48.08 L 152.57 48.28 L 152.69 48.48 L 152.70 48.48 L 152.68 47.81 L 152.68 45.10 L 153.72 45.10 L 153.72 50.00 Z M 160.00 46.00 L 158.60 46.00 L 158.60 50.00 L 157.50 50.00 L 157.50 46.00 L 156.11 46.00 L 156.11 45.10 L 160.00 45.10 L 160.00 46.00 Z M 164.75 50.00 L 161.81 50.00 L 161.81 45.10 L 164.64 45.10 L 164.64 46.00 L 162.91 46.00 L 162.91 47.09 L 164.52 47.09 L 164.52 47.98 L 162.91 47.98 L 162.91 49.10 L 164.75 49.10 L 164.75 50.00 Z M 169.98 50.00 L 167.06 50.00 L 167.06 45.10 L 168.16 45.10 L 168.16 49.10 L 169.98 49.10 L 169.98 50.00 Z M 175.23 50.00 L 172.31 50.00 L 172.31 45.10 L 173.41 45.10 L 173.41 49.10 L 175.23 49.10 L 175.23 50.00 Z M 178.66 50.00 L 177.56 50.00 L 177.56 45.10 L 178.66 45.10 L 178.66 50.00 Z M 184.83 49.67 L 183.05 50.09 L 181.18 49.43 L 180.50 47.63 L 181.25 45.74 L 183.23 45.02 L 184.60 45.23 L 184.60 46.27 L 183.22 45.94 L 182.10 46.39 L 181.67 47.58 L 182.05 48.75 L 183.10 49.16 L 183.46 49.13 L 183.73 49.05 L 183.73 48.09 L 182.75 48.09 L 182.75 47.21 L 184.83 47.21 L 184.83 49.67 Z M 190.00 50.00 L 187.06 50.00 L 187.06 45.10 L 189.89 45.10 L 189.89 46.00 L 188.16 46.00 L 188.16 47.09 L 189.77 47.09 L 189.77 47.98 L 188.16 47.98 L 188.16 49.10 L 190.00 49.10 L 190.00 50.00 Z M 196.72 50.00 L 195.61 50.00 L 193.59 46.92 L 193.44 46.68 L 193.34 46.51 L 193.33 46.51 L 193.35 46.84 L 193.35 47.31 L 193.35 50.00 L 192.31 50.00 L 192.31 45.10 L 193.50 45.10 L 195.44 48.08 L 195.57 48.28 L 195.69 48.48 L 195.70 48.48 L 195.68 47.81 L 195.68 45.10 L 196.72 45.10 L 196.72 50.00 Z M 203.07 49.83 L 201.67 50.09 L 199.90 49.42 L 199.25 47.66 L 199.98 45.75 L 201.86 45.02 L 203.07 45.20 L 203.07 46.26 L 201.95 45.97 L 200.84 46.40 L 200.42 47.58 L 200.81 48.71 L 201.89 49.13 L 203.07 48.82 L 203.07 49.83 Z M 207.75 50.00 L 204.81 50.00 L 204.81 45.10 L 207.64 45.10 L 207.64 46.00 L 205.91 46.00 L 205.91 47.09 L 207.52 47.09 L 207.52 47.98 L 205.91 47.98 L 205.91 49.10 L 207.75 49.10 L 207.75 50.00 Z" fill="CURRENT_MUTED"/>
</svg>
"""


def _read_asset(relative: str) -> str | None:
    path = ASSET_ROOT / relative
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def _with_color(svg: str, color: str) -> str:
    return svg.replace("CURRENT_COLOR", color)


def _with_brand_tokens(svg: str, theme: Theme) -> str:
    replacements = {
        "CURRENT_START": theme.logo_start,
        "CURRENT_END": theme.logo_end,
        "CURRENT_FOREGROUND": theme.logo_foreground,
        "CURRENT_BORDER": theme.logo_border,
        "CURRENT_PUPIL": theme.logo_end,
        "CURRENT_TEXT": theme.text,
        "CURRENT_ACCENT": theme.accent,
        "CURRENT_MUTED": theme.text_muted,
    }
    for token, value in replacements.items():
        svg = svg.replace(token, value)
    return svg


def icon_svg(name: str, color: str) -> str:
    """Return one local icon SVG with the requested stroke colour."""
    asset = _read_asset(f"icons/{name}.svg")
    if asset is None:
        paths = _ICON_PATHS.get(name, _ICON_PATHS["shield_check"])
        asset = _ICON_HEADER + paths + _ICON_FOOTER
    return _with_color(asset, color)


@lru_cache(maxsize=256)
def icon_pixmap(name: str, size: int, color: str) -> QPixmap:
    """Render a vector icon to a transparent pixmap at one size."""
    svg = icon_svg(name, color)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return pixmap


def icon(name: str, color: str, sizes: tuple[int, ...] = (16, 20, 24, 32)) -> QIcon:
    """Build a multi-resolution QIcon from a local SVG icon."""
    result = QIcon()
    for size in sizes:
        result.addPixmap(icon_pixmap(name, size, color))
    return result


def brand_mark_svg(theme: Theme) -> str:
    asset = _read_asset("brand/logsentinel-mark.svg")
    return _with_brand_tokens(asset or _BRAND_MARK_FALLBACK, theme)


def brand_logo_svg(theme: Theme, *, sidebar: bool = False) -> str:
    filename = "logsentinel-sidebar.svg" if sidebar else "logsentinel-logo.svg"
    asset = _read_asset(f"brand/{filename}")
    return _with_brand_tokens(asset or _BRAND_LOGO_FALLBACK, theme)


@lru_cache(maxsize=32)
def _brand_mark_pixmap_cached(theme_key: str, size: int) -> QPixmap:
    from .themes import get_theme

    svg = brand_mark_svg(get_theme(theme_key))
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return pixmap


def brand_mark_pixmap(theme: Theme, size: int) -> QPixmap:
    return _brand_mark_pixmap_cached(theme.key, size)


def brand_icon(theme: Theme) -> QIcon:
    """Window/taskbar icon with multiple native sizes."""
    result = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        result.addPixmap(brand_mark_pixmap(theme, size))
    return result


@lru_cache(maxsize=32)
def _brand_logo_pixmap_cached(
    theme_key: str, width: int, height: int, sidebar: bool
) -> QPixmap:
    from .themes import get_theme

    svg = brand_logo_svg(get_theme(theme_key), sidebar=sidebar)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter, QRectF(0, 0, width, height))
    painter.end()
    return pixmap


def brand_pixmap(
    theme: Theme,
    width: int,
    height: int,
    *,
    sidebar: bool = False,
) -> QPixmap:
    return _brand_logo_pixmap_cached(theme.key, width, height, sidebar)


@lru_cache(maxsize=32)
def theme_preview_pixmap(theme: Theme, width: int = 54, height: int = 32) -> QPixmap:
    """Small graphic swatch used by the Settings theme selector."""
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(theme.background))
    painter.drawRoundedRect(QRectF(0, 0, width, height), 6, 6)
    painter.setBrush(QColor(theme.surface))
    painter.drawRoundedRect(QRectF(4, 4, width - 8, height - 8), 4, 4)
    painter.setBrush(QColor(theme.sidebar))
    painter.drawRoundedRect(QRectF(7, 7, 10, height - 14), 2, 2)
    painter.setBrush(QColor(theme.accent))
    painter.drawRoundedRect(QRectF(21, 8, 12, 3), 1.5, 1.5)
    painter.setBrush(QColor(theme.text_muted))
    painter.drawRoundedRect(QRectF(21, 14, width - 29, 2), 1, 1)
    painter.drawRoundedRect(QRectF(21, 19, width - 35, 2), 1, 1)
    painter.end()
    return pixmap


def available_icon_names() -> tuple[str, ...]:
    return tuple(sorted(_ICON_PATHS))
