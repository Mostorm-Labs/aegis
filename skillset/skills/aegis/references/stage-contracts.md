# Stage Contracts

## Discovery

| ID | Stage | Required output | Exit criterion |
| --- | --- | --- | --- |
| P00 | Problem Discovery | Problem Statement, affected user/scenario, evidence, root constraint, success criteria, non-goals, unknowns | Problem is solution-neutral enough to test and can be falsified |
| P01 | Product Research | Findings, alternatives, assumptions, evidence/source notes, open questions | Important claims are sourced or explicitly labeled assumptions |
| P02 | Product Requirement | JTBD, scenarios, FR/NFR, priority, acceptance criteria, out of scope | Each important requirement traces to user/system value |
| P03 | Capability Traceability | Requirement -> capability -> object -> behavior -> operation -> module -> platform -> verification | No important orphan requirement or unjustified module |

## Design

| ID | Stage | Required output | Exit criterion |
| --- | --- | --- | --- |
| P10 | Product Object Model | Entity/value/aggregate/external/session/derived taxonomy | Durable truth is separated from transient and derived state |
| P11 | Interaction / Behavior | session lifecycle, state transitions, commit/cancel semantics | User behavior resolves into stable mutations or explicit non-mutations |
| P12 | Semantic Schema | canonical state, IDs, versions, validation, compatibility | UI/cache/network/runtime-derived state is not confused with canonical truth |
| P13 | Operation / Mutation | mutation vocabulary, payload, atomicity, ordering, undo/replay | canonical mutation units are explicit and replayable where required |
| P14 | System Architecture | subsystem ownership, dependencies, boundaries, lifecycle, failure domains | every capability/state has an accountable owner |
| P15 | Module Design | module internals, stable interfaces, ownership, invariants | module can be implemented without reopening system architecture |
| P16 | Runtime Data Flow | end-to-end happy/failure paths, state transitions, backpressure/error paths | major flows have no unexplained ownership/state gaps |
| P17 | Platform Contract | ABI/bridge/thread/input/surface/lifecycle/capability matrix as applicable | physical platform differences do not silently redefine common semantics |
| P18 | Engineering / Optimization | performance model, budgets, scheduler/caching/diagnostics choices | optimization decisions have measurable evidence plans |

## Verification & Governance

| ID | Stage | Required output | Exit criterion |
| --- | --- | --- | --- |
| P20 | Verification Design | requirement/invariant/failure-mode mapping, independent coverage, oracle/reference, fixture/corpus, exact execution, blocking vs corroborative evidence, Gate criterion | important requirements have credible proof; blocking evidence has unique high-impact detection justification |
| P21 | Authority Review | source-of-truth map, conflicts, missing contracts, unresolved decisions | READY or explicitly BLOCKED; no silent conflicts |
| P22 | Five-Axis Drift Review | product, semantic, architecture, implementation, verification drift findings | each drift is classified and owned |
| P23 | Authority Supersession | old/new relation, reason, change summary, downstream impact | one Current Authority per scope; old version clearly superseded |
| P24 | Release Readiness | RC evidence proportionate to active profile, migration/recovery/rollback/observability status as applicable | release gate passes or exact risk-relevant blockers are named |

## Implementation

| ID | Stage | Required output | Exit criterion |
| --- | --- | --- | --- |
| P30 | Implementation Planning | dependency graph, vertical slices, gate order | each slice has independent evidence and exit criteria |
| P31 | Task Packaging | authority refs, scope/non-goals, required/forbidden changes, tests/oracles, blocking/corroborative evidence, terminal success/blockers in `EXECUTION_CLOSURE_CONTRACT` | blocking completion target is frozen; coding agent need not redesign system or infer finish criteria |
| P32 | Implementation | code/change, frozen required tests/evidence, durable result identities, terminal blocker if any | complete frozen closure contract reaches terminal success or explicit terminal blocker |
| P33 | Resume | current state/diff, completed work, pending work, safe continuation plus root-cause check for any newly introduced work | valid work is preserved; resume does not expand package; P20/P31 omissions route earlier |
| P34 | Gate Review | Frozen Requirement Audit, Frozen Evidence Audit, Repository Reality Audit, classified late findings | PASS/PASS_WITH_FINDINGS or blocker justified by frozen failure or real newly discovered uncovered high-impact defect |
| P35 | Defect Classification | defect type/layer/owner, late-finding source, affected authority/gate | implementation vs spec vs Verification Design vs Task Package vs non-blocking hardening is distinguished |
| P36 | Fix / Reverification | implementation-owned fix plus rerun frozen evidence and regression closure | original implementation defect and introduced regressions are closed; upstream defects have regenerated authority/package |
