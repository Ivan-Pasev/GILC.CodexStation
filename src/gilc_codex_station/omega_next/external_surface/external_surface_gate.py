"""Fail-closed validation for externally executed Ω NEXT live gates."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

EXPECTED_FINGERPRINT = "074218146dbea2821277e98b90c89bd405bc2f882443fe03cd477337f5100863"
EXPECTED_PLUGIN = {
    "plugin_id": "Plugin_61ce89a2af3c819183f45b6d721005e2",
    "version": "0.3.0-alpha.2",
    "release_id": "pluginrel_6abecf39798c8191a75c350743c84dc0",
}

NB00_CRITICAL = {"T1", "T2", "T3", "T4", "T5"}

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def validate_gate_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if manifest.get("root_semantic_fingerprint") != EXPECTED_FINGERPRINT:
        reasons.append("ROOT_SEMANTIC_FINGERPRINT_MISMATCH")
    if manifest.get("plugin_baseline") != EXPECTED_PLUGIN:
        reasons.append("PLUGIN_BASELINE_MISMATCH")
    gates = list(manifest.get("gates", []))
    ids = {g.get("gate_id") for g in gates}
    if ids != {"NB00_LIVE_CONFORMANCE_01", "RGT-04_BUNDLED_FALLBACK_CLEAN_CHAT"}:
        reasons.append("EXACT_EXTERNAL_GATE_SET_REQUIRED")
    expected_surface = {
        "NB00_LIVE_CONFORMANCE_01": "GEMINI_NOTEBOOK",
        "RGT-04_BUNDLED_FALLBACK_CLEAN_CHAT": "CHAT_CLEAN",
    }
    for gate in gates:
        gid = gate.get("gate_id")
        if gate.get("required_surface") != expected_surface.get(gid):
            reasons.append(f"WRONG_REQUIRED_SURFACE:{gid}")
    if manifest.get("authority_delta") != "NONE":
        reasons.append("MANIFEST_AUTHORITY_DELTA_FORBIDDEN")
    return {
        "check": "EXTERNAL_SURFACE_GATE_MANIFEST",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "manifest_digest": digest(manifest),
    }

def _validate_nb00(receipt: Mapping[str, Any], reasons: list[str]) -> None:
    if receipt.get("surface") != "GEMINI_NOTEBOOK":
        reasons.append("NB00_REQUIRES_GEMINI_NOTEBOOK_SURFACE")
    if receipt.get("independent_surface_observed") is not True:
        reasons.append("NB00_REQUIRES_INDEPENDENT_SURFACE_OBSERVATION")
    if receipt.get("root_semantic_fingerprint") != EXPECTED_FINGERPRINT:
        reasons.append("NB00_ROOT_FINGERPRINT_MISMATCH")
    if receipt.get("six_core_sources_attached") is not True:
        reasons.append("NB00_REQUIRES_SIX_CORE_SOURCES")
    if receipt.get("instruction_applied") is not True:
        reasons.append("NB00_REQUIRES_INSTRUCTION_APPLIED")
    if not receipt.get("notebook_locator"):
        reasons.append("NB00_REQUIRES_NOTEBOOK_LOCATOR")
    tests = {t.get("id"): t.get("status") for t in receipt.get("tests") or []}
    for tid in NB00_CRITICAL:
        if tests.get(tid) != "PASS":
            reasons.append(f"NB00_CRITICAL_TEST_NOT_PASS:{tid}")
    # T6-T8 must be explicit even if limited/blocked.
    for tid in {"T6", "T7", "T8"}:
        if tid not in tests:
            reasons.append(f"NB00_NONCRITICAL_TEST_NOT_RECORDED:{tid}")

def _validate_rgt04(receipt: Mapping[str, Any], reasons: list[str]) -> None:
    if receipt.get("surface") != "CHAT_CLEAN":
        reasons.append("RGT04_REQUIRES_CHAT_CLEAN_SURFACE")
    if receipt.get("independent_surface_observed") is not True:
        reasons.append("RGT04_REQUIRES_INDEPENDENT_SURFACE_OBSERVATION")
    if receipt.get("plugin_id") != EXPECTED_PLUGIN["plugin_id"]:
        reasons.append("RGT04_PLUGIN_ID_MISMATCH")
    if receipt.get("plugin_version") != EXPECTED_PLUGIN["version"]:
        reasons.append("RGT04_PLUGIN_VERSION_MISMATCH")
    if receipt.get("plugin_release_id") != EXPECTED_PLUGIN["release_id"]:
        reasons.append("RGT04_PLUGIN_RELEASE_MISMATCH")
    if receipt.get("project_context_present") is not False:
        reasons.append("RGT04_PROJECT_CONTEXT_MUST_BE_FALSE")
    if receipt.get("bundled_source_named") is not True:
        reasons.append("RGT04_BUNDLED_SOURCE_MUST_BE_NAMED")
    if receipt.get("snapshot_caveat_present") is not True:
        reasons.append("RGT04_SNAPSHOT_CAVEAT_REQUIRED")
    if receipt.get("live_canon_claim_without_live_evidence") is not False:
        reasons.append("RGT04_LIVE_CANON_CLAIM_FORBIDDEN")
    if receipt.get("scientific_authority_delta") != "NONE":
        reasons.append("RGT04_SCIENTIFIC_AUTHORITY_DELTA_FORBIDDEN")
    if receipt.get("result") != "PASS":
        reasons.append("RGT04_RECEIPT_RESULT_NOT_PASS")
    if not receipt.get("transcript_excerpt"):
        reasons.append("RGT04_TRANSCRIPT_EXCERPT_REQUIRED")

def validate_external_surface_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if receipt.get("authority_delta") != "NONE":
        reasons.append("RECEIPT_AUTHORITY_DELTA_FORBIDDEN")
    if not receipt.get("evidence_refs"):
        reasons.append("EVIDENCE_REFS_REQUIRED")
    gate_id = receipt.get("gate_id")
    if gate_id == "NB00_LIVE_CONFORMANCE_01":
        _validate_nb00(receipt, reasons)
    elif gate_id == "RGT-04_BUNDLED_FALLBACK_CLEAN_CHAT":
        _validate_rgt04(receipt, reasons)
    else:
        reasons.append("UNKNOWN_GATE_ID")
    return {
        "check": "EXTERNAL_SURFACE_RECEIPT",
        "gate_id": gate_id,
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "receipt_digest": digest(receipt),
        "gate_effect": "CLOSE_THIS_GATE_ONLY" if not reasons else "NONE",
        "authority_delta": "NONE",
    }
