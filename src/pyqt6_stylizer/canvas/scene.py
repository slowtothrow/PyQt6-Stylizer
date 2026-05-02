from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import QEvent, QPointF, QRectF, QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush, QPen
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDial,
    QFontComboBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsItem,
    QGraphicsOpacityEffect,
    QGraphicsProxyWidget,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsTextItem,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QScrollBar,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QToolBox,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..document import StudioDocument, StudioNode


ITEM_LABEL_ROLE = 0
ITEM_NODE_ID_ROLE = 1
MOVE_HANDLE_WIDTH = 68.0
MOVE_HANDLE_HEIGHT = 24.0
MOVE_HANDLE_MARGIN = 10.0
RESIZE_HANDLE_SIZE = 14.0
RESIZE_HANDLE_MARGIN = 8.0
SCENE_CARD_MIN_SIZE = (240.0, 140.0)
DEFAULT_WIDGET_PREVIEW_MIN_SIZE = (420, 320)
WIDGET_PREVIEW_MIN_SIZES: dict[str, tuple[int, int]] = {
    "simple-controls": (420, 340),
    "choice-matrix": (420, 380),
    "slider-lab": (420, 360),
    "font-color-lab": (430, 360),
    "flyout-lab": (500, 340),
    "dialog-lab": (480, 340),
    "scroll-gallery": (430, 440),
    "navigation-workspace": (600, 440),
    "inspector-tree": (600, 440),
    "data-table-console": (600, 440),
    "effects-lab": (430, 360),
    "workspace-shell": (1040, 680),
}


class _ResizeHandleItem(QGraphicsRectItem):
    def __init__(
        self,
        read_size: Callable[[], tuple[float, float]],
        apply_size: Callable[[float, float], None],
        parent: QGraphicsItem,
    ) -> None:
        super().__init__(0.0, 0.0, RESIZE_HANDLE_SIZE, RESIZE_HANDLE_SIZE, parent)
        self._read_size = read_size
        self._apply_size = apply_size
        self._base_size = (0.0, 0.0)
        self._start_scene_pos: QPointF | None = None
        self.setBrush(QBrush(QColor("#223647")))
        self.setPen(QPen(QColor("#fffdf8"), 1.0))
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.setToolTip("Drag this corner to resize the selected example.")
        self.setZValue(3.0)

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        self._start_scene_pos = event.scenePos()
        self._base_size = self._read_size()
        event.accept()

    def mouseMoveEvent(self, event):  # type: ignore[override]
        if self._start_scene_pos is None:
            super().mouseMoveEvent(event)
            return

        delta = event.scenePos() - self._start_scene_pos
        self._apply_size(self._base_size[0] + delta.x(), self._base_size[1] + delta.y())
        event.accept()

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        self._start_scene_pos = None
        event.accept()


class _MoveHandleItem(QGraphicsRectItem):
    def __init__(self, read_size: Callable[[], tuple[float, float]], parent: QGraphicsItem) -> None:
        super().__init__(0.0, 0.0, MOVE_HANDLE_WIDTH, MOVE_HANDLE_HEIGHT, parent)
        self._read_size = read_size
        self._start_scene_pos: QPointF | None = None
        self._start_parent_pos = QPointF()
        self.setBrush(QBrush(QColor("#223647")))
        self.setPen(QPen(QColor("#fffdf8"), 1.0))
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setToolTip("Drag this grip to move the example on the canvas.")
        self.setZValue(3.0)

        label = QGraphicsSimpleTextItem("Move", self)
        label.setBrush(QBrush(QColor("#fffdf8")))
        label.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        label_rect = label.boundingRect()
        label.setPos(
            (MOVE_HANDLE_WIDTH - label_rect.width()) / 2.0,
            (MOVE_HANDLE_HEIGHT - label_rect.height()) / 2.0,
        )

    def reposition(self) -> None:
        width, _height = self._read_size()
        self.setPos(max(width - MOVE_HANDLE_WIDTH - MOVE_HANDLE_MARGIN, 0.0), MOVE_HANDLE_MARGIN)

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        parent = self.parentItem()
        if parent is None:
            event.ignore()
            return

        scene = parent.scene()
        if scene is not None and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            scene.clearSelection()
        parent.setSelected(True)
        self._start_scene_pos = event.scenePos()
        self._start_parent_pos = parent.pos()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        event.accept()

    def mouseMoveEvent(self, event):  # type: ignore[override]
        if self._start_scene_pos is None:
            super().mouseMoveEvent(event)
            return

        parent = self.parentItem()
        if parent is None:
            event.ignore()
            return

        delta = event.scenePos() - self._start_scene_pos
        parent.setPos(self._start_parent_pos + delta)
        event.accept()

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        self._start_scene_pos = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        event.accept()


class _NodeRectItem(QGraphicsRectItem):
    def __init__(
        self,
        node_id: str,
        on_position_changed: Callable[[str, QPointF], None],
        on_size_changed: Callable[[str, float, float], None],
    ) -> None:
        super().__init__()
        self._node_id = node_id
        self._on_position_changed = on_position_changed
        self._on_size_changed = on_size_changed
        self._resize_handle = _ResizeHandleItem(self._runtime_size, self.apply_runtime_size, self)
        self._resize_handle.hide()

    def set_node_rect(self, width: float, height: float) -> None:
        self.setRect(0.0, 0.0, width, height)
        self._position_resize_handle()

    def apply_runtime_size(self, width: float, height: float, *, notify: bool = True) -> None:
        clamped_width = max(width, SCENE_CARD_MIN_SIZE[0])
        clamped_height = max(height, SCENE_CARD_MIN_SIZE[1])
        self.set_node_rect(clamped_width, clamped_height)
        if notify:
            self._on_size_changed(self._node_id, clamped_width, clamped_height)

    def _runtime_size(self) -> tuple[float, float]:
        rect = self.rect()
        return rect.width(), rect.height()

    def _position_resize_handle(self) -> None:
        width, height = self._runtime_size()
        self._resize_handle.setPos(
            max(width - RESIZE_HANDLE_SIZE - RESIZE_HANDLE_MARGIN, 0.0),
            max(height - RESIZE_HANDLE_SIZE - RESIZE_HANDLE_MARGIN, 0.0),
        )

    def itemChange(self, change, value):  # type: ignore[override]
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            position = value if isinstance(value, QPointF) else self.pos()
            self._on_position_changed(self._node_id, position)
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self._resize_handle.setVisible(bool(value))
        return super().itemChange(change, value)


