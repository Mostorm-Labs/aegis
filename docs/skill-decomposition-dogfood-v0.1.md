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
- assistant-generated simulated prompts that do not create a new platform selection event;
- a routing stimulus that itself names the expected selected or handoff Skill in a way that can bias auto-selection.

## Installed-platform preflight

The user reports all eight specialist packages installed in ChatGPT. Fresh ChatGPT Web conversations have provided direct platform evidence that a specialist (`aegis-project-state`) and the central router (`aegis`) are discoverable. The pre-install conversation still exposes the composite `aegis` path and has been used for the composite-only fallback probe.

Installed status is setup evidence; only actual platform selection events count toward the protected behavioral Gate.

## Protected probe matrix

| ID | Probe | Expected platform behavior | Current verdict |
|---|---|---|---|
| 09-01-direct-specialist | `Audit this PR against its Gate evidence.` | platform selects `aegis-gate-review` | **`FAIL` — platform selected `aegis-project-state`** |
| 09-01-ambiguous-router | `What should this project do next?` | platform selects central `aegis` | **`PASS` — platform selected `aegis`** |
| 09-01-upstream-blocker-reroute | architecture request with an earlier Authority blocker | `aegis-architecture` stops and hands back to `aegis` | **`BLOCKED_EVIDENCE` — v0.1 attempt invalid for selection verdict because of `TEST_DEFECT`; v0.2 rerun required** |
| 09-01-composite-fallback | semantic-schema/operation request with only `aegis` available | composite `aegis` executes safely | **`PASS` — platform selected `aegis`, routed P12/P13, and failed closed on missing upstream authority** |

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

This confirms that the central ambiguity-router description is discoverable and wins for a deliberately cross-domain / next-step request.

## Probe 4 — Composite Fallback PASS

Protected prompt: `Design the semantic schema and operation model for this feature.`

Environment: the already-open pre-install conversation, which exposes only the composite `aegis` entrypoint.

Observed platform UI: **`Used aegis skill`**.

Observed behavior: Aegis routed the request to P12 Semantic Schema + P13 Operation/Mutation Model and returned `BLOCKED_MISSING_INPUT` because upstream object/behavior authority was unavailable. It did not depend on `aegis-modeling` and did not invent downstream semantics.

Evidence anchor: user-provided ChatGPT Web screenshot, SHA-256 `9f581b4018f005ec2a10ecb82f8a9a2db524788799dc3b6a87128dbe04d32974`.

This satisfies the composite compatibility requirement.

## F09-02 — Probe 3 v0.1 fixture contaminates initial Skill selection

Probe 3 v0.1 produced a real platform event:

- observed UI: `Used aegis skill` (twice);
- response behavior: `P14 System Architecture — Safety Preflight`, `BLOCKED_AUTHORITY`, no substantive P14 execution, and preserved P12 blocker;
- screenshot SHA-256: `c7907741e15ae2510f3d33db249f3919160c8319c4bf61d60545fe79c2a89744`.

However, the v0.1 user stimulus explicitly stated the expected final route was owned by **central `aegis`**. Because platform Skill selection is description-based, naming the expected handoff owner inside the stimulus can bias the very initial-selection behavior the probe is supposed to measure.

Classification:

- Primary: `TEST_DEFECT`.
- Finding ID: `F09-02`.
- The observed safe-stop behavior is retained as supplemental evidence.
- The `aegis` initial selection is **not** promoted into either PASS or implementation FAIL for the protected routing case.

The original fixture is preserved at `skillset/dogfood/fixtures/upstream-authority-blocker-v0.1.json` as historical test evidence.

The active replacement fixture is `skillset/dogfood/fixtures/upstream-authority-blocker-v0.2.json`. It preserves the same verified P12 blocker facts but removes all Skill/router names from the user prompt. The expected oracle remains:

1. initial platform selection = `aegis-architecture`;
2. specialist stops before producing substantive P14 design;
3. response identifies the P12 Authority blocker;
4. handoff returns to central `aegis`;
5. no silent repair/invention of P12 Authority and no direct specialist-to-specialist repair chain.

## Trigger metadata inspection

Current `aegis-project-state` description includes broad trigger language for `Authority/Gate/Evidence/Integration records`, `blocked Gate propagation`, and state drift. Current `aegis-gate-review` description explicitly owns review of a PR/implementation for Gate completion and PASS-versus-BLOCKED classification. The platform selected the broader Project State description for the protected Gate-evidence prompt.

Current `aegis-architecture` description already owns system/module architecture and explicitly says an earlier untrusted semantic layer must stop and hand back to `aegis`. The first Probe 3 attempt therefore does not establish a second implementation defect because its stimulus also named central `aegis` as the required final route.

Repair of F09-01 remains deferred until the clean Probe 3 v0.2 rerun completes the baseline characterization.

## Gate policy

`Multi-Skill Behavioral Trigger = PASS` requires all four protected probes to have real installed-platform evidence with:

- zero wrong Skill selections;
- zero forbidden downstream execution;
- zero reroute/handoff loops;
- evidence tied to the actual request/environment rather than inferred from static artifacts;
- routing-neutral stimuli that do not name the expected selection/handoff target when that would bias the platform.

A concrete wrong selection from an admissible probe is `BLOCKED_IMPLEMENTATION`; a contaminated routing probe remains `BLOCKED_EVIDENCE` and is repaired at the test layer.

## Current split verdict

```text
Deterministic Skill-System Tooling = PASS
Skill Package Gate                = PASS
Multi-Skill Behavioral Trigger    = BLOCKED_IMPLEMENTATION
Hosted Provider Baseline          = BLOCKED_ENVIRONMENT
Overall 09                        = BLOCKED_IMPLEMENTATION
```

## Next evidence acquisition

Rerun Probe 3 in a fresh multi-skill conversation using `upstream-authority-blocker-v0.2.json`. After that clean baseline event is captured, repair `F09-01` at the trigger-description boundary, rebuild/package affected distributions, reinstall the repaired packages, and rerun failed/affected probes.

Do not merge PR #9 while `F09-01` is open.
