import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from gilc_codex_station.omega_next.openai_plugin.openai_plugin_sync import (
    EXPECTED_FINGERPRINT,
    REQUIRED_PLUGIN_SKILLS,
    validate_runtime_receipt,
    validate_sync_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = json.loads(
    (ROOT / "contracts" / "omega_next" / "openai_plugin" / "OPENAI_PLUGIN_SYNC_SLICE_01.bundle.json").read_text(encoding="utf-8")
)
SCHEMAS = BUNDLE["schemas"]
MANIFEST = BUNDLE["sync_manifest"]

@pytest.mark.parametrize("schema_name", sorted(SCHEMAS))
def test_schema_meta_validation(schema_name):
    Draft202012Validator.check_schema(SCHEMAS[schema_name])

def validate(schema_name, instance):
    Draft202012Validator(
        SCHEMAS[schema_name],
        format_checker=FormatChecker(),
    ).validate(instance)

def test_sync_manifest_validates():
    validate("OpenAIPluginSyncManifest.schema.json", MANIFEST)
    receipt = validate_sync_manifest(MANIFEST)
    assert receipt["decision"] == "PASS"
    assert receipt["deployment_allowed"] is False

def test_runtime_receipt_validates_project_vectors():
    receipt = MANIFEST["runtime_gate_receipt"]
    validate("PluginRuntimeGateReceipt.schema.json", receipt)
    result = validate_runtime_receipt(receipt)
    assert result["decision"] == "PASS"
    vectors = {x["id"]: x["status"] for x in receipt["vectors"]}
    assert vectors == {
        "RGT-01": "PASS",
        "RGT-02": "PASS",
        "RGT-03": "PASS",
        "RGT-04": "OPEN",
    }

def test_required_plugin_skill_surface_observed():
    observed = set(MANIFEST["observed_plugin_skills"])
    assert REQUIRED_PLUGIN_SKILLS.issubset(observed)
    assert len(observed) == 9

def test_root_fingerprint_matches_distribution_compiler():
    assert MANIFEST["root_semantic_fingerprint"] == EXPECTED_FINGERPRINT

def test_rgt04_open_forces_prepared_not_deployed():
    assert MANIFEST["deployment_state"] == "PREPARED_NOT_DEPLOYED"
    assert "RGT-04_BUNDLED_FALLBACK_CLEAN_CHAT" in MANIFEST["deployment_blockers"]
    assert MANIFEST["planned_extension"]["status"] == "PREPARED_NOT_DEPLOYED"

def test_sync_cannot_hide_rgt04_blocker():
    bad = json.loads(json.dumps(MANIFEST))
    bad["deployment_blockers"] = []
    result = validate_sync_manifest(bad)
    assert result["decision"] == "FAIL"
    assert "RGT04_BLOCKER_MUST_BE_EXPLICIT" in result["reasons"]

def test_sync_cannot_claim_deployment_while_rgt04_open():
    bad = json.loads(json.dumps(MANIFEST))
    bad["deployment_state"] = "DEPLOYED_ALPHA"
    result = validate_sync_manifest(bad)
    assert result["decision"] == "FAIL"
    assert "DEPLOYMENT_FORBIDDEN_WHILE_RGT04_NOT_PASS" in result["reasons"]

def test_sync_cannot_create_authority_delta():
    bad = json.loads(json.dumps(MANIFEST))
    bad["authority_delta"] = "FORMAL"
    result = validate_sync_manifest(bad)
    assert result["decision"] == "FAIL"
    assert "SYNC_CANNOT_CREATE_AUTHORITY_DELTA" in result["reasons"]

def test_missing_existing_plugin_skill_fails_closed():
    bad = json.loads(json.dumps(MANIFEST))
    bad["observed_plugin_skills"].remove("codexstation-regression-harness")
    result = validate_sync_manifest(bad)
    assert result["decision"] == "FAIL"
    assert "MISSING_INSTALLED_SKILL:codexstation-regression-harness" in result["reasons"]

def test_binding_cannot_claim_unobserved_skill():
    bad = json.loads(json.dumps(MANIFEST))
    bad["skill_bindings"][0]["plugin_skill"] = "not-installed"
    result = validate_sync_manifest(bad)
    assert result["decision"] == "FAIL"
    assert "BINDING_CLAIMS_UNOBSERVED_SKILL:not-installed" in result["reasons"]

def test_project_receipt_must_be_non_mutating():
    bad = json.loads(json.dumps(MANIFEST))
    bad["runtime_gate_receipt"]["mutation_status"] = "MUTATED"
    result = validate_sync_manifest(bad)
    assert result["decision"] == "FAIL"
    assert "RUNTIME:REGRESSION_RECEIPT_MUST_BE_NON_MUTATING" in result["reasons"]

def test_scientific_authority_delta_forbidden_in_runtime_receipt():
    bad = json.loads(json.dumps(MANIFEST["runtime_gate_receipt"]))
    bad["scientific_authority_delta"] = "FORMAL"
    result = validate_runtime_receipt(bad)
    assert result["decision"] == "FAIL"
    assert "SCIENTIFIC_AUTHORITY_DELTA_FORBIDDEN" in result["reasons"]

def test_rgt01_to_03_are_required_for_sync_preparation():
    for rid in ("RGT-01", "RGT-02", "RGT-03"):
        bad = json.loads(json.dumps(MANIFEST["runtime_gate_receipt"]))
        next(x for x in bad["vectors"] if x["id"] == rid)["status"] = "OPEN"
        result = validate_runtime_receipt(bad)
        assert result["decision"] == "FAIL"
        assert f"{rid}_MUST_PASS_FOR_SYNC_PREPARATION" in result["reasons"]

def test_rgt04_pass_removes_clean_chat_blocker_but_does_not_imply_release():
    good = json.loads(json.dumps(MANIFEST))
    next(x for x in good["runtime_gate_receipt"]["vectors"] if x["id"] == "RGT-04")["status"] = "PASS"
    good["deployment_blockers"] = []
    # Deployment remains only evaluable here; the validator must not create
    # release authority. PREPARED_NOT_DEPLOYED is still acceptable.
    result = validate_sync_manifest(good)
    assert result["decision"] == "PASS"
    assert result["deployment_allowed"] is True
    assert good["authority_delta"] == "NONE"
