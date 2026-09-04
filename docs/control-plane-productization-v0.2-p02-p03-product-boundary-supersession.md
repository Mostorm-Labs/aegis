# Aegis Control Plane Productization v0.2 — P02/P03 Product Boundary Supersession

Status: **Draft / Proposed Product Authority — minimal P02/P03 supersession**

Scope: `aegis/control-plane-productization`

Exact superseded Product Authority basis:

- base Product Authority head: `c628bdc15fdd3d32511a04b6f09055413f2786c3`
- Product Authority Review #2: `5061188138`
- verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`
- normative base documents:
  - `docs/control-plane-productization-v0.2.md`
  - `docs/control-plane-productization-v0.2-p02-p03-repair.md`

This amendment is intentionally narrow. The two base documents remain normative except where this amendment is more specific about **delivery form, release claim scope, and verification applicability**.

It does **not** reopen the accepted Control Plane problem, lifecycle, ownership, state, routing, proof, repair, resume, or auditability requirements.

---

# 1. Why this supersession exists

The accepted P02/P03 Product Authority defines Aegis v0.2 as a software-development Control Plane whose core product value is to maintain:

- what may be trusted;
- what may happen next;
- what must be escalated to a human;
- durable lifecycle/control state;
- stage/owner routing;
- bounded repair/reverification loops;
- evidence compilation;
- sessionless resume;
- auditability and fail-closed control.

The accepted P02/P03 capability model contains no numeric service-throughput, multi-tenant scale, completed-month availability, or standalone daemon requirement.

Downstream P18 Engineering / Optimization later introduced a distinct assumption:

> R0 is the launch benchmark profile for one logical `Control Service` deployment.

and froze production-shaped reference scale such as 10,000 active WorkScopes, 100 interactive clients, sustained high request/mutation/projection/provider/dispatch rates, plus S0 at 4x R0 for 15 minutes.

P20 Verification then inherited those P18 engineering targets into mandatory R0/S0/long-window proof obligations, and CP-I09 materialized them as release-blocking implementation evidence.

Recent CP-I09 execution exposed that the implementation/reverification loop is spending substantial effort on benchmark admission queues, wall-clock load-delivery accounting, schedule-window overruns, and synthetic service throughput. Those failures are real evidence about the benchmark/profile, but they revealed a **claim-scope mismatch**: v0.2 does not require the product to be a standalone production-scale Control Service in order for the Control Plane product to be valid.

This amendment is therefore not a waiver of failed evidence. It corrects the upstream product claim so downstream proof is proportional to the product actually being released.

---

# 2. Normative v0.2 product boundary

## 2.1 Delivery form

Aegis v0.2 MUST be valid and complete when delivered and used as:

```text
ChatGPT host
  -> Aegis Plugin
  -> nine Aegis Skills
  -> governed external surfaces such as GitHub / Notion / Codex / CI
