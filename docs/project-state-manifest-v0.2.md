# Aegis Project State Manifest + Authority Dependency Graph v0.2

Status: **Current Replacement Authority v0.2 — P34 PASS_WITH_FINDINGS; integrated in `main`.**

This document is the repository companion to Notion `07 v0.2 Aegis Project State Authority Repair — Gate Propagation + Integration Lifecycle Closure` and supersedes `docs/project-state-manifest-v0.1.md`.

## Authority basis

v0.2 is driven only by two confirmed self-hosting findings from 08:

- **F08-01 — SPEC_DEFECT + MISSING_CONTRACT:** a current `BLOCKED_*` Gate can exist while generated state reports no blocker, no earliest untrusted layer, and no next stage.
- **F08-02 — MISSING_CONTRACT:** P34 PASS cannot currently be distinguished from repository integration; open/unmerged PRs can only be stored as opaque evidence.

07 v0.1 remains preserved as Superseded/Historical authority. v0.2 was accepted at P34 with an explicit GitHub check-suite environment finding and integrated through PR #7 at merge revision `8ca7b49d40a17e8cb7ffba86632da3aeae5e911c`.

## Repository integration reality

At v0.2 integration:

- PR #3 (06-02 provider tooling) is **integrated** into `main` at `d55686123bd22254c196f8232c8b115f469bde1e`; the live provider baseline remains separately `BLOCKED_ENVIRONMENT` because no OpenAI API credential is available.
- PR #4 (07 v0.1) is **integrated** into `main` at `555bac21d485fc4530680c61719fc36831021b0d`.
- PR #6 is **closed/unmerged** historical `ENVIRONMENT_DEFECT` / check-suite evidence.
- PR #7 (07 v0.2) is **integrated** into `main` at `8ca7b49d40a17e8cb7ffba86632da3aeae5e911c`.

Authority acceptance, Gate verdict/validity, repository integration, and external behavioral evidence are separate state dimensions.

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

Minimal integrated record:

```json
{
  "id": "int-pr7",
  "kind": "pull_request",
  "ref": "https://github.com/Mostorm-Labs/aegis/pull/7",
  "gate_id": "gate-project-state-v02-pr7",
  "status": "integrated",
  "target_ref": "main",
  "evidence_ids": ["ev-pr7-merged"],
  "integrated_revision": "8ca7b49d40a17e8cb7ffba86632da3aeae5e911c"
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

Do not overwrite `schemas/project-state/v0.1/`. v0.2 uses `schemas/project-state/v0.2/`; v0.1 remains preserved as history.

A v0.2 project has five authored control manifests plus generated state:

```text
.aegis/project.json
.aegis/authorities.json
.aegis/gates.json
.aegis/evidence.json
.aegis/integrations.json
.aegis/state.json   # generated
```

## Accepted P34 evidence

The initial PR #6 accumulated cancelled/startup-failure workflow records, later followed by valid main-based PR-context runs. Accepted core merge-ref evidence is run `33021019280`, job `98351117474`, which checked out `refs/pull/6/merge` and produced:

```text
schema parse = PASS
VALID
STATE_OK
Ran 34 tests in 0.327s
OK
```

The replacement line was then clean-rebased onto current `main`; ancestry became ahead-only (`behind=0`) and remained exactly the 25 project-state files. The core `tools/aegis_state/compute.py` blob remained byte-identical to the merge-ref-tested core (`d6e2a21f0c32b8d3c71f973d230d1118a397508b`). Final-head run `33021291693`, job `98352018093`, produced:

```text
schema parse = PASS
VALID
STATE_OK
Ran 34 tests in 0.221s
OK
```

GitHub did not emit a fresh `pull_request` run for replacement PR #7 despite a valid merge ref. P34 therefore used an explicit P20 compound-evidence fallback and returned **PASS_WITH_FINDINGS**. The finding is classified as check-suite `ENVIRONMENT_DEFECT`, not implementation defect; no nonexistent run is treated as evidence.

## Downstream verification handoff

08 Self-Hosting must now be formally rerun on v0.2. The expected semantic oracle is not an all-clean project: the real OpenAI behavioral baseline remains `BLOCKED_ENVIRONMENT`, so correct v0.2 derived state should surface that Gate as the primary `verification / P34` blocker while representing integrated repository changes accurately.
