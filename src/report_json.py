from src.failure_summary import build_failure_summary
from src.trace_schema import build_run_summary, summarize_trace


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
            "duration_ms": event.get("duration_ms", 0),
            "exit_code": event.get("exit_code", details.get("exit_code")),
        }
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
            "added_lines": change.get("added_lines", details.get("added_lines")),
            "removed_lines": change.get("removed_lines", details.get("removed_lines")),
            "summary": change.get("summary") or details.get("summary"),
        }
        if event_ref in artifact_refs:
            row["artifacts"] = artifact_refs[event_ref]
        rows.append(row)
    return rows


def build_json_summary(trace):
    events = trace.get("events", [])
    summary = summarize_trace(events)
    metadata = _run_metadata(trace)
    return {
        "task": metadata["task"],
        "run_id": metadata["run_id"],
        "status": metadata["status"],
        "timing": metadata["timing"],
        "summary": summary,
        "run_summary": trace.get("summary") or build_run_summary(trace),
        "failure_summary": build_failure_summary(trace),
        "command_timing": build_command_timing(events, trace.get("artifacts", [])),
        "edit_summary": build_edit_summary(events, trace.get("artifacts", [])),
    }
