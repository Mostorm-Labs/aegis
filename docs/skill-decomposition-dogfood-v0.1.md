# 09-01 Multi-Skill Installed-Platform Behavioral Dogfooding

Status: **ACTIVE — `F09-01` and `F09-03` confirmed; overall behavioral Gate is `BLOCKED_IMPLEMENTATION`.**

## Purpose

This dogfood pass validates actual installed-platform Skill selection and rerouting behavior for the 09 Aegis Multi-Skill architecture. It deliberately separates platform observation from deterministic routing, package validation, and static expectations.

The machine-readable evidence matrix is `skillset/dogfood/installed-platform-v0.1.json`.

## Authority

- 09 Aegis Skill Decomposition & Multi-Skill Architecture v0.1 is the governing proposed execution authority.
- PR #9 remains open/unmerged while the Multi-Skill Behavioral Trigger Gate is unresolved.
- Deterministic Skill-System Tooling and Skill Package Gates have already passed.
- The live hosted-provider baseline remains independently `BLOCKED_ENVIRONMENT`.

## Evidence rule

A protected probe may pass only from a real platform selection event in an environment satisfying that probe's installation/fixture preconditions.

The following are explicitly insufficient substitutes:

- deterministic routing corpus results;
- Skill Creator validation/package success;
- reasoning about which Skill should have been selected;
- assistant-generated simulated prompts that do not create a new platform selection event;
- a routing stimulus that itself names the expected selected or handoff Skill in a way that can bias auto-selection.

## Protected probe baseline

| ID | Probe | Expected platform behavior | Baseline verdict |
|---|---|---|---|
| 09-01-direct-specialist | `Audit this PR against its Gate evidence.` | platform selects `aegis-gate-review` | **`FAIL` — selected `aegis-project-state`** |
| 09-01-ambiguous-router | `What should this project do next?` | platform selects central `aegis` | **`PASS` — selected `aegis`** |
| 09-01-upstream-blocker-reroute | P14 request with an earlier P12 Authority blocker | platform selects `aegis-architecture`, specialist stops, handoff returns to `aegis` | **`FAIL` — routing-neutral v0.2 selected composite `aegis`; safe-stop behavior itself was correct** |
| 09-01-composite-fallback | modeling request in composite-only environment | composite `aegis` executes safely | **`PASS` — selected `aegis` and failed closed on missing upstream authority** |

Baseline characterization is therefore complete: **2 PASS / 2 FAIL** on admissible protected platform events.

## F09-01 — Gate audit prompt misroutes to Project State

Observed platform UI: **`Used aegis-project-state skill`** for the protected direct-specialist prompt.

Expected: `aegis-gate-review`.

Evidence anchor: user-provided ChatGPT Web screenshot, SHA-256 `b3d559dbca24a809442befdd402d67c5679a7a342d9f1052a3d7b64832e5da8d`.

Classification:

- Primary: `IMPLEMENTATION_DEFECT`.
- Owning boundary: Skill trigger metadata / specialist description discrimination.

## Probe 2 — Ambiguous Router PASS

Protected prompt: `What should this project do next?`

Expected and observed: central `aegis`.

Evidence anchor: user-provided ChatGPT Web screenshot, SHA-256 `898ac9e74e65b6a1bcf6675e1a9e3cef486c8069c2dafe34ef3eb207be3fd2a2`.

This confirms the central router works for deliberately ambiguous/cross-domain next-step requests.

## Probe 4 — Composite Fallback PASS

Protected prompt: `Design the semantic schema and operation model for this feature.`

Environment: the already-open pre-install conversation, exposing only the composite `aegis` entrypoint.

Observed: `Used aegis skill`; Aegis routed to P12/P13 and returned `BLOCKED_MISSING_INPUT` because upstream object/behavior authority was unavailable. It did not depend on `aegis-modeling` and did not invent semantic truth.

Evidence anchor: user-provided screenshot, SHA-256 `9f581b4018f005ec2a10ecb82f8a9a2db524788799dc3b6a87128dbe04d32974`.

## F09-02 — Probe 3 v0.1 test fixture contamination

The first Probe 3 stimulus explicitly named the expected final handoff owner (`central aegis`). The platform selected `aegis`, but because the stimulus exposed the expected router, that event is inadmissible for initial-selection verdict.

- Primary: `TEST_DEFECT`.
- Historical fixture: `skillset/dogfood/fixtures/upstream-authority-blocker-v0.1.json`.
- Replacement: routing-neutral `skillset/dogfood/fixtures/upstream-authority-blocker-v0.2.json`.
- The v0.1 event is still valid supplemental evidence that the composite path fails closed safely.

## F09-03 — Routing-neutral P14 request misroutes to composite Aegis

The v0.2 fixture removes all Skill/router names from the user stimulus while preserving the verified blocker facts.

Observed platform UI: **`Used aegis skill`** (twice).

Expected initial selection: `aegis-architecture`.

Observed content behavior: safe. The response returned `BLOCKED_AUTHORITY`, stopped substantive P14 architecture design, and preserved the P12 blocker. The failure is therefore **initial Skill selection**, not safety-preflight behavior.

Evidence anchor: user-provided screenshot, SHA-256 `4b131dcab83c12b64c6f5fd60782f8d474a7a04e5f2c8d7df0451415c7c16c54`.

Classification:

- Primary: `IMPLEMENTATION_DEFECT`.
- Finding ID: `F09-03`.
- Owning boundary: Skill discovery metadata.

## Root cause — F09-RC-01 Trigger boundary violation

The approved 09 architecture says **Specific Skill Wins** and central `aegis` owns ambiguity/cross-domain routing. The implemented frontmatter descriptions do not fully enforce that boundary:

1. composite `aegis` explicitly advertises direct specialist-owned work such as feature/architecture design, Gate audit, defect classification, and evidence definition;
2. `aegis-project-state` advertises generic Authority/Gate/Evidence/Integration records rather than remaining tightly scoped to `.aegis` manifests and deterministic Project State operations;
3. `aegis-architecture` and `aegis-gate-review` own the failed protected requests but use less discriminative direct-trigger wording than their competing general/cross-cutting entrypoints.

Skill Creator defines `SKILL.md` frontmatter `name` + `description` as the discovery/auto-invocation interface; `agents/openai.yaml` is UI metadata. The observed failures therefore map directly to the canonical Skill descriptions rather than runtime stage logic.

Classification: **`IMPLEMENTATION_DEFECT`**. The 09 specification remains correct; its Specific-Skill-Wins rule was implemented inadequately.

## Repair strategy

Use RED→GREEN and change only the owning boundary:

- narrow composite `aegis` to ambiguous/cross-domain/start-resume/central-handoff routing plus composite fallback;
- narrow `aegis-project-state` to explicit `.aegis` manifest validation/recomputation/drift operations;
- strengthen `aegis-architecture` with direct system-architecture / P14-P18 trigger language;
- strengthen `aegis-gate-review` with direct PR Gate / Gate-evidence trigger language;
- add deterministic trigger-boundary regressions so future descriptions cannot silently reclaim specialist-owned requests;
- rebuild generated distributions and rerun Skill Creator validation/package;
- reinstall only affected packages and rerun affected platform probes before promotion.

## Current split verdict

```text
Deterministic Skill-System Tooling = PASS
Skill Package Gate                = PASS
Multi-Skill Behavioral Trigger    = BLOCKED_IMPLEMENTATION
Hosted Provider Baseline          = BLOCKED_ENVIRONMENT
Overall 09                        = BLOCKED_IMPLEMENTATION
```

PR #9 remains open/unmerged until the repaired installed version passes all protected behavioral probes.
