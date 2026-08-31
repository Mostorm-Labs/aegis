# Aegis Control Plane Productization v0.2 — P30 Implementation Planning

Status: **P30 COMPLETE / MATERIALIZED — implementation planning only**

Scope: `aegis/control-plane-productization/implementation-plan`

Owner: `aegis-implementation`

Execution surface: `CONTROL_REASONING`

This artifact is an implementation-control plan. It is not Product/Model/Architecture/Verification Authority, not a P31 task package, not P32 implementation, not Evidence, and not a P34 Gate verdict.

---

# 1. Exact trusted basis

P30 consumes the exact accepted downstream chain below without reopening it.

## Product Authority

- exact head: `c628bdc15fdd3d32511a04b6f09055413f2786c3`
- Product Authority Review #2: `5061188138`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

## Modeling Authority

- exact head: `f29c4da3698038e0174e4380707fa618b03c40b2`
- P21 Authority Review #3: `5062616510`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

## Architecture Authority

- exact head: `e657f0e74771184b98f8c8e6f8a8581e4858c82d`
- P21 Authority Review: `5062769390`
- disposition: `PASS / ACCEPTED_FOR_DOWNSTREAM`

## Verification Design

Accepted P20 head:

`db83168e4086e47a7f431acf289006e4f25b8ffd`

Fresh P20 P21 Authority Review #2:

`5062933855` — `PASS / ACCEPTED_FOR_DOWNSTREAM`

Combined normative P20 package:

1. `docs/control-plane-productization-verification-v0.2.md`
2. `docs/control-plane-productization-verification-v0.2-p21-repair.md`

Repair blob:

`5bed0ce054ead0902bc8c72601814b2f63525067`

Historical P20 review `5062825477` remains historical for old head `c54ed3a9b2058fc1549d855465b42e24b566996c`; its B1/B2/B3 blockers are closed for the accepted repaired head and are not reopened here.

---

# 2. P30 objective

Translate the accepted Product + Modeling + Architecture + Verification contracts into a dependency-aware sequence of **evidence-gated vertical implementation slices**.

The plan deliberately avoids two unsafe decompositions:

```text
module-by-module horizontal implementation
```

and:

```text
implement everything first -> prove it later
```

Instead, each slice must create a bounded executable behavior plus the independent evidence needed to trust the next slice.

The sequence is designed so that later performance, platform, and autonomy claims cannot become credible before the semantic and verifier foundations they depend on have already produced exact durable evidence.

---

# 3. Global invariants controlling every slice

Every later P31 package and P32 execution must preserve all of the following.

1. Project State remains owner of Authority / GateDecision / Integration truth.
2. Proof Plane remains owner of VerificationSpec / ProofObligation / Evidence / ProofEvaluation truth.
3. P34 remains the sole official Gate owner.
4. Control Plane owns only Control Plane control truth.
5. `control-mutation` is the single canonical Control Plane writer.
6. Projection, policy, scheduler, dispatch, recovery, app, worker, cache, webhook, callback, dashboard, CI, provider success, and executor prose are not canonical lifecycle truth.
7. One substantive `StageOccurrence` has exactly one Primary owner.
8. Cross-owner continuation is `terminal A -> recompute -> schedule separate B`, never Primary A executing Primary B.
9. Current Skill Decomposition / Execution Surface Authority still denies unauthorized zero-user-turn cross-Primary rollout.
10. Architecture capability does not imply Current rollout authorization.
11. Commit-before-dispatch and transactional outbox are mandatory.
12. Lane CAS / optimistic compare-and-append is the semantic concurrency oracle; no project-wide global lock.
13. Duplicate delivery of one occurrence is transport retry, not semantic retry.
14. Semantic repair/retry/reverify/rereview is a new governed `StageOccurrence`.
15. Every occurrence has at most one terminal revision; immutable history is never rewritten.
16. Terminalizing occurrence A and scheduling successor B are separate durable transitions.
17. Stale projection cannot authorize mutation.
18. Webhooks/callbacks are hints; exact provider query/reconciliation is the trust path.
19. `Task Anchor != Execution Cursor`.
20. P33 preserves exactly `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, `DIVERGED`.
21. HUMAN_DECISION requires a durable exact external decision ref.
22. No unsafe manual fallback may duplicate already-controlled active work.
23. D0, R0, S0, seven-day cost, and monthly availability remain distinct proof windows.
24. Any zero-tolerance semantic failure invalidates performance evidence from the same candidate.
25. Monthly `>=99.9%` historical attainment cannot be claimed before a complete real UTC calendar month exists.

---

# 4. Decomposition rules

## 4.1 Evidence before dependent complexity

A slice may depend on an earlier slice only after the earlier slice has a reviewer-resolvable durable result and the slice-specific required evidence is complete enough for the declared dependency.

A local worktree, local-only commit, terminal transcript, or executor statement does not satisfy that boundary.

## 4.2 Proof dependency ordering

The controlling proof dependency is:

```text
qualified independent verifier/oracle path
  -> canonical semantic correctness
  -> mutation/CAS/outbox atomicity
  -> projection/policy/scheduler correctness
  -> external trust + historical binding
  -> dispatch/reconciliation/resume
  -> repair/recovery/escalation
  -> platform/capability integration
  -> integrated D0 closure
  -> R0/S0/7-day engineering evidence
