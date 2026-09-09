# Core Invariants

Use the lifecycle `Problem -> Authority -> Contract -> Evidence -> Plan -> Code -> Gate -> Release -> Feedback -> Problem`.

Never delete these questions:
1. Is the problem correct?
2. Is the authority/contract explicit?
3. What evidence proves the result?
4. Who or what Gate decides whether downstream work may proceed?

Route to the earliest untrusted layer. `Code Complete != Gate Complete`. `Missing Evidence != Automatically Gate Blocked`. Do not silently change upstream authority to make downstream work easier.

## Gate Closure Stability Principle

Once P31 authorizes implementation, the blocking completion target is frozen.

P34 MAY block only for:
1. violation of an explicitly frozen requirement;
2. failure of an explicitly frozen verification obligation; or
3. a newly discovered high-impact correctness, safety, security, compatibility, data-integrity, or release-critical failure mode that was not reasonably covered by the frozen contract.

P34 MUST NOT create new blocking evidence obligations solely to increase confidence in behavior that is already covered by independent evidence. Confidence improvements, redundant proof, diagnostics, auditability, observability, and hardening may become successor work but do not move the current Gate finish line.

Closure stability is not permission to ignore a real late defect. A newly discovered high-impact uncovered failure mode may override the frozen target, but the reviewer must identify the failure mode, impact, existing independent coverage gap, and why the severity justifies blocking current closure.

## Blocking Evidence Necessity Invariant

An Evidence Artifact MAY become a blocking Gate requirement only when its absence leaves at least one high-impact failure mode without credible independent detection coverage.

Before making evidence blocking:
1. identify the failure mode and why its impact is high;
2. enumerate existing detection mechanisms and determine whether they credibly cover that failure mode;
3. assess independence at the mechanism and oracle level, not by artifact name, execution location, or duplicate run;
4. state the residual proof gap that remains without the proposed artifact; and
5. choose the lowest-cost credible evidence that closes that residual proof gap.

If the same failure mode is already credibly covered by another independent mechanism, additional evidence MAY improve confidence, diagnostics, auditability, or observability, but MUST NOT block lifecycle progression solely for redundant proof.

## Anti-Proof-Recursion Rule

Do not require evidence solely to prove that another evidence mechanism is trustworthy unless all three conditions hold:
1. the evidence mechanism itself is a material source of undetected failure;
2. no independent system already validates it; and
3. failure of that mechanism would materially affect the Gate decision.

A proof-of-proof chain that does not add unique detection value for a material high-impact failure mode is corroborative, not blocking. Do not add generator tests, validator provenance, provenance-of-provenance, or equivalent recursive proof merely because each step can increase confidence.
