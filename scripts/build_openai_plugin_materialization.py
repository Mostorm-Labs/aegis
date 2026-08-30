#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.aegis_skillset.plugin_materialization import (
    check_materialization,
    write_materialization,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify the OpenAI-native Aegis Plugin materialization."
    )
    parser.add_argument(
        "--release-version",
        required=True,
        help="Committed Aegis release version used to bind the Plugin materialization.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        if args.write:
            write_materialization(ROOT, args.release_version)
            print("OPENAI_PLUGIN_MATERIALIZATION_WRITTEN")
        else:
            check_materialization(ROOT, args.release_version)
            print("OPENAI_PLUGIN_MATERIALIZATION_OK")
    except (OSError, ValueError) as error:
        print(f"OPENAI_PLUGIN_MATERIALIZATION_ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
