#!/usr/bin/env python3
"""Build exact-head, non-published Plugin parity evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.aegis_skillset.package import tree_sha256, validate_repository_identity


ROOT = Path(__file__).resolve().parents[1]


def _revision(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def build(root: Path, output: Path) -> dict:
    root = Path(root)
    repository = validate_repository_identity(
        {"provider": "github", "full_name": "Mostorm-Labs/aegis"}
    )
    distribution = json.loads(
        (root / "skillset" / "distribution.json").read_text(encoding="utf-8")
    )
    names = distribution.get("plugin", {}).get("skills")
    if not isinstance(names, list) or len(names) != 9 or len(set(names)) != 9:
        raise ValueError("candidate parity requires exactly nine unique Plugin Skills")

    skills = []
    for name in names:
        tree = root / "skills" / name
        if not tree.is_dir():
            raise ValueError(f"missing candidate Skill tree: skills/{name}")
        skills.append({"name": name, "tree_sha256": tree_sha256(tree)})

    artifact = {
        "schema_version": "0.2",
        "artifact_class": "CANDIDATE_PLUGIN_PARITY_EVIDENCE",
        "repository": repository,
        "source_revision": _revision(root),
        "plugin": {"id": "aegis", "skills": skills, "required_apps": [], "optional_apps": []},
        "exact_nine": True,
        "public_release": False,
        "service_profile": "NOT_CLAIMED",
        "writes_plugin_tree": False,
    }
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="/tmp/aegis-candidate-plugin-parity.json")
    args = parser.parse_args()
    try:
        artifact = build(ROOT, Path(args.output))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"CANDIDATE_PLUGIN_PARITY_ERROR: {error}", file=sys.stderr)
        return 1
    print(f"CANDIDATE_PLUGIN_PARITY_WRITTEN {artifact['source_revision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
