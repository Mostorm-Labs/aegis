# Aegis Execution Surface Contract v0.1

Status: **Proposed Additive Authority v0.1 — human-approved; deterministic implementation and hosted CI PASS; integration remains stacked behind PR #9.**

This contract adds execution-surface routing to Aegis without changing lifecycle-stage ownership. It formalizes the control-plane / execution-plane split validated in real Axiom development: reasoning-heavy planning and review stay on a conversational control surface, while repository-heavy implementation and reverification move to a coding execution surface.

## 1. Problem

Aegis already routes work to the correct lifecycle stage and Primary Owner, but stage ownership does not answer a second question:

> Where should the authorized work execute?

Without an explicit surface contract, a coding agent may spend large context/token budget rediscovering Authority and architecture that the control plane already resolved, or a conversational agent may inefficiently perform repository-heavy implementation work.

## 2. Core Principle

`Stage Ownership != Execution Surface`

Stage ownership answers **who owns the substantive lifecycle result**. Execution surface answers **where the authorized work should be performed**.

A surface transfer never changes Current Authority, Primary Owner, Gate ownership, or lifecycle stage by itself.

## 3. Surface Vocabulary

Aegis v0.1 defines four semantic surfaces:

- `CONTROL_REASONING` — long-context reasoning, Authority synthesis, architecture, verification design, planning, task packaging, governance, and review.
- `CODE_EXECUTION` — repository inspection, code edits, builds, tests, CI interaction, benchmarks, diffs, and implementation evidence collection.
- `CONTROL_REVIEW` — Gate review, defect classification, Authority repair routing, and release/governance judgment.
- `CODE_REVERIFY` — implementation fixes, regression execution, and repository-level reverification after an accepted repair decision.

The default OpenAI profile maps these semantic surfaces as follows:

- `CONTROL_REASONING` -> ChatGPT
- `CODE_EXECUTION` -> Codex
- `CONTROL_REVIEW` -> ChatGPT
- `CODE_REVERIFY` -> Codex

Provider/product names are profile metadata, not semantic Authority. Other environments may map the semantic surfaces to equivalent tools.

## 4. Default P30-P36 Mapping

The default implementation-family surface mapping is:

```text
P30 Implementation Planning      -> CONTROL_REASONING
P31 Task Packaging               -> CONTROL_REASONING
P32 Implementation               -> CODE_EXECUTION
P33 Resume Interrupted Work      -> CODE_EXECUTION
P34 Gate Review                  -> CONTROL_REVIEW
P35 Defect Classification        -> CONTROL_REVIEW
P36 Fix / Reverification         -> CODE_REVERIFY
```

The stage Primary Owner remains unchanged. In the current multi-skill architecture, `aegis-implementation` still owns P30-P33 and `aegis-gate-review` still owns P34-P36.

## 5. Surface Handoff

A surface handoff is ephemeral execution metadata. It is distinct from both `support_return` and `ownership_handoff`.

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: repository_heavy_execution
package_ref: <task-package-ref>
return_surface: CONTROL_REVIEW
```

Semantics:

- `surface_handoff` changes execution location only;
- `stage_owner` remains the same unless a separate valid ownership handoff occurs;
- `package_ref` must identify the approved P31 task package or equivalent execution contract;
- the receiving surface must not invent upstream Authority to fill omissions;
- blocked execution returns the exact blocker/evidence to the owning Aegis lifecycle flow.

`Surface Handoff != Ownership Handoff`.

## 6. Task-Package Compression Rule

Before handing P32 work to `CODE_EXECUTION`, P31 should compress already-resolved reasoning into an executable task package containing at minimum:

- Current Authority references;
- task purpose and scope;
- affected modules/files when known;
- required changes;
- explicit non-goals;
- tests/oracles and evidence obligations;
- dependencies;
- exit criteria;
- blocked-return behavior.

Invariant:

> Do not spend execution-context tokens rediscovering decisions that the control plane can resolve once and encode into an authoritative task package.

This is a context-efficiency rule, not permission to omit required repository inspection. The executor must still inspect current repository state and detect drift before editing.

## 7. Routing Rules

Aegis should prefer `CONTROL_REASONING` when the dominant work is:

- problem/requirement reasoning;
- Authority classification or synthesis;
- semantic/schema/architecture design;
- verification design;
- implementation planning/task packaging;
- Gate judgment or defect classification.

Aegis should prefer `CODE_EXECUTION` when the dominant work is:

- repository exploration needed for implementation;
- code modification;
- build/test/CI execution;
- benchmark/evidence collection;
- branch/diff/worktree operations.

Aegis should prefer `CODE_REVERIFY` after P35 has classified a repair as implementation-owned and the fix contract is explicit.

If a task legitimately spans both classes, Aegis splits it at the nearest stable contract boundary instead of forcing one surface to perform both jobs.

## 8. Safety Boundary

The coding surface must fail closed when:

- Current Authority is missing or contradictory;
- the task package leaves a semantic decision unresolved;
- implementation requires changing upstream architecture outside authorized scope;
- required evidence cannot be produced in the current environment.

The coding surface returns a blocker; it does not silently expand scope or reinterpret Authority.

## 9. Interaction with Multi-Skill Composition

Execution-surface routing is orthogonal to Skill composition:

```text
Skill / Primary Owner graph
        x
