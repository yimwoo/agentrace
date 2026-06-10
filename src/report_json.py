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


def _compact_artifact_ref(artifact):
    if not isinstance(artifact, dict) or not artifact.get("path"):
        return None
    return {
        "kind": artifact.get("kind", "artifact"),
        "path": artifact["path"],
    }


def _artifact_refs_for_event(event, artifact_refs):
    """Return normalized artifact refs linked either inline or by top-level event_id."""
    refs = []
    seen = set()
    event_ref = _event_ref(event)
    for artifact in artifact_refs.get(event_ref, []):
        key = (artifact.get("kind"), artifact.get("path"))
        if key not in seen:
            refs.append(artifact)
            seen.add(key)
    for artifact in event.get("artifacts", []) if isinstance(event, dict) else []:
        compact = _compact_artifact_ref(artifact)
        if not compact:
            continue
        key = (compact.get("kind"), compact.get("path"))
        if key not in seen:
            refs.append(compact)
            seen.add(key)
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
        command_summary = command.get("summary") or details.get("summary") or event.get("summary")
        if command_summary:
            row["summary"] = command_summary
            if event.get("summary") and not command.get("summary") and not details.get("summary"):
                row["summary_source"] = "event.summary"
        if event.get("started_at"):
            row["started_at"] = event["started_at"]
        if event.get("ended_at"):
            row["ended_at"] = event["ended_at"]
        if event.get("stdout_preview") or details.get("stdout_preview"):
            row["stdout_preview"] = event.get("stdout_preview") or details.get("stdout_preview")
        if event.get("stderr_preview") or details.get("stderr_preview"):
            row["stderr_preview"] = event.get("stderr_preview") or details.get("stderr_preview")
        event_artifacts = _artifact_refs_for_event(event, artifact_refs)
        if event_artifacts:
            row["artifacts"] = event_artifacts
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
            "summary": change.get("summary") or details.get("summary") or event.get("summary"),
        }
        if row.get("summary") and event.get("summary") and not change.get("summary") and not details.get("summary"):
            row["summary_source"] = "event.summary"
        row["net_line_delta"] = _net_line_delta(row)
        if event.get("started_at"):
            row["started_at"] = event["started_at"]
        if event.get("ended_at"):
            row["ended_at"] = event["ended_at"]
        error = event.get("error") if isinstance(event.get("error"), dict) else {}
        error_message = error.get("message") or details.get("error_message") or details.get("error")
        if error_message:
            row["error_message"] = error_message
        event_artifacts = _artifact_refs_for_event(event, artifact_refs)
        if event_artifacts:
            row["artifacts"] = event_artifacts
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


def _duration_coverage(rows):
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    recorded_count = sum(
        1
        for row in normalized_rows
        if (row.get("duration_source") or "unknown") != "missing"
    )
    missing_count = len(normalized_rows) - recorded_count
    return {
        "duration_recorded_count": recorded_count,
        "duration_missing_count": missing_count,
        "duration_coverage_ratio": 0 if not normalized_rows else round(recorded_count / len(normalized_rows), 4),
    }


