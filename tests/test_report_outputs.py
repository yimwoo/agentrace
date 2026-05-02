from pathlib import Path
import json
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
    assert payload["run_summary"]["result"] == "success"


def test_build_markdown_summary():
    text = build_markdown_summary(TRACE)
    assert "Trace Summary: debug sample" in text
    assert "event_count: 1" in text


def test_json_and_markdown_stay_consistent():
    payload = build_json_summary(TRACE)
    text = build_markdown_summary(TRACE)
    assert str(payload["summary"]["ok_events"]) in text
    assert payload["run_id"] in text


def test_build_sample_trace_shape():
    trace = build_sample_trace()
    assert trace["trace_version"] == "0.1"
    assert trace["run"]["id"] == "sample-1"
    assert trace["run"]["status"] == "success"
    assert trace["events"][0]["tool"]["args"]["query"] == "agent trace"
    assert trace["summary"]["event_counts"] == {"tool_call": 1}


def test_new_trace_shape_preserves_report_compatibility():
    payload = build_json_summary(build_sample_trace())
    assert payload["task"] == "debug sample"
    assert payload["run_id"] == "sample-1"
    assert payload["status"] == "success"
    assert payload["timing"] == {"wall_clock_ms": 12}


def test_report_includes_command_timing_and_edit_summary():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "run-commands", "task": "inspect commands", "status": "failed", "started_at": "2026-04-25T00:00:00Z", "duration_ms": 3700},
        "events": [
            {
                "id": "evt_cmd",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:01Z",
                "duration_ms": 3200,
                "command": {"value": "pytest tests/test_auth.py -q", "cwd": "/workspace/app"},
                "exit_code": 1,
                "stderr_preview": "AssertionError: expected 401 but got 500",
            },
            {
                "id": "evt_edit",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:05Z",
                "duration_ms": 500,
                "file": {"path": "src/auth.py"},
                "change": {"kind": "modify", "added_lines": 4, "removed_lines": 1, "summary": "Translate decoder errors into 401 responses"},
            },
        ],
    }
    payload = build_json_summary(trace)
    assert payload["command_timing"] == [{
        "event": "evt_cmd",
        "command": "pytest tests/test_auth.py -q",
        "cwd": "/workspace/app",
        "status": "failed",
        "duration_ms": 3200,
        "exit_code": 1,
        "started_at": "2026-04-25T00:00:01Z",
    }]
    assert payload["edit_summary"] == [{
        "event": "evt_edit",
        "path": "src/auth.py",
        "kind": "modify",
        "status": "succeeded",
        "duration_ms": 500,
        "added_lines": 4,
        "removed_lines": 1,
        "summary": "Translate decoder errors into 401 responses",
        "started_at": "2026-04-25T00:00:05Z",
    }]
    assert payload["run_summary"]["command_durations_ms"][0]["duration_ms"] == 3200
    assert payload["run_summary"]["edit_summaries"][0]["summary"] == "Translate decoder errors into 401 responses"


def test_markdown_report_renders_command_timing_and_edit_summary():
    trace = {
        "task": "legacy edit trace",
        "run_id": "legacy-1",
        "events": [
            {"timestamp": "2026-04-25T00:00:00Z", "type": "command", "name": "pytest -q", "status": "ok", "details": {"exit_code": 0}, "duration_ms": 9},
            {"timestamp": "2026-04-25T00:00:01Z", "type": "file_edit", "name": "src/report.py", "status": "ok", "details": {"kind": "modify", "added_lines": 2, "removed_lines": 0, "summary": "Add timing section"}, "duration_ms": 1},
        ],
        "result_summary": {"status": "success"},
        "timing": {"wall_clock_ms": 10},
    }
    text = build_markdown_summary(trace)
    assert "## Command Timing" in text
    assert "`pytest -q` — 9ms, status=ok, exit_code=0" in text
    assert "## Edit Summary" in text
    assert "src/report.py: modify (+2/-0) — Add timing section" in text


def test_markdown_report_matches_rich_trace_fixture():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "rich-1", "task": "investigate auth failure", "status": "failed", "duration_ms": 3325},
        "events": [
            {
                "id": "evt_cmd_1",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:04.200Z",
                "duration_ms": 3200,
                "command": {"value": "pytest tests/test_auth.py -q", "cwd": "/workspace/app"},
                "exit_code": 1,
            },
            {
                "id": "evt_edit_1",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:05Z",
                "ended_at": "2026-04-25T00:00:05.125Z",
                "duration_ms": 125,
                "file": {"path": "src/auth.py"},
                "change": {"kind": "modify", "added_lines": 4, "removed_lines": 1, "summary": "Translate decoder errors into 401 responses"},
            },
            {
                "id": "evt_test_1",
                "seq": 3,
                "type": "test_result",
                "status": "failed",
                "started_at": "2026-04-25T00:00:06Z",
                "duration_ms": 0,
                "test": {"command_event": "evt_cmd_1", "failed": 1},
            },
        ],
    }
    expected = Path("tests/fixtures/rich-report.md").read_text()
    assert build_markdown_summary(trace) == expected


