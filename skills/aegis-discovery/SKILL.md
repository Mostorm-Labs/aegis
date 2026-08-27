---
name: aegis-discovery
description: Run Aegis problem discovery, product research, product requirements, and capability traceability. Use when starting a software effort, validating whether a proposed solution addresses the real problem, researching alternatives/evidence, turning a validated problem into requirements, or tracing requirements through capabilities toward implementation and verification.
---

# Aegis Discovery

Own `P00` Problem Discovery, `P01` Product Research, `P02` Product Requirement, and `P03` Capability Traceability.

## Discovery sequence

Separate symptom/pain/root constraint from candidate solution; use research to challenge rather than merely confirm; translate validated problems into JTBD/scenarios/FR/NFR/acceptance criteria; then trace important requirements toward capability, semantics, ownership, platform, and verification.

**Earlier untrusted layer:** if observed reality or problem evidence is insufficient, stay at the earliest discovery stage and hand back to `aegis` when cross-domain routing is needed; do not jump into design.

Read [references/discovery.md](references/discovery.md) and shared core/Authority contracts.

## Composition boundary

Once substantive execution begins in this Skill's owned stage family, this Skill is the unique Primary Owner for that substantive result. It may consume Project State support from `aegis-project-state`; Project State support does not transfer ownership.

Direct Primary-to-Primary substantive chaining is forbidden. After completing its owned stage, this Skill may suggest an unambiguous next Skill, but it must not automatically execute substantive work owned by that next Primary.

If an earlier untrusted layer blocks safe execution, emit an `ownership_handoff` to `aegis` and stop substantive execution. Do not repair or silently redefine the earlier layer inside this specialist.
