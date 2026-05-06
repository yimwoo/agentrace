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
- JSON and Markdown reports now surface command timing rows and file edit summaries with per-row net line deltas (including compact run-summary rows), linked command-log/diff artifact references, row duration sources, available start/end timestamp context, command stdout/stderr previews, and edit error messages; summary-only fallback rows are normalized with derived durations/duration sources, safe defaults for omitted row identity/status/line fields, and computed edit net line deltas when older summaries omit those fields
- aggregate JSON and Markdown report totals now show command count/unique command count/command list/repeated commands/per-command attempt totals with duration-source counts and time windows/working-directory counts/total and average duration/failures/failed-command rows with timing and stderr context/status counts/duration source counts/time window/slowest command plus deduplicated changed-file count/list/per-file change totals with duration-source counts and time windows, edit failure/status counts/edit-kind counts, failed-edit rows with timing/error context, duration source counts/time window, added/removed lines, net line delta, total/average edit duration, largest edit by churn, and timing context for the selected slowest/largest aggregate entries
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
- make command duration, unique and repeated command activity, per-command attempt totals with timing context, command working-directory distribution, failed command identities with timing/failure context, command status distribution, aggregate command/edit time windows, slowest-command identity and timing context, row-level duration source/start/end timestamp context (including normalized summary-only rows), edit status distribution/failures, edit-kind distribution, failed edit identities with timing/error context, per-file change totals with timing context, largest edit and timing context, and file-change impact visible without opening raw events first

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
