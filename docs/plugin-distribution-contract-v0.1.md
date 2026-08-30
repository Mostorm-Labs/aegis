# Aegis Plugin Distribution Contract v0.1

Status: **Current Authority v0.1 — P34 Gate accepted; published in Aegis `v0.1.0-beta.2`; PR #13 repository integration closed as current/conforming under Project State v0.5.**

Companion design: `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md`.
Repair package: `docs/superpowers/plans/2026-08-29-aegis-catalog-provenance-repair.md`.

This contract defines how Aegis is packaged and observed without changing the nine-entrypoint ownership semantics defined by `docs/skill-decomposition-v0.2.md`.

The 2026-08-29 P34 installed-platform intake found and corrected one draft defect: the earlier draft coupled runtime **Catalog State** to **Distribution Provenance**. That coupling conflicted with Skill Decomposition v0.2, which allows specialist availability to be proven by installed-Skill inventory or an equivalent observable platform fact. The repair was accepted before the final Plugin Distribution P34 Gate; Git history and the P34 evidence preserve the prior wording and repair lineage.

## 1. Scope

This contract governs:

- Aegis Product, Plugin, Skills, optional Apps, and Standalone Aegis;
- normal product packaging and compatibility packaging;
- installed Aegis catalog classification;
- distribution provenance classification;
- release/component consistency and upgrade safety;
- the catalog-evidence preflight used by PR #9 Task 6.

This contract does **not** change:

- the nine Skill entrypoints;
- P-stage Primary Owner assignments;
- `aegis-project-state` support semantics;
- central `aegis` Router semantics;
- `terminal_trace_v0.2`;
- the four protected PR #9 Task 6 cases;
- the 4/4 behavioral Gate threshold;
- Project State, Execution Surface, or historical Integration truth.

## 2. Product / Distribution Model

```text
Aegis Product
│
├── Aegis Plugin
│   ├── exact 9 Skills
│   └── 0..N optional Apps
│
└── Standalone Aegis
    └── central aegis only
```

Normative distinction:

```text
Product != Plugin != Skill != App
```

- **Product** is the user-facing Aegis offering and release identity.
- **Plugin** is the preferred normal product distribution envelope.
- **Skill** is a reasoning/ownership entrypoint.
- **App** is an external capability/evidence provider and never a lifecycle owner.

The Plugin itself is never a tenth Primary Owner.

## 3. Normal Aegis Plugin Catalog

The normal Plugin contains exactly:

1. `aegis`
2. `aegis-project-state`
3. `aegis-discovery`
4. `aegis-modeling`
5. `aegis-architecture`
6. `aegis-verification`
7. `aegis-governance`
8. `aegis-implementation`
9. `aegis-gate-review`

The Plugin owns packaging/install coherence only. It does not own stages, final answers, Authority repair, Gate verdicts, or runtime short-circuits.

## 4. Standalone Compatibility Distribution

`skills/aegis` remains the Standalone Aegis compatibility distribution.

Normal product guidance should prefer the Plugin. Standalone exists for backward compatibility, single-Skill installation, controlled composite-only use, development, and platforms where Plugin distribution is unavailable.

A broken/partial Plugin must never be reinterpreted as Standalone compatibility.

## 5. Catalog State and Distribution Provenance Are Orthogonal

Normative invariant:

```text
Catalog State != Distribution Provenance
```

These answer different questions:

- **Catalog State:** which Aegis Skill entrypoints are actually observable and whether the observed components belong to one coherent release/component set?
- **Distribution Provenance:** how did those entrypoints arrive in the environment?

PR #9 Task 6 is a **Skill Composition** Gate. Therefore its environment precondition is based on Catalog State plus release consistency. Distribution provenance is recorded separately and must not become an extra semantic acceptance condition.

Plugin Distribution product acceptance is a separate downstream concern and may require `PLUGIN` provenance.

## 6. Installed Catalog Evidence Contract

A normalized snapshot carries independently auditable facts such as:

```yaml
schema_version: "0.1"
fresh_platform_event: true
complete_catalog_capture: true
platform_event_id: <event-id>
surface:
  product: chatgpt
  surface: web | desktop | mobile | other

observed_distributions:
  - kind: plugin | standalone | individual_skills
    id: <provenance-id>
    release_version: <release>

installed_skills:
  - aegis
  - ...

component_release_versions:
  aegis: <release-if-observable>
  ...

release_manifest_ref: <durable release manifest>
materialization_ref: <reviewer-accessible platform evidence>
```

`installed_skills` is an Aegis-family inventory. Non-Aegis Skills such as `skill-creator` do not alter the Aegis catalog state.

Catalog comparison is **set-based**, not UI-order-based. A platform may display the same nine Skills in any order.

## 7. Catalog States

### 7.1 `FULL_SPECIALIST`

Derived when:

- the complete Aegis-family inventory is exactly the expected nine Skills; and
- the observed release/component set is coherent.

Runtime mode: existing Multi-Skill Mode.

Valid provenance for PR #9 Task 6 includes `PLUGIN` or `INDIVIDUAL_SKILLS`.

### 7.2 `COMPOSITE_ONLY`

Derived when:

- the complete Aegis-family inventory contains only central `aegis`; and
- the observed release/component set is coherent.

Runtime mode: existing Composite Compatibility Mode **only when provenance is an intended standalone/single-Skill context**, such as `STANDALONE` or `INDIVIDUAL_SKILLS`.

Specialist unavailability comes from complete catalog evidence, never prompt prose or absence from a partial trace.

### 7.3 `PARTIAL_CATALOG`

Any other non-empty Aegis subset/shape, for example `aegis + aegis-project-state`.

Result: `BLOCKED_ENVIRONMENT`.

### 7.4 `MIXED_REVISION`

The catalog inventory is otherwise classifiable but release/component observations do not resolve to one release/component set.

Result: `BLOCKED_ENVIRONMENT`.

## 8. Distribution Provenance States

Distribution provenance is reported separately:

- `PLUGIN` — Aegis Plugin distribution observed.
- `STANDALONE` — Standalone Aegis distribution observed.
- `INDIVIDUAL_SKILLS` — one or more Aegis Skills imported/installed individually.
- `DUPLICATE_DISTRIBUTION` — incompatible simultaneous distribution provenance, such as Plugin + Standalone, without deterministic deduplication.
- `UNKNOWN` — provenance evidence is missing or not recognized.

`DUPLICATE_DISTRIBUTION` is an environment blocker, not a Catalog State.
`UNKNOWN` is an evidence blocker.

## 9. Provenance Safety Matrix

| Provenance | Catalog State | Result |
| --- | --- | --- |
| `PLUGIN` | `FULL_SPECIALIST` | PASS / `multi_skill` |
| `STANDALONE` | `COMPOSITE_ONLY` | PASS / `compatibility` |
| `INDIVIDUAL_SKILLS` | `FULL_SPECIALIST` | PASS / `multi_skill` for PR #9 Task 6 |
| `INDIVIDUAL_SKILLS` | `COMPOSITE_ONLY` | PASS / `compatibility` for PR #9 Task 6 |
| `PLUGIN` | `COMPOSITE_ONLY` | `BLOCKED_ENVIRONMENT`; incomplete Plugin, never fallback |
| `PLUGIN` | `PARTIAL_CATALOG` | `BLOCKED_ENVIRONMENT` |
| `STANDALONE` | `FULL_SPECIALIST` or `PARTIAL_CATALOG` | `BLOCKED_ENVIRONMENT` |
| `DUPLICATE_DISTRIBUTION` | any | `BLOCKED_ENVIRONMENT` |
| `UNKNOWN` | any | `BLOCKED_EVIDENCE` |
| any recognized provenance | `MIXED_REVISION` | `BLOCKED_ENVIRONMENT` |

This matrix preserves the old safety property: **upgrade/install corruption cannot silently become compatibility mode.**

