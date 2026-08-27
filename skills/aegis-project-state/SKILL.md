---
name: aegis-project-state
description: Inspect, validate, recompute, and reason about Aegis .aegis project-control manifests and Project State v0.3. Use when a user asks to read, validate, repair, persist, compare, or resume from .aegis state, Authority/Gate/Evidence/Integration records, state drift, blocked Gate propagation, or historical integration applicability.
---

# Aegis Project State

Own deterministic Project State inspection, validation, recomputation, and state-drift diagnosis. Do not claim lifecycle-stage ownership.

## Safety preflight

If deterministic project-state tooling is present, prefer it over conversational reimplementation. Treat `state.json` as generated cache, never Authority. If authored manifests conflict with Current Authority or repository evidence, return to the central `aegis` router for reconciliation.

**Earlier untrusted layer:** when Project State reveals an earlier Authority or Gate blocker, report it and hand back to `aegis`; do not repair unrelated lifecycle stages here.

Read [references/project-state.md](references/project-state.md) for the v0.3 contract and [references/shared/authority-contract.md](references/shared/authority-contract.md) for global Authority semantics.
