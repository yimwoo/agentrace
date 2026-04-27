PYTHON ?= python3

bootstrap:
	bash scripts/bootstrap_env.sh

test:
	bash scripts/run_tests.sh tests/test_trace_schema.py tests/test_report_outputs.py -q

smoke:
	bash scripts/smoke_check.sh

ci:
	bash scripts/ci_check.sh
