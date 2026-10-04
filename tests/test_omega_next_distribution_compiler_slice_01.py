import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from gilc_codex_station.omega_next.compiler import (
    compile_distribution,
    resolve_skills,
    semantic_fingerprint,
    validate_bridge_capsule,
    validate_context_capsule,
    validate_distribution_conformance,
    validate_lineage_registry,
    validate_skill_record,
)

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = json.loads(
    (ROOT / "contracts" / "omega_next" / "DISTRIBUTION_COMPILER_SLICE_01.bundle.json").read_text(encoding="utf-8")
)
SCHEMAS = BUNDLE["schemas"]
ROOT_MANIFEST = BUNDLE["canonical_root_manifest"]
LINEAGES = BUNDLE["source_lineage_registry"]
SKILLS = BUNDLE["skill_index"]
CELLS = BUNDLE["notebook_cells"]
GOOGLE = json.loads(
    (ROOT / "contracts" / "omega_next" / "compiled" / "google_gemini_notebook.profile.json").read_text(encoding="utf-8")
)
OPENAI = json.loads(
    (ROOT / "contracts" / "omega_next" / "compiled" / "openai_chatgpt_codex.profile.json").read_text(encoding="utf-8")
)

@pytest.mark.parametrize("schema_name", sorted(SCHEMAS))
def test_schema_meta_validation(schema_name):
    Draft202012Validator.check_schema(SCHEMAS[schema_name])

def validate(schema_name, instance):
    Draft202012Validator(SCHEMAS[schema_name], format_checker=FormatChecker()).validate(instance)

def test_root_manifest_validates():
    validate("CanonicalRootManifest.schema.json", ROOT_MANIFEST)

def test_lineage_registry_validates_and_has_one_active_parent():
    validate("SourceLineageRegistry.schema.json", LINEAGES)
    receipt = validate_lineage_registry(LINEAGES)
    assert receipt["decision"] == "PASS"
    assert sum(1 for x in LINEAGES["records"] if x["active_parent"]) == 1

def test_skill_index_and_seed_skills_validate():
    validate("SkillIndex.schema.json", SKILLS)
    skill_schema = SCHEMAS["SkillSpindleRecord.schema.json"]
    v = Draft202012Validator(skill_schema, format_checker=FormatChecker())
    for skill in SKILLS["skills"]:
        v.validate(skill)
        receipt = validate_skill_record(skill, observed_capabilities=[])
        assert receipt["decision"] == "PASS"
        assert receipt["executable_now"] is True

def test_notebook_cell_profiles_validate_and_share_four_source_boot_pack():
    v = Draft202012Validator(SCHEMAS["NotebookCellProfile.schema.json"], format_checker=FormatChecker())
    expected = list(ROOT_MANIFEST["control_documents"].values())
    assert {c["cell_id"] for c in CELLS} == {"NB00", "NB10", "NB20", "NB30", "NB40"}
    for cell in CELLS:
        v.validate(cell)
        assert cell["required_control_docs"] == expected
        assert cell["bridge_policy"] == "VISIBLE_DRIVE_BRIDGE_ONLY"

def test_compiled_profiles_validate():
    validate("DistributionProfile.schema.json", GOOGLE)
    validate("DistributionProfile.schema.json", OPENAI)

def test_both_profiles_bind_same_semantic_fingerprint():
    expected = semantic_fingerprint(ROOT_MANIFEST)
    assert GOOGLE["root_semantic_fingerprint"] == expected
    assert OPENAI["root_semantic_fingerprint"] == expected
    assert GOOGLE["root_semantic_fingerprint"] == OPENAI["root_semantic_fingerprint"]

def test_google_conformance_passes():
    receipt = validate_distribution_conformance(ROOT_MANIFEST, GOOGLE)
    validate("DistributionConformanceReceipt.schema.json", receipt)
    assert receipt["decision"] == "PASS"
    assert receipt["authority_delta"] == "NONE"

def test_openai_conformance_passes():
    receipt = validate_distribution_conformance(ROOT_MANIFEST, OPENAI)
    validate("DistributionConformanceReceipt.schema.json", receipt)
    assert receipt["decision"] == "PASS"
    assert receipt["authority_delta"] == "NONE"

def test_semantic_override_is_rejected_by_compiler():
    spec = {
        "profile_id": "bad.profile",
        "provider": "GOOGLE",
        "version": "0.1",
        "surfaces": ["test"],
        "limitations": ["test limitation"],
        "compiled_views": ["test"],
        "semantic_overrides": ["SOURCE == AUTHORITY"],
    }
    with pytest.raises(ValueError, match="semantic overrides"):
        compile_distribution(ROOT_MANIFEST, spec)

def test_distribution_without_limitations_is_rejected():
    spec = {
        "profile_id": "bad.profile",
        "provider": "GOOGLE",
        "version": "0.1",
        "surfaces": ["test"],
        "limitations": [],
        "compiled_views": ["test"],
        "semantic_overrides": [],
    }
    with pytest.raises(ValueError, match="limitations"):
        compile_distribution(ROOT_MANIFEST, spec)

def test_profile_cannot_change_inherited_invariants_without_failing_conformance():
    bad = dict(GOOGLE)
    bad["inherited_invariants"] = GOOGLE["inherited_invariants"][:-1]
    receipt = validate_distribution_conformance(ROOT_MANIFEST, bad)
    assert receipt["decision"] == "FAIL"
    assert any(x["check"] == "INVARIANT_INHERITANCE" and x["status"] == "FAIL" for x in receipt["checks"])

