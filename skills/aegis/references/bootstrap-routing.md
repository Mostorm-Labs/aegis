# Bootstrap Routing

## Purpose

Route a new or existing software effort to the earliest stage that cannot safely be trusted. Bootstrap output is navigation, not product or architecture authority.

## Project Profile Card

Capture:

- Project / change
- Work type
- Current maturity
- Recommended profile
- Profile justification when Full is selected
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

A late review finding does not automatically make implementation the earliest untrusted layer. If the root cause is an omitted Verification Design obligation, return to P20. If the package omitted a frozen execution requirement, return to P31. Use P33 only for interrupted valid execution, not for repeatedly expanding the package after P31.

## Default routes

- Only a vague idea -> `P00`.
- Problem validated, requirements not frozen -> `P02`; use `P01` when research evidence is missing.
- Mature product adding a feature -> `P21` first if authority is not already reconciled, then affected `P10-P18` stages.
- Existing design documents conflict -> `P21 -> P22`; use `P23` after an accepted replacement authority exists.
- Authority complete, preparing implementation -> `P20 -> P30 -> P31` when Verification is not already current; otherwise `P30 -> P31`.
- Interrupted coding task with a valid frozen package -> `P33`.
- Clear implementation bug under a trusted frozen contract -> `P35 -> P36 -> P34`.
- Late P34 package/verification omission -> `P35 -> P31` or `P35 -> P20`, then regenerate downstream execution authority.
- Performance problem with correctness already proven -> `P18 -> P20`, then implementation planning.
- Release candidate -> `P24`.
- Breaking semantic or architecture change -> `P21 -> affected P10-P18 -> P20 -> P23 -> P30`.

## Profiles

### Lite

Use for small/local changes, prototypes, simple internal tools, low blast radius, easy rollback, and strong existing tests. Merge adjacent stages when useful, but retain Problem, Contract, Evidence, and Gate logic. Do not import Full rituals merely because tooling exists.

### Standard

Standard is the default for most ordinary feature, bugfix, and module work. Use it for typical customer-facing applications, bounded integrations, reversible migrations, and ordinary multi-module changes unless specific risk signals justify Full.

Keep explicit requirements, architecture boundaries, Verification Design, an Execution Closure Contract, and Gate review. Evidence should be proportionate: an exact PR source SHA, required local tests, hosted CI, artifact identity where applicable, and normal reviewer-accessible logs are usually sufficient when they credibly cover the frozen high-impact failure modes.

A separate evidence-only descendant, clean-room reproduction, formal provenance graph, negative evidence-generator suite, or proof-of-proof chain is not mandatory under Standard. Require one only when the frozen Verification Contract identifies a concrete uncovered high-impact failure mode that the additional mechanism uniquely detects.

### Full

Select Full only with an explicit profile justification tied to risk. Typical triggers include protocol/schema release, security critical behavior, data-integrity critical behavior, cross-language conformance release, formal SDK release, irreversible migration impact, long-lived compatibility boundaries, or regulated/high-assurance environments.

Full may require exact source freeze, clean checkout, exact hosted provider identity, materialized evidence, provenance, independent oracle/reference evidence, source/evidence separation, and stronger reproducibility controls. These controls remain conditional on the Full Verification Contract; Full is stricter, not an excuse for proof recursion.

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

Do not escalate merely because more evidence could increase confidence. Escalate when risk or an uncovered failure mode justifies the additional assurance cost.
