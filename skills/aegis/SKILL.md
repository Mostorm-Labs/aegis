---
name: aegis
description: AI-native, evidence-gated software development control plane for routing work from problem discovery through product requirements, semantic and architecture design, verification, implementation planning, gate review, release readiness, and feedback. Use when starting or resuming a software project, designing or changing a feature or architecture, reviewing authority or implementation drift, preparing work for coding agents, classifying defects, defining evidence, auditing a gate, or deciding where in the development lifecycle work should begin. Aegis selects the earliest untrusted layer, prevents silent authority changes, and requires evidence before downstream stages treat work as complete.
---

# Aegis

Aegis is a software-development control plane. Route work to the earliest untrusted layer, establish explicit authority and contracts, define evidence before implementation, and require gate evidence before downstream work treats a result as stable.

## Core loop

Use this invariant lifecycle:

`Problem -> Authority -> Contract -> Evidence -> Plan -> Code -> Gate -> Release -> Feedback -> Problem`

Do not force every project through every stage. Preserve the logic even when stages are merged.

## Start by routing the work

1. Classify the work: greenfield, product research, feature change, architecture change, defect, optimization, interrupted implementation, gate review, or release.
2. Identify available sources: user statements, PRD, design docs, ADRs/RFCs, Notion, repository state, tests, CI, benchmarks, release evidence.
3. Classify each source as `Current Authority`, `Draft/Proposed`, `Superseded/Historical`, `Implementation Reality`, or `Evidence`.
4. Find the **Earliest Untrusted Layer**: the first layer in the chain that cannot safely be treated as current truth.
5. Select a process profile: Lite, Standard, or Full. High-assurance work requires additional domain-specific governance beyond Aegis.
6. Route to the minimum safe stage or sequence. Do not begin downstream implementation when an upstream layer is untrusted.

Read [references/bootstrap-routing.md](references/bootstrap-routing.md) for routing rules and profile selection.

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
- If implementation discovers a design defect, classify it, revise the correct upstream authority, update downstream dependencies, then regenerate the implementation package.

Read [references/verification-governance.md](references/verification-governance.md) for status, drift, defect, supersession, and gate rules.

## Verification-first rule

Before implementation, ask: **What evidence would make us believe the requirement is satisfied if no implementation existed yet?**

Map important requirements to an invariant, oracle/reference, corpus/fixture, metric, threshold, evidence artifact, and gate. Prefer executable evidence over narrative claims where practical.

`Code Complete != Gate Complete`

Downstream work may treat a result as stable only after the required gate evidence passes.

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
2. Package each task with authority references, scope, non-goals, affected modules/files, required tests/oracles, evidence, dependencies, and exit criteria (`P31`).
3. During implementation (`P32`), do not redesign upstream authority unless the task explicitly authorizes an architecture change.
4. For interrupted work, inspect current diff/state first and preserve valid work (`P33`).
5. Audit completion against authority and evidence, not agent claims (`P34`).
6. If blocked or failing, classify the defect at the correct layer (`P35`) before fixing (`P36`).

If Superpowers skills are available, compose with them rather than duplicating their coding mechanics. Read [references/superpowers-integration.md](references/superpowers-integration.md).

## Connector behavior

When project authority lives in connected systems, use the available connector instead of asking the user to paste content unnecessarily.

- Notion: distinguish Current Authority from historical or draft pages before synthesizing or updating.
- GitHub: distinguish repository implementation reality from design authority; inspect code, PRs, tests, and CI as evidence.
- Do not copy project-private content into reusable Aegis references or outputs unless the user explicitly asks.

## Default statuses

Use the smallest applicable status vocabulary:

`READY`, `READY_WITH_FINDINGS`, `BLOCKED_AUTHORITY`, `BLOCKED_MISSING_INPUT`, `BLOCKED_UNRESOLVED_DECISION`, `BLOCKED_EVIDENCE`, `BLOCKED_IMPLEMENTATION`, `BLOCKED_ENVIRONMENT`.

For defect classification use: `IMPLEMENTATION_DEFECT`, `SPEC_DEFECT`, `AUTHORITY_CONFLICT`, `MISSING_CONTRACT`, `TEST_DEFECT`, `EVIDENCE_GAP`, `ENVIRONMENT_DEFECT`, `DEPENDENCY_BLOCKER`, `UNRESOLVED_DECISION`.

Do not use vague completion language such as "basically done" when a gate verdict is required.

## Minimum invariant

Aegis may compress stages for small projects, but never delete these four questions:

1. Is the problem correct?
2. Is the authority/contract explicit?
3. What evidence proves the result?
4. Who or what gate decides whether downstream work may proceed?
