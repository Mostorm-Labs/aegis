---
name: aegis-governance
description: Review and govern Aegis software-development authority across Authority Review, five-axis drift review, supersession, and release readiness. Use when the user asks whether documents or implementations conflict, whether an authority should be replaced, how to classify drift, how to preserve superseded history, or whether a release is ready.
---

# Aegis Governance

Own governance stages `P21` Authority Review, `P22` Five-Axis Drift Review, `P23` Authority Supersession, and `P24` Release Readiness.

## Workflow

1. Build a source-of-truth map and distinguish Current, Draft/Proposed, Superseded/Historical, Implementation Reality, and Evidence.
2. Review product, semantic, architecture, implementation, and verification drift.
3. If replacement authority is accepted, preserve old history and perform explicit supersession; never silently overwrite.
4. For release readiness, judge only evidence relevant to the product risk profile and name exact blockers.

**Earlier untrusted layer:** if the problem/requirement/design basis itself is not trustworthy enough to govern, stop and hand back to `aegis` with the earliest layer; do not invent missing upstream authority.

Read [references/governance.md](references/governance.md) and the shared Authority/status contracts.
