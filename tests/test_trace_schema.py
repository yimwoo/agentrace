from src.trace_schema import validate_trace_event


def test_validate_trace_event_accepts_complete_event():
    event = {
        "timestamp": "2026-04-25T00:00:00Z",
        "type": "tool_call",
        "name": "search",
        "status": "ok",
        "details": {},
        "duration_ms": 3,
    }
    result = validate_trace_event(event)
    assert result["ok"] is True
    assert result["missing"] == []
