# Aegis Roadmap

## v0.1 — Single-Skill control plane

- Bootstrap routing and Earliest Untrusted Layer.
- 25 stage contracts.
- Authority, drift, supersession, defect, and gate governance.
- Verification-first rules.
- Implementation task packaging.
- Superpowers composition guidance.
- Standard output contracts.

## v0.2 — Evaluation & dogfooding

The first closure is `Aegis Evaluation & Dogfooding Framework v0.1`:

- protected 30-case seed corpus across routing, authority, defect, and gate behavior;
- extensible dogfood/incident regression corpus;
- deterministic corpus-integrity validator;
- CI integrity gate;
- critical-safety-error model;
- provisional deterministic behavioral thresholds;
- dogfood/incident -> regression-case workflow.

The framework intentionally separates corpus integrity from Aegis behavior. Corpus CI proves that evaluation inputs are structurally valid; it does not claim that Aegis itself passes the behavioral corpus.

Evaluation closures include the provider-neutral execution adapter, normalized extractor, deterministic scorer, evidence report pipeline, and an OpenAI hosted-skill driver whose live behavioral baseline remains environment-dependent when no API credential is available.

## v0.2.x — Project State Manifest + Authority Dependency Graph

This capability was pulled forward from the original v0.4 exploration because it unlocks reliable resume, supersession invalidation, and machine-readable Gate validity without waiting for model-provider evaluation.

`Aegis Project State Manifest + Authority Dependency Graph v0.1` introduces optional project-owned state:

```text
.aegis/
├── project.json
├── authorities.json
├── gates.json
├── evidence.json
└── state.json
```

Goals:

- persistent Authority Registry;
- validity-bearing dependency DAG;
- explicit Gate verdict vs current validity;
- Evidence Registry;
- supersession -> stale/needs-review propagation;
- deterministic generated state and drift detection;
- Aegis bootstrap from project-control state before normal routing.

The manifests never outrank contradictory Current Authority sources.

## v0.3 — Split high-value Skills

Promote frequently independent workflows into separate Skills while retaining a central router. Keep shared governance and output taxonomy in references rather than duplicating them.

Do not split solely to mirror P00-P36. Split when a workflow is independently triggered, independently testable, and benefits from its own progressive context.

## v0.4 — Project-state automation and reconciliation

Extend the v0.2.x manifest foundation only after real usage evidence. Candidate work includes controlled manifest mutation, cross-repository state, event/audit history when Git history is insufficient, and Notion/GitHub Authority reconciliation. Do not add these before the v0.1 manifest semantics are stable.

## v1.0 — Evidence-backed suite

Declare v1.0 only after Aegis has been exercised on multiple real projects and its routing, stage boundaries, authority classification, defect routing, gate vocabulary, and persistent project-state behavior have demonstrated stable behavior under regression evaluation.
