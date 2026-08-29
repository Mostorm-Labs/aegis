# Modeling Workflow

## P10 Product Object Model
Classify entities, value objects, aggregates, sessions, external resources, transient state, and derived state. State identity/lifecycle explicitly.

## P11 Interaction / Behavior
Specify start, transient state, commit, cancellation, retry, and resulting canonical mutation/non-mutation.

## P12 Semantic Schema
Define canonical state, stable identity, field meaning, defaults, validation, versioning, compatibility, optionality, and extensibility. Keep UI/cache/transport/runtime-derived state out unless truly canonical.

## P13 Operation / Mutation Model
Define mutation vocabulary, payload, validation, atomicity, ordering, idempotency/dedup where relevant, undo/redo, replay, compatibility, and error behavior.
