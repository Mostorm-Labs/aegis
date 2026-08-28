# Aegis Multi-Skill Composition Semantics v0.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the approved 09 v0.2 Single-Owner Compositional Graph so Aegis accepts support-first multi-Skill execution without losing unique substantive ownership, rejects ownership leaks/chains/loops, requires observable specialist-unavailability evidence for composite fallback, and evaluates complete terminal traces instead of first-Skill selection.

**Architecture:** Keep the v0.1 nine-entrypoint topology and stage ownership unchanged. Extend `skillset/ownership.json` with the minimum machine-readable composition contract, normalize protected routing cases into ownership policies, and add a deterministic terminal-trace oracle in `tools/aegis_skillset/routing.py`. Narrative runtime boundaries live in the canonical shared handoff contract and canonical Skill sources, then flow to committed `skills/*` distributions through the existing deterministic builder. Historical 09-01 v0.1 evidence remains immutable; v0.2 creates separate interpretation/rerun artifacts.

**Tech Stack:** Python 3.12 stdlib, JSON/Markdown, existing `tools.aegis_skillset` deterministic tooling, existing Skill Creator structure validator, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-08-27-aegis-multi-skill-composition-semantics-v0.2-design.md`

## Global Constraints

- `docs/skill-decomposition-v0.1.md` remains the Current Proposed Execution Authority until v0.2 implementation/reverification and P34 acceptance; do not mark it Superseded during P30-P33.
- Preserve exactly nine entrypoints and the existing P00-P36 primary ownership map.
- `aegis-project-state` is the only generally allowlisted Supporting Skill in v0.2.
- During support-only preflight there may be zero substantive owners; once substantive execution begins there is exactly one Primary Owner; never more than one.
- `Support Edge != Ownership Handoff Edge`.
- `aegis` is the only central Router. In Multi-Skill Mode it may own routing/ambiguity/blocked-short-circuit results but must not steal specialist-owned substantive work when the relevant specialist is known available.
- Composite Compatibility Mode requires observable evidence that the relevant specialist is unavailable; absence from a partial trace is insufficient.
- A trusted earlier blocker may short-circuit a requested Primary before substantive execution; that terminal blocked/routing result is owned by `aegis`.
- Direct Primary-to-Primary substantive chaining is forbidden by default.
- A bounded `Router -> Primary -> Router` blocker return is allowed once only when the Primary emits no substantive result and discovers an earlier blocker not already conclusively known.
- Behavioral acceptance uses a complete terminal invocation trace. `actual_first_skill == expected_skill` is not normative acceptance in v0.2.
- Incomplete platform evidence yields `BLOCKED_EVIDENCE`; do not infer ownership, availability, or absence from a partial trace.
- Preserve 09-01 v0.1 evidence bytes/history. Add new v0.2 interpretation/rerun artifacts instead of rewriting old verdicts.
- Do not broaden trigger-description tuning unless a new classified behavioral defect requires it.
- Existing OpenAI hosted provider baseline remains independently `BLOCKED_ENVIRONMENT`.

---

## P31 Task Package 1 — Machine-Readable Composition Contract

**Purpose:** Freeze the smallest executable representation of v0.2 roles/modes without changing stage ownership.

**Authority:** `docs/skill-decomposition-v0.2.md`; approved written design §§4-5, 10, 16-18.

**Dependencies:** Existing `skillset/manifest.json`, `skillset/ownership.json`, `tools/aegis_skillset/model.py`.

**Scope / Files:**
- Modify: `skillset/ownership.json`
- Modify: `tools/aegis_skillset/model.py`
- Modify: `tests/skillset/test_metadata.py`

**Non-goals:** No routing evaluator yet; no Skill text changes; no Project State schema changes.

**Interfaces:**
- `SkillSetConfig.supporting_skills: tuple[str, ...]`
- `SkillSetConfig.compatibility_owner: str`
- `SkillSetConfig.compatibility_requires_unavailable_evidence: bool`
- Existing `primary_owner_by_stage`, `cross_cutting_owners`, `ambiguity_router` remain unchanged.

- [ ] **Step 1: Write RED metadata tests**

Add tests that require `ownership.json` v0.2 composition metadata and reject unknown support/router owners:

```python
def test_v02_composition_metadata_is_frozen(self):
    from tools.aegis_skillset.model import load_skillset
    config = load_skillset(ROOT)
    self.assertEqual(('aegis-project-state',), config.supporting_skills)
    self.assertEqual('aegis', config.compatibility_owner)
    self.assertTrue(config.compatibility_requires_unavailable_evidence)