```

An independently deployed agent product, daemon, hosted multi-tenant service, always-on scheduler, or production Control Service is **not required** for v0.2 product completion.

The Control Plane is a **logical/software-development control system**, not a required standalone service deployment.

A future product may realize the same contracts as a daemon, service, desktop host, or hosted agent, but that is a later deployment claim unless separately governed.

## 2.2 Meaning of “autonomous” in v0.2

The accepted terms `autonomous control plane`, `automatic routing`, `bounded automatic repair`, and `zero clean-path user round trips` are retained.

For v0.2 they mean:

> When the active host/execution surface is available and policy permits, Aegis may derive and perform the next legal control transition without requiring the user to manually transport lifecycle state or issue a mechanical `next step` command.

They do **not** imply:

- a continuously running background process;
- 24x7 service residency;
- a multi-tenant scheduler;
- high-RPS API serving capability;
- guaranteed background polling while no host/session is executing;
- hosted-service availability SLO attainment.

## 2.3 Meaning of “durable” in v0.2

Durable Control State means that trust/control facts required for safe continuation are materialized at reviewer/executor-resolvable durable boundaries and are not dependent on one conversation transcript.

It does **not** require those facts to be owned by a continuously running dedicated Control Service process.

---

# 3. v0.2 release claim envelope

The release-blocking claim for v0.2 is:

> **The Aegis Control Plane contracts are semantically correct, durable, resumable, auditable, fail-closed, ownership-preserving, and usable through the Plugin / nine-Skill product form.**

The release MUST prove, at an appropriate representative workload, at least the following product properties:

1. deterministic lifecycle/control-state derivation;
2. correct Stage Occurrence ownership and transition semantics;
3. correct Trusted Basis propagation and stale/diverged basis rejection;
4. `Trusted Basis != Control Cursor != Execution Cursor` preservation;
5. idempotent replay / duplicate-delivery safety;
6. commit-before-dispatch and no semantic duplicate creation from transport retry;
7. interrupted-work / sessionless resume correctness;
8. bounded P35/P36 repair lineage and fail-closed loop termination;
9. Verification-bound Implementation Package enforcement;
10. exact evidence/materialization provenance;
11. independent P34 Gate ownership and no CI/Pipeline-success substitution for Gate PASS;
12. cross-Skill / cross-surface handoff consistency without ownership collapse;
13. Project State / generated-current-projection consistency where applicable;
14. provider callback/query/reconciliation semantics required by the claimed Plugin workflow;
15. no silent weakening of Authority, proof assurance, scope, or historical evidence.

Exact proof profiles, corpus sizes, or repetition counts remain P20 Verification Design concerns.

---

# 4. Explicit v0.2 non-claims

Unless a later Authority explicitly opts into them, v0.2 does **not** claim:

- production `Control Service` deployment readiness;
- standalone agent / daemon product readiness;
- multi-tenant service capacity;
- 24x7 autonomous background execution;
- R0-scale sustained service throughput;
- S0 4x service-load resilience as a release criterion;
- a 10,000-active-WorkScope / 100-interactive-client service envelope;
- completed-month `>=99.9%` availability attainment;
- production vendor-cost economics under a seven-day service workload;
- global, multi-region, or horizontal service scalability.

A future release may add any of these claims, at which point proportional engineering/verification evidence becomes mandatory.

---

# 5. New P02 non-functional requirements

## CP-NFR11 — Delivery-form sufficiency

The v0.2 Control Plane MUST be realizable through the Plugin / nine-Skill delivery form without requiring a standalone Control Service, daemon, or hosted agent as a prerequisite for semantic correctness or lifecycle completion.

A platform realization may use durable external state and provider integrations, but no dedicated always-on service is required by the v0.2 Product Authority.

## CP-NFR12 — Claim-proportional verification applicability

Release-blocking verification MUST correspond to product capabilities and deployment claims actually made by the release.

A failed engineering characterization for an **unclaimed** deployment/scale profile MUST NOT be converted into a failure of the v0.2 Control Plane product claim.

Conversely:

- semantic correctness failures remain release-blocking regardless of workload size;
- evidence may not be discarded, rewritten, or relabeled to manufacture PASS;
- previously failed R0/S0 evidence remains historical evidence about those profiles;
- if a release later claims an R0/S0/service-scale profile, the corresponding evidence becomes mandatory again.

This requirement is an applicability rule, not a weakening of proof assurance.

---

# 6. P03 capability traceability delta

## 6.1 Existing v0.2 capability model retained

The accepted P03 capability families remain required:

| Existing requirement family | Capability | Disposition |
|---|---|---|
| CP-FR01 / FR10 | Persistent Control State / resumable projection | RETAIN |
| CP-FR02 | Automatic Router | RETAIN |
| CP-FR03 | Surface Orchestration | RETAIN |
| CP-FR04 | Repair Loop Controller | RETAIN |
| CP-FR05 / FR09 | Escalation & Macro UX | RETAIN |
| CP-FR06 | Evidence Compiler | RETAIN |
| CP-FR07 | Control Policy Engine | RETAIN |
| CP-FR08 | Verification-Bound Package | RETAIN |
| CP-FR11 | Control Audit Trail | RETAIN |
| CP-FR12 | Loop Safety Guard | RETAIN |

No new product object is required by this supersession.

## 6.2 Added traceability

| Requirement | Required capability / policy | Object/model impact | Architecture impact | Verification impact |
|---|---|---|---|---|
| CP-NFR11 | Deployment-form applicability | none required | Plugin / nine-Skill realization must be sufficient; standalone service is optional | tests must not assume a dedicated service is required for product validity |
| CP-NFR12 | Claim / proof applicability binding | no new semantic aggregate required | engineering profiles must be labeled by claimed deployment envelope | P20 must distinguish release-blocking correctness proof from optional service-scale characterization |

The control semantics remain deployment-neutral. Deployment form may change without redefining Stage Occurrence, Trusted Basis, Control Cursor, repair lineage, package, proof, or Gate truth.

---

# 7. Verification applicability after this supersession

## 7.1 v0.2 release-blocking proof

P20 must continue to require strong evidence for semantic/control correctness, including negative/mutant/oracle evidence where appropriate.

Release-blocking proof should cover the properties listed in section 3 and may use deterministic, property, integration, replay, bounded-load, or repeated-occurrence profiles appropriate to the Plugin / nine-Skill product form.

Representative repetition/load may be used to expose races or state drift, but throughput itself is not the product claim.

## 7.2 Engineering characterization

The following may be retained as valuable engineering characterization, but are not v0.2 release blockers unless a corresponding deployment claim is separately adopted:

```text
R0 production-shaped service throughput / latency profile
S0 4x R0 service stress / backlog-recovery profile
W7D service economics characterization
completed-month availability attainment
```

Historical artifacts and failed runs remain immutable evidence for those characterization profiles.

---

# 8. Downstream Authority impact map

This supersession intentionally distinguishes **semantic/control Authority** from **deployment-scale engineering Authority**.

## 8.1 Retained without product redesign

### Product base

- `c628bdc15fdd3d32511a04b6f09055413f2786c3`
- review `5061188138`

Disposition: retained except where this amendment is more specific.

### P10-P13 Modeling

- accepted head `f29c4da3698038e0174e4380707fa618b03c40b2`
- review `5062616510`

Candidate disposition: **RETAIN**.

Reason: this supersession does not change the product objects, interaction semantics, canonical schema, or mutation/operation contracts. Stage Occurrence, Trusted Basis, Control Cursor, Control Policy, Escalation, Repair Lineage, and Verification-bound Package remain required.

### CP-I01 through CP-I08 accepted implementation semantics

Candidate disposition: **RETAIN / DO NOT RERUN BY DEFAULT**.

Reason: their accepted value is semantic/control correctness, not standalone service-scale attainment. Governance must still fail closed if any individual slice is shown to depend normatively on a service-only claim.

## 8.2 Requires targeted applicability review

### P14-P17 Architecture / Platform

Candidate disposition: **RETAIN SEMANTIC CONTRACTS; REVIEW DEPLOYMENT ASSUMPTIONS ONLY**.

No architecture redesign is requested. Governance should identify only clauses that make a standalone Control Service mandatory rather than one optional realization.

## 8.3 Directly impacted

### P18 Engineering / Optimization

- accepted head `e657f0e74771184b98f8c8e6f8a8581e4858c82d`
- review `5062769390`

Impact:

- the R0 `first production-shaped Control Service deployment` launch profile is no longer a required v0.2 release claim;
- S0 `4 x R0 for 15 minutes` is no longer a required v0.2 release claim;
- service-throughput, service-latency, service-backlog, seven-day economics, and completed-month availability targets become deployment-profile characterization unless separately opted into;
- semantic correctness invariants and safe optimization rules remain valid.

Candidate governance disposition: **PARTIAL SUPERSESSION / TARGETED P18 APPLICABILITY REPAIR**.

### P20 Verification Design

- accepted head `db83168e4086e47a7f431acf289006e4f25b8ffd`
- review `5062933855`

Impact:

- any proof obligation whose release applicability exists solely because P18 made R0/S0/service economics a v0.2 launch claim must be reclassified;
- `CPV-C11 R0 Engineering Budget`, S0 service-scale proof, and `CPV-C19 Long-window Cost / Availability` require targeted applicability repair;
- D0/semantic correctness, invariant, mutation/oracle, evidence, ownership, replay, recovery, fail-closed, provider-boundary, and Gate-independence proof remains required;
- no prior evidence or Gate history is rewritten.

Candidate governance disposition: **TARGETED P20 SUPERSESSION REQUIRED**.

### CP-I09 P30/P31/P32/P34/P35/P36 line

Package:

- `CP-I09-P31-01`
- package ref `9f4b76d51ce2e8a2c0ac23d6fba323bc078a9385`

Most recent exact-head reverification discussed by this supersession:

- result revision `85956ea32f7df9f393526473ad5da3382d49ad11`
- workflow run `33657495026`
- R0: FAIL
- S0: FAIL
- W7D: PASS
- combine: SKIPPED

Disposition if this Product supersession is accepted:

> The existing CP-I09 package remains historical evidence for the old service-scale proof contract but is no longer an executable release-blocking package for the narrowed v0.2 claim. The failed R0/S0 results remain true historical results; they are not retroactively PASS.

Do not continue benchmark-queue tuning under the old P31 package while this supersession is under Governance review.

---

# 9. Acceptance criteria for this P02/P03 supersession

This amendment is acceptable only if Governance confirms all of the following:

1. the original accepted P02/P03 did not require a production-scale standalone Control Service as the v0.2 delivery form;
2. Plugin / nine-Skill delivery still satisfies the accepted Control Plane value proposition;
3. autonomous routing/repair semantics remain intact and are not redefined as requiring a daemon;
4. proof assurance, exact refs, independent P34, historical evidence, fail-closed behavior, and ownership boundaries are unchanged;
5. the amendment removes only unclaimed deployment-scale release requirements rather than weakening a claimed semantic requirement;
6. P10-P13 modeling remains valid unless a concrete contradiction is found;
7. P18/P20/CP-I09 service-scale applicability is explicitly superseded rather than silently ignored;
8. failed R0/S0 evidence remains durable historical evidence and is not rewritten as PASS;
9. Current cross-Primary rollout remains `DENIED` until separately governed;
10. no merge, release, rollout expansion, or Gate PASS is implied by Product Authority acceptance.

---

# 10. Explicit non-goals of this supersession

This amendment does not:

- redesign the Control Plane;
- remove automatic routing, bounded repair, or sessionless resume;
- remove the Evidence Compiler or Verification-bound Package;
- remove Stage Occurrence / Trusted Basis / Control Cursor semantics;
- weaken Proof Assurance;
- weaken independent review;
- weaken semantic zero-tolerance invariants;
- authorize a new autonomous agent product;
- authorize Current cross-Primary continuation;
- delete or falsify R0/S0/W7D evidence;
- modify CP-I01 through CP-I08;
- repair P18 or P20 directly;
- create a replacement CP-I09 implementation package;
- merge or release anything.

---

# 11. P02/P03 disposition

```yaml
stage: P02/P03 minimal Product supersession
scope: aegis/control-plane-productization
base_product_authority: c628bdc15fdd3d32511a04b6f09055413f2786c3
base_review: 5061188138
change_class: PRODUCT_CLAIM_APPLICABILITY_NARROWING
core_product_semantics_changed: false
delivery_form_clarified: Plugin / nine Skills is sufficient
standalone_agent_or_service_required: false
service_scale_release_claim: NOT_CLAIMED
r0_s0_w7d_release_blocking: false_if_supersession_accepted
historical_evidence_preserved: true
cp_i01_i08_default_disposition: RETAIN
p18_disposition_candidate: TARGETED_APPLICABILITY_REPAIR
p20_disposition_candidate: TARGETED_SUPERSESSION_REQUIRED
cp_i09_old_package_disposition_candidate: HISTORICAL_ONLY
status: READY_FOR_P21_AUTHORITY_REVIEW
```

Earliest next owner after materialization:

`aegis-governance`

Requested next stage:

`P21 Authority Review — v0.2 Product Boundary Supersession`

Governance must review this exact materialized amendment before any downstream Authority or CP-I09 package is changed.
