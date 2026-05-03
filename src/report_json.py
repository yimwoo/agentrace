from src.failure_summary import build_failure_summary
from src.trace_schema import build_run_summary, summarize_trace, event_duration_ms


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
            "exit_code": event.get("exit_code", details.get("exit_code")),
        }
        if event.get("started_at"):
            row["started_at"] = event["started_at"]
        if event.get("ended_at"):
            row["ended_at"] = event["ended_at"]
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
            "added_lines": change.get("added_lines", details.get("added_lines")),
            "removed_lines": change.get("removed_lines", details.get("removed_lines")),
            "summary": change.get("summary") or details.get("summary"),
        }
        if event.get("started_at"):
            row["started_at"] = event["started_at"]
        if event.get("ended_at"):
            row["ended_at"] = event["ended_at"]
        if event_ref in artifact_refs:
            row["artifacts"] = artifact_refs[event_ref]
        rows.append(row)
    return rows


def _numeric_value(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return value


def build_command_timing_summary(rows):
    """Build aggregate command timing metrics for quick report inspection."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    slowest = None
    for row in normalized_rows:
        if slowest is None or _numeric_value(row.get("duration_ms")) > _numeric_value(slowest.get("duration_ms")):
            slowest = row
    return {
        "count": len(normalized_rows),
        "total_duration_ms": sum(_numeric_value(row.get("duration_ms")) for row in normalized_rows),
        "failed_count": sum(1 for row in normalized_rows if row.get("status") in {"failed", "error"} or _numeric_value(row.get("exit_code")) != 0),
        "slowest": None if slowest is None else {
            "event": slowest.get("event"),
            "command": slowest.get("command"),
            "duration_ms": _numeric_value(slowest.get("duration_ms")),
            "status": slowest.get("status"),
            "exit_code": slowest.get("exit_code"),
        },
    }


def build_edit_summary_totals(rows):
    """Build aggregate edit impact metrics for quick report inspection."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    files = [row.get("path") for row in normalized_rows if row.get("path")]
    return {
        "count": len(normalized_rows),
        "files_changed": files,
        "files_changed_count": len(set(files)),
        "total_added_lines": sum(_numeric_value(row.get("added_lines")) for row in normalized_rows),
        "total_removed_lines": sum(_numeric_value(row.get("removed_lines")) for row in normalized_rows),
        "total_duration_ms": sum(_numeric_value(row.get("duration_ms")) for row in normalized_rows),
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
