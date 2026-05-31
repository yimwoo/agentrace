# TRACE_SCHEMA.md

## Goal
Define the first useful, implementation-friendly trace shape for inspecting code-agent workflows.

This schema is intentionally narrow. It optimizes for debugging real agent runs rather than modeling every possible agent abstraction.

## Design principles
- capture what a developer needs to answer: what happened, in what order, why did it fail, what changed, and what should I inspect next
- keep the trace append-only and event-oriented
- separate top-level run summary from per-event details
- prefer explicit timestamps, status fields, and durations over inferred meaning
- support partial traces from incomplete or crashed runs

## Top-level trace object

```json
{
  "trace_version": "0.1",
  "run": {},
  "events": [],
  "artifacts": [],
  "summary": {}
}
```

## `run`
Required metadata about the overall agent execution.

```json
{
  "id": "run_2026_04_23_001",
  "task": "Fix failing auth test and explain the root cause",
  "agent": {
    "name": "example-agent",
    "version": "0.1.0",
    "model": "gpt-5"
  },
  "repo": {
    "name": "acme-app",
    "branch": "main",
    "commit": "abc123def"
  },
  "status": "failed",
  "started_at": "2026-04-23T13:00:00Z",
  "ended_at": "2026-04-23T13:03:42Z",
  "duration_ms": 222000,
  "attempt": 1,
  "parent_run_id": null
}
```

### Required `run` fields
- `id`
- `task`
- `status`
- `started_at`

### Recommended `run` fields
- `ended_at`
- `duration_ms`
- `agent.name`
- `agent.model`
- `repo.name`
- `repo.branch`
- `repo.commit`
- `attempt`
- `parent_run_id`

## Event model
Each event should share a small common envelope.

```json
{
  "id": "evt_004",
  "seq": 4,
  "type": "command",
  "started_at": "2026-04-23T13:01:10Z",
  "ended_at": "2026-04-23T13:01:12Z",
  "duration_ms": 2100,
  "status": "failed"
}
```

### Common event fields
- `id`: stable event id within the trace
- `seq`: monotonic order for replay and debugging
- `type`: event kind
- `started_at`: event start timestamp
- `ended_at`: optional event end timestamp
- `duration_ms`: optional event duration
- `status`: `started`, `succeeded`, `failed`, `cancelled`, or `unknown`
- `error`: optional structured error object

### Error object

```json
{
  "message": "pytest exited with status 1",
  "type": "nonzero_exit",
  "details": {
    "exit_code": 1
  }
}
```

## Event types

### 1. `model_call`
Captures a model request/response boundary without requiring full prompt logging.

```json
{
  "id": "evt_001",
  "seq": 1,
  "type": "model_call",
  "status": "succeeded",
  "started_at": "2026-04-23T13:00:01Z",
  "ended_at": "2026-04-23T13:00:04Z",
  "duration_ms": 3200,
  "input": {
    "messages": 6,
    "system_chars": 1200,
    "user_chars": 340,
    "context_chars": 8200
  },
  "output": {
    "finish_reason": "tool_use",
    "assistant_chars": 180
  }
}
```

Useful for understanding pacing, retries, and whether the model chose to call tools.

### 2. `tool_call`
Captures structured tool usage.

```json
{
  "id": "evt_002",
  "seq": 2,
  "type": "tool_call",
  "status": "succeeded",
  "started_at": "2026-04-23T13:00:05Z",
  "ended_at": "2026-04-23T13:00:05Z",
  "duration_ms": 120,
  "tool": {
    "name": "search_files",
    "args": {
      "pattern": "AuthError",
      "path": "src"
    }
  },
  "result": {
    "preview": "3 matches in src/auth.py",
    "item_count": 3
  }
}
```

Minimum useful fields:
- `tool.name`
- `tool.args`
- `result.preview` or `error`

### 3. `command`
Captures terminal commands, which are especially important for debugging.

```json
{
  "id": "evt_003",
  "seq": 3,
  "type": "command",
  "status": "failed",
  "started_at": "2026-04-23T13:01:10Z",
  "ended_at": "2026-04-23T13:01:12Z",
  "duration_ms": 2100,
  "command": {
    "value": "pytest tests/test_auth.py -q",
    "cwd": "/workspace/app"
  },
  "exit_code": 1,
  "stdout_preview": "F                                                                    [100%]",
  "stderr_preview": "AssertionError: expected 401 but got 500"
}
```

Minimum useful fields:
- `command.value`
- `exit_code`
- `stdout_preview`
- `stderr_preview`

### 4. `file_edit`
Captures materialized repo changes.

