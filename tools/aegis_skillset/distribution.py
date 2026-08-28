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
    if not text.startswith("---\n"): return {}
    end = text.find("\n---\n", 4)
    if end < 0: return {}
    out = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k,v = line.split(":",1); out[k.strip()] = v.strip().strip('"').strip("'")
    return out

def validate_generated_skills(root: Path) -> list[str]:
    errors=[]; config=load_skillset(Path(root))
    for skill in config.skills:
        d=Path(root)/skill.distribution_path; md=d/"SKILL.md"; agents=d/"agents/openai.yaml"
        if not md.is_file(): errors.append(f"{skill.name}: missing SKILL.md"); continue
        if not agents.is_file(): errors.append(f"{skill.name}: missing agents/openai.yaml")
        text=md.read_text(encoding="utf-8"); fm=_frontmatter(md)
        if fm.get("name") != skill.name: errors.append(f"{skill.name}: frontmatter name mismatch")
        if not fm.get("description"): errors.append(f"{skill.name}: missing frontmatter description")
        if _PLACEHOLDER_WORD_RE.search(text): errors.append(f"{skill.name}: placeholder token")
        for token in _PLACEHOLDER_TOKENS:
            if token in text: errors.append(f"{skill.name}: placeholder token {token}")
        for target in _LINK_RE.findall(text):
            if "://" in target or target.startswith("#"): continue
            clean=target.split("#",1)[0]
            if clean and not (d/clean).is_file(): errors.append(f"{skill.name}: missing reference {clean}")
    return errors

CatalogState = Literal["FULL_SPECIALIST", "COMPOSITE_ONLY", "PARTIAL_CATALOG", "MIXED_REVISION", "DUPLICATE_DISTRIBUTION"]

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
    runtime_mode: str | None
    specialist_availability: dict[str, str]
    evidence_gaps: tuple[str, ...]
    errors: tuple[str, ...]

def load_distribution_contract(root: Path) -> DistributionContract:
    raw = json.loads((Path(root) / "skillset/distribution.json").read_text(encoding="utf-8"))
    def spec(v):
        return DistributionSpec(v["id"], v["kind"], tuple(v.get("skills", ())), tuple(v.get("required_apps", ())), tuple(v.get("optional_apps", ())))
    return DistributionContract(raw.get("schema_version", ""), raw.get("product_id", ""), spec(raw["plugin"]), spec(raw["standalone"]))

def validate_distribution_contract(root: Path, contract: DistributionContract) -> list[str]:
    errors = []
    if contract.schema_version != "0.1": errors.append("schema_version must be 0.1")
    if contract.product_id != "aegis": errors.append("product_id must be aegis")
    expected = tuple(s.name for s in load_skillset(Path(root)).skills)
    if contract.plugin.kind != "plugin" or contract.plugin.id != "aegis": errors.append("invalid plugin kind/id")
    if contract.standalone.kind != "standalone" or contract.standalone.id != "aegis-standalone": errors.append("invalid standalone kind/id")
    if contract.plugin.skills != expected: errors.append("plugin skills must exactly match skillset manifest")
    if contract.standalone.skills != ("aegis",): errors.append("standalone skills must be aegis only")
    if contract.plugin.required_apps or contract.plugin.optional_apps or contract.standalone.required_apps or contract.standalone.optional_apps: errors.append("apps are not allowed in v0.1")
    return errors

def _blocked(gaps=(), errors=()):
    return CatalogEvaluation("BLOCKED_EVIDENCE", None, None, {}, tuple(gaps), tuple(errors))

def evaluate_catalog_snapshot(root: Path, snapshot: dict) -> CatalogEvaluation:
    gaps=[]
    for key in ("schema_version", "platform_event_id", "materialization_ref"):
        if not snapshot.get(key): gaps.append(key)
    if snapshot.get("schema_version") != "0.1": gaps.append("schema_version 0.1")
    if snapshot.get("fresh_platform_event") is not True: gaps.append("fresh_platform_event")
    if snapshot.get("complete_catalog_capture") is not True: gaps.append("complete_catalog_capture")
    surface = snapshot.get("surface")
    if not isinstance(surface, dict) or surface.get("product") != "chatgpt" or surface.get("surface") not in {"web", "desktop", "mobile", "other"}:
        gaps.append("platform surface")
    if not isinstance(snapshot.get("observed_distributions"), list) or not snapshot.get("observed_distributions"): gaps.append("observed_distributions")
    installed = snapshot.get("installed_skills")
    if not isinstance(installed, list): gaps.append("installed_skills")
    ref = snapshot.get("release_manifest_ref")
    manifest = None
    if not ref: gaps.append("release_manifest_ref")
    else:
        try: manifest=json.loads((Path(ref) if Path(ref).is_absolute() else Path(root)/ref).read_text(encoding="utf-8"))
        except Exception: gaps.append("readable release_manifest_ref")
    if gaps: return _blocked(gaps)
    observations=snapshot["observed_distributions"]
    kinds={(o.get("kind"),o.get("id")) for o in observations if isinstance(o,dict)}
    has_plugin=any(k==("plugin","aegis") for k in kinds); has_standalone=any(k==("standalone","aegis-standalone") for k in kinds)
    if has_plugin and has_standalone: return CatalogEvaluation("BLOCKED_ENVIRONMENT","DUPLICATE_DISTRIBUTION",None,{},(),())
    contract=load_distribution_contract(root); expected = tuple(contract.plugin.skills)
    names=tuple(installed)
    selected = contract.plugin if has_plugin else contract.standalone if has_standalone else None
    if selected is None: return CatalogEvaluation("BLOCKED_ENVIRONMENT","PARTIAL_CATALOG",None,{},(),("unknown distribution provenance",))
    if names != selected.skills: return CatalogEvaluation("BLOCKED_ENVIRONMENT","PARTIAL_CATALOG",None,{},(),())
    selected_obs=next((o for o in observations if o.get("id")==selected.id), {})
    version=selected_obs.get("release_version")
    if not version or version != manifest.get("release_version"): return CatalogEvaluation("BLOCKED_ENVIRONMENT","MIXED_REVISION",None,{},(),())
    comps=snapshot.get("component_release_versions") or {}
    if isinstance(comps,dict) and any(v != version for v in comps.values()): return CatalogEvaluation("BLOCKED_ENVIRONMENT","MIXED_REVISION",None,{},(),())
    avail={n:("available" if (selected is contract.plugin or n=="aegis") else "unavailable") for n in expected}
    if selected is contract.plugin: return CatalogEvaluation("PASS","FULL_SPECIALIST","multi_skill",avail,(),())
    return CatalogEvaluation("PASS","COMPOSITE_ONLY","compatibility",avail,(),())
