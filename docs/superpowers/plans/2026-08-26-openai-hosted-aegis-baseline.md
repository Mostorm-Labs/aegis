# OpenAI Hosted Aegis Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a provider-neutral-to-OpenAI bridge that uploads the current Aegis Skill as a pinned hosted Agent Skill, runs the current evaluation corpus without golden leakage, preserves provider evidence, and produces the first reproducible deterministic behavioral baseline when credentials are available.

**Architecture:** Keep the accepted `CommandAdapter -> external driver` seam. Add a pure-stdlib OpenAI provider package that (1) builds a deterministic Aegis skill zip, (2) uploads it through the Skills API, (3) sanitizes each evaluation case before the Responses API request, (4) mounts the pinned skill in hosted shell, (5) emits only the structured lifecycle result to stdout for the existing runner, and (6) stores full provider evidence separately. A one-command baseline orchestrator uploads once, invokes the existing runner, and writes a reproducibility manifest.

**Tech Stack:** Python 3 stdlib (`json`, `urllib`, `zipfile`, `hashlib`, `subprocess`, `time`, `pathlib`, `unittest`), OpenAI Skills API, OpenAI Responses API hosted shell, existing Aegis evaluator.

**Spec:** `docs/openai-hosted-skill-baseline-v0.1.md`

## Global Constraints

- Model is `gpt-5.6-sol`; reasoning effort is `medium`.
- Hosted execution mounts an uploaded Agent Skill by explicit `skill_id` and immutable `version`.
- Provider-visible case data must contain only `case_id`, `input.prompt`, and `input.context` projected to `case_id`, `prompt`, `context`.
- `expected`, severity, origin, category, title, tags, scores, thresholds, or other golden metadata must never be sent to the model.
- No external Python dependency is required for the baseline driver.
- Raw provider evidence must be preserved separately from normalized Aegis results.
- Missing API credentials must fail closed as `BLOCKED_ENVIRONMENT`; do not fabricate a baseline.
- Existing golden expectations, score thresholds, and current scorer semantics are not modified by this work.

---

### Task 1: Deterministic Aegis Skill Bundle

**Files:**
- Create: `evals/providers/__init__.py`
- Create: `evals/providers/openai/__init__.py`
- Create: `evals/providers/openai/bundle.py`
- Test: `evals/tests/test_openai_bundle.py`

**Interfaces:**
- Produces: `build_skill_bundle(skill_dir: Path, output_path: Path) -> SkillBundle`
- Produces: `SkillBundle(path: Path, sha256: str, top_level: str, files: tuple[str, ...])`

- [ ] **Step 1: Write the failing deterministic-bundle tests**

Test that two bundles built from identical files are byte-identical, contain exactly one `aegis/` top-level directory, include `aegis/SKILL.md`, exclude transient files such as `__pycache__` / `.DS_Store`, and return the SHA-256 of the exact zip bytes.

- [ ] **Step 2: Run the new test and verify RED**

Run: `python3 -m unittest evals.tests.test_openai_bundle -v`

Expected: import or missing-symbol failure for `evals.providers.openai.bundle`.

- [ ] **Step 3: Implement the minimal deterministic zip builder**

Use sorted relative paths, fixed ZIP timestamps, stable permissions, `ZIP_DEFLATED`, and a single top-level `aegis/` prefix.

- [ ] **Step 4: Re-run the test and verify GREEN**

Run: `python3 -m unittest evals.tests.test_openai_bundle -v`

Expected: PASS.

---

### Task 2: Golden-Safe Provider Projection and Prompt Contract

**Files:**
- Create: `evals/providers/openai/prompt.py`
- Create: `evals/providers/openai/result.strict.schema.json`
- Test: `evals/tests/test_openai_prompt.py`

**Interfaces:**
- Produces: `sanitize_case(case: dict) -> dict`
- Produces: `build_case_prompt(sanitized_case: dict) -> str`
- Produces: `build_strict_result_schema() -> dict`

- [ ] **Step 1: Write failing leakage tests**

