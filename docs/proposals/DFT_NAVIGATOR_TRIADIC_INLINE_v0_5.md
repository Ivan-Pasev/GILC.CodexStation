# DFT Navigator Ω · Triadic Inline Motion Constitution (Draft v0.5)

**Status:** proposal for review, not an installed CodexStation kernel or canonical DFT release.

## Default three-layer ChatGPT response

1. Substantive evidence-bound answer, then **2–4 numbered semantic action pills** (1 first is the best admissible action).
2. Nearly always present **one-row motion strip**: `↑ ASCEND | ◎ STABILIZE | ↓ DESCEND`.
3. Optional **descriptor pills** for action meaning, source provenance, evidence and gate status. Console/HUD opens only on explicit `Navigator Console`.

Mobile should remain compact, with wrap-friendly pill controls and meaningful non-interactive text fallback. Clicking uses a host new-user-turn action; it does not itself execute/authorize a mutation.

## Typed motion frame
`N=(focus,lineage,axis,level,evidence,sources,open_gates,above?,below?,menu_id)`

Axis is an explicit choice from `SEMANTIC_ABSTRACTION`, `REALIZATION_DEPTH`, `RESEARCH_SCOPE`, `PHYSICAL_SCALE`, `ORDINAL_STAGE`. These are independent meanings; no universal numeric height/rank is inferred.

- `ASCEND_VIEW`: explore grounded governing principles/invariants via typed `ABSTRACTS` edge; absent edge, propose search rather than assert superior object.
- `DESCEND_VIEW`: grounded realization (example/model/specification/test/experiment/implementation) via `REALIZES`; absent edge, propose search.
- `STABILIZE_VIEW`: same-level definitions/evidence/negative-results/claim-gate/provenance audit, no implicit gate closure.
- Scope moves use `EXPANDS_SCOPE/NARROWS_SCOPE`; physical scale requires `SCALE_BRIDGE`; ordinal stage demands specifically justified successor/predecessor relation. Cross-lineage moves require separately sourced typed bindings.

## DFT grounding

The UI contract is informed by DFT 2.0 frozen candidate `K*=(X,Ty,rho,T,I,tau,O,boundary)`, **without asserting a new DFT theorem**. Respect ATI–DFT architectural separation: ATI vertical realizations/scopes; DFT horizontal composition/evidence. All DFT 2.0 scientific status and CodexStation plugin RGT gates remain unchanged.

### Source anchors
- [DFT 2.0 canonical START HERE](https://docs.google.com/document/d/1ZB75URP14IPMvbO8pBDLNKkFbyD-LlzYQY52p6K-7Dw/edit)
- [DFT 2.0 Master Monograph](https://docs.google.com/document/d/1_s6axcN1OxbS1iCX3adOn_D0kUtkEvGcX31UU63ODck/edit)
- [DFT claim/evidence ledger](https://docs.google.com/document/d/1rHJnuJPQYCtPo1N7SoQ1-bBc5DVdy5_AX5UN_i9Nveg/edit)
- [ATI–DFT START HERE](https://docs.google.com/document/d/1jguN1jpcVpsYWBHXWbNDDwwYnrXk7sX46IBFixZJt-Q/edit)

## Authority guards

`VIEW_ASCENT != CANONICAL_PROMOTION`; `STABILIZE != SCIENTIFIC_PASS`; `DESCENT != PHYSICAL_VALIDATION`; `SCOPE != SCALE != ORDINAL_STAGE`; `MISSING_EDGE -> SEARCH_ONLY`; `ONE_TAP != HOST_EXECUTION`; `SAME_LABEL != SAME_LINEAGE`; `NAV_CONSOLE_EXPLICIT_OPT_IN`.

**Validation in local standalone v0.5 package:** 40 tests PASS (19 inherited + 21 added), pure Python source. This PR adds the review specification only, not the installed skill or current-release regression evidence.