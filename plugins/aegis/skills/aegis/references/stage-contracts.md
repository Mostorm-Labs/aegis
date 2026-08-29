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
| P20 | Verification Design | invariant, oracle/reference, corpus/fixture, metric, threshold, evidence artifact, gate mapping | important requirements have credible proof methods |
| P21 | Authority Review | source-of-truth map, conflicts, missing contracts, unresolved decisions | READY or explicitly BLOCKED; no silent conflicts |
| P22 | Five-Axis Drift Review | product, semantic, architecture, implementation, verification drift findings | each drift is classified and owned |
| P23 | Authority Supersession | old/new relation, reason, change summary, downstream impact | one Current Authority per scope; old version clearly superseded |
| P24 | Release Readiness | RC evidence, migration/recovery/rollback/observability status as applicable | release gate passes or exact blockers are named |

## Implementation

| ID | Stage | Required output | Exit criterion |
| --- | --- | --- | --- |
| P30 | Implementation Planning | dependency graph, vertical slices, gate order | each slice has independent evidence and exit criteria |
| P31 | Task Packaging | authority refs, scope, non-goals, modules/files, tests/oracles, evidence, dependencies | coding agent need not redesign the system to execute |
| P32 | Implementation | code/change, tests, evidence, blocker classification | task evidence is complete enough for gate review |
| P33 | Resume | current state/diff, completed work, pending work, safe continuation | valid work is preserved and authority context restored |
| P34 | Gate Review | authority/contract/evidence conformance verdict | PASS/PASS_WITH_FINDINGS or precise blocker |
| P35 | Defect Classification | defect type, layer, owner, affected authority/gate | fix is routed to the correct layer |
| P36 | Fix / Reverification | fix plus rerun evidence and regression closure | original defect and introduced regressions are closed |
