# PROJECT_STATE.md

## Current phase
Bootstrap moving into first concrete trace spec

## What exists now
- initial README
- initial agent operating docs
- first concrete JSON trace example in `examples/trace-example.json`
- first practical trace schema checkpoint in `TRACE_SCHEMA.md`

## What is incomplete
- event capture implementation
- report generation in Markdown/HTML
- demo/example workflow runner
- actual code structure for ingestion and rendering

## Active focus
- turn the trace schema into a small code skeleton for emitting traces
- define the first Markdown summary/report shape
- preserve narrow scope around practical debugging value

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
