# Output Contracts

## Generic stage output

Use this as a default, adapting sections to the task:

```text
Status: READY | READY_WITH_FINDINGS | BLOCKED_*

Source of Truth
- Current authority:
- Draft/proposed:
- Historical/superseded:
- Implementation reality:
- Evidence:

Objective
Non-goals

Findings
- ...

Decisions / Contract
- ...

Open Questions / Blockers
- ...

Verification Implications
- ...

Handoff
- Stable outputs the next stage may rely on
- Inputs still required
```

## Bootstrap output

```text
Status: READY_TO_ROUTE | BLOCKED_MISSING_INPUT | BLOCKED_AUTHORITY

Project Profile Card
- Project / Change:
- Work Type:
- Current Maturity:
- Recommended Profile:
- Earliest Untrusted Layer:
- Existing Current Authority:
- Critical Missing Authority:
- Complexity / Risk Signals:

Recommended Route
- Start Stage:
- Required Sequence:
- Optional / Conditional Stages:
- Safe to Skip:

Why This Route
Escalation Conditions
First Action
```

## Gate review output

```text
Gate: <id/name>
Verdict: PASS | PASS_WITH_FINDINGS | BLOCKED_IMPLEMENTATION | BLOCKED_AUTHORITY | BLOCKED_EVIDENCE | BLOCKED_ENVIRONMENT

Authority Baseline
Implementation Baseline

Evidence Review
- Contract:
- Tests:
- Oracle/Golden/Differential:
- Performance:
- Platform:
- Demo/Artifact:

Drift Review
- Product:
- Semantic:
- Architecture:
- Implementation:
- Verification:

Findings
- <classification>: <finding>

Downstream Impact
Next Action
```

## Writing rule

Use the user's language unless a project authority specifies another language. Preserve project terminology exactly when it is defined by authority. Clearly distinguish source-derived facts from inference or recommendations.
