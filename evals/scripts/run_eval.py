#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

from aegis_eval.adapters import CommandAdapter, RecordedAdapter
from aegis_eval.runner import evaluate_cases
from validate_corpus import load_cases, validate_cases

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES_DIR = ROOT / "evals" / "cases"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run and score the Aegis evaluation corpus")
    parser.add_argument("--adapter", choices=("recorded", "command"), required=True)
    parser.add_argument("--results", help="JSON object keyed by case_id for recorded adapter")
    parser.add_argument("--command", help="External driver command for command adapter")
    parser.add_argument("--cases-dir", type=Path, default=DEFAULT_CASES_DIR)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    cases, load_errors = load_cases(args.cases_dir)
    validation_errors, _ = validate_cases(cases) if cases else ([], {})
    errors = load_errors + validation_errors
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if args.adapter == "recorded":
        if not args.results:
            print("ERROR: --results is required for recorded adapter", file=sys.stderr)
            return 1
        adapter = RecordedAdapter(args.results)
    else:
        if not args.command:
            print("ERROR: --command is required for command adapter", file=sys.stderr)
            return 1
        adapter = CommandAdapter(shlex.split(args.command))

    try:
        summary = evaluate_cases(cases, adapter, args.output)
    except (ValueError, KeyError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["deterministic_gate_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
