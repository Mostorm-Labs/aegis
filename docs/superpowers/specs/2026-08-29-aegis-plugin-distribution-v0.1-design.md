# Aegis Plugin Distribution v0.1 Design

Status: **Proposed Design Authority v0.1 — conceptual design approved in chat; written-spec human review pending; implementation not authorized.**

Companion authority: `docs/plugin-distribution-contract-v0.1.md`.

## 1. Context

Aegis currently has a nine-entrypoint Skill architecture in the repository, but installed-platform Task 6 dogfooding exposed an important distribution ambiguity: a user may install only a subset of those Skills and accidentally create a state such as `aegis + aegis-project-state`. That state is neither the intended full multi-Skill catalog nor the intended composite-only compatibility catalog.

The product problem is therefore distinct from Skill Decomposition:

- Skill Decomposition answers **how Aegis internally owns and routes work**.
- Plugin Distribution answers **how that internally consistent system is installed, versioned, upgraded, and observed as one product**.

The design goal is to make normal installation atomic at the product boundary while preserving the existing Single-Owner Composition semantics underneath.

## 2. Design Objective

Freeze a distribution architecture in which:

1. the user installs one normal Aegis product package;
2. that package exposes the exact nine-Skill catalog;
3. the nine Skills keep their current ownership/composition semantics;
4. a separate standalone composite Aegis remains available only for compatibility and controlled fallback testing;
5. Apps remain orthogonal capability providers;
6. catalog provenance/version consistency becomes explicit evidence;
7. PR #9 Task 6 can migrate its environment evidence without moving its semantic acceptance oracle.

## 3. Alternatives Considered

### 3.1 Manual nine-Skill installation

Each Skill is uploaded/installed independently.

Advantages:

- minimal repository packaging change;
- direct visibility of each Skill.

Rejected as the normal product model because:

- users must understand internal architecture;
- partial installation is easy;
- version skew is likely;
- upgrade is non-atomic;
- Task 6 cannot easily distinguish intentional compatibility from accidental missing specialists.

Manual installation remains useful only for narrow development/debug scenarios.

### 3.2 Recombine everything into one composite Skill

Return to one `aegis` Skill with specialist logic as references.

Rejected because it destroys the point of the accepted nine-entrypoint architecture: specialist discovery, unique Primary Owner semantics, support boundaries, and installed-platform composition behavior become invisible or simulated rather than real.

### 3.3 One Plugin containing nine Skills + separate Standalone Aegis — Selected

Normal users install one Aegis Plugin that carries the full catalog. Standalone Aegis exists independently as a compatibility distribution.

This keeps installation simple without collapsing internal ownership boundaries.

## 4. Product Architecture

```text
                         AEGIS PRODUCT
                              │
                              ▼
                         Aegis Release
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
            AEGIS PLUGIN            STANDALONE AEGIS
        normal distribution          compatibility
                 │                         │
                 ▼                         ▼
            exact 9 Skills             aegis only
                 │                         │
                 ▼                         ▼
           FULL_SPECIALIST          COMPOSITE_ONLY
                 │                         │
                 └────────────┬────────────┘
                              ▼
                       Runtime Selection
                              │
                              ▼
                 Single-Owner Composition
```

Apps attach laterally and do not enter the ownership graph.

## 5. Component Responsibilities

### 5.1 Aegis Product

Owns user-facing identity and release semantics. It does not participate in runtime routing.

### 5.2 Aegis Plugin

Owns normal packaging and installation coherence.

Responsibilities:

- include/pin the expected nine Skills;
- expose one product release identity;
- make the expected installed catalog auditable;
- optionally declare App dependencies/capabilities in future releases.

Non-responsibilities:

- stage ownership;
- final-answer ownership;
- Authority repair;
- Gate verdicts;
- runtime short-circuit decisions.

### 5.3 Nine Skills

Remain the only semantic routing/ownership units. Their topology and roles are inherited from Skill Decomposition v0.2.

### 5.4 Standalone Aegis

A compatibility distribution that carries only the composite central `aegis` Skill. It is not a partially installed Plugin and should have explicit standalone provenance.

### 5.5 Apps

Provide external data and actions such as GitHub/Notion access. App availability can satisfy or block evidence obligations but never changes who owns a lifecycle stage.

## 6. Installed Catalog Model

The platform-facing contract needs a normalized catalog snapshot with enough evidence to answer three separate questions:

