from src.trace_schema import build_run_summary, summarize_trace, validate_trace_event


def test_validate_trace_event_accepts_complete_event():
    event = {"timestamp": "2026-04-25T00:00:00Z", "type": "tool_call", "name": "search", "status": "ok", "details": {}, "duration_ms": 3}
    result = validate_trace_event(event)
    assert result["ok"] is True
    assert result["missing"] == []


def test_validate_trace_event_accepts_schema_event_envelope():
    event = {
        "id": "evt_001",
        "seq": 1,
        "type": "tool_call",
        "started_at": "2026-04-25T00:00:00Z",
        "status": "succeeded",
    }
    result = validate_trace_event(event)
    assert result["ok"] is True
    assert result["missing"] == []


def test_summarize_trace_counts_ok_events_and_duration():
    events = [{"timestamp": "2026-04-25T00:00:00Z", "type": "tool_call", "name": "search", "status": "ok", "details": {}, "duration_ms": 3}]
    result = summarize_trace(events)
    assert result == {"event_count": 1, "ok_events": 1, "total_duration_ms": 3}


def test_build_run_summary_surfaces_debugging_targets():
    trace = {
        "summary": {"result": "failed"},
        "events": [
            {
                "id": "evt_001",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "command": {"value": "pytest tests/test_trace_schema.py -q"},
                "stderr_preview": "AssertionError: expected compact summary",
            },
            {
                "id": "evt_002",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "file": {"path": "src/trace_schema.py"},
                "change": {"kind": "modify", "summary": "Add compact run summaries"},
            },
        ],
    }

    summary = build_run_summary(trace)

    assert summary["result"] == "failed"
    assert summary["failure_reason"] == "AssertionError: expected compact summary"
    assert summary["event_counts"] == {"command": 1, "file_edit": 1}
    assert summary["files_changed"] == ["src/trace_schema.py"]
    assert summary["commands_run"] == ["pytest tests/test_trace_schema.py -q"]
    assert summary["next_inspection_targets"] == ["command evt_001 stderr_preview"]


def test_build_run_summary_handles_legacy_event_details():
    trace = {
        "result_summary": {"status": "success"},
        "events": [
            {
                "timestamp": "2026-04-25T00:00:00Z",
                "type": "command",
                "name": "pytest",
                "status": "ok",
                "details": {"command": "pytest -q", "file": "tests/test_trace_schema.py"},
                "duration_ms": 3,
            }
        ],
    }

    summary = build_run_summary(trace)

    assert summary["result"] == "success"
    assert summary["event_counts"] == {"command": 1}
    assert summary["files_changed"] == ["tests/test_trace_schema.py"]
    assert summary["commands_run"] == ["pytest -q"]
    assert summary["next_inspection_targets"] == []