def test_reports_include_artifact_refs_for_commands_and_edits():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "artifact-1", "task": "inspect artifacts", "status": "failed", "duration_ms": 52},
        "events": [
            {
                "id": "evt_cmd_log",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:01Z",
                "duration_ms": 50,
                "command": {"value": "pytest -q", "cwd": "/workspace/app"},
                "exit_code": 1,
            },
            {
                "id": "evt_diff",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:02Z",
                "duration_ms": 2,
                "file": {"path": "src/report.py"},
                "change": {"kind": "modify", "added_lines": 3, "removed_lines": 1, "summary": "Surface linked artifacts"},
            },
        ],
        "artifacts": [
            {"kind": "command_log", "path": "artifacts/evt_cmd_log.log", "event_id": "evt_cmd_log"},
            {"kind": "diff", "path": "artifacts/evt_diff.diff", "event_id": "evt_diff"},
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing"][0]["artifacts"] == [
        {"kind": "command_log", "path": "artifacts/evt_cmd_log.log"}
    ]
    assert payload["edit_summary"][0]["artifacts"] == [
        {"kind": "diff", "path": "artifacts/evt_diff.diff"}
    ]

    text = build_markdown_summary(trace)
    assert "artifacts: command_log=artifacts/evt_cmd_log.log" in text
    assert "artifacts: diff=artifacts/evt_diff.diff" in text


def test_report_outputs_fall_back_to_existing_run_summary_rows():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "summary-only", "task": "inspect summarized run", "status": "failed", "duration_ms": 60},
        "events": [],
        "summary": {
            "result": "failed",
            "event_counts": {"command": 1, "file_edit": 1},
            "files_changed": ["src/report.py"],
            "commands_run": ["pytest -q"],
            "command_durations_ms": [{
                "event": "evt_cmd",
                "command": "pytest -q",
                "duration_ms": 50,
                "status": "failed",
                "exit_code": 1,
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:01.050Z",
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd.log"}],
            }],
            "edit_summaries": [{
                "event": "evt_edit",
                "path": "src/report.py",
                "kind": "modify",
                "status": "succeeded",
                "duration_ms": 10,
                "added_lines": 1,
                "removed_lines": 0,
                "summary": "Document existing summary rows",
                "started_at": "2026-04-25T00:00:02Z",
                "ended_at": "2026-04-25T00:00:02.010Z",
                "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit.diff"}],
            }],
            "next_inspection_targets": [],
        },
    }

    payload = build_json_summary(trace)
    assert payload["command_timing"] == trace["summary"]["command_durations_ms"]
    assert payload["edit_summary"] == trace["summary"]["edit_summaries"]

    text = build_markdown_summary(trace)
    assert "evt_cmd: `pytest -q` — 50ms, status=failed, exit_code=1" in text
    assert "started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.050Z" in text
    assert "artifacts: command_log=artifacts/evt_cmd.log" in text
    assert "src/report.py: modify (+1/-0) — Document existing summary rows" in text
    assert "artifacts: diff=artifacts/evt_edit.diff" in text


def test_report_outputs_derive_duration_from_time_windows():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "window-1", "task": "derive durations", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_window",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:00.333Z",
                "command": {"value": "python -m pytest"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_window",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:01.012Z",
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Derive report timing"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing"][0]["duration_ms"] == 333
    assert payload["edit_summary"][0]["duration_ms"] == 12

    text = build_markdown_summary(trace)
    assert "`python -m pytest` — 333ms" in text
    assert "src/report_json.py: modify (+2/-1) — Derive report timing, status=succeeded, duration_ms=12" in text


def test_example_write(tmp_path):
    out = tmp_path / "trace-example.json"
    out.write_text(json.dumps(build_sample_trace(), indent=2) + "\n")
    payload = json.loads(out.read_text())
    assert payload["trace_version"] == "0.1"


def test_script_main_writes_example(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    runpy.run_module("src.emit_example_trace", run_name="__main__")
    out = tmp_path / "examples" / "trace-example.json"
    assert out.exists()
    payload = json.loads(out.read_text())
    assert payload["events"][0]["tool"]["args"]["query"] == "agent trace"
