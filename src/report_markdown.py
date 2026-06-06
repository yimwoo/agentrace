from src.report_json import build_json_summary


def _format_artifacts(row):
    artifacts = row.get("artifacts") or []
    if not artifacts:
        return ""
    refs = "; ".join(f"{artifact['kind']}={artifact['path']}" for artifact in artifacts)
    return f", artifacts: {refs}"


def _format_artifact_details(row):
    artifacts = row.get("artifacts") or []
    if not artifacts:
        return ""
    refs = "; ".join(f"{artifact['kind']}={artifact['path']}" for artifact in artifacts)
    return f"artifacts={refs}"


def _format_time_window(row):
    parts = []
    if row.get("started_at"):
        parts.append(f"started_at={row['started_at']}")
    if row.get("ended_at"):
        parts.append(f"ended_at={row['ended_at']}")
    return f", {', '.join(parts)}" if parts else ""


def _format_duration_source(row):
    source = row.get("duration_source")
    if not source and "duration_ms" in row:
        source = "explicit"
    if not source:
        return ""
    return f", duration_source={source}"


def _format_command_highlight(row):
    if not row:
        return "none"
    event = row.get("event") or "summary"
    command = row.get("command") or "<unknown command>"
    duration = row.get("duration_ms", 0)
    status = row.get("status") or "unknown"
    exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
    duration_source = _format_duration_source(row).removeprefix(", ")
    timing = _format_time_window(row).removeprefix(", ")
    details = [f"{duration}ms", f"status={status}", f"exit_code={exit_code}"]
    if duration_source:
        details.append(duration_source)
    if timing:
        details.append(timing)
    if row.get("cwd"):
        details.append(f"cwd={row['cwd']}")
    if row.get("summary"):
        details.append(f"summary={row['summary']}")
        if row.get("summary_source"):
            details.append(f"summary_source={row['summary_source']}")
    artifact_details = _format_artifact_details(row)
    if artifact_details:
        details.append(artifact_details)
    return f"{event}: `{command}` ({', '.join(details)})"


def _format_slowest_command(slowest):
    return _format_command_highlight(slowest)


def _format_fastest_command(fastest):
    return _format_command_highlight(fastest)


def _format_changed_files(files):
    if not files:
        return "none"
    return ", ".join(files)


def _format_repeated_commands(repeated_commands):
    if not repeated_commands:
        return "none"
    return ", ".join(f"`{command}`={count}" for command, count in sorted(repeated_commands.items()))


