# 09 v0.2 Aegis Multi-Skill Composition Semantics — Primary Owner + Supporting Skill Contract

Status: **Proposed Design Authority v0.2 — conceptual design approved in chat; written-spec human review pending; implementation not authorized.**

Companion authority: `docs/skill-decomposition-v0.2.md`.

## 1. Context

09 v0.1 decomposed Aegis into one central `aegis` entrypoint plus eight specialists. Its deterministic tooling, generated distributions, Skill Creator packages, and existing Project State/evaluation regressions passed. Installed-platform dogfooding then exposed behavior that the v0.1 runtime-selection model did not define.

The critical evidence is a real ChatGPT Web Gate-audit run with an explicit PR target. The platform invoked `aegis-project-state` first and then `aegis-gate-review` in the same response. This is neither the v0.1 expected single-winner path nor evidence that Gate Review was absent.

The resulting finding is:

```text
F09-04
Primary                  = MISSING_CONTRACT
Secondary                = TEST_DEFECT
Earliest Untrusted Layer = Authority
Start Stage              = P21
```

No further Skill-description tuning is authorized until composition semantics are frozen.

## 2. Problem

v0.1 conflated three different concerns:

1. **discovery order** — which installed Skill the platform invokes first;
2. **semantic ownership** — which Skill is authorized to own the substantive stage result;
3. **composition** — whether another Skill may contribute bounded facts before or during the owning Skill's work.

This made the behavioral oracle over-constrained: it treated the first visible Skill as the unique winner. Real platform behavior demonstrates that multiple Skills can participate in one turn.

The required v0.2 invariant is therefore:

> Multi-Skill execution may compose several Skills, but substantive authority remains single-owner and evidence-gated.

## 3. Alternatives Considered

### 3.1 Strict Single Winner

Each user turn must resolve to exactly one Skill.

Rejected because real installed-platform behavior already composes Skills in one turn, and fighting the platform through increasingly narrow descriptions would make the system brittle without proving semantic correctness.

### 3.2 Free Multi-Skill DAG

Any Skill may call or hand off to any other Skill as long as the final answer looks correct.

Rejected because this creates ambiguous Authority, direct primary-to-primary chaining, handoff loops, silent upstream repair, and duplicate verdict ownership.

### 3.3 Single-Owner Compositional Graph — Selected

Multiple Skills may participate, but every substantive result has exactly one Primary Owning Skill. Supporting Skills are non-owning. The central `aegis` router controls ambiguity and blocked handoff, not specialist substantive work.

This model matches observed platform composition while preserving Aegis's evidence-gated authority discipline.

## 4. Role Model

### 4.1 Primary Owning Skill

A Primary Owning Skill is the unique Skill authorized to own the user-visible substantive result for the active stage family.

Examples:

| Stage family | Primary owner |
| --- | --- |
| P00-P03 | `aegis-discovery` |
| P10-P13 | `aegis-modeling` |
| P14-P18 | `aegis-architecture` |
| P20 | `aegis-verification` |
| P21-P24 | `aegis-governance` |
| P30-P33 | `aegis-implementation` |
| P34-P36 | `aegis-gate-review` |

Direct Project State validation is owned by `aegis-project-state`, but Project State remains cross-cutting and is not a P-stage family.

`Specific Skill Wins` is redefined normatively as:

> If the requested substantive work belongs unambiguously to one available specialist and no earlier blocker short-circuits execution, that specialist must own the substantive result.

It no longer means the specialist must be the first invocation in the trace.

### 4.2 Supporting Skill

A Supporting Skill contributes bounded facts, validation, or derived state without changing substantive ownership.

v0.2 authorizes only `aegis-project-state` as a general cross-cutting Supporting Skill. Additional Supporting Skills require future Authority; they are not inferred from platform behavior.

Allowed Supporting operations:

- read Project State source manifests;
- validate deterministic Project State consistency;
- derive current Authority/Gate/Evidence/Integration facts;
- report blocking Gates and earliest untrusted layer;
- return bounded facts to the owner or router.

Forbidden Supporting operations:

- claim another Skill's P-stage;
- issue another Skill family's final substantive verdict;
- repair or synthesize missing Authority;
- silently choose and execute a different Primary owner;
- convert support into a durable Authority/Gate record by itself.

Role is contextual. `aegis-project-state` is Primary when the user asks to validate `.aegis/`; it is Supporting when a Gate audit needs current Gate/evidence facts.

