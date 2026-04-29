from pathlib import Path
import runpy

from src.emit_example_trace import build_sample_trace
from src.report_json import build_json_summary
from src.report_markdown import build_markdown_summary

TRACE = {
    "task": "debug sample",
    "run_id": "sample-1",
    "events": [{"timestamp": "2026-04-25T00:00:00Z", "type": "tool_call", "name": "search", "status": "ok", "details": {}, "duration_ms": 3}],
    "result_summary": {"status": "success"},
    "timing": {"wall_clock_ms": 3},
}


def test_build_json_summary():
    payload = build_json_summary(TRACE)
    assert payload["summary"]["event_count"] == 1
    assert payload["status"] == "success"
    assert payload["run_summary"]["event_counts"] == {"tool_call": 1}


def test_build_markdown_summary():
    text = build_markdown_summary(TRACE)
    assert "Trace Summary: debug sample" in text
    assert "event_count: 1" in text
    assert "event_counts: tool_call: 1" in text
    assert "next_inspection_targets: none" in text


def test_json_and_markdown_stay_consistent():
    payload = build_json_summary(TRACE)
    text = build_markdown_summary(TRACE)
    assert str(payload["summary"]["ok_events"]) in text
    assert payload["run_id"] in text


def test_build_sample_trace_shape():
    trace = build_sample_trace()
    assert trace["task"] == "debug sample"
    assert trace["result_summary"]["status"] == "success"
    assert trace["events"][0]["details"]["query"] == "agent trace"


def test_example_write(tmp_path):
    examples = tmp_path / "examples"
    examples.mkdir()
    out = examples / "trace-example.json"
    out.write_text(__import__("json").dumps(build_sample_trace(), indent=2) + "\n")
    assert out.exists()
    assert "sample-1" in out.read_text()


def test_script_main_writes_example(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    runpy.run_module("src.emit_example_trace", run_name="__main__")
    out = tmp_path / "examples" / "trace-example.json"
    assert out.exists()
    assert "agent trace" in out.read_text()
