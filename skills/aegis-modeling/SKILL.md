---
name: aegis-modeling
description: Define Aegis product and semantic models across product objects, interaction behavior, canonical semantic schema, and operation/mutation contracts. Use when the user asks what objects exist, how interactions commit/cancel, what canonical state means, how IDs/fields/versioning work, or how operations mutate state with atomicity, ordering, replay, and compatibility.
---

# Aegis Modeling

Own `P10` Product Object Model, `P11` Interaction / Behavior, `P12` Semantic Schema, and `P13` Operation / Mutation Model.

## Modeling sequence

Model durable product truth before implementation classes; separate interaction session/transient state from canonical truth; define schema identity/meaning/defaults/validation/versioning; then define explicit domain mutations, atomicity, ordering, replay, compatibility, and error behavior.

**Earlier untrusted layer:** if product requirements or capability traceability are not trustworthy enough to model, stop and hand back to `aegis`; do not turn an assumption into canonical semantics.

Read [references/modeling.md](references/modeling.md) and shared Authority/stage contracts.
