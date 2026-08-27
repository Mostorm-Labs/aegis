# 09-01 Multi-Skill Installed-Platform Behavioral Dogfooding

Status: **ACTIVE — `F09-01` confirmed; overall behavioral Gate is `BLOCKED_IMPLEMENTATION`.**

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
- assistant-generated simulated prompts that do not create a new platform selection event.

## Installed-platform preflight

The user reports all eight specialist packages installed in ChatGPT. Fresh ChatGPT Web conversations have now provided direct platform evidence that both a specialist (`aegis-project-state`) and the central router (`aegis`) are discoverable.

Installed status is setup evidence; only actual platform selection events count toward the protected behavioral Gate.

## Protected probe matrix

| ID | Probe | Expected platform behavior | Current verdict |
|---|---|---|---|
| 09-01-direct-specialist | `Audit this PR against its Gate evidence.` | platform selects `aegis-gate-review` | **`FAIL` — platform selected `aegis-project-state`** |
| 09-01-ambiguous-router | `What should this project do next?` | platform selects central `aegis` | **`PASS` — platform selected `aegis`** |
| 09-01-upstream-blocker-reroute | architecture request with an earlier Authority blocker | `aegis-architecture` stops and hands back to `aegis` | `BLOCKED_EVIDENCE` — protected scenario not yet executed |
| 09-01-composite-fallback | semantic-schema/operation request with only `aegis` available | composite `aegis` executes safely | `BLOCKED_EVIDENCE` — protected prompt not yet executed |

## F09-01 — Gate audit prompt misroutes to Project State

Observed platform UI: **`Used aegis-project-state skill`** for the protected direct-specialist prompt.

Expected: `aegis-gate-review`.

Evidence anchor: user-provided ChatGPT Web screenshot, SHA-256 `b3d559dbca24a809442befdd402d67c5679a7a342d9f1052a3d7b64832e5da8d`.

Classification:

- Primary: `IMPLEMENTATION_DEFECT`.
- Owning boundary: Skill trigger metadata / specialist description discrimination.
- Current suspected cause: `aegis-project-state` describes Gate/Evidence records broadly enough to overlap with a direct PR Gate-evidence audit, while `aegis-gate-review` owns P34-P36 and explicitly owns PR/Gate completion review.

This does **not** invalidate the deterministic routing oracle; it proves that intended routing and real platform description-based selection are different evidence layers.

## Probe 2 — Ambiguous Router PASS

Protected prompt: `What should this project do next?`

Expected: central `aegis`.

Observed platform UI: **`Used aegis skill`**.

Evidence anchor: user-provided ChatGPT Web screenshot, SHA-256 `898ac9e74e65b6a1bcf6675e1a9e3cef486c8069c2dafe34ef3eb207be3fd2a2`.

This confirms that the central ambiguity-router description is discoverable and wins for a deliberately cross-domain / next-step request. It does not offset F09-01; the Gate remains blocked until all protected probes pass on a repaired installed version.

## Trigger metadata inspection

Current `aegis-project-state` description includes broad trigger language for `Authority/Gate/Evidence/Integration records`, `blocked Gate propagation`, and state drift. Current `aegis-gate-review` description explicitly owns review of a PR/implementation for Gate completion and PASS-versus-BLOCKED classification. The platform selected the broader Project State description for the protected Gate-evidence prompt.

This is sufficient to classify the observed behavior as an implementation defect in trigger discrimination. Repair is deferred until the remaining probes have characterized the same installed version.

## Gate policy

`Multi-Skill Behavioral Trigger = PASS` requires all four protected probes to have real installed-platform evidence with:

- zero wrong Skill selections;
- zero forbidden downstream execution;
- zero reroute/handoff loops;
- evidence tied to the actual request/environment rather than inferred from static artifacts.

A concrete wrong selection is `BLOCKED_IMPLEMENTATION`, not `BLOCKED_EVIDENCE`.

## Current split verdict

```text
Deterministic Skill-System Tooling = PASS
Skill Package Gate                = PASS
Multi-Skill Behavioral Trigger    = BLOCKED_IMPLEMENTATION
Hosted Provider Baseline          = BLOCKED_ENVIRONMENT
Overall 09                        = BLOCKED_IMPLEMENTATION
```

## Next evidence acquisition

Continue the remaining protected probes on the same installed version before changing trigger metadata, so the first behavioral pass captures the full collision surface. After the four-probe matrix is complete, repair trigger descriptions at the owning layer, rebuild/package the affected distributions, and rerun the failed probes on the new installed version.

Do not merge PR #9 while `F09-01` is open.
