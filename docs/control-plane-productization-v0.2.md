# Aegis Control Plane Productization v0.2

Status: **Draft / Proposed Product Authority — P02 Product Requirement + P03 Capability Traceability**

Scope: `aegis/control-plane-productization`

Evidence basis:

- observed end-to-end use of the `GT-G1-04-B` lane, including repeated P31/P32/P34/P35/P36 handoffs, exact-ref transport, evidence-only repair, and session-resume friction;
- existing Verification Productization P02/P03 direction: preserve proof depth, compress workflow surface, deterministic evidence collection, exception-centric review, risk-proportional assurance;
- existing Verification Productization P10-P14 candidate work on PR #23 / PR #24;
- current Project State v0.5 Gate Decision lineage and generated blocker projections;
- current Execution Surface v0.2 task-anchor / resume-cursor semantics.

This document does not reject the current Verification Productization work. It reframes it as the **Proof Plane** inside a larger Control Plane productization effort.

Core observation:

> **Aegis's proof model is not excessively complex; its user-visible operation model is excessively complex.**

Core product rule:

> **Preserve proof depth. Remove human participation from lifecycle mechanics.**

Core product definition:

> **Aegis is a software-development control plane that automatically maintains what may be trusted, what may happen next, and what must be escalated to a human.**

---

# 1. P00/P02 problem refinement

The previous productization pass correctly attacked proof-surface complexity, but field use shows that a second class of complexity remains dominant.

## 1.1 Complexity that must remain

The following are trust mechanics and are not considered UX defects:

- exact Authority must be known;
- implementation and independent acceptance must remain separable;
- evidence must be reproducible and reviewer-resolvable;
- immutable source/result/evidence identity must be preserved where required;
- high-risk claims must receive independently credible review;
- unresolved semantic or evidence ambiguity must fail closed;
- historical decisions/evidence must not be rewritten to manufacture trust.

## 1.2 Complexity that must disappear from the normal user path

The following are control-plane mechanics and should not require routine user orchestration:

- approving or requesting every internal B0/B1/B2-style transition;
- manually moving P34 -> P35 -> P36 -> P34 messages between surfaces;
- repeatedly copying `package_ref`, `source_ref`, `result_revision`, and `materialized_ref`;
- manually invoking the next legal stage after a clean PASS;
- manually invoking evidence-only/test-infrastructure repairs that are already within authorized scope;
- reconstructing current state from conversation history and long handoff prompts;
- acting as the message bus between ChatGPT, Codex, CI, GitHub, evidence artifacts, and review.

## 1.3 Root constraint

The root problem is not lifecycle formalization itself.

The root problem is:

```text
formal internal state machine
+ no durable autonomous control loop
= every transition becomes a conversation turn
= human becomes orchestration transport
```

The vNext product must therefore productize **lifecycle control**, not merely verification semantics.

---

# 2. Reconciliation with current design

The current design contains several correct foundations that should be retained.

## 2.1 Retain as-is or nearly as-is

- proof depth and fail-closed semantics;
- `VerificationSpec -> ProofObligation -> EvidenceArtifact -> ProofEvaluation -> P34` separation;
- `STANDARD / CHALLENGED / QUALIFIED` AssuranceClass as proof-strength policy;
- exact EvidenceInputRef / result materialization requirements;
- independent Completeness Checker boundary;
- P34 as the sole official Gate owner;
- append-only/historical Gate Decision lineage;
- Task Anchor != Execution Cursor;
- compact verification UI of Status + Critical Claims + Exceptions;
- deterministic collection of facts that should not be retyped by executors.

## 2.2 Expand, not replace

### Verification Summary -> Lifecycle Summary

The compact exception-centric view must cover the whole control loop, not only verification.

### Evidence Collector -> Evidence Compiler

Collection of runtime facts is necessary but insufficient. Evidence should be generated from canonical semantic expectations plus structured observations, rather than separately maintaining semantically duplicated JSON summaries.

### Project State -> Persistent Control State

Current Project State already proves the value of immutable decision lineage plus generated current projections, but it is not yet a complete project-control cursor for autonomous continuation.

### Execution Surface handoff -> Internal transport

`surface_handoff`, task anchors, resume cursors, and exact result refs remain valuable contracts, but they should become internal protocol fields rather than routine user-facing payload.

### Risk-proportional assurance -> Risk-adaptive control policy

Existing AssuranceClass answers **how strong proof must be**. vNext additionally needs an independent policy answering **how autonomously the control plane may proceed**.

