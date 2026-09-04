# Repository Identity Targeted Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make repository-backed Aegis P31/P32/P33/P36 execution handoffs explicitly repository-bound and fail closed before package/anchor/cursor reconciliation, while proving exact-nine candidate Plugin parity without mutating the published `0.1.0-beta.3` release or prematurely consuming RC-I01 `0.2.0-beta.1`.

**Architecture:** Keep Aegis instruction-first: no repository resolver service and no new runtime orchestration layer. Add repository identity and package-materialization semantics to canonical handoff/implementation/Gate instructions, prove them with bounded deterministic corpora and tests, regenerate distributed Skills, and create a non-published exact-nine candidate Plugin parity artifact from the exact implementation revision. Separate current-candidate parity from immutable beta.3 historical release validation.

**Tech Stack:** Markdown Skill contracts, Python 3.12, `unittest`, JSON dogfood corpora, deterministic Skill generation, GitHub Actions artifacts.

**Spec:** `docs/execution-surface-contract-v0.2-repository-identity-repair.md`

## Global Constraints

- Repository: `Mostorm-Labs/aegis`.
- P17 repository-identity Platform Authority: `e851531a000c5c84ee2f00b429d813c048d29ab8`.
- Repository-identity core P20 Authority: `61aa42e98558a1621b0228223835473f248ee869`.
- Current materialization-proof sub-scope Authority: `8fc76fc6c10951c4748c04be60bbc1c953e6de7e`.
- P23 materialization supersession review: `5109657871`.
- Core invariant: `Repository Identity != Task Anchor != Execution Cursor`.
- Core addressing rule: `A revision is not a repository locator.`
- Repository-backed P31/P32/P33/P36 must carry `repository.provider`, `repository.full_name`, `package_ref`, `package_materialization_ref`, and a non-null `task_anchor` when baseline-dependent.
- Repository identity preflight happens before package resolution, ancestry checks, worktree creation, cursor classification, or authored mutation.
- Wrong/missing/ambiguous repository identity fails closed as `BLOCKED_REPOSITORY_IDENTITY`; ambient context never selects a substitute repository.
- Dirty work in the declared repository is preserved; isolation stays inside that declared repository.
- Required deterministic corpus: `RI-S01..RI-S10` = 10/10.
- Required negative qualification: `RI-M01..RI-M06` = 6/6, `negative_false_acceptance = 0`.
- Required fresh installed Codex corroboration: `RI-PFC01..RI-PFC06` = 6/6.
- Safety thresholds: wrong-repository authored mutations = 0; dirty-work loss = 0; cross-repository SHA follow events = 0; package-materialization repository mismatches accepted = 0; P33 repository-preflight ordering violations = 0; P36 repository-contract omissions = 0; canonical/generated candidate mismatches = 0.
- Published `0.1.0-beta.3` is immutable historical release materialization. Do not rewrite its manifest, Skill payload, Plugin version, tag, or release identity.
- This repair must not create or consume RC-I01 `0.2.0-beta.1` release manifest/tag/GitHub Release/published Plugin.
- Candidate Plugin evidence is `CANDIDATE_PLUGIN_PARITY_EVIDENCE`: exact-revision, reviewer-resolvable, exact-nine, non-published, no public release identity.
- Do not reopen PP0, the 40-WorkScope harness, SERVICE_PROFILE, rollout expansion, prior Control Plane P34, or Project State release closure.

---

## File Structure

**Canonical execution contract and specialist behavior**
- Modify `skillset/shared/handoff-contract.md` — canonical repository-bound surface-handoff schema and fail-closed ordering.
- Modify `skillset/skills/aegis-implementation/SKILL.md` — P31/P32/P33 repository identity obligations and return binding.
- Modify `skillset/skills/aegis-implementation/references/implementation-control.md` — detailed package/preflight/resume rules.
- Modify `skillset/skills/aegis-gate-review/SKILL.md` — repository-backed P36 CODE_REVERIFY parity.
- Modify `skillset/skills/aegis-gate-review/references/gate-review.md` — P36 repository preflight/materialization rules.

