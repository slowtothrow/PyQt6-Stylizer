from __future__ import annotations

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

SURFACE_APP = "#eef3f8"
SURFACE_PANEL = "#f8fbff"
SURFACE_ELEVATED = "#ffffff"
SURFACE_MUTED = "#f3f6fb"
BORDER_SUBTLE = "#d8e1ec"
BORDER_STRONG = "#bfd0e4"
TEXT_PRIMARY = "#162332"
TEXT_MUTED = "#526273"
ACCENT = "#2f80ed"
ACCENT_HOVER = "#1f6ad1"
ACCENT_SOFT = "#dceaff"
SUCCESS = "#1f9d74"
WARNING = "#b7791f"
DANGER = "#c05621"


def apply_application_palette(app: QApplication) -> None:
    """Apply a cool neutral palette that modernizes Fusion without fighting local demo styles."""
    palette = QPalette(app.palette())
    palette.setColor(QPalette.ColorRole.Window, QColor(SURFACE_APP))
    palette.setColor(QPalette.ColorRole.Base, QColor(SURFACE_ELEVATED))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(SURFACE_MUTED))
    palette.setColor(QPalette.ColorRole.Button, QColor(SURFACE_PANEL))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(TEXT_MUTED))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#122033"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#f8fbff"))
    app.setPalette(palette)


MAIN_WINDOW_STYLESHEET = f"""
QMainWindow#mainWindow {{
    background: {SURFACE_APP};
    color: {TEXT_PRIMARY};
}}
QMenuBar {{
    background: {SURFACE_PANEL};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {BORDER_SUBTLE};
    padding: 4px 8px;
}}
QMenuBar::item {{
    padding: 6px 10px;
    border-radius: 8px;
    background: transparent;
}}
QMenuBar::item:selected {{
    background: {ACCENT_SOFT};
}}
QMenu {{
    background: {SURFACE_ELEVATED};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 10px;
    padding: 6px;
}}
QMenu::item {{
    padding: 7px 12px;
    border-radius: 7px;
}}
QMenu::item:selected {{
    background: {ACCENT_SOFT};
}}
QToolBar {{
    background: {SURFACE_PANEL};
    border: none;
    border-bottom: 1px solid {BORDER_SUBTLE};
    spacing: 6px;
    padding: 8px 10px;
}}
QToolBar QToolButton, QToolButton {{
    background: {SURFACE_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 10px;
    padding: 6px 10px;
}}
QToolBar QToolButton:hover, QToolButton:hover {{
    border-color: {BORDER_STRONG};
    background: {ACCENT_SOFT};
}}
QStatusBar {{
    background: {SURFACE_PANEL};
    color: {TEXT_MUTED};
    border-top: 1px solid {BORDER_SUBTLE};
}}
QDockWidget {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QDockWidget::title {{
    text-align: left;
    background: {SURFACE_PANEL};
    border: 1px solid {BORDER_SUBTLE};
    border-bottom: none;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-weight: 700;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}}
QDockWidget > QWidget {{
    background: {SURFACE_ELEVATED};
    border: 1px solid {BORDER_SUBTLE};
    border-top: none;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}}
QTabBar::tab {{
    background: {SURFACE_MUTED};
    color: {TEXT_MUTED};
    border: 1px solid {BORDER_SUBTLE};
    padding: 7px 12px;
    margin-right: 4px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}}
QTabBar::tab:selected {{
    background: {SURFACE_ELEVATED};
    color: {TEXT_PRIMARY};
    border-color: {BORDER_STRONG};
}}
QTreeWidget, QListWidget, QPlainTextEdit, QTextEdit, QScrollArea, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QFontComboBox {{
    background: {SURFACE_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 10px;
    selection-background-color: {ACCENT};
    selection-color: #ffffff;
}}
QTreeWidget, QListWidget, QPlainTextEdit, QTextEdit {{
    padding: 4px;
}}
QHeaderView::section {{
    background: {SURFACE_MUTED};
    color: {TEXT_PRIMARY};
    border: none;
    border-right: 1px solid {BORDER_SUBTLE};
    border-bottom: 1px solid {BORDER_SUBTLE};
    padding: 6px 8px;
    font-weight: 700;
}}
QPushButton {{
    background: {SURFACE_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 10px;
    padding: 7px 12px;
    font-weight: 600;
}}
QPushButton:hover {{
    border-color: {BORDER_STRONG};
    background: {ACCENT_SOFT};
}}
QPushButton:pressed {{
    background: #cfe2ff;
}}
QGroupBox {{
    background: {SURFACE_ELEVATED};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 12px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: {TEXT_MUTED};
}}
QLabel {{
    color: {TEXT_PRIMARY};
}}
QSplitter::handle {{
    background: transparent;
}}
QSplitter::handle:horizontal {{
    width: 8px;
}}
QSplitter::handle:vertical {{
    height: 8px;
}}
QScrollBar:vertical, QScrollBar:horizontal {{
    background: {SURFACE_MUTED};
    border-radius: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: #c5d4e5;
    border-radius: 6px;
    min-height: 24px;
    min-width: 24px;
}}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
    background: #a9bfdc;
}}
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{
    background: transparent;
    border: none;
}}
"""
