# Design To Code Map

| Requirement | Source Sections | Code Targets | Tests |
|---|---|---|---|
| `R-001` Coding agents can modify files, run shell commands, call tools, retry after failures, and produc | D-01 | src/**/*.py | tests/**/*.py |
| `R-002` Portfolio automation that must distinguish useful code work from documentation churn | D-02 | src/**/*.py | tests/**/*.py |
| `R-003` agentrace should provide an executable local workflow that ingests a structured agent trace, val | D-03 | src/**/*.py | tests/**/*.py |
| `R-004` The CLI normalizes the trace into a run model containing task metadata, tool calls, commands, ed | D-05 | src/**/*.py | tests/**/*.py |
| `R-005` The CLI emits JSON and Markdown reports that can be reviewed in a pull request or attached to a  | D-05 | src/**/*.py | tests/**/*.py |
| `R-006` The project must expose a trace validation API that accepts a trace object or JSONL event stream | D-06 | src/**/*.py | tests/**/*.py |
| `R-007` The project must define a stable event envelope with event id, timestamp, event type, status, ac | D-06 | src/**/*.py | tests/**/*.py |
| `R-008` The project must support at least these event families: model call, tool call, shell command, fi | D-06 | src/**/*.py | tests/**/*.py |
| `R-009` The project must normalize partial or crashed traces without discarding valid earlier events | D-06 | src/**/*.py | tests/**/*.py |
| `R-010` The project must compute a chronological run timeline from normalized events | D-06 | src/**/*.py | tests/**/*.py |
| `R-011` The project must identify failed commands, failed tests, failed edits, retry chains, and missing | D-06 | src/**/*.py | tests/**/*.py |
| `R-012` The project must expose a CLI command that reads an example trace file and writes JSON and Markd | D-06 | src/**/*.py | tests/**/*.py |
| `R-013` The project must include at least one realistic example trace fixture that exercises commands, e | D-06 | src/**/*.py | tests/**/*.py |
| `R-014` The project must include tests for validation errors, timeline ordering, failure extraction, ret | D-06 | src/**/*.py | tests/**/*.py |
| `R-015` The project must treat documentation-only or agent-ledger-only changes as TARGET_MISS for automa | D-06 | src/**/*.py | tests/**/*.py |
| `R-016` The code should prefer plain data structures and deterministic rendering so scheduled agents can | D-07 | src/**/*.py | tests/**/*.py |
| `R-017` A trace has a top-level run record and an ordered event list. The run record includes run id, ta | D-08 | src/**/*.py | tests/**/*.py |
| `R-018` The CLI must accept a trace path and output format flags | D-09 | src/**/*.py | tests/**/*.py |
| `R-019` The CLI should fail with a non-zero status when validation fails unless an explicit partial-mode | D-09 | src/**/*.py | tests/**/*.py |
| `R-020` The CLI should support writing reports to paths so CI or cron jobs can attach artifacts | D-09 | src/**/*.py | tests/**/*.py |
| `R-021` The CLI should provide a smoke-testable path using only files committed in the repository | D-09 | src/**/*.py | tests/**/*.py |
| `R-022` Scheduled AgentSpec runs for this repo must start from a bounded context pack. A successful impl | D-10 | src/**/*.py | tests/**/*.py |
| `R-023` Stabilize the trace validation API and failure-oriented run model | D-11 | src/**/*.py | tests/**/*.py |
| `R-024` Add comparison helpers for multiple runs after single-run inspection is reliable | D-11 | src/**/*.py | tests/**/*.py |
| `R-025` A developer can run one command against a trace fixture and understand what the agent did, where | D-12 | src/**/*.py | tests/**/*.py |
| `R-026` A scheduled agent run can attach an agentrace report that reviewers can inspect without reading  | D-12 | src/**/*.py | tests/**/*.py |
| `R-027` JSONL event streams or top-level JSON trace objects be the default interchange format? | D-13 | src/**/*.py | tests/**/*.py |
| `R-028` Which external agent log format should be adapted first? | D-13 | src/**/*.py | tests/**/*.py |
| `R-029` How strict should partial trace validation be when a run crashes before writing a final outcome? | D-13 | src/**/*.py | tests/**/*.py |
| `R-030` CLI behavior | D-09 | src/**/*.py | tests/**/*.py |
