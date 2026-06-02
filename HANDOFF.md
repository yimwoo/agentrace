## Latest status
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
