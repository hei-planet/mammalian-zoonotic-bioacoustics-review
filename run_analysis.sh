#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python scripts/validate_data.py
python scripts/generate_summary.py