Assert that a full golden case containing `expected`, category, severity, origin, title, and tags produces exactly the keys `case_id`, `prompt`, `context`; recursively serialize the sanitized object and assert golden sentinel strings do not appear.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest evals.tests.test_openai_prompt -v`

Expected: missing module/function failure.

- [ ] **Step 3: Implement minimal projection, prompt, and strict schema**

The prompt must explicitly require use of the mounted `aegis` skill, prohibit answer-key inference, and request only the normalized lifecycle fields. The strict schema uses `additionalProperties: false` and canonical status/defect vocabularies.

- [ ] **Step 4: Verify GREEN**

Run: `python3 -m unittest evals.tests.test_openai_prompt -v`

Expected: PASS.

---

### Task 3: OpenAI HTTP Transport and Hosted-Skill Payload

**Files:**
- Create: `evals/providers/openai/http.py`
- Create: `evals/providers/openai/api.py`
- Test: `evals/tests/test_openai_api.py`

**Interfaces:**
- Produces: `OpenAIHTTPTransport(api_key: str, base_url: str = "https://api.openai.com/v1")`
- Produces: `OpenAIHostedSkillAPI(transport)`
- Produces: `create_skill(zip_path: Path) -> SkillRef`
- Produces: `create_response(case: dict, skill: SkillRef, model: str, reasoning_effort: str) -> ProviderResponse`

- [ ] **Step 1: Write failing tests around serialized requests using an injected fake transport**

Verify Skills API upload uses multipart file data; Responses payload uses model `gpt-5.6-sol`, reasoning effort `medium`, a hosted shell `container_auto`, a `skill_reference` with both `skill_id` and version, and strict structured output. Verify the model input contains only the sanitized scenario and never the case `expected` sentinel.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest evals.tests.test_openai_api -v`

Expected: missing production types/functions.

- [ ] **Step 3: Implement the transport and API wrapper**

Use stdlib `urllib.request`. Map missing key / 401 / 403 to `ProviderEnvironmentError`; retry 429 and 5xx with bounded exponential delays; preserve HTTP response bodies in raised provider errors.

- [ ] **Step 4: Verify GREEN**

Run: `python3 -m unittest evals.tests.test_openai_api -v`

Expected: PASS.

---

### Task 4: Provider Response Extraction and Evidence Record

**Files:**
- Create: `evals/providers/openai/response.py`
- Test: `evals/tests/test_openai_response.py`

**Interfaces:**
- Produces: `extract_output_text(response: dict) -> str`
- Produces: `provider_evidence_record(...) -> dict`

- [ ] **Step 1: Write failing tests**

Cover completed Responses output with `output_text`, incomplete status, missing output text, usage propagation, response ID, latency, and retry count.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest evals.tests.test_openai_response -v`

Expected: missing module/functions.

- [ ] **Step 3: Implement extraction and fail-closed response handling**

Do not infer a result from tool-call traces or arbitrary prose when the structured output message is missing.

- [ ] **Step 4: Verify GREEN**

Run: `python3 -m unittest evals.tests.test_openai_response -v`

Expected: PASS.

---

### Task 5: Single-Case OpenAI Driver Compatible with Existing CommandAdapter

**Files:**
- Create: `evals/providers/openai/driver.py`
- Test: `evals/tests/test_openai_driver.py`

**Interfaces:**
- CLI stdin: full evaluation case JSON from existing `CommandAdapter`
- CLI stdout: only the structured Aegis normalized-result JSON text
- Side evidence: `<provider-evidence-dir>/<case-id>.json`
- Required args: `--skill-id`, `--skill-version`, `--evidence-dir`

- [ ] **Step 1: Write failing driver tests with injected/fake API behavior**

Verify the driver sanitizes before calling the API, writes provider evidence atomically, outputs the lifecycle result, rejects missing key as `BLOCKED_ENVIRONMENT`, and never writes secrets into evidence.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest evals.tests.test_openai_driver -v`

Expected: missing driver implementation.

- [ ] **Step 3: Implement the driver**

Keep provider metadata out of stdout so the accepted normalizer/scorer contract remains unchanged.

- [ ] **Step 4: Verify GREEN**

Run: `python3 -m unittest evals.tests.test_openai_driver -v`

Expected: PASS.

