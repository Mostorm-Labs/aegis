# Aegis Model Execution Adapter + Normalized Result Extractor + Deterministic Scorer v0.1

Status: Proposed Evaluation Tooling

## 1. Purpose

Implement the executable layer beneath `Aegis Evaluation & Dogfooding Framework v0.1` without hard-coding a model provider.

This closure turns the current corpus into a reproducible pipeline:

`Case -> Execution Adapter -> Raw Output -> Normalizer -> Exact Scorer -> Evidence Artifacts -> Deterministic Gate`

It does **not** claim a real Aegis behavioral baseline until a reproducible provider-specific driver actually executes Aegis against the corpus.

## 2. Authority

Upstream Current Verification Authority:

- `docs/evaluation-and-dogfooding-v0.1.md`
- `evals/schema/case.schema.json`
- `skills/aegis/SKILL.md`
- `skills/aegis/references/verification-governance.md`

The tooling must not weaken framework thresholds or reinterpret a failing golden case to make a candidate pass.

## 3. Provider-neutral execution boundary

`ExecutionAdapter.run(case) -> raw_text`

v0.1 ships two adapters:

- `RecordedAdapter`: replays previously captured raw/structured outputs for reproducible scoring and regression analysis.
- `CommandAdapter`: sends one complete case JSON object to an external process on stdin and records stdout as raw model/skill evidence.

The core scorer embeds no OpenAI, ChatGPT, Anthropic, local-model, or other provider credentials/protocols. Provider drivers connect through the command boundary.

## 4. Raw Evidence Contract

Every execution preserves raw output before normalization:

```text
<run>/raw/<case-id>.txt
```

A raw result may be direct JSON or prose containing one fenced `json` object. Unstructured prose without an extractable result object is an evaluation failure; the scorer must not guess a lifecycle decision from it.

## 5. Normalized Result Contract

Normalized results are stored at:

```text
<run>/normalized/<case-id>.json
```

Schema: `evals/schema/result.schema.json`.

Core fields:

```json
{
  "case_id": "routing-001",
  "status": "READY",
  "earliest_untrusted_layer": "problem",
  "start_stage": "P00",
  "route": ["P00"],
  "authority_classification": [],
  "defect_classification": null,
  "gate_verdict": null,
  "findings": [],
  "evidence_requirements": []
}
```

Compatibility aliasing is allowed only at this boundary. v0.1 maps `READY_TO_ROUTE -> READY`; goldens and scores stay canonical.

## 6. Deterministic scoring

Applicable exact assertions:

- status exact match;
- Earliest Untrusted Layer exact match;
- start stage exact match;
- required-stage recall;
- forbidden-stage absence;
- explicit authority classification set match;
- defect classification exact match;
- gate verdict exact match.

Per-case exact score is the mean of applicable assertions.

Severity weights:

```text
normal   = 1
high     = 2
critical = 4
```

Overall weighted exact score is the severity-weighted mean across the current corpus.

## 7. Critical safety detector

The scorer separately records failures that cannot be averaged away:

- a golden blocking state answered as non-blocking / READY;
- a blocked gate answered PASS / PASS_WITH_FINDINGS;
- a high/critical case enters a forbidden stage;
- a critical upstream authority/spec/test problem is incorrectly classified as an implementation defect.

Release thresholds remain owned by the Current Verification Authority.

## 8. Deterministic Gate vs Behavioral Gate

v0.1 deliberately prevents a false full PASS.

```text
Deterministic Gate
= structured exact assertions satisfy current thresholds

Behavioral Gate
= Deterministic Gate
  + accepted semantic required/forbidden finding evidence
```

The Semantic Judge / Manual Review Evidence Contract is not implemented in this closure. Therefore:

- deterministic failure -> `BLOCKED_IMPLEMENTATION`;
- deterministic pass -> full Behavioral Gate remains `BLOCKED_EVIDENCE`.

A CLI flag or unchecked string is not sufficient evidence to promote the Behavioral Gate.

## 9. Evidence layout

Each run emits:

```text
<output>/
├── raw/<case-id>.txt
├── normalized/<case-id>.json
├── case-scores.json
├── summary.json
└── report.md
```

`summary.json` includes overall weighted score, routing/authority/defect/gate metrics, required-stage recall, forbidden-stage rate, critical errors, deterministic gate result, and Behavioral Gate status.

## 10. CLI

Recorded evidence:

```bash
python3 evals/scripts/run_eval.py \
  --adapter recorded \
  --results path/to/recorded-results.json \
  --output artifacts/aegis-eval
```

External provider driver:

```bash
python3 evals/scripts/run_eval.py \
  --adapter command \
  --command "python3 path/to/provider_driver.py" \
  --output artifacts/aegis-eval
```

The provider driver reads one complete case JSON from stdin and writes one result object, either direct JSON or fenced JSON, to stdout.

## 11. Verification

The implementation has deterministic unit coverage for:

- direct and fenced JSON extraction;
- canonical status alias normalization;
- rejection of unstructured results;
- exact perfect-score behavior;
- false-PASS critical detection;
- forbidden-stage gate failure;
- protected-seed extensibility and missing-seed detection;
- recorded-adapter evidence artifact generation;
- missing recorded result failure;
- command-adapter stdin/stdout contract;
- refusal to promote Behavioral Gate using only a semantic PASS flag.

CI must run corpus validation and the full unit-test suite from repository root.

## 12. Baseline boundary

This closure creates the machinery to generate a behavioral baseline. It does not fabricate one.

Until a reproducible provider-specific Aegis driver is available and actually executed over the corpus:

```text
Model Execution Adapter Contract = IMPLEMENTED
Normalizer                       = IMPLEMENTED
Deterministic Scorer             = IMPLEMENTED
Pipeline Unit Evidence           = available after CI
Real Aegis v0.1 Baseline         = BLOCKED_EVIDENCE
Semantic Behavioral Evidence     = BLOCKED_EVIDENCE
```

## 13. Next closure

1. implement or connect a reproducible provider-specific Aegis driver;
2. capture raw Aegis v0.1 outputs for the full current corpus;
3. run deterministic scoring and publish the first baseline report;
4. define Semantic Judge / Manual Review Evidence Contract;
5. close semantic required/forbidden findings;
6. use future Aegis changes as before/after regression comparisons.
