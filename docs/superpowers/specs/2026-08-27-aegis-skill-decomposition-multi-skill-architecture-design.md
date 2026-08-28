# 09 Aegis Skill Decomposition & Multi-Skill Architecture v0.1

Status: **Proposed Design Authority v0.1 — written spec pending human review; implementation not authorized.**

## 1. Context and Authority

Aegis has reached a point where the current single `aegis` Skill is a healthy thin control plane with progressively loaded references, not an overloaded monolith. The next problem is therefore not file size; it is whether several cognitive workflows are mature enough to become independently discoverable, independently loadable, and independently testable Skills without fragmenting Aegis authority.

Current upstream authority and evidence:

- Aegis methodology and stage contracts remain Current Authority.
- Project State v0.3 is Current and integrated.
- 08 Self-Hosting is accepted with `PASS_WITH_FINDINGS`; F08-01, F08-02, and F08-03 are closed.
- The protected evaluation corpus remains 30 seed cases plus four dogfood cases = 34 cases.
- Existing OpenAI hosted provider tooling still packages one top-level `skills/aegis/` bundle. The live provider baseline remains independently `BLOCKED_ENVIRONMENT` because no authorized API key is available.

09 does not redesign P00-P36, Gate verdicts, defect taxonomy, Project State v0.3, or Superpowers coding mechanics.

## 2. Problem Statement

The single Aegis Skill currently owns both project-level routing/safety and execution guidance for multiple stage families. That is safe, but it limits direct specialist triggering and stage-specific context loading.

09 introduces specialist Skills only where a cognitive workflow has a stable independent trigger, clear ownership, explicit input/output contract, and credible independent verification surface.

The decomposition must not create competing routers, competing definitions of Authority/Gate/status semantics, stage ownership ambiguity, handoff loops, provider incompatibility, or manually synchronized shared invariants.

## 3. Selected Architecture — Hub-and-Spoke + Composite Compatibility Facade

Aegis becomes a Skill System with one central control-plane Skill and eight specialist Skills.

```text
                         aegis
                Router / Control Plane
                         |
       +-----------------+------------------+
       |                 |                  |
       v                 v                  v
project-state        discovery           modeling
 cross-cutting        P00-P03            P10-P13
       |                                    |
       +---------------> architecture <-----+
                          P14-P18
                              |
                        verification
                            P20
                              |
       +----------------------+-------------------+
       |                      |                   |
       v                      v                   v
  governance           implementation        gate-review
   P21-P24               P30-P33              P34-P36
                              |
                         Superpowers
```

The nine entrypoints are:

| Skill | Primary ownership | Typical direct trigger |
| --- | --- | --- |
| `aegis` | source classification, Project State preflight, Earliest Untrusted Layer, profile selection, ambiguity/cross-domain routing, compatibility facade | “What should this project do next?” |
| `aegis-project-state` | machine-readable Authority/Gate/Evidence/Integration state and deterministic Project State validation | “Read or validate this project’s `.aegis/` state.” |
| `aegis-discovery` | P00-P03 | problem discovery, research, requirements, capability traceability |
| `aegis-modeling` | P10-P13 | object model, behavior, semantic schema, operation/mutation model |
| `aegis-architecture` | P14-P18 | system/module architecture, runtime flow, platform contract, engineering/optimization architecture |
| `aegis-verification` | P20 | invariants, oracle/golden/fixture, evidence design, verification matrix |
| `aegis-governance` | P21-P24 | authority review, drift review, supersession, release readiness |
| `aegis-implementation` | P30-P33 | implementation planning/task packaging, implementation control, interrupted-work resume |
| `aegis-gate-review` | P34-P36 | Gate audit, defect classification, fix/reverification routing |

No P-stage has more than one primary owner. Cross-cutting Project State preflight does not count as P-stage ownership.

## 4. Why Not One Skill per Stage

Aegis explicitly rejects a P00-P36 one-Skill-per-stage topology. Adjacent stages such as P10-P13, P21-P24, and P34-P36 share coherent cognitive loops and substantial contract context. Mechanical splitting would increase trigger collisions, package count, handoff ceremony, and shared-contract drift.

Future decomposition requires dogfood/evaluation evidence that a workflow is independently triggerable and testable. Skill count is not a success metric.

## 5. Runtime Selection Rules