### 4.3 Central Router

`aegis` remains the single central Router in Multi-Skill Mode.

Router ownership is legitimate when the requested result is itself routing/classification, such as:

- “What should this project do next?”
- “Where should we resume?”
- “Which Aegis stage owns this?”
- a blocked short-circuit whose only valid result is to state the blocker and next owning stage.

The Router may:

- classify source/reality/evidence;
- resolve ambiguity across stage families;
- use or receive Project State support;
- determine Earliest Untrusted Layer;
- select a Primary owner;
- receive a blocked handoff from a Primary;
- emit the terminal routing/blocking result.

The Router may not perform specialist-owned substantive work in Multi-Skill Mode when the relevant specialist is available and execution is not short-circuited.

## 5. Runtime Modes

### 5.1 Multi-Skill Mode

Reviewed specialists are installed and available.

```text
aegis               -> Router / routing answer owner
aegis-project-state -> support or direct state owner
specialists         -> substantive stage owners
```

The platform invoking `aegis` first does not by itself authorize composite fallback.

### 5.2 Composite Compatibility Mode

The relevant specialist is genuinely unavailable and the complete composite `aegis` distribution is the supported fallback.

In this mode, `aegis` may execute stage-family work as compatibility owner while preserving all Aegis Authority/Gate rules.

The runtime must not infer “specialist unavailable” merely from the absence of an earlier invocation in a partially observed trace.

## 6. Invocation Graph

### 6.1 Edge Types

Two edge semantics are frozen:

```text
Support Edge
!=
Ownership Handoff Edge
```

A Support Edge preserves the current substantive owner. An Ownership Handoff transfers control to the central Router because the current owner cannot safely continue.

### 6.2 Allowed Graph Shapes

```text
User -> Primary
User -> Primary -> Support -> Primary
User -> Support -> Primary
User -> Router
User -> Router -> Primary
User -> Support -> Router
Primary -> Router
```

Support-first composition is explicitly valid:

```text
aegis-project-state
        ->
aegis-gate-review
```

when Project State contributes facts and Gate Review owns the P34-P36 conclusion.

### 6.3 Bounded Router Re-entry

One bounded `Router -> Primary -> Router` cycle is permitted only when all conditions hold:

1. the Router selected the Primary based on available facts;
2. the Primary discovers an earlier blocker not already conclusively known;
3. the Primary produces no substantive stage result;
4. the Primary hands ownership back to `aegis`;
5. `aegis` emits the terminal blocker/routing result;
6. no second Primary is automatically executed in the same substantive run.

Anything beyond this is an ownership loop or unauthorized multi-stage continuation.

## 7. Supporting Preflight

Supporting preflight is the bounded fact-establishment phase used to answer whether substantive execution is safe.

It may establish:

- current/superseded Authority identity and status;
- Gate verdict and current validity;
- Evidence availability/current usability;
- Integration occurrence/applicability;
- blocking Gate set;
- earliest untrusted layer.

Supporting preflight does not itself decide a stage-specific substantive conclusion unless Project State validation is the user's requested task.

### 7.1 Support Before Primary

The platform may invoke `aegis-project-state` before a Primary owner. This is valid when the resulting facts are used by the Primary or Router and the Supporting Skill does not issue the owning stage verdict.

### 7.2 Support During Primary

A Primary may consult Project State support and continue if no earlier blocker is found.

### 7.3 Unverifiable Support

If Project State exists but cannot be deterministically verified, the Supporting Skill must not treat generated `state.json` as Authority. The result is an evidence/authority blocker returned to the Router or Primary according to the current ownership state.

## 8. Blocked Short-Circuit

A requested Primary need not execute merely to rediscover a conclusively established earlier blocker.

Two paths are valid.

### 8.1 Primary-Detected Blocker

```text
User -> Primary
Primary -> discovers earlier blocker
Primary -> aegis ownership handoff
aegis -> terminal blocked/routing answer
```

### 8.2 Preflight-Detected Blocker

```text
User -> Support or verified explicit input
Support/input -> conclusively proves earlier blocker
-> aegis
aegis -> terminal blocked/routing answer
```

The requested Primary may be skipped because substantive execution is already unauthorized.

### 8.3 Terminality

A blocked short-circuit terminates the current substantive request. The Router may name the next owning stage but must not automatically execute that repair stage and resume the blocked downstream stage in the same run unless a separate Current Authority explicitly authorizes the end-to-end workflow.

