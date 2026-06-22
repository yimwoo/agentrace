`agentrace` reports now label summary row coverage versus summarized-duration share skew for command/edit report summaries. JSON and Markdown include `summary_text_coverage_duration_share_gap_label` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can filter no/low/medium/high normalized coverage-vs-duration-share skew without interpreting ratios manually.

Session notes:
- created AgentSpec task `T-237` for coverage-vs-duration-share skew labels
- added `summary_text_coverage_duration_share_gap_label` to JSON summary text metrics and rendered `coverage_duration_share_gap_label=` in Markdown
- refreshed regression expectations, schema/state docs, rich Markdown fixture, and this handoff

`agentrace` reports now expose normalized summary row coverage versus summarized-duration share skew for command/edit report summaries. JSON and Markdown include `summary_text_coverage_duration_share_delta_abs_ratio` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can compare skew severity across buckets with different baseline coverage/duration shares.

Session notes:
- created AgentSpec task `T-236` for normalized coverage-vs-duration-share skew metrics
- added `summary_text_coverage_duration_share_delta_abs_ratio` to JSON summary text metrics and rendered `coverage_duration_share_delta_abs_ratio=` in Markdown
- refreshed regression expectations, schema/state docs, rich Markdown fixture, and this handoff

`agentrace` reports now expose the absolute magnitude of summary row coverage versus summarized-duration share skew for command/edit report summaries. JSON and Markdown include `summary_text_coverage_duration_share_delta_abs` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can sort coverage/duration-share skew magnitude regardless of direction.

Session notes:
- created AgentSpec task `T-235` for coverage-vs-duration-share skew magnitude metrics
- added `summary_text_coverage_duration_share_delta_abs` to JSON summary text metrics and rendered `coverage_duration_share_delta_abs=` in Markdown
- refreshed regression expectations, schema/state docs, rich Markdown fixture, and this handoff

`agentrace` reports now expose summary row coverage versus summarized-duration share skew for command/edit report summaries. JSON and Markdown include `summary_text_coverage_duration_share_delta` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can tell whether summary coverage by row count over- or under-represents the duration share of summarized work.

Session notes:
- created AgentSpec task `T-234` for summary text coverage-vs-duration-share skew metrics
- added `summary_text_coverage_duration_share_delta` to JSON summary text metrics and rendered `coverage_duration_share_delta=` in Markdown
- refreshed regression expectations, schema/state docs, rich Markdown fixture, and this handoff

`agentrace` reports now expose summarized-row duration per summary character for command/edit report summaries. JSON and Markdown include `summary_text_summarized_duration_ms_per_char` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can sort terse summary coverage specifically over rows that actually have summaries.

Session notes:
- created AgentSpec task `T-233` for summarized-row duration-per-summary-character metrics
- added `summary_text_summarized_duration_ms_per_char` to JSON summary text metrics and rendered `summarized_duration_ms_per_char=` in Markdown
- refreshed regression expectations, schema/state docs, rich Markdown fixture, and this handoff

`agentrace` reports now expose duration per summary character for command/edit report summaries. JSON and Markdown include `summary_text_duration_ms_per_char` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can spot terse summaries over long recorded command/edit work by sorting the reciprocal of summary text density.

Session notes:
- created AgentSpec task `T-230` for summary text duration-per-character metrics
- added `summary_text_duration_ms_per_char` to JSON summary text metrics and rendered `duration_ms_per_char=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now name the average-duration gap direction between summarized and unsummarized rows for command/edit report summaries. JSON and Markdown include `summary_text_average_duration_gap_direction` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can see whether summarized rows, unsummarized rows, or neither bucket has the higher average duration without interpreting signed deltas manually.

Session notes:
- created AgentSpec task `T-229` for summary text average-duration gap direction labels
- added `summary_text_average_duration_gap_direction` to JSON summary text metrics and rendered `average_duration_gap_direction=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now rank normalized average-duration gap severity between summarized and unsummarized rows for command/edit report summaries. JSON and Markdown include `summary_text_average_duration_gap_rank` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can sort none/low/medium/high sparse-summary timing gaps numerically without parsing label text.

