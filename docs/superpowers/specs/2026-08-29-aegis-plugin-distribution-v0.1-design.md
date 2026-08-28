# Aegis Plugin Distribution v0.1 Design

Status: **Proposed Design Authority v0.1 — human-approved; P30/P31 complete; deterministic implementation exists; catalog/provenance repair amendment accepted 2026-08-29; not Gate-accepted.**

Companion authority: `docs/plugin-distribution-contract-v0.1.md`.
Repair package: `docs/superpowers/plans/2026-08-29-aegis-catalog-provenance-repair.md`.

## 1. Context

Aegis has nine real Skill entrypoints. Plugin Distribution solves a product packaging problem: normal users should install one coherent Aegis product rather than understand and maintain nine internal components.

Installed-platform dogfooding exposed a separate verification fact: ChatGPT can also host the same nine Skills as individually imported entrypoints. Skill Decomposition v0.2 defines Multi-Skill availability from installed-Skill inventory or an equivalent observable platform fact, not from packaging provenance.

The original draft incorrectly modeled:

```text
Plugin provenance -> FULL_SPECIALIST
Standalone provenance -> COMPOSITE_ONLY
```

That mixed two different axes. The repaired model is:

```text
Catalog State != Distribution Provenance
```

## 2. Design Objective

Preserve all of these at once:

1. normal Aegis product distribution is one Plugin containing exact nine Skills;
2. Standalone Aegis remains a one-Skill compatibility distribution;
3. nine Skill entrypoints retain existing ownership/composition semantics;
4. PR #9 Task 6 may test real Skill Composition through any independently proven catalog, including individual Skill imports;
5. packaging provenance remains separately auditable and cannot silently alter runtime ownership;
6. partial/mixed/broken Plugin states still fail closed;
7. Plugin product acceptance remains separate from PR #9 Skill Composition acceptance.

## 3. Product Architecture

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
        preferred distribution        compatibility
                 │                         │
                 ▼                         ▼
            exact 9 Skills             aegis only
```

For development/dogfood, the same Skill components may also be imported individually. That is not the normal product model.

## 4. Component Responsibilities

### Aegis Product

Owns user-facing identity and release semantics. No runtime stage ownership.

### Aegis Plugin

Owns normal packaging, installation coherence, release identity and later whole-catalog upgrade semantics.

It does **not** own lifecycle stages, final answers, Authority repair, Gate verdicts or short-circuit routing.

### Nine Skills

Remain the semantic routing/ownership units inherited from Skill Decomposition v0.2.

### Standalone Aegis

Carries only central `aegis` for compatibility use. It is not a partially installed Plugin.

### Apps

Provide external data/actions/evidence. They never enter the Primary Owner graph.

## 5. Three Independent Questions

Installed-platform evidence must answer three independent questions:

1. **Catalog State** — which Aegis Skill entrypoints are observable?
2. **Release Consistency** — do the observed components belong to one coherent release/component set?
3. **Distribution Provenance** — Plugin, Standalone, individual imports, duplicate, or unknown?

None may be inferred from prompt prose.

## 6. Catalog State

Catalog comparison is set-based; ChatGPT UI ordering is non-semantic.

| State | Meaning | Base runtime consequence |
| --- | --- | --- |
| `FULL_SPECIALIST` | exact nine Aegis Skills observable, coherent release | Multi-Skill candidate |
| `COMPOSITE_ONLY` | only central `aegis` observable for the Aegis family, coherent release | Compatibility candidate |
| `PARTIAL_CATALOG` | any other non-empty subset/shape | `BLOCKED_ENVIRONMENT` |
| `MIXED_REVISION` | component/release observations conflict | `BLOCKED_ENVIRONMENT` |

Non-Aegis Skills such as `skill-creator` are outside this Aegis-family inventory.

## 7. Distribution Provenance

| Provenance | Meaning |
| --- | --- |
| `PLUGIN` | normal Aegis Plugin distribution observed |
| `STANDALONE` | Standalone Aegis distribution observed |
| `INDIVIDUAL_SKILLS` | Aegis Skills imported/installed individually |
| `DUPLICATE_DISTRIBUTION` | conflicting simultaneous distribution provenance without deterministic deduplication |
| `UNKNOWN` | provenance cannot be established |

Provenance is evidence metadata, not a lifecycle owner and not a substitute for catalog inventory.

## 8. Runtime Safety Matrix

```text
PLUGIN + FULL_SPECIALIST
    -> PASS / multi_skill

STANDALONE + COMPOSITE_ONLY
    -> PASS / compatibility

INDIVIDUAL_SKILLS + FULL_SPECIALIST
    -> PASS / multi_skill for PR #9 Task 6