## 2.3 Missing from the current productization design

The current design does not yet provide a first-class capability for:

- autonomous next-stage routing;
- bounded automatic repair loops;
- persistent lifecycle/control cursor;
- escalation-only user interaction;
- evidence compilation from a single semantic source;
- user-facing macro lifecycle abstraction;
- implementation-package-bound acceptance and repair policy;
- automatic cross-surface orchestration while preserving independent stage ownership.

These are the primary v0.2 additions.

---

# 3. Product thesis v0.2

Aegis should no longer be presented primarily as:

> a strict process that humans execute correctly.

It should be presented as:

> **an autonomous trust control plane that advances work while the next transition is provably allowed, and interrupts humans only when authority, semantics, product intent, or material risk requires a decision.**

The core internal graph remains:

```text
Authority
  -> Contract
  -> Implementation
  -> Evidence
  -> Gate
  -> Downstream Trust
```

The product adds a control loop around that graph:

```text
observe durable state
  -> determine next legal action
  -> route to owning stage/surface
  -> execute/materialize result
  -> evaluate evidence / review
  -> classify outcome
  -> auto-advance, auto-repair, or escalate
  -> persist new control state
```

---

# 4. User-facing lifecycle abstraction

P00-P36 remain internal lifecycle stages.

They are not removed and are not renamed as normative stages.

The default user experience exposes four **macro views**, not four replacement lifecycle stages:

```text
DEFINE
  Problem / Authority / Contract

BUILD
  Plan / Package / Implementation

PROVE
  Verification / Evidence / Gate

SHIP
  Integration / Release / Feedback
```

Normal users should interact with:

```text
current macro phase
status
what changed
trusted result
open exceptions
next human decision, if any
```

Internal P-stage trajectory remains expandable for audit/debug purposes.

Acceptance principle:

> A normal user must not need to know the next P-stage in order to continue correct work.

---

# 5. Two orthogonal risk dimensions

A major v0.2 requirement is to keep **proof strength** separate from **control autonomy**.

## 5.1 Proof Assurance — existing semantic axis

Retain:

```text
STANDARD
CHALLENGED
QUALIFIED
```

This answers:

> How strong and independent must the proof be before the result may be trusted?

## 5.2 Control Autonomy — new product-policy axis

Introduce a product-level policy concept with semantics equivalent to:

```text
AUTONOMOUS
REVIEW_GUARDED
HUMAN_DECISION
```

Names may be refined downstream; semantics are normative at P02:

### AUTONOMOUS

The control plane may route, execute, classify, repair, reverify, and re-review within the already-authorized scope without asking the user for each transition.

### REVIEW_GUARDED

Execution and mechanical routing may be automatic, but a credible independent review boundary must be crossed before downstream trust is granted. The user is interrupted only for an unresolved exception, not merely because a review stage exists.

### HUMAN_DECISION

Progression must stop for an explicit human/product/Authority/risk decision before the next trust transition.

Control Autonomy MUST NOT weaken Proof Assurance.

A low-interaction path may still require QUALIFIED proof.

---

# 6. Change classification and default control policy

The policy engine should classify at least these change classes:

| Change class | Default control tendency | Notes |
|---|---|---|
| Authority / product semantics | HUMAN_DECISION | cannot be auto-invented |
| public API / protocol / schema semantics | HUMAN_DECISION or REVIEW_GUARDED | blast radius determines policy |
| production implementation within frozen contract | REVIEW_GUARDED | execution can be automatic; Gate remains independent |
| test implementation | AUTONOMOUS or REVIEW_GUARDED | only if oracle semantics are unchanged |
| test oracle / expected semantic truth | REVIEW_GUARDED or HUMAN_DECISION | oracle changes may redefine proof |
| evidence serializer/compiler | AUTONOMOUS or REVIEW_GUARDED | exact evidence integrity still required |
| evidence metadata regeneration | AUTONOMOUS | append new artifact; never rewrite history |
| narrative docs / typo | AUTONOMOUS | unless document is Authority-bearing |
| irreversible migration / destructive external action | HUMAN_DECISION | explicit decision required |

The exact mapping may be refined by risk factors, but a system MUST distinguish an evidence-format defect from an Authority/semantic defect.

---

# 7. P02 functional requirements

## CP-FR01 — Persistent Control State

Aegis must durably know enough current state to resume the project without reconstructing a long conversation.

The state must make available at minimum:

