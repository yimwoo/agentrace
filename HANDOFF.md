## Latest status
`agentrace` repeated command/edit aggregate groups now include compact missing-summary examples. JSON nested aggregate rows produced for per-command attempts, command cwd totals, per-file change totals, and edit-kind totals include `summary_missing_examples` beside `summary_examples`, and Markdown renders those missing-summary examples so reviewers can identify repeated rows still lacking human-readable explanations without scanning details.

## What was done
- created AgentSpec task `T-103` for a report observability follow-up slice after `T-096` remained halted for attention
- added missing-summary examples to repeated command/edit aggregate rows via shared duration-spread enrichment
- rendered nested missing-summary examples in Markdown command attempts, command cwd totals, file change totals, and edit-kind totals
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for nested missing-summary visibility
- completed AgentSpec run `t-103-add-command-timing-and-edit-summaries-to-reports-20260525180024180055`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 34 passed, 1 warning
- `bash scripts/ci_check.sh` — 41 passed, 1 warning

## Previous status
## Latest status
`agentrace` report aggregate totals now include compact missing-summary examples. JSON `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary` expose `summary_missing_examples`, and Markdown renders those examples beside existing summary coverage so reviewers can identify representative rows that still lack human-readable explanations.

## What was done
- created AgentSpec task `T-102` for a report observability follow-up slice after `T-096` remained halted for attention
- added compact missing-summary example rows for command, edit, and activity aggregate summaries
- rendered missing-summary examples in Markdown report totals and the activity timeline summary
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for missing-summary visibility
- completed AgentSpec run `t-102-add-command-timing-and-edit-summaries-to-reports-20260525130054449874`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 34 passed, 1 warning

## Previous status
# HANDOFF.md

## Latest status
`agentrace` command exit-code timing reports now identify the dominant duration exit code. JSON `command_timing_summary` includes `dominant_duration_exit_code`, and Markdown renders that highlight inside `command_exit_code_duration_summary` beside exit-code duration totals, shares, and summary coverage.

## What was done
- created AgentSpec task `T-101` for a report observability follow-up slice after `T-096` remained halted for attention
- added a dominant exit-code duration highlight to command timing report totals
- rendered the dominant exit-code duration in Markdown summaries
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for dominant exit-code visibility
- completed AgentSpec run `t-101-add-command-timing-and-edit-summaries-to-reports-20260525080056230097`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 34 passed, 1 warning
- `bash scripts/ci_check.sh` — 41 passed, 1 warning

## Previous status
# HANDOFF.md

## Latest status
`agentrace` command aggregate totals now break timing and summary coverage down by exit code. JSON `command_timing_summary` includes exit-code duration totals, averages, min/max extremes, duration coverage, duration shares, and exit-code summary coverage, while Markdown renders a compact `command_exit_code_duration_summary` next to the existing exit-code counts.

## What was done
- created AgentSpec task `T-100` for a report observability follow-up slice after `T-096` remained halted for attention
- added exit-code timing and summary-coverage aggregate fields to command timing reports
- rendered exit-code duration/coverage/share metrics in Markdown summaries
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for exit-code timing visibility
- completed AgentSpec run `t-100-add-command-timing-and-edit-summaries-to-reports-20260525040010047150`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 34 passed, 1 warning

## Previous status
# HANDOFF.md

## Latest status
`agentrace` repeated command/edit aggregate groups now surface compact summary examples. JSON repeated-group rows produced for per-command attempts, command cwd totals, per-file change totals, and edit-kind totals include `summary_examples` when grouped rows have human-readable summaries, and Markdown renders those examples beside summary coverage so repeated work can be explained without scanning detail rows.

## What was done
- created AgentSpec task `T-099` for a report observability follow-up slice after `T-096` remained halted for attention
- added repeated-group summary example extraction to command/edit aggregate rows
- rendered repeated-group summary examples in Markdown nested aggregate totals
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for repeated-group summary-example visibility
- completed AgentSpec run `t-099-add-command-timing-and-edit-summaries-to-reports-20260524230022803050`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 33 passed, 1 warning
- `bash scripts/ci_check.sh` — 40 passed, 1 warning

