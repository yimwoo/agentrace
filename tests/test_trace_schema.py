from src.trace_schema import build_run_summary, summarize_trace, validate_trace_event


def test_validate_trace_event_accepts_complete_legacy_event():
    event = {"timestamp": "2026-04-25T00:00:00Z", "type": "tool_call", "name": "search", "status": "ok", "details": {}, "duration_ms": 3}
    result = validate_trace_event(event)
    assert result["ok"] is True
    assert result["missing"] == []
    assert result["schema"] == "legacy"


def test_validate_trace_event_accepts_common_envelope():
    event = {"id": "evt_001", "seq": 1, "type": "tool_call", "started_at": "2026-04-25T00:00:00Z", "status": "succeeded"}
    result = validate_trace_event(event)
    assert result["ok"] is True
    assert result["missing"] == []
    assert result["schema"] == "envelope"


def test_validate_trace_event_rejects_bad_envelope_status():
    event = {"id": "evt_001", "seq": 1, "type": "tool_call", "started_at": "2026-04-25T00:00:00Z", "status": "ok"}
    result = validate_trace_event(event)
    assert result["ok"] is False
    assert any("status" in error for error in result["errors"])


def test_summarize_trace_counts_ok_events_and_duration():
    events = [{"timestamp": "2026-04-25T00:00:00Z", "type": "tool_call", "name": "search", "status": "ok", "details": {}, "duration_ms": 3}]
    result = summarize_trace(events)
    assert result == {"event_count": 1, "ok_events": 1, "total_duration_ms": 3}


def test_build_run_summary_extracts_failure_inspection_targets():
    trace = {"run": {"status": "failed"}, "events": [{"id": "evt_1", "seq": 1, "type": "command", "status": "failed", "started_at": "2026-04-25T00:00:00Z", "command": {"value": "pytest -q"}, "stderr_preview": "AssertionError"}, {"id": "evt_2", "seq": 2, "type": "file_edit", "status": "succeeded", "started_at": "2026-04-25T00:00:01Z", "file": {"path": "src/example.py"}}]}
    result = build_run_summary(trace)
    assert result["result"] == "failed"
    assert result["failure_reason"] == "AssertionError"
    assert result["commands_run"] == ["pytest -q"]
    assert result["files_changed"] == ["src/example.py"]
    assert result["next_inspection_targets"] == ["command evt_1 stderr_preview"]


def test_build_run_summary_carries_report_ready_timing_and_edit_fields():
    trace = {
        "run": {"status": "failed"},
        "events": [
            {
                "id": "evt_cmd",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:02Z",
                "duration_ms": 2000,
                "command": {"value": "pytest -q", "cwd": "/workspace/app"},
                "exit_code": 1,
            },
            {
                "id": "evt_edit",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:03Z",
                "ended_at": "2026-04-25T00:00:03.100Z",
                "duration_ms": 100,
                "file": {"path": "src/example.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Tighten report rows"},
            },
        ],
        "artifacts": [
            {"kind": "command_log", "path": "artifacts/evt_cmd.log", "event_id": "evt_cmd"},
            {"kind": "diff", "path": "artifacts/evt_edit.diff", "event_id": "evt_edit"},
        ],
    }

    result = build_run_summary(trace)

    assert result["command_durations_ms"] == [{
        "event": "evt_cmd",
        "command": "pytest -q",
        "duration_ms": 2000,
        "duration_source": "explicit",
        "status": "failed",
        "exit_code": 1,
        "cwd": "/workspace/app",
        "started_at": "2026-04-25T00:00:00Z",
        "ended_at": "2026-04-25T00:00:02Z",
        "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd.log"}],
    }]
    assert result["edit_summaries"] == [{
        "event": "evt_edit",
        "path": "src/example.py",
        "kind": "modify",
        "status": "succeeded",
        "duration_ms": 100,
        "duration_source": "explicit",
        "added_lines": 2,
        "removed_lines": 1,
        "summary": "Tighten report rows",
        "started_at": "2026-04-25T00:00:03Z",
        "ended_at": "2026-04-25T00:00:03.100Z",
        "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit.diff"}],
    }]


def test_build_run_summary_derives_duration_from_time_window_when_missing():
    trace = {
        "run": {"status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_window",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:01.250Z",
                "command": {"value": "pytest -q"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_window",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:02Z",
                "ended_at": "2026-04-25T00:00:02.075Z",
                "file": {"path": "src/example.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0, "summary": "Derive timing"},
            },
        ],
    }

    result = build_run_summary(trace)

    assert result["command_durations_ms"][0]["duration_ms"] == 1250
    assert result["command_durations_ms"][0]["duration_source"] == "derived"
    assert result["edit_summaries"][0]["duration_ms"] == 75
    assert result["edit_summaries"][0]["duration_source"] == "derived"
