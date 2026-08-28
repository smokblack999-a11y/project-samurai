#!/usr/bin/env bash
set -euo pipefail
python -m data.validate_labels "$1"
python evaluation.py
python benchmark.py
python evaluate_report.py
