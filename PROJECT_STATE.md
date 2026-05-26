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
- JSON and Markdown reports now surface command timing rows and file edit summaries with per-row net line deltas (including compact run-summary rows), a combined chronological command/edit activity timeline that renders command summaries when present with aggregate totals, grouped report summary coverage by command/edit/activity labels including per-command, per-command-working-directory, per-command-exit-code, per-edit-status, and per-file breakdowns, command summaries, command/edit/activity summary coverage counts/ratios with compact command/edit/activity summary example rows and missing-summary example rows, grouped activity type/status/duration-source/identity summary and missing-summary examples, grouped command identity/cwd/status and edit path/kind/status summary and missing-summary examples, repeated command/edit group summary coverage counts/ratios with nested missing-summary examples, exit-code-grouped command summary and missing-summary examples, command exit-code duration totals/averages/min-max extremes/coverage/shares plus dominant exit-code duration highlights and exit-code summary coverage, command and edit status-duration totals/averages/min-max extremes/coverage/shares with dominant status highlights, command working-directory duration totals/averages/min-max extremes/coverage/shares with dominant cwd highlights, edit-kind duration totals/averages/min-max extremes/coverage/shares with dominant kind highlights, per-type activity duration totals/averages/min-max extremes/coverage, per-status activity duration totals/averages/min-max extremes/coverage/shares, and edit first/largest/slowest/shortest/last highlights with timing context and edit summaries plus repeated-group duration coverage and status-duration totals/averages/min-max extremes/coverage/shares and dominant status highlights throughout nested command/edit totals.
- aggregate JSON and Markdown report totals now show grouped summary coverage, compact summary examples, repeated-group summary examples, timing/duration spreads, status/source shares, time windows, artifact context, and command/edit highlight context across command attempts, cwd totals, per-file changes, edit-kind totals, failed rows, and selected command/edit aggregate entries.
- failed-command aggregate rows and first/slowest/fastest/last command highlights include working-directory context in JSON and Markdown so selected command execution locations are visible without scanning detail rows
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
- make command duration, command summaries, summary coverage (including per-command and per-file sparse-summary checks), unique and repeated command activity, per-command attempt totals with timing/artifact context, command working-directory distribution and per-cwd timing/artifact totals with repeated-group first/last event references, failed command identities with timing/failure context, command exit-code distribution and dominant exit-code duration highlights, command status distribution, command and edit status-duration totals/averages/min-max extremes/shares with dominant status highlights, aggregate command/edit time windows, command/edit/activity duration recorded/missing counts and coverage ratios, command/edit/activity summary recorded/missing counts and coverage ratios, command/edit/activity duration totals, averages, and shares by duration source, command/edit/activity average recorded-only durations, command/edit/activity median, duration-range, and duration min/max-extremes metrics, chronological command/edit activity timeline with type/status/source/timing/span and per-type/per-status duration totals plus per-type/per-status averages, min/max extremes, and duration shares and dominant duration type/status shares, first activity, slowest activity, fastest activity, idle gap totals/averages/largest gaps, overlap totals/averages/largest overlaps plus overlap ratio, uncovered timeline span with uncovered interval windows/count/average/largest highlights, first failed plus all failed-activity identities, first/slowest/fastest/last command identities with timing and working-directory context, row-level duration source/start/end timestamp context (including normalized summary-only rows), edit status distribution/failures, edit-kind distribution and per-kind timing/line-impact/artifact totals with repeated-group first/last event references, failed edit identities with timing/error context, per-file change totals with timing/artifact context and repeated-group first/last event references, first/largest/shortest/last edit identities with timing and summary context, and file-change impact visible without opening raw events first

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