def _format_command_attempts(command_attempts):
    if not command_attempts:
        return "none"
    lines = []
    for row in command_attempts:
        details = [
            f"count={row.get('count', 0)}",
            f"total_duration_ms={row.get('total_duration_ms', 0)}",
            f"average_duration_ms={row.get('average_duration_ms', 0)}",
            f"failed_count={row.get('failed_count', 0)}",
            f"statuses={_format_status_counts(row.get('status_counts'))}",
        ]
        _append_duration_spread_details(details, row)
        details.append(f"duration_sources={_format_status_counts(row.get('duration_source_counts'))}")
        time_window = _format_aggregate_time_window(row.get("time_window"))
        if time_window != "none":
            details.append(f"time_window={time_window}")
        if row.get("first_event"):
            details.append(f"first_event={row['first_event']}")
        if row.get("last_event"):
            details.append(f"last_event={row['last_event']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"`{row.get('command') or '<unknown command>'}` ({', '.join(details)})")
    return "; ".join(lines)


def _append_duration_spread_details(details, row):
    """Render nested aggregate spread metrics when the JSON row includes them."""
    if "median_duration_ms" not in row:
        return
    details.extend([
        f"median_duration_ms={row.get('median_duration_ms', 0)}",
        f"duration_range_ms={row.get('duration_range_ms', 0)}",
        f"duration_extremes_ms={_format_duration_extremes(row.get('duration_extremes_ms'))}",
        f"duration_recorded_count={row.get('duration_recorded_count', 0)}",
        f"duration_missing_count={row.get('duration_missing_count', 0)}",
        f"duration_coverage_ratio={row.get('duration_coverage_ratio', 0)}",
        f"summary_recorded_count={row.get('summary_recorded_count', 0)}",
        f"summary_missing_count={row.get('summary_missing_count', 0)}",
        f"summary_coverage_ratio={row.get('summary_coverage_ratio', 0)}",
        f"summary_source_counts={_format_status_counts(row.get('summary_source_counts'))}",
        f"summary_examples={_format_summary_examples(row.get('summary_examples'))}",
        f"summary_missing_examples={_format_summary_missing_examples(row.get('summary_missing_examples'))}",
        f"status_duration_ms={_format_status_counts(row.get('status_duration_ms'))}",
        f"status_average_duration_ms={_format_status_counts(row.get('status_average_duration_ms'))}",
        f"status_duration_extremes_ms={_format_duration_source_extremes(row.get('status_duration_extremes_ms'))}",
        f"status_duration_coverage={_format_duration_coverage_by_label(row.get('status_duration_coverage'))}",
        f"status_duration_share={_format_status_counts(row.get('status_duration_share'))}",
        f"dominant_duration_status={_format_dominant_duration_status(row.get('dominant_duration_status'))}",
        f"duration_source_duration_ms={_format_status_counts(row.get('duration_source_duration_ms'))}",
        f"duration_source_average_ms={_format_status_counts(row.get('duration_source_average_ms'))}",
        f"duration_source_extremes_ms={_format_duration_source_extremes(row.get('duration_source_extremes_ms'))}",
        f"duration_source_share={_format_status_counts(row.get('duration_source_share'))}",
    ])


def _format_file_change_totals(file_change_totals):
    if not file_change_totals:
        return "none"
    lines = []
    for row in file_change_totals:
        path = row.get("path") or "<unknown file>"
        details = [
            f"count={row.get('count', 0)}",
            f"failed_count={row.get('failed_count', 0)}",
            f"+{row.get('total_added_lines', 0)}/-{row.get('total_removed_lines', 0)}",
            f"net={row.get('net_line_delta', 0)}",
            f"total_duration_ms={row.get('total_duration_ms', 0)}",
            f"average_duration_ms={row.get('average_duration_ms', 0)}",
            f"statuses={_format_status_counts(row.get('status_counts'))}",
            f"kinds={_format_status_counts(row.get('kind_counts'))}",
            f"duration_sources={_format_status_counts(row.get('duration_source_counts'))}",
        ]
        _append_duration_spread_details(details, row)
        time_window = _format_aggregate_time_window(row.get("time_window"))
        if time_window != "none":
            details.append(f"time_window={time_window}")
        if row.get("first_event"):
            details.append(f"first_event={row['first_event']}")
        if row.get("last_event"):
            details.append(f"last_event={row['last_event']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{path} ({', '.join(details)})")
    return "; ".join(lines)



def _format_command_cwd_totals(cwd_totals):
    if not cwd_totals:
        return "none"
    lines = []
    for row in cwd_totals:
        cwd = row.get("cwd") or "unknown"
        details = [
            f"count={row.get('count', 0)}",
            f"commands={_format_changed_files(row.get('commands_run'))}",
            f"failed_count={row.get('failed_count', 0)}",
            f"total_duration_ms={row.get('total_duration_ms', 0)}",
            f"average_duration_ms={row.get('average_duration_ms', 0)}",
            f"statuses={_format_status_counts(row.get('status_counts'))}",
            f"duration_sources={_format_status_counts(row.get('duration_source_counts'))}",
        ]
        _append_duration_spread_details(details, row)
        time_window = _format_aggregate_time_window(row.get("time_window"))
        if time_window != "none":
            details.append(f"time_window={time_window}")
        if row.get("first_event"):
            details.append(f"first_event={row['first_event']}")
        if row.get("last_event"):
            details.append(f"last_event={row['last_event']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{cwd} ({', '.join(details)})")
    return "; ".join(lines)


def _format_edit_kind_totals(kind_totals):
    if not kind_totals:
        return "none"
    lines = []
    for row in kind_totals:
        kind = row.get("kind") or "unknown"
        details = [
            f"count={row.get('count', 0)}",
            f"files={_format_changed_files(row.get('files_changed'))}",
            f"failed_count={row.get('failed_count', 0)}",
            f"+{row.get('total_added_lines', 0)}/-{row.get('total_removed_lines', 0)}",
            f"net={row.get('net_line_delta', 0)}",
            f"total_duration_ms={row.get('total_duration_ms', 0)}",
            f"average_duration_ms={row.get('average_duration_ms', 0)}",
            f"statuses={_format_status_counts(row.get('status_counts'))}",
            f"duration_sources={_format_status_counts(row.get('duration_source_counts'))}",
        ]
        _append_duration_spread_details(details, row)
        time_window = _format_aggregate_time_window(row.get("time_window"))
        if time_window != "none":
            details.append(f"time_window={time_window}")
        if row.get("first_event"):
            details.append(f"first_event={row['first_event']}")
        if row.get("last_event"):
            details.append(f"last_event={row['last_event']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{kind} ({', '.join(details)})")
    return "; ".join(lines)

def _format_failed_commands(failed_commands):
    if not failed_commands:
        return "none"
    lines = []
    for row in failed_commands:
        event = row.get("event") or "summary"
        command = row.get("command") or "<unknown command>"
        duration = row.get("duration_ms", 0)
        status = row.get("status") or "unknown"
        exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
        duration_source = _format_duration_source(row).removeprefix(", ")
        timing = _format_time_window(row).removeprefix(", ")
        details = [f"{duration}ms", f"status={status}", f"exit_code={exit_code}"]
        if duration_source:
            details.append(duration_source)
        if timing:
            details.append(timing)
        if row.get("cwd"):
            details.append(f"cwd={row['cwd']}")
        if row.get("stdout_preview"):
            details.append(f"stdout_preview={row['stdout_preview']}")
        if row.get("stderr_preview"):
            details.append(f"stderr_preview={row['stderr_preview']}")
        if row.get("summary"):
            details.append(f"summary={row['summary']}")
            if row.get("summary_source"):
                details.append(f"summary_source={row['summary_source']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{event}: `{command}` ({', '.join(details)})")
    return "; ".join(lines)


def _format_failed_edits(failed_edits):
    if not failed_edits:
        return "none"
    lines = []
    for row in failed_edits:
        event = row.get("event") or "summary"
        path = row.get("path") or "<unknown file>"
        kind = row.get("kind") or "unknown"
        duration = row.get("duration_ms", 0)
        status = row.get("status") or "unknown"
        duration_source = _format_duration_source(row).removeprefix(", ")
        timing = _format_time_window(row).removeprefix(", ")
        added = row.get("added_lines", 0)
        removed = row.get("removed_lines", 0)
        net = row.get("net_line_delta", added - removed)
        details = [f"kind={kind}", f"+{added}/-{removed}", f"net={net}", f"{duration}ms", f"status={status}"]
        if duration_source:
            details.append(duration_source)
        if timing:
            details.append(timing)
        if row.get("summary"):
            details.append(f"summary={row['summary']}")
            if row.get("summary_source"):
                details.append(f"summary_source={row['summary_source']}")
        if row.get("error_message"):
            details.append(f"error_message={row['error_message']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{event}: {path} ({', '.join(details)})")
    return "; ".join(lines)


def _format_status_counts(status_counts):
    if not status_counts:
        return "none"
    return ", ".join(f"{status}={count}" for status, count in sorted(status_counts.items()))


def _format_summary_source_counts_by_label(counts_by_label):
    if not counts_by_label:
        return "none"
    return ", ".join(
        f"{label}={_format_status_counts(counts)}"
        for label, counts in sorted(counts_by_label.items())
    )


def _format_report_summary_source_counts(source_counts):
    if not source_counts:
        return "none"
    labels = [
        "command",
        "command_by_duration_source",
        "command_by_status",
        "command_by_command",
        "command_by_cwd",
        "command_by_exit_code",
        "edit",
        "edit_by_duration_source",
        "edit_by_status",
        "edit_by_kind",
        "edit_by_path",
        "activity",
        "activity_by_type",
        "activity_by_status",
        "activity_by_duration_source",
        "activity_by_identity",
    ]
    parts = []
    for label in labels:
        if label not in source_counts:
            continue
        value = source_counts.get(label)
        if label in {"command", "edit", "activity"}:
            parts.append(f"{label}={_format_status_counts(value)}")
        else:
            parts.append(f"{label}={_format_summary_source_counts_by_label(value)}")
    return "; ".join(parts) if parts else "none"


def _format_duration_extremes(extremes):
    if not extremes:
        return "none"
    return f"min={extremes.get('min', 0)}, max={extremes.get('max', 0)}"


def _format_duration_source_extremes(extremes_by_source):
    if not extremes_by_source:
        return "none"
    return ", ".join(
        f"{source}=min={extremes.get('min', 0)}/max={extremes.get('max', 0)}"
        for source, extremes in sorted(extremes_by_source.items())
    )


def _format_duration_coverage_by_label(coverage_by_label):
    if not coverage_by_label:
        return "none"
    return ", ".join(
        f"{label}=recorded={coverage.get('duration_recorded_count', 0)}/missing={coverage.get('duration_missing_count', 0)}/ratio={coverage.get('duration_coverage_ratio', 0)}"
        for label, coverage in sorted(coverage_by_label.items())
    )


def _format_summary_coverage_by_label(coverage_by_label):
    if not coverage_by_label:
        return "none"
    return ", ".join(
        f"{label}=recorded={coverage.get('summary_recorded_count', 0)}/missing={coverage.get('summary_missing_count', 0)}/ratio={coverage.get('summary_coverage_ratio', 0)}"
        for label, coverage in sorted(coverage_by_label.items())
    )


def _format_summary_examples_by_label(examples_by_label, formatter):
    if not examples_by_label:
        return "none"
    rendered = []
    for label, rows in sorted(examples_by_label.items()):
        examples = formatter(rows)
        if examples == "none":
            continue
        rendered.append(f"{label}={examples}")
    return "; ".join(rendered) if rendered else "none"



def _format_summary_examples(rows):
    if not rows:
        return "none"
    rendered = []
    for row in rows:
        summary = row.get("summary") or ""
        duration = row.get("duration_ms", 0)
        status = row.get("status") or "unknown"
        source = row.get("duration_source") or "unknown"
        if row.get("command"):
            label = f"`{row.get('command')}`"
            extras = []
            if row.get("cwd"):
                extras.append(f"cwd={row['cwd']}")
            if row.get("exit_code") is not None:
                extras.append(f"exit_code={row['exit_code']}")
        else:
            label = row.get("path") or "<unknown file>"
            extras = [f"kind={row.get('kind') or 'unknown'}"]
            if "net_line_delta" in row:
                extras.append(f"net={row.get('net_line_delta', 0)}")
        details = [f"event={row.get('event') or 'summary'}", f"status={status}", f"duration_ms={duration}", f"duration_source={source}"]
        details.extend(extras)
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        details.append(f"summary={summary}")
        rendered.append(f"{label} ({', '.join(details)})")
    return "; ".join(rendered)


def _format_summary_missing_examples(rows):
    if not rows:
        return "none"
    rendered = []
    for row in rows:
        duration = row.get("duration_ms", 0)
        status = row.get("status") or "unknown"
        source = row.get("duration_source") or "unknown"
        if row.get("command"):
            label = f"`{row.get('command')}`"
            extras = []
            if row.get("cwd"):
                extras.append(f"cwd={row['cwd']}")
            if row.get("exit_code") is not None:
                extras.append(f"exit_code={row['exit_code']}")
        else:
            label = row.get("path") or "<unknown file>"
            extras = [f"kind={row.get('kind') or 'unknown'}"]
            if "net_line_delta" in row:
                extras.append(f"net={row.get('net_line_delta', 0)}")
        details = [f"event={row.get('event') or 'summary'}", f"status={status}", f"duration_ms={duration}", f"duration_source={source}"]
        details.extend(extras)
        if row.get("timestamp_window_ms") is not None:
            details.append(f"timestamp_window_ms={row['timestamp_window_ms']}")
        if row.get("duration_window_delta_ms") is not None:
            details.append(f"duration_window_delta_ms={row['duration_window_delta_ms']}")
            details.append(f"duration_window_delta_abs_ms={row.get('duration_window_delta_abs_ms', abs(row['duration_window_delta_ms']))}")
        if row.get("summary"):
            details.append(f"summary={row['summary']}")
            if row.get("summary_source"):
                details.append(f"summary_source={row['summary_source']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        rendered.append(f"{label} ({', '.join(details)})")
    return "; ".join(rendered)



def _format_timing_window_example(example):
    if not example:
        return "none"
    return _format_summary_missing_examples([example])


def _format_timing_window_missing_examples(examples):
    if not examples:
        return "none"
    rendered = []
    for example in examples:
        missing = []
        if example.get("missing_started_at"):
            missing.append("started_at")
        if example.get("missing_ended_at"):
            missing.append("ended_at")
        suffix = f" missing={'+'.join(missing)}" if missing else ""
        rendered_example = _format_timing_window_example(example)
        rendered.append(f"{rendered_example}{suffix}")
    return " | ".join(rendered)


def _format_report_timing_direction_examples(examples_by_direction):
    if not examples_by_direction:
        return "none"
    rendered = []
    for direction in ["matches", "duration_exceeds_window", "window_exceeds_duration"]:
        examples = examples_by_direction.get(direction) or []
        rendered.append(f"{direction}={_format_timing_window_missing_examples(examples)}")
    return ", ".join(rendered)


def _format_partial_timing_window_examples(examples_by_bucket):
    if not examples_by_bucket:
        return "none"
    rendered = []
    for bucket in ["started_only", "ended_only", "missing_both"]:
        examples = examples_by_bucket.get(bucket) or []
        rendered.append(f"{bucket}={_format_timing_window_missing_examples(examples)}")
    return ", ".join(rendered)


def _format_report_timing_window_coverage(coverage):
    if not coverage:
        return "none"
    parts = []
    for label in ["command", "edit", "activity"]:
        row = coverage.get(label) or {}
        parts.append(
            f"{label}=rows={row.get('timing_row_count', 0)}/"
            f"started_at={row.get('started_at_count', 0)}/"
            f"ended_at={row.get('ended_at_count', 0)}/"
            f"started_only={row.get('started_only_count', 0)}/"
            f"ended_only={row.get('ended_only_count', 0)}/"
            f"missing_started_at={row.get('missing_started_at_count', 0)}/"
            f"missing_ended_at={row.get('missing_ended_at_count', 0)}/"
            f"complete_windows={row.get('complete_window_count', 0)}/"
            f"missing_windows={row.get('missing_window_count', 0)}/"
            f"complete_window_ratio={row.get('complete_window_ratio', 0)}/"
            f"complete_window_duration_ms={row.get('complete_window_duration_ms', 0)}/"
            f"complete_window_duration_share={row.get('complete_window_duration_share', 0)}/"
            f"missing_window_duration_ms={row.get('missing_window_duration_ms', 0)}/"
            f"missing_window_duration_share={row.get('missing_window_duration_share', 0)}/"
            f"partial_timestamp_window_duration_ms={_format_status_counts(row.get('partial_timestamp_window_duration_ms'))}/"
            f"timestamp_window_total_ms={row.get('timestamp_window_total_ms', 0)}/"
            f"timestamp_window_average_ms={row.get('timestamp_window_average_ms', 0)}/"
            f"timestamp_window_extremes_ms={row.get('timestamp_window_extremes_ms', {'min': 0, 'max': 0})}/"
            f"largest_timestamp_window_ms={row.get('largest_timestamp_window_ms', 0)}/"
            f"largest_timestamp_window_example={_format_timing_window_example(row.get('largest_timestamp_window_example'))}/"
            f"duration_window_comparable_count={row.get('duration_window_comparable_count', 0)}/"
            f"duration_window_delta_total_ms={row.get('duration_window_delta_total_ms', 0)}/"
            f"duration_window_delta_abs_total_ms={row.get('duration_window_delta_abs_total_ms', 0)}/"
            f"duration_window_delta_average_ms={row.get('duration_window_delta_average_ms', 0)}/"
            f"duration_window_delta_abs_average_ms={row.get('duration_window_delta_abs_average_ms', 0)}/"
            f"duration_window_delta_abs_recorded_duration_share={row.get('duration_window_delta_abs_recorded_duration_share', 0)}/"
            f"duration_window_delta_consistency_label={row.get('duration_window_delta_consistency_label', 'no_comparable_rows')}/"
            f"duration_window_delta_direction_counts={_format_status_counts(row.get('duration_window_delta_direction_counts'))}/"
            f"duration_window_delta_direction_examples={_format_report_timing_direction_examples(row.get('duration_window_delta_direction_examples'))}/"
            f"largest_duration_window_delta_ms={row.get('largest_duration_window_delta_ms', 0)}/"
            f"largest_duration_window_delta_example={_format_timing_window_example(row.get('largest_duration_window_delta_example'))}/"
            f"partial_timestamp_window_examples={_format_partial_timing_window_examples(row.get('partial_timestamp_window_examples'))}/"
            f"missing_timestamp_window_examples={_format_timing_window_missing_examples(row.get('missing_timestamp_window_examples'))}"
        )
    return "; ".join(parts)


def _format_report_inspection_targets(targets):
    if not targets:
        return "none"
    rendered = []
    for target in targets:
        details = [
            f"event={target.get('event') or 'summary'}",
            f"type={target.get('type') or 'unknown'}",
            f"reason={target.get('reason') or 'unknown'}",
            f"status={target.get('status') or 'unknown'}",
            f"duration_ms={target.get('duration_ms', 0)}",
            f"duration_source={target.get('duration_source') or 'unknown'}",
        ]
        if target.get("detail"):
            details.append(f"detail={target['detail']}")
        timing = _format_time_window(target).removeprefix(", ")
        if timing:
            details.append(timing)
        if target.get("cwd"):
            details.append(f"cwd={target['cwd']}")
        if target.get("exit_code") is not None:
            details.append(f"exit_code={target['exit_code']}")
        if target.get("kind"):
            details.append(f"kind={target['kind']}")
        if "net_line_delta" in target:
            details.append(f"net={target.get('net_line_delta', 0)}")
        if target.get("stderr_preview"):
            details.append(f"stderr_preview={target['stderr_preview']}")
        if target.get("error_message"):
            details.append(f"error_message={target['error_message']}")
        artifact_details = _format_artifact_details(target)
        if artifact_details:
            details.append(artifact_details)
        rendered.append(f"{target.get('identity') or 'unknown'} ({', '.join(details)})")
    return "; ".join(rendered)


def _format_report_summary_duration_examples(rows):
    if not rows:
        return "none"
    return _format_summary_missing_examples(rows)


def _format_report_summary_timing_window_impact(impact):
    if not impact:
        return "none"
    parts = []
    for label in ["command", "edit", "activity"]:
        row = impact.get(label) or {}
        parts.append(
            f"{label}=recorded_complete_windows={row.get('summary_recorded_complete_window_count', 0)}/"
            f"missing_complete_windows={row.get('summary_missing_complete_window_count', 0)}/"
            f"recorded_missing_windows={row.get('summary_recorded_missing_window_count', 0)}/"
            f"missing_missing_windows={row.get('summary_missing_missing_window_count', 0)}/"
            f"recorded_complete_window_duration_ms={row.get('summary_recorded_complete_window_duration_ms', 0)}/"
            f"missing_complete_window_duration_ms={row.get('summary_missing_complete_window_duration_ms', 0)}/"
            f"recorded_missing_window_duration_ms={row.get('summary_recorded_missing_window_duration_ms', 0)}/"
            f"missing_missing_window_duration_ms={row.get('summary_missing_missing_window_duration_ms', 0)}/"
            f"recorded_complete_window_share={row.get('summary_recorded_complete_window_share', 0)}/"
            f"missing_complete_window_share={row.get('summary_missing_complete_window_share', 0)}/"
            f"recorded_missing_window_share={row.get('summary_recorded_missing_window_share', 0)}/"
            f"missing_missing_window_share={row.get('summary_missing_missing_window_share', 0)}/"
            f"missing_window_share_delta={row.get('summary_missing_window_share_delta', 0)}/"
            f"recorded_complete_window_duration_share={row.get('summary_recorded_complete_window_duration_share', 0)}/"
            f"missing_complete_window_duration_share={row.get('summary_missing_complete_window_duration_share', 0)}/"
            f"recorded_missing_window_duration_share={row.get('summary_recorded_missing_window_duration_share', 0)}/"
            f"missing_missing_window_duration_share={row.get('summary_missing_missing_window_duration_share', 0)}/"
            f"missing_window_duration_share_delta={row.get('summary_missing_window_duration_share_delta', 0)}"
        )
    return "; ".join(parts)


def _format_report_summary_duration_impact(impact):
    if not impact:
        return "none"
    parts = []
    for label in ["command", "edit", "activity"]:
        row = impact.get(label) or {}
        examples = _format_report_summary_duration_examples(row.get("summary_missing_duration_examples"))
        recorded_examples = _format_report_summary_duration_examples(row.get("summary_recorded_duration_examples"))
        parts.append(
            f"{label}=recorded_duration_count={row.get('summary_recorded_duration_count', 0)}/"
            f"missing_duration_count={row.get('summary_missing_duration_count', 0)}/"
            f"total_duration_count={row.get('summary_total_duration_count', 0)}/"
            f"recorded_count_share={row.get('summary_recorded_count_share', 0)}/"
            f"missing_count_share={row.get('summary_missing_count_share', 0)}/"
            f"total_duration_ms={row.get('summary_total_duration_ms', 0)}/"
            f"recorded_duration_ms={row.get('summary_recorded_duration_ms', 0)}/"
            f"recorded_duration_share={row.get('summary_recorded_duration_share', 0)}/"
            f"recorded_average_duration_ms={row.get('summary_recorded_average_duration_ms', 0)}/"
            f"recorded_median_duration_ms={row.get('summary_recorded_median_duration_ms', 0)}/"
            f"recorded_duration_range_ms={row.get('summary_recorded_duration_range_ms', 0)}/"
            f"recorded_duration_extremes_ms={row.get('summary_recorded_duration_extremes_ms', {'min': 0, 'max': 0})}/"
            f"recorded_duration_source_counts={_format_status_counts(row.get('summary_recorded_duration_source_counts'))}/"
            f"recorded_duration_source_duration_ms={_format_status_counts(row.get('summary_recorded_duration_source_duration_ms'))}/"
            f"recorded_duration_source_share={_format_status_counts(row.get('summary_recorded_duration_source_share'))}/"
            f"largest_recorded_duration_ms={row.get('summary_largest_recorded_duration_ms', 0)}/"
            f"largest_recorded_duration_share={row.get('summary_largest_recorded_duration_share', 0)}/"
            f"largest_recorded_total_duration_share={row.get('summary_largest_recorded_total_duration_share', 0)}/"
            f"recorded_duration_examples={recorded_examples}/"
            f"missing_duration_ms={row.get('summary_missing_duration_ms', 0)}/"
            f"missing_average_duration_ms={row.get('summary_missing_average_duration_ms', 0)}/"
            f"missing_median_duration_ms={row.get('summary_missing_median_duration_ms', 0)}/"
            f"missing_duration_range_ms={row.get('summary_missing_duration_range_ms', 0)}/"
            f"missing_duration_extremes_ms={row.get('summary_missing_duration_extremes_ms', {'min': 0, 'max': 0})}/"
            f"missing_duration_source_counts={_format_status_counts(row.get('summary_missing_duration_source_counts'))}/"
            f"missing_duration_source_duration_ms={_format_status_counts(row.get('summary_missing_duration_source_duration_ms'))}/"
            f"missing_duration_source_share={_format_status_counts(row.get('summary_missing_duration_source_share'))}/"
            f"missing_duration_status_counts={_format_status_counts(row.get('summary_missing_duration_status_counts'))}/"
            f"missing_duration_status_duration_ms={_format_status_counts(row.get('summary_missing_duration_status_duration_ms'))}/"
            f"missing_duration_status_share={_format_status_counts(row.get('summary_missing_duration_status_share'))}/"
            f"missing_duration_share={row.get('summary_missing_duration_share', 0)}/"
            f"missing_recorded_duration_delta_ms={row.get('summary_missing_recorded_duration_delta_ms', 0)}/"
            f"missing_recorded_duration_delta_share={row.get('summary_missing_recorded_duration_delta_share', 0)}/"
            f"missing_recorded_duration_ratio={row.get('summary_missing_recorded_duration_ratio', 0)}/"
            f"missing_recorded_excess_duration_ms={row.get('summary_missing_recorded_excess_duration_ms', 0)}/"
            f"duration_balance={row.get('summary_duration_balance', 'none')}/"
            f"missing_duration_attention={row.get('summary_missing_duration_attention', 'none')}/"
            f"missing_exceeds_recorded_duration={row.get('summary_missing_exceeds_recorded_duration', False)}/"
            f"missing_duration_concentration={row.get('summary_missing_duration_concentration', 'none')}/"
            f"largest_missing_duration_ms={row.get('summary_largest_missing_duration_ms', 0)}/"
            f"largest_missing_duration_share={row.get('summary_largest_missing_duration_share', 0)}/"
            f"largest_missing_total_duration_share={row.get('summary_largest_missing_total_duration_share', 0)}/"
            f"missing_duration_examples={examples}"
        )
    return "; ".join(parts)


def _format_report_summary_coverage(coverage):
    if not coverage:
        return "none"
    labels = [
        "command_by_duration_source",
        "command_by_status",
        "command_by_command",
        "command_by_cwd",
        "command_by_exit_code",
        "edit_by_duration_source",
        "edit_by_status",
        "edit_by_kind",
        "edit_by_path",
        "activity_by_type",
        "activity_by_status",
        "activity_by_duration_source",
        "activity_by_identity",
    ]
    parts = []
    for label in labels:
        if label in coverage:
            parts.append(f"{label}={_format_summary_coverage_by_label(coverage.get(label))}")
    return "; ".join(parts) if parts else "none"

def _format_aggregate_time_window(time_window):
    if not time_window:
        return "none"
    parts = []
    if time_window.get("started_at"):
        parts.append(f"started_at={time_window['started_at']}")
    if time_window.get("ended_at"):
        parts.append(f"ended_at={time_window['ended_at']}")
    return ", ".join(parts) if parts else "none"


def _format_edit_highlight(row):
    if not row:
        return "none"
    event = row.get("event") or "summary"
    path = row.get("path") or "<unknown file>"
    added = row.get("added_lines", 0)
    removed = row.get("removed_lines", 0)
    net = row.get("net_line_delta", 0)
    duration = row.get("duration_ms", 0)
    status = row.get("status") or "unknown"
    duration_source = _format_duration_source(row).removeprefix(", ")
    timing = _format_time_window(row).removeprefix(", ")
    details = [f"+{added}/-{removed}", f"net={net}", f"duration_ms={duration}", f"status={status}"]
    if duration_source:
        details.append(duration_source)
    if timing:
        details.append(timing)
    if row.get("summary"):
        details.append(f"summary={row['summary']}")
        if row.get("summary_source"):
            details.append(f"summary_source={row['summary_source']}")
    artifact_details = _format_artifact_details(row)
    if artifact_details:
        details.append(artifact_details)
    return f"{event}: {path} ({', '.join(details)})"


def _format_largest_edit(largest_edit):
    return _format_edit_highlight(largest_edit)


def _format_slowest_edit(slowest_edit):
    return _format_edit_highlight(slowest_edit)


def _format_shortest_edit(shortest_edit):
    return _format_edit_highlight(shortest_edit)


def _format_command_timing(rows):
    if not rows:
        return ["## Command Timing", "", "No command events recorded."]
    lines = ["## Command Timing", ""]
    for row in rows:
        command = row.get("command") or "<unknown command>"
        duration = row.get("duration_ms", 0)
        exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
        cwd = f", cwd={row['cwd']}" if row.get("cwd") else ""
        time_window = _format_time_window(row)
        duration_source = _format_duration_source(row)
        artifacts = _format_artifacts(row)
        output_context = ""
        if row.get("stdout_preview"):
            output_context += f", stdout_preview={row['stdout_preview']}"
        if row.get("stderr_preview"):
            output_context += f", stderr_preview={row['stderr_preview']}"
        event = row.get("event", "summary")
        command_summary = ""
        if row.get("summary"):
            command_summary = f", summary={row['summary']}"
            if row.get("summary_source"):
                command_summary += f", summary_source={row['summary_source']}"
        lines.append(f"- {event}: `{command}` — {duration}ms, status={row.get('status')}, exit_code={exit_code}{duration_source}{cwd}{time_window}{command_summary}{output_context}{artifacts}")
    return lines


def _format_edit_summary(rows):
    if not rows:
        return ["## Edit Summary", "", "No file edit events recorded."]
    lines = ["## Edit Summary", ""]
    for row in rows:
        added = 0 if row.get("added_lines") is None else row.get("added_lines", 0)
        removed = 0 if row.get("removed_lines") is None else row.get("removed_lines", 0)
        summary = row.get("summary") or "No edit summary recorded."
        status = f", status={row['status']}" if row.get("status") else ""
        duration = f", duration_ms={row['duration_ms']}" if "duration_ms" in row else ""
        net_delta = f", net={row['net_line_delta']}" if "net_line_delta" in row else ""
        duration_source = _format_duration_source(row)
        time_window = _format_time_window(row)
        error_context = f", error_message={row['error_message']}" if row.get("error_message") else ""
        artifacts = _format_artifacts(row)
        path = row.get("path") or "<unknown file>"
        kind = row.get("kind") or "unknown"
        summary_source = f", summary_source={row['summary_source']}" if row.get("summary_source") else ""
        lines.append(f"- {path}: {kind} (+{added}/-{removed}{net_delta}) — {summary}{summary_source}{status}{duration}{duration_source}{time_window}{error_context}{artifacts}")
    return lines




def _format_failed_activity(failed_activity):
    if not failed_activity:
        return "none"
    lines = []
    for row in failed_activity:
        event = row.get("event") or "summary"
        duration = row.get("duration_ms", 0)
        status = row.get("status") or "unknown"
        duration_source = _format_duration_source(row).removeprefix(", ")
        timing = _format_time_window(row).removeprefix(", ")
        details = [f"type={row.get('type') or 'unknown'}", f"{duration}ms", f"status={status}"]
        if duration_source:
            details.append(duration_source)
        if timing:
            details.append(timing)
        if row.get("type") == "command":
            identity = f"`{row.get('command') or '<unknown command>'}`"
            exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
            details.append(f"exit_code={exit_code}")
            if row.get("cwd"):
                details.append(f"cwd={row['cwd']}")
            if row.get("summary"):
                details.append(f"summary={row['summary']}")
                if row.get("summary_source"):
                    details.append(f"summary_source={row['summary_source']}")
            if row.get("stdout_preview"):
                details.append(f"stdout_preview={row['stdout_preview']}")
            if row.get("stderr_preview"):
                details.append(f"stderr_preview={row['stderr_preview']}")
        else:
            identity = row.get("path") or "<unknown file>"
            kind = row.get("kind") or "unknown"
            added = row.get("added_lines", 0)
            removed = row.get("removed_lines", 0)
            net = row.get("net_line_delta", added - removed)
            details.extend([f"kind={kind}", f"+{added}/-{removed}", f"net={net}"])
            if row.get("summary"):
                details.append(f"summary={row['summary']}")
                if row.get("summary_source"):
                    details.append(f"summary_source={row['summary_source']}")
            if row.get("error_message"):
                details.append(f"error_message={row['error_message']}")
        artifact_details = _format_artifact_details(row)
        if artifact_details:
            details.append(artifact_details)
        lines.append(f"{event}: {identity} ({', '.join(details)})")
    return "; ".join(lines)


def _format_first_failed_activity(first_failed_activity):
    if not first_failed_activity:
        return "none"
    return _format_failed_activity([first_failed_activity])


def _format_first_activity(first_activity):
    if not first_activity:
        return "none"
    return _format_failed_activity([first_activity])


def _format_slowest_activity(slowest_activity):
    if not slowest_activity:
        return "none"
    return _format_failed_activity([slowest_activity])


def _format_fastest_activity(fastest_activity):
    if not fastest_activity:
        return "none"
    return _format_failed_activity([fastest_activity])


def _format_last_activity(last_activity):
    if not last_activity:
        return "none"
    return _format_failed_activity([last_activity])


def _format_activity_gap(gap):
    if not gap:
        return "none"
    details = [
        f"from_event={gap.get('from_event') or 'unknown'}",
        f"to_event={gap.get('to_event') or 'unknown'}",
        f"gap_ms={gap.get('gap_ms', 0)}",
    ]
    if gap.get("from_ended_at"):
        details.append(f"from_ended_at={gap['from_ended_at']}")
    if gap.get("to_started_at"):
        details.append(f"to_started_at={gap['to_started_at']}")
    return "(" + ", ".join(details) + ")"


def _format_activity_overlap(overlap):
    if not overlap:
        return "none"
    details = [
        f"from_event={overlap.get('from_event') or 'unknown'}",
        f"to_event={overlap.get('to_event') or 'unknown'}",
        f"overlap_ms={overlap.get('overlap_ms', 0)}",
    ]
    if overlap.get("from_ended_at"):
        details.append(f"from_ended_at={overlap['from_ended_at']}")
    if overlap.get("to_started_at"):
        details.append(f"to_started_at={overlap['to_started_at']}")
    return "(" + ", ".join(details) + ")"


def _format_activity_covered_intervals(intervals):
    if not intervals:
        return "none"
    formatted = []
    for interval in intervals:
        details = [
            f"started_at={interval.get('started_at') or 'unknown'}",
            f"ended_at={interval.get('ended_at') or 'unknown'}",
            f"duration_ms={interval.get('duration_ms', 0)}",
        ]
        formatted.append("(" + ", ".join(details) + ")")
    return "; ".join(formatted)


def _format_activity_uncovered_intervals(intervals):
    if not intervals:
        return "none"
    formatted = []
    for interval in intervals:
        details = [
            f"started_at={interval.get('started_at') or 'unknown'}",
            f"ended_at={interval.get('ended_at') or 'unknown'}",
            f"duration_ms={interval.get('duration_ms', 0)}",
        ]
        formatted.append("(" + ", ".join(details) + ")")
    return "; ".join(formatted)


def _format_activity_uncovered_interval(interval):
    if not interval:
        return "none"
    return _format_activity_uncovered_intervals([interval])


def _format_dominant_duration_type(row):
    if not row:
        return "none"
    return f"{row.get('type') or 'unknown'} ({row.get('duration_ms', 0)}ms, share={row.get('duration_share', 0)})"


def _format_dominant_duration_cwd(row):
    if not row:
        return "none"
    return f"{row.get('cwd') or 'unknown'} ({row.get('duration_ms', 0)}ms, share={row.get('duration_share', 0)})"


def _format_dominant_duration_kind(row):
    if not row:
        return "none"
    return f"{row.get('kind') or 'unknown'} ({row.get('duration_ms', 0)}ms, share={row.get('duration_share', 0)})"


def _format_dominant_duration_status(row):
    if not row:
        return "none"
    return f"{row.get('status') or 'unknown'} ({row.get('duration_ms', 0)}ms, share={row.get('duration_share', 0)})"


def _format_dominant_duration_exit_code(row):
    if not row:
        return "none"
    exit_code = row.get("exit_code")
    label = "unknown" if exit_code is None else exit_code
    return f"{label} ({row.get('duration_ms', 0)}ms, share={row.get('duration_share', 0)})"


def _format_status_duration_summary(row):
    if not row:
        return "none"
    return ", ".join([
        f"status_duration_ms={_format_status_counts(row.get('status_duration_ms'))}",
        f"status_average_duration_ms={_format_status_counts(row.get('status_average_duration_ms'))}",
        f"status_duration_extremes_ms={_format_duration_source_extremes(row.get('status_duration_extremes_ms'))}",
        f"status_duration_coverage={_format_duration_coverage_by_label(row.get('status_duration_coverage'))}",
        f"status_duration_share={_format_status_counts(row.get('status_duration_share'))}",
        f"dominant_duration_status={_format_dominant_duration_status(row.get('dominant_duration_status'))}",
    ])


def _format_cwd_duration_summary(row):
    if not row:
        return "none"
    return ", ".join([
        f"cwd_duration_ms={_format_status_counts(row.get('cwd_duration_ms'))}",
        f"cwd_average_duration_ms={_format_status_counts(row.get('cwd_average_duration_ms'))}",
        f"cwd_duration_extremes_ms={_format_duration_source_extremes(row.get('cwd_duration_extremes_ms'))}",
        f"cwd_duration_coverage={_format_duration_coverage_by_label(row.get('cwd_duration_coverage'))}",
        f"cwd_duration_share={_format_status_counts(row.get('cwd_duration_share'))}",
        f"dominant_duration_cwd={_format_dominant_duration_cwd(row.get('dominant_duration_cwd'))}",
    ])


def _format_exit_code_duration_summary(row):
    if not row:
        return "none"
    return ", ".join([
        f"exit_code_duration_ms={_format_status_counts(row.get('exit_code_duration_ms'))}",
        f"exit_code_average_duration_ms={_format_status_counts(row.get('exit_code_average_duration_ms'))}",
        f"exit_code_duration_extremes_ms={_format_duration_source_extremes(row.get('exit_code_duration_extremes_ms'))}",
        f"exit_code_duration_coverage={_format_duration_coverage_by_label(row.get('exit_code_duration_coverage'))}",
        f"exit_code_duration_share={_format_status_counts(row.get('exit_code_duration_share'))}",
        f"dominant_duration_exit_code={_format_dominant_duration_exit_code(row.get('dominant_duration_exit_code'))}",
        f"exit_code_summary_coverage={_format_summary_coverage_by_label(row.get('exit_code_summary_coverage'))}",
        f"exit_code_summary_examples={_format_summary_examples_by_label(row.get('exit_code_summary_examples'), _format_summary_examples)}",
        f"exit_code_summary_missing_examples={_format_summary_examples_by_label(row.get('exit_code_summary_missing_examples'), _format_summary_missing_examples)}",
    ])


def _format_kind_duration_summary(row):
    if not row:
        return "none"
    return ", ".join([
        f"kind_duration_ms={_format_status_counts(row.get('kind_duration_ms'))}",
        f"kind_average_duration_ms={_format_status_counts(row.get('kind_average_duration_ms'))}",
        f"kind_duration_extremes_ms={_format_duration_source_extremes(row.get('kind_duration_extremes_ms'))}",
        f"kind_duration_coverage={_format_duration_coverage_by_label(row.get('kind_duration_coverage'))}",
        f"kind_duration_share={_format_status_counts(row.get('kind_duration_share'))}",
        f"dominant_duration_kind={_format_dominant_duration_kind(row.get('dominant_duration_kind'))}",
    ])


def _format_activity_timeline_summary(timeline_totals):
    if not timeline_totals:
        return "none"
    details = [
        f"count={timeline_totals.get('count', 0)}",
        f"types={_format_status_counts(timeline_totals.get('type_counts'))}",
        f"type_duration_ms={_format_status_counts(timeline_totals.get('type_duration_ms'))}",
        f"type_average_duration_ms={_format_status_counts(timeline_totals.get('type_average_duration_ms'))}",
        f"type_duration_extremes_ms={_format_duration_source_extremes(timeline_totals.get('type_duration_extremes_ms'))}",
        f"type_duration_coverage={_format_duration_coverage_by_label(timeline_totals.get('type_duration_coverage'))}",
        f"type_duration_share={_format_status_counts(timeline_totals.get('type_duration_share'))}",
        f"dominant_duration_type={_format_dominant_duration_type(timeline_totals.get('dominant_duration_type'))}",
        f"statuses={_format_status_counts(timeline_totals.get('status_counts'))}",
        f"status_duration_ms={_format_status_counts(timeline_totals.get('status_duration_ms'))}",
        f"status_average_duration_ms={_format_status_counts(timeline_totals.get('status_average_duration_ms'))}",
        f"status_duration_extremes_ms={_format_duration_source_extremes(timeline_totals.get('status_duration_extremes_ms'))}",
        f"status_duration_coverage={_format_duration_coverage_by_label(timeline_totals.get('status_duration_coverage'))}",
        f"status_duration_share={_format_status_counts(timeline_totals.get('status_duration_share'))}",
        f"dominant_duration_status={_format_dominant_duration_status(timeline_totals.get('dominant_duration_status'))}",
        f"duration_sources={_format_status_counts(timeline_totals.get('duration_source_counts'))}",
        f"duration_source_duration_ms={_format_status_counts(timeline_totals.get('duration_source_duration_ms'))}",
        f"duration_source_average_ms={_format_status_counts(timeline_totals.get('duration_source_average_ms'))}",
        f"duration_source_extremes_ms={_format_duration_source_extremes(timeline_totals.get('duration_source_extremes_ms'))}",
        f"duration_source_share={_format_status_counts(timeline_totals.get('duration_source_share'))}",
        f"duration_recorded_count={timeline_totals.get('duration_recorded_count', 0)}",
        f"duration_missing_count={timeline_totals.get('duration_missing_count', 0)}",
        f"duration_coverage_ratio={timeline_totals.get('duration_coverage_ratio', 0)}",
        f"summary_recorded_count={timeline_totals.get('summary_recorded_count', 0)}",
        f"summary_missing_count={timeline_totals.get('summary_missing_count', 0)}",
        f"summary_coverage_ratio={timeline_totals.get('summary_coverage_ratio', 0)}",
        f"summary_source_counts={_format_status_counts(timeline_totals.get('summary_source_counts'))}",
        f"summary_examples={_format_summary_examples(timeline_totals.get('summary_examples'))}",
        f"summary_missing_examples={_format_summary_missing_examples(timeline_totals.get('summary_missing_examples'))}",
        f"type_summary_examples={_format_summary_examples_by_label(timeline_totals.get('type_summary_examples'), _format_summary_examples)}",
        f"type_summary_missing_examples={_format_summary_examples_by_label(timeline_totals.get('type_summary_missing_examples'), _format_summary_missing_examples)}",
        f"status_summary_examples={_format_summary_examples_by_label(timeline_totals.get('status_summary_examples'), _format_summary_examples)}",
        f"status_summary_missing_examples={_format_summary_examples_by_label(timeline_totals.get('status_summary_missing_examples'), _format_summary_missing_examples)}",
        f"duration_source_summary_examples={_format_summary_examples_by_label(timeline_totals.get('duration_source_summary_examples'), _format_summary_examples)}",
        f"duration_source_summary_missing_examples={_format_summary_examples_by_label(timeline_totals.get('duration_source_summary_missing_examples'), _format_summary_missing_examples)}",
        f"identity_summary_examples={_format_summary_examples_by_label(timeline_totals.get('identity_summary_examples'), _format_summary_examples)}",
        f"identity_summary_missing_examples={_format_summary_examples_by_label(timeline_totals.get('identity_summary_missing_examples'), _format_summary_missing_examples)}",
        f"span_duration_ms={timeline_totals.get('span_duration_ms', 0)}",
        f"covered_duration_ms={timeline_totals.get('covered_duration_ms', 0)}",
        f"covered_intervals={_format_activity_covered_intervals(timeline_totals.get('covered_intervals'))}",
        f"uncovered_duration_ms={timeline_totals.get('uncovered_duration_ms', 0)}",
        f"uncovered_intervals={_format_activity_uncovered_intervals(timeline_totals.get('uncovered_intervals'))}",
        f"uncovered_interval_count={timeline_totals.get('uncovered_interval_count', 0)}",
        f"average_uncovered_interval_ms={timeline_totals.get('average_uncovered_interval_ms', 0)}",
        f"largest_uncovered_interval={_format_activity_uncovered_interval(timeline_totals.get('largest_uncovered_interval'))}",
        f"coverage_ratio={timeline_totals.get('coverage_ratio', 0)}",
        f"idle_ratio={timeline_totals.get('idle_ratio', 0)}",
        f"covered_interval_count={timeline_totals.get('covered_interval_count', 0)}",
        f"merged_covered_interval_count={timeline_totals.get('merged_covered_interval_count', 0)}",
        f"total_duration_ms={timeline_totals.get('total_duration_ms', 0)}",
        f"average_duration_ms={timeline_totals.get('average_duration_ms', 0)}",
        f"average_recorded_duration_ms={timeline_totals.get('average_recorded_duration_ms', 0)}",
        f"median_duration_ms={timeline_totals.get('median_duration_ms', 0)}",
        f"duration_range_ms={timeline_totals.get('duration_range_ms', 0)}",
        f"duration_extremes_ms={_format_duration_extremes(timeline_totals.get('duration_extremes_ms'))}",
        f"first_activity={_format_first_activity(timeline_totals.get('first_activity'))}",
        f"slowest_activity={_format_slowest_activity(timeline_totals.get('slowest_activity'))}",
        f"fastest_activity={_format_fastest_activity(timeline_totals.get('fastest_activity'))}",
        f"last_activity={_format_last_activity(timeline_totals.get('last_activity'))}",
        f"total_idle_gap_ms={timeline_totals.get('total_idle_gap_ms', 0)}",
        f"average_idle_gap_ms={timeline_totals.get('average_idle_gap_ms', 0)}",
        f"largest_idle_gap={_format_activity_gap(timeline_totals.get('largest_idle_gap'))}",
        f"total_overlap_ms={timeline_totals.get('total_overlap_ms', 0)}",
        f"average_overlap_ms={timeline_totals.get('average_overlap_ms', 0)}",
        f"overlap_ratio={timeline_totals.get('overlap_ratio', 0)}",
        f"largest_overlap={_format_activity_overlap(timeline_totals.get('largest_overlap'))}",
        f"failed_count={timeline_totals.get('failed_count', 0)}",
    ]
    time_window = _format_aggregate_time_window(timeline_totals.get("time_window"))
    if time_window != "none":
        details.append(f"time_window={time_window}")
    return ", ".join(details)


def _format_activity_timeline(rows):
    if not rows:
        return ["## Activity Timeline", "", "No command or file edit activity recorded."]
    lines = ["## Activity Timeline", ""]
    for row in rows:
        event = row.get("event") or "summary"
        duration = row.get("duration_ms", 0)
        duration_source = _format_duration_source(row)
        time_window = _format_time_window(row)
        artifacts = _format_artifacts(row)
        status = row.get("status") or "unknown"
        if row.get("type") == "command":
            command = row.get("command") or "<unknown command>"
            exit_code = "unknown" if row.get("exit_code") is None else row.get("exit_code")
            cwd = f", cwd={row['cwd']}" if row.get("cwd") else ""
            output_context = ""
            if row.get("stdout_preview"):
                output_context += f", stdout_preview={row['stdout_preview']}"
            if row.get("stderr_preview"):
                output_context += f", stderr_preview={row['stderr_preview']}"
            command_summary = ""
            if row.get("summary"):
                command_summary = f", summary={row['summary']}"
                if row.get("summary_source"):
                    command_summary += f", summary_source={row['summary_source']}"
            lines.append(f"- {event}: command `{command}` — {duration}ms, status={status}, exit_code={exit_code}{duration_source}{cwd}{time_window}{command_summary}{output_context}{artifacts}")
            continue

        path = row.get("path") or "<unknown file>"
        kind = row.get("kind") or "unknown"
        added = row.get("added_lines", 0)
        removed = row.get("removed_lines", 0)
        net = row.get("net_line_delta", added - removed)
        summary = row.get("summary") or "No edit summary recorded."
        summary_source = f", summary_source={row['summary_source']}" if row.get("summary_source") else ""
        error_context = f", error_message={row['error_message']}" if row.get("error_message") else ""
        lines.append(f"- {event}: edit {path} ({kind}, +{added}/-{removed}, net={net}) — {summary}{summary_source}, status={status}, duration_ms={duration}{duration_source}{time_window}{error_context}{artifacts}")
    return lines


def build_markdown_summary(trace):
    payload = build_json_summary(trace)
    command_totals = payload["command_timing_summary"]
    edit_totals = payload["edit_summary_totals"]
    timeline_totals = payload["activity_timeline_summary"]
    lines = [
        f"# Trace Summary: {payload['task']}",
        f"- run_id: {payload['run_id']}",
        f"- status: {payload['status']}",
        f"- event_count: {payload['summary']['event_count']}",
        f"- ok_events: {payload['summary']['ok_events']}",
        f"- total_duration_ms: {payload['summary']['total_duration_ms']}",
        f"- report_inspection_targets: {_format_report_inspection_targets(payload['report_inspection_targets'])}",
        f"- report_summary_coverage: {_format_report_summary_coverage(payload['report_summary_coverage'])}",
        f"- report_summary_duration_impact: {_format_report_summary_duration_impact(payload['report_summary_duration_impact'])}",
        f"- report_summary_timing_window_impact: {_format_report_summary_timing_window_impact(payload['report_summary_timing_window_impact'])}",
        f"- report_summary_source_counts: {_format_report_summary_source_counts(payload['report_summary_source_counts'])}",
        f"- report_timing_window_coverage: {_format_report_timing_window_coverage(payload['report_timing_window_coverage'])}",
        f"- command_count: {command_totals['count']}",
        f"- unique_command_count: {command_totals['unique_command_count']}",
        f"- commands_run: {_format_changed_files(command_totals['commands_run'])}",
        f"- repeated_commands: {_format_repeated_commands(command_totals['repeated_commands'])}",
        f"- command_attempts: {_format_command_attempts(command_totals['command_attempts'])}",
        f"- command_cwd_counts: {_format_status_counts(command_totals['cwd_counts'])}",
        f"- command_cwd_duration_summary: {_format_cwd_duration_summary(command_totals)}",
        f"- command_cwd_totals: {_format_command_cwd_totals(command_totals['cwd_totals'])}",
        f"- command_total_duration_ms: {command_totals['total_duration_ms']}",
        f"- command_average_duration_ms: {command_totals['average_duration_ms']}",
        f"- command_average_recorded_duration_ms: {command_totals['average_recorded_duration_ms']}",
        f"- command_median_duration_ms: {command_totals['median_duration_ms']}",
        f"- command_duration_range_ms: {command_totals['duration_range_ms']}",
        f"- command_duration_extremes_ms: {_format_duration_extremes(command_totals['duration_extremes_ms'])}",
        f"- command_failed_count: {command_totals['failed_count']}",
        f"- failed_commands: {_format_failed_commands(command_totals['failed_commands'])}",
        f"- command_exit_code_counts: {_format_status_counts(command_totals['exit_code_counts'])}",
        f"- command_exit_code_duration_summary: {_format_exit_code_duration_summary(command_totals)}",
        f"- command_status_counts: {_format_status_counts(command_totals['status_counts'])}",
        f"- command_status_duration_summary: {_format_status_duration_summary(command_totals)}",
        f"- command_duration_sources: {_format_status_counts(command_totals['duration_source_counts'])}",
        f"- command_duration_source_duration_ms: {_format_status_counts(command_totals['duration_source_duration_ms'])}",
        f"- command_duration_source_average_ms: {_format_status_counts(command_totals['duration_source_average_ms'])}",
        f"- command_duration_source_extremes_ms: {_format_duration_source_extremes(command_totals['duration_source_extremes_ms'])}",
        f"- command_duration_source_share: {_format_status_counts(command_totals['duration_source_share'])}",
        f"- command_duration_recorded_count: {command_totals['duration_recorded_count']}",
        f"- command_duration_missing_count: {command_totals['duration_missing_count']}",
        f"- command_duration_coverage_ratio: {command_totals['duration_coverage_ratio']}",
        f"- command_summary_recorded_count: {command_totals['summary_recorded_count']}",
        f"- command_summary_missing_count: {command_totals['summary_missing_count']}",
        f"- command_summary_coverage_ratio: {command_totals['summary_coverage_ratio']}",
        f"- command_summary_source_counts: {_format_status_counts(command_totals['summary_source_counts'])}",
        f"- command_summary_examples: {_format_summary_examples(command_totals['summary_examples'])}",
        f"- command_summary_missing_examples: {_format_summary_missing_examples(command_totals['summary_missing_examples'])}",
        f"- command_identity_summary_examples: {_format_summary_examples_by_label(command_totals.get('command_summary_examples'), _format_summary_examples)}",
        f"- command_identity_summary_missing_examples: {_format_summary_examples_by_label(command_totals.get('command_summary_missing_examples'), _format_summary_missing_examples)}",
        f"- command_cwd_summary_examples: {_format_summary_examples_by_label(command_totals.get('cwd_summary_examples'), _format_summary_examples)}",
        f"- command_cwd_summary_missing_examples: {_format_summary_examples_by_label(command_totals.get('cwd_summary_missing_examples'), _format_summary_missing_examples)}",
        f"- command_status_summary_examples: {_format_summary_examples_by_label(command_totals.get('status_summary_examples'), _format_summary_examples)}",
        f"- command_status_summary_missing_examples: {_format_summary_examples_by_label(command_totals.get('status_summary_missing_examples'), _format_summary_missing_examples)}",
        f"- command_duration_source_summary_examples: {_format_summary_examples_by_label(command_totals.get('duration_source_summary_examples'), _format_summary_examples)}",
        f"- command_duration_source_summary_missing_examples: {_format_summary_examples_by_label(command_totals.get('duration_source_summary_missing_examples'), _format_summary_missing_examples)}",
        f"- command_time_window: {_format_aggregate_time_window(command_totals['time_window'])}",
        f"- first_command: {_format_command_highlight(command_totals['first'])}",
        f"- slowest_command: {_format_slowest_command(command_totals['slowest'])}",
        f"- fastest_command: {_format_fastest_command(command_totals['fastest'])}",
        f"- last_command: {_format_command_highlight(command_totals['last'])}",
        f"- activity_timeline_summary: {_format_activity_timeline_summary(timeline_totals)}",
        f"- first_failed_activity: {_format_first_failed_activity(timeline_totals.get('first_failed_activity'))}",
        f"- failed_activity: {_format_failed_activity(timeline_totals.get('failed_activity'))}",
        f"- files_changed_count: {edit_totals['files_changed_count']}",
        f"- files_changed: {_format_changed_files(edit_totals['files_changed'])}",
        f"- file_change_totals: {_format_file_change_totals(edit_totals['file_change_totals'])}",
        f"- edit_failed_count: {edit_totals['failed_count']}",
        f"- failed_edits: {_format_failed_edits(edit_totals['failed_edits'])}",
        f"- edit_kind_counts: {_format_status_counts(edit_totals['kind_counts'])}",
        f"- edit_kind_duration_summary: {_format_kind_duration_summary(edit_totals)}",
        f"- edit_kind_totals: {_format_edit_kind_totals(edit_totals['kind_totals'])}",
        f"- edit_status_counts: {_format_status_counts(edit_totals['status_counts'])}",
        f"- edit_status_duration_summary: {_format_status_duration_summary(edit_totals)}",
        f"- edit_duration_sources: {_format_status_counts(edit_totals['duration_source_counts'])}",
        f"- edit_duration_source_duration_ms: {_format_status_counts(edit_totals['duration_source_duration_ms'])}",
        f"- edit_duration_source_average_ms: {_format_status_counts(edit_totals['duration_source_average_ms'])}",
        f"- edit_duration_source_extremes_ms: {_format_duration_source_extremes(edit_totals['duration_source_extremes_ms'])}",
        f"- edit_duration_source_share: {_format_status_counts(edit_totals['duration_source_share'])}",
        f"- edit_duration_recorded_count: {edit_totals['duration_recorded_count']}",
        f"- edit_duration_missing_count: {edit_totals['duration_missing_count']}",
        f"- edit_duration_coverage_ratio: {edit_totals['duration_coverage_ratio']}",
        f"- edit_summary_recorded_count: {edit_totals['summary_recorded_count']}",
        f"- edit_summary_missing_count: {edit_totals['summary_missing_count']}",
        f"- edit_summary_coverage_ratio: {edit_totals['summary_coverage_ratio']}",
        f"- edit_summary_source_counts: {_format_status_counts(edit_totals['summary_source_counts'])}",
        f"- edit_summary_examples: {_format_summary_examples(edit_totals['summary_examples'])}",
        f"- edit_summary_missing_examples: {_format_summary_missing_examples(edit_totals['summary_missing_examples'])}",
        f"- edit_path_summary_examples: {_format_summary_examples_by_label(edit_totals.get('path_summary_examples'), _format_summary_examples)}",
        f"- edit_path_summary_missing_examples: {_format_summary_examples_by_label(edit_totals.get('path_summary_missing_examples'), _format_summary_missing_examples)}",
        f"- edit_kind_summary_examples: {_format_summary_examples_by_label(edit_totals.get('kind_summary_examples'), _format_summary_examples)}",
        f"- edit_kind_summary_missing_examples: {_format_summary_examples_by_label(edit_totals.get('kind_summary_missing_examples'), _format_summary_missing_examples)}",
        f"- edit_status_summary_examples: {_format_summary_examples_by_label(edit_totals.get('status_summary_examples'), _format_summary_examples)}",
        f"- edit_status_summary_missing_examples: {_format_summary_examples_by_label(edit_totals.get('status_summary_missing_examples'), _format_summary_missing_examples)}",
        f"- edit_duration_source_summary_examples: {_format_summary_examples_by_label(edit_totals.get('duration_source_summary_examples'), _format_summary_examples)}",
        f"- edit_duration_source_summary_missing_examples: {_format_summary_examples_by_label(edit_totals.get('duration_source_summary_missing_examples'), _format_summary_missing_examples)}",
        f"- edit_time_window: {_format_aggregate_time_window(edit_totals['time_window'])}",
        f"- edit_total_lines: +{edit_totals['total_added_lines']}/-{edit_totals['total_removed_lines']}",
        f"- edit_net_line_delta: {edit_totals['net_line_delta']}",
        f"- edit_total_duration_ms: {edit_totals['total_duration_ms']}",
        f"- edit_average_duration_ms: {edit_totals['average_duration_ms']}",
        f"- edit_average_recorded_duration_ms: {edit_totals['average_recorded_duration_ms']}",
        f"- edit_median_duration_ms: {edit_totals['median_duration_ms']}",
        f"- edit_duration_range_ms: {edit_totals['duration_range_ms']}",
        f"- edit_duration_extremes_ms: {_format_duration_extremes(edit_totals['duration_extremes_ms'])}",
        f"- first_edit: {_format_edit_highlight(edit_totals['first_edit'])}",
        f"- largest_edit: {_format_largest_edit(edit_totals['largest_edit'])}",
        f"- slowest_edit: {_format_slowest_edit(edit_totals['slowest_edit'])}",
        f"- shortest_edit: {_format_shortest_edit(edit_totals['shortest_edit'])}",
        f"- last_edit: {_format_edit_highlight(edit_totals['last_edit'])}",
        "",
    ]
    lines.extend(_format_command_timing(payload["command_timing"]))
    lines.append("")
    lines.extend(_format_edit_summary(payload["edit_summary"]))
    lines.append("")
    lines.extend(_format_activity_timeline(payload["activity_timeline"]))
    return "\n".join(lines) + "\n"
