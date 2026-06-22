from pathlib import Path
import json
import runpy

from src.emit_example_trace import build_sample_trace
from src.report_json import build_json_summary
from src.report_markdown import build_markdown_summary

def _timing_window_delta_expected(
    comparable_count,
    delta_total_ms=0,
    delta_abs_total_ms=0,
    delta_average_ms=0.0,
    delta_abs_average_ms=0.0,
    largest_delta_ms=0,
    largest_delta_example=None,
):
    return {
        "duration_window_comparable_count": comparable_count,
        "duration_window_delta_total_ms": delta_total_ms,
        "duration_window_delta_abs_total_ms": delta_abs_total_ms,
        "duration_window_delta_average_ms": delta_average_ms,
        "duration_window_delta_abs_average_ms": delta_abs_average_ms,
        "duration_window_delta_abs_recorded_duration_share": 0.0 if not delta_abs_total_ms else 1.0,
        "duration_window_delta_consistency_label": "no_comparable_rows" if not comparable_count else ("matched" if not delta_abs_total_ms else "high_delta"),
        "duration_window_delta_direction_counts": {
            "matches": comparable_count,
            "duration_exceeds_window": 0,
            "window_exceeds_duration": 0,
        },
        "duration_window_delta_direction_examples": {
            "matches": [] if largest_delta_example is None else [largest_delta_example],
            "duration_exceeds_window": [],
            "window_exceeds_duration": [],
        },
        "largest_duration_window_delta_ms": largest_delta_ms,
        "largest_duration_window_delta_example": largest_delta_example,
    }


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


def test_report_summary_text_metrics_quantify_command_and_edit_summary_detail():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "summary-text-1", "task": "inspect summary text", "status": "succeeded"},
        "events": [
            {
                "id": "cmd_summary",
                "type": "command",
                "status": "succeeded",
                "duration_ms": 4,
                "command": {"value": "pytest -q", "summary": "Run tests"},
            },
            {
                "id": "cmd_missing_summary",
                "type": "command",
                "status": "succeeded",
                "duration_ms": 2,
                "command": {"value": "ruff check"},
            },
            {
                "id": "edit_summary",
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 3,
                "file": {"path": "docs/notes.md"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0, "summary": "Document edit"},
            },
        ],
    }

    payload = build_json_summary(trace)

    assert payload["report_summary_text_metrics"] == {
        "command": {
            "summary_text_count": 1,
            "summary_text_total_chars": 9,
            "summary_text_average_chars": 9.0,
            "summary_text_min_chars": 9,
            "summary_text_max_chars": 9,
            "summary_text_empty_count": 1,
            "summary_text_coverage_ratio": 0.5,
            "summary_text_missing_ratio": 0.5,
            "summary_text_duration_ms": 6,
            "summary_text_summarized_duration_ms": 4,
            "summary_text_unsummarized_duration_ms": 2,
            "summary_text_summarized_average_duration_ms": 4.0,
            "summary_text_unsummarized_average_duration_ms": 2.0,
            "summary_text_average_duration_delta_ms": -2.0,
            "summary_text_average_duration_delta_abs_ms": 2.0,
            "summary_text_average_duration_delta_abs_ratio": 0.5,
            "summary_text_average_duration_gap_label": "medium_average_duration_gap",
            "summary_text_average_duration_gap_rank": 2,
            "summary_text_average_duration_gap_direction": "summarized_rows_slower",
            "summary_text_summarized_duration_ratio": 0.6667,
            "summary_text_unsummarized_duration_ratio": 0.3333,
            "summary_text_coverage_duration_share_delta": -0.1667,
            "summary_text_coverage_duration_share_delta_abs": 0.1667,
            "summary_text_coverage_duration_share_delta_abs_ratio": 0.25,
            "summary_text_chars_per_duration_ms": 1.5,
            "summary_text_duration_ms_per_char": 0.6667,
            "summary_text_chars_per_summarized_duration_ms": 2.25,
            "summary_text_summarized_duration_ms_per_char": 0.4444,
            "summary_text_chars_per_row": 4.5,
        },
        "edit": {
            "summary_text_count": 1,
            "summary_text_total_chars": 13,
            "summary_text_average_chars": 13.0,
            "summary_text_min_chars": 13,
            "summary_text_max_chars": 13,
            "summary_text_empty_count": 0,
            "summary_text_coverage_ratio": 1.0,
            "summary_text_missing_ratio": 0.0,
            "summary_text_duration_ms": 3,
            "summary_text_summarized_duration_ms": 3,
            "summary_text_unsummarized_duration_ms": 0,
            "summary_text_summarized_average_duration_ms": 3.0,
            "summary_text_unsummarized_average_duration_ms": 0,
            "summary_text_average_duration_delta_ms": -3.0,
            "summary_text_average_duration_delta_abs_ms": 3.0,
            "summary_text_average_duration_delta_abs_ratio": 1.0,
            "summary_text_average_duration_gap_label": "high_average_duration_gap",
            "summary_text_average_duration_gap_rank": 3,
            "summary_text_average_duration_gap_direction": "summarized_rows_slower",
            "summary_text_summarized_duration_ratio": 1.0,
            "summary_text_unsummarized_duration_ratio": 0.0,
            "summary_text_coverage_duration_share_delta": 0.0,
            "summary_text_coverage_duration_share_delta_abs": 0.0,
            "summary_text_coverage_duration_share_delta_abs_ratio": 0.0,
            "summary_text_chars_per_duration_ms": 4.3333,
            "summary_text_duration_ms_per_char": 0.2308,
            "summary_text_chars_per_summarized_duration_ms": 4.3333,
            "summary_text_summarized_duration_ms_per_char": 0.2308,
            "summary_text_chars_per_row": 13.0,
        },
        "activity": {
            "summary_text_count": 2,
            "summary_text_total_chars": 22,
            "summary_text_average_chars": 11.0,
            "summary_text_min_chars": 9,
            "summary_text_max_chars": 13,
            "summary_text_empty_count": 1,
            "summary_text_coverage_ratio": 0.6667,
            "summary_text_missing_ratio": 0.3333,
            "summary_text_duration_ms": 9,
            "summary_text_summarized_duration_ms": 7,
            "summary_text_unsummarized_duration_ms": 2,
            "summary_text_summarized_average_duration_ms": 3.5,
            "summary_text_unsummarized_average_duration_ms": 2.0,
            "summary_text_average_duration_delta_ms": -1.5,
            "summary_text_average_duration_delta_abs_ms": 1.5,
            "summary_text_average_duration_delta_abs_ratio": 0.4286,
            "summary_text_average_duration_gap_label": "medium_average_duration_gap",
            "summary_text_average_duration_gap_rank": 2,
            "summary_text_average_duration_gap_direction": "summarized_rows_slower",
            "summary_text_summarized_duration_ratio": 0.7778,
            "summary_text_unsummarized_duration_ratio": 0.2222,
            "summary_text_coverage_duration_share_delta": -0.1111,
            "summary_text_coverage_duration_share_delta_abs": 0.1111,
            "summary_text_coverage_duration_share_delta_abs_ratio": 0.1428,
            "summary_text_chars_per_duration_ms": 2.4444,
            "summary_text_duration_ms_per_char": 0.4091,
            "summary_text_chars_per_summarized_duration_ms": 3.1429,
            "summary_text_summarized_duration_ms_per_char": 0.3182,
            "summary_text_chars_per_row": 7.3333,
        },
    }
    markdown = build_markdown_summary(trace)
    assert "- report_summary_text_metrics: command=count=1,total_chars=9,average_chars=9.0,min_chars=9,max_chars=9,empty=1,coverage=0.5,missing=0.5,duration_ms=6,summarized_duration_ms=4,unsummarized_duration_ms=2,summarized_average_duration_ms=4.0,unsummarized_average_duration_ms=2.0,average_duration_delta_ms=-2.0,average_duration_delta_abs_ms=2.0,average_duration_delta_abs_ratio=0.5,average_duration_gap_label=medium_average_duration_gap,average_duration_gap_rank=2,average_duration_gap_direction=summarized_rows_slower,summarized_duration_ratio=0.6667,unsummarized_duration_ratio=0.3333,coverage_duration_share_delta=-0.1667,coverage_duration_share_delta_abs=0.1667,coverage_duration_share_delta_abs_ratio=0.25,chars_per_duration_ms=1.5,duration_ms_per_char=0.6667,chars_per_summarized_duration_ms=2.25,summarized_duration_ms_per_char=0.4444,chars_per_row=4.5" in markdown
    assert "edit=count=1,total_chars=13,average_chars=13.0,min_chars=13,max_chars=13,empty=0,coverage=1.0,missing=0.0,duration_ms=3,summarized_duration_ms=3,unsummarized_duration_ms=0,summarized_average_duration_ms=3.0,unsummarized_average_duration_ms=0,average_duration_delta_ms=-3.0,average_duration_delta_abs_ms=3.0,average_duration_delta_abs_ratio=1.0,average_duration_gap_label=high_average_duration_gap,average_duration_gap_rank=3,average_duration_gap_direction=summarized_rows_slower,summarized_duration_ratio=1.0,unsummarized_duration_ratio=0.0,coverage_duration_share_delta=0.0,coverage_duration_share_delta_abs=0.0,coverage_duration_share_delta_abs_ratio=0.0,chars_per_duration_ms=4.3333,duration_ms_per_char=0.2308,chars_per_summarized_duration_ms=4.3333,summarized_duration_ms_per_char=0.2308,chars_per_row=13.0" in markdown
    assert "activity=count=2,total_chars=22,average_chars=11.0,min_chars=9,max_chars=13,empty=1,coverage=0.6667,missing=0.3333,duration_ms=9,summarized_duration_ms=7,unsummarized_duration_ms=2,summarized_average_duration_ms=3.5,unsummarized_average_duration_ms=2.0,average_duration_delta_ms=-1.5,average_duration_delta_abs_ms=1.5,average_duration_delta_abs_ratio=0.4286,average_duration_gap_label=medium_average_duration_gap,average_duration_gap_rank=2,average_duration_gap_direction=summarized_rows_slower,summarized_duration_ratio=0.7778,unsummarized_duration_ratio=0.2222,coverage_duration_share_delta=-0.1111,coverage_duration_share_delta_abs=0.1111,coverage_duration_share_delta_abs_ratio=0.1428,chars_per_duration_ms=2.4444,duration_ms_per_char=0.4091,chars_per_summarized_duration_ms=3.1429,summarized_duration_ms_per_char=0.3182,chars_per_row=7.3333" in markdown


