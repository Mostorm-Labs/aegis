# Aegis Plugin Distribution v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a deterministic Aegis Plugin distribution/evidence layer that packages the existing nine-Skill topology as one normal product distribution, preserves Standalone Aegis as the only compatibility distribution, derives installed-catalog trust states, and closes PR #9 Task 6 without changing `terminal_trace_v0.2` semantics.

**Architecture:** Keep distribution and lifecycle ownership orthogonal. Add a machine-readable distribution contract and catalog evaluator under `skillset/` / `tools/aegis_skillset/`; build deterministic release/source bundles from the existing generated `skills/*` tree; preserve the current Task 6 rerun manifest as history and add a distribution-aware v0.2.1 companion that separates Catalog Evidence from Behavior Evidence; then return the exact repository result to `CONTROL_REVIEW` for real ChatGPT Plugin/Standalone installed-platform evidence and independent P34.

**Tech Stack:** Python 3.12 stdlib, JSON, deterministic ZIP packaging, `unittest`, existing Aegis Skillset and Project State tooling, GitHub Actions, ChatGPT Plugins/Skills installed-platform dogfood.

**Spec:** `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md`

## Global Constraints

- `Product != Plugin != Skill != App`.
- The normal Aegis Plugin catalog is exactly the nine Skills declared by `skillset/manifest.json`.
- Standalone Aegis contains only central `aegis` and is the only distribution allowed to enter Composite Compatibility Mode.
- Only `FULL_SPECIALIST` and `COMPOSITE_ONLY` are valid runtime catalog states.
- `PARTIAL_CATALOG`, `MIXED_REVISION`, and `DUPLICATE_DISTRIBUTION` fail closed as `BLOCKED_ENVIRONMENT`.
- Plugin packaging must not add a P-stage owner, final-answer owner, Authority-repair owner, or Gate-verdict owner.
- Apps remain orthogonal capabilities. Plugin v0.1 requires no Apps.
- Preserve `skillset/ownership.json` stage ownership/composition/execution-surface semantics unless a later classified defect explicitly requires change.
- Preserve `tools/aegis_skillset/routing.py::evaluate_terminal_trace()` semantics and the four protected PR #9 case IDs unchanged.
- Preserve `skillset/dogfood/installed-platform-rerun-v0.2.json` byte-for-byte and create a v0.2.1 companion for the evidence-layer migration.
- Task 6 remains 4/4 PASS. `BLOCKED_EVIDENCE` and `BLOCKED_ENVIRONMENT` are not PASS substitutes.
- Use test release `0.1.0-task6.1`. It is a pre-release evidence artifact, not a production Aegis release or Authority promotion.
- The public OpenAI platform supports Plugins containing multiple Skills, but this plan does not invent an undocumented ChatGPT local-plugin archive schema. Repository ZIPs are deterministic **source bundles**. Platform materialization uses the actual supported Plugin UI/import path available at test time.
- If ChatGPT cannot materialize one local/test Plugin containing all nine Skills on the required surface, return `BLOCKED_ENVIRONMENT`; do not substitute nine independent personal Skill installs for final Task 6 acceptance.
- Do not rewrite the historical fact that `int-pr9` integrated under a non-PASS Gate.
- No P23 promotion of Skill Decomposition v0.2, Execution Surface v0.1, or Plugin Distribution v0.1 occurs during P32.

### Protected pre-P32 semantic baselines

Before any code edit, verify these Git blob SHAs exactly:

```text
tools/aegis_skillset/routing.py                         5d7dc81ff9de84ff0facaa08c0dcdaf047bf7180
skillset/routing/direct-trigger.json                    3f2452c625226c6b90fd73cf018feeef6a86cc00
skillset/routing/ambiguous-routing.json                 3e3d0e24ac5afc012923efc08a3a1a38392f4293
skillset/routing/upstream-blocker.json                  e19589284639b689c51768e245f31a27c9342d6e
skillset/routing/compatibility.json                     ac204c7225719371db195d299d085e2947a5b0e4
skillset/dogfood/installed-platform-rerun-v0.2.json     0944a95aca2f6c565ee5835efc5adaaf67abd480
```

If any differs before P32 starts, stop and return to P31 review; do not silently rebase the semantic acceptance target.

---

## File / Responsibility Map

| Path | Responsibility |
| --- | --- |
| `docs/plugin-distribution-contract-v0.1.md` | Human-readable Proposed Authority; record written-spec approval and implementation boundary. |
| `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md` | Approved design source for this plan. |
| `.aegis/authorities.json` | Register `aegis-plugin-distribution-v0.1` as Proposed and dependent on Skill Decomposition v0.2. |
| `.aegis/state.json` | Generated Project State after Authority registration. |
| `skillset/distribution.json` | Machine-readable Plugin/Standalone distribution contract. |
| `tools/aegis_skillset/distribution.py` | Parse/validate distribution contract and evaluate installed-catalog evidence. |
| `tools/aegis_skillset/package.py` | Deterministic release manifest and source-bundle rendering from generated `skills/*`. |
| `scripts/build_aegis_distributions.py` | CLI wrapper for release-manifest check/write and source-bundle build. |
| `skillset/releases/aegis-0.1.0-task6.1.json` | Generated durable release manifest pinning exact Skill tree digests for the test release. |
| `skillset/dogfood/installed-platform-rerun-v0.2.1.json` | Distribution-aware Task 6 orchestration; semantic oracle remains `terminal_trace_v0.2`. |
| `tools/aegis_skillset/dogfood.py` | Compose catalog evidence with behavior evidence before invoking the existing terminal-trace oracle. |
| `tests/skillset/test_distribution_contract.py` | Distribution metadata + five catalog-state RED/GREEN oracle. |
| `tests/skillset/test_plugin_package.py` | Deterministic release/source-bundle and canonical-source parity tests. |
| `tests/skillset/test_installed_platform_distribution_gate.py` | v0.2.1 evidence separation, availability derivation, blocker precedence, and 4/4 Gate tests. |
| `tests/project_state/test_plugin_distribution_authority.py` | Root Project State registration/dependency regression. |
| `.github/workflows/skillset.yml` | Deterministic distribution/build/tests + source-bundle CI artifact. |
| `.github/workflows/project-state.yml` | Ensure Plugin Distribution Authority/spec/plan changes trigger Project State self-host validation. |

