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
    tree_sha256,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERSION = "0.1.0-task6.1"


def check_published_history(root: Path, version: str) -> None:
    """Verify immutable release metadata against its committed Plugin payload."""
    target = root / f"skillset/releases/aegis-{version}.json"
    if not target.is_file():
        raise ValueError(f"missing committed published release manifest: {target}")
    release = json.loads(target.read_text(encoding="utf-8"))
    if release.get("release_version") != version:
        raise ValueError("published release manifest version mismatch")
    entries = release.get("plugin", {}).get("skills", [])
    if len(entries) != 9 or len({entry.get("name") for entry in entries}) != 9:
        raise ValueError("published beta.3 Plugin history must contain exactly nine Skills")
    for entry in entries:
        name = entry["name"]
        payload = root / "plugins/aegis/skills" / name
        if not payload.is_dir() or tree_sha256(payload) != entry.get("tree_sha256"):
            raise ValueError(f"published Plugin payload drift for {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument(
        "--published-history",
        action="store_true",
        help="Explicitly operate on the immutable published beta.3 history.",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--package-dir")
    parser.add_argument("--installation-kit-archive-dir")
    args = parser.parse_args()

    version = args.version
    if args.published_history and version != "0.1.0-beta.3":
        parser.error("--published-history is only valid with --version 0.1.0-beta.3")

    if args.published_history:
        try:
            check_published_history(ROOT, version)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            print(f"PUBLISHED_HISTORY_ERROR: {error}", file=sys.stderr)
            return 1
        print("PUBLISHED_HISTORY_OK")
        return 0
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
