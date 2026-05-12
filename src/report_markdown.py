from src.report_json import build_json_summary


def _format_artifacts(row):
    artifacts = row.get("artifacts") or []
    if not artifacts:
        return ""
    refs = "; ".join(f"{artifact['kind']}={artifact['path']}" for artifact in artifacts)
    return f", artifacts: {refs}"


def _format_artifact_details(row):
    artifacts = row.get("artifacts") or []
    if not artifacts:
        return ""
    refs = "; ".join(f"{artifact['kind']}={artifact['path']}" for artifact in artifacts)
    return f"artifacts={refs}"


def _format_time_window(row):
    parts = []
    if row.get("started_at"):
        parts.append(f"started_at={row['started_at']}")
    if row.get("ended_at"):
        parts.append(f"ended_at={row['ended_at']}")
    return f", {', '.join(parts)}" if parts else ""


def _format_duration_source(row):
    source = row.get("duration_source")
    if not source and "duration_ms" in row:
        source = "explicit"
    if not source:
        return ""
    return f", duration_source={source}"


def _format_slowest_command(slowest):
    if not slowest:
        return "none"
    event = slowest.get("event") or "summary"
    command = slowest.get("command") or "<unknown command>"
    duration = slowest.get("duration_ms", 0)
    status = slowest.get("status") or "unknown"
    exit_code = "unknown" if slowest.get("exit_code") is None else slowest.get("exit_code")
    duration_source = _format_duration_source(slowest).removeprefix(", ")
    timing = _format_time_window(slowest).removeprefix(", ")
    details = [f"{duration}ms", f"status={status}", f"exit_code={exit_code}"]
    if duration_source:
        details.append(duration_source)
    if timing:
        details.append(timing)
    artifact_details = _format_artifact_details(slowest)
    if artifact_details:
        details.append(artifact_details)
    return f"{event}: `{command}` ({', '.join(details)})"


def _format_changed_files(files):
    if not files:
        return "none"
    return ", ".join(files)


def _format_repeated_commands(repeated_commands):
    if not repeated_commands:
        return "none"
    return ", ".join(f"`{command}`={count}" for command, count in sorted(repeated_commands.items()))


