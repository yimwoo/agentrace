# Trace Summary: investigate auth failure
- run_id: rich-1
- status: failed
- event_count: 3
- ok_events: 3
- total_duration_ms: 3325
- command_count: 1
- command_total_duration_ms: 3200
- command_average_duration_ms: 3200.0
- command_failed_count: 1
- slowest_command: evt_cmd_1: `pytest tests/test_auth.py -q` (3200ms, status=failed, exit_code=1)
- files_changed_count: 1
- files_changed: src/auth.py
- edit_total_lines: +4/-1
- edit_net_line_delta: 3
- edit_total_duration_ms: 125

## Command Timing

- evt_cmd_1: `pytest tests/test_auth.py -q` — 3200ms, status=failed, exit_code=1, cwd=/workspace/app, started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:04.200Z

## Edit Summary

- src/auth.py: modify (+4/-1) — Translate decoder errors into 401 responses, status=succeeded, duration_ms=125, started_at=2026-04-25T00:00:05Z, ended_at=2026-04-25T00:00:05.125Z
