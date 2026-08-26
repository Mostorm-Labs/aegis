# Aegis Roadmap

## v0.1 — Single-Skill control plane

- Bootstrap routing and Earliest Untrusted Layer.
- 25 stage contracts.
- Authority, drift, supersession, defect, and gate governance.
- Verification-first rules.
- Implementation task packaging.
- Superpowers composition guidance.
- Standard output contracts.

## v0.2 — Evaluation & dogfooding

The first closure is `Aegis Evaluation & Dogfooding Framework v0.1`:

- machine-readable evaluation case contract;
- 30-case seed corpus: routing, authority, defect, and gate behavior;
- deterministic corpus-integrity validator;
- CI integrity gate;
- critical-safety-error model;
- provisional behavioral release thresholds;
- dogfood/incident -> regression-case workflow.

The framework intentionally separates corpus integrity from model behavior. Corpus CI proves that evaluation inputs are structurally valid; it does not claim that Aegis itself passes the behavioral corpus.

Next v0.2 implementation closures:

1. Model Execution Adapter v0.1
2. Normalized Result Extractor v0.1
3. Deterministic Scorer v0.1
4. Semantic finding judge / manual-review evidence contract
5. Baseline behavioral run for Aegis v0.1
6. Regression comparison report
7. Paraphrase and adversarial corpus expansion
8. Real-project dogfooding across greenfield, SaaS, mobile/desktop, runtime/infrastructure, defect, and release scenarios

Collect and preserve failures in routing, trigger ambiguity, excessive ceremony, missing evidence patterns, false PASS/READY, wrong authority promotion, incorrect defect layer, and stage overlap.

## v0.3 — Split high-value Skills

Promote frequently independent workflows into separate Skills while retaining a central router. Keep shared governance and output taxonomy in references rather than duplicating them.

Do not split solely to mirror P00-P36. Split when a workflow is independently triggered, independently testable, and benefits from its own progressive context.

## v0.4 — Machine-readable project state

Explore an optional `aegis.yaml` / project manifest describing current authorities, stage status, gates, evidence locations, and downstream dependencies so coding agents can consume project state without repeatedly reconstructing it.

## v1.0 — Evidence-backed suite

Declare v1.0 only after Aegis has been exercised on multiple real projects and its routing, stage boundaries, authority classification, defect routing, and gate vocabulary have demonstrated stable behavior under regression evaluation.
