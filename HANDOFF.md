## Latest status
`agentrace` report summary-duration-impact rows now break unsummarized duration down by status. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_missing_duration_status_counts`, `summary_missing_duration_status_duration_ms`, and `summary_missing_duration_status_share`, and Markdown renders the same fields beside missing duration-source totals so reviewers can see whether sparse summaries are concentrated in failed, succeeded, or unknown-status work.

## What was done
- created AgentSpec task `T-139` for a report summary-duration-impact status-breakdown follow-up slice
- added JSON missing-summary duration status counts, duration totals, and shares for command, edit, and combined activity duration-impact metrics
- rendered the new status breakdown fields in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new status fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_summary_duration_impact_labels_missing_duration_concentration tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 4 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` report summary-duration-impact rows now include a missing-duration concentration label. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_missing_duration_concentration` (`none`, `single_row`, `clustered`, or `distributed`), and Markdown renders `missing_duration_concentration` beside the existing missing-duration attention fields so reviewers can see whether sparse summaries are dominated by one expensive row or spread across multiple rows.

## What was done
- created AgentSpec task `T-138` for a report summary-duration-impact concentration-label follow-up slice
- added JSON missing-duration concentration labels for command, edit, and combined activity duration-impact metrics
- rendered the new concentration label in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new concentration field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact tests/test_report_outputs.py::test_summary_duration_impact_labels_missing_duration_concentration tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 3 passed
- `bash scripts/ci_check.sh` — 44 passed, 1 warning; wrote `examples/trace-example.json`
