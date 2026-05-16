from datetime import datetime, timedelta, timezone

from src.failure_summary import build_failure_summary
from src.trace_schema import build_run_summary, summarize_trace, event_duration_ms, event_duration_source, _parse_trace_timestamp


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


def _numeric_value(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return value


def _net_line_delta(row):
    return _numeric_value(row.get("added_lines")) - _numeric_value(row.get("removed_lines"))


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
            "duration_ms": event_duration_ms(event),
            "duration_source": event_duration_source(event),
            "exit_code": event.get("exit_code", details.get("exit_code")),
        }
        if event.get("started_at"):
            row["started_at"] = event["started_at"]
        if event.get("ended_at"):
            row["ended_at"] = event["ended_at"]
        if event.get("stdout_preview") or details.get("stdout_preview"):
            row["stdout_preview"] = event.get("stdout_preview") or details.get("stdout_preview")
        if event.get("stderr_preview") or details.get("stderr_preview"):
            row["stderr_preview"] = event.get("stderr_preview") or details.get("stderr_preview")
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
            "status": event.get("status"),
            "duration_ms": event_duration_ms(event),
            "duration_source": event_duration_source(event),
            "added_lines": change.get("added_lines", details.get("added_lines")),
            "removed_lines": change.get("removed_lines", details.get("removed_lines")),
            "summary": change.get("summary") or details.get("summary"),
        }
        row["net_line_delta"] = _net_line_delta(row)
        if event.get("started_at"):
            row["started_at"] = event["started_at"]
        if event.get("ended_at"):
            row["ended_at"] = event["ended_at"]
        error = event.get("error") if isinstance(event.get("error"), dict) else {}
        error_message = error.get("message") or details.get("error_message") or details.get("error")
        if error_message:
            row["error_message"] = error_message
        if event_ref in artifact_refs:
            row["artifacts"] = artifact_refs[event_ref]
        rows.append(row)
    return rows


