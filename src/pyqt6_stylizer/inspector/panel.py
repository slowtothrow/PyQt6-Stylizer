from __future__ import annotations

import json

from PyQt6.QtCore import QSignalBlocker, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..document import StudioNode


class InspectorPanel(QWidget):
    CORE_PROPERTY_KEYS = {"x", "y", "width", "height", "cta_label", "description", "fill"}

    property_change_requested = pyqtSignal(str, str, object)
    property_remove_requested = pyqtSignal(str, str)
    block_apply_requested = pyqtSignal(str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.current_node_id: str | None = None
        self._active_fill = "#f8f3e6"
        self._block_snapshot = ""
        self._syncing_block_preview = False
        self._dynamic_property_editors: dict[str, QWidget] = {}
        self._dynamic_property_remove_buttons: dict[str, QPushButton] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self._workflow_hint = QLabel(
            "Select an element, then change values here. The canvas and the selected block preview update immediately."
        )
        self._workflow_hint.setWordWrap(True)
        self._workflow_hint.setToolTip(
            "This panel is the primary edit surface. Next: click a canvas element or drag a new one onto the canvas."
        )
        layout.addWidget(self._workflow_hint)

        self._selection_summary = QLabel("Canvas selection will appear here.")
        self._selection_summary.setWordWrap(True)
        layout.addWidget(self._selection_summary)

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(8)

        self._label_editor = QLineEdit(self)
        self._label_editor.setToolTip(
            "Rename the selected element. Next: move it on canvas or adjust its geometry below."
        )
        self._label_editor.editingFinished.connect(
            lambda: self._emit_property_change("label", self._label_editor.text())
        )
        form.addRow("Label", self._label_editor)

        self._x_editor = self._build_spin_box(
            "Horizontal position in pixels. Changing this immediately repositions the selected element."
        )
        self._x_editor.valueChanged.connect(lambda value: self._emit_property_change("x", value))
        form.addRow("X", self._x_editor)

        self._y_editor = self._build_spin_box(
            "Vertical position in pixels. Changing this immediately repositions the selected element."
        )
        self._y_editor.valueChanged.connect(lambda value: self._emit_property_change("y", value))
        form.addRow("Y", self._y_editor)

        self._width_editor = self._build_spin_box(
            "Width in pixels for drawn scene cards. Next: change height or fill color."
        )
        self._width_editor.valueChanged.connect(
            lambda value: self._emit_property_change("width", value)
        )
        self._width_label = QLabel("Width", self)
        form.addRow(self._width_label, self._width_editor)

        self._height_editor = self._build_spin_box(
            "Height in pixels for drawn scene cards. The canvas updates as soon as the value changes."
        )
        self._height_editor.valueChanged.connect(
            lambda value: self._emit_property_change("height", value)
        )
        self._height_label = QLabel("Height", self)
        form.addRow(self._height_label, self._height_editor)

        self._cta_editor = QLineEdit(self)
        self._cta_editor.setToolTip(
            "Update the embedded button label. Next: inspect the block preview below to see the matching structured node."
        )
        self._cta_editor.editingFinished.connect(
            lambda: self._emit_property_change("cta_label", self._cta_editor.text())
        )
        self._cta_label = QLabel("CTA Label", self)
        form.addRow(self._cta_label, self._cta_editor)

        self._description_editor = QLineEdit(self)
        self._description_editor.setToolTip(
            "Describe the selected element. This text appears on the live preview right away."
        )
        self._description_editor.editingFinished.connect(
            lambda: self._emit_property_change("description", self._description_editor.text())
        )
        form.addRow("Description", self._description_editor)

        self._fill_button = QPushButton(self)
        self._fill_button.setToolTip(
            "Choose the fill color for drawn cards. Next: compare the new value in the block preview below."
        )
        self._fill_button.clicked.connect(self._pick_fill_color)
        self._fill_label = QLabel("Fill", self)
        form.addRow(self._fill_label, self._fill_button)

        layout.addLayout(form)

        self._extra_properties_label = QLabel("Additional properties")
        self._extra_properties_label.setToolTip(
            "These are every non-core node property exposed as live controls. Add your own keys to drive new experiments."
        )
        layout.addWidget(self._extra_properties_label)

        self._extra_properties_hint = QLabel(
            "Every property outside the common position, size, fill, and description fields appears here."
        )
        self._extra_properties_hint.setWordWrap(True)
        layout.addWidget(self._extra_properties_hint)

        self._dynamic_properties_container = QWidget(self)
        self._dynamic_properties_layout = QVBoxLayout(self._dynamic_properties_container)
        self._dynamic_properties_layout.setContentsMargins(0, 0, 0, 0)
        self._dynamic_properties_layout.setSpacing(8)
        layout.addWidget(self._dynamic_properties_container)

        add_row = QHBoxLayout()
        add_row.setContentsMargins(0, 0, 0, 0)
        add_row.setSpacing(8)
        self._new_property_key_editor = QLineEdit(self)
        self._new_property_key_editor.setPlaceholderText("new_property")
        self._new_property_key_editor.setToolTip(
            "Add any extra property key here. Use block JSON for nested structures if the value gets complex."
        )
        add_row.addWidget(self._new_property_key_editor)
        self._new_property_value_editor = QLineEdit(self)
        self._new_property_value_editor.setPlaceholderText('true, 12, "soft", [1, 2]')
        self._new_property_value_editor.setToolTip(
            "Values are parsed as JSON when possible, otherwise they stay strings."
        )
        add_row.addWidget(self._new_property_value_editor)
        self._add_property_button = QPushButton("Add Property", self)
        self._add_property_button.clicked.connect(self._emit_property_add)
        add_row.addWidget(self._add_property_button)
        layout.addLayout(add_row)

        self._block_label = QLabel("Selected block preview")
        self._block_label.setToolTip(
            "This is the structured block for the selected element. Edit the JSON, then apply it to rebuild the live selection."
        )
        layout.addWidget(self._block_label)

        self._block_hint = QLabel(
            "Edit the selected JSON block here, then click Apply Block. Revert restores the live document version."
        )
        self._block_hint.setWordWrap(True)
        self._block_hint.setToolTip(
            "This is the bi-directional canvas/code link for the refactor. Start with label, position, or description changes."
        )
        layout.addWidget(self._block_hint)

        self.block_preview = QPlainTextEdit(self)
        self.block_preview.setReadOnly(True)
        self.block_preview.setPlaceholderText("Select a canvas element to see its live structured block.")
        self.block_preview.setToolTip(
            "Selection drives this preview. Edit the JSON here, then apply it to sync the canvas back to the document."
        )
        self.block_preview.textChanged.connect(self._handle_block_text_changed)
        layout.addWidget(self.block_preview, stretch=1)

        block_actions = QHBoxLayout()
        block_actions.setContentsMargins(0, 0, 0, 0)
        block_actions.setSpacing(8)

        self._apply_block_button = QPushButton("Apply Block", self)
        self._apply_block_button.setToolTip(
            "Apply the JSON below to the selected element. Next: confirm the canvas and outliner match the edited block."
        )
        self._apply_block_button.clicked.connect(self._emit_block_apply)
        block_actions.addWidget(self._apply_block_button)

        self._revert_block_button = QPushButton("Revert", self)
        self._revert_block_button.setToolTip(
            "Throw away unsaved JSON edits and restore the current live document block."
        )
        self._revert_block_button.clicked.connect(self._revert_block_preview)
        block_actions.addWidget(self._revert_block_button)

        layout.addLayout(block_actions)

        self._block_status = QLabel("Select a canvas element to edit its structured block.")
        self._block_status.setWordWrap(True)
        layout.addWidget(self._block_status)

        self._set_fill_button(self._active_fill)
        self._set_editing_enabled(False)
        self._set_block_feedback("Select a canvas element to edit its structured block.")
        self._set_block_controls_enabled(False)

    def _build_spin_box(self, tooltip: str) -> QDoubleSpinBox:
        editor = QDoubleSpinBox(self)
        editor.setRange(0.0, 5000.0)
        editor.setDecimals(1)
        editor.setSingleStep(4.0)
        editor.setToolTip(tooltip)
        return editor

    def _set_fill_button(self, fill: str) -> None:
        self._active_fill = fill
        self._fill_button.setText(fill)
        self._fill_button.setStyleSheet(
            f"background-color: {fill}; color: {'#ffffff' if QColor(fill).lightness() < 128 else '#1f1f1f'};"
        )

    def _set_editing_enabled(self, enabled: bool) -> None:
        for widget in (
            self._label_editor,
            self._x_editor,
            self._y_editor,
            self._width_editor,
            self._height_editor,
            self._cta_editor,
            self._description_editor,
            self._fill_button,
            self._new_property_key_editor,
            self._new_property_value_editor,
            self._add_property_button,
        ):
            widget.setEnabled(enabled)
        for editor in self._dynamic_property_editors.values():
            editor.setEnabled(enabled)
        for button in self._dynamic_property_remove_buttons.values():
            button.setEnabled(enabled)

    def _set_optional_row_visibility(self, editor_label: QLabel, editor: QWidget, visible: bool) -> None:
        editor_label.setVisible(visible)
        editor.setVisible(visible)

    def _clear_dynamic_property_rows(self) -> None:
        self._dynamic_property_editors.clear()
        self._dynamic_property_remove_buttons.clear()
        while self._dynamic_properties_layout.count():
            item = self._dynamic_properties_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _rebuild_dynamic_property_rows(self, properties: dict[str, object]) -> None:
        self._clear_dynamic_property_rows()
        for key in sorted(properties):
            if key in self.CORE_PROPERTY_KEYS:
                continue
            row = QWidget(self._dynamic_properties_container)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)
            label = QLabel(key, row)
            label.setMinimumWidth(120)
            row_layout.addWidget(label)

            value = properties[key]
            editor: QWidget
            if isinstance(value, bool):
                checkbox = QCheckBox(row)
                checkbox.setChecked(value)
                checkbox.toggled.connect(lambda checked, property_key=key: self._emit_property_change(property_key, checked))
                editor = checkbox
            elif isinstance(value, (int, float)) and not isinstance(value, bool):
                number_editor = self._build_spin_box(f"Edit {key}")
                number_editor.setRange(-5000.0, 5000.0)
                number_editor.setValue(float(value))
                number_editor.valueChanged.connect(
                    lambda changed_value, property_key=key: self._emit_property_change(property_key, changed_value)
                )
                editor = number_editor
            else:
                text_editor = QLineEdit(str(value), row)
                text_editor.editingFinished.connect(
                    lambda property_key=key, widget=text_editor: self._emit_property_change(property_key, widget.text())
                )
                editor = text_editor

            row_layout.addWidget(editor, stretch=1)
            remove_button = QPushButton("Remove", row)
            remove_button.clicked.connect(lambda _checked=False, property_key=key: self._emit_property_remove(property_key))
            row_layout.addWidget(remove_button)

            self._dynamic_property_editors[key] = editor
            self._dynamic_property_remove_buttons[key] = remove_button
            self._dynamic_properties_layout.addWidget(row)

        self._dynamic_properties_container.setVisible(bool(self._dynamic_property_editors))
        self._extra_properties_hint.setText(
            "Every property outside the common fields appears here."
            if self._dynamic_property_editors
            else "No extra properties on this selection yet. Add one below to explore more parameters."
        )

    def _set_block_controls_enabled(self, enabled: bool) -> None:
        self.block_preview.setReadOnly(not enabled)
        self._apply_block_button.setEnabled(False)
        self._revert_block_button.setEnabled(False)

    def _set_block_feedback(self, message: str, *, is_error: bool = False) -> None:
        self._block_status.setText(message)
        self._block_status.setStyleSheet(
            f"color: {'#8a1c1c' if is_error else '#405261'};"
        )

    def set_block_error(self, message: str) -> None:
        self._set_block_feedback(message, is_error=True)

    def _set_block_preview_text(self, raw_json: str) -> None:
        self._syncing_block_preview = True
        self.block_preview.setPlainText(raw_json)
        self._syncing_block_preview = False

    def _refresh_block_editor_state(self) -> None:
        if self.current_node_id is None:
            self._set_block_controls_enabled(False)
            self._set_block_feedback("Select a canvas element to edit its structured block.")
            return

        self.block_preview.setReadOnly(False)
        raw_text = self.block_preview.toPlainText()
        is_dirty = raw_text != self._block_snapshot
        self._revert_block_button.setEnabled(is_dirty)

        if not is_dirty:
            self._apply_block_button.setEnabled(False)
            self._set_block_feedback(
                "Block matches the live canvas selection. Edit JSON here, then click Apply Block."
            )
            return

        try:
            payload = json.loads(raw_text)
        except json.JSONDecodeError as error:
            self._apply_block_button.setEnabled(False)
            self._set_block_feedback(
                f"Fix JSON before applying: line {error.lineno}, column {error.colno}.",
                is_error=True,
            )
            return

        if not isinstance(payload, dict):
            self._apply_block_button.setEnabled(False)
            self._set_block_feedback("Block JSON must stay an object with node_id, node_type, label, and properties.", is_error=True)
            return

        self._apply_block_button.setEnabled(True)
        self._set_block_feedback(
            "Ready to apply. Click Apply Block to rebuild the selected live block from this JSON."
        )

    def set_selected_node(self, node: StudioNode | None, selection_summary: str) -> None:
        self.current_node_id = node.node_id if node is not None else None
        self._selection_summary.setText(selection_summary)

        if node is None:
            self._set_editing_enabled(False)
            self._block_snapshot = ""
            self._set_block_preview_text("")
            self._clear_dynamic_property_rows()
            self._dynamic_properties_container.hide()
            self._set_optional_row_visibility(self._width_label, self._width_editor, False)
            self._set_optional_row_visibility(self._height_label, self._height_editor, False)
            self._set_optional_row_visibility(self._cta_label, self._cta_editor, False)
            self._set_optional_row_visibility(self._fill_label, self._fill_button, False)
            self._refresh_block_editor_state()
            return

        self._set_editing_enabled(True)
        properties = node.properties
        blockers = [
            QSignalBlocker(self._label_editor),
            QSignalBlocker(self._x_editor),
            QSignalBlocker(self._y_editor),
            QSignalBlocker(self._width_editor),
            QSignalBlocker(self._height_editor),
            QSignalBlocker(self._cta_editor),
            QSignalBlocker(self._description_editor),
        ]

        self._label_editor.setText(node.label)
        self._x_editor.setValue(float(properties.get("x", 0.0)))
        self._y_editor.setValue(float(properties.get("y", 0.0)))
        self._width_editor.setValue(float(properties.get("width", 0.0)))
        self._height_editor.setValue(float(properties.get("height", 0.0)))
        self._cta_editor.setText(str(properties.get("cta_label", "")))
        self._description_editor.setText(str(properties.get("description", "")))
        self._set_fill_button(str(properties.get("fill", self._active_fill)))
        self._set_optional_row_visibility(self._width_label, self._width_editor, "width" in properties)
        self._set_optional_row_visibility(self._height_label, self._height_editor, "height" in properties)
        self._set_optional_row_visibility(self._cta_label, self._cta_editor, "cta_label" in properties)
        self._set_optional_row_visibility(self._fill_label, self._fill_button, "fill" in properties)
        self._rebuild_dynamic_property_rows(properties)
        self._block_snapshot = json.dumps(node.to_dict(), indent=2, sort_keys=True)
        self._set_block_preview_text(self._block_snapshot)
        self._refresh_block_editor_state()
        del blockers

    def _emit_property_change(self, key: str, value: object) -> None:
        if self.current_node_id is None:
            return
        self.property_change_requested.emit(self.current_node_id, key, value)

    def _emit_property_remove(self, key: str) -> None:
        if self.current_node_id is None:
            return
        self.property_remove_requested.emit(self.current_node_id, key)

    def _emit_property_add(self) -> None:
        if self.current_node_id is None:
            return
        key = self._new_property_key_editor.text().strip()
        raw_value = self._new_property_value_editor.text().strip()
        if not key:
            return
        try:
            value = json.loads(raw_value) if raw_value else ""
        except json.JSONDecodeError:
            value = raw_value
        self._emit_property_change(key, value)
        self._new_property_key_editor.clear()
        self._new_property_value_editor.clear()

    def _handle_block_text_changed(self) -> None:
        if self._syncing_block_preview:
            return
        self._refresh_block_editor_state()

    def _emit_block_apply(self) -> None:
        if self.current_node_id is None or not self._apply_block_button.isEnabled():
            return
        self.block_apply_requested.emit(self.current_node_id, self.block_preview.toPlainText())

    def _revert_block_preview(self) -> None:
        self._set_block_preview_text(self._block_snapshot)
        self._refresh_block_editor_state()

    def _pick_fill_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._active_fill), self, "Choose Fill Color")
        if not color.isValid():
            return
        fill = color.name()
        self._set_fill_button(fill)
        self._emit_property_change("fill", fill)
