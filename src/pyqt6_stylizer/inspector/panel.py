from __future__ import annotations

import json
from dataclasses import dataclass

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..document import StudioNode


# ── Property library data ────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class _PropExample:
    key: str
    default_value: str  # JSON-parseable default (will be shown in value field)
    type_hint: str       # Human-readable type label
    pyqt6_api: str       # The exact PyQt6 call this corresponds to
    description: str     # Beginner-friendly explanation


_PROPERTY_LIBRARY: list[tuple[str, list[_PropExample]]] = [
    (
        "Visual / Style",
        [
            _PropExample(
                "opacity", "0.85", "float 0.0–1.0",
                "QGraphicsOpacityEffect().setOpacity(0.85)\nwidget.setGraphicsEffect(effect)",
                "Controls how transparent the widget appears.  1.0 is fully opaque; 0.0 is invisible.  "
                "In PyQt6 this is achieved with QGraphicsOpacityEffect rather than a property setter.",
            ),
            _PropExample(
                "border_radius", "8", "int (pixels)",
                "widget.setStyleSheet('border-radius: 8px')",
                "Rounds the widget corners.  Requires a background-color in the stylesheet to be visible.  "
                "This is a QSS (Qt Style Sheet) property, not a direct method call.",
            ),
            _PropExample(
                "background_color", '"#e8f0fe"', "hex color string",
                "widget.setStyleSheet('background-color: #e8f0fe')",
                "Fills the widget background with a solid color.  "
                "Use a hex code (#rrggbb) or a CSS color name like 'tomato'.  "
                "Overrides the QPalette.Window / QPalette.Button roles for this one widget.",
            ),
            _PropExample(
                "border_color", '"#4a90d9"', "hex color string",
                "widget.setStyleSheet('border: 1px solid #4a90d9')",
                "Draws a visible border around the widget.  "
                "Pair with border_radius to get a rounded border.  "
                "border_width (int) controls thickness.",
            ),
            _PropExample(
                "border_width", "2", "int (pixels)",
                "widget.setStyleSheet('border: 2px solid <color>')",
                "Border stroke thickness in pixels.  Only has effect when border_color is also set.",
            ),
            _PropExample(
                "text_color", '"#1a2b3c"', "hex color string",
                "widget.setStyleSheet('color: #1a2b3c')",
                "Sets the foreground (text) color for labels, buttons, and inputs.  "
                "In stylesheet terms this is the CSS 'color' property.",
            ),
            _PropExample(
                "font_size", "14", "int (pixels)",
                "widget.setStyleSheet('font-size: 14px')",
                "Sets the font size for this widget's text in pixels.  "
                "Use widget.setFont(QFont(family, pointSize)) for point-based sizing.",
            ),
            _PropExample(
                "font_family", '"Segoe UI"', "string (font family name)",
                "widget.setStyleSheet('font-family: \"Segoe UI\"')\n# or:\nwidget.setFont(QFont('Segoe UI', 12))",
                "Changes the typeface used to render text in this widget.  "
                "For reliable cross-platform choices use: 'Arial', 'Verdana', 'Courier New', or 'Monospace'.",
            ),
            _PropExample(
                "padding", "10", "int (pixels)",
                "widget.setStyleSheet('padding: 10px')",
                "Adds internal spacing between the widget boundary and its content.  "
                "You can also write 'padding: 4px 12px' for vertical / horizontal.",
            ),
        ],
    ),
    (
        "Widget Behavior",
        [
            _PropExample(
                "enabled", "false", "bool",
                "widget.setEnabled(False)",
                "When False the widget is greyed out and ignores all user input.  "
                "Useful for showing that an action is not available without hiding it.",
            ),
            _PropExample(
                "visible", "false", "bool",
                "widget.setVisible(False)  # or widget.hide()",
                "Hides the widget completely (equivalent to widget.hide()).  "
                "Hidden widgets still exist; setVisible(True) / widget.show() restores them.",
            ),
            _PropExample(
                "flat", "true", "bool  (QPushButton only)",
                "button.setFlat(True)",
                "Removes the raised-button appearance and border from a QPushButton, "
                "making it look like a plain clickable label.  Often used in toolbars.",
            ),
            _PropExample(
                "checkable", "true", "bool  (QPushButton only)",
                "button.setCheckable(True)",
                "Turns a QPushButton into a toggle button that stays pressed or released.  "
                "Read the state with button.isChecked().",
            ),
            _PropExample(
                "checked", "true", "bool",
                "widget.setChecked(True)",
                "Sets the initial checked state of a QCheckBox, QRadioButton, or checkable QPushButton.",
            ),
            _PropExample(
                "read_only", "true", "bool  (QLineEdit / QTextEdit)",
                "line_edit.setReadOnly(True)",
                "Prevents the user from editing the text in a QLineEdit or QPlainTextEdit.  "
                "The text is still selectable and copyable.",
            ),
        ],
    ),
    (
        "Size & Layout",
        [
            _PropExample(
                "minimum_width", "120", "int (pixels)",
                "widget.setMinimumWidth(120)",
                "Prevents the widget from shrinking narrower than this value even when the "
                "window is resized.  The layout manager respects this as a hard constraint.",
            ),
            _PropExample(
                "maximum_width", "400", "int (pixels)",
                "widget.setMaximumWidth(400)",
                "Prevents the widget from growing wider than this value.  "
                "Combine with setMinimumWidth to lock the widget to a fixed range.",
            ),
            _PropExample(
                "minimum_height", "40", "int (pixels)",
                "widget.setMinimumHeight(40)",
                "Prevents the widget from shrinking shorter than this value.",
            ),
            _PropExample(
                "fixed_width", "200", "int (pixels)",
                "widget.setFixedWidth(200)",
                "Sets both minimum and maximum width to the same value so the widget never resizes "
                "horizontally.  Equivalent to calling setMinimumWidth and setMaximumWidth with the same value.",
            ),
            _PropExample(
                "spacing", "12", "int (pixels)",
                "layout.setSpacing(12)",
                "Gap between child items in a layout manager (QVBoxLayout, QHBoxLayout, etc.).  "
                "This is a layout property, not a widget property — set it on the layout, not the widget.",
            ),
            _PropExample(
                "margin", "16", "int (pixels)",
                "layout.setContentsMargins(16, 16, 16, 16)",
                "Padding between the widget boundary and the first layout item.  "
                "You can specify all four sides individually: (left, top, right, bottom).",
            ),
        ],
    ),
    (
        "Text & Interaction",
        [
            _PropExample(
                "tooltip", '"Hover text shown to the user"', "string",
                "widget.setToolTip('Hover text shown to the user')",
                "Pops up a short description when the user hovers over the widget for a moment.  "
                "Keep tooltips short and actionable.",
            ),
            _PropExample(
                "placeholder", '"Type here…"', "string  (QLineEdit / QPlainTextEdit)",
                "line_edit.setPlaceholderText('Type here…')",
                "Gray hint text shown when a QLineEdit or QPlainTextEdit is empty.  "
                "Disappears as soon as the user starts typing.",
            ),
            _PropExample(
                "value", "50", "int or float",
                "widget.setValue(50)  # QSlider, QSpinBox, QProgressBar",
                "Sets the current numeric value of a range widget.  "
                "The value must be within the widget's minimum–maximum range.",
            ),
            _PropExample(
                "maximum", "100", "int",
                "widget.setMaximum(100)  # QSlider, QSpinBox, QProgressBar",
                "Upper bound of the widget's numeric range.",
            ),
            _PropExample(
                "minimum", "0", "int",
                "widget.setMinimum(0)  # QSlider, QSpinBox, QProgressBar",
                "Lower bound of the widget's numeric range.",
            ),
            _PropExample(
                "tab_order", "1", "int (hint only)",
                "QWidget.setTabOrder(widget_a, widget_b)",
                "A canvas-level ordering hint.  In PyQt6 focus order is set with the static "
                "QWidget.setTabOrder(first, second) call, chained for each pair.  "
                "Lower numbers appear earlier in the tab sequence.",
            ),
        ],
    ),
    (
        "Animation Hints",
        [
            _PropExample(
                "animation_duration", "200", "int (milliseconds)",
                "QPropertyAnimation(...).setDuration(200)\n# or QTimeLine(200)",
                "Duration hint for hover/press/expand animations.  "
                "In PyQt6 animations use QPropertyAnimation targeting geometry, opacity, etc.  "
                "150–300 ms is the sweet spot for UI micro-interactions.",
            ),
            _PropExample(
                "hover_color", '"#d0e4f7"', "hex color string",
                "# Apply in QSS:\n"
                "QPushButton:hover { background-color: #d0e4f7; }",
                "Color shown when the user hovers the cursor over the widget.  "
                "In PyQt6 this is typically a QSS pseudo-state rule (:hover) rather than a method call.",
            ),
            _PropExample(
                "press_color", '"#a8c8ef"', "hex color string",
                "# Apply in QSS:\n"
                "QPushButton:pressed { background-color: #a8c8ef; }",
                "Color shown while the user holds the mouse button down on the widget.  "
                "Use the :pressed QSS pseudo-class.  Make it noticeably darker than hover_color.",
            ),
            _PropExample(
                "transition_easing", '"ease-in-out"', "string hint",
                "anim.setEasingCurve(QEasingCurve.Type.InOutQuad)\n# Choices: Linear, InQuad, OutQuad, InOutQuad, InOutCubic …",
                "Controls how an animation accelerates.  "
                "In PyQt6 this is a QEasingCurve.Type enum value set on a QPropertyAnimation instance.  "
                "InOutQuad gives a natural feel; Linear feels mechanical.",
            ),
        ],
    ),
]


