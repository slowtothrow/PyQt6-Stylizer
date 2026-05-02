# PyQt6 Stylizer

PyQt6 Stylizer is a Linux-first desktop studio for exploring the visual tone and interaction density of Qt Widgets applications. The current refactor centers everything on one giant showcase canvas built on `QGraphicsView`, with many inspectable examples that can be duplicated, moved, restyled, and rewritten through structured JSON.

## Current milestone

- Hybrid shell: `QMainWindow` with a `QGraphicsView` canvas and dockable tool panels.
- Document-backed canvas rendering with synchronized scene and outliner selection.
- One large showcase canvas with simple controls, flyouts, dialogs, scroll regions, tables, dense nested shells, and styling studies side by side.
- Live duplication plus property and JSON block editing so any example can be forked and customized directly on the canvas.
- Ubuntu and Debian-ready launcher strategy that clears snap-polluted environment variables.

## Repository notes

- The repository is designed for a Linux-first PyQt6 workflow with a document-backed canvas that synchronizes editable JSON, live previews, and a drag-resize surface.
- The canvas examples are deliberately built to remain selectable and movable, including embedded widget previews that forward selection from child controls to the owning canvas node.
- Use `scripts/launch.sh` with `QT_QPA_PLATFORM=xcb` on this system to run the UI reliably under the current environment.

## Ubuntu development setup

Use the system `python3-pyqt6` package on Ubuntu instead of pip-installing PyQt6 alongside your project dependencies.

```bash
sudo apt install python3-pyqt6 python3-venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
python -m pyqt6_stylizer
```

If you prefer a shell launcher, use `scripts/launch.sh`. It unsets the environment variables exported by the VS Code snap before execing Python.

## Startup shortcuts

You can start directly in the showcase playground and reload it whenever you want a clean baseline.

```bash
python -m pyqt6_stylizer --list-presets
python -m pyqt6_stylizer --preset showcase-playground
```

## Canvas controls

The showcase is intentionally large, so the fastest way to work is to stay on the canvas as much as possible.

- `F` fits the full showcase back into view.
- `Shift+F` frames the current selection.
- `Ctrl+D` duplicates the selected example.
- `Delete` or `Backspace` removes the current selection.
- Scroll the mouse wheel to zoom in or out under the cursor.
- Middle-mouse drag pans the canvas.
- `Esc` clears the current selection.
- Drag the lower-right corner of a selected example to resize it directly on the canvas.

## Repository GUI Evaluation Prompt

The repo also ships a prompt generator for AI-assisted PyQt6 repository analysis. It writes a `prompt.md` template that tells another agent how to interrogate any repository, extract PyQt6 architecture/styling patterns, and anonymize identifying details with silly placeholder names.

```bash
python -m pyqt6_stylizer --write-repository-gui-evaluation-prompt
python -m pyqt6_stylizer --write-repository-gui-evaluation-prompt prompt.md --report-repository-root /path/to/repo
```

The generated prompt preserves real PyQt6 APIs and technical behavior, but instructs the answering agent to replace repository names, files, classes, functions, variables, and textual copy with invented placeholders while still extracting styling systems, widget inventories, and unique implementations.

## Layout

```text
src/pyqt6_stylizer/    Application package
tests/                 Pure-Python tests for schema and non-GUI logic
docs/                  Initial architecture and schema notes
scripts/               Local developer launchers
debian/                Debian packaging skeleton
```

## Validation

The repo is structured so the document layer and CLI stay testable without importing the GUI runtime, but GUI validation still depends on the system `python3-pyqt6` package on Ubuntu.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 -m unittest tests.test_main_window
```

## Initial user test

Use Showcase, Add to Canvas, Properties, and the User Test Guide together.

1. Start in `showcase-playground` and ask the tester which examples feel simplest versus densest at a glance.
2. Ask the tester to open at least one flyout and one dialog without guidance.
3. Ask the tester to duplicate one example, move it, and change live values in Properties.
4. Ask the tester to edit one obvious field in the duplicated block JSON and click `Apply Block`.
5. Capture confusion around discoverability, popup triggers, duplication flow, density, and whether the examples feel broad enough to inspire real product directions.
