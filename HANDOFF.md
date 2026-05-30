## Latest status
`agentrace` report duration-impact summaries now include duration-source counts for rows that have human-readable summaries. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets expose `summary_recorded_duration_source_counts`, and Markdown renders `recorded_duration_source_counts` next to recorded-duration totals so reviewers can compare explained duration provenance against the existing missing-summary source counts.

## What was done
- created AgentSpec task `T-124` for a report summary-duration-impact recorded-source-count follow-up slice
- added JSON `summary_recorded_duration_source_counts` under each command/edit/activity duration-impact bucket
- rendered `recorded_duration_source_counts` in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new summarized-duration source-count field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed

## Previous status
## Latest status
`agentrace` report duration-impact summaries now include duration-source counts for rows that lack human-readable summaries. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets expose `summary_missing_duration_source_counts`, and Markdown renders `missing_duration_source_counts` next to the existing missing-duration average, median, range, and min/max spread.

## What was done
- created AgentSpec task `T-123` for a report summary-duration-impact source-count follow-up slice
- added JSON `summary_missing_duration_source_counts` under each command/edit/activity duration-impact bucket
- rendered `missing_duration_source_counts` in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new sparse-summary source-count field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed

## Previous status
## Latest status
`agentrace` report duration-impact summaries now include range and min/max extremes for rows that lack human-readable summaries. This extends the average/median/largest-missing signals so reviewers can see the spread of unsummarized command/edit/activity durations without scanning detail rows.

## What was done
- created AgentSpec task `T-122` for a report summary-duration-impact spread follow-up slice
- added JSON `summary_missing_duration_range_ms` and `summary_missing_duration_extremes_ms` under each command/edit/activity duration-impact bucket
- rendered missing-duration range and min/max extremes in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new sparse-summary spread fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed

## Previous status
## Latest status
`agentrace` report duration-impact summaries now include the median duration of rows that lack human-readable summaries. This complements the average and largest-missing-duration signals so reviewers can see whether sparse summary coverage is skewed by one expensive row or reflects the typical unsummarized command/edit/activity row.

## What was done
- created AgentSpec task `T-121` for a report summary-duration-impact median follow-up slice
- added JSON `summary_missing_median_duration_ms` under each command/edit/activity duration-impact bucket
- rendered `missing_median_duration_ms` in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new sparse-summary median field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed

## Previous status
## Latest status
`agentrace` report duration-impact summaries now include the average duration of rows that lack human-readable summaries. This complements the largest-missing-duration signal so reviewers can distinguish one expensive sparse row from a broader set of similarly costly unsummarized command/edit/activity rows.

## What was done
- created AgentSpec task `T-120` for a report summary-duration-impact average follow-up slice
- added JSON `summary_missing_average_duration_ms` under each command/edit/activity duration-impact bucket
- rendered `missing_average_duration_ms` in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new sparse-summary average field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed
- `bash scripts/ci_check.sh` — 43 passed, 1 warning

## Previous status
## Latest status
`agentrace` report duration-impact summaries now surface the largest missing-summary duration and its share of each command/edit/activity missing-summary bucket. This extends the summarized-vs-unsummarized duration signal so reviewers can quickly see whether sparse summary coverage is dominated by one expensive unsummarized row or distributed across multiple rows.

## What was done
- created AgentSpec task `T-119` for a report summary-duration-impact concentration follow-up slice
- added JSON `summary_largest_missing_duration_ms` and `summary_largest_missing_duration_share` under each command/edit/activity duration-impact bucket
- rendered largest-missing duration/share in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new duration-impact concentration fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed
- `bash scripts/ci_check.sh` — 43 passed, 1 warning

## Previous status
## Latest status
`agentrace` report duration-impact summaries now include row counts beside duration totals for summarized vs. unsummarized command, edit, and combined activity rows. The top-level `report_summary_duration_impact` block/line still names highest-duration rows that lack human-readable summaries, and now also shows recorded/missing/total row counts so reviewers can distinguish one expensive sparse row from many smaller missing-summary rows.

## What was done
- created AgentSpec task `T-118` for a report summary-duration-impact count follow-up slice
- added JSON `summary_recorded_duration_count`, `summary_missing_duration_count`, and `summary_total_duration_count` under each command/edit/activity duration-impact bucket
- rendered duration-impact counts in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new duration-impact count fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 36 passed, 1 warning
- `bash scripts/ci_check.sh` — 43 passed, 1 warning