## Previous status
## Latest status
`agentrace` activity timeline aggregate totals now expose compact activity summary examples. JSON `activity_timeline_summary.summary_examples` carries representative command/edit rows with timing/status/type identity context, and Markdown renders those examples alongside activity summary coverage metrics so chronological explanations are visible without scanning timeline detail rows.

## What was done
- created AgentSpec task `T-098` for a report observability follow-up slice after `T-096` remained halted for attention
- added compact activity summary example rows to JSON activity timeline totals
- rendered activity summary examples in Markdown activity timeline aggregate totals
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for activity summary-example visibility
- completed AgentSpec run `t-098-add-command-timing-and-edit-summaries-to-reports-20260524180113020467`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 33 passed, 1 warning
- `bash scripts/ci_check.sh` — 40 passed, 1 warning

## Previous status
`agentrace` aggregate report totals now expose compact command/edit summary examples. JSON `command_timing_summary.summary_examples` and `edit_summary_totals.summary_examples` include representative rows with timing/status/identity context, and Markdown renders those examples beside summary coverage counts so sparse human-readable explanations are visible without scanning detail rows.

## What was done
- created AgentSpec task `T-097` for a report observability follow-up slice after `T-096` halted for attention
- declared explicit host-worktree execution in the AgentSpec context pack for the scheduled cron run
- added compact command and edit summary example rows to JSON report totals
- rendered command/edit summary examples in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for summary-example visibility
- completed AgentSpec run `t-097-add-command-timing-and-edit-summaries-to-reports-20260524130336753849`

## Verification
- `bash scripts/ci_check.sh` — 40 passed, 1 warning

## Previous status
## Latest status
`agentrace` failed-command aggregate rows now retain command working-directory context. JSON `command_timing_summary.failed_commands` carries `cwd` when available, and Markdown renders it in the failed-command summary so command failures can be tied to execution location without scanning detail rows.

## What was done
- created AgentSpec task `T-094` for a report observability follow-up slice
- added cwd preservation to failed command aggregate rows in JSON reports
- rendered failed-command cwd context in Markdown reports
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for failed-command cwd visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 32 passed, 1 warning
- `bash scripts/ci_check.sh` — 39 passed, 1 warning

## Previous status
`agentrace` repeated command/edit aggregate groups now expose summary coverage alongside duration coverage. JSON repeated-group rows for command attempts, command cwd totals, per-file change totals, and edit-kind totals include summary recorded/missing counts and coverage ratios when the group has multiple rows, and Markdown renders those metrics in the same nested aggregate details.

## What was done
- created AgentSpec task `T-092` for a report observability follow-up slice
- added repeated-group summary coverage metrics to JSON aggregate rows
- rendered repeated-group summary coverage in Markdown command/edit aggregate totals
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for nested summary coverage visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 31 passed, 1 warning

## Previous status
`agentrace` grouped report summary coverage now drills down to command identity and edit file path. JSON `report_summary_coverage` includes `command_by_command` and `edit_by_path`, and Markdown renders those labels in the compact top-level coverage line so sparse explanations can be tied to specific commands or files without scanning detail rows.

## What was done
- created AgentSpec task `T-091` for a report observability follow-up slice
- added per-command and per-file summary coverage breakdowns to JSON reports
- rendered the new coverage labels in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for command/file summary coverage visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 31 passed, 1 warning
- `bash scripts/ci_check.sh` — 38 passed, 1 warning

## Previous status
`agentrace` JSON and Markdown reports now expose grouped human-readable summary coverage. A new top-level JSON `report_summary_coverage` block breaks coverage down by command duration source/status, edit duration source/kind, and activity type/status/duration source, and Markdown renders the same compact line near the top of the report so sparse explanations are visible without scanning detail rows.

