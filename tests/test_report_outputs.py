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
                "stdout_preview": "F",
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
        "duration_source": "explicit",
        "exit_code": 1,
        "started_at": "2026-04-25T00:00:01Z",
        "stdout_preview": "F",
        "stderr_preview": "AssertionError: expected 401 but got 500",
    }]
    assert payload["edit_summary"] == [{
        "event": "evt_edit",
        "path": "src/auth.py",
        "kind": "modify",
        "status": "succeeded",
        "duration_ms": 500,
        "duration_source": "explicit",
        "added_lines": 4,
        "removed_lines": 1,
        "summary": "Translate decoder errors into 401 responses",
        "net_line_delta": 3,
        "started_at": "2026-04-25T00:00:05Z",
    }]
    assert payload["run_summary"]["command_durations_ms"][0]["duration_ms"] == 3200
    assert payload["command_timing_summary"]["failed_commands"] == [{
        "event": "evt_cmd",
        "command": "pytest tests/test_auth.py -q",
        "duration_ms": 3200,
        "duration_source": "explicit",
        "status": "failed",
        "exit_code": 1,
        "started_at": "2026-04-25T00:00:01Z",
        "ended_at": None,
        "stdout_preview": "F",
        "stderr_preview": "AssertionError: expected 401 but got 500",
    }]
    assert payload["run_summary"]["edit_summaries"][0]["summary"] == "Translate decoder errors into 401 responses"
    assert payload["run_summary"]["edit_summaries"][0]["net_line_delta"] == 3


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
    assert "`pytest -q` — 9ms, status=ok, exit_code=0, duration_source=explicit" in text
    assert "## Edit Summary" in text
    assert "src/report.py: modify (+2/-0, net=2) — Add timing section, status=ok, duration_ms=1, duration_source=explicit" in text


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


def test_failed_command_and_edit_aggregates_preserve_artifact_refs():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "failed-artifacts-1", "task": "inspect failed artifacts", "status": "failed"},
        "events": [
            {
                "id": "evt_cmd_failed_log",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "duration_ms": 80,
                "command": {"value": "pytest -q"},
                "exit_code": 1,
                "stderr_preview": "AssertionError: expected 401",
            },
            {
                "id": "evt_edit_failed_diff",
                "seq": 2,
                "type": "file_edit",
                "status": "failed",
                "duration_ms": 5,
                "file": {"path": "src/auth.py"},
                "change": {"kind": "modify", "added_lines": 0, "removed_lines": 0, "summary": "Patch auth handling"},
                "error": {"message": "target hunk not found"},
            },
        ],
        "artifacts": [
            {"kind": "command_log", "path": "artifacts/evt_cmd_failed_log.log", "event_id": "evt_cmd_failed_log"},
            {"kind": "diff", "path": "artifacts/evt_edit_failed_diff.diff", "event_id": "evt_edit_failed_diff"},
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"]["failed_commands"][0]["artifacts"] == [
        {"kind": "command_log", "path": "artifacts/evt_cmd_failed_log.log"}
    ]
    assert payload["edit_summary_totals"]["failed_edits"][0]["artifacts"] == [
        {"kind": "diff", "path": "artifacts/evt_edit_failed_diff.diff"}
    ]

    text = build_markdown_summary(trace)
    assert "failed_commands: evt_cmd_failed_log: `pytest -q` (80ms, status=failed, exit_code=1, duration_source=explicit, stderr_preview=AssertionError: expected 401, artifacts=command_log=artifacts/evt_cmd_failed_log.log)" in text
    assert "failed_edits: evt_edit_failed_diff: src/auth.py (kind=modify, +0/-0, net=0, 5ms, status=failed, duration_source=explicit, summary=Patch auth handling, error_message=target hunk not found, artifacts=diff=artifacts/evt_edit_failed_diff.diff)" in text


def test_slowest_command_and_largest_edit_preserve_artifact_refs():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "selected-artifacts-1", "task": "inspect selected artifacts", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_fast",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 5,
                "command": {"value": "ruff check"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_slowest_log",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 75,
                "command": {"value": "pytest -q"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_small",
                "seq": 3,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 2,
                "file": {"path": "src/small.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0, "summary": "Small edit"},
            },
            {
                "id": "evt_edit_largest_diff",
                "seq": 4,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 3,
                "file": {"path": "src/large.py"},
                "change": {"kind": "modify", "added_lines": 5, "removed_lines": 2, "summary": "Large edit"},
            },
        ],
        "artifacts": [
            {"kind": "command_log", "path": "artifacts/evt_cmd_slowest_log.log", "event_id": "evt_cmd_slowest_log"},
            {"kind": "diff", "path": "artifacts/evt_edit_largest_diff.diff", "event_id": "evt_edit_largest_diff"},
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"]["slowest"]["artifacts"] == [
        {"kind": "command_log", "path": "artifacts/evt_cmd_slowest_log.log"}
    ]
    assert payload["edit_summary_totals"]["largest_edit"]["artifacts"] == [
        {"kind": "diff", "path": "artifacts/evt_edit_largest_diff.diff"}
    ]

    text = build_markdown_summary(trace)
    assert "slowest_command: evt_cmd_slowest_log: `pytest -q` (75ms, status=succeeded, exit_code=0, duration_source=explicit, artifacts=command_log=artifacts/evt_cmd_slowest_log.log)" in text
    assert "largest_edit: evt_edit_largest_diff: src/large.py (+5/-2, net=3, duration_ms=3, status=succeeded, duration_source=explicit, artifacts=diff=artifacts/evt_edit_largest_diff.diff)" in text


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
                "net_line_delta": 1,
                "summary": "Document existing summary rows",
                "started_at": "2026-04-25T00:00:02Z",
                "ended_at": "2026-04-25T00:00:02.010Z",
                "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit.diff"}],
            }],
            "next_inspection_targets": [],
        },
    }

    payload = build_json_summary(trace)
    assert payload["command_timing"] == [{
        **trace["summary"]["command_durations_ms"][0],
        "duration_source": "explicit",
    }]
    assert payload["edit_summary"] == [{
        **trace["summary"]["edit_summaries"][0],
        "duration_source": "explicit",
    }]

    text = build_markdown_summary(trace)
    assert "evt_cmd: `pytest -q` — 50ms, status=failed, exit_code=1" in text
    assert "duration_source=explicit" in text
    assert "started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.050Z" in text
    assert "artifacts: command_log=artifacts/evt_cmd.log" in text
    assert "src/report.py: modify (+1/-0, net=1) — Document existing summary rows" in text
    assert "artifacts: diff=artifacts/evt_edit.diff" in text


def test_report_outputs_normalize_summary_only_timing_and_edit_fields():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "summary-window", "task": "inspect summary timing", "status": "succeeded"},
        "events": [],
        "summary": {
            "result": "succeeded",
            "event_counts": {"command": 1, "file_edit": 1},
            "files_changed": ["src/report_json.py"],
            "commands_run": ["pytest -q"],
            "command_durations_ms": [{
                "event": "evt_cmd_summary_window",
                "command": "pytest -q",
                "status": "succeeded",
                "exit_code": 0,
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:00.250Z",
            }],
            "edit_summaries": [{
                "event": "evt_edit_summary_window",
                "path": "src/report_json.py",
                "kind": "modify",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:01.010Z",
                "added_lines": 3,
                "removed_lines": 1,
                "summary": "Normalize summary-only rows",
            }],
            "next_inspection_targets": [],
        },
    }

    payload = build_json_summary(trace)
    assert payload["command_timing"][0]["duration_ms"] == 250
    assert payload["command_timing"][0]["duration_source"] == "derived"
    assert payload["edit_summary"][0]["duration_ms"] == 10
    assert payload["edit_summary"][0]["duration_source"] == "derived"
    assert payload["edit_summary"][0]["net_line_delta"] == 2
    assert payload["command_timing_summary"]["total_duration_ms"] == 250
    assert payload["edit_summary_totals"]["total_duration_ms"] == 10
    assert payload["edit_summary_totals"]["net_line_delta"] == 2

    text = build_markdown_summary(trace)
    assert "evt_cmd_summary_window: `pytest -q` — 250ms, status=succeeded, exit_code=0, duration_source=derived" in text
    assert "src/report_json.py: modify (+3/-1, net=2) — Normalize summary-only rows, status=succeeded, duration_ms=10, duration_source=derived" in text


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
    assert payload["summary"]["total_duration_ms"] == 345

    text = build_markdown_summary(trace)
    assert "total_duration_ms: 345" in text
    assert "`python -m pytest` — 333ms, status=succeeded, exit_code=0, duration_source=derived" in text
    assert "src/report_json.py: modify (+2/-1, net=1) — Derive report timing, status=succeeded, duration_ms=12, duration_source=derived" in text


