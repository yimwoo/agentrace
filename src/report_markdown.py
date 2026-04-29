from src.report_json import build_json_summary


def build_markdown_summary(trace):
    payload = build_json_summary(trace)
    run_summary = payload["run_summary"]
    event_counts = ", ".join(
        f"{event_type}: {count}"
        for event_type, count in sorted(run_summary["event_counts"].items())
    ) or "none"
    files_changed = ", ".join(run_summary["files_changed"]) or "none"
    commands_run = "; ".join(run_summary["commands_run"]) or "none"
    inspection_targets = "; ".join(run_summary["next_inspection_targets"]) or "none"

    return "\n".join([
        f"# Trace Summary: {payload['task']}",
        f"- run_id: {payload['run_id']}",
        f"- status: {payload['status']}",
        f"- result: {run_summary['result']}",
        f"- failure_reason: {run_summary['failure_reason'] or 'none'}",
        f"- event_count: {payload['summary']['event_count']}",
        f"- ok_events: {payload['summary']['ok_events']}",
        f"- total_duration_ms: {payload['summary']['total_duration_ms']}",
        f"- event_counts: {event_counts}",
        f"- files_changed: {files_changed}",
        f"- commands_run: {commands_run}",
        f"- next_inspection_targets: {inspection_targets}",
    ]) + "\n"
