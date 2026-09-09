# Implementation Execution

## P30 Implementation Planning

Decompose authority into evidence-gated vertical slices, not layers that stay unverifiable until the end. For each slice identify dependencies, implementation scope, mock/reference/oracle, automated verification, observable demo/artifact when useful, performance gate when applicable, and exit criteria.

Do not create one task called "implement the system" when independent gates can prove progress earlier.

## P31 Task Packaging

Each coding-agent task must include:

- Task ID and purpose
- Current authority references
- Inputs/dependencies
- Scope and affected modules/files
- Required changes and forbidden changes
- Explicit non-goals
- Required tests and oracle/reference
- Hosted verification: required vs optional
- Evidence: blocking vs corroborative
- Performance constraints when applicable
- Terminal success conditions
- Explicit terminal blocker classes
- Return policy with `continue_until_terminal_state: true`

Represent these completion semantics as `EXECUTION_CLOSURE_CONTRACT`. A good package lets the agent implement without inventing architecture or waiting for a later reviewer to gradually define completion.

If terminal success is ambiguous, a required oracle/input is missing, or a Verification obligation is not frozen, return to P20/P31 before coding.

## P32 Implementation

Before editing, inspect current repository state and task authority. Implement only the assigned scope. Execute the complete frozen Execution Closure Contract until terminal success or an explicit terminal blocker occurs. Do not return at an intermediate checkpoint when remaining frozen work is executable in the same run.

Resolve ordinary uncertainty by reading repository/Authority/package/tests. If Authority is missing or contradictory, scope conflicts, environment prevents execution, frozen Verification fails, or a new high-impact failure mode appears, stop with the precise terminal blocker rather than inventing semantics.

Do not weaken tests, redefine requirements, expand scope, or add new blocking completion requirements merely to make the task pass.

## P33 Resume Interrupted Work

P33 resumes valid partial work after session/tool/API/environment interruption. First inspect current branch, local changes/diff, generated artifacts, tests already run, and task authority. Preserve valid existing modifications; do not reset/rollback by default. Resume from the first incomplete verified step in the same frozen closure contract.

Apply `P33_REPETITION_GUARD`: if resumed work exists only because P31 omitted a requirement, classify `TASK_PACKAGE_DEFECT` and return P31. If P20 omitted a required verification obligation/oracle, classify `VERIFICATION_DESIGN_DEFECT` and return P20. Do not turn P33 into an indefinite package-enhancement loop.

## P34 Gate Review

Review independently:

- Frozen Requirement Audit
- Frozen Evidence Audit
- Repository Reality Audit
- New findings classified as blocking high-impact vs non-blocking

P34 may block frozen failures. A late new finding may block only when it exposes a material high-impact correctness/safety/security/compatibility/data-integrity/release-critical failure mode not reasonably covered by frozen evidence. Redundant evidence ideas and hardening remain non-blocking successor work.

## P35 Defect Classification

Before fixing, decide which layer owns the defect. Distinguish implementation, spec, Verification Design, Task Package, and non-blocking hardening. Identify affected authority, task, gate, and whether downstream work must be invalidated or regenerated.

## P36 Fix / Reverification

Repair at the owning layer. For implementation-owned repair, re-run the failed frozen evidence plus relevant regression evidence. If upstream authority/Verification/package changed, regenerate downstream execution authority before treating old tasks as current.

A fix is complete only when the original failure and relevant regression obligations are closed against the current frozen contract.