For example, this is forbidden by default:

```text
P14 requested
-> P12 BLOCKED_AUTHORITY
-> aegis
-> aegis-governance repairs P12
-> aegis-architecture resumes P14
```

## 9. Handoff Model

### 9.1 `support_return`

Non-owning fact return:

```yaml
type: support_return
supporting_skill: aegis-project-state
facts:
  blocking_gates:
    - gate-openai-real-baseline
  earliest_untrusted_layer: verification
```

Ownership does not change.

### 9.2 `ownership_handoff`

Transfer from a Primary to the Router:

```yaml
type: ownership_handoff
from_owner: aegis-architecture
to: aegis
reason: earlier_untrusted_layer
requested_stage: P14
earliest_untrusted_layer: P12
status: BLOCKED_AUTHORITY
suggested_next_stage: P21
```

A handoff is ephemeral execution/navigation metadata. It is not Authority, Evidence, Gate, Integration, or Project State.

## 10. Final-Answer Ownership

Every completed user turn has one semantic final-answer owner.

### 10.1 Substantive Stage Completed

`final_answer_owner = Primary Owning Skill`

Example: a completed Gate audit verdict is owned by `aegis-gate-review`, even if `aegis-project-state` supplied facts first.

### 10.2 Routing or Blocked Short-Circuit Only

`final_answer_owner = aegis`

Example: P14 is conclusively blocked by unresolved P12 Authority; no P14 design occurs; `aegis` owns the blocker/next-stage result.

### 10.3 Direct Project State Task

`final_answer_owner = aegis-project-state`

### 10.4 Composite Compatibility

`final_answer_owner = aegis`, with `mode = compatibility`.

### 10.5 Evidence Limitation

`final_answer_owner` is a semantic contract, not assumed to be a platform-native UI field. Behavioral evidence must use the complete response, visible Skill invocation markers, and stage-result content. If those cannot establish ownership, the case is `BLOCKED_EVIDENCE`, not inferred PASS.

## 11. Composition Violations

### 11.1 `MULTIPLE_PRIMARY_OWNERS`

Two Skills claim ownership of the same substantive stage result.

### 11.2 `SUPPORT_OWNERSHIP_LEAK`

A Supporting Skill issues the final result for another Primary's stage family.

Example: `aegis-project-state` independently declares P34 PASS as the Gate owner.

### 11.3 `ROUTER_OWNERSHIP_LEAK`

`aegis` performs specialist-owned substantive work in Multi-Skill Mode while the relevant specialist is available and no short-circuit applies.

### 11.4 `DIRECT_PRIMARY_CHAIN`

Primary A automatically transfers substantive work to Primary B without the central routing/evidence boundary.

### 11.5 `OWNERSHIP_LOOP`

The trace cycles through owner/router/support roles without terminal progress.

Examples:

```text
architecture -> aegis -> architecture -> aegis
```

or

```text
project-state -> aegis -> project-state -> aegis
```

when no new evidence changes actionability.

## 12. Behavioral Evidence Model v0.2

### 12.1 Terminal Trace, Not First Winner

Behavioral evaluation uses the complete terminal invocation trace. A screenshot captured while the model is still working cannot prove that a required Skill never appears later.

The v0.1 predicate:

```text
actual_first_skill == expected_skill
```

is removed from normative acceptance.

### 12.2 Protected Case Schema

Implementation planning should evolve protected cases toward fields equivalent to:

```json
{
  "required_primary_owner": "aegis-gate-review",
  "allowed_supporting_skills": ["aegis-project-state"],
  "router_allowed": true,
  "primary_may_be_skipped_if": ["earlier_blocker_conclusively_established"],
  "expected_terminal_owner": "aegis-gate-review",
  "forbidden_violations": [
    "MULTIPLE_PRIMARY_OWNERS",
    "SUPPORT_OWNERSHIP_LEAK",
    "ROUTER_OWNERSHIP_LEAK",
    "DIRECT_PRIMARY_CHAIN",
    "OWNERSHIP_LOOP"
  ]
}
```

This is a design-level shape, not a frozen file schema until P30/P31.

### 12.3 PASS Rule

A protected installed-platform case PASSes only when the terminal trace proves:

