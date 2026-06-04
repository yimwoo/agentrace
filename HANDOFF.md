`agentrace` timing-window coverage now includes compact direction examples for duration-vs-window consistency. JSON `report_timing_window_coverage` command/edit/activity buckets include `duration_window_delta_direction_examples` keyed by matches, recorded-duration-greater rows, and timestamp-window-greater rows; Markdown renders those examples beside direction counts so reviewers can jump to representative mismatch rows with identity, timing, summary, cwd/exit-code or edit line-impact context.

## What was done
- created AgentSpec task `T-152` for timing-window direction examples
- added direction-bucket examples to JSON timing-window consistency metrics
- rendered direction examples in Markdown timing-window coverage
- refreshed regression coverage, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_timing_window_delta_direction_examples_show_mismatch_context -q` — 1 passed

## Older status
`agentrace` timing-window coverage now classifies duration-vs-window deltas by direction. JSON `report_timing_window_coverage` command/edit/activity buckets include `duration_window_delta_direction_counts` for exact matches, rows where recorded `duration_ms` exceeds the timestamp window, and rows where the timestamp window exceeds recorded duration; Markdown renders those counts beside existing delta totals/averages so reviewers can distinguish harmless matches from over- or under-reported durations quickly.

## What was done
- created AgentSpec task `T-151` for duration/window direction counts
- added direction-count metrics to report timing-window consistency buckets
- rendered the new direction counts in Markdown timing-window coverage
- refreshed regression coverage and `TRACE_SCHEMA.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed

## Older status
`agentrace` timing-window coverage now compares complete timestamp windows against recorded row durations. JSON `report_timing_window_coverage` command/edit/activity buckets add comparable-row counts, signed and absolute duration-vs-window delta totals/averages, and largest-delta examples; Markdown renders those consistency metrics inline with the existing timestamp-window coverage so reviewers can spot producers whose `duration_ms` disagrees with `started_at`/`ended_at` without scanning detail rows.

## What was done
- created AgentSpec task `T-150` for duration-vs-window consistency metrics
- added JSON timing-window delta metrics and enriched largest-window examples with timestamp/duration delta context
- rendered the new timing-window consistency fields in Markdown report coverage
- refreshed regression coverage and `TRACE_SCHEMA.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now include top-level timing-window coverage for command, edit, and combined activity rows. JSON exposes `report_timing_window_coverage` with started/ended/complete/missing timestamp-window counts, complete-window ratios, total/average/min/max timestamp-window durations, and largest-window examples; Markdown renders the same compact line near the existing summary coverage/source/impact lines so reviewers can quickly see whether command/edit reports have usable timestamp windows in addition to duration values.

## What was done
- created AgentSpec task `T-148` for report timing-window coverage
- added JSON `report_timing_window_coverage` for command, edit, and activity rows
- rendered the timing-window coverage line in Markdown reports
- refreshed regression coverage and `TRACE_SCHEMA.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed

## Older status
`agentrace` report-wide summary provenance now mirrors the grouped coverage dimensions. Top-level JSON `report_summary_source_counts` still reports command/edit/activity provenance totals, and now also includes per-label source-count breakdowns for command duration source/status/command/cwd/exit code, edit duration source/status/kind/path, and activity type/status/duration source/identity; Markdown renders those grouped provenance counts in the compact `report_summary_source_counts` line so reviewers can see where `event.summary` fallbacks are concentrated without cross-referencing detail rows.

## What was done
- created AgentSpec task `T-147` for grouped report summary-source provenance
- expanded JSON `report_summary_source_counts` with grouped command/edit/activity provenance counts matching summary coverage labels
- expanded Markdown report summary-source rendering for the grouped provenance counts
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` activity timeline summary aggregates now expose local `summary_source_counts`, complementing report-wide provenance counts and repeated command/edit group counts. JSON `activity_timeline_summary.summary_source_counts` counts nested/inline vs `event.summary` timeline summaries, and Markdown renders `summary_source_counts=...` inside the compact activity timeline summary line.

## What was done
- created AgentSpec task `T-146` for activity timeline summary-source aggregate visibility
- added activity timeline summary-source counts in JSON reports
- rendered activity timeline summary-source counts in Markdown reports
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` repeated aggregate report groups now expose local `summary_source_counts` when duration-spread metadata is present. Per-command attempt groups, repeated cwd groups, repeated per-file groups, and repeated edit-kind groups now count nested/inline vs `event.summary` provenance beside their summary coverage metrics in JSON, and Markdown renders `summary_source_counts=...` inside those group detail lines.

