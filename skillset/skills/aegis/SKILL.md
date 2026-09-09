---
name: aegis
description: Central Aegis router for requests whose owning lifecycle stage is unknown or genuinely spans multiple Aegis stage families. Use for "what should this project do next?", "where should we start or resume?", or an explicit handoff from a specialist after it stops. In a multi-skill installation, do not use this entrypoint when a single specialist clearly owns the request. When only this composite Skill is installed, it may act as the fallback.
---

# Aegis

Aegis is a software-development control plane. Route work to the earliest untrusted layer, establish explicit authority and contracts, define evidence before implementation, freeze implementation completion before coding, and require Gate evidence before downstream work treats a result as stable.

## Core loop

Use this invariant lifecycle:

`Problem -> Authority -> Contract -> Evidence -> Plan -> Code -> Gate -> Release -> Feedback -> Problem`

Do not force every project through every stage. Preserve the logic even when stages are merged.

## Start by routing the work

1. Classify the work: greenfield, product research, feature change, architecture change, defect, optimization, interrupted implementation, gate review, or release.
2. Identify available sources: user statements, PRD, design docs, ADRs/RFCs, Notion, repository state, tests, CI, benchmarks, release evidence.
3. Classify each source as `Current Authority`, `Draft/Proposed`, `Superseded/Historical`, `Implementation Reality`, or `Evidence`.
4. Find the **Earliest Untrusted Layer**: the first layer in the chain that cannot safely be treated as current truth.
5. Select a process profile: Lite, Standard, or Full. Standard is the ordinary default; Full requires explicit risk justification. High-assurance work requires additional domain-specific governance beyond Aegis.
6. Route to the minimum safe stage or sequence. Do not begin downstream implementation when an upstream layer is untrusted.

A late finding does not automatically route to implementation. Verification omissions route to P20; task-package omissions route to P31; only implementation-owned frozen-contract failures route to implementation repair. Interrupted work routes to P33 only when the package remains valid.

Read [references/bootstrap-routing.md](references/bootstrap-routing.md) for routing rules and profile selection.

## Project-state bootstrap

When the project contains a `.aegis/` directory, inspect project-control state before ordinary routing:

1. Read `project.json`, `authorities.json`, `gates.json`, `evidence.json`, and `integrations.json`; determine their consistent schema version before applying version-specific rules.
2. Treat `state.json` as a generated cache, never as independent authority.
3. Validate IDs, current-authority uniqueness, dependency/supersession graphs, Gate evidence references, Integration occurrence evidence, and declared Gate validity.
4. Recompute derived validity, Gate actionability, Integration applicability, and version-appropriate Integration Gate conformance; compare them with committed `state.json`.
5. If manifest metadata conflicts with actual Current Authority or repository reality, route to `P21`/`P22`; do not let `.aegis/` silently override authoritative documents or erase a proven repository occurrence.
6. Include active `BLOCKED_*` Gate verdicts and current awaiting repository integrations in derived routing. Preserve completed Gate/Integration occurrence history without reactivating it solely from provenance.
7. Keep Authority status, Gate verdict/validity, Integration occurrence, Gate conformance, current applicability, and current actionability separate. A real merge under a blocked Gate is an occurrence plus nonconforming conformance, not implicit Gate PASS.
8. If only current Gate/Evidence validity is stale or a current Gate is blocked, route from the mapped Gate layer; if an upstream authority dependency is stale or needs review, route from that earlier layer.

Read [references/project-state.md](references/project-state.md) for the version-aware manifest, occurrence/conformance/applicability/actionability split, blocked-Gate propagation, Integration lifecycle, invalidation, and routing contract.

## Stage map

Use these stage IDs consistently:

- Discovery: `P00` Problem Discovery, `P01` Product Research, `P02` Product Requirement, `P03` Capability Traceability.
- Design: `P10` Product Object Model, `P11` Interaction / Behavior, `P12` Semantic Schema, `P13` Operation / Mutation Model, `P14` System Architecture, `P15` Module Design, `P16` Runtime Data Flow, `P17` Platform Contract, `P18` Engineering / Optimization.
- Verification & Governance: `P20` Verification Design, `P21` Authority Review, `P22` Five-Axis Drift Review, `P23` Authority Supersession, `P24` Release Readiness.
- Implementation: `P30` Implementation Planning, `P31` Task Packaging, `P32` Implementation, `P33` Resume Interrupted Work, `P34` Gate Review, `P35` Defect Classification, `P36` Fix / Reverification.

Read [references/stage-contracts.md](references/stage-contracts.md) for required inputs, outputs, and exit criteria. Read only the relevant stage-family reference for detailed execution:

- [references/discovery-design.md](references/discovery-design.md) for `P00-P18`.
- [references/verification-governance.md](references/verification-governance.md) for `P20-P24`.
- [references/implementation.md](references/implementation.md) for `P30-P36`.

## Authority rules

Treat authority as the current effective design basis, not as a pile of documents.

- Never infer that repository code is architecture authority merely because it exists.
- Never silently rewrite an upstream authority to make implementation easier.
- Keep one `Current Authority` per scope.
- Preserve superseded versions as history; link old to new and state why supersession occurred.
- If sources conflict materially, stop downstream work and route to `P21` or `P22`.
- If implementation/review discovers a design or Verification defect, classify it, revise the correct earlier authority, update downstream dependencies, then regenerate the implementation package.

