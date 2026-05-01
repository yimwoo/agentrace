import json
from pathlib import Path

from src.trace_schema import build_run_summary


def build_sample_trace():
    trace = {
        "trace_version": "0.1",
        "run": {
            "id": "sample-1",
            "task": "debug sample",
            "agent": {"name": "example-agent", "version": "0.1.0", "model": "sample-model"},
            "repo": {"name": "agentrace-example", "branch": "main", "commit": "abc123def"},
            "status": "success",
            "started_at": "2026-04-25T00:00:00Z",
            "ended_at": "2026-04-25T00:00:00.012Z",
            "duration_ms": 12,
            "attempt": 1,
            "parent_run_id": None,
        },
        "events": [{
            "id": "evt_001",
            "seq": 1,
            "type": "tool_call",
            "status": "succeeded",
            "started_at": "2026-04-25T00:00:00Z",
            "ended_at": "2026-04-25T00:00:00.012Z",
            "duration_ms": 12,
            "tool": {"name": "search", "args": {"query": "agent trace"}},
            "result": {"preview": "Found introductory agent trace notes", "item_count": 1},
        }],
        "artifacts": [],
    }
    trace["summary"] = build_run_summary(trace)
    return trace


if __name__ == "__main__":
    trace = build_sample_trace()
    Path("examples").mkdir(exist_ok=True)
    Path("examples/trace-example.json").write_text(json.dumps(trace, indent=2) + "\n")
    print("wrote examples/trace-example.json")
