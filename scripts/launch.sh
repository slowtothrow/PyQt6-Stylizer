#!/usr/bin/env bash
set -euo pipefail

unset LD_LIBRARY_PATH
unset LD_PRELOAD
unset GTK_PATH
unset GIO_MODULE_DIR
unset GSETTINGS_SCHEMA_DIR
unset LOCPATH
unset XDG_DATA_DIRS_SAVED

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYQT6_STYLIZER_PYTHON:-/usr/bin/python3}"

export PYTHONPATH="${ROOT_DIR}/src${PYTHONPATH:+:${PYTHONPATH}}"

exec "${PYTHON_BIN}" -m pyqt6_stylizer "$@"
