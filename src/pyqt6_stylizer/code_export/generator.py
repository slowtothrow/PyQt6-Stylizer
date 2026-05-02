"""Generates a complete, runnable PyQt6 Python script from a StudioDocument.

The generator is intentionally teaching-focused: every section of the output
is commented with the PyQt6 concept it demonstrates so the exported file is
readable as a tutorial as well as a starting point for a real project.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import pyqtSignal

from ..document.schema import StudioDocument, StudioNode

# ── widget-kind → PyQt6 class name ──────────────────────────────────────────

_KIND_TO_CLASS: dict[str, str] = {
    "button-card": "QPushButton",
    "simple-controls": "QPushButton",
    "toggle-card": "QCheckBox",
    "slider-card": "QSlider",
    "font-color-lab": "QLabel",
    "form-card": "QWidget",
    "table-card": "QTableWidget",
    "tree-card": "QTreeWidget",
    "dialog-card": "QDialog",
    "list-card": "QListWidget",
    "progress-card": "QProgressBar",
    "tabs-card": "QTabWidget",
    "combobox-card": "QComboBox",
    "spinbox-card": "QSpinBox",
    "textedit-card": "QPlainTextEdit",
    "lineedit-card": "QLineEdit",
    "radio-card": "QRadioButton",
    "groupbox-card": "QGroupBox",
    "scene-card": "QFrame",
    "showcase-map": "QFrame",
    "elegant-patterns": "QFrame",
    "dense-patterns": "QFrame",
    "duplicate-remix": "QFrame",
    # Widget-preview kinds present in the default showcase
    "choice-matrix": "QGroupBox",
    "slider-lab": "QSlider",
    "flyout-lab": "QWidget",
    "dialog-lab": "QDialog",
    "scroll-gallery": "QScrollArea",
    "navigation-workspace": "QWidget",
    "inspector-tree": "QTreeWidget",
    "data-table-console": "QTableWidget",
    "workspace-shell": "QWidget",
    "effects-lab": "QWidget",
}

# Widgets that live in QtWidgets
_WIDGETS_MODULE = {
    "QApplication", "QWidget", "QVBoxLayout", "QHBoxLayout", "QGridLayout",
    "QFormLayout", "QPushButton", "QCheckBox", "QLabel", "QLineEdit",
    "QPlainTextEdit", "QTextEdit", "QFrame", "QSlider", "QComboBox", "QSpinBox",
    "QDoubleSpinBox", "QProgressBar", "QTabWidget", "QListWidget", "QTreeWidget",
    "QTableWidget", "QDialog", "QGroupBox", "QRadioButton", "QFontComboBox",
    "QSizePolicy", "QScrollArea", "QSplitter", "QToolBox",
}
# Widgets that live in QtCore
_CORE_MODULE = {"Qt", "QSize", "QPoint", "QRect", "QTimer"}
# Widgets that live in QtGui
_GUI_MODULE = {
    "QFont", "QColor", "QPalette", "QIcon", "QPixmap",
    "QGraphicsOpacityEffect", "QGraphicsDropShadowEffect",
}


def _widget_class(node: StudioNode) -> str:
    kind = str(node.properties.get("kind", ""))
    if node.node_type == "scene-card":
        return _KIND_TO_CLASS.get(kind, "QFrame")
    return _KIND_TO_CLASS.get(kind, "QWidget")


def _safe_var(label: str, used: set[str]) -> str:
    """Create a unique, safe Python identifier from a node label."""
    cleaned = "".join(
        c if (c.isalnum() or c == "_") else "_"
        for c in label.replace(" ", "_").replace("-", "_").lower()
    )
    if not cleaned or cleaned[0].isdigit():
        cleaned = "w_" + cleaned
    base = cleaned or "widget"
    candidate = base
    counter = 2
    while candidate in used:
        candidate = f"{base}_{counter}"
        counter += 1
    used.add(candidate)
    return candidate


def _stylesheet_for_node(node: StudioNode, widget_class: str) -> str:
    """Build a QSS fragment from custom node properties."""
    p = node.properties
    parts: list[str] = []
    bg = p.get("background_color", p.get("fill"))
    if bg:
        parts.append(f"background-color: {bg};")
    if "border_radius" in p:
        parts.append(f"border-radius: {int(p['border_radius'])}px;")
    if "border_color" in p:
        bw = int(p.get("border_width", 1))
        parts.append(f"border: {bw}px solid {p['border_color']};")
    if "text_color" in p:
        parts.append(f"color: {p['text_color']};")
    if "font_size" in p:
        parts.append(f"font-size: {int(p['font_size'])}px;")
    if "font_family" in p:
        parts.append(f"font-family: \"{p['font_family']}\";")
    if "padding" in p:
        parts.append(f"padding: {int(p['padding'])}px;")
    if not parts:
        return ""
    css_body = " ".join(parts)
    return f'{widget_class} {{ {css_body} }}'


def _lines_for_node(node: StudioNode, used_vars: set[str]) -> tuple[list[str], set[str]]:
    """Return (source lines, set of required class names) for one node."""
    cls = _widget_class(node)
    var = _safe_var(node.label, used_vars)
    needed: set[str] = {cls}
    p = node.properties
    lines: list[str] = []

    lines.append(f"# ── {node.label} {'─' * max(0, 60 - len(node.label))}")

    # Construction
    if cls in ("QPushButton", "QCheckBox", "QRadioButton"):
        cta = str(p.get("cta_label", node.label))
        lines.append(f'self.{var} = {cls}("{cta}", self)')
    elif cls == "QLabel":
        desc = str(p.get("description", node.label))
        lines.append(f'self.{var} = {cls}("{desc}", self)')
    elif cls == "QSlider":
        needed.add("Qt")
        lines.append(f"self.{var} = {cls}(Qt.Orientation.Horizontal, self)")
    elif cls == "QTableWidget":
        lines.append(f"self.{var} = {cls}(4, 3, self)  # 4 rows, 3 columns")
    elif cls == "QProgressBar":
        lines.append(f"self.{var} = {cls}(self)")
        lines.append(f"self.{var}.setRange(0, 100)")
        lines.append(f"self.{var}.setValue(42)  # Replace with your data value")
    elif cls == "QGroupBox":
        lines.append(f'self.{var} = {cls}("{node.label}", self)')
    else:
        lines.append(f"self.{var} = {cls}(self)")

    # Geometry — setGeometry(x, y, width, height)
    x = int(p.get("x", 0))
    y = int(p.get("y", 0))
    w = int(p.get("width", 200))
    h = int(p.get("height", 100))
    lines.append(
        f"self.{var}.setGeometry({x}, {y}, {w}, {h})"
        "  # x, y, width, height in pixels"
    )

    # Description as tooltip if present
    desc = str(p.get("description", ""))
    if desc:
        safe_desc = desc.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'self.{var}.setToolTip("{safe_desc}")')

    # Explicit tooltip property (takes precedence)
    if "tooltip" in p:
        tip = str(p["tooltip"]).replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'self.{var}.setToolTip("{tip}")')

    # Boolean widget behavior
    if "enabled" in p:
        lines.append(f"self.{var}.setEnabled({bool(p['enabled'])})")
    if "visible" in p:
        lines.append(f"self.{var}.setVisible({bool(p['visible'])})")
    if "flat" in p and cls == "QPushButton":
        lines.append(f"self.{var}.setFlat({bool(p['flat'])})")
    if "checkable" in p and cls == "QPushButton":
        lines.append(f"self.{var}.setCheckable({bool(p['checkable'])})")
    if "checked" in p and cls in ("QPushButton", "QCheckBox", "QRadioButton"):
        lines.append(f"self.{var}.setChecked({bool(p['checked'])})")
    if "read_only" in p and cls in ("QLineEdit", "QPlainTextEdit", "QTextEdit"):
        lines.append(f"self.{var}.setReadOnly({bool(p['read_only'])})")

    # Placeholder text
    if "placeholder" in p and cls in ("QLineEdit", "QPlainTextEdit"):
        ph = str(p["placeholder"]).replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'self.{var}.setPlaceholderText("{ph}")')

    # Size constraints
    if "minimum_width" in p:
        lines.append(f"self.{var}.setMinimumWidth({int(p['minimum_width'])})")
    if "maximum_width" in p:
        lines.append(f"self.{var}.setMaximumWidth({int(p['maximum_width'])})")
    if "minimum_height" in p:
        lines.append(f"self.{var}.setMinimumHeight({int(p['minimum_height'])})")
    if "fixed_width" in p:
        lines.append(f"self.{var}.setFixedWidth({int(p['fixed_width'])})")

    # Value / range
    if "value" in p and cls in ("QSlider", "QSpinBox", "QDoubleSpinBox", "QProgressBar"):
        lines.append(f"self.{var}.setValue({p['value']})")
    if "maximum" in p and cls in ("QSlider", "QSpinBox", "QProgressBar"):
        lines.append(f"self.{var}.setMaximum({int(p['maximum'])})")
    if "minimum" in p and cls in ("QSlider", "QSpinBox", "QProgressBar"):
        lines.append(f"self.{var}.setMinimum({int(p['minimum'])})")

    # Opacity effect
    if "opacity" in p:
        opacity = max(0.0, min(1.0, float(p["opacity"])))
        needed.add("QGraphicsOpacityEffect")
        eff_var = f"_eff_{var}"
        lines.append(f"# opacity: use QGraphicsEffect — widget.setGraphicsEffect(effect)")
        lines.append(f"{eff_var} = QGraphicsOpacityEffect(self)")
        lines.append(f"{eff_var}.setOpacity({opacity:.2f})")
        lines.append(f"self.{var}.setGraphicsEffect({eff_var})")

    # Stylesheet (visual overrides from custom properties)
    ss = _stylesheet_for_node(node, cls)
    if ss:
        lines.append(f'self.{var}.setStyleSheet("{ss}")')

    lines.append(f"layout.addWidget(self.{var})")
    lines.append("")
    return lines, needed


def _build_imports(needed: set[str]) -> list[str]:
    widgets = sorted(needed & _WIDGETS_MODULE)
    core = sorted(needed & _CORE_MODULE)
    gui = sorted(needed & _GUI_MODULE)

    lines: list[str] = ["from __future__ import annotations", "", "import sys", ""]
    if widgets:
        lines.append("from PyQt6.QtWidgets import (")
        for name in widgets:
            lines.append(f"    {name},")
        lines.append(")")
    if core:
        lines.append(f"from PyQt6.QtCore import {', '.join(core)}")
    if gui:
        lines.append(f"from PyQt6.QtGui import {', '.join(gui)}")
    return lines


def generate_code(document: StudioDocument) -> str:
    """Return a complete, runnable PyQt6 Python script for *document*.

    The output is structured as a teaching artefact:
    - Imports section explains which module each class lives in.
    - The MainWindow class uses absolute geometry (setGeometry) so the layout
      mirrors the canvas exactly.  A comment on each widget suggests the next
      step (layout managers, signals, etc.).
    - A theme-tokens block preserves the palette choices you set on the canvas.
    - main() wires the QApplication startup boilerplate.
    """
    all_needed: set[str] = {"QApplication", "QWidget", "QVBoxLayout"}
    used_vars: set[str] = set()
    body_lines: list[str] = []

    for node in document.nodes:
        node_lines, node_needed = _lines_for_node(node, used_vars)
        all_needed |= node_needed
        body_lines.extend(node_lines)

    imports = _build_imports(all_needed)

    title_safe = document.title.replace("\\", "\\\\").replace('"', '\\"')

    out: list[str] = []
    out.extend(imports)
    out.append("")
    out.append("")
    out.append("class MainWindow(QWidget):")
    out.append('    """')
    out.append(f"    Exported from PyQt6 Stylizer canvas: {document.title}")
    out.append(f"    Document schema version: {document.schema_version}")
    out.append("")
    out.append("    HOW TO READ THIS FILE")
    out.append("    ─────────────────────")
    out.append("    • Each widget block maps to one canvas element.")
    out.append("    • setGeometry(x, y, w, h) reproduces the canvas position exactly.")
    out.append("    • Replace setGeometry with QVBoxLayout / QHBoxLayout / QGridLayout")
    out.append("      once you are ready to build a responsive layout.")
    out.append("    • Connect button.clicked, slider.valueChanged, etc. to your own slots.")
    out.append('    """')
    out.append("")
    out.append("    def __init__(self) -> None:")
    out.append("        super().__init__()")
    out.append(f'        self.setWindowTitle("{title_safe}")')
    out.append("        self.resize(1280, 800)")
    out.append("")
    out.append("        # QVBoxLayout stacks widgets vertically.")
    out.append("        # Swap for QHBoxLayout (horizontal) or QGridLayout (grid) as needed.")
    out.append("        layout = QVBoxLayout(self)")
    out.append("        layout.setContentsMargins(12, 12, 12, 12)")
    out.append("        layout.setSpacing(8)")

    if document.theme_tokens:
        out.append("")
        out.append("        # ── Theme tokens recorded on this canvas ──────────────────────────")
        out.append("        # Apply these to QPalette or stylesheet to reproduce the color scheme.")
        for token in document.theme_tokens:
            out.append(f"        #   {token.name} = {token.value!r}  [{token.category}]")

    out.append("")
    for line in body_lines:
        out.append("        " + line if line else "")

    out.append("")
    out.append("")
    out.append("def main() -> int:")
    out.append("    # QApplication must be created before any QWidget.")
    out.append("    app = QApplication(sys.argv)")
    out.append('    app.setStyle("Fusion")  # Cross-platform look; swap for "Windows" on Windows.')
    out.append("    window = MainWindow()")
    out.append("    window.show()")
    out.append("    # app.exec() starts the event loop; returns when the window closes.")
    out.append("    return app.exec()")
    out.append("")
    out.append("")
    out.append('if __name__ == "__main__":')
    out.append("    raise SystemExit(main())")
    out.append("")

    return "\n".join(out)


