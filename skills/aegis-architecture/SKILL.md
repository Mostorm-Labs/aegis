---
name: aegis-architecture
description: Design Aegis system and module architecture, runtime data flow, platform contracts, and engineering/optimization boundaries. Use when the user asks who owns state or capabilities, how modules depend on each other, how runtime flows execute, how platform bridges differ without changing semantics, or how to define performance/resource architecture.
---

# Aegis Architecture

Own `P14` System Architecture, `P15` Module Design, `P16` Runtime Data Flow, `P17` Platform Contract, and `P18` Engineering / Optimization.

## Architecture sequence

Assign ownership first; then freeze module interfaces/invariants; trace temporal happy/failure/recovery flows; separate common semantics from platform realization; and make optimization decisions from measurable cost models and evidence plans.

**Earlier untrusted layer:** if product object/behavior/schema/operation semantics are not trustworthy, stop and hand back to `aegis`; architecture must not invent semantic truth.

Read [references/architecture.md](references/architecture.md) and shared Authority/stage contracts.
