"""Live QApplication-level option controls for the PyQt6 Stylizer.

Every control in this panel maps to a real PyQt6 API call and shows the exact
call as a label so beginners can copy the pattern directly into their own project.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFontComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QStyleFactory,
    QVBoxLayout,
    QWidget,
)

# Each entry: (display label, QPalette.ColorRole, tooltip explaining the PyQt6 API)
_PALETTE_ROLES: list[tuple[str, QPalette.ColorRole, str]] = [
    (
        "Window Background",
        QPalette.ColorRole.Window,
        "palette.setColor(QPalette.ColorRole.Window, color)\n"
        "The default fill for top-level windows and widget surfaces that inherit the window color.",
    ),
    (
        "Widget Base (inputs)",
        QPalette.ColorRole.Base,
        "palette.setColor(QPalette.ColorRole.Base, color)\n"
        "Background for text-input widgets: QLineEdit, QTextEdit, QListView, QTreeView.",
    ),
    (
        "Button Face",
        QPalette.ColorRole.Button,
        "palette.setColor(QPalette.ColorRole.Button, color)\n"
        "Background color of QPushButton and other button-like controls.",
    ),
    (
        "Window Text",
        QPalette.ColorRole.WindowText,
        "palette.setColor(QPalette.ColorRole.WindowText, color)\n"
        "Default foreground color for QLabel and text drawn on the window surface.",
    ),
    (
        "Button Text",
        QPalette.ColorRole.ButtonText,
        "palette.setColor(QPalette.ColorRole.ButtonText, color)\n"
        "Label text drawn on top of Button-role buttons.",
    ),
    (
        "Highlight",
        QPalette.ColorRole.Highlight,
        "palette.setColor(QPalette.ColorRole.Highlight, color)\n"
        "Background of selected items in QListWidget, QTreeWidget, QTableWidget.",
    ),
    (
        "Highlighted Text",
        QPalette.ColorRole.HighlightedText,
        "palette.setColor(QPalette.ColorRole.HighlightedText, color)\n"
        "Text drawn inside a highlighted (selected) item.",
    ),
    (
        "Link Color",
        QPalette.ColorRole.Link,
        "palette.setColor(QPalette.ColorRole.Link, color)\n"
        "Color for unvisited hyperlinks shown via QLabel rich text.",
    ),
    (
        "ToolTip Background",
        QPalette.ColorRole.ToolTipBase,
        "palette.setColor(QPalette.ColorRole.ToolTipBase, color)\n"
        "Background fill for all QToolTip pop-up boxes.",
    ),
]

_STYLESHEET_PLACEHOLDER = """\
/* Type or paste a global Qt Style Sheet here.
   It is applied to EVERY widget in the application.

   Examples:
   QPushButton { border-radius: 8px; padding: 6px 14px; }
   QLineEdit   { border: 1px solid #9aabbc; border-radius: 4px; }
   QWidget     { font-family: "Segoe UI"; font-size: 13px; }
   QToolTip    { background: #1f2d3d; color: #e8ecf0; border: none; }

   Leave empty and click Clear to remove all overrides.
*/"""


class GlobalOptionsPanel(QWidget):
    """Dock panel that exposes all major QApplication-level PyQt6 options.

    Each control shows the exact Python API call it performs so that learners
    can see precisely how to replicate the effect in their own code.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._palette_buttons: dict[QPalette.ColorRole, QPushButton] = {}
        self._working_palette: QPalette = QPalette(QApplication.palette())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        root.addWidget(scroll)

        inner = QWidget(scroll)
        scroll.setWidget(inner)
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(14)

        intro = QLabel(
            "<b>Global App Options</b><br>"
            "Each control below calls a real QApplication method on the running app so you can see the "
            "effect immediately. The exact Python call is shown as the group-box title — copy it into "
            "your own project to reproduce the same look."
        )
        intro.setWordWrap(True)
        intro.setTextFormat(Qt.TextFormat.RichText)
        intro.setStyleSheet("color: #2c4258; padding: 4px 0;")
        layout.addWidget(intro)

        layout.addWidget(self._build_style_group())
        layout.addWidget(self._build_font_group())
        layout.addWidget(self._build_palette_group())
        layout.addWidget(self._build_stylesheet_group())
        layout.addWidget(self._build_reset_group())
        layout.addStretch(1)

    # ── Application Style ────────────────────────────────────────────────────

    def _build_style_group(self) -> QGroupBox:
        group = QGroupBox("QApplication.setStyle(name)")
        layout = QVBoxLayout(group)

        note = QLabel(
            "Switches the entire widget rendering engine.  <b>Fusion</b> is cross-platform and identical "
            "on every OS — strongly recommended when learning PyQt6 because its rendering is predictable.  "
            "Windows / WindowsVista are only available on Windows."
        )
        note.setWordWrap(True)
        note.setTextFormat(Qt.TextFormat.RichText)
        note.setStyleSheet("font-size: 11px; color: #405261;")
        layout.addWidget(note)

        self._style_combo = QComboBox(group)
        available_styles = QStyleFactory.keys() or ["Fusion"]
        self._style_combo.addItems(available_styles)
        current = QApplication.style()
        if current:
            idx = self._style_combo.findText(
                current.objectName().capitalize(),
                Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive,
            )
            if idx < 0:
                idx = self._style_combo.findText("Fusion")
            if idx >= 0:
                self._style_combo.setCurrentIndex(idx)
        self._style_combo.currentTextChanged.connect(self._apply_style)
        layout.addWidget(self._style_combo)
        return group

    def _apply_style(self, name: str) -> None:
        QApplication.setStyle(name)

    # ── Application Font ─────────────────────────────────────────────────────

    def _build_font_group(self) -> QGroupBox:
        group = QGroupBox("QApplication.setFont(QFont(family, pointSize))")
        layout = QVBoxLayout(group)

        note = QLabel(
            "Sets the default font for every widget.  Individual widgets can still override it with "
            "<code>widget.setFont(font)</code>.  The point-size spinner lets you explore readable sizes "
            "without touching any source file."
        )
        note.setWordWrap(True)
        note.setTextFormat(Qt.TextFormat.RichText)
        note.setStyleSheet("font-size: 11px; color: #405261;")
        layout.addWidget(note)

        row = QHBoxLayout()
        self._font_combo = QFontComboBox(group)
        self._font_combo.setCurrentFont(QApplication.font())
        self._font_combo.currentFontChanged.connect(self._apply_font)
        row.addWidget(self._font_combo, stretch=1)

        self._font_size_spin = QDoubleSpinBox(group)
        self._font_size_spin.setRange(6.0, 48.0)
        self._font_size_spin.setDecimals(0)
        ps = QApplication.font().pointSize()
        self._font_size_spin.setValue(float(ps) if ps > 0 else 12.0)
        self._font_size_spin.setSuffix(" pt")
        self._font_size_spin.setToolTip("font.setPointSize(n)  — passed to QApplication.setFont()")
        self._font_size_spin.valueChanged.connect(self._apply_font)
        row.addWidget(self._font_size_spin)
        layout.addLayout(row)
        return group

    def _apply_font(self) -> None:
        font = self._font_combo.currentFont()
        font.setPointSize(int(self._font_size_spin.value()))
        QApplication.setFont(font)

    # ── Palette Color Roles ──────────────────────────────────────────────────

    def _build_palette_group(self) -> QGroupBox:
        group = QGroupBox("QApplication.setPalette(palette)  —  QPalette color roles")
        layout = QVBoxLayout(group)

        note = QLabel(
            "A <b>QPalette</b> maps named <i>color roles</i> to actual colors.  Changing a role here "
            "rebuilds the active palette and calls <code>QApplication.setPalette()</code> so every "
            "widget updates instantly.  This is how professional dark-mode or brand-color themes work "
            "in PyQt6 — no stylesheet required."
        )
        note.setWordWrap(True)
        note.setTextFormat(Qt.TextFormat.RichText)
        note.setStyleSheet("font-size: 11px; color: #405261;")
        layout.addWidget(note)

        form = QFormLayout()
        form.setContentsMargins(0, 4, 0, 4)
        form.setSpacing(6)
        for label_text, role, tooltip in _PALETTE_ROLES:
            button = QPushButton(group)
            button.setToolTip(tooltip)
            color = self._working_palette.color(QPalette.ColorGroup.Active, role)
            self._set_color_button(button, color)
            button.clicked.connect(
                lambda _checked=False, r=role, b=button: self._pick_palette_color(r, b)
            )
            self._palette_buttons[role] = button
            form.addRow(label_text, button)
        layout.addLayout(form)

        reset_btn = QPushButton("Reset palette to style defaults", group)
        reset_btn.setToolTip("Calls QApplication.setPalette(QApplication.style().standardPalette())")
        reset_btn.clicked.connect(self._reset_palette)
        layout.addWidget(reset_btn)
        return group

    def _set_color_button(self, button: QPushButton, color: QColor) -> None:
        button.setText(color.name())
        button.setStyleSheet(
            f"background-color: {color.name()}; "
            f"color: {'#ffffff' if color.lightness() < 128 else '#1f1f1f'}; "
            "padding: 2px 8px; min-width: 80px;"
        )

    def _pick_palette_color(self, role: QPalette.ColorRole, button: QPushButton) -> None:
        current_color = self._working_palette.color(QPalette.ColorGroup.Active, role)
        picked = QColorDialog.getColor(current_color, self, "Pick Color")
        if not picked.isValid():
            return
        self._working_palette.setColor(role, picked)
        self._set_color_button(button, picked)
        QApplication.setPalette(self._working_palette)

    def _reset_palette(self) -> None:
        style = QApplication.style()
        if style is not None:
            self._working_palette = style.standardPalette()
        else:
            self._working_palette = QPalette()
        for role, button in self._palette_buttons.items():
            color = self._working_palette.color(QPalette.ColorGroup.Active, role)
            self._set_color_button(button, color)
        QApplication.setPalette(self._working_palette)

    # ── Global Stylesheet ────────────────────────────────────────────────────

    def _build_stylesheet_group(self) -> QGroupBox:
        group = QGroupBox("QApplication.setStyleSheet(css)  —  global QSS override")
        layout = QVBoxLayout(group)

        note = QLabel(
            "A <b>Qt Style Sheet (QSS)</b> string applied to the whole application.  Selectors match "
            "widget class names like <code>QPushButton</code>, <code>QLineEdit</code>, etc.  The syntax "
            "is similar to CSS.  An empty string removes all overrides and falls back to the current "
            "style + palette."
        )
        note.setWordWrap(True)
        note.setTextFormat(Qt.TextFormat.RichText)
        note.setStyleSheet("font-size: 11px; color: #405261;")
        layout.addWidget(note)

        self._stylesheet_editor = QPlainTextEdit(group)
        self._stylesheet_editor.setPlaceholderText(_STYLESHEET_PLACEHOLDER)
        self._stylesheet_editor.setMinimumHeight(110)
        self._stylesheet_editor.setMaximumHeight(200)
        layout.addWidget(self._stylesheet_editor)

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply Stylesheet", group)
        apply_btn.setToolTip("Calls QApplication.setStyleSheet(text) with the content above.")
        apply_btn.clicked.connect(self._apply_stylesheet)
        clear_btn = QPushButton("Clear", group)
        clear_btn.setToolTip("Empties the editor and calls QApplication.setStyleSheet('').")
        clear_btn.clicked.connect(self._clear_stylesheet)
        btn_row.addWidget(apply_btn)
        btn_row.addWidget(clear_btn)
        layout.addLayout(btn_row)
        return group

    def _apply_stylesheet(self) -> None:
        QApplication.setStyleSheet(self._stylesheet_editor.toPlainText())

    def _clear_stylesheet(self) -> None:
        self._stylesheet_editor.setPlainText("")
        QApplication.setStyleSheet("")

    # ── Hard reset ───────────────────────────────────────────────────────────

    def _build_reset_group(self) -> QGroupBox:
        group = QGroupBox("Reset all app options")
        layout = QVBoxLayout(group)
        note = QLabel(
            "Restores Fusion style, clears the global stylesheet, resets the palette to style defaults, "
            "and resets the font to 12 pt Arial."
        )
        note.setWordWrap(True)
        note.setStyleSheet("font-size: 11px; color: #405261;")
        layout.addWidget(note)
        btn = QPushButton("Reset Everything to Defaults", group)
        btn.clicked.connect(self._reset_all)
        layout.addWidget(btn)
        return group

    def _reset_all(self) -> None:
        QApplication.setStyle("Fusion")
        self._style_combo.blockSignals(True)
        idx = self._style_combo.findText("Fusion")
        if idx >= 0:
            self._style_combo.setCurrentIndex(idx)
        self._style_combo.blockSignals(False)

        self._clear_stylesheet()
        self._reset_palette()

        font = QFont("Arial", 12)
        QApplication.setFont(font)
        self._font_combo.blockSignals(True)
        self._font_combo.setCurrentFont(font)
        self._font_combo.blockSignals(False)
        self._font_size_spin.blockSignals(True)
        self._font_size_spin.setValue(12.0)
        self._font_size_spin.blockSignals(False)