1. terminal response reached;
2. required Primary Owner appears, or an accepted earlier-blocker short-circuit explains safe absence;
3. all Supporting Skills are allowlisted;
4. Supporting Skills do not issue the substantive owning-stage verdict;
5. Router does not steal specialist substantive work;
6. final-answer owner is correct;
7. forbidden downstream substantive execution count is zero;
8. ownership cycles count is zero;
9. handoff loops count is zero.

### 12.4 BLOCKED_EVIDENCE Rule

Use `BLOCKED_EVIDENCE` when the platform evidence is incomplete enough that final-answer ownership or the full Skill sequence cannot be established.

Do not infer absence from a mid-response screenshot.

## 13. Reinterpretation of Existing 09-01 Evidence

Historical v0.1 evidence remains immutable. v0.2 creates new interpretation records.

### 13.1 Direct Gate Review

Observed explicit-target trace:

```text
aegis-project-state
-> aegis-gate-review
```

Under v0.2 this becomes `PASS_CANDIDATE`, not automatic FAIL, because Project State can legally support Gate Review. Final PASS requires the completed response to show that Gate Review owns the P34-P36 substantive result.

### 13.2 Ambiguous Router

`What should this project do next? -> aegis` remains a PASS candidate because routing itself is the requested substantive result.

### 13.3 Upstream Architecture Blocker

The protected case must no longer require `aegis-architecture` as the first invocation. A trusted preflight may short-circuit P14 if unresolved P12 Authority is conclusively established before substantive architecture execution. The required terminal owner becomes `aegis` for the blocked routing result.

### 13.4 Composite Fallback

Composite-only `aegis` remains valid when the relevant specialist is genuinely unavailable.

## 14. Deterministic Verification Changes Required After Approval

No implementation occurs before written-spec approval. The subsequent plan must include RED-first coverage for:

- role definitions and one substantive owner invariant;
- allowlisted Supporting Skills;
- support-first valid traces;
- Primary-first support-return traces;
- earlier-blocker short-circuit with Primary skipped;
- valid bounded `Router -> Primary -> Router` blocker return;
- `support_return` versus `ownership_handoff` distinction;
- each violation class;
- terminal-trace acceptance replacing first-skill acceptance;
- preservation of historical v0.1 dogfood evidence;
- re-evaluation artifacts for v0.2 without rewriting history.

## 15. Skill Instruction Consequences

Implementation may need to update shared contracts and specialist instructions so they can express role/ownership boundaries. However, v0.2 does not authorize another round of broad trigger-description tuning unless a new behavioral defect specifically requires it.

The desired correction is semantic composition, not forcing ChatGPT into a single-dispatch execution model.

## 16. Project State Boundary

v0.2 does not change Project State v0.3 schemas or make invocation traces durable Project State truth.

Invocation composition remains execution evidence. Durable project facts continue to live in Authority, Evidence, Gate, Integration, and generated Project State systems.

## 17. Supersession and Version Governance

Before written-spec acceptance:

```text
09 v0.1 = current proposed execution authority, blocked by F09-04
09 v0.2 = proposed replacement authority
PR #9   = open / unmerged
```

After v0.2 P34 acceptance:

- mark the superseded v0.1 runtime-selection/composition sections historical;
- v0.2 becomes Current Execution Authority for composition semantics;
- preserve all v0.1 documents/evidence;
- Master/parent 09 points to v0.2 for Runtime Selection, Project-State support composition, Handoff, and Behavioral Gate semantics.

The nine-entrypoint topology and existing stage ownership remain inherited from v0.1 unless a future Authority explicitly changes them.

## 18. Non-Goals

v0.2 does not:

- redesign the nine Skill entrypoints;
- add more general Supporting Skills beyond `aegis-project-state`;
- change P00-P36 stage ownership;
- change Project State v0.3;
- make invocation traces a new project-state ledger;
- permit free primary-to-primary orchestration;
- permit automatic cross-stage substantive repair/resume;
- change existing OpenAI hosted provider assumptions;
- claim static routing tests prove platform behavioral composition.

## 19. Acceptance Boundary

This written design is ready for human review only. Implementation remains unauthorized.

After human written-spec approval, the only next skill/process transition is:

```text
writing-plans
-> P30 Implementation Plan
-> P31 Task Packages
-> RED-first composition semantics regressions
-> minimal contract/runtime/oracle implementation
-> Skill Creator validation/package
-> installed-platform 09-01 re-evaluation
-> P34
-> supersession/integration decision
```
