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

## OpenAI hosted Aegis baseline v0.1

`evals/providers/openai/` implements the first real-provider baseline path while preserving the accepted provider-neutral `CommandAdapter` boundary.

The baseline identity is:

```text
provider          = openai
endpoint          = /v1/responses
model             = gpt-5.6-sol
reasoning_effort  = medium
skill transport   = uploaded Agent Skill + pinned skill_id/version
shell             = hosted container_auto
```

The baseline runner creates a deterministic zip from `skills/aegis/`, uploads it once, pins the returned skill version, then executes the current corpus through the existing evaluator:

```bash
OPENAI_API_KEY=... python3 evals/scripts/run_openai_baseline.py \
  --output artifacts/aegis-v0.1-openai-gpt-5.6-sol
```

Do not commit API credentials. If `OPENAI_API_KEY` is absent or the API returns 401/403, the runner exits with `BLOCKED_ENVIRONMENT` instead of fabricating a baseline.

### Golden leakage boundary

The existing `CommandAdapter` supplies the full case to the external driver, but the OpenAI driver projects it before any provider request. The provider-visible scenario contains only:

```text
case_id
input.prompt -> prompt
input.context -> context
```

`expected`, category, severity, origin, title, tags, thresholds, scores, and answer-bearing metadata must never be sent to the model. Regression tests use sentinel values to enforce this boundary.

### Provider evidence

A complete live run stores provider evidence separately from normalized scorer artifacts:

```text
<output>/
├── provider/
│   ├── aegis-skill.zip
│   └── skill-reference.json
├── provider-evidence/
│   └── <case-id>.json
├── raw/<case-id>.txt
├── normalized/<case-id>.json
├── case-scores.json
├── summary.json
├── report.md
└── baseline-manifest.json
```

`baseline-manifest.json` records source/runner git SHA, skill ID/version/bundle digest, corpus digest/count, prompt template version, response IDs, usage, latency, retries, deterministic gate result, and semantic gate status. The manifest is rejected if provider evidence is missing for any evaluated case.

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

A deterministic score does **not** grade semantic `required_findings / forbidden_findings`. Until a separately auditable semantic evidence contract exists, the full Semantic Behavioral Gate remains `BLOCKED_EVIDENCE` even when deterministic checks pass.

See:

- `docs/evaluation-and-dogfooding-v0.1.md` — Current Verification Authority
- `docs/model-execution-and-scoring-v0.1.md` — Current Evaluation Tooling
- `docs/openai-hosted-skill-baseline-v0.1.md` — proposed OpenAI baseline execution authority
- `evals/schema/result.schema.json` — canonical normalized result contract
- `evals/providers/openai/result.strict.schema.json` — strict provider projection
