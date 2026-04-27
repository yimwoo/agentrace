#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$ROOT/.venv"
STAMP="$VENV_DIR/.bootstrap.stamp"
LOCKFILE="$ROOT/dev-requirements.lock"
REQFILE="$ROOT/dev-requirements.txt"
if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --upgrade pip >/dev/null
if [ -f "$LOCKFILE" ]; then
  "$VENV_DIR/bin/python" -m pip install -r "$LOCKFILE"
else
  "$VENV_DIR/bin/python" -m pip install -r "$REQFILE"
fi
python_ver="$($VENV_DIR/bin/python -c 'import sys; print(sys.version.split()[0])')"
lock_hash="$(shasum -a 256 "${LOCKFILE:-$REQFILE}" | awk '{print $1}')"
printf 'python=%s\nlock_hash=%s\nbootstrapped_at=%s\n' "$python_ver" "$lock_hash" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STAMP"
