# Project State v0.6 Root Persistence — P31 Targeted Repair Amendment

Package ID: `PS-V06-P31-02`

Amendment ID: `PS-V06-P31-02-R1`

Stage: `P31 Task Packaging`

Owner: `aegis-implementation`

Repository: `Mostorm-Labs/aegis`

Task anchor: `cfb69ee10dee03e34b363820cd66136a127658cc` (`ancestor`)

Prior package ref: `3b6da50c2e0b71d8c28455dabfebf036ae1137e2`

Blocked P32 result: `800d6c21e751201a89ed8ce15dd1e4bea24ac775`

Hosted Project State run: `34018005000`

## Purpose

Repair two implementation-package contradictions discovered only after the authorized root v0.5 -> v0.6 persistence was materialized and exact-SHA hosted CI executed. This amendment does not change Project State Authority semantics, the persisted v0.6 data model, PR #81 history, or the PR #82 hard stop.

## Root-cause findings

### R1-F1 — migration tests incorrectly bind their v0.5 source to repository root

Two tests call `migrate_v05_to_v06(load_manifests(ROOT))`:

- `tests/project_state/test_v06_binding.py::test_v05_migration_is_lossless_bound_and_never_infers_absent`
- `tests/project_state/test_v06_p20_evidence.py::test_v7_migration_zero_inferred_absent`

That assumption was valid only while root `.aegis` remained v0.5. Once `PS-V06-P31-02` correctly persists root schema v0.6, both tests deterministically fail with `ValueError: v0.6 migration requires schema_version 0.5` even though root validation, generated-state checking, and v0.5 -> v0.6 transition checking pass.

The repair must preserve the migration contract and move the test input to the repository's canonical v0.5 fixture. The migrator itself must not be weakened to accept v0.6 input.

### R1-F2 — required independent hosted workflows cannot be triggered by `.aegis/**`

The original package requires exact-SHA hosted Project State, Skillset, and Verification Productization CI, but the Skillset and Verification Productization workflows do not include `.aegis/**` in their `pull_request` / `push` path filters. A compliant root-only persistence change therefore cannot produce those two independent runs.

The repair adds `.aegis/**` to both workflows' `pull_request` and `push` path filters. It does not otherwise change workflow behavior.

## Additional authorized implementation files

This amendment authorizes exactly four additional files for the targeted repair:

```text
tests/project_state/test_v06_binding.py
tests/project_state/test_v06_p20_evidence.py
.github/workflows/skillset.yml
.github/workflows/verification-productization-ecv0.yml
```

Together with the six already-materialized root `.aegis` files, these are the only implementation surfaces authorized by `PS-V06-P31-02-R1`.

## Required repair

1. In `tests/project_state/test_v06_binding.py`, change only the v0.5 migration source used by `test_v05_migration_is_lossless_bound_and_never_infers_absent` from repository `ROOT` to `ROOT / "examples/project-state/v0.5-minimal"`.
2. In `tests/project_state/test_v06_p20_evidence.py`, change only the v0.5 migration source used by `test_v7_migration_zero_inferred_absent` from repository `ROOT` to `ROOT / "examples/project-state/v0.5-minimal"`.
3. In `.github/workflows/skillset.yml`, add `.aegis/**` to both `push.paths` and `pull_request.paths`.
4. In `.github/workflows/verification-productization-ecv0.yml`, add `.aegis/**` to both `push.paths` and `pull_request.paths`.
5. Do not alter `migrate_v05_to_v06`, schema/model semantics, fixtures, production code, generated Skill bytes, release files, or root persistence records merely to satisfy tests.

## Precedence over the original package

For this targeted retry only, this amendment supersedes the original statements that:

- no test/workflow files may change;
- no files outside the six root `.aegis` files may change.

All other original package requirements and non-goals remain in force, including:

- root schema remains exactly v0.6;
- every legacy v0.5 Integration remains mechanically migrated to `Bound`;
- inferred `Absent` remains zero;
- `int-pr81` remains Bound to its pre-occurrence P24 PASS decision;
- `int-pr82` must not be created;
- no synthetic PR #82 Gate Decision;
- no merge of PR #87;
- no release or rollout expansion;
- no self-declared P34 PASS.

## Verification / exit criteria

The repaired exact result must satisfy all of the following:

```text
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli check .
python3 -m unittest discover -s tests/project_state -v
python3 -m tools.aegis_skillset.cli validate .
python3 scripts/build_skillset.py --check
python3 -m unittest discover -s tests/skillset -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
```

Hosted exact-SHA evidence must include terminal success for:

- Aegis Project State Integrity;
- Aegis Skillset Integrity;
- Aegis Verification Productization ECV0.

The Project State run must include a full successful Project State test suite on the persisted v0.6 root. The two independent workflows must be triggered by the repaired path filters rather than being inferred from another workflow.

`READY_FOR_P34` remains only a P32 execution return and never constitutes Gate PASS.
