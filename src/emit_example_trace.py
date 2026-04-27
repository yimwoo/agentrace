import json
from pathlib import Path

from trace_schema import validate_trace_event


def build_sample_trace():
    event = {
        "timestamp": "2026-04-25T00:00:00Z",
        "type": "tool_call",
        "name": "search",
        "status": "ok",
        "details": {"query": "agent trace"},
        "duration_ms": 12,
    }
    return {
        "task": "debug sample",
        "run_id": "sample-1",
        "events": [event],
        "result_summary": {"status": "success"},
        "timing": {"wall_clock_ms": 12},
    }


if __name__ == "__main__":
    trace = build_sample_trace()
    assert validate_trace_event(trace["events"][0])["ok"] is True
    Path("examples").mkdir(exist_ok=True)
    Path("examples/trace-example.json").write_text(json.dumps(trace, indent=2) + "\n")
    print("wrote examples/trace-example.json")