1. **Distribution provenance** — Plugin or Standalone?
2. **Component completeness** — which expected Skills are observable?
3. **Release consistency** — do all observed components belong to one release/component set?

The snapshot should not be inferred from user prose. It must come from platform-observable installation/distribution evidence where possible.

Derived states:

| State | Meaning | Runtime consequence |
| --- | --- | --- |
| `FULL_SPECIALIST` | Plugin provenance + exact nine Skills + one release set | existing Multi-Skill Mode |
| `COMPOSITE_ONLY` | Standalone provenance + only `aegis` | existing Composite Compatibility Mode |
| `PARTIAL_CATALOG` | expected Plugin catalog incomplete | `BLOCKED_ENVIRONMENT` |
| `MIXED_REVISION` | catalog spans incompatible release/component revisions | `BLOCKED_ENVIRONMENT` |
| `DUPLICATE_DISTRIBUTION` | Plugin + Standalone ambiguity without deterministic deduplication | `BLOCKED_ENVIRONMENT` |

## 7. Why Partial Catalog Must Fail Closed

A partial Plugin install cannot safely be treated as compatibility mode.

Without this rule, an installation or upgrade defect can silently alter semantic ownership:

```text
missing aegis-modeling
-> central aegis assumes specialist unavailable
-> central aegis owns P12
```

That would turn distribution corruption into legitimate runtime behavior.

The selected rule is:

```text
intended standalone absence -> compatibility may execute
unexpected Plugin absence   -> BLOCKED_ENVIRONMENT
```

This preserves the meaning of specialist availability evidence.

## 8. Versioning Design

### 8.1 One public release line

Use a single Aegis product version. The Plugin release version is the product version.

```text
Aegis Product 0.x.y == Aegis Plugin 0.x.y
```

### 8.2 Independent internal contract versions

Authority/contract versions remain independent because they describe different semantics, not product packaging chronology.

Examples:

- Skill Decomposition v0.2;
- Project State v0.4;
- Execution Surface v0.1;
- Plugin Distribution v0.1.

### 8.3 No public per-Skill SemVer matrix

Each Skill keeps a stable identifier plus exact revision/digest pinned by the release. This avoids an unnecessary 9-dimensional compatibility matrix.

### 8.4 Canonical-source rule

For a given Aegis release, the central `aegis` component inside the Plugin and the Standalone package must derive from the same canonical source revision.

## 9. Upgrade Design

Upgrade occurs at the Plugin/release level rather than per Skill.

Desired observable transition:

```text
complete release X
-> upgrade
-> complete release Y
```

If the platform exposes an intermediate partial/mixed state, runtime work fails closed until coherence is restored.

Upgrade must never be used as evidence that compatibility fallback is legitimate.

## 10. Apps Design

Plugin v0.1 should be **Skills-only** from an Aegis contract perspective: no App is required for core installation or Task 6 closure.

Future optional Apps may include GitHub and Notion. Their role is capability/evidence only.

Example:

```text
P34 owner = aegis-gate-review
GitHub App unavailable
-> owner unchanged
-> evidence may be BLOCKED
```

This prevents OAuth/workspace policy from becoming an accidental dependency of Skill Decomposition closure.

## 11. Authority Dependency

Plugin Distribution v0.1 is downstream of Skill Decomposition v0.2:

```text
Skill Decomposition v0.2
        ↓
Plugin Distribution v0.1
```

The Plugin packages the topology; it does not define it.

Because Skill Decomposition v0.2 is still Proposed/BLOCKED_EVIDENCE, Plugin Distribution v0.1 must remain Proposed during the Task 6 test-build phase.

A test build is permitted as evidence tooling. It is not sufficient for Authority promotion.

## 12. PR #9 Task 6 Migration Decision

The Task 6 semantic target is frozen and must not be replaced by a Plugin Gate.

### Unchanged normative elements

- `terminal_trace_v0.2`;
- all four protected case IDs;
- Primary Owner rules;
- support/Router boundaries;
- blocker short-circuit rules;
- compatibility fallback semantics;
- 4/4 PASS threshold.

### Changed evidence layer

Task 6 gains a distribution-aware catalog preflight:

```text
distribution evidence
        ↓
Installed Catalog Snapshot
        ↓
derived catalog mode
        ↓
fresh platform event
        ↓
terminal_trace_v0.2
        ↓
Task 6 aggregate verdict
```

