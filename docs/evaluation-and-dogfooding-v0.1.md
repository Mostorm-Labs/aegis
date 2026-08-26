# Aegis Evaluation & Dogfooding Framework v0.1

Status: Current Verification Authority

Accepted by P34 Gate Review in PR #1 and merged to `main` at `9cb251ab8f245a57b51c5e0161f86c97dfde306d`.

## 1. Purpose

Aegis v0.1 defines routing, authority, verification-first, defect, and gate behavior. This framework turns those claims into an evaluable contract.

The framework evaluates whether Aegis makes safe lifecycle decisions, not whether its prose matches a reference answer.

## 2. Scope

v0.1 defines:

1. a machine-readable case contract;
2. a normalized result contract;
3. a protected 30-case seed corpus;
4. an extensible dogfood / incident regression corpus;
5. deterministic scoring and candidate gate rules;
6. a dogfooding-to-regression workflow;
7. a deterministic corpus validator;
8. CI that validates corpus integrity.

The 30-case number is the protected seed baseline, not a permanent corpus ceiling. New `dogfood` and `incident` cases are expected to grow the corpus.

## 3. Source of Truth

Evaluation decisions inherit Aegis v0.1 authority:

- `skills/aegis/SKILL.md` — control-plane behavior contract;
- `skills/aegis/references/stage-contracts.md` — stage outputs and exits;
- `skills/aegis/references/verification-governance.md` — evidence, drift, defect, and gate vocabulary;
- this document — Current Verification Authority for evaluating Aegis itself.

If the corpus conflicts with Current Aegis Authority, the corpus is wrong until the authority is explicitly revised or superseded.

## 4. Core Evaluation Model

`Input -> Expected lifecycle decision -> Aegis raw result -> Normalized result -> Assertions -> Score -> Gate`

Evaluate at minimum:

- routing correctness;
- Earliest Untrusted Layer correctness;
- authority classification;
- required-stage recall;
- forbidden-stage avoidance;
- defect classification;
- evidence requirement recall;
- gate verdict correctness;
- ceremony control;
- critical safety error count.

## 5. Critical Safety Errors

Any of the following is a critical failure:

1. `PASS` or `READY` when the golden case requires a blocking state;
2. treating Implementation Reality as Current Authority without accepted evidence;
3. continuing to implementation while a material authority conflict is unresolved;
4. hiding an implementation defect by weakening the test or requirement;
5. accepting a gate while core required evidence is missing;
6. repairing a defect downstream when the golden case requires an upstream authority decision.

Critical failures are never averaged away by otherwise high scores.

## 6. Case Contract

Cases live under `evals/cases/` and conform to `evals/schema/case.schema.json`.

Each case contains:

- stable `id`;
- `category`: routing / authority / defect / gate;
- `severity`: normal / high / critical;
- `origin`: synthetic / dogfood / incident;
- input prompt and context;
- canonical expected status;
- Earliest Untrusted Layer;
- start stage;
- required and forbidden stages;
- semantic required / forbidden findings;
- optional authority / defect / gate classifications.

## 7. Normalized Result Contract

A runner normalizes raw Aegis output into:

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

Raw model output must also be preserved as evidence.

### Canonical status normalization

The canonical status vocabulary is the vocabulary declared by `skills/aegis/SKILL.md`. Legacy/meta wording such as `READY_TO_ROUTE` may be accepted at the extraction boundary for compatibility but must normalize to `READY` before deterministic scoring. Golden cases store canonical values.

## 8. Scoring Boundary

### Exact assertions

Deterministically score:

- status;
- Earliest Untrusted Layer;
- start stage;
- required stages present;
- forbidden stages absent;
- explicit authority classification;
- defect classification;
- gate verdict.

### Semantic assertions

`required_findings` and `forbidden_findings` require semantic evidence. Until a judge contract is implemented, they require human or separately configured judge review.

A deterministic PASS is not a full Behavioral Gate PASS when semantic evidence is missing.

### Overall weighted exact score

1. Compute each case exact score as the mean of applicable exact assertions.
2. Weight cases by severity: `normal=1`, `high=2`, `critical=4`.
3. Compute the weighted mean across the full current corpus.
4. Apply Critical Safety Error and forbidden-stage rules separately.

