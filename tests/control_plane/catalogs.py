"""Stable CP-I01 fixture and mutant catalogs bound to accepted P20 sources."""

from __future__ import annotations

from tools.aegis_control.canonical import canonical_digest


_BASE = "docs/control-plane-productization-verification-v0.2.md@db83168e4086e47a7f431acf289006e4f25b8ffd"
_REPAIR = "docs/control-plane-productization-verification-v0.2-p21-repair.md@db83168e4086e47a7f431acf289006e4f25b8ffd"

_G = [
    ("clean one-lane schedule -> execute -> terminalize -> separately continue", "CRM/SUT exact semantic equivalence"),
    ("two schedulers race same lane", "exactly one canonical winner; loser creates no occurrence/outbox"),
    ("unrelated lanes mutate concurrently", "no semantic cross-lane serialization/conflict"),
    ("duplicate outbox delivery", "same occurrence; no semantic retry"),
    ("crash after OPEN+outbox commit before first dispatch", "restart dispatches same committed occurrence"),
    ("callback lost after provider completion", "polling/query reconciles same occurrence"),
    ("callback duplicate/reordered", "callback payload never directly mutates canonical truth"),
    ("late conflicting terminal result", "terminal history immutable; conflict rejected"),
    ("REQUIRED child incomplete", "parent successor blocked"),
    ("REQUIRED child accepted", "successor includes exact RequiredChildAcceptanceBinding"),
    ("multiple REQUIRED children", "all must bind before successor"),
    ("NON_BLOCKING child still open", "parent may continue if all other rules permit"),
    ("stale SourceSnapshot/current Authority changes before commit", "mutation fails/recomputes; no stale-success"),
    ("external truth changes after historical commit", "historical basis unchanged; current actionability recomputed"),
    ("worker crash/timeout", "same occurrence reconciled; no replacement occurrence by age alone"),
    ("provider outage/rate limit", "only dependent work degrades; independent lanes may continue"),
    ("EXACT_CURSOR", "resume from accepted cursor"),
    ("DESCENDANT_CURSOR", "preserve valid descendant work; no replay"),
    ("ANCHOR_DESCENDANT_WITHOUT_CURSOR", "reconcile and establish cursor; no reset"),
    ("DIVERGED", "fail closed; no force-reset/discard"),
    ("platform technically callable, Current rollout denies cross-Primary automation", "no autonomous new occurrence/outbox; NextLegalAction exposed"),
    ("explicit test-policy fixture authorizes separate-occurrence cross-owner continuation", "capability works without ownership transfer; fixture is not Current Authority"),
    ("human escalation resolved by durable external decision ref", "resolving occurrence consumes exact decision ref"),
    ("raw chat acknowledgement with no governed decision materialization", "semantic approval rejected"),
    ("pause then unpause", "no history rewrite; admission resumes only after fresh recompute"),
    ("cache loss/corruption", "rebuild from canonical truth; same projection"),
    ("canonical store unavailable", "no new mutation/dispatch admission; conversation memory not used as store"),
    ("active controlled WorkScope while service unavailable", "no silent independent manual duplicate execution"),
    ("identical operation request replay", "exact prior result returned; no duplicate mutation"),
    ("same operation_request_id with conflicting fingerprint/body", "fail closed"),
    ("unsupported semantic/platform version", "fail closed; no reinterpretation"),
    ("webhook signature invalid/unverifiable", "rejected before semantic reconciliation"),
    ("immutable exact ref remains old while current Authority changes", "immutability not confused with current actionability"),
    ("remote provider call attempted while canonical tx open", "instrumentation/test fails immediately"),
    ("Escalation terminalization companion transaction", "atomicity matches accepted model; no half state"),
    ("modify one byte/field in valid SourceSnapshotToken payload without new integrity tag", "O-SNAPSHOT rejects; no trust-sensitive mutation"),
    ("valid token issued for another adapter/source kind", "adapter/source compatibility rejects; no canonical success"),
    ("valid token for wrong provider resource/version/currentness binding", "exact binding/currentness rejects or re-resolves; no stale/cross-resource success"),
    ("callback-only provider claims autonomous capability without durable query/correlation", "autonomous trust-sensitive capability rejected/degraded"),
    ("repeated delivery failure across virtual time", "retry policy preserves one semantic occurrence"),
    ("lost callbacks for OPEN occurrence across all age bands", "reconciliation queries follow policy; age alone never creates semantic retry"),
    ("provider 429/rate-limit responses above/below governed threshold", "concurrency adapts without weakening proof/review"),
    ("canonical records/envelopes around size targets with silent truncation attempt", "full canonical digest never uses truncated bytes"),
    ("virtual-time operational-retention and alert-threshold boundary sweep", "retention/alerts match governed thresholds without semantic mutation"),
]

GOLDEN_SCENARIOS = {f"G{i:02d}": {"description": description, "expected": expected, "source": _BASE if i <= 35 else _REPAIR} for i, (description, expected) in enumerate(_G, start=1)}

_MUTANTS = [
    "dispatch before OPEN/outbox commit",
    "retry creates a second StageOccurrence",
    "second canonical writer bypasses control-mutation",
    "stale snapshot accepted after provider version change",
    "REQUIRED child barrier crossed without acceptance binding",
    "historical acceptance inferred from current boolean projection",
    "terminalization and successor collapsed into one cross-owner transition",
    "worker restart creates semantic retry",
    "P34/Gate PASS inferred from CI/ProofEvaluation",
    "Execution Cursor treated as Authority/scope truth",
    "unauthorized cross-Primary auto-dispatch despite rollout denial",
    "projection cache authorizes mutation after canonical change",
    "outbox loss after acknowledged schedule commit",
    "unsafe manual fallback duplicates active controlled work",
    "late conflicting terminal result rewrites history",
    "SourceSnapshotToken payload modified while original integrity tag is accepted",
    "SourceSnapshotToken from wrong adapter/source-kind accepted at another trust boundary",
    "SourceSnapshotToken with mismatched provider resource/version binding accepted as current",
    "callback-only async provider accepted as full autonomous trust-sensitive capability",
    "canonical representation silently truncated before digest/acceptance",
]

MANDATORY_MUTANTS = {f"M{i:02d}": {"description": description, "source": _BASE if i <= 15 else _REPAIR} for i, description in enumerate(_MUTANTS, start=1)}


def fixture_catalog_digest() -> str:
    return canonical_digest(GOLDEN_SCENARIOS)


def mutant_catalog_digest() -> str:
    return canonical_digest(MANDATORY_MUTANTS)
