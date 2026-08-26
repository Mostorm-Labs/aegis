from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .compute import compute_state
from .model import ManifestError, load_manifests, validate_manifests


def _render(state: dict) -> str:
    return json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _load(root: str):
    try:
        return load_manifests(Path(root))
    except ManifestError as exc:
        print(f"MANIFEST_ERROR: {exc}")
        return None


def cmd_validate(root: str) -> int:
    manifests = _load(root)
    if manifests is None:
        return 2
    errors = validate_manifests(manifests, strict_gate_validity=True)
    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        return 2
    print("VALID")
    return 0


def _structural_errors(manifests) -> list[str]:
    return validate_manifests(manifests, strict_gate_validity=False)


def cmd_recompute(root: str, write: bool) -> int:
    manifests = _load(root)
    if manifests is None:
        return 2
    errors = _structural_errors(manifests)
    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        return 2
    state = compute_state(manifests)
    rendered = _render(state)
    if write:
        path = Path(root) / ".aegis" / "state.json"
        path.write_text(rendered, encoding="utf-8")
        print(f"STATE_WRITTEN: {path}")
    else:
        sys.stdout.write(rendered)
    return 0


def cmd_check(root: str) -> int:
    manifests = _load(root)
    if manifests is None:
        return 2
    errors = _structural_errors(manifests)
    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        return 2
    computed = compute_state(manifests)
    state_path = Path(root) / ".aegis" / "state.json"
    if not state_path.exists():
        print("STATE_DRIFT: .aegis/state.json is missing")
        return 3
    try:
        committed = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"STATE_DRIFT: invalid state.json: {exc}")
        return 3
    if committed != computed:
        print("STATE_DRIFT: committed state.json differs from fresh recomputation")
        return 3
    strict_errors = validate_manifests(manifests, strict_gate_validity=True)
    if strict_errors:
        for error in strict_errors:
            print(f"INVALID: {error}")
        return 2
    print("STATE_OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Aegis project state manifest tooling")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("project_root")
    recompute = sub.add_parser("recompute")
    recompute.add_argument("project_root")
    recompute.add_argument("--write", action="store_true")
    check = sub.add_parser("check")
    check.add_argument("project_root")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        return cmd_validate(args.project_root)
    if args.command == "recompute":
        return cmd_recompute(args.project_root, args.write)
    if args.command == "check":
        return cmd_check(args.project_root)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
