from datetime import timezone

from src.failure_summary import build_failure_summary
from src.trace_schema import build_run_summary, summarize_trace, event_duration_ms, event_duration_source, _parse_trace_timestamp


def _event_ref(event):
    return event.get("id") or event.get("seq") or event.get("name")


def _run_metadata(trace):
    run = trace.get("run", {}) if isinstance(trace.get("run"), dict) else {}
    return {
        "task": run.get("task") or trace.get("task"),
        "run_id": run.get("id") or trace.get("run_id"),
        "status": run.get("status") or trace.get("result_summary", {}).get("status"),
        "timing": {"wall_clock_ms": run.get("duration_ms")} if "duration_ms" in run else trace.get("timing", {}),
    }


def _artifact_refs_by_event(artifacts):
    refs = {}
    for artifact in artifacts or []:
        if not isinstance(artifact, dict):
            continue
        event_id = artifact.get("event_id")
        path = artifact.get("path")
        if not event_id or not path:
            continue
        refs.setdefault(event_id, []).append({
            "kind": artifact.get("kind", "artifact"),
            "path": path,
        })
    return refs


def build_command_timing(events, artifacts=None):
    """Extract report-ready timing rows for command events."""
    rows = []
    artifact_refs = _artifact_refs_by_event(artifacts)
    for event in events:
        if not isinstance(event, dict) or event.get("type") != "command":
            continue
        command = event.get("command") if isinstance(event.get("command"), dict) else {}
        details = event.get("details") if isinstance(event.get("details"), dict) else {}
        event_ref = _event_ref(event)
        row = {
            "event": event_ref,
            "command": command.get("value") or event.get("name") or details.get("command"),
            "cwd": command.get("cwd") or details.get("cwd"),
            "status": event.get("status"),
            "duration_ms": event_duration_ms(event),
            "duration_source": event_duration_source(event),
            "exit_code": event.get("exit_code", details.get("exit_code")),
        }
        if event.get("started_at"):
            row["started_at"] = event["started_at"]
        if event.get("ended_at"):
            row["ended_at"] = event["ended_at"]
        if event.get("stdout_preview") or details.get("stdout_preview"):
            row["stdout_preview"] = event.get("stdout_preview") or details.get("stdout_preview")
        if event.get("stderr_preview") or details.get("stderr_preview"):
            row["stderr_preview"] = event.get("stderr_preview") or details.get("stderr_preview")
        if event_ref in artifact_refs:
            row["artifacts"] = artifact_refs[event_ref]
        rows.append(row)
    return rows


def build_edit_summary(events, artifacts=None):
    """Extract report-ready summaries for file_edit events."""
    rows = []
    artifact_refs = _artifact_refs_by_event(artifacts)
    for event in events:
        if not isinstance(event, dict) or event.get("type") != "file_edit":
            continue
        file_info = event.get("file") if isinstance(event.get("file"), dict) else {}
        change = event.get("change") if isinstance(event.get("change"), dict) else {}
        details = event.get("details") if isinstance(event.get("details"), dict) else {}
        event_ref = _event_ref(event)
        row = {
            "event": event_ref,
            "path": file_info.get("path") or details.get("path") or event.get("name"),
            "kind": change.get("kind") or details.get("kind"),
            "status": event.get("status"),
            "duration_ms": event_duration_ms(event),
            "duration_source": event_duration_source(event),
            "added_lines": change.get("added_lines", details.get("added_lines")),
            "removed_lines": change.get("removed_lines", details.get("removed_lines")),
            "summary": change.get("summary") or details.get("summary"),
        }
        if event.get("started_at"):
            row["started_at"] = event["started_at"]
        if event.get("ended_at"):
            row["ended_at"] = event["ended_at"]
        error = event.get("error") if isinstance(event.get("error"), dict) else {}
        error_message = error.get("message") or details.get("error_message") or details.get("error")
        if error_message:
            row["error_message"] = error_message
        if event_ref in artifact_refs:
            row["artifacts"] = artifact_refs[event_ref]
        rows.append(row)
    return rows


