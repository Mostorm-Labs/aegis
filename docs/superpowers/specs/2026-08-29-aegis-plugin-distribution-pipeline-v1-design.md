# Aegis Installation Kit V1 — Design

Status: **Approved in chat on 2026-08-29; implementation authorized in this thread.**

Related work:

- `docs/plugin-distribution-contract-v0.1.md`
- `docs/superpowers/specs/2026-08-29-aegis-plugin-distribution-v0.1-design.md`
- `docs/superpowers/specs/2026-08-29-aegis-catalog-provenance-repair.md`

## 1. Product Goal

Aegis V1 must remove the repetitive packaging work required to install the exact nine-Skill catalog in ChatGPT.

The current supported ChatGPT Skill UI accepts one Skill ZIP at a time. Aegis therefore must not require the maintainer or tester to manually create nine ZIP archives for every release.

The V1 delivery path is:

```text
Aegis source
    ↓
CI validates one coherent release
    ↓
CI packages nine upload-ready Skill ZIPs
    ↓
one downloadable GitHub artifact
    ↓
user extracts once
    ↓
9 ready-to-upload Skill ZIPs
```

### V1 success criterion

For each Aegis release, CI automatically produces one installation-kit artifact containing the exact nine Aegis Skills as nine independently uploadable ZIP files. The maintainer performs **zero manual Skill compression operations**.

A future Plugin or bulk-install API may remove the remaining nine upload clicks, but neither is required for V1.

## 2. First-Class Principle: Minimize Human Work

Aegis exists to reduce coordination and verification burden.

Normative principle:

```text
credible evidence at the lowest human cost
```

For packaging this means:

```text
source folders
-> machine packaging
-> upload-ready artifacts
```

and never:

```text
source folders
-> human creates 9 ZIPs
-> human checks 9 layouts
```

## 3. Distribution Model

The Aegis release is the coherent identity boundary. Delivery mechanisms are adapters around that release.

```text
Aegis Release
├── exact 9 Skill identities + digests
└── Delivery adapters
    ├── Skill Installation Kit      # required V1 path
    ├── Plugin                      # optional/future platform path
    └── Bulk Install API            # optional/future platform path
```

`Product != Release != Delivery Adapter != Skill`.

No delivery adapter becomes a lifecycle Primary Owner.

## 4. Installation Kit Layout

CI must produce one directory that is uploaded as one GitHub Actions artifact:

```text
aegis-skills-<release>/
├── release.json
├── aegis.zip
├── aegis-project-state.zip
├── aegis-discovery.zip
├── aegis-modeling.zip
├── aegis-architecture.zip
├── aegis-verification.zip
├── aegis-governance.zip
├── aegis-implementation.zip
└── aegis-gate-review.zip
```

Downloading the GitHub artifact may wrap this directory in the platform artifact ZIP. The user experience is still one download and one extraction before the nine upload-ready Skill ZIPs are visible.

## 5. Individual Skill ZIP Contract

Each nested Skill ZIP is directly uploadable through the ChatGPT Skill upload UI.

The ZIP root must contain the Skill contents directly, for example:

```text
aegis-modeling.zip
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
├── scripts/        # when present
└── assets/         # when present
```

Forbidden layout:

```text
aegis-modeling.zip
└── aegis-modeling/
    └── SKILL.md
```

The packaging pipeline must not require a second repackaging operation by the user.

## 6. Determinism and Release Identity

All nine ZIPs must be deterministic for the same source tree and release inputs.

The release manifest must pin, per Skill:

```yaml
name: aegis-modeling
tree_sha256: <digest of source Skill tree>
zip_filename: aegis-modeling.zip
zip_sha256: <digest of deterministic upload ZIP>
```

The artifact is also bound to the exact GitHub workflow run / head SHA that produced it.

Skill public versioning does not split from the Aegis release. All nine ZIPs in one installation kit belong to one coherent release/component set.

## 7. Packaging Algorithm

For each Skill in `skillset/manifest.json` order:

1. read the generated `skills/<skill-id>/` tree;
2. validate required Skill structure;
3. create a deterministic ZIP whose archive root is the contents of that Skill directory;
4. compute `zip_sha256`;
5. record source-tree and ZIP digests in `release.json`;
6. place the ZIP in the installation-kit directory.

After all nine are written, the pipeline verifies:

- exactly nine expected ZIP filenames exist;
- every ZIP contains root-level `SKILL.md`;
- every ZIP contains `agents/openai.yaml`;
- no ZIP contains an extra enclosing `<skill-id>/` directory;
- ZIP digests match `release.json`;
- source-tree digests match the release manifest;
- repeated builds are byte-for-byte reproducible.

## 8. CI Contract

`Aegis Skillset Integrity` must build the installation kit after deterministic validation and upload it as a named artifact.

V1 artifact name:

```text
aegis-skill-installation-kit-<release>
```

The artifact path must contain `release.json` and all nine nested Skill ZIP files, not raw Skill folders that require manual recompression.

Existing source-bundle artifacts may remain for repository/evidence use, but they are not the user-facing installation deliverable.

## 9. Compatibility and Plugin Boundaries

Standalone central `aegis` may continue to exist as a compatibility distribution. It is not required to be manually reconstructed as part of the normal nine-Skill installation flow.

A future Plugin delivery adapter may package the same exact release into one Plugin installation. A future supported bulk-install API may install all nine Skill ZIPs from one action.

Neither future adapter changes:

- the nine Skill identities;
- ownership semantics;
- routing semantics;
- release digests;
- `terminal_trace_v0.2`.

V1 must not invent an undocumented Plugin upload format or bulk-install API.

## 10. Human Interaction Budget

### Maintainer / tester

```text
manual Skill compression operations per release = 0
manual Skill folder repackaging = 0
manual release consistency assembly = 0
```

### Current ChatGPT installation path

```text
1 artifact download
1 artifact extraction
9 Skill uploads
```

The remaining nine upload actions are a platform/UI limitation, not work that Aegis should amplify with manual packaging.

### Future target

When ChatGPT exposes a supported Plugin or bulk-install path usable for this distribution:

```text
1 install action
-> exact nine Skills
```

## 11. Failure Modes

### Missing Skill or invalid generated Skill structure

Packaging fails. No installation-kit artifact is published.

### ZIP layout is not directly uploadable

Packaging tests fail. No artifact is published.

### ZIP digest or source-tree digest mismatch

Release consistency fails. No artifact is published.

### Partial kit

A kit with fewer or more than the exact nine expected Skill ZIPs is invalid.

### Bulk install unavailable

This does not block V1. Users receive the nine upload-ready ZIPs and do not manually create archives.

## 12. Non-Goals

V1 does not require:

- a directly uploadable multi-Skill Plugin;
- an undocumented Plugin schema;
- an automated ChatGPT bulk-install API;
- changing any Skill's substantive instructions;
- changing lifecycle ownership;
- changing routing or compatibility oracle semantics;
- deleting existing source bundles used for evidence/debugging.

## 13. Acceptance Criteria

V1 is complete when:

1. one CI run produces one named installation-kit artifact;
2. that artifact contains `release.json` plus exactly nine nested Skill ZIPs;
3. each nested ZIP is directly uploadable without repackaging and has root-level `SKILL.md` and `agents/openai.yaml`;
4. all nine expected Skill IDs are present exactly once;
5. every Skill ZIP is deterministic;
6. every Skill ZIP has a `zip_sha256` recorded in `release.json`;
7. source `tree_sha256` and ZIP digest identity are machine-verifiable;
8. repeated builds are byte-for-byte reproducible;
9. existing deterministic routing/ownership/project-state regressions remain green;
10. no user or maintainer manually compresses the nine Skill directories for a release.
