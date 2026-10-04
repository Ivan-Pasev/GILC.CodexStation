import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from gilc_codex_station.omega_g.validator import (
    digest,
    validate_canon_admission,
    validate_claim_authority,
    validate_execution_receipt,
    validate_frontier,
    validate_highestone_selection,
    validate_host_capability,
    validate_migration_witness,
    validate_noncollapse,
)

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = json.loads(
    (ROOT / "contracts" / "omega_g" / "MACHINE_CONTRACT_SLICE_01.bundle.json").read_text(encoding="utf-8")
)
SCHEMAS = BUNDLE["schemas"]
REGISTRIES = BUNDLE["registries"]

H = "a" * 64
H2 = "b" * 64
H3 = "c" * 64
H4 = "d" * 64

ONTOLOGY = {
    "object_id": "omega-g.station",
    "object_type": "STATION",
    "lineage_id": "codexstation.omega",
    "version": "0.4.0-alpha.0",
    "scope": "OmegaG working branch",
    "authority_class": "CANONICAL",
    "evidence_class": "FORMAL_SPEC",
    "status": "WORKING",
    "source_refs": ["drive:omega-g:start"],
}

NONCOLLAPSE = {
    "rule_id": "NC-MODEL-REALITY",
    "left_type": "MODEL_SERVICE",
    "right_type": "REALITY",
    "disposition": "FORBID",
    "rationale": "Model is not reality",
    "symmetry": True,
    "authority_ceiling": "NONE",
    "allowed_witness_types": [],
    "source_refs": ["omega-g:ontology:v0.1"],
}

FRONTIER = {
    "fabric_state_id": "fabric:001",
    "lineage_id": "codexstation.omega",
    "candidate_ids": ["frontier:machine-contracts"],
    "open_obligations": ["omega-g-g4"],
    "contradictions": [],
    "evidence_state": {"class": "WORKING"},
    "capability_state": {"github": "AVAILABLE_WRITE"},
    "authority_state": {"repo": "writer"},
    "resource_constraints": [],
    "protected_invariants": ["CLAIM_NE_EVIDENCE", "HOST_NE_CANON"],
    "recovery_requirements": ["preserve-lineage"],
    "source_refs": ["drive:omega-g:handoff"],
    "freshness": "FRESH",
    "observed_at": "2026-10-04T07:00:00Z",
}

SELECTION = {
    "selection_id": "sel:001",
    "fabric_state_id": "fabric:001",
    "selected_frontier_id": "frontier:machine-contracts",
    "selection_class": "PRIMARY",
    "selection_rationale": "Close machine-contract gate before expansion",
    "priority_dimensions": ["blocking-obligation leverage", "closure leverage"],
    "blocking_obligations": [],
    "required_capabilities": ["github.write"],
    "required_authority": ["repo.writer"],
    "expected_closure_gain": 0.8,
    "expected_information_gain": 0.5,
    "risk_and_reversibility": "Reversible development branch commit",
    "termination_condition": "Schemas, validator and adversarial tests pass",
    "verification_plan": ["json-schema meta-validation", "pytest semantic suite"],
    "crystallization_target": "OmegaG G4/G6 evidence",
    "lineage_parent": "omega-g:v0.4.0-alpha.0",
    "witness_refs": ["drive:omega-g:handoff"],
    "uncertainties": [],
    "rejected_or_deferred_candidates": ["google-adapter-live-binding"],
    "next_recompute_trigger": "machine contract test receipt",
}

MISSION = {
    "mission_id": "mission:mc01",
    "selection_id": "sel:001",
    "objective": "Implement MACHINE_CONTRACT_SLICE_01",
    "scope": "OmegaG finite machine-contract surface",
    "success_conditions": ["schemas meta-validate", "semantic tests pass"],
    "stop_conditions": ["authority ambiguity", "schema/test failure"],
    "primary_path": {
        "target_gate": "OmegaG-G4",
        "steps": ["emit schemas", "emit validator", "run tests"],
        "termination_condition": "all tests pass",
        "reconciliation_requirement": "update Drive handoff",
    },
    "falsification_path": {
        "reason": "search for authority inflation",
        "target_gate": "OmegaG-G6",
        "steps": ["run negative fixtures"],
        "termination_condition": "all forbidden cases block",
        "reconciliation_requirement": "record failures or pass",
    },
    "alternative_path": None,
    "required_sources": ["omega-g start", "omega-g handoff", "theorematic spine", "ontology registry"],
    "required_tools": ["GitHub", "Google Drive"],
    "required_capabilities": ["github.write", "drive.write"],
    "required_authority": ["repo.writer", "drive.writer"],
    "execution_plan": ["branch from main", "commit machine contracts", "run tests"],
    "critique_plan": ["check overclaiming", "check host/canon separation"],
    "verification_plan": ["schema validation", "deterministic receipts", "adversarial suite"],
    "artifact_targets": ["schemas", "validator", "tests", "receipt"],
    "evidence_requirements": ["commit sha", "test counts", "validation receipt"],
    "state_update_targets": ["OmegaG handoff", "parent plugin handoff"],
    "continuation_output": "NEXT target after G4/G6",
    "human_approval_points": [],
    "risk_register": ["do not promote RC gates"],
    "unresolved_questions": [],
}

