## Latest status
`agentrace` report summary-duration-impact rows now expose the largest missing-summary row's total-duration share. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_largest_missing_total_duration_share`, and Markdown renders `largest_missing_total_duration_share` beside the missing-bucket share so reviewers can see whether one unexplained row dominates the whole command/edit activity duration, not just the missing-summary bucket.

## What was done
- created AgentSpec task `T-132` for a report summary-duration-impact missing-total-share follow-up slice
- added JSON largest-missing total-duration share fields for command, edit, and combined activity duration-impact metrics
- rendered largest-missing total-duration share fields in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new largest-missing total-share field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact -q` — 2 passed

## Older status
`agentrace` report summary-duration-impact rows now expose the largest summarized-row duration and its concentration shares. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_largest_recorded_duration_ms`, `summary_largest_recorded_duration_share`, and `summary_largest_recorded_total_duration_share`, and Markdown renders matching `largest_recorded_*` fields beside summarized duration-source shares so reviewers can see whether summarized coverage is dominated by one expensive explained row.

## What was done
- created AgentSpec task `T-131` for a report summary-duration-impact largest-recorded follow-up slice
- added JSON largest-recorded duration/share fields for command, edit, and combined activity duration-impact metrics
- rendered largest-recorded duration/share fields in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new largest-recorded fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact -q` — 2 passed