## What was done
- created AgentSpec task `T-090` for a report observability follow-up slice
- added grouped summary coverage metrics in JSON report output
- rendered grouped summary coverage in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for grouped summary coverage visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 31 passed, 1 warning
- `bash scripts/ci_check.sh` — 38 passed, 1 warning

## Previous status
`agentrace` activity timeline totals now expose summary coverage. JSON `activity_timeline_summary` includes `summary_recorded_count`, `summary_missing_count`, and `summary_coverage_ratio`, and Markdown renders those counts beside duration coverage so reviewers can see whether chronological command/edit activity has human-readable explanations.

## What was done
- created AgentSpec task `T-089` for a report observability follow-up slice
- added activity timeline summary coverage metrics in JSON report totals
- rendered activity timeline summary coverage in Markdown report totals
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for activity summary coverage visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status
`agentrace` report totals now expose command and edit summary coverage. JSON command timing and edit aggregate blocks include summary recorded/missing counts plus coverage ratios, and Markdown renders those coverage metrics beside duration coverage so reviewers can see whether report rows carry human-readable explanations without scanning each row.

## What was done
- created AgentSpec task `T-088` for a report observability follow-up slice
- added command and edit `summary_recorded_count`, `summary_missing_count`, and `summary_coverage_ratio` aggregate fields
- rendered command/edit summary coverage in Markdown report totals
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for summary coverage visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status
`agentrace` command timing and selected edit highlights now preserve and render human-readable summaries. JSON command highlight rows (first/slowest/fastest/last), failed command rows, activity timeline command rows, and edit highlight rows include `summary` when present; Markdown renders those summaries beside timing, status, artifact, output-preview, and line-impact context.

## What was done
- created AgentSpec task `T-087` for a report observability follow-up slice
- preserved command summaries from command events and run-summary rows through JSON report timing/highlight/activity rows
- rendered command summaries in Markdown command timing, failed-command, command-highlight, and activity rows
- retained selected edit summaries in JSON/Markdown edit highlight rows and refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status
`agentrace` repeated command/edit aggregate groups now expose nested duration-source average and min/max timing context. Command attempts, command cwd totals, per-file edit totals, and edit-kind totals already exposed source counts, source duration totals, and shares; they now also include `duration_source_average_ms` and `duration_source_extremes_ms` in JSON, with Markdown rendering the same nested source-duration spread beside existing repeated-group duration-source totals.

## What was done
- created AgentSpec task `T-084` for a report observability follow-up slice
- extended repeated aggregate duration spread rows with duration-source average durations and min/max extremes
- rendered nested duration-source averages/extremes for command attempts, cwd totals, file change totals, and edit-kind totals in Markdown
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for nested duration-source spread visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status
`agentrace` repeated command/edit aggregate groups now expose nested status-duration timing context. Command attempts, command cwd totals, per-file edit totals, and edit-kind totals include per-status duration totals, averages, min/max extremes, coverage ratios, duration shares, and dominant status highlights in JSON reports, and Markdown renders the same nested status-duration detail beside existing repeated-group duration-source totals.

## What was done
- created AgentSpec task `T-083` for a report observability follow-up slice
- extended repeated aggregate duration spread rows with status-duration totals/averages/extremes/coverage/shares and dominant status highlights
- rendered nested status-duration metrics for command attempts, cwd totals, file change totals, and edit-kind totals in Markdown
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for nested status-duration visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status

`agentrace` report aggregate summaries now expose duration totals grouped by command working directory and edit kind. Command timing totals include `cwd_duration_ms`, cwd averages/extremes/coverage/shares, and a dominant-duration cwd highlight; edit totals include equivalent `kind_duration_*` metrics and a dominant-duration edit-kind highlight, with Markdown rendering both grouped summaries next to the existing cwd/kind counts.