**Deterministic repository-identity proof**
- Create `skillset/dogfood/repository-identity-v0.2.json` — normative `RI-S01..RI-S10` scenarios.
- Create `skillset/dogfood/repository-identity-negative-v0.2.json` — normative `RI-M01..RI-M06` perturbations.
- Create `tests/skillset/test_repository_identity_handoff.py` — canonical markers, scenario decisions, negative rejection, P33/P36 ordering, generated parity.
- Modify `tests/skillset/test_execution_anchor_resume_cursor.py` — assert repository preflight precedes P33 cursor classification while retaining all four existing cursor classes.

**Published-release preservation and candidate Plugin parity**
- Modify `tools/aegis_skillset/package.py` — add historical published-release manifest validation against the committed published Plugin Skill payload without changing current release-manifest rendering.
- Modify `scripts/build_aegis_distributions.py` — add `--check-published` for immutable published release validation.
- Modify `tools/aegis_skillset/plugin_materialization.py` — add `check_published_materialization`, plus candidate parity artifact writer/checker.
- Modify `scripts/build_openai_plugin_materialization.py` — add `--check-published` while retaining existing `--write`/`--check` semantics.
- Create `scripts/build_candidate_plugin_parity.py` — deterministic exact-nine non-release candidate parity artifact CLI.
- Modify `tests/skillset/test_openai_plugin_materialization.py` — separate published beta.3 history checks from current candidate parity.
- Create `tests/skillset/test_candidate_plugin_parity.py` — candidate artifact schema, exact-nine inventory, digests, required repository-identity markers, and reproducibility.

**Generated/distributed and CI surfaces**
- Regenerate `skills/**` only through `python3 scripts/build_skillset.py --write`.
- Modify `.github/workflows/skillset.yml` — historical beta.3 checks use published modes; add exact-head candidate parity artifact job; do not manufacture a beta.3 candidate from current Skills.
- Update `skillset/releases/aegis-0.1.0-task6.1.json` only if the existing development-oracle manifest check requires current generated Skill digests; do not modify `skillset/releases/aegis-0.1.0-beta.3.json`.
- Do not modify `plugins/aegis/**` in this repair.

---

### Task 1: Repository-bound canonical handoff and specialist instructions

**Files:**
- Modify: `skillset/shared/handoff-contract.md`
- Modify: `skillset/skills/aegis-implementation/SKILL.md`
- Modify: `skillset/skills/aegis-implementation/references/implementation-control.md`
- Modify: `skillset/skills/aegis-gate-review/SKILL.md`
- Modify: `skillset/skills/aegis-gate-review/references/gate-review.md`
- Test: `tests/skillset/test_repository_identity_handoff.py`

**Interfaces:**
- Consumes: P17 `e851531a...`, P20 `61aa42e...`, materialization amendment `8fc76fc6...`.
- Produces: one canonical repository-backed envelope contract used by P31/P32/P33/P36 and all generated Skills.

- [ ] **Step 1: Write failing canonical contract tests**

Create `tests/skillset/test_repository_identity_handoff.py` with tests that require these exact markers in `skillset/shared/handoff-contract.md` and the affected specialists:

```python
REQUIRED = (
    "Repository Identity != Task Anchor != Execution Cursor",
    "A revision is not a repository locator",
    "repository.provider",
    "repository.full_name",
    "package_materialization_ref",
    "BLOCKED_REPOSITORY_IDENTITY",
    "repository identity preflight",
    "cross-repository",
    "dirty",
)
```

Also assert a repository-backed example envelope includes:

```yaml
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
package_ref: 1111111111111111111111111111111111111111
package_materialization_ref: https://github.com/Mostorm-Labs/aegis/pull/1
task_anchor:
  revision: 2222222222222222222222222222222222222222
  relation: ancestor
```

