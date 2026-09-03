# Aegis Control Plane Productization v0.2 — P20 Plugin-Profile P21-B1 Repair

Status: **Draft / Proposed Authority — local P20 repair after P21 BLOCKED_AUTHORITY**

Scope: `aegis/control-plane-productization/verification`

This document is a narrow normative amendment to:

- `docs/control-plane-productization-verification-v0.2-plugin-profile-repair.md`
- blocked exact head `fc71950af3337beaf73256c38eff1bf7c47c22a4`

It repairs only P21 finding `P20-PLUGIN-B1` from review `5097316364`.

The original Plugin-profile repair and this amendment are normative together for the repaired P20 candidate. Where this amendment is more specific about `CPV-R37`, `CPV-R38`, and `CPV-C18` applicability, this amendment controls.

---

## 1. Exact trusted basis

- Product boundary: `e6f79e92d60b1fea126db4efec321fd5ddc1ada7`
- Product P21: `5097117641` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- P23 applicability supersession: `b5677ad112a7a2067754b209ccde7fc97ef7469d`
- P23 review: `5097214759` — `PASS / AUTHORITY_SUPERSESSION_COMPLETE`
- historical accepted P20: `db83168e4086e47a7f431acf289006e4f25b8ffd`
- historical P20 review: `5062933855` — `PASS / ACCEPTED_FOR_DOWNSTREAM`
- blocked Plugin-profile P20 candidate: `fc71950af3337beaf73256c38eff1bf7c47c22a4`
- blocking P21 review: `5097316364`
- finding: `P20-PLUGIN-B1`
- classification: `SPEC_DEFECT`

No earlier Product, Modeling, Architecture, or Governance basis is reopened by this repair.

---

## 2. Defect statement

The blocked P20 candidate correctly declared the retained Plugin-profile Requirement set as including:

```text
CPV-R27 ... CPV-R38
```

Therefore both of the following remain release-applicable for `PLUGIN_PROFILE` in their deterministic/policy-conformance meaning:

```text
CPV-R37 Operational Retention
CPV-R38 Alerting
```

Historical P20 maps them to:

```text
CPV-C18 Operational Retention / Alerting
```

However, the blocked candidate's §6.1 release-blocking Claim list omitted `CPV-C18`, while the following applicability clarification still said C18 deterministic retention/alert policy conformance was retained.

That left an ambiguous chain:

```text
R37/R38 = release-blocking
  -> C18 = textually retained
  -> C18 = omitted from mandatory Claim list
```

Under `CoverageBasis = REVIEW_DECLARED`, P34 may not infer the missing Claim applicability. The Requirement -> Claim -> Gate chain must be explicit.

---

## 3. Normative repair

### 3.1 `CPV-C18` is release-blocking for deterministic Plugin-profile conformance

For v0.2 `PLUGIN_PROFILE`, add the following Claim to the release-blocking Claim set:

```text
CPV-C18 Operational Retention / Alerting
```

Its required Plugin-profile scope is:

- deterministic/virtual-time retention-policy conformance for operational and telemetry state that the candidate implements or claims;
- proof that canonical StageOccurrence/package/Escalation/semantic-idempotency history is not deleted or rewritten by operational retention policy;
- deterministic alert-rule qualification for accepted critical/urgent/warning thresholds where those rules are implemented;
- proof that alerts/retention timers remain operational state and never become lifecycle semantic truth;
- exact evidence that expiry/alert transitions cannot authorize canonical mutation, Gate PASS, semantic retry, or historical rewrite.

`CPV-C18` remains:

```text
Criticality: ORDINARY
Minimum assurance: CHALLENGED
Base profile: PROPERTY
Execution context: PLATFORM / deterministic policy conformance
```

### 3.2 Continuous production-service attainment remains conditional

This repair does **not** reintroduce a service-scale claim.

The following remain `SERVICE_PROFILE_CONDITIONAL`:

- continuously observed production retention-window attainment;
- continuously observed production alert-firing/operational SLO attainment;
- dedicated service telemetry capacity or alert throughput;
- any retention/alert objective whose only justification is the superseded mandatory production Control Service profile.

Therefore:

```text
C18 deterministic policy correctness = PLUGIN_PROFILE release-blocking
C18 continuous production service attainment = SERVICE_PROFILE_CONDITIONAL
```

### 3.3 Exact Requirement -> Claim mapping

For the repaired candidate:

```text
CPV-R37 -> CPV-C18 -> P34
CPV-R38 -> CPV-C18 -> P34
```

There is no remaining unclaimed release-blocking Requirement in this pair.

---

## 4. Effect on existing corpus and oracles

No new corpus, oracle, workload, mutant, or performance profile is introduced.

The existing retained evidence remains the proof vehicle:

- `G44` remains the deterministic/virtual-time retention and alert-threshold boundary scenario;
- `O-TIMEPOLICY` remains the independent timing/policy oracle;
- `O-STORE` remains responsible for proving canonical history is unaffected by operational expiry;
- `O-AUTH` remains the exact Authority/reference oracle;
- `O-COMPLETE` must include `CPV-C18` in the expected Plugin-profile Claim set and detect omission/duplication/extra claims;
- semantic zero-tolerance metrics remain unchanged.

