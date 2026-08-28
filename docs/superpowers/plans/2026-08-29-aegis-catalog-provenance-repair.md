# Aegis Catalog / Provenance Decoupling Repair

Status: **P31 bounded repair package — approved by user 2026-08-29; authority repair required before Task 6 evidence acceptance.**

## Finding

PR #13 P34 installed-platform intake exposed a contradiction between upstream Skill Decomposition v0.2 and Plugin Distribution v0.1:

- `docs/skill-decomposition-v0.2.md` defines Multi-Skill availability from installed-Skill inventory or equivalent observable platform fact; it does not require Plugin provenance.
- Plugin Distribution v0.1 coupled `FULL_SPECIALIST` to Aegis Plugin provenance and `COMPOSITE_ONLY` to Standalone provenance.
- Real ChatGPT platform evidence shows exact nine independently imported Aegis Skills can exist as nine real entrypoints, and central `aegis` can exist alone without a Plugin/Standalone wrapper.

Classification:

```text
Primary   = SPEC_DEFECT
Secondary = AUTHORITY_CONFLICT
Earliest untrusted layer = Proposed Authority / evidence contract
```

## Repair invariant

```text
Catalog State != Distribution Provenance
```

Catalog state answers what Aegis entrypoints are actually available and whether their release set is coherent.
Distribution provenance answers how those entrypoints were installed or packaged.

PR #9 Task 6 is a Skill Composition Gate, so its environment precondition may use independently imported Skills when catalog evidence proves the required state. Plugin Distribution product acceptance remains a separate downstream Gate that may require Plugin provenance.

## Frozen boundaries

This repair must not change:

- `tools/aegis_skillset/routing.py` / `terminal_trace_v0.2` semantics;
- the four protected Task 6 case IDs/prompts;
- Primary Owner / Router / support / blocked-short-circuit semantics;
- `skillset/dogfood/installed-platform-rerun-v0.2.json` bytes;
- the 4/4 Task 6 threshold;
- historical `int-pr9` nonconforming-at-merge truth.

## Data model

Catalog states:

- `FULL_SPECIALIST` — exact nine Aegis Skills observable, one coherent release/component set.
- `COMPOSITE_ONLY` — only central `aegis` observable for the Aegis family, coherent release/component set.
- `PARTIAL_CATALOG` — any other non-empty subset/malformed Aegis inventory.
- `MIXED_REVISION` — observed components/provenance do not resolve to one release/component set.

Distribution provenance states:

- `PLUGIN`
- `STANDALONE`
- `INDIVIDUAL_SKILLS`
- `DUPLICATE_DISTRIBUTION`
- `UNKNOWN`

Safety matrix:

| Provenance | Catalog | Result |
| --- | --- | --- |
| Plugin | FULL_SPECIALIST | PASS / multi_skill |
| Standalone | COMPOSITE_ONLY | PASS / compatibility |
| Individual Skills | FULL_SPECIALIST | PASS / multi_skill for PR #9 Task 6 |
| Individual Skills | COMPOSITE_ONLY | PASS / compatibility for PR #9 Task 6 |
| Plugin | COMPOSITE_ONLY or partial | BLOCKED_ENVIRONMENT; never compatibility fallback |
| Standalone | FULL_SPECIALIST or partial | BLOCKED_ENVIRONMENT |
| Duplicate distribution | any | BLOCKED_ENVIRONMENT |
| Unknown provenance | any | BLOCKED_EVIDENCE |
| any | MIXED_REVISION | BLOCKED_ENVIRONMENT |

Installed Skill inventory comparison is set-based, not UI-order-based.

## RED -> GREEN package

1. Update deterministic tests first so individually imported exact-nine and aegis-only inventories are required to pass, including arbitrary UI order; require provenance to be returned separately.
2. Run focused RED against the current evaluator; expected failure is current provenance coupling.
3. Repair `tools/aegis_skillset/distribution.py` only as needed to satisfy the matrix.
4. Update Task 6 distribution tests so synthetic FULL_SPECIALIST / COMPOSITE_ONLY evidence can use `INDIVIDUAL_SKILLS` provenance.
5. Consolidate Proposed Authority/design wording so manual installation remains rejected as the normal product distribution but is admissible as PR #9 Task 6 catalog evidence.
6. Re-run deterministic Skillset/Project State/eval CI and re-check protected semantic blobs.
7. Return to P34. Do not populate normative real evidence refs or claim Task 6 PASS until catalog release provenance and complete terminal behavior evidence are materialized.

## Evidence intake after repair

Environment A may be accepted for PR #9 when evidence proves:

```text
catalog_state = FULL_SPECIALIST
installed Aegis Skills = exact nine
release/component set = coherent
provenance = INDIVIDUAL_SKILLS | PLUGIN
```

Environment B may be accepted when evidence proves:

```text
catalog_state = COMPOSITE_ONLY
installed Aegis Skills = [aegis]
release/component set = coherent
provenance = INDIVIDUAL_SKILLS | STANDALONE
```

Non-Aegis Skills such as `skill-creator` do not affect the Aegis-family catalog state.
