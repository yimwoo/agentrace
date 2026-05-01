FAILURE_EVENT_STATUSES = {"failed", "error"}


def _event_label(event):
    return event.get("id") or event.get("name") or f"seq-{event.get('seq', 'unknown')}"


def _failure_reason(event):
    error = event.get("error")
    if isinstance(error, dict) and error.get("message"):
        return error["message"]
    return event.get("stderr_preview") or event.get("message") or "failure details unavailable"


def failure_events(trace):
    return [event for event in trace.get("events", []) if event.get("status") in FAILURE_EVENT_STATUSES or event.get("error")]


def build_failure_summary(trace):
    failures = failure_events(trace)
    return {"failure_count": len(failures), "primary_failure": _failure_reason(failures[0]) if failures else None, "inspection_targets": [f"{event.get('type', 'event')} {_event_label(event)}" for event in failures[:5]]}


def markdown_failure_section(trace):
    summary = build_failure_summary(trace)
    if summary["failure_count"] == 0:
        return "## Failures\n\nNo failed events recorded.\n"
    lines = ["## Failures", "", f"Primary failure: {summary['primary_failure']}", "", "Inspection targets:"]
    lines.extend(f"- {target}" for target in summary["inspection_targets"])
    return "\n".join(lines) + "\n"
