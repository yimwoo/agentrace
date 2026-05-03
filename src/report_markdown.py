from src.report_json import build_json_summary


def _format_artifacts(row):
    artifacts = row.get("artifacts") or []
    if not artifacts:
        return ""
    refs = "; ".join(f"{artifact['kind']}={artifact['path']}" for artifact in artifacts)
    return f", artifacts: {refs}"


def _format_time_window(row):
    parts = []
    if row.get("started_at"):
        parts.append(f"started_at={row['started_at']}")
    if row.get("ended_at"):
        parts.append(f"ended_at={row['ended_at']}")
    return f", {', '.join(parts)}" if parts else ""


def _format_slowest_command(slowest):
    if not slowest:
        return "none"
    event = slowest.get("event") or "summary"
    command = slowest.get("command") or "<unknown command>"
    duration = slowest.get("duration_ms", 0)
    status = slowest.get("status") or "unknown"
    exit_code = "unknown" if slowest.get("exit_code") is None else slowest.get("exit_code")
    return f"{event}: `{command}` ({duration}ms, status={status}, exit_code={exit_code})"


def _format_changed_files(files):
    if not files:
        return "none"
    return ", ".join(files)


def _format_command_timing(rows):
    if not rows:
        return ["## Command Timing", "", "No command events recorded."]
    lines = ["## Command Timing", ""]
    for row in rows:
        command = row["command"] or "<unknown command>"
        duration = row["duration_ms"]
        exit_code = "unknown" if row["exit_code"] is None else row["exit_code"]
        cwd = f", cwd={row['cwd']}" if row.get("cwd") else ""
        time_window = _format_time_window(row)
        artifacts = _format_artifacts(row)
        event = row.get("event", "summary")
        lines.append(f"- {event}: `{command}` — {duration}ms, status={row['status']}, exit_code={exit_code}{cwd}{time_window}{artifacts}")
    return lines


def _format_edit_summary(rows):
    if not rows:
        return ["## Edit Summary", "", "No file edit events recorded."]
    lines = ["## Edit Summary", ""]
    for row in rows:
        added = 0 if row["added_lines"] is None else row["added_lines"]
        removed = 0 if row["removed_lines"] is None else row["removed_lines"]
        summary = row["summary"] or "No edit summary recorded."
        status = f", status={row['status']}" if row.get("status") else ""
        duration = f", duration_ms={row['duration_ms']}" if "duration_ms" in row else ""
        time_window = _format_time_window(row)
        artifacts = _format_artifacts(row)
        path = row.get("path") or "<unknown file>"
        kind = row.get("kind") or "unknown"
        lines.append(f"- {path}: {kind} (+{added}/-{removed}) — {summary}{status}{duration}{time_window}{artifacts}")
    return lines


def build_markdown_summary(trace):
    payload = build_json_summary(trace)
    command_totals = payload["command_timing_summary"]
    edit_totals = payload["edit_summary_totals"]
    lines = [
        f"# Trace Summary: {payload['task']}",
        f"- run_id: {payload['run_id']}",
        f"- status: {payload['status']}",
        f"- event_count: {payload['summary']['event_count']}",
        f"- ok_events: {payload['summary']['ok_events']}",
        f"- total_duration_ms: {payload['summary']['total_duration_ms']}",
        f"- command_count: {command_totals['count']}",
        f"- command_total_duration_ms: {command_totals['total_duration_ms']}",
        f"- command_average_duration_ms: {command_totals['average_duration_ms']}",
        f"- command_failed_count: {command_totals['failed_count']}",
        f"- slowest_command: {_format_slowest_command(command_totals['slowest'])}",
        f"- files_changed_count: {edit_totals['files_changed_count']}",
        f"- files_changed: {_format_changed_files(edit_totals['files_changed'])}",
        f"- edit_total_lines: +{edit_totals['total_added_lines']}/-{edit_totals['total_removed_lines']}",
        f"- edit_net_line_delta: {edit_totals['net_line_delta']}",
        f"- edit_total_duration_ms: {edit_totals['total_duration_ms']}",
        "",
    ]
    lines.extend(_format_command_timing(payload["command_timing"]))
    lines.append("")
    lines.extend(_format_edit_summary(payload["edit_summary"]))
    return "\n".join(lines) + "\n"
