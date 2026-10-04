# CodexStation Ω Public — architecture blueprint

## 1. Architectural position

```text
PRIVATE Ω NEXT DRIVE CANON
        |
        | publication compiler
        v
PUBLIC OMEGA REPOSITORY
        |
        +--------------------+--------------------+
        |                    |                    |
        v                    v                    v
CHATGPT PLUGIN          GEMINI NOTEBOOK      PUBLIC RESEARCH/
DISTRIBUTION            DISTRIBUTION         ENGINEERING ANCHORS
```

The public repository is a **compiled constitutional/publication layer**. The private Google Drive tree remains the R&D control plane.

### Identity law

```text
DRIVE_CANON != PUBLIC_REPO != PLUGIN_DIST != NOTEBOOK_DIST
```

They can be semantically conformant without being identical objects.

## 2. Why dense files

The project already has evidence that many tiny files create retrieval drift, duplicated semantics and source-slot pressure. Dense files give:

- fewer attachment operations;
- fewer cross-file contradictions;
- easier release fingerprinting;
- better Notebook source-budget use;
- simpler public browsing;
- simpler publication witnesses;
- lower synchronization complexity.

The counter-risk is oversized context. Therefore the build system should maintain **one logical carrier** but permit platform-specific physical sharding.

```text
LOGICAL_CARRIER == SAME_SEMANTICS
PHYSICAL_SHARDING != CANON_FORK
```

## 3. Proposed logical corpus

### 3.1 OMEGA_CORE

Contains only the cross-domain operating substrate.

Required semantic namespaces:

```text
CS.IDENTITY
CS.LINEAGE
CS.AUTHORITY
CS.CAPABILITY
CS.MEMORY
CS.STATE
CS.EVIDENCE
CS.CLAIM
CS.FRONTIER
CS.MISSION
CS.EXECUTION
CS.RECEIPT
CS.RELEASE
CS.MIGRATION
```

It binds but does not collapse:

```text
KBI
HIGHESTONE
OMNIUS
DFT
CRYSTAL
CODEXSTATION
HOST_ADAPTER
```

### 3.2 OMEGA_CRYSTAL

This is the large semantic object the project has repeatedly approached through MLCO RC0.37, Crystal P65, Ω-CSA, Ω101 and ΩG.

It should contain typed sections for:

- canonical ontology;
- grammar and relation types;
- non-collapse registry;
- theorem/evidence semantics;
- formal status calculus;
- research/discovery/verification method;
- engineering and agentic-systems method;
- source/provenance semantics;
- continuity/reinstantiation semantics;
- effect/receipt semantics;
- public/private boundary semantics;
- adversarial patterns;
- negative results;
- open gates.

Every major object should expose:

```text
id
definition
scope
lineage
status
authority_ceiling
source_refs
dependencies
non_identity_with
failure_modes
supersedes
version
```

### 3.3 OMEGA_SKILL_SPINDLE

A skill is a portable method object, not an agent personality.

```text
SKILL = (
  intent,
  accepts,
  preconditions,
  method,
  emits,
  guards,
  evidence_requirements,
  required_capabilities,
  host_bindings,
  authority_ceiling,
  freshness,
  tests,
  failure_modes
)
```

The public spindle should include only methods that are either provider-independent or have clearly typed adapter bindings.

### 3.4 OMEGA_THEOREMATIC_SPINE

Use four status families:

```text
DEFINITION
DERIVED_LAW
FORMAL_THEOREM
THEOREM_TARGET
FINITE_MACHINE_EVIDENCE
EMPIRICAL_EVIDENCE
```

Never reduce these to one scalar maturity score.

High-value public theorem targets include:

- no free authority/status upgrade by transport;
- no orchestration-based authority escalation;
- provenance conservation under semantic transport;
- no silent identity substitution;
- substrate-independent station identity under explicit invariants;
- migration/reinstantiation sufficiency;
- witnessed cross-level promotion;
- host failure non-epistemic mutation;
- bounded progress under explicit assumptions.

### 3.5 OMEGA_PUBLIC_ANCHORS

Every public anchor is typed:

```text
REPOSITORY
PAPER
STANDARD
DATASET
EXPERIMENT
SOFTWARE_RELEASE
PROOF_ARTIFACT
BENCHMARK
INSTITUTIONAL_SOURCE
```

Each entry has:
URI, title, owner, date, relevance, evidence class, and exact claim boundary.

## 4. Public repository should not become the 66 MB plugin dump

The current private plugin demonstrates that large archives are technically workable, but the public repo should remove duplicate provider releases and bundled binaries.

The public corpus should store **one semantic copy**.

Provider builds can generate duplicates when required.

## 5. Suggested repository tree

```text
/
  README.md
  AGENTS.md
  MANIFEST.json

  canon/
    OMEGA_CORE.md
    OMEGA_CRYSTAL.md
    OMEGA_SKILL_SPINDLE.md
    OMEGA_THEOREMATIC_SPINE.md
    OMEGA_PUBLIC_ANCHORS.md

  schemas/
    *.schema.json

  runtime/
    reference implementation + validators

  dist/
    chatgpt/
    gemini/
```

The logical corpus remains five dense Markdown carriers even if the repository contains validators and generated distribution artifacts.

## 6. Release compilation

```text
CANON_FILES
-> NORMALIZE
-> WORD/TOKEN COUNT
-> LINK/ANCHOR VALIDATE
-> SECRET SCAN
-> CLAIM-LINT
-> SCHEMA VALIDATE
-> SEMANTIC FINGERPRINT
-> PLATFORM COMPILE
-> PLATFORM TEST
-> RELEASE MANIFEST
```

The same semantic fingerprint must be embedded in both ChatGPT and Gemini distributions.

## 7. Public/private policy

The public repo should maximize reproducibility while minimizing accidental IP leakage.

Public by default:

- constitutional primitives;
- schemas;
- reference implementation;
- evidence methodology;
- public repo links;
- published papers;
- public datasets;
- reproducible tests.

Private until explicitly promoted:

- unpublished hypotheses;
- sensitive institutional material;
- private credentials;
- private user data;
- unreleased partner data;
- contractual/confidential material;
- internal strategic dossiers.

## 8. Capability claim discipline

The public repository may describe adapters for systems such as ChatGPT, Codex, Gemini Notebook and Google Drive.

It may only mark a capability as observed when a receipt exists.

```text
DOCUMENTED_FEATURE != OBSERVED_ACCOUNT_CAPABILITY
OBSERVED_CAPABILITY != AUTHORIZATION
AUTHORIZATION != SUCCESSFUL_EFFECT
```

## 9. AGI/ASI positioning

The repository should not market itself by asserting that it has already achieved AGI or ASI.

A stronger public position is:

> CodexStation Ω is a provider-independent cybernetic architecture for persistent, evidence-governed, corrigible, tool-using cognitive systems. It is designed to test and operationalize capabilities often associated with advanced general-purpose AI while keeping identity, authority, provenance, verification and human control explicit.

That framing is stronger scientifically because it is testable.

## 10. Evolution rule

Each iteration should increase **semantic density and evidence quality**, not merely file size.

```text
NEXT =
  HARVEST
  -> DEDUP
  -> TYPE
  -> VERIFY
  -> INTEGRATE
  -> PUBLICATION_FILTER
  -> COMPILE
  -> TEST
  -> RELEASE
```
