# HANDOFF.md

## Latest status
`agentrace` JSON and Markdown report totals now include average recorded-only duration metrics for command timing, edit summaries, and the combined command/edit activity timeline. These averages exclude rows whose `duration_source` is `missing`, so partial traces can show both all-row averages and recorded-timing-only averages next to coverage metrics.

## What was done
- created AgentSpec task `T-069` for a report observability follow-up slice
- added JSON `average_recorded_duration_ms` to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity average recorded-only duration metrics in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for recorded-only duration averages

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status
`agentrace` JSON and Markdown report totals now include duration recorded/missing counts and coverage ratios for command timing, edit summaries, and the combined command/edit activity timeline, making timing-data completeness visible next to duration-source distributions.

## What was done
- created AgentSpec task `T-068` for a report observability follow-up slice
- added JSON `duration_recorded_count`, `duration_missing_count`, and `duration_coverage_ratio` to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity duration coverage metrics in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for duration coverage visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning
