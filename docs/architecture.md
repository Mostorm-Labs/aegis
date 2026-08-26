# Aegis Plugin Architecture

## v0.1 shape

Aegis v0.1 deliberately ships as **one installable Skill**.

The entrypoint is a compact control plane. Detailed process knowledge is moved into references and loaded progressively only when the routed stage needs it.

```text
User request / project state
        |
        v
     Aegis
        |
        +-- Bootstrap Router
        |     \-- Earliest Untrusted Layer
        |
        +-- Discovery / Design references
        +-- Verification / Governance references
        +-- Implementation references
        +-- Output contracts
        \-- Superpowers composition rules
```

## Why not 25 Skills immediately

A multi-Skill suite is likely the long-term architecture, but v0.1 first needs evidence about:

- which stages are frequently invoked independently;
- where auto-trigger descriptions become ambiguous;
- which references are consistently co-loaded;
- whether routing should remain centralized;
- which implementation stages should be delegated entirely to Superpowers.

Prematurely splitting all stages would create trigger and maintenance complexity before real usage evidence exists.

## Persistent project-control state

Aegis may optionally consume a project-owned `.aegis/` directory:

```text
.aegis/
├── project.json
├── authorities.json
├── gates.json
├── evidence.json
└── state.json
```

The first four files are authored control metadata; `state.json` is a deterministic generated projection. This layer reduces repeated project-state reconstruction, makes validity dependencies machine-readable, and allows supersession to invalidate downstream authority/gates without rewriting historical Gate verdicts.

The project-state layer does **not** become a new product/design authority. It points to and validates existing authority. If manifest metadata conflicts with a Current PRD/ADR/schema/architecture source, Aegis routes to Authority Review instead of silently preferring the manifest.

See `docs/project-state-manifest-v0.1.md`.

## Future suite boundary

Likely high-value independent Skills include:

- aegis-bootstrap
- problem-discovery
- authority-review
- verification-design
- architecture-review
- task-packaging
- gate-review
- defect-classification
- release-readiness

Other low-frequency stages may remain reference-driven under a shared Aegis router.

## Authority boundary

Aegis itself is reusable process authority. It must not embed private product authority.

Project-specific Notion pages, repositories, PRDs, schemas, CI logs, architecture decisions, and `.aegis/` manifests are read at execution time and classified as Current Authority, Draft/Proposed, Superseded/Historical, Implementation Reality, Evidence, or project-control metadata as appropriate.
