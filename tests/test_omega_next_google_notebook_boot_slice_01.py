import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from gilc_codex_station.omega_next.compiler import (
    validate_bridge_capsule,
    validate_context_capsule,
)
from gilc_codex_station.omega_next.google_notebook.google_notebook_boot import (
    EXPECTED_FINGERPRINT,
    validate_boot_manifest,
    validate_capability_observation,
    validate_live_boot_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = json.loads(
    (ROOT / "contracts" / "omega_next" / "google_notebook" / "GOOGLE_NOTEBOOK_BOOT_SLICE_01.bundle.json").read_text(encoding="utf-8")
)
SCHEMAS = BUNDLE["schemas"]
MANIFEST = BUNDLE["boot_manifest"]

@pytest.mark.parametrize("schema_name", sorted(SCHEMAS))
def test_schema_meta_validation(schema_name):
    Draft202012Validator.check_schema(SCHEMAS[schema_name])

def validate(schema_name, instance):
    Draft202012Validator(
        SCHEMAS[schema_name], format_checker=FormatChecker()
    ).validate(instance)

def test_boot_manifest_validates():
    validate("GoogleNotebookBootManifest.schema.json", MANIFEST)
    receipt = validate_boot_manifest(MANIFEST)
    assert receipt["decision"] == "PASS"

def test_exact_five_cell_constellation_and_nb00_first():
    cells = MANIFEST["cells"]
    assert {c["cell_id"] for c in cells} == {"NB00", "NB10", "NB20", "NB30", "NB40"}
    assert next(c for c in cells if c["cell_id"] == "NB00")["initialization_order"] == 1
    assert sorted(c["initialization_order"] for c in cells) == [1, 2, 3, 4, 5]

def test_exact_six_boot_sources_are_required():
    sources = MANIFEST["boot_sources"]
    assert len(sources) == 6
    assert [s["slot"] for s in sources] == [1, 2, 3, 4, 5, 6]
    assert all(s["required"] is True for s in sources)

def test_capability_observations_validate_without_overclaim():
    for obs in MANIFEST["capability_observations"]:
        validate("GoogleCapabilityObservation.schema.json", obs)
        assert validate_capability_observation(obs)["decision"] == "PASS"
    create = next(x for x in MANIFEST["capability_observations"] if x["capability_id"] == "gemini.notebook.create.via_chatgpt")
    assert create["state"] == "UNAVAILABLE_IN_CURRENT_SURFACE"
    assert "Does not imply" in create["claim_boundary"]

def test_false_observed_capability_without_evidence_fails():
    bad = {
        "capability_id": "gemini.notebook.create",
        "surface": "test",
        "state": "OBSERVED_AVAILABLE",
        "evidence_class": "HOST_CAPABILITY_OBSERVATION",
        "evidence_refs": [],
        "observed_at": "2026-10-04",
        "claim_boundary": "test",
    }
    receipt = validate_capability_observation(bad)
    assert receipt["decision"] == "FAIL"
    assert "OBSERVED_AVAILABLE_REQUIRES_EVIDENCE" in receipt["reasons"]

def test_source_reported_feature_is_not_host_observation():
    sync = next(x for x in MANIFEST["capability_observations"] if x["capability_id"] == "gemini.notebook.drive.auto_sync")
    assert sync["state"] == "SOURCE_REPORTED_FEATURE"
    assert sync["evidence_class"] == "SOURCE_REPORTED"

def test_context_capsule_canary_passes():
    for capsule in BUNDLE["context_capsules"]:
        assert validate_context_capsule(capsule)["decision"] == "PASS"

def test_bridge_canaries_preserve_authority_ceiling():
    for bridge in BUNDLE["bridge_canaries"]:
        receipt = validate_bridge_capsule(bridge)
        assert receipt["decision"] == "PASS"
        for claim in bridge["claims"]:
            assert claim["source_authority_ceiling"] == claim["target_authority_ceiling"]

def test_bridge_authority_promotion_is_blocked():
    bad = json.loads(json.dumps(BUNDLE["bridge_canaries"][0]))
    bad["claims"][0]["target_authority_ceiling"] = "FORMAL"
    receipt = validate_bridge_capsule(bad)
    assert receipt["decision"] == "FAIL"
    assert "BRIDGE_TRANSPORT_CANNOT_PROMOTE_OR_REWRITE_AUTHORITY" in receipt["reasons"]

def prepared_receipt():
    return {
        "receipt_id": "boot:nb00:prepared",
        "cell_id": "NB00",
        "notebook_name": "CODEXSTATION Ω NEXT — NB00 — ORCHESTRATOR CONTROL TOWER",
        "status": "BOOT_PREPARED",
        "root_semantic_fingerprint": EXPECTED_FINGERPRINT,
        "core_sources_attached": False,
        "instruction_applied": False,
        "canaries": [
            {"canary_id": "T1_ROOT_RETRIEVAL", "critical": True, "status": "NOT_RUN", "detail": "live notebook not created"}
        ],
        "observed_capabilities": [],
        "evidence_refs": ["drive:14N4eyqgYIfCsWYQH2fyjAZugx6OYmjNoORZccynZaRk"],
        "authority_delta": "NONE",
        "observed_source_limit": None,
        "limitations": ["LIVE_NOTEBOOK_NOT_CREATED"],
    }

def live_pass_receipt():
    r = prepared_receipt()
    r.update({
        "receipt_id": "boot:nb00:live-pass",
        "status": "LIVE_BOOT_PASS",
        "core_sources_attached": True,
        "instruction_applied": True,
        "observed_source_limit": 300,
        "evidence_refs": ["google-notebook:nb00", "drive:boot-registry"],
        "observed_capabilities": ["source-citations", "drive-source-sync"],
        "canaries": [
            {"canary_id": "T1_ROOT_RETRIEVAL", "critical": True, "status": "PASS", "detail": "root and fingerprint correct"},
            {"canary_id": "T2_LINEAGE_NON_COLLAPSE", "critical": True, "status": "PASS", "detail": "lineages kept distinct"},
            {"canary_id": "T3_HIGHESTONE_AUTHORITY", "critical": True, "status": "PASS", "detail": "selection not authorization"},
            {"canary_id": "T4_HOST_CAPABILITY", "critical": True, "status": "PASS", "detail": "no broad permission inference"},
            {"canary_id": "T5_NOTEBOOK_CANON", "critical": True, "status": "PASS", "detail": "notebook output not canon"},
        ],
    })
    return r

def test_prepared_receipt_is_valid_but_not_live_pass():
    r = prepared_receipt()
    validate("NotebookLiveBootReceipt.schema.json", r)
    assert validate_live_boot_receipt(r)["decision"] == "PASS"
    assert r["status"] == "BOOT_PREPARED"

def test_live_pass_requires_every_critical_canary():
    r = live_pass_receipt()
    validate("NotebookLiveBootReceipt.schema.json", r)
    assert validate_live_boot_receipt(r)["decision"] == "PASS"
    bad = json.loads(json.dumps(r))
    bad["canaries"][1]["status"] = "FAIL"
    receipt = validate_live_boot_receipt(bad)
    assert receipt["decision"] == "FAIL"
    assert "CRITICAL_CANARY_NOT_PASS:T2_LINEAGE_NON_COLLAPSE" in receipt["reasons"]

def test_live_pass_requires_observed_source_limit():
    bad = live_pass_receipt()
    bad["observed_source_limit"] = None
    receipt = validate_live_boot_receipt(bad)
    assert receipt["decision"] == "FAIL"
    assert "LIVE_PASS_REQUIRES_OBSERVED_SOURCE_LIMIT" in receipt["reasons"]

def test_boot_cannot_create_authority_delta():
    bad = live_pass_receipt()
    bad["authority_delta"] = "FORMAL"
    receipt = validate_live_boot_receipt(bad)
    assert receipt["decision"] == "FAIL"
    assert "BOOT_CANNOT_CREATE_AUTHORITY_DELTA" in receipt["reasons"]

def test_root_fingerprint_mismatch_blocks_live_pass():
    bad = live_pass_receipt()
    bad["root_semantic_fingerprint"] = "0" * 64
    receipt = validate_live_boot_receipt(bad)
    assert receipt["decision"] == "FAIL"
    assert "ROOT_SEMANTIC_FINGERPRINT_MISMATCH" in receipt["reasons"]