HOST = {
    "descriptor_id": "cap:github:write",
    "adapter_id": "github:connector",
    "provider": "GitHub",
    "surface": "repository contents",
    "account_scope": "Ivan-Pasev/GILC.CodexStation",
    "capability": "github.write",
    "state": "AVAILABLE_WRITE",
    "observed_evidence": ["connector:create_file available"],
    "freshness": "FRESH",
    "last_verified_at": "2026-10-04T07:00:00Z",
    "permission_model": "OAuth connector",
    "data_boundary": "selected repository",
    "export_paths": ["git"],
    "import_paths": ["git"],
    "quota_constraints": [],
    "retention_constraints": [],
    "privacy_constraints": [],
    "failure_modes": ["PERMISSION_DENIED", "NETWORK_ERROR"],
    "approval_requirements": [],
    "unknowns": [],
}

AUTH = {
    "receipt_id": "auth:001",
    "claim_id": "claim:machine-contracts",
    "transition_axis": "IMPLEMENTATION",
    "from_status": "SPECIFIED",
    "to_status": "TESTED",
    "decision": "ALLOW",
    "evidence_refs": ["test:omega-g:mc01"],
    "witness_refs": ["commit:placeholder"],
    "authority_source": "repository+test witness",
    "scope": "finite machine-contract implementation",
    "authority_ceiling": "EXECUTION",
    "reason": "Tested implementation evidence only",
    "semantic_authority_delta": "IMPLEMENTATION",
    "digest": None,
}

MIGRATION = {
    "witness_id": "mig:001",
    "station_identity": "codexstation.omega",
    "entity_roots": ["entity:root:1"],
    "source_adapter": "chatgpt:plugin",
    "target_adapter": "google:projection",
    "canonical_state_digest": H,
    "lineage_digest": H2,
    "provenance_digest": H3,
    "authority_map_digest": H4,
    "capability_rediscovery_required": True,
    "continuity_verified": True,
    "source_refs": ["drive:omega-g:handoff"],
    "residual_obligations": ["regression target adapter"],
}

CANON = {
    "receipt_id": "canon:001",
    "object_id": "omega-g:machine-contracts",
    "decision": "ADMIT",
    "source_state": "WORKING",
    "target_state": "CANDIDATE",
    "scope": "OmegaG machine contracts",
    "evidence_class": "IMPLEMENTATION_TEST",
    "authority_ceiling": "CANONICAL",
    "evidence_refs": ["test:mc01"],
    "witness_refs": ["commit:placeholder"],
    "residual_obligations": [],
    "lineage_parent": "omega-g:v0.4.0-alpha.0",
    "supersedes": [],
    "semantic_authority_delta": "CANONICAL",
    "target_canonical_digest": H,
}

EXECUTION_POLICY_REFUSAL = {
    "receipt_id": "exec:bad1",
    "mission_id": "mission:mc01",
    "action_id": "action:provider-refusal",
    "host_adapter": "provider:x",
    "capability_used": "model.generate",
    "authority_used": "permission:model",
    "input_digest": H,
    "prestate_digest": H2,
    "output_digest": H3,
    "poststate_digest": H4,
    "operation": "generate",
    "execution_status": "BLOCKED",
    "observed_effect": "Provider refused",
    "evidence_refs": ["provider:refusal:receipt"],
    "errors_or_refusals": ["policy refusal"],
    "failure_class": "POLICY_REFUSAL",
    "semantic_authority_delta": "EMPIRICAL",
    "reproducibility_notes": "",
}

VALID_INSTANCES = [
    ("CanonicalOntologyRecord.schema.json", ONTOLOGY),
    ("NonCollapseRule.schema.json", NONCOLLAPSE),
    ("FrontierSnapshot.schema.json", FRONTIER),
    ("HighestOneSelection.schema.json", SELECTION),
    ("OmniusMissionContract.schema.json", MISSION),
    ("HostCapabilityDescriptor.schema.json", HOST),
    ("ClaimAuthorityReceipt.schema.json", AUTH),
    ("MigrationWitness.schema.json", MIGRATION),
    ("CanonAdmissionReceipt.schema.json", CANON),
    ("ExecutionReceipt.schema.json", EXECUTION_POLICY_REFUSAL),
]

@pytest.mark.parametrize("schema_name", sorted(SCHEMAS))
def test_schema_meta_validation(schema_name):
    Draft202012Validator.check_schema(SCHEMAS[schema_name])

@pytest.mark.parametrize("schema_name,instance", VALID_INSTANCES)
def test_valid_instances(schema_name, instance):
    Draft202012Validator(SCHEMAS[schema_name], format_checker=FormatChecker()).validate(instance)