```json
{
  "id": "evt_004",
  "seq": 4,
  "type": "file_edit",
  "status": "succeeded",
  "started_at": "2026-04-23T13:02:00Z",
  "ended_at": "2026-04-23T13:02:01Z",
  "duration_ms": 400,
  "file": {
    "path": "src/auth.py"
  },
  "change": {
    "kind": "modify",
    "added_lines": 4,
    "removed_lines": 1,
    "summary": "Return 401 for invalid tokens instead of re-raising decoder exception"
  }
}
```

Minimum useful fields:
- `file.path`
- `change.kind`
- `change.summary`

### 5. `test_result`
Captures test execution outcomes, either from a command or a higher-level test runner.

```json
{
  "id": "evt_005",
  "seq": 5,
  "type": "test_result",
  "status": "succeeded",
  "started_at": "2026-04-23T13:02:15Z",
  "ended_at": "2026-04-23T13:02:18Z",
  "duration_ms": 3100,
  "test": {
    "runner": "pytest",
    "target": "tests/test_auth.py",
    "passed": 1,
    "failed": 0,
    "skipped": 0
  },
  "source_command_event_id": "evt_006"
}
```

### 6. `note`
Short explanatory agent note when there is useful reasoning or an explicit retry/failure explanation.

```json
{
  "id": "evt_006",
  "seq": 6,
  "type": "note",
  "status": "succeeded",
  "started_at": "2026-04-23T13:02:20Z",
  "message": "Initial failure came from exception translation in auth middleware. Retesting after patch."
}
```

This is preferred over trying to store complete hidden reasoning.

## `artifacts`
Optional references to larger payloads that should not be inlined in every event.

```json
[
  {
    "kind": "command_log",
    "path": "artifacts/evt_003.log",
    "event_id": "evt_003"
  },
  {
    "kind": "diff",
    "path": "artifacts/evt_004.diff",
    "event_id": "evt_004"
  }
]
```

## `summary`
A compact run-level summary for quick inspection.

```json
{
  "result": "failed",
  "failure_reason": "Auth test still failing after first patch",
  "event_counts": {
    "model_call": 2,
    "tool_call": 4,
    "command": 2,
    "file_edit": 1,
    "test_result": 1,
    "note": 1
  },
  "files_changed": [
    "src/auth.py"
  ],
  "commands_run": [
    "pytest tests/test_auth.py -q"
  ],
  "command_durations_ms": [
    {
      "command": "pytest tests/test_auth.py -q",
      "duration_ms": 2100,
      "status": "failed",
      "exit_code": 1,
      "started_at": "2026-04-23T13:01:10Z",
      "ended_at": "2026-04-23T13:01:12Z"
    }
  ],
  "edit_summaries": [
    {
      "path": "src/auth.py",
      "kind": "modify",
      "status": "succeeded",
      "duration_ms": 400,
      "started_at": "2026-04-23T13:02:00Z",
      "ended_at": "2026-04-23T13:02:01Z",
      "added_lines": 4,
      "removed_lines": 1,
      "net_line_delta": 3,
      "summary": "Return 401 for invalid tokens instead of re-raising decoder exception"
    }
  ],
  "next_inspection_targets": [
    "command evt_003 stderr_preview",
    "diff artifact for evt_004"
  ]
}
```

