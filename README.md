# PyQt6 Stylizer

> **A Linux-first desktop studio for learning, exploring, and exporting PyQt6 widget styles and layouts.**

PyQt6 Stylizer is an interactive teaching tool and visual sandbox for Qt Widgets development. It gives you a live canvas full of real, inspectable widgets — buttons, sliders, dialogs, tables, nested layouts, and more — that you can select, resize, restyle, and duplicate in real time. When you are happy with what you have built, export a complete, runnable PyQt6 Python script with tutorial comments included.

---

## Features

- **Live canvas** built on `QGraphicsView` — drag, resize, and rearrange widget examples without touching code
- **Inspector panel** — edit core widget properties and dynamic extra properties with a built-in property library of ~36 documented examples
- **Global App Options** — live `QApplication`-level controls: style, font, palette color roles, and application-wide stylesheet
- **Code Export** — generate a complete, ready-to-run PyQt6 Python script from the current canvas state with inline tutorial comments
- **Save / Load canvas states** — persist and reload `.pyqtcs` snapshots of your full canvas
- **Preset system** — ship and load named example canvases; includes a rich `showcase-playground` preset
- **Outliner** — synchronized tree view of every canvas element for quick selection
- **Ubuntu/Debian native** — ships a `debian/` packaging skeleton and a snap-safe launcher

---

## Quick Start — Ubuntu / Debian

### Option A — Install from `.deb` (recommended for end users)

Download the latest `.deb` from the [Releases page](https://github.com/slowtothrow/PyQt6-Stylizer/releases) and run:

```bash
sudo apt install ./pyqt6-stylizer_0.1.0-1_all.deb
pyqt6-stylizer
```

The `.deb` pulls in `python3-pyqt6` automatically as a dependency.

### Option B — pip / pipx (any Linux distro)

```bash
# system PyQt6 first — avoids mixing system Qt and pip Qt
sudo apt install python3-pyqt6

# install the app into an isolated environment
pipx install git+https://github.com/slowtothrow/PyQt6-Stylizer.git

pyqt6-stylizer
```

### Option C — Development setup from source

```bash
# 1. system PyQt6 (avoids pip version conflicts with system Qt)
sudo apt install python3-pyqt6 python3-venv python3-dev

# 2. clone
git clone https://github.com/slowtothrow/PyQt6-Stylizer.git
cd PyQt6-Stylizer

# 3. create venv that can see the system PyQt6
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

# 4. install project in editable mode with dev extras
pip install -e ".[dev]"

# 5. run
python -m pyqt6_stylizer
```

> **VS Code / snap users:** If you launch from a VS Code snap terminal, use `scripts/launch.sh` instead. It unsets the snap-exported environment variables that break Qt library loading.
>
> ```bash
> bash scripts/launch.sh
> ```

---

## Building the `.deb` package

The `debian/` directory contains a complete `debhelper` packaging skeleton.

```bash
sudo apt install debhelper dh-python pybuild-plugin-pyproject python3-all python3-setuptools

cd PyQt6-Stylizer
dpkg-buildpackage -us -uc -b

# the .deb lands one directory up
sudo apt install ../pyqt6-stylizer_0.1.0-1_all.deb
```

---

## CLI reference

```
usage: pyqt6-stylizer [-h] [--preset PRESET_ID] [--list-presets]
                       [--write-repository-gui-evaluation-prompt [FILE]]
                       [--report-repository-root DIR]

Options:
  --preset PRESET_ID          Load a named preset on startup
  --list-presets               Print available preset IDs and exit
  --write-repository-gui-evaluation-prompt [FILE]
                               Write the AI-assisted repository analysis
                               prompt template to FILE (default: prompt.md)
  --report-repository-root DIR
                               Root directory for the evaluation prompt
```

### Examples

```bash
# start on the showcase playground preset
python -m pyqt6_stylizer --preset showcase-playground

# print available presets
python -m pyqt6_stylizer --list-presets
```

---

## Canvas keyboard shortcuts

| Key | Action |
|-----|--------|
| `F` | Fit entire canvas in view |
| `Shift+F` | Frame the current selection |
| `Ctrl+D` | Duplicate selected element |
| `Delete` / `Backspace` | Remove selected element |
| `Ctrl+S` | Save canvas state to file |
| `Ctrl+O` | Load canvas state from file |
| `Ctrl+E` | Open Code Export panel |
| Mouse wheel | Zoom under cursor |
| Middle-mouse drag | Pan canvas |
| `Esc` | Clear selection |
| Drag resize handle | Resize selected element |

---

## Project layout

```
src/pyqt6_stylizer/        Application package
  app.py                     QApplication factory and entry point
  main_window.py             QMainWindow — orchestrates all docks
  canvas/                    QGraphicsView/Scene canvas
  document/                  JSON-backed document model (StudioDocument)
  inspector/                 Properties panel + property library
  global_options/            Live QApplication-level controls panel
  code_export/               PyQt6 code generator and export panel
  registry/                  Element and preset registries
tests/                       Pure-Python unit tests (offscreen Qt)
docs/                        Architecture notes, schema, preset inspirations
scripts/                     Developer launchers (snap-safe)
debian/                      Debian packaging skeleton
```

---

## Canvas state file format

Canvas states are saved as `.pyqtcs` files (plain JSON). They contain the full `StudioDocument` — all nodes, their positions, sizes, properties, and theme tokens. Default save location: `~/.local/share/pyqt6-stylizer/states/`.

---

## Running the tests

```bash
# headless — no display required
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python -m unittest discover -s tests -v
```

All 30 tests run against the offscreen Qt platform; no physical display or GPU is needed.

---

## Code Export

The **Code Export** dock (`Ctrl+E`) converts the current canvas into a complete, self-contained PyQt6 Python script. Each widget is translated with:

- Correct import statements
- `setGeometry()` positioning
- Stylesheet properties mapped to `setStyleSheet()`
- Behavioral properties (`setEnabled`, `setVisible`, `setFlat`, etc.)
- A `QGraphicsOpacityEffect` where opacity is set
- Tutorial comments explaining every API call

The generated script runs immediately with `python generated_ui.py` (requires `python3-pyqt6`).

---

## Global App Options

The **Global App Options** dock lets you experiment with application-wide Qt settings live:

| Control | PyQt6 API |
|---------|-----------|
| Style (Fusion, Windows, …) | `QApplication.setStyle()` |
| Font family + size | `QApplication.setFont()` |
| Palette color roles | `QApplication.setPalette()` |
| Application stylesheet | `QApplication.setStyleSheet()` |
| Reset to defaults | Restores Fusion + system palette |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

[MIT](LICENSE)
