import argparse
import json
import sys
from pathlib import Path

from src.report_json import build_json_summary
from src.report_markdown import build_markdown_summary


FORMAT_CHOICES = ("markdown", "json")


def load_trace(path="-"):
    """Load a trace JSON document from a file path or stdin.

    A small library entrypoint makes report rendering usable outside tests and
    avoids forcing callers to import report_json/report_markdown directly.
    """
    raw = sys.stdin.read() if path in (None, "-") else Path(path).read_text()
    return json.loads(raw)


def render_trace_report(trace, output_format="markdown"):
    if output_format == "markdown":
        return build_markdown_summary(trace)
    if output_format == "json":
        return json.dumps(build_json_summary(trace), indent=2, sort_keys=True) + "\n"
    raise ValueError(f"unsupported output format: {output_format}")


def build_parser():
    parser = argparse.ArgumentParser(description="Render an AgentTrace JSON trace report.")
    parser.add_argument("trace", nargs="?", default="-", help="Trace JSON file path, or '-' for stdin.")
    parser.add_argument("--format", choices=FORMAT_CHOICES, default="markdown", help="Report output format.")
    parser.add_argument("--output", "-o", help="Write report to this path instead of stdout.")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    trace = load_trace(args.trace)
    rendered = render_trace_report(trace, args.format)
    if args.output:
        Path(args.output).write_text(rendered)
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised through main()
    raise SystemExit(main())