- [ ] **Step 2: Run the new test and verify RED**

Run:

```bash
python3 -m unittest tests.skillset.test_repository_identity_handoff -v
```

Expected: failures because the canonical/shared and specialist texts do not yet contain the repository identity schema and fail-closed rules.

- [ ] **Step 3: Update `skillset/shared/handoff-contract.md`**

Add a repository-backed envelope that explicitly includes `repository` and `package_materialization_ref`, state that all bare revisions are scoped to `repository.full_name`, require repository identity preflight before package/anchor/cursor work, and define `BLOCKED_REPOSITORY_IDENTITY` for missing/mismatched/ambiguous repository context.

Preserve the exact existing Codex execution prefix; do not alter its text. Add the repository fields to the YAML envelope, not to the prefix.

- [ ] **Step 4: Update `aegis-implementation` canonical Skill and reference**

Add these normative behaviors to both the Skill and `implementation-control.md`:

```text
P31 repository-backed package:
  repository.provider + repository.full_name mandatory
  package_materialization_ref mandatory and same-repository

P32/P33 receiving order:
  repository identity
  -> declared-repository checkout/worktree
  -> package resolution/materialization match
  -> task_anchor ancestry
  -> resume_cursor classification
  -> authored mutation

wrong repository / unresolved declared repository:
  BLOCKED_REPOSITORY_IDENTITY
  continue_execution: false
```

P33 must explicitly say repository mismatch is handled before `EXACT_CURSOR`, `DESCENDANT_CURSOR`, `ANCHOR_DESCENDANT_WITHOUT_CURSOR`, or `DIVERGED` is claimed.

Execution returns must carry repository identity and materialize repository result evidence in the declared repository unless the package explicitly authorized a separate evidence repository.

- [ ] **Step 5: Update `aegis-gate-review` P36 canonical Skill and reference**

Require repository-backed CODE_REVERIFY to use the same repository object, package-materialization match, dirty-work preservation, and preflight ordering as P32/P33 before any repair mutation.

- [ ] **Step 6: Run focused tests**

Run:

```bash
python3 -m unittest tests.skillset.test_repository_identity_handoff -v
python3 -m unittest tests.skillset.test_execution_anchor_resume_cursor -v
```

Expected: repository contract tests PASS and all prior anchor/cursor semantics remain PASS.

- [ ] **Step 7: Commit Task 1**

```bash
git add skillset/shared/handoff-contract.md \
  skillset/skills/aegis-implementation/SKILL.md \
  skillset/skills/aegis-implementation/references/implementation-control.md \
  skillset/skills/aegis-gate-review/SKILL.md \
  skillset/skills/aegis-gate-review/references/gate-review.md \
  tests/skillset/test_repository_identity_handoff.py
git commit -m "fix: bind execution handoffs to repository identity"
```

---

### Task 2: Deterministic RI-S01..RI-S10 and RI-M01..RI-M06 qualification

**Files:**
- Create: `skillset/dogfood/repository-identity-v0.2.json`
- Create: `skillset/dogfood/repository-identity-negative-v0.2.json`
- Modify: `tests/skillset/test_repository_identity_handoff.py`
- Modify: `tests/skillset/test_execution_anchor_resume_cursor.py`

**Interfaces:**
- Consumes: canonical decision rules from Task 1.
- Produces: reviewer-readable deterministic evidence for all ten mandatory scenarios and all six direct negative perturbations.

- [ ] **Step 1: Materialize the ten scenario records**

Create `skillset/dogfood/repository-identity-v0.2.json` with exactly `RI-S01` through `RI-S10` and the fields required by P20. Encode the normative outcomes exactly:

```text
RI-S01 correct Aegis repository + matching package -> CONTINUE_TO_ANCHOR_PREFLIGHT
RI-S02 current Axtp + Aegis available -> ISOLATE_DECLARED_REPOSITORY
RI-S03 current Axtp + Aegis unavailable -> BLOCKED_REPOSITORY_IDENTITY
RI-S04 repository object missing -> BLOCKED_REPOSITORY_IDENTITY
RI-S05 SHA exists only in Axtp -> BLOCKED_REPOSITORY_IDENTITY
RI-S06 package materialization URL points to Axtp -> BLOCKED_REPOSITORY_IDENTITY
RI-S07 multiple repos / ambient Axtp -> execute only in Aegis
RI-S08 dirty Aegis -> preserve dirty state; isolate inside Aegis if needed
RI-S09 P33 wrong repo + valid-looking cursor -> BLOCKED before cursor classification
RI-S10 P36 wrong repo -> same repository preflight as P32/P33; zero wrong-repo mutation
```

- [ ] **Step 2: Materialize six negative perturbations**

Create `skillset/dogfood/repository-identity-negative-v0.2.json` with exactly:

```text
RI-M01 remove repository object
RI-M02 change repository.full_name to another accessible repository
RI-M03 keep repository correct but use another-repository package_materialization_ref
RI-M04 package SHA resolves only in another repository
RI-M05 ambient repository overrides declared repository
RI-M06 P33 cursor classified before repository preflight
```

Every case must declare `expected_rejected: true`, `continue_execution: false` when applicable, and `wrong_repository_authored_mutations: 0`.

- [ ] **Step 3: Extend tests to validate scenario semantics, not just IDs**

Assert exactly ten unique scenario IDs and six unique mutation IDs. For each blocking scenario, assert `expected_mutated_repositories` is empty. For `RI-S02`, `RI-S07`, and `RI-S08`, assert any execution/isolation repository is `Mostorm-Labs/aegis` and never `Mostorm-Labs/axtp`.

For `RI-S09` and `RI-M06`, assert `p33_classification_performed` is false before repository identity succeeds.

- [ ] **Step 4: Strengthen the existing anchor/cursor regression**

In `tests/skillset/test_execution_anchor_resume_cursor.py`, retain the four existing reconciliation classes, then add an assertion that repository identity preflight text appears before the P33 classification language in the canonical implementation reference.

- [ ] **Step 5: Run qualification tests**

```bash
python3 -m unittest tests.skillset.test_repository_identity_handoff -v
python3 -m unittest tests.skillset.test_execution_anchor_resume_cursor -v
```

Expected: 10/10 scenario coverage, 6/6 negative coverage, zero false acceptance in the deterministic corpus, prior cursor behavior unchanged.

- [ ] **Step 6: Commit Task 2**

```bash
git add skillset/dogfood/repository-identity-v0.2.json \
  skillset/dogfood/repository-identity-negative-v0.2.json \
  tests/skillset/test_repository_identity_handoff.py \
  tests/skillset/test_execution_anchor_resume_cursor.py
git commit -m "test: qualify repository identity fail-closed behavior"
```

---

### Task 3: Separate immutable beta.3 history from exact-head candidate Plugin parity

**Files:**
- Modify: `tools/aegis_skillset/package.py`
- Modify: `scripts/build_aegis_distributions.py`
- Modify: `tools/aegis_skillset/plugin_materialization.py`
- Modify: `scripts/build_openai_plugin_materialization.py`
- Create: `scripts/build_candidate_plugin_parity.py`
- Modify: `tests/skillset/test_openai_plugin_materialization.py`
- Create: `tests/skillset/test_candidate_plugin_parity.py`

**Interfaces:**
- Consumes: current generated `skills/**`, immutable `skillset/releases/aegis-0.1.0-beta.3.json`, committed `plugins/aegis/**` historical payload.
- Produces: `check_published_*` history validation plus a non-release candidate parity directory containing `candidate-plugin-parity.json` and exact-nine `skills/`.

- [ ] **Step 1: Write RED tests for published-history validation**

Add tests proving:

