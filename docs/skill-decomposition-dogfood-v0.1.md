# 09-01 Multi-Skill Installed-Platform Behavioral Dogfooding

Status: **ACTIVE — overall behavioral Gate remains `BLOCKED_EVIDENCE`.**

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

## Environment preflight — 2026-08-27T10:28+08:00

In the current ChatGPT conversation, the observable installed Aegis entrypoint is the composite `aegis` Skill. The eight generated specialist packages exist as reviewed artifacts, but they are not observable as installed specialist entrypoints in this session.

This means the environment can provide useful supplemental evidence for the central facade, but cannot yet satisfy specialist-selection probes.

## Protected probe matrix

| ID | Probe | Expected platform behavior | Current verdict |
|---|---|---|---|
| 09-01-direct-specialist | `Audit this PR against its Gate evidence.` | platform selects `aegis-gate-review` | `BLOCKED_EVIDENCE` — specialist not observed installed |
| 09-01-ambiguous-router | `What should this project do next?` | platform selects central `aegis` | `BLOCKED_EVIDENCE` — protected prompt not yet executed as an independent selection event |
| 09-01-upstream-blocker-reroute | architecture request with an earlier Authority blocker | `aegis-architecture` stops and hands back to `aegis` | `BLOCKED_EVIDENCE` — specialist not observed installed |
| 09-01-composite-fallback | semantic-schema/operation request with only `aegis` installed | composite `aegis` executes the stage family without specialist dependency | `BLOCKED_EVIDENCE` — protected prompt not yet executed as an independent selection event |

## Supplemental observation

The current request to enter and execute 09-01 was routed through the installed composite `aegis` Skill. This is genuine platform behavior and supports the general central-router design, but it is **not** promoted into the protected Gate because the request is not the protected ambiguous-router prompt.

## Gate policy

`Multi-Skill Behavioral Trigger = PASS` requires all four protected probes to have real installed-platform evidence with:

- zero wrong Skill selections;
- zero forbidden downstream execution;
- zero reroute/handoff loops;
- evidence tied to the actual request/environment rather than inferred from static artifacts.

If any protected probe lacks valid platform evidence, the Gate remains `BLOCKED_EVIDENCE`.

## Current split verdict

```text
Deterministic Skill-System Tooling = PASS
Skill Package Gate                = PASS
Multi-Skill Behavioral Trigger    = BLOCKED_EVIDENCE
Hosted Provider Baseline          = BLOCKED_ENVIRONMENT
Overall 09                        = BLOCKED_EVIDENCE
```

## Next evidence acquisition

Install the reviewed specialist Skills in a platform environment that exposes their entrypoints, then execute the protected probes as independent requests. Record the actually selected Skill, handoff behavior, forbidden-stage behavior, and platform evidence back into `skillset/dogfood/installed-platform-v0.1.json`.

Do not merge PR #9 solely on deterministic/package evidence while this behavioral Gate remains blocked.
