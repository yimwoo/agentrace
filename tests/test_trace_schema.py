from src.trace_schema import summarize_trace, validate_trace_event


def test_validate_trace_event_accepts_complete_event():
    event = {"timestamp": "2026-04-25T00:00:00Z", "type": "tool_call", "name": "search", "status": "ok", "details": {}, "duration_ms": 3}
    result = validate_trace_event(event)
    assert result["ok"] is True
    assert result["missing"] == []


def test_summarize_trace_counts_ok_events_and_duration():
    events = [{"timestamp": "2026-04-25T00:00:00Z", "type": "tool_call", "name": "search", "status": "ok", "details": {}, "duration_ms": 3}]
    result = summarize_trace(events)
    assert result == {"event_count": 1, "ok_events": 1, "total_duration_ms": 3}
