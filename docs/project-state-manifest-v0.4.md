# Aegis Project State Out-of-Gate Integration Semantics v0.4

Status: **P34 PASS — Approved Replacement Authority candidate v0.4; P23 supersession and repository integration pending.**

This document repairs F09-06, discovered when PR #9 was physically merged while its recorded Gate remained `BLOCKED_EVIDENCE`. v0.3 preserves historical integration occurrence only when a PASS/PASS_WITH_FINDINGS Gate exists, so it cannot truthfully represent a real repository merge that violated Gate policy.

v0.4 does **not** reinterpret the PR #9 Gate, manufacture missing behavioral evidence, or convert the merge into a conforming event. It separates occurrence from Gate conformance.

## F09-06 classification

```text
Finding                  = F09-06
Primary                  = MISSING_CONTRACT
Secondary                = AUTHORITY_CONFLICT
Earliest Untrusted Layer = Authority
Start Stage              = P21
Review                    = P22
Repair                    = Project State replacement Authority v0.4
```

## Core invariant

```text
Integration Occurrence
!=
Gate Conformance
!=
Current Applicability
!=
Current Actionability
```

Repository truth answers whether an integration happened. Gate conformance answers whether that occurrence was authorized by the Gate verdict that governed it. Applicability answers whether the occurrence still applies to the current baseline. Actionability answers what Aegis should do now.

A real integration occurrence must never be erased or falsified merely because it violated Gate policy.

## Integration occurrence

The existing statuses remain unchanged:

```text
awaiting_integration
integrated
closed_unmerged
```

`integrated` means repository evidence proves that the change entered the target baseline and `integrated_revision` identifies that occurrence.

v0.4 changes one v0.3 rule: an `integrated` occurrence no longer requires the referenced Gate verdict to be PASS/PASS_WITH_FINDINGS. A blocked Gate may support the *provenance link* for an actual integration occurrence, but it does not authorize it.

Available occurrence evidence remains mandatory.

`awaiting_integration` remains unchanged and still requires a current-effective PASS/PASS_WITH_FINDINGS Gate. Aegis must never recommend a future integration from a blocked Gate.

## Derived Gate conformance

Gate conformance is derived, not authored:

```text
Gate verdict PASS / PASS_WITH_FINDINGS
    -> conforming

Gate verdict BLOCKED_*
    -> nonconforming
```

The generated state exposes:

```json
{
  "integration_conformance": [
    {"integration_id":"int-pr9","conformance":"nonconforming"}
  ],
  "nonconforming_integrations": ["int-pr9"]
}
```

Only `integrated` occurrences appear in these projections. `closed_unmerged` has no integration occurrence to classify.

Conformance is historical truth tied to the referenced Gate verdict. Later Authority supersession may make the Gate and Integration historical, but it does not rewrite a nonconforming occurrence into a conforming one.

## Applicability and actionability

Existing v0.3 applicability values remain:

```text
current
needs_review
stale
historical
```

Conformance does not replace applicability. A nonconforming integration may be `current` because the merged code is in the active baseline while its Gate remains blocked.

For still-current/Proposed Authority, an active blocked Gate remains actionable under existing Gate routing semantics. The nonconforming integration adds an explicit finding but does not create a second competing route when the Gate already supplies the correct route.

When all validity-bearing Authority becomes historical, the integration occurrence and its conformance remain audit history and do not reactivate a current blocker solely from provenance.

## PR #9 reconciliation

v0.4 permits the root Project State to record the facts without changing their meaning:

```text
int-pr9.status              = integrated
int-pr9.integrated_revision = a0c6b0103b119f517c7adf9ec4a90b5963e5e1e3
Gate verdict                = BLOCKED_EVIDENCE
Derived conformance         = nonconforming
Authority v0.2              = Proposed
Current route               = verification / P34
```

The PR #9 merge is occurrence evidence only. It is not behavioral acceptance evidence and must not be added to the Gate evidence set as proof of PASS.

## Versioning

v0.4 is a replacement Project State semantic contract and introduces a new schema/generator version:

```text
schemas/project-state/v0.4/
SCHEMA_VERSION = "0.4"
GENERATOR_VERSION = "0.4"
```

The updated tooling continues to validate historical v0.3 projects under v0.3 semantics. In particular, a v0.3 `integrated` record backed by a blocked Gate remains invalid; only v0.4 opts into the repaired semantics.

## Acceptance

P34 acceptance requires deterministic evidence proving:

1. v0.4 accepts an `integrated` occurrence backed by a blocked Gate when revision and occurrence evidence are available;
2. that occurrence is derived as `nonconforming` and appears in `nonconforming_integrations[]`;
3. the blocked Gate remains in `blocking_gates[]` and routing remains `verification / P34`;
4. a PASS-backed v0.4 integration is `conforming`;
5. `awaiting_integration` still rejects blocked/non-current Gates;
6. v0.3 historical validation behavior remains unchanged;
7. v0.4 schemas parse and both minimal/self-host generated state checks pass;
8. root `.aegis` records PR #9 integration occurrence without promoting its Gate or Authority;
9. existing Project State and Aegis regressions remain green.

## P34 evidence — PASS

Fresh merge-ref evidence on head `08e71fe1391d700bbf0ab85995c706cdd9475555` satisfies all nine acceptance items:

- **Aegis Project State Integrity** run `33163536074`: PASS. v0.3/v0.4 schemas parse, minimal v0.4 manifests validate, minimal generated state matches, Project State unit regressions pass, root v0.4 self-host validation/check passes, and the Aegis evaluation corpus remains valid.
- **Aegis Skillset Integrity** run `33163536133`: PASS. Canonical/generated Skill distributions match and the broader Skillset, Project State, routing, installed-platform-state, and evaluation regressions remain green.
- The RED oracle was independently observed in run `33162821606` before production semantics existed; only the two expected v0.4 cases failed while the pre-existing Project State regression set remained green.

P34 verdict:

```text
Project State v0.4 semantic contract     PASS
Out-of-Gate integration representation  PASS
v0.3 backward compatibility             PASS
PR #9 truthful occurrence persistence   PASS
Gate preservation / no fake PASS        PASS
Skill instruction/distribution parity   PASS
Overall F09-06 repair                    PASS
```

P23 supersession remains a separate step. v0.3 remains Current and v0.4 remains Proposed until that transition is explicitly persisted.

## Non-goals

v0.4 does not automatically revert an out-of-Gate merge, change GitHub branch protection, modify Gate verdict taxonomy, promote PR #9 Authority, infer missing behavioral evidence, or authorize PR #10 merely because its repository dependency was merged.