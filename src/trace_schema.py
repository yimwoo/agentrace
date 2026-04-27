TRACE_EVENT_FIELDS = [
    "timestamp",
    "type",
    "name",
    "status",
    "details",
    "duration_ms",
]


def validate_trace_event(event):
    missing = [field for field in TRACE_EVENT_FIELDS if field not in event]
    return {"ok": not missing, "missing": missing}