INDIVIDUAL_SKILLS + COMPOSITE_ONLY
    -> PASS / compatibility for PR #9 Task 6

PLUGIN + COMPOSITE_ONLY or PARTIAL_CATALOG
    -> BLOCKED_ENVIRONMENT
    -> never compatibility fallback

STANDALONE + FULL_SPECIALIST or PARTIAL_CATALOG
    -> BLOCKED_ENVIRONMENT

DUPLICATE_DISTRIBUTION
    -> BLOCKED_ENVIRONMENT

UNKNOWN
    -> BLOCKED_EVIDENCE

MIXED_REVISION
    -> BLOCKED_ENVIRONMENT
```

This preserves the central safety invariant: a broken normal installation can never masquerade as intended compatibility.

## 9. Why Manual Installation Is Still Rejected as the Normal Product Model

Individual import is valid verification provenance, but remains a poor normal product experience because:

- users must understand internal architecture;
- partial install is easy;
- upgrades are non-atomic;
- version skew is easier to create;
- product identity is fragmented.

So:

```text
manual nine-Skill import
= admissible Skill Composition dogfood
!= preferred product distribution
```

## 10. Versioning and Upgrade

Use one public Aegis product/Plugin release version. Individual Skills use stable IDs plus exact component digests/revisions pinned by the release.

Plugin upgrades are whole-catalog transitions. If a transition exposes partial/mixed state, runtime work fails closed until coherence is restored.

## 11. Apps

Plugin v0.1 requires no Apps. Future GitHub/Notion Apps may satisfy capability/evidence obligations but never modify stage ownership.

## 12. Authority Dependency

```text
Skill Decomposition v0.2
        ↓
Plugin Distribution v0.1
```

The downstream Plugin contract may constrain product packaging, but may not tighten the upstream Skill Composition Gate by requiring Plugin provenance.

## 13. PR #9 Task 6

Task 6 remains a Skill Composition behavioral Gate.

Unchanged:

- `terminal_trace_v0.2`;
- four protected case IDs/prompts;
- Primary Owner rules;
- support/Router boundaries;
- blocked short-circuit rules;
- compatibility fallback semantics;
- 4/4 PASS threshold.

Environment evidence becomes:

```text
Installed Aegis inventory
        +
release consistency
        +
separate provenance
        ↓
Catalog Evaluation
        ↓
fresh behavior event
        ↓
terminal_trace_v0.2
```

### Environment A

For Cases 1-3:

```text
catalog_state = FULL_SPECIALIST
provenance = PLUGIN | INDIVIDUAL_SKILLS
```

### Environment B

For Case 4:

```text
catalog_state = COMPOSITE_ONLY
provenance = STANDALONE | INDIVIDUAL_SKILLS
```

The prompt's sentence “Only composite Aegis is installed” is never evidence of unavailability; catalog evidence supplies that fact.

## 14. Evidence Separation

```text
Catalog Evidence
!= Behavior Evidence
!= Plugin Product Gate Evidence
```

Catalog Evidence proves installed Aegis availability and release coherence.
Behavior Evidence proves invocation trace, terminal owner and forbidden execution facts.
Plugin Product Gate Evidence proves packaging properties such as one-install provenance and upgrade behavior.

PR #9 requires the first two only.

## 15. Verification Strategy

Deterministic tests must prove:

- exact-nine catalog derives `FULL_SPECIALIST` under Plugin and individual-import provenance;
- aegis-only catalog derives `COMPOSITE_ONLY` under Standalone and individual-import provenance;
- UI order does not affect classification;
- Plugin partial state fails closed and cannot become compatibility;
- Standalone/full mismatch fails closed;
- partial/mixed/duplicate/unknown provenance failures are classified correctly;
- distribution provenance is reported separately;
- no Plugin object becomes a stage owner;
- protected routing/oracle semantics remain unchanged.

Installed-platform dogfood then supplies real catalog and behavior evidence.

## 16. Historical Safety

If PR #9 later passes, preserve that PR #9 originally merged under a non-PASS Gate. `int-pr9` remains historical nonconforming-at-merge truth.

## 17. Non-Goals

This repair does not:

- abandon the one-Plugin normal product architecture;
- make individual import the recommended product install path;
- change Skill ownership/routing;
- change protected Task 6 prompts/oracle;
- require Apps;
- promote Plugin Distribution v0.1 merely because PR #9 Task 6 passes.

## 18. Implementation Boundary

The bounded repair is defined by `docs/superpowers/plans/2026-08-29-aegis-catalog-provenance-repair.md`. Only catalog/provenance evaluation, its deterministic tests, and directly inconsistent Proposed documentation may change. Protected routing semantics remain pinned.
