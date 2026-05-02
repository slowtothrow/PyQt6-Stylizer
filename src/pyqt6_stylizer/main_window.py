from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import QMimeData, QSettings, QSignalBlocker, Qt
from PyQt6.QtGui import QAction, QCloseEvent, QFont, QKeySequence
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDockWidget,
    QFileDialog,
    QFrame,
    QGroupBox,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStatusBar,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .canvas import StudioScene, StudioView
from .code_export import CodeExportPanel, generate_code
from .document import StudioDocument, StudioNode, make_stable_id
from .global_options import GlobalOptionsPanel
from .inspector import InspectorPanel
from .registry import ElementRegistry, PresetRegistry
from .styles import MAIN_WINDOW_STYLESHEET


class ElementPaletteList(QListWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setToolTip(
            "Drag an element onto the canvas to place it exactly. Double-click still works as a quick fallback."
        )

    def mimeData(self, items: list[QListWidgetItem]) -> QMimeData:  # type: ignore[override]
        mime_data = QMimeData()
        if items:
            element_type = items[0].data(Qt.ItemDataRole.UserRole)
            if isinstance(element_type, str):
                mime_data.setData(StudioView.ELEMENT_MIME_TYPE, element_type.encode())
        return mime_data

    def supportedDropActions(self) -> Qt.DropAction:  # type: ignore[override]
        return Qt.DropAction.CopyAction


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.element_registry = ElementRegistry.default()
        self.preset_registry = PresetRegistry.default()
        self._current_preset_id = self.preset_registry.default_preset_id
        self.document = self.preset_registry.instantiate(self._current_preset_id) or StudioDocument.example()
        self._settings = QSettings("slowtothrow", "PyQt6Stylizer")
        self._dock_widgets: list[QDockWidget] = []
        self._outliner_items: dict[str, QTreeWidgetItem] = {}
        self._undo_stack: list[str] = []
        self._redo_stack: list[str] = []

        self.setObjectName("mainWindow")
        self.setWindowTitle(f"PyQt6 Stylizer - {self.document.title}")
        self.resize(1440, 920)
        self.setStyleSheet(MAIN_WINDOW_STYLESHEET)
        self.setDockOptions(
            QMainWindow.DockOption.AnimatedDocks
            | QMainWindow.DockOption.AllowNestedDocks
            | QMainWindow.DockOption.AllowTabbedDocks
            | QMainWindow.DockOption.GroupedDragging
        )

        self.scene = StudioScene(self)
        self.scene.render_document(self.document)
        self.scene.selectionChanged.connect(self._handle_scene_selection_change)
        self.scene.node_moved.connect(self._handle_node_moved)
        self.scene.node_resized.connect(self._handle_node_resized)

        self.view = StudioView(self.scene, self)
        self.view.element_dropped.connect(self._handle_canvas_drop)
        self.view.zoom_changed.connect(self._update_zoom_label)
        self.setCentralWidget(self.view)

        self.inspector_panel = InspectorPanel(self)
        self.inspector_panel.property_change_requested.connect(self._handle_property_change)
        self.inspector_panel.property_remove_requested.connect(self._handle_property_remove)
        self.inspector_panel.block_apply_requested.connect(self._handle_block_apply)

        self._create_actions()
        self._create_menus()
        self._create_toolbar()
        self._create_docks()
        self._create_status_bar()
        self._update_reload_action()
        self._restore_window_state()
        self._handle_scene_selection_change()
        self._apply_document_workspace_state()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._settings.setValue("main_window/geometry", self.saveGeometry())
        self._settings.setValue("main_window/state", self.saveState())
        super().closeEvent(event)

    def _create_actions(self) -> None:
        self.reset_layout_action = QAction("Reset Layout", self)
        self.reset_layout_action.triggered.connect(self._reset_layout)

        self.reload_preset_action = QAction("Reload Current Example", self)
        self.reload_preset_action.triggered.connect(self._reload_current_preset)

        self.duplicate_selected_action = QAction("Duplicate Selected", self)
        self.duplicate_selected_action.setShortcut(QKeySequence("Ctrl+D"))
        self.duplicate_selected_action.triggered.connect(self._duplicate_selected_node)

        self.delete_selected_action = QAction("Delete Selected", self)
        self.delete_selected_action.setShortcuts([QKeySequence("Delete"), QKeySequence("Backspace")])
        self.delete_selected_action.triggered.connect(self._delete_selected_nodes)

        self.fit_canvas_action = QAction("Fit Canvas", self)
        self.fit_canvas_action.setShortcut(QKeySequence("F"))
        self.fit_canvas_action.triggered.connect(self._fit_canvas)

        self.frame_selection_action = QAction("Frame Selection", self)
        self.frame_selection_action.setShortcut(QKeySequence("Shift+F"))
        self.frame_selection_action.triggered.connect(self._frame_selection)

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcuts(QKeySequence.keyBindings(QKeySequence.StandardKey.ZoomIn))
        self.zoom_in_action.triggered.connect(self.view.zoom_in)

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcuts(QKeySequence.keyBindings(QKeySequence.StandardKey.ZoomOut))
        self.zoom_out_action.triggered.connect(self.view.zoom_out)

        self.actual_size_action = QAction("Actual Size", self)
        self.actual_size_action.setShortcut(QKeySequence("Ctrl+0"))
        self.actual_size_action.triggered.connect(self._reset_canvas_zoom)

        self.new_canvas_action = QAction("New Canvas", self)
        self.new_canvas_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_canvas_action.triggered.connect(self._new_canvas)

        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.undo_action.setEnabled(False)
        self.undo_action.triggered.connect(self._undo)

        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        self.redo_action.setEnabled(False)
        self.redo_action.triggered.connect(self._redo)

        self.save_canvas_action = QAction("Save Current Canvas State…", self)
        self.save_canvas_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_canvas_action.setToolTip(
            "Serialises the entire canvas document to a .pyqtcs JSON file so you can reload it later."
        )
        self.save_canvas_action.triggered.connect(self._save_canvas_state)

        self.load_canvas_action = QAction("Load Canvas State…", self)
        self.load_canvas_action.setShortcut(QKeySequence("Ctrl+O"))
        self.load_canvas_action.setToolTip(
            "Opens a previously saved .pyqtcs canvas state file and loads it onto the canvas."
        )
        self.load_canvas_action.triggered.connect(self._load_canvas_state_from_dialog)

        self.export_code_action = QAction("Export to PyQt6 Code…", self)
        self.export_code_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_code_action.setToolTip(
            "Generates a complete runnable PyQt6 Python script from the current canvas and opens the Code Export panel."
        )
        self.export_code_action.triggered.connect(self._trigger_code_export)

    def _create_menus(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.new_canvas_action)
        file_menu.addSeparator()
        file_menu.addAction(self.undo_action)
        file_menu.addAction(self.redo_action)
        file_menu.addSeparator()
        file_menu.addAction(self.reload_preset_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_canvas_action)
        file_menu.addAction(self.load_canvas_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_code_action)
        file_menu.addSeparator()
        file_menu.addAction(self.duplicate_selected_action)
        file_menu.addAction(self.delete_selected_action)

        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self.fit_canvas_action)
        view_menu.addAction(self.frame_selection_action)
        view_menu.addAction(self.actual_size_action)
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        view_menu.addSeparator()
        view_menu.addAction(self.reset_layout_action)
        view_menu.addSeparator()

        self._view_menu = view_menu

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Studio", self)
        toolbar.setObjectName("mainToolbar")
        toolbar.setMovable(False)
        toolbar.addAction(self.reload_preset_action)
        toolbar.addAction(self.duplicate_selected_action)
        toolbar.addAction(self.delete_selected_action)
        toolbar.addAction(self.fit_canvas_action)
        toolbar.addAction(self.frame_selection_action)
        toolbar.addAction(self.actual_size_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_canvas_action)
        toolbar.addAction(self.load_canvas_action)
        toolbar.addAction(self.export_code_action)
        toolbar.addSeparator()
        toolbar.addAction(self.new_canvas_action)
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self.reset_layout_action)
        toolbar.addSeparator()

        workflow_label = QLabel(
            "Mission control: New · Undo · Redo · Fit · Frame · Duplicate · Save · Export",
            toolbar,
        )
        workflow_label.setToolTip(
            "Ctrl+N blank canvas · Ctrl+Z/Ctrl+Shift+Z undo/redo · F fit canvas · Shift+F frame selection · "
            "Ctrl+D duplicate · Ctrl+S save · Ctrl+O load · Ctrl+E export PyQt6 code."
        )
        toolbar.addWidget(workflow_label)

        toolbar.addSeparator()
        self._zoom_label = QLabel("Zoom: 100%", toolbar)
        self._zoom_label.setMinimumWidth(80)
        toolbar.addWidget(self._zoom_label)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

    def _create_docks(self) -> None:
        examples_dock = self._add_dock(
            title="Showcase",
            object_name="dock.examples",
            area=Qt.DockWidgetArea.LeftDockWidgetArea,
            widget=self._create_preset_library(),
        )

        library_dock = self._add_dock(
            title="Add to Canvas",
            object_name="dock.elementLibrary",
            area=Qt.DockWidgetArea.LeftDockWidgetArea,
            widget=self._create_element_library(),
        )

        outliner_dock = self._add_dock(
            title="Layers",
            object_name="dock.outliner",
            area=Qt.DockWidgetArea.LeftDockWidgetArea,
            widget=self._create_outliner_tree(),
        )

        canvas_states_dock = self._add_dock(
            title="Canvas States",
            object_name="dock.canvasStates",
            area=Qt.DockWidgetArea.LeftDockWidgetArea,
            widget=self._create_canvas_states_panel(),
        )

        inspector_dock = self._add_dock(
            title="Properties",
            object_name="dock.inspector",
            area=Qt.DockWidgetArea.RightDockWidgetArea,
            widget=self.inspector_panel,
        )

        interaction_dock = self._add_dock(
            title="Signals & Slots",
            object_name="dock.interactions",
            area=Qt.DockWidgetArea.RightDockWidgetArea,
            widget=self._create_signals_slots_panel(),
        )

        # Global App Options — live QApplication controls
        self._global_options_panel = GlobalOptionsPanel(self)
        global_options_dock = self._add_dock(
            title="Global App Options",
            object_name="dock.globalOptions",
            area=Qt.DockWidgetArea.RightDockWidgetArea,
            widget=self._global_options_panel,
        )

        # Code Export — generates runnable PyQt6 from the canvas
        self._code_export_panel = CodeExportPanel(self)
        self._code_export_panel.generate_requested.connect(self._handle_code_export_generate)
        code_export_dock = self._add_dock(
            title="Code Export",
            object_name="dock.codeExport",
            area=Qt.DockWidgetArea.RightDockWidgetArea,
            widget=self._code_export_panel,
        )

        user_test_dock = self._add_dock(
            title="Getting Started",
            object_name="dock.userTestGuide",
            area=Qt.DockWidgetArea.BottomDockWidgetArea,
            widget=self._create_getting_started_panel(),
        )

        tokens_dock = self._add_dock(
            title="Theme Tokens",
            object_name="dock.tokens",
            area=Qt.DockWidgetArea.RightDockWidgetArea,
            widget=self._create_theme_tokens_panel(),
        )

        history_dock = self._add_dock(
            title="History",
            object_name="dock.history",
            area=Qt.DockWidgetArea.BottomDockWidgetArea,
            widget=self._create_history_panel(),
        )

        self.tabifyDockWidget(examples_dock, library_dock)
        self.tabifyDockWidget(library_dock, outliner_dock)
        self.tabifyDockWidget(outliner_dock, canvas_states_dock)
        self.tabifyDockWidget(inspector_dock, interaction_dock)
        self.tabifyDockWidget(interaction_dock, global_options_dock)
        self.tabifyDockWidget(global_options_dock, code_export_dock)
        self.tabifyDockWidget(code_export_dock, tokens_dock)
        self.tabifyDockWidget(user_test_dock, history_dock)
        examples_dock.raise_()
        inspector_dock.raise_()
        user_test_dock.raise_()

    def _create_status_bar(self) -> None:
        status_bar = QStatusBar(self)
        status_bar.showMessage(
            "Load a gallery board, frame it with F, then duplicate, tune, and export the pieces you want to keep."
        )
        self.setStatusBar(status_bar)

    def _restore_window_state(self) -> None:
        geometry = self._settings.value("main_window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self._settings.value("main_window/state")
        if state is not None:
            self.restoreState(state)

    def _add_dock(
        self,
        *,
        title: str,
        object_name: str,
        area: Qt.DockWidgetArea,
        widget: QWidget,
    ) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setObjectName(object_name)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        self._view_menu.addAction(dock.toggleViewAction())
        self._dock_widgets.append(dock)
        return dock

    def _build_outliner(self) -> QTreeWidget:
        self.outliner_tree.clear()
        self._outliner_items.clear()
        for node in self.document.nodes:
            self.outliner_tree.addTopLevelItem(self._build_outliner_item(node))
        self.outliner_tree.expandAll()
        return self.outliner_tree

    def _build_outliner_item(self, node: StudioNode) -> QTreeWidgetItem:
        item = QTreeWidgetItem([node.label])
        item.setData(0, Qt.ItemDataRole.UserRole, node.node_id)
        self._outliner_items[node.node_id] = item
        for child in node.children:
            item.addChild(self._build_outliner_item(child))
        return item

    def _create_outliner_tree(self) -> QTreeWidget:
        self.outliner_tree = QTreeWidget(self)
        self.outliner_tree.setHeaderLabels(["Document Tree"])
        self.outliner_tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.outliner_tree.itemSelectionChanged.connect(self._handle_outliner_selection_change)
        return self._build_outliner()

    def _build_list_widget(self, entries: list[str]) -> QListWidget:
        widget = QListWidget(self)
        widget.addItems(entries)
        return widget

    def _create_getting_started_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        heading = QLabel("Getting Started")
        heading.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(heading)

        self._user_test_summary = QLabel(panel)
        self._user_test_summary.setWordWrap(True)
        layout.addWidget(self._user_test_summary)

        steps_frame = QFrame(panel)
        steps_layout = QVBoxLayout(steps_frame)
        steps_layout.setContentsMargins(0, 0, 0, 0)
        steps_layout.setSpacing(6)
        for step in (
            "1. Explore — Double-click a preset in the Showcase panel to load it onto the canvas.",
            "2. Inspect & Edit — Click any element on the canvas, then change its values in the Properties panel.",
            "3. Add an Element — Drag an item from 'Add to Canvas' onto the canvas, or double-click it.",
            "4. Property Library — Scroll down in Properties to see the full library of CSS-style property suggestions.",
            "5. Save & Export — Use Ctrl+S to save your canvas state; Ctrl+E to export runnable PyQt6 code.",
            "6. Experiment Freely — Use Ctrl+Z to undo, Ctrl+N for a blank slate, Ctrl+D to duplicate any element.",
        ):
            label = QLabel(step, steps_frame)
            label.setWordWrap(True)
            steps_layout.addWidget(label)
        layout.addWidget(steps_frame)

        layout.addStretch(1)
        self._refresh_user_test_guide()
        return panel

    def _refresh_user_test_guide(self) -> None:
        if not hasattr(self, "_user_test_summary"):
            return

        source_references = self.document.meta.get("source_references", [])
        source_text = (
            f"Public GitHub research set ({len(source_references)} source repo{'s' if len(source_references) != 1 else ''})"
            if source_references
            else "Internal baseline"
        )
        selected_ids = self.scene.selected_node_ids()
        selected_text = "Nothing selected yet"
        if selected_ids:
            selected_node = self.document.find_node(selected_ids[0])
            if selected_node is not None:
                selected_text = f"Selected: {selected_node.label}"
        self._user_test_summary.setText(
            f"Current example: {self.document.title}\n"
            f"{selected_text}\n"
            f"Inspiration: {source_text}\n"
            "Expectation: inspect many real widgets, open a popup or dialog, duplicate one example, then adjust it through Properties or the JSON block pane."
        )

    def _create_preset_library(self) -> QListWidget:
        self.preset_library = QListWidget(self)
        self.preset_library.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.preset_library.setToolTip(
            "Reload the giant showcase from here if you want a clean baseline. Then duplicate or drag examples to explore variants."
        )
        self.preset_library.itemDoubleClicked.connect(self._handle_preset_activation)
        self._refresh_preset_library()
        return self.preset_library

    def _create_element_library(self) -> QListWidget:
        self.element_library = ElementPaletteList(self)
        self.element_library.itemDoubleClicked.connect(self._handle_element_library_activation)
        self._refresh_element_library()
        return self.element_library

    def _refresh_preset_library(self) -> None:
        with QSignalBlocker(self.preset_library):
            self.preset_library.clear()
            current_row = -1
            for row, definition in enumerate(self.preset_registry.definitions()):
                item = QListWidgetItem(definition.display_name, self.preset_library)
                item.setData(Qt.ItemDataRole.UserRole, definition.preset_id)
                item.setToolTip(definition.tooltip())
                if definition.preset_id == self._current_preset_id:
                    current_row = row

            if current_row >= 0:
                self.preset_library.setCurrentRow(current_row)

    def _refresh_element_library(self) -> None:
        with QSignalBlocker(self.element_library):
            self.element_library.clear()
            for definition in self.element_registry.definitions():
                item = QListWidgetItem(definition.display_name, self.element_library)
                item.setData(Qt.ItemDataRole.UserRole, definition.element_type)
                item.setToolTip(
                    definition.description
                    + "\nDrag onto the canvas to place it exactly. After drop, adjust its values in Properties."
                )

    def add_element(
        self,
        element_type: str,
        position: tuple[float, float] | None = None,
    ) -> StudioNode | None:
        node = self.element_registry.instantiate(
            element_type,
            len(self.document.iter_nodes()),
            position=position,
        )
        if node is None:
            return None

        self.document.nodes.append(node)
        self._push_undo("Add element")
        self._rerender_and_reselect(node.node_id)
        self._frame_selection()
        self.statusBar().showMessage(f"Added {node.label}", 2500)
        return node

    def update_node_properties(
        self,
        node_id: str,
        updates: dict[str, object],
        *,
        rerender: bool,
    ) -> None:
        node = self.document.find_node(node_id)
        if node is None:
            return

        for key, value in updates.items():
            if key == "label":
                node.label = str(value)
            else:
                node.properties[key] = value

        if rerender:
            self._rerender_and_reselect(node_id)
        else:
            self._update_selection_summary()

    def _duplicate_selected_node(self) -> None:
        selected_ids = self.scene.selected_node_ids()
        if len(selected_ids) != 1:
            self.statusBar().showMessage("Select one example on the canvas before duplicating it.", 2500)
            return

        source = self.document.find_node(selected_ids[0])
        if source is None:
            self.statusBar().showMessage("The selected example could not be found in the document.", 2500)
            return

        duplicate = self._clone_node_tree(source, offset=(48.0, 48.0), rename_root=True)
        self._push_undo(f"Duplicate {source.label}")
        self.document.nodes.append(duplicate)
        self._rerender_and_reselect(duplicate.node_id)
        self._frame_selection()
        self.statusBar().showMessage(f"Duplicated {source.label}", 2500)

    def _delete_selected_nodes(self) -> None:
        selected_ids = self.scene.selected_node_ids()
        if not selected_ids:
            self.statusBar().showMessage("Select at least one example on the canvas before deleting it.", 2500)
            return

        removed_count = 0
        self._push_undo("Delete selected")
        for node_id in list(selected_ids):
            if self.document.remove_node(node_id):
                removed_count += 1

        if removed_count == 0:
            self.statusBar().showMessage("The selected examples could not be removed from the document.", 2500)
            return

        self._rerender_and_reselect(None)
        self._fit_canvas()
        noun = "example" if removed_count == 1 else "examples"
        self.statusBar().showMessage(f"Deleted {removed_count} {noun}.", 2500)

    def _clone_node_tree(
        self,
        node: StudioNode,
        *,
        offset: tuple[float, float],
        rename_root: bool,
    ) -> StudioNode:
        properties = dict(node.properties)
        if "x" in properties:
            properties["x"] = float(properties["x"]) + offset[0]
        if "y" in properties:
            properties["y"] = float(properties["y"]) + offset[1]
        return StudioNode(
            node_id=make_stable_id(node.node_type.replace("_", "-")),
            node_type=node.node_type,
            label=f"{node.label} Copy" if rename_root else node.label,
            properties=properties,
            children=[
                self._clone_node_tree(child, offset=offset, rename_root=False)
                for child in node.children
            ],
        )

    def _handle_element_library_activation(self, item: QListWidgetItem) -> None:
        element_type = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(element_type, str):
            self.add_element(element_type)

    def _handle_canvas_drop(self, element_type: str, x: float, y: float) -> None:
        self.add_element(element_type, position=(x, y))

    def _handle_node_moved(self, node_id: str, x: float, y: float) -> None:
        self.update_node_properties(
            node_id,
            {"x": round(x, 1), "y": round(y, 1)},
            rerender=False,
        )

    def _handle_node_resized(self, node_id: str, width: float, height: float) -> None:
        self.update_node_properties(
            node_id,
            {"width": round(width, 1), "height": round(height, 1)},
            rerender=False,
        )

    def _handle_property_change(self, node_id: str, key: str, value: object) -> None:
        normalized: object = value
        if key in {"x", "y", "width", "height"}:
            normalized = float(value)
        elif isinstance(value, bool):
            normalized = bool(value)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            normalized = value
        elif key in {"label", "cta_label", "description", "fill"}:
            normalized = str(value)
        if key not in {"x", "y", "width", "height"}:
            self._push_undo(f"Change {key}")
        self.update_node_properties(node_id, {key: normalized}, rerender=True)

    def _handle_property_remove(self, node_id: str, key: str) -> None:
        node = self.document.find_node(node_id)
        if node is None or key not in node.properties:
            return
        self._push_undo(f"Remove property: {key}")
        del node.properties[key]
        self._rerender_and_reselect(node_id)

    def _handle_block_apply(self, node_id: str, raw_json: str) -> None:
        current_node = self.document.find_node(node_id)
        if current_node is None:
            self.inspector_panel.set_block_error("The selected block no longer exists in the live document.")
            self.statusBar().showMessage("Unable to apply block: selection is no longer valid.", 3500)
            return

        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError as error:
            message = f"Invalid block JSON at line {error.lineno}, column {error.colno}."
            self.inspector_panel.set_block_error(message)
            self.statusBar().showMessage(message, 3500)
            return

        if not isinstance(payload, dict):
            message = "Block JSON must stay an object with node_id, node_type, label, and properties."
            self.inspector_panel.set_block_error(message)
            self.statusBar().showMessage(message, 3500)
            return

        try:
            replacement = StudioNode.from_dict(payload)
        except (KeyError, TypeError, ValueError) as error:
            message = f"Block JSON is missing required fields: {error}."
            self.inspector_panel.set_block_error(message)
            self.statusBar().showMessage(message, 3500)
            return

        if replacement.node_id != node_id:
            message = "Block JSON must keep the same node_id so selection stays stable."
            self.inspector_panel.set_block_error(message)
            self.statusBar().showMessage(message, 3500)
            return

        if replacement.node_type not in {"scene-card", "widget-preview"}:
            message = "Block JSON can currently render only scene-card or widget-preview node types."
            self.inspector_panel.set_block_error(message)
            self.statusBar().showMessage(message, 3500)
            return

        if not self.document.replace_node(node_id, replacement):
            self.inspector_panel.set_block_error("Unable to replace the selected block in the document.")
            self.statusBar().showMessage("Unable to apply block to the live document.", 3500)
            return

        self._push_undo("Apply block")
        self._rerender_and_reselect(node_id)
        self.statusBar().showMessage(f"Applied block changes to {replacement.label}", 2500)

    def _handle_preset_activation(self, item: QListWidgetItem) -> None:
        preset_id = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(preset_id, str):
            self.load_preset(preset_id)

    def load_preset(self, preset_id: str) -> StudioDocument | None:
        document = self.preset_registry.instantiate(preset_id)
        if document is None:
            return None

        self._current_preset_id = preset_id
        self.document = document
        self.setWindowTitle(f"PyQt6 Stylizer - {self.document.title}")
        self._update_reload_action()
        self._rerender_and_reselect(None)
        self._apply_document_workspace_state()
        self._refresh_user_test_guide()
        self.statusBar().showMessage(f"Loaded example: {self.document.title}", 2500)
        return document

    # ── Canvas States ─────────────────────────────────────────────────────────

    def _create_canvas_states_panel(self) -> QWidget:
        """Build the Canvas States dock widget content."""
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        heading = QLabel(
            "<b>Canvas States</b><br>"
            "Save the current canvas so you can switch between ideas freely.  "
            "Each saved state is a portable JSON file — share it or open it in any future session."
        )
        heading.setWordWrap(True)
        heading.setTextFormat(Qt.TextFormat.RichText)
        heading.setStyleSheet("color: #2c4258; font-size: 11px;")
        layout.addWidget(heading)

        save_btn = QPushButton("Save Current Canvas State…", panel)
        save_btn.setToolTip(
            "Ctrl+S  —  Saves the entire canvas document to a .pyqtcs JSON file.\n"
            "You can reload it at any time to restore this exact state."
        )
        save_btn.clicked.connect(self._save_canvas_state)
        layout.addWidget(save_btn)

        load_btn = QPushButton("Load Canvas State…", panel)
        load_btn.setToolTip(
            "Ctrl+O  —  Open a previously saved .pyqtcs canvas file and load it onto the canvas."
        )
        load_btn.clicked.connect(self._load_canvas_state_from_dialog)
        layout.addWidget(load_btn)

        recent_label = QLabel("Recent states (double-click to reload):")
        recent_label.setStyleSheet("font-size: 11px; color: #405261; margin-top: 4px;")
        layout.addWidget(recent_label)

        self._canvas_states_list = QListWidget(panel)
        self._canvas_states_list.setToolTip(
            "Double-click a recent state to reload it onto the canvas."
        )
        self._canvas_states_list.itemDoubleClicked.connect(self._handle_canvas_state_activation)
        layout.addWidget(self._canvas_states_list, stretch=1)

        remove_btn = QPushButton("Remove from Recent List", panel)
        remove_btn.setToolTip(
            "Removes the selected entry from the recent list (does not delete the file)."
        )
        remove_btn.clicked.connect(self._remove_canvas_state_from_recent)
        layout.addWidget(remove_btn)

        self._refresh_canvas_states_list()
        return panel

    def _canvas_states_dir(self) -> Path:
        states_dir = Path.home() / ".local" / "share" / "pyqt6-stylizer" / "states"
        states_dir.mkdir(parents=True, exist_ok=True)
        return states_dir

    def _recent_state_paths(self) -> list[str]:
        raw = self._settings.value("canvas_states/recent", [])
        return list(raw) if isinstance(raw, list) else []

    def _add_to_recent_states(self, path_str: str) -> None:
        recent = self._recent_state_paths()
        if path_str in recent:
            recent.remove(path_str)
        recent.insert(0, path_str)
        self._settings.setValue("canvas_states/recent", recent[:20])
        self._refresh_canvas_states_list()

    def _refresh_canvas_states_list(self) -> None:
        if not hasattr(self, "_canvas_states_list"):
            return
        with QSignalBlocker(self._canvas_states_list):
            self._canvas_states_list.clear()
            for path_str in self._recent_state_paths():
                p = Path(path_str)
                item = QListWidgetItem(p.name, self._canvas_states_list)
                item.setData(Qt.ItemDataRole.UserRole, path_str)
                item.setToolTip(
                    path_str + ("" if p.exists() else "\n(file no longer found)")
                )

    def _save_canvas_state(self) -> None:
        default_name = (
            self.document.title.replace(" ", "_").replace("/", "-") + ".pyqtcs"
        )
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Current Canvas State",
            str(self._canvas_states_dir() / default_name),
            "PyQt6 Stylizer Documents (*.pyqtcs);;JSON Files (*.json);;All Files (*)",
        )
        if not path_str:
            return
        try:
            Path(path_str).write_text(self.document.to_json(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, "Save Failed", f"Could not write file:\n{exc}")
            return
        self._add_to_recent_states(path_str)
        self.setWindowTitle(f"PyQt6 Stylizer - {Path(path_str).name}")
        self.statusBar().showMessage(f"Saved canvas state to {path_str}", 3000)

    def _load_canvas_state_from_dialog(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Load Canvas State",
            str(self._canvas_states_dir()),
            "PyQt6 Stylizer Documents (*.pyqtcs);;JSON Files (*.json);;All Files (*)",
        )
        if path_str:
            self._load_canvas_from_file(path_str)

    def _load_canvas_from_file(self, path_str: str) -> None:
        path = Path(path_str)
        if not path.exists():
            QMessageBox.warning(
                self,
                "File Not Found",
                f"The canvas state file could not be found:\n{path_str}",
            )
            return
        try:
            raw = path.read_text(encoding="utf-8")
            document = StudioDocument.from_json(raw)
        except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Could not load canvas state:\n{exc}",
            )
            return
        self.document = document
        self._current_preset_id = ""
        self._update_reload_action()
        self.setWindowTitle(f"PyQt6 Stylizer - {path.name}")
        self._rerender_and_reselect(None)
        self._fit_canvas()
        self._refresh_user_test_guide()
        self._add_to_recent_states(path_str)
        self.statusBar().showMessage(f"Loaded canvas state: {path.name}", 3000)

    def _handle_canvas_state_activation(self, item: QListWidgetItem) -> None:
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(path_str, str):
            self._load_canvas_from_file(path_str)

    def _remove_canvas_state_from_recent(self) -> None:
        selected = self._canvas_states_list.currentItem()
        if selected is None:
            return
        path_str = selected.data(Qt.ItemDataRole.UserRole)
        recent = self._recent_state_paths()
        if path_str in recent:
            recent.remove(path_str)
            self._settings.setValue("canvas_states/recent", recent)
        self._refresh_canvas_states_list()
        self.statusBar().showMessage("Removed from recent list.", 2000)

    # ── Code Export ───────────────────────────────────────────────────────────

    def _trigger_code_export(self) -> None:
        self._handle_code_export_generate()
        dock = self.findChild(QDockWidget, "dock.codeExport")
        if dock is not None:
            dock.show()
            dock.raise_()

    def _handle_code_export_generate(self) -> None:
        code = generate_code(self.document)
        self._code_export_panel.set_code(code)
        self.statusBar().showMessage("Generated PyQt6 code — see Code Export panel.", 2500)

    def _reload_current_preset(self) -> None:
        reloaded = self.load_preset(self._current_preset_id)
        if reloaded is None:
            self.statusBar().showMessage("No example preset is active.", 2500)

    def _update_reload_action(self) -> None:
        definition = self.preset_registry.definition_for(self._current_preset_id)
        if definition is None:
            self.reload_preset_action.setText("Reload Current Example")
            return
        self.reload_preset_action.setText(f"Reload {definition.display_name}")

    def _apply_document_workspace_state(self) -> None:
        panel_object_names = {
            "inspector": "dock.inspector",
            "interactions": "dock.interactions",
            "tokens": "dock.tokens",
            "history": "dock.history",
            "outliner": "dock.outliner",
            "examples": "dock.examples",
            "library": "dock.elementLibrary",
        }
        active_panel = self.document.workspace_state.get("active_panel")
        if isinstance(active_panel, str):
            dock = self.findChild(QDockWidget, panel_object_names.get(active_panel, ""))
            if dock is not None:
                dock.show()
                dock.raise_()

        recommended_zoom = self.document.workspace_state.get("recommended_zoom", 1.0)
        zoom_factor = float(recommended_zoom) if isinstance(recommended_zoom, (int, float)) else 1.0
        self.view.fit_to_scene_contents(extra_scale=zoom_factor)

    def _fit_canvas(self) -> None:
        recommended_zoom = self.document.workspace_state.get("recommended_zoom", 1.0)
        zoom_factor = float(recommended_zoom) if isinstance(recommended_zoom, (int, float)) else 1.0
        if self.view.fit_to_scene_contents(extra_scale=zoom_factor):
            self.statusBar().showMessage("Framed the full showcase on the canvas.", 2500)
        self._update_zoom_label()

    def _frame_selection(self) -> None:
        if self.view.frame_selected_items(extra_scale=0.96):
            self.statusBar().showMessage("Framed the selected example.", 2500)
            self._update_zoom_label()
            return
        self.statusBar().showMessage("Select an example before framing the selection.", 2500)

    def _reset_canvas_zoom(self) -> None:
        self.view.reset_zoom()
        self._update_zoom_label()
        self.statusBar().showMessage("Reset the canvas zoom to actual size.", 2500)

    def _rerender_and_reselect(self, node_id: str | None) -> None:
        self._build_outliner()
        self.scene.render_document(self.document)
        if node_id is not None:
            self.scene.select_node(node_id)
        self._handle_scene_selection_change()
        self._refresh_theme_tokens_panel()

    def _reset_layout(self) -> None:
        for dock in self._dock_widgets:
            dock.show()
        self.removeToolBar(self.findChild(QToolBar, "mainToolbar"))
        self._create_toolbar()
        self.statusBar().showMessage("Layout reset to the simpler guided workspace.", 3500)

    def _handle_outliner_selection_change(self) -> None:
        selected_items = self.outliner_tree.selectedItems()
        node_id = selected_items[0].data(0, Qt.ItemDataRole.UserRole) if selected_items else None
        self.scene.select_node(node_id if isinstance(node_id, str) else None)

    def _handle_scene_selection_change(self) -> None:
        self._sync_outliner_selection_from_scene()
        self._update_selection_summary()
        self._refresh_user_test_guide()
        self._update_action_states()

    def _sync_outliner_selection_from_scene(self) -> None:
        selected_ids = self.scene.selected_node_ids()
        with QSignalBlocker(self.outliner_tree):
            self.outliner_tree.clearSelection()
            if not selected_ids:
                return

            item = self._outliner_items.get(selected_ids[0])
            if item is not None:
                item.setSelected(True)
                self.outliner_tree.setCurrentItem(item)

    def _update_selection_summary(self) -> None:
        selected_ids = self.scene.selected_node_ids()
        selected_node = self.document.find_node(selected_ids[0]) if len(selected_ids) == 1 else None
        self.inspector_panel.set_selected_node(selected_node, self.scene.selection_summary())

    def _update_action_states(self) -> None:
        selected_ids = self.scene.selected_node_ids()
        self.duplicate_selected_action.setEnabled(len(selected_ids) == 1)
        self.delete_selected_action.setEnabled(bool(selected_ids))
        self.frame_selection_action.setEnabled(bool(selected_ids))

    # ── New Canvas ────────────────────────────────────────────────────────────

    def _new_canvas(self) -> None:
        """Replace the current document with a blank canvas and clear undo history."""
        blank = self.preset_registry.instantiate("blank-canvas")
        if blank is None:
            blank = StudioDocument(title="Blank Canvas", nodes=[], theme_tokens=[], interactions=[], workspace_state={}, meta={})
        self.document = blank
        self._current_preset_id = "blank-canvas"
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._update_undo_actions()
        self.setWindowTitle("PyQt6 Stylizer - Blank Canvas")
        self._update_reload_action()
        self._rerender_and_reselect(None)
        self.statusBar().showMessage("New blank canvas created. Drag elements from 'Add to Canvas' to get started.", 3000)

    # ── Undo / Redo ───────────────────────────────────────────────────────────

    def _push_undo(self, description: str = "Action") -> None:
        self._undo_stack.append(self.document.to_json())
        self._redo_stack.clear()
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
        self._update_undo_actions()
        self._append_history(description)

    def _undo(self) -> None:
        if not self._undo_stack:
            return
        self._redo_stack.append(self.document.to_json())
        raw = self._undo_stack.pop()
        self.document = StudioDocument.from_json(raw)
        self._current_preset_id = ""
        self._update_reload_action()
        self._rerender_and_reselect(None)
        self._update_undo_actions()
        self.statusBar().showMessage("Undo.", 2000)

    def _redo(self) -> None:
        if not self._redo_stack:
            return
        self._undo_stack.append(self.document.to_json())
        raw = self._redo_stack.pop()
        self.document = StudioDocument.from_json(raw)
        self._current_preset_id = ""
        self._update_reload_action()
        self._rerender_and_reselect(None)
        self._update_undo_actions()
        self.statusBar().showMessage("Redo.", 2000)

    def _update_undo_actions(self) -> None:
        self.undo_action.setEnabled(bool(self._undo_stack))
        self.redo_action.setEnabled(bool(self._redo_stack))

    # ── Zoom label ────────────────────────────────────────────────────────────

    def _update_zoom_label(self, scale: float | None = None) -> None:
        if not hasattr(self, "_zoom_label"):
            return
        if scale is None:
            scale = self.view.transform().m11()
        pct = int(round(scale * 100))
        self._zoom_label.setText(f"Zoom: {pct}%")

    # ── History panel helpers ─────────────────────────────────────────────────

    def _append_history(self, description: str) -> None:
        if not hasattr(self, "_history_list"):
            return
        item = QListWidgetItem(description)
        self._history_list.insertItem(0, item)
        if self._history_list.count() > 30:
            self._history_list.takeItem(self._history_list.count() - 1)

    def _create_history_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        heading = QLabel("Edit History")
        heading.setStyleSheet("font-size: 14px; font-weight: 700;")
        layout.addWidget(heading)

        note = QLabel("Most-recent actions appear at the top. Use Ctrl+Z / Ctrl+Shift+Z to undo or redo.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #405261; font-size: 11px;")
        layout.addWidget(note)

        self._history_list = QListWidget(panel)
        layout.addWidget(self._history_list, stretch=1)

        clear_btn = QPushButton("Clear History", panel)
        clear_btn.clicked.connect(self._history_list.clear)
        layout.addWidget(clear_btn)

        return panel

    # ── Theme Tokens panel helpers ────────────────────────────────────────────

    def _refresh_theme_tokens_panel(self) -> None:
        if not hasattr(self, "_theme_tokens_list"):
            return
        with QSignalBlocker(self._theme_tokens_list):
            self._theme_tokens_list.clear()
            if not self.document.theme_tokens:
                self._theme_tokens_list.addItem("(no tokens in this document)")
                return
            for token in self.document.theme_tokens:
                self._theme_tokens_list.addItem(f"{token.name} = {token.value!r}  [{token.category}]")

    def _create_theme_tokens_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        heading = QLabel("Theme Tokens")
        heading.setStyleSheet("font-size: 14px; font-weight: 700;")
        layout.addWidget(heading)

        note = QLabel(
            "Design tokens from the current document. Load a different example preset to see "
            "how tokens change. Tokens drive colour, spacing, and shape across the whole canvas."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #405261; font-size: 11px;")
        layout.addWidget(note)

        self._theme_tokens_list = QListWidget(panel)
        layout.addWidget(self._theme_tokens_list, stretch=1)

        self._refresh_theme_tokens_panel()
        return panel

    # ── Signals & Slots panel ─────────────────────────────────────────────────

    def _create_signals_slots_panel(self) -> QWidget:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        inner = QWidget(scroll)
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        heading = QLabel("Signals & Slots — PyQt6 Core Concept")
        heading.setStyleSheet("font-size: 14px; font-weight: 700;")
        layout.addWidget(heading)

        explanation = QLabel(
            "<b>Signals</b> are notifications emitted by a widget when something happens "
            "(e.g. a button is clicked).<br>"
            "<b>Slots</b> are ordinary Python methods that respond to those notifications.<br>"
            "You connect them with <code>widget.signal.connect(slot)</code>."
        )
        explanation.setWordWrap(True)
        explanation.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(explanation)

        examples = [
            ("Button click",
             "button = QPushButton('Click me')\nbutton.clicked.connect(self.on_click)\n\ndef on_click(self):\n    print('Button was clicked!')"),
            ("Text changed",
             "line_edit = QLineEdit()\nline_edit.textChanged.connect(self.on_text)\n\ndef on_text(self, text: str):\n    print(f'Text is now: {text}')"),
            ("Slider value",
             "slider = QSlider(Qt.Orientation.Horizontal)\nslider.valueChanged.connect(self.on_value)\n\ndef on_value(self, value: int):\n    print(f'Slider: {value}')"),
            ("Custom signal",
             "from PyQt6.QtCore import pyqtSignal, QObject\n\nclass Counter(QObject):\n    count_changed = pyqtSignal(int)\n\n    def increment(self):\n        self._n += 1\n        self.count_changed.emit(self._n)"),
        ]

        for title, code in examples:
            group = QGroupBox(title, inner)
            g_layout = QVBoxLayout(group)
            code_label = QLabel(f"<pre>{code}</pre>", group)
            code_label.setTextFormat(Qt.TextFormat.RichText)
            code_label.setStyleSheet(
                "background: #f4f4f4; padding: 6px; border-radius: 4px; font-size: 11px;"
            )
            g_layout.addWidget(code_label)
            layout.addWidget(group)

        layout.addStretch(1)
        return scroll