```

R0/S0/long-window evidence is invalid if integrated D0 or mandatory verifier qualification is not clean at the exact tested implementation revision.

## 4.3 P31/P32 boundary

P30 defines slices only.

It does **not** emit P31 `VerificationBoundImplementationPackage` records or Codex execution packages.

Later P31 packaging rules:

- package one bounded slice or one explicitly reviewable sub-slice at a time;
- pin Current Authority refs and the applicable P20 proof obligations;
- carry a non-null `task_anchor` for repository-backed work;
- `task_anchor.relation` defaults to `ancestor` where the execution contract permits descendants;
- do not use historical HEAD equality as the only starting predicate;
- keep `resume_cursor` as navigation metadata only;
- require reviewer-accessible `materialized_ref` before returning a completed P32/P33 result to review.

For the first implementation package, the trusted ancestry must descend from the exact materialized P30 head. For later packages, the anchor may advance only to a reviewer-accepted descendant that includes all required predecessor slice results; advancing an anchor never expands semantic scope.

---

# 5. Slice dependency graph

```text
CP-I01  Proof / oracle foundation
   |
   v
CP-I02  Canonical mutation + CAS + transactional outbox
   |
   v
CP-I03  Projection + policy + scheduler + rollout denial
   |
   v
CP-I04  Historical trust + REQUIRED-child + snapshot/provider trust
   |
   v
CP-I05  Dispatch + reconciliation + sessionless resume
   |
   v
CP-I06  Repair + escalation + degraded recovery
   |
   v
CP-I07  Platform API + capability isolation + real adapter boundary
   |
   v
CP-I08  Integrated D0 + verifier qualification + observability closure
   |
   v
CP-I09  R0 + S0 + seven-day cost evidence
```

The graph is intentionally mostly linear because each slice establishes correctness assumptions that the next slice consumes. P31 may split a slice into smaller implementation packages, but may not reorder proof dependencies in a way that lets later claims outrun their prerequisites.

---

# 6. CP-I01 — Independent proof foundation + canonical semantic spine

## Authority basis

- P12 canonical schema and identity/digest rules at modeling head `f29c4da...`.
- P20 independent oracle rules, `CoverageBasis = REVIEW_DECLARED`, `O-CRM`, `O-COMPLETE`, exact `EvidenceInputRef` semantics.
- P20 repair mandatory verifier qualification `M01-M20` and D0 corpus identity `G01-G44`.

## Objective

Create the smallest executable semantic/reference foundation that later runtime code can be compared against without using production control flow as its own oracle.

## Authorized scope

- implementation-neutral `control-domain` canonical types/values/enums;
- RFC 8785 canonicalization + SHA-256 digest primitives required by P12;
- structural validators and exact `CanonicalRef` handling;
- independent deterministic `O-CRM` reference transition interpreter;
- independent obligation/CoverageBasis completeness checker path required by `O-COMPLETE`;
- deterministic fixture/mutant runner capable of representing G01-G44 and M01-M20 inputs;
- exact evidence manifest/digest plumbing for later EvidenceArtifacts.

## Explicit non-goals

- no production scheduler/policy/store/service yet;
- no external provider integration;
- no P34 verdict logic;
- no second Proof Plane store;
- no semantic redesign of P12/P20.

## Runtime / semantic invariants

- canonical bytes/digests deterministic;
- immutable revision identity preserved;
- reference model cannot call production scheduler/mutation control flow;
- completeness checker cannot call the execution-side obligation generator for expected truth;
- unknown/malformed trust-sensitive semantics fail closed.

## Affected modules / surfaces

- `control-domain`;
- test/reference tooling outside production control-flow ownership;
- Proof Plane integration boundary only for exact refs/materialization, not canonical proof ownership.

## Dependencies

Accepted P20 only; no prior implementation slice.

## Required tests / oracle / corpus

- canonicalization/digest golden vectors;
- schema/identity/property tests;
- reference-model deterministic replay tests;
- completeness positive/omission/duplicate/extra obligation cases;
- verifier qualification harness proving every M01-M20 mutant is observable by its designated independent verifier path.

## Required EvidenceArtifacts

- `CPV-E-SPEC`;
- `CPV-E-OBLIGATIONS` when obligation materialization is available;
- `CPV-E-COMPLETENESS`;
- `CPV-E-VERIFIER-QUALIFICATION`.

## Exit criteria

- deterministic canonical codec/reference harness exists at an exact materialized revision;
- mandatory mutant detection = `100%` for M01-M20 with `0` false acceptance;
- `O-CRM` and `O-COMPLETE` independence constraints are mechanically/testably enforced;
- no production control-flow implementation is used as expected truth.

## Downstream Gate applicability

P34-required evidence dependency for every later integrated candidate; no P34 verdict is issued in this slice.

## Failure / repair routing

If canonical semantics cannot be implemented without ambiguity, classify as earlier Authority defect and hand back to P12/P20 owner. Do not patch semantics inside the implementation task.

---

# 7. CP-I02 — Canonical mutation, lane CAS, idempotency, transactional outbox

## Authority basis

- P13 operation vocabulary and append-only mutation rules;
- P15 `control-store` / `control-mutation` boundaries;
- P16 commit-before-dispatch transaction choreography;
- P20 `CPV-C01` and canonical portions of `CPV-C02`.

## Objective

Prove that one durable control trajectory can be mutated safely through the single writer before any real dispatch or provider integration exists.

## Authorized scope

- `control-store` persistence contract;
- lane head/version CAS;
- semantic idempotency records;
- `control-mutation` operation dispatcher/validation pipeline;
- package materialize/revise;
- schedule `OPEN` occurrence;
- terminalize occurrence;
- escalation atomic companion where required;
- schedule transaction + durable outbox creation in one transaction;
- read/audit hooks needed by `O-STORE`.

## Explicit non-goals

- no actual remote dispatch;
- no autonomous cross-Primary scheduling;
- no projection cache optimization;
- no real provider trust adapters;
- no global lock.

## Runtime / semantic invariants

- only `control-mutation` authors canonical records;
- immutable revisions only;
- same request ID + same fingerprint replays result; different fingerprint fails closed;
- one lane CAS winner; loser creates no occurrence/outbox;
- independent lanes can commit independently;
- OPEN + lane advance + idempotency + permitted outbox commit all-or-none;
- terminal revision unique;
- terminal A does not implicitly create successor B.

## Affected modules / surfaces

- `control-domain`;
- `control-store`;
- `control-mutation`;
- minimal `control-query`/audit test surface.

## Dependencies

`CP-I01` complete.

## Required tests / oracle / corpus

- `O-CRM + O-STORE + O-AUTH` differential tests;
- same-lane race and unrelated-lane concurrency tests;
- transaction crash-point tests;
- idempotency replay/conflict tests;
- direct durable-state audit;
- applicable G01-G03 and canonical atomicity/history scenarios from G01-G44.

## Required EvidenceArtifacts

- `CPV-E-CANONICAL-CONFORMANCE`;
- `CPV-E-STORE-AUDIT` or equivalent exact store-audit artifact retained by the accepted P20 contract;
- raw canonical trace corpus with exact revision/config refs.

## Exit criteria

- illegal accepted transitions = 0;
- duplicate canonical head = 0;
- half-committed semantic transactions = 0;
- dispatch-before-commit is structurally impossible on this slice because no dispatcher can consume uncommitted work;
- exact result is materialized at a reviewer-accessible durable ref.

## Downstream Gate applicability

Mandatory dependency for `CPV-C01`; partial prerequisite for `CPV-C02`, D0, R0, and S0.

## Failure / repair routing

Implementation defects remain in P32/P36. If atomicity cannot satisfy accepted multi-record semantics with the chosen persistence capability, route to P17/P14 rather than weaken semantics.

---

# 8. CP-I03 — Projection, policy, scheduler, and Current rollout denial

## Authority basis

- P12 generated-only projections;
- P15 `control-projection`, `control-policy`, `control-scheduler` boundaries;
- P16 `read -> trust -> project -> policy -> candidate -> revalidate -> mutate` choreography;
- Current Skill Decomposition / Execution Surface rollout restriction;
- P20 `CPV-C04` and `CPV-C08`.

## Objective

Add automated derivation of current control state and next legal action without granting derived state permission to write or silently enabling cross-Primary zero-turn progression.

## Authorized scope

- deterministic projection from canonical history + supplied external snapshots;
- ControlCursor / macro phase / repair lineage / open escalation / NextLegalAction / lifecycle summary projection;
- policy evaluation including Current rollout authorization;
- transient scheduler candidate derivation;
- candidate revalidation through `control-mutation` before commit;
- disposable projection cache if useful, with correctness-safe miss/rebuild behavior.

## Explicit non-goals

- no dispatch worker;
- no current cross-Primary automatic continuation;
- no canonical cursor/status writes;
- no policy-generated Gate/Authority truth.

## Runtime / semantic invariants

- projection is read-only, deterministic, rebuildable, disposable;
- stale projection cannot authorize mutation;
- scheduler candidate is transient;
- policy may deny autonomous progression even when architecture can derive a next action;
- no cross-owner same-occurrence substantive execution;
- non-Current test fixtures demonstrating future architecture capability cannot be cited as Current authorization.

## Affected modules / surfaces

- `control-projection`;
- `control-policy`;
- `control-scheduler`;
- `control-query`;
- `control-mutation` revalidation boundary;
- optional projection cache.

## Dependencies

`CP-I02` complete.

## Required tests / oracle / corpus

- projection differential tests against `O-CRM`;
- stale-cache/stale-candidate rejection;
- policy matrix with Current rollout denial;
- same-state concurrent scheduler candidate race ending in one CAS winner;
- pause/cache/lease changes proving no canonical history mutation by themselves.

## Required EvidenceArtifacts

- `CPV-E-OWNERSHIP-ROLLOUT`;
- `CPV-E-DERIVED-STATE`;
- update to `CPV-E-CANONICAL-CONFORMANCE` for scheduler/CAS integration.

## Exit criteria

- unauthorized auto-schedules = 0;
- unofficial Gate decisions accepted = 0;
- stale projection authorization = 0;
- cache/pause/lease-only canonical mutations = 0;
- Current cross-Primary rollout remains denied exactly as governed.

## Downstream Gate applicability

Mandatory for `CPV-C04` and `CPV-C08`; prerequisite for all later control-loop slices.

## Failure / repair routing

Any need to weaken Current rollout restriction is an Authority/governance issue, not an implementation repair. Fail closed and route upstream.

---

# 9. CP-I04 — Historical trust, REQUIRED-child barrier, snapshot/provider trust

## Authority basis

- P12 `TrustedBasis`, `RequiredChildAcceptanceBinding`, exact refs;
- P13 REQUIRED-child barrier and atomic successor semantics;
- P15 `control-trust-resolver` / `control-external-ports`;
- P17 `SourceSnapshotToken` and webhook/query trust boundary;
- P20 `CPV-C03`, repaired `CPV-C15`, and exact-envelope trust rules.

## Objective

Make externally owned trust facts consumable without importing their ownership, and prove that historical transitions pin the exact facts that authorized them.

## Authorized scope

- typed external ports and fake deterministic adapters for Project State / Proof / Execution / Human Decision classes;
- `control-trust-resolver` transient support bundles;
- SourceSnapshotToken issue/verify boundary required by P17;
- currentness/resource/version/adapter binding checks;
- REQUIRED child spawn/join/barrier crossing and immutable acceptance binding;
- historical replay from pinned basis rather than today's projection;
- provider capability declaration requiring durable query/correlation for autonomous trust-sensitive capability.

## Explicit non-goals

- no real vendor credential rollout yet;
- no callback-only provider classified as fully autonomous;
- no new ChildAccepted/Finding/Gate aggregate;
- no Current cross-Primary auto dispatch.

## Runtime / semantic invariants

- external truth remains externally owned;
- stale/ambiguous trust fails closed;
- token integrity + adapter/source/resource/version binding required;
- historical replay uses pinned immutable acceptance facts;
- REQUIRED barrier crossing + parent successor creation is atomic;
- all REQUIRED children must be accepted before crossing the barrier;
- no mutable barrier-consumed flag.

## Affected modules / surfaces

- `control-external-ports`;
- `control-trust-resolver`;
- `control-mutation`;
- `control-store`;
- test/provider simulation boundary.

## Dependencies

`CP-I03` complete.

## Required tests / oracle / corpus

- `O-CRM + O-STORE + O-PROVIDER + O-SNAPSHOT + O-AUTH`;
- stale snapshot/version-change-between-read-and-commit;
- tampered/wrong-adapter/wrong-resource token cases G36-G38;
- callback-only provider case G39;
- REQUIRED child acceptance/conflict/ambiguity/history replay scenarios;
- M16-M19 verifier mutants.

## Required EvidenceArtifacts

- `CPV-E-TRUST-CURRENTNESS`;
- `CPV-E-HISTORICAL-REPLAY`;
- `CPV-E-SNAPSHOT-INTEGRITY`;
- `CPV-E-ASYNC-PROVIDER-CAPABILITY`.

## Exit criteria

- stale-success commits = 0;
- historical replay mismatch = 0;
- unbound REQUIRED successor = 0;
- tampered/cross-boundary snapshot accepted = 0;
- no provider is classified fully autonomous without durable query/correlation.

## Downstream Gate applicability

Mandatory for `CPV-C03` and `CPV-C15`; prerequisite for trustworthy dispatch/reconciliation.

## Failure / repair routing

Provider capability gaps remain explicit degraded/blocking facts. Do not invent autonomy or weaken snapshot/currentness contracts to fit a provider.

---

# 10. CP-I05 — Dispatch, reconciliation, exact result materialization, sessionless resume

## Authority basis

- P16 outbox/dispatch/reconciliation choreography;
- P17 Execution Surface contract boundary;
- P12/P13 execution navigation semantics;
- P20 `CPV-C02`, `CPV-C05`, repaired `CPV-C16`.

## Objective

Connect committed occurrences to an execution surface and reconcile exact durable results while preserving at-least-once transport, semantic identity, and sessionless resume.

## Authorized scope

- `control-dispatch` over committed outbox only;
- execution-surface adapter with durable dispatch/query correlation;
- duplicate-delivery dedup/reconciliation by occurrence identity;
- exact reviewer-accessible `materialized_ref` result resolution;
- execution progress checkpointing through accepted `RECORD_EXECUTION_PROGRESS` semantics;
- all four P33 reconciliation states;
- callback-loss query reconciliation;
- delivery uncertainty policy instrumentation.

## Explicit non-goals

- no executor may write canonical records directly;
- no local-only commit/transcript accepted as review-ready evidence;
- no duplicate semantic attempt to erase delivery uncertainty;
- no cross-Primary zero-turn rollout beyond Current authorization.

## Runtime / semantic invariants

- OPEN + outbox committed before dispatch;
- at-least-once transport;
- duplicate delivery remains one occurrence;
- remote acknowledgement is not semantic completion;
- exact result is independently resolvable before terminal completion claiming review readiness;
- `Task Anchor != Execution Cursor`;
- valid descendants are reconciled rather than falsely rejected;
- true divergence fails closed;
- terminalization and successor scheduling remain separate.

## Affected modules / surfaces

- `control-dispatch`;
- `control-recovery` reconciliation entrypoints;
- execution-surface adapter;
- `control-trust-resolver`;
- `control-mutation` progress/terminal operations;
- internal outbox metadata APIs.

## Dependencies

`CP-I04` complete.

## Required tests / oracle / corpus

- G04-G06 style duplicate/crash/callback-loss scenarios plus repaired G40-G41;
- exact-result missing/mismatched/materialized cases;
- P33 four-state resume corpus;
- delivery failure to `12 attempts or 30 min` uncertainty boundary under virtual clock;
- callback loss across accepted reconciliation age bands;
- executor crash/restart without semantic retry.

## Required EvidenceArtifacts

- `CPV-E-DISPATCH-FAULT-MATRIX`;
- `CPV-E-RESUME-CORPUS`;
- `CPV-E-DELIVERY-POLICY`;
- `CPV-E-RECONCILIATION-POLICY`.

## Exit criteria

- dispatch-before-commit = 0;
- semantic occurrence amplification from duplicate transport = 0;
- duplicate terminal revision = 0;
- all four resume states classify correctly with no valid descendant work replayed;
- missing reviewer-accessible materialization returns `BLOCKED_EVIDENCE` rather than false completion.

## Downstream Gate applicability

Mandatory for `CPV-C02`, full persistent-profile `CPV-C05`, and worker/provider portion of `CPV-C16`.

## Failure / repair routing

Execution-provider ambiguity or unavailable durable result materialization must block. Do not substitute executor prose or local state.

---

# 11. CP-I06 — Repair, reverify, rereview, escalation, human decision, degraded recovery

## Authority basis

- P12 RepairContext/Escalation semantics;
- P13 repair/reverify/rereview/escalation operations;
- P16 recovery and timeout-not-failure rules;
- P18 degraded-mode/recovery budgets;
- P20 `CPV-C06`, `CPV-C09`, operational portions of `CPV-C16`.

## Objective

Make failure handling evidence-driven and bounded without turning operational uncertainty into semantic retry or allowing manual escape hatches to duplicate controlled work.

## Authorized scope

- bounded repair lineage and attempt counters;
- separate repair/reverification/rereview occurrences;
- recovery sweeps over OPEN occurrences/outbox;
- timeout/age reconciliation without automatic semantic failure;
- escalation materialization;
- durable HumanDecision external refs;
- pause/unpause and admission/backpressure directives as operational state;
- supported process/store restart and backup/restore test path;
- provider rate-limit adaptation and gradual recovery.

## Explicit non-goals

- no Authority/product/semantic redesign inside repair;
- no generic approved=true override;
- no replacement occurrence merely because time elapsed;
- no unsafe manual duplicate execution of active controlled work;
- no alert becoming semantic truth.

## Runtime / semantic invariants

- semantic repair attempts are new occurrences;
- attempt budget finite and contiguous;
- human-required path waits for exact durable external decision;
- recovery uses normal interfaces and no privileged canonical-write backdoor;
- age/liveness is diagnostic only;
- pause/backpressure affects when, not what history is true;
- rate-limit adaptation reduces provider pressure before weakening proof/review behavior;
- acknowledged canonical history is not lost in supported fault model.

## Affected modules / surfaces

- `control-recovery`;
- `control-policy`;
- `control-scheduler`;
- `control-mutation`;
- `control-store`;
- HumanDecision/provider adapters;
- observability hooks required for recovery evidence.

## Dependencies

`CP-I05` complete.

## Required tests / oracle / corpus

- repair budget exhaustion / wrong-class / scope expansion denial;
- reverify/rereview as separate occurrences;
- human decision absent/chat-only/exact-durable-ref cases;
- crash/restart/backup/restore fault matrix;
- OPEN occurrence age bands;
- G42 rate-limit adaptation;
- unsafe manual fallback negative test.

## Required EvidenceArtifacts

- `CPV-E-HUMAN-DECISION`;
- `CPV-E-RECOVERY-FAULT-MATRIX`;
- `CPV-E-BACKUP-RESTORE`;
- `CPV-E-RATE-LIMIT-CONTROL`;
- updates to `CPV-E-DERIVED-STATE` for pause/backpressure nonsemantic behavior.

## Exit criteria

- unmaterialized human acknowledgement accepted = 0;
- semantic retry caused only by restart/age = 0;
- unsafe manual duplicate = 0;
- acknowledged-commit loss in supported primary fault model = 0;
- repair policy never expands scope or invents upstream Authority.

## Downstream Gate applicability

Mandatory where HUMAN_DECISION/recovery/provider worker profiles are claimed; prerequisite for production-shaped stress/degraded evidence.

## Failure / repair routing

Authority/semantic defects route to earliest upstream owner. Environment/provider defects remain explicit `BLOCKED_ENVIRONMENT`/capability facts rather than being hidden by implementation repair.

---

# 12. CP-I07 — Platform API, capability isolation, adapter corroboration, envelope integrity

## Authority basis

- P17 deployment/process/API/capability contract;
- P15 module isolation;
- P18 record/request-size and credential rules;
- P20 `CPV-C07`, repaired `CPV-C15`/`C17`, and real-platform corroboration requirement.

## Objective

Realize the first production-shaped Control Service boundary while proving that platform convenience does not create new semantic owners or write paths.

## Authorized scope

- logical `aegis-control-api` and `aegis-control-worker` process/profile boundary;
- versioned HTTPS + UTF-8 JSON public `/v1` and internal `/internal/v1` capabilities;
- `POST /v1/operations` P13 operation envelope path;
- OpenAPI 3.1 or equivalent machine-readable API description;
- Control App/tool bridge boundary;
- worker claim/attempt/reconcile interfaces without direct canonical-table write capability;
- credential/capability isolation and secret-exclusion tests;
- provider event ingress as authenticated wakeup + provider query;
- qualified staging/real adapters for claimed launch provider classes;
- payload/record/request-size enforcement with no silent truncation before digest.

## Explicit non-goals

- no generic PATCH status/Gate/canonical endpoint;
- no worker direct append/advance/terminal write;
- no App/Service/Plugin becoming a Primary owner;
- no webhook payload trusted as current truth;
- no CI/provider success interpreted as P34 PASS;
- no silent truncation to make envelopes fit.

## Runtime / semantic invariants

- one logical canonical mutation boundary;
- process colocation does not weaken logical capability separation;
- credentials remain transport capability only;
- unsupported protocol version fails closed;
- canonical semantics round-trip exactly;
- oversized noncanonical artifacts may externalize by exact ref; canonical semantics may not be truncated;
- provider adapters preserve semantic ownership.

## Affected modules / surfaces

- `control-facade` / `control-query`;
- Control Service API surface;
- internal worker API;
- external adapters;
- Aegis Control App/tool bridge;
- capability/credential configuration;
- protocol schemas/OpenAPI.

## Dependencies

`CP-I06` complete.

## Required tests / oracle / corpus

- `O-CONTRACT + O-SNAPSHOT + O-PLATFORM`;
- positive/negative API contract suite;
- forbidden PATCH/direct-write probes;
- idempotency header/body identity checks;
- credential leak scanning over canonical payloads/digests/log fields;
- real/staging callback-loss + query reconciliation corroboration;
- G43 size boundary and M20 silent-truncation mutant.

## Required EvidenceArtifacts

- `CPV-E-API-CONTRACT`;
- `CPV-E-CAPABILITY-SECURITY`;
- `CPV-E-PLATFORM-CORROBORATION`;
- `CPV-E-ENVELOPE-SIZE-INTEGRITY`;
- refreshed `CPV-E-SNAPSHOT-INTEGRITY` / `CPV-E-ASYNC-PROVIDER-CAPABILITY` for claimed real adapters.

## Exit criteria

- forbidden mutation accepted = 0;
- worker canonical append possible = 0;
- secret/capability token in prohibited semantic/log field = 0;
- unsupported version silently interpreted = 0;
- silent truncation before canonical digest = 0;
- every provider claimed autonomous has durable query/correlation corroboration.

## Downstream Gate applicability

Mandatory for full platform profile and prerequisite for integrated D0/full production-shaped evidence.

## Failure / repair routing

If a provider cannot meet exact-query/materialization/capability constraints, the launch capability claim must be reduced or blocked; the adapter may not weaken the semantic contract.

---

# 13. CP-I08 — Integrated D0 closure, observability/retention/alerting, verifier requalification

## Authority basis

- complete combined P20 `CPV-R01..R40` / `CPV-C01..C19`;
- mandatory G01-G44 corpus;
- mandatory M01-M20 qualification;
- P18 observability and operational-retention/alert thresholds.

## Objective

At one exact integrated implementation revision, prove the whole deterministic semantic system is trustworthy before accepting any production-shaped performance result.

## Authorized scope

- integrated deterministic D0 runner over all slices;
- exact evidence input identity/manifests;
- full verifier requalification at the exact integrated revision;
- required metrics/traces/correlation IDs and raw evidence export;
- operational retention behavior;
- alert-rule qualification;
- availability evaluator/classifier qualification only, not historical attainment;
- canonical retention/replay/audit checks.

## Explicit non-goals

- no R0/S0 pass claim yet;
- no seven-day cost pass claim yet;
- no fabricated monthly availability;
- no P34 Gate verdict.

## Runtime / semantic invariants

- every semantic mismatch is zero tolerance;
- performance telemetry cannot override semantic failures;
- evidence is exact/recomputable, not dashboard-only;
- operational retention expiry cannot mutate canonical history;
- alert state cannot mutate lifecycle truth;
- canonical history remains no-auto-delete in v0.2;
- availability evaluator uses explicit numerator/denominator/exclusion/store-health classification and is independently qualified.

## Affected modules / surfaces

- all implemented Control Plane modules through deterministic integration harness;
- observability/export tooling;
- retention/alert configuration;
- independent availability evaluator test tooling;
- evidence materialization/review bundle plumbing.

## Dependencies

`CP-I01` through `CP-I07` complete.

## Required tests / oracle / corpus

- G01-G44 = mandatory;
- M01-M20 = mandatory;
- seeded property traces;
- canonical replay/archive tests;
- G44 retention/alert boundary sweep;
- availability evaluator qualification corpus;
- independent raw-vs-aggregate recomputation.

## Required EvidenceArtifacts

- `CPV-E-D0-CONFORMANCE`;
- `CPV-E-VERIFIER-QUALIFICATION` at the exact integrated revision;
- `CPV-E-RETENTION-REPLAY`;
- `CPV-E-OBSERVABILITY-COST`;
- `CPV-E-OPERATIONAL-RETENTION`;
- `CPV-E-ALERTING-CONFORMANCE`;
- `CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION`;
- applicable refreshed artifacts from CP-I01..I07 with exact EvidenceInputRefs.

## Exit criteria

```text
G01-G44 mandatory scenarios = 44/44 PASS
semantic differential mismatches = 0
zero-tolerance invariant events = 0
M01-M20 detected = 20/20
false acceptance = 0
```

and:

- no required metric family is missing;
- canonical replay drift = 0;
- alert/retention seeded boundaries conform;
- availability evaluator seeded classifications = 100% correct with 0 false exclusion of local failure.

Only after these criteria are satisfied at the exact candidate revision may CP-I09 engineering evidence be treated as credible.

## Downstream Gate applicability

Hard prerequisite for considering R0/S0/7-day evidence. Produces mandatory P34 evidence inputs but not a Gate verdict.

## Failure / repair routing

Any D0 semantic or verifier-qualification failure blocks CP-I09. Fix/reverify the responsible earlier slice and rerun integrated D0; do not continue to performance benchmarking and mark the failure as a performance caveat.

---

# 14. CP-I09 — R0 performance, S0 stress/backpressure, seven-day cost evidence

## Authority basis

- P18 D0/R0/S0 engineering budgets;
- P20 `CPV-C11` / `CPV-C12` / `CPV-C14` / repaired `CPV-C19`;
- accepted long-window distinction.

## Objective

Measure the exact integrated implementation under production-shaped load only after semantic correctness and verifier credibility are established.

## Authorized scope

- 30-minute R0 latency/throughput/resource/provider-amplification benchmark;
- S0 `4 x R0` for 15 minutes with deterministic backpressure/recovery observation;
- exact `CPV-W7D-R0` 168-hour logical workload for cost accounting;
- deterministic accelerated replay only for seven-day cost when exact workload/provider/cost-model identity is preserved;
- raw sample retention and independent metric/cost recomputation;
- final prelaunch evidence bundle assembly.

## Explicit non-goals

- accelerated replay is not availability evidence;
- accelerated replay is not real wall-clock latency evidence;
- 30-minute R0 is not seven-day cost evidence;
- no monthly `>=99.9%` attainment claim before a complete real UTC month;
- no performance optimization may weaken semantic invariants;
- no P34 Gate verdict is emitted by implementation.

## Runtime / semantic invariants

- zero semantic invariant violations during R0 and S0;
- zero acknowledged canonical commit loss;
- provider wait separated from Aegis-local latency;
- already committed outbox work is not dropped to restore metrics;
- critical backpressure defers new autonomous admission before sacrificing committed work;
- seven-day cost numerator/denominator independently recomputable;
- exact workload/provider/cost-model identity retained.

## Affected modules / surfaces

- full production-shaped Control Service/worker profile;
- benchmark/load harness;
- raw metrics/event export;
- independent performance/cost evaluator;
- staging/real adapter path where required.

## Dependencies

`CP-I08` exact integrated D0 closure.

## Required tests / oracle / corpus

- `O-PERF` independent recomputation;
- R0 30-minute benchmark at accepted workload shape;
- S0 4x R0 / 15-minute stress run;
- exact 168 logical hourly slices for `CPV-W7D-R0` cost;
- semantic zero-tolerance counters continuously checked;
- provider-call amplification and rate-limit behavior retained in raw evidence.

## Required EvidenceArtifacts

- `CPV-E-R0-PERFORMANCE`;
- `CPV-E-S0-STRESS`;
- `CPV-E-OBSERVABILITY-COST` refreshed for measured candidate;
- `CPV-E-7D-COST`;
- `CPV-E-PLATFORM-CORROBORATION` where the claimed profile requires it;
- final exact review navigation inputs for later `CPV-E-PROOF-EVALUATION` / `CPV-E-REVIEW-BUNDLE` production by their owning workflows.

## Exit criteria

- all applicable P18 R0 targets evaluated against raw evidence;
- S0 has zero semantic invariant violations and zero acknowledged commit loss, with deterministic admission/backpressure and backlog recovery;
- seven-day cost ratio:

```text
orchestration_overhead_cost
/
substantive_provider_cost
<= 0.10
```

under exact bound workload/provider/cost-model identity;
- no evidence set contains a semantic failure masked by performance success;
- no historical monthly-availability claim is made.

## Downstream Gate applicability

Provides the last implementation-owned prelaunch evidence required for the full production-shaped profile. Later P34 independently resolves exact evidence and remains the only official Gate owner.

Actual `CPV-E-MONTHLY-AVAILABILITY` is deferred to a complete real post-launch UTC calendar month and any release/readiness decision consuming it belongs to the applicable governance/P24 path.

## Failure / repair routing

If semantic counters fail, evidence is invalid and the defect routes to the responsible earlier implementation slice. If only engineering thresholds fail, classify as implementation/engineering defect and repair without changing accepted semantic contracts. If the simple platform capability itself cannot satisfy an accepted requirement without architecture change, hand back to the earliest P14-P18 owner rather than redesign inside P32.

---

# 15. Cross-slice evidence gate matrix

| Slice | Evidence gate required before successor | Main claims |
|---|---|---|
| CP-I01 | independent verifier/oracle foundation; M01-M20 qualification capability | verifier trust / completeness |
| CP-I02 | canonical conformance + store audit clean | C01, prerequisite C02 |
| CP-I03 | rollout + derived-state evidence clean | C04, C08 |
| CP-I04 | trust currentness + historical replay + snapshot/provider capability clean | C03, C15 |
| CP-I05 | dispatch fault + resume + delivery/reconciliation policy clean | C02, C05, C16 |
| CP-I06 | human decision + recovery + backup + rate-limit evidence clean | C06, C09, C16 |
| CP-I07 | API/capability/platform/envelope evidence clean | C07, C15, C17 |
| CP-I08 | G01-G44 + M01-M20 exact integrated closure; retention/alert/evaluator qualification clean | C10, C13, C14, C18 plus integrated critical claims |
| CP-I09 | R0/S0/7-day evidence clean; semantic counters remain zero | C11, C12, C19 |

No successor slice may treat a predecessor's green CI status as equivalent to its evidence gate.

---

# 16. Evidence materialization contract for later P31/P32

Every later repository-backed execution package must require the executor to return at least:

```yaml
result_revision: <exact revision>
materialized_ref: <reviewer-accessible durable ref>
changed_scope: <bounded package scope>
test_evidence_refs:
  - <exact durable evidence/artifact refs>
authority_deviation: none | <exact blocker>
scope_deviation: none | <exact blocker>
blocker: none | <classified blocker>
```

A local-only commit/worktree/test transcript is context, not review evidence.

A later review surface must resolve `materialized_ref` independently before relying on executor claims.

---

# 17. Current rollout restriction treatment

P30 explicitly preserves the distinction:

```text
Target architecture capability
!=
Current rollout authorization
```

Implementation may build the internal capability to derive and represent cross-Primary next actions and separately owned successor occurrences.

Until a separately governed Authority changes Current Skill Decomposition / Execution Surface rules, implementation and tests must keep unauthorized zero-user-turn cross-Primary progression denied in the Current policy fixture.

A test fixture for future/non-Current policy may prove architecture capability, but that fixture and its result may not be cited as Current rollout authorization or as evidence that Current policy permits such progression.

---

# 18. Long-window evidence treatment

## R0 performance

30-minute R0 proves production-shaped latency/throughput/resource budgets only.

It is not seven-day cost evidence.

## Seven-day cost

Required workload:

`CPV-W7D-R0`

Logical window:

`168h`

Evidence:

`CPV-E-7D-COST`

Pass rule:

```text
orchestration_overhead_cost / substantive_provider_cost <= 0.10
```

Deterministic accelerated replay is permitted only for exact cost accounting while preserving workload/provider/cost-model identity.

## Monthly availability

Prelaunch implementation must qualify the availability evaluator/instrumentation and produce:

`CPV-E-AVAILABILITY-EVALUATOR-QUALIFICATION`

It must not fabricate:

`CPV-E-MONTHLY-AVAILABILITY`

Historical attainment for:

- `CONTROL_API_AVAILABILITY`
- `WRITE_PATH_AVAILABILITY`
- `QUERY_PATH_WHEN_STORE_HEALTHY_AVAILABILITY`

requires one complete actual UTC calendar month, with each SLI `>=99.9%` to claim attainment.

---

# 19. P30 disposition

P30 has found no new contradictory Authority, semantic scope conflict, or missing accepted verification contract that requires upstream redesign.

Therefore:

```text
P30 Implementation Planning
  = COMPLETE / MATERIALIZED
```

Earliest untrusted layer moves to:

```text
P31 Task Packaging
```

Next owner remains:

`aegis-implementation`

Next execution surface remains:

`CONTROL_REASONING`

P31 must package the first authorized slice without automatically entering P32 in the same control occurrence.

This P30 completion does not:

- merge PR #25/#26/#27/#28;
- modify `.aegis` Current Authorities;
- supersede Skill Decomposition / Execution Surface;
- enable Current cross-Primary automatic continuation;
- write implementation code;
- create a Codex execution package;
- issue P34 Gate PASS.
