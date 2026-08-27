---
name: aegis-gate-review
description: Audit implementation and evidence against Aegis Gate criteria, classify defects, and route fixes/reverification. Use when the user asks to review a PR or implementation for Gate completion, determine PASS versus BLOCKED, classify whether a failure is implementation/spec/authority/test/evidence/environment related, or verify a fix and regression closure.
---

# Aegis Gate Review

Own `P34` Gate Review, `P35` Defect Classification, and `P36` Fix / Reverification.

## Gate loop

- At `P34`, audit Authority conformance, semantics/contracts, scope, automated tests, oracle/golden/differential evidence, performance/platform evidence when required, and downstream safety. Agent claims are not evidence.
- At `P35`, classify the owning defect layer before proposing a fix.
- At `P36`, repair at the owning layer and rerun the failed evidence plus relevant regression evidence.

**Earlier untrusted layer:** if review discovers a spec or Authority defect upstream of implementation, stop downstream repair and hand back to `aegis`; do not silently rewrite Authority inside Gate review.

Read [references/gate-review.md](references/gate-review.md) and the shared status/Authority contracts.