class _NodeProxyWidget(QGraphicsProxyWidget):
    def __init__(
        self,
        node_id: str,
        on_position_changed: Callable[[str, QPointF], None],
        on_size_changed: Callable[[str, float, float], None],
        minimum_size: tuple[int, int],
    ) -> None:
        super().__init__()
        self._node_id = node_id
        self._on_position_changed = on_position_changed
        self._on_size_changed = on_size_changed
        self._minimum_size = minimum_size
        self._move_handle = _MoveHandleItem(self._runtime_size, self)
        self._resize_handle = _ResizeHandleItem(self._runtime_size, self.apply_runtime_size, self)
        self._resize_handle.hide()

    def attach_widget(self, widget: QWidget) -> None:
        self.setWidget(widget)
        self._install_selection_filters(widget)

    def apply_runtime_size(self, width: float, height: float, *, notify: bool = True) -> None:
        clamped_width = max(width, float(self._minimum_size[0]))
        clamped_height = max(height, float(self._minimum_size[1]))
        self.prepareGeometryChange()
        widget = self.widget()
        if widget is not None:
            widget.setFixedSize(int(round(clamped_width)), int(round(clamped_height)))
            widget.updateGeometry()
        self.resize(clamped_width, clamped_height)
        self.updateGeometry()
        self.update()
        self._position_resize_handle()
        if notify:
            self._on_size_changed(self._node_id, clamped_width, clamped_height)

    def _runtime_size(self) -> tuple[float, float]:
        widget = self.widget()
        if widget is not None:
            return float(widget.width()), float(widget.height())
        rect = self.boundingRect()
        return rect.width(), rect.height()

    def _position_resize_handle(self) -> None:
        width, height = self._runtime_size()
        self._resize_handle.setPos(
            max(width - RESIZE_HANDLE_SIZE - RESIZE_HANDLE_MARGIN, 0.0),
            max(height - RESIZE_HANDLE_SIZE - RESIZE_HANDLE_MARGIN, 0.0),
        )
        self._move_handle.reposition()

    def _install_selection_filters(self, widget: QWidget) -> None:
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.installEventFilter(self)

    # Ensure embedded widgets forward selection events to the proxy item.
    # Without this, child buttons and controls can swallow mouse clicks and prevent
    # the owning canvas node from being selected or dragged.
    def eventFilter(self, watched, event):  # type: ignore[override]
        if event.type() in {QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonDblClick}:
            if event.button() == Qt.MouseButton.LeftButton:
                scene = self.scene()
                if scene is not None and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                    scene.clearSelection()
                self.setSelected(True)
        return super().eventFilter(watched, event)

    def boundingRect(self) -> QRectF:  # type: ignore[override]
        width, height = self._runtime_size()
        return QRectF(0.0, 0.0, width, height)

    def itemChange(self, change, value):  # type: ignore[override]
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            position = value if isinstance(value, QPointF) else self.pos()
            self._on_position_changed(self._node_id, position)
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self._resize_handle.setVisible(bool(value))
        return super().itemChange(change, value)


