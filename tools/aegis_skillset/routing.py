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


def validate_routing_corpus(root: Path) -> list[str]:
    root=Path(root); config=load_skillset(root); skills={s.name for s in config.skills}; errors=[]
    routing=root/'skillset/routing'
    seen=set()
    for name in CORPUS_FILES:
        cases=json.loads((routing/name).read_text(encoding='utf-8'))
        for case in cases:
            cid=case.get('id')
            if not cid or cid in seen: errors.append(f'invalid or duplicate case id: {cid}')
            seen.add(cid)
            expected=case.get('expected_skill')
            if expected not in skills: errors.append(f'{cid}: unknown expected skill {expected}')
            if name=='ambiguous-routing.json' and expected!='aegis': errors.append(f'{cid}: ambiguous case must route to aegis')
            if name=='upstream-blocker.json':
                if not case.get('must_stop') or expected!='aegis': errors.append(f'{cid}: blocker case must stop and route to aegis')
            if name=='direct-trigger.json':
                stages=case.get('expected_stage_family',[])
                for stage in stages:
                    if config.primary_owner_by_stage.get(stage)!=expected:
                        errors.append(f'{cid}: {stage} is not owned by {expected}')
    handoffs=json.loads((routing/'cross-skill-handoff.json').read_text(encoding='utf-8'))
    for case in handoffs.get('valid',[]):
        if case['from'] not in skills or case['to'] not in skills: errors.append(f"{case['id']}: unknown handoff skill")
    for case in handoffs.get('forbidden_cycles',[]):
        if not _has_cycle(case['edges']): errors.append(f"{case['id']}: protected cycle fixture is not cyclic")
    valid_edges=[(c['from'],c['to']) for c in handoffs.get('valid',[])]
    if _has_cycle(valid_edges): errors.append('valid handoff graph contains cycle')
    return errors
