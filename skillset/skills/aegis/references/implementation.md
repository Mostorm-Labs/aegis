# Implementation Execution

## P30 Implementation Planning

Decompose authority into evidence-gated vertical slices, not layers that stay unverifiable until the end. For each slice identify dependencies, implementation scope, mock/reference/oracle, automated verification, observable demo/artifact when useful, performance gate when applicable, and exit criteria.

Do not create one task called "implement the system" when independent gates can prove progress earlier.

## P31 Task Packaging

Each coding-agent task should include:

- Task ID and purpose
- Current authority references
- Inputs/dependencies
- Scope and affected modules/files
- Required changes
- Explicit non-goals
- Required tests and oracle/reference
- Evidence artifacts
- Performance constraints when applicable
- Exit criteria
- What to return when blocked

A good package lets the agent implement without inventing architecture.

## P32 Implementation

Before editing, inspect current repository state and task authority. Implement only the assigned scope. Run the specified verification and collect evidence. If authority is missing or contradictory, stop and return a blocked classification rather than inventing semantics.

Do not weaken tests, redefine requirements, or expand scope merely to make the task pass.

## P33 Resume Interrupted Work

First inspect current branch, local changes/diff, generated artifacts, tests already run, and task authority. Report completed changes and remaining work. Preserve valid existing modifications; do not reset/rollback by default. Resume from the first incomplete verified step.

## P34 Gate Review

Review these independently:

- Authority conformance
- Contract/semantic conformance
- Scope drift
- Required automated tests
- Required oracle/golden/differential evidence
- Performance/resource evidence where applicable
- Platform evidence where applicable
- Demo/observable artifact where required

Agent claims are context, not evidence. Produce a gate verdict and list exact blockers/findings.

## P35 Defect Classification

Before fixing, decide which layer owns the defect. Use the governance taxonomy. Identify affected authority, task, gate, and whether downstream work must be invalidated or rerun.

## P36 Fix / Reverification

Repair at the owning layer. Re-run the failed evidence plus relevant regression evidence. If an upstream authority changed, update supersession and downstream execution packages before treating old implementation tasks as current.

A fix is complete only when the original failure and any relevant regression obligations are closed.
