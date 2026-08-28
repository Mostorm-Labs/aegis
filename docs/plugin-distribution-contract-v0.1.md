# Aegis Plugin Distribution Contract v0.1

Status: **Proposed Authority v0.1 — conceptual design approved in chat; written-spec human review pending; implementation not authorized.**

Companion design: `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md`.

This contract defines how the Aegis product is distributed without changing the existing nine-entrypoint ownership semantics. It depends on `docs/skill-decomposition-v0.2.md` for runtime ownership/composition semantics and does not supersede that Authority.

## 1. Scope

This contract governs:

- the relationship between Aegis Product, Aegis Plugin, Aegis Skills, optional Apps, and Standalone Aegis;
- the normal installed catalog and compatibility catalog;
- catalog-state classification and fail-closed behavior;
- release, component-revision, and contract versioning;
- upgrade semantics;
- the distribution-aware evidence preflight used by PR #9 Task 6.

This contract does **not** change:

- the nine Skill entrypoints;
- P-stage Primary Owner assignments;
- `aegis-project-state` support semantics;
- central `aegis` Router semantics;
- `terminal_trace_v0.2`;
- the four protected PR #9 Task 6 behavioral cases;
- Gate thresholds or defect taxonomy;
- Project State, Execution Surface, or repository integration semantics.

## 2. Product / Distribution Model

Aegis has one product identity and two distribution forms:

```text
Aegis Product
│
├── Aegis Plugin
│   ├── 9 Skills
│   └── 0..N optional Apps
│
└── Standalone Aegis
    └── composite aegis only
```

Normative distinction:

```text
Product != Plugin != Skill != App
```

- **Product** is the user-facing Aegis offering and release identity.
- **Plugin** is the normal installation/distribution envelope.
- **Skill** is a reasoning/ownership unit governed by Skill Decomposition Authority.
- **App** is an external data/action capability and never a lifecycle owner.

## 3. Normal Aegis Plugin Catalog

The normal Aegis Plugin contains exactly these nine Skills:

| Skill | Role / ownership |
| --- | --- |
| `aegis` | central Router, routing-only answers, accepted blocked short-circuit, compatibility facade |
| `aegis-project-state` | Project State direct owner / cross-cutting support |
| `aegis-discovery` | P00-P03 |
| `aegis-modeling` | P10-P13 |
| `aegis-architecture` | P14-P18 |
| `aegis-verification` | P20 |
| `aegis-governance` | P21-P24 |
| `aegis-implementation` | P30-P33 |
| `aegis-gate-review` | P34-P36 |

The Plugin itself has no P-stage ownership, final-answer ownership, Authority-repair power, or Gate-verdict power.

> Plugin installation changes the capability envelope, not the ownership graph.

## 4. Standalone Compatibility Distribution

`skills/aegis` remains available as the **Standalone Aegis Compatibility Distribution**.

Its purposes are limited to:

- backward compatibility;
- single-Skill installation;
- development/platform fallback where Plugin distribution is unavailable;
- controlled composite-only dogfooding.

Normal product guidance should prefer the Aegis Plugin, not manual specialist installation.

A valid compatibility runtime requires:

```text
distribution = standalone
installed Aegis catalog = [aegis]
runtime mode = COMPOSITE_COMPATIBILITY
```

A partial Plugin catalog is not compatibility mode.

## 5. Installed Catalog Contract

Aegis must distinguish platform-observable installation state from behavior traces.

Conceptual installed-catalog snapshot:

```yaml
aegis_release: 0.x.y

distribution:
  kind: plugin | standalone
  id: aegis

skillset_contract_version: "0.2"

installed_skills:
  - aegis
  - aegis-project-state
  - ...

component_revisions:
  aegis: <digest-or-revision>
  aegis-project-state: <digest-or-revision>
  ...

surface:
  product: chatgpt
  surface: web | desktop | mobile | other

apps:
  github:
    state: connected | available | unavailable
  notion:
    state: connected | available | unavailable

evidence_ref: <reviewer-accessible platform evidence>
```

The exact machine-readable representation is implementation-owned and requires a later P30/P31 package; the semantic state model below is normative now.

## 6. Catalog States

Aegis v0.1 defines five distribution/catalog states.

### 6.1 `FULL_SPECIALIST`

Valid normal mode only when:

- distribution provenance is Aegis Plugin;
- all nine expected Aegis Skills are observable;
- all nine belong to one Aegis release/component set;
- no duplicate standalone distribution creates ambiguous provenance.

Runtime semantics use existing Multi-Skill Mode.

### 6.2 `COMPOSITE_ONLY`

Valid compatibility mode only when:

- distribution provenance is Standalone Aegis;
- only central `aegis` is installed for Aegis;
- relevant specialist unavailability is proven by installed-catalog evidence, not inferred from a prompt or partial trace.

Runtime semantics use existing Composite Compatibility Mode.

### 6.3 `PARTIAL_CATALOG`

Examples include `aegis + aegis-project-state` or a Plugin installation missing one or more expected specialists.

Result: `BLOCKED_ENVIRONMENT` for normal specialist-owned execution. Do not silently enter compatibility fallback.

### 6.4 `MIXED_REVISION`

The expected catalog is present but component revisions do not belong to one release/component set.

Result: `BLOCKED_ENVIRONMENT` until catalog consistency is restored.

### 6.5 `DUPLICATE_DISTRIBUTION`

Plugin and Standalone Aegis are simultaneously present and platform behavior cannot prove deterministic deduplication/provenance.

Result: `BLOCKED_ENVIRONMENT`.

## 7. Fallback Safety Rule

