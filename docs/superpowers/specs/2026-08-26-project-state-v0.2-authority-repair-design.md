# Project State v0.2 Authority Repair Design

## Context

08 self-hosting proved that v0.1 can be structurally valid while semantically false-clean. The repository can contain a current `BLOCKED_ENVIRONMENT` Gate and still generate `blocking_findings=[]`, `earliest_untrusted_layer=null`, and `recommended_next_stage=null`. It also proved that P34 PASS and repository integration are separate facts.

## Design goals

1. Propagate current `BLOCKED_*` Gate verdicts into deterministic project state.
2. Model repository integration separately from Authority and Gate state.
3. Preserve deterministic recomputation and fail-closed validation.
4. Keep Aegis as control plane; do not make it a git merge engine.
5. Preserve v0.1 schemas as historical artifacts.

## Component changes

### `tools/aegis_state/model.py`

- bump active manifest schema/generator contract to 0.2;
- load `integrations.json`;
- expose `integration_items`;
- validate integration IDs, gate/evidence references, status enum, pass/current requirements, available evidence, and `integrated_revision` requirements.

### `tools/aegis_state/compute.py`

Add deterministic Gate verdict routing:

```text
BLOCKED_AUTHORITY      -> authority/P21
BLOCKED_EVIDENCE       -> verification/P34
BLOCKED_IMPLEMENTATION -> implementation/P35
BLOCKED_ENVIRONMENT    -> verification/P34
```

Only effective-current Gates count as active verdict blockers.

Add integration computation:

- `awaiting_integration` -> derived `awaiting_integrations`;
- `integrated` -> not awaiting;
- `closed_unmerged` -> historical/non-current baseline result;
- if awaiting integration is the earliest open item, choose layer `implementation`, no P-stage, hand off to `superpowers:finishing-a-development-branch`.

All blockers participate in the existing lifecycle precedence calculation. A verification blocker outranks awaiting integration.

### `schemas/project-state/v0.2/`

Create 0.2 versions of project, authorities, gates, evidence, state schemas plus new `integrations.schema.json`. Keep v0.1 untouched.

`state.schema.json` adds:

```text
blocking_gates[]
awaiting_integrations[]
recommended_handoff
```

### Examples and self-host fixtures

Migrate the minimal example to v0.2 and add a pass-gated awaiting integration example. 08 root self-host manifests are not copied into this repair branch; they are rerun after v0.2 P34.

### Skill integration

Update `skills/aegis/references/project-state.md` to v0.2 semantics. `SKILL.md` remains a thin bootstrap and should not absorb detailed integration rules.

## Validation rules

Integration record required fields:

```text
id
kind
ref
gate_id
status
target_ref
evidence_ids[]
```

Allowed status:

```text
awaiting_integration
integrated
closed_unmerged
```

`integrated_revision` is required iff status is `integrated`.

For `awaiting_integration` and `integrated`:

- referenced Gate verdict must be `PASS` or `PASS_WITH_FINDINGS`;
- Gate declared/effective validity must be current;
- referenced evidence must be available;
- `integrated` additionally requires a non-empty revision.

A blocked/stale Gate cannot support repository integration.

## Derived-state rules

`blocking_gates` contains active current-valid `BLOCKED_*` Gate IDs.

Each active blocked Gate emits one stable finding:

```text
gate <id> is currently <verdict>
```

Awaiting integration emits:

```text
integration <id> is awaiting integration into <target_ref> after Gate PASS
```

Primary route is selected from all authority validity, Gate validity, Gate verdict, and integration candidates using lifecycle precedence.

If the primary candidate is awaiting integration:

```text
earliest_untrusted_layer = implementation
recommended_next_stage = null
recommended_handoff = superpowers:finishing-a-development-branch
```

If the primary candidate is a blocked Gate, use the fixed mapping above and leave `recommended_handoff=null` unless a later design explicitly defines one.

## Error handling

- malformed/missing `integrations.json` in a 0.2 project -> manifest error;
- dangling gate/evidence reference -> validation error;
- awaiting/integrated record backed by blocked/stale Gate -> validation error;
- integrated without revision -> validation error;
- missing/unavailable integration evidence -> validation error;
- state cache mismatch -> existing `STATE_DRIFT` behavior.

## Testing strategy

Use TDD. Add failing tests before implementation for every rule listed in the authority. Re-run the complete existing 16-test project-state suite plus new tests. Add an end-to-end v0.2 example `validate -> recompute --write -> check` workflow. Update CI to run the v0.2 example.

The two original dogfood cases `defect-008` and `defect-009` remain in the evaluation corpus; the project-state tests provide executable regression proof for their concrete semantics.

## Supersession and integration

This branch starts from PR #4 head because it repairs the unmerged v0.1 implementation. After P34:

1. mark v0.2 as Current Replacement Authority;
2. mark 07 v0.1 Superseded, preserving links/reason;
3. decide integration strategy for PR #4 (close/replace or merge lineage) without losing history;
4. retarget/replay PR #5 onto the accepted v0.2 implementation;
5. rerun 08 and require semantic fidelity before PR #5 can pass.
