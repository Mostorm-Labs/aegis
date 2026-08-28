from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .model import load_skillset

_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_PLACEHOLDER_WORD_RE = re.compile(r"\b(?:TODO|TBD)\b")
_PLACEHOLDER_TOKENS = ("example_asset", "example_script", "example_reference")


def _frontmatter(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    out = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def validate_generated_skills(root: Path) -> list[str]:
    errors = []
    config = load_skillset(Path(root))
    for skill in config.skills:
        skill_dir = Path(root) / skill.distribution_path
        skill_md = skill_dir / "SKILL.md"
        agents = skill_dir / "agents/openai.yaml"
        if not skill_md.is_file():
            errors.append(f"{skill.name}: missing SKILL.md")
            continue
        if not agents.is_file():
            errors.append(f"{skill.name}: missing agents/openai.yaml")
        text = skill_md.read_text(encoding="utf-8")
        fm = _frontmatter(skill_md)
        if fm.get("name") != skill.name:
            errors.append(f"{skill.name}: frontmatter name mismatch")
        if not fm.get("description"):
            errors.append(f"{skill.name}: missing frontmatter description")
        if _PLACEHOLDER_WORD_RE.search(text):
            errors.append(f"{skill.name}: placeholder token")
        for token in _PLACEHOLDER_TOKENS:
            if token in text:
                errors.append(f"{skill.name}: placeholder token {token}")
        for target in _LINK_RE.findall(text):
            if "://" in target or target.startswith("#"):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (skill_dir / clean).is_file():
                errors.append(f"{skill.name}: missing reference {clean}")
    return errors


CatalogState = Literal[
    "FULL_SPECIALIST",
    "COMPOSITE_ONLY",
    "PARTIAL_CATALOG",
    "MIXED_REVISION",
]

DistributionProvenance = Literal[
    "PLUGIN",
    "STANDALONE",
    "INDIVIDUAL_SKILLS",
    "DUPLICATE_DISTRIBUTION",
    "UNKNOWN",
]


@dataclass(frozen=True)
class DistributionSpec:
    id: str
    kind: str
    skills: tuple[str, ...]
    required_apps: tuple[str, ...] = ()
    optional_apps: tuple[str, ...] = ()


@dataclass(frozen=True)
class DistributionContract:
    schema_version: str
    product_id: str
    plugin: DistributionSpec
    standalone: DistributionSpec


@dataclass(frozen=True)
class CatalogEvaluation:
    verdict: str
    catalog_state: str | None
    distribution_provenance: str | None
    runtime_mode: str | None
    specialist_availability: dict[str, str]
    evidence_gaps: tuple[str, ...]
    errors: tuple[str, ...]


def load_distribution_contract(root: Path) -> DistributionContract:
    raw = json.loads((Path(root) / "skillset/distribution.json").read_text(encoding="utf-8"))

    def spec(value):
        return DistributionSpec(
            value["id"],
            value["kind"],
            tuple(value.get("skills", ())),
            tuple(value.get("required_apps", ())),
            tuple(value.get("optional_apps", ())),
        )

    return DistributionContract(
        raw.get("schema_version", ""),
        raw.get("product_id", ""),
        spec(raw["plugin"]),
        spec(raw["standalone"]),
    )


def validate_distribution_contract(root: Path, contract: DistributionContract) -> list[str]:
    errors = []
    if contract.schema_version != "0.1":
        errors.append("schema_version must be 0.1")
    if contract.product_id != "aegis":
        errors.append("product_id must be aegis")
    expected = tuple(skill.name for skill in load_skillset(Path(root)).skills)
    if contract.plugin.kind != "plugin" or contract.plugin.id != "aegis":
        errors.append("invalid plugin kind/id")
    if contract.standalone.kind != "standalone" or contract.standalone.id != "aegis-standalone":
        errors.append("invalid standalone kind/id")
    if contract.plugin.skills != expected:
        errors.append("plugin skills must exactly match skillset manifest")
    if contract.standalone.skills != ("aegis",):
        errors.append("standalone skills must be aegis only")
    if (
        contract.plugin.required_apps
        or contract.plugin.optional_apps
        or contract.standalone.required_apps
        or contract.standalone.optional_apps
    ):
        errors.append("apps are not allowed in v0.1")
    return errors


def _blocked(gaps=(), errors=()):
    return CatalogEvaluation(
        "BLOCKED_EVIDENCE",
        None,
        None,
        None,
        {},
        tuple(gaps),
        tuple(errors),
    )


def _derive_provenance(observations: list[dict]) -> str:
    kinds: set[str] = set()
    unknown = False
    for observation in observations:
        if not isinstance(observation, dict):
            unknown = True
            continue
        key = (observation.get("kind"), observation.get("id"))
        if key == ("plugin", "aegis"):
            kinds.add("PLUGIN")
        elif key == ("standalone", "aegis-standalone"):
            kinds.add("STANDALONE")
        elif key == ("individual_skills", "aegis-individual"):
            kinds.add("INDIVIDUAL_SKILLS")
        else:
            unknown = True

    if len(kinds) > 1:
        return "DUPLICATE_DISTRIBUTION"
    if unknown or not kinds:
        return "UNKNOWN"
    return next(iter(kinds))


def _derive_catalog_state(expected: set[str], installed: set[str]) -> str:
    if installed == expected:
        return "FULL_SPECIALIST"
    if installed == {"aegis"}:
        return "COMPOSITE_ONLY"
    return "PARTIAL_CATALOG"


def evaluate_catalog_snapshot(root: Path, snapshot: dict) -> CatalogEvaluation:
    gaps = []
    for key in ("schema_version", "platform_event_id", "materialization_ref"):
        if not snapshot.get(key):
            gaps.append(key)
    if snapshot.get("schema_version") != "0.1":
        gaps.append("schema_version 0.1")
    if snapshot.get("fresh_platform_event") is not True:
        gaps.append("fresh_platform_event")
    if snapshot.get("complete_catalog_capture") is not True:
        gaps.append("complete_catalog_capture")

    surface = snapshot.get("surface")
    if (
        not isinstance(surface, dict)
        or surface.get("product") != "chatgpt"
        or surface.get("surface") not in {"web", "desktop", "mobile", "other"}
    ):
        gaps.append("platform surface")

    observations = snapshot.get("observed_distributions")
    if not isinstance(observations, list) or not observations:
        gaps.append("observed_distributions")

    installed = snapshot.get("installed_skills")
    if not isinstance(installed, list):
        gaps.append("installed_skills")

    release_ref = snapshot.get("release_manifest_ref")
    manifest = None
    if not release_ref:
        gaps.append("release_manifest_ref")
    else:
        try:
            path = Path(release_ref) if Path(release_ref).is_absolute() else Path(root) / release_ref
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            gaps.append("readable release_manifest_ref")

    if gaps:
        return _blocked(gaps)

    contract = load_distribution_contract(root)
    expected = set(contract.plugin.skills)
    installed_set = set(installed)
    availability = {
        name: ("available" if name in installed_set else "unavailable")
        for name in contract.plugin.skills
    }
    catalog_state = _derive_catalog_state(expected, installed_set)
    provenance = _derive_provenance(observations)

    if provenance == "UNKNOWN":
        return CatalogEvaluation(
            "BLOCKED_EVIDENCE",
            catalog_state,
            provenance,
            None,
            availability,
            ("known distribution provenance",),
            (),
        )

    observed_versions = {
        observation.get("release_version")
        for observation in observations
        if isinstance(observation, dict) and observation.get("release_version")
    }
    expected_version = manifest.get("release_version")
    components = snapshot.get("component_release_versions") or {}
    component_versions = set(components.values()) if isinstance(components, dict) else set()

    version_consistent = (
        len(observed_versions) == 1
        and observed_versions == {expected_version}
        and all(version == expected_version for version in component_versions)
    )
    if not version_consistent:
        return CatalogEvaluation(
            "BLOCKED_ENVIRONMENT",
            "MIXED_REVISION",
            provenance,
            None,
            availability,
            (),
            (),
        )

    if provenance == "DUPLICATE_DISTRIBUTION":
        return CatalogEvaluation(
            "BLOCKED_ENVIRONMENT",
            catalog_state,
            provenance,
            None,
            availability,
            (),
            (),
        )

    if catalog_state == "PARTIAL_CATALOG":
        return CatalogEvaluation(
            "BLOCKED_ENVIRONMENT",
            catalog_state,
            provenance,
            None,
            availability,
            (),
            (),
        )

    if provenance == "PLUGIN":
        if catalog_state != "FULL_SPECIALIST":
            return CatalogEvaluation(
                "BLOCKED_ENVIRONMENT",
                catalog_state,
                provenance,
                None,
                availability,
                (),
                (),
            )
        return CatalogEvaluation(
            "PASS",
            catalog_state,
            provenance,
            "multi_skill",
            availability,
            (),
            (),
        )

    if provenance == "STANDALONE":
        if catalog_state != "COMPOSITE_ONLY":
            return CatalogEvaluation(
                "BLOCKED_ENVIRONMENT",
                catalog_state,
                provenance,
                None,
                availability,
                (),
                (),
            )
        return CatalogEvaluation(
            "PASS",
            catalog_state,
            provenance,
            "compatibility",
            availability,
            (),
            (),
        )

    if provenance == "INDIVIDUAL_SKILLS":
        runtime_mode = "multi_skill" if catalog_state == "FULL_SPECIALIST" else "compatibility"
        return CatalogEvaluation(
            "PASS",
            catalog_state,
            provenance,
            runtime_mode,
            availability,
            (),
            (),
        )

    return CatalogEvaluation(
        "BLOCKED_EVIDENCE",
        catalog_state,
        "UNKNOWN",
        None,
        availability,
        ("known distribution provenance",),
        (),
    )
