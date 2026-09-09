# Verification Design

## Failure-Mode-First blocking qualification

For each important requirement, define this chain before implementation:

`Requirement -> Invariant -> Failure Mode -> Existing Independent Coverage -> Residual Proof Gap -> Oracle/Reference -> Fixture/Corpus -> Exact Execution Method -> Evidence Artifact -> Blocking/Corroborative -> Gate Criterion`

A proposed Evidence Artifact qualifies as a blocking Gate requirement only when all of the following are true:

1. it detects at least one material high-impact failure mode;
2. existing mechanisms do not already provide credible independent detection coverage for that failure mode;
3. without the proposed artifact, a residual proof gap remains; and
4. the artifact's unique detection value is proportionate to the selected assurance profile.

For every blocking artifact record at least:

```yaml
evidence_qualification:
  failure_mode: null
  impact: null
  existing_independent_coverage: []
  new_evidence_unique_detection_value: null
  blocking_justification: null
  classification: blocking | corroborative
```

If those conditions are not met, classify the evidence as corroborative/supporting confidence evidence or diagnostic/audit/observability evidence and keep it non-blocking.

Independence is a property of the detection mechanism and oracle, not the number or location of executions. Running the same test local and CI does not create independent coverage. Two tests that depend on a shared oracle do not create independent coverage against an error in that oracle. By contrast, an implementation test and an external differential reference, or a static contract check and a real-platform runtime probe, may be independent when they detect the same failure mode through genuinely different mechanisms.

When a blocking proof is justified, choose the lowest-cost credible evidence that closes the residual proof gap. Evidence strength may range from narrative/manual observation through automated, deterministic golden/differential, and platform-qualified evidence; choose proportionately to risk and to the uncovered failure mode.

## Verification closure before P31

P20 SHOULD close the important Verification design before P31 authorizes implementation. Do not defer ambiguous terminal criteria, missing required oracles, or undefined blocking/corroborative classification to P34. A P31 package that cannot freeze these obligations returns to P20 rather than asking implementation or Gate review to invent them.

`Code Complete != Gate Complete`. Missing core proof is a blocker when it leaves a high-impact failure mode without credible independent detection coverage. `Missing Evidence != Automatically Gate Blocked`.

## Anti-Proof-Recursion Rule

Do not require evidence solely to prove that another evidence mechanism is trustworthy unless:

1. that evidence mechanism is itself a material source of undetected failure;
2. no independent mechanism already validates it; and
3. failure of the mechanism would materially affect the Gate decision.

A generator test, provenance validator, validator-provenance test, or similar proof-of-proof chain remains corroborative when it cannot detect a distinct material uncovered failure mode.
