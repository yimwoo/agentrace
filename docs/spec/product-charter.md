# Product Charter

Status: draft
Confidence: medium

## Source Sections

- `D-02` Target users
- `D-04` Non-goals
- `D-12` Success criteria

## Source-Backed Notes

### D-02 Target users

Source-backed.

## Target users

- Developers using coding agents on real repositories.
- Maintainers reviewing autonomous or scheduled agent work.
- Tool builders who need a small, local trace format for agent runs.
- Portfolio automation that must distinguish useful code work from documentation churn.

### D-04 Non-goals

Source-backed.

## Non-goals

- Do not become a generic agent framework.
- Do not build a large hosted observability platform before the local trace workflow is useful.
- Do not treat handoff or ledger updates as product progress unless an executable trace capability changed.
- Do not add new report fields without tying them to a user-visible inspection or debugging flow.

### D-12 Success criteria

Source-backed.

## Success criteria

- A developer can run one command against a trace fixture and understand what the agent did, where it failed, and what changed.
- A scheduled agent run can attach an `agentrace` report that reviewers can inspect without reading raw logs.
- Tests verify validation, timeline extraction, failure extraction, and rendering behavior.
- Repeated automation produces product capability changes rather than endless report-field churn.
