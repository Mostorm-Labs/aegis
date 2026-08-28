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

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
