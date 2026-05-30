## Latest status
`agentrace` report duration-impact summaries now split summarized and unsummarized duration by duration source. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets expose `summary_recorded_duration_source_duration_ms`, `summary_recorded_duration_source_share`, `summary_missing_duration_source_duration_ms`, and `summary_missing_duration_source_share`, and Markdown renders those source totals/shares next to the existing duration-source counts.

## What was done
- created AgentSpec task `T-128` for a report summary-duration-impact source-share follow-up slice
- added JSON duration-source duration totals and within-bucket shares for summarized and unsummarized rows
- rendered recorded/missing duration-source totals and shares in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new source total/share fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed

## Older status
`agentrace` report duration-impact summaries now show the duration share for rows that already have human-readable summaries. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets expose `summary_recorded_duration_share`, and Markdown renders `recorded_duration_share` beside `recorded_duration_ms` so reviewers can compare explained vs. unexplained duration concentration without manual arithmetic.

## What was done
- created AgentSpec task `T-127` for a report summary-duration-impact recorded-share follow-up slice
- added JSON `summary_recorded_duration_share` under each command/edit/activity duration-impact bucket
- rendered `recorded_duration_share` in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new summarized-duration share field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — refreshed fixture and passed after update

## Previous status
`agentrace` report duration-impact summaries now include compact examples for rows that already have human-readable summaries. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets expose `summary_recorded_duration_examples`, and Markdown renders `recorded_duration_examples` next to recorded duration source counts so reviewers can compare explained high-duration rows against missing-summary examples without scanning detail sections.

## What was done
- created AgentSpec task `T-126` for a report summary-duration-impact recorded-example follow-up slice
- added JSON `summary_recorded_duration_examples` under each command/edit/activity duration-impact bucket
- rendered `recorded_duration_examples` in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new summarized-duration example field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels -q` — 2 passed
