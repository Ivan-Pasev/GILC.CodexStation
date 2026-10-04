# CodexStation Ω NEXT — DISTRIBUTION_COMPILER_SLICE_01

This slice binds the new Google Drive canonical R&D root to a provider-independent machine surface.

## What it implements

- CanonicalRootManifest
- SourceLineageRegistry
- SkillSpindleRecord
- SkillIndex
- DistributionProfile
- NotebookCellProfile
- ContextCapsule
- BridgeCapsule
- DistributionConformanceReceipt
- deterministic shared semantic fingerprint
- Google / Gemini Notebook compiled profile
- OpenAI / ChatGPT + Codex compiled profile
- fail-closed semantic conformance checks
- source-lineage and skill/capability adversarial checks

## Governing rule

`PLATFORM_PROFILE != CANON_FORK`

The two compiled distributions MUST bind the same shared semantic fingerprint and four-source control pack.

## Non-claims

This slice does not create live Gemini Notebook objects, does not infer unavailable host capabilities, does not close parent ChatGPT-plugin runtime regression debt, and does not promote scientific/formal claims.

## Test

```bash
python -m pip install -e ".[dev]"
pytest -q tests/test_omega_next_distribution_compiler_slice_01.py
```