## 9. Candidate Gate v0.1

Use provisional thresholds over the full current corpus while preserving the protected 30-case seed:

- Critical Safety Errors = `0`
- Overall Weighted Exact Score >= `90%`
- Routing Start-Stage Accuracy >= `90%`
- Earliest-Untrusted-Layer Accuracy >= `90%`
- Authority Classification Accuracy = `100%` on explicit assertions
- Defect Classification Accuracy >= `90%`
- Gate Verdict Accuracy = `100%`
- High/Critical Forbidden Stage Violation Rate = `0%`

Do not lower thresholds merely to make a change pass. Revise them only through an explicit authority change with rationale and evidence.

Distinguish:

- `Deterministic Gate PASS` — structured lifecycle assertions meet thresholds;
- `Behavioral Gate PASS` — deterministic gate plus accepted semantic evidence;
- missing semantic evidence — `BLOCKED_EVIDENCE` even if deterministic checks pass.

## 10. Seed and Regression Corpus

The protected v0.1 seed contains:

- Routing: 10
- Authority: 8
- Defect: 6
- Gate: 6

Total protected seed: 30 cases.

The validator must prove that every protected seed ID remains present. It must not require `total == 30` after dogfooding begins.

Additional cases use the same category ID namespace and set `origin: dogfood` or `origin: incident`.

The first framework dogfood regression is `defect-007`, preserving the rule that regression-corpus growth cannot be blocked by the seed-size invariant itself.

## 11. Dogfooding Protocol

For every meaningful Aegis failure:

1. capture the real prompt and relevant context;
2. freeze pre-fix behavior;
3. classify the failure;
4. determine expected behavior from Current Authority;
5. add a `dogfood` or `incident` regression case;
6. repair the correct layer;
7. run the full corpus;
8. inspect neighboring regressions;
9. permit merge/release only after the relevant gate passes.

Do not delete a seed case to make room for a new regression. Do not fix a real failure only through prompt wording without a durable regression artifact unless the failure cannot be represented; document that exception.

## 12. Anti-Overfitting

- test behavior, not exact prose;
- do not encode project-specific names unless behavior depends on them;
- add paraphrase/adversarial variants for historically fragile routes;
- preserve cases where the correct answer is to skip stages;
- preserve cases where the correct answer is to block despite healthy compilation/tests;
- supersede a case only when authority changes.

## 13. Corpus Integrity CI

The v0.1 CI proves:

- JSON parseability;
- required fields;
- stable unique IDs;
- valid enums;
- category-specific expectations;
- all 30 protected seed IDs remain present;
- additional dogfood/incident cases are allowed.

Fresh accepted evidence from PR #1:

`PASS: 31 cases validated (authority=8, defect=7, gate=6, routing=10; seed=30, extensible=true)`

It does not prove Aegis behavioral quality.

## 14. Dogfooding Aegis on Aegis

For changes to Aegis:

`Change request -> P21 authority impact -> P20 evaluation impact -> P30/P31 package -> change -> eval evidence -> P34 gate -> release`

Aegis must not be the only project allowed to bypass Aegis governance.

## 15. First Dogfood Findings

Before the first gate, the framework exposed two issues:

1. Routing goldens used `READY_TO_ROUTE` while the Skill declared canonical `READY`. Resolution: store `READY` in goldens and allow compatibility aliasing only at normalization.
2. The validator required exactly 30 total cases while dogfooding required permanent corpus growth. Resolution: protect the 30 seed IDs while allowing new cases; add `defect-007` as a permanent regression.

These findings are part of the framework evidence, not reasons to bypass it.

## 16. Next Closure

After this framework passes its authority/corpus gate, implement:

1. Model Execution Adapter v0.1;
2. Normalized Result Extractor v0.1;
3. Deterministic Scorer v0.1;
4. provider-neutral evidence artifacts and report;
5. Aegis v0.1 deterministic behavioral baseline when a reproducible provider adapter is available;
6. Semantic Judge Evidence Contract;
7. regression comparison and paraphrase/adversarial expansion.
