# Runtime Architecture

Status: draft
Confidence: medium

## Source Sections

- `D-07` Architecture

## Source-Backed Notes

### D-07 Architecture

Source-backed.

## Architecture

`agentrace` remains a small Python project:

- `src/trace_schema.py` owns trace envelope validation and normalization helpers.
- `src/report_json.py` renders machine-readable inspection output.
- `src/report_markdown.py` renders human-readable summaries.
- `src/report_cli.py` provides the local CLI entry point.
- `examples/` contains trace fixtures and generated report examples.
- `tests/` verifies schema behavior, timeline behavior, failure extraction, CLI behavior, and report output.

The code should prefer plain data structures and deterministic rendering so scheduled agents can verify behavior without external services.
