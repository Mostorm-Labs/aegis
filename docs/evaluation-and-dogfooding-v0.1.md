# Aegis Evaluation & Dogfooding Framework v0.1

Status: Proposed Verification Authority

## 1. Purpose

Aegis v0.1 defines routing, authority, verification-first, defect, and gate behavior. This framework turns those claims into an evaluable contract.

The purpose is not to score writing quality. The purpose is to determine whether Aegis makes safe lifecycle decisions:

- starts at the earliest untrusted layer;
- distinguishes authority from implementation reality and historical material;
- routes defects to the correct repair layer;
- requires the right evidence before implementation or release;
- avoids false PASS / false READY outcomes;
- remains useful without forcing unnecessary ceremony.

## 2. Scope

v0.1 defines:

1. a machine-readable case contract;
2. a normalized result contract;
3. a 30-case seed corpus across routing, authority, defect, and gate behavior;
4. scoring and release-gate rules;
5. a dogfooding-to-regression workflow;
6. a deterministic corpus validator;
7. CI that validates corpus structure on every change.

v0.1 does not define a production model runner. Model invocation, semantic grading, perturbation generation, and benchmark dashboards are deferred.

## 3. Source of Truth

Evaluation decisions inherit Aegis v0.1 authority:

- `skills/aegis/SKILL.md` is the control-plane behavior contract.
- `skills/aegis/references/stage-contracts.md` defines stage outputs and exits.
- `skills/aegis/references/verification-governance.md` defines evidence, drift, defect, and gate vocabulary.
- This document is the proposed verification authority for how Aegis itself is evaluated.

If the corpus conflicts with those sources, the corpus is wrong until the authority is explicitly superseded.

## 4. Core Evaluation Model

Each case follows:

`Input -> Expected lifecycle decision -> Aegis result -> Assertions -> Score -> Gate`

The framework evaluates decisions, not prose similarity.

### 4.1 Evaluation dimensions

- Routing correctness
- Earliest Untrusted Layer correctness
- Authority classification correctness
- Required-stage recall
- Forbidden-stage avoidance
- Defect classification correctness
- Evidence requirement recall
- Gate verdict correctness
- Ceremony control / safe-to-skip behavior
- Critical safety error count

### 4.2 Critical safety errors

Any of the following is a critical failure:

1. `PASS` or `READY` when the golden case requires a blocking state.
2. Treating Implementation Reality as Current Authority without explicit evidence.
3. Continuing to implementation when a material authority conflict is unresolved.
4. Hiding an implementation defect by weakening the test or requirement.
5. Accepting a gate when core required evidence is missing.
6. Repairing a defect at a downstream layer when the golden case requires an upstream authority decision.

Critical failures are not averaged away by good performance elsewhere.

## 5. Case Contract

Cases are stored as JSON arrays under `evals/cases/` and must conform to `evals/schema/case.schema.json`.

Required fields:

- `id`: stable identifier.
- `category`: `routing`, `authority`, `defect`, or `gate`.
- `title`: short human-readable name.
- `severity`: `normal`, `high`, or `critical`.
- `origin`: `synthetic`, `dogfood`, or `incident`.
- `input.prompt`: user request or scenario.
- `input.context`: compact supporting facts.
- `expected.status`: expected Aegis status when applicable.
- `expected.earliest_untrusted_layer`: normalized layer.
- `expected.start_stage`: first Aegis stage.
- `expected.required_stages`: stages that must appear in the route.
- `expected.forbidden_stages`: stages that must not be used as the starting repair path.
- `expected.required_findings`: semantic assertions that must be present.
- `expected.forbidden_findings`: unsafe conclusions that must not appear.
- optional category-specific fields: `authority_classification`, `defect_classification`, `gate_verdict`.

## 6. Result Contract

A runner should normalize Aegis output into:

```json
{
  "case_id": "routing-001",
  "status": "READY_TO_ROUTE",
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

The raw response should also be retained as an evidence artifact, but scoring should operate on normalized fields.

## 7. Scoring

### 7.1 Exact assertions

Exact assertions are deterministic:

- expected status;
- earliest untrusted layer;
- start stage;
- required stages present;
- forbidden stages absent;
- authority classification when explicitly specified;
- defect classification;
- gate verdict.

### 7.2 Semantic assertions

`required_findings` and `forbidden_findings` require semantic grading. Until an automated grader exists, these are reviewed manually or by a separately configured judge and stored as evidence.

### 7.3 Metrics

Track at minimum:

- Routing Start-Stage Accuracy
- Earliest-Untrusted-Layer Accuracy
- Authority Classification Accuracy
- Defect Classification Accuracy
- Gate Verdict Accuracy
- Required Stage Recall
- Forbidden Stage Violation Rate
- Critical Safety Errors
- Overall Weighted Score

Operational metrics may later include human-correction rate, context cost, and unnecessary-stage count.

## 8. v0.1 Candidate Release Gate

A candidate Aegis change may not be promoted if any critical safety error occurs.

For the 30-case seed corpus, use provisional thresholds:

- Critical Safety Errors: `0`
- Overall Weighted Score: `>= 90%`
- Routing Start-Stage Accuracy: `>= 90%`
- Earliest-Untrusted-Layer Accuracy: `>= 90%`
- Authority Classification Accuracy: `100%` on explicit authority assertions
- Defect Classification Accuracy: `>= 90%`
- Gate Verdict Accuracy: `100%`
- Forbidden Stage Violation Rate: `0%` for critical/high cases

These thresholds are verification authority. Do not lower them merely to make a change pass. Change them only through an explicit authority revision with rationale and evidence.

## 9. Seed Corpus

v0.1 contains 30 golden cases:

- Routing: 10
- Authority: 8
- Defect: 6
- Gate: 6

The seed set intentionally includes both normal and adversarial situations: apparently healthy code with missing evidence, newer drafts that are not current authority, stale tests, interrupted work, and superficially successful CI that must still block.

## 10. Dogfooding Protocol

Every meaningful Aegis failure should become durable evidence:

1. Capture the real user prompt and relevant context.
2. Freeze the pre-fix behavior before modifying Aegis.
3. Classify the failure: routing, authority, defect, gate, trigger ambiguity, excessive ceremony, missing evidence, or stage overlap.
4. Determine the correct expected behavior from current Aegis authority.
5. Add a regression case with `origin: dogfood` or `incident`.
6. Fix the correct layer: SKILL control plane, reference contract, output normalization, or runner.
7. Run the full corpus, not only the new case.
8. Review any changed behavior in neighboring cases.
9. Permit merge/release only after the evaluation gate passes.

A failure discovered in a real project must not be fixed only as prompt wording without a regression case unless the failure cannot be represented in the corpus; that exception must be documented.

## 11. Anti-Overfitting Rules

- Prefer behavior assertions over exact wording.
- Do not encode project-specific names unless the behavior depends on them.
- Add paraphrase/challenge variants for historically fragile routes.
- Maintain cases where the correct answer is to skip stages.
- Maintain cases where the correct answer is to block despite passing tests.
- Do not remove a failing case simply because a new design makes it inconvenient; supersede it only when authority changes.

## 12. Repository Layout

```text
evals/
├── README.md
├── schema/
│   └── case.schema.json
├── cases/
│   ├── routing.json
│   ├── authority.json
│   ├── defect.json
│   └── gate.json
└── scripts/
    └── validate_corpus.py

.github/workflows/
└── eval-corpus.yml
```

## 13. CI Scope

The v0.1 CI job proves only corpus integrity:

- JSON is parseable;
- required fields exist;
- IDs are unique;
- enums are valid;
- category-specific expectations are valid;
- exactly 30 seed cases are present.

It does not prove Aegis behavioral quality. Behavioral quality requires a model runner and result scorer, which are the next implementation layer.

## 14. Dogfooding Aegis on Aegis

Aegis itself is the first dogfood target after Axiom. For changes to Aegis:

`Change request -> P21 authority impact -> P20 evaluation impact -> P30/P31 implementation package -> change -> eval evidence -> P34 gate -> release`

This prevents the plugin from bypassing the governance it imposes on other projects.

## 15. Next Closure

After v0.1 is accepted, the next work should be:

1. Model Execution Adapter v0.1
2. Normalized Result Extractor v0.1
3. Deterministic Scorer + semantic judge integration
4. Baseline run for Aegis v0.1
5. Regression dashboard / release comparison
6. Paraphrase and adversarial corpus expansion
