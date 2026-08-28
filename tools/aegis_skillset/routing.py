from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .model import SkillSetConfig, load_skillset

CORPUS_FILES = ('direct-trigger.json','ambiguous-routing.json','upstream-blocker.json','compatibility.json')


@dataclass(frozen=True)
class TraceEvaluation:
    verdict: str
    violations: tuple[str, ...]
    evidence_gaps: tuple[str, ...]


def _has_cycle(edges):
    graph = {}
    for a, b in edges:
        graph.setdefault(a, set()).add(b)
    visiting = set()
    visited = set()

    def dfs(node):
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(dfs(n) for n in graph.get(node, ())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(dfs(n) for n in list(graph))


def _is_allowed_bounded_router_reentry(case: dict, trace: dict, router: str) -> bool:
    primary = case.get('required_primary_owner') or case.get('requested_primary_owner')
    if not primary:
        return False
    invocations = trace.get('invocations') or []
    expected = [
        {'skill': router, 'role': 'router'},
        {'skill': primary, 'role': 'primary'},
        {'skill': router, 'role': 'router'},
    ]
    return (
        invocations == expected
        and trace.get('earlier_blocker_conclusively_established') is True
        and trace.get('primary_substantive_result_emitted') is False
        and trace.get('final_answer_owner') == router
        and trace.get('forbidden_downstream_substantive_execution') == 0
    )


def evaluate_terminal_trace(case: dict, trace: dict, config: SkillSetConfig) -> TraceEvaluation:
    violations: list[str] = []
    evidence_gaps: list[str] = []
    router = config.ambiguity_router
    invocations = trace.get('invocations')

    if trace.get('terminal') is not True:
        evidence_gaps.append('terminal response')
    if not isinstance(invocations, list):
        evidence_gaps.append('complete invocation trace')
        invocations = []
    if not trace.get('final_answer_owner'):
        evidence_gaps.append('final answer owner')
    mode = trace.get('mode')
    if mode not in {'multi_skill', 'compatibility'}:
        evidence_gaps.append('runtime mode')

    known_skills = {skill.name for skill in config.skills}
    support_invocations = [i for i in invocations if i.get('role') == 'support']
    primary_invocations = [i for i in invocations if i.get('role') == 'primary']
    primary_owners = {i.get('skill') for i in primary_invocations if i.get('skill')}
    case_support = set(case.get('allowed_supporting_skills', ()))
    global_support = set(config.supporting_skills)

    for invocation in support_invocations:
        skill = invocation.get('skill')
        if skill not in known_skills or skill not in global_support or skill not in case_support:
            violations.append('SUPPORT_NOT_ALLOWLISTED')

    if len(primary_owners) > 1:
        violations.append('MULTIPLE_PRIMARY_OWNERS')

    final_owner = trace.get('final_answer_owner')
    expected_primary = case.get('required_primary_owner') or case.get('requested_primary_owner')
    if (
        expected_primary
        and final_owner in global_support
        and final_owner != expected_primary
    ):
        violations.append('SUPPORT_OWNERSHIP_LEAK')

    ownership_edges = trace.get('ownership_edges') or []
    primary_specialists = set(config.primary_owner_by_stage.values())
    for edge in ownership_edges:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            evidence_gaps.append('valid ownership edges')
            continue
        source, target = edge
        if source in primary_specialists and target in primary_specialists and source != target:
            violations.append('DIRECT_PRIMARY_CHAIN')

    bounded_reentry = _is_allowed_bounded_router_reentry(case, trace, router)
    handoff_edges = trace.get('handoff_edges') or []
    if not bounded_reentry and (_has_cycle(ownership_edges) or _has_cycle(handoff_edges)):
        violations.append('OWNERSHIP_LOOP')

    short_circuit = case.get('short_circuit') or {}
    short_circuit_allowed = short_circuit.get('allowed') is True
    short_circuit_active = (
        short_circuit_allowed
        and trace.get('earlier_blocker_conclusively_established') is True
        and final_owner == short_circuit.get('terminal_owner', router)
        and trace.get('primary_substantive_result_emitted') is False
        and trace.get('forbidden_downstream_substantive_execution') == 0
    )

    availability = trace.get('specialist_availability')
    if not isinstance(availability, dict):
        availability = {}

    if mode == 'compatibility':
        requested_primary = case.get('requested_primary_owner') or case.get('required_primary_owner')
        requires_unavailable = case.get(
            'requires_specialist_unavailable_evidence',
            config.compatibility_requires_unavailable_evidence,
        )
        if requires_unavailable and requested_primary:
            state = availability.get(requested_primary)
            if state is None:
                evidence_gaps.append(f'specialist availability: {requested_primary}')
            elif state != 'unavailable':
                violations.append('ROUTER_OWNERSHIP_LEAK')
        if final_owner and final_owner != case.get('compatibility_owner', config.compatibility_owner):
            violations.append('ROUTER_OWNERSHIP_LEAK')

    if mode == 'multi_skill':
        genuine_ambiguity = trace.get('genuine_ambiguity') is True
        if expected_primary and not short_circuit_active:
            if expected_primary not in primary_owners:
                if final_owner == router and availability.get(expected_primary) == 'available' and not genuine_ambiguity:
                    violations.append('ROUTER_OWNERSHIP_LEAK')
                else:
                    violations.append('MISSING_REQUIRED_PRIMARY_OWNER')
            normal_owner = case.get('normal_terminal_owner')
            if normal_owner and final_owner and final_owner != normal_owner:
                if final_owner == router and availability.get(expected_primary) == 'available' and not genuine_ambiguity:
                    if 'ROUTER_OWNERSHIP_LEAK' not in violations:
                        violations.append('ROUTER_OWNERSHIP_LEAK')
                else:
                    violations.append('WRONG_FINAL_ANSWER_OWNER')
        router_policy = case.get('router_policy')
        if router_policy == 'required' and final_owner and final_owner != router:
            violations.append('WRONG_FINAL_ANSWER_OWNER')

    if short_circuit_active and trace.get('forbidden_downstream_substantive_execution') != 0:
        violations.append('FORBIDDEN_DOWNSTREAM_EXECUTION')

    violations = list(dict.fromkeys(violations))
    evidence_gaps = list(dict.fromkeys(evidence_gaps))
    if violations:
        verdict = 'FAIL'
    elif evidence_gaps:
        verdict = 'BLOCKED_EVIDENCE'
    else:
        verdict = 'PASS'
    return TraceEvaluation(verdict, tuple(violations), tuple(evidence_gaps))


def _legacy_selection_keys(case: dict) -> tuple[str, ...]:
    return tuple(
        key for key in ('expected_skill', 'expected_initial_skill', 'actual_first_skill')
        if key in case
    )


def _validate_case_support(case: dict, config: SkillSetConfig, cid: str, errors: list[str]) -> None:
    global_support = set(config.supporting_skills)
    for skill in case.get('allowed_supporting_skills', ()):
        if skill not in global_support:
            errors.append(f'{cid}: supporting skill is not allowlisted: {skill}')


def validate_routing_corpus(root: Path) -> list[str]:
    root = Path(root)
    config = load_skillset(root)
    skills = {skill.name for skill in config.skills}
    primary_specialists = set(config.primary_owner_by_stage.values())
    router = config.ambiguity_router
    routing = root / 'skillset/routing'
    errors: list[str] = []
    seen: set[str] = set()

    for name in CORPUS_FILES:
        cases = json.loads((routing / name).read_text(encoding='utf-8'))
        if not isinstance(cases, list):
            errors.append(f'{name}: corpus must be a list')
            continue
        for case in cases:
            cid = case.get('id')
            if not cid or cid in seen:
                errors.append(f'invalid or duplicate case id: {cid}')
                continue
            seen.add(cid)
            legacy = _legacy_selection_keys(case)
            if legacy:
                errors.append(f"{cid}: legacy first-skill fields are forbidden: {','.join(legacy)}")
            _validate_case_support(case, config, cid, errors)

            if name == 'direct-trigger.json':
                required = case.get('required_primary_owner')
                if required not in skills:
                    errors.append(f'{cid}: unknown required primary owner {required}')
                if case.get('normal_terminal_owner') != required:
                    errors.append(f'{cid}: normal terminal owner must match required primary owner')
                stages = case.get('expected_stage_family', [])
                if required == config.cross_cutting_owners.get('project_state'):
                    if stages:
                        errors.append(f'{cid}: direct project-state case must not own P-stages')
                else:
                    for stage in stages:
                        if config.primary_owner_by_stage.get(stage) != required:
                            errors.append(f'{cid}: {stage} is not owned by {required}')

            elif name == 'ambiguous-routing.json':
                if case.get('router_policy') != 'required':
                    errors.append(f'{cid}: ambiguous case must require router')
                if case.get('normal_terminal_owner') != router:
                    errors.append(f'{cid}: ambiguous case terminal owner must be {router}')
                if case.get('required_primary_owner') or case.get('requested_primary_owner'):
                    errors.append(f'{cid}: ambiguous case must not preselect a primary owner')

            elif name == 'upstream-blocker.json':
                requested = case.get('requested_primary_owner')
                if requested not in primary_specialists:
                    errors.append(f'{cid}: unknown requested primary owner {requested}')
                short = case.get('short_circuit') or {}
                if not case.get('must_stop'):
                    errors.append(f'{cid}: blocker case must stop')
                if short.get('allowed') is not True:
                    errors.append(f'{cid}: blocker case must allow short-circuit')
                if short.get('condition') != 'earlier_blocker_conclusively_established':
                    errors.append(f'{cid}: blocker short-circuit condition is invalid')
                if short.get('terminal_owner') != router:
                    errors.append(f'{cid}: blocker terminal owner must be {router}')

            elif name == 'compatibility.json':
                requested = case.get('requested_primary_owner')
                if requested not in primary_specialists:
                    errors.append(f'{cid}: unknown requested primary owner {requested}')
                if case.get('compatibility_owner') != config.compatibility_owner:
                    errors.append(f'{cid}: compatibility owner must be {config.compatibility_owner}')
                if case.get('requires_specialist_unavailable_evidence') is not True:
                    errors.append(f'{cid}: compatibility requires specialist-unavailable evidence')
                if case.get('normal_terminal_owner') != config.compatibility_owner:
                    errors.append(f'{cid}: compatibility terminal owner must be {config.compatibility_owner}')
                stage = case.get('fallback_stage')
                if stage and config.primary_owner_by_stage.get(stage) != requested:
                    errors.append(f'{cid}: fallback stage {stage} is not owned by {requested}')

    handoffs = json.loads((routing / 'cross-skill-handoff.json').read_text(encoding='utf-8'))
    if 'valid' in handoffs:
        errors.append('cross-skill handoff corpus contains legacy valid primary handoffs')

    for case in handoffs.get('valid_support_returns', []):
        cid = case.get('id')
        if case.get('type') != 'support_return':
            errors.append(f'{cid}: support return type must be support_return')
        if case.get('supporting_skill') not in config.supporting_skills:
            errors.append(f'{cid}: invalid supporting skill')
        if case.get('to_owner') not in skills:
            errors.append(f'{cid}: unknown support return owner')

    for case in handoffs.get('valid_ownership_handoffs', []):
        cid = case.get('id')
        if case.get('type') != 'ownership_handoff':
            errors.append(f'{cid}: ownership handoff type must be ownership_handoff')
        if case.get('from_owner') not in primary_specialists:
            errors.append(f'{cid}: ownership handoff must originate from a primary specialist')
        if case.get('to') != router:
            errors.append(f'{cid}: ownership handoff must return to {router}')

    for case in handoffs.get('forbidden_primary_chains', []):
        cid = case.get('id')
        edges = case.get('edges', [])
        if not edges:
            errors.append(f'{cid}: forbidden primary chain must contain an edge')
        for edge in edges:
            if not isinstance(edge, list) or len(edge) != 2:
                errors.append(f'{cid}: invalid primary-chain edge')
                continue
            source, target = edge
            if source not in primary_specialists or target not in primary_specialists or source == target:
                errors.append(f'{cid}: primary-chain edge must connect distinct primary specialists')

    for case in handoffs.get('forbidden_cycles', []):
        if not _has_cycle(case.get('edges', [])):
            errors.append(f"{case.get('id')}: protected cycle fixture is not cyclic")

    trace_path = routing / 'composition-traces.json'
    if not trace_path.is_file():
        errors.append('composition trace regression corpus missing')
        return errors

    fixtures = json.loads(trace_path.read_text(encoding='utf-8'))
    trace_ids: set[str] = set()
    protected_violations: set[str] = set()
    has_blocked_evidence = False
    normative_violations = {
        'MULTIPLE_PRIMARY_OWNERS',
        'SUPPORT_OWNERSHIP_LEAK',
        'ROUTER_OWNERSHIP_LEAK',
        'DIRECT_PRIMARY_CHAIN',
        'OWNERSHIP_LOOP',
    }
    for fixture in fixtures:
        fid = fixture.get('id')
        if not fid or fid in trace_ids:
            errors.append(f'invalid or duplicate trace fixture id: {fid}')
            continue
        trace_ids.add(fid)
        legacy = _legacy_selection_keys(fixture.get('case', {}))
        if legacy:
            errors.append(f"{fid}: trace case contains legacy first-skill fields: {','.join(legacy)}")
        expected = fixture.get('expected_verdict')
        if expected not in {'PASS', 'FAIL', 'BLOCKED_EVIDENCE'}:
            errors.append(f'{fid}: invalid expected verdict {expected}')
            continue
        result = evaluate_terminal_trace(fixture.get('case', {}), fixture.get('trace', {}), config)
        if result.verdict != expected:
            errors.append(f'{fid}: expected {expected}, got {result.verdict}')
        for violation in fixture.get('expected_violations', []):
            protected_violations.add(violation)
            if violation not in result.violations:
                errors.append(f'{fid}: missing expected violation {violation}')
        for gap in fixture.get('expected_evidence_gaps', []):
            if gap not in result.evidence_gaps:
                errors.append(f'{fid}: missing expected evidence gap {gap}')
        if expected == 'BLOCKED_EVIDENCE':
            has_blocked_evidence = True

    missing_violation_fixtures = normative_violations - protected_violations
    if missing_violation_fixtures:
        errors.append('missing composition violation fixtures: ' + ','.join(sorted(missing_violation_fixtures)))
    if not has_blocked_evidence:
        errors.append('missing BLOCKED_EVIDENCE composition trace fixture')

    return errors