def test_reports_include_aggregate_command_and_edit_totals():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "aggregate-1", "task": "review report totals", "status": "failed"},
        "events": [
            {
                "id": "evt_cmd_slow",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:02Z",
                "command": {"value": "pytest -q"},
                "exit_code": 1,
            },
            {
                "id": "evt_cmd_fast",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:03Z",
                "duration_ms": 125,
                "command": {"value": "ruff check"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_one",
                "seq": 3,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:04Z",
                "duration_ms": 12,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 8, "removed_lines": 2, "summary": "Add report totals"},
            },
            {
                "id": "evt_edit_two",
                "seq": 4,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:05Z",
                "duration_ms": 8,
                "file": {"path": "src/report_markdown.py"},
                "change": {"kind": "modify", "added_lines": 3, "removed_lines": 1, "summary": "Render report totals"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"] == {
        "count": 2,
        "unique_command_count": 2,
        "commands_run": ["pytest -q", "ruff check"],
        "repeated_commands": {},
        "command_attempts": [
            {
                "command": "pytest -q",
                "count": 1,
                "total_duration_ms": 2000,
                "average_duration_ms": 2000.0,
                "failed_count": 1,
                "status_counts": {"failed": 1},
                "duration_source_counts": {"derived": 1},
                "time_window": {"started_at": "2026-04-25T00:00:00Z", "ended_at": "2026-04-25T00:00:02Z"},
                "first_event": "evt_cmd_slow",
                "last_event": "evt_cmd_slow",
            },
            {
                "command": "ruff check",
                "count": 1,
                "total_duration_ms": 125,
                "average_duration_ms": 125.0,
                "failed_count": 0,
                "status_counts": {"succeeded": 1},
                "duration_source_counts": {"explicit": 1},
                "time_window": {"started_at": "2026-04-25T00:00:03Z", "ended_at": None},
                "first_event": "evt_cmd_fast",
                "last_event": "evt_cmd_fast",
            },
        ],
        "cwd_counts": {"unknown": 2},
        "cwd_totals": [{
            "cwd": "unknown",
            "count": 2,
            "commands_run": ["pytest -q", "ruff check"],
            "failed_count": 1,
            "total_duration_ms": 2125,
            "average_duration_ms": 1062.5,
            "status_counts": {"failed": 1, "succeeded": 1},
            "duration_source_counts": {"derived": 1, "explicit": 1},
            "time_window": {"started_at": "2026-04-25T00:00:00Z", "ended_at": "2026-04-25T00:00:02Z"},
            "first_event": "evt_cmd_slow",
            "last_event": "evt_cmd_fast",
        }],
        "total_duration_ms": 2125,
        "average_duration_ms": 1062.5,
        "median_duration_ms": 1062.5,
        "failed_count": 1,
        "failed_commands": [{
            "event": "evt_cmd_slow",
            "command": "pytest -q",
            "duration_ms": 2000,
            "duration_source": "derived",
            "status": "failed",
            "exit_code": 1,
            "started_at": "2026-04-25T00:00:00Z",
            "ended_at": "2026-04-25T00:00:02Z",
        }],
        "exit_code_counts": {"1": 1, "0": 1},
        "status_counts": {"failed": 1, "succeeded": 1},
        "duration_source_counts": {"derived": 1, "explicit": 1},
        "time_window": {"started_at": "2026-04-25T00:00:00Z", "ended_at": "2026-04-25T00:00:02Z"},
        "first": {
            "event": "evt_cmd_slow",
            "command": "pytest -q",
            "duration_ms": 2000,
            "duration_source": "derived",
            "status": "failed",
            "exit_code": 1,
            "started_at": "2026-04-25T00:00:00Z",
            "ended_at": "2026-04-25T00:00:02Z",
        },
        "slowest": {
            "event": "evt_cmd_slow",
            "command": "pytest -q",
            "duration_ms": 2000,
            "duration_source": "derived",
            "status": "failed",
            "exit_code": 1,
            "started_at": "2026-04-25T00:00:00Z",
            "ended_at": "2026-04-25T00:00:02Z",
        },
        "fastest": {
            "event": "evt_cmd_fast",
            "command": "ruff check",
            "duration_ms": 125,
            "duration_source": "explicit",
            "status": "succeeded",
            "exit_code": 0,
            "started_at": "2026-04-25T00:00:03Z",
            "ended_at": None,
        },
        "last": {
            "event": "evt_cmd_fast",
            "command": "ruff check",
            "duration_ms": 125,
            "duration_source": "explicit",
            "status": "succeeded",
            "exit_code": 0,
            "started_at": "2026-04-25T00:00:03Z",
            "ended_at": None,
        },
    }
    assert payload["edit_summary_totals"] == {
        "count": 2,
        "files_changed": ["src/report_json.py", "src/report_markdown.py"],
        "files_changed_count": 2,
        "file_change_totals": [
            {
                "path": "src/report_json.py",
                "count": 1,
                "failed_count": 0,
                "total_added_lines": 8,
                "total_removed_lines": 2,
                "net_line_delta": 6,
                "total_duration_ms": 12,
                "average_duration_ms": 12.0,
                "status_counts": {"succeeded": 1},
                "kind_counts": {"modify": 1},
                "duration_source_counts": {"explicit": 1},
                "time_window": {"started_at": "2026-04-25T00:00:04Z", "ended_at": None},
            },
            {
                "path": "src/report_markdown.py",
                "count": 1,
                "failed_count": 0,
                "total_added_lines": 3,
                "total_removed_lines": 1,
                "net_line_delta": 2,
                "total_duration_ms": 8,
                "average_duration_ms": 8.0,
                "status_counts": {"succeeded": 1},
                "kind_counts": {"modify": 1},
                "duration_source_counts": {"explicit": 1},
                "time_window": {"started_at": "2026-04-25T00:00:05Z", "ended_at": None},
            },
        ],
        "failed_count": 0,
        "failed_edits": [],
        "kind_counts": {"modify": 2},
        "kind_totals": [{
            "kind": "modify",
            "count": 2,
            "files_changed": ["src/report_json.py", "src/report_markdown.py"],
            "failed_count": 0,
            "total_added_lines": 11,
            "total_removed_lines": 3,
            "net_line_delta": 8,
            "total_duration_ms": 20,
            "average_duration_ms": 10.0,
            "status_counts": {"succeeded": 2},
            "duration_source_counts": {"explicit": 2},
            "time_window": {"started_at": "2026-04-25T00:00:04Z", "ended_at": None},
            "first_event": "evt_edit_one",
            "last_event": "evt_edit_two",
        }],
        "status_counts": {"succeeded": 2},
        "duration_source_counts": {"explicit": 2},
        "time_window": {"started_at": "2026-04-25T00:00:04Z", "ended_at": None},
        "total_added_lines": 11,
        "total_removed_lines": 3,
        "net_line_delta": 8,
        "total_duration_ms": 20,
        "average_duration_ms": 10.0,
        "median_duration_ms": 10.0,
        "first_edit": {
            "event": "evt_edit_one",
            "path": "src/report_json.py",
            "kind": "modify",
            "added_lines": 8,
            "removed_lines": 2,
            "net_line_delta": 6,
            "duration_ms": 12,
            "duration_source": "explicit",
            "status": "succeeded",
            "started_at": "2026-04-25T00:00:04Z",
            "ended_at": None,
        },
        "largest_edit": {
            "event": "evt_edit_one",
            "path": "src/report_json.py",
            "kind": "modify",
            "added_lines": 8,
            "removed_lines": 2,
            "net_line_delta": 6,
            "duration_ms": 12,
            "duration_source": "explicit",
            "status": "succeeded",
            "started_at": "2026-04-25T00:00:04Z",
            "ended_at": None,
        },
        "shortest_edit": {
            "event": "evt_edit_two",
            "path": "src/report_markdown.py",
            "kind": "modify",
            "added_lines": 3,
            "removed_lines": 1,
            "net_line_delta": 2,
            "duration_ms": 8,
            "duration_source": "explicit",
            "status": "succeeded",
            "started_at": "2026-04-25T00:00:05Z",
            "ended_at": None,
        },
        "last_edit": {
            "event": "evt_edit_two",
            "path": "src/report_markdown.py",
            "kind": "modify",
            "added_lines": 3,
            "removed_lines": 1,
            "net_line_delta": 2,
            "duration_ms": 8,
            "duration_source": "explicit",
            "status": "succeeded",
            "started_at": "2026-04-25T00:00:05Z",
            "ended_at": None,
        },
    }

    text = build_markdown_summary(trace)
    assert "command_count: 2" in text
    assert "unique_command_count: 2" in text
    assert "commands_run: pytest -q, ruff check" in text
    assert "repeated_commands: none" in text
    assert "command_attempts: `pytest -q` (count=1, total_duration_ms=2000, average_duration_ms=2000.0, failed_count=1, statuses=failed=1, duration_sources=derived=1, time_window=started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z, first_event=evt_cmd_slow, last_event=evt_cmd_slow); `ruff check` (count=1, total_duration_ms=125, average_duration_ms=125.0, failed_count=0, statuses=succeeded=1, duration_sources=explicit=1, time_window=started_at=2026-04-25T00:00:03Z, first_event=evt_cmd_fast, last_event=evt_cmd_fast)" in text
    assert "command_cwd_counts: unknown=2" in text
    assert "command_cwd_totals: unknown (count=2, commands=pytest -q, ruff check, failed_count=1, total_duration_ms=2125, average_duration_ms=1062.5, statuses=failed=1, succeeded=1, duration_sources=derived=1, explicit=1, time_window=started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z, first_event=evt_cmd_slow, last_event=evt_cmd_fast)" in text
    assert "command_total_duration_ms: 2125" in text
    assert "command_average_duration_ms: 1062.5" in text
    assert "command_median_duration_ms: 1062.5" in text
    assert "command_failed_count: 1" in text
    assert "failed_commands: evt_cmd_slow: `pytest -q` (2000ms, status=failed, exit_code=1, duration_source=derived, started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z)" in text
    assert "command_exit_code_counts: 0=1, 1=1" in text
    assert "command_status_counts: failed=1, succeeded=1" in text
    assert "command_duration_sources: derived=1, explicit=1" in text
    assert "command_time_window: started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z" in text
    assert "first_command: evt_cmd_slow: `pytest -q` (2000ms, status=failed, exit_code=1, duration_source=derived, started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z)" in text
    assert "slowest_command: evt_cmd_slow: `pytest -q` (2000ms, status=failed, exit_code=1, duration_source=derived, started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z)" in text
    assert "fastest_command: evt_cmd_fast: `ruff check` (125ms, status=succeeded, exit_code=0, duration_source=explicit, started_at=2026-04-25T00:00:03Z)" in text
    assert "last_command: evt_cmd_fast: `ruff check` (125ms, status=succeeded, exit_code=0, duration_source=explicit, started_at=2026-04-25T00:00:03Z)" in text
    assert "files_changed_count: 2" in text
    assert "files_changed: src/report_json.py, src/report_markdown.py" in text
    assert "file_change_totals: src/report_json.py (count=1, failed_count=0, +8/-2, net=6, total_duration_ms=12, average_duration_ms=12.0, statuses=succeeded=1, kinds=modify=1, duration_sources=explicit=1, time_window=started_at=2026-04-25T00:00:04Z); src/report_markdown.py (count=1, failed_count=0, +3/-1, net=2, total_duration_ms=8, average_duration_ms=8.0, statuses=succeeded=1, kinds=modify=1, duration_sources=explicit=1, time_window=started_at=2026-04-25T00:00:05Z)" in text
    assert "edit_failed_count: 0" in text
    assert "failed_edits: none" in text
    assert "edit_kind_counts: modify=2" in text
    assert "edit_kind_totals: modify (count=2, files=src/report_json.py, src/report_markdown.py, failed_count=0, +11/-3, net=8, total_duration_ms=20, average_duration_ms=10.0, statuses=succeeded=2, duration_sources=explicit=2, time_window=started_at=2026-04-25T00:00:04Z, first_event=evt_edit_one, last_event=evt_edit_two)" in text
    assert "edit_status_counts: succeeded=2" in text
    assert "edit_duration_sources: explicit=2" in text
    assert "edit_time_window: started_at=2026-04-25T00:00:04Z" in text
    assert "edit_total_lines: +11/-3" in text
    assert "edit_net_line_delta: 8" in text
    assert "edit_total_duration_ms: 20" in text
    assert "edit_average_duration_ms: 10.0" in text
    assert "edit_median_duration_ms: 10.0" in text
    assert "first_edit: evt_edit_one: src/report_json.py (+8/-2, net=6, duration_ms=12, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:04Z)" in text
    assert "largest_edit: evt_edit_one: src/report_json.py (+8/-2, net=6, duration_ms=12, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:04Z)" in text
    assert "shortest_edit: evt_edit_two: src/report_markdown.py (+3/-1, net=2, duration_ms=8, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:05Z)" in text
    assert "last_edit: evt_edit_two: src/report_markdown.py (+3/-1, net=2, duration_ms=8, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:05Z)" in text


def test_report_aggregate_time_windows_use_full_row_ranges():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "aggregate-window-1", "task": "inspect aggregate windows", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_late",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:05+00:00",
                "ended_at": "2026-04-25T00:00:06+00:00",
                "command": {"value": "ruff check"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_early",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:02Z",
                "command": {"value": "pytest -q"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_mid",
                "seq": 3,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:03Z",
                "ended_at": "2026-04-25T00:00:04Z",
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Expose aggregate windows"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"]["time_window"] == {
        "started_at": "2026-04-25T00:00:01Z",
        "ended_at": "2026-04-25T00:00:06+00:00",
    }
    assert payload["edit_summary_totals"]["time_window"] == {
        "started_at": "2026-04-25T00:00:03Z",
        "ended_at": "2026-04-25T00:00:04Z",
    }

    text = build_markdown_summary(trace)
    assert "command_time_window: started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:06+00:00" in text
    assert "edit_time_window: started_at=2026-04-25T00:00:03Z, ended_at=2026-04-25T00:00:04Z" in text


def test_report_totals_include_command_cwd_and_edit_kind_distributions():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "distribution-1", "task": "inspect distributions", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_src",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 10,
                "command": {"value": "pytest -q", "cwd": "/workspace/app"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_docs",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 5,
                "command": {"value": "mkdocs build", "cwd": "/workspace/app/docs"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_unknown_cwd",
                "seq": 3,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 2,
                "command": {"value": "ruff check"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_modify",
                "seq": 4,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 3,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Update report totals"},
            },
            {
                "id": "evt_edit_create",
                "seq": 5,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 4,
                "file": {"path": "docs/report.md"},
                "change": {"kind": "create", "added_lines": 8, "removed_lines": 0, "summary": "Document report totals"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"]["cwd_counts"] == {
        "/workspace/app": 1,
        "/workspace/app/docs": 1,
        "unknown": 1,
    }
    assert payload["edit_summary_totals"]["kind_counts"] == {"modify": 1, "create": 1}

    text = build_markdown_summary(trace)
    assert "command_cwd_counts: /workspace/app=1, /workspace/app/docs=1, unknown=1" in text
    assert "edit_kind_counts: create=1, modify=1" in text


def test_report_totals_deduplicate_files_and_show_repeated_commands():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "repeat-1", "task": "inspect repeated work", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_first",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "duration_ms": 20,
                "command": {"value": "pytest -q"},
                "exit_code": 1,
            },
            {
                "id": "evt_cmd_retry",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 30,
                "command": {"value": "pytest -q"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_lint",
                "seq": 3,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 5,
                "command": {"value": "ruff check"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_first",
                "seq": 4,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 7,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0, "summary": "First change"},
            },
            {
                "id": "evt_edit_second",
                "seq": 5,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 8,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Second change"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"]["count"] == 3
    assert payload["command_timing_summary"]["unique_command_count"] == 2
    assert payload["command_timing_summary"]["commands_run"] == ["pytest -q", "ruff check"]
    assert payload["command_timing_summary"]["repeated_commands"] == {"pytest -q": 2}
    assert payload["command_timing_summary"]["command_attempts"][0] == {
        "command": "pytest -q",
        "count": 2,
        "total_duration_ms": 50,
        "average_duration_ms": 25.0,
        "failed_count": 1,
        "status_counts": {"failed": 1, "succeeded": 1},
        "duration_source_counts": {"explicit": 2},
        "time_window": None,
        "first_event": "evt_cmd_first",
        "last_event": "evt_cmd_retry",
    }
    assert payload["command_timing_summary"]["failed_commands"] == [{
        "event": "evt_cmd_first",
        "command": "pytest -q",
        "duration_ms": 20,
        "duration_source": "explicit",
        "status": "failed",
        "exit_code": 1,
        "started_at": None,
        "ended_at": None,
    }]
    assert payload["edit_summary_totals"]["files_changed"] == ["src/report_json.py"]
    assert payload["edit_summary_totals"]["files_changed_count"] == 1
    assert payload["edit_summary_totals"]["file_change_totals"] == [{
        "path": "src/report_json.py",
        "count": 2,
        "failed_count": 0,
        "total_added_lines": 3,
        "total_removed_lines": 1,
        "net_line_delta": 2,
        "total_duration_ms": 15,
        "average_duration_ms": 7.5,
        "status_counts": {"succeeded": 2},
        "kind_counts": {"modify": 2},
        "duration_source_counts": {"explicit": 2},
        "time_window": None,
        "first_event": "evt_edit_first",
        "last_event": "evt_edit_second",
    }]

    text = build_markdown_summary(trace)
    assert "unique_command_count: 2" in text
    assert "commands_run: pytest -q, ruff check" in text
    assert "repeated_commands: `pytest -q`=2" in text
    assert "command_attempts: `pytest -q` (count=2, total_duration_ms=50, average_duration_ms=25.0, failed_count=1, statuses=failed=1, succeeded=1, duration_sources=explicit=2, first_event=evt_cmd_first, last_event=evt_cmd_retry); `ruff check` (count=1, total_duration_ms=5, average_duration_ms=5.0, failed_count=0, statuses=succeeded=1, duration_sources=explicit=1, first_event=evt_cmd_lint, last_event=evt_cmd_lint)" in text
    assert "failed_commands: evt_cmd_first: `pytest -q` (20ms, status=failed, exit_code=1, duration_source=explicit)" in text
    assert "files_changed_count: 1" in text
    assert "files_changed: src/report_json.py" in text
    assert "file_change_totals: src/report_json.py (count=2, failed_count=0, +3/-1, net=2, total_duration_ms=15, average_duration_ms=7.5, statuses=succeeded=2, kinds=modify=2, duration_sources=explicit=2, first_event=evt_edit_first, last_event=evt_edit_second)" in text


def test_reports_expose_duration_source_for_timing_rows_and_totals():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "duration-source-1", "task": "inspect duration sources", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_explicit",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:00Z",
                "duration_ms": 10,
                "command": {"value": "pytest -q"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_derived",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:01.025Z",
                "command": {"value": "ruff check"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_missing",
                "seq": 3,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:02Z",
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0, "summary": "Show duration source"},
            },
            {
                "id": "evt_edit_derived",
                "seq": 4,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:03Z",
                "ended_at": "2026-04-25T00:00:03.005Z",
                "file": {"path": "src/report_markdown.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Render duration source"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert [row["duration_source"] for row in payload["command_timing"]] == ["explicit", "derived"]
    assert [row["duration_source"] for row in payload["edit_summary"]] == ["missing", "derived"]
    assert payload["command_timing_summary"]["duration_source_counts"] == {"explicit": 1, "derived": 1}
    assert payload["edit_summary_totals"]["duration_source_counts"] == {"missing": 1, "derived": 1}
    assert payload["summary"]["total_duration_ms"] == 40

    text = build_markdown_summary(trace)
    assert "command_duration_sources: derived=1, explicit=1" in text
    assert "edit_duration_sources: derived=1, missing=1" in text
    assert "evt_cmd_explicit: `pytest -q` — 10ms, status=succeeded, exit_code=0, duration_source=explicit" in text
    assert "evt_cmd_derived: `ruff check` — 25ms, status=succeeded, exit_code=0, duration_source=derived" in text
    assert "evt_edit_missing: edit src/report_json.py (modify, +1/-0, net=1) — Show duration source, status=succeeded, duration_ms=0, duration_source=missing, started_at=2026-04-25T00:00:02Z" in text
    assert "src/report_json.py: modify (+1/-0, net=1) — Show duration source, status=succeeded, duration_ms=0, duration_source=missing" in text
    assert "src/report_markdown.py: modify (+2/-1, net=1) — Render duration source, status=succeeded, duration_ms=5, duration_source=derived" in text


def test_markdown_detail_rows_include_failure_output_and_edit_error_context():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "detail-context-1", "task": "inspect detail context", "status": "failed"},
        "events": [
            {
                "id": "evt_cmd_failed_context",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "duration_ms": 42,
                "command": {"value": "pytest -q"},
                "exit_code": 1,
                "stdout_preview": "F",
                "stderr_preview": "AssertionError: expected 401",
            },
            {
                "id": "evt_edit_failed_context",
                "seq": 2,
                "type": "file_edit",
                "status": "failed",
                "duration_ms": 3,
                "file": {"path": "src/auth.py"},
                "change": {"kind": "modify", "added_lines": 0, "removed_lines": 0, "summary": "Patch auth error handling"},
                "error": {"message": "target hunk not found"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["run_summary"]["command_durations_ms"][0]["stdout_preview"] == "F"
    assert payload["run_summary"]["command_durations_ms"][0]["stderr_preview"] == "AssertionError: expected 401"
    assert payload["run_summary"]["edit_summaries"][0]["error_message"] == "target hunk not found"

    text = build_markdown_summary(trace)
    assert "evt_cmd_failed_context: `pytest -q` — 42ms, status=failed, exit_code=1, duration_source=explicit, stdout_preview=F, stderr_preview=AssertionError: expected 401" in text
    assert "src/auth.py: modify (+0/-0, net=0) — Patch auth error handling, status=failed, duration_ms=3, duration_source=explicit, error_message=target hunk not found" in text


def test_summary_only_markdown_detail_rows_include_preserved_failure_context():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "summary-detail-context-1", "task": "inspect summary detail context", "status": "failed"},
        "events": [],
        "summary": {
            "result": "failed",
            "event_counts": {"command": 1, "file_edit": 1},
            "files_changed": ["src/auth.py"],
            "commands_run": ["pytest -q"],
            "command_durations_ms": [{
                "event": "evt_cmd_summary_context",
                "command": "pytest -q",
                "duration_ms": 42,
                "status": "failed",
                "exit_code": 1,
                "stdout_preview": "F",
                "stderr_preview": "AssertionError: expected 401",
            }],
            "edit_summaries": [{
                "event": "evt_edit_summary_context",
                "path": "src/auth.py",
                "kind": "modify",
                "status": "failed",
                "duration_ms": 3,
                "added_lines": 0,
                "removed_lines": 0,
                "net_line_delta": 0,
                "summary": "Patch auth error handling",
                "error_message": "target hunk not found",
            }],
            "next_inspection_targets": [],
        },
    }

    text = build_markdown_summary(trace)
    assert "evt_cmd_summary_context: `pytest -q` — 42ms, status=failed, exit_code=1, duration_source=explicit, stdout_preview=F, stderr_preview=AssertionError: expected 401" in text
    assert "src/auth.py: modify (+0/-0, net=0) — Patch auth error handling, status=failed, duration_ms=3, duration_source=explicit, error_message=target hunk not found" in text



def test_summary_only_rows_with_partial_fields_are_report_safe():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "summary-partial-1", "task": "inspect partial summary rows", "status": "succeeded"},
        "events": [],
        "summary": {
            "result": "succeeded",
            "event_counts": {"command": 1, "file_edit": 1},
            "files_changed": ["src/report_json.py"],
            "commands_run": ["python -m pytest"],
            "command_durations_ms": [{
                "command": "python -m pytest",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:00.125Z",
            }],
            "edit_summaries": [{
                "path": "src/report_json.py",
                "added_lines": 2,
                "removed_lines": 1,
            }],
            "next_inspection_targets": [],
        },
    }

    payload = build_json_summary(trace)
    assert payload["command_timing"] == [{
        "command": "python -m pytest",
        "started_at": "2026-04-25T00:00:00Z",
        "ended_at": "2026-04-25T00:00:00.125Z",
        "event": "summary",
        "status": None,
        "exit_code": None,
        "duration_source": "derived",
        "duration_ms": 125,
    }]
    assert payload["edit_summary"] == [{
        "path": "src/report_json.py",
        "added_lines": 2,
        "removed_lines": 1,
        "event": "summary",
        "kind": None,
        "status": None,
        "summary": None,
        "duration_source": "missing",
        "duration_ms": 0,
        "net_line_delta": 1,
    }]

    text = build_markdown_summary(trace)
    assert "summary: `python -m pytest` — 125ms, status=None, exit_code=unknown, duration_source=derived" in text
    assert "src/report_json.py: unknown (+2/-1, net=1) — No edit summary recorded., duration_ms=0, duration_source=missing" in text

def test_report_totals_include_failed_edit_details():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "failed-edit-1", "task": "inspect failed edits", "status": "failed"},
        "events": [
            {
                "id": "evt_edit_failed",
                "seq": 1,
                "type": "file_edit",
                "status": "failed",
                "started_at": "2026-04-25T00:00:04Z",
                "ended_at": "2026-04-25T00:00:04.010Z",
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 0, "removed_lines": 0, "summary": "Patch failed to apply"},
                "error": {"message": "target hunk not found"},
            },
            {
                "id": "evt_edit_ok",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 5,
                "file": {"path": "src/report_markdown.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Render failed edits"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["edit_summary"][0]["error_message"] == "target hunk not found"
    assert payload["edit_summary_totals"]["failed_count"] == 1
    assert payload["edit_summary_totals"]["failed_edits"] == [{
        "event": "evt_edit_failed",
        "path": "src/report_json.py",
        "kind": "modify",
        "duration_ms": 10,
        "duration_source": "derived",
        "status": "failed",
        "started_at": "2026-04-25T00:00:04Z",
        "ended_at": "2026-04-25T00:00:04.010Z",
        "added_lines": 0,
        "removed_lines": 0,
        "net_line_delta": 0,
        "summary": "Patch failed to apply",
        "error_message": "target hunk not found",
    }]

    text = build_markdown_summary(trace)
    assert "edit_failed_count: 1" in text
    assert "failed_edits: evt_edit_failed: src/report_json.py (kind=modify, +0/-0, net=0, 10ms, status=failed, duration_source=derived, started_at=2026-04-25T00:00:04Z, ended_at=2026-04-25T00:00:04.010Z, summary=Patch failed to apply, error_message=target hunk not found)" in text


def test_report_totals_include_cwd_and_edit_kind_aggregate_rows():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "nested-distribution-1", "task": "inspect nested distribution totals", "status": "failed"},
        "events": [
            {
                "id": "evt_cmd_src_fail",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:00.010Z",
                "command": {"value": "pytest -q", "cwd": "/workspace/app"},
                "exit_code": 1,
            },
            {
                "id": "evt_cmd_docs_ok",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 5,
                "command": {"value": "mkdocs build", "cwd": "/workspace/app/docs"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_modify",
                "seq": 3,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 7,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 3, "removed_lines": 1, "summary": "Add nested totals"},
            },
            {
                "id": "evt_edit_create_failed",
                "seq": 4,
                "type": "file_edit",
                "status": "failed",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:01.002Z",
                "file": {"path": "docs/report.md"},
                "change": {"kind": "create", "added_lines": 2, "removed_lines": 0, "summary": "Draft report docs"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"]["cwd_totals"] == [
        {
            "cwd": "/workspace/app",
            "count": 1,
            "commands_run": ["pytest -q"],
            "failed_count": 1,
            "total_duration_ms": 10,
            "average_duration_ms": 10.0,
            "status_counts": {"failed": 1},
            "duration_source_counts": {"derived": 1},
            "time_window": {"started_at": "2026-04-25T00:00:00Z", "ended_at": "2026-04-25T00:00:00.010Z"},
        },
        {
            "cwd": "/workspace/app/docs",
            "count": 1,
            "commands_run": ["mkdocs build"],
            "failed_count": 0,
            "total_duration_ms": 5,
            "average_duration_ms": 5.0,
            "status_counts": {"succeeded": 1},
            "duration_source_counts": {"explicit": 1},
            "time_window": None,
        },
    ]
    assert payload["edit_summary_totals"]["kind_totals"] == [
        {
            "kind": "modify",
            "count": 1,
            "files_changed": ["src/report_json.py"],
            "failed_count": 0,
            "total_added_lines": 3,
            "total_removed_lines": 1,
            "net_line_delta": 2,
            "total_duration_ms": 7,
            "average_duration_ms": 7.0,
            "status_counts": {"succeeded": 1},
            "duration_source_counts": {"explicit": 1},
            "time_window": None,
        },
        {
            "kind": "create",
            "count": 1,
            "files_changed": ["docs/report.md"],
            "failed_count": 1,
            "total_added_lines": 2,
            "total_removed_lines": 0,
            "net_line_delta": 2,
            "total_duration_ms": 2,
            "average_duration_ms": 2.0,
            "status_counts": {"failed": 1},
            "duration_source_counts": {"derived": 1},
            "time_window": {"started_at": "2026-04-25T00:00:01Z", "ended_at": "2026-04-25T00:00:01.002Z"},
        },
    ]

    text = build_markdown_summary(trace)
    assert "command_cwd_totals: /workspace/app (count=1, commands=pytest -q, failed_count=1, total_duration_ms=10, average_duration_ms=10.0, statuses=failed=1, duration_sources=derived=1, time_window=started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:00.010Z); /workspace/app/docs (count=1, commands=mkdocs build, failed_count=0, total_duration_ms=5, average_duration_ms=5.0, statuses=succeeded=1, duration_sources=explicit=1)" in text
    assert "edit_kind_totals: modify (count=1, files=src/report_json.py, failed_count=0, +3/-1, net=2, total_duration_ms=7, average_duration_ms=7.0, statuses=succeeded=1, duration_sources=explicit=1); create (count=1, files=docs/report.md, failed_count=1, +2/-0, net=2, total_duration_ms=2, average_duration_ms=2.0, statuses=failed=1, duration_sources=derived=1, time_window=started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.002Z)" in text


def test_activity_timeline_interleaves_command_and_edit_rows_by_timestamp():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "timeline-1", "task": "inspect activity timeline", "status": "failed"},
        "events": [
            {
                "id": "evt_edit_late_diff",
                "seq": 2,
                "type": "file_edit",
                "status": "failed",
                "started_at": "2026-04-25T00:00:03Z",
                "duration_ms": 5,
                "file": {"path": "src/report.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Edit report timeline"},
                "error": {"message": "patch failed"},
            },
            {
                "id": "evt_cmd_early_log",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:01.020Z",
                "command": {"value": "pytest -q", "cwd": "/repo"},
                "exit_code": 1,
                "stderr_preview": "AssertionError: expected 401",
            },
        ],
        "artifacts": [
            {"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff", "event_id": "evt_edit_late_diff"},
            {"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log", "event_id": "evt_cmd_early_log"},
        ],
    }

    payload = build_json_summary(trace)
    assert payload["activity_timeline_summary"] == {
        "count": 2,
        "type_counts": {"command": 1, "file_edit": 1},
        "status_counts": {"failed": 2},
        "duration_source_counts": {"derived": 1, "explicit": 1},
        "time_window": {"started_at": "2026-04-25T00:00:01Z", "ended_at": "2026-04-25T00:00:01.020Z"},
        "span_duration_ms": 20,
        "covered_duration_ms": 25,
        "uncovered_duration_ms": 0,
        "uncovered_intervals": [],
        "coverage_ratio": 1.0,
        "idle_ratio": 0.0,
        "covered_interval_count": 2,
        "total_duration_ms": 25,
        "average_duration_ms": 12.5,
        "median_duration_ms": 12.5,
        "first_activity": {
            "type": "command",
            "event": "evt_cmd_early_log",
            "status": "failed",
            "duration_ms": 20,
            "duration_source": "derived",
            "started_at": "2026-04-25T00:00:01Z",
            "ended_at": "2026-04-25T00:00:01.020Z",
            "command": "pytest -q",
            "cwd": "/repo",
            "exit_code": 1,
            "stderr_preview": "AssertionError: expected 401",
            "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
        },
        "slowest_activity": {
            "type": "command",
            "event": "evt_cmd_early_log",
            "status": "failed",
            "duration_ms": 20,
            "duration_source": "derived",
            "started_at": "2026-04-25T00:00:01Z",
            "ended_at": "2026-04-25T00:00:01.020Z",
            "command": "pytest -q",
            "cwd": "/repo",
            "exit_code": 1,
            "stderr_preview": "AssertionError: expected 401",
            "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
        },
        "fastest_activity": {
            "type": "file_edit",
            "event": "evt_edit_late_diff",
            "status": "failed",
            "duration_ms": 5,
            "duration_source": "explicit",
            "started_at": "2026-04-25T00:00:03Z",
            "ended_at": None,
            "path": "src/report.py",
            "kind": "modify",
            "added_lines": 2,
            "removed_lines": 1,
            "net_line_delta": 1,
            "summary": "Edit report timeline",
            "error_message": "patch failed",
            "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
        },
        "last_activity": {
            "type": "file_edit",
            "event": "evt_edit_late_diff",
            "status": "failed",
            "duration_ms": 5,
            "duration_source": "explicit",
            "started_at": "2026-04-25T00:00:03Z",
            "ended_at": None,
            "path": "src/report.py",
            "kind": "modify",
            "added_lines": 2,
            "removed_lines": 1,
            "net_line_delta": 1,
            "summary": "Edit report timeline",
            "error_message": "patch failed",
            "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
        },
        "inter_activity_gaps": [{
            "from_event": "evt_cmd_early_log",
            "to_event": "evt_edit_late_diff",
            "gap_ms": 1980,
            "from_ended_at": "2026-04-25T00:00:01.020Z",
            "to_started_at": "2026-04-25T00:00:03Z",
        }],
        "total_idle_gap_ms": 1980,
        "largest_idle_gap": {
            "from_event": "evt_cmd_early_log",
            "to_event": "evt_edit_late_diff",
            "gap_ms": 1980,
            "from_ended_at": "2026-04-25T00:00:01.020Z",
            "to_started_at": "2026-04-25T00:00:03Z",
        },
        "inter_activity_overlaps": [],
        "total_overlap_ms": 0,
        "overlap_ratio": 0.0,
        "largest_overlap": None,
        "failed_count": 2,
        "first_failed_activity": {
            "type": "command",
            "event": "evt_cmd_early_log",
            "status": "failed",
            "duration_ms": 20,
            "duration_source": "derived",
            "started_at": "2026-04-25T00:00:01Z",
            "ended_at": "2026-04-25T00:00:01.020Z",
            "command": "pytest -q",
            "cwd": "/repo",
            "exit_code": 1,
            "stderr_preview": "AssertionError: expected 401",
            "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
        },
        "failed_activity": [
            {
                "type": "command",
                "event": "evt_cmd_early_log",
                "status": "failed",
                "duration_ms": 20,
                "duration_source": "derived",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:01.020Z",
                "command": "pytest -q",
                "cwd": "/repo",
                "exit_code": 1,
                "stderr_preview": "AssertionError: expected 401",
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
            },
            {
                "type": "file_edit",
                "event": "evt_edit_late_diff",
                "status": "failed",
                "duration_ms": 5,
                "duration_source": "explicit",
                "started_at": "2026-04-25T00:00:03Z",
                "ended_at": None,
                "path": "src/report.py",
                "kind": "modify",
                "added_lines": 2,
                "removed_lines": 1,
                "net_line_delta": 1,
                "summary": "Edit report timeline",
                "error_message": "patch failed",
                "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
            },
        ],
    }
    assert payload["activity_timeline"] == [
        {
            "type": "command",
            "event": "evt_cmd_early_log",
            "status": "failed",
            "duration_ms": 20,
            "duration_source": "derived",
            "started_at": "2026-04-25T00:00:01Z",
            "ended_at": "2026-04-25T00:00:01.020Z",
            "command": "pytest -q",
            "cwd": "/repo",
            "exit_code": 1,
            "stderr_preview": "AssertionError: expected 401",
            "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
        },
        {
            "type": "file_edit",
            "event": "evt_edit_late_diff",
            "status": "failed",
            "duration_ms": 5,
            "duration_source": "explicit",
            "started_at": "2026-04-25T00:00:03Z",
            "ended_at": None,
            "path": "src/report.py",
            "kind": "modify",
            "added_lines": 2,
            "removed_lines": 1,
            "net_line_delta": 1,
            "summary": "Edit report timeline",
            "error_message": "patch failed",
            "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
        },
    ]

    text = build_markdown_summary(trace)
    assert "activity_timeline_summary: count=2, types=command=1, file_edit=1, statuses=failed=2, duration_sources=derived=1, explicit=1, span_duration_ms=20, covered_duration_ms=25, uncovered_duration_ms=0, uncovered_intervals=none, coverage_ratio=1.0, idle_ratio=0.0, covered_interval_count=2, total_duration_ms=25, average_duration_ms=12.5, median_duration_ms=12.5, first_activity=evt_cmd_early_log: `pytest -q` (type=command, 20ms, status=failed, duration_source=derived, started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.020Z, exit_code=1, cwd=/repo, stderr_preview=AssertionError: expected 401, artifacts=command_log=artifacts/evt_cmd_early_log.log), slowest_activity=evt_cmd_early_log: `pytest -q` (type=command, 20ms, status=failed, duration_source=derived, started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.020Z, exit_code=1, cwd=/repo, stderr_preview=AssertionError: expected 401, artifacts=command_log=artifacts/evt_cmd_early_log.log), fastest_activity=evt_edit_late_diff: src/report.py (type=file_edit, 5ms, status=failed, duration_source=explicit, started_at=2026-04-25T00:00:03Z, kind=modify, +2/-1, net=1, summary=Edit report timeline, error_message=patch failed, artifacts=diff=artifacts/evt_edit_late_diff.diff), last_activity=evt_edit_late_diff: src/report.py (type=file_edit, 5ms, status=failed, duration_source=explicit, started_at=2026-04-25T00:00:03Z, kind=modify, +2/-1, net=1, summary=Edit report timeline, error_message=patch failed, artifacts=diff=artifacts/evt_edit_late_diff.diff), total_idle_gap_ms=1980, largest_idle_gap=(from_event=evt_cmd_early_log, to_event=evt_edit_late_diff, gap_ms=1980, from_ended_at=2026-04-25T00:00:01.020Z, to_started_at=2026-04-25T00:00:03Z), total_overlap_ms=0, overlap_ratio=0.0, largest_overlap=none, failed_count=2, time_window=started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.020Z" in text
    assert "first_failed_activity: evt_cmd_early_log: `pytest -q` (type=command, 20ms, status=failed, duration_source=derived, started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.020Z, exit_code=1, cwd=/repo, stderr_preview=AssertionError: expected 401, artifacts=command_log=artifacts/evt_cmd_early_log.log)" in text
    assert "failed_activity: evt_cmd_early_log: `pytest -q` (type=command, 20ms, status=failed, duration_source=derived, started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.020Z, exit_code=1, cwd=/repo, stderr_preview=AssertionError: expected 401, artifacts=command_log=artifacts/evt_cmd_early_log.log); evt_edit_late_diff: src/report.py (type=file_edit, 5ms, status=failed, duration_source=explicit, started_at=2026-04-25T00:00:03Z, kind=modify, +2/-1, net=1, summary=Edit report timeline, error_message=patch failed, artifacts=diff=artifacts/evt_edit_late_diff.diff)" in text
    assert "## Activity Timeline" in text
    assert text.index("evt_cmd_early_log: command `pytest -q`") < text.index("evt_edit_late_diff: edit src/report.py")
    assert "evt_cmd_early_log: command `pytest -q` — 20ms, status=failed, exit_code=1, duration_source=derived, cwd=/repo, started_at=2026-04-25T00:00:01Z, ended_at=2026-04-25T00:00:01.020Z, stderr_preview=AssertionError: expected 401, artifacts: command_log=artifacts/evt_cmd_early_log.log" in text
    assert "evt_edit_late_diff: edit src/report.py (modify, +2/-1, net=1) — Edit report timeline, status=failed, duration_ms=5, duration_source=explicit, started_at=2026-04-25T00:00:03Z, error_message=patch failed, artifacts: diff=artifacts/evt_edit_late_diff.diff" in text


def test_activity_timeline_summary_reports_overlapping_activity():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "overlap-1", "task": "inspect overlapping work", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_long",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:05Z",
                "command": {"value": "pytest -q"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_overlap",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:03Z",
                "ended_at": "2026-04-25T00:00:04Z",
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Surface overlap timing"},
            },
            {
                "id": "evt_cmd_later",
                "seq": 3,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:06Z",
                "ended_at": "2026-04-25T00:00:07Z",
                "command": {"value": "ruff check"},
                "exit_code": 0,
            },
        ],
    }

    payload = build_json_summary(trace)
    timeline_totals = payload["activity_timeline_summary"]
    assert timeline_totals["inter_activity_overlaps"] == [{
        "from_event": "evt_cmd_long",
        "to_event": "evt_edit_overlap",
        "overlap_ms": 2000,
        "from_ended_at": "2026-04-25T00:00:05Z",
        "to_started_at": "2026-04-25T00:00:03Z",
    }]
    assert timeline_totals["total_overlap_ms"] == 2000
    assert timeline_totals["overlap_ratio"] == 0.2857
    assert timeline_totals["largest_overlap"] == timeline_totals["inter_activity_overlaps"][0]
    assert timeline_totals["total_idle_gap_ms"] == 2000
    assert timeline_totals["time_window"] == {"started_at": "2026-04-25T00:00:00Z", "ended_at": "2026-04-25T00:00:07Z"}
    assert timeline_totals["span_duration_ms"] == 7000
    assert timeline_totals["covered_duration_ms"] == 6000
    assert timeline_totals["uncovered_duration_ms"] == 1000
    assert timeline_totals["uncovered_intervals"] == [{
        "started_at": "2026-04-25T00:00:05Z",
        "ended_at": "2026-04-25T00:00:06Z",
        "duration_ms": 1000,
    }]
    assert timeline_totals["coverage_ratio"] == 0.8571
    assert timeline_totals["idle_ratio"] == 0.1429
    assert timeline_totals["covered_interval_count"] == 3

    text = build_markdown_summary(trace)
    assert "span_duration_ms=7000" in text
    assert "covered_duration_ms=6000" in text
    assert "uncovered_duration_ms=1000" in text
    assert "uncovered_intervals=(started_at=2026-04-25T00:00:05Z, ended_at=2026-04-25T00:00:06Z, duration_ms=1000)" in text
    assert "coverage_ratio=0.8571" in text
    assert "idle_ratio=0.1429" in text
    assert "covered_interval_count=3" in text
    assert "total_overlap_ms=2000" in text
    assert "overlap_ratio=0.2857" in text
    assert "largest_overlap=(from_event=evt_cmd_long, to_event=evt_edit_overlap, overlap_ms=2000, from_ended_at=2026-04-25T00:00:05Z, to_started_at=2026-04-25T00:00:03Z)" in text


def test_activity_timeline_summary_derives_coverage_for_partial_windows():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "coverage-1", "task": "inspect partial timing coverage", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_started_only",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:00Z",
                "duration_ms": 3000,
                "command": {"value": "pytest -q"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_ended_only",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "ended_at": "2026-04-25T00:00:05Z",
                "duration_ms": 1000,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0, "summary": "Track covered timing"},
            },
        ],
    }

    payload = build_json_summary(trace)
    timeline_totals = payload["activity_timeline_summary"]
    assert timeline_totals["time_window"] == {
        "started_at": "2026-04-25T00:00:00Z",
        "ended_at": "2026-04-25T00:00:05Z",
    }
    assert timeline_totals["span_duration_ms"] == 5000
    assert timeline_totals["covered_duration_ms"] == 4000
    assert timeline_totals["uncovered_duration_ms"] == 1000
    assert timeline_totals["uncovered_intervals"] == [{
        "started_at": "2026-04-25T00:00:03Z",
        "ended_at": "2026-04-25T00:00:04Z",
        "duration_ms": 1000,
    }]
    assert timeline_totals["coverage_ratio"] == 0.8
    assert timeline_totals["idle_ratio"] == 0.2
    assert timeline_totals["covered_interval_count"] == 2

    text = build_markdown_summary(trace)
    assert "covered_duration_ms=4000" in text
    assert "uncovered_duration_ms=1000" in text
    assert "uncovered_intervals=(started_at=2026-04-25T00:00:03Z, ended_at=2026-04-25T00:00:04Z, duration_ms=1000)" in text
    assert "coverage_ratio=0.8" in text
    assert "idle_ratio=0.2" in text
    assert "covered_interval_count=2" in text


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


def test_nested_aggregate_totals_preserve_artifact_refs():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "nested-artifacts-1", "task": "inspect nested aggregate artifacts", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_with_log",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 25,
                "command": {"value": "pytest -q", "cwd": "/workspace/app"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_with_diff",
                "seq": 2,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 4,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 3, "removed_lines": 1, "summary": "Preserve nested aggregate artifacts"},
            },
        ],
        "artifacts": [
            {"kind": "command_log", "path": "artifacts/evt_cmd_with_log.log", "event_id": "evt_cmd_with_log"},
            {"kind": "diff", "path": "artifacts/evt_edit_with_diff.diff", "event_id": "evt_edit_with_diff"},
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"]["command_attempts"][0]["artifacts"] == [
        {"kind": "command_log", "path": "artifacts/evt_cmd_with_log.log"}
    ]
    assert payload["command_timing_summary"]["cwd_totals"][0]["artifacts"] == [
        {"kind": "command_log", "path": "artifacts/evt_cmd_with_log.log"}
    ]
    assert payload["edit_summary_totals"]["file_change_totals"][0]["artifacts"] == [
        {"kind": "diff", "path": "artifacts/evt_edit_with_diff.diff"}
    ]
    assert payload["edit_summary_totals"]["kind_totals"][0]["artifacts"] == [
        {"kind": "diff", "path": "artifacts/evt_edit_with_diff.diff"}
    ]

    text = build_markdown_summary(trace)
    assert "command_attempts: `pytest -q` (count=1, total_duration_ms=25, average_duration_ms=25.0, failed_count=0, statuses=succeeded=1, duration_sources=explicit=1, first_event=evt_cmd_with_log, last_event=evt_cmd_with_log, artifacts=command_log=artifacts/evt_cmd_with_log.log)" in text
    assert "command_cwd_totals: /workspace/app (count=1, commands=pytest -q, failed_count=0, total_duration_ms=25, average_duration_ms=25.0, statuses=succeeded=1, duration_sources=explicit=1, artifacts=command_log=artifacts/evt_cmd_with_log.log)" in text
    assert "file_change_totals: src/report_json.py (count=1, failed_count=0, +3/-1, net=2, total_duration_ms=4, average_duration_ms=4.0, statuses=succeeded=1, kinds=modify=1, duration_sources=explicit=1, artifacts=diff=artifacts/evt_edit_with_diff.diff)" in text
    assert "edit_kind_totals: modify (count=1, files=src/report_json.py, failed_count=0, +3/-1, net=2, total_duration_ms=4, average_duration_ms=4.0, statuses=succeeded=1, duration_sources=explicit=1, artifacts=diff=artifacts/evt_edit_with_diff.diff)" in text