def test_report_summary_coverage_groups_explanations_by_report_labels():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "summary-coverage-1", "task": "inspect summary coverage", "status": "failed"},
        "events": [
            {
                "id": "evt_cmd_with_summary",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 10,
                "command": {"value": "pytest -q", "cwd": "repo", "summary": "Run tests"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_without_summary",
                "seq": 2,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:00.005Z",
                "command": {"value": "ruff check", "cwd": "repo"},
                "exit_code": 1,
            },
            {
                "id": "evt_edit_with_summary",
                "seq": 3,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 3,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 0, "summary": "Add coverage"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["report_summary_coverage"] == {
        "command_by_duration_source": {
            "explicit": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
            "derived": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
        },
        "command_by_status": {
            "succeeded": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
            "failed": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
        },
        "command_by_command": {
            "pytest -q": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
            "ruff check": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
        },
        "command_by_cwd": {
            "repo": {"summary_recorded_count": 1, "summary_missing_count": 1, "summary_coverage_ratio": 0.5},
        },
        "command_by_exit_code": {
            "0": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
            "1": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
        },
        "edit_by_duration_source": {
            "explicit": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
        },
        "edit_by_status": {
            "succeeded": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
        },
        "edit_by_kind": {
            "modify": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
        },
        "edit_by_path": {
            "src/report_json.py": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
        },
        "activity_by_type": {
            "command": {"summary_recorded_count": 1, "summary_missing_count": 1, "summary_coverage_ratio": 0.5},
            "file_edit": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
        },
        "activity_by_status": {
            "succeeded": {"summary_recorded_count": 2, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
            "failed": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
        },
        "activity_by_duration_source": {
            "explicit": {"summary_recorded_count": 2, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
            "derived": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
        },
        "activity_by_identity": {
            "command:pytest -q": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
            "command:ruff check": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
            "file_edit:src/report_json.py": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
        },
    }

    activity_totals = payload["activity_timeline_summary"]
    assert activity_totals["type_summary_examples"]["command"][0]["summary"] == "Run tests"
    assert activity_totals["type_summary_examples"]["file_edit"][0]["summary"] == "Add coverage"
    assert activity_totals["type_summary_missing_examples"]["command"][0]["command"] == "ruff check"
    assert activity_totals["status_summary_missing_examples"]["failed"][0]["command"] == "ruff check"
    assert activity_totals["duration_source_summary_examples"]["explicit"][0]["summary"] == "Run tests"
    assert activity_totals["duration_source_summary_missing_examples"]["derived"][0]["command"] == "ruff check"
    assert payload["report_summary_duration_impact"]["activity"] == {
        "summary_recorded_duration_count": 2,
        "summary_missing_duration_count": 1,
        "summary_total_duration_count": 3,
        "summary_recorded_count_share": 0.6667,
        "summary_missing_count_share": 0.3333,
        "summary_total_duration_ms": 18,
        "summary_recorded_duration_ms": 13,
        "summary_recorded_duration_share": 0.7222,
        "summary_recorded_average_duration_ms": 6.5,
        "summary_recorded_median_duration_ms": 6.5,
        "summary_recorded_duration_range_ms": 7,
        "summary_recorded_duration_extremes_ms": {"min": 3, "max": 10},
        "summary_recorded_duration_source_counts": {"explicit": 2},
        "summary_recorded_duration_source_duration_ms": {"explicit": 13},
        "summary_recorded_duration_source_share": {"explicit": 1.0},
        "summary_largest_recorded_duration_ms": 10,
        "summary_largest_recorded_duration_share": 0.7692,
        "summary_largest_recorded_total_duration_share": 0.5556,
        "summary_recorded_duration_examples": [{
            "event": "evt_cmd_with_summary",
            "status": "succeeded",
            "duration_ms": 10,
            "duration_source": "explicit",
            "type": "command",
            "command": "pytest -q",
            "cwd": "repo",
            "exit_code": 0,
            "summary": "Run tests",
        }, {
            "event": "evt_edit_with_summary",
            "status": "succeeded",
            "duration_ms": 3,
            "duration_source": "explicit",
            "type": "file_edit",
            "path": "src/report_json.py",
            "kind": "modify",
            "added_lines": 2,
            "removed_lines": 0,
            "net_line_delta": 2,
            "summary": "Add coverage",
        }],
        "summary_missing_duration_ms": 5,
        "summary_missing_average_duration_ms": 5.0,
        "summary_missing_median_duration_ms": 5,
        "summary_missing_duration_range_ms": 0,
        "summary_missing_duration_extremes_ms": {"min": 5, "max": 5},
        "summary_missing_duration_source_counts": {"derived": 1},
        "summary_missing_duration_source_duration_ms": {"derived": 5},
        "summary_missing_duration_source_share": {"derived": 1.0},
        "summary_missing_duration_status_counts": {"failed": 1},
        "summary_missing_duration_status_duration_ms": {"failed": 5},
        "summary_missing_duration_status_share": {"failed": 1.0},
        "summary_missing_duration_share": 0.2778,
        "summary_missing_recorded_duration_delta_ms": -8,
        "summary_missing_recorded_duration_delta_share": -0.4444,
        "summary_missing_recorded_duration_ratio": 0.3846,
        "summary_missing_recorded_excess_duration_ms": 0,
        "summary_duration_balance": "recorded_dominates",
        "summary_missing_duration_attention": "low",
        "summary_missing_exceeds_recorded_duration": False,
        "summary_missing_duration_concentration": "single_row",
        "summary_largest_missing_duration_ms": 5,
        "summary_largest_missing_duration_share": 1.0,
        "summary_largest_missing_total_duration_share": 0.2778,
        "summary_missing_duration_examples": [{
            "event": "evt_cmd_without_summary",
            "status": "failed",
            "duration_ms": 5,
            "duration_source": "derived",
            "type": "command",
            "command": "ruff check",
            "cwd": "repo",
            "exit_code": 1,
            "started_at": "2026-04-25T00:00:00Z",
            "ended_at": "2026-04-25T00:00:00.005Z",
        }],
    }
    assert activity_totals["identity_summary_examples"]["command:pytest -q"][0]["summary"] == "Run tests"
    assert activity_totals["identity_summary_examples"]["file_edit:src/report_json.py"][0]["summary"] == "Add coverage"
    assert activity_totals["identity_summary_missing_examples"]["command:ruff check"][0]["event"] == "evt_cmd_without_summary"

    assert payload["report_inspection_targets"][0] == {
        "type": "command",
        "event": "evt_cmd_without_summary",
        "reason": "failed_activity",
        "identity": "ruff check",
        "status": "failed",
        "duration_ms": 5,
        "duration_source": "derived",
        "detail": "failed status or non-zero command exit code",
        "started_at": "2026-04-25T00:00:00Z",
        "ended_at": "2026-04-25T00:00:00.005Z",
        "cwd": "repo",
        "exit_code": 1,
    }
    assert payload["report_inspection_targets"][1]["reason"] == "missing_command_summary"
    assert payload["report_inspection_targets"][2] == {
        "type": "command",
        "event": "evt_cmd_with_summary",
        "reason": "slowest_activity",
        "identity": "pytest -q",
        "status": "succeeded",
        "duration_ms": 10,
        "duration_source": "explicit",
        "detail": "largest recorded duration in command/edit activity timeline",
        "cwd": "repo",
        "exit_code": 0,
    }

    text = build_markdown_summary(trace)
    assert "report_inspection_targets: ruff check (event=evt_cmd_without_summary, type=command, reason=failed_activity" in text
    assert "detail=failed status or non-zero command exit code, started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:00.005Z" in text
    assert "pytest -q (event=evt_cmd_with_summary, type=command, reason=slowest_activity" in text
    assert "report_summary_coverage:" in text
    assert "command_by_duration_source=derived=recorded=0/missing=1/ratio=0.0, explicit=recorded=1/missing=0/ratio=1.0" in text
    assert "command_by_command=pytest -q=recorded=1/missing=0/ratio=1.0, ruff check=recorded=0/missing=1/ratio=0.0" in text
    assert "command_by_cwd=repo=recorded=1/missing=1/ratio=0.5" in text
    assert "command_by_exit_code=0=recorded=1/missing=0/ratio=1.0, 1=recorded=0/missing=1/ratio=0.0" in text
    assert "edit_by_status=succeeded=recorded=1/missing=0/ratio=1.0" in text
    assert "edit_by_path=src/report_json.py=recorded=1/missing=0/ratio=1.0" in text
    assert "activity_by_type=command=recorded=1/missing=1/ratio=0.5, file_edit=recorded=1/missing=0/ratio=1.0" in text
    assert "activity_by_identity=command:pytest -q=recorded=1/missing=0/ratio=1.0, command:ruff check=recorded=0/missing=1/ratio=0.0, file_edit:src/report_json.py=recorded=1/missing=0/ratio=1.0" in text
    assert "type_summary_examples=command=`pytest -q` (event=evt_cmd_with_summary, status=succeeded, duration_ms=10, duration_source=explicit, cwd=repo, exit_code=0, summary=Run tests); file_edit=src/report_json.py (event=evt_edit_with_summary, status=succeeded, duration_ms=3, duration_source=explicit, kind=modify, net=2, summary=Add coverage)" in text
    assert "type_summary_missing_examples=command=`ruff check` (event=evt_cmd_without_summary, status=failed, duration_ms=5, duration_source=derived, cwd=repo, exit_code=1)" in text
    assert "report_summary_duration_impact: command=recorded_duration_count=1/missing_duration_count=1/total_duration_count=2/recorded_count_share=0.5/missing_count_share=0.5/total_duration_ms=15/recorded_duration_ms=10/recorded_duration_share=0.6667/recorded_average_duration_ms=10.0/recorded_median_duration_ms=10/recorded_duration_range_ms=0/recorded_duration_extremes_ms={'min': 10, 'max': 10}/recorded_duration_source_counts=explicit=1/recorded_duration_source_duration_ms=explicit=10/recorded_duration_source_share=explicit=1.0/largest_recorded_duration_ms=10/largest_recorded_duration_share=1.0/largest_recorded_total_duration_share=0.6667/recorded_duration_examples=`pytest -q` (event=evt_cmd_with_summary, status=succeeded, duration_ms=10, duration_source=explicit, cwd=repo, exit_code=0, summary=Run tests)/missing_duration_ms=5/missing_average_duration_ms=5.0/missing_median_duration_ms=5/missing_duration_range_ms=0/missing_duration_extremes_ms={'min': 5, 'max': 5}/missing_duration_source_counts=derived=1/missing_duration_source_duration_ms=derived=5/missing_duration_source_share=derived=1.0/missing_duration_status_counts=failed=1/missing_duration_status_duration_ms=failed=5/missing_duration_status_share=failed=1.0/missing_duration_share=0.3333/missing_recorded_duration_delta_ms=-5/missing_recorded_duration_delta_share=-0.3333/missing_recorded_duration_ratio=0.5/missing_recorded_excess_duration_ms=0/duration_balance=recorded_dominates/missing_duration_attention=low/missing_exceeds_recorded_duration=False/missing_duration_concentration=single_row/largest_missing_duration_ms=5/largest_missing_duration_share=1.0/largest_missing_total_duration_share=0.3333/missing_duration_examples=`ruff check` (event=evt_cmd_without_summary, status=failed, duration_ms=5, duration_source=derived, cwd=repo, exit_code=1); edit=recorded_duration_count=1/missing_duration_count=0/total_duration_count=1/recorded_count_share=1.0/missing_count_share=0.0/total_duration_ms=3/recorded_duration_ms=3/recorded_duration_share=1.0/recorded_average_duration_ms=3.0/recorded_median_duration_ms=3/recorded_duration_range_ms=0/recorded_duration_extremes_ms={'min': 3, 'max': 3}/recorded_duration_source_counts=explicit=1/recorded_duration_source_duration_ms=explicit=3/recorded_duration_source_share=explicit=1.0/largest_recorded_duration_ms=3/largest_recorded_duration_share=1.0/largest_recorded_total_duration_share=1.0/recorded_duration_examples=src/report_json.py (event=evt_edit_with_summary, status=succeeded, duration_ms=3, duration_source=explicit, kind=modify, net=2, summary=Add coverage)/missing_duration_ms=0/missing_average_duration_ms=0/missing_median_duration_ms=0/missing_duration_range_ms=0/missing_duration_extremes_ms={'min': 0, 'max': 0}/missing_duration_source_counts=none/missing_duration_source_duration_ms=none/missing_duration_source_share=none/missing_duration_status_counts=none/missing_duration_status_duration_ms=none/missing_duration_status_share=none/missing_duration_share=0.0/missing_recorded_duration_delta_ms=-3/missing_recorded_duration_delta_share=-1.0/missing_recorded_duration_ratio=0.0/missing_recorded_excess_duration_ms=0/duration_balance=recorded_dominates/missing_duration_attention=none/missing_exceeds_recorded_duration=False/missing_duration_concentration=none/largest_missing_duration_ms=0/largest_missing_duration_share=0/largest_missing_total_duration_share=0.0/missing_duration_examples=none; activity=recorded_duration_count=2/missing_duration_count=1/total_duration_count=3/recorded_count_share=0.6667/missing_count_share=0.3333/total_duration_ms=18/recorded_duration_ms=13/recorded_duration_share=0.7222/recorded_average_duration_ms=6.5/recorded_median_duration_ms=6.5/recorded_duration_range_ms=7/recorded_duration_extremes_ms={'min': 3, 'max': 10}/recorded_duration_source_counts=explicit=2/recorded_duration_source_duration_ms=explicit=13/recorded_duration_source_share=explicit=1.0/largest_recorded_duration_ms=10/largest_recorded_duration_share=0.7692/largest_recorded_total_duration_share=0.5556/recorded_duration_examples=`pytest -q` (event=evt_cmd_with_summary, status=succeeded, duration_ms=10, duration_source=explicit, cwd=repo, exit_code=0, summary=Run tests); src/report_json.py (event=evt_edit_with_summary, status=succeeded, duration_ms=3, duration_source=explicit, kind=modify, net=2, summary=Add coverage)/missing_duration_ms=5/missing_average_duration_ms=5.0/missing_median_duration_ms=5/missing_duration_range_ms=0/missing_duration_extremes_ms={'min': 5, 'max': 5}/missing_duration_source_counts=derived=1/missing_duration_source_duration_ms=derived=5/missing_duration_source_share=derived=1.0/missing_duration_status_counts=failed=1/missing_duration_status_duration_ms=failed=5/missing_duration_status_share=failed=1.0/missing_duration_share=0.2778/missing_recorded_duration_delta_ms=-8/missing_recorded_duration_delta_share=-0.4444/missing_recorded_duration_ratio=0.3846/missing_recorded_excess_duration_ms=0/duration_balance=recorded_dominates/missing_duration_attention=low/missing_exceeds_recorded_duration=False/missing_duration_concentration=single_row/largest_missing_duration_ms=5/largest_missing_duration_share=1.0/largest_missing_total_duration_share=0.2778/missing_duration_examples=`ruff check` (event=evt_cmd_without_summary, status=failed, duration_ms=5, duration_source=derived, cwd=repo, exit_code=1)" in text
    assert "identity_summary_examples=command:pytest -q=`pytest -q` (event=evt_cmd_with_summary, status=succeeded, duration_ms=10, duration_source=explicit, cwd=repo, exit_code=0, summary=Run tests); file_edit:src/report_json.py=src/report_json.py (event=evt_edit_with_summary, status=succeeded, duration_ms=3, duration_source=explicit, kind=modify, net=2, summary=Add coverage)" in text
    assert "identity_summary_missing_examples=command:ruff check=`ruff check` (event=evt_cmd_without_summary, status=failed, duration_ms=5, duration_source=derived, cwd=repo, exit_code=1)" in text


def test_activity_timeline_renders_command_summaries():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "activity-command-summary-1", "task": "inspect activity command summaries", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_summary",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 42,
                "command": {"value": "pytest -q", "cwd": "repo", "summary": "Run regression tests"},
                "exit_code": 0,
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["activity_timeline"][0]["summary"] == "Run regression tests"

    text = build_markdown_summary(trace)
    assert "- evt_cmd_summary: command `pytest -q` — 42ms, status=succeeded, exit_code=0, duration_source=explicit, cwd=repo, summary=Run regression tests" in text


def test_summary_coverage_includes_missing_summary_duration_impact():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "summary-duration-impact-1", "task": "inspect missing summaries", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_summarized",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 25,
                "command": {"value": "pytest -q", "summary": "Run focused tests"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_unsummarized",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 75,
                "command": {"value": "python scripts/slow.py"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_unsummarized",
                "seq": 3,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 20,
                "file": {"path": "src/slow.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["report_summary_duration_impact"] == {
        "command": {
            "summary_recorded_duration_count": 1,
            "summary_missing_duration_count": 1,
            "summary_total_duration_count": 2,
            "summary_recorded_count_share": 0.5,
            "summary_missing_count_share": 0.5,
            "summary_total_duration_ms": 100,
            "summary_recorded_duration_ms": 25,
            "summary_recorded_duration_share": 0.25,
            "summary_recorded_average_duration_ms": 25.0,
            "summary_recorded_median_duration_ms": 25,
            "summary_recorded_duration_range_ms": 0,
            "summary_recorded_duration_extremes_ms": {"min": 25, "max": 25},
            "summary_recorded_duration_source_counts": {"explicit": 1},
            "summary_recorded_duration_source_duration_ms": {"explicit": 25},
            "summary_recorded_duration_source_share": {"explicit": 1.0},
            "summary_largest_recorded_duration_ms": 25,
            "summary_largest_recorded_duration_share": 1.0,
            "summary_largest_recorded_total_duration_share": 0.25,
            "summary_recorded_duration_examples": [{
                "event": "evt_cmd_summarized",
                "status": "succeeded",
                "duration_ms": 25,
                "duration_source": "explicit",
                "command": "pytest -q",
                "exit_code": 0,
                "summary": "Run focused tests",
            }],
            "summary_missing_duration_ms": 75,
            "summary_missing_average_duration_ms": 75.0,
            "summary_missing_median_duration_ms": 75,
            "summary_missing_duration_range_ms": 0,
            "summary_missing_duration_extremes_ms": {"min": 75, "max": 75},
            "summary_missing_duration_source_counts": {"explicit": 1},
            "summary_missing_duration_source_duration_ms": {"explicit": 75},
            "summary_missing_duration_source_share": {"explicit": 1.0},
            "summary_missing_duration_status_counts": {"succeeded": 1},
            "summary_missing_duration_status_duration_ms": {"succeeded": 75},
            "summary_missing_duration_status_share": {"succeeded": 1.0},
            "summary_missing_duration_share": 0.75,
            "summary_missing_recorded_duration_delta_ms": 50,
            "summary_missing_recorded_duration_delta_share": 0.5,
            "summary_missing_recorded_duration_ratio": 3.0,
            "summary_missing_recorded_excess_duration_ms": 50,
            "summary_duration_balance": "missing_dominates",
            "summary_missing_duration_attention": "high",
            "summary_missing_exceeds_recorded_duration": True,
            "summary_missing_duration_concentration": "single_row",
            "summary_largest_missing_duration_ms": 75,
            "summary_largest_missing_duration_share": 1.0,
            "summary_largest_missing_total_duration_share": 0.75,
            "summary_missing_duration_examples": [{
                "event": "evt_cmd_unsummarized",
                "status": "succeeded",
                "duration_ms": 75,
                "duration_source": "explicit",
                "command": "python scripts/slow.py",
                "exit_code": 0,
            }],
        },
        "edit": {
            "summary_recorded_duration_count": 0,
            "summary_missing_duration_count": 1,
            "summary_total_duration_count": 1,
            "summary_recorded_count_share": 0.0,
            "summary_missing_count_share": 1.0,
            "summary_total_duration_ms": 20,
            "summary_recorded_duration_ms": 0,
            "summary_recorded_duration_share": 0.0,
            "summary_recorded_average_duration_ms": 0,
            "summary_recorded_median_duration_ms": 0,
            "summary_recorded_duration_range_ms": 0,
            "summary_recorded_duration_extremes_ms": {"min": 0, "max": 0},
            "summary_recorded_duration_source_counts": {},
            "summary_recorded_duration_source_duration_ms": {},
            "summary_recorded_duration_source_share": {},
            "summary_largest_recorded_duration_ms": 0,
            "summary_largest_recorded_duration_share": 0,
            "summary_largest_recorded_total_duration_share": 0,
            "summary_recorded_duration_examples": [],
            "summary_missing_duration_ms": 20,
            "summary_missing_average_duration_ms": 20.0,
            "summary_missing_median_duration_ms": 20,
            "summary_missing_duration_range_ms": 0,
            "summary_missing_duration_extremes_ms": {"min": 20, "max": 20},
            "summary_missing_duration_source_counts": {"explicit": 1},
            "summary_missing_duration_source_duration_ms": {"explicit": 20},
            "summary_missing_duration_source_share": {"explicit": 1.0},
            "summary_missing_duration_status_counts": {"succeeded": 1},
            "summary_missing_duration_status_duration_ms": {"succeeded": 20},
            "summary_missing_duration_status_share": {"succeeded": 1.0},
            "summary_missing_duration_share": 1.0,
            "summary_missing_recorded_duration_delta_ms": 20,
            "summary_missing_recorded_duration_delta_share": 1.0,
            "summary_missing_recorded_duration_ratio": None,
            "summary_missing_recorded_excess_duration_ms": 20,
            "summary_duration_balance": "missing_dominates",
            "summary_missing_duration_attention": "high",
            "summary_missing_exceeds_recorded_duration": True,
            "summary_missing_duration_concentration": "single_row",
            "summary_largest_missing_duration_ms": 20,
            "summary_largest_missing_duration_share": 1.0,
            "summary_largest_missing_total_duration_share": 1.0,
            "summary_missing_duration_examples": [{
                "event": "evt_edit_unsummarized",
                "status": "succeeded",
                "duration_ms": 20,
                "duration_source": "explicit",
                "path": "src/slow.py",
                "kind": "modify",
                "added_lines": 1,
                "removed_lines": 0,
                "net_line_delta": 1,
            }],
        },
        "activity": {
            "summary_recorded_duration_count": 1,
            "summary_missing_duration_count": 2,
            "summary_total_duration_count": 3,
            "summary_recorded_count_share": 0.3333,
            "summary_missing_count_share": 0.6667,
            "summary_total_duration_ms": 120,
            "summary_recorded_duration_ms": 25,
            "summary_recorded_duration_share": 0.2083,
            "summary_recorded_average_duration_ms": 25.0,
            "summary_recorded_median_duration_ms": 25,
            "summary_recorded_duration_range_ms": 0,
            "summary_recorded_duration_extremes_ms": {"min": 25, "max": 25},
            "summary_recorded_duration_source_counts": {"explicit": 1},
            "summary_recorded_duration_source_duration_ms": {"explicit": 25},
            "summary_recorded_duration_source_share": {"explicit": 1.0},
            "summary_largest_recorded_duration_ms": 25,
            "summary_largest_recorded_duration_share": 1.0,
            "summary_largest_recorded_total_duration_share": 0.2083,
            "summary_recorded_duration_examples": [{
                "event": "evt_cmd_summarized",
                "status": "succeeded",
                "duration_ms": 25,
                "duration_source": "explicit",
                "type": "command",
                "command": "pytest -q",
                "exit_code": 0,
                "summary": "Run focused tests",
            }],
            "summary_missing_duration_ms": 95,
            "summary_missing_average_duration_ms": 47.5,
            "summary_missing_median_duration_ms": 47.5,
            "summary_missing_duration_range_ms": 55,
            "summary_missing_duration_extremes_ms": {"min": 20, "max": 75},
            "summary_missing_duration_source_counts": {"explicit": 2},
            "summary_missing_duration_source_duration_ms": {"explicit": 95},
            "summary_missing_duration_source_share": {"explicit": 1.0},
            "summary_missing_duration_status_counts": {"succeeded": 2},
            "summary_missing_duration_status_duration_ms": {"succeeded": 95},
            "summary_missing_duration_status_share": {"succeeded": 1.0},
            "summary_missing_duration_share": 0.7917,
            "summary_missing_recorded_duration_delta_ms": 70,
            "summary_missing_recorded_duration_delta_share": 0.5833,
            "summary_missing_recorded_duration_ratio": 3.8,
            "summary_missing_recorded_excess_duration_ms": 70,
            "summary_duration_balance": "missing_dominates",
            "summary_missing_duration_attention": "high",
            "summary_missing_exceeds_recorded_duration": True,
            "summary_missing_duration_concentration": "single_row",
            "summary_largest_missing_duration_ms": 75,
            "summary_largest_missing_duration_share": 0.7895,
            "summary_largest_missing_total_duration_share": 0.625,
            "summary_missing_duration_examples": [{
                "event": "evt_cmd_unsummarized",
                "status": "succeeded",
                "duration_ms": 75,
                "duration_source": "explicit",
                "type": "command",
                "command": "python scripts/slow.py",
                "exit_code": 0,
            }, {
                "event": "evt_edit_unsummarized",
                "status": "succeeded",
                "duration_ms": 20,
                "duration_source": "explicit",
                "type": "file_edit",
                "path": "src/slow.py",
                "kind": "modify",
                "added_lines": 1,
                "removed_lines": 0,
                "net_line_delta": 1,
            }],
        },
    }

    text = build_markdown_summary(trace)
    assert "command=recorded_duration_count=1/missing_duration_count=1/total_duration_count=2/recorded_count_share=0.5/missing_count_share=0.5/total_duration_ms=100/recorded_duration_ms=25/recorded_duration_share=0.25/recorded_average_duration_ms=25.0/recorded_median_duration_ms=25/recorded_duration_range_ms=0/recorded_duration_extremes_ms={'min': 25, 'max': 25}/recorded_duration_source_counts=explicit=1/recorded_duration_source_duration_ms=explicit=25/recorded_duration_source_share=explicit=1.0/largest_recorded_duration_ms=25/largest_recorded_duration_share=1.0/largest_recorded_total_duration_share=0.25/recorded_duration_examples=`pytest -q` (event=evt_cmd_summarized, status=succeeded, duration_ms=25, duration_source=explicit, exit_code=0, summary=Run focused tests)/missing_duration_ms=75/missing_average_duration_ms=75.0/missing_median_duration_ms=75/missing_duration_range_ms=0/missing_duration_extremes_ms={'min': 75, 'max': 75}/missing_duration_source_counts=explicit=1/missing_duration_source_duration_ms=explicit=75/missing_duration_source_share=explicit=1.0/missing_duration_status_counts=succeeded=1/missing_duration_status_duration_ms=succeeded=75/missing_duration_status_share=succeeded=1.0/missing_duration_share=0.75/missing_recorded_duration_delta_ms=50/missing_recorded_duration_delta_share=0.5/missing_recorded_duration_ratio=3.0/missing_recorded_excess_duration_ms=50/duration_balance=missing_dominates/missing_duration_attention=high/missing_exceeds_recorded_duration=True/missing_duration_concentration=single_row/largest_missing_duration_ms=75/largest_missing_duration_share=1.0/largest_missing_total_duration_share=0.75/missing_duration_examples=`python scripts/slow.py` (event=evt_cmd_unsummarized, status=succeeded, duration_ms=75, duration_source=explicit, exit_code=0)" in text
    assert "edit=recorded_duration_count=0/missing_duration_count=1/total_duration_count=1/recorded_count_share=0.0/missing_count_share=1.0/total_duration_ms=20/recorded_duration_ms=0/recorded_duration_share=0.0/recorded_average_duration_ms=0/recorded_median_duration_ms=0/recorded_duration_range_ms=0/recorded_duration_extremes_ms={'min': 0, 'max': 0}/recorded_duration_source_counts=none/recorded_duration_source_duration_ms=none/recorded_duration_source_share=none/largest_recorded_duration_ms=0/largest_recorded_duration_share=0/largest_recorded_total_duration_share=0.0/recorded_duration_examples=none/missing_duration_ms=20/missing_average_duration_ms=20.0/missing_median_duration_ms=20/missing_duration_range_ms=0/missing_duration_extremes_ms={'min': 20, 'max': 20}/missing_duration_source_counts=explicit=1/missing_duration_source_duration_ms=explicit=20/missing_duration_source_share=explicit=1.0/missing_duration_status_counts=succeeded=1/missing_duration_status_duration_ms=succeeded=20/missing_duration_status_share=succeeded=1.0/missing_duration_share=1.0/missing_recorded_duration_delta_ms=20/missing_recorded_duration_delta_share=1.0/missing_recorded_duration_ratio=None/missing_recorded_excess_duration_ms=20/duration_balance=missing_dominates/missing_duration_attention=high/missing_exceeds_recorded_duration=True/missing_duration_concentration=single_row/largest_missing_duration_ms=20/largest_missing_duration_share=1.0/largest_missing_total_duration_share=1.0/missing_duration_examples=src/slow.py (event=evt_edit_unsummarized, status=succeeded, duration_ms=20, duration_source=explicit, kind=modify, net=1)" in text
    assert "activity=recorded_duration_count=1/missing_duration_count=2/total_duration_count=3/recorded_count_share=0.3333/missing_count_share=0.6667/total_duration_ms=120/recorded_duration_ms=25/recorded_duration_share=0.2083/recorded_average_duration_ms=25.0/recorded_median_duration_ms=25/recorded_duration_range_ms=0/recorded_duration_extremes_ms={'min': 25, 'max': 25}/recorded_duration_source_counts=explicit=1/recorded_duration_source_duration_ms=explicit=25/recorded_duration_source_share=explicit=1.0/largest_recorded_duration_ms=25/largest_recorded_duration_share=1.0/largest_recorded_total_duration_share=0.2083/recorded_duration_examples=`pytest -q` (event=evt_cmd_summarized, status=succeeded, duration_ms=25, duration_source=explicit, exit_code=0, summary=Run focused tests)/missing_duration_ms=95/missing_average_duration_ms=47.5/missing_median_duration_ms=47.5/missing_duration_range_ms=55/missing_duration_extremes_ms={'min': 20, 'max': 75}/missing_duration_source_counts=explicit=2/missing_duration_source_duration_ms=explicit=95/missing_duration_source_share=explicit=1.0/missing_duration_status_counts=succeeded=2/missing_duration_status_duration_ms=succeeded=95/missing_duration_status_share=succeeded=1.0/missing_duration_share=0.7917/missing_recorded_duration_delta_ms=70/missing_recorded_duration_delta_share=0.5833/missing_recorded_duration_ratio=3.8/missing_recorded_excess_duration_ms=70/duration_balance=missing_dominates/missing_duration_attention=high/missing_exceeds_recorded_duration=True/missing_duration_concentration=single_row/largest_missing_duration_ms=75/largest_missing_duration_share=0.7895/largest_missing_total_duration_share=0.625/missing_duration_examples=`python scripts/slow.py` (event=evt_cmd_unsummarized, status=succeeded, duration_ms=75, duration_source=explicit, exit_code=0); src/slow.py (event=evt_edit_unsummarized, status=succeeded, duration_ms=20, duration_source=explicit, kind=modify, net=1)" in text
    assert text.index("python scripts/slow.py") < text.index("evt_edit_unsummarized")


def test_summary_duration_impact_labels_missing_duration_concentration():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "duration-concentration-1", "task": "inspect concentration", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_summarized",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 90,
                "command": {"value": "pytest -q", "summary": "Run focused tests"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_missing_large",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 60,
                "command": {"value": "python scripts/slow.py"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_missing_small",
                "seq": 3,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 40,
                "command": {"value": "python scripts/other.py"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_missing_a",
                "seq": 4,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 40,
                "file": {"path": "src/a.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0},
            },
            {
                "id": "evt_edit_missing_b",
                "seq": 5,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 35,
                "file": {"path": "src/b.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0},
            },
            {
                "id": "evt_edit_missing_c",
                "seq": 6,
                "type": "file_edit",
                "status": "succeeded",
                "duration_ms": 25,
                "file": {"path": "src/c.py"},
                "change": {"kind": "modify", "added_lines": 1, "removed_lines": 0},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["report_summary_duration_impact"]["command"]["summary_missing_duration_concentration"] == "clustered"
    assert payload["report_summary_duration_impact"]["edit"]["summary_missing_duration_concentration"] == "distributed"
    assert payload["report_summary_duration_impact"]["activity"]["summary_missing_duration_concentration"] == "distributed"

    text = build_markdown_summary(trace)
    assert "command=recorded_duration_count=1/missing_duration_count=2" in text
    assert "missing_duration_concentration=clustered" in text
    assert "edit=recorded_duration_count=0/missing_duration_count=3" in text
    assert "missing_duration_concentration=distributed" in text


def test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "summary-window-impact-1", "task": "inspect summary timing windows", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_summarized_window",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:00.050Z",
                "duration_ms": 50,
                "command": {"value": "pytest -q", "summary": "Run tests"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_missing_window",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:01Z",
                "duration_ms": 150,
                "command": {"value": "python scripts/slow.py"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_summarized_partial",
                "seq": 3,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:02Z",
                "duration_ms": 80,
                "file": {"path": "src/report_json.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1, "summary": "Add metric"},
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["report_summary_timing_window_impact"] == {
        "command": {
            "summary_recorded_complete_window_count": 1,
            "summary_missing_complete_window_count": 0,
            "summary_complete_window_count_delta": -1,
            "summary_complete_window_count_delta_abs": 1,
            "summary_complete_window_count_delta_abs_share": 1.0,
            "summary_complete_window_count_delta_share": -1.0,
            "summary_complete_window_count_delta_label": "recorded_summary_complete_window_count_higher",
            "summary_complete_window_count_delta_attention_label": "high_complete_window_count_delta",
            "summary_recorded_missing_window_count": 0,
            "summary_missing_missing_window_count": 1,
            "summary_missing_window_excess_count": 1,
            "summary_missing_window_excess_share": 0.5,
            "summary_recorded_complete_window_duration_ms": 50,
            "summary_missing_complete_window_duration_ms": 0,
            "summary_complete_window_duration_total_ms": 50,
            "summary_complete_window_duration_total_share": 0.25,
            "summary_complete_window_duration_delta_ms": -50,
            "summary_complete_window_duration_delta_label": "recorded_summary_complete_window_duration_higher",
            "summary_complete_window_duration_delta_abs_ms": 50,
            "summary_complete_window_duration_delta_abs_share": 1.0,
            "summary_complete_window_duration_delta_share": -1.0,
            "summary_complete_window_duration_ratio": 0,
            "summary_complete_window_duration_ratio_label": "recorded_summary_only_complete_window_duration",
            "summary_recorded_missing_window_duration_ms": 0,
            "summary_missing_missing_window_duration_ms": 150,
            "summary_missing_window_duration_delta_ms": 150,
            "summary_missing_window_duration_delta_label": "missing_summary_missing_window_duration_higher",
            "summary_missing_window_duration_delta_abs_ms": 150,
            "summary_missing_window_duration_total_ms": 150,
            "summary_missing_window_duration_total_share": 0.75,
            "summary_missing_window_duration_delta_abs_share": 1.0,
            "summary_missing_window_duration_delta_share": 1.0,
            "summary_missing_window_excess_duration_ms": 150,
            "summary_missing_window_excess_duration_share": 0.75,
            "summary_missing_window_excess_missing_duration_share": 1.0,
            "summary_missing_window_duration_ratio": None,
            "summary_missing_window_duration_ratio_label": "missing_summary_only_missing_window_duration",
            "summary_missing_window_excess_average_duration_ms": 150.0,
            "summary_missing_window_excess_attention_label": "high_missing_summary_window_excess",
            "summary_recorded_complete_window_share": 1.0,
            "summary_missing_complete_window_share": 0.0,
            "summary_complete_window_share_delta": -1.0,
            "summary_recorded_missing_window_share": 0.0,
            "summary_missing_missing_window_share": 1.0,
            "summary_missing_window_share_delta": 1.0,
            "summary_recorded_complete_window_duration_share": 1.0,
            "summary_missing_complete_window_duration_share": 0.0,
            "summary_complete_window_duration_share_delta": -1.0,
            "summary_complete_window_coverage_label": "high_recorded_summary_complete_window_coverage",
            "summary_recorded_missing_window_duration_share": 0.0,
            "summary_missing_missing_window_duration_share": 1.0,
            "summary_missing_window_duration_share_delta": 1.0,
            "summary_missing_window_gap_delta_max": 1.0,
            "summary_missing_window_gap_source": "count_and_duration_missing_summary_gap_source",
            "summary_missing_window_gap_duration_minus_count_delta": 0.0,
            "summary_missing_window_gap_duration_minus_count_delta_abs": 0.0,
            "summary_missing_window_gap_delta_comparison_label": "balanced_missing_summary_gap_signals",
            "summary_missing_window_gap_delta_comparison_attention_label": "no_missing_summary_gap_signal_divergence",
            "summary_missing_window_gap_delta_comparison_attention_rank": 0,
            "summary_missing_window_gap_delta_comparison_attention_required": False,
            "summary_missing_window_gap_delta_comparison_attention_status": "no_missing_summary_gap_signal_attention_needed",
            "summary_missing_window_gap_delta_comparison_attention_trigger": "no_missing_summary_gap_signal_attention_trigger",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal": "none",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_label": "no_missing_summary_gap_signal_family",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_rank": 0,
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_required": False,
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_status": "no_missing_summary_gap_trigger_signal_attention_needed",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action": "no_missing_summary_gap_trigger_signal_action",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_label": "no_missing_summary_gap_trigger_signal_review_action",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_label": "no_priority_missing_summary_gap_trigger_signal_review_action",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_rank": 0,
            "summary_missing_window_gap_label": "high_missing_summary_gap",
        },
        "edit": {
            "summary_recorded_complete_window_count": 0,
            "summary_missing_complete_window_count": 0,
            "summary_complete_window_count_delta": 0,
            "summary_complete_window_count_delta_abs": 0,
            "summary_complete_window_count_delta_abs_share": 0,
            "summary_complete_window_count_delta_share": 0,
            "summary_complete_window_count_delta_label": "balanced_complete_window_count_delta",
            "summary_complete_window_count_delta_attention_label": "no_complete_window_count_delta",
            "summary_recorded_missing_window_count": 1,
            "summary_missing_missing_window_count": 0,
            "summary_missing_window_excess_count": 0,
            "summary_missing_window_excess_share": 0.0,
            "summary_recorded_complete_window_duration_ms": 0,
            "summary_missing_complete_window_duration_ms": 0,
            "summary_complete_window_duration_total_ms": 0,
            "summary_complete_window_duration_total_share": 0.0,
            "summary_complete_window_duration_delta_ms": 0,
            "summary_complete_window_duration_delta_label": "balanced_complete_window_duration_delta",
            "summary_complete_window_duration_delta_abs_ms": 0,
            "summary_complete_window_duration_delta_abs_share": 0,
            "summary_complete_window_duration_delta_share": 0,
            "summary_complete_window_duration_ratio": 0,
            "summary_complete_window_duration_ratio_label": "no_complete_window_duration",
            "summary_recorded_missing_window_duration_ms": 80,
            "summary_missing_missing_window_duration_ms": 0,
            "summary_missing_window_duration_delta_ms": -80,
            "summary_missing_window_duration_delta_label": "recorded_summary_missing_window_duration_higher",
            "summary_missing_window_duration_delta_abs_ms": 80,
            "summary_missing_window_duration_total_ms": 80,
            "summary_missing_window_duration_total_share": 1.0,
            "summary_missing_window_duration_delta_abs_share": 1.0,
            "summary_missing_window_duration_delta_share": -1.0,
            "summary_missing_window_excess_duration_ms": 0,
            "summary_missing_window_excess_duration_share": 0.0,
            "summary_missing_window_excess_missing_duration_share": 0,
            "summary_missing_window_duration_ratio": 0,
            "summary_missing_window_duration_ratio_label": "recorded_summary_only_missing_window_duration",
            "summary_missing_window_excess_average_duration_ms": 0,
            "summary_missing_window_excess_attention_label": "no_missing_summary_window_excess",
            "summary_recorded_complete_window_share": 0.0,
            "summary_missing_complete_window_share": 0,
            "summary_complete_window_share_delta": 0.0,
            "summary_recorded_missing_window_share": 1.0,
            "summary_missing_missing_window_share": 0,
            "summary_missing_window_share_delta": -1.0,
            "summary_recorded_complete_window_duration_share": 0.0,
            "summary_missing_complete_window_duration_share": 0,
            "summary_complete_window_duration_share_delta": 0.0,
            "summary_complete_window_coverage_label": "balanced_complete_window_coverage",
            "summary_recorded_missing_window_duration_share": 1.0,
            "summary_missing_missing_window_duration_share": 0,
            "summary_missing_window_duration_share_delta": -1.0,
            "summary_missing_window_gap_delta_max": 0,
            "summary_missing_window_gap_source": "no_missing_summary_gap_source",
            "summary_missing_window_gap_duration_minus_count_delta": 0.0,
            "summary_missing_window_gap_duration_minus_count_delta_abs": 0.0,
            "summary_missing_window_gap_delta_comparison_label": "balanced_missing_summary_gap_signals",
            "summary_missing_window_gap_delta_comparison_attention_label": "no_missing_summary_gap_signal_divergence",
            "summary_missing_window_gap_delta_comparison_attention_rank": 0,
            "summary_missing_window_gap_delta_comparison_attention_required": False,
            "summary_missing_window_gap_delta_comparison_attention_status": "no_missing_summary_gap_signal_attention_needed",
            "summary_missing_window_gap_delta_comparison_attention_trigger": "no_missing_summary_gap_signal_attention_trigger",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal": "none",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_label": "no_missing_summary_gap_signal_family",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_rank": 0,
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_required": False,
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_status": "no_missing_summary_gap_trigger_signal_attention_needed",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action": "no_missing_summary_gap_trigger_signal_action",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_label": "no_missing_summary_gap_trigger_signal_review_action",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_label": "no_priority_missing_summary_gap_trigger_signal_review_action",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_rank": 0,
            "summary_missing_window_gap_label": "no_missing_summary_gap",
        },
        "activity": {
            "summary_recorded_complete_window_count": 1,
            "summary_missing_complete_window_count": 0,
            "summary_complete_window_count_delta": -1,
            "summary_complete_window_count_delta_abs": 1,
            "summary_complete_window_count_delta_abs_share": 1.0,
            "summary_complete_window_count_delta_share": -1.0,
            "summary_complete_window_count_delta_label": "recorded_summary_complete_window_count_higher",
            "summary_complete_window_count_delta_attention_label": "high_complete_window_count_delta",
            "summary_recorded_missing_window_count": 1,
            "summary_missing_missing_window_count": 1,
            "summary_missing_window_excess_count": 0,
            "summary_missing_window_excess_share": 0.0,
            "summary_recorded_complete_window_duration_ms": 50,
            "summary_missing_complete_window_duration_ms": 0,
            "summary_complete_window_duration_total_ms": 50,
            "summary_complete_window_duration_total_share": 0.1786,
            "summary_complete_window_duration_delta_ms": -50,
            "summary_complete_window_duration_delta_label": "recorded_summary_complete_window_duration_higher",
            "summary_complete_window_duration_delta_abs_ms": 50,
            "summary_complete_window_duration_delta_abs_share": 1.0,
            "summary_complete_window_duration_delta_share": -1.0,
            "summary_complete_window_duration_ratio": 0,
            "summary_complete_window_duration_ratio_label": "recorded_summary_only_complete_window_duration",
            "summary_recorded_missing_window_duration_ms": 80,
            "summary_missing_missing_window_duration_ms": 150,
            "summary_missing_window_duration_delta_ms": 70,
            "summary_missing_window_duration_delta_label": "missing_summary_missing_window_duration_higher",
            "summary_missing_window_duration_delta_abs_ms": 70,
            "summary_missing_window_duration_total_ms": 230,
            "summary_missing_window_duration_total_share": 0.8214,
            "summary_missing_window_duration_delta_abs_share": 0.3043,
            "summary_missing_window_duration_delta_share": 0.3043,
            "summary_missing_window_excess_duration_ms": 70,
            "summary_missing_window_excess_duration_share": 0.25,
            "summary_missing_window_excess_missing_duration_share": 0.4667,
            "summary_missing_window_duration_ratio": 1.875,
            "summary_missing_window_duration_ratio_label": "missing_summary_duration_elevated",
            "summary_missing_window_excess_average_duration_ms": 0,
            "summary_missing_window_excess_attention_label": "medium_missing_summary_window_excess",
            "summary_recorded_complete_window_share": 0.5,
            "summary_missing_complete_window_share": 0.0,
            "summary_complete_window_share_delta": -0.5,
            "summary_recorded_missing_window_share": 0.5,
            "summary_missing_missing_window_share": 1.0,
            "summary_missing_window_share_delta": 0.5,
            "summary_recorded_complete_window_duration_share": 0.3846,
            "summary_missing_complete_window_duration_share": 0.0,
            "summary_complete_window_duration_share_delta": -0.3846,
            "summary_complete_window_coverage_label": "high_recorded_summary_complete_window_coverage",
            "summary_recorded_missing_window_duration_share": 0.6154,
            "summary_missing_missing_window_duration_share": 1.0,
            "summary_missing_window_duration_share_delta": 0.3846,
            "summary_missing_window_gap_delta_max": 0.5,
            "summary_missing_window_gap_source": "count_share_missing_summary_gap_source",
            "summary_missing_window_gap_duration_minus_count_delta": -0.1154,
            "summary_missing_window_gap_duration_minus_count_delta_abs": 0.1154,
            "summary_missing_window_gap_delta_comparison_label": "count_share_missing_summary_gap_higher",
            "summary_missing_window_gap_delta_comparison_attention_label": "low_missing_summary_gap_signal_divergence",
            "summary_missing_window_gap_delta_comparison_attention_rank": 1,
            "summary_missing_window_gap_delta_comparison_attention_required": True,
            "summary_missing_window_gap_delta_comparison_attention_status": "missing_summary_gap_signal_attention_needed",
            "summary_missing_window_gap_delta_comparison_attention_trigger": "count_share_missing_summary_gap_signal_attention_trigger",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal": "count_share",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_label": "count_share_missing_summary_gap_signal_family",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_rank": 1,
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_required": True,
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_status": "missing_summary_gap_trigger_signal_attention_needed",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action": "review_count_share_missing_summary_gap_signal",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_label": "count_share_missing_summary_gap_signal_review_action",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_label": "low_priority_missing_summary_gap_trigger_signal_review_action",
            "summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_rank": 1,
            "summary_missing_window_gap_label": "high_missing_summary_gap",
        },
    }

    text = build_markdown_summary(trace)
    assert "report_summary_timing_window_impact:" in text
    assert "command=recorded_complete_windows=1/missing_complete_windows=0/complete_window_count_delta=-1/complete_window_count_delta_abs=1/complete_window_count_delta_abs_share=1.0/complete_window_count_delta_share=-1.0/complete_window_count_delta_label=recorded_summary_complete_window_count_higher/complete_window_count_delta_attention_label=high_complete_window_count_delta/recorded_missing_windows=0/missing_missing_windows=1" in text
    assert "recorded_missing_window_share=0.5" in text
    assert "complete_window_count_delta=-1" in text
    assert "complete_window_count_delta=0" in text
    assert "complete_window_count_delta_abs=1" in text
    assert "complete_window_count_delta_abs_share=1.0" in text
    assert "complete_window_count_delta_share=-1.0" in text
    assert "complete_window_count_delta_share=0" in text
    assert "complete_window_count_delta_label=recorded_summary_complete_window_count_higher" in text
    assert "complete_window_count_delta_label=balanced_complete_window_count_delta" in text
    assert "complete_window_count_delta_attention_label=high_complete_window_count_delta" in text
    assert "complete_window_count_delta_attention_label=no_complete_window_count_delta" in text
    assert "complete_window_count_delta_abs=0" in text
    assert "complete_window_share_delta=-1.0" in text
    assert "complete_window_share_delta=0.0" in text
    assert "complete_window_share_delta=-0.5" in text
    assert "missing_window_share_delta=0.5" in text
    assert "complete_window_duration_share_delta=-1.0" in text
    assert "complete_window_duration_share_delta=0.0" in text
    assert "complete_window_duration_share_delta=-0.3846" in text
    assert "complete_window_coverage_label=high_recorded_summary_complete_window_coverage" in text
    assert "complete_window_coverage_label=balanced_complete_window_coverage" in text
    assert "recorded_missing_window_duration_share=0.6154" in text
    assert "missing_window_duration_share_delta=0.3846" in text
    assert "missing_window_gap_delta_max=1.0" in text
    assert "missing_window_gap_delta_max=0" in text
    assert "missing_window_gap_delta_max=0.5" in text
    assert "missing_window_gap_source=count_and_duration_missing_summary_gap_source" in text
    assert "missing_window_gap_source=no_missing_summary_gap_source" in text
    assert "missing_window_gap_source=count_share_missing_summary_gap_source" in text
    assert "missing_window_gap_duration_minus_count_delta=0.0" in text
    assert "missing_window_gap_duration_minus_count_delta=-0.1154" in text
    assert "missing_window_gap_duration_minus_count_delta_abs=0.0" in text
    assert "missing_window_gap_duration_minus_count_delta_abs=0.1154" in text
    assert "missing_window_gap_delta_comparison_label=balanced_missing_summary_gap_signals" in text
    assert "missing_window_gap_delta_comparison_label=count_share_missing_summary_gap_higher" in text
    assert "missing_window_gap_delta_comparison_attention_label=no_missing_summary_gap_signal_divergence" in text
    assert "missing_window_gap_delta_comparison_attention_label=low_missing_summary_gap_signal_divergence" in text
    assert "missing_window_gap_delta_comparison_attention_rank=0" in text
    assert "missing_window_gap_delta_comparison_attention_rank=1" in text
    assert "missing_window_gap_delta_comparison_attention_required=False" in text
    assert "missing_window_gap_delta_comparison_attention_required=True" in text
    assert "missing_window_gap_delta_comparison_attention_status=no_missing_summary_gap_signal_attention_needed" in text
    assert "missing_window_gap_delta_comparison_attention_status=missing_summary_gap_signal_attention_needed" in text
    assert "missing_window_gap_delta_comparison_attention_trigger=no_missing_summary_gap_signal_attention_trigger" in text
    assert "missing_window_gap_delta_comparison_attention_trigger=count_share_missing_summary_gap_signal_attention_trigger" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal=none" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal=count_share" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_label=no_missing_summary_gap_signal_family" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_label=count_share_missing_summary_gap_signal_family" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_rank=0" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_rank=1" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_required=False" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_required=True" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_status=no_missing_summary_gap_trigger_signal_attention_needed" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_status=missing_summary_gap_trigger_signal_attention_needed" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_action=no_missing_summary_gap_trigger_signal_action" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_action=review_count_share_missing_summary_gap_signal" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_action_label=no_missing_summary_gap_trigger_signal_review_action" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_action_label=count_share_missing_summary_gap_signal_review_action" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_label=no_priority_missing_summary_gap_trigger_signal_review_action" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_label=low_priority_missing_summary_gap_trigger_signal_review_action" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_rank=0" in text
    assert "missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_rank=1" in text
    assert "missing_window_duration_delta_ms=150" in text
    assert "missing_window_duration_delta_ms=-80" in text
    assert "missing_window_duration_delta_ms=70" in text
    assert "missing_window_duration_delta_label=missing_summary_missing_window_duration_higher" in text
    assert "missing_window_duration_delta_label=recorded_summary_missing_window_duration_higher" in text
    assert "missing_window_duration_delta_abs_ms=150" in text
    assert "missing_window_duration_delta_abs_ms=80" in text
    assert "missing_window_duration_delta_abs_ms=70" in text
    assert "complete_window_duration_total_ms=50" in text
    assert "complete_window_duration_total_ms=0" in text
    assert "complete_window_duration_total_share=0.25" in text
    assert "complete_window_duration_total_share=0.0" in text
    assert "complete_window_duration_total_share=0.1786" in text
    assert "complete_window_duration_delta_ms=-50" in text
    assert "complete_window_duration_delta_ms=0" in text
    assert "complete_window_duration_delta_label=recorded_summary_complete_window_duration_higher" in text
    assert "complete_window_duration_delta_label=balanced_complete_window_duration_delta" in text
    assert "complete_window_duration_delta_abs_ms=50" in text
    assert "complete_window_duration_delta_abs_ms=0" in text
    assert "complete_window_duration_delta_abs_share=1.0" in text
    assert "complete_window_duration_delta_abs_share=0" in text
    assert "complete_window_duration_delta_share=-1.0" in text
    assert "complete_window_duration_delta_share=0" in text
    assert "complete_window_duration_ratio=0" in text
    assert "complete_window_duration_ratio_label=recorded_summary_only_complete_window_duration" in text
    assert "complete_window_duration_ratio_label=no_complete_window_duration" in text
    assert "missing_window_duration_total_ms=150" in text
    assert "missing_window_duration_total_ms=80" in text
    assert "missing_window_duration_total_ms=230" in text
    assert "missing_window_duration_total_share=0.75" in text
    assert "missing_window_duration_total_share=1.0" in text
    assert "missing_window_duration_total_share=0.8214" in text
    assert "missing_window_duration_delta_abs_share=1.0" in text
    assert "missing_window_duration_delta_abs_share=0.3043" in text
    assert "missing_window_duration_delta_share=1.0" in text
    assert "missing_window_duration_delta_share=-1.0" in text
    assert "missing_window_duration_delta_share=0.3043" in text
    assert "missing_window_excess_count=1" in text
    assert "missing_window_excess_share=0.5" in text
    assert "missing_window_excess_duration_ms=70" in text
    assert "missing_window_excess_duration_share=0.25" in text
    assert "missing_window_excess_missing_duration_share=0.4667" in text
    assert "missing_window_duration_ratio=1.875" in text
    assert "missing_window_duration_ratio=None" in text
    assert "missing_window_duration_ratio_label=missing_summary_duration_elevated" in text
    assert "missing_window_duration_ratio_label=missing_summary_only_missing_window_duration" in text
    assert "missing_window_excess_average_duration_ms=150.0" in text
    assert "missing_window_excess_average_duration_ms=0" in text
    assert "missing_window_excess_attention_label=medium_missing_summary_window_excess" in text
    assert "missing_window_gap_label=high_missing_summary_gap" in text
    assert "activity=recorded_complete_windows=1/missing_complete_windows=0/complete_window_count_delta=-1/complete_window_count_delta_abs=1/complete_window_count_delta_abs_share=1.0/complete_window_count_delta_share=-1.0/complete_window_count_delta_label=recorded_summary_complete_window_count_higher/complete_window_count_delta_attention_label=high_complete_window_count_delta/recorded_missing_windows=1/missing_missing_windows=1" in text


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
            {
                "id": "evt_cmd_top_level_summary",
                "seq": 3,
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:06Z",
                "ended_at": "2026-04-25T00:00:06.025Z",
                "duration_ms": 25,
                "summary": "Run focused auth tests",
                "command": {"value": "pytest tests/test_auth.py -q", "cwd": "/workspace/app"},
                "exit_code": 0,
            },
            {
                "id": "evt_edit_top_level_summary",
                "seq": 4,
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:07Z",
                "ended_at": "2026-04-25T00:00:07.100Z",
                "duration_ms": 100,
                "summary": "Document auth error handling behavior",
                "file": {"path": "docs/auth.md"},
                "change": {"kind": "modify", "added_lines": 3, "removed_lines": 0},
            },
        ],
    }
    payload = build_json_summary(trace)
    assert payload["command_timing"] == [
        {
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
        },
        {
            "event": "evt_cmd_top_level_summary",
            "command": "pytest tests/test_auth.py -q",
            "cwd": "/workspace/app",
            "status": "succeeded",
            "duration_ms": 25,
            "duration_source": "explicit",
            "exit_code": 0,
            "summary": "Run focused auth tests",
            "summary_source": "event.summary",
            "started_at": "2026-04-25T00:00:06Z",
            "ended_at": "2026-04-25T00:00:06.025Z",
        },
    ]
    assert payload["edit_summary"] == [
        {
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
        },
        {
            "event": "evt_edit_top_level_summary",
            "path": "docs/auth.md",
            "kind": "modify",
            "status": "succeeded",
            "duration_ms": 100,
            "duration_source": "explicit",
            "added_lines": 3,
            "removed_lines": 0,
            "summary": "Document auth error handling behavior",
            "summary_source": "event.summary",
            "net_line_delta": 3,
            "started_at": "2026-04-25T00:00:07Z",
            "ended_at": "2026-04-25T00:00:07.100Z",
        },
    ]
    assert payload["run_summary"]["command_durations_ms"][0]["duration_ms"] == 3200
    assert payload["run_summary"]["command_durations_ms"][1]["summary"] == "Run focused auth tests"
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
        "cwd": "/workspace/app",
    }]
    assert payload["command_timing"][1] == {
        "event": "evt_cmd_top_level_summary",
        "command": "pytest tests/test_auth.py -q",
        "cwd": "/workspace/app",
        "status": "succeeded",
        "duration_ms": 25,
        "duration_source": "explicit",
        "exit_code": 0,
        "summary": "Run focused auth tests",
        "summary_source": "event.summary",
        "started_at": "2026-04-25T00:00:06Z",
        "ended_at": "2026-04-25T00:00:06.025Z",
    }
    assert payload["edit_summary"][1] == {
        "event": "evt_edit_top_level_summary",
        "path": "docs/auth.md",
        "kind": "modify",
        "status": "succeeded",
        "duration_ms": 100,
        "duration_source": "explicit",
        "added_lines": 3,
        "removed_lines": 0,
        "summary": "Document auth error handling behavior",
        "summary_source": "event.summary",
        "net_line_delta": 3,
        "started_at": "2026-04-25T00:00:07Z",
        "ended_at": "2026-04-25T00:00:07.100Z",
    }
    assert payload["run_summary"]["command_durations_ms"][1]["summary_source"] == "event.summary"
    assert payload["run_summary"]["edit_summaries"][1]["summary_source"] == "event.summary"
    assert payload["activity_timeline"][2]["summary_source"] == "event.summary"
    assert payload["activity_timeline"][3]["summary_source"] == "event.summary"
    assert payload["activity_timeline_summary"]["last_activity"]["summary_source"] == "event.summary"
    assert payload["activity_timeline_summary"]["summary_source_counts"] == {"nested_or_inline": 1, "event.summary": 2}
    assert payload["report_summary_source_counts"] == {
        "command": {"event.summary": 1},
        "command_by_duration_source": {"explicit": {"event.summary": 1}},
        "command_by_status": {"failed": {}, "succeeded": {"event.summary": 1}},
        "command_by_command": {"pytest tests/test_auth.py -q": {"event.summary": 1}},
        "command_by_cwd": {"/workspace/app": {"event.summary": 1}},
        "command_by_exit_code": {"0": {"event.summary": 1}, "1": {}},
        "edit": {"nested_or_inline": 1, "event.summary": 1},
        "edit_by_duration_source": {"explicit": {"nested_or_inline": 1, "event.summary": 1}},
        "edit_by_status": {"succeeded": {"nested_or_inline": 1, "event.summary": 1}},
        "edit_by_kind": {"modify": {"nested_or_inline": 1, "event.summary": 1}},
        "edit_by_path": {
            "src/auth.py": {"nested_or_inline": 1},
            "docs/auth.md": {"event.summary": 1},
        },
        "activity": {"nested_or_inline": 1, "event.summary": 2},
        "activity_by_type": {
            "command": {"event.summary": 1},
            "file_edit": {"nested_or_inline": 1, "event.summary": 1},
        },
        "activity_by_status": {
            "failed": {},
            "succeeded": {"nested_or_inline": 1, "event.summary": 2},
        },
        "activity_by_duration_source": {"explicit": {"nested_or_inline": 1, "event.summary": 2}},
        "activity_by_identity": {
            "command:pytest tests/test_auth.py -q": {"event.summary": 1},
            "file_edit:src/auth.py": {"nested_or_inline": 1},
            "file_edit:docs/auth.md": {"event.summary": 1},
        },
    }
    assert payload["report_timing_window_coverage"] == {
        "command": {
            "timing_row_count": 2,
            "started_at_count": 2,
            "ended_at_count": 1,
            "started_only_count": 1,
            "ended_only_count": 0,
            "missing_started_at_count": 0,
            "missing_ended_at_count": 1,
            "complete_window_count": 1,
            "missing_window_count": 1,
            "complete_window_ratio": 0.5,
            "complete_window_duration_ms": 25,
            "complete_window_duration_share": 0.0078,
            "missing_window_duration_ms": 3200,
            "missing_window_duration_share": 0.9922,
            "partial_timestamp_window_duration_ms": {"started_only": 3200, "ended_only": 0, "missing_both": 0},
            "timestamp_window_total_ms": 25,
            "timestamp_window_average_ms": 25.0,
            "timestamp_window_extremes_ms": {"min": 25, "max": 25},
            "largest_timestamp_window_ms": 25,
            "largest_timestamp_window_example": {
                "event": "evt_cmd_top_level_summary",
                "status": "succeeded",
                "duration_ms": 25,
                "duration_source": "explicit",
                "command": "pytest tests/test_auth.py -q",
                "cwd": "/workspace/app",
                "exit_code": 0,
                "started_at": "2026-04-25T00:00:06Z",
                "ended_at": "2026-04-25T00:00:06.025Z",
                "summary": "Run focused auth tests",
                "summary_source": "event.summary",
                "timestamp_window_ms": 25,
                "duration_window_delta_ms": 0,
                "duration_window_delta_abs_ms": 0,
            },
            "missing_timestamp_window_examples": [
                {
                    "event": "evt_cmd",
                    "status": "failed",
                    "duration_ms": 3200,
                    "duration_source": "explicit",
                    "command": "pytest tests/test_auth.py -q",
                    "cwd": "/workspace/app",
                    "exit_code": 1,
                    "started_at": "2026-04-25T00:00:01Z",
                    "missing_ended_at": True,
                }
            ],
            "partial_timestamp_window_examples": {
                "started_only": [
                    {
                        "event": "evt_cmd",
                        "status": "failed",
                        "duration_ms": 3200,
                        "duration_source": "explicit",
                        "command": "pytest tests/test_auth.py -q",
                        "cwd": "/workspace/app",
                        "exit_code": 1,
                        "started_at": "2026-04-25T00:00:01Z",
                        "missing_ended_at": True,
                    }
                ],
                "ended_only": [],
                "missing_both": [],
            },
            "duration_window_comparable_count": 1,
            "duration_window_delta_total_ms": 0,
            "duration_window_delta_abs_total_ms": 0,
            "duration_window_delta_average_ms": 0.0,
            "duration_window_delta_abs_average_ms": 0.0,
            "duration_window_delta_abs_recorded_duration_share": 0.0,
            "duration_window_delta_consistency_label": "matched",
            "duration_window_delta_direction_counts": {
                "matches": 1,
                "duration_exceeds_window": 0,
                "window_exceeds_duration": 0,
            },
            "duration_window_delta_direction_examples": {
                "matches": [
                    {
                        "event": "evt_cmd_top_level_summary",
                        "status": "succeeded",
                        "duration_ms": 25,
                        "duration_source": "explicit",
                        "command": "pytest tests/test_auth.py -q",
                        "cwd": "/workspace/app",
                        "exit_code": 0,
                        "started_at": "2026-04-25T00:00:06Z",
                        "ended_at": "2026-04-25T00:00:06.025Z",
                        "summary": "Run focused auth tests",
                        "summary_source": "event.summary",
                        "timestamp_window_ms": 25,
                        "duration_window_delta_ms": 0,
                        "duration_window_delta_abs_ms": 0,
                    }
                ],
                "duration_exceeds_window": [],
                "window_exceeds_duration": [],
            },
            "largest_duration_window_delta_ms": 0,
            "largest_duration_window_delta_example": {
                "event": "evt_cmd_top_level_summary",
                "status": "succeeded",
                "duration_ms": 25,
                "duration_source": "explicit",
                "command": "pytest tests/test_auth.py -q",
                "cwd": "/workspace/app",
                "exit_code": 0,
                "started_at": "2026-04-25T00:00:06Z",
                "ended_at": "2026-04-25T00:00:06.025Z",
                "summary": "Run focused auth tests",
                "summary_source": "event.summary",
                "timestamp_window_ms": 25,
                "duration_window_delta_ms": 0,
                "duration_window_delta_abs_ms": 0,
            },
        },
        "edit": {
            "timing_row_count": 2,
            "started_at_count": 2,
            "ended_at_count": 1,
            "started_only_count": 1,
            "ended_only_count": 0,
            "missing_started_at_count": 0,
            "missing_ended_at_count": 1,
            "complete_window_count": 1,
            "missing_window_count": 1,
            "complete_window_ratio": 0.5,
            "complete_window_duration_ms": 100,
            "complete_window_duration_share": 0.1667,
            "missing_window_duration_ms": 500,
            "missing_window_duration_share": 0.8333,
            "partial_timestamp_window_duration_ms": {"started_only": 500, "ended_only": 0, "missing_both": 0},
            "timestamp_window_total_ms": 100,
            "timestamp_window_average_ms": 100.0,
            "timestamp_window_extremes_ms": {"min": 100, "max": 100},
            "largest_timestamp_window_ms": 100,
            "largest_timestamp_window_example": {
                "event": "evt_edit_top_level_summary",
                "status": "succeeded",
                "duration_ms": 100,
                "duration_source": "explicit",
                "path": "docs/auth.md",
                "kind": "modify",
                "added_lines": 3,
                "removed_lines": 0,
                "net_line_delta": 3,
                "started_at": "2026-04-25T00:00:07Z",
                "ended_at": "2026-04-25T00:00:07.100Z",
                "summary": "Document auth error handling behavior",
                "summary_source": "event.summary",
                "timestamp_window_ms": 100,
                "duration_window_delta_ms": 0,
                "duration_window_delta_abs_ms": 0,
            },
            "missing_timestamp_window_examples": [
                {
                    "event": "evt_edit",
                    "status": "succeeded",
                    "duration_ms": 500,
                    "duration_source": "explicit",
                    "path": "src/auth.py",
                    "kind": "modify",
                    "added_lines": 4,
                    "removed_lines": 1,
                    "net_line_delta": 3,
                    "started_at": "2026-04-25T00:00:05Z",
                    "summary": "Translate decoder errors into 401 responses",
                    "missing_ended_at": True,
                }
            ],
            "partial_timestamp_window_examples": {
                "started_only": [
                    {
                        "event": "evt_edit",
                        "status": "succeeded",
                        "duration_ms": 500,
                        "duration_source": "explicit",
                        "path": "src/auth.py",
                        "kind": "modify",
                        "added_lines": 4,
                        "removed_lines": 1,
                        "net_line_delta": 3,
                        "started_at": "2026-04-25T00:00:05Z",
                        "summary": "Translate decoder errors into 401 responses",
                        "missing_ended_at": True,
                    }
                ],
                "ended_only": [],
                "missing_both": [],
            },
            "duration_window_comparable_count": 1,
            "duration_window_delta_total_ms": 0,
            "duration_window_delta_abs_total_ms": 0,
            "duration_window_delta_average_ms": 0.0,
            "duration_window_delta_abs_average_ms": 0.0,
            "duration_window_delta_abs_recorded_duration_share": 0.0,
            "duration_window_delta_consistency_label": "matched",
            "duration_window_delta_direction_counts": {
                "matches": 1,
                "duration_exceeds_window": 0,
                "window_exceeds_duration": 0,
            },
            "duration_window_delta_direction_examples": {
                "matches": [
                    {
                        "event": "evt_edit_top_level_summary",
                        "status": "succeeded",
                        "duration_ms": 100,
                        "duration_source": "explicit",
                        "path": "docs/auth.md",
                        "kind": "modify",
                        "added_lines": 3,
                        "removed_lines": 0,
                        "net_line_delta": 3,
                        "started_at": "2026-04-25T00:00:07Z",
                        "ended_at": "2026-04-25T00:00:07.100Z",
                        "summary": "Document auth error handling behavior",
                        "summary_source": "event.summary",
                        "timestamp_window_ms": 100,
                        "duration_window_delta_ms": 0,
                        "duration_window_delta_abs_ms": 0,
                    }
                ],
                "duration_exceeds_window": [],
                "window_exceeds_duration": [],
            },
            "largest_duration_window_delta_ms": 0,
            "largest_duration_window_delta_example": {
                "event": "evt_edit_top_level_summary",
                "status": "succeeded",
                "duration_ms": 100,
                "duration_source": "explicit",
                "path": "docs/auth.md",
                "kind": "modify",
                "added_lines": 3,
                "removed_lines": 0,
                "net_line_delta": 3,
                "started_at": "2026-04-25T00:00:07Z",
                "ended_at": "2026-04-25T00:00:07.100Z",
                "summary": "Document auth error handling behavior",
                "summary_source": "event.summary",
                "timestamp_window_ms": 100,
                "duration_window_delta_ms": 0,
                "duration_window_delta_abs_ms": 0,
            },
        },
        "activity": {
            "timing_row_count": 4,
            "started_at_count": 4,
            "ended_at_count": 2,
            "started_only_count": 2,
            "ended_only_count": 0,
            "missing_started_at_count": 0,
            "missing_ended_at_count": 2,
            "complete_window_count": 2,
            "missing_window_count": 2,
            "complete_window_ratio": 0.5,
            "complete_window_duration_ms": 125,
            "complete_window_duration_share": 0.0327,
            "missing_window_duration_ms": 3700,
            "missing_window_duration_share": 0.9673,
            "partial_timestamp_window_duration_ms": {"started_only": 3700, "ended_only": 0, "missing_both": 0},
            "timestamp_window_total_ms": 125,
            "timestamp_window_average_ms": 62.5,
            "timestamp_window_extremes_ms": {"min": 25, "max": 100},
            "largest_timestamp_window_ms": 100,
            "largest_timestamp_window_example": {
                "event": "evt_edit_top_level_summary",
                "status": "succeeded",
                "duration_ms": 100,
                "duration_source": "explicit",
                "type": "file_edit",
                "path": "docs/auth.md",
                "kind": "modify",
                "added_lines": 3,
                "removed_lines": 0,
                "net_line_delta": 3,
                "started_at": "2026-04-25T00:00:07Z",
                "ended_at": "2026-04-25T00:00:07.100Z",
                "summary": "Document auth error handling behavior",
                "summary_source": "event.summary",
                "timestamp_window_ms": 100,
                "duration_window_delta_ms": 0,
                "duration_window_delta_abs_ms": 0,
            },
            "missing_timestamp_window_examples": [
                {
                    "event": "evt_cmd",
                    "status": "failed",
                    "duration_ms": 3200,
                    "duration_source": "explicit",
                    "type": "command",
                    "command": "pytest tests/test_auth.py -q",
                    "cwd": "/workspace/app",
                    "exit_code": 1,
                    "started_at": "2026-04-25T00:00:01Z",
                    "missing_ended_at": True,
                },
                {
                    "event": "evt_edit",
                    "status": "succeeded",
                    "duration_ms": 500,
                    "duration_source": "explicit",
                    "type": "file_edit",
                    "path": "src/auth.py",
                    "kind": "modify",
                    "added_lines": 4,
                    "removed_lines": 1,
                    "net_line_delta": 3,
                    "started_at": "2026-04-25T00:00:05Z",
                    "summary": "Translate decoder errors into 401 responses",
                    "missing_ended_at": True,
                },
            ],
            "partial_timestamp_window_examples": {
                "started_only": [
                    {
                        "event": "evt_cmd",
                        "status": "failed",
                        "duration_ms": 3200,
                        "duration_source": "explicit",
                        "type": "command",
                        "command": "pytest tests/test_auth.py -q",
                        "cwd": "/workspace/app",
                        "exit_code": 1,
                        "started_at": "2026-04-25T00:00:01Z",
                        "missing_ended_at": True,
                    },
                    {
                        "event": "evt_edit",
                        "status": "succeeded",
                        "duration_ms": 500,
                        "duration_source": "explicit",
                        "type": "file_edit",
                        "path": "src/auth.py",
                        "kind": "modify",
                        "added_lines": 4,
                        "removed_lines": 1,
                        "net_line_delta": 3,
                        "started_at": "2026-04-25T00:00:05Z",
                        "summary": "Translate decoder errors into 401 responses",
                        "missing_ended_at": True,
                    },
                ],
                "ended_only": [],
                "missing_both": [],
            },
            "duration_window_comparable_count": 2,
            "duration_window_delta_total_ms": 0,
            "duration_window_delta_abs_total_ms": 0,
            "duration_window_delta_average_ms": 0.0,
            "duration_window_delta_abs_average_ms": 0.0,
            "duration_window_delta_abs_recorded_duration_share": 0.0,
            "duration_window_delta_consistency_label": "matched",
            "duration_window_delta_direction_counts": {
                "matches": 2,
                "duration_exceeds_window": 0,
                "window_exceeds_duration": 0,
            },
            "duration_window_delta_direction_examples": {
                "matches": [
                    {
                        "event": "evt_cmd_top_level_summary",
                        "status": "succeeded",
                        "duration_ms": 25,
                        "duration_source": "explicit",
                        "type": "command",
                        "command": "pytest tests/test_auth.py -q",
                        "cwd": "/workspace/app",
                        "exit_code": 0,
                        "started_at": "2026-04-25T00:00:06Z",
                        "ended_at": "2026-04-25T00:00:06.025Z",
                        "summary": "Run focused auth tests",
                        "summary_source": "event.summary",
                        "timestamp_window_ms": 25,
                        "duration_window_delta_ms": 0,
                        "duration_window_delta_abs_ms": 0,
                    },
                    {
                        "event": "evt_edit_top_level_summary",
                        "status": "succeeded",
                        "duration_ms": 100,
                        "duration_source": "explicit",
                        "type": "file_edit",
                        "path": "docs/auth.md",
                        "kind": "modify",
                        "added_lines": 3,
                        "removed_lines": 0,
                        "net_line_delta": 3,
                        "started_at": "2026-04-25T00:00:07Z",
                        "ended_at": "2026-04-25T00:00:07.100Z",
                        "summary": "Document auth error handling behavior",
                        "summary_source": "event.summary",
                        "timestamp_window_ms": 100,
                        "duration_window_delta_ms": 0,
                        "duration_window_delta_abs_ms": 0,
                    },
                ],
                "duration_exceeds_window": [],
                "window_exceeds_duration": [],
            },
            "largest_duration_window_delta_ms": 0,
            "largest_duration_window_delta_example": {
                "event": "evt_cmd_top_level_summary",
                "status": "succeeded",
                "duration_ms": 25,
                "duration_source": "explicit",
                "type": "command",
                "command": "pytest tests/test_auth.py -q",
                "cwd": "/workspace/app",
                "exit_code": 0,
                "started_at": "2026-04-25T00:00:06Z",
                "ended_at": "2026-04-25T00:00:06.025Z",
                "summary": "Run focused auth tests",
                "summary_source": "event.summary",
                "timestamp_window_ms": 25,
                "duration_window_delta_ms": 0,
                "duration_window_delta_abs_ms": 0,
            },
        },
    }
    assert payload["command_timing_summary"]["summary_source_counts"] == {"event.summary": 1}
    assert payload["edit_summary_totals"]["summary_source_counts"] == {"nested_or_inline": 1, "event.summary": 1}

    text = build_markdown_summary(trace)
    assert "activity_timeline_summary: count=4" in text
    assert "summary_source_counts=event.summary=2, nested_or_inline=1" in text
    assert "report_summary_source_counts: command=event.summary=1; command_by_duration_source=explicit=event.summary=1; command_by_status=failed=none, succeeded=event.summary=1; command_by_command=pytest tests/test_auth.py -q=event.summary=1; command_by_cwd=/workspace/app=event.summary=1; command_by_exit_code=0=event.summary=1, 1=none; edit=event.summary=1, nested_or_inline=1; edit_by_duration_source=explicit=event.summary=1, nested_or_inline=1; edit_by_status=succeeded=event.summary=1, nested_or_inline=1; edit_by_kind=modify=event.summary=1, nested_or_inline=1; edit_by_path=docs/auth.md=event.summary=1, src/auth.py=nested_or_inline=1; activity=event.summary=2, nested_or_inline=1; activity_by_type=command=event.summary=1, file_edit=event.summary=1, nested_or_inline=1; activity_by_status=failed=none, succeeded=event.summary=2, nested_or_inline=1; activity_by_duration_source=explicit=event.summary=2, nested_or_inline=1; activity_by_identity=command:pytest tests/test_auth.py -q=event.summary=1, file_edit:docs/auth.md=event.summary=1, file_edit:src/auth.py=nested_or_inline=1" in text
    assert "report_timing_window_coverage: command=rows=2/started_at=2/ended_at=1/started_only=1/ended_only=0/missing_started_at=0/missing_ended_at=1/complete_windows=1/missing_windows=1/complete_window_ratio=0.5/complete_window_duration_ms=25/complete_window_duration_share=0.0078/missing_window_duration_ms=3200/missing_window_duration_share=0.9922/partial_timestamp_window_duration_ms=ended_only=0, missing_both=0, started_only=3200/timestamp_window_total_ms=25/timestamp_window_average_ms=25.0" in text
    assert "edit=rows=2/started_at=2/ended_at=1/started_only=1/ended_only=0/missing_started_at=0/missing_ended_at=1/complete_windows=1/missing_windows=1/complete_window_ratio=0.5/complete_window_duration_ms=100/complete_window_duration_share=0.1667/missing_window_duration_ms=500/missing_window_duration_share=0.8333/partial_timestamp_window_duration_ms=ended_only=0, missing_both=0, started_only=500/timestamp_window_total_ms=100/timestamp_window_average_ms=100.0" in text
    assert "activity=rows=4/started_at=4/ended_at=2/started_only=2/ended_only=0/missing_started_at=0/missing_ended_at=2/complete_windows=2/missing_windows=2/complete_window_ratio=0.5/complete_window_duration_ms=125/complete_window_duration_share=0.0327/missing_window_duration_ms=3700/missing_window_duration_share=0.9673/partial_timestamp_window_duration_ms=ended_only=0, missing_both=0, started_only=3700/timestamp_window_total_ms=125/timestamp_window_average_ms=62.5" in text
    assert "largest_timestamp_window_example=docs/auth.md (event=evt_edit_top_level_summary, status=succeeded, duration_ms=100, duration_source=explicit, kind=modify, net=3, timestamp_window_ms=100, duration_window_delta_ms=0, duration_window_delta_abs_ms=0, summary=Document auth error handling behavior, summary_source=event.summary)" in text
    assert "duration_window_comparable_count=2/duration_window_delta_total_ms=0/duration_window_delta_abs_total_ms=0" in text
    assert "duration_window_delta_abs_recorded_duration_share=0.0/duration_window_delta_consistency_label=matched" in text
    assert "duration_window_delta_direction_counts=duration_exceeds_window=0, matches=2, window_exceeds_duration=0" in text
    assert "partial_timestamp_window_examples=started_only=`pytest tests/test_auth.py -q` (event=evt_cmd" in text
    assert "ended_only=none, missing_both=none" in text
    assert "command_summary_source_counts: event.summary=1" in text
    assert "edit_summary_source_counts: event.summary=1, nested_or_inline=1" in text


def test_timing_window_delta_direction_examples_show_mismatch_context():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "timing-direction-examples", "task": "inspect timing mismatches", "status": "failed"},
        "events": [
            {
                "id": "evt_duration_long",
                "type": "command",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:00.100Z",
                "duration_ms": 150,
                "summary": "Run short command",
                "command": {"value": "python short.py", "cwd": "/workspace/app"},
                "exit_code": 0,
            },
            {
                "id": "evt_window_long",
                "type": "file_edit",
                "status": "succeeded",
                "started_at": "2026-04-25T00:00:01Z",
                "ended_at": "2026-04-25T00:00:01.250Z",
                "duration_ms": 200,
                "summary": "Patch report",
                "file": {"path": "src/report.py"},
                "change": {"kind": "modify", "added_lines": 2, "removed_lines": 1},
            },
        ],
    }

    payload = build_json_summary(trace)
    activity_coverage = payload["report_timing_window_coverage"]["activity"]
    assert activity_coverage["duration_window_delta_abs_recorded_duration_share"] == 0.2857
    assert activity_coverage["duration_window_delta_consistency_label"] == "high_delta"
    assert activity_coverage["duration_window_delta_direction_counts"] == {
        "matches": 0,
        "duration_exceeds_window": 1,
        "window_exceeds_duration": 1,
    }
    assert activity_coverage["duration_window_delta_direction_examples"]["duration_exceeds_window"] == [{
        "event": "evt_duration_long",
        "status": "succeeded",
        "duration_ms": 150,
        "duration_source": "explicit",
        "type": "command",
        "command": "python short.py",
        "cwd": "/workspace/app",
        "exit_code": 0,
        "started_at": "2026-04-25T00:00:00Z",
        "ended_at": "2026-04-25T00:00:00.100Z",
        "summary": "Run short command",
        "summary_source": "event.summary",
        "timestamp_window_ms": 100,
        "duration_window_delta_ms": 50,
        "duration_window_delta_abs_ms": 50,
    }]
    assert activity_coverage["duration_window_delta_direction_examples"]["window_exceeds_duration"] == [{
        "event": "evt_window_long",
        "status": "succeeded",
        "duration_ms": 200,
        "duration_source": "explicit",
        "type": "file_edit",
        "path": "src/report.py",
        "kind": "modify",
        "added_lines": 2,
        "removed_lines": 1,
        "net_line_delta": 1,
        "started_at": "2026-04-25T00:00:01Z",
        "ended_at": "2026-04-25T00:00:01.250Z",
        "summary": "Patch report",
        "summary_source": "event.summary",
        "timestamp_window_ms": 250,
        "duration_window_delta_ms": -50,
        "duration_window_delta_abs_ms": 50,
    }]

    text = build_markdown_summary(trace)
    assert "duration_window_delta_abs_recorded_duration_share=0.2857/duration_window_delta_consistency_label=high_delta" in text
    assert "duration_window_delta_direction_examples=matches=none, duration_exceeds_window=`python short.py`" in text
    assert "window_exceeds_duration=src/report.py (event=evt_window_long" in text


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
                "artifacts": [{"kind": "stdout", "path": "artifacts/evt_cmd_stdout.txt"}],
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
        {"kind": "command_log", "path": "artifacts/evt_cmd_log.log"},
        {"kind": "stdout", "path": "artifacts/evt_cmd_stdout.txt"},
    ]
    assert payload["command_timing_summary"]["summary_missing_examples"] == [{
        "event": "evt_cmd_log",
        "status": "failed",
        "duration_ms": 50,
        "duration_source": "explicit",
        "command": "pytest -q",
        "cwd": "/workspace/app",
        "exit_code": 1,
        "artifacts": [
            {"kind": "command_log", "path": "artifacts/evt_cmd_log.log"},
            {"kind": "stdout", "path": "artifacts/evt_cmd_stdout.txt"},
        ],
    }]
    assert payload["edit_summary"][0]["artifacts"] == [
        {"kind": "diff", "path": "artifacts/evt_diff.diff"}
    ]
    assert payload["edit_summary_totals"]["summary_examples"] == [{
        "event": "evt_diff",
        "status": "succeeded",
        "duration_ms": 2,
        "duration_source": "explicit",
        "summary": "Surface linked artifacts",
        "path": "src/report.py",
        "kind": "modify",
        "added_lines": 3,
        "removed_lines": 1,
        "net_line_delta": 2,
        "artifacts": [{"kind": "diff", "path": "artifacts/evt_diff.diff"}],
    }]

    text = build_markdown_summary(trace)
    assert "artifacts: command_log=artifacts/evt_cmd_log.log; stdout=artifacts/evt_cmd_stdout.txt" in text
    assert "artifacts: diff=artifacts/evt_diff.diff" in text
    assert "command_summary_missing_examples: `pytest -q` (event=evt_cmd_log, status=failed, duration_ms=50, duration_source=explicit, cwd=/workspace/app, exit_code=1, artifacts=command_log=artifacts/evt_cmd_log.log; stdout=artifacts/evt_cmd_stdout.txt)" in text
    assert "edit_summary_examples: src/report.py (event=evt_diff, status=succeeded, duration_ms=2, duration_source=explicit, kind=modify, net=2, artifacts=diff=artifacts/evt_diff.diff, summary=Surface linked artifacts)" in text


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
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
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
        {"kind": "command_log", "path": "artifacts/evt_cmd_failed_log.log"},
        {"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"},
    ]
    assert payload["edit_summary_totals"]["failed_edits"][0]["artifacts"] == [
        {"kind": "diff", "path": "artifacts/evt_edit_failed_diff.diff"}
    ]

    text = build_markdown_summary(trace)
    assert "failed_commands: evt_cmd_failed_log: `pytest -q` (80ms, status=failed, exit_code=1, duration_source=explicit, stderr_preview=AssertionError: expected 401, artifacts=command_log=artifacts/evt_cmd_failed_log.log; command_log=artifacts/evt_cmd_early_log.log)" in text
    assert "failed_edits: evt_edit_failed_diff: src/auth.py (kind=modify, +0/-0, net=0, 5ms, status=failed, duration_source=explicit, summary=Patch auth handling, error_message=target hunk not found, artifacts=diff=artifacts/evt_edit_failed_diff.diff)" in text


def test_failed_command_aggregates_include_working_directory_context():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "failed-cwd-1", "task": "inspect failed cwd", "status": "failed"},
        "events": [
            {
                "id": "evt_cmd_failed_cwd",
                "seq": 1,
                "type": "command",
                "status": "failed",
                "duration_ms": 80,
                "command": {"value": "pytest -q", "cwd": "/workspace/app"},
                "exit_code": 1,
            },
        ],
    }

    payload = build_json_summary(trace)
    assert payload["command_timing_summary"]["failed_commands"][0]["cwd"] == "/workspace/app"

    text = build_markdown_summary(trace)
    assert "failed_commands: evt_cmd_failed_cwd: `pytest -q` (80ms, status=failed, exit_code=1, duration_source=explicit, cwd=/workspace/app)" in text


def test_command_summary_totals_break_down_duration_by_exit_code():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "exit-code-duration-1", "task": "inspect exit code timing", "status": "failed"},
        "events": [
            {
                "id": "evt_cmd_ok",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 20,
                "command": {"value": "ruff check", "summary": "Lint passed"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_fail_first",
                "seq": 2,
                "type": "command",
                "status": "failed",
                "duration_ms": 80,
                "command": {"value": "pytest -q", "summary": "Tests failed"},
                "exit_code": 1,
            },
            {
                "id": "evt_cmd_fail_retry",
                "seq": 3,
                "type": "command",
                "status": "failed",
                "started_at": "2026-04-25T00:00:00Z",
                "ended_at": "2026-04-25T00:00:00.100Z",
                "command": {"value": "pytest -q"},
                "exit_code": 1,
            },
            {
                "id": "evt_cmd_unknown_exit",
                "seq": 4,
                "type": "command",
                "status": "cancelled",
                "duration_ms": 5,
                "command": {"value": "npm test"},
            },
        ],
    }

    payload = build_json_summary(trace)
    command_totals = payload["command_timing_summary"]
    assert command_totals["exit_code_duration_ms"] == {"0": 20, "1": 180, "unknown": 5}
    assert command_totals["exit_code_average_duration_ms"] == {"0": 20.0, "1": 90.0, "unknown": 5.0}
    assert command_totals["exit_code_duration_extremes_ms"] == {
        "0": {"min": 20, "max": 20},
        "1": {"min": 80, "max": 100},
        "unknown": {"min": 5, "max": 5},
    }
    assert command_totals["exit_code_duration_coverage"] == {
        "0": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        "1": {"duration_recorded_count": 2, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        "unknown": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
    }
    assert command_totals["exit_code_duration_share"] == {"0": 0.0976, "1": 0.878, "unknown": 0.0244}
    assert command_totals["dominant_duration_exit_code"] == {"exit_code": "1", "duration_ms": 180, "duration_share": 0.878}
    assert command_totals["exit_code_summary_coverage"] == {
        "0": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
        "1": {"summary_recorded_count": 1, "summary_missing_count": 1, "summary_coverage_ratio": 0.5},
        "unknown": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
    }
    assert command_totals["status_summary_examples"]["failed"] == [{
        "event": "evt_cmd_fail_first",
        "status": "failed",
        "duration_ms": 80,
        "duration_source": "explicit",
        "summary": "Tests failed",
        "command": "pytest -q",
        "exit_code": 1,
    }]
    assert command_totals["status_summary_missing_examples"]["failed"] == [{
        "event": "evt_cmd_fail_retry",
        "status": "failed",
        "duration_ms": 100,
        "duration_source": "derived",
        "command": "pytest -q",
        "exit_code": 1,
    }]
    assert command_totals["cwd_summary_examples"]["unknown"][0]["summary"] == "Lint passed"
    assert command_totals["cwd_summary_missing_examples"]["unknown"][0]["command"] == "pytest -q"
    assert command_totals["command_summary_examples"]["pytest -q"] == [{
        "event": "evt_cmd_fail_first",
        "status": "failed",
        "duration_ms": 80,
        "duration_source": "explicit",
        "summary": "Tests failed",
        "command": "pytest -q",
        "exit_code": 1,
    }]
    assert command_totals["command_summary_missing_examples"]["pytest -q"][0]["event"] == "evt_cmd_fail_retry"
    assert command_totals["duration_source_summary_examples"]["explicit"][0]["summary"] == "Lint passed"
    assert command_totals["duration_source_summary_missing_examples"]["derived"][0]["event"] == "evt_cmd_fail_retry"

    text = build_markdown_summary(trace)
    assert "command_exit_code_duration_summary: exit_code_duration_ms=0=20, 1=180, unknown=5" in text
    assert "dominant_duration_exit_code=1 (180ms, share=0.878)" in text
    assert "exit_code_summary_coverage=0=recorded=1/missing=0/ratio=1.0, 1=recorded=1/missing=1/ratio=0.5, unknown=recorded=0/missing=1/ratio=0.0" in text
    assert "exit_code_summary_examples=0=`ruff check` (event=evt_cmd_ok, status=succeeded, duration_ms=20, duration_source=explicit, exit_code=0, summary=Lint passed); 1=`pytest -q` (event=evt_cmd_fail_first, status=failed, duration_ms=80, duration_source=explicit, exit_code=1, summary=Tests failed)" in text
    assert "exit_code_summary_missing_examples=1=`pytest -q` (event=evt_cmd_fail_retry, status=failed, duration_ms=100, duration_source=derived, exit_code=1); unknown=`npm test` (event=evt_cmd_unknown_exit, status=cancelled, duration_ms=5, duration_source=explicit)" in text
    assert "command_status_summary_examples: failed=`pytest -q` (event=evt_cmd_fail_first, status=failed, duration_ms=80, duration_source=explicit, exit_code=1, summary=Tests failed); succeeded=`ruff check`" in text
    assert "command_status_summary_missing_examples: cancelled=`npm test` (event=evt_cmd_unknown_exit, status=cancelled, duration_ms=5, duration_source=explicit); failed=`pytest -q` (event=evt_cmd_fail_retry, status=failed, duration_ms=100, duration_source=derived, exit_code=1)" in text
    assert "command_identity_summary_examples: pytest -q=`pytest -q` (event=evt_cmd_fail_first, status=failed, duration_ms=80, duration_source=explicit, exit_code=1, summary=Tests failed); ruff check=`ruff check`" in text
    assert "command_identity_summary_missing_examples: npm test=`npm test` (event=evt_cmd_unknown_exit, status=cancelled, duration_ms=5, duration_source=explicit); pytest -q=`pytest -q` (event=evt_cmd_fail_retry, status=failed, duration_ms=100, duration_source=derived, exit_code=1)" in text
    assert "command_duration_source_summary_examples: explicit=`ruff check` (event=evt_cmd_ok, status=succeeded, duration_ms=20, duration_source=explicit, exit_code=0, summary=Lint passed)" in text
    assert "command_duration_source_summary_missing_examples: derived=`pytest -q` (event=evt_cmd_fail_retry, status=failed, duration_ms=100, duration_source=derived, exit_code=1); explicit=`npm test`" in text


def test_slowest_command_largest_edit_and_edit_grouped_summary_examples():
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
    assert payload["edit_summary_totals"]["largest_edit"] == {
        "event": "evt_edit_largest_diff",
        "path": "src/large.py",
        "kind": "modify",
        "added_lines": 5,
        "removed_lines": 2,
        "net_line_delta": 3,
        "duration_ms": 3,
        "duration_source": "explicit",
        "status": "succeeded",
        "started_at": None,
        "ended_at": None,
        "summary": "Large edit",
        "artifacts": [
            {"kind": "diff", "path": "artifacts/evt_edit_largest_diff.diff"}
        ],
    }
    edit_totals = payload["edit_summary_totals"]
    assert edit_totals["kind_summary_examples"]["modify"][0]["summary"] == "Small edit"
    assert edit_totals["status_summary_examples"]["succeeded"][1]["path"] == "src/large.py"
    assert edit_totals["kind_summary_missing_examples"]["modify"] == []
    assert edit_totals["path_summary_examples"]["src/large.py"][0]["summary"] == "Large edit"
    assert edit_totals["path_summary_missing_examples"]["src/large.py"] == []
    assert edit_totals["duration_source_summary_examples"]["explicit"][0]["summary"] == "Small edit"
    assert edit_totals["duration_source_summary_missing_examples"]["explicit"] == []

    text = build_markdown_summary(trace)
    assert "slowest_command: evt_cmd_slowest_log: `pytest -q` (75ms, status=succeeded, exit_code=0, duration_source=explicit, artifacts=command_log=artifacts/evt_cmd_slowest_log.log)" in text
    assert "largest_edit: evt_edit_largest_diff: src/large.py (+5/-2, net=3, duration_ms=3, status=succeeded, duration_source=explicit, summary=Large edit, artifacts=diff=artifacts/evt_edit_largest_diff.diff)" in text
    assert "edit_path_summary_examples: src/large.py=src/large.py (event=evt_edit_largest_diff, status=succeeded, duration_ms=3, duration_source=explicit, kind=modify, net=3, artifacts=diff=artifacts/evt_edit_largest_diff.diff, summary=Large edit); src/small.py=src/small.py" in text
    assert "edit_path_summary_missing_examples: none" in text
    assert "edit_kind_summary_examples: modify=src/small.py (event=evt_edit_small, status=succeeded, duration_ms=2, duration_source=explicit, kind=modify, net=1, summary=Small edit); src/large.py" in text
    assert "edit_kind_summary_missing_examples: none" in text
    assert "edit_duration_source_summary_examples: explicit=src/small.py (event=evt_edit_small, status=succeeded, duration_ms=2, duration_source=explicit, kind=modify, net=1, summary=Small edit); src/large.py" in text
    assert "edit_duration_source_summary_missing_examples: none" in text


def test_command_highlight_aggregates_include_working_directory_context():
    trace = {
        "trace_version": "0.1",
        "run": {"id": "highlight-cwd-1", "task": "inspect command highlight cwd", "status": "succeeded"},
        "events": [
            {
                "id": "evt_cmd_setup",
                "seq": 1,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 20,
                "command": {"value": "python manage.py migrate", "cwd": "/workspace/api"},
                "exit_code": 0,
            },
            {
                "id": "evt_cmd_test",
                "seq": 2,
                "type": "command",
                "status": "succeeded",
                "duration_ms": 5,
                "command": {"value": "npm test", "cwd": "/workspace/web"},
                "exit_code": 0,
            },
        ],
    }

    payload = build_json_summary(trace)
    command_totals = payload["command_timing_summary"]
    assert command_totals["first"]["cwd"] == "/workspace/api"
    assert command_totals["slowest"]["cwd"] == "/workspace/api"
    assert command_totals["fastest"]["cwd"] == "/workspace/web"
    assert command_totals["last"]["cwd"] == "/workspace/web"

    text = build_markdown_summary(trace)
    assert "first_command: evt_cmd_setup: `python manage.py migrate` (20ms, status=succeeded, exit_code=0, duration_source=explicit, cwd=/workspace/api)" in text
    assert "fastest_command: evt_cmd_test: `npm test` (5ms, status=succeeded, exit_code=0, duration_source=explicit, cwd=/workspace/web)" in text
    assert "last_command: evt_cmd_test: `npm test` (5ms, status=succeeded, exit_code=0, duration_source=explicit, cwd=/workspace/web)" in text


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
                "command": {"value": "pytest -q", "summary": "Run focused tests"},
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
        "cwd_duration_ms": {"unknown": 2125},
        "cwd_average_duration_ms": {"unknown": 1062.5},
        "cwd_duration_extremes_ms": {"unknown": {"min": 125, "max": 2000}},
        "cwd_duration_coverage": {
            "unknown": {"duration_recorded_count": 2, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "cwd_duration_share": {"unknown": 1.0},
        "cwd_summary_examples": {
            "unknown": [{
                "event": "evt_cmd_slow",
                "status": "failed",
                "duration_ms": 2000,
                "duration_source": "derived",
                "summary": "Run focused tests",
                "command": "pytest -q",
                "exit_code": 1,
            }],
        },
        "cwd_summary_missing_examples": {
            "unknown": [{
                "event": "evt_cmd_fast",
                "status": "succeeded",
                "duration_ms": 125,
                "duration_source": "explicit",
                "command": "ruff check",
                "exit_code": 0,
            }],
        },
        "dominant_duration_cwd": {"cwd": "unknown", "duration_ms": 2125, "duration_share": 1.0},
        "cwd_totals": [{
            "cwd": "unknown",
            "count": 2,
            "commands_run": ["pytest -q", "ruff check"],
            "failed_count": 1,
            "total_duration_ms": 2125,
            "average_duration_ms": 1062.5,
            "median_duration_ms": 1062.5,
            "duration_range_ms": 1875,
            "duration_extremes_ms": {"min": 125, "max": 2000},
            "duration_recorded_count": 2,
            "duration_missing_count": 0,
            "duration_coverage_ratio": 1.0,
            "summary_recorded_count": 1,
            "summary_missing_count": 1,
            "summary_coverage_ratio": 0.5,
            "summary_source_counts": {"nested_or_inline": 1},
            "summary_examples": [{
                "event": "evt_cmd_slow",
                "status": "failed",
                "duration_ms": 2000,
                "duration_source": "derived",
                "summary": "Run focused tests",
                "command": "pytest -q",
                "exit_code": 1,
            }],
            "summary_missing_examples": [{
                "event": "evt_cmd_fast",
                "status": "succeeded",
                "duration_ms": 125,
                "duration_source": "explicit",
                "command": "ruff check",
                "exit_code": 0,
            }],
            "duration_source_duration_ms": {"derived": 2000, "explicit": 125},
            "duration_source_average_ms": {"derived": 2000.0, "explicit": 125.0},
            "duration_source_extremes_ms": {"derived": {"min": 2000, "max": 2000}, "explicit": {"min": 125, "max": 125}},
            "duration_source_share": {"derived": 0.9412, "explicit": 0.0588},
            "status_duration_ms": {"failed": 2000, "succeeded": 125},
            "status_average_duration_ms": {"failed": 2000.0, "succeeded": 125.0},
            "status_duration_extremes_ms": {"failed": {"min": 2000, "max": 2000}, "succeeded": {"min": 125, "max": 125}},
            "status_duration_coverage": {
                "failed": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
                "succeeded": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
            },
            "status_duration_share": {"failed": 0.9412, "succeeded": 0.0588},
            "dominant_duration_status": {"status": "failed", "duration_ms": 2000, "duration_share": 0.9412},
            "status_counts": {"failed": 1, "succeeded": 1},
            "duration_source_counts": {"derived": 1, "explicit": 1},
            "time_window": {"started_at": "2026-04-25T00:00:00Z", "ended_at": "2026-04-25T00:00:02Z"},
            "first_event": "evt_cmd_slow",
            "last_event": "evt_cmd_fast",
        }],
        "total_duration_ms": 2125,
        "average_duration_ms": 1062.5,
        "average_recorded_duration_ms": 1062.5,
        "median_duration_ms": 1062.5,
        "duration_range_ms": 1875,
        "duration_extremes_ms": {"min": 125, "max": 2000},
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
            "summary": "Run focused tests",
        }],
        "exit_code_counts": {"1": 1, "0": 1},
        "exit_code_duration_ms": {"1": 2000, "0": 125},
        "exit_code_average_duration_ms": {"1": 2000.0, "0": 125.0},
        "exit_code_duration_extremes_ms": {"1": {"min": 2000, "max": 2000}, "0": {"min": 125, "max": 125}},
        "exit_code_duration_coverage": {
            "1": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
            "0": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "exit_code_duration_share": {"1": 0.9412, "0": 0.0588},
        "dominant_duration_exit_code": {"exit_code": "1", "duration_ms": 2000, "duration_share": 0.9412},
        "exit_code_summary_coverage": {
            "1": {"summary_recorded_count": 1, "summary_missing_count": 0, "summary_coverage_ratio": 1.0},
            "0": {"summary_recorded_count": 0, "summary_missing_count": 1, "summary_coverage_ratio": 0.0},
        },
        "exit_code_summary_examples": {
            "1": [{
                "event": "evt_cmd_slow",
                "status": "failed",
                "duration_ms": 2000,
                "duration_source": "derived",
                "summary": "Run focused tests",
                "command": "pytest -q",
                "exit_code": 1,
            }],
            "0": [],
        },
        "exit_code_summary_missing_examples": {
            "1": [],
            "0": [{
                "event": "evt_cmd_fast",
                "status": "succeeded",
                "duration_ms": 125,
                "duration_source": "explicit",
                "command": "ruff check",
                "exit_code": 0,
            }],
        },
        "status_counts": {"failed": 1, "succeeded": 1},
        "status_duration_ms": {"failed": 2000, "succeeded": 125},
        "status_average_duration_ms": {"failed": 2000.0, "succeeded": 125.0},
        "status_duration_extremes_ms": {"failed": {"min": 2000, "max": 2000}, "succeeded": {"min": 125, "max": 125}},
        "status_duration_coverage": {
            "failed": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
            "succeeded": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "status_duration_share": {"failed": 0.9412, "succeeded": 0.0588},
        "status_summary_examples": {
            "failed": [{
                "event": "evt_cmd_slow",
                "status": "failed",
                "duration_ms": 2000,
                "duration_source": "derived",
                "summary": "Run focused tests",
                "command": "pytest -q",
                "exit_code": 1,
            }],
            "succeeded": [],
        },
        "status_summary_missing_examples": {
            "failed": [],
            "succeeded": [{
                "event": "evt_cmd_fast",
                "status": "succeeded",
                "duration_ms": 125,
                "duration_source": "explicit",
                "command": "ruff check",
                "exit_code": 0,
            }],
        },
        "dominant_duration_status": {"status": "failed", "duration_ms": 2000, "duration_share": 0.9412},
        "duration_source_counts": {"derived": 1, "explicit": 1},
        "duration_source_duration_ms": {"derived": 2000, "explicit": 125},
        "duration_source_average_ms": {"derived": 2000.0, "explicit": 125.0},
        "duration_source_extremes_ms": {"derived": {"min": 2000, "max": 2000}, "explicit": {"min": 125, "max": 125}},
        "duration_source_share": {"derived": 0.9412, "explicit": 0.0588},
        "duration_source_summary_examples": {
            "derived": [{
                "event": "evt_cmd_slow",
                "status": "failed",
                "duration_ms": 2000,
                "duration_source": "derived",
                "summary": "Run focused tests",
                "command": "pytest -q",
                "exit_code": 1,
            }],
            "explicit": [],
        },
        "duration_source_summary_missing_examples": {
            "derived": [],
            "explicit": [{
                "event": "evt_cmd_fast",
                "status": "succeeded",
                "duration_ms": 125,
                "duration_source": "explicit",
                "command": "ruff check",
                "exit_code": 0,
            }],
        },
        "duration_recorded_count": 2,
        "duration_missing_count": 0,
        "duration_coverage_ratio": 1.0,
        "summary_recorded_count": 1,
        "summary_missing_count": 1,
        "summary_coverage_ratio": 0.5,
        "summary_source_counts": {"nested_or_inline": 1},
        "summary_examples": [{
            "event": "evt_cmd_slow",
            "status": "failed",
            "duration_ms": 2000,
            "duration_source": "derived",
            "summary": "Run focused tests",
            "command": "pytest -q",
            "exit_code": 1,
        }],
        "summary_missing_examples": [{
            "event": "evt_cmd_fast",
            "status": "succeeded",
            "duration_ms": 125,
            "duration_source": "explicit",
            "command": "ruff check",
            "exit_code": 0,
        }],
        "command_summary_examples": {
            "pytest -q": [{
                "event": "evt_cmd_slow",
                "status": "failed",
                "duration_ms": 2000,
                "duration_source": "derived",
                "summary": "Run focused tests",
                "command": "pytest -q",
                "exit_code": 1,
            }],
            "ruff check": [],
        },
        "command_summary_missing_examples": {
            "pytest -q": [],
            "ruff check": [{
                "event": "evt_cmd_fast",
                "status": "succeeded",
                "duration_ms": 125,
                "duration_source": "explicit",
                "command": "ruff check",
                "exit_code": 0,
            }],
        },
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
            "summary": "Run focused tests",
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
            "summary": "Run focused tests",
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
        "kind_duration_ms": {"modify": 20},
        "kind_average_duration_ms": {"modify": 10.0},
        "kind_duration_extremes_ms": {"modify": {"min": 8, "max": 12}},
        "kind_duration_coverage": {
            "modify": {"duration_recorded_count": 2, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "kind_duration_share": {"modify": 1.0},
        "kind_summary_examples": {
            "modify": [
                {
                    "event": "evt_edit_one",
                    "status": "succeeded",
                    "duration_ms": 12,
                    "duration_source": "explicit",
                    "summary": "Add report totals",
                    "path": "src/report_json.py",
                    "kind": "modify",
                    "added_lines": 8,
                    "removed_lines": 2,
                    "net_line_delta": 6,
                },
                {
                    "event": "evt_edit_two",
                    "status": "succeeded",
                    "duration_ms": 8,
                    "duration_source": "explicit",
                    "summary": "Render report totals",
                    "path": "src/report_markdown.py",
                    "kind": "modify",
                    "added_lines": 3,
                    "removed_lines": 1,
                    "net_line_delta": 2,
                },
            ],
        },
        "kind_summary_missing_examples": {"modify": []},
        "dominant_duration_kind": {"kind": "modify", "duration_ms": 20, "duration_share": 1.0},
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
            "median_duration_ms": 10.0,
            "duration_range_ms": 4,
            "duration_extremes_ms": {"min": 8, "max": 12},
            "duration_recorded_count": 2,
            "duration_missing_count": 0,
            "duration_coverage_ratio": 1.0,
            "summary_recorded_count": 2,
            "summary_missing_count": 0,
            "summary_coverage_ratio": 1.0,
            "summary_source_counts": {"nested_or_inline": 2},
            "summary_examples": [
                {
                    "event": "evt_edit_one",
                    "status": "succeeded",
                    "duration_ms": 12,
                    "duration_source": "explicit",
                    "summary": "Add report totals",
                    "path": "src/report_json.py",
                    "kind": "modify",
                    "added_lines": 8,
                    "removed_lines": 2,
                    "net_line_delta": 6,
                },
                {
                    "event": "evt_edit_two",
                    "status": "succeeded",
                    "duration_ms": 8,
                    "duration_source": "explicit",
                    "summary": "Render report totals",
                    "path": "src/report_markdown.py",
                    "kind": "modify",
                    "added_lines": 3,
                    "removed_lines": 1,
                    "net_line_delta": 2,
                },
            ],
            "summary_missing_examples": [],
            "duration_source_duration_ms": {"explicit": 20},
            "duration_source_average_ms": {"explicit": 10.0},
            "duration_source_extremes_ms": {"explicit": {"min": 8, "max": 12}},
            "duration_source_share": {"explicit": 1.0},
            "status_duration_ms": {"succeeded": 20},
            "status_average_duration_ms": {"succeeded": 10.0},
            "status_duration_extremes_ms": {"succeeded": {"min": 8, "max": 12}},
            "status_duration_coverage": {
                "succeeded": {"duration_recorded_count": 2, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
            },
            "status_duration_share": {"succeeded": 1.0},
            "dominant_duration_status": {"status": "succeeded", "duration_ms": 20, "duration_share": 1.0},
            "status_counts": {"succeeded": 2},
            "duration_source_counts": {"explicit": 2},
            "time_window": {"started_at": "2026-04-25T00:00:04Z", "ended_at": None},
            "first_event": "evt_edit_one",
            "last_event": "evt_edit_two",
        }],
        "status_counts": {"succeeded": 2},
        "status_duration_ms": {"succeeded": 20},
        "status_average_duration_ms": {"succeeded": 10.0},
        "status_duration_extremes_ms": {"succeeded": {"min": 8, "max": 12}},
        "status_duration_coverage": {
            "succeeded": {"duration_recorded_count": 2, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "status_duration_share": {"succeeded": 1.0},
        "status_summary_examples": {
            "succeeded": [
                {
                    "event": "evt_edit_one",
                    "status": "succeeded",
                    "duration_ms": 12,
                    "duration_source": "explicit",
                    "summary": "Add report totals",
                    "path": "src/report_json.py",
                    "kind": "modify",
                    "added_lines": 8,
                    "removed_lines": 2,
                    "net_line_delta": 6,
                },
                {
                    "event": "evt_edit_two",
                    "status": "succeeded",
                    "duration_ms": 8,
                    "duration_source": "explicit",
                    "summary": "Render report totals",
                    "path": "src/report_markdown.py",
                    "kind": "modify",
                    "added_lines": 3,
                    "removed_lines": 1,
                    "net_line_delta": 2,
                },
            ],
        },
        "status_summary_missing_examples": {"succeeded": []},
        "dominant_duration_status": {"status": "succeeded", "duration_ms": 20, "duration_share": 1.0},
        "duration_source_counts": {"explicit": 2},
        "duration_source_duration_ms": {"explicit": 20},
        "duration_source_average_ms": {"explicit": 10.0},
        "duration_source_extremes_ms": {"explicit": {"min": 8, "max": 12}},
        "duration_source_share": {"explicit": 1.0},
        "duration_source_summary_examples": {
            "explicit": [
                {
                    "event": "evt_edit_one",
                    "status": "succeeded",
                    "duration_ms": 12,
                    "duration_source": "explicit",
                    "summary": "Add report totals",
                    "path": "src/report_json.py",
                    "kind": "modify",
                    "added_lines": 8,
                    "removed_lines": 2,
                    "net_line_delta": 6,
                },
                {
                    "event": "evt_edit_two",
                    "status": "succeeded",
                    "duration_ms": 8,
                    "duration_source": "explicit",
                    "summary": "Render report totals",
                    "path": "src/report_markdown.py",
                    "kind": "modify",
                    "added_lines": 3,
                    "removed_lines": 1,
                    "net_line_delta": 2,
                },
            ],
        },
        "duration_source_summary_missing_examples": {"explicit": []},
        "duration_recorded_count": 2,
        "duration_missing_count": 0,
        "duration_coverage_ratio": 1.0,
        "summary_recorded_count": 2,
        "summary_missing_count": 0,
        "summary_coverage_ratio": 1.0,
        "summary_source_counts": {"nested_or_inline": 2},
        "summary_examples": [
            {
                "event": "evt_edit_one",
                "status": "succeeded",
                "duration_ms": 12,
                "duration_source": "explicit",
                "summary": "Add report totals",
                "path": "src/report_json.py",
                "kind": "modify",
                "added_lines": 8,
                "removed_lines": 2,
                "net_line_delta": 6,
            },
            {
                "event": "evt_edit_two",
                "status": "succeeded",
                "duration_ms": 8,
                "duration_source": "explicit",
                "summary": "Render report totals",
                "path": "src/report_markdown.py",
                "kind": "modify",
                "added_lines": 3,
                "removed_lines": 1,
                "net_line_delta": 2,
            },
        ],
        "summary_missing_examples": [],
        "path_summary_examples": {
            "src/report_json.py": [{
                "event": "evt_edit_one",
                "status": "succeeded",
                "duration_ms": 12,
                "duration_source": "explicit",
                "summary": "Add report totals",
                "path": "src/report_json.py",
                "kind": "modify",
                "added_lines": 8,
                "removed_lines": 2,
                "net_line_delta": 6,
            }],
            "src/report_markdown.py": [{
                "event": "evt_edit_two",
                "status": "succeeded",
                "duration_ms": 8,
                "duration_source": "explicit",
                "summary": "Render report totals",
                "path": "src/report_markdown.py",
                "kind": "modify",
                "added_lines": 3,
                "removed_lines": 1,
                "net_line_delta": 2,
            }],
        },
        "path_summary_missing_examples": {
            "src/report_json.py": [],
            "src/report_markdown.py": [],
        },
        "time_window": {"started_at": "2026-04-25T00:00:04Z", "ended_at": None},
        "total_added_lines": 11,
        "total_removed_lines": 3,
        "net_line_delta": 8,
        "total_duration_ms": 20,
        "average_duration_ms": 10.0,
        "average_recorded_duration_ms": 10.0,
        "median_duration_ms": 10.0,
        "duration_range_ms": 4,
        "duration_extremes_ms": {"min": 8, "max": 12},
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
            "summary": "Add report totals",
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
            "summary": "Add report totals",
        },
        "slowest_edit": {
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
            "summary": "Add report totals",
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
            "summary": "Render report totals",
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
            "summary": "Render report totals",
        },
    }

    text = build_markdown_summary(trace)
    assert "command_count: 2" in text
    assert "unique_command_count: 2" in text
    assert "commands_run: pytest -q, ruff check" in text
    assert "repeated_commands: none" in text
    assert "command_attempts: `pytest -q` (count=1, total_duration_ms=2000, average_duration_ms=2000.0, failed_count=1, statuses=failed=1, duration_sources=derived=1, time_window=started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z, first_event=evt_cmd_slow, last_event=evt_cmd_slow); `ruff check` (count=1, total_duration_ms=125, average_duration_ms=125.0, failed_count=0, statuses=succeeded=1, duration_sources=explicit=1, time_window=started_at=2026-04-25T00:00:03Z, first_event=evt_cmd_fast, last_event=evt_cmd_fast)" in text
    assert "command_cwd_counts: unknown=2" in text
    assert "command_cwd_duration_summary: cwd_duration_ms=unknown=2125, cwd_average_duration_ms=unknown=1062.5, cwd_duration_extremes_ms=unknown=min=125/max=2000, cwd_duration_coverage=unknown=recorded=2/missing=0/ratio=1.0, cwd_duration_share=unknown=1.0, dominant_duration_cwd=unknown (2125ms, share=1.0)" in text
    assert "command_cwd_totals: unknown (count=2, commands=pytest -q, ruff check, failed_count=1, total_duration_ms=2125, average_duration_ms=1062.5, statuses=failed=1, succeeded=1, duration_sources=derived=1, explicit=1, median_duration_ms=1062.5, duration_range_ms=1875, duration_extremes_ms=min=125, max=2000, duration_recorded_count=2, duration_missing_count=0, duration_coverage_ratio=1.0, summary_recorded_count=1, summary_missing_count=1, summary_coverage_ratio=0.5, summary_source_counts=nested_or_inline=1, summary_examples=`pytest -q` (event=evt_cmd_slow, status=failed, duration_ms=2000, duration_source=derived, exit_code=1, summary=Run focused tests), summary_missing_examples=`ruff check` (event=evt_cmd_fast, status=succeeded, duration_ms=125, duration_source=explicit, exit_code=0), status_duration_ms=failed=2000, succeeded=125, status_average_duration_ms=failed=2000.0, succeeded=125.0, status_duration_extremes_ms=failed=min=2000/max=2000, succeeded=min=125/max=125, status_duration_coverage=failed=recorded=1/missing=0/ratio=1.0, succeeded=recorded=1/missing=0/ratio=1.0, status_duration_share=failed=0.9412, succeeded=0.0588, dominant_duration_status=failed (2000ms, share=0.9412), duration_source_duration_ms=derived=2000, explicit=125, duration_source_average_ms=derived=2000.0, explicit=125.0, duration_source_extremes_ms=derived=min=2000/max=2000, explicit=min=125/max=125, duration_source_share=derived=0.9412, explicit=0.0588, time_window=started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z, first_event=evt_cmd_slow, last_event=evt_cmd_fast)" in text
    assert "command_total_duration_ms: 2125" in text
    assert "command_average_duration_ms: 1062.5" in text
    assert "command_average_recorded_duration_ms: 1062.5" in text
    assert "command_median_duration_ms: 1062.5" in text
    assert "command_duration_range_ms: 1875" in text
    assert "command_failed_count: 1" in text
    assert "failed_commands: evt_cmd_slow: `pytest -q` (2000ms, status=failed, exit_code=1, duration_source=derived, started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z, summary=Run focused tests)" in text
    assert "command_exit_code_counts: 0=1, 1=1" in text
    assert "exit_code_summary_examples=1=`pytest -q` (event=evt_cmd_slow, status=failed, duration_ms=2000, duration_source=derived, exit_code=1, summary=Run focused tests)" in text
    assert "exit_code_summary_missing_examples=0=`ruff check` (event=evt_cmd_fast, status=succeeded, duration_ms=125, duration_source=explicit, exit_code=0)" in text
    assert "command_status_counts: failed=1, succeeded=1" in text
    assert "command_duration_sources: derived=1, explicit=1" in text
    assert "command_duration_source_duration_ms: derived=2000, explicit=125" in text
    assert "command_duration_source_average_ms: derived=2000.0, explicit=125.0" in text
    assert "command_duration_source_extremes_ms: derived=min=2000/max=2000, explicit=min=125/max=125" in text
    assert "command_duration_source_share: derived=0.9412, explicit=0.0588" in text
    assert "command_duration_recorded_count: 2" in text
    assert "command_duration_missing_count: 0" in text
    assert "command_duration_coverage_ratio: 1.0" in text
    assert "command_summary_recorded_count: 1" in text
    assert "command_summary_missing_count: 1" in text
    assert "command_summary_coverage_ratio: 0.5" in text
    assert "command_summary_source_counts: nested_or_inline=1" in text
    assert "command_summary_examples: `pytest -q` (event=evt_cmd_slow, status=failed, duration_ms=2000, duration_source=derived, exit_code=1, summary=Run focused tests)" in text
    assert "command_summary_missing_examples: `ruff check` (event=evt_cmd_fast, status=succeeded, duration_ms=125, duration_source=explicit, exit_code=0)" in text
    assert "command_duration_source_summary_examples: derived=`pytest -q` (event=evt_cmd_slow, status=failed, duration_ms=2000, duration_source=derived, exit_code=1, summary=Run focused tests)" in text
    assert "command_duration_source_summary_missing_examples: explicit=`ruff check` (event=evt_cmd_fast, status=succeeded, duration_ms=125, duration_source=explicit, exit_code=0)" in text
    assert "command_time_window: started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z" in text
    assert "first_command: evt_cmd_slow: `pytest -q` (2000ms, status=failed, exit_code=1, duration_source=derived, started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z, summary=Run focused tests)" in text
    assert "slowest_command: evt_cmd_slow: `pytest -q` (2000ms, status=failed, exit_code=1, duration_source=derived, started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:02Z, summary=Run focused tests)" in text
    assert "fastest_command: evt_cmd_fast: `ruff check` (125ms, status=succeeded, exit_code=0, duration_source=explicit, started_at=2026-04-25T00:00:03Z)" in text
    assert "last_command: evt_cmd_fast: `ruff check` (125ms, status=succeeded, exit_code=0, duration_source=explicit, started_at=2026-04-25T00:00:03Z)" in text
    assert "files_changed_count: 2" in text
    assert "files_changed: src/report_json.py, src/report_markdown.py" in text
    assert "file_change_totals: src/report_json.py (count=1, failed_count=0, +8/-2, net=6, total_duration_ms=12, average_duration_ms=12.0, statuses=succeeded=1, kinds=modify=1, duration_sources=explicit=1, time_window=started_at=2026-04-25T00:00:04Z); src/report_markdown.py (count=1, failed_count=0, +3/-1, net=2, total_duration_ms=8, average_duration_ms=8.0, statuses=succeeded=1, kinds=modify=1, duration_sources=explicit=1, time_window=started_at=2026-04-25T00:00:05Z)" in text
    assert "edit_failed_count: 0" in text
    assert "failed_edits: none" in text
    assert "edit_kind_counts: modify=2" in text
    assert "edit_kind_duration_summary: kind_duration_ms=modify=20, kind_average_duration_ms=modify=10.0, kind_duration_extremes_ms=modify=min=8/max=12, kind_duration_coverage=modify=recorded=2/missing=0/ratio=1.0, kind_duration_share=modify=1.0, dominant_duration_kind=modify (20ms, share=1.0)" in text
    assert "edit_kind_totals: modify (count=2, files=src/report_json.py, src/report_markdown.py, failed_count=0, +11/-3, net=8, total_duration_ms=20, average_duration_ms=10.0, statuses=succeeded=2, duration_sources=explicit=2, median_duration_ms=10.0, duration_range_ms=4, duration_extremes_ms=min=8, max=12, duration_recorded_count=2, duration_missing_count=0, duration_coverage_ratio=1.0, summary_recorded_count=2, summary_missing_count=0, summary_coverage_ratio=1.0, summary_source_counts=nested_or_inline=2, summary_examples=src/report_json.py (event=evt_edit_one, status=succeeded, duration_ms=12, duration_source=explicit, kind=modify, net=6, summary=Add report totals); src/report_markdown.py (event=evt_edit_two, status=succeeded, duration_ms=8, duration_source=explicit, kind=modify, net=2, summary=Render report totals), summary_missing_examples=none, status_duration_ms=succeeded=20, status_average_duration_ms=succeeded=10.0, status_duration_extremes_ms=succeeded=min=8/max=12, status_duration_coverage=succeeded=recorded=2/missing=0/ratio=1.0, status_duration_share=succeeded=1.0, dominant_duration_status=succeeded (20ms, share=1.0), duration_source_duration_ms=explicit=20, duration_source_average_ms=explicit=10.0, duration_source_extremes_ms=explicit=min=8/max=12, duration_source_share=explicit=1.0, time_window=started_at=2026-04-25T00:00:04Z, first_event=evt_edit_one, last_event=evt_edit_two)" in text
    assert "edit_status_counts: succeeded=2" in text
    assert "edit_duration_sources: explicit=2" in text
    assert "edit_duration_source_duration_ms: explicit=20" in text
    assert "edit_duration_source_average_ms: explicit=10.0" in text
    assert "edit_duration_source_extremes_ms: explicit=min=8/max=12" in text
    assert "edit_duration_source_share: explicit=1.0" in text
    assert "edit_duration_recorded_count: 2" in text
    assert "edit_duration_missing_count: 0" in text
    assert "edit_duration_coverage_ratio: 1.0" in text
    assert "edit_summary_recorded_count: 2" in text
    assert "edit_summary_missing_count: 0" in text
    assert "edit_summary_coverage_ratio: 1.0" in text
    assert "edit_summary_source_counts: nested_or_inline=2" in text
    assert "edit_summary_examples: src/report_json.py (event=evt_edit_one, status=succeeded, duration_ms=12, duration_source=explicit, kind=modify, net=6, summary=Add report totals); src/report_markdown.py (event=evt_edit_two, status=succeeded, duration_ms=8, duration_source=explicit, kind=modify, net=2, summary=Render report totals)" in text
    assert "edit_summary_missing_examples: none" in text
    assert "edit_duration_source_summary_examples: explicit=src/report_json.py (event=evt_edit_one, status=succeeded, duration_ms=12, duration_source=explicit, kind=modify, net=6, summary=Add report totals); src/report_markdown.py (event=evt_edit_two, status=succeeded, duration_ms=8, duration_source=explicit, kind=modify, net=2, summary=Render report totals)" in text
    assert "edit_duration_source_summary_missing_examples: none" in text
    assert "edit_time_window: started_at=2026-04-25T00:00:04Z" in text
    assert "edit_total_lines: +11/-3" in text
    assert "edit_net_line_delta: 8" in text
    assert "edit_total_duration_ms: 20" in text
    assert "edit_average_duration_ms: 10.0" in text
    assert "edit_average_recorded_duration_ms: 10.0" in text
    assert "edit_median_duration_ms: 10.0" in text
    assert "edit_duration_range_ms: 4" in text
    assert "first_edit: evt_edit_one: src/report_json.py (+8/-2, net=6, duration_ms=12, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:04Z, summary=Add report totals)" in text
    assert "largest_edit: evt_edit_one: src/report_json.py (+8/-2, net=6, duration_ms=12, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:04Z, summary=Add report totals)" in text
    assert "slowest_edit: evt_edit_one: src/report_json.py (+8/-2, net=6, duration_ms=12, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:04Z, summary=Add report totals)" in text
    assert "shortest_edit: evt_edit_two: src/report_markdown.py (+3/-1, net=2, duration_ms=8, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:05Z, summary=Render report totals)" in text
    assert "last_edit: evt_edit_two: src/report_markdown.py (+3/-1, net=2, duration_ms=8, status=succeeded, duration_source=explicit, started_at=2026-04-25T00:00:05Z, summary=Render report totals)" in text


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
                "command": {"value": "pytest -q", "summary": "Initial failing test run"},
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
        "median_duration_ms": 25.0,
        "duration_range_ms": 10,
        "duration_extremes_ms": {"min": 20, "max": 30},
        "duration_recorded_count": 2,
        "duration_missing_count": 0,
        "duration_coverage_ratio": 1.0,
        "summary_recorded_count": 1,
        "summary_missing_count": 1,
        "summary_coverage_ratio": 0.5,
        "summary_source_counts": {"nested_or_inline": 1},
        "summary_examples": [{
            "event": "evt_cmd_first",
            "status": "failed",
            "duration_ms": 20,
            "duration_source": "explicit",
            "summary": "Initial failing test run",
            "command": "pytest -q",
            "exit_code": 1,
        }],
        "summary_missing_examples": [{
            "event": "evt_cmd_retry",
            "status": "succeeded",
            "duration_ms": 30,
            "duration_source": "explicit",
            "command": "pytest -q",
            "exit_code": 0,
        }],
        "duration_source_duration_ms": {"explicit": 50},
        "duration_source_average_ms": {"explicit": 25.0},
        "duration_source_extremes_ms": {"explicit": {"min": 20, "max": 30}},
        "duration_source_share": {"explicit": 1.0},
        "status_duration_ms": {"failed": 20, "succeeded": 30},
        "status_average_duration_ms": {"failed": 20.0, "succeeded": 30.0},
        "status_duration_extremes_ms": {"failed": {"min": 20, "max": 20}, "succeeded": {"min": 30, "max": 30}},
        "status_duration_coverage": {
            "failed": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
            "succeeded": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "status_duration_share": {"failed": 0.4, "succeeded": 0.6},
        "dominant_duration_status": {"status": "succeeded", "duration_ms": 30, "duration_share": 0.6},
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
        "summary": "Initial failing test run",
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
        "median_duration_ms": 7.5,
        "duration_range_ms": 1,
        "duration_extremes_ms": {"min": 7, "max": 8},
        "duration_recorded_count": 2,
        "duration_missing_count": 0,
        "duration_coverage_ratio": 1.0,
        "summary_recorded_count": 2,
        "summary_missing_count": 0,
        "summary_coverage_ratio": 1.0,
        "summary_source_counts": {"nested_or_inline": 2},
        "summary_examples": [
            {
                "event": "evt_edit_first",
                "status": "succeeded",
                "duration_ms": 7,
                "duration_source": "explicit",
                "summary": "First change",
                "path": "src/report_json.py",
                "kind": "modify",
                "added_lines": 1,
                "removed_lines": 0,
                "net_line_delta": 1,
            },
            {
                "event": "evt_edit_second",
                "status": "succeeded",
                "duration_ms": 8,
                "duration_source": "explicit",
                "summary": "Second change",
                "path": "src/report_json.py",
                "kind": "modify",
                "added_lines": 2,
                "removed_lines": 1,
                "net_line_delta": 1,
            },
        ],
        "summary_missing_examples": [],
        "duration_source_duration_ms": {"explicit": 15},
        "duration_source_average_ms": {"explicit": 7.5},
        "duration_source_extremes_ms": {"explicit": {"min": 7, "max": 8}},
        "duration_source_share": {"explicit": 1.0},
        "status_duration_ms": {"succeeded": 15},
        "status_average_duration_ms": {"succeeded": 7.5},
        "status_duration_extremes_ms": {"succeeded": {"min": 7, "max": 8}},
        "status_duration_coverage": {
            "succeeded": {"duration_recorded_count": 2, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "status_duration_share": {"succeeded": 1.0},
        "dominant_duration_status": {"status": "succeeded", "duration_ms": 15, "duration_share": 1.0},
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
    assert "command_attempts: `pytest -q` (count=2, total_duration_ms=50, average_duration_ms=25.0, failed_count=1, statuses=failed=1, succeeded=1, median_duration_ms=25.0, duration_range_ms=10, duration_extremes_ms=min=20, max=30, duration_recorded_count=2, duration_missing_count=0, duration_coverage_ratio=1.0, summary_recorded_count=1, summary_missing_count=1, summary_coverage_ratio=0.5, summary_source_counts=nested_or_inline=1, summary_examples=`pytest -q` (event=evt_cmd_first, status=failed, duration_ms=20, duration_source=explicit, exit_code=1, summary=Initial failing test run), summary_missing_examples=`pytest -q` (event=evt_cmd_retry, status=succeeded, duration_ms=30, duration_source=explicit, exit_code=0), status_duration_ms=failed=20, succeeded=30, status_average_duration_ms=failed=20.0, succeeded=30.0, status_duration_extremes_ms=failed=min=20/max=20, succeeded=min=30/max=30, status_duration_coverage=failed=recorded=1/missing=0/ratio=1.0, succeeded=recorded=1/missing=0/ratio=1.0, status_duration_share=failed=0.4, succeeded=0.6, dominant_duration_status=succeeded (30ms, share=0.6), duration_source_duration_ms=explicit=50, duration_source_average_ms=explicit=25.0, duration_source_extremes_ms=explicit=min=20/max=30, duration_source_share=explicit=1.0, duration_sources=explicit=2, first_event=evt_cmd_first, last_event=evt_cmd_retry); `ruff check` (count=1, total_duration_ms=5, average_duration_ms=5.0, failed_count=0, statuses=succeeded=1, duration_sources=explicit=1, first_event=evt_cmd_lint, last_event=evt_cmd_lint)" in text
    assert "failed_commands: evt_cmd_first: `pytest -q` (20ms, status=failed, exit_code=1, duration_source=explicit, summary=Initial failing test run)" in text
    assert "files_changed_count: 1" in text
    assert "files_changed: src/report_json.py" in text
    assert "file_change_totals: src/report_json.py (count=2, failed_count=0, +3/-1, net=2, total_duration_ms=15, average_duration_ms=7.5, statuses=succeeded=2, kinds=modify=2, duration_sources=explicit=2, median_duration_ms=7.5, duration_range_ms=1, duration_extremes_ms=min=7, max=8, duration_recorded_count=2, duration_missing_count=0, duration_coverage_ratio=1.0, summary_recorded_count=2, summary_missing_count=0, summary_coverage_ratio=1.0, summary_source_counts=nested_or_inline=2, summary_examples=src/report_json.py (event=evt_edit_first, status=succeeded, duration_ms=7, duration_source=explicit, kind=modify, net=1, summary=First change); src/report_json.py (event=evt_edit_second, status=succeeded, duration_ms=8, duration_source=explicit, kind=modify, net=1, summary=Second change), summary_missing_examples=none, status_duration_ms=succeeded=15, status_average_duration_ms=succeeded=7.5, status_duration_extremes_ms=succeeded=min=7/max=8, status_duration_coverage=succeeded=recorded=2/missing=0/ratio=1.0, status_duration_share=succeeded=1.0, dominant_duration_status=succeeded (15ms, share=1.0), duration_source_duration_ms=explicit=15, duration_source_average_ms=explicit=7.5, duration_source_extremes_ms=explicit=min=7/max=8, duration_source_share=explicit=1.0, first_event=evt_edit_first, last_event=evt_edit_second)" in text


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
    assert payload["edit_summary_totals"]["kind_totals"][0]["duration_recorded_count"] == 1
    assert payload["edit_summary_totals"]["kind_totals"][0]["duration_missing_count"] == 1
    assert payload["edit_summary_totals"]["kind_totals"][0]["duration_coverage_ratio"] == 0.5
    assert payload["summary"]["total_duration_ms"] == 40

    text = build_markdown_summary(trace)
    assert "command_duration_sources: derived=1, explicit=1" in text
    assert "command_duration_source_duration_ms: derived=25, explicit=10" in text
    assert "command_duration_source_average_ms: derived=25.0, explicit=10.0" in text
    assert "command_duration_source_extremes_ms: derived=min=25/max=25, explicit=min=10/max=10" in text
    assert "command_duration_source_share: derived=0.7143, explicit=0.2857" in text
    assert "edit_duration_sources: derived=1, missing=1" in text
    assert "edit_duration_source_duration_ms: derived=5, missing=0" in text
    assert "edit_duration_source_average_ms: derived=5.0, missing=0.0" in text
    assert "edit_duration_source_extremes_ms: derived=min=5/max=5, missing=min=0/max=0" in text
    assert "edit_duration_source_share: derived=1.0, missing=0.0" in text
    assert "edit_kind_totals: modify (count=2, files=src/report_json.py, src/report_markdown.py, failed_count=0, +3/-1, net=2, total_duration_ms=5, average_duration_ms=2.5, statuses=succeeded=2, duration_sources=derived=1, missing=1, median_duration_ms=2.5, duration_range_ms=5, duration_extremes_ms=min=0, max=5, duration_recorded_count=1, duration_missing_count=1, duration_coverage_ratio=0.5, summary_recorded_count=2, summary_missing_count=0, summary_coverage_ratio=1.0" in text
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
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
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
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
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
        "type_duration_ms": {"command": 20, "file_edit": 5},
        "type_average_duration_ms": {"command": 20.0, "file_edit": 5.0},
        "type_duration_extremes_ms": {"command": {"min": 20, "max": 20}, "file_edit": {"min": 5, "max": 5}},
        "type_duration_coverage": {
            "command": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
            "file_edit": {"duration_recorded_count": 1, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "type_duration_share": {"command": 0.8, "file_edit": 0.2},
        "dominant_duration_type": {"type": "command", "duration_ms": 20, "duration_share": 0.8},
        "status_counts": {"failed": 2},
        "status_duration_ms": {"failed": 25},
        "status_average_duration_ms": {"failed": 12.5},
        "status_duration_extremes_ms": {"failed": {"min": 5, "max": 20}},
        "status_duration_coverage": {
            "failed": {"duration_recorded_count": 2, "duration_missing_count": 0, "duration_coverage_ratio": 1.0},
        },
        "status_duration_share": {"failed": 1.0},
        "dominant_duration_status": {"status": "failed", "duration_ms": 25, "duration_share": 1.0},
        "duration_source_counts": {"derived": 1, "explicit": 1},
        "duration_source_duration_ms": {"derived": 20, "explicit": 5},
        "duration_source_average_ms": {"derived": 20.0, "explicit": 5.0},
        "duration_source_extremes_ms": {"derived": {"min": 20, "max": 20}, "explicit": {"min": 5, "max": 5}},
        "duration_source_share": {"derived": 0.8, "explicit": 0.2},
        "duration_recorded_count": 2,
        "duration_missing_count": 0,
        "duration_coverage_ratio": 1.0,
        "summary_recorded_count": 1,
        "summary_missing_count": 1,
        "summary_coverage_ratio": 0.5,
        "summary_source_counts": {"nested_or_inline": 1},
        "summary_examples": [{
            "type": "file_edit",
            "event": "evt_edit_late_diff",
            "status": "failed",
            "duration_ms": 5,
            "duration_source": "explicit",
            "summary": "Edit report timeline",
            "path": "src/report.py",
            "kind": "modify",
            "added_lines": 2,
            "removed_lines": 1,
            "net_line_delta": 1,
            "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
        }],
        "summary_missing_examples": [{
            "type": "command",
            "event": "evt_cmd_early_log",
            "status": "failed",
            "duration_ms": 20,
            "duration_source": "derived",
            "command": "pytest -q",
            "cwd": "/repo",
            "exit_code": 1,
            "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
        }],
        "type_summary_examples": {
            "command": [],
            "file_edit": [{
                "type": "file_edit",
                "event": "evt_edit_late_diff",
                "status": "failed",
                "duration_ms": 5,
                "duration_source": "explicit",
                "summary": "Edit report timeline",
                "path": "src/report.py",
                "kind": "modify",
                "added_lines": 2,
                "removed_lines": 1,
                "net_line_delta": 1,
                "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
            }],
        },
        "type_summary_missing_examples": {
            "command": [{
                "type": "command",
                "event": "evt_cmd_early_log",
                "status": "failed",
                "duration_ms": 20,
                "duration_source": "derived",
                "command": "pytest -q",
                "cwd": "/repo",
                "exit_code": 1,
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
            }],
            "file_edit": [],
        },
        "status_summary_examples": {
            "failed": [{
                "type": "file_edit",
                "event": "evt_edit_late_diff",
                "status": "failed",
                "duration_ms": 5,
                "duration_source": "explicit",
                "summary": "Edit report timeline",
                "path": "src/report.py",
                "kind": "modify",
                "added_lines": 2,
                "removed_lines": 1,
                "net_line_delta": 1,
                "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
            }],
        },
        "status_summary_missing_examples": {
            "failed": [{
                "type": "command",
                "event": "evt_cmd_early_log",
                "status": "failed",
                "duration_ms": 20,
                "duration_source": "derived",
                "command": "pytest -q",
                "cwd": "/repo",
                "exit_code": 1,
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
            }],
        },
        "duration_source_summary_examples": {
            "derived": [],
            "explicit": [{
                "type": "file_edit",
                "event": "evt_edit_late_diff",
                "status": "failed",
                "duration_ms": 5,
                "duration_source": "explicit",
                "summary": "Edit report timeline",
                "path": "src/report.py",
                "kind": "modify",
                "added_lines": 2,
                "removed_lines": 1,
                "net_line_delta": 1,
                "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
            }],
        },
        "duration_source_summary_missing_examples": {
            "derived": [{
                "type": "command",
                "event": "evt_cmd_early_log",
                "status": "failed",
                "duration_ms": 20,
                "duration_source": "derived",
                "command": "pytest -q",
                "cwd": "/repo",
                "exit_code": 1,
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
            }],
            "explicit": [],
        },
        "identity_summary_examples": {
            "command:pytest -q": [],
            "file_edit:src/report.py": [{
                "type": "file_edit",
                "event": "evt_edit_late_diff",
                "status": "failed",
                "duration_ms": 5,
                "duration_source": "explicit",
                "summary": "Edit report timeline",
                "path": "src/report.py",
                "kind": "modify",
                "added_lines": 2,
                "removed_lines": 1,
                "net_line_delta": 1,
                "artifacts": [{"kind": "diff", "path": "artifacts/evt_edit_late_diff.diff"}],
            }],
        },
        "identity_summary_missing_examples": {
            "command:pytest -q": [{
                "type": "command",
                "event": "evt_cmd_early_log",
                "status": "failed",
                "duration_ms": 20,
                "duration_source": "derived",
                "command": "pytest -q",
                "cwd": "/repo",
                "exit_code": 1,
                "artifacts": [{"kind": "command_log", "path": "artifacts/evt_cmd_early_log.log"}],
            }],
            "file_edit:src/report.py": [],
        },
        "time_window": {"started_at": "2026-04-25T00:00:01Z", "ended_at": "2026-04-25T00:00:01.020Z"},
        "span_duration_ms": 20,
        "covered_duration_ms": 25,
        "covered_intervals": [
            {"started_at": "2026-04-25T00:00:01Z", "ended_at": "2026-04-25T00:00:01.02Z", "duration_ms": 20},
            {"started_at": "2026-04-25T00:00:03Z", "ended_at": "2026-04-25T00:00:03.005Z", "duration_ms": 5},
        ],
        "uncovered_duration_ms": 0,
        "uncovered_intervals": [],
        "uncovered_interval_count": 0,
        "average_uncovered_interval_ms": 0,
        "largest_uncovered_interval": None,
        "coverage_ratio": 1.0,
        "idle_ratio": 0.0,
        "covered_interval_count": 2,
        "merged_covered_interval_count": 2,
        "total_duration_ms": 25,
        "average_duration_ms": 12.5,
        "average_recorded_duration_ms": 12.5,
        "median_duration_ms": 12.5,
        "duration_range_ms": 15,
        "duration_extremes_ms": {"min": 5, "max": 20},
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
        "average_idle_gap_ms": 1980.0,
        "largest_idle_gap": {
            "from_event": "evt_cmd_early_log",
            "to_event": "evt_edit_late_diff",
            "gap_ms": 1980,
            "from_ended_at": "2026-04-25T00:00:01.020Z",
            "to_started_at": "2026-04-25T00:00:03Z",
        },
        "inter_activity_overlaps": [],
        "total_overlap_ms": 0,
        "average_overlap_ms": 0,
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
    assert "type_average_duration_ms=command=20.0, file_edit=5.0" in text
    assert "type_duration_extremes_ms=command=min=20/max=20, file_edit=min=5/max=5" in text
    assert "type_duration_share=command=0.8, file_edit=0.2" in text
    assert "status_duration_ms=failed=25" in text
    assert "status_duration_share=failed=1.0" in text
    assert "dominant_duration_status=failed (25ms, share=1.0)" in text
    assert "duration_range_ms=15" in text
    assert "duration_source_duration_ms=derived=20, explicit=5" in text
    assert "duration_source_average_ms=derived=20.0, explicit=5.0" in text
    assert "duration_source_extremes_ms=derived=min=20/max=20, explicit=min=5/max=5" in text
    assert "duration_source_share=derived=0.8, explicit=0.2" in text
    assert "summary_recorded_count=1" in text
    assert "summary_missing_count=1" in text
    assert "summary_coverage_ratio=0.5" in text
    assert "summary_examples=src/report.py (event=evt_edit_late_diff, status=failed, duration_ms=5, duration_source=explicit, kind=modify, net=1, artifacts=diff=artifacts/evt_edit_late_diff.diff, summary=Edit report timeline)" in text
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
    assert timeline_totals["average_overlap_ms"] == 2000.0
    assert timeline_totals["overlap_ratio"] == 0.2857
    assert timeline_totals["largest_overlap"] == timeline_totals["inter_activity_overlaps"][0]
    assert timeline_totals["total_idle_gap_ms"] == 2000
    assert timeline_totals["average_idle_gap_ms"] == 1000.0
    assert timeline_totals["time_window"] == {"started_at": "2026-04-25T00:00:00Z", "ended_at": "2026-04-25T00:00:07Z"}
    assert timeline_totals["span_duration_ms"] == 7000
    assert timeline_totals["covered_duration_ms"] == 6000
    assert timeline_totals["covered_intervals"] == [
        {
            "started_at": "2026-04-25T00:00:00Z",
            "ended_at": "2026-04-25T00:00:05Z",
            "duration_ms": 5000,
        },
        {
            "started_at": "2026-04-25T00:00:06Z",
            "ended_at": "2026-04-25T00:00:07Z",
            "duration_ms": 1000,
        },
    ]
    assert timeline_totals["uncovered_duration_ms"] == 1000
    assert timeline_totals["uncovered_intervals"] == [{
        "started_at": "2026-04-25T00:00:05Z",
        "ended_at": "2026-04-25T00:00:06Z",
        "duration_ms": 1000,
    }]
    assert timeline_totals["uncovered_interval_count"] == 1
    assert timeline_totals["average_uncovered_interval_ms"] == 1000.0
    assert timeline_totals["largest_uncovered_interval"] == timeline_totals["uncovered_intervals"][0]
    assert timeline_totals["coverage_ratio"] == 0.8571
    assert timeline_totals["idle_ratio"] == 0.1429
    assert timeline_totals["covered_interval_count"] == 3
    assert timeline_totals["merged_covered_interval_count"] == 2
    assert timeline_totals["status_duration_ms"] == {"succeeded": 7000}
    assert timeline_totals["status_duration_share"] == {"succeeded": 1.0}
    assert timeline_totals["dominant_duration_status"] == {"status": "succeeded", "duration_ms": 7000, "duration_share": 1.0}

    text = build_markdown_summary(trace)
    assert "span_duration_ms=7000" in text
    assert "covered_duration_ms=6000" in text
    assert "covered_intervals=(started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:05Z, duration_ms=5000); (started_at=2026-04-25T00:00:06Z, ended_at=2026-04-25T00:00:07Z, duration_ms=1000)" in text
    assert "uncovered_duration_ms=1000" in text
    assert "uncovered_intervals=(started_at=2026-04-25T00:00:05Z, ended_at=2026-04-25T00:00:06Z, duration_ms=1000)" in text
    assert "uncovered_interval_count=1" in text
    assert "average_uncovered_interval_ms=1000.0" in text
    assert "largest_uncovered_interval=(started_at=2026-04-25T00:00:05Z, ended_at=2026-04-25T00:00:06Z, duration_ms=1000)" in text
    assert "coverage_ratio=0.8571" in text
    assert "idle_ratio=0.1429" in text
    assert "covered_interval_count=3" in text
    assert "merged_covered_interval_count=2" in text
    assert "total_overlap_ms=2000" in text
    assert "average_overlap_ms=2000.0" in text
    assert "overlap_ratio=0.2857" in text
    assert "average_idle_gap_ms=1000.0" in text
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
    assert timeline_totals["covered_intervals"] == [
        {
            "started_at": "2026-04-25T00:00:00Z",
            "ended_at": "2026-04-25T00:00:03Z",
            "duration_ms": 3000,
        },
        {
            "started_at": "2026-04-25T00:00:04Z",
            "ended_at": "2026-04-25T00:00:05Z",
            "duration_ms": 1000,
        },
    ]
    assert timeline_totals["uncovered_duration_ms"] == 1000
    assert timeline_totals["uncovered_intervals"] == [{
        "started_at": "2026-04-25T00:00:03Z",
        "ended_at": "2026-04-25T00:00:04Z",
        "duration_ms": 1000,
    }]
    assert timeline_totals["uncovered_interval_count"] == 1
    assert timeline_totals["average_uncovered_interval_ms"] == 1000.0
    assert timeline_totals["largest_uncovered_interval"] == timeline_totals["uncovered_intervals"][0]
    assert timeline_totals["coverage_ratio"] == 0.8
    assert timeline_totals["idle_ratio"] == 0.2
    assert timeline_totals["covered_interval_count"] == 2
    assert timeline_totals["merged_covered_interval_count"] == 2
    assert timeline_totals["status_duration_ms"] == {"succeeded": 4000}
    assert timeline_totals["status_duration_share"] == {"succeeded": 1.0}
    assert timeline_totals["dominant_duration_status"] == {"status": "succeeded", "duration_ms": 4000, "duration_share": 1.0}
    coverage = payload["report_timing_window_coverage"]
    assert coverage["command"]["started_only_count"] == 1
    assert coverage["command"]["ended_only_count"] == 0
    assert coverage["command"]["missing_started_at_count"] == 0
    assert coverage["command"]["missing_ended_at_count"] == 1
    assert coverage["edit"]["started_only_count"] == 0
    assert coverage["edit"]["ended_only_count"] == 1
    assert coverage["edit"]["missing_started_at_count"] == 1
    assert coverage["edit"]["missing_ended_at_count"] == 0
    assert coverage["activity"]["started_only_count"] == 1
    assert coverage["activity"]["ended_only_count"] == 1
    assert coverage["activity"]["missing_started_at_count"] == 1
    assert coverage["activity"]["missing_ended_at_count"] == 1

    text = build_markdown_summary(trace)
    assert "covered_duration_ms=4000" in text
    assert "command=rows=1/started_at=1/ended_at=0/started_only=1/ended_only=0/missing_started_at=0/missing_ended_at=1" in text
    assert "edit=rows=1/started_at=0/ended_at=1/started_only=0/ended_only=1/missing_started_at=1/missing_ended_at=0" in text
    assert "activity=rows=2/started_at=1/ended_at=1/started_only=1/ended_only=1/missing_started_at=1/missing_ended_at=1" in text
    assert "covered_intervals=(started_at=2026-04-25T00:00:00Z, ended_at=2026-04-25T00:00:03Z, duration_ms=3000); (started_at=2026-04-25T00:00:04Z, ended_at=2026-04-25T00:00:05Z, duration_ms=1000)" in text
    assert "uncovered_duration_ms=1000" in text
    assert "uncovered_intervals=(started_at=2026-04-25T00:00:03Z, ended_at=2026-04-25T00:00:04Z, duration_ms=1000)" in text
    assert "uncovered_interval_count=1" in text
    assert "average_uncovered_interval_ms=1000.0" in text
    assert "largest_uncovered_interval=(started_at=2026-04-25T00:00:03Z, ended_at=2026-04-25T00:00:04Z, duration_ms=1000)" in text
    assert "coverage_ratio=0.8" in text
    assert "idle_ratio=0.2" in text
    assert "covered_interval_count=2" in text
    assert "merged_covered_interval_count=2" in text


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