---

# P32 Repository Implementation Packages

### Task Package 1 — Register the approved Proposed Authority without changing current trust

**Purpose:** Make the reviewed Plugin Distribution Authority visible to Project State before implementation while keeping it Proposed and downstream of unresolved Skill Decomposition v0.2.

**Files:**
- Modify: `docs/plugin-distribution-contract-v0.1.md`
- Modify: `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md`
- Modify: `.aegis/authorities.json`
- Regenerate: `.aegis/state.json`
- Modify: `.github/workflows/project-state.yml`
- Create: `tests/project_state/test_plugin_distribution_authority.py`

**Interfaces:**
- Consumes: `aegis-skill-decomposition-v0.2` Proposed Authority and Project State v0.4.
- Produces: Authority ID `aegis-plugin-distribution-v0.1`, scope `aegis/plugin-distribution`, status `Proposed`.

- [ ] **Step 1: Write the RED Project State registration test**

Create `tests/project_state/test_plugin_distribution_authority.py`:

```python
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class PluginDistributionAuthorityTests(unittest.TestCase):
    def test_plugin_distribution_authority_is_registered_as_proposed(self):
        authorities = json.loads((ROOT / ".aegis/authorities.json").read_text(encoding="utf-8"))
        matches = [
            item for item in authorities["authorities"]
            if item.get("id") == "aegis-plugin-distribution-v0.1"
        ]
        self.assertEqual(1, len(matches))
        authority = matches[0]
        self.assertEqual("aegis/plugin-distribution", authority["scope"])
        self.assertEqual("skill_contract", authority["kind"])
        self.assertEqual("v0.1", authority["version"])
        self.assertEqual("Proposed", authority["status"])
        self.assertEqual("docs/plugin-distribution-contract-v0.1.md", authority["ref"])
        self.assertEqual(["aegis-skill-decomposition-v0.2"], authority["depends_on"])

    def test_registration_preserves_existing_project_blockers(self):
        state = json.loads((ROOT / ".aegis/state.json").read_text(encoding="utf-8"))
        self.assertIn("gate-skill-decomposition-v02-pr9", state["blocking_gates"])
        self.assertIn("int-pr9", state["nonconforming_integrations"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused RED test**

Run:

```bash
python3 -m unittest tests.project_state.test_plugin_distribution_authority -v
```

Expected: FAIL because `aegis-plugin-distribution-v0.1` is not registered.

- [ ] **Step 3: Record written-spec approval in the two Authority documents**

Change only each document's status line so it records: written spec human-approved on 2026-08-29; P30/P31 complete; P32 implementation authorized only for the test/evidence scope in this plan; Authority remains Proposed and not Gate-accepted.

- [ ] **Step 4: Add the exact Proposed Authority record**

Append this object to `.aegis/authorities.json.authorities`:

```json
{
  "id": "aegis-plugin-distribution-v0.1",
  "scope": "aegis/plugin-distribution",
  "kind": "skill_contract",
  "version": "v0.1",
  "status": "Proposed",
  "ref": "docs/plugin-distribution-contract-v0.1.md",
  "depends_on": ["aegis-skill-decomposition-v0.2"]
}
```

Do not add a Gate, integration, supersession edge, or impact review in this step.

- [ ] **Step 5: Extend Project State workflow path coverage**

Add these push and pull-request path patterns to `.github/workflows/project-state.yml`:

```yaml
      - "docs/plugin-distribution-contract-v*.md"
      - "docs/superpowers/specs/*plugin-distribution*.md"
      - "docs/superpowers/plans/*plugin-distribution*.md"
```

- [ ] **Step 6: Recompute generated Project State**

Run:

```bash
python3 -m tools.aegis_state.cli validate .
python3 -m tools.aegis_state.cli recompute . > /tmp/aegis-plugin-state.json
cp /tmp/aegis-plugin-state.json .aegis/state.json
python3 -m tools.aegis_state.cli check .
```

Expected: validation/check PASS; existing `gate-skill-decomposition-v02-pr9` blocker and `int-pr9` nonconformance remain visible.

- [ ] **Step 7: Run focused GREEN and Project State regression tests**

Run:

```bash
python3 -m unittest tests.project_state.test_plugin_distribution_authority -v
python3 -m unittest discover -s tests/project_state -v
```

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add docs/plugin-distribution-contract-v0.1.md \
  docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md \
  .aegis/authorities.json .aegis/state.json \
  .github/workflows/project-state.yml \
  tests/project_state/test_plugin_distribution_authority.py
git commit -m "docs: register plugin distribution authority"
```

**Exit Criteria:** Plugin Distribution v0.1 is a valid Proposed Authority; no existing blocker, Gate verdict, integration conformance, or Current Authority is rewritten.

---

### Task Package 2 — Machine-readable distribution contract + catalog-state evaluator

**Purpose:** Make Plugin/Standalone topology and the five catalog states deterministic without touching stage ownership.

**Files:**
- Create: `skillset/distribution.json`
- Create: `tools/aegis_skillset/distribution.py`
- Modify: `tools/aegis_skillset/cli.py`
- Create: `tests/skillset/test_distribution_contract.py`

**Interfaces:**
- Consumes: `skillset/manifest.json` as the canonical nine-Skill identity list.
- Produces:
  - `DistributionSpec`
  - `DistributionContract`
  - `CatalogEvaluation`
  - `load_distribution_contract(root)`
  - `validate_distribution_contract(root, contract)`
  - `evaluate_catalog_snapshot(root, snapshot)`
  - CLI command `distribution-check`.

- [ ] **Step 1: Write RED contract tests**

Create tests that require this exact normal/standalone topology and reject unknown/missing/extra Skills:

```python
class DistributionContractTests(unittest.TestCase):
    def test_plugin_is_exactly_the_skillset_manifest_and_standalone_is_aegis_only(self):
        contract = load_distribution_contract(ROOT)
        skill_names = tuple(skill.name for skill in load_skillset(ROOT).skills)
        self.assertEqual(skill_names, contract.plugin.skills)
        self.assertEqual(("aegis",), contract.standalone.skills)
        self.assertEqual((), contract.plugin.required_apps)
        self.assertEqual((), contract.plugin.optional_apps)

    def test_distribution_does_not_create_a_new_stage_owner(self):
        config = load_skillset(ROOT)
        self.assertNotIn("aegis-plugin", set(config.primary_owner_by_stage.values()))
```

Add negative tests using `dataclasses.replace` for an extra Plugin Skill, missing Plugin Skill, Standalone specialist, and required App.

- [ ] **Step 2: Write RED catalog-state tests for all five states**

Use temporary release manifests and snapshots to require:

```text
FULL_SPECIALIST        -> PASS / multi_skill
COMPOSITE_ONLY         -> PASS / compatibility
PARTIAL_CATALOG        -> BLOCKED_ENVIRONMENT
MIXED_REVISION         -> BLOCKED_ENVIRONMENT
DUPLICATE_DISTRIBUTION -> BLOCKED_ENVIRONMENT
```

Also require missing `materialization_ref`, missing `platform_event_id`, or `complete_catalog_capture != true` to return `BLOCKED_EVIDENCE` with `catalog_state = None`.

- [ ] **Step 3: Run RED tests**

Run:

```bash
python3 -m unittest tests.skillset.test_distribution_contract -v
```

Expected: FAIL because the distribution contract/evaluator do not exist.

- [ ] **Step 4: Create the exact source contract**

Create `skillset/distribution.json`:

```json
{
  "schema_version": "0.1",
  "product_id": "aegis",
  "plugin": {
    "id": "aegis",
    "kind": "plugin",
    "skills": [
      "aegis",
      "aegis-project-state",
      "aegis-discovery",
      "aegis-modeling",
      "aegis-architecture",
      "aegis-verification",
      "aegis-governance",
      "aegis-implementation",
      "aegis-gate-review"
    ],
    "required_apps": [],
    "optional_apps": []
  },
  "standalone": {
    "id": "aegis-standalone",
    "kind": "standalone",
    "skills": ["aegis"]
  }
}
```

The Plugin skill order must match `skillset/manifest.json` exactly.

- [ ] **Step 5: Implement the data model**

Use these public types in `tools/aegis_skillset/distribution.py`:

```python
from dataclasses import dataclass
from typing import Literal

CatalogState = Literal[
    "FULL_SPECIALIST",
    "COMPOSITE_ONLY",
    "PARTIAL_CATALOG",
    "MIXED_REVISION",
    "DUPLICATE_DISTRIBUTION",
]


@dataclass(frozen=True)
class DistributionSpec:
    id: str
    kind: str
    skills: tuple[str, ...]
    required_apps: tuple[str, ...] = ()
    optional_apps: tuple[str, ...] = ()


@dataclass(frozen=True)
class DistributionContract:
    schema_version: str
    product_id: str
    plugin: DistributionSpec
    standalone: DistributionSpec


@dataclass(frozen=True)
class CatalogEvaluation:
    verdict: str
    catalog_state: str | None
    runtime_mode: str | None
    specialist_availability: dict[str, str]
    evidence_gaps: tuple[str, ...]
    errors: tuple[str, ...]
```

- [ ] **Step 6: Implement exact catalog-evidence validation and state derivation**

A catalog snapshot must carry these fields:

```text
schema_version = 0.1
fresh_platform_event = true
complete_catalog_capture = true
platform_event_id = non-empty real/synthetic event ID
surface.product = chatgpt
surface.surface = web | desktop | mobile | other
observed_distributions = non-empty list of distribution observations
installed_skills = complete observed Aegis Skill inventory
component_release_versions = optional explicit per-Skill release observations
release_manifest_ref = readable repository-relative release manifest
materialization_ref = non-empty reviewer-accessible durable ref
```

Each distribution observation has exactly `kind`, `id`, and `release_version`.

State derivation rules:

1. Missing/invalid evidence envelope fields -> `BLOCKED_EVIDENCE`, `catalog_state = None`.
2. Both Plugin and Standalone observed -> `DUPLICATE_DISTRIBUTION` / `BLOCKED_ENVIRONMENT`.
3. Plugin provenance + wrong/incomplete Skill set -> `PARTIAL_CATALOG` / `BLOCKED_ENVIRONMENT`.
4. Standalone provenance + anything other than `("aegis",)` -> `PARTIAL_CATALOG` / `BLOCKED_ENVIRONMENT`.
5. Any explicitly observed component release version differing from the selected distribution release -> `MIXED_REVISION` / `BLOCKED_ENVIRONMENT`.
6. Plugin provenance + exact nine Skills + selected release matching the durable release manifest -> `FULL_SPECIALIST`, `PASS`, runtime mode `multi_skill`.
7. Standalone provenance + only `aegis` + selected release matching the durable release manifest -> `COMPOSITE_ONLY`, `PASS`, runtime mode `compatibility`.
8. `FULL_SPECIALIST` maps every non-router specialist in `skillset/manifest.json` to `available`.
9. `COMPOSITE_ONLY` maps every specialist except central `aegis` to `unavailable`.

- [ ] **Step 7: Validate the source contract**

`validate_distribution_contract()` must reject:

- schema version other than `0.1`;
- product id other than `aegis`;
- Plugin Skill tuple not exactly equal to `skillset/manifest.json` names;
- Standalone Skill tuple not exactly `("aegis",)`;
- any required/optional App in v0.1;
- unknown distribution kind/id.

- [ ] **Step 8: Add `distribution-check` CLI command**

Extend the existing command list in `tools/aegis_skillset/cli.py`. On success print exactly:

```text
DISTRIBUTION_VALID
```

On validation failure print `INVALID: ...` lines and exit 1.

- [ ] **Step 9: Run GREEN tests and ownership regressions**

Run:

```bash
python3 -m unittest tests.skillset.test_distribution_contract -v
python3 -m unittest tests.skillset.test_metadata -v
python3 -m tools.aegis_skillset.cli distribution-check .
python3 -m tools.aegis_skillset.cli validate .
```

Expected: PASS, `DISTRIBUTION_VALID`, `SKILLSET_VALID`.

- [ ] **Step 10: Commit**

```bash
git add skillset/distribution.json \
  tools/aegis_skillset/distribution.py tools/aegis_skillset/cli.py \
  tests/skillset/test_distribution_contract.py
git commit -m "feat: add plugin distribution contract"
```

**Exit Criteria:** Distribution metadata is machine-readable; all five catalog states fail/pass exactly as Authority requires; ownership metadata remains unchanged.

---

### Task Package 3 — Deterministic release manifest + Plugin/Standalone source bundles

**Purpose:** Pin the exact nine generated Skill revisions into one test release and produce reproducible source bundles without claiming an undocumented OpenAI upload format.

**Files:**
- Create: `tools/aegis_skillset/package.py`
- Create: `scripts/build_aegis_distributions.py`
- Create/Generate: `skillset/releases/aegis-0.1.0-task6.1.json`
- Create: `tests/skillset/test_plugin_package.py`

**Interfaces:**
- Consumes: generated `skills/<skill-name>/...` distributions and `skillset/distribution.json`.
- Produces:
  - `tree_sha256(path: Path) -> str`
  - `render_release_manifest(root: Path, release_version: str) -> dict`
  - `build_source_bundles(root: Path, release_version: str, output_dir: Path) -> tuple[Path, Path]`
  - deterministic release manifest for `0.1.0-task6.1`.

- [ ] **Step 1: Write RED package tests**

Require:

- release manifest contains exactly the nine Plugin Skill names in manifest order;
- Standalone contains exactly `aegis`;
- every release component has a deterministic tree SHA-256;
- central `aegis` digest is identical in Plugin and Standalone sections;
- Plugin source ZIP contains `release.json` plus exactly the nine `skills/<name>/` trees;
- Standalone ZIP contains `release.json` plus only `skills/aegis/`;
- two builds from the same tree are byte-identical.

- [ ] **Step 2: Run RED tests**

Run:

```bash
python3 -m unittest tests.skillset.test_plugin_package -v
```

Expected: FAIL because package tooling does not exist.

- [ ] **Step 3: Implement deterministic tree digests**

Use:

```python
def tree_sha256(directory: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        rel = path.relative_to(directory).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()
```

Digest generated `skills/*`, not canonical `skillset/skills/*`, because generated distributions are what the source bundle carries.

- [ ] **Step 4: Implement the release manifest without synthetic digest literals**

`render_release_manifest()` must build the Skill entries programmatically:

```python
plugin_skills = [
    {"name": name, "tree_sha256": tree_sha256(root / "skills" / name)}
    for name in contract.plugin.skills
]
standalone_skills = [
    {"name": "aegis", "tree_sha256": tree_sha256(root / "skills" / "aegis")}
]
manifest = {
    "schema_version": "0.1",
    "product_id": "aegis",
    "release_version": release_version,
    "distribution_contract_ref": "skillset/distribution.json",
    "plugin": {"id": "aegis", "skills": plugin_skills},
    "standalone": {"id": "aegis-standalone", "skills": standalone_skills},
}
```

The generated manifest must be serialized with sorted keys and stable indentation/newline rules.

- [ ] **Step 5: Implement deterministic source ZIP layout**

Use fixed ZIP timestamp `(1980, 1, 1, 0, 0, 0)`, sorted archive names, `ZIP_DEFLATED`, and POSIX file mode `0644`, matching the determinism pattern already used by `evals/providers/openai/bundle.py`.

Plugin source bundle layout:

```text
aegis-plugin-0.1.0-task6.1/
├── release.json
└── skills/
    ├── aegis/
    ├── aegis-project-state/
    ├── aegis-discovery/
    ├── aegis-modeling/
    ├── aegis-architecture/
    ├── aegis-verification/
    ├── aegis-governance/
    ├── aegis-implementation/
    └── aegis-gate-review/
```

Standalone source bundle layout:

```text
aegis-standalone-0.1.0-task6.1/
├── release.json
└── skills/
    └── aegis/
```

These archives are source/evidence bundles. Do not label them as a guaranteed ChatGPT import schema.

- [ ] **Step 6: Implement the build script**

`python3 scripts/build_aegis_distributions.py --check`:

- recomputes the release manifest;
- compares it byte-for-byte with `skillset/releases/aegis-0.1.0-task6.1.json`;
- prints `AEGIS_DISTRIBUTION_STATE_OK` and exits 0 when equal;
- prints a unified diff and exits 1 on drift.

`python3 scripts/build_aegis_distributions.py --write-manifest` writes only the generated release manifest.

`python3 scripts/build_aegis_distributions.py --package-dir /tmp/aegis-plugin-dist` builds both deterministic source ZIPs without modifying tracked files.

- [ ] **Step 7: Generate the committed release manifest**

Run:

```bash
python3 scripts/build_aegis_distributions.py --write-manifest
python3 scripts/build_aegis_distributions.py --check
```

Expected: `AEGIS_DISTRIBUTION_STATE_OK`.

- [ ] **Step 8: Run package GREEN tests**

Run:

```bash
python3 -m unittest tests.skillset.test_plugin_package -v
python3 scripts/build_aegis_distributions.py --package-dir /tmp/aegis-plugin-dist
sha256sum /tmp/aegis-plugin-dist/*.zip
```

Expected: tests PASS; exactly two ZIPs are produced.

- [ ] **Step 9: Commit**

