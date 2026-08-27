# Aegis Project State Manifest + Authority Dependency Graph v0.2

Status: **Superseded / Historical v0.2.**

This historical document superseded `docs/project-state-manifest-v0.1.md` and is now superseded by **`docs/project-state-manifest-v0.3.md`**, the Current Replacement Authority.

Supersession reason: formal 08 self-hosting confirmed **F08-03 — SPEC_DEFECT + MISSING_CONTRACT**. v0.2 correctly solved blocked-Gate propagation and basic integration lifecycle, but incorrectly required a completed `integrated` occurrence to retain a current/current-valid PASS Gate forever. v0.3 separates Historical Occurrence, Current Applicability, and Current Actionability and was integrated through PR #8 at `be385b3549900ba5bc34170dbfa8b4e583631a1d`.

The following v0.2 record is preserved for audit/history and must not be used as Current execution authority.

## v0.2 closures

- **F08-01:** active current `BLOCKED_*` Gate verdicts propagate into generated project state and routing.
- **F08-02:** Authority status, Gate verdict/validity, and repository Integration state are separate facts; `.aegis/integrations.json` records `awaiting_integration`, `integrated`, and `closed_unmerged`.

v0.2 Gate routing map:

| Verdict | Earliest layer | Recommended stage |
| --- | --- | --- |
| `BLOCKED_AUTHORITY` | `authority` | `P21` |
| `BLOCKED_EVIDENCE` | `verification` | `P34` |
| `BLOCKED_IMPLEMENTATION` | `implementation` | `P35` |
| `BLOCKED_ENVIRONMENT` | `verification` | `P34` |
| `PASS` | none | none |
| `PASS_WITH_FINDINGS` | none | none |

Generated v0.2 state added `blocking_gates[]`, `awaiting_integrations[]`, and `recommended_handoff`.

## Historical repository reality

At the v0.2 period:

- PR #3 provider tooling was integrated at `d55686123bd22254c196f8232c8b115f469bde1e`; live OpenAI behavioral baseline remained `BLOCKED_ENVIRONMENT` because no API credential existed.
- PR #4 project-state v0.1 was integrated at `555bac21d485fc4530680c61719fc36831021b0d`.
- PR #6 remained closed/unmerged check-suite history.
- PR #7 project-state v0.2 was integrated at `8ca7b49d40a17e8cb7ffba86632da3aeae5e911c`.

## Accepted v0.2 P34 evidence

Core PR #6 merge-ref run `33021019280`, job `98351117474`:

```text
schema parse = PASS
VALID
STATE_OK
Ran 34 tests in 0.327s
OK
```

Final clean-head run `33021291693`, job `98352018093`:

```text
schema parse = PASS
VALID
STATE_OK
Ran 34 tests in 0.221s
OK
```

P34 returned **PASS_WITH_FINDINGS** using an explicit P20 compound-evidence fallback because GitHub did not emit the expected fresh PR #7 event run. That was classified as `ENVIRONMENT_DEFECT`, not implementation defect.

## Historical defect boundary

The later 08 rerun showed that this v0.2 rule was incomplete:

```text
integrated occurrence
requires current-valid PASS Gate forever
```

Once 07 v0.1 was superseded, PR #4 was still truly integrated but its Gate was stale, making truthful history impossible to validate. That is F08-03 and the reason this document is now historical.

For current semantics, use `docs/project-state-manifest-v0.3.md`.
