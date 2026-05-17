# PROJECT_STATE.md

## Current phase
Bootstrap moving into first concrete trace spec

## What exists now
- initial README
- initial agent operating docs
- first concrete JSON trace example in `examples/trace-example.json` using the `trace_version` / `run` / `summary` shape
- first practical trace schema checkpoint in `TRACE_SCHEMA.md`
- AgentSpec artifacts bootstrapped under `.agentspec/`, `agent/`, `docs/`, and `reports/`
- compact run-level summary extraction for JSON and Markdown reports
- JSON and Markdown reports now surface command timing rows and file edit summaries with per-row net line deltas (including compact run-summary rows), a combined chronological command/edit activity timeline with aggregate totals, per-type activity duration totals, per-status activity duration totals and duration shares, dominant duration status/share, dominant duration type/share, first-activity, slowest-activity, fastest-activity, last-activity, timeline span duration, merged covered-duration/uncovered-duration/coverage-ratio/idle-ratio/covered interval windows/covered interval counts/uncovered interval totals, uncovered interval windows plus uncovered interval count, average uncovered interval duration, and largest uncovered interval highlights, total-idle-gap, average-idle-gap, largest-idle-gap, total-overlap, average-overlap, overlap-ratio, and largest-overlap highlights, failed-activity identities plus first-failed-activity highlights, command exit-code distributions, command stdout/stderr previews, linked command-log/diff artifact references in detail rows, nested aggregate command/edit totals, failed aggregate rows, command/edit/activity median and duration-range metrics, the selected first-command/slowest-command/fastest-command/last-command and first-edit/largest-edit/shortest-edit/last-edit aggregate highlights, row duration sources, available start/end timestamp context, command stdout/stderr previews, edit error messages, and first/last event references for repeated nested aggregate groups; summary-only fallback rows are normalized with derived durations/duration sources, safe defaults for omitted row identity/status/line fields, and computed edit net line deltas when older summaries omit those fields
- aggregate JSON and Markdown report totals now show command count/unique command count/command list/repeated commands/per-command attempt totals with duration-source counts, time windows, and artifact context/working-directory counts and per-cwd timing totals with repeated-group first/last event references, artifact context/total, average, and median duration/failures/failed-command rows with timing, stderr, and artifact context/status counts/duration source counts/time window/slowest and fastest command highlights plus deduplicated changed-file count/list/per-file change totals with repeated-group first/last event references, duration-source counts, time windows, and artifact context, edit failure/status counts/edit-kind counts and per-kind timing/line-impact totals with repeated-group first/last event references and artifact context, failed-edit rows with timing/error/artifact context, duration source counts/time window, added/removed lines, net line delta, total/average/median edit duration, largest edit by churn, shortest edit by duration, and timing context for the selected command/edit aggregate entries
- a rich Markdown report fixture demonstrates command timing with cwd, per-row duration source, edit summaries, aggregate report totals, and test-result context

## What is incomplete
- event capture implementation
- report generation in HTML
- demo/example workflow runner
- actual capture/ingestion code beyond the current schema/report helpers

## Active focus
- turn the trace schema into a small code skeleton for emitting traces
- define the first Markdown summary/report shape
- preserve narrow scope around practical debugging value
- keep report summaries aligned with `TRACE_SCHEMA.md` quick-inspection fields
- make command duration, unique and repeated command activity, per-command attempt totals with timing/artifact context, command working-directory distribution and per-cwd timing/artifact totals with repeated-group first/last event references, failed command identities with timing/failure context, command exit-code distribution, command status distribution, aggregate command/edit time windows, command/edit/activity median and duration-range metrics, chronological command/edit activity timeline with type/status/source/timing/span and per-type/per-status duration totals plus per-type/per-status duration shares and dominant duration type/status shares, first activity, slowest activity, fastest activity, idle gap totals/averages/largest gaps, overlap totals/averages/largest overlaps plus overlap ratio, uncovered timeline span with uncovered interval windows/count/average/largest highlights, first failed plus all failed-activity identities, first/slowest/fastest/last command identities and timing context, row-level duration source/start/end timestamp context (including normalized summary-only rows), edit status distribution/failures, edit-kind distribution and per-kind timing/line-impact/artifact totals with repeated-group first/last event references, failed edit identities with timing/error context, per-file change totals with timing/artifact context and repeated-group first/last event references, first/largest/shortest/last edit identities and timing context, and file-change impact visible without opening raw events first

## Risks / blockers
- risk of becoming too abstract or framework-heavy
- risk of building generic telemetry without coding-agent-specific value
- risk of adding schema complexity before capture and reporting exist

## Current success definition
A user can inspect a coding-agent run and understand what happened across tools, commands, edits, tests, and outcomes.

## First concrete artifact target
- define a minimal JSON trace example
- define one Markdown summary example
- keep schema tied to debugging questions, not generic spans

## Trace schema checkpoint
- minimum run metadata defined
- minimum event envelope defined
- minimum event types defined: model_call, tool_call, command, file_edit, test_result, note
- run summary fields defined for fast inspection
