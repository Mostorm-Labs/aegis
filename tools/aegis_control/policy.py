"""Fail-closed Control Autonomy and Current rollout policy for CP-I03."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .canonical import canonical_digest


@dataclass(frozen=True)
class PolicyDecision:
    mode: str
    reason_codes: tuple[str, ...]
    auto_schedule_authorized: bool
    policy_digest: str
    source_primary_owner: str
    target_primary_owner: str
    gate_decision: bool = False


class PolicyEvaluator:
    """Derive transient policy decisions; never author Gate or Authority truth."""

    def evaluate_next_action(
        self,
        *,
        next_legal_action: str,
        source_primary_owner: str,
        target_primary_owner: str,
        control_autonomy: str,
        policy_basis: Mapping[str, Any] | None,
    ) -> PolicyDecision:
        basis = dict(policy_basis or {})
        digest = canonical_digest(
            {
                "next_legal_action": next_legal_action,
                "source_primary_owner": source_primary_owner,
                "target_primary_owner": target_primary_owner,
                "control_autonomy": control_autonomy,
                "policy_basis": basis,
                "policy_version": "cp-i03-current-rollout-v0.1",
            }
        )

        if not isinstance(policy_basis, Mapping) or policy_basis.get("current") is not True:
            return self._decision(
                "PROHIBITED",
                ("MISSING_OR_STALE_POLICY_BASIS",),
                False,
                digest,
                source_primary_owner,
                target_primary_owner,
            )
        if next_legal_action not in {"SCHEDULE_INITIAL", "SCHEDULE_SUCCESSOR"}:
            return self._decision(
                "PROHIBITED",
                ("NO_AUTONOMOUS_SCHEDULABLE_ACTION",),
                False,
                digest,
                source_primary_owner,
                target_primary_owner,
            )
        if control_autonomy == "HUMAN_DECISION":
            return self._decision(
                "HUMAN_DECISION",
                ("HUMAN_DECISION_REQUIRED",),
                False,
                digest,
                source_primary_owner,
                target_primary_owner,
            )
        if control_autonomy == "REVIEW_GUARDED":
            return self._decision(
                "REVIEW_GUARDED",
                ("REVIEW_GUARD_REQUIRED",),
                False,
                digest,
                source_primary_owner,
                target_primary_owner,
            )
        if control_autonomy != "AUTONOMOUS":
            return self._decision(
                "PROHIBITED",
                ("UNKNOWN_CONTROL_AUTONOMY",),
                False,
                digest,
                source_primary_owner,
                target_primary_owner,
            )
        if source_primary_owner != target_primary_owner:
            return self._decision(
                "PROHIBITED",
                ("CURRENT_CROSS_PRIMARY_ROLLOUT_DENIED",),
                False,
                digest,
                source_primary_owner,
                target_primary_owner,
            )
        if policy_basis.get("rollout_authorized") is not True:
            return self._decision(
                "PROHIBITED",
                ("CURRENT_ROLLOUT_DENIED",),
                False,
                digest,
                source_primary_owner,
                target_primary_owner,
            )
        return self._decision(
            "AUTONOMOUS",
            (),
            True,
            digest,
            source_primary_owner,
            target_primary_owner,
        )

    @staticmethod
    def _decision(
        mode: str,
        reasons: tuple[str, ...],
        authorized: bool,
        digest: str,
        source_primary_owner: str,
        target_primary_owner: str,
    ) -> PolicyDecision:
        return PolicyDecision(
            mode=mode,
            reason_codes=reasons,
            auto_schedule_authorized=authorized,
            policy_digest=digest,
            source_primary_owner=source_primary_owner,
            target_primary_owner=target_primary_owner,
            gate_decision=False,
        )