# ── Panel widget ─────────────────────────────────────────────────────────────


class CodeExportPanel(QWidget):
    """Dock panel that generates and displays exportable PyQt6 source code.

    The parent (MainWindow) connects *generate_requested* to a slot that calls
    ``set_code(generate_code(document))``.
    """

    generate_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        intro = QLabel(
            "<b>Code Export</b><br>"
            "Converts the current canvas state into a complete, runnable PyQt6 Python script.  "
            "Click <i>Generate Code</i> to refresh, then copy or save the result.  "
            "The exported file is annotated with explanations so it also works as a tutorial."
        )
        intro.setWordWrap(True)
        intro.setTextFormat(Qt.TextFormat.RichText)
        intro.setStyleSheet("color: #2c4258;")
        layout.addWidget(intro)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)

        generate_btn = QPushButton("Generate Code", self)
        generate_btn.setToolTip(
            "Reads the current canvas document and renders a complete PyQt6 Python script."
        )
        generate_btn.clicked.connect(self.generate_requested)
        btn_row.addWidget(generate_btn)

        copy_btn = QPushButton("Copy to Clipboard", self)
        copy_btn.setToolTip("Copies the generated source code to the system clipboard.")
        copy_btn.clicked.connect(self._copy_to_clipboard)
        btn_row.addWidget(copy_btn)

        save_btn = QPushButton("Save to File…", self)
        save_btn.setToolTip("Saves the generated code as a .py file you can run immediately.")
        save_btn.clicked.connect(self._save_to_file)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)

        mono_font = QFont("Monospace", 10)
        mono_font.setStyleHint(QFont.StyleHint.Monospace)

        self._code_view = QPlainTextEdit(self)
        self._code_view.setReadOnly(True)
        self._code_view.setFont(mono_font)
        self._code_view.setPlaceholderText(
            "Click 'Generate Code' to convert the current canvas state into a runnable PyQt6 Python script."
        )
        layout.addWidget(self._code_view, stretch=1)

        self._status_label = QLabel("", self)
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet("color: #405261; font-size: 11px;")
        layout.addWidget(self._status_label)

    # ── Public API ───────────────────────────────────────────────────────────

    def set_code(self, code: str) -> None:
        """Display *code* in the read-only editor."""
        self._code_view.setPlainText(code)
        line_count = code.count("\n")
        self._status_label.setText(
            f"Generated {line_count} lines.  Copy or save to use in your project."
        )

    # ── Private ──────────────────────────────────────────────────────────────

    def _copy_to_clipboard(self) -> None:
        code = self._code_view.toPlainText()
        if not code:
            self._status_label.setText("Nothing to copy — generate code first.")
            return
        QApplication.clipboard().setText(code)
        self._status_label.setText("Code copied to clipboard.")

    def _save_to_file(self) -> None:
        code = self._code_view.toPlainText()
        if not code:
            self._status_label.setText("Nothing to save — generate code first.")
            return
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Generated PyQt6 Code",
            "canvas_export.py",
            "Python Files (*.py);;All Files (*)",
        )
        if not path_str:
            return
        Path(path_str).write_text(code, encoding="utf-8")
        self._status_label.setText(f"Saved to {path_str}")