## What was done
- created AgentSpec task `T-145` for repeated aggregate summary-source count visibility
- added repeated-group `summary_source_counts` via shared duration-spread aggregate metadata
- rendered repeated-group summary-source counts in Markdown aggregate detail rows
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_totals_deduplicate_files_and_show_repeated_commands tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 37 passed, 1 warning

## Older status
`agentrace` command and edit aggregate report sections now expose local `summary_source_counts` in addition to the top-level `report_summary_source_counts`. JSON `command_timing_summary` and `edit_summary_totals` count whether summarized rows came from `event.summary` or nested/inline sources, and Markdown renders `command_summary_source_counts` plus `edit_summary_source_counts` beside each section's summary coverage line.

## What was done
- created AgentSpec task `T-144` for command/edit summary-source aggregate follow-up
- added command and edit aggregate `summary_source_counts` in JSON reports
- rendered command/edit summary-source counts in Markdown reports
- refreshed regression coverage, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_reports_include_aggregate_command_and_edit_totals tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 3 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` JSON and Markdown reports now include `report_summary_source_counts` for command, edit, and combined activity rows. The new aggregate counts summarized rows by provenance, using `event.summary` for top-level canonical event fallback summaries and `nested_or_inline` for command/change/details or precomputed summary rows, so reviewers can quantify fallback summary usage without scanning every detail row.

## What was done
- created AgentSpec task `T-143` for report summary provenance counts
- added JSON `report_summary_source_counts` for command/edit/activity report rows
- rendered the new source-count line in Markdown reports near summary coverage and duration impact
- refreshed regression coverage plus `TRACE_SCHEMA.md` and `PROJECT_STATE.md` wording

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` activity timeline rows now preserve `summary_source=event.summary` for command/edit summaries recovered from top-level canonical event summaries. The marker carries through combined timeline rows and timeline highlight rows so JSON and Markdown activity views explain where fallback summaries came from, matching the command timing and edit summary tables.

## What was done
- created AgentSpec task `T-142` for activity timeline summary-source propagation
- carried `summary_source` from command/edit rows into combined activity timeline rows
- preserved `summary_source` in activity identity/highlight rows such as first/last/slowest activity
- refreshed regression coverage and `TRACE_SCHEMA.md` wording for timeline-level summary-source markers

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` report rows now mark summaries that were recovered from top-level canonical event summaries. Command timing, file-edit summaries, run-summary rows, compact JSON examples, and Markdown detail/highlight rows preserve `summary_source=event.summary` when the human-readable explanation came from the top-level event fallback rather than nested command/change/details fields.

## What was done
- created AgentSpec task `T-141` for top-level summary source visibility
- added `summary_source` to command timing and file-edit report rows when summaries come from `event.summary`
- carried the source marker into run-summary rows, compact JSON summary examples, and Markdown command/edit/activity report rendering
- refreshed regression coverage and `TRACE_SCHEMA.md` wording for top-level event-summary source markers

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` report rows now preserve human-readable command/edit summaries when producers attach them directly to canonical events. Command timing extracts `event.summary` after `command.summary`/`details.summary`, file-edit summaries extract `event.summary` after `change.summary`/`details.summary`, and run-summary fallbacks use the same precedence so JSON and Markdown reports do not classify top-level event summaries as missing.
`agentrace` report summary-duration-impact rows now include a missing-duration concentration label. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_missing_duration_concentration` (`none`, `single_row`, `clustered`, or `distributed`), and Markdown renders `missing_duration_concentration` beside the existing missing-duration attention fields so reviewers can see whether sparse summaries are dominated by one expensive row or spread across multiple rows.

## What was done
- created AgentSpec task `T-138` for a report summary-duration-impact concentration-label follow-up slice
- added JSON missing-duration concentration labels for command, edit, and combined activity duration-impact metrics
- rendered the new concentration label in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new concentration field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_summary_duration_impact_labels_missing_duration_concentration tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 3 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`