Session notes:
- created AgentSpec task `T-228` for summary text average-duration gap ranks
- added `summary_text_average_duration_gap_rank` to JSON summary text metrics and rendered `average_duration_gap_rank=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now label normalized average-duration gaps between summarized and unsummarized rows for command/edit report summaries. JSON and Markdown include `summary_text_average_duration_gap_label` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can filter none/low/medium/high sparse-summary timing gaps without interpreting ratios manually.

Session notes:
- created AgentSpec task `T-227` for summary text average-duration gap labels
- added `summary_text_average_duration_gap_label` to JSON summary text metrics and rendered `average_duration_gap_label=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now expose normalized absolute average-duration gaps between unsummarized and summarized rows for command/edit report summaries. JSON and Markdown include `summary_text_average_duration_delta_abs_ratio` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can compare sparse-summary timing gap magnitude across buckets with different timing scales.

Session notes:
- created AgentSpec task `T-226` for summary text average-duration absolute delta ratios
- added `summary_text_average_duration_delta_abs_ratio` to JSON summary text metrics and rendered `average_duration_delta_abs_ratio=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now expose absolute average-duration gaps between unsummarized and summarized rows for command/edit report summaries. JSON and Markdown include `summary_text_average_duration_delta_abs_ms` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can sort sparse-summary timing gaps by magnitude even when the signed delta changes direction.

Session notes:
- created AgentSpec task `T-225` for summary text average-duration absolute delta metrics
- added `summary_text_average_duration_delta_abs_ms` to JSON summary text metrics and rendered `average_duration_delta_abs_ms=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now expose the signed average-duration gap between unsummarized and summarized rows for command/edit report summaries. JSON and Markdown include `summary_text_average_duration_delta_ms` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can immediately see whether unsummarized work is slower or faster on average before detail scanning.

Session notes:
- created AgentSpec task `T-224` for summary text average-duration delta metrics
- added `summary_text_average_duration_delta_ms` to JSON summary text metrics and rendered `average_duration_delta_ms=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now expose average summarized and unsummarized row durations for command/edit report summaries. JSON and Markdown include `summary_text_summarized_average_duration_ms` and `summary_text_unsummarized_average_duration_ms` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can see whether missing summaries are concentrated in longer rows before detail scanning.

Session notes:
- created AgentSpec task `T-222` for summary text average duration split metrics
- added summarized and unsummarized average duration metrics to JSON summary text metrics and rendered `summarized_average_duration_ms=` and `unsummarized_average_duration_ms=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now expose summary-text duration share ratios for command/edit report summaries. JSON and Markdown include `summary_text_summarized_duration_ratio` and `summary_text_unsummarized_duration_ratio` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can compare summary coverage against the share of recorded time explained by summarized versus unsummarized rows before detail scanning.

Session notes:
- created AgentSpec task `T-220` for summary text duration share ratios
- added summarized and unsummarized duration ratios to JSON summary text metrics and rendered `summarized_duration_ratio=` and `unsummarized_duration_ratio=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now expose the timing denominators behind summary-text density for command/edit report summaries. JSON and Markdown include `summary_text_duration_ms`, `summary_text_summarized_duration_ms`, and `summary_text_unsummarized_duration_ms` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can see exactly which recorded durations back each summary-text density value before detail scanning.

Session notes:
- created AgentSpec task `T-219` for summary text duration denominators
- added total, summarized, and unsummarized duration denominators to JSON summary text metrics and rendered `duration_ms=`, `summarized_duration_ms=`, and `unsummarized_duration_ms=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now include summary-text density per summarized duration for command/edit report summaries. JSON and Markdown include `summary_text_chars_per_summarized_duration_ms` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can compare human-readable summary density against only rows that actually have summaries before detail scanning.

Session notes:
- created AgentSpec task `T-218` for summary text density per summarized duration
- added `summary_text_chars_per_summarized_duration_ms` to JSON summary text metrics and rendered `chars_per_summarized_duration_ms=` in Markdown
- refreshed regression expectations, rich Markdown fixture, schema/state docs, and this handoff

`agentrace` reports now include summary-text density per report row for command/edit report summaries. JSON and Markdown include `summary_text_chars_per_row` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can compare how much human-readable summary detail exists across all rows, including unsummarized rows, before detail scanning.

Session notes:
- created AgentSpec task `T-217` for summary text density per row
- added `summary_text_chars_per_row` to JSON summary text metrics and rendered `chars_per_row=` in Markdown
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now include summary-text density per duration for command/edit report summaries. JSON and Markdown include `summary_text_chars_per_duration_ms` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can compare how much human-readable summary detail exists relative to recorded command/edit timing before detail scanning.