def test_ontology_registry_records_validate():
    v = Draft202012Validator(SCHEMAS["CanonicalOntologyRecord.schema.json"], format_checker=FormatChecker())
    for record in REGISTRIES["CanonicalOntologyRegistry.v0.1"]["records"]:
        v.validate(record)

def test_noncollapse_registry_rules_validate():
    v = Draft202012Validator(SCHEMAS["NonCollapseRule.schema.json"], format_checker=FormatChecker())
    for rule in REGISTRIES["NonCollapseRules.v0.1"]["rules"]:
        v.validate(rule)

def test_forbidden_model_reality_collapse_blocks():
    receipt = validate_noncollapse("MODEL_SERVICE", "REALITY", [NONCOLLAPSE])
    assert receipt["decision"] == "BLOCK"

def test_same_label_requires_witness():
    rules = REGISTRIES["NonCollapseRules.v0.1"]["rules"]
    assert validate_noncollapse("SAME_LABEL", "SAME_LINEAGE", rules)["decision"] == "BLOCK"
    assert validate_noncollapse("SAME_LABEL", "SAME_LINEAGE", rules, "LINEAGE_EQUIVALENCE_WITNESS")["decision"] == "ALLOW"

def test_host_capability_requires_fresh_observation():
    assert validate_host_capability(HOST)["decision"] == "ALLOW"
    bad = {**HOST, "descriptor_id": "cap:bad", "observed_evidence": [], "freshness": "UNKNOWN", "state": "AVAILABLE_EXECUTE"}
    receipt = validate_host_capability(bad)
    assert receipt["decision"] == "BLOCK"
    assert "CAPABILITY_STATE_NOT_FRESH" in receipt["reasons"]
    assert "AVAILABLE_CAPABILITY_REQUIRES_OBSERVED_EVIDENCE" in receipt["reasons"]

def test_stale_frontier_blocks_selection():
    stale = {**FRONTIER, "fabric_state_id": "fabric:stale", "freshness": "STALE"}
    assert validate_frontier(stale)["decision"] == "BLOCK"
    receipt = validate_highestone_selection(SELECTION, stale)
    assert receipt["decision"] == "BLOCK"
    assert "SOURCE_FRONTIER_NOT_ADMISSIBLE" in receipt["reasons"]

def test_highestone_selection_is_bounded_and_in_snapshot():
    assert validate_highestone_selection(SELECTION, FRONTIER)["decision"] == "ALLOW"

def test_authority_inflation_blocks_without_evidence_and_witness():
    bad = {
        **AUTH,
        "receipt_id": "auth:bad",
        "transition_axis": "FORMAL",
        "from_status": "STATED",
        "to_status": "PROVED",
        "evidence_refs": [],
        "witness_refs": [],
        "authority_source": None,
        "authority_ceiling": "FORMAL",
        "reason": "mere orchestration",
        "semantic_authority_delta": "FORMAL",
    }
    receipt = validate_claim_authority(bad)
    assert receipt["decision"] == "BLOCK"
    assert "ALLOW_REQUIRES_AUTHORITY_SOURCE" in receipt["reasons"]
    assert "ALLOW_REQUIRES_EVIDENCE" in receipt["reasons"]
    assert "ALLOW_REQUIRES_WITNESS" in receipt["reasons"]

def test_witnessed_implementation_transition_allows():
    assert validate_claim_authority(AUTH)["decision"] == "ALLOW"

def test_provider_refusal_does_not_become_empirical_refutation():
    receipt = validate_execution_receipt(EXECUTION_POLICY_REFUSAL)
    assert receipt["decision"] == "BLOCK"
    assert "PROVIDER_REFUSAL_CANNOT_CREATE_EPISTEMIC_OR_CANONICAL_DELTA" in receipt["reasons"]

def test_migration_requires_verified_continuity_and_capability_rediscovery():
    assert validate_migration_witness(MIGRATION)["decision"] == "ALLOW"
    bad = {**MIGRATION, "witness_id": "mig:bad", "continuity_verified": False}
    receipt = validate_migration_witness(bad)
    assert receipt["decision"] == "BLOCK"
    assert "CONTINUITY_NOT_VERIFIED" in receipt["reasons"]

def test_canon_admission_requires_evidence_witness_and_digest():
    assert validate_canon_admission(CANON)["decision"] == "ALLOW"
    bad = {**CANON, "receipt_id": "canon:bad", "evidence_refs": [], "witness_refs": [], "target_canonical_digest": None}
    receipt = validate_canon_admission(bad)
    assert receipt["decision"] == "BLOCK"
    assert "ADMISSION_REQUIRES_EVIDENCE" in receipt["reasons"]
    assert "ADMISSION_REQUIRES_WITNESS" in receipt["reasons"]
    assert "ADMISSION_REQUIRES_TARGET_DIGEST" in receipt["reasons"]

def test_semantic_receipts_are_deterministic():
    a = validate_host_capability(HOST)
    b = validate_host_capability(HOST)
    assert a == b
    assert a["receipt_digest"] == digest({k: v for k, v in a.items() if k != "receipt_digest"})
