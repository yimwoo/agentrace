# Trace Summary: investigate auth failure
- run_id: rich-1
- status: failed
- event_count: 3
- ok_events: 3
- total_duration_ms: 3325

## Command Timing

- evt_cmd_1: `pytest tests/test_auth.py -q` — 3200ms, status=failed, exit_code=1, cwd=/workspace/app

## Edit Summary

- src/auth.py: modify (+4/-1) — Translate decoder errors into 401 responses
