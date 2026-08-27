from __future__ import annotations
import json
from pathlib import Path
from .model import load_skillset

CORPUS_FILES = ('direct-trigger.json','ambiguous-routing.json','upstream-blocker.json','compatibility.json')

def _has_cycle(edges):
    graph={}
    for a,b in edges: graph.setdefault(a,set()).add(b)
    visiting=set(); visited=set()
    def dfs(node):
        if node in visiting: return True
        if node in visited: return False
        visiting.add(node)
        if any(dfs(n) for n in graph.get(node,())): return True
        visiting.remove(node); visited.add(node); return False
    return any(dfs(n) for n in list(graph))

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