def test_profile_cannot_bind_different_root_without_failing_conformance():
    bad = dict(OPENAI)
    bad["root_id"] = "drive:wrong"
    receipt = validate_distribution_conformance(ROOT_MANIFEST, bad)
    assert receipt["decision"] == "FAIL"
    assert any(x["check"] == "ROOT_BINDING" and x["status"] == "FAIL" for x in receipt["checks"])

def test_same_label_different_lineage_requires_distinct_merge_policy():
    bad = json.loads(json.dumps(LINEAGES))
    clone = dict(bad["records"][1])
    clone["lineage_id"] = "codexstation.omega.g.clone"
    clone["label"] = bad["records"][1]["label"]
    clone["merge_policy"] = "ACTIVE_ROOT"
    clone["active_parent"] = False
    bad["records"].append(clone)
    receipt = validate_lineage_registry(bad)
    assert receipt["decision"] == "FAIL"
    assert any(x.startswith("SAME_LABEL_REQUIRES_DISTINCT_MERGE_POLICY") for x in receipt["reasons"])

def test_multiple_active_parents_fail_lineage_registry():
    bad = json.loads(json.dumps(LINEAGES))
    bad["records"][1]["active_parent"] = True
    receipt = validate_lineage_registry(bad)
    assert receipt["decision"] == "FAIL"
    assert "EXACTLY_ONE_ACTIVE_PARENT_REQUIRED" in receipt["reasons"]

def test_declared_skill_binding_does_not_claim_observed_capability():
    skill = dict(SKILLS["skills"][0])
    skill["skill_uri"] = "cs://skill/test/declared@1"
    skill["host_bindings"] = [{
        "provider": "GOOGLE",
        "capability": "gemini.notebook.create",
        "binding_state": "DECLARED_ONLY",
        "observed_evidence": [],
    }]
    skill["required_capabilities"] = ["gemini.notebook.create"]
    receipt = validate_skill_record(skill, observed_capabilities=[])
    assert receipt["decision"] == "PASS"
    assert receipt["executable_now"] is False

def test_false_observed_skill_capability_fails_closed():
    skill = dict(SKILLS["skills"][0])
    skill["skill_uri"] = "cs://skill/test/fake-observed@1"
    skill["host_bindings"] = [{
        "provider": "GOOGLE",
        "capability": "gemini.notebook.create",
        "binding_state": "OBSERVED_AVAILABLE",
        "observed_evidence": [],
    }]
    skill["required_capabilities"] = ["gemini.notebook.create"]
    receipt = validate_skill_record(skill, observed_capabilities=[])
    assert receipt["decision"] == "FAIL"
    assert "CAPABILITY_NOT_OBSERVED:gemini.notebook.create" in receipt["reasons"]
    assert "OBSERVED_CAPABILITY_REQUIRES_EVIDENCE:gemini.notebook.create" in receipt["reasons"]

def test_skill_router_is_intent_bounded():
    matches = resolve_skills(SKILLS, ["evidence"], observed_capabilities=[])
    assert matches
    assert all("evidence" in next(s for s in SKILLS["skills"] if s["skill_uri"] == m["skill_uri"])["retrieval_tags"] for m in matches)

def test_context_capsule_requires_provenance():
    capsule = {
        "capsule_id": "capsule:test",
        "lineage_id": "codexstation.omega.next",
        "title": "Test",
        "purpose": "test",
        "scope": "test",
        "authority_ceiling": "METHOD",
        "definitions": [],
        "current_state": ["working"],
        "invariants": ["SOURCE != AUTHORITY"],
        "claims": [],
        "open_gates": [],
        "negative_results": [],
        "source_refs": ["drive:test"],
        "freshness": "FRESH",
    }
    validate("ContextCapsule.schema.json", capsule)
    assert validate_context_capsule(capsule)["decision"] == "PASS"
    bad = dict(capsule)
    bad["source_refs"] = []
    assert validate_context_capsule(bad)["decision"] == "FAIL"

def test_bridge_transport_cannot_promote_authority():
    bridge = {
        "bridge_id": "bridge:nb10-nb00",
        "source_cell": "NB10",
        "target_cell": "NB00",
        "mission_id": "mission:test",
        "lineage_id": "codexstation.omega.next",
        "claims": [{
            "claim": "candidate result",
            "evidence_class": "MODEL_DERIVED",
            "source_authority_ceiling": "METHOD",
            "target_authority_ceiling": "METHOD",
            "source_refs": ["drive:test"],
        }],
        "uncertainties": ["unverified"],
        "open_obligations": ["verify"],
        "artifacts": [],
        "recommended_delta": "review only",
        "source_refs": ["drive:test"],
    }
    validate("BridgeCapsule.schema.json", bridge)
    assert validate_bridge_capsule(bridge)["decision"] == "PASS"
    bad = json.loads(json.dumps(bridge))
    bad["claims"][0]["target_authority_ceiling"] = "FORMAL"
    receipt = validate_bridge_capsule(bad)
    assert receipt["decision"] == "FAIL"
    assert "BRIDGE_TRANSPORT_CANNOT_PROMOTE_OR_REWRITE_AUTHORITY" in receipt["reasons"]

def test_compiler_is_deterministic_for_same_spec():
    spec = {
        "profile_id": "omega-next.test",
        "provider": "OPENAI",
        "version": "0.1",
        "surfaces": ["surface"],
        "limitations": ["limitation"],
        "host_adapters": ["adapter"],
        "compiled_views": ["view"],
        "semantic_overrides": [],
    }
    assert compile_distribution(ROOT_MANIFEST, spec) == compile_distribution(ROOT_MANIFEST, spec)
