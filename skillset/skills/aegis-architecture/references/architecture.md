# Architecture Workflow

## P14 System Architecture
Assign subsystem ownership, dependencies, public boundaries, lifecycle, thread/process boundaries, failure domains, and explicit non-ownership.

## P15 Module Design
Refine subsystems into independently understandable modules with stable interfaces and invariants.

## P16 Runtime Data Flow
Trace happy/error/retry/recovery/cancel/backpressure/persistence flows in temporal order; every state transition names its owner.

## P17 Platform Contract
Separate common semantics from ABI/bridge/thread/input/surface/lifecycle/capability realization. Platform shortcuts must not silently redefine semantics.

## P18 Engineering / Optimization
Start from workload, metric, baseline, target, resource budget, observability, and rollback/reference path before algorithm choices.
