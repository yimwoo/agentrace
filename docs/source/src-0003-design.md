# agentrace design source

## Problem

Coding agents can modify files, run shell commands, call tools, retry after failures, and produce commits, but developers often cannot reconstruct what happened when a run succeeds partially, fails late, or lands a suspicious change. Existing logs are verbose, model-specific, and difficult to compare across runs. `agentrace` exists to make code-agent workflows inspectable, failure-oriented, and reproducible enough for debugging.

## Target users

- Developers using coding agents on real repositories.
- Maintainers reviewing autonomous or scheduled agent work.
- Tool builders who need a small, local trace format for agent runs.
- Portfolio automation that must distinguish useful code work from documentation churn.

## Product goal

`agentrace` should provide an executable local workflow that ingests a structured agent trace, validates its events, builds a run timeline, highlights failures and retries, and emits readable JSON and Markdown inspection reports.

## Non-goals

- Do not become a generic agent framework.
- Do not build a large hosted observability platform before the local trace workflow is useful.
- Do not treat handoff or ledger updates as product progress unless an executable trace capability changed.
- Do not add new report fields without tying them to a user-visible inspection or debugging flow.

## MVP workflow

The MVP workflow is local-first and file-based:

1. A user records or receives a trace file in JSON or JSONL form.
2. The CLI validates the trace envelope, event order, event timestamps, event types, and required fields.
3. The CLI normalizes the trace into a run model containing task metadata, tool calls, commands, edits, tests, retries, artifacts, and final outcome.
4. The CLI builds a timeline that makes failure points and retry chains visible.
5. The CLI emits JSON and Markdown reports that can be reviewed in a pull request or attached to a scheduled run summary.

## Requirements

- The project must expose a trace validation API that accepts a trace object or JSONL event stream and returns structured validation errors.
- The project must define a stable event envelope with event id, timestamp, event type, status, actor, summary, and optional artifact references.
- The project must support at least these event families: model call, tool call, shell command, file edit, test run, retry, artifact, and final outcome.
- The project must normalize partial or crashed traces without discarding valid earlier events.
- The project must compute a chronological run timeline from normalized events.
- The project must identify failed commands, failed tests, failed edits, retry chains, and missing final outcomes.
- The project must expose a CLI command that reads an example trace file and writes JSON and Markdown reports.
- The project must include at least one realistic example trace fixture that exercises commands, edits, tests, retry, and failure context.
- The project must include tests for validation errors, timeline ordering, failure extraction, retry extraction, and report generation.
- The project must treat documentation-only or agent-ledger-only changes as `TARGET_MISS` for automated repo-improvement runs.

## Architecture

`agentrace` remains a small Python project:

- `src/trace_schema.py` owns trace envelope validation and normalization helpers.
- `src/report_json.py` renders machine-readable inspection output.
- `src/report_markdown.py` renders human-readable summaries.
- `src/report_cli.py` provides the local CLI entry point.
- `examples/` contains trace fixtures and generated report examples.
- `tests/` verifies schema behavior, timeline behavior, failure extraction, CLI behavior, and report output.

The code should prefer plain data structures and deterministic rendering so scheduled agents can verify behavior without external services.

## Data model

A trace has a top-level run record and an ordered event list. The run record includes run id, task title, repository, branch, start time, end time, status, agent identity, model identity when available, and source commit when available. Events include a common envelope plus type-specific payloads. Artifact references point to larger files rather than embedding all content in every event.

## CLI behavior

- The CLI must accept a trace path and output format flags.
- The CLI should fail with a non-zero status when validation fails unless an explicit partial-mode flag is used.
- The CLI should support writing reports to paths so CI or cron jobs can attach artifacts.
- The CLI should provide a smoke-testable path using only files committed in the repository.

## Automation policy

Scheduled AgentSpec runs for this repo must start from a bounded context pack. A successful implementation run must change at least one of `src/**`, `tests/**`, `examples/**`, or `TRACE_SCHEMA.md`. Supporting docs may be updated, but docs alone are not success.

## Rollout plan

1. Stabilize the trace validation API and failure-oriented run model.
2. Add a realistic example trace and CLI smoke path.
3. Improve JSON and Markdown reports around timeline, retries, and failure context.
4. Add comparison helpers for multiple runs after single-run inspection is reliable.
5. Consider lightweight HTML output only after the local CLI workflow is useful.

## Success criteria

- A developer can run one command against a trace fixture and understand what the agent did, where it failed, and what changed.
- A scheduled agent run can attach an `agentrace` report that reviewers can inspect without reading raw logs.
- Tests verify validation, timeline extraction, failure extraction, and rendering behavior.
- Repeated automation produces product capability changes rather than endless report-field churn.

## Open questions

- Should JSONL event streams or top-level JSON trace objects be the default interchange format?
- Which external agent log format should be adapted first?
- How strict should partial trace validation be when a run crashes before writing a final outcome?
