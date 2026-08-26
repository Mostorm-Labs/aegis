# Aegis Evals

This directory contains the machine-readable corpus for the Aegis Evaluation & Dogfooding Framework v0.1.

## Protected seed corpus

- `cases/routing.json`: routing seed cases 001-010
- `cases/authority.json`: authority seed cases 001-008
- `cases/defect.json`: defect seed cases 001-006
- `cases/gate.json`: gate seed cases 001-006

Protected seed total: **30 cases**.

The seed total is not a corpus-size ceiling. New real failures are added with `origin: dogfood` or `origin: incident` and must not replace protected seed cases.

Current first dogfood regression:

- `cases/dogfood.json`: `defect-007` — protects extensible corpus growth.

## What corpus CI proves

The validator proves corpus integrity only: JSON shape, required fields, stable/unique IDs, enum values, category-specific expectations, and continued presence of all 30 protected seed IDs.

It explicitly allows additional dogfood/incident cases.

It does **not** prove Aegis behavioral quality. Behavioral execution, normalization, deterministic scoring, and semantic evidence are separate layers.

## Case lifecycle

1. Add or update a case only when Current Aegis Authority supports the expected result.
2. For a real Aegis failure, add the failing scenario before changing the skill whenever practical.
3. Mark real failures with `origin: dogfood` or `origin: incident`.
4. Never delete a failing case only to make a change pass.
5. Never delete a protected seed case to keep a fixed total.
6. If authority changes, revise/supersede affected expectations with explicit rationale.
7. Preserve behavior assertions rather than exact prose whenever possible.

## Validate locally

```bash
python3 evals/scripts/validate_corpus.py
```

A successful run reports the full current count plus protected-seed integrity and exits with code 0.

## Normalized execution contract

Execution adapters must retain raw Aegis output and normalize it to fields including:

- `case_id`
- `status`
- `earliest_untrusted_layer`
- `start_stage`
- `route`
- `authority_classification`
- `defect_classification`
- `gate_verdict`
- `findings`
- `evidence_requirements`

Canonical statuses follow `skills/aegis/SKILL.md`; compatibility aliases such as `READY_TO_ROUTE` normalize to canonical `READY` before scoring.

See `docs/evaluation-and-dogfooding-v0.1.md` for the verification authority.
