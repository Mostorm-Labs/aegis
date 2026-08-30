# Task 6 Case 3 — Router Re-entry Finding

Status: **P34 finding / P35 classification candidate**

Observed protected case:

`09-01-upstream-blocker-reroute`

Prompt:

`Design module architecture, but project authority is unresolved.`

Fresh ChatGPT web observation on 2026-08-29:

- `aegis-architecture` was visibly invoked;
- Architecture correctly refused substantive P15 design;
- it conclusively established an earlier Authority blocker;
- it emitted an `ownership_handoff` from `aegis-architecture` to central `aegis`;
- it emitted no downstream architecture result;
- no central `aegis` invocation was visibly observed before the terminal user-facing response.

Raw observation:

`skillset/dogfood/evidence/task6-09-01-upstream-blocker-reroute-chatgpt-web-20260829-observation.json`

## Authority comparison

Skill Decomposition v0.2 permits an earlier-blocker path of:

`Primary -> detects earlier blocker -> aegis -> stop`

and defines blocked short-circuit / routing-only terminal ownership as central `aegis`.

The protected blocker corpus also pins `short_circuit.terminal_owner = aegis`.

The current Architecture Skill tells the specialist to emit an `ownership_handoff` to `aegis` and stop substantive execution, but does not make explicit that the terminal user-facing blocked/routing answer must occur only after central-router re-entry.

## Root-cause hypothesis

The deterministic Skill implementation under-specifies the **handoff completion boundary**. It specifies handoff emission but not same-turn router acceptance / terminal ownership. The observed model therefore treats the handoff metadata itself as terminal output.

This is narrower than an Authority defect: the v0.2 Authority, protected blocker case, and central Router role already agree that the blocked short-circuit terminal owner is `aegis`.

## P35 candidate classification

Primary: `IMPLEMENTATION_DEFECT`

Secondary: `TEST_DEFECT`

Why `TEST_DEFECT` is secondary: the current terminal-trace oracle only recognizes a short-circuit when the final owner is already `aegis`; if an earlier blocker is conclusively established but the turn terminates under the requested specialist, the oracle does not explicitly enforce the protected `terminal_owner` and may fail to surface `WRONG_FINAL_ANSWER_OWNER`.

## Repair boundary

Do not change Skill Decomposition v0.2, the protected Case 3 prompt, requested owner, or blocked-short-circuit ownership semantics.

A bounded repair should:

1. add a negative oracle regression proving that an established earlier blocker with a non-router terminal owner is rejected;
2. make the specialist handoff completion rule executable/explicit: after an earlier-blocker `ownership_handoff`, the terminal blocked/routing answer belongs to central `aegis` in Multi-Skill Mode;
3. regenerate only affected Skill distributions;
4. rerun deterministic regressions;
5. rerun protected Case 3 on the installed platform.

Until that rerun passes, Case 3 is **not accepted as PASS**.
