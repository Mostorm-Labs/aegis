# Verification Design

## Failure-Mode-First blocking qualification

For each important requirement, identify the relevant failure modes before choosing evidence. A proposed Evidence Artifact qualifies as a blocking Gate requirement only when all of the following are true:

1. it detects at least one high-impact failure mode;
2. existing mechanisms do not already provide credible independent detection coverage for that failure mode; and
3. without the proposed artifact, a residual proof gap remains.

If those conditions are not met, classify the evidence as supporting/confidence evidence or diagnostic/audit/observability evidence and keep it non-blocking.

Independence is a property of the detection mechanism and oracle, not the number or location of executions. Running the same test local and CI does not create independent coverage. Two tests that depend on a shared oracle do not create independent coverage against an error in that oracle. By contrast, an implementation test and an external differential reference, or a static contract check and a real-platform runtime probe, may be independent when they detect the same failure mode through genuinely different mechanisms.

When a blocking proof is justified, choose the lowest-cost credible evidence that closes the residual proof gap. Then define the invariant, oracle/reference, corpus/fixture, test/probe, metric, threshold, evidence artifact, and Gate. Evidence strength may range from narrative/manual observation through automated, deterministic golden/differential, and platform-qualified evidence; choose proportionately to risk and to the uncovered failure mode.

`Code Complete != Gate Complete`. Missing core proof is a blocker when it leaves a high-impact failure mode without credible independent detection coverage. `Missing Evidence != Automatically Gate Blocked`.