This is explicitly an **evidence-layer migration, not a semantic Gate migration**.

## 13. Task 6 Environment Mapping

### Environment A — Plugin test build

Requirements:

- one Aegis Plugin test build;
- platform-observable exact nine-Skill catalog;
- release/component revisions consistent;
- derived state `FULL_SPECIALIST`.

Run unchanged:

1. `09-01-direct-specialist`;
2. `09-01-ambiguous-router`;
3. `09-01-upstream-blocker-reroute`.

### Environment B — Standalone Aegis

Requirements:

- standalone distribution provenance;
- only central `aegis` observable;
- derived state `COMPOSITE_ONLY`.

Run unchanged:

4. `09-01-composite-fallback`.

The case's prompt text cannot serve as the evidence that `aegis-modeling` is unavailable. Availability comes from the catalog evidence.

A future neutral-prompt regression may test `Design a semantic schema.` under standalone-only evidence, but that is outside current PR #9 acceptance.

## 14. Evidence Model

Separate two truths that were previously conflated:

```text
Catalog Evidence != Behavior Evidence
```

Catalog Evidence proves:

- distribution provenance;
- installed Skill inventory;
- specialist availability/unavailability;
- component release/revision consistency.

Behavior Evidence proves:

- complete terminal invocation trace;
- final answer owner;
- support/primary/router roles;
- blocker/ambiguity facts;
- downstream substantive-execution count;
- cycle/loop observations.

The Task 6 evaluator may represent these as separate artifact references or as a normalized wrapper, but each truth must remain independently auditable.

## 15. Historical PR #9 Integration

If fresh Task 6 evidence later causes `gate-skill-decomposition-v02-pr9` to PASS, Project State must preserve that PR #9 originally merged while the Gate was non-PASS.

Later acceptance changes current trust and Authority status; it does not rewrite the historical integration occurrence into a conforming-at-merge event.

## 16. Error Handling

Distribution errors fail closed before specialist behavioral acceptance.

- missing catalog evidence -> `BLOCKED_EVIDENCE`;
- unavailable test environment / platform cannot expose required catalog mode -> `BLOCKED_ENVIRONMENT`;
- partial/mixed/duplicate catalog -> `BLOCKED_ENVIRONMENT`;
- complete catalog but wrong routing/ownership trace -> behavioral `FAIL` with existing v0.2 violation classes;
- complete catalog + incomplete terminal trace -> `BLOCKED_EVIDENCE`.

The evaluator must not convert an environment/catalog defect into `ROUTER_OWNERSHIP_LEAK` unless specialist availability is independently established.

## 17. Verification Strategy

Implementation must prove at least these layers independently:

### 17.1 Deterministic repository tests

- expected Plugin catalog = exactly nine known Skills;
- standalone catalog = only `aegis`;
- state derivation for all five catalog states;
- same-release revision consistency;
- no Plugin object is introduced as a Primary Owner;
- Apps do not modify the ownership map;
- existing `terminal_trace_v0.2` tests remain unchanged/green.

### 17.2 Package validation

- test Plugin package includes the nine expected Skill bundles;
- standalone package derives central `aegis` from the same canonical source revision;
- package manifest/version data is deterministic.

### 17.3 Installed-platform dogfood

- Environment A yields reviewer-accessible `FULL_SPECIALIST` evidence;
- Environment B yields reviewer-accessible `COMPOSITE_ONLY` evidence;
- four protected Task 6 traces rerun fresh;
- evaluator obtains 4/4 PASS before P34 can accept Skill Decomposition v0.2.

## 18. Non-Goals

v0.1 does not attempt to:

- require GitHub/Notion Apps;
- design a general third-party App plugin ecosystem;
- change Aegis lifecycle stages;
- change Execution Surface routing;
- invent per-Skill public SemVer;
- silently migrate existing partial personal installations;
- make PR #9 historically conforming;
- merge or promote any Authority merely because a test Plugin is built.

## 19. Implementation Boundary

No Plugin packaging code, catalog schema/tooling, Task 6 manifest migration, or Skill text change is authorized by this document alone.

Next required sequence after written-spec approval:

```text
P30 implementation plan
        ↓
P31 task packages
        ↓
RED-first deterministic catalog contract
        ↓
test-only Plugin distribution
        ↓
Task 6 evidence-layer migration
        ↓
installed-platform rerun
        ↓
P34
```
