# Security And Governance

Status: draft
Confidence: medium

## Source Sections

- `D-10` Automation policy

## Source-Backed Notes

### D-10 Automation policy

Source-backed.

## Automation policy

Scheduled AgentSpec runs for this repo must start from a bounded context pack. A successful implementation run must change at least one of `src/**`, `tests/**`, `examples/**`, or `TRACE_SCHEMA.md`. Supporting docs may be updated, but docs alone are not success.
