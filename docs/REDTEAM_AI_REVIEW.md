# Red Team — AI / Agent Review

**Auditor:** AI Engineer persona  
**Verdict:** PASS — defensible AI labeling

## Component classification

| Component | Classification | Engine mode shown |
|-----------|----------------|-------------------|
| Candidate Intelligence Agent | LLM (optional) / DEMO_FALLBACK | `DEMO_FALLBACK` in demo |
| Job Decomposition Agent | LLM (optional) / DEMO_FALLBACK | `DEMO_FALLBACK` in demo |
| Diagnosis Service | DETERMINISTIC BUSINESS LOGIC | `DETERMINISTIC_ENGINE` |
| Capability Gap Engine | DETERMINISTIC BUSINESS LOGIC | — |
| Counterfactual Engine | DETERMINISTIC BUSINESS LOGIC | — |
| Pathway Engine | DETERMINISTIC BUSINESS LOGIC + SAP_SIMULATED | — |
| Proof-of-Skill Engine | DETERMINISTIC BUSINESS LOGIC | Rubric evaluator |
| Market Intelligence | DATA TRANSFORMATION (synthetic fixtures) | `SYNTHETIC` |
| Opportunity Viability | DETERMINISTIC BUSINESS LOGIC | — |
| Employer Readiness | DETERMINISTIC BUSINESS LOGIC | — |
| Intervention Simulator | DETERMINISTIC BUSINESS LOGIC | `SIMULATED PROJECTION` |
| Explainability Service | DATA TRANSFORMATION | Structured reports |
| Human Review | GOVERNANCE | Separate from AI |
| LangGraph orchestrator | ORCHESTRATION (not AI) | Audit per node |

## What is actually "agentic"

1. **Candidate Intelligence** — extracts capabilities from evidence (LLM or fixture fallback)
2. **Job Decomposition** — decomposes role into tasks/requirements (LLM or fixture fallback)

## What is NOT agentic (but critical)

Diagnosis, pathway, proof, viability, intervention — deterministic engines with schema-validated outputs.

## Mislabeling risks

| Risk | Finding |
|------|---------|
| Calling diagnosis "AI" | MITIGATED — labeled engine in orchestrator |
| Hiding DEMO_FALLBACK | MITIGATED — shown in Control Room header |
| LLM chain-of-thought exposed | PASS — not stored in export |

## LLM failure behavior

`DeterministicFallbackProvider` catches LLM errors → fixture-based structured output. Case completes.

## Defensibility statement

"Agents discover and decompose. Deterministic engines govern, validate, and simulate. Humans decide."
