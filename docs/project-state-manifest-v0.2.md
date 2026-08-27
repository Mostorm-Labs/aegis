# Aegis Project State Manifest + Authority Dependency Graph v0.2

Status: **Superseded / Historical v0.2.**

This document is the repository companion to Notion `07 v0.2 Aegis Project State Authority Repair — Gate Propagation + Integration Lifecycle Closure`. It superseded `docs/project-state-manifest-v0.1.md` and is now itself superseded by `docs/project-state-manifest-v0.3.md`.

Supersession reason: the formal 08 self-host rerun confirmed **F08-03 — SPEC_DEFECT + MISSING_CONTRACT**. v0.2 required an `integrated` repository occurrence to retain a current/current-valid PASS Gate forever, so a truthful historical integration could become impossible to represent after its supporting Authority was correctly superseded. v0.3 separates Historical Occurrence, Current Applicability, and Current Actionability and was accepted at P34, then integrated through PR #8 at `be385b3549900ba5bc34170dbfa8b4e583631a1d`.

The v0.2 conclusions and evidence below remain historical record and continue to explain F08-01/F08-02 closure. They are no longer Current execution/design authority.

## Authority basis

v0.2 was driven only by two confirmed self-hosting findings from 08:

- **F08-01 — SPEC_DEFECT + MISSING_CONTRACT:** a current `BLOCKED_*` Gate could exist while generated state reported no blocker, no earliest untrusted layer, and no next stage.
- **F08-02 — MISSING_CONTRACT:** P34 PASS could not be distinguished from repository integration; open/unmerged PRs could only be stored as opaque evidence.

07 v0.1 remains preserved as Superseded/Historical authority. v0.2 was accepted at P34 with an explicit GitHub check-suite environment finding and integrated through PR #7 at merge revision `8ca7b49d40a17e8cb7ffba86632da3aeae5e911c`.

## Repository integration reality at v0.2

- PR #3 (06-02 provider tooling) was integrated into `main` at `d55686123bd22254c196f8232c8b115f469bde1e`; the live provider baseline remains separately `BLOCKED_ENVIRONMENT` because no OpenAI API credential is available.
- PR #4 (07 v0.1) was integrated into `main` at `555bac21d485fc4530680c61719fc36831021b0d`.
- PR #6 is closed/unmerged historical `ENVIRONMENT_DEFECT` / check-suite evidence.
- PR #7 (07 v0.2) was integrated into `main` at `8ca7b49d40a17e8cb7ffba86632da3aeae5e911c`.

Authority acceptance, Gate verdict/validity, repository integration, and external behavioral evidence are separate state dimensions.

## Scope

v0.2 closed only:

1. current blocked Gate verdict -> derived blocker/routing semantics;
2. repository integration lifecycle as a separate authored manifest;
3. derived handoff for accepted-but-not-integrated implementation.

It did not redesign authority DAGs, evidence status, supersession invalidation, P00-P36, or Gate verdict vocabulary.

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

Generated state added `blocking_gates[]` and stable blocker findings.

## Integration manifest

v0.2 added authored `.aegis/integrations.json`.

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

`integrated` additionally required `integrated_revision`.

## Historical v0.2 integration invariants

v0.2 required:

- unique Integration IDs;
- resolvable Gate/Evidence references;
- `awaiting_integration` to depend on a current-valid `PASS` / `PASS_WITH_FINDINGS` Gate;
- `integrated` to depend on a current-valid pass Gate, non-empty `integrated_revision`, and available evidence;
- blocked/stale Gates not to be represented as integrated;
- `closed_unmerged` not to advance current repository baseline;
- Authority status, Gate verdict, and Integration status to remain separate facts.

The bolded defect later discovered in F08-03 was the requirement that a completed `integrated` occurrence continue to have a current-valid Gate. v0.3 replaces that semantic rule; this historical document does not.

## Derived integration state

Generated `state.json` v0.2 added:

```text
blocking_gates[]
awaiting_integrations[]
recommended_handoff
```

If no earlier Authority/Gate blocker existed but an integration was awaiting:

```text
earliest_untrusted_layer = implementation
recommended_next_stage = null
recommended_handoff = superpowers:finishing-a-development-branch
```

If a verification blocker such as `BLOCKED_ENVIRONMENT` and an awaiting integration coexisted, lifecycle precedence selected `verification / P34` as primary while preserving the integration finding.

## Versioning

v0.2 used `schemas/project-state/v0.2/`; v0.1 remained preserved as history. v0.3 now uses its own `schemas/project-state/v0.3/` and v0.2 schema files remain immutable historical contract artifacts.

## Accepted P34 evidence

The initial PR #6 accumulated cancelled/startup-failure workflow records, later followed by valid main-based PR-context runs. Accepted core merge-ref evidence was run `33021019280`, job `98351117474`, which checked out `refs/pull/6/merge` and produced:

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

GitHub did not emit a fresh `pull_request` run for replacement PR #7 despite a valid merge ref. P34 therefore used an explicit P20 compound-evidence fallback and returned **PASS_WITH_FINDINGS**. The finding was classified as check-suite `ENVIRONMENT_DEFECT`, not implementation defect.

## Supersession handoff

The downstream 08 Self-Hosting rerun on v0.2 correctly closed F08-01/F08-02 but exposed F08-03. That finding routed work back to P21/P20 and produced v0.3. Do not use this v0.2 document as Current project-state authority; follow `docs/project-state-manifest-v0.3.md`.
