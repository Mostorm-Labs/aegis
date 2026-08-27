---
name: aegis-architecture
description: Design the system architecture for a feature or project, including module ownership, runtime data flow, platform contracts, and engineering or performance boundaries. Use for direct architecture-design requests, P14-P18 work, questions about who owns state or capabilities, or how modules depend on each other. If required semantic authority is untrusted, apply the architecture safety preflight and stop before substantive design.
---

# Aegis Architecture

Own `P14` System Architecture, `P15` Module Design, `P16` Runtime Data Flow, `P17` Platform Contract, and `P18` Engineering / Optimization.

## Architecture sequence

Assign ownership first; then freeze module interfaces/invariants; trace temporal happy/failure/recovery flows; separate common semantics from platform realization; and make optimization decisions from measurable cost models and evidence plans.

**Earlier untrusted layer:** if product object/behavior/schema/operation semantics are not trustworthy, stop and hand back to `aegis`; architecture must not invent semantic truth.

Read [references/architecture.md](references/architecture.md) and shared Authority/stage contracts.
