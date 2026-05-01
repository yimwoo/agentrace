from src.failure_summary import build_failure_summary
from src.trace_schema import build_run_summary, summarize_trace


def _run_metadata(trace):
    run = trace.get("run", {}) if isinstance(trace.get("run"), dict) else {}
    return {
        "task": run.get("task") or trace.get("task"),
        "run_id": run.get("id") or trace.get("run_id"),
        "status": run.get("status") or trace.get("result_summary", {}).get("status"),
        "timing": {"wall_clock_ms": run.get("duration_ms")} if "duration_ms" in run else trace.get("timing", {}),
    }


def build_json_summary(trace):
    summary = summarize_trace(trace.get("events", []))
    metadata = _run_metadata(trace)
    return {
        "task": metadata["task"],
        "run_id": metadata["run_id"],
        "status": metadata["status"],
        "timing": metadata["timing"],
        "summary": summary,
        "run_summary": trace.get("summary") or build_run_summary(trace),
        "failure_summary": build_failure_summary(trace),
    }