def _numeric_value(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return value


def _normalized_timestamp(value):
    parsed = _parse_trace_timestamp(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _timestamp_extreme(rows, field, pick_max=False):
    candidates = []
    for row in rows:
        value = row.get(field)
        parsed = _normalized_timestamp(value)
        if parsed is not None:
            candidates.append((parsed, value))
    if not candidates:
        return None
    return max(candidates)[1] if pick_max else min(candidates)[1]


def _time_window(rows):
    started_at = _timestamp_extreme(rows, "started_at")
    ended_at = _timestamp_extreme(rows, "ended_at", pick_max=True)
    if started_at is None and ended_at is None:
        return None
    return {"started_at": started_at, "ended_at": ended_at}


def _duration_source_counts(rows):
    counts = {}
    for row in rows:
        source = row.get("duration_source") or "unknown"
        counts[source] = counts.get(source, 0) + 1
    return counts


def _ordered_values(rows, field):
    values = []
    seen = set()
    for row in rows:
        value = row.get(field)
        if not value or value in seen:
            continue
        seen.add(value)
        values.append(value)
    return values


def _value_counts(rows, field, missing_label=None):
    counts = {}
    for row in rows:
        value = row.get(field)
        if not value and missing_label is None:
            continue
        if not value:
            value = missing_label
        counts[value] = counts.get(value, 0) + 1
    return counts


def _repeated_value_counts(rows, field):
    return {value: count for value, count in _value_counts(rows, field).items() if count > 1}


def _is_failed_command(row):
    return row.get("status") in {"failed", "error"} or _numeric_value(row.get("exit_code")) != 0


def _failed_command_rows(rows):
    failed = []
    for row in rows:
        if not _is_failed_command(row):
            continue
        failed_row = {
            "event": row.get("event"),
            "command": row.get("command"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
            "status": row.get("status"),
            "exit_code": row.get("exit_code"),
            "started_at": row.get("started_at"),
            "ended_at": row.get("ended_at"),
        }
        if row.get("stdout_preview"):
            failed_row["stdout_preview"] = row["stdout_preview"]
        if row.get("stderr_preview"):
            failed_row["stderr_preview"] = row["stderr_preview"]
        failed.append(failed_row)
    return failed


def build_command_timing_summary(rows):
    """Build aggregate command timing metrics for quick report inspection."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    slowest = None
    status_counts = {}
    for row in normalized_rows:
        if slowest is None or _numeric_value(row.get("duration_ms")) > _numeric_value(slowest.get("duration_ms")):
            slowest = row
        status = row.get("status") or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    total_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in normalized_rows)
    commands_run = _ordered_values(normalized_rows, "command")
    return {
        "count": len(normalized_rows),
        "unique_command_count": len(commands_run),
        "commands_run": commands_run,
        "repeated_commands": _repeated_value_counts(normalized_rows, "command"),
        "cwd_counts": _value_counts(normalized_rows, "cwd", missing_label="unknown"),
        "total_duration_ms": total_duration_ms,
        "average_duration_ms": 0 if not normalized_rows else round(total_duration_ms / len(normalized_rows), 2),
        "failed_count": sum(1 for row in normalized_rows if _is_failed_command(row)),
        "failed_commands": _failed_command_rows(normalized_rows),
        "status_counts": status_counts,
        "duration_source_counts": _duration_source_counts(normalized_rows),
        "time_window": _time_window(normalized_rows),
        "slowest": None if slowest is None else {
            "event": slowest.get("event"),
            "command": slowest.get("command"),
            "duration_ms": _numeric_value(slowest.get("duration_ms")),
            "duration_source": slowest.get("duration_source"),
            "status": slowest.get("status"),
            "exit_code": slowest.get("exit_code"),
            "started_at": slowest.get("started_at"),
            "ended_at": slowest.get("ended_at"),
        },
    }


def _largest_edit_row(rows):
    largest = None
    for row in rows:
        if largest is None:
            largest = row
            continue
        row_churn = _numeric_value(row.get("added_lines")) + _numeric_value(row.get("removed_lines"))
        largest_churn = _numeric_value(largest.get("added_lines")) + _numeric_value(largest.get("removed_lines"))
        if row_churn > largest_churn:
            largest = row
    return largest


def _is_failed_edit(row):
    return row.get("status") in {"failed", "error"}


def _failed_edit_rows(rows):
    failed = []
    for row in rows:
        if not _is_failed_edit(row):
            continue
        failed_row = {
            "event": row.get("event"),
            "path": row.get("path"),
            "kind": row.get("kind"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
            "status": row.get("status"),
            "started_at": row.get("started_at"),
            "ended_at": row.get("ended_at"),
            "added_lines": _numeric_value(row.get("added_lines")),
            "removed_lines": _numeric_value(row.get("removed_lines")),
        }
        if row.get("summary"):
            failed_row["summary"] = row["summary"]
        if row.get("error_message"):
            failed_row["error_message"] = row["error_message"]
        failed.append(failed_row)
    return failed


def build_edit_summary_totals(rows):
    """Build aggregate edit impact metrics for quick report inspection."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    files = _ordered_values(normalized_rows, "path")
    status_counts = {}
    for row in normalized_rows:
        status = row.get("status") or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    total_added_lines = sum(_numeric_value(row.get("added_lines")) for row in normalized_rows)
    total_removed_lines = sum(_numeric_value(row.get("removed_lines")) for row in normalized_rows)
    total_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in normalized_rows)
    largest_edit = _largest_edit_row(normalized_rows)
    return {
        "count": len(normalized_rows),
        "files_changed": files,
        "files_changed_count": len(files),
        "failed_count": sum(1 for row in normalized_rows if _is_failed_edit(row)),
        "failed_edits": _failed_edit_rows(normalized_rows),
        "kind_counts": _value_counts(normalized_rows, "kind", missing_label="unknown"),
        "status_counts": status_counts,
        "duration_source_counts": _duration_source_counts(normalized_rows),
        "time_window": _time_window(normalized_rows),
        "total_added_lines": total_added_lines,
        "total_removed_lines": total_removed_lines,
        "net_line_delta": total_added_lines - total_removed_lines,
        "total_duration_ms": total_duration_ms,
        "average_duration_ms": 0 if not normalized_rows else round(total_duration_ms / len(normalized_rows), 2),
        "largest_edit": None if largest_edit is None else {
            "event": largest_edit.get("event"),
            "path": largest_edit.get("path"),
            "kind": largest_edit.get("kind"),
            "added_lines": _numeric_value(largest_edit.get("added_lines")),
            "removed_lines": _numeric_value(largest_edit.get("removed_lines")),
            "net_line_delta": _numeric_value(largest_edit.get("added_lines")) - _numeric_value(largest_edit.get("removed_lines")),
            "duration_ms": _numeric_value(largest_edit.get("duration_ms")),
            "duration_source": largest_edit.get("duration_source"),
            "status": largest_edit.get("status"),
            "started_at": largest_edit.get("started_at"),
            "ended_at": largest_edit.get("ended_at"),
        },
    }


def build_json_summary(trace):
    events = trace.get("events", [])
    summary = summarize_trace(events)
    metadata = _run_metadata(trace)
    run_summary = trace.get("summary") or build_run_summary(trace)
    command_timing = build_command_timing(events, trace.get("artifacts", [])) or run_summary.get("command_durations_ms", [])
    edit_summary = build_edit_summary(events, trace.get("artifacts", [])) or run_summary.get("edit_summaries", [])
    return {
        "task": metadata["task"],
        "run_id": metadata["run_id"],
        "status": metadata["status"],
        "timing": metadata["timing"],
        "summary": summary,
        "run_summary": run_summary,
        "failure_summary": build_failure_summary(trace),
        "command_timing_summary": build_command_timing_summary(command_timing),
        "command_timing": command_timing,
        "edit_summary_totals": build_edit_summary_totals(edit_summary),
        "edit_summary": edit_summary,
    }
