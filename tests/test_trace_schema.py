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