Execution Surface graph
```

A support edge does not imply a surface transfer. An ownership handoff does not imply a surface transfer. A surface handoff does not imply either support or ownership transfer.

The existing prohibition on direct Primary-to-Primary substantive chaining remains unchanged.

## 10. Machine-Readable Contract

`skillset/ownership.json` owns the machine-readable surface metadata because it already binds lifecycle stages to Primary Owners. The contract must expose:

- the semantic surface vocabulary;
- default executor profile mapping;
- `execution_surface_by_stage` for P30-P36;
- explicit declaration that surface handoff does not transfer ownership.

`tools/aegis_skillset/model.py` must parse and validate this metadata, and tests must reject missing/unknown mappings.

## 11. Skill Instruction Boundary

Shared `handoff-contract.md` defines `surface_handoff` semantics once.

`aegis-implementation` instructions must:

- keep P30/P31 reasoning and task packaging on the control surface by default;
- hand P32/P33 repository-heavy execution to the code surface when available;
- include the approved task package in the handoff;
- preserve Primary Owner semantics.

`aegis-gate-review` continues to own P34-P36 lifecycle semantics, but P36 repository repair/reverification may execute on `CODE_REVERIFY` after classification.

The central `aegis` router may recommend the target execution surface but must not reinterpret surface transfer as stage ownership.

## 12. Acceptance

The implementation is accepted when deterministic tests prove:

1. every P30-P36 stage has exactly one valid semantic execution surface;
2. all referenced surfaces exist in the declared vocabulary;
3. the OpenAI default profile maps control surfaces to ChatGPT and code surfaces to Codex;
4. P30/P31 map to `CONTROL_REASONING`;
5. P32/P33 map to `CODE_EXECUTION`;
6. P34/P35 map to `CONTROL_REVIEW`;
7. P36 maps to `CODE_REVERIFY`;
8. shared handoff instructions explicitly distinguish `surface_handoff` from support and ownership handoff;
9. generated/distributed Skill instructions preserve the same boundary;
10. existing v0.2 composition and ownership tests remain green.

## 13. Non-Goals

v0.1 does not:

- change P-stage ownership;
- add a new lifecycle stage;
- make token count a Gate metric;
- require ChatGPT or Codex as the only possible products;
- automatically launch an external coding agent;
- permit autonomous multi-stage substantive chaining;
- change Project State Authority/Gate/Evidence semantics.

## 14. Verification Evidence

Deterministic implementation evidence on stacked PR #10:

- focused metadata RED observed before implementation; final focused metadata suite: 13/13 PASS;
- focused surface-handoff/instruction RED observed before canonical contract changes; final focused suite: 3/3 PASS;
- GitHub Actions `Aegis Skillset Integrity` run `33139045503`, job `98745523977`: PASS, including ownership validation, generated-distribution drift check, routing/handoff validation, installed-platform state, standalone Skill validation, skillset tests, Project State regressions, corpus validation, and evaluation regressions;
- GitHub Actions `Aegis Project State Integrity` run `33139045493`: PASS for both `self-host` and `validate-tooling` jobs.

These results satisfy the deterministic acceptance criteria of this contract. They do not supersede or bypass the unresolved installed-platform/P34 authority state of PR #9, which remains the base dependency for this stacked change.
