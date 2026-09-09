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

## P31 Execution Closure output

```yaml
EXECUTION_CLOSURE_CONTRACT:
  implementation:
    required_changes: []
    forbidden_changes: []
  tests:
    required: []
  hosted_verification:
    required: []
    optional: []
  evidence:
    blocking: []
    corroborative: []
  terminal_success:
    all_of: []
  terminal_blockers:
    explicit_classes:
      - AUTHORITY_CONFLICT
      - MISSING_REQUIRED_INPUT
      - ENVIRONMENT_BLOCKER
      - FROZEN_VERIFICATION_FAILURE
      - NEW_HIGH_IMPACT_FAILURE_MODE
  return_policy:
    continue_until_terminal_state: true
```

Do not issue P32 when terminal success or a required blocking oracle is ambiguous. Repair P20/P31 first.

## Bootstrap output

```text
Status: READY_TO_ROUTE | BLOCKED_MISSING_INPUT | BLOCKED_AUTHORITY

Project Profile Card
- Project / Change:
- Work Type:
- Current Maturity:
- Recommended Profile:
- Profile Justification if Full:
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

```yaml
gate_review:
  gate: null
  verdict: PASS | PASS_WITH_FINDINGS | BLOCKED_IMPLEMENTATION | BLOCKED_AUTHORITY | BLOCKED_EVIDENCE | BLOCKED_ENVIRONMENT
  authority_baseline: null
  implementation_baseline: null
  frozen_requirements:
    passed: []
    failed: []
  frozen_evidence:
    passed: []
    failed: []
  new_findings:
    blocking_high_impact: []
    non_blocking: []
  downstream_impact: null
  next_action: null
```

Every newly discovered blocking finding must include failure mode, impact, existing independent coverage, unique detection value, why frozen evidence did not cover it, and why severity justifies overriding closure stability.

## Writing rule

Use the user's language unless a project authority specifies another language. Preserve project terminology exactly when it is defined by authority. Clearly distinguish source-derived facts from inference or recommendations.
