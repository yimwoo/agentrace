# AGENTS.md

## Project purpose
`agentrace` is a developer tool for tracing, inspecting, and debugging code-agent workflows.

## Primary users
- developers using code agents
- teams experimenting with agent workflows
- builders of agent-based developer tools

## Current priorities
- create a clear trace/event model
- capture useful run artifacts: tool calls, commands, edits, tests, failures
- generate readable reports
- prefer visible usefulness over abstract overengineering

## Non-goals
- do not become a generic agent framework
- do not prioritize flashy UI before useful trace capture exists
- avoid random refactors unless they unlock clear user value

## Working rules for agents
1. Read `README.md`, `PROJECT_STATE.md`, `ROADMAP.md`, and `HANDOFF.md` before starting work.
2. Prefer practical improvements that increase observability, debuggability, or replay value.
3. If researching adjacent tools, extract concrete lessons and reflect them in repo docs.
4. Before ending a session, update `HANDOFF.md` and any state files affected by the work.
5. Keep docs aligned with actual repo state.

## Definition of meaningful progress
- a new trace event or capture capability
- improved report generation or summaries
- clearer failure inspection
- better example/demo artifacts
- architecture improvements directly supporting useful trace workflows

## Key files
- `README.md`: public project description
- `PROJECT_STATE.md`: current repo snapshot
- `ROADMAP.md`: next milestones
- `HANDOFF.md`: latest session handoff
- `DECISIONS.md`: important project decisions
- `RESEARCH_NOTES.md`: findings from adjacent tools and workflows
