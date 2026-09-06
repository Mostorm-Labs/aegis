# Aegis Project State migration guide — v0.2

Status: **documentation of the current implementation; not new migration Authority**

This guide describes how existing Aegis Project State repositories can move between the schema versions supported by the current v0.2 runtime.

The current Project State schema is `0.6`. The runtime accepts top-level Project State schema versions `0.3`, `0.4`, `0.5`, and `0.6`, but **parser/validation support is not the same as migration support**.

The implemented migration commands are deliberately narrower:

- `migrate-v05`: `0.4 -> 0.5`
- `migrate-v06`: `0.5 -> 0.6`

There is currently **no supported CLI migration path from `0.3`**. Do not infer one from the fact that the runtime can read and validate `0.3` manifests.

Implementation references:

- `tools/aegis_state/model.py`
- `tools/aegis_state/cli.py`
- `tools/aegis_state/migrate_v05.py`
- `tools/aegis_state/migrate_v06.py`
- `tools/aegis_state/transition_v05.py`
- `tools/aegis_state/transition_v06.py`

## Old Project Migration Matrix

| Source schema | Runtime read / validate | Direct CLI migration | Supported next hop | Important conditions |
| --- | --- | --- | --- | --- |
| `0.6` | Yes | None required | Current schema | Use normal `validate`, `recompute`, and `check`. `transition-check` is for `0.6 -> 0.6` lifecycle transitions, not migration. |
| `0.5` | Yes | `migrate-v06` | `0.6` | Source must be strict-valid `0.5`. Every integration must carry a non-empty `gate_decision_id`. Migration converts it to a `gate_decision_binding` of kind `bound`. It never invents `absent`. |
| `0.4` | Yes | `migrate-v05` | `0.5`, then optionally `0.6` | Source must be strict-valid `0.4`, and stored Project State must equal recomputed state. The migration materializes deterministic legacy gate-decision/evidence lineage from valid historical source data. |
| `0.3` | Yes | **None** | **No supported migration hop today** | Runtime compatibility only. Do not hand-edit schema versions, call `migrate-v05` on `0.3`, or synthesize missing later-version lineage. Treat upgrade as blocked pending a dedicated migration contract. |

## Command naming

The migration command name identifies the **destination** schema, not the source schema:

```text
migrate-v05 = migrate 0.4 -> 0.5
migrate-v06 = migrate 0.5 -> 0.6
```

There is no `migrate-v04`, `migrate-v03`, or direct `migrate-v06` path from `0.3`/`0.4`.

## Migration is out-of-place

Migration does not rewrite the source `.aegis` directory in place.

Both migration commands take a source project root and a destination project root. The destination must be fresh for Project State purposes: it must not already contain `.aegis`.

This is an intentional safety boundary. Keep the original project state available until the migrated destination has been independently validated and accepted.

## Standard migration runbook

For every supported migration:

1. Keep the source Project State unchanged and preserve a rollback copy/reference.
2. Run `validate` against the source.
3. Choose a fresh destination root that does not already contain `.aegis`.
4. Run the exact migration command supported for the source schema.
5. Run `validate` against the destination.
6. Run `recompute` against the destination and inspect the recomputed state.
7. Run `check` against the destination to confirm stored and recomputed state agree.
8. Inspect the semantic lineage that changed, especially gate decisions, integration records, and evidence records.
9. Adopt/switch to the migrated destination only after those checks are accepted.
10. Roll back by continuing to use the untouched original source state if migration acceptance fails.

Do not use `transition-check` to compare the source and destination of a schema migration. The transition validators are same-schema lifecycle validators:

```text
transition_v05: 0.5 -> 0.5 only
transition_v06: 0.6 -> 0.6 only
```

A cross-version migration has its own migration preconditions and output validation.

## `0.4 -> 0.5`

Run:

```bash
python3 -m tools.aegis_state.cli validate /path/to/project-v04
python3 -m tools.aegis_state.cli migrate-v05 /path/to/project-v04 /path/to/project-v05
python3 -m tools.aegis_state.cli validate /path/to/project-v05
python3 -m tools.aegis_state.cli recompute /path/to/project-v05
python3 -m tools.aegis_state.cli check /path/to/project-v05
```

`migrate-v05` first validates the `0.4` source and recomputes its Project State. If the stored source state cannot be preserved because it differs from recomputed state, migration fails closed rather than normalizing the inconsistency silently.

