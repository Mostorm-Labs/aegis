# Aegis Control Plane Productization v0.2 — P17 Platform Contract

Status: **Draft / Proposed Authority — P17 Platform Contract**

Scope: `aegis/control-plane-productization/platform-contract`

Exact upstream basis:

- accepted P10-P13 modeling head: `f29c4da3698038e0174e4380707fa618b03c40b2`
- P21 Authority Review #3: `5062616510`
- modeling verdict: `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P14 System Architecture materialized head: `54999ce91ff4f35455916c33b4f7891e2b6b8d4d`
- P15 Module Design materialized head: `12f75bc1938406d8d0cadca4d343fcdb95fdbfb9`
- P16 Runtime Data Flow materialized head: `56f7df8aab30a2720b9b180eea0237eae689f291`

Retained Current boundaries:

- Project State registry / Gate Decision lineage remains externally owned;
- `aegis/skill/decomposition` remains the owner of nine-Skill composition and Primary-owner rules;
- `aegis/execution-surface` remains the owner of `Task Anchor != Execution Cursor` and P32/P33 execution-position semantics;
- Aegis Plugin remains a distribution envelope, not a tenth lifecycle owner;
- P34 remains the sole official Gate owner.

P17 consumes those exact semantics. It chooses the physical platform contracts needed to realize P14-P16 without silently changing them.

---

# 1. P17 objective

Freeze the first deployable platform contract for the Aegis Control Plane.

P17 answers:

> **Where does durable control live, how do ChatGPT, Codex, GitHub, CI, Proof Plane, and human decisions connect to it, what protocol crosses each boundary, how are exact snapshots represented, and what capabilities/credentials may each participant possess?**

The platform must make this product behavior possible:

```text
user says "继续 Aegis"
  -> Aegis reasoning surface resolves durable control state
  -> next legal action is derived from canonical/external truth
  -> authorized work is transported without user copy/paste
  -> executor/reviewer returns exact materialized refs
  -> Control Plane reconciles and advances or escalates
```

while preserving:

```text
Aegis Control Plane = orchestration / control progression
ChatGPT Skills       = reasoning / lifecycle stage ownership
Codex                = repository execution surface
GitHub               = repository + durable collaboration/materialization surface
CI                    = execution observation / evidence producer
Proof Plane           = verification/proof semantic owner
P34                   = official Gate owner
Human                 = required product/Authority/risk decisions
```

Core platform rule:

> **Persistent control state must exist outside any one conversation, agent thread, Codex worktree, browser tab, or process memory.**

---

# 2. Non-goals

P17 does not:

- redefine any P10-P13 object, identity, schema, mutation, replay, REQUIRED-child, repair, escalation, or package semantics;
- change P14 subsystem ownership, P15 module ownership, or P16 temporal ordering;
- choose a final cloud vendor;
- choose a final managed database vendor;
- choose a final queue/broker vendor;
- define P18 throughput, SLO, timeout, retry, retention, queue-depth, freshness, or cost budgets;
- implement the Control Plane;
- modify Current Skills, `.aegis`, Project State, Proof Plane, Execution Surface, or Plugin Distribution Authorities;
- make ChatGPT, Codex, GitHub, CI, or an App the canonical Control Plane store;
- require a conversation/session identifier as durable state;
- grant execution surfaces direct canonical database write access;
- make webhook/callback payloads semantic truth;
- make CI success a Gate PASS;
- claim distributed exactly-once execution;
- enable cross-Primary automatic dispatch before Current Authority permits it;
- begin P18/P20/P30/P32 implementation.

---

# 3. Platform principles

P17 freezes these platform-level principles.

## 3.1 Conversation-independent control

ChatGPT conversations, Codex threads, terminal sessions, and browser sessions are clients/execution contexts only.

They may improve UX but are never the sole source of:

- current WorkScope;
- current lane head;
- current occurrence;
- accepted package revision;
- execution cursor;
- Gate/Authority truth;
- repair lineage;
- open escalation;
- next legal action.

## 3.2 One durable control service boundary

The reference platform uses one logical **Aegis Control Service** backed by a transactional durable store.

The service hosts the P15 control-core modules and is the only platform boundary allowed to invoke `control-mutation` against canonical storage.

Multiple service replicas are allowed; correctness still comes from store CAS, not from a singleton process.

## 3.3 Versioned HTTPS + UTF-8 JSON at cross-process boundaries

All network-visible Aegis platform contracts use:

```text
HTTPS
+ UTF-8 JSON
+ explicit protocol version
```

Canonical P12 records retain RFC 8785 + SHA-256 digest semantics.

Transport envelopes may contain operational metadata, but that metadata cannot alter canonical semantic payloads.

## 3.4 Webhooks are wakeups; query/read is reconciliation

Provider callbacks/webhooks/subscriptions are permitted for low latency.

They are never trusted as the sole current-state oracle.

Canonical pattern:

```text
webhook/callback
  -> authenticate + correlate
  -> wake reconciliation
  -> fetch/query exact provider state
  -> resolve exact refs/snapshot token
  -> derive/validate
  -> maybe mutate
```

Missed webhooks therefore cannot permanently lose semantic progress; recovery polling/reconciliation remains available.

## 3.5 Credentials are transport capabilities, not semantic input

Secrets, OAuth tokens, GitHub App tokens, Codex credentials, CI tokens, and callback signing secrets are never stored in:

- TrustedBasis;
- implementation package semantic fields;
- StageOccurrence semantic payload;
- EvidenceArtifact semantic content merely for transport convenience;
- user-visible audit summaries.

Only non-secret capability references/correlation metadata may cross semantic boundaries.

---

# 4. Reference deployment topology

The first production-shaped platform is:

```text
                     User / Product UX
                            |
                            v
                 ChatGPT + Aegis Plugin
                (exact 9 Skills / Router)
                            |
                    tool/app invocation
                            v
                 +-----------------------+
                 |  Aegis Control App    |
                 |  transport bridge     |
                 +-----------+-----------+
                             |
                         HTTPS/JSON
                             |
                             v
+-------------------------------------------------------------------+
|                    AEGIS CONTROL SERVICE                          |
|                                                                   |
| control-facade / query                                            |
| trust resolver / projection / policy / scheduler                  |
| control-mutation                                                  |
| recovery coordinator                                              |
| provider webhook/event ingress                                    |
+-------------------------+-------------------+-----------------------+
                          |                   |
                 transaction/CAS             | internal worker API
                          v                   v
                +----------------+      +--------------------+
                | Canonical      |      | Dispatch /         |
                | Control Store  |      | Reconcile Workers  |
                | + outbox       |      +---------+----------+
                +----------------+                |
                                                  |
                   +------------------------------+------------------+
                   |              |               |                  |
                   v              v               v                  v
              ChatGPT         Codex / repo      GitHub / CI      Human/Proof
              reasoning       execution          adapters          adapters
              surface
```

This is a **logical production profile**. Modules may be colocated initially, but the capability and protocol boundaries remain.

The Aegis Control App is an App/capability bridge. It is not a Skill, not a Primary owner, and not a canonical state owner.

---

# 5. Platform components and ownership

## 5.1 Aegis Plugin

Purpose:

- distribute the exact reviewed Aegis Skill catalog;
- expose `aegis`, `aegis-project-state`, and specialist reasoning entrypoints;
- own no new persistent Control Plane truth.

The Plugin remains governed by existing distribution/composition contracts.

## 5.2 Aegis Control App

Purpose:

- expose versioned Control Service tools to ChatGPT/other clients;
- carry user identity and request correlation;
- render query/escalation outputs in the product surface;
- transport exact refs without asking users to copy them.

The App may call Control Service APIs but cannot:

- decide stage ownership;
- issue Gate verdicts;
- synthesize Authority;
- write canonical records directly;
- bypass `control-mutation`.

## 5.3 Aegis Control Service

Production trust boundary containing:

- `control-facade`;
- `control-query`;
- `control-trust-resolver`;
- `control-projection`;
- `control-policy`;
- `control-scheduler`;
- `control-mutation`;
- `control-recovery` coordination;
- external-event ingress and adapter coordination.

Only this service receives the database capability required to perform canonical Control Store transactions.

## 5.4 Canonical Control Store

Required capability class:

```text
ACID transactional durable store
+ compare-and-append / conditional update
+ unique constraints
+ atomic multi-record commit
+ durable outbox rows/records
+ durable idempotency records
```

P17 deliberately does not pick PostgreSQL, MySQL, SQLite, FoundationDB, or another vendor.

Production conformance is capability-based.

A local-development profile may use a smaller transactional implementation if it passes the same store contract.

## 5.5 Dispatch / Reconcile Workers

Workers own operational delivery/reconciliation only.

They may:

- claim ready outbox work through an internal Control Service contract;
- invoke execution-surface adapters;
- query provider job/delivery state;
- submit non-authoritative observations back for reconciliation;
- request normal mutation/recovery operations through the Control Service.

They may not:

- write canonical StageOccurrence/package/Escalation records directly;
- schedule a new occurrence by editing storage;
- change semantic envelope fields;
- issue a Gate or Authority decision.

## 5.6 Projection cache

Optional disposable cache outside canonical truth.

Any cache technology is allowed if:

- cache deletion loses no semantic history;
- cache values are keyed by projection algorithm version + exact input identity;
- stale cache entries cannot authorize mutation.

---

# 6. Process boundary

P17 chooses the following minimum production process boundary.

## Process A — `aegis-control-api`

Contains:

```text
facade
query
trust resolver
projection
policy
scheduler
mutation
recovery coordinator
provider event ingress
store adapter
```

Capabilities:

- canonical Control Store read/write through `control-mutation`;
- read-only/restricted external trust adapters;
- no general repository execution credential.

## Process B — `aegis-control-worker`

Contains:

```text
dispatch
provider delivery clients
poll/reconciliation loops
operational retry/backoff
```

Capabilities:

- claim/read outbox through internal API;
- update delivery metadata through internal API;
- call external execution providers;
- no canonical record-table write credential.

## Colocation rule

For an initial small deployment, A and B may run in one binary/process.

Even when colocated:

```text
DispatchService
  -> cannot call ControlStore canonical append primitives directly
```

It must use the same logical module contract as if separated.

---

# 7. Language / ABI contract

P17 does not require one implementation language, but it freezes interoperability.

## 7.1 In-process

Modules colocated in one runtime may use native language calls/interfaces.

Those calls must preserve the P15 module dependency/write boundaries.

## 7.2 Cross-process

Cross-process boundaries use versioned HTTPS JSON.

No shared-memory ABI, direct FFI pointer contract, or shared mutable object graph is required across Control Service, workers, ChatGPT, Codex, GitHub/CI, Proof Plane, or Human Decision providers.

## 7.3 Semantic representation

Canonical records crossing a process boundary use their P12 UTF-8 JSON representation.

If a language-specific implementation uses structs/classes internally, serialization must round-trip without changing:

- IDs;
- record revisions;
- canonical refs;
- ordering/canonicalization requirements;
- basis/package/policy digests;
- immutable historical values.

---

# 8. Public Control API contract

The Control Service exposes a versioned `/v1` HTTPS JSON API.

Actual route names may be implemented equivalently, but the following capability families are normative.

## 8.1 Query

```text
GET /v1/work-scopes/{work_scope_id}
GET /v1/work-scopes/{work_scope_id}/control
GET /v1/work-scopes/{work_scope_id}/audit
GET /v1/occurrences/{occurrence_id}
GET /v1/escalations/{escalation_id}
```

Query responses are projection/query DTOs and exact refs, never new semantic truth.

## 8.2 Canonical operation submission

```text
POST /v1/operations
```

Body is one accepted P13 operation envelope.

HTTP header:

```text
Idempotency-Key: <operation_request_id>
```

Rule:

> `Idempotency-Key` MUST equal the P13 `operation_request_id` when both are present.

A mismatch is `INVALID_REQUEST`; the platform does not invent a second idempotency identity.

There is no generic canonical:

```text
PATCH /status
PATCH /cursor
PATCH /gate
PATCH /stage-occurrence
```

API.

## 8.3 Application intents

The facade may expose user/product intents such as:

```text
POST /v1/work-scopes/{id}/request-next-action
POST /v1/work-scopes/{id}/resume
POST /v1/work-scopes/{id}/pause
POST /v1/work-scopes/{id}/unpause
POST /v1/escalations/{id}/submit-decision-ref
```

These are **application intents**, not new P13 mutations.

They must resolve into:

- a query/projection;
- an operational pause directive;
- an exact external decision ref;
- or an existing P13 operation submitted through `control-mutation`.

No facade intent may bypass accepted operation semantics.

## 8.4 API description

The production API should be described by an OpenAPI 3.1 document or equivalent machine-readable contract.

Generated SDK/CLI clients are wrappers over the same API and receive no direct database authority.

---

# 9. Internal worker API

When worker and Control Service are separated, worker coordination uses an authenticated internal `/internal/v1` HTTPS JSON contract.

Required capability families:

```text
claim ready outbox batch
renew/release delivery lease hint
record delivery attempt metadata
request occurrence reconciliation
submit provider observation
query platform capability state
```

Example logical calls:

```text
POST /internal/v1/outbox/claim
POST /internal/v1/outbox/{entry}/attempts
POST /internal/v1/occurrences/{id}/reconcile
POST /internal/v1/provider-observations
```

The internal API intentionally does not expose:

```text
append occurrence revision
advance lane head
set terminal status
set Gate verdict
```

to dispatch workers.

Leases remain coordination only. Store CAS remains semantic concurrency truth.

---

# 10. External event ingress

Provider events enter through adapter-specific signed endpoints or subscriptions.

Normalized operational envelope:

```yaml
platform_event:
  event_id: <provider/native or generated id>
  provider: <github | codex | ci | proof | human-decision | other>
  event_kind: <provider event kind>
  resource_hint: <non-authoritative correlation hint>
  observed_at: <operational timestamp>
  signature_verified: true
```

Rules:

1. duplicate event IDs may be operationally deduplicated;
2. event payload contents are hints until the adapter re-queries the provider;
3. a provider event never directly authorizes a canonical mutation;
4. unsupported/unverifiable signatures are rejected before reconciliation;
5. a missed event is recoverable by periodic/provider query;
6. event order never overrides canonical revision/predecessor order.

---

# 11. SourceSnapshotToken physical representation

P15 requires opaque source snapshot tokens. P17 freezes their wire representation while keeping them semantically opaque to core domain modules.

## 11.1 Compact token form

```text
sst1.<base64url(payload)>. <integrity-tag>
```

Whitespace shown above is illustrative only; the actual token has no spaces.

Logical payload before compact encoding:

```yaml
v: 1
source_kind: <PROJECT_STATE | PROOF_PLANE | EXECUTION_SURFACE | HUMAN_DECISION | OTHER_GOVERNED_SOURCE>
adapter_id: <stable adapter instance/type id>
resource_key: <provider-scoped resource identity>
version_scheme: <provider version scheme>
version_value: <exact provider version value or normalized digest>
observed_at: <RFC3339 operational timestamp>
expires_at: null | <operational freshness deadline>
```

The issuing adapter integrity-protects the compact payload using a service-held signing/MAC capability.

The Control Plane domain treats the whole token as an opaque string.

## 11.2 Freshness validation

`verify_snapshot(token)` is owned by the issuing adapter.

Validation checks:

- token integrity;
- adapter/source compatibility;
- provider resource still resolvable;
- currentness when the consuming mutation requires current truth;
- any configured operational freshness window.

Expiration or staleness is not a semantic verdict; it means the caller must re-resolve the source before a trust-sensitive mutation.

## 11.3 Provider version examples

### GitHub repository file / Project State snapshot

```text
version_scheme = git-commit+blob
version_value  = <commit_sha>:<blob_sha-or-normalized-manifest-digest>
```

### GitHub PR mutable state

```text
version_scheme = github-normalized-resource
version_value  = sha256:<digest of normalized PR state including head/base/state fields>
```

### CI run

```text
version_scheme = ci-run-attempt
version_value  = <run_id>:<run_attempt>:<head_sha>:<normalized-result-digest>
```

### Execution surface position

```text
version_scheme = execution-position
version_value  = <provider_job_id>:<execution_ref>:<exact_revision>:<normalized-position-digest>
```

These tokens are validation guards. Exact semantic refs remain `CanonicalRef` values under P12.

---

# 12. Platform capability discovery

The runtime must distinguish architectural capability from what the installed/current platform can actually perform.

The Control Service exposes a non-semantic capability descriptor:

```text
GET /v1/platform-capabilities
```

Representative shape:

```yaml
platform_contract_version: "0.2"
control_service:
  persistent_state: true
  async_workers: true

catalog:
  state: FULL_SPECIALIST | COMPOSITE_ONLY | PARTIAL_CATALOG | MIXED_REVISION | UNKNOWN

surfaces:
  control_reasoning:
    interactive: true | false
    programmatic_dispatch: true | false
    durable_result_materialization: true | false
  code_execution:
    dispatch: true | false
    status_query: true | false
    callback: true | false
    repository_materialization: true | false
  control_review:
    interactive: true | false
    programmatic_dispatch: true | false
  code_reverify:
    dispatch: true | false

providers:
  github:
    read: true | false
    scoped_write: true | false
    webhooks: true | false
  ci:
    trigger: true | false
    query: true | false
  proof_plane:
    exact_ref_resolution: true | false
  human_decision:
    durable_materialization: true | false
```

Rules:

- capability state is operational/environment evidence, not Authority;
- `programmatic_dispatch: true` does not override current Control Autonomy or Skill Decomposition policy;
- missing capability may yield `BLOCKED_ENVIRONMENT`, user-mediated continuation, or deferred scheduling according to P16/current policy;
- Plugin catalog state remains governed by existing Plugin/Skill Distribution contracts.

---

# 13. Authentication and actor propagation

## 13.1 User -> Control App / Control Service

User-facing clients authenticate through the host workspace/product identity mechanism and present an authenticated subject to the Control Service.

The service maps that identity into P13 actor/audit fields when a user-originated semantic operation is ultimately submitted.

The Control App cannot invent actor identities.

## 13.2 Internal service identity

`aegis-control-api` and `aegis-control-worker` use distinct service identities.

Internal calls require mutually authenticated transport or an equivalent short-lived service credential.

Workers receive only the capabilities required for:

- outbox claim;
- delivery metadata;
- provider dispatch/query;
- reconciliation submission.

## 13.3 External provider credentials

Provider credentials are separated by purpose.

Examples:

```text
GitHub Project State reader
  -> repository metadata/contents/PR/CI read

GitHub materialization writer
  -> only repositories/refs required by the authorized execution workflow

Codex execution credential
  -> occurrence-scoped job/repository execution capability

CI trigger credential
  -> named workflow/job capability

Proof adapter credential
  -> proof-runtime capabilities only
```

A generic Project State read adapter must not receive a convenience credential capable of issuing Gate decisions.

## 13.4 Short-lived execution capability

Dispatch transport may carry a short-lived, target-scoped capability token in transport metadata.

The token is bound to:

- occurrence identity;
- target provider/surface;
- allowed resource/repository scope;
- expiration;
- operation class.

It is not part of the semantic DispatchEnvelope and is never included in canonical digest calculation.

## 13.5 Secrets handling

Secrets live in a platform secret store/environment binding.

They must be redacted from:

- canonical storage;
- GitHub comments/docs;
- evidence summaries unless the evidence contract explicitly requires a non-secret identity;
- logs/traces;
- ChatGPT/Codex prompts except for provider-managed opaque capability injection.

---

# 14. Dispatch wire contract

P15 freezes the semantic `DispatchEnvelope`. P17 wraps it in transport metadata without changing the semantic payload.

```yaml
dispatch_request:
  dispatch_contract_version: "0.2"
  delivery_attempt_id: <operational id>
  correlation_id: <trace id>
  semantic:
    occurrence_ref: <exact StageOccurrence ref>
    work_scope_ref: <WorkScopeRef>
    control_lane_id: <lane>
    stage_span: <accepted stage span>
    primary_owner: <specialist>
    execution_surface: <surface>
    trusted_basis_digest: <digest>
    policy_digest: <digest>
    package_ref: null | <exact P31 package ref>
    input_refs: [...]
  transport:
    provider: <chatgpt | codex | other>
    callback_ref: null | <registered callback endpoint identifier>
    capability_token: <short-lived secret, never persisted as semantic truth>
```

Rules:

1. `semantic` is immutable for all delivery attempts of the same occurrence;
2. `delivery_attempt_id` may change on transport retry;
3. `capability_token` may rotate/reissue without semantic retry;
4. dispatch receiver deduplicates/reconciles by occurrence identity + semantic contract;
5. provider job/thread IDs are transport correlation only.

---

# 15. Delivery receipt and execution observation

A transport acknowledgement is not substantive completion.

## 15.1 Delivery receipt

Representative operational receipt:

```yaml
delivery_receipt:
  delivery_attempt_id: <id>
  provider_job_id: null | <provider id>
  state: ACCEPTED | DUPLICATE | REJECTED | UNKNOWN
  observed_at: <timestamp>
```

This may update outbox delivery metadata only.

## 15.2 Execution observation

A provider may emit:

```yaml
execution_observation:
  occurrence_ref: <exact occurrence>
  provider_job_id: <provider id>
  provider_state: <opaque/normalized operational state>
  execution_position_hint: null | <position hint>
  result_revision_hint: null | <exact revision hint>
  materialized_ref_hint: null | <durable ref hint>
  observed_at: <timestamp>
```

The observation is a reconciliation trigger.

Before terminalization, the adapter must independently resolve:

- exact occurrence correspondence;
- exact accepted execution position where relevant;
- exact reviewer-accessible result/materialized ref;
- applicable source snapshot token.

A raw `success: true` provider field is never sufficient by itself to become Gate/Proof/terminal truth.

---

# 16. ChatGPT / Aegis Plugin platform contract

ChatGPT is the primary current **CONTROL_REASONING** and **CONTROL_REVIEW** product surface.

## 16.1 Plugin role

The Aegis Plugin provides the exact reviewed Skill catalog.

The Control Plane does not collapse the catalog into one universal agent.

The stage-to-Primary mapping remains governed by Skill Decomposition.

## 16.2 Control App role

For Control Plane productization, the recommended ChatGPT installation adds an Aegis Control App/tool connection capable of:

- querying current durable WorkScope/control projection;
- submitting permitted facade intents;
- resolving exact refs through the Control Service;
- displaying escalation/lifecycle summaries;
- receiving/returning exact occurrence context without user copy/paste.

The App is optional at Plugin-distribution level but is required for the full persistent Control Plane product profile.

## 16.3 Sessionless resume

A fresh ChatGPT conversation may begin with:

```text
继续 Aegis
```

The owning/router Skill uses the Control App to query durable state.

Conversation history is supplementary only.

No canonical field depends on:

- ChatGPT conversation ID;
- message ID;
- browser tab;
- hidden chain of thought;
- prior copied handoff prose.

## 16.4 Reasoning occurrence input

A reasoning/review occurrence receives only the context needed for its owned stage, including exact refs and compact summaries.

The runtime may lazily fetch more exact evidence through adapters.

It must not dump the entire historical conversation into every occurrence merely to reconstruct state.

## 16.5 Reasoning result materialization

When downstream trust requires an exact durable result, the reasoning surface must materialize it to a reviewer-resolvable provider, normally:

- repository document/commit;
- PR/review/comment with immutable/native identity as permitted by the relevant contract;
- Proof/Project State artifact owned by the appropriate external workflow.

Assistant prose alone is not a durable exact result when the stage contract requires materialization.

## 16.6 Programmatic invocation capability

P17 distinguishes two platform modes:

### Interactive-only ChatGPT capability

The user starts the ChatGPT turn.

Aegis can still hydrate state automatically and remove copy/paste transport, but the runtime cannot claim zero-user-turn dispatch into a new ChatGPT reasoning occurrence.

### Managed/programmatic reasoning capability

If a governed platform interface can invoke the reviewed Aegis reasoning owner programmatically, the adapter may expose `programmatic_dispatch: true`.

Even then:

```text
platform capability
!= current orchestration authorization
```

Current Skill Decomposition / Execution Surface Authority still gates automatic cross-Primary dispatch.

---

# 17. Codex execution platform contract

Codex is the preferred repository **CODE_EXECUTION** surface and may also serve **CODE_REVERIFY** where the existing Execution Surface contract assigns it.

## 17.1 Submission

A repository-backed Codex dispatch carries:

- exact occurrence ref;
- exact P31 package ref;
- package scope/non-goals;
- exact task anchor;
- nullable accepted resume cursor according to P33 rules;
- required verification/evidence return contract;
- target repository/ref/worktree correlation;
- short-lived execution capability.

The full Aegis Skill catalog is not required inside Codex for execution correctness; the authorized package is the control contract.

## 17.2 Asynchronous job contract

Codex adapter must support:

```text
submit occurrence work -> provider_job_id / delivery receipt
query provider_job_id or occurrence correlation -> current execution state
resolve execution position -> exact execution ref/revision
resolve materialized result -> exact durable result ref
request stop/suspend if provider capability exists
```

Callback/webhook support is optional for latency; query/reconciliation is mandatory for recovery.

## 17.3 Repository position

The adapter implements the Current Execution Surface semantics exactly:

```text
Task Anchor != Execution Cursor
```

and returns one P33 reconciliation classification:

```text
EXACT_CURSOR
DESCENDANT_CURSOR
ANCHOR_DESCENDANT_WITHOUT_CURSOR
DIVERGED
```

No platform shortcut may turn historical expected-HEAD equality back into the sole resume oracle.

## 17.4 Materialization

Repository implementation completion must be visible at a reviewer-accessible durable ref.

Preferred materialization is GitHub-backed exact identity such as:

- pushed branch + exact commit SHA;
- PR + exact head SHA;
- committed evidence artifact refs.

A local worktree-only commit or terminal transcript remains context, not sufficient P34 evidence.

## 17.5 No direct control write

Codex receives no canonical Control Store credential.

It can only return observations/results through the execution adapter/Control Service reconciliation path.

---

# 18. GitHub platform contract

GitHub is a primary repository, collaboration, and durable materialization provider. It is **not** the Canonical Control Store.

## 18.1 Project State reads

`adapter-project-state` may resolve `.aegis` / governance files from GitHub using:

```text
repository identity
+ exact git commit SHA
+ exact file blob/content identity
```

Current mutable branch state is never represented solely by a branch name.

## 18.2 Repository execution/materialization

Execution adapters may use GitHub for:

- branch/worktree ancestry checks;
- commits;
- PRs;
- reviewer-resolvable diffs;
- durable comments/reviews when their owning contract allows them;
- CI run linkage.

All trust-sensitive references pin exact immutable identity.

## 18.3 GitHub App authentication

Preferred production integration uses a GitHub App/installation identity with repository-scoped permissions rather than user personal tokens distributed to workers.

Read and write capabilities should be separated where practical.

## 18.4 Webhooks

GitHub webhooks may wake:

- Project State refresh;
- PR/head reconciliation;
- CI reconciliation;
- repository execution resume checks.

Webhook payload state is re-fetched before trust-sensitive mutation.

## 18.5 PR comments/handoffs

PR comments may remain durable human/audit handoffs.

They are not the canonical Control Plane database and cannot override canonical/external trust owners.

---

# 19. CI platform contract

CI is an execution-observation/evidence provider, not a Gate.

## 19.1 Trigger

When the owning verification/implementation contract permits CI invocation, the adapter triggers a named workflow/job against an exact source/result revision.

Trigger input pins at least:

- repository;
- workflow/job identity;
- exact source/result revision;
- applicable verification/evidence contract ref;
- occurrence correlation.

## 19.2 Result identity

A resolved CI observation includes exact provider identity such as:

```text
run_id
run_attempt
head_sha / source revision
workflow identity
job/check identity
conclusion
artifact refs/digests where applicable
```

## 19.3 Callback + polling

Provider webhook/subscription is preferred for fast wakeup.

The adapter must still support direct run/job query by exact provider ID so missed callbacks are recoverable.

## 19.4 Evidence boundary

CI output may feed the Evidence Compiler / Proof Plane.

It does not independently create:

- P34 PASS;
- Authority;
- Gate Decision;
- child acceptance verdict;
- canonical Control Plane terminal status.

Those remain governed by their owning layers.

---

# 20. Proof Plane platform contract

The Control Plane integrates through `ProofPlanePort` / `adapter-proof-plane` only.

The adapter must support exact resolution for:

- VerificationSpec;
- ProofObligationSet;
- EvidenceArtifact / EvidenceInputRef;
- ProofEvaluation;
- review bundle refs required by P34.

If Proof Plane exposes asynchronous collection/evaluation runtime capabilities, they use the same platform rule:

```text
owned StageOccurrence committed OPEN
  -> invoke governed Proof Plane capability
  -> materialize exact Proof/Evidence output
  -> callback/query wakes reconciliation
```

The Control Service does not gain a generic `set_proof_pass` operation.

An initial implementation may materialize Proof Plane artifacts in GitHub/CI-backed storage while preserving Proof Plane semantic ownership. P17 does not require a separate proof microservice.

---

# 21. Human decision platform contract

HUMAN_DECISION escalation requires a durable external decision, not only UI acknowledgement.

## 21.1 Display

The Control App/UX renders:

- escalation question;
- owning layer;
- minimal affected trust context;
- allowed decision/action surface;
- expandable exact evidence/refs.

## 21.2 Decision materialization provider

A human response that materially resolves an Escalation must first be materialized by a governed external decision provider as an exact immutable artifact/ref.

Logical minimum fields of that external artifact include:

```text
decision identity
actor identity
question/escalation identity
selected/provided decision content
timestamp/audit metadata
immutable provider identity or content digest
```

This artifact is **externally owned** and enters Control Plane history only through `CanonicalRef object_type=EXTERNAL_DECISION`.

It is not a new Control Plane aggregate.

## 21.3 ChatGPT UX

When the user answers inside ChatGPT, the Aegis Control App may materialize the decision through the external provider and return the exact decision ref.

Raw conversation text alone does not count as durable governed resolution when the decision contract requires exact identity.

## 21.4 Resolution

The exact decision ref is then consumed by the separately owned resolving occurrence under existing P13/P16 semantics.

No generic `user approved` bypass is introduced.

---

# 22. Operational pause / resume representation

P16 classifies pause as operational permission, not canonical lifecycle truth. P17 freezes the physical boundary.

The Control Service maintains an **Operational Control Store** namespace separate from canonical P12 records.

Representative mutable row/document:

```yaml
lane_admission_control:
  work_scope_id: <id>
  control_lane_id: <lane>
  mode: RUN | PAUSED
  set_by_actor: <audit identity>
  reason: null | <operational text/code>
  updated_at: <timestamp>
```

Rules:

1. this record is not Authority, Gate, Evidence, StageOccurrence, or ControlCursor;
2. it is excluded from canonical P12 record digests/history;
3. scheduler/policy checks it before autonomous admission;
4. pause prevents future autonomous scheduling but does not erase OPEN occurrences/outbox/history;
5. unpause causes fresh recomputation, never stale-candidate replay;
6. physical storage may share the same database cluster but must remain a logically separate noncanonical namespace.

Stopping already-running provider work uses the provider stop/suspend capability and later reconciliation; pause does not delete semantic history.

---

# 23. Backpressure / admission platform hooks

P17 defines where backpressure lives; P18 chooses thresholds.

Operational controls include:

- scheduler admission permit;
- worker concurrency permit;
- provider rate-limit state;
- outbox lease/ready scheduling metadata;
- adapter circuit-breaker state;
- recovery retry schedule.

These live outside canonical domain records.

When backpressure prevents a **new** occurrence from being safely admitted, scheduler leaves the candidate transient and recomputes later.

When an occurrence + outbox is already committed, provider/backpressure cannot discard it; dispatch remains pending/retryable under P16.

---

# 24. Provider callback / polling contract

P17 uses a uniform reliability rule across ChatGPT-managed invocation, Codex, GitHub, CI, Proof Plane, and Human Decision providers.

```text
callback/subscription = low-latency wakeup
query/poll            = recovery/reconciliation oracle
periodic sweep        = missed-event recovery
```

A provider adapter is considered asynchronously controllable only if the platform can eventually determine one of:

```text
not accepted / not started
accepted / running
materialized result available
terminal provider failure
state unknown
```

If the provider exposes callbacks but no durable query/correlation mechanism, callback loss can create unrecoverable uncertainty; such a provider cannot claim full autonomous execution capability for a trust-sensitive surface.

---

# 25. Failure behavior by platform boundary

## Control Store unavailable

- no new canonical mutation commits;
- API returns environment/unavailable result;
- no transient scheduler decision is dispatched.

## Projection cache unavailable

- rebuild directly from canonical + exact external truth;
- no semantic loss.

## Worker unavailable

- committed outbox remains durable;
- replacement worker later dispatches the same occurrence.

## Provider unavailable before scheduling

- if current capability/policy requires immediate executable capability, do not create an unjustified dispatching occurrence;
- surface/defer as environment/operational blocker according to current contract.

## Provider unavailable after OPEN + outbox commit

- occurrence remains OPEN;
- outbox remains pending;
- retry same occurrence.

## Webhook delivery lost

- periodic/provider query reconciles.

## Credential expires

- refresh/reissue transport credential if authorized;
- do not create a semantic retry merely because a credential rotated.

## Snapshot stale

- re-resolve exact source;
- no trust-sensitive mutation from stale token.

## Unsupported API/semantic version

- fail closed;
- no silent reinterpretation/migration of canonical records.

---

# 26. Startup and shutdown lifecycle

## 26.1 Startup

Production startup order:

```text
load configuration / secret bindings
  -> establish canonical store connection
  -> validate supported schema/API versions
  -> start Control API
  -> start/invalidate disposable projection cache
  -> start outbox/reconcile workers
  -> reconcile pending outbox
  -> reconcile aged/open occurrences
  -> begin periodic external-truth/recovery sweeps
```

Startup does not synthesize new semantic work merely because the process restarted.

## 26.2 Graceful shutdown

```text
stop accepting new nonessential admission
  -> allow/abort in-flight local transactions cleanly
  -> stop claiming new outbox leases
  -> release/expire operational leases
  -> preserve all committed canonical/outbox state
  -> exit
```

Graceful shutdown is not occurrence cancellation.

## 26.3 Crash restart

Crash restart uses the P16 recovery matrix. Process memory is disposable.

---

# 27. Versioning / compatibility

P17 separates three version families.

## Semantic schema version

```text
P12 canonical schema_version = "0.2"
```

Changed only by a governed semantic schema replacement.

## Platform contract version

```text
platform_contract_version = "0.2"
```

Covers HTTP/wire/provider contract compatibility.

## Adapter version

Each adapter advertises its own implementation/contract version and supported provider capabilities.

Rules:

1. newer platform transport must not silently reinterpret older canonical schema;
2. unknown canonical semantic versions fail closed at trust boundaries;
3. additive transport metadata may be ignored only when explicitly nonsemantic;
4. capability negotiation precedes use of optional provider features;
5. whole-plugin catalog upgrade semantics remain owned by Plugin Distribution Authority.

---

# 28. Deployment profiles

## 28.1 Full Control Plane profile

Required for claiming CP-FR01/FR03/FR10 productized behavior:

```text
Aegis Plugin FULL_SPECIALIST catalog
+ Aegis Control App/tool bridge
+ persistent Aegis Control Service
+ transactional Control Store/outbox
+ required external adapters
+ durable result materialization
```

Programmatic cross-Primary dispatch additionally requires both:

- platform surface capability; and
- Current governance authorization.

## 28.2 Interactive compatibility profile

Aegis Plugin may continue to operate without the Control App/service using the current conversational/manual workflow.

That environment does **not** claim the full persistent autonomous Control Plane behavior merely because the Skills are installed.

It may still perform correct stage reasoning under existing Skill contracts.

## 28.3 Local development profile

The Control Service + worker may run locally with a local transactional store and fake/provider sandbox adapters.

The same wire/semantic invariants apply.

Local fake evidence cannot be promoted to production Gate evidence unless the governing Verification contract permits it.

---

# 29. Security / capability matrix

| Component | Required capabilities | Explicitly forbidden by default |
|---|---|---|
| Aegis Plugin Skills | Control API tools, external read tools required by owned stage | canonical DB credential |
| Aegis Control App | user-authenticated HTTPS calls to Control Service | stage/Gate ownership |
| `aegis-control-api` | canonical store; exact external reads; operation auth | arbitrary repo execution shell |
| `aegis-control-worker` | outbox claim; provider dispatch/query; reconciliation submission | canonical record append/advance |
| Project State adapter | GitHub/governance read | generic Gate write |
| Proof adapter | exact Proof/Evidence read; governed proof-runtime calls | P34 verdict capability |
| ChatGPT reasoning adapter | occurrence-scoped reasoning invocation when available | direct DB write |
| Codex adapter | occurrence/package-scoped repo execution | Authority/Gate mutation |
| GitHub materialization writer | exact authorized repository write scope | unrelated repositories |
| CI adapter | named workflow trigger/query | Gate verdict write |
| Human Decision provider | authenticated immutable decision materialization | generic Authority override |

Least authority is a conformance requirement, not only deployment advice.

---

# 30. Current rollout gate on this platform

P17 intentionally supports more capability than Current Authority necessarily permits.

Example installed platform may report:

```yaml
control_reasoning.programmatic_dispatch: true
code_execution.dispatch: true
control_review.programmatic_dispatch: true
```

but current `aegis/skill/decomposition` / `aegis/execution-surface` policy may still prohibit automatic cross-Primary continuation.

Required behavior:

```text
P16 projection derives next owner
  -> P17 capability says surface is callable
  -> control-policy checks Current Authority
  -> if not authorized:
       no autonomous schedule/outbox
       expose NextLegalAction through query/App
```

P17 therefore does not self-authorize the future Aegis Loop.

When governance later explicitly authorizes the loop, the same platform can enable programmatic dispatch without changing canonical stage ownership.

---

# 31. End-to-end platform examples

## 31.1 Sessionless ChatGPT resume

```text
new ChatGPT conversation
  -> Aegis Skill calls Control App
  -> GET current WorkScope/control projection
  -> Control Service resolves canonical + current external truth
  -> returns macro status / next legal action / exact internal refs
  -> Skill continues owned stage or surfaces real decision
```

No hand-authored multi-thousand-token handoff is required.

## 31.2 Codex implementation

```text
P31 package already canonical
  -> occurrence OPEN + outbox
  -> worker dispatches exact package/task anchor to Codex
  -> Codex works on authorized repo scope
  -> pushes/materializes exact result on GitHub
  -> callback wakes worker
  -> worker queries exact job/repo state
  -> Control Service reconciles result
  -> terminal occurrence commit
```

## 31.3 Missed Codex callback

```text
Codex result materialized
  -> callback lost
  -> periodic reconciliation queries provider/repository
  -> exact result found
  -> same occurrence terminalizes
```

No duplicate semantic attempt.

## 31.4 CI evidence

```text
verification occurrence OPEN
  -> CI job triggered on exact revision
  -> workflow_run webhook arrives
  -> adapter re-fetches run/attempt/artifacts
  -> Proof/Evidence owner materializes exact evidence refs
  -> Control Plane reconciles
  -> P34 later consumes exact review bundle
```

CI green does not itself equal Gate PASS.

## 31.5 Human escalation in ChatGPT

```text
Escalation durable
  -> Control App renders one decision
  -> user responds
  -> App materializes exact external decision artifact
  -> returns CanonicalRef(EXTERNAL_DECISION)
  -> separately owned resolving occurrence consumes ref
  -> original Escalation remains immutable
```

---

# 32. P17 invariants

A conforming platform implementation preserves all of the following.

1. persistent Control Plane truth is external to conversation/session memory;
2. Aegis Plugin/Skills remain reasoning ownership surfaces, not the canonical store;
3. Aegis Control App is a transport/capability bridge, not a lifecycle owner;
4. one logical Control Service owns the canonical mutation boundary;
5. multiple service replicas remain safe because store CAS is authoritative;
6. dispatch/reconcile workers have no direct canonical write privilege;
7. cross-process contracts use versioned HTTPS UTF-8 JSON;
8. canonical records retain P12 JSON/digest semantics;
9. public APIs expose explicit P13 operations, never arbitrary canonical PATCH;
10. HTTP idempotency identity does not create a second semantic request identity;
11. callbacks/webhooks are wakeups, not semantic truth;
12. every async provider used for autonomous trust-sensitive work has a recoverable query/correlation path;
13. source snapshot tokens are integrity-protected opaque adapter tokens;
14. exact CanonicalRefs remain the semantic reference mechanism;
15. credentials/capability tokens are excluded from canonical semantic payload/digests;
16. user/service/provider identities are propagated for audit without inventing Authority;
17. GitHub mutable refs are never treated as exact trust identity without pinned revision/content identity;
18. GitHub is not the Control Store merely because many artifacts are materialized there;
19. Codex has no direct Control Store write capability;
20. Codex repository resume preserves all four Current P33 classifications;
21. local Codex output is insufficient where reviewer-accessible materialization is required;
22. CI success remains observation/evidence input, not Gate PASS;
23. Proof Plane exact refs remain externally owned;
24. P34 remains sole official Gate owner;
25. human decisions are durably materialized as exact external refs when required;
26. raw UI acknowledgement/conversation text does not silently become semantic approval;
27. pause/admission/backpressure state is operational/noncanonical;
28. pause never erases OPEN/outbox/history;
29. provider credential rotation/outage does not create semantic retry;
30. process restart does not create semantic retry;
31. unsupported semantic/platform versions fail closed;
32. full Control Plane capability requires the persistent service profile, not only installed Skills;
33. platform capability does not self-authorize cross-Primary automatic orchestration;
34. no P17 decision requires redesigning P10-P16 semantics.

---

# 33. Decisions deliberately deferred to P18

P18 Engineering / Optimization must use measurable workload/cost evidence to choose or validate:

- expected active WorkScopes/lanes;
- expected simultaneous OPEN occurrences;
- Control API request/mutation throughput;
- canonical-store latency/transaction contention targets;
- projection rebuild/cache hit cost;
- outbox dispatch latency;
- worker concurrency;
- provider retry/backoff limits;
- OPEN occurrence age/reconciliation cadence;
- SourceSnapshot freshness budgets;
- scheduler admission/backpressure thresholds;
- CI/Codex/ChatGPT provider latency/cost budgets;
- storage/index/retention/compaction requirements;
- webhook loss/reconciliation SLO;
- observability/alerting SLOs;
- reference benchmark/load profile;
- rollback/degraded-mode strategy.

P18 may choose concrete performance mechanisms only while preserving the P17 platform boundaries.

---

# 34. P17 handoff boundary

P17 is complete when downstream engineering can implement/benchmark the platform without deciding semantic ownership or inventing transport behavior ad hoc.

The next architecture-family stage is:

```text
P18 Engineering / Optimization
```

P18 must consume the exact materialized P17 head and preserve:

- persistent service outside conversation state;
- Aegis Plugin + Control App non-owner split;
- Control API / worker process-capability separation;
- transactional store + canonical outbox;
- versioned HTTPS JSON contracts;
- explicit P13 operation API/no generic PATCH;
- source snapshot token representation/freshness validation;
- webhook-as-wakeup + query-as-reconciliation;
- least-authority credential propagation;
- ChatGPT interactive vs programmatic capability distinction;
- Codex P32/P33 package/anchor/cursor/materialization boundary;
- GitHub exact-ref behavior;
- CI != Gate;
- Proof Plane/P34 external ownership;
- durable human-decision materialization;
- operational pause/backpressure separation;
- Current cross-Primary rollout gate.

If performance optimization would require breaking one of these boundaries, the problem must route back to P17/P16/P15 rather than silently introducing a platform shortcut.

Do not begin P20/P30/P32 from P17.

---

# 35. P17 disposition

```text
P17 Platform Contract
  -> READY / MATERIALIZED — Draft/Proposed
```

Authority chain:

```text
P10-P13 modeling
  @ f29c4da3698038e0174e4380707fa618b03c40b2
  -> P21 #3 PASS / ACCEPTED_FOR_DOWNSTREAM

P14 System Architecture
  @ 54999ce91ff4f35455916c33b4f7891e2b6b8d4d

P15 Module Design
  @ 12f75bc1938406d8d0cadca4d343fcdb95fdbfb9

P16 Runtime Data Flow
  @ 56f7df8aab30a2720b9b180eea0237eae689f291

P17 Platform Contract
  -> this artifact
```

The next architecture-family stage is P18 Engineering / Optimization, but P17 stops at this durable boundary and does not execute P18 automatically.
