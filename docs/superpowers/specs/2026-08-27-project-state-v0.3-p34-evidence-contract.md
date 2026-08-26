# Project State v0.3 P34 Evidence Contract

This file freezes the evidence set used by P34. It does not alter the approved design.

P34 may accept v0.3 only when all are true:

1. focused v0.3 history regressions pass;
2. complete project-state regression passes;
3. six v0.3 schemas parse and minimal v0.3 manifests return `VALID / STATE_OK`;
4. complete Aegis Skill validates and packages successfully;
5. R03-09 real self-host returns `STATE_OK` with PR #4 historical, PR #7 current, PR #6 closed history, and the OpenAI real baseline as the primary `verification / P34` blocker;
6. production code contains no PR #4/Aegis-specific repair;
7. fresh GitHub CI passes on the final PR head.

Only then may P23 supersede v0.2 with v0.3.