Report builders should surface command timing, command summaries, edit summaries, and a combined
command/edit activity timeline in both JSON and Markdown so a developer can quickly identify slow or failed commands and
understand the file-level impact and human-readable summary of edits without opening raw events first. Failed
command rows may also carry stdout/stderr previews so report-level failure lists
can point directly at the actionable command output.
Command timing rows should carry and Markdown reports should render duration, duration source (`explicit`, `derived`, or
`missing`), status, exit code, cwd, human-readable summaries when available, stdout/stderr previews when available, and available start/end timestamps; summary-derived report rows normalize missing `duration_source` values from the available timing fields, treating a present legacy `duration_ms` as `explicit` and timestamp-window-only rows as `derived`. Edit
summary rows should carry and Markdown reports should render file impact plus edit status, duration, duration
source, available start/end timestamps, and error messages when available; summary-derived report rows use the same duration-source normalization and should be padded with safe fallback values for omitted event/path/kind/status/summary/line-count fields so partial compact summaries remain reportable instead of failing at render time. Edit summary rows should also carry per-row `net_line_delta`; report builders fill it from `added_lines` and `removed_lines` when older summary rows omit it so report detail rows expose added/removed/net line impact without requiring mental arithmetic. JSON reports should also include
aggregate `command_timing_summary` totals (`count`, `unique_command_count`,
ordered `commands_run`, `repeated_commands`, per-command `command_attempts` with attempt counts, total/average duration,
failure counts, status distribution, duration source distribution, repeated-group median/range/min-max duration metrics, duration recorded/missing counts, duration coverage ratio, summary recorded/missing counts, summary coverage ratio, compact summary and missing-summary examples for repeated groups, status-duration totals/averages/min-max extremes/coverage/shares with a dominant status highlight, duration-source duration totals/averages/min-max extremes/shares, aggregate time window, first/last event references, and linked artifacts, `total_duration_ms`,
`average_duration_ms`, `average_recorded_duration_ms`, `median_duration_ms`, `failed_count`, `failed_commands` with timing/failure/working-directory context, `exit_code_counts`, exit-code duration totals/averages/min-max extremes/coverage/shares with a dominant exit-code duration highlight and exit-code summary coverage plus compact exit-code summary and missing-summary examples, `status_counts`, `status_duration_extremes_ms`, `status_duration_coverage` with recorded/missing/coverage ratio by status, `duration_source_counts`, `duration_source_duration_ms`, `duration_source_average_ms`, `duration_source_extremes_ms`, `duration_source_share`,
`duration_recorded_count`, `duration_missing_count`, `duration_coverage_ratio`, `summary_recorded_count`, `summary_missing_count`, `summary_coverage_ratio`, `summary_examples`, `summary_missing_examples`, grouped command `command_summary_examples`/`command_summary_missing_examples`, `cwd_summary_examples`/`cwd_summary_missing_examples`, `status_summary_examples`/`status_summary_missing_examples`, and `duration_source_summary_examples`/`duration_source_summary_missing_examples` for representative explained and unexplained commands by command identity, working directory, status, and duration-source bucket, with linked artifact references preserved on compact summary/missing-summary example rows when available,
aggregate `time_window`, command working-directory distribution `cwd_counts`, cwd duration totals/averages/min-max extremes/coverage/shares with a dominant-duration cwd highlight, per-working-directory `cwd_totals` with commands run, failure counts, timing totals, repeated-group median/range/min-max duration metrics, duration recorded/missing counts, duration coverage ratio, summary recorded/missing counts, summary coverage ratio, compact missing-summary examples, status-duration totals/averages/min-max extremes/coverage/shares with a dominant status highlight, duration-source duration totals/averages/min-max extremes/shares, status/source distributions, time windows, first/last event references for repeated cwd groups, and linked artifacts, command `duration_range_ms`, command `duration_extremes_ms` min/max bounds, and `first`, `slowest`, `fastest`, and `last` command highlights with working-directory context and summaries when present). JSON reports should also include an `activity_timeline` list that interleaves command timing and file-edit summary rows by available start/end timestamp, preserves source order for untimestamped rows, and carries command identity, cwd, exit status, command summaries, stdout/stderr previews when available, edit path/kind/line impact, timing source, error context, and linked artifacts for quick chronological inspection.
JSON reports should pair that list with `report_inspection_targets`, a prioritized set of compact command/edit rows for reviewers to inspect first, including failed activity, missing command/edit timing, missing command/edit summaries, and the slowest activity with identity, reason, duration, timing source, available start/end timestamps, status, cwd/exit code or edit kind/net-line context, stderr/error previews, and linked artifacts when available. JSON reports should pair that list with `activity_timeline_summary` totals (count, type/status/duration-source distributions, per-status duration totals, average durations, min/max extremes, recorded/missing coverage, and duration-share values, per-duration-source duration totals, average-duration values, min/max duration extremes, and duration-share values, summary recorded/missing counts plus coverage ratio, compact `summary_examples`, compact `summary_missing_examples`, grouped activity `type_summary_examples`/`type_summary_missing_examples`, `status_summary_examples`/`status_summary_missing_examples`, and `duration_source_summary_examples`/`duration_source_summary_missing_examples`, `identity_summary_examples`/`identity_summary_missing_examples` grouped by command or file-edit identity, a `dominant_duration_status` highlight, per-type duration totals, `type_average_duration_ms`, `type_duration_extremes_ms` min/max bounds, per-type `type_duration_coverage` recorded/missing/coverage ratios, per-type `type_duration_share` values, a `dominant_duration_type` highlight, failed count, aggregate `time_window`, `span_duration_ms`, covered/uncovered interval metrics, coverage/idle/overlap ratios, first/slowest/fastest/last activity highlights, failed-activity identities, idle gap totals, and overlap totals). JSON reports should also include a top-level `report_summary_coverage` block that breaks human-readable summary coverage down by command duration source/status/command identity/working directory/exit code, edit duration source/status/kind/file path, and activity type/status/duration source/identity so reviewers can identify exactly where explanations are sparse without scanning every detail row.
`edit_summary_totals` (`count`, deduplicated changed files, per-file `file_change_totals` with edit counts,
failure counts, total added/removed/net lines, total/average duration, median duration, duration range, min/max duration extremes for repeated file groups, duration recorded/missing counts, duration coverage ratio, summary recorded/missing counts, summary coverage ratio, compact summary and missing-summary examples for repeated groups, status-duration totals/averages/min-max extremes/coverage/shares with a dominant status highlight, duration-source duration totals/averages/min-max extremes/shares, status distribution, kind distribution, duration source distribution, aggregate time window, first/last event references for repeated file groups, and linked artifacts, total added/removed lines, edit `failed_count`,
`failed_edits`, edit-kind distribution `kind_counts`, kind duration totals/averages/min-max extremes/coverage/shares with a dominant-duration kind highlight, per-kind `kind_totals` with changed files, failure counts, line impact, timing totals, average/median/range/min-max duration metrics for repeated kind groups, duration recorded/missing counts, duration coverage ratio, summary recorded/missing counts, summary coverage ratio, status-duration totals/averages/min-max extremes/coverage/shares with a dominant status highlight, duration-source duration totals/averages/min-max extremes/shares, status/source distributions, time windows, first/last event references for repeated edit-kind groups, and linked artifacts, edit `status_counts`, `status_duration_extremes_ms`, `status_duration_coverage` with recorded/missing/coverage ratio by status, `duration_source_counts`, `duration_source_duration_ms`, `duration_source_average_ms`, `duration_source_extremes_ms`, `duration_source_share`, `duration_recorded_count`, `duration_missing_count`, `duration_coverage_ratio`, `summary_recorded_count`, `summary_missing_count`, `summary_coverage_ratio`, aggregate `time_window`,
`net_line_delta`, total/average/average-recorded-only/median edit duration, edit `duration_range_ms`, edit `duration_extremes_ms` min/max bounds, `summary_examples`, `summary_missing_examples`, grouped edit `path_summary_examples`/`path_summary_missing_examples`, `kind_summary_examples`/`kind_summary_missing_examples`, `status_summary_examples`/`status_summary_missing_examples`, and `duration_source_summary_examples`/`duration_source_summary_missing_examples` for representative explained and unexplained edits by file path, edit kind, status, and duration-source bucket, with linked artifact references preserved on compact summary/missing-summary example rows when available, and `first_edit`, `largest_edit`, `slowest_edit`, `shortest_edit`, and `last_edit` highlights with timing context and edit summaries). Failed command and failed edit aggregate rows should retain linked artifact references when available, so report totals can point at command logs or diff artifacts without requiring a detail-row scan. Failed edit
rows should retain path/kind, line impact, timing context, summary, and available
error message so failed write attempts are visible from aggregate report totals. Aggregate
Nested `command_attempts`, repeated `cwd_totals`, repeated `file_change_totals`, and repeated `kind_totals` rows plus `slowest` and `largest_edit` entries should preserve first/last event references and the same timing context as
their source rows, including duration source, available start/end timestamps, and
linked artifact references, so the top-level report can explain why each aggregate
was selected or grouped and point at its command log or diff. Markdown reports should render
the same aggregate command/edit totals near the top-level summary so reviewers can
inspect the run impact before scanning individual rows, including unique commands,
repeated command retries, grouped summary coverage by command duration source/status/identity/working directory and edit duration source/status/kind/path, per-command attempt totals with attempt-level duration-source counts/totals/shares, repeated-group summary recorded/missing counts and coverage ratios plus compact missing-summary examples, time windows, and artifacts, command working-directory counts, cwd duration totals/averages/min-max extremes/coverage/shares and dominant cwd highlights, per-cwd timing totals with duration-source counts/totals/shares and artifacts, failed command identities with timing/failure context, command exit-code distributions, command status counts,
command duration source counts plus duration totals/averages/shares by source, exit-code duration totals/averages/min-max extremes/coverage/shares with a dominant exit-code duration highlight, exit-code summary coverage, compact exit-code summary/missing-summary examples, grouped command cwd/status/duration-source summary and missing-summary examples, status-duration totals/averages/min-max extremes/coverage/shares with a dominant status highlight, duration recorded/missing counts and coverage ratio, command summary recorded/missing counts and coverage ratio plus compact command summary examples, aggregate command time window, the average, average recorded-only, median, range, and min/max extremes of command durations, first, slowest, fastest, and last command identities with
their timing and working-directory context plus command summaries when present, changed-file list, per-file change totals with file-level duration-source counts/totals/shares, repeated file/edit-kind summary recorded/missing counts and coverage ratios, time windows, and artifacts, net line delta, edit failure counts/status
distribution, edit status-duration totals/averages/min-max extremes/coverage/shares with a dominant status highlight, edit-kind counts, edit-kind duration totals/averages/min-max extremes/coverage/shares and dominant kind highlights, per-kind timing/line-impact totals with duration-source counts/totals/shares and artifacts, failed edit identities with timing/error context, failed command identities with working-directory context, prioritized `report_inspection_targets` for failed activity, sparse timing/summary rows, and slowest activity, edit duration source counts plus duration totals/averages/shares by source, edit duration recorded/missing counts and coverage ratio, edit summary recorded/missing counts and coverage ratio plus compact edit summary/missing-summary examples and grouped edit kind/status/duration-source summary/missing-summary examples with artifact context when available, aggregate edit time window, average
edit duration, average recorded-only edit duration, median edit duration, edit duration range, edit duration min/max extremes, first, largest, slowest, shortest, and last edits with their timing context and edit summaries when present, and a compact activity timeline summary with type/status/source distributions, duration recorded/missing counts and coverage ratio, summary recorded/missing counts, coverage ratio, summary examples, missing-summary examples, and grouped activity identity summary/missing-summary examples, per-type, per-status, and per-duration-source duration totals, type-duration averages, min/max extremes, and coverage, status-duration averages, min/max extremes, and coverage, source-duration averages, and duration shares, the dominant duration type/share, dominant duration status/share, failure count, first activity, slowest activity, fastest activity, last activity, idle gap totals/average/largest gap, overlap totals/average/largest overlap and overlap ratio, first failed and all failed activity identities, span duration, covered duration, covered interval windows, raw and merged covered interval counts, uncovered duration, uncovered interval windows plus uncovered count/average/largest interval, coverage, idle, and overlap ratios, total/average/average-recorded-only/median duration, duration range, duration min/max extremes, and time window. Markdown reports should also render a compact `report_summary_coverage` line near the top-level totals, including per-command and per-file coverage labels, plus a `report_summary_duration_impact` line that totals summarized vs. unsummarized command, edit, and combined activity duration, shows recorded/missing/total row counts, total duration milliseconds, recorded and missing duration shares, average, median, range, min/max extremes, duration-source counts/totals/shares, and highest-duration compact examples for summarized row durations, plus average, median, range, min/max extremes, and duration-source counts/totals/shares for unsummarized row durations in each command/edit/activity duration-impact bucket, surfaces the largest missing-summary duration and its share of all missing-summary duration for that bucket, and includes compact highest-duration missing-summary examples for each bucket so reviewers can prioritize sparse high-duration rows before scanning details, plus an `Activity Timeline` section after the detailed command and edit sections, interleaving commands and edits in chronological order with the same timing, status, command summaries when present, command output-preview, file-impact, error, and artifact context.
If `duration_ms` is absent but both `started_at` and `ended_at` are
present, report builders derive the row duration from that timestamp window.
Derived durations should be used consistently in quick-inspection rows,
aggregate command/edit totals, and the report-level `summary.total_duration_ms`
so report timing does not undercount traces that record timestamp windows only.
When command or diff artifacts are linked to those events, reports should also
show the artifact kind and path beside the relevant command timing or edit row.
Report builders normalize both top-level `artifacts[].event_id` references and
inline per-event `artifacts` arrays into the same compact `{kind, path}` rows,
deduplicate them, and carry that merged artifact context into summary and
missing-summary examples so aggregate rows point at every supporting log/diff
without forcing reviewers to scan raw events.

## MVP acceptance rule
A trace is MVP-useful if a developer can answer all of the following from one artifact bundle:
- what task was the agent trying to do
- which tools and commands it used
- what files changed
- whether tests passed or failed
- where the first actionable failure signal appeared
- what to inspect next

## Scope note
This is a practical schema checkpoint, not a final standard. Future versions can add retry groups, parent/child spans, token metrics, and richer command/test payloads once basic traces are working.

## Minimum trace event fields
- `timestamp`
- `type`
- `name`
- `status`
- `details`
- `duration_ms`

## Trace run artifact
- `run_id`
- `task`
- `events`
- `result_summary`
- `timing`

## Trace report outputs
- JSON summary should include event_count, ok_events, and total_duration_ms
- Markdown summary should include task, run_id, status, and timing overview
