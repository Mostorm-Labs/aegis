# Aegis Skill Decomposition & Multi-Skill Architecture v0.1

Status: **Current Proposed Execution Authority — implementation complete; runtime composition semantics blocked by `F09-04`; proposed replacement v0.2 is under written-spec review.**

Proposed replacement for Runtime Selection / Project-State support composition / Handoff / Platform Behavioral Trigger semantics: `docs/skill-decomposition-v0.2.md`. v0.1 is **not yet Superseded**; its nine-entrypoint topology, stage ownership, canonical source/build model, and historical evidence remain authoritative for this PR until v0.2 is accepted.

## Purpose

Aegis v0.1 decomposes the accepted composite Skill into a Hub-and-Spoke Skill System without changing Aegis lifecycle semantics. The central `aegis` Skill remains the sole ambiguity/cross-domain router and a complete single-Skill compatibility facade.

## Entry points

- `aegis` — central router and compatibility facade.
- `aegis-project-state` — cross-cutting deterministic Project State inspection; no P-stage ownership.
- `aegis-discovery` — P00-P03.
- `aegis-modeling` — P10-P13.
- `aegis-architecture` — P14-P18.
- `aegis-verification` — P20.
- `aegis-governance` — P21-P24.
- `aegis-implementation` — P30-P33.
- `aegis-gate-review` — P34-P36.

Every P-stage has exactly one primary owner. `skillset/ownership.json` is the only machine-readable stage-ownership authority.

## Canonical source and generated distributions

`skillset/` is canonical source. `skills/*` is deterministic generated output and is committed so existing consumers require no runtime build step.

- `skillset/manifest.json` owns Skill identity/source/distribution/build metadata.
- `skillset/ownership.json` owns P-stage and cross-cutting ownership.
- `skillset/shared/` owns global Aegis invariants and vocabulary.
- `skillset/skills/` owns per-Skill source instructions and specialist references.
- `skillset/routing/` owns protected intended-routing/handoff cases.
- `scripts/build_skillset.py --check` rejects generated distribution drift.

Generated Skills are self-contained and may not depend on sibling Skill directories at runtime.

## Specialist safety preflight

A directly selected specialist performs only the minimum preflight needed to decide whether its owned stage family may execute. If `.aegis/` exists and deterministic Project State validation is available, validate/check before downstream work. If Project State cannot be deterministically verified, do not trust committed `state.json` as Authority; fail closed to `aegis` / `aegis-project-state` unless explicit Current Authority independently proves execution safety. Any earlier untrusted layer stops specialist execution and hands control back to `aegis`.

**Governance note:** this preflight/composition wording is the area blocked by `F09-04`. Do not reinterpret it beyond v0.1's historical meaning while v0.2 is pending review.

## Handoff boundary

Cross-Skill handoff is ephemeral navigation metadata. It is not Authority, Evidence, Gate, Integration, or Project State. Durable facts remain in existing Aegis control systems. Protected handoff cycles are invalid.

## Composite compatibility

`skills/aegis/` remains a semantically complete distribution assembled from the same canonical source/shared contracts as specialists. Existing OpenAI hosted provider tooling may continue to package that one directory with top-level archive name `aegis/`. 09 does not introduce a hosted multi-Skill provider and does not require an OpenAI API key.

## Evidence split

Three evidence layers must remain separate:

1. **Deterministic Skill-System Tooling** — ownership, source/distribution reproducibility, standalone structure, intended routing/handoff corpus, Project State/eval regressions.
2. **Skill Package Evidence** — official Skill Creator validation/package of each distribution.
3. **Platform Behavioral Trigger Evidence** — actual installed-Skill auto-selection and rerouting behavior.

The deterministic routing corpus defines intended Aegis routing. It is not proof that ChatGPT auto-selects the correct installed Skill. If platform behavioral evidence is unavailable, its Gate remains `BLOCKED_EVIDENCE` rather than being inferred from static tests.

The existing live OpenAI behavioral baseline remains independently `BLOCKED_ENVIRONMENT` until real provider evidence exists.

## Deterministic Gate

Required repository evidence:

```text
SKILLSET_VALID
SKILLSET_STATE_OK
ROUTING_OK
SKILLS_VALID
skillset unit tests PASS
Project State regressions PASS
evaluation corpus PASS
evaluation unit tests PASS
```

Official Skill Creator must additionally validate/package all nine reviewed distributions before P34 deterministic-tooling acceptance.