### 5.1 Specific Skill Wins

When the request is unambiguously owned by one specialist, prefer that specialist over the general `aegis` facade.

```text
“Design an operation schema.”          -> aegis-modeling
“Review this authority drift.”         -> aegis-governance
“Define the oracle for this contract.” -> aegis-verification
“Audit this PR Gate evidence.”         -> aegis-gate-review
“Validate the root .aegis state.”      -> aegis-project-state
```

### 5.2 Central Router Owns Ambiguity

Use `aegis` when the request is broad/cross-domain, the lifecycle layer is unknown, multiple specialists plausibly match, the user asks where to start/continue, or a specialist discovers an earlier blocker outside its owned family.

The router owns source classification, Project State preflight when present, Earliest Untrusted Layer selection, profile selection, and specialist choice.

### 5.3 Specialist Safety Preflight

A specialist does not become a second router. On direct invocation it performs only the minimum preflight needed to answer:

> “May I safely execute my owned stage family now?”

Rules:

1. If no Project State context exists, use explicit Authority/Evidence supplied by the task and execute only the owned family.
2. If `.aegis/` exists and deterministic `tools.aegis_state` (or equivalent accepted tooling) is available, validate/check it before downstream execution.
3. If `.aegis/` exists but cannot be deterministically verified, do **not** trust committed `state.json` as Authority. Fail closed and hand back to `aegis` / `aegis-project-state` for state resolution unless explicit Current Authority independently proves the specialist is safe to execute.
4. If verified Project State or explicit Authority shows an earlier untrusted layer, stop and hand back to `aegis` with blocker + stage hint.
5. A specialist must never silently repair upstream authority or choose an unrelated specialist as a new routing authority.

## 6. Cross-Skill Handoff Contract

Handoff is execution/navigation metadata, not Authority, Evidence, Gate, or Project State.

```yaml
owner_skill: aegis-architecture
completed_stage: P14
status: READY
authority_refs:
  - architecture-v0.4
evidence_required:
  - architecture-review
next_stage: P20
suggested_skill: aegis-verification
blockers: []
```

Rules:

1. Specialists may emit `next_stage` / `suggested_skill` only when the transition is unambiguous.
2. Ambiguous/cross-domain rerouting remains owned by `aegis`.
3. Earlier blockers return to `aegis`; do not create specialist repair chains.
4. Durable facts remain in Authority/Evidence/Gate/Integration systems.
5. Handoff cycles are a verification failure.

## 7. Project State Boundary

`aegis-project-state` is cross-cutting, not a P-stage family. All specialists respect `.aegis/` when present, but do not implement independent copies of the Project State algorithm.

`state.json` remains generated cache only. 09 does not change Project State v0.3 schemas.

## 8. Canonical Source vs Distribution Layout

After migration, canonical Skill System source lives under `skillset/`; distributable Skill directories under `skills/` are generated, validated, self-contained, and committed.

```text
skillset/
├── manifest.json
├── ownership.json
├── shared/
│   ├── core-invariants.md
│   ├── stage-vocabulary.md
│   ├── authority-contract.md
│   ├── status-contract.md
│   └── handoff-contract.md
├── skills/
│   ├── aegis/
│   ├── aegis-project-state/
│   ├── aegis-discovery/
│   ├── aegis-modeling/
│   ├── aegis-architecture/
│   ├── aegis-verification/
│   ├── aegis-governance/
│   ├── aegis-implementation/
│   └── aegis-gate-review/
└── routing/
    ├── direct-trigger.json
    ├── ambiguous-routing.json
    ├── cross-skill-handoff.json
    ├── upstream-blocker.json
    └── compatibility.json

scripts/build_skillset.py

skills/    # generated + committed standalone distributions
```

### 8.1 Single-Owner Metadata Rule

`manifest.json` and `ownership.json` must not encode the same authority twice.

- `skillset/manifest.json` is canonical for Skill identity, source path, distribution path, facade/specialist role, shared-reference inclusion, and build metadata.
- `skillset/ownership.json` is canonical for P-stage primary ownership and cross-cutting ownership declarations.
- `manifest.json` may reference `ownership.json`; it must not duplicate the P-stage ownership map.
- CI validates referential integrity between both files and rejects duplicate or contradictory ownership declarations.

### 8.2 Editing Rule

After migration:

- edit canonical skill definitions/shared contracts under `skillset/`;
- do not manually edit generated shared-contract copies under `skills/*`;
- generated output is committed so existing consumers require no runtime build step;
- CI runs `build_skillset.py --check` and fails if committed distributions differ from canonical source;
- deterministic generation must not inject timestamps or other unstable bytes.

### 8.3 Standalone Distribution Rule

Every `skills/<name>/` remains a valid standalone Skill with its own `SKILL.md`, `agents/openai.yaml`, and required references. A specialist package must not depend on sibling Skill directories at runtime.

The build may copy canonical shared contract text into each distribution. Digest/check validation prevents drift.

## 9. Shared Contract Ownership

`skillset/shared/` is globally canonical for:

- lifecycle stage IDs/names;
- Authority source classes;
- Earliest Untrusted Layer semantics;
- default statuses;
- defect taxonomy;
- Gate verdict vocabulary;
- four minimum Aegis invariant questions;
- handoff contract;
- Superpowers boundary rule.

Specialists may specialize usage but cannot silently redefine these concepts. A shared-contract change is a system-level Authority change and requires drift review before regeneration.

## 10. Composite `aegis` Compatibility Facade

The central `aegis` Skill remains a supported self-contained distribution for:

1. general/ambiguous user entry;
2. fallback when only one Skill is available;
3. compatibility with existing 06-02 Hosted Skill provider tooling;
4. behavioral reference proving decomposition did not change lifecycle semantics.

The facade stays semantically complete enough to execute all Aegis stage families when specialists are unavailable. Its stage-family execution references are assembled from the same canonical source as specialists; they are not a second independently maintained methodology.

## 11. Hosted Provider / Evaluation Compatibility

Current provider tooling zips `skills/aegis/` as one top-level Skill. 09 preserves that distribution path.

```text
Canonical Skill Set
        |
        +--> specialist distributions -> multi-Skill capable environments
        |
        +--> composite skills/aegis   -> current single-Skill provider path
```

The absence of an API key does not block deterministic architecture/build/package work. The existing live provider baseline remains independently `BLOCKED_ENVIRONMENT` and must not be fabricated or weakened.

A future true hosted multi-Skill driver is outside 09 v0.1.

## 12. Superpowers Boundary

Aegis continues to own project-level authority, lifecycle routing, evidence obligations, task boundaries, Gate review, and release readiness. Superpowers continues to own coding-agent mechanics such as brainstorming, writing plans, TDD, debugging, worktrees, plan execution, and verification-before-completion.

`aegis-implementation` must not duplicate those mechanics.

## 13. Verification Model

09 distinguishes three evidence layers. They must not be conflated.

### 13.1 Deterministic Structural/Build Gate

Machine-verifiable requirements:

| Dimension | Acceptance |
| --- | --- |
| P-stage primary ownership coverage | 100% |
| P-stage with multiple primary owners | 0 |
| Unowned P-stage | 0 |
| Invalid standalone distribution | 0 |
| Shared-contract digest mismatch | 0 |
| Generated distribution drift | 0 |
| Existing 34-case lifecycle semantic regression | 0 |
| Protected explicit-router case mismatch | 0 |
| Forbidden downstream execution in protected preflight cases | 0 |
| Protected handoff cycle | 0 |
| Composite facade deterministic compatibility | required |

The routing corpus under `skillset/routing/` is the **intended-routing oracle** for explicit Aegis routing/handoff behavior. Passing it does not prove ChatGPT platform auto-selection.

### 13.2 Skill Package Gate

Skill Creator validates and packages every reviewed distribution. Package validity proves structure/instruction references, not behavioral trigger correctness.

### 13.3 Platform Behavioral Trigger Gate

Real specialist auto-discovery depends on platform Skill selection from descriptions. It requires separate behavioral evidence, such as manual installed-Skill dogfood or a future hosted multi-Skill evaluation harness.

Required protected behaviors include:

- unambiguous prompt selects the intended specialist;
- ambiguous/cross-domain prompt selects central `aegis`;
- direct specialist invocation with an earlier blocker stops and reroutes safely;
- composite fallback remains usable when specialists are unavailable.

A deterministic routing corpus or successful package build **must not** be reported as proof of platform auto-trigger behavior.