```bash
git add tools/aegis_skillset/package.py \
  scripts/build_aegis_distributions.py \
  skillset/releases/aegis-0.1.0-task6.1.json \
  tests/skillset/test_plugin_package.py
git commit -m "feat: build deterministic aegis distributions"
```

**Exit Criteria:** Test release `0.1.0-task6.1` deterministically pins the generated Skill trees; Plugin and Standalone central `aegis` bytes derive from the same generated distribution.

---

### Task Package 4 — Distribution-aware Task 6 evidence migration, without oracle migration

**Purpose:** Separate Catalog Evidence from Behavior Evidence and derive specialist availability from catalog truth before invoking the unchanged v0.2 terminal-trace oracle.

**Files:**
- Preserve unchanged: `skillset/dogfood/installed-platform-rerun-v0.2.json`
- Create: `skillset/dogfood/installed-platform-rerun-v0.2.1.json`
- Modify: `tools/aegis_skillset/dogfood.py`
- Modify: `tools/aegis_skillset/cli.py` only if output fields need extension
- Create: `tests/skillset/test_installed_platform_distribution_gate.py`
- Keep existing: `tests/skillset/test_installed_platform_gate.py`

**Interfaces:**
- Consumes: `evaluate_catalog_snapshot()` and existing `evaluate_terminal_trace()`.
- Produces: a v0.2.1 installed-platform Gate where catalog provenance/availability is independently auditable.

- [ ] **Step 1: Write the historical-byte preservation test**

Use:

```python
import hashlib


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def test_v02_rerun_manifest_is_preserved_byte_for_byte():
    path = ROOT / "skillset/dogfood/installed-platform-rerun-v0.2.json"
    self.assertEqual(
        "0944a95aca2f6c565ee5835efc5adaaf67abd480",
        git_blob_sha(path.read_bytes()),
    )
```

This test must PASS before and after the migration.

- [ ] **Step 2: Write RED v0.2.1 tests**

Require:

1. missing `catalog_evidence_ref` -> `BLOCKED_EVIDENCE`;
2. Plugin partial catalog -> `BLOCKED_ENVIRONMENT` even if behavior trace claims the specialist is unavailable;
3. FULL_SPECIALIST + direct Gate trace with `aegis-gate-review` owner -> PASS;
4. FULL_SPECIALIST + central router substantive Gate result -> FAIL / `ROUTER_OWNERSHIP_LEAK`;
5. COMPOSITE_ONLY + composite modeling trace -> PASS when catalog evidence proves `aegis-modeling` unavailable;
6. prompt text is never read as availability evidence;
7. trace/catalog mode conflict -> `BLOCKED_EVIDENCE`;
8. trace/catalog specialist-availability conflict -> `BLOCKED_EVIDENCE`;
9. aggregate precedence: any semantic FAIL -> `FAIL`; otherwise any environment blocker -> `BLOCKED_ENVIRONMENT`; otherwise any evidence gap -> `BLOCKED_EVIDENCE`; otherwise 4/4 -> `PASS`.

- [ ] **Step 3: Run RED tests**

Run:

```bash
python3 -m unittest tests.skillset.test_installed_platform_distribution_gate -v
```

Expected: FAIL because v0.2.1 orchestration/evidence composition does not exist.

- [ ] **Step 4: Create the exact v0.2.1 rerun manifest**

Create:

```json
{
  "schema_version": "0.2.1",
  "oracle": "terminal_trace_v0.2",
  "predecessor": "skillset/dogfood/installed-platform-rerun-v0.2.json",
  "purpose": "Distribution-aware evidence-layer migration for Task 6. Semantic routing/ownership acceptance remains terminal_trace_v0.2.",
  "cases": [
    {
      "id": "09-01-direct-specialist",
      "case_source": {"path": "skillset/routing/direct-trigger.json", "id": "direct-004"},
      "required_catalog_state": "FULL_SPECIALIST",
      "catalog_evidence_ref": null,
      "behavior_evidence_ref": null
    },
    {
      "id": "09-01-ambiguous-router",
      "case_source": {"path": "skillset/routing/ambiguous-routing.json", "id": "ambiguous-001"},
      "required_catalog_state": "FULL_SPECIALIST",
      "catalog_evidence_ref": null,
      "behavior_evidence_ref": null
    },
    {
      "id": "09-01-upstream-blocker-reroute",
      "case_source": {"path": "skillset/routing/upstream-blocker.json", "id": "blocker-001"},
      "required_catalog_state": "FULL_SPECIALIST",
      "catalog_evidence_ref": null,
      "behavior_evidence_ref": null
    },
    {
      "id": "09-01-composite-fallback",
      "case_source": {"path": "skillset/routing/compatibility.json", "id": "compat-001"},
      "required_catalog_state": "COMPOSITE_ONLY",
      "catalog_evidence_ref": null,
      "behavior_evidence_ref": null
    }
  ]
}
```

- [ ] **Step 5: Add a v0.2.1 evaluation path while preserving explicit v0.2 evaluation**

`evaluate_installed_platform_rerun(root, manifest_path=None)` must default to `installed-platform-rerun-v0.2.1.json`.

If an explicit manifest has schema `0.2`, keep the current evaluation behavior.

For schema `0.2.1`:

1. load/validate Catalog Evidence first;
2. if catalog verdict is `BLOCKED_EVIDENCE`, do not invoke terminal-trace semantics for that case;
3. if catalog verdict is `BLOCKED_ENVIRONMENT`, do not convert it into a routing violation;
4. load Behavior Evidence only after a valid `FULL_SPECIALIST` or `COMPOSITE_ONLY` catalog;
5. derive runtime mode and relevant specialist availability from Catalog Evaluation;
6. if Behavior Evidence contains conflicting `mode` or `specialist_availability`, record an evidence conflict and return `BLOCKED_EVIDENCE`;
7. copy the trace, set catalog-derived mode/availability, then call the unchanged `evaluate_terminal_trace()`.

Do not change `tools/aegis_skillset/routing.py`.

- [ ] **Step 6: Freeze the Behavior Evidence envelope**