## What was done
- created AgentSpec task `T-082` for a report observability follow-up slice
- added grouped duration aggregate fields for command cwd and edit kind summaries in JSON reports
- rendered command cwd and edit kind duration summaries in Markdown reports
- refreshed regression coverage and the rich Markdown fixture for grouped cwd/kind duration visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status


## Latest status
`agentrace` JSON and Markdown nested aggregate rows now include duration-source duration totals and shares for repeated command attempts, repeated command cwd groups, repeated file-change groups, and repeated edit-kind groups. These nested rows already exposed count, total/average duration, median duration, duration range, and min/max duration extremes; the new per-source totals/shares make it clear how much of each repeated group came from explicit, derived, or missing-duration rows without scanning raw events.

## What was done
- created AgentSpec task `T-079` for a report observability follow-up slice
- added repeated-group `duration_source_duration_ms` and `duration_source_share` fields to command attempts, command cwd totals, file change totals, and edit kind totals
- rendered those nested duration-source totals/shares in Markdown reports when repeated-group spread metrics are present
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for nested aggregate duration-source total/share visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status

## Latest status
`agentrace` JSON and Markdown activity timeline summaries now include per-activity-type average durations and min/max duration extremes. These metrics sit beside per-type totals/shares and the dominant type highlight so readers can compare command vs file-edit duration spread without scanning the chronological rows.

## What was done
- created AgentSpec task `T-077` for a report observability follow-up slice
- added JSON `type_average_duration_ms` and `type_duration_extremes_ms` to `activity_timeline_summary`
- rendered activity type-duration average and min/max metrics in Markdown report aggregate summaries
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for per-type duration spread visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status

## Latest status
`agentrace` JSON and Markdown report totals now include per-status min/max duration extremes for command timing, edit summaries, and the combined activity timeline. These bounds sit beside per-status duration totals, averages, shares, and dominant-status highlights so readers can see duration spread for failed/succeeded/unknown rows without scanning detail rows.

## What was done
- created AgentSpec task `T-076` for a report observability follow-up slice
- added JSON `status_duration_extremes_ms` to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity status-duration min/max metrics in Markdown report aggregate summaries
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for per-status duration extremes visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning

## Previous status

`agentrace` JSON and Markdown report totals now include per-status average durations for command timing, edit summaries, and the combined activity timeline. These averages sit beside per-status duration totals, shares, and dominant-status highlights so readers can compare typical failed/succeeded/unknown row cost without recalculating from raw rows.

## What was done
- created AgentSpec task `T-075` for a report observability follow-up slice
- added JSON `status_average_duration_ms` to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity status-average duration metrics in Markdown report aggregate summaries
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for per-status average duration visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning

## Previous status

`agentrace` JSON and Markdown report totals now include per-duration-source min/max extremes for command timing, edit summaries, and the combined activity timeline. These bounds sit beside duration-source counts, totals, averages, shares, and coverage metrics so report readers can see duration spread within explicit, derived, and missing-duration rows without scanning detail rows.

## What was done
- created AgentSpec task `T-074` for a report observability follow-up slice
- added JSON `duration_source_extremes_ms` to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity duration-source min/max metrics in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for duration-source extremes visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status

`agentrace` JSON and Markdown report totals now include per-duration-source average durations for command timing, edit summaries, and the combined activity timeline. These averages sit beside duration-source counts, total durations, shares, and coverage metrics so report readers can compare typical explicit, derived, and missing-duration rows without recomputing totals.

## What was done
- created AgentSpec task `T-073` for a report observability follow-up slice
- added JSON `duration_source_average_ms` to `command_timing_summary`, `edit_summary_totals`, and `activity_timeline_summary`
- rendered command, edit, and activity duration-source average metrics in Markdown reports
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for duration-source average visibility

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 30 passed, 1 warning
- `bash scripts/ci_check.sh` — 37 passed, 1 warning

## Previous status


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
