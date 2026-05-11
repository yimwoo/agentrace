# App Build

Task type: `implementation`

Use this workflow for web, UI, and long-running app-build tasks.

1. Planner: expand the requirement into user-visible behavior, acceptance criteria, allowed paths, and required evidence.
2. Generator: run the external code agent or runner against the bounded context pack. AgentSpec does not own code generation.
3. Evaluator: review the implementation against requirements, tests, and runner evidence before completion.
4. For UI changes, require browser-oriented evidence such as screenshots, DOM snapshots, navigation traces, console logs, network logs, videos, or traces.
5. Record the evaluator verdict and cite requirement IDs in task completion summaries.