def _format_command_attempts(command_attempts):
    if not command_attempts:
        return "none"
    lines = []
    for row in command_attempts:
        details = [
            f"count={row.get('count', 0)}",
            f"total_duration_ms={row.get('total_duration_ms', 0)}",
            f"average_duration_ms={row.get('average_duration_ms', 0)}",
            f"failed_count={row.get('failed_count', 0)}",
            f"statuses={_format_status_counts(row.get('status_counts'))}",
        ]
        details.append(f"duration_sources={_format_status_counts(row.get('duration_source_counts'))}")
        time_window = _format_aggregate_time_window(row.get("time_window"))
        if time_window != "none":
            details.append(f"time_window={time_window}")
        if row.get("first_event"):
            details.append(f"first_event={row['first_event']}")
        if row.get("last_event"):
            details.append(f"last_event={row['last_event']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"`{row.get('command') or '<unknown command>'}` ({', '.join(details)})")
    return "; ".join(lines)


def _format_file_change_totals(file_change_totals):
    if not file_change_totals:
        return "none"
    lines = []
    for row in file_change_totals:
        path = row.get("path") or "<unknown file>"
        details = [
            f"count={row.get('count', 0)}",
            f"failed_count={row.get('failed_count', 0)}",
            f"+{row.get('total_added_lines', 0)}/-{row.get('total_removed_lines', 0)}",
            f"net={row.get('net_line_delta', 0)}",
            f"total_duration_ms={row.get('total_duration_ms', 0)}",
            f"average_duration_ms={row.get('average_duration_ms', 0)}",
            f"statuses={_format_status_counts(row.get('status_counts'))}",
            f"kinds={_format_status_counts(row.get('kind_counts'))}",
            f"duration_sources={_format_status_counts(row.get('duration_source_counts'))}",
        ]
        time_window = _format_aggregate_time_window(row.get("time_window"))
        if time_window != "none":
            details.append(f"time_window={time_window}")
        if row.get("first_event"):
            details.append(f"first_event={row['first_event']}")
        if row.get("last_event"):
            details.append(f"last_event={row['last_event']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{path} ({', '.join(details)})")
    return "; ".join(lines)



def _format_command_cwd_totals(cwd_totals):
    if not cwd_totals:
        return "none"
    lines = []
    for row in cwd_totals:
        cwd = row.get("cwd") or "unknown"
        details = [
            f"count={row.get('count', 0)}",
            f"commands={_format_changed_files(row.get('commands_run'))}",
            f"failed_count={row.get('failed_count', 0)}",
            f"total_duration_ms={row.get('total_duration_ms', 0)}",
            f"average_duration_ms={row.get('average_duration_ms', 0)}",
            f"statuses={_format_status_counts(row.get('status_counts'))}",
            f"duration_sources={_format_status_counts(row.get('duration_source_counts'))}",
        ]
        time_window = _format_aggregate_time_window(row.get("time_window"))
        if time_window != "none":
            details.append(f"time_window={time_window}")
        if row.get("first_event"):
            details.append(f"first_event={row['first_event']}")
        if row.get("last_event"):
            details.append(f"last_event={row['last_event']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{cwd} ({', '.join(details)})")
    return "; ".join(lines)


def _format_edit_kind_totals(kind_totals):
    if not kind_totals:
        return "none"
    lines = []
    for row in kind_totals:
        kind = row.get("kind") or "unknown"
        details = [
            f"count={row.get('count', 0)}",
            f"files={_format_changed_files(row.get('files_changed'))}",
            f"failed_count={row.get('failed_count', 0)}",
            f"+{row.get('total_added_lines', 0)}/-{row.get('total_removed_lines', 0)}",
            f"net={row.get('net_line_delta', 0)}",
            f"total_duration_ms={row.get('total_duration_ms', 0)}",
            f"average_duration_ms={row.get('average_duration_ms', 0)}",
            f"statuses={_format_status_counts(row.get('status_counts'))}",
            f"duration_sources={_format_status_counts(row.get('duration_source_counts'))}",
        ]
        time_window = _format_aggregate_time_window(row.get("time_window"))
        if time_window != "none":
            details.append(f"time_window={time_window}")
        if row.get("first_event"):
            details.append(f"first_event={row['first_event']}")
        if row.get("last_event"):
            details.append(f"last_event={row['last_event']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{kind} ({', '.join(details)})")
    return "; ".join(lines)

def _format_failed_commands(failed_commands):
    if not failed_commands:
        return "none"
    lines = []
    for row in failed_commands:
        event = row.get("event") or "summary"
        command = row.get("command") or "<unknown command>"
        duration = row.get("duration_ms", 0)
        status = row.get("status") or "unknown"
        exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
        duration_source = _format_duration_source(row).removeprefix(", ")
        timing = _format_time_window(row).removeprefix(", ")
        details = [f"{duration}ms", f"status={status}", f"exit_code={exit_code}"]
        if duration_source:
            details.append(duration_source)
        if timing:
            details.append(timing)
        if row.get("stdout_preview"):
            details.append(f"stdout_preview={row['stdout_preview']}")
        if row.get("stderr_preview"):
            details.append(f"stderr_preview={row['stderr_preview']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{event}: `{command}` ({', '.join(details)})")
    return "; ".join(lines)


def _format_failed_edits(failed_edits):
    if not failed_edits:
        return "none"
    lines = []
    for row in failed_edits:
        event = row.get("event") or "summary"
        path = row.get("path") or "<unknown file>"
        kind = row.get("kind") or "unknown"
        duration = row.get("duration_ms", 0)
        status = row.get("status") or "unknown"
        duration_source = _format_duration_source(row).removeprefix(", ")
        timing = _format_time_window(row).removeprefix(", ")
        added = row.get("added_lines", 0)
        removed = row.get("removed_lines", 0)
        net = row.get("net_line_delta", added - removed)
        details = [f"kind={kind}", f"+{added}/-{removed}", f"net={net}", f"{duration}ms", f"status={status}"]
        if duration_source:
            details.append(duration_source)
        if timing:
            details.append(timing)
        if row.get("summary"):
            details.append(f"summary={row['summary']}")
        if row.get("error_message"):
            details.append(f"error_message={row['error_message']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{event}: {path} ({', '.join(details)})")
    return "; ".join(lines)


def _format_status_counts(status_counts):
    if not status_counts:
        return "none"
    return ", ".join(f"{status}={count}" for status, count in sorted(status_counts.items()))


def _format_aggregate_time_window(time_window):
    if not time_window:
        return "none"
    parts = []
    if time_window.get("started_at"):
        parts.append(f"started_at={time_window['started_at']}")
    if time_window.get("ended_at"):
        parts.append(f"ended_at={time_window['ended_at']}")
    return ", ".join(parts) if parts else "none"


def _format_largest_edit(largest_edit):
    if not largest_edit:
        return "none"
    event = largest_edit.get("event") or "summary"
    path = largest_edit.get("path") or "<unknown file>"
    added = largest_edit.get("added_lines", 0)
    removed = largest_edit.get("removed_lines", 0)
    net = largest_edit.get("net_line_delta", 0)
    duration = largest_edit.get("duration_ms", 0)
    status = largest_edit.get("status") or "unknown"
    duration_source = _format_duration_source(largest_edit).removeprefix(", ")
    timing = _format_time_window(largest_edit).removeprefix(", ")
    details = [f"+{added}/-{removed}", f"net={net}", f"duration_ms={duration}", f"status={status}"]
    if duration_source:
        details.append(duration_source)
    if timing:
        details.append(timing)
    artifact_details = _format_artifact_details(largest_edit)
    if artifact_details:
        details.append(artifact_details)
    return f"{event}: {path} ({', '.join(details)})"


def _format_command_timing(rows):
    if not rows:
        return ["## Command Timing", "", "No command events recorded."]
    lines = ["## Command Timing", ""]
    for row in rows:
        command = row.get("command") or "<unknown command>"
        duration = row.get("duration_ms", 0)
        exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
        cwd = f", cwd={row['cwd']}" if row.get("cwd") else ""
        time_window = _format_time_window(row)
        duration_source = _format_duration_source(row)
        artifacts = _format_artifacts(row)
        output_context = ""
        if row.get("stdout_preview"):
            output_context += f", stdout_preview={row['stdout_preview']}"
        if row.get("stderr_preview"):
            output_context += f", stderr_preview={row['stderr_preview']}"
        event = row.get("event", "summary")
        lines.append(f"- {event}: `{command}` — {duration}ms, status={row.get('status')}, exit_code={exit_code}{duration_source}{cwd}{time_window}{output_context}{artifacts}")
    return lines


def _format_edit_summary(rows):
    if not rows:
        return ["## Edit Summary", "", "No file edit events recorded."]
    lines = ["## Edit Summary", ""]
    for row in rows:
        added = 0 if row.get("added_lines") is None else row.get("added_lines", 0)
        removed = 0 if row.get("removed_lines") is None else row.get("removed_lines", 0)
        summary = row.get("summary") or "No edit summary recorded."
        status = f", status={row['status']}" if row.get("status") else ""
        duration = f", duration_ms={row['duration_ms']}" if "duration_ms" in row else ""
        net_delta = f", net={row['net_line_delta']}" if "net_line_delta" in row else ""
        duration_source = _format_duration_source(row)
        time_window = _format_time_window(row)
        error_context = f", error_message={row['error_message']}" if row.get("error_message") else ""
        artifacts = _format_artifacts(row)
        path = row.get("path") or "<unknown file>"
        kind = row.get("kind") or "unknown"
        lines.append(f"- {path}: {kind} (+{added}/-{removed}{net_delta}) — {summary}{status}{duration}{duration_source}{time_window}{error_context}{artifacts}")
    return lines




def _format_failed_activity(failed_activity):
    if not failed_activity:
        return "none"
    lines = []
    for row in failed_activity:
        event = row.get("event") or "summary"
        duration = row.get("duration_ms", 0)
        status = row.get("status") or "unknown"
        duration_source = _format_duration_source(row).removeprefix(", ")
        timing = _format_time_window(row).removeprefix(", ")
        details = [f"type={row.get('type') or 'unknown'}", f"{duration}ms", f"status={status}"]
        if duration_source:
            details.append(duration_source)
        if timing:
            details.append(timing)
        if row.get("type") == "command":
            identity = f"`{row.get('command') or '<unknown command>'}`"
            exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
            details.append(f"exit_code={exit_code}")
            if row.get("cwd"):
                details.append(f"cwd={row['cwd']}")
            if row.get("stdout_preview"):
                details.append(f"stdout_preview={row['stdout_preview']}")
            if row.get("stderr_preview"):
                details.append(f"stderr_preview={row['stderr_preview']}")
        else:
            identity = row.get("path") or "<unknown file>"
            kind = row.get("kind") or "unknown"
            added = row.get("added_lines", 0)
            removed = row.get("removed_lines", 0)
            net = row.get("net_line_delta", added - removed)
            details.extend([f"kind={kind}", f"+{added}/-{removed}", f"net={net}"])
            if row.get("summary"):
                details.append(f"summary={row['summary']}")
            if row.get("error_message"):
                details.append(f"error_message={row['error_message']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{event}: {identity} ({', '.join(details)})")
    return "; ".join(lines)


def _format_first_failed_activity(first_failed_activity):
    if not first_failed_activity:
        return "none"
    return _format_failed_activity([first_failed_activity])


def _format_first_activity(first_activity):
    if not first_activity:
        return "none"
    return _format_failed_activity([first_activity])


def _format_slowest_activity(slowest_activity):
    if not slowest_activity:
        return "none"
    return _format_failed_activity([slowest_activity])


def _format_fastest_activity(fastest_activity):
    if not fastest_activity:
        return "none"
    return _format_failed_activity([fastest_activity])


def _format_last_activity(last_activity):
    if not last_activity:
        return "none"
    return _format_failed_activity([last_activity])


def _format_activity_timeline_summary(timeline_totals):
    if not timeline_totals:
        return "none"
    details = [
        f"count={timeline_totals.get('count', 0)}",
        f"types={_format_status_counts(timeline_totals.get('type_counts'))}",
        f"statuses={_format_status_counts(timeline_totals.get('status_counts'))}",
        f"duration_sources={_format_status_counts(timeline_totals.get('duration_source_counts'))}",
        f"total_duration_ms={timeline_totals.get('total_duration_ms', 0)}",
        f"average_duration_ms={timeline_totals.get('average_duration_ms', 0)}",
        f"median_duration_ms={timeline_totals.get('median_duration_ms', 0)}",
        f"first_activity={_format_first_activity(timeline_totals.get('first_activity'))}",
        f"slowest_activity={_format_slowest_activity(timeline_totals.get('slowest_activity'))}",
        f"fastest_activity={_format_fastest_activity(timeline_totals.get('fastest_activity'))}",
        f"last_activity={_format_last_activity(timeline_totals.get('last_activity'))}",
        f"failed_count={timeline_totals.get('failed_count', 0)}",
    ]
    time_window = _format_aggregate_time_window(timeline_totals.get("time_window"))
    if time_window != "none":
        details.append(f"time_window={time_window}")
    return ", ".join(details)


def _format_activity_timeline(rows):
    if not rows:
        return ["## Activity Timeline", "", "No command or file edit activity recorded."]
    lines = ["## Activity Timeline", ""]
    for row in rows:
        event = row.get("event") or "summary"
        duration = row.get("duration_ms", 0)
        duration_source = _format_duration_source(row)
        time_window = _format_time_window(row)
        artifacts = _format_artifacts(row)
        status = row.get("status") or "unknown"
        if row.get("type") == "command":
            command = row.get("command") or "<unknown command>"
            exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
            cwd = f", cwd={row['cwd']}" if row.get("cwd") else ""
            output_context = ""
            if row.get("stdout_preview"):
                output_context += f", stdout_preview={row['stdout_preview']}"
            if row.get("stderr_preview"):
                output_context += f", stderr_preview={row['stderr_preview']}"
            lines.append(f"- {event}: command `{command}` — {duration}ms, status={status}, exit_code={exit_code}{duration_source}{cwd}{time_window}{output_context}{artifacts}")
            continue

        path = row.get("path") or "<unknown file>"
        kind = row.get("kind") or "unknown"
        added = row.get("added_lines", 0)
        removed = row.get("removed_lines", 0)
        net = row.get("net_line_delta", added - removed)
        summary = row.get("summary") or "No edit summary recorded."
        error_context = f", error_message={row['error_message']}" if row.get("error_message") else ""
        lines.append(f"- {event}: edit {path} ({kind}, +{added}/-{removed}, net={net}) — {summary}, status={status}, duration_ms={duration}{duration_source}{time_window}{error_context}{artifacts}")
    return lines


def build_markdown_summary(trace):
    payload = build_json_summary(trace)
    command_totals = payload["command_timing_summary"]
    edit_totals = payload["edit_summary_totals"]
    timeline_totals = payload["activity_timeline_summary"]
    lines = [
        f"# Trace Summary: {payload['task']}",
        f"- run_id: {payload['run_id']}",
        f"- status: {payload['status']}",
        f"- event_count: {payload['summary']['event_count']}",
        f"- ok_events: {payload['summary']['ok_events']}",
        f"- total_duration_ms: {payload['summary']['total_duration_ms']}",
        f"- command_count: {command_totals['count']}",
        f"- unique_command_count: {command_totals['unique_command_count']}",
        f"- commands_run: {_format_changed_files(command_totals['commands_run'])}",
        f"- repeated_commands: {_format_repeated_commands(command_totals['repeated_commands'])}",
        f"- command_attempts: {_format_command_attempts(command_totals['command_attempts'])}",
        f"- command_cwd_counts: {_format_status_counts(command_totals['cwd_counts'])}",
        f"- command_cwd_totals: {_format_command_cwd_totals(command_totals['cwd_totals'])}",
        f"- command_total_duration_ms: {command_totals['total_duration_ms']}",
        f"- command_average_duration_ms: {command_totals['average_duration_ms']}",
        f"- command_median_duration_ms: {command_totals['median_duration_ms']}",
        f"- command_failed_count: {command_totals['failed_count']}",
        f"- failed_commands: {_format_failed_commands(command_totals['failed_commands'])}",
        f"- command_status_counts: {_format_status_counts(command_totals['status_counts'])}",
        f"- command_duration_sources: {_format_status_counts(command_totals['duration_source_counts'])}",
        f"- command_time_window: {_format_aggregate_time_window(command_totals['time_window'])}",
        f"- slowest_command: {_format_slowest_command(command_totals['slowest'])}",
        f"- activity_timeline_summary: {_format_activity_timeline_summary(timeline_totals)}",
        f"- first_failed_activity: {_format_first_failed_activity(timeline_totals.get('first_failed_activity'))}",
        f"- failed_activity: {_format_failed_activity(timeline_totals.get('failed_activity'))}",
        f"- files_changed_count: {edit_totals['files_changed_count']}",
        f"- files_changed: {_format_changed_files(edit_totals['files_changed'])}",
        f"- file_change_totals: {_format_file_change_totals(edit_totals['file_change_totals'])}",
        f"- edit_failed_count: {edit_totals['failed_count']}",
        f"- failed_edits: {_format_failed_edits(edit_totals['failed_edits'])}",
        f"- edit_kind_counts: {_format_status_counts(edit_totals['kind_counts'])}",
        f"- edit_kind_totals: {_format_edit_kind_totals(edit_totals['kind_totals'])}",
        f"- edit_status_counts: {_format_status_counts(edit_totals['status_counts'])}",
        f"- edit_duration_sources: {_format_status_counts(edit_totals['duration_source_counts'])}",
        f"- edit_time_window: {_format_aggregate_time_window(edit_totals['time_window'])}",
        f"- edit_total_lines: +{edit_totals['total_added_lines']}/-{edit_totals['total_removed_lines']}",
        f"- edit_net_line_delta: {edit_totals['net_line_delta']}",
        f"- edit_total_duration_ms: {edit_totals['total_duration_ms']}",
        f"- edit_average_duration_ms: {edit_totals['average_duration_ms']}",
        f"- edit_median_duration_ms: {edit_totals['median_duration_ms']}",
        f"- largest_edit: {_format_largest_edit(edit_totals['largest_edit'])}",
        "",
    ]
    lines.extend(_format_command_timing(payload["command_timing"]))
    lines.append("")
    lines.extend(_format_edit_summary(payload["edit_summary"]))
    lines.append("")
    lines.extend(_format_activity_timeline(payload["activity_timeline"]))
    return "\n".join(lines) + "\n"
