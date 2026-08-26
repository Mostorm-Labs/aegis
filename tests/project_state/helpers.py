import json
from pathlib import Path


def base_project():
    return {"schema_version":"0.2","project":{"id":"demo","name":"Demo","profile":"standard","required_layers":["problem","authority","verification"],"lifecycle_hint":"implementation"}}


def base_authorities():
    return {"schema_version":"0.2","authorities":[
        {"id":"schema-v1","scope":"document","kind":"semantic_schema","version":"v1","status":"Current","ref":"docs/schema-v1.md","depends_on":[]},
        {"id":"arch-v1","scope":"runtime","kind":"system_architecture","version":"v1","status":"Current","ref":"docs/arch-v1.md","depends_on":["schema-v1"]}
    ],"impact_reviews":[]}


def base_evidence():
    return {"schema_version":"0.2","evidence":[{"id":"ev-g1","type":"automated_test","ref":"ci://g1","status":"available","subject_ids":["G1"]}]}


def base_gates():
    return {"schema_version":"0.2","gates":[{"id":"G1","stage":"P34","verdict":"PASS","validity":"current","authority_ids":["arch-v1"],"evidence_ids":["ev-g1"]}]}


def base_integrations():
    return {"schema_version":"0.2","integrations":[]}


def manifests():
    return base_project(), base_authorities(), base_gates(), base_evidence()


def write_project(root: Path, project=None, authorities=None, gates=None, evidence=None, state=None, integrations=None):
    aegis = root / ".aegis"
    aegis.mkdir(parents=True, exist_ok=True)
    project = base_project() if project is None else project
    authorities = base_authorities() if authorities is None else authorities
    gates = base_gates() if gates is None else gates
    evidence = base_evidence() if evidence is None else evidence
    integrations = base_integrations() if integrations is None else integrations
    for name, data in [("project.json",project),("authorities.json",authorities),("gates.json",gates),("evidence.json",evidence),("integrations.json",integrations)]:
        (aegis/name).write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    if state is not None:
        (aegis/"state.json").write_text(json.dumps(state, indent=2)+"\n", encoding="utf-8")
    return aegis
