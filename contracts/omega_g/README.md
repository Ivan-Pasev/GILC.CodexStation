# CodexStation ΩG — MACHINE_CONTRACT_SLICE_01

Status: **working implementation evidence** for `v0.4.0-alpha.0`.

This slice converts the ΩG architecture into a finite machine-readable surface. The bundle contains ten named Draft 2020-12 schemas:

- `CanonicalOntologyRecord.schema.json`
- `NonCollapseRule.schema.json`
- `FrontierSnapshot.schema.json`
- `HighestOneSelection.schema.json`
- `OmniusMissionContract.schema.json`
- `HostCapabilityDescriptor.schema.json`
- `ClaimAuthorityReceipt.schema.json`
- `ExecutionReceipt.schema.json`
- `MigrationWitness.schema.json`
- `CanonAdmissionReceipt.schema.json`

It also carries the canonical ontology registry, anti-collapse rule registry, fail-closed semantic validators, and adversarial tests for authority inflation, host-capability hallucination, stale frontier use, provider-refusal promotion, migration without verified continuity, and evidence-free canon admission.

## Authority boundary

This implementation does **not** prove the open `T-ΩG-*` theorem targets. It does not close the parent ChatGPT-plugin runtime-regression gates, and it does not convert implementation PASS into formal or empirical PASS.

## Run

```bash
python -m pip install -e ".[dev]"
pytest -q tests/test_omega_g_machine_contract_slice_01.py
```