Session notes:
- created AgentSpec task `T-216` for summary text density per duration
- added `summary_text_chars_per_duration_ms` to JSON summary text metrics and rendered `chars_per_duration_ms=` in Markdown
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now include summary-text missing ratios for command/edit report summaries. JSON and Markdown include `summary_text_missing_ratio` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can see the unsummarized share next to coverage ratios before scanning detail rows.

Session notes:
- created AgentSpec task `T-215` for command/edit summary text missing ratios
- added `summary_text_missing_ratio` to JSON summary text metrics and rendered `missing=` in Markdown
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now include summary-text coverage ratios for command/edit report summaries. JSON and Markdown include `summary_text_coverage_ratio` inside `report_summary_text_metrics` for command, edit, and combined activity rows, so reviewers can see the share of rows with human-readable summaries alongside raw character counts before detail scanning.

Session notes:
- created AgentSpec task `T-214` for command/edit summary text coverage ratios
- added `summary_text_coverage_ratio` to JSON summary text metrics and rendered `coverage=` in Markdown
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now quantify command/edit summary text length. JSON and Markdown include `report_summary_text_metrics` for command, edit, and combined activity rows, exposing summary text counts, total/average/min/max character lengths, and empty-summary counts so reviewers can spot absent or overly terse summaries before detail scanning.

Session notes:
- created AgentSpec task `T-213` for command/edit summary text metrics
- added `report_summary_text_metrics` to JSON reports and rendered it in Markdown
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now expose a sortable action-priority rank for missing-window gap comparison trigger-signal review actions. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_rank` next to the existing no/low/medium/high priority label, so reviewers can sort action priority numerically without parsing label text.

Session notes:
- created AgentSpec task `T-212` for trigger-signal review action priority ranks
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_rank` to JSON `report_summary_timing_window_impact`
- rendered and tested the new priority rank in Markdown reports
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now expose a review-priority label for missing-window gap comparison trigger-signal actions. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_label` next to the action label, so reviewers can distinguish no/low/medium/high priority action follow-up without recomputing the count-vs-duration signal delta.

Session notes:
- created AgentSpec task `T-211` for trigger-signal review action priority labels
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_priority_label` to JSON `report_summary_timing_window_impact`
- rendered and tested the new priority label in Markdown reports
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now expose a readable action label for missing-window gap comparison trigger-signal review actions. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_label` next to the copy-ready action enum, so reviewers can distinguish count-share, duration-share, and no-op action families without parsing command-style action text.

Session notes:
- created AgentSpec task `T-210` for trigger-signal review action labels
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal_action_label` to JSON `report_summary_timing_window_impact`
- rendered and tested the new action label in Markdown reports
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now expose a next review action for missing-window gap comparison trigger signals. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_trigger_signal_action` next to the trigger signal status, mapping count-led, duration-led, and balanced signal families to copy-ready review actions.

Session notes:
- created AgentSpec task `T-209` for trigger-signal review actions
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal_action` to JSON `report_summary_timing_window_impact`
- rendered and tested the new action in Markdown reports
- refreshed the rich Markdown fixture and documented the schema/state update

`agentrace` reports now expose a compact trigger-signal attention status for missing-window gap comparison attention. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_trigger_signal_status` next to the compact trigger signal required flag, so reviewers can filter no-attention versus attention-needed sparse-summary signal divergence without interpreting booleans alone.

## What was done
- created AgentSpec task `T-208` for missing-window gap comparison trigger signal statuses
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal_status` to JSON `report_summary_timing_window_impact`
- rendered the new trigger signal status in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — failed until the rich Markdown fixture was regenerated, then passed in the combined focused run
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose a compact trigger-signal required flag for missing-window gap comparison attention. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_trigger_signal_required` next to the compact signal rank, so reviewers can filter buckets where count-share or duration-share divergence actually drives a sparse-summary attention trigger.

## What was done
- created AgentSpec task `T-207` for missing-window gap comparison trigger signal required flags
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal_required` to JSON `report_summary_timing_window_impact`
- rendered the new trigger signal required flag in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — failed first while the required flag was missing, then 1 passed after implementation
- Full CI pending in current AgentSpec run

## Older status
`agentrace` reports now rank compact missing-window gap comparison attention trigger signals. JSON and Markdown expose `summary_missing_window_gap_delta_comparison_attention_trigger_signal_rank` beside the compact signal and readable signal-family label, so reviewers can sort no-signal, count-share-led, and duration-share-led divergence buckets without parsing enum text.

