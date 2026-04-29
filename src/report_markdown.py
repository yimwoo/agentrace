from src.report_json import build_json_summary


def build_markdown_summary(trace):
    payload = build_json_summary(trace)
    return "\n".join([
        f"# Trace Summary: {payload['task']}",
        f"- run_id: {payload['run_id']}",
        f"- status: {payload['status']}",
        f"- event_count: {payload['summary']['event_count']}",
        f"- ok_events: {payload['summary']['ok_events']}",
        f"- total_duration_ms: {payload['summary']['total_duration_ms']}",
    ]) + "\n"
