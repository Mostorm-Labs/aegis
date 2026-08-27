# Aegis Self-Hosting / Manual Dogfooding + Manifest Adoption Design

## Status

Approved architectural design for 08. The original design is preserved as historical authority for the self-hosting experiment; later reruns may update repository facts and project-state schema versions without rewriting this original design intent.

## Purpose

Use Aegis on itself as the first real project-state consumer. The design deliberately separates **manifest adoption** from **upstream contract repair**: exercise the accepted project-state contract, compare generated state with independently known GitHub/Notion reality, and if the contract cannot represent that reality, stop at classification and create regression input rather than silently modifying authority.

## Architecture

```text
Notion Current Authority + GitHub implementation/evidence
                         |
                         v
                    root .aegis/
        project / authority / gate / evidence
                         |
                         v
             tools.aegis_state validate
                         |
                         v
                    recompute
                         |
                         v
                  generated state
                         |
                         v
          Manual Dogfood Reality Oracle
                         |
                         v
                 Compare / classify
            /                         \
 representation OK               representation gap
       |                                |
     P34                           P35 -> upstream repair
```

The success condition is not an all-green project. It is faithful representation and routing of real authority, Gate, evidence, and repository facts.

## Canonical root manifests

The self-hosting repository uses root `.aegis/` project, authority, Gate, evidence, integration, and generated state manifests supported by the current accepted project-state schema.

Do not register every document as an authority node. Include only validity-bearing dependencies.

## Manual dogfood oracle

The oracle is source reconciliation, not a hand-edited state file. Known repository and Authority facts must be encoded truthfully, recomputed, and compared with generated state.

The experiment historically discovered:

- F08-01: blocked Gate verdict disappeared from derived state;
- F08-02: P34 PASS was not separable from repository integration;
- F08-03: durable historical integration could not survive later Authority supersession.

Each confirmed finding must route upstream and become permanent regression input rather than being special-cased inside the Aegis repository.

## Regression capture

Confirmed lifecycle/governance failures belong in `evals/cases/dogfood.json` without modifying protected seed IDs. The dogfood cases freeze correct Aegis classification/routing; executable state semantics remain owned by the 07 Project State Authority and its dedicated unit tests.

## CI behavior

Repository CI should separately prove generic project-state tooling health and repository-root self-host semantic fidelity:

```text
parse current project-state schemas
validate/check minimal example
run tests/project_state
validate repository root
check repository root
validate eval corpus
```

A generic tooling PASS cannot override a root semantic failure, and a real unrelated project blocker may remain present while self-host semantic fidelity itself passes.

## Non-goals

- No auto-merge behavior owned by Aegis.
- No API-key workaround.
- No new status vocabulary merely for dogfood.
- No hand-authored derived state.
- No repository-specific special case to make self-hosting pass.
- No claim that green generic CI alone proves project-control correctness.
