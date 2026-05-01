from src.report_json import build_json_summary


def _format_command_timing(rows):
    if not rows:
        return ["## Command Timing", "", "No command events recorded."]
    lines = ["## Command Timing", ""]
    for row in rows:
        command = row["command"] or "<unknown command>"
        duration = row["duration_ms"]
        exit_code = "unknown" if row["exit_code"] is None else row["exit_code"]
        lines.append(f"- {row['event']}: `{command}` — {duration}ms, status={row['status']}, exit_code={exit_code}")
    return lines


def _format_edit_summary(rows):
    if not rows:
        return ["## Edit Summary", "", "No file edit events recorded."]
    lines = ["## Edit Summary", ""]
    for row in rows:
        added = 0 if row["added_lines"] is None else row["added_lines"]
        removed = 0 if row["removed_lines"] is None else row["removed_lines"]
        summary = row["summary"] or "No edit summary recorded."
        lines.append(f"- {row['path']}: {row['kind']} (+{added}/-{removed}) — {summary}")
    return lines


def build_markdown_summary(trace):
    payload = build_json_summary(trace)
    lines = [
        f"# Trace Summary: {payload['task']}",
        f"- run_id: {payload['run_id']}",
        f"- status: {payload['status']}",
        f"- event_count: {payload['summary']['event_count']}",
        f"- ok_events: {payload['summary']['ok_events']}",
        f"- total_duration_ms: {payload['summary']['total_duration_ms']}",
        "",
    ]
    lines.extend(_format_command_timing(payload["command_timing"]))
    lines.append("")
    lines.extend(_format_edit_summary(payload["edit_summary"]))
    return "\n".join(lines) + "\n"