1. beta.3 published Plugin Skill trees match the frozen release-manifest `tree_sha256`/ZIP digests;
2. published Plugin manifest version remains `0.1.0-beta.3`;
3. modifying current canonical `skills/aegis-implementation` in a temp fixture does not redefine the published beta.3 check;
4. modifying the published Plugin payload itself makes the published check fail.

- [ ] **Step 2: Add `validate_published_release_manifest`**

In `tools/aegis_skillset/package.py`, add a function that reads the committed release manifest and validates its plugin/standalone Skill entries against a supplied published Skill root, defaulting to `plugins/aegis/skills`. Compare both `tree_sha256` and deterministic Skill ZIP SHA256. Do not change `render_release_manifest`.

- [ ] **Step 3: Add `--check-published` to `build_aegis_distributions.py`**

Make published checking an explicit mode that validates the frozen manifest against the published Skill payload and prints:

```text
AEGIS_PUBLISHED_RELEASE_STATE_OK
```

Retain existing `--check` semantics for a current release candidate; do not silently reinterpret it.

- [ ] **Step 4: Add `check_published_materialization`**

In `tools/aegis_skillset/plugin_materialization.py`, validate:

- marketplace manifest remains expected;
- committed Plugin manifest equals `render_plugin_manifest("0.1.0-beta.3")`;
- exact-nine inventory matches release manifest;
- each committed `plugins/aegis/skills/<name>` digest matches the frozen beta.3 release entry.

Do not require current generated `skills/**` to equal beta.3 in this published-history mode.

- [ ] **Step 5: Add `--check-published` to `build_openai_plugin_materialization.py`**

Keep existing `--write` and `--check` unchanged. Add a third mutually exclusive mode that calls `check_published_materialization` and prints:

```text
OPENAI_PUBLISHED_PLUGIN_MATERIALIZATION_OK
```

- [ ] **Step 6: Write RED candidate parity tests**

Create `tests/skillset/test_candidate_plugin_parity.py` expecting these functions:

```python
write_candidate_parity_artifact(root, output_dir, source_revision)
check_candidate_parity_artifact(root, output_dir, source_revision)
```

The artifact must contain exactly:

```text
candidate-plugin-parity.json
skills/<the exact nine Aegis Skill trees>/...
```

Metadata must include:

```json
{
  "artifact_class": "CANDIDATE_PLUGIN_PARITY_EVIDENCE",
  "source_revision": "40-lowercase-hex",
  "repository": {"provider": "github", "full_name": "Mostorm-Labs/aegis"},
  "public_release": false,
  "release_tag": null,
  "release_version_claim": null,
  "skill_inventory_count": 9,
  "exact_nine": true
}
```

The checker must reject wrong source revision, missing/extra Skill directories, digest mismatch, and absence of repository-identity markers in candidate copies of `aegis-implementation` or `aegis-gate-review`.

- [ ] **Step 7: Implement candidate parity writer/checker and CLI**

In `plugin_materialization.py`, copy from generated `skills/<name>` into the output `skills/` tree, calculate deterministic tree digests, write `candidate-plugin-parity.json`, then verify the output.

Create `scripts/build_candidate_plugin_parity.py` with:

```text
--source-revision <40-char SHA>
--output-dir <directory>
--write | --check
```

It must not write `plugins/aegis/**`, a release manifest, `.codex-plugin/plugin.json`, a tag, or release-version metadata.

- [ ] **Step 8: Run focused materialization tests**

```bash
python3 -m unittest tests.skillset.test_openai_plugin_materialization -v
python3 -m unittest tests.skillset.test_candidate_plugin_parity -v
```

Expected: immutable beta.3 validation PASS; candidate parity artifact reproducible and exact-nine; deliberate drift cases rejected.

- [ ] **Step 9: Commit Task 3**

```bash
git add tools/aegis_skillset/package.py \
  scripts/build_aegis_distributions.py \
  tools/aegis_skillset/plugin_materialization.py \
  scripts/build_openai_plugin_materialization.py \
  scripts/build_candidate_plugin_parity.py \
  tests/skillset/test_openai_plugin_materialization.py \
  tests/skillset/test_candidate_plugin_parity.py
git commit -m "test: separate published plugin history from candidate parity"
```

