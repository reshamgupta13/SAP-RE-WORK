# Judge Q&A

## Why is this not just an ATS?

ATS filters applications. RE:WORK diagnoses capability vs requirements, separates genuine gaps from eligibility proxies, generates evidence-backed pathways, simulates interventions, and requires human governance before action.

## Why isn't this SAP Opportunity Marketplace?

SAP lists opportunities. RE:WORK answers **under what conditions** a candidate can become viable, with proof-of-skill and employer readiness on both sides.

## Why isn't this SAP Learning?

SAP delivers learning catalogs. RE:WORK selects **minimum-effective** learning tied to diagnosed gaps and validates outcomes via proof-of-skill.

## Why isn't this just a skills graph?

Skills graphs store proficiency. RE:WORK adds evidence quality, diagnosis, counterfactuals, intervention simulation, and human review.

## What does RE:WORK uniquely add?

Evidence synthesis → capability diagnosis → counterfactuals → minimum intervention → proof → two-sided viability → explainability → human decision.

## Where is AI used?

Candidate intelligence and job decomposition (with deterministic `DEMO_FALLBACK`). Diagnosis, gaps, viability, and interventions are **rule-based engines** with structured outputs.

## Where is deterministic logic used?

Capability gap engine, diagnosis engine, counterfactual engine, pathway engine, proof rubric, viability engine, intervention simulator.

## Why human-in-the-loop?

No autonomous hire/reject. Low confidence, proxies, and interventions require HR decision. AI recommendation is preserved separately.

## How do you prevent bias?

No protected characteristics in scoring. Proxies flagged as **potential** eligibility barriers — never “bias confirmed.” Counterfactuals suggest alternatives; humans decide.

## How do you handle uncertainty?

Confidence labels (heuristic), `INSUFFICIENT_EVIDENCE`, `REQUIRES_HUMAN_REVIEW`, explicit assumptions on projections.

## How does SAP integrate?

Read-only adapter layer (`SAPProvider`). Simulated by default. Live only with verified OAuth + tenant URL. Mapper converts SAP → canonical domain.

## What if SAP is unavailable?

`SAP_MODE=SIMULATED` — demo continues with labeled fixtures. Health endpoint reports status.

## What if the LLM fails?

`DEMO_FALLBACK` uses fixture-based candidate/job intelligence. Full case still runs.

## How do you prove skill acquisition?

Structured proof-of-skill assessment with rubric; verified evidence updates capability; reassessment reuses diagnosis engine.

## How could this scale?

Case graph + event log + repository pattern; SAP read adapters per module; async pipeline execution.

## What would you build next?

Verified live SAP skills read, production persistence, expanded benchmark fixtures, outcome feedback loop.