def _looks_like_hex_color(s: str) -> bool:
    s = s.strip()
    if not s.startswith("#"):
        return False
    hex_part = s[1:]
    return len(hex_part) in (3, 6) and all(c in "0123456789abcdefABCDEF" for c in hex_part)


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

        # Wrap everything in a scroll area so properties are never clipped on
        # smaller displays.  The outer layout simply holds the scroll area.
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer.addWidget(scroll)

        inner = QWidget(scroll)
        scroll.setWidget(inner)

        layout = QVBoxLayout(inner)
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

        # ── Additional Properties ─────────────────────────────────────────────
        extra_label = QLabel("Additional Properties")
        extra_label.setStyleSheet("font-weight: 700; font-size: 13px; margin-top: 4px;")
        layout.addWidget(extra_label)

        extra_intro = QLabel(
            "Properties beyond the core fields appear here as live controls.  "
            "Use the <b>Property Library</b> below to discover ready-made examples "
            "with explanations — click any item to pre-fill the add form, then click "
            "<i>Add Property</i> to apply it to the selected element."
        )
        extra_intro.setWordWrap(True)
        extra_intro.setTextFormat(Qt.TextFormat.RichText)
        extra_intro.setStyleSheet("color: #405261; font-size: 11px;")
        layout.addWidget(extra_intro)

        self._extra_properties_hint = QLabel(
            "No extra properties on this selection yet."
        )
        self._extra_properties_hint.setWordWrap(True)
        self._extra_properties_hint.setStyleSheet("color: #405261; font-size: 11px;")
        layout.addWidget(self._extra_properties_hint)

        self._dynamic_properties_container = QWidget(self)
        self._dynamic_properties_layout = QVBoxLayout(self._dynamic_properties_container)
        self._dynamic_properties_layout.setContentsMargins(0, 0, 0, 0)
        self._dynamic_properties_layout.setSpacing(8)
        layout.addWidget(self._dynamic_properties_container)

        # ── Property Library (collapsible) ───────────────────────────────────
        layout.addWidget(self._build_property_library())

        # ── Manual add-property form ─────────────────────────────────────────
        add_group = QGroupBox("Add a property to the selected element")
        add_group_layout = QVBoxLayout(add_group)
        add_group_layout.setContentsMargins(8, 8, 8, 8)
        add_group_layout.setSpacing(6)

        add_hint = QLabel(
            "Key is the property name (e.g. <code>opacity</code>).  "
            "Value is JSON: <code>true</code>, <code>0.85</code>, <code>\"red\"</code>, <code>[1,2]</code>."
        )
        add_hint.setWordWrap(True)
        add_hint.setTextFormat(Qt.TextFormat.RichText)
        add_hint.setStyleSheet("font-size: 11px; color: #405261;")
        add_group_layout.addWidget(add_hint)

        add_row = QHBoxLayout()
        add_row.setContentsMargins(0, 0, 0, 0)
        add_row.setSpacing(8)
        self._new_property_key_editor = QLineEdit(self)
        self._new_property_key_editor.setPlaceholderText("property_key")
        self._new_property_key_editor.setToolTip(
            "Property name — use the Property Library above to pick from documented examples."
        )
        add_row.addWidget(self._new_property_key_editor)
        self._new_property_value_editor = QLineEdit(self)
        self._new_property_value_editor.setPlaceholderText('true, 0.85, "red", 12')
        self._new_property_value_editor.setToolTip(
            "JSON value — booleans: true/false, numbers: 12 or 0.5, strings: \"text\", lists: [1,2,3]."
        )
        add_row.addWidget(self._new_property_value_editor)
        self._add_property_button = QPushButton("Add Property", self)
        self._add_property_button.setToolTip(
            "Adds this key/value pair to the selected element and re-renders the canvas immediately."
        )
        self._add_property_button.clicked.connect(self._emit_property_add)
        add_row.addWidget(self._add_property_button)
        add_group_layout.addLayout(add_row)
        layout.addWidget(add_group)

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

    def _build_property_library(self) -> QGroupBox:
        """Build the collapsible Property Library group box."""
        group = QGroupBox("Property Library — click an item to pre-fill the add form")
        group.setToolTip(
            "36 documented PyQt6 property examples across 5 categories.  "
            "Click any item, inspect the description, then click 'Insert into Add Form' to try it."
        )
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(8, 8, 8, 8)
        group_layout.setSpacing(6)

        top_hint = QLabel(
            "Select a <b>category</b>, click a property, read the explanation, then click "
            "<i>Insert into Add Form</i> to pre-fill the form above."
        )
        top_hint.setWordWrap(True)
        top_hint.setTextFormat(Qt.TextFormat.RichText)
        top_hint.setStyleSheet("font-size: 11px; color: #405261;")
        group_layout.addWidget(top_hint)

        self._prop_lib_category = QComboBox(group)
        self._prop_lib_category.setToolTip("Filter properties by category.")
        for category_name, _ in _PROPERTY_LIBRARY:
            self._prop_lib_category.addItem(category_name)
        self._prop_lib_category.currentIndexChanged.connect(self._refresh_prop_lib_list)
        group_layout.addWidget(self._prop_lib_category)

        self._prop_lib_list = QListWidget(group)
        self._prop_lib_list.setMaximumHeight(130)
        self._prop_lib_list.setToolTip(
            "Click a property name to see its description and pre-fill the Add Property form."
        )
        self._prop_lib_list.currentItemChanged.connect(self._handle_prop_lib_selection)
        group_layout.addWidget(self._prop_lib_list)

        self._prop_lib_description = QLabel("", group)
        self._prop_lib_description.setWordWrap(True)
        self._prop_lib_description.setTextFormat(Qt.TextFormat.RichText)
        self._prop_lib_description.setStyleSheet(
            "font-size: 11px; color: #2c4258; background: #f0f5fb; "
            "border: 1px solid #c6d6e8; border-radius: 4px; padding: 6px;"
        )
        self._prop_lib_description.setMinimumHeight(60)
        self._prop_lib_description.hide()
        group_layout.addWidget(self._prop_lib_description)

        insert_btn = QPushButton("Insert into Add Form ↑", group)
        insert_btn.setToolTip(
            "Pre-fills the Key and Value fields in the 'Add a property' form above with the selected example."
        )
        insert_btn.clicked.connect(self._insert_prop_lib_example)
        group_layout.addWidget(insert_btn)

        self._refresh_prop_lib_list(0)
        return group

    def _refresh_prop_lib_list(self, index: int) -> None:
        self._prop_lib_list.clear()
        self._prop_lib_description.hide()
        if index < 0 or index >= len(_PROPERTY_LIBRARY):
            return
        _, examples = _PROPERTY_LIBRARY[index]
        for example in examples:
            item = QListWidgetItem(
                f"{example.key}  [{example.type_hint}]", self._prop_lib_list
            )
            item.setData(Qt.ItemDataRole.UserRole, example)
            item.setToolTip(example.description)

    def _handle_prop_lib_selection(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current is None:
            self._prop_lib_description.hide()
            return
        example: _PropExample | None = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(example, _PropExample):
            self._prop_lib_description.hide()
            return
        api_safe = example.pyqt6_api.replace("\n", "<br>").replace("<", "&lt;").replace(">", "&gt;")
        desc_safe = example.description.replace("<", "&lt;").replace(">", "&gt;")
        self._prop_lib_description.setText(
            f"<b>{example.key}</b> &nbsp; <i>({example.type_hint})</i><br>"
            f"<code style='font-size:10px;color:#1a3a5c;'>{api_safe}</code><br>"
            f"<span style='color:#2c4258;'>{desc_safe}</span>"
        )
        self._prop_lib_description.show()

    def _insert_prop_lib_example(self) -> None:
        current = self._prop_lib_list.currentItem()
        if current is None:
            return
        example: _PropExample | None = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(example, _PropExample):
            return
        self._new_property_key_editor.setText(example.key)
        self._new_property_value_editor.setText(example.default_value)
        self._new_property_key_editor.setFocus()

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
                # Add a colour swatch button for hex colour strings so the user
                # can pick a colour visually instead of typing hex digits.
                if _looks_like_hex_color(str(value)):
                    swatch = QPushButton(row)
                    swatch.setFixedSize(24, 24)
                    swatch.setToolTip("Click to pick a colour")
                    swatch.setStyleSheet(f"background-color: {value}; border: 1px solid #888;")

                    def _on_swatch_clicked(
                        _checked: bool = False,
                        _editor: QLineEdit = text_editor,
                        _swatch: QPushButton = swatch,
                        _key: str = key,
                    ) -> None:
                        initial = QColor(_editor.text()) if QColor(_editor.text()).isValid() else QColor()
                        color = QColorDialog.getColor(initial, self, "Choose colour")
                        if color.isValid():
                            hex_val = color.name()
                            _editor.setText(hex_val)
                            _swatch.setStyleSheet(f"background-color: {hex_val}; border: 1px solid #888;")
                            self._emit_property_change(_key, hex_val)

                    swatch.clicked.connect(_on_swatch_clicked)
                    row_layout.addWidget(swatch)

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
