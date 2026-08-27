# Project State v0.3 Implementation Clarifications

Status: **Normative clarification to the approved Proposed v0.3 design; no scope expansion.**

This note records two ambiguities exposed by RED-first implementation. It does not change the approved architectural split:

```text
Historical Occurrence
!=
Current Applicability
!=
Current Actionability
```

## C03-01 — Historical Gate requires completed-history provenance

The phrase “all Gate Authorities are Superseded/Historical” is not sufficient by itself to make a Gate non-actionable history.

A Gate is automatically classified as `historical` only when both are true:

1. all validity-bearing Gate `authority_ids` are `Superseded/Historical`; and
2. the Gate is retained as provenance for a completed Integration whose status is `integrated` or `closed_unmerged`.

Without completed-history provenance, a current-declared PASS Gate that points at non-current Authority remains invalid/stale under the pre-existing fail-closed rules. This preserves the legacy safety invariant that an arbitrary PASS Gate cannot escape review merely because its Authority became historical.

## C03-02 — `closed_unmerged` is completed Integration history

`closed_unmerged` means the repository candidate did not enter the target baseline and no current integration action remains.

Therefore:

```text
closed_unmerged
→ Integration occurrence is complete
→ integration applicability = historical
→ not in awaiting_integrations
→ no finishing-development-branch handoff
```

This is true even if the supporting Gate Authority remains Current.

Gate actionability is still independent. A Current Gate may remain actionable for other reasons even when one candidate Integration has been closed unmerged.

## Verification additions

The focused v0.3 regression suite must include:

- all-historical Gate with no completed Integration does **not** bypass current/non-current Authority validation;
- `closed_unmerged` under a Current PASS Gate projects as Integration applicability `historical` and never becomes awaiting work;
- a Current Gate with stale evidence continues to route `verification / P34` even if a related Integration is `closed_unmerged`.

These clarifications were captured before P34 and are part of the v0.3 acceptance contract.
