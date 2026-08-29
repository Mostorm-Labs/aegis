# Superpowers Integration

Aegis and Superpowers are complementary.

Aegis owns the project-level control plane:

- correct problem and requirement routing;
- domain/semantic/architecture authority;
- contract and verification design;
- authority/drift/supersession governance;
- evidence-gated task packaging and gate review;
- release readiness.

Superpowers, when available, owns proven coding-agent mechanics. Prefer composition instead of rewriting them.

## Recommended mapping

- New implementation still has design ambiguity -> `superpowers:brainstorming` before implementation.
- Multi-step implementation plan -> `superpowers:writing-plans`.
- Feature/bug code implementation -> `superpowers:test-driven-development`.
- Execute an approved written implementation plan -> `superpowers:executing-plans` or its supported equivalent.
- Unexpected failure/bug -> `superpowers:systematic-debugging`.
- Before integration/merge -> `superpowers:requesting-code-review` where useful.
- Review feedback -> `superpowers:receiving-code-review`.
- Before claiming completion -> `superpowers:verification-before-completion`.

## Boundary rule

Superpowers coding workflows do not override Aegis Current Authority. If a coding workflow discovers that the specification or authority is wrong, stop the implementation path, classify the issue in Aegis (`P35`), repair/supersede the correct authority, then regenerate the implementation package.

## If Superpowers is not available

Follow Aegis `P30-P36` directly. Require plan/task boundaries, tests/evidence, systematic root-cause classification, and verification-before-completion behavior, but do not pretend unavailable skills were invoked.