## What was done
- created AgentSpec task `T-206` for missing-window gap comparison trigger signal ranking
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal_rank` to JSON `report_summary_timing_window_impact`
- rendered the new trigger signal rank in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — failed first while the rank field was missing, then 1 passed after implementation
- Full CI pending in current AgentSpec run

## Older status
`agentrace` reports now label compact missing-window gap comparison attention trigger signals. JSON and Markdown expose `summary_missing_window_gap_delta_comparison_attention_trigger_signal_label` beside the compact `summary_missing_window_gap_delta_comparison_attention_trigger_signal`, so reviewers can keep the short `count_share` / `duration_share` / `none` grouping while also filtering on explicit signal-family labels.

## What was done
- created AgentSpec task `T-205` for missing-window gap comparison attention trigger signal labels
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal_label` to JSON `report_summary_timing_window_impact`
- rendered the new trigger signal label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- Full CI pending in current AgentSpec run

## Older status
`agentrace` reports now include a compact signal-family field for missing-window gap comparison attention triggers. JSON and Markdown expose `summary_missing_window_gap_delta_comparison_attention_trigger_signal` beside the verbose trigger enum for command, edit, and combined activity buckets, so reviewers can group divergence attention by `count_share`, `duration_share`, or `none` without parsing long trigger strings.

## What was done
- created AgentSpec task `T-204` for missing-window gap comparison attention trigger signals
- added `summary_missing_window_gap_delta_comparison_attention_trigger_signal` to JSON `report_summary_timing_window_impact`
- rendered the new trigger signal in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now name which sparse-summary signal triggers missing-window count-vs-duration gap attention. JSON and Markdown expose `summary_missing_window_gap_delta_comparison_attention_trigger` beside the existing attention status, required flag, rank, and label for command, edit, and combined activity buckets, so reviewers can distinguish count-share-led divergence from duration-share-led divergence without recomputing the signed comparison.

## What was done
- created AgentSpec task `T-203` for missing-window gap signal-divergence attention triggers
- added `summary_missing_window_gap_delta_comparison_attention_trigger` to JSON `report_summary_timing_window_impact`
- rendered the new comparison attention trigger in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — failed first because the trigger field was missing, then 1 passed after implementation
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — failed until the rich Markdown fixture was regenerated
- Full CI pending in current AgentSpec run

## Older status
`agentrace` reports now include a compact status for missing-window count-vs-duration gap divergence attention. JSON and Markdown expose `summary_missing_window_gap_delta_comparison_attention_status` beside the existing attention-required boolean, label, and rank for command, edit, and combined activity buckets, so reviewers can filter for explicit “attention needed” vs “no attention needed” states without interpreting booleans alone.

## What was done
- created AgentSpec task `T-202` for missing-window gap signal-divergence attention status
- added `summary_missing_window_gap_delta_comparison_attention_status` to JSON `report_summary_timing_window_impact`
- rendered the new comparison attention status in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed after RED failure and implementation
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- Full CI pending in current AgentSpec run

## Older status
`agentrace` reports now expose whether missing-window count-vs-duration gap divergence requires attention. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_required` alongside the existing comparison attention label and rank for command, edit, and combined activity buckets, so reviewers can filter buckets with any sparse-summary signal divergence without interpreting labels or ranks.

## What was done
- created AgentSpec task `T-201` for missing-window gap signal-divergence attention filtering
- added `summary_missing_window_gap_delta_comparison_attention_required` to JSON `report_summary_timing_window_impact`
- rendered the new comparison attention-required flag in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed after RED failure and implementation
- Full CI pending in current AgentSpec run

## Older status
`agentrace` reports now add a sortable attention rank for missing-window count-vs-duration gap divergence in the summary/timing-window impact block. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_rank` alongside the existing attention label for command, edit, and combined activity buckets, so reviewers can sort sparse-summary timestamp signal divergence by severity without parsing label text.

## What was done
- created AgentSpec task `T-200` for missing-window gap signal-divergence attention ranking
- added `summary_missing_window_gap_delta_comparison_attention_rank` to JSON `report_summary_timing_window_impact`
- rendered the new comparison attention rank in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- Full CI pending in current AgentSpec run

## Older status
`agentrace` reports now add an attention label for missing-window count-vs-duration gap divergence in the summary/timing-window impact block. JSON and Markdown include `summary_missing_window_gap_delta_comparison_attention_label` for command, edit, and combined activity buckets, so reviewers can tell whether sparse-summary timestamp gap signals have no, low, medium, or high count/duration disagreement before interpreting the source and comparison labels.

