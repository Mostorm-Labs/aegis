# Aegis Evals

This directory is the machine-readable seed of the Aegis Evaluation & Dogfooding Framework v0.1.

## Seed corpus

- `cases/routing.json`: 10 routing cases
- `cases/authority.json`: 8 authority cases
- `cases/defect.json`: 6 defect cases
- `cases/gate.json`: 6 gate cases

Total: 30 cases.

## What v0.1 proves

The checked-in validator proves corpus integrity only: JSON shape, required fields, stable IDs, enum values, category counts, and category-specific expectations.

It does **not** run Aegis or score model behavior. Behavioral execution is the next layer.

## Case lifecycle

1. Add or update a case only when current Aegis authority supports the expected result.
2. For a real Aegis failure, add the failing scenario before changing the skill whenever practical.
3. Mark real failures with `origin: dogfood` or `origin: incident`.
4. Never delete a failing case only to make a change pass. If authority changes, supersede or revise the case with explicit rationale.
5. Preserve behavior assertions rather than exact prose whenever possible.

## Validate locally

```bash
python3 evals/scripts/validate_corpus.py
```

A successful run prints the category counts and exits with code 0.

## Future execution contract

A future model runner should retain raw Aegis output and normalize it to a result object with fields such as:

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

Exact fields are described in `docs/evaluation-and-dogfooding-v0.1.md`.