def _normalized_timestamp(value):
    parsed = _parse_trace_timestamp(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _timestamp_extreme(rows, field, pick_max=False):
    candidates = []
    for row in rows:
        value = row.get(field)
        parsed = _normalized_timestamp(value)
        if parsed is not None:
            candidates.append((parsed, value))
    if not candidates:
        return None
    return max(candidates)[1] if pick_max else min(candidates)[1]


def _time_window(rows):
    started_at = _timestamp_extreme(rows, "started_at")
    ended_at = _timestamp_extreme(rows, "ended_at", pick_max=True)
    if started_at is None and ended_at is None:
        return None
    return {"started_at": started_at, "ended_at": ended_at}


def _duration_source_counts(rows):
    counts = {}
    for row in rows:
        source = row.get("duration_source") or "unknown"
        counts[source] = counts.get(source, 0) + 1
    return counts


def _duration_totals_by_type(rows):
    totals = {}
    for row in rows:
        row_type = row.get("type") or "unknown"
        totals[row_type] = totals.get(row_type, 0) + _numeric_value(row.get("duration_ms"))
    return totals


def _duration_shares_by_type(type_duration_ms, total_duration_ms):
    if not type_duration_ms:
        return {}
    if not total_duration_ms:
        return {row_type: 0 for row_type in type_duration_ms}
    return {
        row_type: round(duration_ms / total_duration_ms, 4)
        for row_type, duration_ms in type_duration_ms.items()
    }


def _dominant_duration_type(type_duration_ms, total_duration_ms):
    if not type_duration_ms:
        return None
    dominant_type = None
    dominant_duration = 0
    for row_type, duration_ms in type_duration_ms.items():
        if dominant_type is None or duration_ms > dominant_duration:
            dominant_type = row_type
            dominant_duration = duration_ms
    return {
        "type": dominant_type,
        "duration_ms": dominant_duration,
        "duration_share": 0 if not total_duration_ms else round(dominant_duration / total_duration_ms, 4),
    }


def _median_duration_ms(rows):
    durations = sorted(_numeric_value(row.get("duration_ms")) for row in rows or [] if isinstance(row, dict))
    if not durations:
        return 0
    middle = len(durations) // 2
    if len(durations) % 2:
        return durations[middle]
    return round((durations[middle - 1] + durations[middle]) / 2, 2)


def _timeline_sort_key(item):
    started_at = _normalized_timestamp(item.get("started_at"))
    ended_at = _normalized_timestamp(item.get("ended_at"))
    timestamp = started_at or ended_at
    # Keep rows with no timestamp after timestamped activity while preserving
    # their source order. This makes partial traces readable without hiding
    # summary-only command/edit rows that lack timing windows.
    return (timestamp is None, timestamp or datetime.max.replace(tzinfo=timezone.utc), item["_source_order"])


def build_activity_timeline(command_rows, edit_rows):
    """Build a compact, chronological command/edit activity timeline."""
    timeline = []
    source_order = 0
    for row in command_rows or []:
        if not isinstance(row, dict):
            continue
        item = {
            "type": "command",
            "event": row.get("event"),
            "status": row.get("status"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
            "started_at": row.get("started_at"),
            "ended_at": row.get("ended_at"),
            "command": row.get("command"),
            "cwd": row.get("cwd"),
            "exit_code": row.get("exit_code"),
            "_source_order": source_order,
        }
        if row.get("stdout_preview"):
            item["stdout_preview"] = row["stdout_preview"]
        if row.get("stderr_preview"):
            item["stderr_preview"] = row["stderr_preview"]
        if row.get("artifacts"):
            item["artifacts"] = row["artifacts"]
        timeline.append(item)
        source_order += 1

    for row in edit_rows or []:
        if not isinstance(row, dict):
            continue
        item = {
            "type": "file_edit",
            "event": row.get("event"),
            "status": row.get("status"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
            "started_at": row.get("started_at"),
            "ended_at": row.get("ended_at"),
            "path": row.get("path"),
            "kind": row.get("kind"),
            "added_lines": _numeric_value(row.get("added_lines")),
            "removed_lines": _numeric_value(row.get("removed_lines")),
            "net_line_delta": _net_line_delta(row),
            "summary": row.get("summary"),
            "_source_order": source_order,
        }
        if row.get("error_message"):
            item["error_message"] = row["error_message"]
        if row.get("artifacts"):
            item["artifacts"] = row["artifacts"]
        timeline.append(item)
        source_order += 1

    return [
        {key: value for key, value in item.items() if key != "_source_order"}
        for item in sorted(timeline, key=_timeline_sort_key)
    ]


def _is_failed_activity(row):
    row_type = row.get("type")
    status = row.get("status")
    return status in {"failed", "error"} or (row_type == "command" and _numeric_value(row.get("exit_code")) != 0)


def _activity_identity_row(row):
    activity_row = {
        "type": row.get("type"),
        "event": row.get("event"),
        "status": row.get("status"),
        "duration_ms": _numeric_value(row.get("duration_ms")),
        "duration_source": row.get("duration_source"),
        "started_at": row.get("started_at"),
        "ended_at": row.get("ended_at"),
    }
    if row.get("type") == "command":
        activity_row.update({
            "command": row.get("command"),
            "cwd": row.get("cwd"),
            "exit_code": row.get("exit_code"),
        })
        if row.get("stdout_preview"):
            activity_row["stdout_preview"] = row["stdout_preview"]
        if row.get("stderr_preview"):
            activity_row["stderr_preview"] = row["stderr_preview"]
    elif row.get("type") == "file_edit":
        activity_row.update({
            "path": row.get("path"),
            "kind": row.get("kind"),
            "added_lines": _numeric_value(row.get("added_lines")),
            "removed_lines": _numeric_value(row.get("removed_lines")),
            "net_line_delta": _net_line_delta(row),
        })
        if row.get("summary"):
            activity_row["summary"] = row["summary"]
        if row.get("error_message"):
            activity_row["error_message"] = row["error_message"]
    if row.get("artifacts"):
        activity_row["artifacts"] = row["artifacts"]
    return activity_row


def _failed_activity_rows(rows):
    failed = []
    for row in rows:
        if not _is_failed_activity(row):
            continue
        failed.append(_activity_identity_row(row))
    return failed


def _first_activity_row(rows):
    if not rows:
        return None
    return _activity_identity_row(rows[0])


def _slowest_activity_row(rows):
    slowest = None
    for row in rows:
        if slowest is None or _numeric_value(row.get("duration_ms")) > _numeric_value(slowest.get("duration_ms")):
            slowest = row
    return _activity_identity_row(slowest) if slowest is not None else None


def _fastest_activity_row(rows):
    fastest = None
    for row in rows:
        if fastest is None or _numeric_value(row.get("duration_ms")) < _numeric_value(fastest.get("duration_ms")):
            fastest = row
    return _activity_identity_row(fastest) if fastest is not None else None


def _last_activity_row(rows):
    if not rows:
        return None
    return _activity_identity_row(rows[-1])


def _duration_between_ms(start_value, end_value):
    start = _normalized_timestamp(start_value)
    end = _normalized_timestamp(end_value)
    if start is None or end is None:
        return None
    return max(0, round((end - start).total_seconds() * 1000))


def _time_window_span_ms(time_window):
    if not time_window:
        return 0
    return _duration_between_ms(time_window.get("started_at"), time_window.get("ended_at")) or 0


def _activity_interval(row):
    start = _normalized_timestamp(row.get("started_at"))
    end = _normalized_timestamp(row.get("ended_at"))
    duration = _numeric_value(row.get("duration_ms"))
    if start is None and end is None:
        return None
    if start is None and end is not None and duration:
        start = end - timedelta(milliseconds=duration)
    if end is None and start is not None and duration:
        end = start + timedelta(milliseconds=duration)
    if start is None or end is None or end < start:
        return None
    return start, end


def _timestamp_label(value):
    if value is None:
        return None
    text = value.astimezone(timezone.utc).isoformat()
    if text.endswith("+00:00"):
        text = text[:-6] + "Z"
    if "." in text:
        prefix, suffix = text.split(".", 1)
        fraction = suffix[:-1] if suffix.endswith("Z") else suffix
        fraction = fraction.rstrip("0")
        text = f"{prefix}.{fraction}Z" if fraction else f"{prefix}Z"
    return text


def _uncovered_activity_intervals(time_window, merged_intervals):
    if not time_window or not merged_intervals:
        return []
    window_start = _normalized_timestamp(time_window.get("started_at"))
    window_end = _normalized_timestamp(time_window.get("ended_at"))
    if window_start is None or window_end is None or window_end <= window_start:
        return []

    gaps = []
    cursor = window_start
    for start, end in merged_intervals:
        if end <= window_start or start >= window_end:
            continue
        clipped_start = max(start, window_start)
        clipped_end = min(end, window_end)
        if clipped_start > cursor:
            gaps.append({
                "started_at": _timestamp_label(cursor),
                "ended_at": _timestamp_label(clipped_start),
                "duration_ms": round((clipped_start - cursor).total_seconds() * 1000),
            })
        if clipped_end > cursor:
            cursor = clipped_end
    if cursor < window_end:
        gaps.append({
            "started_at": _timestamp_label(cursor),
            "ended_at": _timestamp_label(window_end),
            "duration_ms": round((window_end - cursor).total_seconds() * 1000),
        })
    return gaps


def _activity_coverage(rows, time_window=None):
    intervals = []
    for row in rows:
        interval = _activity_interval(row)
        if interval is not None:
            intervals.append(interval)
    if not intervals:
        return {"covered_duration_ms": 0, "covered_interval_count": 0, "uncovered_intervals": []}

    merged = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
            continue
        if end > merged[-1][1]:
            merged[-1][1] = end

    covered_duration_ms = sum(round((end - start).total_seconds() * 1000) for start, end in merged)
    return {
        "covered_duration_ms": covered_duration_ms,
        "covered_interval_count": len(intervals),
        "uncovered_intervals": _uncovered_activity_intervals(time_window, merged),
    }


def _activity_gap_rows(rows):
    gaps = []
    for previous, current in zip(rows, rows[1:]):
        previous_boundary = previous.get("ended_at") or previous.get("started_at")
        current_boundary = current.get("started_at") or current.get("ended_at")
        gap_ms = _duration_between_ms(previous_boundary, current_boundary)
        if gap_ms is None:
            continue
        gaps.append({
            "from_event": previous.get("event"),
            "to_event": current.get("event"),
            "gap_ms": gap_ms,
            "from_ended_at": previous.get("ended_at"),
            "to_started_at": current.get("started_at"),
        })
    return gaps


def _activity_overlap_rows(rows):
    overlaps = []
    for previous, current in zip(rows, rows[1:]):
        previous_end = previous.get("ended_at")
        current_start = current.get("started_at")
        previous_end_at = _normalized_timestamp(previous_end)
        current_start_at = _normalized_timestamp(current_start)
        if previous_end_at is None or current_start_at is None or current_start_at >= previous_end_at:
            continue
        overlaps.append({
            "from_event": previous.get("event"),
            "to_event": current.get("event"),
            "overlap_ms": round((previous_end_at - current_start_at).total_seconds() * 1000),
            "from_ended_at": previous_end,
            "to_started_at": current_start,
        })
    return overlaps


def build_activity_timeline_summary(rows):
    """Build aggregate metrics for the combined command/edit activity timeline."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    status_counts = {}
    type_counts = {}
    failed_count = 0
    for row in normalized_rows:
        row_type = row.get("type") or "unknown"
        type_counts[row_type] = type_counts.get(row_type, 0) + 1
        status = row.get("status") or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        if _is_failed_activity(row):
            failed_count += 1
    total_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in normalized_rows)
    failed_activity = _failed_activity_rows(normalized_rows)
    inter_activity_gaps = _activity_gap_rows(normalized_rows)
    total_idle_gap_ms = sum(gap.get("gap_ms", 0) for gap in inter_activity_gaps)
    largest_idle_gap = None
    for gap in inter_activity_gaps:
        if largest_idle_gap is None or gap.get("gap_ms", 0) > largest_idle_gap.get("gap_ms", 0):
            largest_idle_gap = gap
    inter_activity_overlaps = _activity_overlap_rows(normalized_rows)
    total_overlap_ms = sum(overlap.get("overlap_ms", 0) for overlap in inter_activity_overlaps)
    largest_overlap = None
    for overlap in inter_activity_overlaps:
        if largest_overlap is None or overlap.get("overlap_ms", 0) > largest_overlap.get("overlap_ms", 0):
            largest_overlap = overlap
    time_window = _time_window(normalized_rows)
    span_duration_ms = _time_window_span_ms(time_window)
    coverage = _activity_coverage(normalized_rows, time_window)
    uncovered_intervals = coverage["uncovered_intervals"]
    uncovered_duration_ms = max(0, span_duration_ms - coverage["covered_duration_ms"])
    largest_uncovered_interval = None
    for interval in uncovered_intervals:
        if largest_uncovered_interval is None or interval.get("duration_ms", 0) > largest_uncovered_interval.get("duration_ms", 0):
            largest_uncovered_interval = interval
    coverage_ratio = 0 if not span_duration_ms else round(min(coverage["covered_duration_ms"], span_duration_ms) / span_duration_ms, 4)
    idle_ratio = 0 if not span_duration_ms else round(uncovered_duration_ms / span_duration_ms, 4)
    type_duration_ms = _duration_totals_by_type(normalized_rows)
    return {
        "count": len(normalized_rows),
        "type_counts": type_counts,
        "type_duration_ms": type_duration_ms,
        "type_duration_share": _duration_shares_by_type(type_duration_ms, total_duration_ms),
        "dominant_duration_type": _dominant_duration_type(type_duration_ms, total_duration_ms),
        "status_counts": status_counts,
        "duration_source_counts": _duration_source_counts(normalized_rows),
        "time_window": time_window,
        "span_duration_ms": span_duration_ms,
        "covered_duration_ms": coverage["covered_duration_ms"],
        "uncovered_duration_ms": uncovered_duration_ms,
        "uncovered_intervals": uncovered_intervals,
        "uncovered_interval_count": len(uncovered_intervals),
        "average_uncovered_interval_ms": 0 if not uncovered_intervals else round(uncovered_duration_ms / len(uncovered_intervals), 2),
        "largest_uncovered_interval": largest_uncovered_interval,
        "coverage_ratio": coverage_ratio,
        "idle_ratio": idle_ratio,
        "covered_interval_count": coverage["covered_interval_count"],
        "total_duration_ms": total_duration_ms,
        "average_duration_ms": 0 if not normalized_rows else round(total_duration_ms / len(normalized_rows), 2),
        "median_duration_ms": _median_duration_ms(normalized_rows),
        "first_activity": _first_activity_row(normalized_rows),
        "slowest_activity": _slowest_activity_row(normalized_rows),
        "fastest_activity": _fastest_activity_row(normalized_rows),
        "last_activity": _last_activity_row(normalized_rows),
        "inter_activity_gaps": inter_activity_gaps,
        "total_idle_gap_ms": total_idle_gap_ms,
        "average_idle_gap_ms": 0 if not inter_activity_gaps else round(total_idle_gap_ms / len(inter_activity_gaps), 2),
        "largest_idle_gap": largest_idle_gap,
        "inter_activity_overlaps": inter_activity_overlaps,
        "total_overlap_ms": total_overlap_ms,
        "average_overlap_ms": 0 if not inter_activity_overlaps else round(total_overlap_ms / len(inter_activity_overlaps), 2),
        "overlap_ratio": 0 if not span_duration_ms else round(total_overlap_ms / span_duration_ms, 4),
        "largest_overlap": largest_overlap,
        "failed_count": failed_count,
        "first_failed_activity": failed_activity[0] if failed_activity else None,
        "failed_activity": failed_activity,
    }


def _ordered_values(rows, field):
    values = []
    seen = set()
    for row in rows:
        value = row.get(field)
        if not value or value in seen:
            continue
        seen.add(value)
        values.append(value)
    return values


def _value_counts(rows, field, missing_label=None):
    counts = {}
    for row in rows:
        value = row.get(field)
        if not value and missing_label is None:
            continue
        if not value:
            value = missing_label
        counts[value] = counts.get(value, 0) + 1
    return counts


def _exit_code_counts(rows):
    counts = {}
    for row in rows:
        exit_code = row.get("exit_code")
        label = "unknown" if exit_code is None else str(exit_code)
        counts[label] = counts.get(label, 0) + 1
    return counts


def _repeated_value_counts(rows, field):
    return {value: count for value, count in _value_counts(rows, field).items() if count > 1}


def _command_attempt_rows(rows):
    attempts_by_command = {}
    for row in rows:
        command = row.get("command") or "<unknown command>"
        if command not in attempts_by_command:
            attempts_by_command[command] = {
                "command": command,
                "count": 0,
                "total_duration_ms": 0,
                "average_duration_ms": 0,
                "failed_count": 0,
                "status_counts": {},
                "duration_source_counts": {},
                "time_window": None,
                "first_event": row.get("event"),
                "last_event": row.get("event"),
                "artifacts": [],
                "_rows": [],
            }
        summary = attempts_by_command[command]
        summary["count"] += 1
        summary["total_duration_ms"] += _numeric_value(row.get("duration_ms"))
        if _is_failed_command(row):
            summary["failed_count"] += 1
        status = row.get("status") or "unknown"
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
        source = row.get("duration_source") or "unknown"
        summary["duration_source_counts"][source] = summary["duration_source_counts"].get(source, 0) + 1
        summary["last_event"] = row.get("event")
        if row.get("artifacts"):
            summary["artifacts"].extend(row["artifacts"])
        summary["_rows"].append(row)

    summaries = []
    for summary in attempts_by_command.values():
        summary["average_duration_ms"] = round(summary["total_duration_ms"] / summary["count"], 2)
        summary["time_window"] = _time_window(summary.pop("_rows"))
        if not summary["artifacts"]:
            summary.pop("artifacts")
        summaries.append(summary)
    return summaries


def _command_cwd_total_rows(rows):
    totals_by_cwd = {}
    for row in rows:
        cwd = row.get("cwd") or "unknown"
        if cwd not in totals_by_cwd:
            totals_by_cwd[cwd] = {
                "cwd": cwd,
                "count": 0,
                "commands_run": [],
                "failed_count": 0,
                "total_duration_ms": 0,
                "average_duration_ms": 0,
                "status_counts": {},
                "duration_source_counts": {},
                "time_window": None,
                "first_event": row.get("event"),
                "last_event": row.get("event"),
                "artifacts": [],
                "_rows": [],
            }
        summary = totals_by_cwd[cwd]
        summary["count"] += 1
        command = row.get("command")
        if command and command not in summary["commands_run"]:
            summary["commands_run"].append(command)
        if _is_failed_command(row):
            summary["failed_count"] += 1
        summary["total_duration_ms"] += _numeric_value(row.get("duration_ms"))
        status = row.get("status") or "unknown"
        source = row.get("duration_source") or "unknown"
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
        summary["duration_source_counts"][source] = summary["duration_source_counts"].get(source, 0) + 1
        summary["last_event"] = row.get("event")
        if row.get("artifacts"):
            summary["artifacts"].extend(row["artifacts"])
        summary["_rows"].append(row)

    summaries = []
    for summary in totals_by_cwd.values():
        summary["average_duration_ms"] = round(summary["total_duration_ms"] / summary["count"], 2)
        summary["time_window"] = _time_window(summary.pop("_rows"))
        if summary["count"] <= 1:
            summary.pop("first_event")
            summary.pop("last_event")
        if not summary["artifacts"]:
            summary.pop("artifacts")
        summaries.append(summary)
    return summaries


def _is_failed_command(row):
    return row.get("status") in {"failed", "error"} or _numeric_value(row.get("exit_code")) != 0


def _failed_command_rows(rows):
    failed = []
    for row in rows:
        if not _is_failed_command(row):
            continue
        failed_row = {
            "event": row.get("event"),
            "command": row.get("command"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
            "status": row.get("status"),
            "exit_code": row.get("exit_code"),
            "started_at": row.get("started_at"),
            "ended_at": row.get("ended_at"),
        }
        if row.get("stdout_preview"):
            failed_row["stdout_preview"] = row["stdout_preview"]
        if row.get("stderr_preview"):
            failed_row["stderr_preview"] = row["stderr_preview"]
        if row.get("artifacts"):
            failed_row["artifacts"] = row["artifacts"]
        failed.append(failed_row)
    return failed


def _command_identity_row(row):
    if row is None:
        return None
    summary = {
        "event": row.get("event"),
        "command": row.get("command"),
        "duration_ms": _numeric_value(row.get("duration_ms")),
        "duration_source": row.get("duration_source"),
        "status": row.get("status"),
        "exit_code": row.get("exit_code"),
        "started_at": row.get("started_at"),
        "ended_at": row.get("ended_at"),
    }
    if row.get("artifacts"):
        summary["artifacts"] = row["artifacts"]
    return summary


def _slowest_command_row(row):
    return _command_identity_row(row)


def _first_command_row(rows):
    return _command_identity_row(rows[0]) if rows else None


def _fastest_command_row(rows):
    fastest = None
    for row in rows:
        if fastest is None or _numeric_value(row.get("duration_ms")) < _numeric_value(fastest.get("duration_ms")):
            fastest = row
    return _command_identity_row(fastest)


def _last_command_row(rows):
    return _command_identity_row(rows[-1]) if rows else None


def build_command_timing_summary(rows):
    """Build aggregate command timing metrics for quick report inspection."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    slowest = None
    status_counts = {}
    for row in normalized_rows:
        if slowest is None or _numeric_value(row.get("duration_ms")) > _numeric_value(slowest.get("duration_ms")):
            slowest = row
        status = row.get("status") or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    total_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in normalized_rows)
    commands_run = _ordered_values(normalized_rows, "command")
    return {
        "count": len(normalized_rows),
        "unique_command_count": len(commands_run),
        "commands_run": commands_run,
        "repeated_commands": _repeated_value_counts(normalized_rows, "command"),
        "command_attempts": _command_attempt_rows(normalized_rows),
        "cwd_counts": _value_counts(normalized_rows, "cwd", missing_label="unknown"),
        "cwd_totals": _command_cwd_total_rows(normalized_rows),
        "total_duration_ms": total_duration_ms,
        "average_duration_ms": 0 if not normalized_rows else round(total_duration_ms / len(normalized_rows), 2),
        "median_duration_ms": _median_duration_ms(normalized_rows),
        "failed_count": sum(1 for row in normalized_rows if _is_failed_command(row)),
        "failed_commands": _failed_command_rows(normalized_rows),
        "exit_code_counts": _exit_code_counts(normalized_rows),
        "status_counts": status_counts,
        "duration_source_counts": _duration_source_counts(normalized_rows),
        "time_window": _time_window(normalized_rows),
        "first": _first_command_row(normalized_rows),
        "slowest": _slowest_command_row(slowest),
        "fastest": _fastest_command_row(normalized_rows),
        "last": _last_command_row(normalized_rows),
    }


def _largest_edit_row(rows):
    largest = None
    for row in rows:
        if largest is None:
            largest = row
            continue
        row_churn = _numeric_value(row.get("added_lines")) + _numeric_value(row.get("removed_lines"))
        largest_churn = _numeric_value(largest.get("added_lines")) + _numeric_value(largest.get("removed_lines"))
        if row_churn > largest_churn:
            largest = row
    return largest


def _shortest_edit_row(rows):
    shortest = None
    for row in rows:
        if shortest is None or _numeric_value(row.get("duration_ms")) < _numeric_value(shortest.get("duration_ms")):
            shortest = row
    return shortest


def _first_edit_row(rows):
    return rows[0] if rows else None


def _last_edit_row(rows):
    return rows[-1] if rows else None


def _largest_edit_summary_row(row):
    if row is None:
        return None
    summary = {
        "event": row.get("event"),
        "path": row.get("path"),
        "kind": row.get("kind"),
        "added_lines": _numeric_value(row.get("added_lines")),
        "removed_lines": _numeric_value(row.get("removed_lines")),
        "net_line_delta": _net_line_delta(row),
        "duration_ms": _numeric_value(row.get("duration_ms")),
        "duration_source": row.get("duration_source"),
        "status": row.get("status"),
        "started_at": row.get("started_at"),
        "ended_at": row.get("ended_at"),
    }
    if row.get("artifacts"):
        summary["artifacts"] = row["artifacts"]
    return summary


def _is_failed_edit(row):
    return row.get("status") in {"failed", "error"}


def _failed_edit_rows(rows):
    failed = []
    for row in rows:
        if not _is_failed_edit(row):
            continue
        failed_row = {
            "event": row.get("event"),
            "path": row.get("path"),
            "kind": row.get("kind"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
            "status": row.get("status"),
            "started_at": row.get("started_at"),
            "ended_at": row.get("ended_at"),
            "added_lines": _numeric_value(row.get("added_lines")),
            "removed_lines": _numeric_value(row.get("removed_lines")),
            "net_line_delta": _net_line_delta(row),
        }
        if row.get("summary"):
            failed_row["summary"] = row["summary"]
        if row.get("error_message"):
            failed_row["error_message"] = row["error_message"]
        if row.get("artifacts"):
            failed_row["artifacts"] = row["artifacts"]
        failed.append(failed_row)
    return failed


def _file_change_total_rows(rows):
    totals_by_file = {}
    for row in rows:
        path = row.get("path") or "<unknown file>"
        if path not in totals_by_file:
            totals_by_file[path] = {
                "path": path,
                "count": 0,
                "failed_count": 0,
                "total_added_lines": 0,
                "total_removed_lines": 0,
                "net_line_delta": 0,
                "total_duration_ms": 0,
                "average_duration_ms": 0,
                "status_counts": {},
                "kind_counts": {},
                "duration_source_counts": {},
                "time_window": None,
                "first_event": row.get("event"),
                "last_event": row.get("event"),
                "artifacts": [],
                "_rows": [],
            }
        summary = totals_by_file[path]
        added = _numeric_value(row.get("added_lines"))
        removed = _numeric_value(row.get("removed_lines"))
        summary["count"] += 1
        if _is_failed_edit(row):
            summary["failed_count"] += 1
        summary["total_added_lines"] += added
        summary["total_removed_lines"] += removed
        summary["net_line_delta"] += added - removed
        summary["total_duration_ms"] += _numeric_value(row.get("duration_ms"))
        status = row.get("status") or "unknown"
        kind = row.get("kind") or "unknown"
        source = row.get("duration_source") or "unknown"
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
        summary["kind_counts"][kind] = summary["kind_counts"].get(kind, 0) + 1
        summary["duration_source_counts"][source] = summary["duration_source_counts"].get(source, 0) + 1
        summary["last_event"] = row.get("event")
        if row.get("artifacts"):
            summary["artifacts"].extend(row["artifacts"])
        summary["_rows"].append(row)

    summaries = []
    for summary in totals_by_file.values():
        summary["average_duration_ms"] = round(summary["total_duration_ms"] / summary["count"], 2)
        summary["time_window"] = _time_window(summary.pop("_rows"))
        if summary["count"] <= 1:
            summary.pop("first_event")
            summary.pop("last_event")
        if not summary["artifacts"]:
            summary.pop("artifacts")
        summaries.append(summary)
    return summaries


def _edit_kind_total_rows(rows):
    totals_by_kind = {}
    for row in rows:
        kind = row.get("kind") or "unknown"
        if kind not in totals_by_kind:
            totals_by_kind[kind] = {
                "kind": kind,
                "count": 0,
                "files_changed": [],
                "failed_count": 0,
                "total_added_lines": 0,
                "total_removed_lines": 0,
                "net_line_delta": 0,
                "total_duration_ms": 0,
                "average_duration_ms": 0,
                "status_counts": {},
                "duration_source_counts": {},
                "time_window": None,
                "first_event": row.get("event"),
                "last_event": row.get("event"),
                "artifacts": [],
                "_rows": [],
            }
        summary = totals_by_kind[kind]
        added = _numeric_value(row.get("added_lines"))
        removed = _numeric_value(row.get("removed_lines"))
        summary["count"] += 1
        path = row.get("path")
        if path and path not in summary["files_changed"]:
            summary["files_changed"].append(path)
        if _is_failed_edit(row):
            summary["failed_count"] += 1
        summary["total_added_lines"] += added
        summary["total_removed_lines"] += removed
        summary["net_line_delta"] += added - removed
        summary["total_duration_ms"] += _numeric_value(row.get("duration_ms"))
        status = row.get("status") or "unknown"
        source = row.get("duration_source") or "unknown"
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
        summary["duration_source_counts"][source] = summary["duration_source_counts"].get(source, 0) + 1
        summary["last_event"] = row.get("event")
        if row.get("artifacts"):
            summary["artifacts"].extend(row["artifacts"])
        summary["_rows"].append(row)

    summaries = []
    for summary in totals_by_kind.values():
        summary["average_duration_ms"] = round(summary["total_duration_ms"] / summary["count"], 2)
        summary["time_window"] = _time_window(summary.pop("_rows"))
        if summary["count"] <= 1:
            summary.pop("first_event")
            summary.pop("last_event")
        if not summary["artifacts"]:
            summary.pop("artifacts")
        summaries.append(summary)
    return summaries


def build_edit_summary_totals(rows):
    """Build aggregate edit impact metrics for quick report inspection."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    files = _ordered_values(normalized_rows, "path")
    status_counts = {}
    for row in normalized_rows:
        status = row.get("status") or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    total_added_lines = sum(_numeric_value(row.get("added_lines")) for row in normalized_rows)
    total_removed_lines = sum(_numeric_value(row.get("removed_lines")) for row in normalized_rows)
    total_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in normalized_rows)
    largest_edit = _largest_edit_row(normalized_rows)
    shortest_edit = _shortest_edit_row(normalized_rows)
    return {
        "count": len(normalized_rows),
        "files_changed": files,
        "files_changed_count": len(files),
        "file_change_totals": _file_change_total_rows(normalized_rows),
        "failed_count": sum(1 for row in normalized_rows if _is_failed_edit(row)),
        "failed_edits": _failed_edit_rows(normalized_rows),
        "kind_counts": _value_counts(normalized_rows, "kind", missing_label="unknown"),
        "kind_totals": _edit_kind_total_rows(normalized_rows),
        "status_counts": status_counts,
        "duration_source_counts": _duration_source_counts(normalized_rows),
        "time_window": _time_window(normalized_rows),
        "total_added_lines": total_added_lines,
        "total_removed_lines": total_removed_lines,
        "net_line_delta": total_added_lines - total_removed_lines,
        "total_duration_ms": total_duration_ms,
        "average_duration_ms": 0 if not normalized_rows else round(total_duration_ms / len(normalized_rows), 2),
        "median_duration_ms": _median_duration_ms(normalized_rows),
        "first_edit": _largest_edit_summary_row(_first_edit_row(normalized_rows)),
        "largest_edit": _largest_edit_summary_row(largest_edit),
        "shortest_edit": _largest_edit_summary_row(shortest_edit),
        "last_edit": _largest_edit_summary_row(_last_edit_row(normalized_rows)),
    }



def _normalize_summary_command_rows(rows):
    normalized = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        normalized_row = dict(row)
        normalized_row.setdefault("event", "summary")
        normalized_row.setdefault("command", None)
        normalized_row.setdefault("status", None)
        normalized_row.setdefault("exit_code", None)
        if not normalized_row.get("duration_source"):
            normalized_row["duration_source"] = event_duration_source(normalized_row)
        if normalized_row.get("duration_ms") is None:
            normalized_row["duration_ms"] = event_duration_ms(normalized_row)
        normalized.append(normalized_row)
    return normalized


def _normalize_summary_edit_rows(rows):
    normalized = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        normalized_row = dict(row)
        normalized_row.setdefault("event", "summary")
        normalized_row.setdefault("path", None)
        normalized_row.setdefault("kind", None)
        normalized_row.setdefault("status", None)
        normalized_row.setdefault("added_lines", 0)
        normalized_row.setdefault("removed_lines", 0)
        normalized_row.setdefault("summary", None)
        if not normalized_row.get("duration_source"):
            normalized_row["duration_source"] = event_duration_source(normalized_row)
        if normalized_row.get("duration_ms") is None:
            normalized_row["duration_ms"] = event_duration_ms(normalized_row)
        if "net_line_delta" not in normalized_row:
            normalized_row["net_line_delta"] = _net_line_delta(normalized_row)
        normalized.append(normalized_row)
    return normalized


def build_json_summary(trace):
    events = trace.get("events", [])
    summary = summarize_trace(events)
    metadata = _run_metadata(trace)
    run_summary = trace.get("summary") or build_run_summary(trace)
    command_timing = build_command_timing(events, trace.get("artifacts", [])) or _normalize_summary_command_rows(run_summary.get("command_durations_ms", []))
    edit_summary = build_edit_summary(events, trace.get("artifacts", [])) or _normalize_summary_edit_rows(run_summary.get("edit_summaries", []))
    activity_timeline = build_activity_timeline(command_timing, edit_summary)
    return {
        "task": metadata["task"],
        "run_id": metadata["run_id"],
        "status": metadata["status"],
        "timing": metadata["timing"],
        "summary": summary,
        "run_summary": run_summary,
        "failure_summary": build_failure_summary(trace),
        "command_timing_summary": build_command_timing_summary(command_timing),
        "activity_timeline_summary": build_activity_timeline_summary(activity_timeline),
        "activity_timeline": activity_timeline,
        "command_timing": command_timing,
        "edit_summary_totals": build_edit_summary_totals(edit_summary),
        "edit_summary": edit_summary,
    }