No R0, S0, W7D, real-wall-clock stress, service RPS, latency percentile, or completed-month observation is required to satisfy this repaired Plugin-profile C18 contract.

---

## 5. Repaired Plugin-profile Claim set

The release-blocking Claim set from the blocked P20 candidate is retained with exactly one correction: `CPV-C18` is explicitly included.

```text
CPV-C01 Canonical Safety
CPV-C02 Dispatch / Idempotency Safety
CPV-C03 Historical Child / External Truth
CPV-C04 Ownership / Gate / Rollout Integrity
CPV-C05 Resume / Sessionless Control
CPV-C06 Human Decision Integrity
CPV-C07 API / Capability / Credential Boundary
CPV-C08 Derived / Operational State Separation
CPV-C09 Degraded Recovery / Durability
CPV-C10 D0 Semantic Conformance
CPV-C13 Retention / Replay / Audit
CPV-C14 Observability / Cost Attribution
CPV-C15 Snapshot / Async Provider Trust
CPV-C16 Delivery / Reconciliation Control
CPV-C17 Exact Envelope Representation
CPV-C18 Operational Retention / Alerting
CPV-C20 Plugin-Profile Repeated Integration Stability
CPV-C21 Plugin Product-Form Corroboration
```

Conditional service Claims remain unchanged:

```text
CPV-C11 R0 Engineering Budget          -> SERVICE_PROFILE_CONDITIONAL
CPV-C12 S0 Stress / Backpressure       -> SERVICE_PROFILE_CONDITIONAL for real-wall-clock service load
CPV-C19 Long-window Cost / Availability -> SERVICE_PROFILE_CONDITIONAL
```

---

## 6. P34 coverage consequence

For `PLUGIN_PROFILE`, P34 independent coverage completeness must now explicitly verify:

1. `CPV-R37` is covered by `CPV-C18`;
2. `CPV-R38` is covered by `CPV-C18`;
3. G44 / O-TIMEPOLICY / O-STORE evidence supports the deterministic/policy-conformance scope;
4. canonical history is unaffected by operational retention expiry;
5. alert/retention operational state cannot authorize semantic mutation or Gate truth;
6. no continuous production-service retention/alert attainment is inferred unless `SERVICE_PROFILE` is separately claimed.

Missing `CPV-C18` from the evaluated Plugin-profile Claim set is `BLOCKED_EVIDENCE` / coverage failure, not a cosmetic omission.

---

## 7. No other P20 change

This local repair does not alter:

- PP0's exact 40-WorkScope workload;
- PP0 zero-tolerance metrics;
- G01-G44 mandatory status;
- M01-M20 mandatory status;
- `CPV-R41` / `CPV-C20`;
- `CPV-R42` / `CPV-C21`;
- `CoverageBasis = REVIEW_DECLARED`;
- independent oracle boundaries;
- exact evidence inheritance rules for CP-I01..CP-I08;
- fresh installed Plugin/nine-Skill corroboration;
- P34 sole-Gate ownership;
- old CP-I09 `HISTORICAL_ONLY` status;
- historical R0/S0/W7D results;
- current cross-Primary rollout `DENIED`;
- `SERVICE_PROFILE_CONDITIONAL` status of R25/C11, R26/C12, R39/C19, or R40/C19.

No replacement CP-I09 P31 package is created or authorized by this repair.

---

## 8. Local repair acceptance criteria

This repair is complete only if fresh P21 rereview confirms:

1. `R37 -> C18 -> P34` is explicit and unambiguous;
2. `R38 -> C18 -> P34` is explicit and unambiguous;
3. C18 deterministic/policy correctness remains Plugin-profile release-blocking;
4. continuous production-service retention/alert attainment remains service-profile conditional;
5. no other P20 Claim/Requirement applicability is changed;
6. PP0 and all existing zero-tolerance proof remain unchanged;
7. old CP-I09 evidence remains historical and unmodified;
8. no implementation package, P34, merge, release, or rollout is implied.

---

## 9. P20 local repair disposition

```yaml
P20_local_repair:
  finding: P20-PLUGIN-B1
  prior_blocked_head: fc71950af3337beaf73256c38eff1bf7c47c22a4
  prior_p21_review: 5097316364
  defect_class: SPEC_DEFECT

  repaired_mapping:
    CPV_R37: CPV_C18
    CPV_R38: CPV_C18
    CPV_C18_plugin_profile: RELEASE_BLOCKING_DETERMINISTIC_POLICY_CONFORMANCE
    CPV_C18_service_attainment: SERVICE_PROFILE_CONDITIONAL

  PP0_changed: false
  G01_G44_changed: false
  M01_M20_changed: false
  service_claims_changed: false
  old_CP_I09_changed: false
  current_cross_primary_rollout: DENIED

  status: READY_FOR_P21_REREVIEW
```

Stop after this P20 repair materialization. Do not execute P21 rereview, create a replacement CP-I09 package, resume PR #44 P36, run P34, merge, release, or expand rollout automatically.
