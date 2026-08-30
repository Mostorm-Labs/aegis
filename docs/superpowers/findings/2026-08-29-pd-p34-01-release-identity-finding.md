# PD-P34-01 Finding F13-PD01-01 — Published Release Identity Reuse

Status: **ACCEPTED — SPEC_DEFECT; repair required before PD-P34-01 PASS.**

Date: 2026-08-29

## Finding

The first PD-P34-01 GREEN implementation bound the new native Plugin manifest to `0.1.0-beta.1` because the approved Final Gate Design v0.1 said to use that release initially.

That binding is invalid for final acceptance.

`v0.1.0-beta.1` is already a published historical Aegis prerelease whose immutable source provenance is `6a20969d66d1d594e7c37f970f43142e5a061e2e`. Its explicit scope is the nine-Skill Installation Kit prerelease and it does not contain the subsequently created native Plugin source.

A new Plugin source at a later revision must not retrospectively claim that already-published release identity.

## Classification

- Defect class: `SPEC_DEFECT`
- Ultimate owning layer: **P20 Verification Design / Plugin Distribution P34 Final Gate release-binding rule**
- Not an implementation defect: the implementation correctly followed the frozen PD-P34-01 target.
- Not a Product/Skill Distribution Authority conflict: the existing product contract already requires one coherent Aegis release identity and does not authorize rewriting historical releases.
- Historical `v0.1.0-beta.1` remains unchanged.

## Repair

Amend the still-unaccepted Final Gate design in place, preserving Git history, so PD-P34-01 binds to the next unpublished candidate release:

```text
Aegis candidate release: 0.1.0-beta.2
Plugin manifest:          0.1.0-beta.2
Installation Kit:         buildable as 0.1.0-beta.2
Published beta.1:         unchanged historical release
```

Create and validate `skillset/releases/aegis-0.1.0-beta.2.json` from the same canonical nine Skill sources. The candidate manifest is not a GitHub Release and must not be promoted until the applicable Plugin P34/P24 evidence is complete.

The repair strengthens the previously frozen non-regression invariant:

> Plugin and Installation Kit are parallel adapters of the same candidate/public Aegis release; a later Plugin materialization must never reuse an already-published Installation-Kit-only release identity.

## Reverification

PD-P34-01 can only PASS after fresh hosted evidence proves:

- Plugin manifest version = `0.1.0-beta.2`;
- candidate release manifest = `0.1.0-beta.2` and is deterministic;
- exact-nine Plugin materialization is bound to that candidate manifest;
- an exact-nine `0.1.0-beta.2` Installation Kit can still be built from the same canonical Skill source;
- existing `v0.1.0-beta.1` Release/tag/assets are untouched;
- existing routing/Project State/eval regressions remain green.
