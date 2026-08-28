# Aegis Execution Surface Contract v0.1

Status: **Proposed Additive Authority v0.1 — human-approved candidate on PR #10.**

This contract adds execution-surface routing to Aegis without changing lifecycle-stage ownership. It formalizes the control-plane / execution-plane split validated in real development: reasoning-heavy planning and review stay on a conversational control surface, while repository-heavy implementation and reverification move to a coding execution surface.

## 1. Problem

Aegis routes work to the correct lifecycle stage and Primary Owner, but stage ownership does not answer where authorized work should execute. Without an explicit surface contract, a coding agent may spend context rediscovering Authority already resolved by the control plane, while a conversational agent may inefficiently perform repository-heavy implementation work.

The contract must also preserve independent review. An executor result that exists only in a local worktree or transcript cannot be treated as Gate evidence merely because the executor reports success.

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

```text
P30 Implementation Planning      -> CONTROL_REASONING
P31 Task Packaging               -> CONTROL_REASONING
P32 Implementation               -> CODE_EXECUTION
P33 Resume Interrupted Work      -> CODE_EXECUTION
P34 Gate Review                  -> CONTROL_REVIEW
P35 Defect Classification        -> CONTROL_REVIEW
P36 Fix / Reverification         -> CODE_REVERIFY
```

The stage Primary Owner remains unchanged. `aegis-implementation` owns P30-P33 and `aegis-gate-review` owns P34-P36.

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
- `package_ref` identifies the approved P31 task package or equivalent execution contract;
- the receiving surface must not invent upstream Authority to fill omissions;
- blocked execution returns the exact blocker/evidence to the owning Aegis lifecycle flow.

`Surface Handoff != Ownership Handoff`.

### Evidence return boundary

Before an execution surface returns a result to `CONTROL_REVIEW`, the exact result must be materialized into a **reviewer-accessible durable evidence boundary**.

For repository execution, this normally means the exact result commit/ref is available on a remote branch or pull request that the reviewer can independently resolve. Other execution environments may use an equivalent durable artifact or immutable ref.

The executor return must carry:

```yaml
result_revision: <exact-result-revision>
materialized_ref: <reviewer-accessible-durable-ref>
return_surface: CONTROL_REVIEW
```

A local-only commit SHA, worktree path/state, test transcript, or executor message is context only and cannot by itself satisfy P34 corroboration. If the executor cannot produce a reviewer-accessible `materialized_ref`, it must return `BLOCKED_EVIDENCE` with the exact materialization blocker instead of claiming review readiness.

P34 independently resolves `materialized_ref` before relying on executor claims.

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
- blocked-return behavior;
- the reviewer-accessible evidence-materialization boundary expected before return to review.

Invariant:

> Do not spend execution-context tokens rediscovering decisions that the control plane can resolve once and encode into an authoritative task package.

This is a context-efficiency rule, not permission to omit repository inspection or evidence publication. The executor must inspect current repository state, detect drift, and materialize the exact result before returning reviewable evidence.

## 7. Routing Rules

Prefer `CONTROL_REASONING` when the dominant work is problem/requirement reasoning, Authority classification/synthesis, semantic or architecture design, verification design, implementation planning/task packaging, Gate judgment, or defect classification.

Prefer `CODE_EXECUTION` when the dominant work is repository exploration for implementation, code modification, build/test/CI execution, benchmark/evidence collection, or branch/diff/worktree operations.

Prefer `CODE_REVERIFY` after P35 has classified a repair as implementation-owned and the repair contract is explicit.

If a task legitimately spans control and code work, split it at the nearest stable contract boundary instead of forcing one surface to perform both jobs.

## 8. Safety Boundary

The coding surface must fail closed when:

- Current Authority is missing or contradictory;
- the task package leaves a semantic decision unresolved;
- implementation requires changing upstream architecture outside authorized scope;
- required evidence cannot be produced in the current environment;
- the exact result cannot be materialized into the reviewer-accessible evidence boundary required by the task package.

A materialization failure is `BLOCKED_EVIDENCE`; a local-only result is not silently promoted to review evidence.

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

`skillset/ownership.json` owns the machine-readable surface metadata because it already binds lifecycle stages to Primary Owners. The contract exposes:

- semantic surface vocabulary;
- default executor profile mapping;
- `execution_surface_by_stage` for P30-P36;
- explicit declaration that surface handoff does not transfer ownership.

`materialized_ref` is return-evidence metadata, not a new semantic execution surface, lifecycle stage, ownership edge, Gate, or Project State field. It is defined by the shared handoff/instruction contract rather than by `execution_surface_by_stage`.

## 11. Skill Instruction Boundary

Shared `handoff-contract.md` defines `surface_handoff` and evidence-return materialization semantics once.

`aegis-implementation` instructions must:

- keep P30/P31 planning and task packaging on the control surface by default;
- hand P32/P33 repository-heavy execution to the code surface when available;
- include the approved task package in the handoff;
- define the reviewer-accessible materialization obligation in the package;
- require a returned `materialized_ref` before claiming readiness for `CONTROL_REVIEW`;
- preserve Primary Owner semantics.

`aegis-gate-review` continues to own P34-P36 lifecycle semantics. It must resolve `materialized_ref` independently before treating executor claims as evidence. P36 repository repair/reverification may execute on `CODE_REVERIFY` after classification, but its result must be materialized before returning to P34.

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
8. shared handoff instructions distinguish `surface_handoff` from support and ownership handoff;
9. generated/distributed Skill instructions preserve the same boundary;
10. existing v0.2 composition and ownership tests remain green;
11. the shared handoff contract requires reviewer-accessible evidence materialization and `materialized_ref` before review return;
12. implementation instructions reject local-only completion as sufficient P34 evidence;
13. gate-review instructions resolve `materialized_ref` independently before relying on executor claims.

## 13. Non-Goals

v0.1 does not:

- change P-stage ownership;
- add a new lifecycle stage;
- add a new semantic execution surface;
- make token count a Gate metric;
- require ChatGPT or Codex as the only possible products;
- automatically launch an external coding agent;
- permit autonomous multi-stage substantive chaining;
- change Project State Authority/Gate/Evidence semantics;
- require GitHub specifically when another reviewer-accessible durable evidence boundary exists.

## 14. Verification Evidence

Deterministic implementation evidence established the original surface mapping and ownership boundary on PR #10. Execution Surface Behavioral Dogfood v0.1 then exercised the real loop:

```text
ChatGPT P30/P31
-> Codex P32
-> ChatGPT P34
-> P35 EVIDENCE_GAP
-> Codex P36
-> ChatGPT P34 rerun
```

The initial P34 correctly blocked because the P32 result existed only locally. P36 materialized the exact commit `6d614ab6ee297171d2ed5e9c0d487fd3b66f313f` to the PR #10 remote branch. P34 independently resolved that commit and fresh hosted CI passed (`Aegis Project State Integrity` run `33182902314`; `Aegis Skillset Integrity` run `33182902328`, including the behavioral dogfood tests).

That dogfood finding is `F10-01 — Evidence Boundary Materialization`, classified as `MISSING_CONTRACT`. This revision incorporates the resulting rule. Final P34 evidence for the F10-01 repair is recorded against the resulting PR #10 revision rather than hard-coded into this Authority before that revision exists.
