---
name: aegis-project-state
description: Inspect, validate, recompute, and compare Aegis .aegis project-control manifests and Project State v0.4, while preserving v0.3 compatibility. Use when the user explicitly asks to read, validate, repair, persist, or diagnose .aegis manifests, state.json drift, Integration occurrence versus Gate conformance, current versus historical applicability, or deterministic project-state recomputation.
---

# Aegis Project State

Own deterministic Project State inspection, validation, recomputation, and state-drift diagnosis. Do not claim lifecycle-stage ownership.

## Safety preflight

If deterministic project-state tooling is present, prefer it over conversational reimplementation. Treat `state.json` as generated cache, never Authority. Determine the manifest schema version before applying Integration rules: v0.4 separates Integration occurrence from Gate conformance; v0.3 retains its historical stricter integrated-Gate rule.

Repository occurrence and Gate acceptance are different facts. If repository evidence proves an Integration happened under a blocked Gate, preserve the occurrence, preserve the blocked Gate, and classify v0.4 conformance as `nonconforming`; never manufacture PASS evidence from the merge itself.

If authored manifests conflict with Current Authority or repository evidence, return to the central `aegis` router for reconciliation.

**Earlier untrusted layer:** when Project State reveals an earlier Authority or Gate blocker, report it and hand back to `aegis`; do not repair unrelated lifecycle stages here.

Read [references/project-state.md](references/project-state.md) for the version-aware v0.4/v0.3 contract and [references/shared/authority-contract.md](references/shared/authority-contract.md) for global Authority semantics.

## Composition boundary

**Direct Project State task:** when the user's task is Project State inspection, validation, recomputation, persistence, or diagnosis itself, `aegis-project-state` is the final-answer owner.

**Support mode:** when another lifecycle stage family owns the user request, Project State support provides facts only through `support_return`; it gives no stage verdict and does not take final-answer ownership from the Primary Owner.

Project State support may conclusively establish an earlier Authority or Gate blocker. In that case, return the supporting facts and route the terminal blocked result to `aegis`; do not repair the earlier layer or own the downstream stage.