## What was done
- created AgentSpec task `T-199` for missing-window gap signal-divergence attention labeling
- added `summary_missing_window_gap_delta_comparison_attention_label` to JSON `report_summary_timing_window_impact`
- rendered the new comparison attention label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the rich Markdown fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now label the missing-window gap duration-vs-count comparison in the summary/timing-window impact block. JSON and Markdown include `summary_missing_window_gap_delta_comparison_label` for command, edit, and combined activity buckets, so reviewers can see whether sparse-summary timestamp gaps are duration-led, count-led, or balanced without interpreting the signed comparison manually.

## What was done
- created AgentSpec task `T-198` for missing-window gap comparison labeling
- added `summary_missing_window_gap_delta_comparison_label` to JSON `report_summary_timing_window_impact`
- rendered the new comparison label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — initially failed until the rich Markdown fixture was regenerated
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the absolute magnitude of the missing-window gap duration-vs-count comparison in the summary/timing-window impact block. JSON and Markdown include `summary_missing_window_gap_duration_minus_count_delta_abs` for command, edit, and combined activity buckets, so reviewers can see how far duration-share and count-share sparsity signals diverge regardless of which signal is larger.

## What was done
- created AgentSpec task `T-197` for missing-window gap comparison magnitude visibility
- added `summary_missing_window_gap_duration_minus_count_delta_abs` to JSON `report_summary_timing_window_impact`
- rendered the new absolute duration-minus-count gap delta in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now quantify disagreement between missing-window count-share and duration-share gaps in the summary/timing-window impact block. JSON and Markdown include `summary_missing_window_gap_duration_minus_count_delta` for command, edit, and combined activity buckets, so reviewers can tell whether the strongest missing-summary timestamp-sparsity signal is count-led, duration-led, or tied before reading the qualitative gap label.

## What was done
- created AgentSpec task `T-196` for missing-window gap signal comparison
- added `summary_missing_window_gap_duration_minus_count_delta` to JSON `report_summary_timing_window_impact`
- rendered the new gap duration-minus-count delta in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now name the source of the maximum missing-window summary gap in the summary/timing-window impact block. JSON and Markdown include `summary_missing_window_gap_source` for command, edit, and combined activity buckets, so reviewers can tell whether the strongest missing-summary timestamp-sparsity gap is driven by count share, duration share, both, or neither before reading the qualitative gap label.

## What was done
- created AgentSpec task `T-195` for missing-window gap source visibility
- added `summary_missing_window_gap_source` to JSON `report_summary_timing_window_impact`
- rendered the new gap source in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — initially failed until the rich Markdown fixture was regenerated
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the maximum positive missing-window gap delta in the summary/timing-window impact block. JSON and Markdown include `summary_missing_window_gap_delta_max` for command, edit, and combined activity buckets, so reviewers can quantify the strongest missing-summary timestamp-sparsity gap before reading the qualitative gap label.

## What was done
- created AgentSpec task `T-194` for missing-window gap delta visibility
- added `summary_missing_window_gap_delta_max` to JSON `report_summary_timing_window_impact`
- rendered the new maximum gap delta in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed after RED failure and implementation
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now include an attention label for complete-window count-delta imbalance in the summary/timing-window impact block. JSON and Markdown expose `summary_complete_window_count_delta_attention_label` for command, edit, and combined activity buckets, so reviewers can distinguish no, low, medium, and high complete-window row-count imbalance without interpreting the normalized share manually.

## What was done
- created AgentSpec task `T-193` for complete-window count-delta attention labeling
- added `summary_complete_window_count_delta_attention_label` to JSON `report_summary_timing_window_impact`
- rendered the new count-delta attention label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now label the signed complete-window count-delta in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_count_delta_label` for command, edit, and combined activity buckets, so reviewers can immediately tell whether fully timestamped row-count imbalance favors missing-summary rows, recorded-summary rows, or is balanced.

## What was done
- created AgentSpec task `T-192` for complete-window count-delta labeling
- added `summary_complete_window_count_delta_label` to JSON `report_summary_timing_window_impact`
- rendered the new count-delta label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the signed complete-window count-delta share in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_count_delta_share` for command, edit, and combined activity buckets, so reviewers can see whether fully timestamped row-count imbalance favors missing-summary or recorded-summary rows with the same denominator as the absolute count-delta share.

