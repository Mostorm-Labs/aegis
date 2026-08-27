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

The single Aegis Skill currently owns both:

1. project-level routing and safety invariants; and
2. detailed execution guidance for multiple stage families.

That is safe, but it limits direct specialist triggering and forces unrelated stage-family context to remain behind the same entrypoint. The goal is to introduce specialist Skills only where a cognitive workflow has a stable independent trigger, clear ownership, an explicit input/output contract, and a credible independent verification surface.

The decomposition must not create:

- multiple competing routers;
- multiple definitions of Authority/Gate/status semantics;
- stage ownership ambiguity;
- handoff loops;
- provider/evaluation incompatibility;
- manually synchronized copies of shared invariants.

## 3. Selected Architecture: Hub-and-Spoke with Composite Compatibility Facade

Aegis becomes a Skill System with one central control-plane Skill and eight specialist Skills.

```text
                         aegis
                Router / Control Plane
                         |
       +-----------------+------------------+
       |                 |                  |
       v                 v                  v
project-state        discovery           modeling
  cross-cutting       P00-P03            P10-P13
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
| `aegis` | source classification, `.aegis` preflight, Earliest Untrusted Layer, profile selection, cross-domain routing, compatibility facade | “What should this project do next?” |
| `aegis-project-state` | machine-readable Authority/Gate/Evidence/Integration state and deterministic project-state validation | “Read or validate this project’s `.aegis/` state.” |
| `aegis-discovery` | P00-P03 | problem discovery, research, requirements, capability traceability |
| `aegis-modeling` | P10-P13 | object model, behavior, semantic schema, operation/mutation model |
| `aegis-architecture` | P14-P18 | system/module architecture, runtime flow, platform contract, engineering/optimization architecture |
| `aegis-verification` | P20 | invariants, oracle/golden/fixture, evidence design, verification matrix |
| `aegis-governance` | P21-P24 | authority review, drift review, supersession, release readiness |
| `aegis-implementation` | P30-P33 | implementation planning/task packaging, implementation control, interrupted-work resume |
| `aegis-gate-review` | P34-P36 | Gate audit, defect classification, fix/reverification routing |

No P-stage has more than one primary owner. Cross-cutting preflight does not count as stage ownership.

## 4. Why Not One Skill per Stage

Aegis explicitly rejects a P00-P36 one-Skill-per-stage topology.

Adjacent stages such as P10-P13, P21-P24, and P34-P36 share a coherent cognitive loop and substantial contract context. Splitting them mechanically would increase trigger collisions, handoff ceremony, package count, and shared-contract drift without creating meaningfully independent workflows.

Future decomposition requires dogfood or evaluation evidence that a workflow has become independently triggerable and testable. Skill count is not a success metric.

## 5. Runtime Selection Rules

### 5.1 Specific Skill Wins

When the user request is unambiguously owned by one specialist, prefer that specialist over the general `aegis` facade.

Examples:

```text
“Design an operation schema.”            -> aegis-modeling
“Review this authority drift.”           -> aegis-governance
“Define the oracle for this contract.”    -> aegis-verification
“Audit this PR Gate evidence.”            -> aegis-gate-review
“Validate the root .aegis state.”         -> aegis-project-state
```

### 5.2 Central Router Owns Ambiguity

Use `aegis` when:

- the request is broad or cross-domain;
- the correct lifecycle layer is not yet known;
- multiple specialist descriptions plausibly match;
- the user asks where to start or continue;
- a specialist discovers an earlier blocker outside its owned stage family.

The router performs source classification, Project State preflight when present, Earliest Untrusted Layer selection, profile selection, and specialist choice.

### 5.3 Specialist Safety Preflight

A specialist does not become a second router. On direct invocation it performs only the minimum safety preflight needed to answer:

> “May I safely execute my owned stage family now?”

If `.aegis/` or explicit authority evidence shows an earlier untrusted layer, the specialist must stop downstream execution and return a handoff to `aegis` with the blocker and stage hint. It must not silently repair an upstream layer or choose an unrelated specialist as a new authority.

## 6. Cross-Skill Handoff Contract

Cross-Skill handoff is an execution/navigation envelope, not Authority, Evidence, Gate, or Project State.

Canonical logical shape:

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

1. A specialist may emit `next_stage` and `suggested_skill` when the transition is unambiguous.
2. The central router remains the authority for ambiguous or cross-domain rerouting.
3. A handoff must never create a new source of durable truth.
4. Durable facts belong in the existing Authority/Evidence/Gate/Integration system.
5. A handoff that encounters an earlier blocker must point back to `aegis` rather than creating specialist-to-specialist repair chains.
6. Handoff cycles are a verification failure.

## 7. Project State as Cross-Cutting Preflight

`aegis-project-state` is not a lifecycle stage family. It owns deterministic inspection and validation of `.aegis/` and the Project State v0.3 contract.

All stage specialists must respect Project State when it is present, but must not carry independent copies of the Project State algorithm.

Runtime rule:

```text
specialist selected
-> detect project-state context
-> validate/read project-control state using available deterministic tooling
-> earlier blocker exists?
   -> yes: stop and hand off to aegis
   -> no: execute owned stage family
