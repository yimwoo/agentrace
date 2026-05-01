LEGACY_TRACE_EVENT_FIELDS = [
    "timestamp", "type", "name", "status", "details", "duration_ms"
]

TRACE_EVENT_ENVELOPE_FIELDS = ["id", "seq", "type", "started_at", "status"]
TRACE_EVENT_STATUSES = {"started", "succeeded", "failed", "cancelled", "unknown"}
LEGACY_OK_STATUSES = {"ok", "success", "succeeded"}


def _missing_fields(event, fields):
    return [field for field in fields if field not in event]


def validate_trace_event(event):
    """Validate either the canonical event envelope or the legacy MVP event.

    R-005 / D-05 requires every event to share a small common envelope.  The
    repo still has older examples that use timestamp/name/details/status, so
    this validator accepts both shapes while reporting which schema matched.
    """
    if not isinstance(event, dict):
        return {"ok": False, "missing": TRACE_EVENT_ENVELOPE_FIELDS[:], "errors": ["event must be an object"], "schema": "unknown"}

    envelope_missing = _missing_fields(event, TRACE_EVENT_ENVELOPE_FIELDS)
    legacy_missing = _missing_fields(event, LEGACY_TRACE_EVENT_FIELDS)
    errors = []

    if not envelope_missing:
        if not isinstance(event.get("seq"), int) or isinstance(event.get("seq"), bool) or event.get("seq") < 1:
            errors.append("seq must be a positive integer")
        if event.get("status") not in TRACE_EVENT_STATUSES:
            errors.append(f"status must be one of {sorted(TRACE_EVENT_STATUSES)}")
        if "duration_ms" in event and (not isinstance(event["duration_ms"], (int, float)) or isinstance(event["duration_ms"], bool) or event["duration_ms"] < 0):
            errors.append("duration_ms must be a non-negative number")
        return {"ok": not errors, "missing": [], "errors": errors, "schema": "envelope"}

    if not legacy_missing:
        if event.get("status") not in LEGACY_OK_STATUSES:
            errors.append(f"legacy status must be one of {sorted(LEGACY_OK_STATUSES)}")
        if not isinstance(event.get("duration_ms"), (int, float)) or isinstance(event.get("duration_ms"), bool) or event.get("duration_ms") < 0:
            errors.append("duration_ms must be a non-negative number")
        return {"ok": not errors, "missing": [], "errors": errors, "schema": "legacy"}

    missing = envelope_missing if len(envelope_missing) <= len(legacy_missing) else legacy_missing
    return {"ok": False, "missing": missing, "errors": ["event does not match envelope or legacy trace shape"], "schema": "unknown"}


def summarize_trace(events):
    return {
        "event_count": len(events),
        "ok_events": sum(1 for event in events if validate_trace_event(event)["ok"]),
        "total_duration_ms": sum(event.get("duration_ms", 0) for event in events if isinstance(event, dict)),
    }


def build_run_summary(trace):
    """Build a compact R-007 summary from canonical event envelopes."""
    events = trace.get("events", [])
    event_counts = {}
    files_changed = []
    commands_run = []
    next_inspection_targets = []
    failure_reason = None

    for event in events:
        if not isinstance(event, dict):
            continue
        event_type = event.get("type", "unknown")
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        command_value = event.get("command", {}).get("value") if isinstance(event.get("command"), dict) else None
        if command_value:
            commands_run.append(command_value)
        file_path = event.get("file", {}).get("path") if isinstance(event.get("file"), dict) else None
        if file_path:
            files_changed.append(file_path)
        if event.get("status") == "failed":
            if event.get("stderr_preview"):
                failure_reason = failure_reason or event["stderr_preview"]
                next_inspection_targets.append(f"{event_type} {event.get('id', event.get('seq', '?'))} stderr_preview")
            elif event.get("error", {}).get("message") if isinstance(event.get("error"), dict) else None:
                failure_reason = failure_reason or event["error"]["message"]
                next_inspection_targets.append(f"{event_type} {event.get('id', event.get('seq', '?'))} error")

    run = trace.get("run", {}) if isinstance(trace.get("run"), dict) else {}
    result = run.get("status") or trace.get("result_summary", {}).get("status")
    return {
        "result": result,
        "failure_reason": failure_reason,
        "event_counts": event_counts,
        "files_changed": files_changed,
        "commands_run": commands_run,
        "next_inspection_targets": next_inspection_targets,
    }