## What was done
- created AgentSpec task `T-191` for signed complete-window count-delta share visibility
- added `summary_complete_window_count_delta_share` to JSON `report_summary_timing_window_impact`
- rendered the new signed count-delta share in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed after RED failure and implementation
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the complete-window-normalized share of the absolute complete-window count delta in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_count_delta_abs_share` for command, edit, and combined activity buckets, so reviewers can see how large the complete-window count imbalance is relative to all complete-window rows in that bucket.

## What was done
- created AgentSpec task `T-190` for complete-window count-delta absolute-share visibility
- added `summary_complete_window_count_delta_abs_share` to JSON `report_summary_timing_window_impact`
- rendered the new absolute count-delta share in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed after RED failure and implementation
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the absolute magnitude of the signed complete-window count delta in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_count_delta_abs` for command, edit, and combined activity buckets, so reviewers can see count-imbalance size even when direction differs between missing-summary and recorded-summary rows.

## What was done
- created AgentSpec task `T-189` for complete-window count-delta magnitude visibility
- added `summary_complete_window_count_delta_abs` to JSON `report_summary_timing_window_impact`
- rendered the new absolute count delta in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the signed complete-window count delta in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_count_delta` for command, edit, and combined activity buckets, so reviewers can see whether fully timestamped row counts favor missing-summary or recorded-summary rows before comparing share and duration deltas.

## What was done
- created AgentSpec task `T-188` for signed complete-window count-delta visibility
- added `summary_complete_window_count_delta` to JSON `report_summary_timing_window_impact`
- rendered the new count delta in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed after RED failure and implementation
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose complete-window summary coverage deltas in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_share_delta`, `summary_complete_window_duration_share_delta`, and `summary_complete_window_coverage_label` for command, edit, and combined activity buckets, so reviewers can tell whether fully timestamped coverage is stronger for missing-summary rows, stronger for recorded-summary rows, or balanced before comparing incomplete-window sparsity.

## What was done
- created AgentSpec task `T-186` for complete-window summary coverage delta visibility
- added complete-window count-share and duration-share deltas to JSON `report_summary_timing_window_impact`
- rendered the new deltas and coverage label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now label complete-window duration ratios in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_duration_ratio_label` next to `summary_complete_window_duration_ratio` for command, edit, and combined activity buckets, so reviewers can distinguish no complete-window duration, recorded-summary-only complete duration, missing-summary-only complete duration, and balanced/elevated/dominant complete-window duration without interpreting the raw ratio alone.

## What was done
- created AgentSpec task `T-185` for complete-window duration ratio labeling
- added `summary_complete_window_duration_ratio_label` to JSON `report_summary_timing_window_impact`
- rendered the new complete-window duration ratio label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed after RED failure and implementation
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the complete-window duration ratio in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_duration_ratio` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can compare unsummarized complete-window duration against summarized complete-window duration without recalculating from the raw duration totals.

## What was done
- created AgentSpec task `T-184` for complete-window duration ratio visibility
- added `summary_complete_window_duration_ratio` to JSON `report_summary_timing_window_impact`
- rendered the new complete-window duration ratio in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the signed share of complete-window duration imbalance in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_duration_delta_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see whether fully timestamped duration imbalance favors missing-summary or recorded-summary rows with the same normalized denominator as the absolute complete-window share.

## What was done
- created AgentSpec task `T-183` for signed complete-window duration-delta share visibility
- added `summary_complete_window_duration_delta_share` to JSON `report_summary_timing_window_impact`
- rendered the new signed complete-window duration-delta share in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now normalize the absolute magnitude of the signed complete-window duration delta in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_duration_delta_abs_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see what share of all fully timestamped duration is represented by the complete-window summary imbalance.

## What was done
- created AgentSpec task `T-182` for summary/timing-window complete-window duration-delta absolute-share visibility
- added `summary_complete_window_duration_delta_abs_share` to JSON `report_summary_timing_window_impact`
- rendered the new complete-window absolute duration-delta share in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the absolute magnitude of the signed complete-window duration delta in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_duration_delta_abs_ms` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see the size of complete timestamp-window duration imbalance regardless of whether it favors missing-summary or recorded-summary rows.

## What was done
- created AgentSpec task `T-181` for summary/timing-window complete-window duration-delta magnitude visibility
- added `summary_complete_window_duration_delta_abs_ms` to JSON `report_summary_timing_window_impact`
- rendered the new complete-window absolute duration delta in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now label the signed complete-window duration delta in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_duration_delta_label` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can immediately tell whether complete timestamp-window duration is heavier for missing-summary rows, heavier for recorded-summary rows, or balanced without interpreting the signed millisecond value alone.

