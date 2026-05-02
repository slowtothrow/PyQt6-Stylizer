from __future__ import annotations

from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow
from .styles import apply_application_palette


def create_application() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    app.setOrganizationName("slowtothrow")
    app.setApplicationName("PyQt6 Stylizer")
    app.setApplicationDisplayName("PyQt6 Stylizer")
    app.setStyle("Fusion")
    apply_application_palette(app)
    return app


def run(*, startup_preset: str | None = None) -> int:
    app = create_application()
    window = MainWindow()
    if startup_preset is not None:
        window.load_preset(startup_preset)
    window.show()
    return app.exec()