def test_unknown_supporting_skill_is_rejected(self):
    from tools.aegis_skillset.model import load_skillset, validate_skillset
    config = load_skillset(ROOT)
    config.supporting_skills = ('aegis-project-state', 'aegis-unknown')
    self.assertTrue(any('unknown supporting skill' in e for e in validate_skillset(config)))
```

Because `SkillSetConfig` is currently frozen, implement the negative case using `dataclasses.replace(config, supporting_skills=(...))`.

- [ ] **Step 2: Run focused test and verify RED**

Run:
```bash
python3 -m unittest tests.skillset.test_metadata -v
```
Expected: FAIL because composition fields do not exist.

- [ ] **Step 3: Extend `ownership.json` minimally**

Use this exact shape:

```json
"composition": {
  "supporting_skills": ["aegis-project-state"],
  "compatibility_owner": "aegis",
  "compatibility_requires_unavailable_evidence": true
}
```

Set top-level `version` to `0.2`. Do not duplicate stage ownership or add an invocation ledger.

- [ ] **Step 4: Extend model/load/validation**

Add the three fields to `SkillSetConfig`, load them from `ownership['composition']`, and validate:
- every supporting Skill exists;
- only `aegis-project-state` is allowlisted in v0.2;
- compatibility owner equals `aegis`;
- unavailability evidence requirement is `True`.

- [ ] **Step 5: Run metadata tests**

Run:
```bash
python3 -m unittest tests.skillset.test_metadata -v
python3 -m tools.aegis_skillset.cli validate .
```
Expected: PASS and `SKILLSET_VALID`.

**Evidence:** focused test output + CLI validation.

**Exit Criteria:** Composition metadata is machine-readable, validated, and stage ownership is byte-for-byte semantically unchanged.

---

## P31 Task Package 2 — RED-First Terminal-Trace Oracle + Routing Corpus Migration

**Purpose:** Replace first-Skill routing assertions with deterministic terminal ownership/composition evaluation.

**Authority:** written design §§6-8, 10-12, 14.

**Dependencies:** Task 1 composition metadata.

**Scope / Files:**
- Modify: `tools/aegis_skillset/routing.py`
- Modify: `tests/skillset/test_routing.py`
- Modify: `skillset/routing/direct-trigger.json`
- Modify: `skillset/routing/ambiguous-routing.json`
- Modify: `skillset/routing/upstream-blocker.json`
- Modify: `skillset/routing/compatibility.json`
- Modify: `skillset/routing/cross-skill-handoff.json`
- Create: `skillset/routing/composition-traces.json`

**Non-goals:** No LLM classifier; no inference from prompt text; no runtime platform API; no mutation of historical dogfood evidence.

**Interfaces:**

Add:

```python
@dataclass(frozen=True)
class TraceEvaluation:
    verdict: str
    violations: tuple[str, ...]
    evidence_gaps: tuple[str, ...]


def evaluate_terminal_trace(case: dict, trace: dict, config: SkillSetConfig) -> TraceEvaluation:
    ...
```

Supported verdicts: `PASS`, `FAIL`, `BLOCKED_EVIDENCE`.

Normalized trace fields:

```json
{
  "terminal": true,
  "mode": "multi_skill",
  "invocations": [
    {"skill": "aegis-project-state", "role": "support"},
    {"skill": "aegis-gate-review", "role": "primary"}
  ],
  "final_answer_owner": "aegis-gate-review",
  "genuine_ambiguity": false,
  "earlier_blocker_conclusively_established": false,
  "specialist_availability": {"aegis-gate-review": "available"},
  "ownership_edges": [],
  "handoff_edges": [],
  "forbidden_downstream_substantive_execution": 0
}
```

Protected-case policy fields:

```json
{
  "required_primary_owner": "aegis-gate-review",
  "allowed_supporting_skills": ["aegis-project-state"],
  "router_policy": "only_for_genuine_ambiguity_or_accepted_earlier_blocker",
  "normal_terminal_owner": "aegis-gate-review",
  "short_circuit": {
    "allowed": true,
    "condition": "earlier_blocker_conclusively_established",
    "terminal_owner": "aegis"
  }
}
```

- [ ] **Step 1: Write RED evaluator tests before implementation**

Add explicit tests for at least these traces:

```python
def test_support_first_gate_review_passes(self):
    # project-state support -> gate-review primary -> gate-review final owner