Behavior artifacts retain schema version `0.2` and must include:

```text
case_id
fresh_platform_event = true
complete_response_captured = true
platform_event_id
trace.terminal
trace.invocations
trace.final_answer_owner
trace.genuine_ambiguity
trace.earlier_blocker_conclusively_established
trace.ownership_edges
trace.handoff_edges
trace.forbidden_downstream_substantive_execution
trace.primary_substantive_result_emitted
```

Do not require `trace.mode` or `trace.specialist_availability`; catalog truth supplies those fields. If present, they are consistency assertions only.

- [ ] **Step 7: Extend printed Gate state without changing CLI exit policy**

For v0.2.1 include `catalog_state=` and evidence gaps/violations in case output.

Keep existing semantics:

- `installed-platform-check` exits 0 for a structurally valid non-PASS state;
- `installed-platform-gate` exits 2 unless aggregate verdict is `PASS`;
- malformed manifests/evidence exit 1.

- [ ] **Step 8: Run GREEN + semantic-regression tests**

Run:

```bash
python3 -m unittest tests.skillset.test_installed_platform_distribution_gate -v
python3 -m unittest tests.skillset.test_installed_platform_gate -v
python3 -m unittest tests.skillset.test_routing -v
python3 -m tools.aegis_skillset.cli installed-platform-check .
```

Expected: tests PASS; current real Gate state remains blocked because the v0.2.1 evidence refs are null.

- [ ] **Step 9: Re-verify protected blobs**

Run `git hash-object` for all six protected files listed in Global Constraints. Every hash must still match exactly.

- [ ] **Step 10: Commit**

```bash
git add skillset/dogfood/installed-platform-rerun-v0.2.1.json \
  tools/aegis_skillset/dogfood.py tools/aegis_skillset/cli.py \
  tests/skillset/test_installed_platform_distribution_gate.py
git commit -m "feat: separate task6 catalog and behavior evidence"
```

**Exit Criteria:** Old Task 6 orchestration bytes are preserved; new Task 6 evidence derives availability from distribution truth; `terminal_trace_v0.2` and protected routing cases remain byte-identical.

---

### Task Package 5 — CI/package closure and reviewer-accessible test-build artifacts

**Purpose:** Make the new distribution/evidence layer deterministic in CI and return a materialized repository result before installed-platform review.

**Files:**
- Modify: `.github/workflows/skillset.yml`
- Modify the existing workflow contract test that already checks `installed-platform-check`, or add assertions to `tests/skillset/test_installed_platform_distribution_gate.py` if no narrower workflow test exists.

**Interfaces:**
- Consumes: distribution contract, release builder, v0.2.1 Task 6 evaluator.
- Produces: green deterministic Gate plus GitHub Actions source-bundle artifact for platform materialization.

- [ ] **Step 1: Write RED workflow assertions**

Require the workflow to contain:

```text
python3 -m tools.aegis_skillset.cli distribution-check .
python3 scripts/build_aegis_distributions.py --check
python3 scripts/build_aegis_distributions.py --package-dir /tmp/aegis-plugin-dist
actions/upload-artifact@v4
```

and artifact name `aegis-distributions-0.1.0-task6.1`.

- [ ] **Step 2: Run RED workflow test**

Expected: FAIL because the workflow does not yet build/attach distributions.

- [ ] **Step 3: Extend Skillset workflow path coverage**

Add to both `push.paths` and `pull_request.paths`:

```yaml
      - "docs/plugin-distribution-contract-v*.md"
      - "docs/superpowers/specs/*plugin-distribution*.md"
      - "docs/superpowers/plans/*plugin-distribution*.md"
      - "scripts/build_aegis_distributions.py"
```

`skillset/**`, `tools/aegis_skillset/**`, and `tests/skillset/**` are already covered.

- [ ] **Step 4: Add deterministic distribution steps**

Add before the full test suite:

```yaml
      - name: Validate Aegis distribution contract
        run: python3 -m tools.aegis_skillset.cli distribution-check .
      - name: Check Aegis release manifest
        run: python3 scripts/build_aegis_distributions.py --check
      - name: Build Aegis test distribution source bundles
        run: python3 scripts/build_aegis_distributions.py --package-dir /tmp/aegis-plugin-dist
      - name: Upload Aegis test distribution source bundles
        uses: actions/upload-artifact@v4
        with:
          name: aegis-distributions-0.1.0-task6.1
          path: /tmp/aegis-plugin-dist/*.zip
          if-no-files-found: error
```

Do not replace `installed-platform-check` with `installed-platform-gate` in deterministic CI; the real installed-platform Gate still requires external evidence.

- [ ] **Step 5: Run the complete deterministic Gate locally**

Run exactly:

```bash
python3 -m tools.aegis_skillset.cli validate .
python3 -m tools.aegis_skillset.cli distribution-check .
python3 scripts/build_skillset.py --check
python3 scripts/build_aegis_distributions.py --check
python3 -m tools.aegis_skillset.cli routing-check .
python3 -m tools.aegis_skillset.cli installed-platform-check .
python3 scripts/validate_generated_skills.py
python3 -m unittest discover -s tests/skillset -v
python3 -m unittest discover -s tests/project_state -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
```

Expected: all deterministic checks PASS while `installed-platform-check` truthfully prints a blocked Task 6 state due to missing fresh external evidence.

- [ ] **Step 6: Re-verify all six protected blob SHAs again**

Use `git hash-object` and compare to Global Constraints. Any mismatch blocks this package.

- [ ] **Step 7: Commit workflow closure**

```bash
git add .github/workflows/skillset.yml tests/skillset
git commit -m "ci: gate aegis plugin distribution artifacts"
```

- [ ] **Step 8: Push the exact P32 result and require fresh hosted CI**

Push normally; do not amend/recreate the reviewed result after CI. Require both:

- `Aegis Skillset Integrity` PASS;
- `Aegis Project State Integrity` PASS.

Capture the exact branch-head SHA and the two run URLs/IDs.