def _summary_coverage(rows):
    """Return how many report rows include human-readable summaries."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    recorded_count = sum(1 for row in normalized_rows if row.get("summary"))
    missing_count = len(normalized_rows) - recorded_count
    return {
        "summary_recorded_count": recorded_count,
        "summary_missing_count": missing_count,
        "summary_coverage_ratio": 0 if not normalized_rows else round(recorded_count / len(normalized_rows), 4),
    }


def _summary_source_counts(rows):
    """Count where human-readable report summaries came from."""
    counts = {}
    for row in rows or []:
        if not isinstance(row, dict) or not row.get("summary"):
            continue
        source = row.get("summary_source") or "nested_or_inline"
        counts[source] = counts.get(source, 0) + 1
    return counts


def _summary_source_counts_by_field(rows, field):
    """Return summary provenance counts grouped by a report row field."""
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        label = row.get(field) or "unknown"
        rows_by_label.setdefault(label, []).append(row)
    return {label: _summary_source_counts(group_rows) for label, group_rows in rows_by_label.items()}


def _summary_source_counts_by_exit_code(rows):
    return {label: _summary_source_counts(group_rows) for label, group_rows in _rows_by_exit_code(rows).items()}


def _summary_source_counts_by_activity_identity(rows):
    return {
        label: _summary_source_counts(group_rows)
        for label, group_rows in _activity_rows_by_identity(rows).items()
    }


def _summary_duration_example_row(row):
    """Return compact context for an unsummarized row contributing duration."""
    example = {
        "event": row.get("event"),
        "status": row.get("status"),
        "duration_ms": _numeric_value(row.get("duration_ms")),
        "duration_source": row.get("duration_source"),
    }
    if row.get("type"):
        example["type"] = row.get("type")
    if row.get("command") is not None:
        example["command"] = row.get("command")
        if row.get("cwd"):
            example["cwd"] = row["cwd"]
        if row.get("exit_code") is not None:
            example["exit_code"] = row.get("exit_code")
    elif row.get("path") is not None:
        example.update({
            "path": row.get("path"),
            "kind": row.get("kind"),
            "added_lines": _numeric_value(row.get("added_lines")),
            "removed_lines": _numeric_value(row.get("removed_lines")),
            "net_line_delta": _net_line_delta(row),
        })
    if row.get("started_at"):
        example["started_at"] = row["started_at"]
    if row.get("ended_at"):
        example["ended_at"] = row["ended_at"]
    if row.get("summary"):
        example["summary"] = row["summary"]
        if row.get("summary_source"):
            example["summary_source"] = row["summary_source"]
    if row.get("artifacts"):
        example["artifacts"] = row["artifacts"]
    return example


def _summary_missing_duration_example_rows(rows, limit=3):
    """Return the highest-duration rows that lack human-readable summaries."""
    candidates = [
        (index, row)
        for index, row in enumerate(rows or [])
        if isinstance(row, dict) and not row.get("summary")
    ]
    candidates.sort(key=lambda item: (-_numeric_value(item[1].get("duration_ms")), item[0]))
    return [_summary_duration_example_row(row) for _, row in candidates[:limit]]


def _summary_recorded_duration_example_rows(rows, limit=3):
    """Return the highest-duration rows that include human-readable summaries."""
    candidates = [
        (index, row)
        for index, row in enumerate(rows or [])
        if isinstance(row, dict) and row.get("summary")
    ]
    candidates.sort(key=lambda item: (-_numeric_value(item[1].get("duration_ms")), item[0]))
    return [_summary_duration_example_row(row) for _, row in candidates[:limit]]


def _timing_window_example_row(row):
    """Return compact context for timestamp-window coverage examples."""
    example = _summary_duration_example_row(row)
    timestamp_window_ms = _duration_between_ms(row.get("started_at"), row.get("ended_at"))
    if timestamp_window_ms is not None:
        example["timestamp_window_ms"] = timestamp_window_ms
        if _has_recorded_duration(row):
            duration_window_delta_ms = _numeric_value(row.get("duration_ms")) - timestamp_window_ms
            example["duration_window_delta_ms"] = duration_window_delta_ms
            example["duration_window_delta_abs_ms"] = abs(duration_window_delta_ms)
    if not row.get("started_at"):
        example["missing_started_at"] = True
    if not row.get("ended_at"):
        example["missing_ended_at"] = True
    return example


def _has_recorded_duration(row):
    return isinstance(row, dict) and (row.get("duration_source") or "unknown") != "missing"


def _duration_window_delta_rows(rows):
    comparable_rows = []
    for index, row in enumerate(rows or []):
        if not isinstance(row, dict) or not _has_recorded_duration(row):
            continue
        timestamp_window_ms = _duration_between_ms(row.get("started_at"), row.get("ended_at"))
        if timestamp_window_ms is None:
            continue
        duration_window_delta_ms = _numeric_value(row.get("duration_ms")) - timestamp_window_ms
        comparable_rows.append({
            "index": index,
            "row": row,
            "timestamp_window_ms": timestamp_window_ms,
            "duration_window_delta_ms": duration_window_delta_ms,
            "duration_window_delta_abs_ms": abs(duration_window_delta_ms),
        })
    return comparable_rows


def _duration_window_delta_metrics(rows):
    """Compare recorded duration_ms with complete started_at/ended_at windows."""
    delta_rows = _duration_window_delta_rows(rows)
    total_delta_ms = sum(row["duration_window_delta_ms"] for row in delta_rows)
    total_abs_delta_ms = sum(row["duration_window_delta_abs_ms"] for row in delta_rows)
    comparable_recorded_duration_ms = sum(_numeric_value(row["row"].get("duration_ms")) for row in delta_rows)
    delta_abs_recorded_duration_share = (
        0 if not comparable_recorded_duration_ms else round(total_abs_delta_ms / comparable_recorded_duration_ms, 4)
    )
    if not delta_rows:
        consistency_label = "no_comparable_rows"
    elif not total_abs_delta_ms:
        consistency_label = "matched"
    elif delta_abs_recorded_duration_share >= 0.25:
        consistency_label = "high_delta"
    elif delta_abs_recorded_duration_share >= 0.1:
        consistency_label = "medium_delta"
    else:
        consistency_label = "low_delta"
    direction_counts = {
        "matches": 0,
        "duration_exceeds_window": 0,
        "window_exceeds_duration": 0,
    }
    direction_examples = {
        "matches": [],
        "duration_exceeds_window": [],
        "window_exceeds_duration": [],
    }
    for delta_row in delta_rows:
        delta_ms = delta_row["duration_window_delta_ms"]
        if delta_ms > 0:
            direction = "duration_exceeds_window"
        elif delta_ms < 0:
            direction = "window_exceeds_duration"
        else:
            direction = "matches"
        direction_counts[direction] += 1
        direction_examples[direction].append(delta_row)
    for direction, examples in direction_examples.items():
        examples.sort(key=lambda item: (-item["duration_window_delta_abs_ms"], item["index"]))
        direction_examples[direction] = [_timing_window_example_row(item["row"]) for item in examples[:3]]
    largest_delta = None
    for delta_row in delta_rows:
        if largest_delta is None or delta_row["duration_window_delta_abs_ms"] > largest_delta["duration_window_delta_abs_ms"]:
            largest_delta = delta_row
    largest_delta_example = None
    if largest_delta is not None:
        largest_delta_example = _timing_window_example_row(largest_delta["row"])
    return {
        "duration_window_comparable_count": len(delta_rows),
        "duration_window_delta_total_ms": total_delta_ms,
        "duration_window_delta_abs_total_ms": total_abs_delta_ms,
        "duration_window_delta_average_ms": 0 if not delta_rows else round(total_delta_ms / len(delta_rows), 2),
        "duration_window_delta_abs_average_ms": 0 if not delta_rows else round(total_abs_delta_ms / len(delta_rows), 2),
        "duration_window_delta_abs_recorded_duration_share": delta_abs_recorded_duration_share,
        "duration_window_delta_consistency_label": consistency_label,
        "duration_window_delta_direction_counts": direction_counts,
        "duration_window_delta_direction_examples": direction_examples,
        "largest_duration_window_delta_ms": 0 if largest_delta is None else largest_delta["duration_window_delta_abs_ms"],
        "largest_duration_window_delta_example": largest_delta_example,
    }


def _missing_timing_window_example_rows(rows, limit=3):
    """Return compact rows that lack a complete started_at/ended_at window."""
    candidates = [
        (index, row)
        for index, row in enumerate(rows or [])
        if isinstance(row, dict)
        and _duration_between_ms(row.get("started_at"), row.get("ended_at")) is None
    ]
    candidates.sort(key=lambda item: (-_numeric_value(item[1].get("duration_ms")), item[0]))
    return [_timing_window_example_row(row) for _, row in candidates[:limit]]


def _partial_timing_window_example_rows(rows, limit=3):
    """Return examples grouped by which timestamp boundary is missing."""
    buckets = {
        "started_only": [],
        "ended_only": [],
        "missing_both": [],
    }
    for index, row in enumerate(rows or []):
        if not isinstance(row, dict):
            continue
        has_started_at = bool(row.get("started_at"))
        has_ended_at = bool(row.get("ended_at"))
        if has_started_at and not has_ended_at:
            bucket = "started_only"
        elif has_ended_at and not has_started_at:
            bucket = "ended_only"
        elif not has_started_at and not has_ended_at:
            bucket = "missing_both"
        else:
            continue
        buckets[bucket].append((index, row))

    grouped_examples = {}
    for bucket, candidates in buckets.items():
        candidates.sort(key=lambda item: (-_numeric_value(item[1].get("duration_ms")), item[0]))
        grouped_examples[bucket] = [_timing_window_example_row(row) for _, row in candidates[:limit]]
    return grouped_examples


def _partial_timing_window_duration_totals(rows):
    """Return duration totals grouped by incomplete timestamp boundary shape."""
    totals = {
        "started_only": 0,
        "ended_only": 0,
        "missing_both": 0,
    }
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        has_started_at = bool(row.get("started_at"))
        has_ended_at = bool(row.get("ended_at"))
        if has_started_at and not has_ended_at:
            bucket = "started_only"
        elif has_ended_at and not has_started_at:
            bucket = "ended_only"
        elif not has_started_at and not has_ended_at:
            bucket = "missing_both"
        else:
            continue
        totals[bucket] += _numeric_value(row.get("duration_ms"))
    return totals


def _timing_window_metrics(rows):
    """Return timestamp-window coverage for command, edit, or activity report rows."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    complete_window_rows = [
        row for row in normalized_rows
        if _duration_between_ms(row.get("started_at"), row.get("ended_at")) is not None
    ]
    missing_window_rows = [
        row for row in normalized_rows
        if _duration_between_ms(row.get("started_at"), row.get("ended_at")) is None
    ]
    window_durations = [_duration_between_ms(row.get("started_at"), row.get("ended_at")) for row in complete_window_rows]
    total_window_ms = sum(window_durations)
    total_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in normalized_rows)
    complete_window_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in complete_window_rows)
    missing_window_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in missing_window_rows)
    largest_row = None
    for row in complete_window_rows:
        if largest_row is None or (_duration_between_ms(row.get("started_at"), row.get("ended_at")) or 0) > (_duration_between_ms(largest_row.get("started_at"), largest_row.get("ended_at")) or 0):
            largest_row = row
    timing_window_metrics = {
        "timing_row_count": len(normalized_rows),
        "started_at_count": sum(1 for row in normalized_rows if row.get("started_at")),
        "ended_at_count": sum(1 for row in normalized_rows if row.get("ended_at")),
        "started_only_count": sum(1 for row in normalized_rows if row.get("started_at") and not row.get("ended_at")),
        "ended_only_count": sum(1 for row in normalized_rows if row.get("ended_at") and not row.get("started_at")),
        "missing_started_at_count": sum(1 for row in normalized_rows if not row.get("started_at")),
        "missing_ended_at_count": sum(1 for row in normalized_rows if not row.get("ended_at")),
        "complete_window_count": len(complete_window_rows),
        "missing_window_count": len(normalized_rows) - len(complete_window_rows),
        "complete_window_ratio": 0 if not normalized_rows else round(len(complete_window_rows) / len(normalized_rows), 4),
        "complete_window_duration_ms": complete_window_duration_ms,
        "complete_window_duration_share": 0 if not total_duration_ms else round(complete_window_duration_ms / total_duration_ms, 4),
        "missing_window_duration_ms": missing_window_duration_ms,
        "missing_window_duration_share": 0 if not total_duration_ms else round(missing_window_duration_ms / total_duration_ms, 4),
        "partial_timestamp_window_duration_ms": _partial_timing_window_duration_totals(normalized_rows),
        "timestamp_window_total_ms": total_window_ms,
        "timestamp_window_average_ms": 0 if not complete_window_rows else round(total_window_ms / len(complete_window_rows), 2),
        "timestamp_window_extremes_ms": {"min": min(window_durations), "max": max(window_durations)} if window_durations else {"min": 0, "max": 0},
        "largest_timestamp_window_ms": max(window_durations) if window_durations else 0,
        "largest_timestamp_window_example": _timing_window_example_row(largest_row) if largest_row is not None else None,
        "missing_timestamp_window_examples": _missing_timing_window_example_rows(normalized_rows),
        "partial_timestamp_window_examples": _partial_timing_window_example_rows(normalized_rows),
    }
    timing_window_metrics.update(_duration_window_delta_metrics(normalized_rows))
    return timing_window_metrics


def _summary_timing_window_gap_label(count_delta, duration_delta):
    """Label whether missing-summary rows are more timestamp-sparse than summarized rows."""
    max_gap = max(count_delta, duration_delta)
    if max_gap <= 0:
        return "no_missing_summary_gap"
    if max_gap >= 0.5:
        return "high_missing_summary_gap"
    if max_gap >= 0.25:
        return "medium_missing_summary_gap"
    return "low_missing_summary_gap"


def _summary_timing_window_excess_attention_label(excess_share, excess_duration_share):
    """Label whether positive missing-summary incomplete-window excess needs attention."""
    max_excess = max(excess_share, excess_duration_share)
    if max_excess <= 0:
        return "no_missing_summary_window_excess"
    if max_excess >= 0.5:
        return "high_missing_summary_window_excess"
    if max_excess >= 0.25:
        return "medium_missing_summary_window_excess"
    return "low_missing_summary_window_excess"


def _summary_missing_window_duration_ratio_label(summarized_missing_duration_ms, unsummarized_missing_duration_ms):
    """Label which summary bucket carries missing timestamp-window duration."""
    if not summarized_missing_duration_ms and not unsummarized_missing_duration_ms:
        return "no_missing_window_duration"
    if not summarized_missing_duration_ms:
        return "missing_summary_only_missing_window_duration"
    if not unsummarized_missing_duration_ms:
        return "recorded_summary_only_missing_window_duration"

    ratio = unsummarized_missing_duration_ms / summarized_missing_duration_ms
    if ratio >= 2:
        return "missing_summary_duration_dominant"
    if ratio >= 1.25:
        return "missing_summary_duration_elevated"
    if ratio <= 0.75:
        return "recorded_summary_duration_higher"
    return "balanced_missing_window_duration"


def _summary_missing_window_duration_delta_label(duration_delta_ms):
    """Label the signed missing-window duration delta by summary bucket."""
    if duration_delta_ms > 0:
        return "missing_summary_missing_window_duration_higher"
    if duration_delta_ms < 0:
        return "recorded_summary_missing_window_duration_higher"
    return "balanced_missing_window_duration_delta"