def test_support_ownership_leak_fails(self):
    # project-state support emits final gate verdict


def test_router_ownership_leak_fails(self):
    # direct gate-review case, specialist available, aegis owns substantive result without blocker


def test_direct_primary_chain_fails(self):
    # architecture primary -> verification primary


def test_earlier_blocker_can_skip_requested_primary(self):
    # trusted blocker -> aegis terminal owner, no architecture invocation


def test_compatibility_requires_unavailability_evidence(self):
    # composite mode without observable specialist availability -> BLOCKED_EVIDENCE


def test_bounded_router_primary_router_blocker_return_passes(self):
    # one allowed re-entry, no substantive primary result


def test_ownership_cycle_fails(self):
    # architecture -> aegis -> architecture -> aegis cycle
```

- [ ] **Step 2: Run focused routing tests and verify RED**

Run:
```bash
python3 -m unittest tests.skillset.test_routing -v
```
Expected: FAIL because `TraceEvaluation` / `evaluate_terminal_trace` and v0.2 fixtures do not exist.

- [ ] **Step 3: Migrate routing case vocabulary**

`direct-trigger.json`: replace normative `expected_skill` with `required_primary_owner`, `allowed_supporting_skills`, `router_policy`, `normal_terminal_owner`, optional `short_circuit`.

`ambiguous-routing.json`: set `router_policy = "required"`, `normal_terminal_owner = "aegis"`, no required specialist Primary.

`upstream-blocker.json`: encode `requested_primary_owner`, short-circuit condition, `terminal_owner = "aegis"`, `must_stop = true`.

`compatibility.json`: encode `requested_primary_owner`, `compatibility_owner = "aegis"`, `requires_specialist_unavailable_evidence = true`.

- [ ] **Step 4: Replace v0.1 handoff corpus semantics**

Use this conceptual structure:

```json
{
  "valid_support_returns": [
    {
      "id": "support-return-001",
      "type": "support_return",
      "supporting_skill": "aegis-project-state",
      "to_owner": "aegis-gate-review"
    }
  ],
  "valid_ownership_handoffs": [
    {
      "id": "ownership-handoff-001",
      "type": "ownership_handoff",
      "from_owner": "aegis-architecture",
      "to": "aegis",
      "reason": "earlier_untrusted_layer"
    }
  ],
  "forbidden_primary_chains": [
    {
      "id": "primary-chain-001",
      "edges": [["aegis-architecture", "aegis-verification"]]
    }
  ],
  "forbidden_cycles": [
    {
      "id": "cycle-001",
      "edges": [["aegis-architecture", "aegis"], ["aegis", "aegis-architecture"]]
    }
  ]
}
```

The former `architecture -> verification` and `verification -> implementation` entries must no longer be accepted as substantive handoffs. A specialist may suggest a next Skill after a completed stage, but that suggestion is not automatic ownership transfer.

- [ ] **Step 5: Implement deterministic evaluator**

Rules, in order:
1. missing/incomplete terminal evidence -> collect evidence gaps and return `BLOCKED_EVIDENCE` unless a hard composition violation is already proven;
2. support roles must be globally and case-allowlisted;
3. unique set of substantive Primary owners must contain at most one Skill;
4. normal path requires the case Primary and normal final owner;
5. valid short-circuit requires conclusive earlier blocker and `aegis` terminal owner; requested Primary may be absent;
6. compatibility mode requires explicit `unavailable` evidence for the requested specialist;
7. support final ownership of another family -> `SUPPORT_OWNERSHIP_LEAK`;
8. router substantive ownership in normal Multi-Skill path with available specialist -> `ROUTER_OWNERSHIP_LEAK`;
9. distinct Primary-to-Primary edge -> `DIRECT_PRIMARY_CHAIN`;
10. cycles -> `OWNERSHIP_LOOP`;
11. downstream substantive execution count must be zero for blocked terminal cases.

Do not create a new project-state ledger or infer roles from invocation order.

- [ ] **Step 6: Add `composition-traces.json` regression fixtures**

Include valid support-first, valid primary-support-primary, valid blocker short-circuit, valid bounded router re-entry, valid composite fallback with unavailable evidence, plus one fixture for each violation class and one `BLOCKED_EVIDENCE` incomplete trace.

- [ ] **Step 7: Run routing corpus and focused tests**

Run:
```bash
python3 -m unittest tests.skillset.test_routing -v
python3 -m tools.aegis_skillset.cli routing-check .
```
Expected: PASS and `ROUTING_OK`.

**Evidence:** RED failure captured before implementation; GREEN focused test/CLI output.

**Exit Criteria:** No normative acceptance path depends on first invocation; all v0.2 graph/ownership invariants have deterministic regressions.

---

## P31 Task Package 3 — Shared Runtime Contract + Skill Instruction Boundaries

**Purpose:** Make the approved role/ownership semantics executable by every canonical Skill without trigger-description over-tuning.

**Authority:** written design §§4, 6-10, 15.

**Dependencies:** Task 2 vocabulary and evaluator.

**Scope / Files:**
- Modify: `skillset/shared/handoff-contract.md`
- Modify: `skillset/skills/aegis/SKILL.md`
- Modify: `skillset/skills/aegis-project-state/SKILL.md`
- Modify canonical stage specialists only where needed: `skillset/skills/aegis-{discovery,modeling,architecture,verification,governance,implementation,gate-review}/SKILL.md`
- Regenerate matching `skills/**` through existing builder; do not hand-edit generated copies.
- Modify/add focused tests in `tests/skillset/test_composite.py`, `tests/skillset/test_trigger_boundaries.py`, or `tests/skillset/test_distribution_validation.py` as appropriate.

**Non-goals:** Do not redesign descriptions to force single dispatch; do not add another Supporting Skill; do not change P-stage map.

- [ ] **Step 1: Add RED text-contract tests**

Require generated packages to contain these normative concepts:
- `support_return`
- `ownership_handoff`
- `Support Edge` and `Ownership Handoff Edge`
- `final-answer owner`
- only `aegis-project-state` as general support
- direct Primary-to-Primary substantive chaining forbidden
- composite fallback requires specialist-unavailability evidence.

- [ ] **Step 2: Run focused tests and verify RED**

Run:
```bash
python3 -m unittest tests.skillset.test_composite tests.skillset.test_trigger_boundaries tests.skillset.test_distribution_validation -v
```
Expected: FAIL on missing v0.2 contract tokens/semantics.

- [ ] **Step 3: Rewrite shared handoff contract to v0.2 semantics**

The contract must explicitly distinguish:

```yaml
type: support_return
supporting_skill: aegis-project-state
facts: {}
```

from:

```yaml
type: ownership_handoff
from_owner: <primary>
to: aegis
reason: earlier_untrusted_layer
requested_stage: <stage>
earliest_untrusted_layer: <stage-or-layer>
status: <BLOCKED_*>
suggested_next_stage: <stage>
```

State that handoff metadata is ephemeral and not Authority/Evidence/Gate/Integration/Project State.

- [ ] **Step 4: Update central Router instruction**

`aegis` must say:
- it owns routing/ambiguity/blocked terminal results;
- in Multi-Skill Mode it does not own specialist substantive work when that specialist is known available;
- Composite Compatibility Mode is permitted only with evidence of relevant specialist unavailability;
- a blocked short-circuit is terminal unless separate Current Authority authorizes repair-and-resume.

- [ ] **Step 5: Update Project State instruction**

`aegis-project-state` must say:
- direct `.aegis` validation -> it is final-answer owner;
- when supporting another stage family -> facts only, `support_return`, no stage verdict;
- it may establish an earlier blocker but routes the terminal blocked result to `aegis` rather than repairing or owning the downstream stage.

- [ ] **Step 6: Update stage-specialist instruction boundary**

Each stage specialist must say:
- it is the unique Primary for its owned stage family once substantive execution begins;
- it may consume Project State support without transferring ownership;
- it may not directly chain substantive execution to another Primary;
- an earlier blocker produces `ownership_handoff` to `aegis` and stops substantive execution.

- [ ] **Step 7: Regenerate committed distributions**

Run:
```bash
python3 scripts/build_skillset.py --write
python3 scripts/build_skillset.py --check
python3 scripts/validate_generated_skills.py
```
Expected: no distribution drift; all nine standalone packages structurally valid.

- [ ] **Step 8: Run focused tests**

Run the focused tests from Step 2 plus:
```bash
python3 -m unittest tests.skillset.test_build -v
```
Expected: PASS.

**Evidence:** generated-distribution check, package validation, focused tests.

**Exit Criteria:** Canonical and generated Skill instructions encode v0.2 ownership/support/handoff semantics with no broad trigger-description redesign.

---

## P31 Task Package 4 — v0.2 Historical Evidence Reinterpretation Without Rewrite

**Purpose:** Re-evaluate 09-01 under the v0.2 oracle while preserving v0.1 evidence as historical truth.

**Authority:** written design §§12-13, 16-17.

**Dependencies:** Tasks 1-3.

**Scope / Files:**
- Preserve unchanged: `skillset/dogfood/installed-platform-v0.1.json`
- Preserve unchanged: existing `skillset/dogfood/evidence/*v01.json` and repair-rerun historical files
- Create: `skillset/dogfood/installed-platform-v0.2.json`
- Create v0.2 interpretation records under `skillset/dogfood/evidence/` only where needed
- Modify/add tests in `tests/skillset/test_routing.py` to validate interpretation schema against the terminal-trace oracle.

**Non-goals:** Do not claim new installed-platform PASS without a new/complete terminal trace; do not erase historical FAIL/BLOCKED verdicts.

- [ ] **Step 1: Write RED preservation/reinterpretation tests**

Require:
- v0.2 artifact references v0.1 as historical source;
- no v0.2 case uses `actual_first_skill == expected_skill` as acceptance;
- every v0.2 interpretation records `required_primary_owner` or valid short-circuit/routing-only reason;
- incomplete old screenshots become `BLOCKED_EVIDENCE` rather than inferred PASS when final-answer ownership/full trace is not provable.

- [ ] **Step 2: Create `installed-platform-v0.2.json`**

Use:
```json
{
  "schema_version": "0.2",
  "historical_source": "skillset/dogfood/installed-platform-v0.1.json",
  "oracle": "terminal_trace_v0.2",
  "cases": []
}
```

For each historical protected case, record the v0.2 policy, available evidence references, what can be concluded, and what still requires rerun. Use `BLOCKED_EVIDENCE` when complete terminal ownership/availability cannot be proven from retained evidence.

- [ ] **Step 3: Run focused tests**

Run:
```bash
python3 -m unittest tests.skillset.test_routing -v
```
Expected: PASS.

**Evidence:** new v0.2 interpretation artifact; unchanged historical file shown by Git diff; focused regression.

**Exit Criteria:** Historical 09-01 is reinterpretable under v0.2 without mutating v0.1 evidence, and remaining platform rerun needs are explicit.

---

## P31 Task Package 5 — Deterministic Gate / CI / Package Closure

**Purpose:** Prove the repository implementation is internally consistent before asking the installed platform for behavioral evidence.

**Authority:** written design §§14-15, 19; existing 09 deterministic Gate.

**Dependencies:** Tasks 1-4.

**Scope / Files:**
- Modify: `.github/workflows/skillset.yml`
- Update: PR #9 body/status after evidence exists
- Do not merge PR #9.

**Non-goals:** Do not promote deterministic success into installed-platform behavioral PASS; do not change hosted provider baseline.

- [ ] **Step 1: Fix workflow path coverage**

Ensure CI triggers for:
- `docs/skill-decomposition-v0.2.md`
- `docs/superpowers/specs/*multi-skill-composition*.md`
- `docs/superpowers/plans/*multi-skill-composition*.md`

- [ ] **Step 2: Run the deterministic Gate**

Run:
```bash
python3 -m tools.aegis_skillset.cli validate .
python3 scripts/build_skillset.py --check
python3 -m tools.aegis_skillset.cli routing-check .
python3 scripts/validate_generated_skills.py
python3 -m unittest discover -s tests/skillset -v
python3 -m unittest discover -s tests/project_state -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
```
Expected: all deterministic checks PASS.

- [ ] **Step 3: Verify GitHub Actions on PR head**

Require the `Aegis Skillset Integrity` workflow for the implementation head to succeed. Capture run/job URL as deterministic evidence.

- [ ] **Step 4: Update PR #9 status without supersession**

PR body must say:
```text
09 v0.2 written spec = APPROVED
P30/P31              = COMPLETE
Deterministic impl   = PASS
Installed platform   = rerun required / BLOCKED_EVIDENCE until observed
P34                   = not yet final
v0.1 supersession    = not yet authorized
```

**Evidence:** green CI run + deterministic command results.

**Exit Criteria:** Repository/tooling/package Gate is green, while behavioral Gate remains explicitly separate.

---

## P31 Task Package 6 — Installed-Platform Rerun, P34, Then Supersession Decision

**Purpose:** Obtain new complete terminal-trace evidence from the updated installed packages and decide whether v0.2 can become Current Execution Authority.

**Authority:** written design §§12-13, 17, 19.

**Dependencies:** Task 5 deterministic PASS and updated Skill packages installed in the test environment.

**Scope / Artifacts:**
- Add new 09-01 v0.2 platform evidence under `skillset/dogfood/evidence/`
- Update `skillset/dogfood/installed-platform-v0.2.json`
- Update `docs/skill-decomposition-dogfood-v0.1.md` with an append-only v0.2 reinterpretation/rerun section or create a v0.2 dogfood companion if clearer
- Update `docs/skill-decomposition-v0.2.md` status only after P34
- Update Notion 09/09-01/09-v0.2 status after GitHub evidence is recorded

**Required protected reruns:**
1. direct Gate audit with all specialists available — support-first is allowed, `aegis-gate-review` must own normal substantive conclusion;
2. ambiguous next-step request — `aegis` owns routing result;
3. trusted upstream blocker for P14 — requested Primary may be skipped, `aegis` owns terminal blocker, zero downstream substantive P14;
4. composite-only modeling/Gate request — `aegis` fallback accepted only with observable specialist-unavailability precondition.

- [ ] **Step 1: Capture complete terminal evidence**

Record full invocation sequence, terminality, final-answer owner evidence, specialist availability evidence, blocker evidence where relevant, downstream-execution count, and loop/cycle observations. A mid-stream screenshot alone is insufficient.

- [ ] **Step 2: Normalize each trace and run the v0.2 oracle**

Every case must evaluate to `PASS`; `BLOCKED_EVIDENCE` is not a PASS substitute.

- [ ] **Step 3: P34 split Gate**

Report independently:
```text
Deterministic Skill-System Tooling = PASS | BLOCKED_*
Skill Package Gate                 = PASS | BLOCKED_*
Multi-Skill Behavioral Trigger     = PASS | BLOCKED_EVIDENCE | BLOCKED_*
Existing Hosted Provider Baseline  = BLOCKED_ENVIRONMENT unless new provider evidence exists
Overall 09                         = PASS only if required 09 Gates pass; otherwise exact blocker
```

- [ ] **Step 4: Supersede only after P34 acceptance**

If and only if P34 accepts v0.2:
- mark the v0.1 Runtime Selection / Project-State composition / Cross-Skill Handoff / Behavioral Gate semantics historical;
- make v0.2 Current Execution Authority for those scopes;
- preserve all v0.1 documents and evidence;
- update parent/Master 09 links and Notion status;
- keep PR #9 merge decision separate from the semantic supersession record until repository integration evidence exists.

**Blocked Return:** If any rerun fails, classify via P35 before touching Skill descriptions or the spec. If evidence is incomplete, return `BLOCKED_EVIDENCE`; if the accepted semantics prove wrong, return `SPEC_DEFECT` / `AUTHORITY_CONFLICT` as appropriate rather than weakening the oracle.

**Exit Criteria:** New installed-platform evidence satisfies v0.2 terminal-trace acceptance and P34 decides supersession/integration on evidence, not expectation.

---

## Plan Self-Review

**Spec coverage:**
- Role model / runtime modes -> Tasks 1 and 3.
- Support vs handoff edges / bounded router re-entry -> Tasks 2 and 3.
- Blocked short-circuit / final-answer ownership -> Tasks 2 and 3.
- Composition violations / terminal-trace PASS rule -> Task 2.
- Compatibility availability evidence -> Tasks 1, 2, and 6.
- Historical evidence preservation/reinterpretation -> Task 4.
- RED-first deterministic regressions -> Tasks 1-4.
- Skill instructions/package validation -> Tasks 3 and 5.
- Installed-platform rerun/P34/supersession -> Task 6.

**Placeholder scan:** No `TBD`, `TODO`, “similar to”, or unspecified test steps remain.

**Type/name consistency:** `supporting_skills`, `compatibility_owner`, `compatibility_requires_unavailable_evidence`, `TraceEvaluation`, `evaluate_terminal_trace`, `support_return`, `ownership_handoff`, and the five normative composition violation names are used consistently.

**Safety boundary:** v0.1 remains unsuperseded through deterministic implementation. P34 and installed-platform evidence remain required before v0.2 becomes Current Execution Authority.