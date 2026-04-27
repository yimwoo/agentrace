#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
bash "$ROOT/scripts/bootstrap_env.sh"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
"$ROOT/.venv/bin/python" -m pytest tests/test_trace_schema.py tests/test_report_outputs.py -q
bash "$ROOT/scripts/smoke_check.sh"