## 10. Versioning and Upgrade Contract

Aegis exposes one public release line:

```text
Aegis Product 0.x.y == Aegis Plugin 0.x.y
```

Internal Authorities/contracts version independently. Individual Skills use stable IDs plus exact content revisions/digests pinned by the release rather than independent public SemVer lines.

Normal Plugin upgrade is a whole-catalog transition. Partial or mixed intermediate states fail closed and never trigger compatibility fallback.

## 11. Apps Are Orthogonal to Ownership

Apps may provide external data/actions/evidence. They never change the Primary Owner graph.

Example:

```text
aegis-gate-review owns P34
GitHub capability unavailable
-> owner unchanged
-> evidence may be BLOCKED
```

Aegis Plugin v0.1 requires no Apps.

## 12. Authority Dependency

```text
Skill Decomposition v0.2
        ↓
Plugin Distribution v0.1
```

Plugin Distribution packages the topology defined upstream; it does not redefine Skill Composition acceptance.

## 13. PR #9 Task 6 Migration Rule

PR #9 Task 6 remains a Skill Composition behavioral Gate.

Frozen semantics remain unchanged:

- `terminal_trace_v0.2` stays normative;
- four protected case IDs/prompts stay normative;
- Primary Owner, Router, support, short-circuit and fallback semantics stay unchanged;
- PASS still requires 4/4 protected cases PASS.

Only environment evidence is normalized:

```text
Catalog Evidence
    -> Catalog State + separate Distribution Provenance
    -> fresh Behavior Evidence
    -> terminal_trace_v0.2
    -> Task 6 aggregate Gate
```

This remains an **evidence-layer migration, not a semantic Gate migration**.

## 14. Task 6 Environment Mapping

### Cases 1-3

Require:

```text
catalog_state = FULL_SPECIALIST
exact nine Aegis Skills observable
one coherent release/component set
provenance = PLUGIN | INDIVIDUAL_SKILLS
```

Run unchanged:

- `09-01-direct-specialist`
- `09-01-ambiguous-router`
- `09-01-upstream-blocker-reroute`

### Case 4

Require:

```text
catalog_state = COMPOSITE_ONLY
Aegis-family inventory = [aegis]
one coherent release/component set
provenance = STANDALONE | INDIVIDUAL_SKILLS
```

Run unchanged `09-01-composite-fallback`.
Prompt text is never availability evidence.

## 15. Evidence Separation

```text
Catalog Evidence != Behavior Evidence != Distribution Product Gate Evidence
```

Catalog Evidence proves installed Aegis entrypoint availability and release coherence.
Behavior Evidence proves invocation trace, final-answer ownership, terminality and forbidden downstream execution.
Distribution Product Gate Evidence proves Plugin/Standalone packaging properties such as one-install product provenance and upgrade behavior.

PR #9 needs the first two; it does **not** require Plugin productization evidence.

## 16. Historical Integration Safety

A later PASS of `gate-skill-decomposition-v02-pr9` must not rewrite the historical fact that PR #9 physically integrated while its Gate was non-PASS.

`int-pr9` remains a historical nonconforming occurrence for that merge event.

## 17. Exit Criteria

For PR #9 evidence support, this contract must prove:

- exact-nine inventory can derive `FULL_SPECIALIST` independently of Plugin provenance;
- aegis-only inventory can derive `COMPOSITE_ONLY` independently of Standalone wrapper provenance;
- Plugin partial state still fails closed and cannot enter compatibility;
- mixed revision and duplicate provenance fail closed;
- unknown provenance fails closed as evidence gap;
- installed UI order does not alter catalog classification;
- distribution provenance is exposed separately from catalog state;
- `terminal_trace_v0.2` and the protected four cases remain unchanged.

For Plugin Distribution v0.1 product acceptance, the normal Plugin must additionally prove exact-nine materialization and packaging/upgrade safety. That separate product Gate has now passed; this does not change the distinction that PR #9 Task 6 itself only requires catalog and behavior evidence.
