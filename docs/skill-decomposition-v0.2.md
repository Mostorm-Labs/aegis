# Aegis Multi-Skill Composition Semantics v0.2

Status: **Proposed Replacement Authority v0.2 — conceptual design approved; written-spec human review pending; implementation frozen.**

This document responds to `F09-04` discovered by 09-01 installed-platform dogfooding. It does not yet supersede `docs/skill-decomposition-v0.1.md`. Supersession occurs only after written-spec approval, implementation/reverification, and P34 acceptance.

## 1. Scope

v0.2 replaces only the v0.1 semantics for:

- Runtime Selection;
- cross-cutting Project State preflight;
- cross-Skill handoff/composition;
- behavioral acceptance of installed-platform Skill execution.

v0.2 preserves the v0.1 nine-entrypoint topology, P-stage ownership map, canonical `skillset/` source model, deterministic build/distribution model, Project State v0.3, defect taxonomy, Gate vocabulary, and Superpowers boundary.

## 2. Evidence Basis — F09-04

09-01 proved that ChatGPT may compose more than one installed Skill in one user turn. A protected Gate-audit request with an explicit PR target visibly produced:

```text
aegis-project-state
        ->
aegis-gate-review
```

The first Skill inspected Project State / Gate / Evidence facts. The second Skill entered the P34-P36 Gate-review family.

v0.1 defines `aegis-project-state` as cross-cutting and `aegis-gate-review` as the P34-P36 primary owner, but it does not define whether a non-owning supporting Skill may execute before the primary owner. The prior 09-01 oracle therefore over-constrained PASS to a single initial Skill winner.

Finding:

```text
F09-04
Primary                  = MISSING_CONTRACT
Secondary                = TEST_DEFECT
Earliest Untrusted Layer = Authority
Start Stage              = P21
```

Until v0.2 is accepted, Overall 09 remains `BLOCKED_AUTHORITY`.

## 3. Core Model — Single-Owner Compositional Graph

A user turn may invoke multiple Skills, but there is at most one substantive owner at a time.

```text
Primary Owning Skill
!=
Supporting Skill
!=
Central Router
```

The invocation order does not itself define ownership.

### 3.1 Primary Owning Skill

The Primary Owning Skill is the unique Skill authorized to own the user-visible substantive result for the active stage family.

Examples:

- P12/P13 modeling result -> `aegis-modeling`;
- P14-P18 architecture result -> `aegis-architecture`;
- P20 verification design -> `aegis-verification`;
- P21-P24 governance result -> `aegis-governance`;
- P34-P36 Gate verdict / defect classification -> `aegis-gate-review`.

`Specific Skill Wins` means **specific Skill owns the substantive result**, not **specific Skill must be the first invocation**.

### 3.2 Supporting Skill

A Supporting Skill contributes bounded facts or validation without taking substantive ownership.

v0.2 authorizes only `aegis-project-state` as a general cross-cutting Supporting Skill.

Allowed supporting powers:

```text
READ
VALIDATE
DERIVE FACTS
```

Forbidden supporting powers:

```text
OWN AN UNRELATED P-STAGE
ISSUE THE FINAL STAGE VERDICT
REPAIR UPSTREAM AUTHORITY
CHOOSE AN ARBITRARY NEW PRIMARY OWNER
```

Role is contextual. `aegis-project-state` is Primary for a direct `.aegis` validation request, but Supporting for a Gate audit that needs Project State facts.

### 3.3 Central Router

`aegis` is the only central ambiguity/cross-domain router in Multi-Skill Mode.

It owns:

- unknown owning-stage classification;
- start / resume / next-step routing;
- cross-domain ambiguity resolution;
- earlier-untrusted-layer routing;
- blocked short-circuit and owner handoff destination.

It does not own specialist substantive work when the relevant specialist is available.

## 4. Runtime Modes

### 4.1 Multi-Skill Mode

When reviewed specialists are available:

```text
aegis              = router / routing answer owner
aegis-project-state= cross-cutting support or direct state owner
specialists        = stage-family substantive owners
```

### 4.2 Composite Compatibility Mode

When the relevant specialist is genuinely unavailable, the composite `aegis` distribution may execute the requested stage family as compatibility owner.

The platform merely invoking `aegis` first is not proof that specialists are unavailable.

## 5. Allowed Invocation Graph

Two edge types are distinct:

```text
Support Edge
!=
Ownership Handoff Edge
```

Allowed patterns include:

```text
User -> Primary
User -> Primary -> Supporting -> Primary
User -> Supporting -> Primary
User -> Router
User -> Router -> Primary
User -> Supporting -> Router
Primary -> Router      # only for earlier blocker / ambiguity handoff
```

A support-first sequence is valid when the Supporting Skill remains non-owning and the substantive owner is preserved.

Example valid Gate audit:

```text
aegis-project-state   # support: inspect state/evidence
        ->
aegis-gate-review     # primary: own P34-P36 conclusion
```

## 6. Forbidden Invocation / Ownership Patterns

The following are invalid by default:

- `Primary A -> Primary B` direct specialist chaining;
- Supporting Skill issuing another family's final substantive verdict;
- `aegis` executing specialist-owned substantive work in Multi-Skill Mode when the relevant specialist is available;
- automatic multi-stage substantive continuation such as `P14 -> P20 -> P30` in one turn without a separately authorized workflow;
- ownership loops such as `architecture -> aegis -> architecture -> aegis`;
- silent authority repair by any supporting or downstream Skill.