## What was done
- created AgentSpec task `T-180` for summary/timing-window complete-window duration delta labeling
- added `summary_complete_window_duration_delta_label` to JSON `report_summary_timing_window_impact`
- rendered the new complete-window duration delta label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the signed complete-window duration delta in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_duration_delta_ms` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see whether fully timestamped duration is heavier for missing-summary rows or recorded-summary rows before comparing incomplete-window imbalance.

## What was done
- created AgentSpec task `T-179` for summary/timing-window complete-window duration delta visibility
- added `summary_complete_window_duration_delta_ms` to JSON `report_summary_timing_window_impact`
- rendered the new complete-window duration delta in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose complete-window duration totals alongside incomplete-window duration totals in the summary/timing-window impact block. JSON and Markdown include `summary_complete_window_duration_total_ms` and `summary_complete_window_duration_total_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can compare the complete timestamp-window duration denominator against incomplete-window duration before interpreting normalized summary coverage imbalance.

## What was done
- created AgentSpec task `T-178` for summary/timing-window complete-window duration total visibility
- added `summary_complete_window_duration_total_ms` and `summary_complete_window_duration_total_share` to JSON `report_summary_timing_window_impact`
- rendered the new complete-window duration total metrics in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the share of total bucket duration occupied by incomplete timestamp windows in the summary/timing-window impact block. JSON and Markdown include `summary_missing_window_duration_total_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see how large the recorded-summary plus missing-summary incomplete-window denominator is relative to all summarized plus unsummarized row duration before interpreting normalized imbalance shares.

## What was done
- created AgentSpec task `T-177` for summary/timing-window incomplete-window duration total-share visibility
- added `summary_missing_window_duration_total_share` to JSON `report_summary_timing_window_impact`
- rendered the new duration-total share in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the total incomplete-window duration denominator used by signed and absolute summary/timestamp-window imbalance shares. JSON and Markdown include `summary_missing_window_duration_total_ms` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see the raw recorded-summary plus missing-summary incomplete-window duration behind normalized delta shares.

## What was done
- created AgentSpec task `T-176` for summary/timing-window duration denominator visibility
- added `summary_missing_window_duration_total_ms` to JSON `report_summary_timing_window_impact`
- rendered the new duration-total denominator in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the signed share of missing-window duration imbalance in the summary/timestamp-window impact block. JSON and Markdown include `summary_missing_window_duration_delta_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see both direction and normalized magnitude of the incomplete-window duration imbalance between missing-summary and recorded-summary rows.

