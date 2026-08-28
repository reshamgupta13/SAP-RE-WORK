# Final AI Agent Architecture

## Core agents (LLM + fallback)

1. **Candidate Intelligence** — evidence → capability profile
2. **Job Decomposition** — role → tasks, capabilities, requirements

## Deterministic engines (not agents)

Diagnosis, Counterfactual, Pathway, Proof, Reassessment, Market, Viability, Employer Readiness, Intervention, Explainability

## Orchestrator

LangGraph coordinates all nodes with audit events.

## Engine labels (Control Room)

| Node | Label |
|------|-------|
| Candidate Intelligence | LLM / DEMO_FALLBACK |
| Job Decomposition | LLM / DEMO_FALLBACK |
| Diagnosis | DETERMINISTIC_ENGINE |
| Pathway | DETERMINISTIC_ENGINE + SAP_SIMULATED |
| Proof | DETERMINISTIC_ENGINE |
| Market | SYNTHETIC |

## Contract

Every agent output: INPUT sources, OUTPUT summary, confidence, evidence count, source mode, duration.

Humans decide — agents recommend.
