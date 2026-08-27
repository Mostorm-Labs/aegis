# Aegis Self-Hosting / Manifest Adoption Implementation Plan

**Goal:** Make `Mostorm-Labs/aegis` the first trusted root `.aegis/` consumer and preserve each dogfood defect as regression evidence until the current Project State Authority represents repository reality faithfully.

## Historical route

```text
v0.1 adoption -> F08-01 / F08-02
v0.2 rerun    -> F08-01/F08-02 closed; F08-03 found
v0.3 repair   -> historical occurrence/applicability/actionability split
v0.3 rerun    -> current task
```

## Current v0.3 rerun tasks

- [ ] Clean-rebase the 08 branch onto current `main`; do not carry stale v0.2 runtime files.
- [ ] Preserve `defect-008`, `defect-009`, and `defect-010` in the extensible dogfood corpus.
- [ ] Materialize root `.aegis/` with schema `0.3` using current Authority and repository facts.
- [ ] Preserve historical integration facts for PR #4 / #6 / #7 and add PR #8 as current integrated v0.3.
- [ ] Keep the real OpenAI behavioral baseline as `BLOCKED_ENVIRONMENT`.
- [ ] Generate `state.json` only through `tools.aegis_state.cli recompute --write`.
- [ ] Require `validate .` and `check .` to return `VALID / STATE_OK`.
- [ ] Require generated state to classify PR #4 and PR #7 as historical, PR #6 as closed history, PR #8 as current, and the OpenAI Gate as the sole active project blocker.
- [ ] Run the full current project-state regression and evaluation corpus validator.
- [ ] Add repository CI steps that separately prove generic tooling and root self-host state.
- [ ] Record exact evidence in `docs/dogfood/self-hosting-v0.1-report.md` and `docs/self-hosting-manifest-adoption-v0.1.md`.
- [ ] Perform P34 on fresh final-head CI.

## Current acceptance oracle

```text
historical_gates includes gate-project-state-pr4 and gate-project-state-v02-pr7
blocking_gates = [gate-openai-real-baseline]
earliest_untrusted_layer = verification
recommended_next_stage = P34
recommended_handoff = null
awaiting_integrations = []
int-pr4 = historical
int-pr6 = historical
int-pr7 = historical
int-pr8 = current
root strict check = STATE_OK
```

The real OpenAI `BLOCKED_ENVIRONMENT` is expected and does not by itself fail 08. 08 passes when it represents that blocker faithfully while preserving truthful repository history.