- [ ] **Step 9: Return the P32 materialization block**

Return actual observed values in this shape:

```yaml
stage: P32
owner: aegis-implementation
surface: CODE_EXECUTION
result_revision: <actual exact remote branch head SHA>
materialized_ref: <actual exact GitHub commit or PR ref>
verification:
  skillset_ci: <actual fresh run ref>
  project_state_ci: <actual fresh run ref>
test_distribution_artifact: aegis-distributions-0.1.0-task6.1
return_surface: CONTROL_REVIEW
```

Angle-bracket fields above are schema notation only; the returned evidence block must contain concrete observed values and no angle-bracket text.

**Exit Criteria:** Repository implementation is materialized and deterministically green; real installed-platform evidence is separate and pending P34.

---

# P34 External Evidence Packages

These are not Codex repository-implementation tasks. After Task Package 5 returns to `CONTROL_REVIEW`, ChatGPT/human testing supplies platform evidence. P34 remains blocked until these packages are complete.

### Evidence Package 6 — Materialize and prove the two installed catalog environments

**Purpose:** Establish real `FULL_SPECIALIST` and `COMPOSITE_ONLY` catalog truth before interpreting behavior.

**Files created only after real observations exist:**
- `skillset/dogfood/evidence/task6-catalog-full-plugin-v0.2.1.json`
- `skillset/dogfood/evidence/task6-catalog-standalone-v0.2.1.json`
- Modify: `skillset/dogfood/installed-platform-rerun-v0.2.1.json` to reference real catalog artifacts after they are committed.

- [ ] **Step 1: Use the fresh CI source-bundle artifact from Task Package 5**

Verify the workflow run belongs to the exact P32 result revision. Do not use an older local bundle.

- [ ] **Step 2: Materialize Environment A as one test Aegis Plugin**

Use the actual supported ChatGPT Plugin creation/import UI available to the test account to create one test Plugin whose included Skills are the nine Skill bundles from release `0.1.0-task6.1`.

If the platform cannot create/import a local/test multi-Skill Plugin on the required ChatGPT surface, stop with:

```text
BLOCKED_ENVIRONMENT
reason = supported local multi-Skill Plugin materialization unavailable
```

Do **not** substitute nine separately installed personal Skills for final acceptance.

- [ ] **Step 3: Capture durable Environment A evidence**

The reviewer-accessible evidence must show, from platform/plugin detail state rather than prompt prose:

- one Aegis Plugin distribution;
- exact nine included Skills;
- test release/build identity used;
- ChatGPT surface/account/workspace context sufficient to reproduce the run;
- no simultaneous Standalone Aegis distribution.

Materialize screenshots/export/details at a durable reviewer-accessible ref such as a GitHub PR/issue attachment or another stable platform artifact.

- [ ] **Step 4: Write the Environment A catalog JSON using only observed values**

Populate schema version `0.1`, `fresh_platform_event=true`, `complete_catalog_capture=true`, the actual platform event/observation ID from Step 3, `surface={product: chatgpt, surface: web}`, one observed Plugin distribution with id `aegis` and release `0.1.0-task6.1`, the exact nine installed Skill names, an empty `component_release_versions` map unless the platform exposes per-component versions, `release_manifest_ref=skillset/releases/aegis-0.1.0-task6.1.json`, and the actual durable `materialization_ref` from Step 3.

- [ ] **Step 5: Materialize Environment B as Standalone Aegis only**

Use a clean installation context with only the Standalone `aegis` distribution from release `0.1.0-task6.1`. No Plugin and no individually installed Aegis specialists may be present.

- [ ] **Step 6: Capture and write Environment B catalog evidence**

Use the same envelope with one observed distribution `{kind: standalone, id: aegis-standalone, release_version: 0.1.0-task6.1}` and `installed_skills=[aegis]`, using the actual event/observation ID and durable materialization ref.

- [ ] **Step 7: Evaluate both catalog artifacts before any behavioral PASS claim**

Expected:

```text
Environment A -> FULL_SPECIALIST / PASS
Environment B -> COMPOSITE_ONLY / PASS
```

Any `PARTIAL_CATALOG`, `MIXED_REVISION`, `DUPLICATE_DISTRIBUTION`, missing durable ref, or incomplete capture stops the behavioral Gate with the exact blocker.

**Exit Criteria:** The two legal runtime modes are independently proven by platform evidence; no behavior trace is used to infer Skill availability.

---

### Evidence Package 7 — Fresh four-case behavioral rerun and P34 handoff

**Purpose:** Re-run the unchanged Task 6 cases under proven catalogs and let the existing terminal-trace oracle decide behavior.

**Files created only from fresh observations:**
- `skillset/dogfood/evidence/task6-direct-specialist-v0.2.1.json`
- `skillset/dogfood/evidence/task6-ambiguous-router-v0.2.1.json`
- `skillset/dogfood/evidence/task6-upstream-blocker-v0.2.1.json`
- `skillset/dogfood/evidence/task6-composite-fallback-v0.2.1.json`
- Modify: `skillset/dogfood/installed-platform-rerun-v0.2.1.json` with all eight real evidence refs (catalog + behavior pairs).

- [ ] **Step 1: Run `09-01-direct-specialist` in Environment A**

Use the protected prompt/case without expected-owner hints. Capture the complete terminal response and platform invocation evidence. Normal PASS requires `aegis-gate-review` to own the substantive/final P34 result; Project State support may appear first.

- [ ] **Step 2: Run `09-01-ambiguous-router` in Environment A**

Capture the complete terminal response. PASS requires central `aegis` to own the routing-only result and no specialist substantive ownership leak.

- [ ] **Step 3: Run `09-01-upstream-blocker-reroute` in Environment A**

Capture the complete terminal response. PASS requires accepted earlier-blocker short-circuit semantics and zero forbidden downstream P14/P15 substantive execution.

- [ ] **Step 4: Run `09-01-composite-fallback` in Environment B**

Run the unchanged protected case. Do not count prompt prose as unavailability evidence; the previously accepted COMPOSITE_ONLY catalog supplies that fact.

