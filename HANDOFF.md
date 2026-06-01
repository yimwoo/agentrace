## Latest status
`agentrace` report summary-duration-impact rows now include a missing-duration attention label. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_missing_duration_attention` (`none`, `low`, `medium`, or `high`), and Markdown renders `missing_duration_attention` beside `duration_balance` so reviewers can triage sparse-summary duration risk without comparing raw recorded and missing duration totals.

## What was done
- created AgentSpec task `T-137` for a report summary-duration-impact attention-label follow-up slice
- added JSON missing-duration attention labels for command, edit, and combined activity duration-impact metrics
- rendered the new attention label in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new attention field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact -q` — 2 passed
- `bash scripts/ci_check.sh` — 43 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` report summary-duration-impact rows now label the summarized-vs-unsummarized duration balance. The top-level JSON `report_summary_duration_impact` command/edit/activity buckets include `summary_duration_balance` (`missing_dominates`, `recorded_dominates`, `balanced`, or `none`), and Markdown renders `duration_balance` beside the existing missing-vs-recorded ratio/excess fields so reviewers can classify sparse-summary duration risk without interpreting raw deltas.

## What was done
- created AgentSpec task `T-136` for a report summary-duration-impact balance-label follow-up slice
- added JSON duration-balance labels for command, edit, and combined activity duration-impact metrics
- rendered the new balance label in the Markdown `report_summary_duration_impact` line
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new balance field

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_coverage_groups_explanations_by_report_labels tests/test_report_outputs.py::test_summary_coverage_includes_missing_summary_duration_impact -q` — 2 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 36 passed, 1 warning
- `bash scripts/ci_check.sh` — 43 passed, 1 warning; wrote `examples/trace-example.json`
