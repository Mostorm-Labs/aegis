from __future__ import annotations
import argparse
from pathlib import Path
from .dogfood import evaluate_installed_platform_rerun
from .model import load_skillset, validate_skillset
from .routing import validate_routing_corpus
from .distribution import load_distribution_contract, validate_distribution_contract


def _print_installed_platform(result):
    for error in result.errors:
        print("INVALID:", error)
    for case in result.cases:
        detail = []
        if case.violations:
            detail.append("violations=" + ",".join(case.violations))
        if case.evidence_gaps:
            detail.append("evidence_gaps=" + ",".join(case.evidence_gaps))
        suffix = " " + " ".join(detail) if detail else ""
        print(f"{case.case_id}: {case.verdict}{suffix}")
    print("INSTALLED_PLATFORM_STATE", result.verdict)


def main(argv=None):
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in (
        "validate",
        "routing-check",
        "installed-platform-check",
        "installed-platform-gate",
        "distribution-check",
    ):
        sp = sub.add_parser(name)
        sp.add_argument("root", nargs="?", default=".")
    args = p.parse_args(argv)
    root = Path(args.root)

    if args.cmd in {"installed-platform-check", "installed-platform-gate"}:
        result = evaluate_installed_platform_rerun(root)
        _print_installed_platform(result)
        if result.errors:
            return 1
        if args.cmd == "installed-platform-gate" and result.verdict != "PASS":
            return 2
        return 0

    if args.cmd == "distribution-check":
        errors = validate_distribution_contract(root, load_distribution_contract(root))
        if errors:
            for error in errors: print("INVALID:", error)
            return 1
        print("DISTRIBUTION_VALID")
        return 0
    errors = (
        validate_routing_corpus(root)
        if args.cmd == "routing-check"
        else validate_skillset(load_skillset(root))
    )
    if errors:
        for error in errors:
            print("INVALID:", error)
        return 1
    print("ROUTING_OK" if args.cmd == "routing-check" else "SKILLSET_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