## What was done
- created AgentSpec task `T-175` for signed missing-window duration-delta share visibility
- added `summary_missing_window_duration_delta_share` to JSON `report_summary_timing_window_impact`
- rendered the new signed duration-delta share in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now normalize the absolute signed missing-window duration delta in the summary/timestamp-window impact block. JSON and Markdown include `summary_missing_window_duration_delta_abs_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see what share of all incomplete-window duration is represented by the imbalance between missing-summary and recorded-summary rows.

## What was done
- created AgentSpec task `T-174` for summary/timing-window absolute duration-delta share visibility
- added `summary_missing_window_duration_delta_abs_share` to JSON `report_summary_timing_window_impact`
- rendered the new absolute signed-delta share in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose the absolute magnitude of the signed missing-window duration delta in the summary/timestamp-window impact block. JSON and Markdown include `summary_missing_window_duration_delta_abs_ms` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see the size of the incomplete-window duration imbalance regardless of whether it favors missing-summary or recorded-summary rows.

## What was done
- created AgentSpec task `T-173` for summary/timing-window signed duration-delta magnitude visibility
- added `summary_missing_window_duration_delta_abs_ms` to JSON `report_summary_timing_window_impact`
- rendered the new absolute signed-delta magnitude in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now label the signed missing-window duration delta in the summary/timestamp-window impact block. JSON and Markdown include `summary_missing_window_duration_delta_label` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can immediately tell whether incomplete timestamp-window duration is heavier for missing-summary rows, heavier for recorded-summary rows, or balanced without interpreting the signed millisecond value alone.

## What was done
- created AgentSpec task `T-172` for summary/timing-window signed duration-delta labeling
- added `summary_missing_window_duration_delta_label` to JSON `report_summary_timing_window_impact`
- rendered the new signed duration-delta label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now show the signed raw missing-window duration delta in the summary/timestamp-window impact block. JSON and Markdown include `summary_missing_window_duration_delta_ms` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see whether incomplete timestamp-window duration is heavier for missing-summary rows or recorded-summary rows before interpreting positive excess-only fields.

## What was done
- created AgentSpec task `T-171` for summary/timing-window signed duration-delta visibility
- added `summary_missing_window_duration_delta_ms` to JSON `report_summary_timing_window_impact`
- rendered the new signed duration delta in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now label the missing-summary timestamp-window duration ratio in the summary/timestamp-window impact block. JSON and Markdown include `summary_missing_window_duration_ratio_label` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can tell whether incomplete-window duration is absent, summary-only, missing-summary-only, balanced, elevated, or dominant without interpreting the raw ratio first.

## What was done
- created AgentSpec task `T-170` for summary/timing-window duration-ratio labeling
- added `summary_missing_window_duration_ratio_label` to JSON `report_summary_timing_window_impact`
- rendered the new ratio label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now expose a missing-window duration ratio in the summary/timestamp-window impact block. JSON and Markdown include `summary_missing_window_duration_ratio` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see how much larger unsummarized incomplete-window duration is than summarized incomplete-window duration without calculating the ratio manually.

## What was done
- created AgentSpec task `T-169` for summary/timing-window missing-duration ratio visibility
- added `summary_missing_window_duration_ratio` to JSON `report_summary_timing_window_impact`
- rendered the new ratio in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now quantify how much positive missing-summary incomplete-window duration excess occupies the unsummarized incomplete-window bucket. JSON and Markdown include `summary_missing_window_excess_missing_duration_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can tell whether excess sparse unsummarized duration is the whole missing-window problem or only a portion of it.

## What was done
- created AgentSpec task `T-168` for summary/timing-window excess missing-duration share visibility
- added `summary_missing_window_excess_missing_duration_share` to JSON `report_summary_timing_window_impact`
- rendered the new excess missing-duration share metric in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence -q` — 1 passed
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 1 passed after refreshing the fixture
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now normalize positive missing-summary incomplete-window excess duration by the count-excess rows. JSON and Markdown include `summary_missing_window_excess_average_duration_ms` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see the per-excess-row duration weight behind sparse unsummarized timestamp windows instead of reading only total excess milliseconds.

## What was done
- created AgentSpec task `T-167` for summary/timing-window excess average-duration visibility
- added `summary_missing_window_excess_average_duration_ms` to JSON `report_summary_timing_window_impact`
- rendered the new excess average-duration metric in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now label positive missing-summary incomplete-window excess. JSON and Markdown include `summary_missing_window_excess_attention_label` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can triage whether count or duration excess around unsummarized incomplete timestamp windows is none, low, medium, or high without interpreting raw shares first.

## What was done
- created AgentSpec task `T-166` for summary/timing-window excess attention labels
- added `summary_missing_window_excess_attention_label` to JSON `report_summary_timing_window_impact`
- rendered the new excess attention label in Markdown reports
- refreshed regression expectations, rich Markdown fixture, `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
`agentrace` reports now quantify positive missing-summary incomplete-window count excess. JSON and Markdown include `summary_missing_window_excess_count` and `summary_missing_window_excess_share` inside `report_summary_timing_window_impact` for command, edit, and combined activity buckets, so reviewers can see whether unsummarized rows have more incomplete timestamp windows by count before reading duration-only impact.

## What was done
- created AgentSpec task `T-165` for summary/timing-window excess-count visibility
- added `summary_missing_window_excess_count` and `summary_missing_window_excess_share` to JSON `report_summary_timing_window_impact`
- rendered the new excess-count metrics in Markdown reports
- refreshed regression expectations plus `TRACE_SCHEMA.md`, `PROJECT_STATE.md`, and this handoff

## Verification
- `PYTHONPATH=. python3 -m pytest tests/test_report_outputs.py::test_report_summary_timing_window_impact_splits_complete_windows_by_summary_presence tests/test_report_outputs.py::test_markdown_report_matches_rich_trace_fixture -q` — 2 passed
- `bash scripts/ci_check.sh` — 46 passed, 1 warning; wrote `examples/trace-example.json`

## Older status
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
