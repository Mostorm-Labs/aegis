#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import evidence_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-revision", required=True)
    parser.add_argument("--package-ref", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    commands = [
        "python3 -m unittest discover -s tests/control_plane -v",
        "python3 -m unittest discover -s tests/project_state -v",
        "python3 -m unittest discover -s tests/skillset -v",
    ]
    manifest = evidence_manifest.build_manifest(args.result_revision, args.package_ref, commands)
    if manifest["qualification"]["detected"] != 20 or manifest["qualification"]["false_acceptance"] != 0:
        raise SystemExit("verifier qualification threshold not met")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
