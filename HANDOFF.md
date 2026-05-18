# HANDOFF.md

## Latest status
`agentrace` JSON and Markdown report totals now include duration totals and shares grouped by duration source for command timing, edit summaries, and the combined activity timeline. These source-duration summaries sit beside existing duration-source counts and coverage metrics, so report readers can tell how much recorded time came from explicit durations, derived timestamp windows, or missing-duration fallbacks.

## What was done
- created AgentSpec task `T-072` for a report observability follow-up slice
- added JSON `duration_source_duration_ms` and `duration_source_share` to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity duration-source duration/share metrics in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for duration-source duration visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning

## Previous status

`agentrace` JSON and Markdown report totals now include duration min/max extremes for command timing, edit summaries, and the combined activity timeline. These compact bounds sit beside existing average/median/range metrics so report readers can see absolute shortest/longest recorded durations without recomputing them from detail rows.

## What was done
- created AgentSpec task `T-071` for a report observability follow-up slice
- added JSON `duration_extremes_ms` min/max bounds to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity duration extremes in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for duration min/max visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status

`agentrace` JSON and Markdown report totals now include status-duration summaries for command timing and edit summaries. Command and edit aggregate blocks expose per-status duration totals, per-status duration shares, and a dominant-duration-status highlight so reviewers can see whether failed/succeeded rows consumed most of the recorded command or edit time without scanning detail rows.

## What was done
- created AgentSpec task `T-070` for a report observability follow-up slice
- added JSON `status_duration_ms`, `status_duration_share`, and `dominant_duration_status` to `command_timing_summary`
- added JSON `status_duration_ms`, `status_duration_share`, and `dominant_duration_status` to `edit_summary_totals`
- rendered command and edit status-duration summaries in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for command/edit status-duration visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status
`agentrace` JSON and Markdown report totals now include average recorded-only duration metrics for command timing, edit summaries, and the combined command/edit activity timeline. These averages exclude rows whose `duration_source` is `missing`, so partial traces can show both all-row averages and recorded-timing-only averages next to coverage metrics.

## What was done
- created AgentSpec task `T-069` for a report observability follow-up slice
- added JSON `average_recorded_duration_ms` to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity average recorded-only duration metrics in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for recorded-only duration averages

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning
