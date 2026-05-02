from datetime import datetime, timezone


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


def _parse_trace_timestamp(value):
    if not isinstance(value, str) or not value:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def event_duration_ms(event):
    duration = event.get("duration_ms")
    if duration is not None:
        return duration
    started_at = _parse_trace_timestamp(event.get("started_at"))
    ended_at = _parse_trace_timestamp(event.get("ended_at"))
    if not started_at or not ended_at:
        return 0
    if started_at.tzinfo is None and ended_at.tzinfo is not None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    if ended_at.tzinfo is None and started_at.tzinfo is not None:
        ended_at = ended_at.replace(tzinfo=timezone.utc)
    elapsed_ms = int((ended_at - started_at).total_seconds() * 1000)
    return elapsed_ms if elapsed_ms >= 0 else 0


def summarize_trace(events):
    return {
        "event_count": len(events),
        "ok_events": sum(1 for event in events if validate_trace_event(event)["ok"]),
        "total_duration_ms": sum(event_duration_ms(event) for event in events if isinstance(event, dict)),
    }


def _event_ref(event):
    return event.get("id") or event.get("seq") or event.get("name")


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


def _copy_present(row, source, fields):
    for field in fields:
        if source.get(field) is not None:
            row[field] = source[field]


def build_run_summary(trace):
    """Build a compact R-007 summary from canonical event envelopes."""
    events = trace.get("events", [])
    artifact_refs = _artifact_refs_by_event(trace.get("artifacts", []))
    event_counts = {}
    files_changed = []
    commands_run = []
    command_durations_ms = []
    edit_summaries = []
    next_inspection_targets = []
    failure_reason = None

    for event in events:
        if not isinstance(event, dict):
            continue
        event_type = event.get("type", "unknown")
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        event_ref = _event_ref(event)
        command = event.get("command") if isinstance(event.get("command"), dict) else {}
        details = event.get("details") if isinstance(event.get("details"), dict) else {}
        command_value = command.get("value") or details.get("command") if event_type == "command" else None
        if command_value:
            commands_run.append(command_value)
            row = {
                "event": event_ref,
                "command": command_value,
                "duration_ms": event_duration_ms(event),
                "status": event.get("status"),
                "exit_code": event.get("exit_code", details.get("exit_code")),
            }
            if command.get("cwd") or details.get("cwd"):
                row["cwd"] = command.get("cwd") or details.get("cwd")
            _copy_present(row, event, ["started_at", "ended_at"])
            if event_ref in artifact_refs:
                row["artifacts"] = artifact_refs[event_ref]
            command_durations_ms.append(row)
        file_info = event.get("file") if isinstance(event.get("file"), dict) else {}
        file_path = file_info.get("path") or details.get("path") if event_type == "file_edit" else None
        if file_path:
            files_changed.append(file_path)
            change = event.get("change") if isinstance(event.get("change"), dict) else {}
            row = {
                "event": event_ref,
                "path": file_path,
                "kind": change.get("kind") or details.get("kind"),
                "status": event.get("status"),
                "duration_ms": event_duration_ms(event),
                "added_lines": change.get("added_lines", details.get("added_lines")),
                "removed_lines": change.get("removed_lines", details.get("removed_lines")),
                "summary": change.get("summary") or details.get("summary"),
            }
            _copy_present(row, event, ["started_at", "ended_at"])
            if event_ref in artifact_refs:
                row["artifacts"] = artifact_refs[event_ref]
            edit_summaries.append(row)
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
        "command_durations_ms": command_durations_ms,
        "edit_summaries": edit_summaries,
        "next_inspection_targets": next_inspection_targets,
    }
