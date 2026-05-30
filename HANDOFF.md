## Latest status
`agentrace` report duration-impact summaries now include compact examples for rows that already have human-readable summaries. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets expose `summary_recorded_duration_examples`, and Markdown renders `recorded_duration_examples` next to recorded duration source counts so reviewers can compare explained high-duration rows against missing-summary examples without scanning detail sections.

## What was done
- created AgentSpec task `T-126` for a report summary-duration-impact recorded-example follow-up slice
- added JSON `summary_recorded_duration_examples` under each command/edit/activity duration-impact bucket
- rendered `recorded_duration_examples` in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new summarized-duration example field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed

## Previous status
`agentrace` report duration-impact summaries now include average, median, range, and min/max duration spread for rows that already have human-readable summaries. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets expose `summary_recorded_average_duration_ms`, `summary_recorded_median_duration_ms`, `summary_recorded_duration_range_ms`, and `summary_recorded_duration_extremes_ms`, and Markdown renders the same recorded-duration spread next to the existing summarized-duration source counts.

## What was done
- created AgentSpec task `T-125` for a report summary-duration-impact recorded-duration spread follow-up slice
- added JSON recorded-duration average/median/range/min-max fields under each command/edit/activity duration-impact bucket
- rendered the recorded-duration spread in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new summarized-duration spread fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed
