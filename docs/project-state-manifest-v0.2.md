# Aegis Project State Manifest + Authority Dependency Graph v0.2

Status: **Proposed Replacement Authority v0.2**

This document is the repository companion to Notion `07 v0.2 Aegis Project State Authority Repair — Gate Propagation + Integration Lifecycle Closure`.

## Authority basis

v0.2 is driven only by two confirmed self-hosting findings from 08:

- **F08-01 — SPEC_DEFECT + MISSING_CONTRACT:** a current `BLOCKED_*` Gate can exist while generated state reports no blocker, no earliest untrusted layer, and no next stage.
- **F08-02 — MISSING_CONTRACT:** P34 PASS cannot currently be distinguished from repository integration; open/unmerged PRs can only be stored as opaque evidence.

v0.1 remains historical/current accepted design until v0.2 completes P34. Do not silently mutate the meaning of v0.1 schemas.

## Scope

Close only:

1. current blocked Gate verdict -> derived blocker/routing semantics;
2. repository integration lifecycle as a separate authored manifest;
3. derived handoff for accepted-but-not-integrated implementation.

Do not redesign authority DAGs, evidence status, supersession invalidation, P00-P36, or Gate verdict vocabulary.

## Gate verdict propagation

Only Gates with effective validity `current` contribute active verdict blockers.

| Verdict | Earliest layer | Recommended stage |
| --- | --- | --- |
| `BLOCKED_AUTHORITY` | `authority` | `P21` |
| `BLOCKED_EVIDENCE` | `verification` | `P34` |
| `BLOCKED_IMPLEMENTATION` | `implementation` | `P35` |
| `BLOCKED_ENVIRONMENT` | `verification` | `P34` |
| `PASS` | none | none |
| `PASS_WITH_FINDINGS` | none | none |

A stale/needs-review Gate is handled by validity semantics, not resurrected as a current blocker from its historical verdict.

Generated state adds `blocking_gates[]` and includes stable blocker findings.

## Integration manifest

v0.2 adds authored `.aegis/integrations.json`.

Minimal record:

```json
{
  "id": "int-pr4",
  "kind": "pull_request",
  "ref": "https://github.com/Mostorm-Labs/aegis/pull/4",
  "gate_id": "gate-project-state-pr4",
  "status": "awaiting_integration",
  "target_ref": "main",
  "evidence_ids": ["ev-pr4-open"]
}
```

Allowed statuses:

- `awaiting_integration`
- `integrated`
- `closed_unmerged`

`integrated` additionally requires `integrated_revision`.

## Integration invariants

- IDs are unique.
- `gate_id` resolves to a Gate.
- `evidence_ids` resolve to Evidence.
- `awaiting_integration` requires a current-valid `PASS` or `PASS_WITH_FINDINGS` Gate.
- `integrated` requires a current-valid pass Gate, a non-empty `integrated_revision`, and available integration evidence.
- blocked/stale Gates cannot be represented as integrated.
- `closed_unmerged` never advances the current repository baseline.
- Authority status, Gate verdict, and Integration status remain separate facts.

Aegis records and routes integration state. It does not own the git merge/rebase action.

## Derived integration state

Generated `state.json` v0.2 adds:

```text
blocking_gates[]
awaiting_integrations[]
recommended_handoff
```

If no earlier Authority/Gate blocker exists but an integration is awaiting:

```text
earliest_untrusted_layer = implementation
recommended_next_stage = null
recommended_handoff = superpowers:finishing-a-development-branch
```

The finding must say the Gate passed but implementation is not yet in the target baseline.

If a verification blocker such as `BLOCKED_ENVIRONMENT` and an awaiting integration coexist, lifecycle precedence selects `verification / P34` as primary while preserving the integration finding.

## Versioning

Do not overwrite `schemas/project-state/v0.1/`. Add `schemas/project-state/v0.2/`.

A v0.2 project has five authored control manifests plus generated state:

```text
.aegis/project.json
.aegis/authorities.json
.aegis/gates.json
.aegis/evidence.json
.aegis/integrations.json
.aegis/state.json   # generated
```

The implementation may migrate the repository examples/self-host fixtures to 0.2, but v0.1 files remain preserved as history.

## Required regression evidence

At minimum prove:

1. current `BLOCKED_ENVIRONMENT` -> `blocking_gates` + `verification/P34`;
2. current `BLOCKED_AUTHORITY` -> `authority/P21`;
3. current `BLOCKED_IMPLEMENTATION` -> `implementation/P35`;
4. current `BLOCKED_EVIDENCE` -> `verification/P34`;
5. current `PASS_WITH_FINDINGS` does not block;
6. stale blocked Gate is not an active verdict blocker;
7. awaiting integration requires current-valid pass Gate;
8. integrated requires `integrated_revision` and available evidence;
9. awaiting integration routes to implementation handoff when it is the earliest open item;
10. integrated items do not remain awaiting;
11. earlier blocked Gate wins primary route over awaiting integration;
12. manifest digest includes integration state.

## Acceptance boundary

v0.2 does not supersede v0.1 merely because unit tests pass. Acceptance requires:

- v0.2 schema/validator/state tests PASS;
- PR-context CI PASS;
- Aegis Skill project-state reference updated and repackaged;
- 08 self-hosting rerun shows the real `BLOCKED_ENVIRONMENT` Gate in derived state;
- PR #3/#4 integration records remain `awaiting_integration` until repository reality changes.
