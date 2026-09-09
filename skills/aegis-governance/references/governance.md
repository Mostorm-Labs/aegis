# Governance Workflow

## P21 Authority Review
Classify sources, detect conflicting current documents, missing contracts, unresolved decisions, and stale downstream plans. Repository code does not win merely because it exists.

## P22 Five-Axis Drift Review
Check Product, Semantic, Architecture, Implementation, and Verification drift. Classify every finding and route repair to its owning layer. A P20 Verification omission or P31 Task Package omission discovered late must be owned by that earlier layer rather than relabeled implementation incomplete.

## P23 Authority Supersession
Preserve the old version, mark it Superseded, link the replacement, explain the reason, and update downstream dependency/version expectations. One Current Authority per scope.

## P24 Release Readiness
Review required Gate results plus migration/recovery/rollback/observability/platform/performance/security evidence as applicable to the selected profile. Missing evidence blocks release only when it is frozen as required or leaves a material high-impact failure mode without credible independent coverage. Do not import Full-assurance evidence rituals into Standard releases without explicit profile justification.
