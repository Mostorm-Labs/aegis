from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .package import tree_sha256


PLUGIN_ID = "aegis"
PLUGIN_ROOT_REL = Path("plugins/aegis")
MARKETPLACE_REL = Path(".agents/plugins/marketplace.json")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, indent=2) + "\n"


def _release_path(root: Path, release_version: str) -> Path:
    return root / "skillset" / "releases" / f"aegis-{release_version}.json"


def validate_release_binding(root: Path, release_version: str) -> tuple[dict[str, Any], list[str]]:
    root = Path(root)
    distribution = _load_json(root / "skillset" / "distribution.json")
    plugin_contract = distribution.get("plugin")
    if not isinstance(plugin_contract, dict):
        raise ValueError("skillset/distribution.json must define plugin contract")

    expected_skills = plugin_contract.get("skills")
    if not isinstance(expected_skills, list) or not all(
        isinstance(name, str) and name for name in expected_skills
    ):
        raise ValueError("plugin.skills must be a non-empty string list")
    if len(expected_skills) != 9 or len(set(expected_skills)) != 9:
        raise ValueError("Aegis Plugin materialization requires exactly nine unique Skills")
    if plugin_contract.get("required_apps") != [] or plugin_contract.get("optional_apps") != []:
        raise ValueError("Aegis Plugin v0.1 materialization requires zero Apps")

    release_path = _release_path(root, release_version)
    if not release_path.is_file():
        raise ValueError(f"missing committed release manifest: {release_path}")
    release = _load_json(release_path)
    if release.get("release_version") != release_version:
        raise ValueError("release manifest version does not match requested Plugin release")

    release_plugin = release.get("plugin")
    if not isinstance(release_plugin, dict):
        raise ValueError("release manifest must define plugin component set")
    release_entries = release_plugin.get("skills")
    if not isinstance(release_entries, list):
        raise ValueError("release manifest plugin.skills must be a list")
    release_names = [entry.get("name") for entry in release_entries if isinstance(entry, dict)]
    if release_names != expected_skills:
        raise ValueError("release manifest Plugin Skill order/set differs from distribution contract")

    entries_by_name = {entry["name"]: entry for entry in release_entries}
    for skill_name in expected_skills:
        canonical = root / "skills" / skill_name
        if not canonical.is_dir():
            raise ValueError(f"missing canonical Skill tree: skills/{skill_name}")
        current_digest = tree_sha256(canonical)
        pinned_digest = entries_by_name[skill_name].get("tree_sha256")
        if current_digest != pinned_digest:
            raise ValueError(
                f"canonical Skill {skill_name} no longer matches release {release_version}: "
                f"expected {pinned_digest}, got {current_digest}"
            )

    return release, expected_skills


def render_marketplace() -> dict[str, Any]:
    return {
        "name": "mostorm-labs-aegis",
        "interface": {"displayName": "Mostorm Labs Aegis"},
        "plugins": [
            {
                "name": PLUGIN_ID,
                "source": {"source": "local", "path": "./plugins/aegis"},
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Productivity",
            }
        ],
    }


def render_plugin_manifest(release_version: str) -> dict[str, Any]:
    return {
        "name": PLUGIN_ID,
        "version": release_version,
        "description": "Evidence-driven software development control plane.",
        "author": {
            "name": "Mostorm Labs",
            "url": "https://github.com/Mostorm-Labs",
        },
        "repository": "https://github.com/Mostorm-Labs/aegis",
        "skills": "./skills/",
        "interface": {
            "displayName": "Aegis",
            "shortDescription": "Evidence-driven software development control plane",
            "longDescription": (
                "Route software-development work through explicit authority, evidence, "
                "implementation, and Gate review."
            ),
            "developerName": "Mostorm Labs",
            "category": "Productivity",
            "capabilities": ["Software development", "Workflow", "Verification"],
            "defaultPrompt": [
                "What should this project do next?",
                "Design the semantic schema for this feature.",
                "Audit this implementation against its Gate evidence.",
            ],
        },
    }


def write_materialization(root: Path, release_version: str) -> None:
    root = Path(root)
    _, expected_skills = validate_release_binding(root, release_version)

    plugin_root = root / PLUGIN_ROOT_REL
    if plugin_root.exists():
        shutil.rmtree(plugin_root)

    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        _json_text(render_plugin_manifest(release_version)),
        encoding="utf-8",
    )

    skills_root = plugin_root / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)
    for skill_name in expected_skills:
        shutil.copytree(root / "skills" / skill_name, skills_root / skill_name)

    marketplace_path = root / MARKETPLACE_REL
    marketplace_path.parent.mkdir(parents=True, exist_ok=True)
    marketplace_path.write_text(_json_text(render_marketplace()), encoding="utf-8")


def check_materialization(root: Path, release_version: str) -> None:
    root = Path(root)
    _, expected_skills = validate_release_binding(root, release_version)

    marketplace_path = root / MARKETPLACE_REL
    if not marketplace_path.is_file():
        raise ValueError(f"missing native marketplace manifest: {MARKETPLACE_REL.as_posix()}")
    actual_marketplace = _load_json(marketplace_path)
    expected_marketplace = render_marketplace()
    if actual_marketplace != expected_marketplace:
        raise ValueError("native marketplace manifest drift")

    plugin_root = root / PLUGIN_ROOT_REL
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    if not manifest_path.is_file():
        raise ValueError("missing native Plugin manifest: plugins/aegis/.codex-plugin/plugin.json")
    actual_manifest = _load_json(manifest_path)
    expected_manifest = render_plugin_manifest(release_version)
    if actual_manifest != expected_manifest:
        raise ValueError("native Aegis Plugin manifest drift")

    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        raise ValueError("missing Plugin Skill materialization: plugins/aegis/skills")
    actual_skills = sorted(
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )
    if actual_skills != sorted(expected_skills):
        raise ValueError(
            "Plugin Skill inventory drift: "
            f"expected {sorted(expected_skills)}, got {actual_skills}"
        )

    for skill_name in expected_skills:
        canonical = root / "skills" / skill_name
        materialized = skills_root / skill_name
        canonical_digest = tree_sha256(canonical)
        materialized_digest = tree_sha256(materialized)
        if canonical_digest != materialized_digest:
            raise ValueError(
                f"Plugin materialization drift for {skill_name}: "
                f"canonical {canonical_digest}, materialized {materialized_digest}"
            )
