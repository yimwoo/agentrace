## Latest status
`agentrace` reports now include a top-level `report_summary_duration_impact` block/line. It totals summarized vs. unsummarized duration for command rows, edit rows, and combined activity rows so reviewers can prioritize high-duration rows that lack human-readable summaries before scanning detail sections.

## What was done
- created AgentSpec task `T-116` for a report summary-duration-impact follow-up slice
- added JSON `report_summary_duration_impact` with command/edit/activity summarized vs. unsummarized duration totals and missing-duration share
- rendered the duration-impact line near the top of Markdown summaries next to `report_summary_coverage`
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the new top-level sparse-summary duration signal

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 36 passed, 1 warning
- `bash scripts/ci_check.sh` — 43 passed, 1 warning

## Previous status
`agentrace` report inspection targets now carry explicit timing windows when source rows have them. Failed activity, missing timing/summary targets, and slowest-activity targets preserve `started_at`/`ended_at` in JSON and render that context in Markdown, making the prioritized inspection list line up with the activity timeline and command/edit detail rows.

## What was done
- created AgentSpec task `T-115` for a small report inspection-target timing follow-up slice
- added start/end timestamp preservation to `report_inspection_targets`
- rendered inspection-target start/end timing in Markdown report summaries
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for the inspection-target timing context
- completed AgentSpec task `T-115` via completion run `complete-t-115-add-command-timing-and-edit-summaries-to-reports-20260528040319621662` after the autonomous run recorded a stale pause finding

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 35 passed, 1 warning
- `bash scripts/ci_check.sh` — 42 passed, 1 warning

## Previous status
`agentrace` reports now include prioritized inspection targets near the top of JSON and Markdown output. The new `report_inspection_targets` block points reviewers first to failed command/edit activity, missing command/edit timing, missing command/edit summaries, and the slowest activity, while preserving identity, timing source, status, cwd/exit-code or edit-kind/net-line context, error previews, and linked artifacts when present.

## What was done
- created AgentSpec task `T-114` for a report observability follow-up slice after prior attention-gated runs remained present
- added JSON `report_inspection_targets` derived from command timing, edit summaries, and the activity timeline
- rendered `report_inspection_targets` in the Markdown top-level summary before coverage totals
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for prioritized inspection-target visibility
- completed AgentSpec run `t-114-add-command-timing-and-edit-summaries-to-reports-20260527230023954893`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 35 passed, 1 warning
- `bash scripts/ci_check.sh` — 42 passed, 1 warning

## Previous status
`agentrace` report artifact references now merge top-level artifact links with inline per-event artifact arrays. Command/edit rows and their compact summary or missing-summary examples normalize both sources into deduplicated `{kind, path}` refs, and Markdown renders the merged artifact context so aggregate examples can point at every supporting command log, stdout/stderr capture, or diff.

## What was done
- created AgentSpec task `T-112` for a report observability follow-up slice after prior halted runs remained attention-gated
- normalized inline per-event artifact arrays alongside top-level `artifacts[].event_id` links for command and edit report rows
- deduplicated merged artifact refs and preserved them in compact summary/missing-summary examples and Markdown rendering
- refreshed regression coverage, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for merged artifact-ref visibility
- completed AgentSpec run `t-112-add-command-timing-and-edit-summaries-to-reports-20260527130109132007`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 35 passed, 1 warning
- `bash scripts/ci_check.sh` — 42 passed, 1 warning

## Previous status
`agentrace` aggregate command and edit summaries now include grouped summary and missing-summary examples by duration source. JSON `command_timing_summary` and `edit_summary_totals` expose `duration_source_summary_examples` plus `duration_source_summary_missing_examples`; Markdown renders both so reviewers can see representative explained and unexplained explicit/derived/missing-timing rows without scanning detail rows.

## What was done
- created AgentSpec task `T-110` for a report observability follow-up slice after prior halted runs remained attention-gated
- added command and edit duration-source grouped summary and missing-summary examples to JSON report totals
- rendered command/edit duration-source grouped summary examples in Markdown top-level report summaries
- refreshed regression coverage, the rich Markdown fixture, `TRACE_SCHEMA.md`, and `PROJECT_STATE.md` for duration-source grouped example visibility
- completed AgentSpec run `t-110-add-command-timing-and-edit-summaries-to-reports-20260527040037597025`

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py -q` — 35 passed, 1 warning
- `bash scripts/ci_check.sh` — 42 passed, 1 warning