---

### Task 4: Regenerate distributed Skills without rewriting the published Plugin

**Files:**
- Generated: `skills/**`
- Possibly modify: `skillset/releases/aegis-0.1.0-task6.1.json`
- Must not modify: `skillset/releases/aegis-0.1.0-beta.3.json`
- Must not modify: `plugins/aegis/**`

**Interfaces:**
- Consumes: canonical Skill changes from Task 1.
- Produces: deterministic generated standalone Skills carrying identical repository-identity contract text.

- [ ] **Step 1: Regenerate Skill distributions**

```bash
python3 scripts/build_skillset.py --write
```

- [ ] **Step 2: Verify generated parity**

```bash
python3 scripts/build_skillset.py --check
python3 scripts/validate_generated_skills.py
```

Expected: both exit 0.

- [ ] **Step 3: Refresh only the development-oracle manifest if required**

Run:

```bash
python3 scripts/build_aegis_distributions.py --check
```

If this fails only because `skillset/releases/aegis-0.1.0-task6.1.json` tracks current generated Skill digests, update that development manifest using:

```bash
python3 scripts/build_aegis_distributions.py --write-manifest
python3 scripts/build_aegis_distributions.py --check
```

Then prove beta.3 itself remains untouched:

```bash
git diff --exit-code 8fc76fc6c10951c4748c04be60bbc1c953e6de7e -- skillset/releases/aegis-0.1.0-beta.3.json plugins/aegis
```

Expected: no diff.

- [ ] **Step 4: Verify published beta.3 against its frozen payload**

```bash
python3 scripts/build_aegis_distributions.py --version 0.1.0-beta.3 --check-published
python3 scripts/build_openai_plugin_materialization.py --release-version 0.1.0-beta.3 --check-published
```

Expected: both exit 0.

- [ ] **Step 5: Commit generated surfaces**

```bash
git add skills skillset/releases/aegis-0.1.0-task6.1.json
git commit -m "build: regenerate repository-bound Aegis skills"
```

If the development manifest did not change, omit it from `git add`.

---

### Task 5: CI exact-head candidate Plugin parity artifact

**Files:**
- Modify: `.github/workflows/skillset.yml`
- Test: `tests/skillset/test_workflow_paths.py`
- Test: `tests/skillset/test_candidate_plugin_parity.py`

**Interfaces:**
- Consumes: candidate parity CLI and published-history modes from Task 3.
- Produces: reviewer-resolvable GitHub Actions artifact built from the exact implementation head SHA.

- [ ] **Step 1: Write workflow-path RED assertions**

Extend `tests/skillset/test_workflow_paths.py` to require the new candidate parity script in both push and pull-request path filters and require the workflow to reference `--check-published` for beta.3.

- [ ] **Step 2: Stop treating beta.3 as a current candidate**

In `.github/workflows/skillset.yml`:

- replace current-head beta.3 release-manifest check with `python3 scripts/build_aegis_distributions.py --version 0.1.0-beta.3 --check-published`;
- replace current-head beta.3 Plugin materialization check with `python3 scripts/build_openai_plugin_materialization.py --release-version 0.1.0-beta.3 --check-published`;
- remove or replace any step that builds a new `0.1.0-beta.3` Installation Kit from current generated Skills. Do not relabel current Skills as beta.3.

Keep the existing non-release test distribution (`0.1.0-task6.1`) path available for ordinary regressions.

- [ ] **Step 3: Add a dedicated exact-head candidate parity job**

Use an exact-head checkout:

```yaml
- uses: actions/checkout@v4
  with:
    ref: ${{ github.event.pull_request.head.sha || github.sha }}
```

Derive the source revision once:

```bash
SOURCE_REVISION="$(git rev-parse HEAD)"
```

