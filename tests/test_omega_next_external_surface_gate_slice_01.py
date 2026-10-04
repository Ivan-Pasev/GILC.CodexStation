import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from gilc_codex_station.omega_next.external_surface.external_surface_gate import (
    EXPECTED_FINGERPRINT,
    EXPECTED_PLUGIN,
    validate_external_surface_receipt,
    validate_gate_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = json.loads(
    (ROOT / "contracts" / "omega_next" / "external_surface" / "EXTERNAL_SURFACE_GATE_SLICE_01.bundle.json").read_text(encoding="utf-8")
)
SCHEMAS = BUNDLE["schemas"]
MANIFEST = BUNDLE["manifest"]

@pytest.mark.parametrize("schema_name", sorted(SCHEMAS))
def test_schema_meta_validation(schema_name):
    Draft202012Validator.check_schema(SCHEMAS[schema_name])

def validate(schema_name, instance):
    Draft202012Validator(
        SCHEMAS[schema_name],
        format_checker=FormatChecker(),
    ).validate(instance)

def test_gate_manifest_validates():
    validate("ExternalSurfaceGateManifest.schema.json", MANIFEST)
    result = validate_gate_manifest(MANIFEST)
    assert result["decision"] == "PASS"

def nb00_receipt():
    return {
        "receipt_id": "external:nb00:sample",
        "gate_id": "NB00_LIVE_CONFORMANCE_01",
        "surface": "GEMINI_NOTEBOOK",
        "independent_surface_observed": True,
        "authority_delta": "NONE",
        "evidence_refs": ["gemini-notebook:nb00"],
        "notebook_name": "CODEXSTATION Ω NEXT — NB00 — ORCHESTRATOR CONTROL TOWER",
        "notebook_locator": "https://gemini.google.com/example/nb00",
        "root_semantic_fingerprint": EXPECTED_FINGERPRINT,
        "observed_source_limit": 300,
        "six_core_sources_attached": True,
        "instruction_applied": True,
        "tests": [
            {"id": f"T{i}", "status": "PASS", "detail": "sample"}
            for i in range(1, 9)
        ],
        "plugin_id": None,
        "plugin_version": None,
        "plugin_release_id": None,
        "project_context_present": None,
        "bundled_source_named": None,
        "snapshot_caveat_present": None,
        "live_canon_claim_without_live_evidence": None,
        "scientific_authority_delta": None,
        "result": None,
        "transcript_excerpt": None,
        "observed_capabilities": ["drive-source-citations"],
        "limitations": [],
    }

def rgt04_receipt():
    return {
        "receipt_id": "external:rgt04:sample",
        "gate_id": "RGT-04_BUNDLED_FALLBACK_CLEAN_CHAT",
        "surface": "CHAT_CLEAN",
        "independent_surface_observed": True,
        "authority_delta": "NONE",
        "evidence_refs": ["chat-clean:example"],
        "notebook_name": None,
        "notebook_locator": None,
        "root_semantic_fingerprint": None,
        "observed_source_limit": None,
        "six_core_sources_attached": None,
        "instruction_applied": None,
        "tests": None,
        "plugin_id": EXPECTED_PLUGIN["plugin_id"],
        "plugin_version": EXPECTED_PLUGIN["version"],
        "plugin_release_id": EXPECTED_PLUGIN["release_id"],
        "project_context_present": False,
        "bundled_source_named": True,
        "snapshot_caveat_present": True,
        "live_canon_claim_without_live_evidence": False,
        "scientific_authority_delta": "NONE",
        "result": "PASS",
        "transcript_excerpt": "Using bundled snapshot only; no claim that this is current live canon.",
        "observed_capabilities": [],
        "limitations": [],
    }

def test_nb00_receipt_passes():
    r = nb00_receipt()
    validate("ExternalSurfaceReceipt.schema.json", r)
    result = validate_external_surface_receipt(r)
    assert result["decision"] == "PASS"
    assert result["gate_effect"] == "CLOSE_THIS_GATE_ONLY"

def test_nb00_requires_critical_t1_to_t5():
    for tid in ("T1", "T2", "T3", "T4", "T5"):
        bad = nb00_receipt()
        next(t for t in bad["tests"] if t["id"] == tid)["status"] = "FAIL"
        result = validate_external_surface_receipt(bad)
        assert result["decision"] == "FAIL"
        assert f"NB00_CRITICAL_TEST_NOT_PASS:{tid}" in result["reasons"]

def test_nb00_records_noncritical_t6_to_t8():
    bad = nb00_receipt()
    bad["tests"] = [t for t in bad["tests"] if t["id"] != "T6"]
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "NB00_NONCRITICAL_TEST_NOT_RECORDED:T6" in result["reasons"]

def test_nb00_rejects_wrong_fingerprint():
    bad = nb00_receipt()
    bad["root_semantic_fingerprint"] = "0" * 64
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "NB00_ROOT_FINGERPRINT_MISMATCH" in result["reasons"]

def test_nb00_cannot_self_report_same_surface():
    bad = nb00_receipt()
    bad["independent_surface_observed"] = False
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "NB00_REQUIRES_INDEPENDENT_SURFACE_OBSERVATION" in result["reasons"]

def test_rgt04_receipt_passes():
    r = rgt04_receipt()
    validate("ExternalSurfaceReceipt.schema.json", r)
    result = validate_external_surface_receipt(r)
    assert result["decision"] == "PASS"
    assert result["gate_effect"] == "CLOSE_THIS_GATE_ONLY"

def test_rgt04_requires_clean_chat():
    bad = rgt04_receipt()
    bad["surface"] = "GEMINI_NOTEBOOK"
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "RGT04_REQUIRES_CHAT_CLEAN_SURFACE" in result["reasons"]

def test_rgt04_rejects_project_context():
    bad = rgt04_receipt()
    bad["project_context_present"] = True
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "RGT04_PROJECT_CONTEXT_MUST_BE_FALSE" in result["reasons"]

def test_rgt04_requires_snapshot_caveat():
    bad = rgt04_receipt()
    bad["snapshot_caveat_present"] = False
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "RGT04_SNAPSHOT_CAVEAT_REQUIRED" in result["reasons"]

def test_rgt04_rejects_live_canon_claim():
    bad = rgt04_receipt()
    bad["live_canon_claim_without_live_evidence"] = True
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "RGT04_LIVE_CANON_CLAIM_FORBIDDEN" in result["reasons"]

def test_rgt04_rejects_stale_plugin_release():
    bad = rgt04_receipt()
    bad["plugin_release_id"] = "pluginrel_stale"
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "RGT04_PLUGIN_RELEASE_MISMATCH" in result["reasons"]

def test_receipt_cannot_create_authority_delta():
    bad = nb00_receipt()
    bad["authority_delta"] = "FORMAL"
    result = validate_external_surface_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "RECEIPT_AUTHORITY_DELTA_FORBIDDEN" in result["reasons"]

def test_gate_close_is_local_only():
    for receipt in (nb00_receipt(), rgt04_receipt()):
        result = validate_external_surface_receipt(receipt)
        assert result["gate_effect"] == "CLOSE_THIS_GATE_ONLY"
        assert result["authority_delta"] == "NONE"
