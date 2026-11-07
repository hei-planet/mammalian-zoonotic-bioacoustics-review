#!/usr/bin/env bash
set -euo pipefail

# Execute from any directory. Installs dependencies only in the project's .venv.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if [[ ! -x .venv/bin/python ]]; then
  echo "Creating isolated environment in $repo_root/.venv"
  python3 -m venv .venv
fi

echo "Installing notebook dependencies into .venv"
.venv/bin/python -m pip install -r requirements-notebooks.txt

echo "Exporting notebook figures"
.venv/bin/python scripts/export_notebook_figures.py "$@"

echo "Export complete: results/figures/"
