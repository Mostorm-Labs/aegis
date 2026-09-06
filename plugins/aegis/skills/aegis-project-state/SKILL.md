---
name: aegis-project-state
description: Inspect, validate, recompute, and compare Aegis .aegis project-control manifests and Project State v0.6, while preserving v0.3-v0.5 compatibility.
---

# Aegis Project State

Own deterministic Project State inspection, validation, recomputation, and state-drift diagnosis. Do not claim lifecycle-stage ownership.

## Safety preflight

If deterministic project-state tooling is present, prefer it over conversational reimplementation. Treat `state.json` as generated cache, never Authority. Determine the manifest schema version before applying Integration rules: v0.4 separates Integration occurrence from Gate conformance; v0.3 retains its historical stricter integrated-Gate rule.

Repository occurrence and Gate acceptance are different facts. If repository evidence proves an Integration happened under a blocked Gate, preserve the occurrence, preserve the blocked Gate, and classify v0.4 conformance as `nonconforming`; never manufacture PASS evidence from the merge itself.

If authored manifests conflict with Current Authority or repository evidence, return to the central `aegis` router for reconciliation.

**Earlier untrusted layer:** when Project State reveals an earlier Authority or Gate blocker, report it and hand back to `aegis`; do not repair unrelated lifecycle stages here.

Read [references/project-state.md](references/project-state.md) for the version-aware v0.6 contract and [references/shared/authority-contract.md](references/shared/authority-contract.md) for global Authority semantics.

In v0.6, `gate_decision_binding` is occurrence-time immutable. `missing`, `failed`,
or `unresolved` evidence never means `Absent`; a later PASS cannot rewrite a
historical binding. O1-O6 are semantic vocabulary, not runtime APIs.

This Skill preserves v0.3/v0.4/v0.5 compatibility and v0.5 Gate Contract /
Gate Decision lineage. v0.6 distinguishes `Bound(PASS)`, `Bound(BLOCKED)`, and
`Absent`; only explicit accepted absence evidence permits `Absent`. Read,
lookup, stale, missing, failed, and unresolved states remain unknown/error.
Later PASS decisions append history and never rewrite historical bindings.

The contract is version-aware: v0.3 uses direct Gate references; v0.4 separates
immutable repository occurrence from conformance; v0.5 introduces immutable
Gate Decision lineage via `gate_decision_id`; v0.6 uses the `bound|absent`
binding sum type, status legality matrix, O6 append-only corroboration, and
deterministic v0.5→v0.6 migration with zero inferred absence. O1–O6 are semantic
state vocabulary only, never runtime APIs.

## Composition boundary

**Direct Project State task:** when the user's task is Project State inspection, validation, recomputation, persistence, or diagnosis itself, `aegis-project-state` is the final-answer owner.

**Support mode:** when another lifecycle stage family owns the user request, Project State support provides facts only through `support_return`; it gives no stage verdict and does not take final-answer ownership from the Primary Owner.

Project State support may conclusively establish an earlier Authority or Gate blocker. In that case, return the supporting facts and route the terminal blocked result to `aegis`; do not repair the earlier layer or own the downstream stage.
