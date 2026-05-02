# Contributing to PyQt6 Stylizer

Thanks for your interest in contributing!

---

## Development setup

```bash
sudo apt install python3-pyqt6 python3-venv python3-dev

git clone https://github.com/slowtothrow/PyQt6-Stylizer.git
cd PyQt6-Stylizer

python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running the tests

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python -m unittest discover -s tests -v
```

All 30 tests run headlessly with the offscreen Qt platform plugin. No display or GPU required.

## Code style

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
ruff check src tests
ruff format src tests
```

Type hints are checked with [mypy](https://mypy.readthedocs.io/):

```bash
mypy src
```

## Submitting changes

1. Fork the repository and create a feature branch from `main`.
2. Make your changes with tests where appropriate.
3. Ensure `ruff check` and `mypy` pass cleanly.
4. Ensure all 30 tests pass (`QT_QPA_PLATFORM=offscreen`).
5. Open a pull request with a clear description of what changed and why.

## Reporting bugs

Open an issue at https://github.com/slowtothrow/PyQt6-Stylizer/issues and include:

- Your Ubuntu/Linux version (`lsb_release -a`)
- Python version (`python3 --version`)
- PyQt6 version (`python3 -c "import PyQt6; print(PyQt6.QtCore.PYQT_VERSION_STR)"`)
- Steps to reproduce and what you expected vs. what happened
