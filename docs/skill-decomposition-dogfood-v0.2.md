# 09-01 Multi-Skill Installed-Platform Behavioral Dogfooding v0.2

Status: **ACTIVE — Task Package 6 entered; current execution-environment preflight is `BLOCKED_ENVIRONMENT`; P34 behavioral acceptance is `BLOCKED_EVIDENCE`; supersession is not authorized.**

## Purpose

This companion preserves `docs/skill-decomposition-dogfood-v0.1.md` as historical evidence and defines the fresh installed-platform rerun required by Aegis Multi-Skill Composition Semantics v0.2.

The machine-readable interpretation matrix remains `skillset/dogfood/installed-platform-v0.2.json`. Historical v0.1 evidence is immutable.

## Authority and Gate Boundary

- `docs/skill-decomposition-v0.1.md` is not yet Superseded.
- `docs/skill-decomposition-v0.2.md` is the human-approved Proposed Replacement Authority with deterministic implementation complete.
- P32 Task Packages 1-5 are deterministic PASS.
- Task Package 6 requires new real installed-platform evidence before P34 may accept v0.2.
- `BLOCKED_EVIDENCE` or `BLOCKED_ENVIRONMENT` is never a PASS substitute.
- P23 supersession may execute only after P34 accepts the v0.2 behavioral Gate.

## Current Task 6 Preflight

Evidence: `skillset/dogfood/evidence/task6-platform-preflight-v0.2.json`.

The current assistant execution environment exposes only `aegis` and `aegis-project-state` as executable Aegis Skill resources to this session. It does not expose the complete specialist set required to prove the normal multi-skill Gate-audit, architecture-blocker, and modeling-owner cases, and it cannot create a fresh independent platform selection event or switch itself into a composite-only catalog from inside the current turn.

Therefore this session records **zero protected rerun verdicts**. It must not infer the target user's installed catalog from this limitation.

Current classification:

```text
Task 6 environment preflight = BLOCKED_ENVIRONMENT
P34 behavioral evidence      = BLOCKED_EVIDENCE
P23 supersession             = NOT AUTHORIZED
```

## Evidence Admissibility Rule

Each protected rerun must be a fresh platform request in an environment satisfying the case catalog precondition. Capture the complete terminal response, not only an early `Used <skill>` indicator.

For every case record at minimum:

```json
{
  "terminal": true,
  "mode": "multi_skill | compatibility",
  "invocations": [
    {"skill": "...", "role": "support | primary | router | compatibility"}
  ],
  "final_answer_owner": "...",
  "genuine_ambiguity": false,
  "earlier_blocker_conclusively_established": false,
  "specialist_availability": {},
  "ownership_edges": [],
  "handoff_edges": [],
  "forbidden_downstream_substantive_execution": 0,
  "primary_substantive_result_emitted": true
}
```

Also preserve platform/session facts that prove the installed catalog or specialist availability, plus screenshots or other observable UI evidence for the complete response.

## Protected Rerun 1 — Direct Gate Audit

Environment precondition: all reviewed Aegis specialists installed and available in one fresh ChatGPT conversation.

Stimulus:

```text
Audit Mostorm-Labs/aegis PR #9 against its Gate evidence.
```

Policy basis: `skillset/routing/direct-trigger.json#direct-004`.

Acceptance:

- `aegis-project-state` may appear as non-owning support;
- normal substantive Primary Owner must be `aegis-gate-review`;
- normal final-answer owner must be `aegis-gate-review`;
- `aegis` may own the terminal result only for genuine ambiguity or an accepted earlier-blocker short-circuit;
- no support ownership leak, router ownership leak, direct Primary chain, or ownership loop.

## Protected Rerun 2 — Ambiguous Router

Environment precondition: normal multi-skill catalog available.

Stimulus:

```text
What should this project do next?
```

Policy basis: `skillset/routing/ambiguous-routing.json#ambiguous-001`.

Acceptance:

- result is routing-only;
- `aegis` is the final-answer owner;
- Project State may support but must not own the routing result;
- complete terminal trace must show no ownership loop.

## Protected Rerun 3 — Trusted Upstream P14 Blocker

Environment precondition: normal multi-skill catalog available, including `aegis-architecture` and central `aegis`.

Use the exact routing-neutral stimulus from `skillset/dogfood/fixtures/upstream-authority-blocker-v0.2.json`:

```text
Design the system architecture for this feature.

Treat the following facts as already verified inputs. Do not inspect, repair, or reinterpret them:

- Target stage: P14 System Architecture
- Earliest untrusted layer: Authority at P12 Semantic Schema
- Status: BLOCKED_AUTHORITY
- Reason: The Semantic Schema authority required by P14 is unresolved and cannot be treated as Current Authority.

Apply the owning stage's safety preflight. Do not invent or repair the missing P12 authority.
```

Acceptance under v0.2:

- the trusted earlier blocker may short-circuit the requested architecture Primary before substantive P14 execution;
- `aegis` owns the terminal blocked/routing result;
- `forbidden_downstream_substantive_execution` must be exactly `0`;
- no P12 repair or invented authority;
- a bounded `Router -> Primary -> Router` return is acceptable only under the v0.2 blocker conditions;
- direct Primary-to-Primary substantive chaining remains forbidden.

## Protected Rerun 4 — Composite Compatibility Fallback

Environment precondition: an independently observable **composite-only** catalog in which the relevant specialist is unavailable and only composite `aegis` is available for the requested stage family.

Stimulus:

```text
Design the semantic schema and operation model for this feature.
```

Acceptance:

- `mode = compatibility`;
- observable environment evidence proves `aegis-modeling` unavailable for this run;
- `aegis` is the compatibility and final-answer owner;
- absence from a partial trace is not availability evidence;
- fail-closed behavior is required if upstream product/object authority is missing.

## Normalization and Oracle

For each protected run, create a new evidence artifact under `skillset/dogfood/evidence/`, normalize the complete trace into the current v0.2 trace vocabulary, and evaluate it with `tools.aegis_skillset.routing.evaluate_terminal_trace` against the corresponding policy.

Every protected case must evaluate to:

```text
PASS
```

Any `BLOCKED_EVIDENCE` remains blocked. Any hard composition violation is a P35 finding before repair.

## P34 Split Gate — Current State

```text
Deterministic Skill-System Tooling = PASS
Skill Package Gate                 = PASS
v0.2 Deterministic Implementation = PASS
Multi-Skill Behavioral Trigger     = BLOCKED_EVIDENCE
Task 6 Execution Environment       = BLOCKED_ENVIRONMENT
Hosted Provider Baseline           = BLOCKED_ENVIRONMENT
Overall 09                         = BLOCKED_AUTHORITY
P23 Supersession                   = NOT AUTHORIZED
```

The `Overall 09` parent remains blocked because v0.1 is still the unsuperseded execution authority while the replacement awaits P34 acceptance. The immediate Task 6 causal blocker is missing admissible platform evidence caused by the current execution-environment limitation.

## Project State Finding

The current `.aegis` v0.3 manifests do not yet register the 09 skill-decomposition v0.1/v0.2 authority pair or a PR #9 P34 Gate record. This manifest omission does not override the repository authority documents, but it must be closed as part of P23/P34 persistence if v0.2 is accepted, so Project State does not drift after supersession.

## Supersession Rule

Only after all four protected reruns PASS and P34 accepts v0.2:

1. preserve v0.1 documents/evidence as historical;
2. mark only the replaced Runtime Selection / Project-State composition / Cross-Skill Handoff / Behavioral Gate scopes Superseded;
3. make v0.2 Current Execution Authority for those scopes;
4. update parent/master links, `.aegis` project-control records, and Notion status;
5. keep repository merge/integration evidence separate from semantic supersession.

Until then, PR #9 remains open/unmerged and no supersession record may claim acceptance.
