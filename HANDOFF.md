## Latest status
`agentrace` report summary-duration-impact rows now quantify missing-summary duration deltas as both a share and a positive excess amount. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_missing_recorded_duration_delta_share` and `summary_missing_recorded_excess_duration_ms`, and Markdown renders matching `missing_recorded_duration_delta_share` / `missing_recorded_excess_duration_ms` fields beside the existing missing-vs-recorded comparison so reviewers can size unexplained-duration overage against the full bucket duration.

## What was done
- created AgentSpec task `T-134` for a report summary-duration-impact delta-share/excess follow-up slice
- added JSON missing-minus-recorded duration share and positive excess duration fields for command, edit, and combined activity duration-impact metrics
- rendered the new comparison fields in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new comparison fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact -q` — 2 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 36 passed, 1 warning

## Older status
`agentrace` report summary-duration-impact rows now compare unexplained duration directly against explained duration. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_missing_recorded_duration_delta_ms` and `summary_missing_exceeds_recorded_duration`, and Markdown renders matching `missing_recorded_duration_delta_ms` / `missing_exceeds_recorded_duration` fields so reviewers can immediately spot buckets where unsummarized command/edit time outweighs summarized work.

## What was done
- created AgentSpec task `T-133` for a report summary-duration-impact missing-vs-recorded comparison slice
- added JSON missing-minus-recorded duration delta and missing-exceeds-recorded boolean fields for command, edit, and combined activity duration-impact metrics
- rendered the new comparison fields in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new comparison fields

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact -q` — 2 passed

## Older status
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