## Previous status
## Previous status
`agentrace` reports now include a top-level `report_summary_duration_impact` block/line. It totals summarized vs. unsummarized duration for command rows, edit rows, and combined activity rows so reviewers can prioritize high-duration rows that lack human-readable summaries before scanning detail sections.

## What was done
- created AgentSpec task `T-116` for a report summary-duration-impact follow-up slice
- added JSON `report_summary_duration_impact` with command/edit/activity summarized vs. unsummarized duration totals and missing-duration share
- rendered the duration-impact line near the top of Markdown summaries next to `report_summary_coverage`
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new top-level sparse-summary duration signal

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 36 passed, 1 warning
- `bash scripts/ci_check.sh` — 43 passed, 1 warning

## Previous status
`agentrace` report inspection targets now carry explicit timing windows when source rows have them. Failed activity, missing timing/summary targets, and slowest-activity targets preserve `started_at`/`ended_at` in JSON and render that context in Markdown, making the prioritized inspection list line up with the activity timeline and command/edit detail rows.

## What was done
- created AgentSpec task `T-115` for a small report inspection-target timing follow-up slice
- added start/end timestamp preservation to `report_inspection_targets`
- rendered inspection-target start/end timing in Markdown report summaries
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the inspection-target timing context
- completed AgentSpec task `T-115` via completion run `complete-t-115-add-command-timing-and-edit-summaries-to-reports-20260528040319621662` after the autonomous run recorded a stale pause finding

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 35 passed, 1 warning
- `bash scripts/ci_check.sh` — 42 passed, 1 warning

## Previous status
`agentrace` reports now include prioritized inspection targets near the top of JSON and Markdown output. The new `report_inspection_targets` block points reviewers first to failed command/edit activity, missing command/edit timing, missing command/edit summaries, and the slowest activity, while preserving identity, timing source, status, cwd/exit-code or edit-kind/net-line context, error previews, and linked artifacts when present.

## What was done
- created AgentSpec task `T-114` for a report observability follow-up slice after prior attention-gated runs remained present
- added JSON `report_inspection_targets` derived from command timing, edit summaries, and the activity timeline
- rendered `report_inspection_targets` in the Markdown top-level summary before coverage totals
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for prioritized inspection-target visibility
- completed AgentSpec run `t-114-add-command-timing-and-edit-summaries-to-reports-20260527230023954893`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 35 passed, 1 warning
- `bash scripts/ci_check.sh` — 42 passed, 1 warning

## Previous status
`agentrace` report artifact references now merge top-level artifact links with inline per-event artifact arrays. Command/edit rows and their compact summary or missing-summary examples normalize both sources into deduplicated `{kind, path}` refs, and Markdown renders the merged artifact context so aggregate examples can point at every supporting command log, stdout/stderr capture, or diff.

## What was done
- created AgentSpec task `T-112` for a report observability follow-up slice after prior halted runs remained attention-gated
- normalized inline per-event artifact arrays alongside top-level `artifacts[].event_id` links for command and edit report rows
- deduplicated merged artifact refs and preserved them in compact summary/missing-summary examples and Markdown rendering
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for merged artifact-ref visibility
- completed AgentSpec run `t-112-add-command-timing-and-edit-summaries-to-reports-20260527130109132007`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 35 passed, 1 warning
- `bash scripts/ci_check.sh` — 42 passed, 1 warning

## Previous status
`agentrace` aggregate command and edit summaries now include grouped summary and missing-summary examples by duration source. JSON `command_timing_summary` and `edit_summary_totals` expose `duration_source_summary_examples` plus `duration_source_summary_missing_examples`; Markdown renders both so reviewers can see representative explained and unexplained explicit/derived/missing-timing rows without scanning detail rows.

## What was done
- created AgentSpec task `T-110` for a report observability follow-up slice after prior halted runs remained attention-gated
- added command and edit duration-source grouped summary and missing-summary examples to JSON report totals
- rendered command/edit duration-source grouped summary examples in Markdown top-level report summaries
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for duration-source grouped example visibility
- completed AgentSpec run `t-110-add-command-timing-and-edit-summaries-to-reports-20260527040037597025`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 35 passed, 1 warning
- `bash scripts/ci_check.sh` — 42 passed, 1 warning
