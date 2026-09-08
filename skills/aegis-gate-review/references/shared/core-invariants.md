# Core Invariants

Use the lifecycle `Problem -> Authority -> Contract -> Evidence -> Plan -> Code -> Gate -> Release -> Feedback -> Problem`.

Never delete these questions:
1. Is the problem correct?
2. Is the authority/contract explicit?
3. What evidence proves the result?
4. Who or what Gate decides whether downstream work may proceed?

Route to the earliest untrusted layer. `Code Complete != Gate Complete`. `Missing Evidence != Automatically Gate Blocked`. Do not silently change upstream authority to make downstream work easier.

## Blocking Evidence Necessity Invariant

An Evidence Artifact MAY become a blocking Gate requirement only when its absence leaves at least one high-impact failure mode without credible independent detection coverage.

Before making evidence blocking:
1. identify the failure mode and why its impact is high;
2. enumerate existing detection mechanisms and determine whether they credibly cover that failure mode;
3. assess independence at the mechanism and oracle level, not by artifact name, execution location, or duplicate run;
4. state the residual proof gap that remains without the proposed artifact; and
5. choose the lowest-cost credible evidence that closes that residual proof gap.

If the same failure mode is already credibly covered by another independent mechanism, additional evidence MAY improve confidence, diagnostics, auditability, or observability, but MUST NOT block lifecycle progression solely for redundant proof.