Compatibility fallback is valid only when specialist unavailability is a proven property of the intended standalone distribution.

Forbidden inference:

```text
specialist not seen in trace
-> assume unavailable
-> central aegis executes specialist work
```

Forbidden recovery:

```text
Plugin catalog incomplete during install/upgrade
-> treat missing specialist as compatibility condition
```

Required behavior for incomplete/mixed Plugin state:

```text
BLOCKED_ENVIRONMENT
```

## 8. Versioning

Versioning is three-layered.

### 8.1 Product / Plugin Release

Aegis exposes one release version:

```text
Aegis Product 0.x.y == Aegis Plugin 0.x.y
```

Do not maintain an independent public Plugin version line.

### 8.2 Internal Authority / Contract Versions

Internal contracts version independently, for example:

- Skill Decomposition v0.2;
- Project State v0.4;
- Execution Surface v0.1;
- Plugin Distribution v0.1.

These are not product release numbers.

### 8.3 Skill Component Revisions

Individual Skills do not expose independent SemVer lines. Each has:

- stable `skill_id`;
- exact content revision/digest pinned by the Aegis release.

The Plugin and Standalone distributions must derive central `aegis` from the same canonical source revision for a given release.

## 9. Upgrade Contract

Normal upgrades occur at the Plugin/release level:

```text
Aegis Plugin X
-> whole catalog transition
-> Aegis Plugin Y
```

The desired externally observable states are old-complete or new-complete. If the platform exposes an intermediate mixed/partial catalog, Aegis classifies it as `PARTIAL_CATALOG` or `MIXED_REVISION` and fails closed.

Upgrade state must never trigger compatibility fallback.

## 10. Apps Are Orthogonal to Ownership

Apps may provide external data, actions, or evidence. They do not change the Primary Owner graph.

Example:

```text
aegis-gate-review owns P34
GitHub App supplies repository / PR / CI evidence
```

If GitHub is unavailable, P34 ownership remains `aegis-gate-review`; the result may be `BLOCKED_EVIDENCE` or `BLOCKED_ENVIRONMENT` depending on the missing obligation.

Aegis Plugin v0.1 should initially require no Apps. GitHub/Notion integrations may be added later as optional capabilities under separate Authority/Gate work.

## 11. Authority Dependency

Normative dependency direction:

```text
Skill Decomposition v0.2
        ↓
Plugin Distribution v0.1
```

Plugin Distribution v0.1 depends on Skill Decomposition v0.2 because it packages the topology and ownership system defined there.

A test Plugin artifact may exist before this Authority becomes Current. Test artifact existence is implementation/evidence, not Authority promotion.

## 12. PR #9 Task 6 Migration Rule

PR #9 Task 6 remains a **Skill Composition behavioral Gate**. It does not become a Plugin Distribution Gate.

Frozen semantic acceptance remains unchanged:

- `terminal_trace_v0.2` stays normative;
- the four protected cases stay normative;
- Primary Owner, Router, support, short-circuit, and fallback semantics stay unchanged;
- PASS still requires all four protected cases to PASS.

Only the **catalog evidence provider** changes.

Old evidence setup:

```text
manual individual Skill installation
-> screenshot/inventory inference
-> catalog mode
```

Migration target:

```text
distribution evidence
-> Installed Catalog Snapshot
-> derived catalog mode
-> fresh platform behavior event
-> terminal_trace_v0.2
-> Task 6 aggregate Gate
```

This is an **evidence-layer migration, not a semantic Gate migration**.

## 13. Task 6 Environment Mapping

### Cases 1-3

Use a test-only Aegis Plugin distribution whose observable catalog derives `FULL_SPECIALIST`.

Run the unchanged protected cases:

- `09-01-direct-specialist`;
- `09-01-ambiguous-router`;
- `09-01-upstream-blocker-reroute`.

The existing behavioral outcomes remain required.

### Case 4

Use Standalone Aegis with observable `COMPOSITE_ONLY` catalog evidence.

Run the existing `09-01-composite-fallback` case without treating prompt text as unavailability proof.

A stronger future regression may use a neutral prompt such as `Design a semantic schema.` with standalone catalog evidence, but that is outside PR #9 closure and must not move the current protected Gate.

## 14. Evidence Separation

For installed-platform acceptance:

```text
Catalog Evidence != Behavior Evidence
```

Catalog evidence proves availability/provenance/revision state.
Behavior evidence proves invocation trace, ownership, terminality, and downstream execution behavior.

Conceptually each protected case should be auditable through both references, whether represented as separate artifacts or a normalized wrapper with explicit sub-references.

## 15. Historical Integration Safety

A later PASS of `gate-skill-decomposition-v02-pr9` must not rewrite the historical fact that PR #9 was physically integrated while its Gate was non-PASS.

`int-pr9` remains a historical nonconforming occurrence for that integration event. A later Gate closure and Authority promotion establish current trust through new evidence/governance records; they do not launder the old merge.

## 16. Exit Criteria for Plugin Distribution v0.1 Implementation

Implementation of this Authority is not authorized until the companion design is reviewed and a P30/P31 implementation plan is approved.

Its eventual Gate must at minimum prove:

- one normal Plugin installation exposes the exact nine-Skill catalog;
- Standalone exposes only central `aegis` for compatibility testing;
- partial/mixed/duplicate catalogs fail closed;
- component revisions are release-consistent;
- Plugin packaging does not create a new lifecycle owner;
- optional App availability does not alter ownership;
- Task 6 catalog evidence can be independently resolved without changing `terminal_trace_v0.2` semantics.
