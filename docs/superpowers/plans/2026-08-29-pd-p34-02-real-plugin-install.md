# PD-P34-02 Real Plugin Install Plan

Status: **Authorized execution plan — PD-P34-01 independently PASS; PD-P34-02 RED-first**

Gate: `gate-plugin-distribution-v01-pr13`
Case: `PD-P34-02 — One Plugin Install -> Exact Nine`

## Objective

Prove with one fresh ChatGPT platform event that importing the GitHub-backed Aegis marketplace and installing one Aegis Plugin materializes exactly the nine canonical Aegis Skills under `PLUGIN` provenance and one coherent `0.1.0-beta.2` candidate release.

## Fixed source under test

- Repository: `https://github.com/Mostorm-Labs/aegis`
- Marketplace path: repository root `.agents/plugins/marketplace.json`
- Fixed source commit: `a9efc0fe9221ffda7bf37d86fd3bec4385f7f1e2`
- Plugin: `aegis`
- Candidate release: `0.1.0-beta.2`
- Release manifest: `skillset/releases/aegis-0.1.0-beta.2.json`

A fixed commit is required for the acceptance event so that later branch movement cannot change the source being evaluated.

## RED-first evidence contract

Before performing the platform installation, add a repository test that requires:

- one machine-readable PD-P34-02 evidence file;
- `fresh_platform_event = true`;
- `complete_catalog_capture = true`;
- a non-empty real platform `plugin_id`;
- `plugin_name = aegis`;
- `distribution_provenance = PLUGIN`;
- marketplace source equal to this GitHub repository;
- `source_commit = a9efc0fe9221ffda7bf37d86fd3bec4385f7f1e2`;
- `release_version = 0.1.0-beta.2`;
- release manifest bound to the beta.2 candidate manifest;
- an installation-before snapshot showing no active Aegis Plugin distribution;
- an installation-after snapshot showing one Aegis Plugin distribution and the exact nine Skill IDs;
- `catalog_state = FULL_SPECIALIST`;
- `accepted_runtime = true`;
- `sync_result = not-run` for the initial installation case;
- `same_plugin_id = not-applicable` for the initial installation case;
- a reviewer-accessible durable `materialization_ref`.

The test must fail while the real platform evidence file is absent. Do not satisfy RED with synthetic/fabricated platform evidence.

## Human/platform action

Using a ChatGPT workspace administrator surface:

1. Open `Workspace settings -> Plugins -> Add -> Import marketplace`.
2. Source: `https://github.com/Mostorm-Labs/aegis`.
3. Path: leave empty (marketplace is at repository root).
4. Branch, tag, or commit: `a9efc0fe9221ffda7bf37d86fd3bec4385f7f1e2`.
5. Import the marketplace and review the import result.
6. Open Aegis and install/enable exactly one Plugin distribution for the test role/account.
7. Capture the complete Aegis-family installed catalog and Plugin identity after installation.

If the workspace lacks marketplace import/install capability, classify `BLOCKED_ENVIRONMENT`; do not replace the event with synthetic evidence.

## Evidence materialization

Materialize the observed event as:

`skillset/dogfood/evidence/pd-p34-02-plugin-install-chatgpt-web-20260829.json`

A screenshot or UI note may support the event, but the JSON record is the normative machine-readable capture. The durable PR comment or equivalent evidence reference must be recorded in `materialization_ref`.

## PASS threshold

PD-P34-02 PASS requires all of:

1. one fresh real ChatGPT Plugin installation event;
2. fixed GitHub source commit matches the PD-P34-01 reviewed materialization;
3. exactly one Aegis Plugin distribution observed;
4. exact-nine Aegis Skill IDs after installation;
5. no duplicate Aegis distribution;
6. `distribution_provenance = PLUGIN`;
7. `catalog_state = FULL_SPECIALIST`;
8. coherent `0.1.0-beta.2` release binding;
9. complete catalog capture and durable evidence materialization;
10. repository oracle GREEN on the materialized evidence.

## Non-goals

- Do not run PD-P34-03 behavioral parity yet.
- Do not run upgrade cases PD-P34-04/05 yet.
- Do not publish `v0.1.0-beta.2`.
- Do not merge PR #13.
- Do not mutate historical `v0.1.0-beta.1`.
