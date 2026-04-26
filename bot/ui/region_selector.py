from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class RegionSelector(QWidget):
    """Overlay simples para selecionar área da tela com drag-and-drop."""

    region_selected = Signal(QRect)

    def __init__(self) -> None:
        super().__init__()
        self._origin = QPoint()
        self._current = QPoint()
        self._dragging = False
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._origin = event.globalPosition().toPoint()
            self._current = self._origin
            self._dragging = True
            self.update()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._dragging:
            self._current = event.globalPosition().toPoint()
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self._dragging and event.button() == Qt.LeftButton:
            self._current = event.globalPosition().toPoint()
            self._dragging = False
            rect = QRect(self._origin, self._current).normalized()
            self.region_selected.emit(rect)
            self.close()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        if self._origin != self._current:
            rect = QRect(self._origin, self._current).normalized()
            painter.setPen(QPen(QColor(70, 180, 255), 2))
            painter.fillRect(rect, QColor(70, 180, 255, 50))
            painter.drawRect(rect)
