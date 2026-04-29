from src.trace_schema import build_run_summary, summarize_trace


def build_json_summary(trace):
    summary = summarize_trace(trace.get("events", []))
    run = trace.get("run", {})
    task = trace.get("task") or run.get("task")
    run_id = trace.get("run_id") or run.get("id")
    status = trace.get("result_summary", {}).get("status") or run.get("status")
    timing = trace.get("timing", {})
    if not timing and run.get("duration_ms") is not None:
        timing = {"wall_clock_ms": run.get("duration_ms")}

    return {
        "task": task,
        "run_id": run_id,
        "status": status,
        "timing": timing,
        "summary": summary,
        "run_summary": build_run_summary(trace),
    }
