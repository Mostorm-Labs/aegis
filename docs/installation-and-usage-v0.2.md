# Aegis Installation & Usage Guide v0.2

Aegis v0.2 is an evidence-driven software development Control Plane delivered primarily as one native **Aegis Plugin** exposing the exact nine canonical Skills. A portable **9-Skill Installation Kit** remains the fallback path.

Current published prerelease identity: `v0.2.0-beta.4`.

This guide describes the beta.4 distribution and use model.

## Choose an installation path

| Situation | Recommended path |
| --- | --- |
| ChatGPT workspace with Plugin marketplace access | GitHub Plugin |
| Team/developer environment that should update as one product | GitHub Plugin |
| No Plugin marketplace access | 9-Skill Installation Kit |
| Reproducible/offline archive | immutable published Release kit |

For normal product use, prefer the Plugin. The Plugin owns distribution/install coherence; it is not an additional lifecycle owner.

## Recommended: GitHub Plugin

Import the marketplace from the repository root:

```text
https://github.com/Mostorm-Labs/aegis
```

Use the repository-root `.agents/plugins/marketplace.json`. Do not append `/tree/...`, a branch name, or a manifest filename to the source URL.

For a reproducible beta.4 installation, pin the immutable published tag:

```text
v0.2.0-beta.4
```

## Verify the exact-nine catalog

A normal installation must expose exactly:

```text
aegis
aegis-project-state
aegis-discovery
aegis-modeling
aegis-architecture
aegis-verification
aegis-governance
aegis-implementation
aegis-gate-review
```

Acceptance rule:

```text
one Aegis Plugin + exact nine Skills = normal FULL_SPECIALIST installation
partial or mixed Aegis catalog       = incomplete / fail closed
```

UI ordering is not significant; catalog identity is set-based and coherent as one product.

## Alternative: 9-Skill Installation Kit

The published prerelease asset is:

```text
aegis-skill-installation-kit-v0.2.0-beta.4.zip
```

Verify the outer archive against the Release-provided `SHA256SUMS` or `aegis-release-v0.2.0-beta.4.json`, extract the outer archive once, and upload the nine nested Skill ZIPs without unpacking them.

Expected nested archives:

```text
aegis.zip
aegis-project-state.zip
aegis-discovery.zip
aegis-modeling.zip
aegis-architecture.zip
aegis-verification.zip
aegis-governance.zip
aegis-implementation.zip
aegis-gate-review.zip
```

## What beta.4 changes

The distribution model remains Plugin + exact nine Skills. Beta.4 changes the execution and Gate contracts so completion is stable after P31 without weakening real defect detection.

### P20: complete Verification Design before implementation

For each important requirement, Aegis now explicitly maps:

```text
Requirement
→ Invariant
→ Failure Mode
→ Existing Independent Coverage
→ Residual Proof Gap
→ Oracle / Fixture / Exact Execution
→ Evidence Artifact
→ Blocking or Corroborative
→ Gate Criterion
```

Blocking evidence must identify its failure mode, impact, existing independent coverage, unique detection value, and blocking justification. Evidence that only increases confidence in behavior already independently covered remains corroborative.

### P31: freeze an Execution Closure Contract

Every implementation package carries an `EXECUTION_CLOSURE_CONTRACT` covering:

- required and forbidden implementation changes;
- required tests and oracles;
- required versus optional hosted verification;
- blocking versus corroborative evidence;
- terminal success conditions;
- explicit terminal blocker classes;
- `continue_until_terminal_state: true`.

If terminal success is ambiguous or a required oracle/input is missing, repair P20/P31 before coding instead of asking the executor or reviewer to infer the missing finish line.

### P32: execute to terminal state

P32 should continue through all remaining executable items in the frozen closure contract during the same execution. Ordinary repository/API/test uncertainty should be resolved by inspection when possible. P32 stops only for a real terminal blocker such as Authority conflict, missing required input, environment failure, frozen verification failure, or a newly observed high-impact failure mode requiring classification.

Implementation still cannot redesign upstream Authority.

### P33: Resume Interrupted Work, not package expansion

`P33_REPETITION_GUARD` distinguishes interruption from contract defects:

- P31 omitted work -> `TASK_PACKAGE_DEFECT` -> return P31;
- P20 omitted Verification obligation/oracle -> `VERIFICATION_DESIGN_DEFECT` -> return P20;
- frozen implementation failure -> implementation-owned repair after P35;
- real new high-impact uncovered failure -> P35 late-finding classification.

The decision is root-cause based, not a mechanical retry-count rule.

### P34: Gate Closure Stability

Once P31 authorizes implementation, the blocking completion target is frozen.

P34 performs:

```text
Frozen Requirement Audit
+
Frozen Evidence Audit
+
Repository Reality Audit
```

A late finding may newly block only when it exposes a high-impact correctness, safety, security, compatibility, data-integrity, or release-critical failure mode not reasonably covered by the frozen contract. A redundant new evidence idea, confidence improvement, diagnostic, auditability improvement, observability improvement, or hardening task is non-blocking for the current Gate and may be scheduled as successor work.

### Anti-Proof-Recursion Rule

Evidence solely intended to prove another evidence mechanism becomes blocking only when that mechanism is itself a material source of undetected failure, has no independent validation, and its failure could materially change the Gate decision.

This prevents generator -> generator-test -> provenance-validator -> validator-provenance-test recursion when no distinct high-impact failure mode is being detected.

## Assurance profiles

### Lite

Use for small/local, low-blast-radius, easily reversible changes with strong existing tests.

### Standard