For structurally valid historical `0.4` gates, the migration creates deterministic legacy gate-decision lineage required by `0.5`, and rewrites integration/evidence structures into the `0.5` contract. Those values come from the migration's defined transformation of valid source history; they are not user-supplied guesses.

## `0.5 -> 0.6`

Run:

```bash
python3 -m tools.aegis_state.cli validate /path/to/project-v05
python3 -m tools.aegis_state.cli migrate-v06 /path/to/project-v05 /path/to/project-v06
python3 -m tools.aegis_state.cli validate /path/to/project-v06
python3 -m tools.aegis_state.cli recompute /path/to/project-v06
python3 -m tools.aegis_state.cli check /path/to/project-v06
```

The key integration change in `0.6` is explicit Gate Decision Binding.

A valid `0.5` integration such as:

```json
{
  "gate_decision_id": "decision-example"
}
```

is migrated to the `0.6` form:

```json
{
  "gate_decision_binding": {
    "kind": "bound",
    "gate_decision_id": "decision-example"
  }
}
```

`migrate-v06` requires the historical `gate_decision_id` to exist and be non-empty. It does **not** infer or synthesize an affirmative historical `absent` binding when the evidence is missing.

That distinction is important: `0.6` can represent both `bound` and affirmative historical `absent`, but migration from `0.5` only carries forward historical decisions that are actually present in the valid `0.5` source.

## `0.4 -> 0.6`

There is no direct one-command migration. Use the two supported hops and two fresh destination roots:

```bash
python3 -m tools.aegis_state.cli validate /path/to/project-v04
python3 -m tools.aegis_state.cli migrate-v05 /path/to/project-v04 /path/to/project-v05
python3 -m tools.aegis_state.cli validate /path/to/project-v05
python3 -m tools.aegis_state.cli check /path/to/project-v05

python3 -m tools.aegis_state.cli migrate-v06 /path/to/project-v05 /path/to/project-v06
python3 -m tools.aegis_state.cli validate /path/to/project-v06
python3 -m tools.aegis_state.cli recompute /path/to/project-v06
python3 -m tools.aegis_state.cli check /path/to/project-v06
```

Do not point the second migration at a destination that already contains the first migration's `.aegis`. `project-v05` is the source of the second hop; `project-v06` must be a fresh destination.

## `0.3` compatibility gap

Current behavior is intentionally described as:

```text
0.3: readable / validatable
0.3: no supported migration command
```

These two facts must not be collapsed into a claim that `0.3` has a supported upgrade path.

A safe `0.3` migration would need an explicit semantic contract for how older authority/gate/integration/evidence history maps into the later schema lineage. That contract is not supplied by the current CLI. Therefore an old `0.3` project should fail closed at the migration boundary rather than:

- changing only `schema_version` by hand;
- changing nested manifest versions by hand;
- running `migrate-v05` against an unsupported source;
- manufacturing `gate_decision_id` values;
- manufacturing `gate_decision_binding.absent` claims;
- deleting or rewriting historical evidence merely to make validation pass.

Closing this gap requires dedicated migration design/Authority, implementation, and verification. It is outside this documentation-only cleanup.

## Common migration blockers

| Blocker | Meaning / action |
| --- | --- |
| Source does not strict-validate | Repair or recover the source under its own trusted schema contract before migration. Do not let migration silently normalize invalid history. |
| `0.4` stored state differs from recomputed state | `migrate-v05` must refuse the migration because the source state cannot be preserved safely. |
| `0.5` integration lacks a non-empty `gate_decision_id` | `migrate-v06` must refuse rather than invent a `bound` or `absent` history. |
| Destination already contains `.aegis` | Choose a fresh destination. Migration is intentionally out-of-place. |
| Attempted cross-version `transition-check` | Wrong verifier. `transition-check` validates same-schema lifecycle transitions, not migrations. |
| Source schema is `0.3` | The runtime may read/validate it, but no supported migration route currently exists. Stop at the migration boundary. |

## What older projects should expect

The newer Project State contracts are stricter about preserving explicit historical lineage rather than guessing it. As a result, an old project can be readable while still being unable to migrate automatically.

That is a fail-closed compatibility behavior, not evidence that the old project is corrupted. The correct response is to identify the unsupported or inconsistent historical contract, preserve the original state, and repair or migrate only under a defined transformation.

For current projects, prefer creating and maintaining Project State directly under schema `0.6` rather than relying on future reconstruction of missing historical bindings.
