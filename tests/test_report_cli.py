import json
import pytest

from src.emit_example_trace import build_sample_trace
from src.report_cli import load_trace, main, render_trace_report


def test_render_trace_report_outputs_markdown_and_json():
    trace = build_sample_trace()
    markdown = render_trace_report(trace, "markdown")
    assert markdown.startswith("# Trace Summary: debug sample")
    payload = json.loads(render_trace_report(trace, "json"))
    assert payload["run_id"] == "sample-1"
    assert payload["status"] == "success"


def test_render_trace_report_rejects_unknown_format():
    with pytest.raises(ValueError):
        render_trace_report(build_sample_trace(), "xml")


def test_load_trace_reads_file(tmp_path):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(json.dumps(build_sample_trace()))
    assert load_trace(str(trace_path))["run"]["id"] == "sample-1"


def test_main_writes_markdown_output(tmp_path):
    trace_path = tmp_path / "trace.json"
    output_path = tmp_path / "report.md"
    trace_path.write_text(json.dumps(build_sample_trace()))
    assert main([str(trace_path), "--output", str(output_path)]) == 0
    assert "# Trace Summary: debug sample" in output_path.read_text()


def test_main_prints_json(capsys, tmp_path):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(json.dumps(build_sample_trace()))
    assert main([str(trace_path), "--format", "json"]) == 0
    captured = capsys.readouterr()
    assert json.loads(captured.out)["run_id"] == "sample-1"