Standard is the default for most ordinary feature, bugfix, and module work. An exact PR/result SHA, required local tests, applicable hosted CI, artifact identity when relevant, and reviewer-accessible logs/evidence are normally sufficient when they credibly cover the frozen failure modes.

An evidence-only descendant, clean-room reproduction, formal provenance graph, or negative generator test suite is **not mandatory** merely as ritual.

### Full

Full requires explicit profile justification. Examples include protocol/schema release, security-critical behavior, data-integrity-critical behavior, cross-language conformance, formal SDK release, irreversible migration, or regulated/high-assurance work.

Full may retain exact source freeze, clean checkout, exact hosted provider identity, materialized evidence, provenance, and independent oracle requirements. It remains subject to the Anti-Proof-Recursion Rule.

## Existing v0.2 strengths remain

Beta.4 preserves:

- Current Authority and durable Project State as explicit control inputs;
- Earliest Untrusted Layer routing;
- Authority Review, Five-Axis Drift Review, and Authority Supersession;
- failure-mode-first blocking evidence qualification;
- `Missing Evidence != Automatically Gate Blocked` while preserving `Code Complete != Gate Complete`;
- `Task Anchor != Execution Cursor` and controlled interrupted-work resume;
- independent Gate ownership;
- repository identity preflight before package/anchor/cursor reasoning;
- fail-closed handling for unavailable, ambiguous, or mismatched repository identity;
- integration occurrence versus Gate conformance distinction.

A bare revision is not a repository locator.

## How to use Aegis

Users normally start with the task itself or a routing question such as:

```text
What should this project do next?
```

Aegis determines the earliest untrusted layer, Current Authority, evidence obligations, selected assurance profile, and owning stage. The central `aegis` Skill owns genuine routing ambiguity; specialist Skills retain substantive stage ownership.

Simplified flow:

```text
User task
   ↓
Aegis routing / project-state preflight
   ↓
P20 Verification closure
   ↓
P31 frozen Execution Closure Contract
   ↓
P32 execute to terminal state
   ↓
P34 frozen-obligation Gate audit
   ├─ satisfied -> PASS / PASS_WITH_FINDINGS
   └─ real uncovered high-impact defect -> BLOCK / P35
```

Under current Authority, substantive work owned by different Primary Skills does **not** silently chain across Primary boundaries in one user turn. A completed stage may identify the next owner, but that does not itself authorize the next Primary's substantive stage.

## Repository-backed execution

Repository-backed P31/P32/P33/P36 handoffs carry an explicit repository identity, a same-repository package materialization ref, and a task anchor when a trusted repository ancestry baseline is required.

The execution order is fail-closed:

```text
repository identity
→ declared-repository checkout/worktree
→ package resolution in that repository
→ package materialization repository match
→ task-anchor ancestry
→ resume-cursor classification when applicable
→ authored mutation
```

If the declared repository cannot be established, Aegis must not substitute an ambient checkout or use a bare SHA to infer another repository.

## Updating

Aegis Plugin updates are whole-catalog transitions. After a GitHub-backed marketplace update or **Sync now**, verify the exact-nine catalog before relying on the new state.

Do not accept a partial or mixed Aegis catalog. For reproducibility, pin an immutable published tag or use its Release kit.

## Rollback boundary

The current prerelease is:

```text
v0.2.0-beta.4
```

Earlier immutable published boundaries remain available for rollback and historical reproduction:

```text
v0.2.0-beta.3
v0.2.0-beta.2
v0.2.0-beta.1
v0.1.0-beta.3
```

Their published manifests, notes, tags, Releases, and assets remain historical and unchanged.

## Deliberate product boundaries

Aegis v0.2 does not claim:

- a required standalone daemon or hosted Control Service;
- R0/S0/W7D service-scale qualification;
- `SERVICE_PROFILE` authorization;
- rollout expansion beyond the accepted Plugin profile;
- zero-user-turn cross-Primary substantive chaining.

## Troubleshooting

- **Fewer than nine Aegis Skills are visible:** treat the installation as incomplete.
- **Mixed old/new Aegis Skills are present:** restore one coherent catalog before use.
- **Implementation keeps returning after code/test checkpoints:** inspect the P31 `EXECUTION_CLOSURE_CONTRACT`; required executable closure items should be completed before normal return.
- **P33 repeatedly adds reviewer-requested work:** classify root cause; package omissions belong to P31, Verification omissions to P20, redundant hardening is non-blocking.
- **P34 proposes an extra proof:** require a distinct uncovered high-impact failure mode and unique detection value before it can block.
- **Installation Kit was unpacked too far:** upload the nine nested ZIP files, not their unpacked directories.
- **Repository-backed handoff resolves the wrong repository:** stop; repository identity must be resolved before package/anchor/cursor reasoning.
- **Declared repository is unavailable:** return `BLOCKED_REPOSITORY_IDENTITY`; do not substitute another checkout.
- **Need a reproducible historical environment:** use an immutable published tag and its Release assets, including `v0.2.0-beta.3`, `v0.2.0-beta.2`, `v0.2.0-beta.1`, or `v0.1.0-beta.3` when reproducing earlier behavior.

## References

- distribution semantics: [`plugin-distribution-contract-v0.1.md`](plugin-distribution-contract-v0.1.md)
- prior v0.1 guide: [`installation-and-usage-v0.1.md`](installation-and-usage-v0.1.md)
- beta.4 release notes: [`releases/v0.2.0-beta.4.md`](releases/v0.2.0-beta.4.md)
- previous beta.3 release notes: [`releases/v0.2.0-beta.3.md`](releases/v0.2.0-beta.3.md)
- previous beta.2 release notes: [`releases/v0.2.0-beta.2.md`](releases/v0.2.0-beta.2.md)