- current trusted Authority basis;
- active work scope / lane / package;
- current macro phase and internal lifecycle cursor;
- current stage owner;
- accepted source/result/materialized refs;
- accepted Gate Decision occurrence where applicable;
- open findings/blockers and their owning layer;
- completed/accepted child work;
- next legal action;
- current execution cursor where repository execution is resumable;
- autonomous-repair history/budget relevant to the active occurrence.

Exact schema is deferred to P10-P14.

A conversation or handoff prompt MUST NOT be the only durable source of this state.

## CP-FR02 — Automatic Stage / Owner Routing

After each accepted state transition, Aegis must determine the next legal stage and owner automatically.

The user should not need to issue `下一步` merely to advance from a clean PASS into an unambiguous next stage.

Automatic routing MUST preserve stage ownership and cannot turn one component into the semantic owner of another stage.

## CP-FR03 — Cross-Surface Orchestration

Aegis must be able to move authorized work between reasoning/control, code execution, CI/evidence, and independent review surfaces without requiring the user to copy transport payloads.

Internal transport must still preserve exact package/anchor/cursor/result/evidence identities.

## CP-FR04 — Bounded Automatic Repair Loop

When a finding is classified into an authorized repair class, Aegis must be able to run the repair/reverification/re-review loop automatically.

Canonical pattern:

```text
review finding
-> classify owning defect
-> check repair policy
-> repair in authorized scope
-> materialize new exact result/evidence
-> reverify
-> invoke fresh independent review
-> persist new decision
```

Automatic repair must stop when:

- the repair requires Authority/product/semantic change;
- scope expansion is required;
- the defect class is uncertain at a material trust boundary;
- repair attempts exceed bounded policy;
- irreversible/destructive action is required;
- required environment/credential/human observation is unavailable.

## CP-FR05 — Escalation-Only UX

Normal control mechanics must be silent or summarized.

Mandatory user escalation categories include at least:

- Authority conflict;
- missing semantic contract;
- product decision / ambiguous intended behavior;
- API/protocol/schema semantic scope expansion;
- explicit risk/assurance weakening;
- irreversible migration/destructive external action;
- unresolved independent-oracle credibility;
- repeated/uncertain repair beyond configured bounds;
- environment condition requiring human/physical/credential intervention.

Everything else should default toward automatic progression when policy permits.

## CP-FR06 — Evidence Compiler

Aegis must compile evidence artifacts from canonical proof semantics plus structured execution observations.

The canonical direction is:

```text
ProofContract / OracleSpec / Fixture identity
        +
structured runner observation
        +
exact source/result/environment identities
        ↓
Evidence Compiler
        ↓
EvidenceArtifact / matrix / summary / Gate-input bundle
```

Semantic expectations MUST NOT be independently retyped into multiple evidence JSON layers.

A test implementation is not itself the ultimate semantic Authority. Test cases should reference canonical ProofContract/oracle semantics rather than silently redefining them.

Evidence repair should normally regenerate a new immutable artifact rather than hand-editing prior accepted evidence.

## CP-FR07 — Risk-Adaptive Control Policy

Aegis must select control autonomy from change class, semantic blast radius, reversibility, historical defect context, and required proof independence.

This policy is independent from AssuranceClass.

The product must support a high-assurance but low-interaction path.

## CP-FR08 — Verification-Bound Implementation Package

An implementation package must be born with its acceptance context, rather than discovering verification semantics only after implementation completes.

The package must reference, without duplicating canonical truth:

```text
Authority / Contract basis
Code / scope boundary
VerificationSpec / required obligations
Acceptance oracle / pass contract
Evidence compilation contract
Gate policy
Control-autonomy policy
Authorized auto-repair policy
```

The implementation package is not allowed to redefine the ProofContract locally.

## CP-FR09 — Macro Lifecycle UX

The default UI should expose DEFINE / BUILD / PROVE / SHIP plus status and exceptions.

P-stage detail, exact SHAs, evidence digests, and routing history remain available through progressive disclosure.

## CP-FR10 — Sessionless Resume

When the durable project state is healthy, a new session should be resumable from a compact intent such as:

```text
继续 Aegis
```

The system must derive the trusted current cursor and next action from durable state rather than requesting a multi-thousand-token manual handoff.

## CP-FR11 — Autonomous Transition Auditability

Every automatic transition must remain explainable.

For each material transition Aegis must retain enough information to answer:

- what state/input was trusted;
- which owner/stage acted;
- what policy authorized automatic progression;
- which exact result/evidence/decision was produced;
- why the next route was selected;
- whether repair occurred;
- what would have triggered escalation.

Automation may hide mechanics by default but MUST NOT erase them.

## CP-FR12 — Fail-Closed Loop Termination

The orchestrator must stop rather than guess when trust is insufficient.

An automatic loop must never silently:

- weaken Authority;
- weaken required AssuranceClass;
- widen package scope;
- rewrite historical evidence/Gate decisions;
- convert an unresolved review judgment into deterministic PASS;
- exceed configured repair bounds;
- treat stale/diverged refs as current.

---

# 8. Verification as an implementation companion

The field observation that Verification currently feels like a later phase is accepted as a product gap.

The target is not to delete P20 or collapse Verification into P31/P32.

The target is:

```text
Authority / Contract
        ↓
Verification Design
        ↓
implementation package materialization
  carries exact verification/acceptance references
        ↓
Implementation
        ↓
Evidence compilation happens naturally from package execution
        ↓
Gate
```

Therefore Verification remains independently designed but becomes a **required precondition and companion reference** of executable implementation work.

A package that lacks sufficient acceptance/oracle/evidence policy is not ready for autonomous implementation.

---

# 9. Persistent state model principle

Do not solve Persistent Control State as one mutable giant status document.

The existing Gate Decision lineage demonstrates the safer pattern:

```text
immutable occurrences / decisions
        +
generated current projection
```

vNext should preserve that principle for control state.

At product-requirement level, distinguish at least three concepts:

```text
Trusted Basis
  what Authority / package / accepted refs constrain the work

Control Cursor
  which lifecycle occurrence/owner/action is currently active

Execution Cursor
  where accepted repository execution currently sits
```

These must not be conflated.

The exact object/schema design belongs to P10-P13.

---

# 10. P03 capability model

The v0.2 control-plane capabilities are:

| Requirement family | Required capability | Existing design reuse | v0.2 delta |
|---|---|---|---|
| CP-FR01 / FR10 | Persistent Control State | Project State lineage; Execution cursor semantics | add durable control cursor + resumable projection |
| CP-FR02 | Automatic Router | existing stage ownership/routing rules | machine chooses next legal owner/action |
| CP-FR03 | Surface Orchestration | Execution Surface handoff contract | transport becomes system-managed rather than human-carried |
| CP-FR04 | Repair Loop Controller | P35/P36/P34 semantics | bounded auto classify/repair/reverify/re-review |
| CP-FR05 / FR09 | Escalation & Macro UX | Status + Critical Claims + Exceptions | extend exception-centric UX across full lifecycle |
| CP-FR06 | Evidence Compiler | Evidence Collector/Materializer | compile artifacts from canonical semantics + observations |
| CP-FR07 | Control Policy Engine | AssuranceClass / risk factors | new orthogonal autonomy policy |
| CP-FR08 | Verification-Bound Package | VerificationSpec + P31 Task Projection | acceptance/evidence/gate/repair refs become package prerequisites |
| CP-FR11 | Control Audit Trail | Gate Decision history / exact refs | explain every automatic route/repair occurrence |
| CP-FR12 | Loop Safety Guard | fail-closed semantics | bound autonomous loops and escalation conditions |

The existing Verification Productization subsystems remain a major Proof Plane under this capability model:

```text
Control Plane
├─ Persistent Control State
├─ Router / Policy / Repair Loop
├─ Surface Orchestration
├─ Escalation UX
│
└─ Proof Plane
   ├─ Verification authoring
   ├─ Profile / ProofContract
   ├─ Obligation generation
   ├─ Evidence compilation/materialization
   ├─ Proof evaluation
   ├─ completeness checking
   └─ independent Gate review
```

This hierarchy is a product capability decomposition, not yet a P14 module topology.

---

# 11. P02 non-functional requirements

## CP-NFR01 — Proof preservation

Workflow compression must not reduce required proof strength or independent-review semantics.

## CP-NFR02 — Human-turn minimization

A clean authorized package should not require a human command between every internal stage transition.

## CP-NFR03 — Evidence-only repair zero-turn target

A deterministic evidence-only defect that is unambiguously within authorized repair policy should require zero additional user round trips before fresh independent re-review.

## CP-NFR04 — Resume compactness

A healthy project must be resumable without a long manual state reconstruction prompt.

## CP-NFR05 — Progressive disclosure

Exact refs, stage IDs, digests, and repair trajectories remain inspectable but are hidden from the default UX unless relevant to an exception or explicit inspection.

