# Aegis Evals

This directory contains the machine-readable corpus and provider-neutral evaluation tooling for Aegis.

## Protected seed corpus

- `cases/routing.json`: routing seed cases 001-010
- `cases/authority.json`: authority seed cases 001-008
- `cases/defect.json`: defect seed cases 001-006
- `cases/gate.json`: gate seed cases 001-006

Protected seed total: **30 cases**.

The seed total is not a corpus-size ceiling. New real failures are added with `origin: dogfood` or `origin: incident` and must not replace protected seed cases.

Current first dogfood regression:

- `cases/dogfood.json`: `defect-007` — protects extensible corpus growth.

## Corpus integrity

Validate locally:

```bash
python3 evals/scripts/validate_corpus.py
```

The validator proves JSON/case-contract integrity and continued presence of all protected seed IDs. It allows additional dogfood/incident cases.

## Evaluation tooling v0.1

The provider-neutral pipeline is:

```text
Case -> Execution Adapter -> Raw Output -> Normalizer -> Deterministic Scorer -> Evidence Report
```

Run unit tests:

```bash
python3 -m unittest discover -s evals/tests -v
```

Replay recorded outputs:

```bash
python3 evals/scripts/run_eval.py \
  --adapter recorded \
  --results path/to/results.json \
  --output artifacts/aegis-eval
```

Use an external model/skill driver:

```bash
python3 evals/scripts/run_eval.py \
  --adapter command \
  --command "python3 path/to/provider_driver.py" \
  --output artifacts/aegis-eval
```

The command reads one full case JSON from stdin and writes direct JSON or one fenced JSON result to stdout.

## Evidence boundary

The runner preserves:

```text
raw/<case-id>.txt
normalized/<case-id>.json
case-scores.json
summary.json
report.md
```

Canonical statuses follow `skills/aegis/SKILL.md`; compatibility aliases such as `READY_TO_ROUTE` normalize to canonical `READY` before scoring.

A deterministic score does **not** grade semantic `required_findings / forbidden_findings`. Until a separately auditable semantic evidence contract exists, the full Behavioral Gate remains `BLOCKED_EVIDENCE` even when deterministic checks pass.

See:

- `docs/evaluation-and-dogfooding-v0.1.md` — Current Verification Authority
- `docs/model-execution-and-scoring-v0.1.md` — proposed evaluation tooling design
- `evals/schema/result.schema.json` — normalized result contract
