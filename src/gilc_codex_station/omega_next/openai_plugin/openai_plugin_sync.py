"""Fail-closed Ω NEXT -> ChatGPT plugin synchronization validator."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

EXPECTED_FINGERPRINT = "074218146dbea2821277e98b90c89bd405bc2f882443fe03cd477337f5100863"
REQUIRED_PLUGIN_SKILLS = {
    "canonical-evolution",
    "codexstation-capability-router",
    "codexstation-evolution-kernel",
    "codexstation-knowledge-metabolism",
    "codexstation-orchestrator",
    "codexstation-regression-harness",
    "codexstation-stack-resolver",
    "evidence-gate",
    "release-packager",
}

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def validate_runtime_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    vectors = {x.get("id"): x for x in receipt.get("vectors", [])}
    for rid in ("RGT-01", "RGT-02", "RGT-03", "RGT-04"):
        if rid not in vectors:
            reasons.append(f"MISSING_VECTOR:{rid}")
    if vectors.get("RGT-01", {}).get("status") != "PASS":
        reasons.append("RGT-01_MUST_PASS_FOR_SYNC_PREPARATION")
    if vectors.get("RGT-02", {}).get("status") != "PASS":
        reasons.append("RGT-02_MUST_PASS_FOR_SYNC_PREPARATION")
    if vectors.get("RGT-03", {}).get("status") != "PASS":
        reasons.append("RGT-03_MUST_PASS_FOR_SYNC_PREPARATION")
    if receipt.get("mutation_status") != "NONE":
        reasons.append("REGRESSION_RECEIPT_MUST_BE_NON_MUTATING")
    if receipt.get("scientific_authority_delta") != "NONE":
        reasons.append("SCIENTIFIC_AUTHORITY_DELTA_FORBIDDEN")
    return {
        "check": "PLUGIN_RUNTIME_GATE_RECEIPT",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "receipt_digest": digest(receipt),
    }

def validate_sync_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []

    if manifest.get("root_semantic_fingerprint") != EXPECTED_FINGERPRINT:
        reasons.append("ROOT_SEMANTIC_FINGERPRINT_MISMATCH")

    observed = set(manifest.get("observed_plugin_skills", []))
    missing = sorted(REQUIRED_PLUGIN_SKILLS - observed)
    if missing:
        reasons.extend(f"MISSING_INSTALLED_SKILL:{name}" for name in missing)

    bindings = list(manifest.get("skill_bindings", []))
    bound_plugin_skills = {b.get("plugin_skill") for b in bindings}
    for required in (
        "codexstation-orchestrator",
        "codexstation-stack-resolver",
        "codexstation-knowledge-metabolism",
        "codexstation-capability-router",
        "evidence-gate",
        "canonical-evolution",
        "release-packager",
    ):
        if required not in bound_plugin_skills:
            reasons.append(f"MISSING_SKILL_BINDING:{required}")

    for binding in bindings:
        if binding.get("status") == "OBSERVED_INSTALLED":
            if binding.get("plugin_skill") not in observed:
                reasons.append(f"BINDING_CLAIMS_UNOBSERVED_SKILL:{binding.get('plugin_skill')}")
            if binding.get("capability_claim") != "OBSERVED_PLUGIN_SKILL":
                reasons.append(f"OBSERVED_BINDING_BAD_CAPABILITY_CLASS:{binding.get('plugin_skill')}")
        if binding.get("capability_claim") == "OBSERVED_PLUGIN_SKILL":
            # Presence of a plugin skill is evidence only of installed skill surface,
            # never of external host capability or authorization.
            if binding.get("authority_ceiling") not in {"METHOD", "EXECUTION", "CANONICAL", "NONE"}:
                reasons.append(f"INVALID_AUTHORITY_CEILING:{binding.get('plugin_skill')}")

    runtime = validate_runtime_receipt(manifest.get("runtime_gate_receipt", {}))
    if runtime["decision"] != "PASS":
        reasons.extend(f"RUNTIME:{r}" for r in runtime["reasons"])

    vectors = {x.get("id"): x for x in manifest.get("runtime_gate_receipt", {}).get("vectors", [])}
    rgt04 = vectors.get("RGT-04", {}).get("status")
    deployment_state = manifest.get("deployment_state")
    blockers = set(manifest.get("deployment_blockers", []))

    if rgt04 != "PASS":
        if deployment_state != "PREPARED_NOT_DEPLOYED":
            reasons.append("DEPLOYMENT_FORBIDDEN_WHILE_RGT04_NOT_PASS")
        if "RGT-04_BUNDLED_FALLBACK_CLEAN_CHAT" not in blockers:
            reasons.append("RGT04_BLOCKER_MUST_BE_EXPLICIT")
    else:
        # Passing RGT-04 permits evaluation of deployment, but does not itself
        # authorize release or mutation.
        if "RGT-04_BUNDLED_FALLBACK_CLEAN_CHAT" in blockers:
            reasons.append("STALE_RGT04_BLOCKER_AFTER_PASS")

    if manifest.get("authority_delta") != "NONE":
        reasons.append("SYNC_CANNOT_CREATE_AUTHORITY_DELTA")

    extension = manifest.get("planned_extension", {})
    if extension.get("name") in observed:
        if extension.get("status") == "PREPARED_NOT_DEPLOYED":
            reasons.append("PREPARED_EXTENSION_ALREADY_OBSERVED_INSTALLED")
    if extension.get("status") == "DEPLOYED" and deployment_state == "PREPARED_NOT_DEPLOYED":
        reasons.append("EXTENSION_DEPLOYMENT_STATE_CONTRADICTION")

    return {
        "check": "OPENAI_PLUGIN_SYNC_MANIFEST",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "manifest_digest": digest(manifest),
        "deployment_allowed": rgt04 == "PASS" and not reasons,
    }
