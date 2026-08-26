# Aegis OpenAI Hosted Skill Provider Driver + Behavioral Baseline Run v0.1

Status: Proposed Baseline Execution Authority

## 1. Route

Upstream Current Authority:

- `docs/evaluation-and-dogfooding-v0.1.md`
- `docs/model-execution-and-scoring-v0.1.md`
- `skills/aegis/SKILL.md`

Earliest Untrusted Layer: **Provider Execution / Behavioral Evidence**.

Route:

`P20 baseline evidence contract delta -> P30/P31 provider package -> P32 TDD implementation -> real full-corpus execution -> P34 baseline gate`

## 2. Objective

Create the first reproducible real-provider execution path for Aegis:

`Aegis git SHA -> deterministic skill bundle -> OpenAI Skills API -> pinned skill_id/version -> Responses API hosted shell -> GPT-5.6 Sol -> current golden corpus -> raw provider evidence -> existing normalizer/scorer -> baseline manifest/report`

This authority does not alter golden expected behavior, evaluation thresholds, defect taxonomy, or gate vocabulary.

## 3. Baseline Identity

The v0.1 baseline identity is:

- provider: `openai`
- endpoint: `/v1/responses`
- model: `gpt-5.6-sol`
- reasoning effort: `medium`
- skill transport: uploaded Agent Skill referenced by `skill_id` and immutable `version`
- shell environment: hosted `container_auto`

The provider configuration is baseline metadata, not Aegis semantic authority.

## 4. Skill Bundle Contract

Build `skills/aegis/` into a deterministic zip containing exactly one top-level directory named `aegis/`.

Record:

- `source_git_sha`
- `skill_bundle_sha256`
- `skill_id`
- `skill_version`

A baseline must pin both `skill_id` and `skill_version`. A moving default-version pointer is insufficient evidence.

## 5. Golden Leakage Rule

The existing `CommandAdapter` may pass the complete case object to a provider driver. The provider driver must project that case before any model request.

Allowed provider-visible case:

```json
{
  "case_id": "routing-001",
  "prompt": "...",
  "context": ["..."]
}
```

Forbidden provider-visible fields include:

- `expected`
- `severity`
- `origin`
- `category`
- `title`
- `tags`
- thresholds, scores, correct routes, or other answer-bearing metadata

Any golden leakage is a Critical Evaluation Defect and invalidates the baseline.

## 6. Prompt and Structured Result

Each request must explicitly instruct the model to use the mounted `aegis` skill and make the lifecycle decision only from the sanitized scenario.

The OpenAI provider layer uses a strict JSON Schema projection of the existing normalized result contract. Canonical repository semantics remain owned by `evals/schema/result.schema.json` and the current Evaluation Authority.

## 7. Provider Evidence

For every case preserve provider execution evidence containing at least:

- response ID
- provider/model
- response status
- created timestamp when present
- full provider response JSON
- output text / structured result
- token usage when present
- latency in milliseconds
- retry count

The existing evaluation runner continues to produce `raw/`, `normalized/`, `case-scores.json`, `summary.json`, and `report.md`.

## 8. Baseline Manifest

The baseline manifest must include at least:

- provider / endpoint / model / reasoning effort
- Aegis source git SHA
- runner git SHA
- skill ID / skill version / skill bundle SHA-256
- corpus digest / case count
- prompt template version
- run timestamp
- response IDs
- aggregate usage
- latency statistics
- retry count
- deterministic gate result
- semantic behavioral gate status

Missing identity fields block reproducibility claims.

## 9. Error Semantics

- Missing `OPENAI_API_KEY`, HTTP 401, or HTTP 403 -> `BLOCKED_ENVIRONMENT`.
- HTTP 429 or transient 5xx -> bounded retry; exhausted retries -> execution failure with raw error evidence.
- Refusal, incomplete response, missing structured output, or invalid JSON -> preserve evidence and fail the case. Do not guess.
- Do not weaken the result contract or golden expectations to obtain a baseline.

## 10. Exit Criteria

Tooling scope requires:

- provider driver tests PASS
- deterministic bundle/pinning tests PASS
- golden leakage tests PASS
- provider payload contract tests PASS
- manifest contract tests PASS
- repository CI PASS

Real baseline scope additionally requires:

- one real provider execution for every current case
- provider evidence for every case
- normalized result for every case
- deterministic score and critical-safety result computed
- baseline manifest and report present

If provider credentials are unavailable, tooling may pass independently while the real baseline verdict remains `BLOCKED_ENVIRONMENT`.

## 11. Semantic Boundary

A deterministic provider baseline does not close semantic `required_findings` / `forbidden_findings` evidence. Full Semantic Behavioral Gate remains a later closure.
