# AGENT_PROTOCOL_AGentrace

You are running exactly ONE autonomous repo-improvement cycle for `agentrace`.
The goal is to land one concrete improvement that makes agent tracing, inspection,
replay, or debugging more useful.

This repo is implementation-first. Prefer code, schema, tests, examples, or
report-generation improvements over general planning.

---

## Session contract

Every run must end in exactly one of these outcomes:

- **CODE_LANDED** — a meaningful repo change was committed and pushed.
- **BLOCKED** — no safe meaningful change could be landed; blocker documented with evidence.
- **TARGET_MISS** — the run completed, but only weak/doc-only changes were available, so no success claim.

A valid successful run should usually include at least one of:
- source code change
- schema change
- test improvement
- example/demo artifact improvement
- report/output structure improvement

Doc-only changes are not a strong success unless they directly define or unblock a near-term implementation artifact such as a trace schema, event contract, or executable example.

---

## Required reading before action

Read, in order:
1. `AGENTS.md`
2. `README.md`
3. `PROJECT_STATE.md`
4. `ROADMAP.md`
5. `HANDOFF.md`
6. any directly relevant source/example/schema files for the selected task

Do not broad-replan the repo unless implementation reveals a real contradiction.

---

## Task selection rules

Pick exactly one small, implementable task.
Priority:
1. latest actionable item from `HANDOFF.md`
2. highest-leverage unchecked item in `ROADMAP.md`
3. a small prerequisite that unlocks one of the above

Good task types for `agentrace`:
- add or refine trace/event schema
- improve trace capture artifact structure
- improve examples or replay/debug flows
- add validation logic
- improve report readability tied to actual artifacts
- add or sharpen tests around tracing behavior

Avoid:
- generic documentation churn
- broad architectural rewriting
- speculative framework-building
- unrelated refactors

---

## Execution rules

- Make the smallest useful change that advances one concrete tracing/debugging capability.
- Prefer executable artifacts over narrative text.
- If editing docs, keep them tightly coupled to the implemented artifact.
- Do not claim improvements that are not present in the repo.
- Do not leave the repo dirtier than you found it.

---

## Verification rules

Before declaring success, verify the changed artifact in the smallest meaningful way available.
Examples:
- run targeted tests
- validate schema/examples
- run a demo/example command
- check generated output structure

If no test harness exists, perform the smallest executable check available and record the limitation in `HANDOFF.md`.

---

## Blocker rules

Use **BLOCKED** only if all are true:
- you identified a specific task
- you inspected relevant files
- you can name the exact blocker
- you can cite evidence
- you can state the next action needed

Valid blockers include:
- missing dependency/tool required for verification
- contradictory repo state
- ambiguous requirement that would risk wrong implementation
- broken baseline preventing safe change isolation

---

## Commit quality rules

A successful run should produce a commit that reflects a concrete repo improvement.
Prefer commits that include implementation artifact(s) plus any necessary state-file updates.

A weak run should not be disguised as success.
If only minor notes/handoff text changed, classify the outcome as `TARGET_MISS` or `BLOCKED`, not `CODE_LANDED`.

---

## Required end-of-run updates

When you complete meaningful work, update only the repo memory files actually affected:
- `PROJECT_STATE.md`
- `HANDOFF.md`
- `DECISIONS.md` if a real project decision changed
- `RESEARCH_NOTES.md` only if external findings materially informed the change
- `README.md` only if public-facing behavior/positioning changed

Keep updates concise and consistent with the landed artifact.

---

## Cron architecture constraint

If this protocol is used inside a cron job with a pre-run script:
- the pre-run script is the only part allowed to mutate repo files, commit, or push
- the model summary phase must not perform extra edits
- never claim changes beyond the script output
- if the script output is weak, say so plainly

---

## Desired output shape

Return a concise structured summary containing:
- `OUTCOME:` CODE_LANDED | BLOCKED | TARGET_MISS
- `TASK:` one sentence
- `CHANGED_FILES:` list
- `VERIFY:` command/check and result
- `PUSH:` success | failed | not attempted
- `NEXT:` one concrete next step