If platform behavioral evidence cannot be obtained at P34, the behavioral decomposition Gate is `BLOCKED_EVIDENCE`, not `PASS_WITH_FINDINGS`. Deterministic 09 tooling may still have its own PASS verdict.

## 14. Migration Strategy

Migration is incremental and reversible.

### Phase 1 — Control Layer

Create manifest/ownership/shared/routing/build-check tooling without changing current `skills/aegis` behavior.

### Phase 2 — Composite Migration

Move current Aegis source into canonical skillset source and prove regenerated `skills/aegis` deterministic and behavioral compatibility with the accepted composite baseline.

This is the highest-risk migration because source ownership changes while the distribution interface must not.

### Phase 3 — Specialists

Add specialist distributions one family at a time. Add intended-routing, preflight, handoff, and package tests before each specialist is accepted.

Recommended order:

```text
aegis-project-state
-> aegis-governance
-> aegis-gate-review
-> aegis-verification
-> aegis-architecture
-> aegis-modeling
-> aegis-discovery
-> aegis-implementation
```

### Phase 4 — Multi-Skill Dogfood

Use real tasks to exercise direct specialist selection, central routing, upstream-blocker rerouting, handoff, and composite fallback. Any real routing failure becomes permanent routing/dogfood regression.

## 15. Failure and Rollback Rules

- Unknown trigger ambiguity -> central `aegis`.
- Specialist cannot verify present Project State -> fail closed to Aegis/project-state resolution unless independent Current Authority proves safety.
- Earlier Authority blocker -> specialist stops and hands back.
- Generated/distributed content drift -> CI failure.
- Composite/specialist semantic conflict -> classify at Authority or implementation layer; never silently choose one.
- Existing 34-case corpus regression -> no promotion.
- Package validity without behavioral routing evidence -> `BLOCKED_EVIDENCE` for behavioral decomposition.
- Live provider baseline unavailable -> preserve its independent `BLOCKED_ENVIRONMENT`; do not make it a false blocker for deterministic 09 work.

Rollback is the last accepted composite `skills/aegis`; specialist adoption never requires deleting that fallback.

## 16. Non-Goals

09 v0.1 does not:

- create one Skill per P-stage;
- delete/deprecate the `aegis` facade;
- change Project State v0.3;
- redefine P00-P36, defect taxonomy, Gate verdicts, or default statuses;
- add event sourcing for handoffs;
- duplicate Superpowers mechanics;
- require an API key for deterministic 09 gates;
- claim Skill validation or intended-routing tests prove platform auto-trigger behavior;
- split additional release/semantic/defect Skills without dogfood evidence.

## 17. Acceptance Boundary

This design may proceed to P30/P31 only after human approval of the written spec.

Later implementation has two independent acceptance tracks:

### 17.1 Deterministic Skill-System Tooling Gate

Requires:

1. all nine distributions validate standalone;
2. exactly one primary owner for every P00-P36 stage;
3. central router is the only ambiguity/cross-domain router;
4. specialist safety preflight blocks downstream work on earlier/unverifiable project-state conditions;
5. shared contracts derive from one canonical source with zero drift;
6. generated `skills/*` is deterministic and committed;
7. composite `skills/aegis` remains supported and deterministically compatible;
8. existing 34-case lifecycle corpus has zero critical regression;
9. intended-routing/handoff corpus passes;
10. Skill Creator validation/package succeeds for every distribution.

### 17.2 Multi-Skill Behavioral Gate

Requires real platform evidence for at least:

1. one direct specialist auto-selection path;
2. one ambiguous central-router selection path;
3. one upstream-blocker specialist reroute;
4. one composite fallback path.

If this evidence is unavailable, report `BLOCKED_EVIDENCE` for the behavioral Gate. Do not promote static/deterministic evidence into behavioral evidence.

The unrelated live 06-02 provider baseline keeps its exact independent Gate status.

## 18. Required Next Lifecycle

After written-spec approval:

```text
P30 Implementation Planning
-> P31 Task Packaging
-> RED-first ownership / build / intended-routing tests
-> Skill Set Control Layer
-> composite compatibility migration
-> specialist generation
-> deterministic regression
-> platform/manual multi-Skill dogfood
-> P34 Gate Review
-> repository integration
```

Until the written spec is approved, no specialist Skill creation or `skills/aegis` migration is authorized.
