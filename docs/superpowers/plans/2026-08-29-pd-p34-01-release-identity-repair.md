# PD-P34-01 Release Identity Repair Plan

Status: **Executed repair plan for F13-PD01-01**

**Finding:** The first implementation used `0.1.0-beta.1` for the new Plugin, but `v0.1.0-beta.1` is already a published Installation-Kit-only historical release pinned to source `6a20969d66d1d594e7c37f970f43142e5a061e2e`.

**Classification:** `SPEC_DEFECT`

**Ultimate owning layer:** P20 Verification Design / Plugin Distribution P34 Final Gate release-binding rule.

## Repair sequence

1. Preserve `v0.1.0-beta.1` unchanged.
2. Amend the still-unaccepted P34 Final Gate v0.1 release-binding clause to use the next unpublished candidate: `0.1.0-beta.2`.
3. Create deterministic `skillset/releases/aegis-0.1.0-beta.2.json` from the same canonical exact-nine Skill sources.
4. Bind `plugins/aegis/.codex-plugin/plugin.json` to `0.1.0-beta.2`.
5. Bind the PD-P34-01 materialization oracle/check to `0.1.0-beta.2`.
6. Add hosted CI verification that the candidate release manifest is deterministic.
7. Build an exact-nine `0.1.0-beta.2` Installation Kit candidate from the same manifest and retain it as CI evidence.
8. Re-run Plugin materialization, Skillset, routing, installed-platform, Project State, and evaluation regressions.
9. Only after the repaired exact head is green may PD-P34-01 be independently reviewed for PASS.

## Non-goals

- Do not publish `v0.1.0-beta.2` yet.
- Do not mutate the existing `v0.1.0-beta.1` tag, Release, assets, or release manifest.
- Do not begin PD-P34-02 real platform installation until PD-P34-01 is independently accepted.
- Do not change the canonical nine Skill contents or routing semantics as part of this repair.
