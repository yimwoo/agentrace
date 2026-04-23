# DECISIONS.md

## 2026-04-23 — Repo created as primary portfolio project
- Decision: make `agentrace` the main active build in the portfolio.
- Why: strongest mix of trend relevance, practical pain, and direct usefulness while building with code agents.
- Implication: prioritize visible observability/debugging value over broad framework ambitions.

## 2026-04-23 — First schema should be event-oriented and debugging-first
- Decision: define the initial trace format around a top-level run object plus ordered events, artifacts, and a compact summary.
- Why: developers debugging agent workflows need sequence, failure location, changed files, and inspection targets more than generic framework concepts.
- Implication: prioritize command, tool, file-edit, and test events before adding richer hierarchy or distributed tracing features.
