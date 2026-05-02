from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QMouseEvent, QPainter, QWheelEvent
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QWidget


class StudioView(QGraphicsView):
    ELEMENT_MIME_TYPE = "application/x-pyqt6-stylizer-element"
    element_dropped = pyqtSignal(str, float, float)

    def __init__(self, scene: QGraphicsScene, parent: QWidget | None = None) -> None:
        super().__init__(scene, parent)
        self._zoom_steps = 0
        self._is_panning = False
        self._last_pan_position = None
        self.setAcceptDrops(True)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setToolTip(
            "Drop elements here to place them exactly. After dropping, click the object to edit its live properties and block preview. Scroll the mouse wheel to zoom under the cursor, or middle-mouse drag to pan the canvas."
        )

    def fit_to_scene_contents(self, *, extra_scale: float = 1.0) -> bool:
        scene = self.scene()
        if scene is None:
            return False

        rect = scene.itemsBoundingRect()
        if rect.isNull():
            rect = scene.sceneRect()
        return self.fit_to_rect(rect, extra_scale=extra_scale)

    def frame_selected_items(self, *, extra_scale: float = 1.0) -> bool:
        scene = self.scene()
        if scene is None:
            return False

        selected_items = scene.selectedItems()
        if not selected_items:
            return False

        rect = selected_items[0].sceneBoundingRect()
        for item in selected_items[1:]:
            rect = rect.united(item.sceneBoundingRect())
        return self.fit_to_rect(rect, extra_scale=extra_scale)

    def fit_to_rect(self, rect: QRectF, *, extra_scale: float = 1.0, padding: float = 48.0) -> bool:
        if rect.isNull():
            return False

        padded = rect.adjusted(-padding, -padding, padding, padding)
        self.reset_zoom()
        self.fitInView(padded, Qt.AspectRatioMode.KeepAspectRatio)
        if extra_scale != 1.0:
            self.scale(extra_scale, extra_scale)
        return True

    def reset_zoom(self) -> None:
        self.resetTransform()
        self._zoom_steps = 0

    def zoom_in(self) -> None:
        self._apply_zoom(120)

    def zoom_out(self) -> None:
        self._apply_zoom(-120)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat(self.ELEMENT_MIME_TYPE):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton:
            self._is_panning = True
            self._last_pan_position = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_panning and self._last_pan_position is not None:
            delta = event.position().toPoint() - self._last_pan_position
            self._last_pan_position = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.MiddleButton and self._is_panning:
            self._is_panning = False
            self._last_pan_position = None
            self.unsetCursor()
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            scene = self.scene()
            if scene is not None:
                scene.clearSelection()
            event.accept()
            return

        super().keyPressEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasFormat(self.ELEMENT_MIME_TYPE):
            element_type = bytes(event.mimeData().data(self.ELEMENT_MIME_TYPE)).decode()
            scene_pos = self.mapToScene(event.position().toPoint())
            self.element_dropped.emit(element_type, scene_pos.x(), scene_pos.y())
            event.acceptProposedAction()
            return
        super().dropEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.angleDelta().y() != 0:
            self._apply_zoom(event.angleDelta().y())
            event.accept()
            return

        super().wheelEvent(event)

    def _apply_zoom(self, delta: int) -> None:
        zoom_in = delta > 0
        next_steps = self._zoom_steps + (1 if zoom_in else -1)
        if next_steps < -8 or next_steps > 10:
            return

        self._zoom_steps = next_steps
        factor = 1.15 if zoom_in else 1 / 1.15
        self.scale(factor, factor)
