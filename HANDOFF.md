`agentrace` reports now quantify the share of total duration represented by positive missing-summary incomplete-window excess. JSON and Markdown include `summary_missing_window_excess_duration_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see whether the excess incomplete-window duration is material relative to the bucket instead of reading only raw milliseconds.

## What was done
- created AgentSpec task `T-164` for summary/timing-window excess-duration share visibility
- added `summary_missing_window_excess_duration_share` to JSON `report_summary_timing_window_impact`
- rendered the new excess-duration share in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose positive incomplete-window duration excess inside `report_summary_timing_window_impact`. JSON and Markdown include `summary_missing_window_excess_duration_ms` for command, edit, and combined activity buckets, so reviewers can see how much more missing timestamp-window duration belongs to rows without human-readable summaries than rows with summaries.

## What was done
- created AgentSpec task `T-163` for summary/timing-window excess-duration visibility
- added `summary_missing_window_excess_duration_ms` to JSON `report_summary_timing_window_impact`
- rendered the new excess-duration metric in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now label summary/timestamp-window gaps inside `report_summary_timing_window_impact`. JSON and Markdown include `summary_missing_window_gap_label` for command, edit, and combined activity buckets, so reviewers can quickly triage when rows without human-readable summaries are materially more timestamp-sparse than summarized rows.

## What was done
- created AgentSpec task `T-162` for qualitative summary/timing-window gap triage
- added `summary_missing_window_gap_label` to JSON `report_summary_timing_window_impact`
- rendered the new label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now show missing timestamp-window share deltas inside `report_summary_timing_window_impact`. JSON and Markdown include `summary_missing_window_share_delta` and `summary_missing_window_duration_share_delta` for command, edit, and combined activity buckets, so reviewers can immediately see whether missing-summary rows have more or less incomplete timestamp telemetry than rows with recorded summaries.

## What was done
- created AgentSpec task `T-161` for summary/timing-window missing-share delta visibility
- added missing-window count-share and duration-share delta fields to JSON `report_summary_timing_window_impact`
- rendered the new deltas in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now show explicit missing timestamp-window count shares inside `report_summary_timing_window_impact`. JSON and Markdown include `summary_recorded_missing_window_share` and `summary_missing_missing_window_share` for command, edit, and combined activity buckets, complementing the existing complete-window count shares and duration shares so reviewers can see whether summarized or unsummarized rows lack complete start/end windows without doing subtraction.

## What was done
- created AgentSpec task `T-160` for summary/timing-window missing-count share visibility
- added missing-window count share fields to JSON `report_summary_timing_window_impact`
- rendered the new count shares in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now show missing timestamp-window duration shares inside `report_summary_timing_window_impact`. JSON and Markdown include `summary_recorded_missing_window_duration_share` and `summary_missing_missing_window_duration_share` for command, edit, and combined activity buckets, complementing the existing complete-window shares so reviewers can see how much summarized and unsummarized duration remains outside complete start/end windows.

## What was done
- created AgentSpec task `T-159` for summary/timing-window missing-duration share visibility
- added missing-window duration share fields to JSON `report_summary_timing_window_impact`
- rendered the new shares in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now connect summary coverage to timestamp-window completeness. JSON and Markdown include `report_summary_timing_window_impact` for command, edit, and combined activity rows, splitting complete versus missing timestamp-window counts and duration totals by rows with recorded summaries versus missing summaries so reviewers can tell whether explained and unexplained activity has comparable start/end telemetry.

## What was done
- created AgentSpec task `T-158` for summary/timing-window impact visibility
- added `report_summary_timing_window_impact` to JSON report output
- rendered the new impact block in Markdown reports
- refreshed regression coverage, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 39 passed, 1 warning
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` timing-window coverage now reports both sides of duration-share impact. JSON `report_timing_window_coverage` command/edit/activity buckets include `complete_window_duration_share` beside existing complete/missing window duration totals and missing-window share, and Markdown renders the same value inline so reviewers can see the explained timestamp-window share without subtracting from sparse-window impact.

## What was done
- created AgentSpec task `T-157` for complete timestamp-window duration share visibility
- added `complete_window_duration_share` to JSON timing-window coverage metrics
- rendered the new share in Markdown report timing-window coverage
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 38 passed, 1 warning
- `bash scripts/ci_check.sh` — 45 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` timing-window coverage now quantifies duration impact for incomplete timestamp windows. JSON `report_timing_window_coverage` command/edit/activity buckets include complete-window duration totals, missing-window duration totals and shares, and `partial_timestamp_window_duration_ms` split into `started_only`, `ended_only`, and `missing_both`; Markdown renders the same totals inline so reviewers can see whether incomplete timestamp telemetry covers a material amount of recorded command/edit time.

## What was done
- created AgentSpec task `T-156` for missing timestamp-window duration impact
- added complete vs. missing timestamp-window duration totals and missing-window duration share to JSON coverage metrics
- added partial timestamp-window duration totals by started-only, ended-only, and missing-both buckets
- rendered the new duration impact fields in Markdown and refreshed regression expectations plus schema/project state docs

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
- `bash scripts/ci_check.sh` — 45 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` timing-window coverage now includes grouped examples for partial timestamp telemetry. JSON `report_timing_window_coverage` command/edit/activity buckets expose `partial_timestamp_window_examples` split into `started_only`, `ended_only`, and `missing_both`, and Markdown renders the same buckets beside the existing missing-window examples so reviewers can jump directly to representative incomplete timestamp rows.

## What was done
- created AgentSpec task `T-155` for partial timestamp-window example buckets
- added grouped partial timestamp-window examples to JSON report coverage metrics
- rendered the new grouped examples in Markdown timing-window coverage
- refreshed regression coverage, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 38 passed, 1 warning

## Older status
`agentrace` timing-window coverage now separates partial timestamp telemetry. JSON `report_timing_window_coverage` command/edit/activity buckets include `started_only_count`, `ended_only_count`, `missing_started_at_count`, and `missing_ended_at_count` beside existing started/ended/complete/missing-window totals; Markdown renders the new fields inline so reviewers can distinguish producers that emit only start timestamps from those that emit only end timestamps before inspecting examples.

## What was done
- created AgentSpec task `T-154` for partial timestamp-window coverage counts
- added started-only, ended-only, missing-start, and missing-end counts to JSON timing-window metrics
- rendered the new partial-window counts in Markdown timing-window coverage
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary tests/test_report_outputs.py::test_activity_timeline_summary_derives_coverage_for_partial_windows -q` — 2 passed
- `bash scripts/ci_check.sh` — 45 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` timing-window coverage now labels duration-vs-window consistency severity. JSON `report_timing_window_coverage` command/edit/activity buckets include `duration_window_delta_abs_recorded_duration_share` and `duration_window_delta_consistency_label` (`no_comparable_rows`, `matched`, `low_delta`, `medium_delta`, or `high_delta`); Markdown renders both fields before direction counts so reviewers can triage whether timestamp-window mismatches are material before reading representative rows.

## What was done
- created AgentSpec task `T-153` for timing-window consistency severity labels
- added absolute-delta recorded-duration share and consistency labels to JSON timing-window metrics
- rendered the new severity fields in Markdown timing-window coverage
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary tests/test_report_outputs.py::test_timing_window_delta_direction_examples_show_mismatch_context -q` — 2 passed

## Older status
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