- [ ] **Step 5: Normalize four Behavior Evidence JSON artifacts**

Each artifact must use the v0.2 Behavior Evidence envelope from Task Package 4 and carry the actual fresh platform event ID plus complete normalized terminal trace. Do not synthesize unseen invocation events.

- [ ] **Step 6: Populate v0.2.1 evidence refs**

Cases 1-3 point to the accepted Environment A catalog artifact and their own behavior artifacts. Case 4 points to Environment B catalog evidence and its own behavior artifact.

- [ ] **Step 7: Run the strict installed-platform Gate**

Run:

```bash
python3 -m tools.aegis_skillset.cli installed-platform-gate .
```

Required result for acceptance:

```text
09-01-direct-specialist: PASS
09-01-ambiguous-router: PASS
09-01-upstream-blocker-reroute: PASS
09-01-composite-fallback: PASS
INSTALLED_PLATFORM_STATE PASS
```

If any semantic violation occurs, stop at P35 and classify it. If any capture/catalog evidence is incomplete, preserve `BLOCKED_EVIDENCE`. If the test Plugin/Standalone environment is unavailable or invalid, preserve `BLOCKED_ENVIRONMENT`.

- [ ] **Step 8: Materialize the exact evidence commit and fresh CI**

Commit the evidence artifacts + populated v0.2.1 manifest, push normally, and require fresh Skillset/Project State CI on that exact evidence revision.

- [ ] **Step 9: Return to independent P34**

Return the exact evidence revision, materialized ref, strict Gate output, and fresh CI refs to `aegis-gate-review` on `CONTROL_REVIEW`.

Do not mutate `gate-skill-decomposition-v02-pr9` to PASS inside this evidence package. P34 decides the Gate independently.

**Exit Criteria:** Four real protected traces are attached to accepted catalog evidence and the strict executable Gate is reviewable from a durable exact revision.

---

# Conditional P34 / P35 / P23 Handoff

After Evidence Package 7:

```text
P34 independent review
        |
        +-- 4/4 PASS + admissible evidence
        |       -> gate-skill-decomposition-v02-pr9 may become PASS
        |       -> P23 may promote Skill Decomposition v0.2 to Current
        |       -> preserve int-pr9 historical nonconforming-at-merge truth
        |       -> rerun Execution Surface v0.1 promotion review
        |       -> rerun Plugin Distribution v0.1 dependency/promotion review
        |
        +-- semantic FAIL
        |       -> P35 classify before changing descriptions/spec/oracle
        |
        +-- incomplete evidence
        |       -> BLOCKED_EVIDENCE
        |
        +-- unavailable/invalid Plugin environment
                -> BLOCKED_ENVIRONMENT
```

Plugin Distribution v0.1 does not become Current merely because its test bundle enabled PR #9 evidence collection. Its own Current promotion remains a later governance decision after its upstream Skill Decomposition dependency is trusted.

---

## P31 Surface Handoff Package

Repository implementation Task Packages 1-5 are packageable as:

```yaml
type: surface_handoff
stage: P32
stage_owner: aegis-implementation
from_surface: CONTROL_REASONING
to_surface: CODE_EXECUTION
preferred_executor: codex
reason: deterministic_plugin_distribution_and_task6_evidence_tooling
package_ref: docs/superpowers/plans/2026-08-29-aegis-plugin-distribution-v0.1.md
return_surface: CONTROL_REVIEW
```

Required P32 start preflight:

1. confirm branch `aegis/plugin-distribution-contract-v0.1` is synchronized with current `main` without silently changing the protected semantic files;
2. inspect `git status`, `git diff`, and current PR #13 head;
3. verify the two reviewed Authority/spec files and this plan are present;
4. run `git hash-object` on all six protected files and compare to Global Constraints;
5. execute Task Packages 1-5 in order with RED -> GREEN evidence and small commits;
6. return an exact remote `materialized_ref`; local-only completion is insufficient P34 evidence.

---

## Plan Self-Review

**Spec coverage:**

- Product / Plugin / Skill / App separation -> Task Packages 1-3.
- Exact nine-Skill normal catalog -> Task Packages 2-3.
- Standalone-only compatibility -> Task Packages 2-3 and Evidence Package 6.
- Five catalog states / fail-closed behavior -> Task Package 2.
- One release line + component digests -> Task Package 3.
- Whole-catalog upgrade safety represented by partial/mixed state rejection -> Task Package 2; no updater is built in v0.1.
- Apps orthogonal / no required Apps -> Task Package 2.
- Task 6 evidence-layer migration -> Task Package 4.
- Existing semantic oracle/cases preserved -> protected blob pins + Task Package 4/5 re-verification.
- Reviewer-accessible source bundle + catalog evidence -> Task Package 5 and Evidence Package 6.
- 4/4 installed-platform acceptance -> Evidence Package 7.
- Historical PR #9 nonconforming integration truth preserved -> Task Package 1 regression + conditional P34/P23 handoff.

**Placeholder scan:** No implementation step uses `TBD`, `TODO`, “similar to”, synthetic digest literals, or pre-filled fake platform evidence. Runtime-generated platform IDs/refs are explicitly copied from real observations during Evidence Packages 6-7.

**Type/name consistency:** `DistributionSpec`, `DistributionContract`, `CatalogEvaluation`, `FULL_SPECIALIST`, `COMPOSITE_ONLY`, `PARTIAL_CATALOG`, `MIXED_REVISION`, `DUPLICATE_DISTRIBUTION`, `0.1.0-task6.1`, `installed-platform-rerun-v0.2.1.json`, `catalog_evidence_ref`, and `behavior_evidence_ref` are used consistently across all packages.

**Scope check:** No Skill-description tuning, routing-oracle change, lifecycle ownership change, required App integration, product updater, or production Plugin release is included. Unsupported ChatGPT local/test Plugin materialization is an explicit `BLOCKED_ENVIRONMENT`, not a reason to weaken the Gate.
