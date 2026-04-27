#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT:${PYTHONPATH:-}"
"$ROOT/.venv/bin/python" "$ROOT/src/emit_example_trace.py"