A bounded `Router -> Primary -> Router` sequence is allowed at most once when the Primary discovers an earlier blocker unknown to the Router, emits no substantive stage result, and the Router terminates the current substantive request.

## 7. Supporting Preflight

Supporting preflight may establish facts such as:

- current Authority IDs/status;
- Gate validity/verdict;
- blocking Gates;
- Evidence availability;
- integration applicability;
- earliest untrusted layer.

Supporting preflight does not itself own the requested stage verdict.

If a trusted preflight conclusively establishes an earlier blocker before substantive execution, the requested Primary Skill may be skipped.

## 8. Blocked Short-Circuit

A requested stage may be blocked by an earlier trusted fact without loading the requested Primary owner solely for ceremony.

Both paths are valid:

```text
Primary -> detects earlier blocker -> aegis -> stop
```

and

```text
Supporting/verified input -> conclusively establishes earlier blocker -> aegis -> stop
```

Blocked short-circuit is terminal for the current substantive request. The Router may identify the owning repair stage, but must not automatically execute that repair and then resume the blocked downstream stage in the same run unless a separate Current Authority explicitly authorizes such a workflow.

## 9. Handoff Contract

v0.2 separates `support_return` from `ownership_handoff`.

### 9.1 Support Return

```yaml
type: support_return
supporting_skill: aegis-project-state
facts:
  earliest_untrusted_layer: verification
  blocking_gates:
    - gate-openai-real-baseline
```

A support return does not transfer ownership.

### 9.2 Ownership Handoff

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

Ownership handoff is routing metadata, not Authority, Evidence, Gate, Integration, or Project State.

## 10. Final-Answer Ownership

Every terminal turn has one semantic final-answer owner.

- substantive stage completed -> relevant Primary Owning Skill;
- routing-only or blocked short-circuit -> `aegis`;
- direct Project State task -> `aegis-project-state`;
- composite-only compatibility execution -> `aegis` in compatibility mode.

If available platform evidence cannot establish final-answer ownership, the behavioral case is `BLOCKED_EVIDENCE`; do not infer PASS from invocation order alone.

## 11. Composition Violations

v0.2 defines the following violation classes:

- `MULTIPLE_PRIMARY_OWNERS` — more than one Skill claims the same substantive result;
- `SUPPORT_OWNERSHIP_LEAK` — a Supporting Skill issues the owning stage's final substantive verdict;
- `ROUTER_OWNERSHIP_LEAK` — central `aegis` performs specialist-owned substantive work in Multi-Skill Mode while that specialist is available;
- `DIRECT_PRIMARY_CHAIN` — one primary specialist automatically transfers substantive execution to another primary specialist without the router/evidence boundary;
- `OWNERSHIP_LOOP` — an invocation graph cycles between owner/router/support roles without terminal progress.

## 12. Behavioral Acceptance v0.2

The old rule `actual_first_skill == expected_skill` is removed.

A protected installed-platform case PASSes only when the **complete terminal invocation trace** proves all applicable requirements:

1. the response reaches terminal state;
2. the required Primary Owner appears, **or** an allowed earlier-blocker short-circuit explains why it is safely skipped;
3. only allowlisted Supporting Skills appear;
4. Supporting Skills do not steal ownership;
5. the Router does not steal specialist-owned substantive work;
6. final-answer ownership is correct;
7. forbidden downstream substantive execution is zero;
8. ownership cycles are zero;
9. handoff loops are zero.

A mid-stream screenshot is not a complete invocation trace and cannot prove that a later required owner never appears.

## 13. Protected Probe Reinterpretation

After v0.2 acceptance, existing 09-01 evidence must be re-reviewed under the new oracle rather than mechanically preserving v0.1 verdicts.

Expected consequences:

- explicit Gate audit `project-state -> gate-review` becomes a PASS candidate if the completed response shows Gate Review owns the P34-P36 result;
- ambiguous-router case with `aegis` remains a PASS candidate;
- upstream-blocker cases no longer require `aegis-architecture` to be the first invocation when an accepted preflight conclusively short-circuits P14 before substantive execution;
- composite-only fallback remains valid when specialists are genuinely unavailable.

No historical evidence is rewritten or deleted. Old verdicts remain historical under the v0.1 oracle; v0.2 creates a new interpretation record.

## 14. Required Implementation Consequences After Approval

Implementation is not authorized yet. After written-spec approval, P30/P31 must minimally cover:

- composition-role contract representation;
- allowed invocation-graph / violation oracle;
- replacement of first-skill routing assertions with terminal-trace assertions;
- `support_return` vs `ownership_handoff` contract;
- 09-01 evidence re-evaluation without deleting historical v0.1 results;
- regression protection for Primary Owner, Supporting Skill, Router, short-circuit, final-answer owner, and cycle violations;
- Skill instructions/shared contracts only where needed to make the accepted runtime semantics executable.

## 15. Supersession Rule

Until written-spec review and P34 acceptance:

```text
09 v0.1 = current proposed execution authority, blocked by F09-04
09 v0.2 = proposed replacement authority
PR #9   = open / unmerged
```

After acceptance, v0.2 supersedes the v0.1 Runtime Selection, Specialist Safety Preflight, Cross-Skill Handoff, Project State composition, and Platform Behavioral Trigger semantics. The rest of the v0.1 Skill-system architecture remains inherited unless explicitly changed.