---

### Task 6: Baseline Orchestrator and Reproducibility Manifest

**Files:**
- Create: `evals/providers/openai/baseline.py`
- Create: `evals/scripts/run_openai_baseline.py`
- Test: `evals/tests/test_openai_baseline.py`

**Interfaces:**
- Produces: `compute_corpus_digest(cases_dir: Path) -> str`
- Produces: `write_baseline_manifest(...) -> Path`
- CLI creates/uploads skill once, invokes existing `evals/scripts/run_eval.py` with the OpenAI driver command, then writes `baseline-manifest.json` beside existing scorer artifacts.

- [ ] **Step 1: Write failing manifest/orchestration tests**

Verify manifest contains provider/model/reasoning, source and runner git SHA, skill ID/version/bundle digest, corpus digest/count, prompt version, response IDs, usage, latency/retries, deterministic gate, and semantic gate status. Verify missing provider evidence for any evaluated case blocks manifest completion.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest evals.tests.test_openai_baseline -v`

Expected: missing baseline functions/script.

- [ ] **Step 3: Implement orchestration**

The orchestrator must exit distinctly for provider environment failure versus deterministic evaluation failure. It must not reinterpret the existing scorer result.

- [ ] **Step 4: Verify GREEN**

Run: `python3 -m unittest evals.tests.test_openai_baseline -v`

Expected: PASS.

---

### Task 7: Full Offline Regression and Repository CI

**Files:**
- Modify only if needed: `.github/workflows/eval-corpus.yml`
- Modify: `evals/README.md`

**Interfaces:** Existing evaluator and new provider package must coexist without an API key in CI.

- [ ] **Step 1: Run all offline tests**

Run: `python3 evals/scripts/validate_corpus.py`

Expected: current corpus integrity PASS.

Run: `python3 -m unittest discover -s evals/tests -v`

Expected: all existing and new tests PASS; no live API access required.

- [ ] **Step 2: Update eval documentation**

Document offline verification, required environment variable for live runs, hosted-skill upload semantics, golden-leakage boundary, and artifact layout.

- [ ] **Step 3: Push feature branch and require fresh GitHub Actions evidence**

Do not treat local evidence as repository Gate evidence.

---

### Task 8: Real Aegis v0.1 Provider Baseline Attempt

**Files / Artifacts:**
- Runtime artifact directory: `artifacts/aegis-v0.1-openai-gpt-5.6-sol/`
- Durable baseline content is committed only if the run is complete and contains no secrets.

**Interfaces:** Requires `OPENAI_API_KEY` with Skills and Responses API access.

- [ ] **Step 1: Verify environment without printing the secret**

Check only whether `OPENAI_API_KEY` is set.

- [ ] **Step 2: Execute the one-command baseline**

Run:

```bash
python3 evals/scripts/run_openai_baseline.py \
  --output artifacts/aegis-v0.1-openai-gpt-5.6-sol
```

- [ ] **Step 3: Classify the result**

If credential or API access is missing, return `BLOCKED_ENVIRONMENT` and preserve only non-secret diagnostic evidence. If all current cases execute, verify provider evidence count equals corpus count, then report deterministic scores and critical safety errors from the existing scorer.

- [ ] **Step 4: P34 Gate Review**

Tooling Gate and Real Baseline Gate are reviewed separately. Never promote the baseline because tooling tests pass.

---

## P31 Task Package Summary

- **Authority:** `docs/openai-hosted-skill-baseline-v0.1.md` plus Current Evaluation Authority / Tooling.
- **Scope:** OpenAI hosted-skill provider integration, golden-safe case projection, evidence preservation, baseline orchestration.
- **Non-goals:** changing Aegis semantic authority, changing golden answers, changing scorer thresholds, semantic-judge implementation, multi-sample variance analysis.
- **Oracle:** offline tests for exact request/projection/manifest contracts; existing current golden corpus and deterministic scorer for baseline output.
- **Blocker behavior:** missing credentials/access -> `BLOCKED_ENVIRONMENT`; upstream contract conflict -> `BLOCKED_AUTHORITY`; implementation/test failures -> owning defect classification before repair.
