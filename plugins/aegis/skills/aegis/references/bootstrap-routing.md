# Bootstrap Routing

## Purpose

Route a new or existing software effort to the earliest stage that cannot safely be trusted. Bootstrap output is navigation, not product or architecture authority.

## Project Profile Card

Capture:

- Project / change
- Work type
- Current maturity
- Recommended profile
- Earliest untrusted layer
- Existing current authority
- Critical missing authority
- Complexity / risk signals
- Recommended route
- Safe-to-skip stages
- Escalation conditions
- First action

## Work types

- Greenfield: idea or new product with no trusted problem/requirement authority.
- Existing Product: mature system where current authority needs to be identified before change.
- Feature Change: bounded product capability change in an existing system.
- Architecture Change: ownership, semantic, contract, lifecycle, dependency, or compatibility changes.
- Defect: observed behavior violates an expected contract or evidence gate.
- Optimization: correctness is assumed or already proven; performance/resource behavior is the target.
- Interrupted Work: implementation exists but the execution state is incomplete or uncertain.
- Release: implementation is believed complete and needs release-readiness evidence.

## Maturity levels

`Idea -> Problem-Validated -> Requirement-Defined -> Authority-Defined -> Implementation -> Gate -> Release`

## Earliest Untrusted Layer

Inspect in this order:

`Problem -> Requirement -> Object -> Behavior -> Schema -> Operation -> Architecture -> Module -> Flow -> Platform -> Engineering -> Verification -> Authority Reconciliation -> Implementation -> Release`

Start at the first layer that is missing, contradictory, stale, unsupported, or explicitly under change.

## Default routes

- Only a vague idea -> `P00`.
- Problem validated, requirements not frozen -> `P02`; use `P01` when research evidence is missing.
- Mature product adding a feature -> `P21` first if authority is not already reconciled, then affected `P10-P18` stages.
- Existing design documents conflict -> `P21 -> P22`; use `P23` after an accepted replacement authority exists.
- Authority complete, preparing implementation -> `P30 -> P31`.
- Interrupted coding task -> `P33`.
- Clear bug -> `P35 -> P36 -> P34`.
- Performance problem with correctness already proven -> `P18 -> P20`, then implementation planning.
- Release candidate -> `P24`.
- Breaking semantic or architecture change -> `P21 -> affected P10-P18 -> P20 -> P23 -> P30`.

## Profiles

### Lite

Use for prototypes, small internal tools, simple CRUD, low-cost reversible changes. Merge adjacent stages when useful, but retain Problem, Contract, Evidence, and Gate logic.

### Standard

Use for customer-facing SaaS, mobile/desktop apps, moderate integrations, migrations, or systems with multiple teams/components. Keep explicit requirements, architecture boundaries, verification, and release readiness.

### Full

Use for cross-platform runtimes, protocols, distributed/offline systems, multi-language stacks, concurrency, long-lived compatibility, recovery, high performance, or infrastructure expected to evolve for years. Use explicit semantic, platform, verification, and authority governance.

### High-Assurance warning

For medical, safety-critical, financial-core, regulated, or severe-security-risk systems, Aegis is not sufficient by itself. Add the relevant compliance, hazard, threat, independent verification, and audit frameworks.

## Escalation signals

Upgrade process depth when any of these appears:

- cross-platform or cross-language behavior must be equivalent;
- wire/storage compatibility or migration matters;
- concurrency, ordering, conflict, or distributed recovery semantics appear;
- performance SLOs or resource budgets become product-critical;
- irreversible data loss or corruption is possible;
- authority changes invalidate multiple downstream tasks;
- multiple implementations must conform to the same semantic contract.