class StudioScene(QGraphicsScene):
    GRID_SPACING = 24.0
    node_moved = pyqtSignal(str, float, float)
    node_resized = pyqtSignal(str, float, float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSceneRect(0.0, 0.0, 1400.0, 900.0)
        self._node_items: dict[str, QGraphicsItem] = {}

    def drawBackground(self, painter, rect: QRectF) -> None:  # type: ignore[override]
        super().drawBackground(painter, rect)

        background = QColor("#f1eee7")
        major_line = QColor("#d4cdc0")
        minor_line = QColor("#e4ddd0")

        painter.fillRect(rect, background)

        left = int(rect.left()) - (int(rect.left()) % int(self.GRID_SPACING))
        top = int(rect.top()) - (int(rect.top()) % int(self.GRID_SPACING))

        for x in range(left, int(rect.right()) + int(self.GRID_SPACING), int(self.GRID_SPACING)):
            painter.setPen(QPen(major_line if x % int(self.GRID_SPACING * 4) == 0 else minor_line, 1))
            painter.drawLine(QPointF(float(x), rect.top()), QPointF(float(x), rect.bottom()))

        for y in range(top, int(rect.bottom()) + int(self.GRID_SPACING), int(self.GRID_SPACING)):
            painter.setPen(QPen(major_line if y % int(self.GRID_SPACING * 4) == 0 else minor_line, 1))
            painter.drawLine(QPointF(rect.left(), float(y)), QPointF(rect.right(), float(y)))

    def render_document(self, document: StudioDocument) -> None:
        self.clear()
        self._node_items.clear()
        for node in document.nodes:
            self._add_node(node)
        bounds = self.itemsBoundingRect()
        if bounds.isNull():
            self.setSceneRect(0.0, 0.0, 1400.0, 900.0)
        else:
            self.setSceneRect(bounds.adjusted(-120.0, -120.0, 160.0, 160.0))

    def populate_demo_scene(self) -> None:
        self.render_document(StudioDocument.example())

    def rendered_node_ids(self) -> set[str]:
        return set(self._node_items)

    def item_for_node(self, node_id: str) -> QGraphicsItem | None:
        return self._node_items.get(node_id)

    def resize_node(self, node_id: str, width: float, height: float) -> bool:
        item = self._node_items.get(node_id)
        resize = getattr(item, "apply_runtime_size", None)
        if not callable(resize):
            return False
        resize(width, height)
        return True

    def selected_node_ids(self) -> list[str]:
        node_ids: list[str] = []
        for item in self.selectedItems():
            node_id = item.data(ITEM_NODE_ID_ROLE)
            if isinstance(node_id, str):
                node_ids.append(node_id)
        return node_ids

    def select_node(self, node_id: str | None) -> None:
        self.clearSelection()
        if node_id is None:
            return

        item = self._node_items.get(node_id)
        if item is not None:
            item.setSelected(True)

    def selection_summary(self) -> str:
        labels = [
            item.data(ITEM_LABEL_ROLE)
            for item in self.selectedItems()
            if isinstance(item.data(ITEM_LABEL_ROLE), str)
        ]
        if not labels:
            return "Canvas selection will appear here."
        if len(labels) == 1:
            return str(labels[0])
        return ", ".join(str(label) for label in labels)

    def _apply_interaction_flags(self, item: QGraphicsItem, node: StudioNode) -> None:
        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        item.setData(ITEM_LABEL_ROLE, node.label)
        item.setData(ITEM_NODE_ID_ROLE, node.node_id)
        item.setToolTip(
            f"{node.label}\nDrag to reposition. Select it and drag the lower-right corner to resize. Click to inspect properties and the live block preview."
        )
        self._node_items[node.node_id] = item

    def _emit_node_moved(self, node_id: str, position: QPointF) -> None:
        self._refresh_scene_rect_from_items()
        self.node_moved.emit(node_id, position.x(), position.y())

    def _emit_node_resized(self, node_id: str, width: float, height: float) -> None:
        self._refresh_scene_rect_from_items()
        self.node_resized.emit(node_id, width, height)

    def _refresh_scene_rect_from_items(self) -> None:
        bounds = self.itemsBoundingRect()
        if bounds.isNull():
            return
        self.setSceneRect(bounds.adjusted(-120.0, -120.0, 160.0, 160.0))

    def _add_node(self, node: StudioNode) -> None:
        if node.node_type == "scene-card":
            self._add_scene_card(node)
        elif node.node_type == "widget-preview":
            self._add_widget_card(node)

        for child in node.children:
            self._add_node(child)

    def _add_scene_card(self, node: StudioNode) -> None:
        width = float(node.properties.get("width", 260.0))
        height = float(node.properties.get("height", 180.0))
        x = float(node.properties.get("x", 60.0))
        y = float(node.properties.get("y", 60.0))
        fill = str(node.properties.get("fill", "#f8f3e6"))

        card = _NodeRectItem(node.node_id, self._emit_node_moved, self._emit_node_resized)
        card.set_node_rect(width, height)
        card.setPos(x, y)
        card.setBrush(QBrush(QColor(fill)))
        card.setPen(QPen(QColor("#9eb4cc"), 1.4))
        self._apply_interaction_flags(card, node)
        self.addItem(card)

        title = QGraphicsTextItem(node.label, card)
        title.setDefaultTextColor(QColor("#162332"))
        title.setPos(16.0, 14.0)
        title.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

        body = QGraphicsTextItem(
            str(
                node.properties.get(
                    "description",
                    "Freeform scene items live beside embedded widgets so style exploration can stay loose.",
                )
            ),
            card,
        )
        body.setTextWidth(max(width - 40.0, 120.0))
        body.setDefaultTextColor(QColor("#526273"))
        body.setPos(16.0, 52.0)
        body.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

        required_height = max(height, body.pos().y() + body.boundingRect().height() + 22.0)
        if required_height > height:
            card.set_node_rect(width, required_height)
            node.properties["height"] = required_height

    def _add_widget_card(self, node: StudioNode) -> None:
        width = int(float(node.properties.get("width", DEFAULT_WIDGET_PREVIEW_MIN_SIZE[0])))
        height = int(float(node.properties.get("height", DEFAULT_WIDGET_PREVIEW_MIN_SIZE[1])))
        container = QFrame()
        container.setObjectName("widgetCard")
        container.setStyleSheet(
            """
            QFrame#widgetCard {
                background: #ffffff;
                border: 1px solid #cfdceb;
                border-radius: 20px;
            }
            QWidget#demoWell, QFrame#demoWell {
                background: #f5f8fc;
                border: 1px solid #dbe5f0;
                border-radius: 16px;
            }
            QLabel[role='eyebrow'] {
                color: #5d7086;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.10em;
            }
            QLabel[role='headline'] {
                color: #162332;
                font-size: 20px;
                font-weight: 700;
            }
            QLabel[role='caption'] {
                color: #607284;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.04em;
            }
            QPushButton {
                background: #2f80ed;
                border: none;
                border-radius: 11px;
                color: #f8fbff;
                padding: 10px 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #1f6ad1;
            }
            QToolButton {
                background: #1b2b3f;
                border: none;
                border-radius: 10px;
                color: #f8fbff;
                padding: 8px 12px;
                font-weight: 600;
            }
            QToolButton:hover {
                background: #29435f;
            }
            QLineEdit, QComboBox, QSpinBox, QPlainTextEdit, QListWidget, QTreeWidget, QTableWidget, QTabWidget::pane, QToolBox {
                background: #ffffff;
                border: 1px solid #d7e1ec;
                border-radius: 10px;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 6px 8px;
                min-height: 32px;
            }
            QPlainTextEdit, QListWidget, QTreeWidget, QTableWidget {
                border-radius: 12px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QGroupBox {
                border: 1px solid #d7e1ec;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 12px;
                font-weight: 700;
                color: #203246;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
            }
            QHeaderView::section {
                background: #eef4fb;
                color: #203246;
                border: none;
                border-right: 1px solid #d7e1ec;
                border-bottom: 1px solid #d7e1ec;
                padding: 6px 8px;
                font-weight: 700;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        eyebrow = QLabel(str(node.properties.get("kind", "widget-preview")).replace("-", " ").upper())
        eyebrow.setProperty("role", "eyebrow")

        headline = QLabel(node.label)
        headline.setProperty("role", "headline")

        body = QLabel(
            str(
                node.properties.get(
                    "description",
                    "This preview is rendered through QGraphicsProxyWidget so styling experiments can mix widgets and graphics items on one canvas.",
                )
            )
        )
        body.setWordWrap(True)
        body.setStyleSheet("color: #41505d;")

        demo = self._build_widget_demo(node, container)
        demo.setObjectName("demoWell")

        footer = QLabel("Duplicate this example or edit its block JSON to remix the interaction.")
        footer.setWordWrap(True)
        footer.setProperty("role", "caption")

        layout.addWidget(eyebrow)
        layout.addWidget(headline)
        layout.addWidget(body)
        layout.addWidget(demo, stretch=1)
        layout.addWidget(footer)

        width, height = self._resolve_widget_card_size(node, container, width, height)
        container.setFixedSize(width, height)
        minimum_size = WIDGET_PREVIEW_MIN_SIZES.get(
            str(node.properties.get("kind", "widget-preview")),
            DEFAULT_WIDGET_PREVIEW_MIN_SIZE,
        )

        proxy = _NodeProxyWidget(node.node_id, self._emit_node_moved, self._emit_node_resized, minimum_size)
        proxy.attach_widget(container)
        proxy.apply_runtime_size(width, height, notify=False)
        proxy.setPos(float(node.properties.get("x", 380.0)), float(node.properties.get("y", 120.0)))
        self._apply_interaction_flags(proxy, node)
        self.addItem(proxy)

    def _resolve_widget_card_size(
        self,
        node: StudioNode,
        container: QWidget,
        requested_width: int,
        requested_height: int,
    ) -> tuple[int, int]:
        kind = str(node.properties.get("kind", "widget-preview"))
        minimum_width, minimum_height = WIDGET_PREVIEW_MIN_SIZES.get(kind, DEFAULT_WIDGET_PREVIEW_MIN_SIZE)

        layout = container.layout()
        if layout is not None:
            layout.activate()

        container.ensurePolished()
        hinted = container.sizeHint().expandedTo(container.minimumSizeHint())
        width = max(requested_width, minimum_width, hinted.width())
        height = max(requested_height, minimum_height, hinted.height())
        node.properties["width"] = float(width)
        node.properties["height"] = float(height)
        return width, height

    def _build_widget_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        kind = str(node.properties.get("kind", "simple-controls"))
        builders: dict[str, Callable[[StudioNode, QWidget], QWidget]] = {
            "simple-controls": self._build_simple_controls_demo,
            "button-card": self._build_simple_controls_demo,
            "copy-tester": self._build_simple_controls_demo,
            "theme-switcher": self._build_simple_controls_demo,
            "palette-probe": self._build_simple_controls_demo,
            "icon-surface": self._build_simple_controls_demo,
            "search-inputs": self._build_simple_controls_demo,
            "auth-shell": self._build_simple_controls_demo,
            "choice-matrix": self._build_choice_matrix_demo,
            "slider-lab": self._build_slider_lab_demo,
            "range-slider-lab": self._build_slider_lab_demo,
            "timeline-review": self._build_slider_lab_demo,
            "font-color-lab": self._build_font_color_demo,
            "colormap-bench": self._build_font_color_demo,
            "flyout-lab": self._build_flyout_demo,
            "command-palette-lab": self._build_flyout_demo,
            "dialog-lab": self._build_dialog_demo,
            "multi-dialog-flow": self._build_dialog_demo,
            "scroll-gallery": self._build_scroll_gallery_demo,
            "card-gallery": self._build_scroll_gallery_demo,
            "navigation-workspace": self._build_navigation_workspace_demo,
            "navigation-rail": self._build_navigation_workspace_demo,
            "search-strip": self._build_navigation_workspace_demo,
            "settings-stack": self._build_navigation_workspace_demo,
            "left-rail": self._build_navigation_workspace_demo,
            "content-stack": self._build_navigation_workspace_demo,
            "settings-drawer": self._build_navigation_workspace_demo,
            "frameless-shell": self._build_navigation_workspace_demo,
            "inspector-tree": self._build_inspector_tree_demo,
            "parameter-tree": self._build_inspector_tree_demo,
            "dense-inspector": self._build_inspector_tree_demo,
            "data-table-console": self._build_data_table_demo,
            "plot-pane": self._build_data_table_demo,
            "interaction-matrix": self._build_data_table_demo,
            "ops-console": self._build_data_table_demo,
            "effects-lab": self._build_effects_demo,
            "effects-studio": self._build_effects_demo,
            "workspace-shell": self._build_workspace_shell_demo,
            "creator-shell": self._build_workspace_shell_demo,
            "chat-ops-shell": self._build_workspace_shell_demo,
        }
        builder = builders.get(kind, self._build_generic_widget_demo)
        return builder(node, host)

    def _make_status_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setStyleSheet("color: #5b6d7d; font-size: 11px; font-weight: 600;")
        return label

    def _build_generic_widget_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        entry = QLineEdit(widget)
        entry.setPlaceholderText("Type a label or state name")
        status = self._make_status_label("Generic preview ready")
        button = QPushButton(str(node.properties.get("cta_label", "Trigger Dummy State")), widget)
        button.clicked.connect(lambda: status.setText(f"Triggered: {entry.text() or node.label}"))

        layout.addWidget(entry)
        layout.addWidget(button)
        layout.addWidget(status)
        layout.addStretch(1)
        return widget

    def _build_simple_controls_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        hero = QFrame(widget)
        hero.setStyleSheet("background: #f4ecdf; border-radius: 14px; padding: 12px;")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(12, 12, 12, 12)
        title = QLabel("Simple, elegant control cluster", hero)
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1f2d3a;")
        subtitle = QLabel("One headline, one action, one visible accent choice.", hero)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #5a6875;")
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)

        controls = QHBoxLayout()
        accent = QComboBox(widget)
        accents = {
            "Sand": "#f4ecdf",
            "Ocean": "#d8e4f2",
            "Mint": "#dff2e8",
        }
        accent.addItems(list(accents))
        emphasize = QCheckBox("Emphasize", widget)
        button = QPushButton(str(node.properties.get("cta_label", "Apply")), widget)
        status = self._make_status_label("Use this as the simplest baseline pattern.")

        def refresh() -> None:
            border = "#1c3347" if emphasize.isChecked() else "#cabfae"
            hero.setStyleSheet(
                f"background: {accents[accent.currentText()]}; border: 2px solid {border}; border-radius: 14px;"
            )
            status.setText(
                f"Accent: {accent.currentText()} | emphasis: {'on' if emphasize.isChecked() else 'off'}"
            )

        accent.currentTextChanged.connect(lambda _text: refresh())
        emphasize.toggled.connect(lambda _checked: refresh())
        button.clicked.connect(lambda: status.setText(f"Primary action fired with {accent.currentText()} accent"))
        controls.addWidget(accent)
        controls.addWidget(emphasize)
        controls.addStretch(1)

        layout.addWidget(hero)
        layout.addLayout(controls)
        layout.addWidget(button)
        layout.addWidget(status)
        layout.addStretch(1)
        refresh()
        return widget

    def _build_choice_matrix_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        radio_group = QGroupBox("Priority")
        radio_layout = QVBoxLayout(radio_group)
        radios = [QRadioButton(text, radio_group) for text in ("Quiet", "Balanced", "Loud")]
        radios[1].setChecked(True)
        button_group = QButtonGroup(radio_group)
        for radio in radios:
            button_group.addButton(radio)
            radio_layout.addWidget(radio)

        toggles_group = QGroupBox("Features")
        toggles_layout = QVBoxLayout(toggles_group)
        toggles = [QCheckBox(text, toggles_group) for text in ("Tooltips", "Inline help", "Auto-save")]
        toggles[0].setChecked(True)
        toggles[1].setChecked(True)
        for toggle in toggles:
            toggles_layout.addWidget(toggle)

        status = self._make_status_label("Choice-heavy control groups stay inspectable here.")

        def update_status() -> None:
            selected_radio = next((radio.text() for radio in radios if radio.isChecked()), "None")
            enabled = [toggle.text() for toggle in toggles if toggle.isChecked()]
            status.setText(f"Priority: {selected_radio} | features: {', '.join(enabled) or 'none'}")

        for radio in radios:
            radio.toggled.connect(lambda _checked: update_status())
        for toggle in toggles:
            toggle.toggled.connect(lambda _checked: update_status())

        layout.addWidget(radio_group)
        layout.addWidget(toggles_group)
        layout.addWidget(status)
        layout.addStretch(1)
        update_status()
        return widget

    def _build_slider_lab_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        value_label = QLabel("Intensity: 42")
        value_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #243645;")
        slider = QSlider(Qt.Orientation.Horizontal, widget)
        dial = QDial(widget)
        dial.setNotchesVisible(True)
        scrollbar = QScrollBar(Qt.Orientation.Horizontal, widget)
        progress = QProgressBar(widget)
        for control in (slider, dial, scrollbar, progress):
            control.setRange(0, 100)
            control.setValue(42)

        def sync(value: int) -> None:
            for control in (slider, dial, scrollbar):
                if control.value() != value:
                    blocker = QSignalBlocker(control)
                    control.setValue(value)
                    del blocker
            progress.setValue(value)
            value_label.setText(f"Intensity: {value}")

        slider.valueChanged.connect(sync)
        dial.valueChanged.connect(sync)
        scrollbar.valueChanged.connect(sync)

        layout.addWidget(value_label)
        layout.addWidget(slider)
        layout.addWidget(dial, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(scrollbar)
        layout.addWidget(progress)
        layout.addStretch(1)
        return widget

    def _build_font_color_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        controls = QGridLayout()
        font_picker = QFontComboBox(widget)
        size_picker = QSpinBox(widget)
        size_picker.setRange(10, 32)
        size_picker.setValue(18)
        foreground = QComboBox(widget)
        foreground.addItems(["Ink", "Ocean", "Rose", "Forest"])
        background = QComboBox(widget)
        background.addItems(["Canvas", "Fog", "Sand", "Slate"])

        controls.addWidget(QLabel("Font"), 0, 0)
        controls.addWidget(font_picker, 0, 1)
        controls.addWidget(QLabel("Size"), 1, 0)
        controls.addWidget(size_picker, 1, 1)
        controls.addWidget(QLabel("Text"), 2, 0)
        controls.addWidget(foreground, 2, 1)
        controls.addWidget(QLabel("Surface"), 3, 0)
        controls.addWidget(background, 3, 1)

        sample = QLabel("Typography, color, and hierarchy should all be visible on the same canvas.")
        sample.setWordWrap(True)
        sample.setMinimumHeight(84)
        sample.setStyleSheet("padding: 14px; border-radius: 12px;")
        status = self._make_status_label("Try fonts, sizing, and text tones without leaving the canvas.")

        text_colors = {
            "Ink": "#1d2b36",
            "Ocean": "#20496f",
            "Rose": "#7a375f",
            "Forest": "#2f5a49",
        }
        surface_colors = {
            "Canvas": "#fffdf8",
            "Fog": "#eef1f5",
            "Sand": "#f4ecdf",
            "Slate": "#d9e2ec",
        }

        def refresh() -> None:
            font = font_picker.currentFont()
            font.setPointSize(size_picker.value())
            sample.setFont(font)
            sample.setStyleSheet(
                f"padding: 14px; border-radius: 12px; color: {text_colors[foreground.currentText()]};"
                f"background: {surface_colors[background.currentText()]};"
            )
            status.setText(
                f"Font: {font.family()} | size: {size_picker.value()} | tone: {foreground.currentText()}"
            )

        font_picker.currentFontChanged.connect(lambda _font: refresh())
        size_picker.valueChanged.connect(lambda _value: refresh())
        foreground.currentTextChanged.connect(lambda _value: refresh())
        background.currentTextChanged.connect(lambda _value: refresh())

        layout.addLayout(controls)
        layout.addWidget(sample)
        layout.addWidget(status)
        layout.addStretch(1)
        refresh()
        return widget

    def _build_flyout_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        status = self._make_status_label("Click the flyout or split button to inspect menus and submenus.")
        row = QHBoxLayout()

        flyout_button = QToolButton(widget)
        flyout_button.setText("Open Flyout")
        flyout_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        flyout_menu = QMenu(flyout_button)
        for label in ("New Draft", "Duplicate Selection", "Send Preview"):
            action = flyout_menu.addAction(label)
            action.triggered.connect(lambda _checked=False, text=label: status.setText(f"Flyout action: {text}"))
        placement_menu = flyout_menu.addMenu("Placement")
        for label in ("Top Left", "Center", "Bottom Right"):
            action = placement_menu.addAction(label)
            action.triggered.connect(lambda _checked=False, text=label: status.setText(f"Placement chosen: {text}"))
        flyout_button.setMenu(flyout_menu)

        split_button = QToolButton(widget)
        split_button.setText("Apply Quick Style")
        split_button.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        split_menu = QMenu(split_button)
        for label in ("Minimal", "Editorial", "Dense Admin"):
            action = split_menu.addAction(label)
            action.triggered.connect(lambda _checked=False, text=label: status.setText(f"Quick style: {text}"))
        split_button.clicked.connect(lambda: status.setText("Quick style applied"))
        split_button.setMenu(split_menu)

        combo = QComboBox(widget)
        combo.addItems(["Context menu", "Toolbar flyout", "Inline action rail"])
        combo.currentTextChanged.connect(lambda text: status.setText(f"Popup pattern: {text}"))

        row.addWidget(flyout_button)
        row.addWidget(split_button)
        row.addWidget(combo)

        layout.addLayout(row)
        layout.addWidget(status)
        layout.addStretch(1)
        return widget

    def _build_dialog_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        instructions = QLabel("Launch a semi-functional dialog with tabs, form controls, and accept/cancel flow.")
        instructions.setWordWrap(True)
        status = self._make_status_label("No dialog opened yet.")
        opener = QPushButton(str(node.properties.get("cta_label", "Open Dialog")), widget)
        dialogs: list[QDialog] = []

        def open_dialog() -> None:
            dialog = QDialog(host)
            dialog.setWindowTitle("Interaction Review Dialog")
            dialog.resize(420, 320)
            dialog_layout = QVBoxLayout(dialog)

            tabs = QTabWidget(dialog)
            general = QWidget(dialog)
            general_form = QFormLayout(general)
            general_form.addRow("Title", QLineEdit("Canvas Review"))
            density = QComboBox(general)
            density.addItems(["Airy", "Balanced", "Dense"])
            general_form.addRow("Density", density)
            tabs.addTab(general, "General")

            notes = QWidget(dialog)
            notes_layout = QVBoxLayout(notes)
            editor = QPlainTextEdit(notes)
            editor.setPlainText("Use this dialog to test stack depth, spacing, and confirmation language.")
            notes_layout.addWidget(editor)
            tabs.addTab(notes, "Notes")

            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
                parent=dialog,
            )
            buttons.accepted.connect(lambda: (status.setText("Dialog accepted"), dialog.accept()))
            buttons.rejected.connect(lambda: (status.setText("Dialog cancelled"), dialog.reject()))

            dialog_layout.addWidget(tabs)
            dialog_layout.addWidget(buttons)
            dialogs.append(dialog)
            dialog.finished.connect(lambda _code, dlg=dialog: dialogs.remove(dlg) if dlg in dialogs else None)
            dialog.show()
            status.setText("Dialog opened")

        opener.clicked.connect(open_dialog)

        layout.addWidget(instructions)
        layout.addWidget(opener)
        layout.addWidget(status)
        layout.addStretch(1)
        return widget

    def _build_scroll_gallery_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        scroll = QScrollArea(widget)
        scroll.setWidgetResizable(True)
        inner = QWidget(scroll)
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(8)
        status = self._make_status_label("Scroll through mini panels and tap any action to update state.")

        for title, caption in (
            ("Toast Stack", "Short-lived notices with strong contrast and clear hierarchy."),
            ("Mini Inspector", "A tight properties form for quick in-place adjustments."),
            ("Recent Files", "A scrollable list with mixed metadata and secondary actions."),
            ("Command Shelf", "Small action clusters that should still feel clickable."),
            ("Help Snippets", "Compact hints and examples that travel with the workspace."),
        ):
            panel = QFrame(inner)
            panel.setStyleSheet("background: #fffef8; border: 1px solid #d4cab8; border-radius: 12px;")
            panel_layout = QVBoxLayout(panel)
            title_label = QLabel(title, panel)
            title_label.setStyleSheet("font-weight: 700; color: #243645;")
            copy = QLabel(caption, panel)
            copy.setWordWrap(True)
            action = QPushButton("Inspect", panel)
            action.clicked.connect(lambda _checked=False, text=title: status.setText(f"Scrolled action: {text}"))
            panel_layout.addWidget(title_label)
            panel_layout.addWidget(copy)
            panel_layout.addWidget(action)
            inner_layout.addWidget(panel)
        inner_layout.addStretch(1)
        scroll.setWidget(inner)

        layout.addWidget(scroll, stretch=1)
        layout.addWidget(status)
        return widget

    def _build_navigation_workspace_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal, widget)
        nav = QListWidget(splitter)
        nav.addItems(["Overview", "Workflows", "Settings", "Audit Trail"])
        nav.setCurrentRow(0)

        stack = QStackedWidget(splitter)
        for title in ("Overview", "Workflows", "Settings", "Audit Trail"):
            page = QWidget(stack)
            page_layout = QVBoxLayout(page)
            page_layout.addWidget(QLabel(f"{title} Page", page))
            if title == "Settings":
                tabs = QTabWidget(page)
                for tab_name in ("General", "Shortcuts", "Notifications"):
                    tab = QWidget(tabs)
                    tab_layout = QVBoxLayout(tab)
                    tab_layout.addWidget(QLabel(f"Nested {tab_name} content", tab))
                    tab_layout.addWidget(QCheckBox(f"Enable {tab_name.lower()} helpers", tab))
                    tabs.addTab(tab, tab_name)
                page_layout.addWidget(tabs)
            else:
                note = QLabel(
                    "This page exists to test stacked navigation, persistent rails, and page-specific control density.",
                    page,
                )
                note.setWordWrap(True)
                page_layout.addWidget(note)
                page_layout.addWidget(QPushButton(f"Activate {title}", page))
            page_layout.addStretch(1)
            stack.addWidget(page)
        splitter.addWidget(nav)
        splitter.addWidget(stack)
        splitter.setSizes([140, 340])

        status = self._make_status_label("Navigation shell ready")

        def activate_page(index: int) -> None:
            if index < 0:
                return
            stack.setCurrentIndex(index)
            item = nav.item(index)
            if item is not None:
                status.setText(f"Active page: {item.text()}")

        nav.currentRowChanged.connect(activate_page)

        layout.addWidget(splitter, stretch=1)
        layout.addWidget(status)
        return widget

    def _build_inspector_tree_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal, widget)
        tree = QTreeWidget(splitter)
        tree.setHeaderLabels(["Node", "Role"])
        root = QTreeWidgetItem(["Workspace", "root"])
        tree.addTopLevelItem(root)
        for group, role in (("Canvas", "surface"), ("Inspector", "property"), ("Exports", "handoff")):
            parent = QTreeWidgetItem([group, role])
            root.addChild(parent)
            parent.addChild(QTreeWidgetItem([f"{group} Detail", "leaf"]))
        tree.expandAll()

        details = QTabWidget(splitter)
        properties_tab = QWidget(details)
        properties_form = QFormLayout(properties_tab)
        name_value = QLabel("Workspace")
        role_value = QLabel("root")
        properties_form.addRow("Name", name_value)
        properties_form.addRow("Role", role_value)
        details.addTab(properties_tab, "Properties")

        notes_tab = QWidget(details)
        notes_layout = QVBoxLayout(notes_tab)
        notes_editor = QPlainTextEdit(notes_tab)
        notes_editor.setPlainText("Tree selections should clarify what each region of the app is responsible for.")
        notes_layout.addWidget(notes_editor)
        details.addTab(notes_tab, "Notes")

        splitter.addWidget(tree)
        splitter.addWidget(details)
        splitter.setSizes([220, 260])
        status = self._make_status_label("Select any tree node to inspect its metadata.")

        def update_details(item: QTreeWidgetItem | None) -> None:
            if item is None:
                return
            name_value.setText(item.text(0))
            role_value.setText(item.text(1))
            status.setText(f"Inspecting: {item.text(0)}")

        tree.currentItemChanged.connect(lambda current, _previous: update_details(current))
        tree.setCurrentItem(root)

        layout.addWidget(splitter, stretch=1)
        layout.addWidget(status)
        return widget

    def _build_data_table_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        actions = QHBoxLayout()
        refresh = QPushButton("Run Query", widget)
        export = QPushButton("Export CSV", widget)
        clear = QPushButton("Clear Log", widget)
        for button in (refresh, export, clear):
            actions.addWidget(button)
        actions.addStretch(1)

        table = QTableWidget(4, 4, widget)
        table.setHorizontalHeaderLabels(["Metric", "State", "Owner", "Delta"])
        rows = [
            ("Latency", "Monitoring", "Canvas", "+12ms"),
            ("Menus", "Ready", "Toolbar", "0"),
            ("Dialogs", "Prototype", "Actions", "+1"),
            ("Exports", "Queued", "Inspector", "2"),
        ]
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                table.setItem(row_index, column_index, QTableWidgetItem(value))

        log = QPlainTextEdit(widget)
        log.setReadOnly(True)
        log.setMaximumHeight(96)
        log.setPlainText("Console ready\n")
        status = self._make_status_label("Dense data views should still stay readable and testable.")

        refresh.clicked.connect(lambda: (log.appendPlainText("Query executed"), status.setText("Ran data refresh")))
        export.clicked.connect(lambda: (log.appendPlainText("CSV export requested"), status.setText("Export action triggered")))
        clear.clicked.connect(lambda: (log.setPlainText("Console cleared\n"), status.setText("Console cleared")))

        layout.addLayout(actions)
        layout.addWidget(table, stretch=1)
        layout.addWidget(log)
        layout.addWidget(status)
        return widget

    def _build_effects_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        preview = QFrame(widget)
        preview.setStyleSheet("background: #f7efe1; border-radius: 14px;")
        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        sample = QLabel("Shadow, opacity, and accent effects are all live here.", preview)
        sample.setWordWrap(True)
        sample.setStyleSheet("font-size: 15px; font-weight: 700; color: #233646;")
        preview_layout.addWidget(sample)

        shadow_effect = QGraphicsDropShadowEffect(preview)
        shadow_effect.setBlurRadius(24)
        shadow_effect.setOffset(0, 8)
        shadow_effect.setColor(QColor("#455a73"))
        preview.setGraphicsEffect(shadow_effect)

        opacity_effect = QGraphicsOpacityEffect(sample)
        opacity_effect.setOpacity(0.95)
        sample.setGraphicsEffect(opacity_effect)

        shadow_toggle = QCheckBox("Shadow", widget)
        shadow_toggle.setChecked(True)
        blur = QSlider(Qt.Orientation.Horizontal, widget)
        blur.setRange(0, 40)
        blur.setValue(24)
        opacity = QSlider(Qt.Orientation.Horizontal, widget)
        opacity.setRange(20, 100)
        opacity.setValue(95)
        accent = QComboBox(widget)
        accent.addItems(["Sand", "Ocean", "Lilac"])
        status = self._make_status_label("Effects help compare subtle polish decisions.")

        accents = {
            "Sand": ("#f7efe1", "#233646"),
            "Ocean": ("#d8e4f2", "#20496f"),
            "Lilac": ("#efe7fb", "#5b4a7a"),
        }

        def refresh() -> None:
            background, text = accents[accent.currentText()]
            preview.setStyleSheet(f"background: {background}; border-radius: 14px;")
            sample.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {text};")
            shadow_effect.setEnabled(shadow_toggle.isChecked())
            shadow_effect.setBlurRadius(blur.value())
            opacity_effect.setOpacity(opacity.value() / 100)
            status.setText(
                f"Accent: {accent.currentText()} | blur: {blur.value()} | opacity: {opacity.value()}%"
            )

        shadow_toggle.toggled.connect(lambda _checked: refresh())
        blur.valueChanged.connect(lambda _value: refresh())
        opacity.valueChanged.connect(lambda _value: refresh())
        accent.currentTextChanged.connect(lambda _value: refresh())

        controls = QGridLayout()
        controls.addWidget(QLabel("Blur"), 0, 0)
        controls.addWidget(blur, 0, 1)
        controls.addWidget(QLabel("Opacity"), 1, 0)
        controls.addWidget(opacity, 1, 1)
        controls.addWidget(QLabel("Accent"), 2, 0)
        controls.addWidget(accent, 2, 1)

        layout.addWidget(preview)
        layout.addWidget(shadow_toggle)
        layout.addLayout(controls)
        layout.addWidget(status)
        layout.addStretch(1)
        refresh()
        return widget

    def _build_workspace_shell_demo(self, node: StudioNode, host: QWidget) -> QWidget:
        widget = QWidget(host)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        tabs = QTabWidget(widget)

        author_tab = QWidget(tabs)
        author_layout = QVBoxLayout(author_tab)
        author_splitter = QSplitter(Qt.Orientation.Horizontal, author_tab)

        project_tree = QTreeWidget(author_splitter)
        project_tree.setHeaderLabels(["Surface", "Type"])
        root = QTreeWidgetItem(["Showcase", "workspace"])
        project_tree.addTopLevelItem(root)
        for branch, branch_type in (("Navigation", "shell"), ("Dialogs", "overlay"), ("Inspector", "tooling")):
            parent = QTreeWidgetItem([branch, branch_type])
            parent.addChild(QTreeWidgetItem([f"{branch} Example", "demo"]))
            root.addChild(parent)
        project_tree.expandAll()

        editor_stack = QTabWidget(author_splitter)
        table_page = QWidget(editor_stack)
        table_layout = QVBoxLayout(table_page)
        table = QTableWidget(3, 3, table_page)
        table.setHorizontalHeaderLabels(["Name", "Variant", "Status"])
        for row_index, row in enumerate(
            (
                ("Flyout", "Toolbar", "Ready"),
                ("Dialog", "Review", "Open"),
                ("Console", "Nested", "Draft"),
            )
        ):
            for column_index, value in enumerate(row):
                table.setItem(row_index, column_index, QTableWidgetItem(value))
        table_layout.addWidget(table)
        editor_stack.addTab(table_page, "Matrix")

        log_page = QWidget(editor_stack)
        log_layout = QVBoxLayout(log_page)
        log = QPlainTextEdit(log_page)
        log.setPlainText("Pipeline booted\nDemo shell attached\nAwaiting user edits")
        log_layout.addWidget(log)
        editor_stack.addTab(log_page, "Console")

        author_splitter.addWidget(project_tree)
        author_splitter.addWidget(editor_stack)
        author_splitter.setSizes([220, 420])
        author_layout.addWidget(author_splitter)
        tabs.addTab(author_tab, "Author")

        monitor_tab = QWidget(tabs)
        monitor_layout = QVBoxLayout(monitor_tab)
        toolbox = QToolBox(monitor_tab)
        for title, lines in (
            ("Notifications", ["3 warnings pending", "1 export queued", "No crashes reported"]),
            ("Batch Jobs", ["Generate screenshots", "Export block JSON", "Snapshot theme tokens"]),
            ("Review Checklist", ["Menus open", "Dialogs close", "Controls describe state"]),
        ):
            page = QWidget(toolbox)
            page_layout = QVBoxLayout(page)
            for line in lines:
                page_layout.addWidget(QLabel(line, page))
            page_layout.addStretch(1)
            toolbox.addItem(page, title)
        monitor_layout.addWidget(toolbox)
        tabs.addTab(monitor_tab, "Monitor")

        status = self._make_status_label("This is the densest nested shell in the showcase.")
        layout.addWidget(tabs, stretch=1)
        layout.addWidget(status)
        return widget
