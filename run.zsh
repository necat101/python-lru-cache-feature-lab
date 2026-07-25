#!/usr/bin/env zsh
set -euo pipefail
cd "${0:A:h}"
python3 run_lab.py
python3 -m unittest test_lab -v
