"""Semantic fail-closed validators for CodexStation ΩG machine contracts.

These validators implement the finite ΩG policy surface only. They are
implementation evidence, not a proof of the open T-ΩG theorem targets.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

AVAILABLE_STATES = {
    "AVAILABLE_READ",
    "AVAILABLE_WRITE",
    "AVAILABLE_EXECUTE",
    "AVAILABLE_BUT_APPROVAL_REQUIRED",
}
EPISTEMIC_DELTAS = {"FORMAL", "EMPIRICAL", "PROVENANCE", "SCOPE", "CANONICAL"}

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def _receipt(check: str, decision: str, reasons: Iterable[str], subject: Any) -> dict[str, Any]:
    reasons = tuple(sorted(set(reasons)))
    core = {
        "schema": "GILC/CODEXSTATION/OMEGA-G/SEMANTIC-VALIDATOR/0.1",
        "check": check,
        "decision": decision,
        "reasons": list(reasons),
        "subject_digest": digest(subject),
    }
    return {**core, "receipt_digest": digest(core)}

def validate_noncollapse(
    left_type: str,
    right_type: str,
    rules: Iterable[Mapping[str, Any]],
    witness_type: str | None = None,
) -> dict[str, Any]:
    for rule in rules:
        direct = rule["left_type"] == left_type and rule["right_type"] == right_type
        reverse = bool(rule.get("symmetry")) and rule["left_type"] == right_type and rule["right_type"] == left_type
        if not (direct or reverse):
            continue
        disposition = rule["disposition"]
        subject = {"left_type": left_type, "right_type": right_type, "rule_id": rule["rule_id"], "witness_type": witness_type}
        if disposition == "FORBID":
            return _receipt("NON_COLLAPSE", "BLOCK", [f"FORBIDDEN_COLLAPSE:{rule['rule_id']}"], subject)
        if disposition == "DISTINCT_BY_DEFAULT":
            return _receipt("NON_COLLAPSE", "ESCALATE", [f"DISTINCT_BY_DEFAULT:{rule['rule_id']}"], subject)
        allowed = set(rule.get("allowed_witness_types", []))
        if witness_type and witness_type in allowed:
            return _receipt("NON_COLLAPSE", "ALLOW", [f"WITNESSED_EQUIVALENCE:{rule['rule_id']}"], subject)
        return _receipt("NON_COLLAPSE", "BLOCK", [f"WITNESS_REQUIRED:{rule['rule_id']}"], subject)
    return _receipt(
        "NON_COLLAPSE",
        "ESCALATE",
        ["NO_EXPLICIT_RELATION_RULE"],
        {"left_type": left_type, "right_type": right_type, "witness_type": witness_type},
    )

def validate_host_capability(descriptor: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    state = descriptor.get("state")
    if descriptor.get("freshness") != "FRESH":
        reasons.append("CAPABILITY_STATE_NOT_FRESH")
    if state in AVAILABLE_STATES and not descriptor.get("observed_evidence"):
        reasons.append("AVAILABLE_CAPABILITY_REQUIRES_OBSERVED_EVIDENCE")
    if state in {"UNAVAILABLE", "UNKNOWN", "DECLARED_SOURCE_ONLY"}:
        reasons.append(f"CAPABILITY_NOT_EXECUTABLE:{state}")
    if reasons:
        return _receipt("HOST_CAPABILITY", "BLOCK", reasons, descriptor)
    if state == "AVAILABLE_BUT_APPROVAL_REQUIRED":
        return _receipt("HOST_CAPABILITY", "ESCALATE", ["HUMAN_OR_EXTERNAL_APPROVAL_REQUIRED"], descriptor)
    return _receipt("HOST_CAPABILITY", "ALLOW", ["OBSERVED_FRESH_CAPABILITY"], descriptor)

def validate_frontier(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if snapshot.get("freshness") != "FRESH":
        reasons.append("FRONTIER_NOT_FRESH")
    if not snapshot.get("candidate_ids"):
        reasons.append("NO_CANDIDATES")
    if not snapshot.get("protected_invariants"):
        reasons.append("NO_PROTECTED_INVARIANTS")
    if not snapshot.get("source_refs"):
        reasons.append("NO_SOURCE_REFS")
    if reasons:
        return _receipt("FRONTIER", "BLOCK", reasons, snapshot)
    return _receipt("FRONTIER", "ALLOW", ["FRONTIER_ADMISSIBLE_FOR_SELECTION"], snapshot)

def validate_highestone_selection(
    selection: Mapping[str, Any],
    frontier: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    selection_class = selection.get("selection_class")
    if selection_class == "HOLD":
        if selection.get("selected_frontier_id") is not None:
            reasons.append("HOLD_MUST_NOT_SELECT_FRONTIER")
        if not selection.get("blocking_obligations"):
            reasons.append("HOLD_REQUIRES_BLOCKING_OBLIGATION")
    else:
        selected = selection.get("selected_frontier_id")
        if not selected:
            reasons.append("NON_HOLD_REQUIRES_SELECTION")
        if frontier is not None:
            f_receipt = validate_frontier(frontier)
            if f_receipt["decision"] != "ALLOW":
                reasons.append("SOURCE_FRONTIER_NOT_ADMISSIBLE")
            elif selected not in set(frontier.get("candidate_ids", [])):
                reasons.append("SELECTED_FRONTIER_NOT_IN_SNAPSHOT")
    if not selection.get("verification_plan"):
        reasons.append("VERIFICATION_PLAN_REQUIRED")
    if not selection.get("termination_condition"):
        reasons.append("TERMINATION_CONDITION_REQUIRED")
    if reasons:
        return _receipt("HIGHESTONE_SELECTION", "BLOCK", reasons, selection)
    if selection_class == "HOLD":
        return _receipt("HIGHESTONE_SELECTION", "ALLOW", ["LAWFUL_HOLD"], selection)
    return _receipt("HIGHESTONE_SELECTION", "ALLOW", ["BOUNDED_SELECTION"], selection)

def validate_claim_authority(receipt: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    decision = receipt.get("decision")
    delta = receipt.get("semantic_authority_delta")
    if decision == "ALLOW":
        if not receipt.get("authority_source"):
            reasons.append("ALLOW_REQUIRES_AUTHORITY_SOURCE")
        if not receipt.get("witness_refs"):
            reasons.append("ALLOW_REQUIRES_WITNESS")
        if not receipt.get("evidence_refs"):
            reasons.append("ALLOW_REQUIRES_EVIDENCE")
    if delta != "NONE" and (not receipt.get("witness_refs") or not receipt.get("evidence_refs")):
        reasons.append("AUTHORITY_DELTA_REQUIRES_NEW_EVIDENCE_AND_WITNESS")
    if receipt.get("transition_axis") == "HOST_SUBSTRATE" and delta in EPISTEMIC_DELTAS:
        reasons.append("HOST_TRANSPORT_CANNOT_CREATE_EPISTEMIC_PROMOTION")
    if reasons:
        return _receipt("CLAIM_AUTHORITY", "BLOCK", reasons, receipt)
    if decision == "ESCALATE":
        return _receipt("CLAIM_AUTHORITY", "ESCALATE", ["EXPLICIT_ESCALATION"], receipt)
    if decision == "BLOCK":
        return _receipt("CLAIM_AUTHORITY", "ALLOW", ["VALID_RECORDED_BLOCK"], receipt)
    return _receipt("CLAIM_AUTHORITY", "ALLOW", ["WITNESSED_AUTHORITY_TRANSITION"], receipt)

def validate_execution_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    delta = receipt.get("semantic_authority_delta")
    failure_class = receipt.get("failure_class")
    if failure_class == "POLICY_REFUSAL" and delta in {"FORMAL", "EMPIRICAL", "CANONICAL"}:
        reasons.append("PROVIDER_REFUSAL_CANNOT_CREATE_EPISTEMIC_OR_CANONICAL_DELTA")
    if receipt.get("execution_status") == "PASS" and not receipt.get("evidence_refs"):
        reasons.append("PASS_REQUIRES_EXECUTION_EVIDENCE")
    if delta in {"FORMAL", "EMPIRICAL"}:
        reasons.append("EXECUTION_RECEIPT_CANNOT_BY_ITSELF_PROMOTE_FORMAL_OR_EMPIRICAL_STATUS")
    if reasons:
        return _receipt("EXECUTION_RECEIPT", "BLOCK", reasons, receipt)
    return _receipt("EXECUTION_RECEIPT", "ALLOW", ["EXECUTION_STATUS_RECORDED_WITHOUT_AUTHORITY_INFLATION"], receipt)

def validate_migration_witness(witness: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if witness.get("source_adapter") == witness.get("target_adapter"):
        reasons.append("SOURCE_AND_TARGET_ADAPTER_MUST_DIFFER")
    if witness.get("capability_rediscovery_required") is not True:
        reasons.append("CAPABILITY_REDISCOVERY_REQUIRED")
    if witness.get("continuity_verified") is not True:
        reasons.append("CONTINUITY_NOT_VERIFIED")
    if not witness.get("entity_roots"):
        reasons.append("ENTITY_ROOTS_REQUIRED")
    if not witness.get("source_refs"):
        reasons.append("MIGRATION_SOURCE_REFS_REQUIRED")
    if reasons:
        return _receipt("MIGRATION", "BLOCK", reasons, witness)
    return _receipt("MIGRATION", "ALLOW", ["PORTABLE_CONTINUITY_WITNESSED"], witness)

def validate_canon_admission(receipt: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    decision = receipt.get("decision")
    if decision in {"ADMIT", "SUPERSEDE"}:
        if not receipt.get("evidence_refs"):
            reasons.append("ADMISSION_REQUIRES_EVIDENCE")
        if not receipt.get("witness_refs"):
            reasons.append("ADMISSION_REQUIRES_WITNESS")
        if not receipt.get("target_state"):
            reasons.append("ADMISSION_REQUIRES_TARGET_STATE")
        if not receipt.get("target_canonical_digest"):
            reasons.append("ADMISSION_REQUIRES_TARGET_DIGEST")
    if decision == "SUPERSEDE" and not receipt.get("supersedes"):
        reasons.append("SUPERSEDE_REQUIRES_PREDECESSOR")
    if receipt.get("semantic_authority_delta") in {"FORMAL", "EMPIRICAL"}:
        reasons.append("CANON_ADMISSION_ALONE_CANNOT_CREATE_FORMAL_OR_EMPIRICAL_AUTHORITY")
    if reasons:
        return _receipt("CANON_ADMISSION", "BLOCK", reasons, receipt)
    return _receipt("CANON_ADMISSION", "ALLOW", [f"VALID_{decision}_RECEIPT"], receipt)
