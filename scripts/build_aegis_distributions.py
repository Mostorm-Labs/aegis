#!/usr/bin/env python3
import argparse
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.aegis_skillset.package import (
    build_skill_installation_kit,
    build_skill_installation_kit_archive,
    build_source_bundles,
    render_release_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERSION = "0.1.0-task6.1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--package-dir")
    parser.add_argument("--installation-kit-archive-dir")
    args = parser.parse_args()

    version = args.version
    target = ROOT / f"skillset/releases/aegis-{version}.json"
    manifest = render_release_manifest(ROOT, version)
    text = json.dumps(manifest, sort_keys=True, indent=2) + "\n"

    if args.write_manifest:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    if args.check:
        old = target.read_text(encoding="utf-8") if target.exists() else ""
        if old != text:
            print("".join(difflib.unified_diff(old.splitlines(True), text.splitlines(True))))
            return 1
        print("AEGIS_DISTRIBUTION_STATE_OK")

    if args.package_dir:
        output_dir = Path(args.package_dir)
        build_source_bundles(ROOT, version, output_dir)
        build_skill_installation_kit(ROOT, version, output_dir)

    if args.installation_kit_archive_dir:
        build_skill_installation_kit_archive(ROOT, version, Path(args.installation_kit_archive_dir))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
