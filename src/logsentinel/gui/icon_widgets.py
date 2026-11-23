"""Theme-aware icon labels and brand marks for the desktop shell."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from .icons import brand_mark_pixmap, brand_pixmap, icon, icon_pixmap
from .theme import current_theme, theme_manager

__all__ = [
    "BrandMarkLabel",
    "BrandWordmarkLabel",
    "ThemeIconButton",
    "ThemeIconLabel",
]

_ROLE_TO_TOKEN = {
    "accent": "accent",
    "accent_text": "accent_text",
    "accent_strong": "accent_strong",
    "muted": "text_muted",
    "dim": "text_dim",
    "soft": "text_soft",
    "text": "text",
    "danger": "danger",
    "success": "success",
    "warning": "warning",
}


class ThemeIconLabel(QLabel):
    """Vector icon that follows the active theme's semantic colour."""

    def __init__(
        self,
        icon_name: str,
        size: int = 20,
        *,
        role: str = "muted",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon_name = icon_name
        self._icon_size = size
        self._role = role
        self.setObjectName("ThemeIcon")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        theme_manager.changed.connect(self._refresh)
        self._refresh()

    @property
    def icon_name(self) -> str:
        return self._icon_name

    def set_icon_name(self, icon_name: str) -> None:
        self._icon_name = icon_name
        self._refresh()

    def _refresh(self, *_args) -> None:
        theme = current_theme()
        token = _ROLE_TO_TOKEN.get(self._role, "text_muted")
        color = getattr(theme, token)
        self.setPixmap(icon_pixmap(self._icon_name, self._icon_size, color))


class ThemeIconButton(QPushButton):
    """Button with a local vector icon that follows the active theme."""

    def __init__(
        self,
        text: str,
        icon_name: str,
        *,
        role: str = "muted",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self._icon_name = icon_name
        self._role = role
        self.setIconSize(QSize(16, 16))
        theme_manager.changed.connect(self._refresh)
        self._refresh()

    def _refresh(self, *_args) -> None:
        theme = current_theme()
        token = _ROLE_TO_TOKEN.get(self._role, "text_muted")
        color = theme.disabled_text if not self.isEnabled() else getattr(
            theme, token)
        self.setIcon(icon(self._icon_name, color))

    def changeEvent(self, event) -> None:  # noqa: N802 - Qt API name
        super().changeEvent(event)
        if event.type() == QEvent.Type.EnabledChange:
            self._refresh()


class BrandMarkLabel(QLabel):
    """Compact LogSentinel mark; updates with the active theme."""

    def __init__(
        self,
        size: int = 44,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._size = size
        self.setObjectName("BrandMarkImage")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        theme_manager.changed.connect(self._refresh)
        self._refresh()

    def _refresh(self, *_args) -> None:
        self.setPixmap(brand_mark_pixmap(current_theme(), self._size))


class BrandWordmarkLabel(QLabel):
    """Theme-aware wordmark image sourced from the bundled SVG asset."""

    def __init__(
        self,
        width: int = 260,
        height: int = 52,
        *,
        sidebar: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._width = width
        self._height = height
        self._sidebar = sidebar
        self.setObjectName("BrandWordmarkImage")
        self.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setFixedSize(width, height)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        theme_manager.changed.connect(self._refresh)
        self._refresh()

    def _refresh(self, *_args) -> None:
        self.setPixmap(brand_pixmap(
            current_theme(), self._width, self._height,
            sidebar=self._sidebar))