def _summary_timing_window_metrics(rows):
    """Return complete timestamp-window coverage split by summary presence."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    summarized_rows = [row for row in normalized_rows if row.get("summary")]
    unsummarized_rows = [row for row in normalized_rows if not row.get("summary")]

    summarized_complete_rows = [
        row for row in summarized_rows
        if _duration_between_ms(row.get("started_at"), row.get("ended_at")) is not None
    ]
    unsummarized_complete_rows = [
        row for row in unsummarized_rows
        if _duration_between_ms(row.get("started_at"), row.get("ended_at")) is not None
    ]
    summarized_missing_rows = [row for row in summarized_rows if row not in summarized_complete_rows]
    unsummarized_missing_rows = [row for row in unsummarized_rows if row not in unsummarized_complete_rows]

    summarized_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in summarized_rows)
    unsummarized_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in unsummarized_rows)
    summarized_complete_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in summarized_complete_rows)
    unsummarized_complete_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in unsummarized_complete_rows)
    summarized_missing_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in summarized_missing_rows)
    unsummarized_missing_duration_ms = sum(_numeric_value(row.get("duration_ms")) for row in unsummarized_missing_rows)
    summarized_missing_window_share = (
        0 if not summarized_rows else round(len(summarized_missing_rows) / len(summarized_rows), 4)
    )
    unsummarized_missing_window_share = (
        0 if not unsummarized_rows else round(len(unsummarized_missing_rows) / len(unsummarized_rows), 4)
    )
    summarized_missing_window_duration_share = (
        0 if not summarized_duration_ms else round(summarized_missing_duration_ms / summarized_duration_ms, 4)
    )
    unsummarized_missing_window_duration_share = (
        0 if not unsummarized_duration_ms else round(unsummarized_missing_duration_ms / unsummarized_duration_ms, 4)
    )

    missing_window_share_delta = round(
        unsummarized_missing_window_share - summarized_missing_window_share,
        4,
    )
    missing_window_duration_share_delta = round(
        unsummarized_missing_window_duration_share - summarized_missing_window_duration_share,
        4,
    )
    total_duration_ms = summarized_duration_ms + unsummarized_duration_ms
    missing_window_excess_duration_ms = max(
        0,
        unsummarized_missing_duration_ms - summarized_missing_duration_ms,
    )
    summary_missing_window_duration_delta_ms = (
        unsummarized_missing_duration_ms - summarized_missing_duration_ms
    )
    summary_missing_window_duration_delta_abs_ms = abs(summary_missing_window_duration_delta_ms)
    complete_window_duration_total_ms = summarized_complete_duration_ms + unsummarized_complete_duration_ms
    missing_window_duration_total_ms = summarized_missing_duration_ms + unsummarized_missing_duration_ms
    summary_complete_window_duration_delta_ms = (
        unsummarized_complete_duration_ms - summarized_complete_duration_ms
    )
    summary_complete_window_duration_total_share = (
        0 if not total_duration_ms else round(complete_window_duration_total_ms / total_duration_ms, 4)
    )
    summary_missing_window_duration_total_share = (
        0 if not total_duration_ms else round(missing_window_duration_total_ms / total_duration_ms, 4)
    )
    summary_missing_window_duration_delta_abs_share = (
        0 if not missing_window_duration_total_ms else round(
            summary_missing_window_duration_delta_abs_ms / missing_window_duration_total_ms,
            4,
        )
    )
    summary_missing_window_duration_delta_share = (
        0 if not missing_window_duration_total_ms else round(
            summary_missing_window_duration_delta_ms / missing_window_duration_total_ms,
            4,
        )
    )
    total_row_count = len(summarized_rows) + len(unsummarized_rows)
    missing_window_excess_count = max(
        0,
        len(unsummarized_missing_rows) - len(summarized_missing_rows),
    )
    missing_window_excess_share = (
        0 if not total_row_count else round(missing_window_excess_count / total_row_count, 4)
    )
    missing_window_excess_duration_share = (
        0 if not total_duration_ms else round(missing_window_excess_duration_ms / total_duration_ms, 4)
    )
    missing_window_excess_missing_duration_share = (
        0 if not unsummarized_missing_duration_ms else round(
            missing_window_excess_duration_ms / unsummarized_missing_duration_ms,
            4,
        )
    )
    summary_missing_window_duration_ratio = (
        None if not summarized_missing_duration_ms and unsummarized_missing_duration_ms else (
            0 if not summarized_missing_duration_ms else round(
                unsummarized_missing_duration_ms / summarized_missing_duration_ms,
                4,
            )
        )
    )
    missing_window_excess_average_duration_ms = (
        0 if not missing_window_excess_count else round(missing_window_excess_duration_ms / missing_window_excess_count, 2)
    )

    return {
        "summary_recorded_complete_window_count": len(summarized_complete_rows),
        "summary_missing_complete_window_count": len(unsummarized_complete_rows),
        "summary_recorded_missing_window_count": len(summarized_missing_rows),
        "summary_missing_missing_window_count": len(unsummarized_missing_rows),
        "summary_missing_window_excess_count": missing_window_excess_count,
        "summary_missing_window_excess_share": missing_window_excess_share,
        "summary_recorded_complete_window_duration_ms": summarized_complete_duration_ms,
        "summary_missing_complete_window_duration_ms": unsummarized_complete_duration_ms,
        "summary_complete_window_duration_total_ms": complete_window_duration_total_ms,
        "summary_complete_window_duration_total_share": summary_complete_window_duration_total_share,
        "summary_complete_window_duration_delta_ms": summary_complete_window_duration_delta_ms,
        "summary_recorded_missing_window_duration_ms": summarized_missing_duration_ms,
        "summary_missing_missing_window_duration_ms": unsummarized_missing_duration_ms,
        "summary_missing_window_duration_delta_ms": summary_missing_window_duration_delta_ms,
        "summary_missing_window_duration_delta_label": _summary_missing_window_duration_delta_label(
            summary_missing_window_duration_delta_ms,
        ),
        "summary_missing_window_duration_delta_abs_ms": summary_missing_window_duration_delta_abs_ms,
        "summary_missing_window_duration_total_ms": missing_window_duration_total_ms,
        "summary_missing_window_duration_total_share": summary_missing_window_duration_total_share,
        "summary_missing_window_duration_delta_abs_share": summary_missing_window_duration_delta_abs_share,
        "summary_missing_window_duration_delta_share": summary_missing_window_duration_delta_share,
        "summary_missing_window_excess_duration_ms": missing_window_excess_duration_ms,
        "summary_missing_window_excess_duration_share": missing_window_excess_duration_share,
        "summary_missing_window_excess_missing_duration_share": missing_window_excess_missing_duration_share,
        "summary_missing_window_duration_ratio": summary_missing_window_duration_ratio,
        "summary_missing_window_duration_ratio_label": _summary_missing_window_duration_ratio_label(
            summarized_missing_duration_ms,
            unsummarized_missing_duration_ms,
        ),
        "summary_missing_window_excess_average_duration_ms": missing_window_excess_average_duration_ms,
        "summary_missing_window_excess_attention_label": _summary_timing_window_excess_attention_label(
            missing_window_excess_share,
            missing_window_excess_duration_share,
        ),
        "summary_recorded_complete_window_share": (
            0 if not summarized_rows else round(len(summarized_complete_rows) / len(summarized_rows), 4)
        ),
        "summary_missing_complete_window_share": (
            0 if not unsummarized_rows else round(len(unsummarized_complete_rows) / len(unsummarized_rows), 4)
        ),
        "summary_recorded_missing_window_share": summarized_missing_window_share,
        "summary_missing_missing_window_share": unsummarized_missing_window_share,
        "summary_missing_window_share_delta": missing_window_share_delta,
        "summary_recorded_complete_window_duration_share": (
            0 if not summarized_duration_ms else round(summarized_complete_duration_ms / summarized_duration_ms, 4)
        ),
        "summary_missing_complete_window_duration_share": (
            0 if not unsummarized_duration_ms else round(unsummarized_complete_duration_ms / unsummarized_duration_ms, 4)
        ),
        "summary_recorded_missing_window_duration_share": summarized_missing_window_duration_share,
        "summary_missing_missing_window_duration_share": unsummarized_missing_window_duration_share,
        "summary_missing_window_duration_share_delta": missing_window_duration_share_delta,
        "summary_missing_window_gap_label": _summary_timing_window_gap_label(
            missing_window_share_delta,
            missing_window_duration_share_delta,
        ),
    }


def _summary_duration_metrics(rows):
    """Return duration impact split by rows with and without summaries."""
    normalized_rows = [row for row in rows or [] if isinstance(row, dict)]
    recorded_duration_rows = [row for row in normalized_rows if row.get("summary")]
    missing_duration_rows = [row for row in normalized_rows if not row.get("summary")]
    recorded_duration_count = len(recorded_duration_rows)
    missing_duration_count = len(missing_duration_rows)
    total_duration_count = recorded_duration_count + missing_duration_count
    recorded_duration_ms = sum(
        _numeric_value(row.get("duration_ms"))
        for row in normalized_rows
        if row.get("summary")
    )
    missing_duration_ms = sum(
        _numeric_value(row.get("duration_ms"))
        for row in normalized_rows
        if not row.get("summary")
    )
    total_duration_ms = recorded_duration_ms + missing_duration_ms
    recorded_duration_source_duration_ms = _duration_totals_by_source(recorded_duration_rows)
    missing_duration_source_duration_ms = _duration_totals_by_source(missing_duration_rows)
    recorded_examples = _summary_recorded_duration_example_rows(normalized_rows)
    missing_examples = _summary_missing_duration_example_rows(normalized_rows)
    largest_recorded_duration_ms = recorded_examples[0]["duration_ms"] if recorded_examples else 0
    largest_missing_duration_ms = missing_examples[0]["duration_ms"] if missing_examples else 0
    missing_recorded_duration_delta_ms = missing_duration_ms - recorded_duration_ms
    missing_recorded_duration_delta_share = (
        0 if not total_duration_ms else round(missing_recorded_duration_delta_ms / total_duration_ms, 4)
    )
    missing_recorded_duration_ratio = (
        None if not recorded_duration_ms and missing_duration_ms else (
            0 if not recorded_duration_ms else round(missing_duration_ms / recorded_duration_ms, 4)
        )
    )
    missing_recorded_excess_duration_ms = max(missing_recorded_duration_delta_ms, 0)
    if missing_duration_ms > recorded_duration_ms:
        summary_duration_balance = "missing_dominates"
    elif recorded_duration_ms > missing_duration_ms:
        summary_duration_balance = "recorded_dominates"
    elif total_duration_ms:
        summary_duration_balance = "balanced"
    else:
        summary_duration_balance = "none"
    if not missing_duration_ms:
        summary_missing_duration_attention = "none"
    elif missing_duration_ms > recorded_duration_ms:
        summary_missing_duration_attention = "high"
    elif missing_duration_ms == recorded_duration_ms:
        summary_missing_duration_attention = "medium"
    else:
        summary_missing_duration_attention = "low"
    largest_missing_duration_share = (
        0 if not missing_duration_ms else round(largest_missing_duration_ms / missing_duration_ms, 4)
    )
    if not missing_duration_ms:
        summary_missing_duration_concentration = "none"
    elif largest_missing_duration_share >= 0.75:
        summary_missing_duration_concentration = "single_row"
    elif largest_missing_duration_share >= 0.5:
        summary_missing_duration_concentration = "clustered"
    else:
        summary_missing_duration_concentration = "distributed"
    return {
        "summary_recorded_duration_count": recorded_duration_count,
        "summary_missing_duration_count": missing_duration_count,
        "summary_total_duration_count": total_duration_count,
        "summary_recorded_count_share": 0 if not total_duration_count else round(recorded_duration_count / total_duration_count, 4),
        "summary_missing_count_share": 0 if not total_duration_count else round(missing_duration_count / total_duration_count, 4),
        "summary_total_duration_ms": total_duration_ms,
        "summary_recorded_duration_ms": recorded_duration_ms,
        "summary_recorded_duration_share": 0 if not total_duration_ms else round(recorded_duration_ms / total_duration_ms, 4),
        "summary_recorded_average_duration_ms": (
            0 if not recorded_duration_count else round(recorded_duration_ms / recorded_duration_count, 2)
        ),
        "summary_recorded_median_duration_ms": _median_duration_ms(recorded_duration_rows),
        "summary_recorded_duration_range_ms": _duration_range_ms(recorded_duration_rows),
        "summary_recorded_duration_extremes_ms": _duration_extremes_ms(recorded_duration_rows),
        "summary_recorded_duration_source_counts": _duration_source_counts(recorded_duration_rows),
        "summary_recorded_duration_source_duration_ms": recorded_duration_source_duration_ms,
        "summary_recorded_duration_source_share": _duration_shares(recorded_duration_source_duration_ms, recorded_duration_ms),
        "summary_largest_recorded_duration_ms": largest_recorded_duration_ms,
        "summary_largest_recorded_duration_share": 0 if not recorded_duration_ms else round(largest_recorded_duration_ms / recorded_duration_ms, 4),
        "summary_largest_recorded_total_duration_share": 0 if not total_duration_ms else round(largest_recorded_duration_ms / total_duration_ms, 4),
        "summary_recorded_duration_examples": recorded_examples,
        "summary_missing_duration_ms": missing_duration_ms,
        "summary_missing_average_duration_ms": (
            0 if not missing_duration_count else round(missing_duration_ms / missing_duration_count, 2)
        ),
        "summary_missing_median_duration_ms": _median_duration_ms(missing_duration_rows),
        "summary_missing_duration_range_ms": _duration_range_ms(missing_duration_rows),
        "summary_missing_duration_extremes_ms": _duration_extremes_ms(missing_duration_rows),
        "summary_missing_duration_source_counts": _duration_source_counts(missing_duration_rows),
        "summary_missing_duration_source_duration_ms": missing_duration_source_duration_ms,
        "summary_missing_duration_source_share": _duration_shares(missing_duration_source_duration_ms, missing_duration_ms),
        "summary_missing_duration_status_counts": _value_counts(missing_duration_rows, "status", missing_label="unknown"),
        "summary_missing_duration_status_duration_ms": _duration_totals_by_status(missing_duration_rows),
        "summary_missing_duration_status_share": _duration_shares_by_status(
            _duration_totals_by_status(missing_duration_rows),
            missing_duration_ms,
        ),
        "summary_missing_duration_share": 0 if not total_duration_ms else round(missing_duration_ms / total_duration_ms, 4),
        "summary_missing_recorded_duration_delta_ms": missing_recorded_duration_delta_ms,
        "summary_missing_recorded_duration_delta_share": missing_recorded_duration_delta_share,
        "summary_missing_recorded_duration_ratio": missing_recorded_duration_ratio,
        "summary_missing_recorded_excess_duration_ms": missing_recorded_excess_duration_ms,
        "summary_duration_balance": summary_duration_balance,
        "summary_missing_duration_attention": summary_missing_duration_attention,
        "summary_missing_exceeds_recorded_duration": missing_duration_ms > recorded_duration_ms,
        "summary_missing_duration_concentration": summary_missing_duration_concentration,
        "summary_largest_missing_duration_ms": largest_missing_duration_ms,
        "summary_largest_missing_duration_share": largest_missing_duration_share,
        "summary_largest_missing_total_duration_share": 0 if not total_duration_ms else round(largest_missing_duration_ms / total_duration_ms, 4),
        "summary_missing_duration_examples": missing_examples,
    }


def _summary_example_rows(rows, row_type, limit=3):
    """Return compact examples for rows with human-readable summaries."""
    examples = []
    for row in rows or []:
        if not isinstance(row, dict) or not row.get("summary"):
            continue
        example = {
            "event": row.get("event"),
            "status": row.get("status"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
            "summary": row.get("summary"),
        }
        if row.get("summary_source"):
            example["summary_source"] = row["summary_source"]
        if row_type == "command":
            example["command"] = row.get("command")
            if row.get("cwd"):
                example["cwd"] = row["cwd"]
            if row.get("exit_code") is not None:
                example["exit_code"] = row.get("exit_code")
        elif row_type == "file_edit":
            example.update({
                "path": row.get("path"),
                "kind": row.get("kind"),
                "added_lines": _numeric_value(row.get("added_lines")),
                "removed_lines": _numeric_value(row.get("removed_lines")),
                "net_line_delta": _net_line_delta(row),
            })
        if row.get("artifacts"):
            example["artifacts"] = row["artifacts"]
        examples.append(example)
        if len(examples) >= limit:
            break
    return examples


def _summary_missing_example_rows(rows, row_type, limit=3):
    """Return compact examples for rows that lack human-readable summaries."""
    examples = []
    for row in rows or []:
        if not isinstance(row, dict) or row.get("summary"):
            continue
        example = {
            "event": row.get("event"),
            "status": row.get("status"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
        }
        if row_type == "command":
            example["command"] = row.get("command")
            if row.get("cwd"):
                example["cwd"] = row["cwd"]
            if row.get("exit_code") is not None:
                example["exit_code"] = row.get("exit_code")
        elif row_type == "file_edit":
            example.update({
                "path": row.get("path"),
                "kind": row.get("kind"),
                "added_lines": _numeric_value(row.get("added_lines")),
                "removed_lines": _numeric_value(row.get("removed_lines")),
                "net_line_delta": _net_line_delta(row),
            })
        if row.get("artifacts"):
            example["artifacts"] = row["artifacts"]
        examples.append(example)
        if len(examples) >= limit:
            break
    return examples


def _activity_summary_example_rows(rows, limit=3):
    """Return compact activity examples with human-readable summaries."""
    examples = []
    for row in rows or []:
        if not isinstance(row, dict) or not row.get("summary"):
            continue
        row_type = row.get("type") or "unknown"
        example = {
            "type": row_type,
            "event": row.get("event"),
            "status": row.get("status"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
            "summary": row.get("summary"),
        }
        if row.get("summary_source"):
            example["summary_source"] = row["summary_source"]
        if row_type == "command":
            example["command"] = row.get("command")
            if row.get("cwd"):
                example["cwd"] = row["cwd"]
            if row.get("exit_code") is not None:
                example["exit_code"] = row.get("exit_code")
        elif row_type == "file_edit":
            example.update({
                "path": row.get("path"),
                "kind": row.get("kind"),
                "added_lines": _numeric_value(row.get("added_lines")),
                "removed_lines": _numeric_value(row.get("removed_lines")),
                "net_line_delta": _net_line_delta(row),
            })
        if row.get("artifacts"):
            example["artifacts"] = row["artifacts"]
        examples.append(example)
        if len(examples) >= limit:
            break
    return examples


def _activity_summary_missing_example_rows(rows, limit=3):
    """Return compact activity examples without human-readable summaries."""
    examples = []
    for row in rows or []:
        if not isinstance(row, dict) or row.get("summary"):
            continue
        row_type = row.get("type") or "unknown"
        example = {
            "type": row_type,
            "event": row.get("event"),
            "status": row.get("status"),
            "duration_ms": _numeric_value(row.get("duration_ms")),
            "duration_source": row.get("duration_source"),
        }
        if row_type == "command":
            example["command"] = row.get("command")
            if row.get("cwd"):
                example["cwd"] = row["cwd"]
            if row.get("exit_code") is not None:
                example["exit_code"] = row.get("exit_code")
        elif row_type == "file_edit":
            example.update({
                "path": row.get("path"),
                "kind": row.get("kind"),
                "added_lines": _numeric_value(row.get("added_lines")),
                "removed_lines": _numeric_value(row.get("removed_lines")),
                "net_line_delta": _net_line_delta(row),
            })
        if row.get("artifacts"):
            example["artifacts"] = row["artifacts"]
        examples.append(example)
        if len(examples) >= limit:
            break
    return examples


def _activity_summary_examples_by_field(rows, field, limit=3):
    """Return compact activity summary examples grouped by a timeline row field."""
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        label = row.get(field) or "unknown"
        rows_by_label.setdefault(label, []).append(row)
    return {
        label: _activity_summary_example_rows(group_rows, limit=limit)
        for label, group_rows in rows_by_label.items()
    }


def _activity_summary_missing_examples_by_field(rows, field, limit=3):
    """Return compact missing-summary activity examples grouped by a timeline row field."""
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        label = row.get(field) or "unknown"
        rows_by_label.setdefault(label, []).append(row)
    return {
        label: _activity_summary_missing_example_rows(group_rows, limit=limit)
        for label, group_rows in rows_by_label.items()
    }


def _activity_identity_label(row):
    """Return a stable human-readable identity label for timeline coverage groups."""
    if not isinstance(row, dict):
        return "unknown"
    row_type = row.get("type") or "unknown"
    if row_type == "command":
        return f"command:{row.get('command') or '<unknown command>'}"
    if row_type == "file_edit":
        return f"file_edit:{row.get('path') or '<unknown file>'}"
    return row_type


def _activity_rows_by_identity(rows):
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        rows_by_label.setdefault(_activity_identity_label(row), []).append(row)
    return rows_by_label


def _activity_summary_examples_by_identity(rows, limit=3):
    """Return compact activity summary examples grouped by command/file identity."""
    return {
        label: _activity_summary_example_rows(group_rows, limit=limit)
        for label, group_rows in _activity_rows_by_identity(rows).items()
    }


def _activity_summary_missing_examples_by_identity(rows, limit=3):
    """Return compact missing-summary activity examples grouped by command/file identity."""
    return {
        label: _activity_summary_missing_example_rows(group_rows, limit=limit)
        for label, group_rows in _activity_rows_by_identity(rows).items()
    }


def _summary_coverage_by_activity_identity(rows):
    return {
        label: _summary_coverage(group_rows)
        for label, group_rows in _activity_rows_by_identity(rows).items()
    }


def _duration_coverage_by_field(rows, field):
    """Return duration recorded/missing coverage grouped by a row field."""
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        label = row.get(field) or "unknown"
        rows_by_label.setdefault(label, []).append(row)
    return {label: _duration_coverage(group_rows) for label, group_rows in rows_by_label.items()}


def _summary_coverage_by_field(rows, field):
    """Return human-readable summary recorded/missing coverage grouped by a row field."""
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        label = row.get(field) or "unknown"
        rows_by_label.setdefault(label, []).append(row)
    return {label: _summary_coverage(group_rows) for label, group_rows in rows_by_label.items()}


def _exit_code_label(row):
    exit_code = row.get("exit_code") if isinstance(row, dict) else None
    return "unknown" if exit_code is None else str(exit_code)


def _rows_by_exit_code(rows):
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        rows_by_label.setdefault(_exit_code_label(row), []).append(row)
    return rows_by_label


def _duration_coverage_by_exit_code(rows):
    return {label: _duration_coverage(group_rows) for label, group_rows in _rows_by_exit_code(rows).items()}


def _summary_coverage_by_exit_code(rows):
    return {label: _summary_coverage(group_rows) for label, group_rows in _rows_by_exit_code(rows).items()}


def _summary_examples_by_exit_code(rows, limit=3):
    """Return compact command summary examples grouped by exit-code label."""
    return {
        label: _summary_example_rows(group_rows, "command", limit=limit)
        for label, group_rows in _rows_by_exit_code(rows).items()
    }


def _summary_missing_examples_by_exit_code(rows, limit=3):
    """Return compact missing-summary command examples grouped by exit-code label."""
    return {
        label: _summary_missing_example_rows(group_rows, "command", limit=limit)
        for label, group_rows in _rows_by_exit_code(rows).items()
    }


def _summary_examples_by_field(rows, field, row_type, limit=3):
    """Return compact summary examples grouped by a report row field."""
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        label = row.get(field) or "unknown"
        rows_by_label.setdefault(label, []).append(row)
    return {
        label: _summary_example_rows(group_rows, row_type, limit=limit)
        for label, group_rows in rows_by_label.items()
    }


def _summary_missing_examples_by_field(rows, field, row_type, limit=3):
    """Return compact missing-summary examples grouped by a report row field."""
    rows_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        label = row.get(field) or "unknown"
        rows_by_label.setdefault(label, []).append(row)
    return {
        label: _summary_missing_example_rows(group_rows, row_type, limit=limit)
        for label, group_rows in rows_by_label.items()
    }


def _average_recorded_duration_ms(rows):
    """Average duration across rows that actually recorded or derived timing."""
    recorded_durations = [
        _numeric_value(row.get("duration_ms"))
        for row in rows or []
        if isinstance(row, dict) and (row.get("duration_source") or "unknown") != "missing"
    ]
    if not recorded_durations:
        return 0
    return round(sum(recorded_durations) / len(recorded_durations), 2)


def _duration_totals_by_field(rows, field):
    totals = {}
    for row in rows:
        label = row.get(field) or "unknown"
        totals[label] = totals.get(label, 0) + _numeric_value(row.get("duration_ms"))
    return totals


def _duration_totals_by_type(rows):
    return _duration_totals_by_field(rows, "type")


def _duration_totals_by_status(rows):
    return _duration_totals_by_field(rows, "status")


def _duration_totals_by_exit_code(rows):
    return {
        label: sum(_numeric_value(row.get("duration_ms")) for row in group_rows)
        for label, group_rows in _rows_by_exit_code(rows).items()
    }


def _duration_averages_by_field(rows, field):
    counts = _value_counts(rows, field, missing_label="unknown")
    totals = _duration_totals_by_field(rows, field)
    return {
        label: round(totals.get(label, 0) / count, 2) if count else 0
        for label, count in counts.items()
    }


def _duration_averages_by_type(rows):
    return _duration_averages_by_field(rows, "type")


def _duration_averages_by_status(rows):
    return _duration_averages_by_field(rows, "status")


def _duration_averages_by_exit_code(rows):
    return {
        label: round(sum(_numeric_value(row.get("duration_ms")) for row in group_rows) / len(group_rows), 2) if group_rows else 0
        for label, group_rows in _rows_by_exit_code(rows).items()
    }


def _duration_totals_by_source(rows):
    return _duration_totals_by_field(rows, "duration_source")


def _duration_averages_by_source(rows):
    counts = _duration_source_counts(rows)
    totals = _duration_totals_by_source(rows)
    return {
        source: round(totals.get(source, 0) / count, 2) if count else 0
        for source, count in counts.items()
    }


def _duration_extremes_by_source(rows):
    """Return per-duration-source min/max duration bounds for aggregate report blocks."""
    return _duration_extremes_by_field(rows, "duration_source")


def _duration_extremes_by_status(rows):
    """Return per-status min/max duration bounds for aggregate report blocks."""
    return _duration_extremes_by_field(rows, "status")


def _duration_extremes_by_exit_code(rows):
    durations_by_label = {
        label: [_numeric_value(row.get("duration_ms")) for row in group_rows]
        for label, group_rows in _rows_by_exit_code(rows).items()
    }
    return {
        label: {"min": min(durations), "max": max(durations)}
        for label, durations in durations_by_label.items()
    }


def _duration_extremes_by_type(rows):
    """Return per-activity-type min/max duration bounds for aggregate report blocks."""
    return _duration_extremes_by_field(rows, "type")


def _duration_extremes_by_field(rows, field):
    durations_by_label = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        label = row.get(field) or "unknown"
        durations_by_label.setdefault(label, []).append(_numeric_value(row.get("duration_ms")))
    return {
        label: {"min": min(durations), "max": max(durations)}
        for label, durations in durations_by_label.items()
    }


def _duration_shares(duration_totals, total_duration_ms):
    if not duration_totals:
        return {}
    if not total_duration_ms:
        return {label: 0 for label in duration_totals}
    return {
        label: round(duration_ms / total_duration_ms, 4)
        for label, duration_ms in duration_totals.items()
    }


def _duration_shares_by_type(type_duration_ms, total_duration_ms):
    return _duration_shares(type_duration_ms, total_duration_ms)


def _duration_shares_by_status(status_duration_ms, total_duration_ms):
    return _duration_shares(status_duration_ms, total_duration_ms)


def _dominant_duration_label(duration_totals, total_duration_ms, label_field):
    if not duration_totals:
        return None
    dominant_label = None
    dominant_duration = 0
    for label, duration_ms in duration_totals.items():
        if dominant_label is None or duration_ms > dominant_duration:
            dominant_label = label
            dominant_duration = duration_ms
    return {
        label_field: dominant_label,
        "duration_ms": dominant_duration,
        "duration_share": 0 if not total_duration_ms else round(dominant_duration / total_duration_ms, 4),
    }


def _dominant_duration_type(type_duration_ms, total_duration_ms):
    return _dominant_duration_label(type_duration_ms, total_duration_ms, "type")


def _dominant_duration_cwd(cwd_duration_ms, total_duration_ms):
    return _dominant_duration_label(cwd_duration_ms, total_duration_ms, "cwd")


def _dominant_duration_kind(kind_duration_ms, total_duration_ms):
    return _dominant_duration_label(kind_duration_ms, total_duration_ms, "kind")


def _dominant_duration_status(status_duration_ms, total_duration_ms):
    return _dominant_duration_label(status_duration_ms, total_duration_ms, "status")


def _dominant_duration_exit_code(exit_code_duration_ms, total_duration_ms):
    return _dominant_duration_label(exit_code_duration_ms, total_duration_ms, "exit_code")


def _median_duration_ms(rows):
    durations = sorted(_numeric_value(row.get("duration_ms")) for row in rows or [] if isinstance(row, dict))
    if not durations:
        return 0
    middle = len(durations) // 2
    if len(durations) % 2:
        return durations[middle]
    return round((durations[middle - 1] + durations[middle]) / 2, 2)


def _duration_range_ms(rows):
    durations = [_numeric_value(row.get("duration_ms")) for row in rows or [] if isinstance(row, dict)]
    if not durations:
        return 0
    return max(durations) - min(durations)


def _duration_extremes_ms(rows):
    """Return compact min/max duration bounds for aggregate report blocks."""
    durations = [_numeric_value(row.get("duration_ms")) for row in rows or [] if isinstance(row, dict)]
    if not durations:
        return {"min": 0, "max": 0}
    return {"min": min(durations), "max": max(durations)}


def _summary_example_type(rows):
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        if row.get("command") is not None:
            return "command"
        if row.get("path") is not None:
            return "file_edit"
    return "unknown"


def _add_duration_spread(summary, rows):
    """Attach compact duration spread, coverage, and source-share metrics for repeated aggregate groups."""
    if summary.get("count", 0) <= 1:
        return
    total_duration_ms = summary.get("total_duration_ms", 0)
    source_duration_ms = _duration_totals_by_source(rows)
    status_duration_ms = _duration_totals_by_status(rows)
    duration_coverage = _duration_coverage(rows)
    summary_coverage = _summary_coverage(rows)
    summary["median_duration_ms"] = _median_duration_ms(rows)
    summary["duration_range_ms"] = _duration_range_ms(rows)
    summary["duration_extremes_ms"] = _duration_extremes_ms(rows)
    summary["duration_recorded_count"] = duration_coverage["duration_recorded_count"]
    summary["duration_missing_count"] = duration_coverage["duration_missing_count"]
    summary["duration_coverage_ratio"] = duration_coverage["duration_coverage_ratio"]
    summary["summary_recorded_count"] = summary_coverage["summary_recorded_count"]
    summary["summary_missing_count"] = summary_coverage["summary_missing_count"]
    summary["summary_coverage_ratio"] = summary_coverage["summary_coverage_ratio"]
    summary["summary_source_counts"] = _summary_source_counts(rows)
    summary_example_type = _summary_example_type(rows)
    summary["summary_examples"] = _summary_example_rows(rows, summary_example_type)
    summary["summary_missing_examples"] = _summary_missing_example_rows(rows, summary_example_type)
    summary["status_duration_ms"] = status_duration_ms
    summary["status_average_duration_ms"] = _duration_averages_by_status(rows)
    summary["status_duration_extremes_ms"] = _duration_extremes_by_status(rows)
    summary["status_duration_coverage"] = _duration_coverage_by_field(rows, "status")
    summary["status_duration_share"] = _duration_shares_by_status(status_duration_ms, total_duration_ms)
    summary["dominant_duration_status"] = _dominant_duration_status(status_duration_ms, total_duration_ms)
    summary["duration_source_duration_ms"] = source_duration_ms
    summary["duration_source_average_ms"] = _duration_averages_by_source(rows)
    summary["duration_source_extremes_ms"] = _duration_extremes_by_source(rows)
    summary["duration_source_share"] = _duration_shares(source_duration_ms, total_duration_ms)


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
        if row.get("summary"):
            item["summary"] = row["summary"]
            if row.get("summary_source"):
                item["summary_source"] = row["summary_source"]
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
        if row.get("summary_source"):
            item["summary_source"] = row["summary_source"]
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
        if row.get("summary"):
            activity_row["summary"] = row["summary"]
            if row.get("summary_source"):
                activity_row["summary_source"] = row["summary_source"]
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
            if row.get("summary_source"):
                activity_row["summary_source"] = row["summary_source"]
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


def _covered_activity_intervals(merged_intervals):
    intervals = []
    for start, end in merged_intervals:
        intervals.append({
            "started_at": _timestamp_label(start),
            "ended_at": _timestamp_label(end),
            "duration_ms": round((end - start).total_seconds() * 1000),
        })
    return intervals


def _activity_coverage(rows, time_window=None):
    intervals = []
    for row in rows:
        interval = _activity_interval(row)
        if interval is not None:
            intervals.append(interval)
    if not intervals:
        return {
            "covered_duration_ms": 0,
            "covered_intervals": [],
            "covered_interval_count": 0,
            "merged_covered_interval_count": 0,
            "uncovered_intervals": [],
        }

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
        "covered_intervals": _covered_activity_intervals(merged),
        "covered_interval_count": len(intervals),
        "merged_covered_interval_count": len(merged),
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
    status_duration_ms = _duration_totals_by_status(normalized_rows)
    duration_source_duration_ms = _duration_totals_by_source(normalized_rows)
    duration_coverage = _duration_coverage(normalized_rows)
    summary_coverage = _summary_coverage(normalized_rows)
    return {
        "count": len(normalized_rows),
        "type_counts": type_counts,
        "type_duration_ms": type_duration_ms,
        "type_average_duration_ms": _duration_averages_by_type(normalized_rows),
        "type_duration_extremes_ms": _duration_extremes_by_type(normalized_rows),
        "type_duration_coverage": _duration_coverage_by_field(normalized_rows, "type"),
        "type_duration_share": _duration_shares_by_type(type_duration_ms, total_duration_ms),
        "dominant_duration_type": _dominant_duration_type(type_duration_ms, total_duration_ms),
        "status_counts": status_counts,
        "status_duration_ms": status_duration_ms,
        "status_average_duration_ms": _duration_averages_by_status(normalized_rows),
        "status_duration_extremes_ms": _duration_extremes_by_status(normalized_rows),
        "status_duration_coverage": _duration_coverage_by_field(normalized_rows, "status"),
        "status_duration_share": _duration_shares_by_status(status_duration_ms, total_duration_ms),
        "dominant_duration_status": _dominant_duration_status(status_duration_ms, total_duration_ms),
        "duration_source_counts": _duration_source_counts(normalized_rows),
        "duration_source_duration_ms": duration_source_duration_ms,
        "duration_source_average_ms": _duration_averages_by_source(normalized_rows),
        "duration_source_extremes_ms": _duration_extremes_by_source(normalized_rows),
        "duration_source_share": _duration_shares(duration_source_duration_ms, total_duration_ms),
        "duration_recorded_count": duration_coverage["duration_recorded_count"],
        "duration_missing_count": duration_coverage["duration_missing_count"],
        "duration_coverage_ratio": duration_coverage["duration_coverage_ratio"],
        "summary_recorded_count": summary_coverage["summary_recorded_count"],
        "summary_missing_count": summary_coverage["summary_missing_count"],
        "summary_coverage_ratio": summary_coverage["summary_coverage_ratio"],
        "summary_source_counts": _summary_source_counts(normalized_rows),
        "summary_examples": _activity_summary_example_rows(normalized_rows),
        "summary_missing_examples": _activity_summary_missing_example_rows(normalized_rows),
        "type_summary_examples": _activity_summary_examples_by_field(normalized_rows, "type"),
        "type_summary_missing_examples": _activity_summary_missing_examples_by_field(normalized_rows, "type"),
        "status_summary_examples": _activity_summary_examples_by_field(normalized_rows, "status"),
        "status_summary_missing_examples": _activity_summary_missing_examples_by_field(normalized_rows, "status"),
        "duration_source_summary_examples": _activity_summary_examples_by_field(normalized_rows, "duration_source"),
        "duration_source_summary_missing_examples": _activity_summary_missing_examples_by_field(normalized_rows, "duration_source"),
        "identity_summary_examples": _activity_summary_examples_by_identity(normalized_rows),
        "identity_summary_missing_examples": _activity_summary_missing_examples_by_identity(normalized_rows),
        "time_window": time_window,
        "span_duration_ms": span_duration_ms,
        "covered_duration_ms": coverage["covered_duration_ms"],
        "covered_intervals": coverage["covered_intervals"],
        "uncovered_duration_ms": uncovered_duration_ms,
        "uncovered_intervals": uncovered_intervals,
        "uncovered_interval_count": len(uncovered_intervals),
        "average_uncovered_interval_ms": 0 if not uncovered_intervals else round(uncovered_duration_ms / len(uncovered_intervals), 2),
        "largest_uncovered_interval": largest_uncovered_interval,
        "coverage_ratio": coverage_ratio,
        "idle_ratio": idle_ratio,
        "covered_interval_count": coverage["covered_interval_count"],
        "merged_covered_interval_count": coverage["merged_covered_interval_count"],
        "total_duration_ms": total_duration_ms,
        "average_duration_ms": 0 if not normalized_rows else round(total_duration_ms / len(normalized_rows), 2),
        "average_recorded_duration_ms": _average_recorded_duration_ms(normalized_rows),
        "median_duration_ms": _median_duration_ms(normalized_rows),
        "duration_range_ms": _duration_range_ms(normalized_rows),
        "duration_extremes_ms": _duration_extremes_ms(normalized_rows),
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


def _inspection_target_identity(row):
    """Return the most useful human-readable target for a report row."""
    if not isinstance(row, dict):
        return "unknown"
    row_type = row.get("type")
    if row_type == "command" or row.get("command") is not None:
        return row.get("command") or "<unknown command>"
    if row_type == "file_edit" or row.get("path") is not None:
        return row.get("path") or "<unknown file>"
    return row.get("event") or "unknown"


def _inspection_target_row(row, reason, detail=None):
    target = {
        "type": row.get("type") or ("command" if row.get("command") is not None else "file_edit" if row.get("path") is not None else "activity"),
        "event": row.get("event"),
        "reason": reason,
        "identity": _inspection_target_identity(row),
        "status": row.get("status"),
        "duration_ms": _numeric_value(row.get("duration_ms")),
        "duration_source": row.get("duration_source"),
    }
    if detail:
        target["detail"] = detail
    if row.get("started_at"):
        target["started_at"] = row["started_at"]
    if row.get("ended_at"):
        target["ended_at"] = row["ended_at"]
    if row.get("type") == "command" or row.get("command") is not None:
        if row.get("cwd"):
            target["cwd"] = row["cwd"]
        if row.get("exit_code") is not None:
            target["exit_code"] = row.get("exit_code")
        if row.get("stderr_preview"):
            target["stderr_preview"] = row["stderr_preview"]
    if row.get("type") == "file_edit" or row.get("path") is not None:
        if row.get("kind"):
            target["kind"] = row["kind"]
        if "net_line_delta" in row:
            target["net_line_delta"] = _net_line_delta(row)
        if row.get("error_message"):
            target["error_message"] = row["error_message"]
    if row.get("artifacts"):
        target["artifacts"] = row["artifacts"]
    return target


def build_report_inspection_targets(command_rows, edit_rows, activity_rows, limit=8):
    """Build prioritized rows that tell reviewers what to inspect first."""
    targets = []
    seen = set()

    def add(row, reason, detail=None):
        if not isinstance(row, dict):
            return
        key = (row.get("type"), row.get("event"), reason)
        if key in seen:
            return
        seen.add(key)
        targets.append(_inspection_target_row(row, reason, detail))

    for row in activity_rows or []:
        if _is_failed_activity(row):
            add(row, "failed_activity", "failed status or non-zero command exit code")

    for row in command_rows or []:
        if (row.get("duration_source") or "unknown") == "missing":
            add(row, "missing_command_timing", "command row has no duration or timestamp window")
        if not row.get("summary"):
            add(row, "missing_command_summary", "command row has no human-readable summary")

    for row in edit_rows or []:
        if (row.get("duration_source") or "unknown") == "missing":
            add(row, "missing_edit_timing", "edit row has no duration or timestamp window")
        if not row.get("summary"):
            add(row, "missing_edit_summary", "edit row has no human-readable summary")

    slowest = _slowest_activity_row(activity_rows or [])
    if slowest:
        add(slowest, "slowest_activity", "largest recorded duration in command/edit activity timeline")

    return targets[:limit]


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
        group_rows = summary.pop("_rows")
        summary["average_duration_ms"] = round(summary["total_duration_ms"] / summary["count"], 2)
        _add_duration_spread(summary, group_rows)
        summary["time_window"] = _time_window(group_rows)
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
        group_rows = summary.pop("_rows")
        summary["average_duration_ms"] = round(summary["total_duration_ms"] / summary["count"], 2)
        _add_duration_spread(summary, group_rows)
        summary["time_window"] = _time_window(group_rows)
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
        if row.get("cwd"):
            failed_row["cwd"] = row["cwd"]
        if row.get("summary"):
            failed_row["summary"] = row["summary"]
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
    if row.get("cwd"):
        summary["cwd"] = row["cwd"]
    if row.get("artifacts"):
        summary["artifacts"] = row["artifacts"]
    if row.get("summary"):
        summary["summary"] = row["summary"]
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
    duration_coverage = _duration_coverage(normalized_rows)
    summary_coverage = _summary_coverage(normalized_rows)
    cwd_duration_ms = _duration_totals_by_field(normalized_rows, "cwd")
    status_duration_ms = _duration_totals_by_status(normalized_rows)
    duration_source_duration_ms = _duration_totals_by_source(normalized_rows)
    exit_code_duration_ms = _duration_totals_by_exit_code(normalized_rows)
    return {
        "count": len(normalized_rows),
        "unique_command_count": len(commands_run),
        "commands_run": commands_run,
        "repeated_commands": _repeated_value_counts(normalized_rows, "command"),
        "command_attempts": _command_attempt_rows(normalized_rows),
        "cwd_counts": _value_counts(normalized_rows, "cwd", missing_label="unknown"),
        "cwd_duration_ms": cwd_duration_ms,
        "cwd_average_duration_ms": _duration_averages_by_field(normalized_rows, "cwd"),
        "cwd_duration_extremes_ms": _duration_extremes_by_field(normalized_rows, "cwd"),
        "cwd_duration_coverage": _duration_coverage_by_field(normalized_rows, "cwd"),
        "cwd_duration_share": _duration_shares(cwd_duration_ms, total_duration_ms),
        "dominant_duration_cwd": _dominant_duration_cwd(cwd_duration_ms, total_duration_ms),
        "cwd_totals": _command_cwd_total_rows(normalized_rows),
        "total_duration_ms": total_duration_ms,
        "average_duration_ms": 0 if not normalized_rows else round(total_duration_ms / len(normalized_rows), 2),
        "average_recorded_duration_ms": _average_recorded_duration_ms(normalized_rows),
        "median_duration_ms": _median_duration_ms(normalized_rows),
        "duration_range_ms": _duration_range_ms(normalized_rows),
        "duration_extremes_ms": _duration_extremes_ms(normalized_rows),
        "failed_count": sum(1 for row in normalized_rows if _is_failed_command(row)),
        "failed_commands": _failed_command_rows(normalized_rows),
        "exit_code_counts": _exit_code_counts(normalized_rows),
        "exit_code_duration_ms": exit_code_duration_ms,
        "exit_code_average_duration_ms": _duration_averages_by_exit_code(normalized_rows),
        "exit_code_duration_extremes_ms": _duration_extremes_by_exit_code(normalized_rows),
        "exit_code_duration_coverage": _duration_coverage_by_exit_code(normalized_rows),
        "exit_code_duration_share": _duration_shares(exit_code_duration_ms, total_duration_ms),
        "dominant_duration_exit_code": _dominant_duration_exit_code(exit_code_duration_ms, total_duration_ms),
        "exit_code_summary_coverage": _summary_coverage_by_exit_code(normalized_rows),
        "exit_code_summary_examples": _summary_examples_by_exit_code(normalized_rows),
        "exit_code_summary_missing_examples": _summary_missing_examples_by_exit_code(normalized_rows),
        "status_counts": status_counts,
        "status_duration_ms": status_duration_ms,
        "status_average_duration_ms": _duration_averages_by_status(normalized_rows),
        "status_duration_extremes_ms": _duration_extremes_by_status(normalized_rows),
        "status_duration_coverage": _duration_coverage_by_field(normalized_rows, "status"),
        "status_duration_share": _duration_shares_by_status(status_duration_ms, total_duration_ms),
        "dominant_duration_status": _dominant_duration_status(status_duration_ms, total_duration_ms),
        "duration_source_counts": _duration_source_counts(normalized_rows),
        "duration_source_duration_ms": duration_source_duration_ms,
        "duration_source_average_ms": _duration_averages_by_source(normalized_rows),
        "duration_source_extremes_ms": _duration_extremes_by_source(normalized_rows),
        "duration_source_share": _duration_shares(duration_source_duration_ms, total_duration_ms),
        "duration_recorded_count": duration_coverage["duration_recorded_count"],
        "duration_missing_count": duration_coverage["duration_missing_count"],
        "duration_coverage_ratio": duration_coverage["duration_coverage_ratio"],
        "summary_recorded_count": summary_coverage["summary_recorded_count"],
        "summary_missing_count": summary_coverage["summary_missing_count"],
        "summary_coverage_ratio": summary_coverage["summary_coverage_ratio"],
        "summary_source_counts": _summary_source_counts(normalized_rows),
        "summary_examples": _summary_example_rows(normalized_rows, "command"),
        "summary_missing_examples": _summary_missing_example_rows(normalized_rows, "command"),
        "command_summary_examples": _summary_examples_by_field(normalized_rows, "command", "command"),
        "command_summary_missing_examples": _summary_missing_examples_by_field(normalized_rows, "command", "command"),
        "cwd_summary_examples": _summary_examples_by_field(normalized_rows, "cwd", "command"),
        "cwd_summary_missing_examples": _summary_missing_examples_by_field(normalized_rows, "cwd", "command"),
        "status_summary_examples": _summary_examples_by_field(normalized_rows, "status", "command"),
        "status_summary_missing_examples": _summary_missing_examples_by_field(normalized_rows, "status", "command"),
        "duration_source_summary_examples": _summary_examples_by_field(normalized_rows, "duration_source", "command"),
        "duration_source_summary_missing_examples": _summary_missing_examples_by_field(normalized_rows, "duration_source", "command"),
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


def _slowest_edit_row(rows):
    slowest = None
    for row in rows:
        if slowest is None or _numeric_value(row.get("duration_ms")) > _numeric_value(slowest.get("duration_ms")):
            slowest = row
    return slowest


def _first_edit_row(rows):
    return rows[0] if rows else None


def _last_edit_row(rows):
    return rows[-1] if rows else None


def _edit_summary_highlight_row(row):
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
    if row.get("summary"):
        summary["summary"] = row["summary"]
        if row.get("summary_source"):
            summary["summary_source"] = row["summary_source"]
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
        group_rows = summary.pop("_rows")
        summary["average_duration_ms"] = round(summary["total_duration_ms"] / summary["count"], 2)
        _add_duration_spread(summary, group_rows)
        summary["time_window"] = _time_window(group_rows)
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
        group_rows = summary.pop("_rows")
        summary["average_duration_ms"] = round(summary["total_duration_ms"] / summary["count"], 2)
        _add_duration_spread(summary, group_rows)
        summary["time_window"] = _time_window(group_rows)
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
    slowest_edit = _slowest_edit_row(normalized_rows)
    shortest_edit = _shortest_edit_row(normalized_rows)
    duration_coverage = _duration_coverage(normalized_rows)
    summary_coverage = _summary_coverage(normalized_rows)
    kind_duration_ms = _duration_totals_by_field(normalized_rows, "kind")
    status_duration_ms = _duration_totals_by_status(normalized_rows)
    duration_source_duration_ms = _duration_totals_by_source(normalized_rows)
    return {
        "count": len(normalized_rows),
        "files_changed": files,
        "files_changed_count": len(files),
        "file_change_totals": _file_change_total_rows(normalized_rows),
        "failed_count": sum(1 for row in normalized_rows if _is_failed_edit(row)),
        "failed_edits": _failed_edit_rows(normalized_rows),
        "kind_counts": _value_counts(normalized_rows, "kind", missing_label="unknown"),
        "kind_duration_ms": kind_duration_ms,
        "kind_average_duration_ms": _duration_averages_by_field(normalized_rows, "kind"),
        "kind_duration_extremes_ms": _duration_extremes_by_field(normalized_rows, "kind"),
        "kind_duration_coverage": _duration_coverage_by_field(normalized_rows, "kind"),
        "kind_duration_share": _duration_shares(kind_duration_ms, total_duration_ms),
        "dominant_duration_kind": _dominant_duration_kind(kind_duration_ms, total_duration_ms),
        "kind_totals": _edit_kind_total_rows(normalized_rows),
        "status_counts": status_counts,
        "status_duration_ms": status_duration_ms,
        "status_average_duration_ms": _duration_averages_by_status(normalized_rows),
        "status_duration_extremes_ms": _duration_extremes_by_status(normalized_rows),
        "status_duration_coverage": _duration_coverage_by_field(normalized_rows, "status"),
        "status_duration_share": _duration_shares_by_status(status_duration_ms, total_duration_ms),
        "dominant_duration_status": _dominant_duration_status(status_duration_ms, total_duration_ms),
        "duration_source_counts": _duration_source_counts(normalized_rows),
        "duration_source_duration_ms": duration_source_duration_ms,
        "duration_source_average_ms": _duration_averages_by_source(normalized_rows),
        "duration_source_extremes_ms": _duration_extremes_by_source(normalized_rows),
        "duration_source_share": _duration_shares(duration_source_duration_ms, total_duration_ms),
        "duration_recorded_count": duration_coverage["duration_recorded_count"],
        "duration_missing_count": duration_coverage["duration_missing_count"],
        "duration_coverage_ratio": duration_coverage["duration_coverage_ratio"],
        "summary_recorded_count": summary_coverage["summary_recorded_count"],
        "summary_missing_count": summary_coverage["summary_missing_count"],
        "summary_coverage_ratio": summary_coverage["summary_coverage_ratio"],
        "summary_source_counts": _summary_source_counts(normalized_rows),
        "summary_examples": _summary_example_rows(normalized_rows, "file_edit"),
        "summary_missing_examples": _summary_missing_example_rows(normalized_rows, "file_edit"),
        "path_summary_examples": _summary_examples_by_field(normalized_rows, "path", "file_edit"),
        "path_summary_missing_examples": _summary_missing_examples_by_field(normalized_rows, "path", "file_edit"),
        "kind_summary_examples": _summary_examples_by_field(normalized_rows, "kind", "file_edit"),
        "kind_summary_missing_examples": _summary_missing_examples_by_field(normalized_rows, "kind", "file_edit"),
        "status_summary_examples": _summary_examples_by_field(normalized_rows, "status", "file_edit"),
        "status_summary_missing_examples": _summary_missing_examples_by_field(normalized_rows, "status", "file_edit"),
        "duration_source_summary_examples": _summary_examples_by_field(normalized_rows, "duration_source", "file_edit"),
        "duration_source_summary_missing_examples": _summary_missing_examples_by_field(normalized_rows, "duration_source", "file_edit"),
        "time_window": _time_window(normalized_rows),
        "total_added_lines": total_added_lines,
        "total_removed_lines": total_removed_lines,
        "net_line_delta": total_added_lines - total_removed_lines,
        "total_duration_ms": total_duration_ms,
        "average_duration_ms": 0 if not normalized_rows else round(total_duration_ms / len(normalized_rows), 2),
        "average_recorded_duration_ms": _average_recorded_duration_ms(normalized_rows),
        "median_duration_ms": _median_duration_ms(normalized_rows),
        "duration_range_ms": _duration_range_ms(normalized_rows),
        "duration_extremes_ms": _duration_extremes_ms(normalized_rows),
        "first_edit": _edit_summary_highlight_row(_first_edit_row(normalized_rows)),
        "largest_edit": _edit_summary_highlight_row(largest_edit),
        "slowest_edit": _edit_summary_highlight_row(slowest_edit),
        "shortest_edit": _edit_summary_highlight_row(shortest_edit),
        "last_edit": _edit_summary_highlight_row(_last_edit_row(normalized_rows)),
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
        command_summary = normalized_row.get("command_summary")
        if not normalized_row.get("summary") and command_summary:
            normalized_row["summary"] = command_summary
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
    report_summary_coverage = {
        "command_by_duration_source": _summary_coverage_by_field(command_timing, "duration_source"),
        "command_by_status": _summary_coverage_by_field(command_timing, "status"),
        "command_by_command": _summary_coverage_by_field(command_timing, "command"),
        "command_by_cwd": _summary_coverage_by_field(command_timing, "cwd"),
        "command_by_exit_code": _summary_coverage_by_exit_code(command_timing),
        "edit_by_duration_source": _summary_coverage_by_field(edit_summary, "duration_source"),
        "edit_by_status": _summary_coverage_by_field(edit_summary, "status"),
        "edit_by_kind": _summary_coverage_by_field(edit_summary, "kind"),
        "edit_by_path": _summary_coverage_by_field(edit_summary, "path"),
        "activity_by_type": _summary_coverage_by_field(activity_timeline, "type"),
        "activity_by_status": _summary_coverage_by_field(activity_timeline, "status"),
        "activity_by_duration_source": _summary_coverage_by_field(activity_timeline, "duration_source"),
        "activity_by_identity": _summary_coverage_by_activity_identity(activity_timeline),
    }
    report_summary_duration_impact = {
        "command": _summary_duration_metrics(command_timing),
        "edit": _summary_duration_metrics(edit_summary),
        "activity": _summary_duration_metrics(activity_timeline),
    }
    report_summary_source_counts = {
        "command": _summary_source_counts(command_timing),
        "command_by_duration_source": _summary_source_counts_by_field(command_timing, "duration_source"),
        "command_by_status": _summary_source_counts_by_field(command_timing, "status"),
        "command_by_command": _summary_source_counts_by_field(command_timing, "command"),
        "command_by_cwd": _summary_source_counts_by_field(command_timing, "cwd"),
        "command_by_exit_code": _summary_source_counts_by_exit_code(command_timing),
        "edit": _summary_source_counts(edit_summary),
        "edit_by_duration_source": _summary_source_counts_by_field(edit_summary, "duration_source"),
        "edit_by_status": _summary_source_counts_by_field(edit_summary, "status"),
        "edit_by_kind": _summary_source_counts_by_field(edit_summary, "kind"),
        "edit_by_path": _summary_source_counts_by_field(edit_summary, "path"),
        "activity": _summary_source_counts(activity_timeline),
        "activity_by_type": _summary_source_counts_by_field(activity_timeline, "type"),
        "activity_by_status": _summary_source_counts_by_field(activity_timeline, "status"),
        "activity_by_duration_source": _summary_source_counts_by_field(activity_timeline, "duration_source"),
        "activity_by_identity": _summary_source_counts_by_activity_identity(activity_timeline),
    }
    report_summary_timing_window_impact = {
        "command": _summary_timing_window_metrics(command_timing),
        "edit": _summary_timing_window_metrics(edit_summary),
        "activity": _summary_timing_window_metrics(activity_timeline),
    }
    report_timing_window_coverage = {
        "command": _timing_window_metrics(command_timing),
        "edit": _timing_window_metrics(edit_summary),
        "activity": _timing_window_metrics(activity_timeline),
    }
    return {
        "task": metadata["task"],
        "run_id": metadata["run_id"],
        "status": metadata["status"],
        "timing": metadata["timing"],
        "summary": summary,
        "run_summary": run_summary,
        "failure_summary": build_failure_summary(trace),
        "report_inspection_targets": build_report_inspection_targets(command_timing, edit_summary, activity_timeline),
        "report_summary_coverage": report_summary_coverage,
        "report_summary_duration_impact": report_summary_duration_impact,
        "report_summary_timing_window_impact": report_summary_timing_window_impact,
        "report_summary_source_counts": report_summary_source_counts,
        "report_timing_window_coverage": report_timing_window_coverage,
        "command_timing_summary": build_command_timing_summary(command_timing),
        "activity_timeline_summary": build_activity_timeline_summary(activity_timeline),
        "activity_timeline": activity_timeline,
        "command_timing": command_timing,
        "edit_summary_totals": build_edit_summary_totals(edit_summary),
        "edit_summary": edit_summary,
    }
