TRACE_EVENT_FIELDS = [
    "timestamp", "type", "name", "status", "details", "duration_ms"
]


def validate_trace_event(event):
    missing = [field for field in TRACE_EVENT_FIELDS if field not in event]
    return {"ok": not missing, "missing": missing}


def summarize_trace(events):
    return {
        "event_count": len(events),
        "ok_events": sum(1 for event in events if validate_trace_event(event)["ok"]),
        "total_duration_ms": sum(event.get("duration_ms", 0) for event in events),
    }
