# Changelog

All notable changes to PyQt6 Stylizer are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-05-02

### Added

- `QGraphicsView`-based live canvas with drag, resize, and zoom controls
- Document-backed canvas (`StudioDocument` / `StudioNode` / `ThemeToken`) with JSON round-trip persistence
- Canvas state save/load (`.pyqtcs` format, `Ctrl+S` / `Ctrl+O`)
- Recent canvas states list with double-click reload and remove
- **Inspector panel** — core widget property editors + dynamic extra properties
  - Built-in property library: ~36 documented examples across 5 categories
  - One-click insert from library into the add-property form
- **Global App Options** dock — live `QApplication`-level controls
  - Style picker (Fusion, Windows, etc.)
  - Font family + size (`QApplication.setFont`)
  - Nine QPalette color-role buttons (`QApplication.setPalette`)
  - Application-wide stylesheet editor (`QApplication.setStyleSheet`)
  - Reset-to-defaults button
- **Code Export** dock (`Ctrl+E`) — generates complete, runnable PyQt6 Python scripts with tutorial comments
- Outliner tree synchronized with canvas selection
- Element palette with drag-to-canvas placement
- `showcase-playground` preset with many widget examples
- Preset reload action (`Ctrl+R`)
- Duplicate (`Ctrl+D`) and delete (`Delete` / `Backspace`) canvas elements
- `F` / `Shift+F` fit-to-view and fit-to-selection shortcuts
- `scripts/launch.sh` — snap-safe launcher that unsets VS Code snap env vars
- `debian/` packaging skeleton (`dpkg-buildpackage -us -uc -b`)
- 30 unit tests (offscreen Qt, no display required)
- CLI: `--preset`, `--list-presets`, `--write-repository-gui-evaluation-prompt`