Read [references/verification-governance.md](references/verification-governance.md) for status, drift, defect, supersession, and Gate rules.

## Verification-first and closure-stability rules

Before implementation, ask: **What evidence would make us believe the requirement is satisfied if no implementation existed yet?**

Map important requirements through invariant, failure mode, existing independent coverage, residual proof gap, oracle/reference, fixture/corpus, exact execution method, evidence artifact, blocking/corroborative classification, and Gate criterion.

A blocking evidence artifact must detect a material high-impact failure mode that is not already adequately covered by another independent mechanism. Corroborative evidence may improve confidence but does not automatically block.

`Code Complete != Gate Complete`

`Missing Evidence != Automatically Gate Blocked`

Once P31 authorizes implementation, apply the **Gate Closure Stability Principle**: the blocking completion target is frozen. P34 may block a frozen failure or a genuinely newly discovered high-impact uncovered correctness/safety/security/compatibility/data-integrity/release-critical failure mode, but it must not move the finish line merely to gain more confidence.

Apply the **Anti-Proof-Recursion Rule**: do not require evidence solely to prove another evidence mechanism unless that mechanism itself is a material undetected-failure source, lacks independent validation, and could materially affect the Gate decision.

## Stage contract format

For any stage you execute, keep these eight fields explicit even if the final response is concise:

1. Role
2. Authority
3. Objective
4. Non-goals
5. Required Analysis
6. Required Output
7. Quality / Evidence Gate
8. Handoff

Read [references/output-contracts.md](references/output-contracts.md) for standard result formats and statuses.

## Implementation behavior

When the route reaches implementation:

1. Require an explicit implementation plan (`P30`) when the change has multiple dependent tasks or meaningful architectural risk.
2. At `P31`, freeze an `EXECUTION_CLOSURE_CONTRACT` with required/forbidden changes, required tests/oracles, required vs optional hosted verification, blocking vs corroborative evidence, terminal success, explicit terminal blockers, and `continue_until_terminal_state: true`.
3. At `P32`, execute the complete frozen contract until terminal success or an explicit terminal blocker. Do not redesign upstream authority and do not return merely because an intermediate checkpoint finished.
4. At `P33`, resume valid interrupted work after inspecting current diff/state. If new work exists because P20/P31 omitted obligations, stop the resume loop and route to the earlier owning layer rather than incrementally extending the package.
5. At `P34`, audit Frozen Requirements, Frozen Evidence, and Repository Reality. Late redundant evidence/hardening is non-blocking; a real newly discovered high-impact uncovered failure mode may block with explicit override justification.
6. At `P35`, classify the owning layer before fixing. Do not disguise Verification Design or Task Package defects as implementation incomplete.
7. At `P36`, repair implementation-owned defects and rerun the frozen failing evidence plus relevant regressions.

If Superpowers skills are available, compose with them rather than duplicating their coding mechanics. Read [references/superpowers-integration.md](references/superpowers-integration.md).

## Connector behavior

When project authority lives in connected systems, use the available connector instead of asking the user to paste content unnecessarily.

- Notion: distinguish Current Authority from historical or draft pages before synthesizing or updating.
- GitHub: distinguish repository implementation reality from design authority; inspect code, PRs, tests, and CI as evidence.
- Do not copy project-private content into reusable Aegis references or outputs unless the user explicitly asks.

## Default statuses

Use the smallest applicable status vocabulary:

`READY`, `READY_WITH_FINDINGS`, `BLOCKED_AUTHORITY`, `BLOCKED_MISSING_INPUT`, `BLOCKED_UNRESOLVED_DECISION`, `BLOCKED_EVIDENCE`, `BLOCKED_IMPLEMENTATION`, `BLOCKED_ENVIRONMENT`.

Use the existing global defect vocabulary for durable status compatibility. P35 may additionally express late-finding root-cause labels `VERIFICATION_DESIGN_DEFECT`, `TASK_PACKAGE_DEFECT`, and `NON_BLOCKING_HARDENING` without changing the global enum.

Do not use vague completion language such as "basically done" when a Gate verdict is required.

## Minimum invariant

Aegis may compress stages for small projects, but never delete these four questions:

1. Is the problem correct?
2. Is the authority/contract explicit?
3. What evidence proves the result?
4. Who or what Gate decides whether downstream work may proceed?

## Multi-Skill ownership boundary

In **Multi-Skill Mode**, `aegis` is the final-answer owner only for genuine ambiguity, routing-only results, or an accepted blocked short-circuit. It must not own specialist substantive work when the relevant specialist is known available. A `support_return` from `aegis-project-state` supplies facts and does not transfer substantive ownership to the Router.

In **Composite Compatibility Mode**, `aegis` may perform specialist work only when explicit specialist-unavailability evidence shows that the relevant specialist is unavailable. In that compatibility mode, `aegis` is the final-answer owner for the composite result.

When a specialist discovers an earlier blocker and emits `ownership_handoff` to `aegis`, the blocked short-circuit is terminal unless separate Current Authority explicitly authorizes repair-and-resume.
