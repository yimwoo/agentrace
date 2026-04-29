# Design To Code Map

| Requirement | Source Sections | Code Targets | Tests |
|---|---|---|---|
| `R-001` capture what a developer needs to answer: what happened, in what order, why did it fail, what ch | D-02 | src/**/*.py | tests/**/*.py |
| `R-002` separate top-level run summary from per-event details | D-02 | src/**/*.py | tests/**/*.py |
| `R-003` support partial traces from incomplete or crashed runs | D-02 | src/**/*.py | tests/**/*.py |
| `R-004` "run": {}, | D-03 | src/**/*.py | tests/**/*.py |
| `R-005` Each event should share a small common envelope | D-05 | src/**/*.py | tests/**/*.py |
| `R-006` Optional references to larger payloads that should not be inlined in every event | D-07 | src/**/*.py | tests/**/*.py |
| `R-007` A compact run-level summary for quick inspection | D-08 | src/**/*.py | tests/**/*.py |
| `R-008` JSON summary should include event_count, ok_events, and total_duration_ms | D-13 | src/**/*.py | tests/**/*.py |
| `R-009` Markdown summary should include task, run_id, status, and timing overview | D-13 | src/**/*.py | tests/**/*.py |
