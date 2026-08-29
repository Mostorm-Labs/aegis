#!/usr/bin/env python3
import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.aegis_skillset.package import (
    build_skill_installation_kit,
    build_source_bundles,
    render_release_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-task6.1"
TARGET = ROOT / "skillset/releases/aegis-0.1.0-task6.1.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--package-dir")
    args = parser.parse_args()

    manifest = render_release_manifest(ROOT, VERSION)
    text = json.dumps(manifest, sort_keys=True, indent=2) + "\n"

    if args.write_manifest:
        TARGET.parent.mkdir(parents=True, exist_ok=True)
        TARGET.write_text(text, encoding="utf-8")

    if args.check:
        old = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if old != text:
            print("".join(difflib.unified_diff(old.splitlines(True), text.splitlines(True))))
            return 1
        print("AEGIS_DISTRIBUTION_STATE_OK")

    if args.package_dir:
        output_dir = Path(args.package_dir)
        build_source_bundles(ROOT, VERSION, output_dir)
        build_skill_installation_kit(ROOT, VERSION, output_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
