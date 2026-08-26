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

Project-specific Notion pages, repositories, PRDs, schemas, CI logs, and architecture decisions are read at execution time and classified as Current Authority, Draft/Proposed, Superseded/Historical, Implementation Reality, or Evidence.
