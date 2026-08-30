# Discovery and Design Execution

## P00 Problem Discovery

Separate symptom, pain, root constraint, and candidate solution. A solution proposal is not the problem statement. Ask whether the problem would still exist if the proposed solution were replaced.

Produce: observed reality, affected user/system scenario, impact, evidence, root constraint, success criteria, non-goals, unknowns. Do not choose architecture or technology here.

## P01 Product Research

Use research to challenge the P00 problem, not merely confirm it. Separate source-derived fact, user observation, inference, and assumption. Identify current alternatives and why they are insufficient for the target scenario.

## P02 Product Requirement

Translate the validated problem into JTBD/scenarios, functional and non-functional requirements, priorities, acceptance criteria, and explicit out-of-scope. Reject requirements that cannot trace back to value, constraint, or required platform/compliance behavior.

## P03 Capability Traceability

Build a trace from requirement to implementation responsibility and verification. The exact middle columns may vary by project, but keep both upstream value and downstream proof visible.

Typical chain:

`Requirement -> Capability -> Object -> Behavior -> Operation -> Module -> Platform -> Verification`

## P10 Product Object Model

Model the durable product world before database tables or implementation classes. Classify entities, value objects, aggregates, sessions, external resources, transient state, and derived state. State identity and lifecycle rules.

## P11 Interaction / Behavior

Model interactions as stateful sessions or transitions where useful. Specify start, intermediate/transient state, commit, cancellation, retries, and resulting canonical mutation/non-mutation. Keep interaction state separate from durable semantic truth.

## P12 Semantic Schema

Define only canonical semantic state unless the domain explicitly requires otherwise. Specify stable identity, field meaning, defaults, validation, versioning, compatibility, optionality, and extensibility. Keep caches, UI state, transport retries, render state, and platform details out unless they are truly canonical product semantics.

## P13 Operation / Mutation Model

Define how canonical state changes. Specify operation vocabulary, payload, validation, atomicity, ordering, idempotency/deduplication when relevant, undo/redo semantics, replay, compatibility, and error behavior. Avoid generic patch mechanisms when domain mutations carry important meaning.

## P14 System Architecture

Assign ownership. For each subsystem identify owned state, public contract, dependencies, lifecycle, thread/process boundaries, failure domain, and explicit non-ownership. Dependency direction should follow authority and data ownership, not convenience.

## P15 Module Design

Refine a subsystem into independently understandable modules. Freeze stable interfaces and invariants before implementation. Avoid speculative abstractions not justified by current capability or evidence needs.

## P16 Runtime Data Flow

Trace important end-to-end flows in temporal order. Include happy path, error path, retry/recovery, cancellation, backpressure, persistence/sync, and restart where relevant. Every state transition must name its owner and evidence of completion if asynchronous.

## P17 Platform Contract

Separate common semantics from physical realization. Define ABI/bridge, thread affinity, lifecycle, input/surface/resource ownership, platform capabilities, error mapping, and parity expectations where applicable. A platform shortcut must not silently change common semantic truth.

## P18 Engineering / Optimization

Start from a cost model and measurable bottleneck. Define workload, metric, baseline/reference, target/threshold, resource budget, observability, and rollback/reference path. Do not freeze algorithmic choices purely from historical discussion or intuition when benchmark evidence can decide.
