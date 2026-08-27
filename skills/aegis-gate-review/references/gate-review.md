# Gate Review Workflow

## P34
Review Authority/contract conformance, scope drift, required tests, required oracles, performance/resource evidence, platform evidence, and downstream safety. Return PASS, PASS_WITH_FINDINGS, or a precise blocker.

## P35
Use the shared defect taxonomy. Identify owning layer, affected Authority/task/Gate, and downstream invalidation.

## P36
Fix the owning layer; rerun original failing evidence and relevant regressions. If upstream Authority changed, update supersession and downstream execution packages before reuse.