Build and check:

```bash
python3 scripts/build_candidate_plugin_parity.py \
  --source-revision "$SOURCE_REVISION" \
  --output-dir /tmp/aegis-repository-identity-plugin-parity \
  --write
python3 scripts/build_candidate_plugin_parity.py \
  --source-revision "$SOURCE_REVISION" \
  --output-dir /tmp/aegis-repository-identity-plugin-parity \
  --check
```

Upload `/tmp/aegis-repository-identity-plugin-parity/` using `actions/upload-artifact@v4` with an artifact name containing the exact `SOURCE_REVISION` or the exact GitHub head SHA expression.

- [ ] **Step 4: Run workflow-related tests locally**

```bash
python3 -m unittest tests.skillset.test_workflow_paths -v
python3 -m unittest tests.skillset.test_candidate_plugin_parity -v
```

- [ ] **Step 5: Commit Task 5**

```bash
git add .github/workflows/skillset.yml tests/skillset/test_workflow_paths.py
git commit -m "ci: publish exact-head repository identity parity evidence"
```

---

### Task 6: Full deterministic qualification, materialization, and platform-evidence handoff

**Files:**
- No new production files expected.
- Evidence: exact implementation PR/commit, CI workflow run/artifact, durable PR comments/reviews for `RI-PFC01..RI-PFC06`.

**Interfaces:**
- Consumes: all implementation tasks.
- Produces: the exact evidence graph P34 will review.

- [ ] **Step 1: Run full Skillset and Project State regression commands**

```bash
python3 -m tools.aegis_skillset.cli validate .
python3 scripts/build_skillset.py --check
python3 -m tools.aegis_skillset.cli distribution-check .
python3 scripts/build_aegis_distributions.py --check
python3 scripts/build_aegis_distributions.py --version 0.1.0-beta.3 --check-published
python3 scripts/build_openai_plugin_materialization.py --release-version 0.1.0-beta.3 --check-published
python3 -m tools.aegis_skillset.cli routing-check .
python3 -m tools.aegis_skillset.cli installed-platform-check .
python3 scripts/validate_generated_skills.py
python3 -m unittest discover -s tests/skillset -v
python3 -m unittest discover -s tests/project_state -v
python3 evals/scripts/validate_corpus.py
python3 -m unittest discover -s evals/tests -v
```

Expected: all commands exit 0. No result is called Gate-ready from partial output.

- [ ] **Step 2: Prove forbidden release surfaces are unchanged**

```bash
git diff --exit-code 8fc76fc6c10951c4748c04be60bbc1c953e6de7e -- \
  skillset/releases/aegis-0.1.0-beta.3.json \
  plugins/aegis

git status --short
```

Expected: first command exits 0; second shows no uncommitted work before result materialization.

- [ ] **Step 3: Push the exact implementation result and open/update its implementation PR**

Record:

```bash
RESULT_REVISION="$(git rev-parse HEAD)"
printf '%s\n' "$RESULT_REVISION"
```

The P32 return must use this exact pushed revision and the reviewer-resolvable implementation PR as `materialized_ref`.

- [ ] **Step 4: Resolve CI and exact-head candidate artifact**

P32 must return the exact GitHub Actions workflow run and uploaded candidate parity artifact for `RESULT_REVISION`. The artifact metadata `source_revision` must equal `RESULT_REVISION`, inventory must be exactly nine, and affected Skill copies must contain repository-identity markers.

- [ ] **Step 5: Collect fresh `RI-PFC01..RI-PFC06` installed-Codex observations**

Run six controlled observations against the exact repaired Skill surface and store each outcome as a durable PR comment/review or equivalent reviewer-resolvable ref:

