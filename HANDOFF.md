## Latest status
`agentrace` report rows now preserve human-readable command/edit summaries when producers attach them directly to canonical events. Command timing extracts `event.summary` after `command.summary`/`details.summary`, file-edit summaries extract `event.summary` after `change.summary`/`details.summary`, and run-summary fallbacks use the same precedence so JSON and Markdown reports do not classify top-level event summaries as missing.

## What was done
- created AgentSpec task `T-140` for top-level command/edit event-summary preservation
- taught command timing and run-summary command rows to read top-level event summaries as a fallback
- taught file-edit summary and run-summary edit rows to read top-level event summaries as a fallback
- refreshed regression coverage and `TRACE_SCHEMA.md` wording for summary-source precedence

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_includes_command_timing_and_edit_summary -q` — 1 passed
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
