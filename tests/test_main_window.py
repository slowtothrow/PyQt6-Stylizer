from __future__ import annotations

import json
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtWidgets import QGraphicsTextItem, QPushButton
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from pyqt6_stylizer.main_window import MainWindow
from pyqt6_stylizer.registry import PresetRegistry


class MainWindowSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = MainWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self) -> None:
        self.window.close()
        self.app.processEvents()

    def test_scene_renders_document_nodes(self) -> None:
        self.assertEqual(
            self.window.scene.rendered_node_ids(),
            {node.node_id for node in self.window.document.iter_nodes()},
        )

    def test_scene_and_outliner_selection_stay_in_sync(self) -> None:
        first_node = self.window.document.nodes[0]
        second_node = self.window.document.nodes[1]

        self.window.scene.select_node(first_node.node_id)
        self.app.processEvents()
        selected_item = self.window.outliner_tree.currentItem()
        self.assertIsNotNone(selected_item)
        self.assertEqual(selected_item.data(0, Qt.ItemDataRole.UserRole), first_node.node_id)

        second_item = self.window._outliner_items[second_node.node_id]
        self.window.outliner_tree.clearSelection()
        second_item.setSelected(True)
        self.window.outliner_tree.setCurrentItem(second_item)
        self.app.processEvents()

        self.assertEqual(self.window.scene.selected_node_ids(), [second_node.node_id])

    def test_adding_element_updates_document_scene_and_outliner(self) -> None:
        initial_count = len(self.window.document.nodes)

        new_node = self.window.add_element("palette-swatch")

        self.assertIsNotNone(new_node)
        assert new_node is not None
        self.assertEqual(len(self.window.document.nodes), initial_count + 1)
        self.assertEqual(self.window.document.find_node(new_node.node_id), new_node)
        self.assertIn(new_node.node_id, self.window.scene.rendered_node_ids())
        self.assertIn(new_node.node_id, self.window._outliner_items)
        self.assertEqual(self.window.scene.selected_node_ids(), [new_node.node_id])

    def test_drag_style_add_element_uses_explicit_drop_position(self) -> None:
        new_node = self.window.add_element("scene-card", position=(512.0, 288.0))

        self.assertIsNotNone(new_node)
        assert new_node is not None
        self.assertEqual(new_node.properties["x"], 512.0)
        self.assertEqual(new_node.properties["y"], 288.0)

    def test_loading_preset_updates_document_scene_and_window_title(self) -> None:
        loaded_document = self.window.load_preset("showcase-playground")

        self.assertIsNotNone(loaded_document)
        assert loaded_document is not None
        self.assertEqual(self.window.document.meta.get("preset_id"), "showcase-playground")
        self.assertEqual(self.window.windowTitle(), "PyQt6 Stylizer - UI Showcase Playground")
        self.assertEqual(
            self.window.scene.rendered_node_ids(),
            {node.node_id for node in self.window.document.iter_nodes()},
        )

    def test_examples_and_elements_are_fully_exposed(self) -> None:
        preset_ids = {
            self.window.preset_library.item(index).data(Qt.ItemDataRole.UserRole)
            for index in range(self.window.preset_library.count())
        }
        element_ids = {
            self.window.element_library.item(index).data(Qt.ItemDataRole.UserRole)
            for index in range(self.window.element_library.count())
        }

        self.assertEqual(preset_ids, {"showcase-playground"})
        self.assertIn("effect-stack", element_ids)
        self.assertIn("inspector-host", element_ids)

    def test_showcase_contains_many_examples_and_kinds(self) -> None:
        nodes = self.window.document.nodes
        widget_kinds = {
            str(node.properties.get("kind"))
            for node in nodes
            if node.node_type == "widget-preview"
        }

        self.assertGreaterEqual(len(nodes), 16)
        self.assertIn("flyout-lab", widget_kinds)
        self.assertIn("dialog-lab", widget_kinds)
        self.assertIn("workspace-shell", widget_kinds)

    def test_showcase_widget_examples_keep_a_readable_gap(self) -> None:
        document = PresetRegistry.default().instantiate("showcase-playground")

        self.assertIsNotNone(document)
        assert document is not None
        widget_nodes = [node for node in document.nodes if node.node_type == "widget-preview"]
        minimum_gap = 24.0

        for index, node in enumerate(widget_nodes):
            left = float(node.properties["x"])
            top = float(node.properties["y"])
            width = float(node.properties["width"])
            height = float(node.properties["height"])
            expanded_left = left - minimum_gap
            expanded_top = top - minimum_gap
            expanded_right = left + width + minimum_gap
            expanded_bottom = top + height + minimum_gap

            for other in widget_nodes[index + 1 :]:
                other_left = float(other.properties["x"])
                other_top = float(other.properties["y"])
                other_right = other_left + float(other.properties["width"])
                other_bottom = other_top + float(other.properties["height"])
                overlaps = not (
                    expanded_right <= other_left
                    or other_right <= expanded_left
                    or expanded_bottom <= other_top
                    or other_bottom <= expanded_top
                )
                self.assertFalse(overlaps, f"{node.label} is too close to {other.label}")

    def test_dense_widget_preview_grows_to_fit_demo_content(self) -> None:
        navigation = next(
            node
            for node in self.window.document.nodes
            if node.node_type == "widget-preview" and node.properties.get("kind") == "navigation-workspace"
        )

        self.assertGreaterEqual(float(navigation.properties["width"]), 600.0)
        self.assertGreaterEqual(float(navigation.properties["height"]), 440.0)

        item = self.window.scene.item_for_node(navigation.node_id)
        self.assertIsNotNone(item)
        assert item is not None
        self.assertGreaterEqual(item.boundingRect().width(), 600.0)
        self.assertGreaterEqual(item.boundingRect().height(), 440.0)

    def test_canvas_item_move_updates_document_geometry(self) -> None:
        first_node = self.window.document.nodes[0]
        item = self.window.scene.item_for_node(first_node.node_id)

        self.assertIsNotNone(item)
        assert item is not None
        item.setPos(220.0, 245.0)
        self.app.processEvents()

        moved = self.window.document.find_node(first_node.node_id)
        self.assertIsNotNone(moved)
        assert moved is not None
        self.assertEqual(moved.properties["x"], 220.0)
        self.assertEqual(moved.properties["y"], 245.0)

    def test_canvas_resize_updates_document_geometry(self) -> None:
        widget_node = next(node for node in self.window.document.nodes if node.node_type == "widget-preview")

        resized = self.window.scene.resize_node(widget_node.node_id, 760.0, 520.0)
        self.app.processEvents()

        self.assertTrue(resized)
        changed = self.window.document.find_node(widget_node.node_id)
        item = self.window.scene.item_for_node(widget_node.node_id)

        self.assertIsNotNone(changed)
        self.assertIsNotNone(item)
        assert changed is not None
        assert item is not None
        self.assertEqual(changed.properties["width"], 760.0)
        self.assertEqual(changed.properties["height"], 520.0)
        self.assertGreaterEqual(item.boundingRect().width(), 760.0)
        self.assertGreaterEqual(item.boundingRect().height(), 520.0)

    def test_canvas_mouse_wheel_zooms_without_modifier(self) -> None:
        initial_scale = self.window.view.transform().m11()
        viewport_center = self.window.view.viewport().rect().center()
        event = QWheelEvent(
            QPointF(viewport_center),
            QPointF(viewport_center),
            QPoint(0, 0),
            QPoint(0, 120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.ScrollUpdate,
            False,
        )

        self.window.view.wheelEvent(event)

        self.assertGreater(self.window.view.transform().m11(), initial_scale)

    def test_scene_card_text_is_mouse_transparent(self) -> None:
        scene_card = next(node for node in self.window.document.nodes if node.node_type == "scene-card")
        item = self.window.scene.item_for_node(scene_card.node_id)

        self.assertIsNotNone(item)
        assert item is not None
        text_children = [child for child in item.childItems() if isinstance(child, QGraphicsTextItem)]

        self.assertTrue(text_children)
        self.assertTrue(all(child.acceptedMouseButtons() == Qt.MouseButton.NoButton for child in text_children))

    def test_clicking_widget_preview_button_selects_preview(self) -> None:
        widget_node = next(node for node in self.window.document.nodes if node.node_type == "widget-preview")
        item = self.window.scene.item_for_node(widget_node.node_id)

        self.assertIsNotNone(item)
        assert item is not None
        container = item.widget()

        self.assertIsNotNone(container)
        assert container is not None
        button = container.findChild(QPushButton)

        self.assertIsNotNone(button)
        assert button is not None

        self.window.scene.clearSelection()
        self.app.processEvents()
        QTest.mouseClick(button, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        self.app.processEvents()

        self.assertEqual(self.window.scene.selected_node_ids(), [widget_node.node_id])

    def test_selection_populates_property_panel_and_block_preview(self) -> None:
        first_node = self.window.document.nodes[0]

        self.window.scene.select_node(first_node.node_id)
        self.app.processEvents()

        self.assertEqual(self.window.inspector_panel.current_node_id, first_node.node_id)
        self.assertIn(first_node.node_id, self.window.inspector_panel.block_preview.toPlainText())

    def test_property_panel_changes_selected_node_and_scene(self) -> None:
        first_node = self.window.document.nodes[0]

        self.window.scene.select_node(first_node.node_id)
        self.app.processEvents()
        self.window.inspector_panel._x_editor.setValue(412.0)
        self.app.processEvents()

        changed = self.window.document.find_node(first_node.node_id)
        item = self.window.scene.item_for_node(first_node.node_id)

        self.assertIsNotNone(changed)
        self.assertIsNotNone(item)
        assert changed is not None
        assert item is not None
        self.assertEqual(changed.properties["x"], 412.0)
        self.assertEqual(item.pos().x(), 412.0)

    def test_dynamic_property_editor_updates_non_core_property(self) -> None:
        widget_node = next(node for node in self.window.document.nodes if node.node_type == "widget-preview")

        self.window.scene.select_node(widget_node.node_id)
        self.app.processEvents()

        editor = self.window.inspector_panel._dynamic_property_editors["kind"]
        self.assertEqual(editor.__class__.__name__, "QLineEdit")
        assert hasattr(editor, "setText")
        assert hasattr(editor, "editingFinished")
        editor.setText("effects-lab")
        editor.editingFinished.emit()
        self.app.processEvents()

        changed = self.window.document.find_node(widget_node.node_id)
        self.assertIsNotNone(changed)
        assert changed is not None
        self.assertEqual(changed.properties["kind"], "effects-lab")

    def test_add_and_remove_dynamic_property(self) -> None:
        first_node = self.window.document.nodes[0]

        self.window.scene.select_node(first_node.node_id)
        self.app.processEvents()
        self.window.inspector_panel._new_property_key_editor.setText("variant")
        self.window.inspector_panel._new_property_value_editor.setText('"ornate"')
        self.window.inspector_panel._add_property_button.click()
        self.app.processEvents()

        changed = self.window.document.find_node(first_node.node_id)
        self.assertIsNotNone(changed)
        assert changed is not None
        self.assertEqual(changed.properties["variant"], "ornate")

        remove_button = self.window.inspector_panel._dynamic_property_remove_buttons["variant"]
        remove_button.click()
        self.app.processEvents()

        changed_again = self.window.document.find_node(first_node.node_id)
        self.assertIsNotNone(changed_again)
        assert changed_again is not None
        self.assertNotIn("variant", changed_again.properties)

    def test_duplicate_selected_creates_offset_copy(self) -> None:
        source = self.window.document.nodes[0]

        self.window.scene.select_node(source.node_id)
        self.app.processEvents()
        self.window.duplicate_selected_action.trigger()
        self.app.processEvents()

        duplicate = self.window.document.nodes[-1]

        self.assertNotEqual(duplicate.node_id, source.node_id)
        self.assertEqual(duplicate.label, f"{source.label} Copy")
        self.assertEqual(duplicate.properties["x"], float(source.properties["x"]) + 48.0)
        self.assertEqual(duplicate.properties["y"], float(source.properties["y"]) + 48.0)
        self.assertEqual(self.window.scene.selected_node_ids(), [duplicate.node_id])

    def test_delete_selected_removes_node_from_document_and_scene(self) -> None:
        source = self.window.document.nodes[0]

        self.window.scene.select_node(source.node_id)
        self.app.processEvents()
        self.window.delete_selected_action.trigger()
        self.app.processEvents()

        self.assertIsNone(self.window.document.find_node(source.node_id))
        self.assertNotIn(source.node_id, self.window.scene.rendered_node_ids())
        self.assertEqual(self.window.scene.selected_node_ids(), [])

    def test_block_preview_apply_updates_selected_node_and_scene(self) -> None:
        first_node = self.window.document.nodes[0]

        self.window.scene.select_node(first_node.node_id)
        self.app.processEvents()

        payload = json.loads(self.window.inspector_panel.block_preview.toPlainText())
        payload["label"] = "Canvas Narrative Card"
        payload["properties"]["x"] = 468.0
        payload["properties"]["description"] = "Edited through the structured block pane."

        self.window.inspector_panel.block_preview.setPlainText(json.dumps(payload, indent=2, sort_keys=True))
        self.app.processEvents()
        self.window.inspector_panel._apply_block_button.click()
        self.app.processEvents()

        changed = self.window.document.find_node(first_node.node_id)
        item = self.window.scene.item_for_node(first_node.node_id)

        self.assertIsNotNone(changed)
        self.assertIsNotNone(item)
        assert changed is not None
        assert item is not None
        self.assertEqual(changed.label, "Canvas Narrative Card")
        self.assertEqual(changed.properties["x"], 468.0)
        self.assertEqual(changed.properties["description"], "Edited through the structured block pane.")
        self.assertEqual(item.pos().x(), 468.0)
        self.assertEqual(self.window._outliner_items[first_node.node_id].text(0), "Canvas Narrative Card")

    def test_block_preview_validation_prevents_node_id_changes(self) -> None:
        first_node = self.window.document.nodes[0]

        self.window.scene.select_node(first_node.node_id)
        self.app.processEvents()

        payload = json.loads(self.window.inspector_panel.block_preview.toPlainText())
        payload["node_id"] = "different-node-id"
        payload["label"] = "Should Not Apply"

        self.window.inspector_panel.block_preview.setPlainText(json.dumps(payload, indent=2, sort_keys=True))
        self.app.processEvents()
        self.window.inspector_panel._apply_block_button.click()
        self.app.processEvents()

        unchanged = self.window.document.find_node(first_node.node_id)
        self.assertIsNotNone(unchanged)
        assert unchanged is not None
        self.assertNotEqual(unchanged.label, "Should Not Apply")
        self.assertIn("same node_id", self.window.inspector_panel._block_status.text())