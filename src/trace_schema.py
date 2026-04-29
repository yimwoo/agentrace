from collections import Counter

TRACE_EVENT_FIELDS = [
    "timestamp", "type", "name", "status", "details", "duration_ms"
]


def validate_trace_event(event):
    missing = [field for field in TRACE_EVENT_FIELDS if field not in event]
    return {"ok": not missing, "missing": missing}


def _event_type(event):
    return event.get("type", "unknown")


def _command_value(event):
    command = event.get("command")
    if isinstance(command, dict):
        return command.get("value")
    if isinstance(command, str):
        return command
    details = event.get("details", {})
    if isinstance(details, dict):
        return details.get("command")
    return None


def _file_path(event):
    file_payload = event.get("file")
    if isinstance(file_payload, dict):
        return file_payload.get("path")
    if isinstance(file_payload, str):
        return file_payload
    details = event.get("details", {})
    if isinstance(details, dict):
        return details.get("file") or details.get("path")
    return None


def _failure_target(event):
    event_id = event.get("id") or event.get("name") or f"seq {event.get('seq')}"
    event_type = _event_type(event)
    if event_type == "command":
        return f"command {event_id} stderr_preview"
    if event_type == "test_result":
        return f"test_result {event_id} failure details"
    if event.get("error"):
        return f"{event_type} {event_id} error"
    return f"{event_type} {event_id} details"


def build_run_summary(trace):
    """Build the compact run-level summary described in TRACE_SCHEMA.md D-08."""
    events = trace.get("events", [])
    event_counts = dict(Counter(_event_type(event) for event in events))
    files_changed = sorted({path for event in events for path in [_file_path(event)] if path})
    commands_run = [command for event in events for command in [_command_value(event)] if command]
    failed_events = [event for event in events if event.get("status") in {"failed", "error"} or event.get("error")]

    run = trace.get("run", {})
    existing_summary = trace.get("summary", {})
    result_summary = trace.get("result_summary", {})
    result = existing_summary.get("result") or run.get("status") or result_summary.get("status") or "unknown"
    failure_reason = existing_summary.get("failure_reason")
    if failure_reason is None and failed_events:
        error = failed_events[0].get("error")
        if isinstance(error, dict):
            failure_reason = error.get("message")
        failure_reason = failure_reason or failed_events[0].get("stderr_preview") or failed_events[0].get("message")

    return {
        "result": result,
        "failure_reason": failure_reason,
        "event_counts": event_counts,
        "files_changed": files_changed,
        "commands_run": commands_run,
        "next_inspection_targets": [_failure_target(event) for event in failed_events[:3]],
    }


def summarize_trace(events):
    return {
        "event_count": len(events),
        "ok_events": sum(1 for event in events if validate_trace_event(event)["ok"]),
        "total_duration_ms": sum(event.get("duration_ms", 0) for event in events),
    }
