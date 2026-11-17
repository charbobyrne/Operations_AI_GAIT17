"""Run the complete sample pipeline from CSV to JSON report."""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.ai.client import OpenAIClient
from app.core.config import get_settings
from app.orchestration.pipeline import run_pipeline

DEFAULT_INPUT = ROOT / "sample_data" / "call_center_calls.csv"
DEFAULT_OUTPUT = ROOT / "output" / "sample_e2e_report.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze the included call-center data and optionally run all OpenAI stages."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="CSV file to analyze")
    parser.add_argument("--column", default="handle_seconds", help="Positive numeric duration column")
    parser.add_argument("--unit", default="seconds", help="Unit displayed in the report")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="JSON report path")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use deterministic placeholders even when OPENAI_API_KEY is configured",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 2

    settings = get_settings()
    if not args.offline and not settings.openai_api_key:
        print(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key, "
            "or rerun with --offline.",
            file=sys.stderr,
        )
        return 2

    frame = pd.read_csv(args.input)
    client = None if args.offline else OpenAIClient(settings)

    print(f"Analyzing {len(frame)} rows from {args.input.name}...")
    print("Running deterministic demo stages..." if args.offline else "Calling three OpenAI stages...")
    result = run_pipeline(frame, args.column, args.unit, ai_client=client)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result.model_dump(), indent=2), encoding="utf-8")

    print(f"Valid rows: {result.evidence.row_count_valid}")
    print(f"Excluded rows: {result.evidence.exclusions.total}")
    print(f"Mean: {result.evidence.statistics.mean:.2f} {args.unit}")
    print(f"Critic blocking: {result.critic.blocking}")
    if result.usage:
        print(f"API tokens: {sum(record.total_tokens for record in result.usage)}")
    print(f"Report written to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
