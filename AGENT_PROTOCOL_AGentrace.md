# AGENT_PROTOCOL_AGentrace

You are running exactly ONE autonomous repo-improvement cycle for `agentrace`.
The goal is to land one concrete implementation artifact that makes agent tracing,
inspection, replay, or debugging more useful.

This repo is implementation-required. Planning and memory updates are secondary.
A run that does not improve a real project artifact should not be treated as success.

---

## Session contract

Every run must end in exactly one of these outcomes:

- **CODE_LANDED** — a meaningful project artifact was committed and pushed.
- **BLOCKED** — no safe meaningful change could be landed; blocker documented with evidence.
- **TARGET_MISS** — the run completed, but did not land a strong enough project artifact.

For `agentrace`, `CODE_LANDED` should normally include at least one of:
- `src/**`
- `tests/**`
- `examples/**`
- `TRACE_SCHEMA.md`

Updating only `HANDOFF.md`, `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, or other memory docs is not success.

---

## Required reading before action

Read, in order:
1. `AGENTS.md`
2. `README.md`
3. `PROJECT_STATE.md`
4. `ROADMAP.md`
5. `HANDOFF.md`
6. relevant files under `src/`, `tests/`, `examples/`, or `TRACE_SCHEMA.md`

Do not broad-replan the repo unless implementation reveals a real contradiction.

---

## Task selection rules

Pick exactly one small, implementable task.
Priority:
1. latest actionable item from `HANDOFF.md`
2. highest-leverage unchecked item in `ROADMAP.md`
3. a small prerequisite that unlocks one of the above

Good task types:
- add or refine trace/event schema
- add validator logic
- add replay/debug example artifacts
- add tests around trace behavior
- improve executable trace/report structure

Avoid:
- generic documentation churn
- broad architectural rewriting
- speculative framework-building
- unrelated refactors

---

## Verification rules

Before declaring `CODE_LANDED`, verify the changed artifact in a meaningful way.
Examples:
- run targeted tests
- validate schema/example compatibility
- run a small example/demo flow
- verify parser/validator behavior

If stronger verification is not yet possible, say exactly why.

---

## Commit quality rules

A successful run must change at least one strong project artifact.
Docs may be updated only as support for the landed artifact.

If only memory docs or handoff text changed, the correct outcome is `TARGET_MISS`, not `CODE_LANDED`.

---

## Cron architecture constraint

If this protocol is used inside a cron job with a pre-run script:
- the pre-run script is the only part allowed to mutate repo files, commit, or push
- the model summary phase must not perform extra edits
- never claim changes beyond the script output
- if the script output changed only memory docs, classify it as `TARGET_MISS`

---

## Desired output shape

Return a concise structured summary containing:
- `OUTCOME:` CODE_LANDED | BLOCKED | TARGET_MISS
- `TASK:` one sentence
- `CHANGED_FILES:` list
- `VERIFY:` command/check and result
- `PUSH:` success | failed | not attempted
- `NEXT:` one concrete next step