```

`state.json` remains generated cache only. 09 does not change the Project State v0.3 schema.

## 8. Canonical Source vs Distribution Layout

09 introduces a Skill Set Control Layer. After migration, canonical multi-Skill definitions live under `skillset/`; distributable Skill bundles live under `skills/` and are generated, validated, and committed.

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

scripts/
└── build_skillset.py

skills/                       # generated + committed distributions
├── aegis/
├── aegis-project-state/
├── aegis-discovery/
├── aegis-modeling/
├── aegis-architecture/
├── aegis-verification/
├── aegis-governance/
├── aegis-implementation/
└── aegis-gate-review/
```

### 8.1 Editing Rule

After migration:

- edit canonical skill definitions and shared contracts under `skillset/`;
- do not manually edit generated shared contract copies under `skills/*`;
- build output is committed so existing consumers do not require a runtime build step;
- CI runs `build_skillset.py --check` and fails if committed distributions differ from canonical source.

### 8.2 Self-Contained Distribution Rule

Every directory under `skills/<name>/` must remain a valid standalone Skill with its own `SKILL.md`, `agents/openai.yaml`, and required references. A specialist package must not depend on sibling Skill directories at runtime.

The build may copy canonical shared contract text into each distribution. Digest/check validation prevents those copies from drifting.

## 9. Shared Contract Ownership

These concepts remain globally canonical and must not be redefined independently inside specialists:

- lifecycle stage IDs and names;
- Authority source classes;
- Earliest Untrusted Layer semantics;
- default status vocabulary;
- defect taxonomy;
- Gate verdict vocabulary;
- four minimum Aegis invariant questions;
- cross-Skill handoff envelope;
- Superpowers boundary rule.

`skillset/shared/` owns these contracts. Specialist instructions may reference or specialize them, but may not silently change their meaning.

A change to a shared contract is an Aegis system-level authority change and requires appropriate drift review before regeneration.

## 10. Composite `aegis` Compatibility Facade

The central `aegis` Skill remains a supported distribution target.

It serves four purposes:

1. general user entrypoint and ambiguity router;
2. fallback in environments where only one Skill is available;
3. compatibility target for existing 06-02 Hosted Skill provider tooling;
4. behavioral reference for proving that decomposition did not change Aegis lifecycle semantics.

The composite facade must remain semantically complete enough to execute all Aegis stage families when specialists are unavailable. Its stage-family execution references are assembled from the same canonical skillset source used to build specialists; they are not maintained as an independent second methodology.

## 11. Hosted Provider / Evaluation Compatibility

Current provider tooling builds a deterministic ZIP from `skills/aegis/` and uploads one top-level `aegis` Skill. 09 preserves that path.

Distribution model:

```text
Canonical Skill Set
        |
        +--> specialist distributions -> multi-Skill capable environments
        |
        +--> composite skills/aegis   -> current single-Skill provider path
```

09 v0.1 does not require an OpenAI API key and does not require a live hosted multi-Skill provider run to complete deterministic architecture/tooling gates.

The existing live provider baseline remains independently `BLOCKED_ENVIRONMENT`. 09 must not fabricate behavioral provider evidence or weaken that Gate.

Future provider work may add a true multi-Skill hosted driver, but that is not required to accept the v0.1 decomposition architecture.

## 12. Superpowers Boundary

The existing division remains unchanged:

- Aegis owns project-level control: authority, lifecycle routing, contracts, evidence obligations, task boundaries, Gate review, release readiness.
- Superpowers owns coding-agent mechanics such as brainstorming, writing plans, TDD, systematic debugging, worktree isolation, plan execution, and verification-before-completion.

`aegis-implementation` must not copy Superpowers mechanics. It decides when coding is authorized, what authority constrains it, what evidence must return, and where failures route.

## 13. Trigger and Ownership Verification Design

09 must prove decomposition behavior, not merely package validity.

Required deterministic verification dimensions:

| Dimension | Acceptance |
| --- | --- |
| P-stage primary ownership coverage | 100% |
| P-stage with multiple primary owners | 0 |
| Unowned P-stage | 0 |
| Invalid specialist packages | 0 |
| Shared-contract digest mismatch | 0 |
| Generated distribution drift | 0 |
| Critical safety regression | 0 |
| Existing 34-case lifecycle semantic regression | 0 |
| Unambiguous direct-trigger cases selecting wrong specialist | 0 |
| Ambiguous cases bypassing central router | 0 |
| Forbidden downstream execution after earlier blocker | 0 |
| Handoff cycle in protected cases | 0 |
| Composite facade compatibility | required |

The new routing corpus lives under `skillset/routing/` and must include at least:

- direct specialist triggers;
- ambiguous requests that must route through `aegis`;
- cross-Skill handoffs;
- earlier-upstream-blocker cases;
- single-Skill composite compatibility cases.

Static package validation does not by itself prove behavioral routing correctness.

## 14. Migration Strategy

Migration must be incremental and reversible.

### Phase 1 — Control Layer

Create `skillset/manifest.json`, `ownership.json`, shared contracts, routing corpus schema/cases, and deterministic build/check tooling. Do not change the current `skills/aegis` behavior yet.

### Phase 2 — Generate Composite from Canonical Source

Move current Aegis content into canonical skillset source and prove that regenerated `skills/aegis` is behaviorally compatible with the current distribution.

This is the highest-risk migration point because it changes source ownership while preserving the same distribution interface.

### Phase 3 — Add Specialists

Generate and validate specialist Skill distributions one stage family at a time. Add trigger and handoff cases before each specialist is considered accepted.

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

The order prioritizes workflows already exercised most strongly by self-hosting and evidence-gated development.

### Phase 4 — Multi-Skill Dogfood

Use real Aegis/Axiom-style tasks to compare direct specialist selection, central routing, handoffs, and composite fallback. Any real routing failure becomes a permanent routing/dogfood regression.

## 15. Failure and Rollback Rules

09 must fail closed.

- Trigger ambiguity not represented in the routing corpus -> route through `aegis`, not an arbitrary specialist.
- Specialist discovers missing/upstream authority -> stop and hand off; do not continue downstream.
- Generated distributions differ from canonical source -> CI failure.
- Composite facade differs semantically from specialist/shared authority -> `BLOCKED_AUTHORITY` or `BLOCKED_IMPLEMENTATION` depending on ownership.
- Existing 34-case corpus regresses -> no decomposition promotion.
- Specialist packaging succeeds but behavioral routing is unproven -> `BLOCKED_EVIDENCE`, not PASS.
- Live OpenAI provider baseline remains unavailable -> preserve `BLOCKED_ENVIRONMENT`; do not make it a false blocker for deterministic 09 work that does not require it.

Rollback is to the last accepted composite `skills/aegis` distribution. Specialist adoption must not require deleting that fallback.

## 16. Non-Goals

09 v0.1 explicitly does not:

- create one Skill per P-stage;
- delete or deprecate the `aegis` facade;
- change Project State v0.3 schemas;
- redefine P00-P36 stage semantics;
- redefine defect taxonomy, Gate verdicts, or default statuses;
- implement event sourcing for Skill handoffs;
- duplicate Superpowers coding mechanics;
- require a live OpenAI API key to accept deterministic decomposition tooling;
- claim static Skill validation proves trigger behavior;
- split release-readiness, semantic-modeling, or defect-management into additional Skills without evidence.

## 17. Acceptance Boundary for 09 v0.1

09 design may proceed to implementation planning only after this written spec is human-approved.

Implementation may later reach P34 only when:

1. all nine distributions validate as standalone Skills;
2. ownership registry proves exactly one primary owner for every P00-P36 stage;
3. central router remains the only ambiguity/cross-domain router;
4. specialist safety preflight blocks downstream work when an earlier layer is untrusted;
5. shared contracts are generated from one canonical source with zero digest drift;
6. generated `skills/*` distributions are reproducible and committed;
7. the composite `skills/aegis` distribution remains supported and behaviorally compatible;
8. the existing 34-case lifecycle corpus has zero critical regression;
9. the new Skill-routing corpus passes all protected trigger/handoff cases;
10. manual dogfood demonstrates at least one direct specialist path, one ambiguous central-router path, one upstream-blocker handoff, and one composite fallback path;
11. Skill Creator validation/package checks pass for every distribution under review;
12. any remaining lack of live provider evidence is reported with its exact independent Gate status rather than hidden.

## 18. Required Next Lifecycle

After human approval of this written spec:

```text
P30 Implementation Planning
-> P31 Task Packaging
-> RED-first routing/ownership/build tests
-> canonical skillset control layer
-> composite compatibility migration
-> specialist generation
-> regression + dogfood
-> P34 Gate Review
-> repository integration
```

Until the written spec is approved, no specialist Skill creation or `skills/aegis` migration is authorized.
