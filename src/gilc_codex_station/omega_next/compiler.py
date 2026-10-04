"""Provider-independent distribution compiler for CodexStation Ω NEXT.

Finite implementation surface only. This module preserves the shared semantic root
while allowing host-specific compiled views for Google and OpenAI distributions.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

ALLOWED_PROFILE_PROVIDERS = {"GOOGLE", "OPENAI"}
HOST_BINDING_STATES = {"DECLARED_ONLY", "OBSERVED_AVAILABLE", "UNAVAILABLE", "UNKNOWN"}

def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()

def semantic_payload(root_manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "root_id": root_manifest["root_id"],
        "lineage_id": root_manifest["lineage_id"],
        "control_documents": root_manifest["control_documents"],
        "protected_invariants": root_manifest["protected_invariants"],
        "source_precedence": root_manifest["source_precedence"],
        "authority_model": root_manifest["authority_model"],
    }

def semantic_fingerprint(root_manifest: Mapping[str, Any]) -> str:
    return digest(semantic_payload(root_manifest))

def validate_lineage_registry(registry: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    records = list(registry.get("records", []))
    ids = [r.get("lineage_id") for r in records]
    if len(ids) != len(set(ids)):
        reasons.append("DUPLICATE_LINEAGE_ID")
    active = [r for r in records if r.get("active_parent") is True]
    if len(active) != 1:
        reasons.append("EXACTLY_ONE_ACTIVE_PARENT_REQUIRED")
    labels: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        labels.setdefault(str(record.get("label")), []).append(record)
    for label, group in labels.items():
        if len(group) > 1:
            for record in group:
                if record.get("merge_policy") not in {"DISTINCT_UNLESS_WITNESSED", "EXPLICIT_SUPERSESSION_ONLY"}:
                    reasons.append(f"SAME_LABEL_REQUIRES_DISTINCT_MERGE_POLICY:{label}")
    decision = "PASS" if not reasons else "FAIL"
    return {
        "check": "SOURCE_LINEAGE_REGISTRY",
        "decision": decision,
        "reasons": sorted(set(reasons)),
        "registry_digest": digest(registry),
    }

def validate_skill_record(
    skill: Mapping[str, Any],
    observed_capabilities: Iterable[str] = (),
) -> dict[str, Any]:
    reasons: list[str] = []
    observed = set(observed_capabilities)
    for binding in skill.get("host_bindings", []):
        state = binding.get("binding_state")
        if state not in HOST_BINDING_STATES:
            reasons.append("INVALID_HOST_BINDING_STATE")
        if state == "OBSERVED_AVAILABLE":
            cap = binding.get("capability")
            evidence = binding.get("observed_evidence") or []
            if cap not in observed:
                reasons.append(f"CAPABILITY_NOT_OBSERVED:{cap}")
            if not evidence:
                reasons.append(f"OBSERVED_CAPABILITY_REQUIRES_EVIDENCE:{cap}")
    executable = set(skill.get("required_capabilities", [])).issubset(observed)
    return {
        "check": "SKILL_RECORD",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "executable_now": executable,
        "skill_uri": skill.get("skill_uri"),
        "skill_digest": digest(skill),
    }

def resolve_skills(
    skill_index: Mapping[str, Any],
    intent_tags: Sequence[str],
    observed_capabilities: Iterable[str] = (),
) -> list[dict[str, Any]]:
    wanted = {x.lower() for x in intent_tags}
    results: list[dict[str, Any]] = []
    for skill in skill_index.get("skills", []):
        tags = {str(x).lower() for x in skill.get("retrieval_tags", [])}
        if wanted and not wanted.intersection(tags):
            continue
        receipt = validate_skill_record(skill, observed_capabilities)
        results.append({
            "skill_uri": skill["skill_uri"],
            "name": skill["name"],
            "status": skill["status"],
            "authority_ceiling": skill["authority_ceiling"],
            "executable_now": receipt["executable_now"],
            "validation": receipt["decision"],
            "context_cost": skill["context_cost"],
        })
    return sorted(results, key=lambda x: (not x["executable_now"], x["context_cost"], x["skill_uri"]))

def validate_context_capsule(capsule: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if not capsule.get("source_refs"):
        reasons.append("SOURCE_REFS_REQUIRED")
    if not capsule.get("invariants"):
        reasons.append("INVARIANTS_REQUIRED")
    if not capsule.get("current_state"):
        reasons.append("CURRENT_STATE_REQUIRED")
    for claim in capsule.get("claims", []):
        if not claim.get("source_refs"):
            reasons.append("CLAIM_SOURCE_REFS_REQUIRED")
    return {
        "check": "CONTEXT_CAPSULE",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "capsule_digest": digest(capsule),
    }

def validate_bridge_capsule(capsule: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if capsule.get("source_cell") == capsule.get("target_cell"):
        reasons.append("BRIDGE_REQUIRES_DISTINCT_CELLS")
    if not capsule.get("source_refs"):
        reasons.append("SOURCE_REFS_REQUIRED")
    for claim in capsule.get("claims", []):
        if claim.get("target_authority_ceiling") != claim.get("source_authority_ceiling"):
            reasons.append("BRIDGE_TRANSPORT_CANNOT_PROMOTE_OR_REWRITE_AUTHORITY")
        if not claim.get("source_refs"):
            reasons.append("BRIDGE_CLAIM_SOURCE_REFS_REQUIRED")
    return {
        "check": "BRIDGE_CAPSULE",
        "decision": "PASS" if not reasons else "FAIL",
        "reasons": sorted(set(reasons)),
        "bridge_digest": digest(capsule),
    }

def compile_distribution(
    root_manifest: Mapping[str, Any],
    profile_spec: Mapping[str, Any],
) -> dict[str, Any]:
    provider = profile_spec.get("provider")
    if provider not in ALLOWED_PROFILE_PROVIDERS:
        raise ValueError("unsupported provider")
    if profile_spec.get("semantic_overrides"):
        raise ValueError("semantic overrides are forbidden")
    limitations = list(profile_spec.get("limitations", []))
    if not limitations:
        raise ValueError("distribution limitations must be explicit")
    return {
        "schema": "GILC/CODEXSTATION/OMEGA-NEXT/DISTRIBUTION-PROFILE/0.1",
        "profile_id": profile_spec["profile_id"],
        "provider": provider,
        "version": profile_spec["version"],
        "root_id": root_manifest["root_id"],
        "root_semantic_fingerprint": semantic_fingerprint(root_manifest),
        "inherited_invariants": list(root_manifest["protected_invariants"]),
        "control_documents": list(root_manifest["control_documents"].values()),
        "surfaces": list(profile_spec["surfaces"]),
        "limitations": limitations,
        "host_adapters": list(profile_spec.get("host_adapters", [])),
        "compiled_views": list(profile_spec["compiled_views"]),
        "semantic_overrides": [],
    }

def validate_distribution_conformance(
    root_manifest: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    expected_fp = semantic_fingerprint(root_manifest)

    def add(name: str, ok: bool, detail: str) -> None:
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})

    add("ROOT_BINDING", profile.get("root_id") == root_manifest.get("root_id"), "profile root must equal canonical root")
    add("SEMANTIC_FINGERPRINT", profile.get("root_semantic_fingerprint") == expected_fp, "compiled view must bind exact shared semantic fingerprint")
    add("INVARIANT_INHERITANCE", profile.get("inherited_invariants") == root_manifest.get("protected_invariants"), "protected invariants must be unchanged and ordered")
    add("CONTROL_PACK", profile.get("control_documents") == list(root_manifest.get("control_documents", {}).values()), "four-source control pack must be inherited exactly")
    add("NO_SEMANTIC_OVERRIDES", profile.get("semantic_overrides") == [], "host profile may not redefine shared semantics")
    add("LIMITATIONS_EXPLICIT", bool(profile.get("limitations")), "provider limitations must be explicit")
    decision = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {
        "receipt_id": f"conformance:{profile.get('profile_id')}",
        "profile_id": profile.get("profile_id"),
        "root_id": root_manifest.get("root_id"),
        "root_semantic_fingerprint": expected_fp,
        "decision": decision,
        "checks": checks,
        "limitations": list(profile.get("limitations", [])),
        "authority_delta": "NONE",
        "evidence_refs": ["repo:contracts/omega_next/DISTRIBUTION_COMPILER_SLICE_01.bundle.json"],
    }