```text
RI-PFC01 Aegis declared, ambient Axtp -> Aegis wins; zero Axtp worktree/mutation
RI-PFC02 wrong cwd Axtp, Aegis available -> recognize wrong repo; move/isolate inside Aegis
RI-PFC03 declared repository unavailable -> BLOCKED_REPOSITORY_IDENTITY; no substitute
RI-PFC04 Aegis declared, package URL points to Axtp -> block before package/anchor/cursor reconciliation
RI-PFC05 dirty correct Aegis repository -> preserve dirty work; isolate inside Aegis
RI-PFC06 P33 wrong repository -> block before any cursor reconciliation class is claimed
```

Each observation must identify `RESULT_REVISION` and must report authored repository mutations explicitly. Agent claims without reviewer-resolvable observation evidence do not satisfy P20.

- [ ] **Step 6: Assemble the P32 return without issuing a Gate verdict**

Return exactly these evidence classes:

```yaml
repository_identity_return:
  stage: P32_IMPLEMENTATION_COMPLETE
  repository:
    provider: github
    full_name: Mostorm-Labs/aegis
  result_revision: $RESULT_REVISION
  materialized_ref: <implementation PR URL>

  deterministic:
    mandatory_scenarios: 10/10
    negative_cases_rejected: 6/6
    negative_false_acceptance: 0
    wrong_repository_authored_mutations: 0
    unrelated_dirty_work_loss_events: 0
    cross_repository_sha_follow_events: 0
    p33_repository_preflight_order_violations: 0
    p36_repository_contract_omissions: 0
    canonical_generated_skill_mismatches: 0

  candidate_plugin_parity:
    artifact_class: CANDIDATE_PLUGIN_PARITY_EVIDENCE
    source_revision: $RESULT_REVISION
    exact_nine: true
    public_release: false
    artifact_ref: <exact workflow artifact ref>

  historical_release_integrity:
    beta3_release_manifest_mutated: false
    beta3_published_plugin_mutated: false
    beta3_binding_weakened: false

  rc_i01_separation:
    v0_2_0_beta_1_release_manifest_created: false
    v0_2_0_beta_1_tag_created: false
    github_release_created: false

  platform:
    RI_PFC01: <durable ref>
    RI_PFC02: <durable ref>
    RI_PFC03: <durable ref>
    RI_PFC04: <durable ref>
    RI_PFC05: <durable ref>
    RI_PFC06: <durable ref>

  unresolved_required_refs: 0
  next_owner: aegis-gate-review
  next_stage: P34_GATE_REVIEW
```

At P32, do not claim `P34: PASS`.

---

## P30 Slice Boundary

Use one implementation slice:

```yaml
slice_id: RI-I01
name: REPOSITORY_IDENTITY_EXECUTION_HANDOFF_REPAIR
owner: aegis-implementation
stages: P31 -> P32
repository:
  provider: github
  full_name: Mostorm-Labs/aegis
task_anchor:
  revision: 8fc76fc6c10951c4748c04be60bbc1c953e6de7e
  relation: ancestor
resume_cursor: null
```

The future P31 package must add its exact `package_ref` and same-repository `package_materialization_ref` before any Codex P32 handoff is rendered.

## P30 Exit Criteria

P30 is complete when:

```yaml
P30_repository_identity_repair:
  slice_id: RI-I01
  authority:
    p17: e851531a000c5c84ee2f00b429d813c048d29ab8
    p20_core: 61aa42e98558a1621b0228223835473f248ee869
    p20_materialization: 8fc76fc6c10951c4748c04be60bbc1c953e6de7e
  repository_identity_implementation_scope: FROZEN
  beta3_published_materialization: IMMUTABLE
  rc_i01_release_materialization: OUT_OF_SCOPE
  pp0: NOT_REOPENED
  service_profile: NOT_AUTHORIZED
  rollout: DENIED
  release_authorized: false
  next_owner: aegis-implementation
  next_stage: P31_TASK_PACKAGING
```

Do not merge the P30 plan as implementation. Do not execute P32 from this plan without a materialized P31 package carrying repository identity, `package_ref`, `package_materialization_ref`, and the task anchor above.
