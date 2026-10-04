"""Fail-closed boot validation for the Google/Gemini Notebook projection."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

EXPECTED_CELLS = {"NB00", "NB10", "NB20", "NB30", "NB40"}
EXPECTED_FINGERPRINT = "074218146dbea2821277e98b90c89bd405bc2f882443fe03cd477337f5100863"
PASS_STATES = {"LIVE_BOOT_PASS", "LIVE_BOOT_PASS_WITH_LIMITATIONS"}

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def validate_capability_observation(obs: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    state = obs.get("state")
    evidence = obs.get("evidence_refs") or []
    evidence_class = obs.get("evidence_class")
    if state == "OBSERVED_AVAILABLE":
        if evidence_class != "HOST_CAPABILITY_OBSERVATION":
            reasons.append("OBSERVED_AVAILABLE_REQUIRES_HOST_CAPABILITY_OBSERVATION")
        if not evidence:
            reasons.append("OBSERVED_AVAILABLE_REQUIRES_EVIDENCE")
    if state == "SOURCE_REPORTED_FEATURE":
        if evidence_class != "SOURCE_REPORTED":
            reasons.append("SOURCE_REPORTED_FEATURE_REQUIRES_SOURCE_REPORTED_CLASS")
        if not evidence:
            reasons.append("SOURCE_REPORTED_FEATURE_REQUIRES_SOURCE")
    if state == "UNAVAILABLE_IN_CURRENT_SURFACE" and evidence_class != "ENVIRONMENT_NEGATIVE":
        reasons.append("UNAVAILABLE_CURRENT_SURFACE_REQUIRES_ENVIRONMENT_NEGATIVE_CLASS")
    if state == "UNKNOWN" and evidence_class != "UNKNOWN":
        reasons.append("UNKNOWN_STATE_REQUIRES_UNKNOWN_EVIDENCE_CLASS")
    return {
        "check": "CAPABILITY_OBSERVATION",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "capability_id": obs.get("capability_id"),
        "observation_digest": digest(obs),
    }

def validate_boot_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if manifest.get("root_semantic_fingerprint") != EXPECTED_FINGERPRINT:
        reasons.append("ROOT_SEMANTIC_FINGERPRINT_MISMATCH")
    sources = list(manifest.get("boot_sources", []))
    if len(sources) != 6:
        reasons.append("EXACTLY_SIX_BOOT_SOURCES_REQUIRED")
    slots = [x.get("slot") for x in sources]
    if slots != [1, 2, 3, 4, 5, 6]:
        reasons.append("BOOT_SOURCE_SLOTS_MUST_BE_ORDERED_1_TO_6")
    if any(x.get("required") is not True for x in sources):
        reasons.append("ALL_BOOT_SOURCES_MUST_BE_REQUIRED")
    cells = list(manifest.get("cells", []))
    ids = {x.get("cell_id") for x in cells}
    if ids != EXPECTED_CELLS:
        reasons.append("EXACT_NOTEBOOK_CELL_SET_REQUIRED")
    orders = sorted(x.get("initialization_order") for x in cells)
    if orders != [1, 2, 3, 4, 5]:
        reasons.append("INITIALIZATION_ORDER_MUST_BE_1_TO_5")
    nb00 = next((x for x in cells if x.get("cell_id") == "NB00"), None)
    if not nb00 or nb00.get("initialization_order") != 1:
        reasons.append("NB00_MUST_INITIALIZE_FIRST")
    for obs in manifest.get("capability_observations", []):
        receipt = validate_capability_observation(obs)
        if receipt["decision"] != "PASS":
            reasons.extend(f"CAPABILITY:{obs.get('capability_id')}:{r}" for r in receipt["reasons"])
    return {
        "check": "GOOGLE_NOTEBOOK_BOOT_MANIFEST",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "manifest_digest": digest(manifest),
    }

def validate_live_boot_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    status = receipt.get("status")
    if receipt.get("root_semantic_fingerprint") != EXPECTED_FINGERPRINT:
        reasons.append("ROOT_SEMANTIC_FINGERPRINT_MISMATCH")
    if receipt.get("authority_delta") != "NONE":
        reasons.append("BOOT_CANNOT_CREATE_AUTHORITY_DELTA")
    if status in PASS_STATES:
        if receipt.get("core_sources_attached") is not True:
            reasons.append("LIVE_PASS_REQUIRES_CORE_SOURCES")
        if receipt.get("instruction_applied") is not True:
            reasons.append("LIVE_PASS_REQUIRES_INSTRUCTION")
        if receipt.get("observed_source_limit") is None:
            reasons.append("LIVE_PASS_REQUIRES_OBSERVED_SOURCE_LIMIT")
        canaries = list(receipt.get("canaries", []))
        critical = [x for x in canaries if x.get("critical") is True]
        if not critical:
            reasons.append("LIVE_PASS_REQUIRES_CRITICAL_CANARIES")
        for canary in critical:
            if canary.get("status") != "PASS":
                reasons.append(f"CRITICAL_CANARY_NOT_PASS:{canary.get('canary_id')}")
        if not receipt.get("evidence_refs"):
            reasons.append("LIVE_PASS_REQUIRES_EVIDENCE_REFS")
    if status == "BOOT_PREPARED":
        for canary in receipt.get("canaries", []):
            if canary.get("status") == "PASS":
                reasons.append("BOOT_PREPARED_MUST_NOT_CLAIM_LIVE_CANARY_PASS")
    return {
        "check": "NOTEBOOK_LIVE_BOOT_RECEIPT",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "receipt_digest": digest(receipt),
    }