## CP-NFR06 — Historical truth

Automatic repair/re-review appends new exact occurrences and decisions; it never rewrites old evidence or Gate history.

## CP-NFR07 — Ownership preservation

Automatic routing does not collapse stage ownership. The orchestrator coordinates owners; it does not become the semantic authority for every stage.

## CP-NFR08 — Independent-review preservation

Automatic invocation of review is allowed; correlated self-review is not.

## CP-NFR09 — Bounded autonomy

Every autonomous loop has a deterministic stop/escalation policy.

## CP-NFR10 — No user-facing P-stage dependency

Normal product usage cannot require the user to know P00-P36 sequencing to proceed safely.

---

# 12. Product acceptance scenarios

## Scenario A — Normal implementation

User:

```text
继续 GT-G1-04-B
```

Target behavior:

```text
Aegis authorizes loop
-> routes implementation
-> executes packages
-> compiles evidence
-> invokes independent Gate review
-> advances through clean child work
-> stops only at a real decision or lane completion
```

User receives a compact final summary rather than each internal transition.

## Scenario B — Evidence-only defect

Observed mismatch affects evidence metadata only; production semantics and proof oracle are unchanged.

Target behavior:

```text
P34 finding
-> automatic ownership classification
-> policy confirms evidence-only repair
-> regenerate/materialize new evidence
-> fresh independent P34
-> PASS
```

User receives the repair summary after closure; no `下一步` turn is required.

## Scenario C — Semantic defect

A repair would change public semantics or the accepted contract.

Target behavior:

```text
finding
-> classify semantic/Authority impact
-> stop autonomous loop
-> surface one explicit decision with affected trust graph
```

No silent repair occurs.

## Scenario D — Session resume

A new conversation starts after partial progress.

Target behavior:

```text
read durable current projection
-> verify current trusted refs / execution cursor
-> resume the first incomplete legal action
```

A hand-authored long prompt is not required.

---

# 13. What this changes about the current Verification Productization stack

The current PR #23 / PR #24 work remains useful and should not be discarded.

It has already established important Proof Plane contracts:

- exact CoverageBasis;
- Claims / ProofContracts / obligations;
- risk-proportional AssuranceClass;
- exact evidence-input identity;
- deterministic ProofEvaluation;
- exception-centric summary;
- independent completeness review;
- subject-aware CoverageBasis obligations;
- P34 sole-Gate boundary.

However, continuing directly into P15 for that narrow stack would optimize only the Proof Plane while leaving the dominant observed user pain unresolved.

Therefore the product-level earliest untrusted layer is now this P02/P03 control-plane expansion.

The downstream consequence is:

```text
current Verification Productization P10-P14
  = retained candidate Proof Plane foundation

new Control Plane Productization P02/P03
  = broader upstream product requirement candidate

next productization work
  = model the new control-plane concepts before finalizing further module design
```

No existing P14 historical result is rewritten by this document. Its sufficiency as the complete vNext product architecture is simply no longer assumed.

---

# 14. Explicit non-goals

v0.2 does not require:

- weakening exact refs or evidence immutability;
- deleting P00-P36;
- removing P34 independence;
- making Codex the Authority/lifecycle owner;
- allowing automatic semantic/API scope expansion;
- allowing infinite retry/repair loops;
- replacing all domain manifests with one giant state file;
- making every test definition the semantic source of truth;
- exposing the new Control Autonomy policy as three confusing user modes by default;
- requiring a new lifecycle stage merely to host orchestration.

---

# 15. P02/P03 disposition

The GT-G1-04-B field experience materially changes the productization problem statement.

The prior statement:

> Preserve proof depth, compress verification workflow surface.

remains valid but incomplete.

The v0.2 statement becomes:

> **Preserve proof depth and stage ownership, while moving lifecycle routing, transport, repair, evidence compilation, and resume mechanics into a durable autonomous control plane. Escalate only decisions the machine cannot safely make.**

P02/P03 candidate status:

```text
Problem evidence: SUFFICIENT
Product direction: READY_FOR_REVIEW
Capability traceability: READY_FOR_REVIEW
```

Next earliest untrusted layer after product review/acceptance:

**P10 Product Object Model / P11 Interaction Behavior for the Control Plane**, specifically the durable concepts needed to represent control occurrence, control cursor, policy, escalation, repair attempt/lineage, and verification-bound package relationships without turning every transient noun into a new aggregate.
