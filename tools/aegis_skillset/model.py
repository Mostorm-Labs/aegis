from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

EXPECTED_STAGES = {
    'P00','P01','P02','P03',
    'P10','P11','P12','P13','P14','P15','P16','P17','P18',
    'P20','P21','P22','P23','P24',
    'P30','P31','P32','P33','P34','P35','P36',
}

@dataclass(frozen=True)
class SkillSpec:
    name: str
    role: str
    source_path: str
    distribution_path: str
    shared_refs: tuple[str, ...]

@dataclass(frozen=True)
class SkillSetConfig:
    skills: tuple[SkillSpec, ...]
    primary_owner_by_stage: dict[str, str]
    cross_cutting_owners: dict[str, str]
    ambiguity_router: str
    supporting_skills: tuple[str, ...]
    compatibility_owner: str
    compatibility_requires_unavailable_evidence: bool
    semantic_surfaces: tuple[str, ...]
    default_executor_profile: str
    executor_profiles: dict[str, dict[str, str]]
    execution_surface_by_stage: dict[str, str]
    surface_handoff_transfers_ownership: bool
    raw_manifest: dict


def load_skillset(root: Path) -> SkillSetConfig:
    root = Path(root)
    manifest = json.loads((root / 'skillset/manifest.json').read_text(encoding='utf-8'))
    ownership = json.loads((root / 'skillset/ownership.json').read_text(encoding='utf-8'))
    skills = tuple(SkillSpec(name=i['name'], role=i['role'], source_path=i['source_path'], distribution_path=i['distribution_path'], shared_refs=tuple(i.get('shared_refs', []))) for i in manifest['skills'])
    cross = dict(ownership.get('cross_cutting', {}))
    composition = dict(ownership.get('composition', {}))
    execution_surfaces = dict(ownership.get('execution_surfaces', {}))
    return SkillSetConfig(
        skills,
        dict(ownership['primary_owner_by_stage']),
        cross,
        cross['ambiguity_router'],
        tuple(composition.get('supporting_skills', ())),
        composition.get('compatibility_owner', ''),
        composition.get('compatibility_requires_unavailable_evidence', False),
        tuple(execution_surfaces.get('semantic_surfaces', ())),
        execution_surfaces.get('default_executor_profile', ''),
        {name: dict(mapping) for name, mapping in execution_surfaces.get('executor_profiles', {}).items()},
        dict(execution_surfaces.get('execution_surface_by_stage', {})),
        execution_surfaces.get('surface_handoff_transfers_ownership', True),
        manifest,
    )


def validate_skillset(config: SkillSetConfig) -> list[str]:
    errors: list[str] = []
    names = [s.name for s in config.skills]
    if len(names) != len(set(names)): errors.append('duplicate skill name')
    source_paths = [s.source_path for s in config.skills]
    dist_paths = [s.distribution_path for s in config.skills]
    if len(source_paths) != len(set(source_paths)): errors.append('duplicate source path')
    if len(dist_paths) != len(set(dist_paths)): errors.append('duplicate distribution path')
    if any('stages' in i for i in config.raw_manifest.get('skills', [])): errors.append('manifest duplicates stage ownership')
    actual = set(config.primary_owner_by_stage)
    missing = EXPECTED_STAGES - actual
    extra = actual - EXPECTED_STAGES
    if missing: errors.append('missing stage ownership: ' + ','.join(sorted(missing)))
    if extra: errors.append('unknown stage ownership: ' + ','.join(sorted(extra)))
    owners = set(names)
    unknown = sorted({o for o in config.primary_owner_by_stage.values() if o not in owners})
    if unknown: errors.append('unknown stage owner: ' + ','.join(unknown))
    if config.ambiguity_router != 'aegis': errors.append('ambiguity router must be aegis')
    if config.cross_cutting_owners.get('project_state') != 'aegis-project-state': errors.append('project_state owner must be aegis-project-state')
    unknown_support = sorted({name for name in config.supporting_skills if name not in owners})
    if unknown_support: errors.append('unknown supporting skill: ' + ','.join(unknown_support))
    if tuple(config.supporting_skills) != ('aegis-project-state',): errors.append('v0.2 supporting skills must be aegis-project-state only')
    if config.compatibility_owner != 'aegis': errors.append('compatibility owner must be aegis')
    if not config.compatibility_requires_unavailable_evidence: errors.append('compatibility requires unavailable evidence')
    expected_execution_stages = {'P30','P31','P32','P33','P34','P35','P36'}
    actual_execution_stages = set(config.execution_surface_by_stage)
    missing_execution = expected_execution_stages - actual_execution_stages
    extra_execution = actual_execution_stages - expected_execution_stages
    if missing_execution: errors.append('missing execution surface stage: ' + ','.join(sorted(missing_execution)))
    if extra_execution: errors.append('unknown execution surface stage: ' + ','.join(sorted(extra_execution)))
    declared_surfaces = set(config.semantic_surfaces)
    unknown_execution = sorted({surface for surface in config.execution_surface_by_stage.values() if surface not in declared_surfaces})
    if unknown_execution: errors.append('unknown execution surface: ' + ','.join(unknown_execution))
    if config.default_executor_profile not in config.executor_profiles: errors.append('default executor profile is undefined')
    elif set(config.executor_profiles[config.default_executor_profile]) != declared_surfaces: errors.append('default executor profile must map every semantic surface exactly once')
    if config.surface_handoff_transfers_ownership: errors.append('surface handoff must not transfer ownership')
    return errors
