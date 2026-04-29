from src.trace_schema import build_run_summary, summarize_trace


def build_json_summary(trace):
    summary = summarize_trace(trace.get("events", []))
    return {
        "task": trace.get("task"),
        "run_id": trace.get("run_id"),
        "status": trace.get("result_summary", {}).get("status"),
        "timing": trace.get("timing", {}),
        "summary": summary,
        "run_summary": build_run_summary(trace),
    }
