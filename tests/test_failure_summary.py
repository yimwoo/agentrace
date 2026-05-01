from src.failure_summary import build_failure_summary, failure_events, markdown_failure_section


def failing_trace():
    return {"events": [{"id": "evt_1", "type": "command", "status": "failed", "stderr_preview": "AssertionError"}, {"id": "evt_2", "type": "tool_call", "status": "succeeded"}]}


def test_failure_events_filters_failed_or_error_events():
    assert [event["id"] for event in failure_events(failing_trace())] == ["evt_1"]


def test_build_failure_summary_extracts_primary_reason_and_targets():
    summary = build_failure_summary(failing_trace())
    assert summary["failure_count"] == 1
    assert summary["primary_failure"] == "AssertionError"
    assert summary["inspection_targets"] == ["command evt_1"]


def test_markdown_failure_section_handles_successful_trace():
    assert "No failed events" in markdown_failure_section({"events": []})
