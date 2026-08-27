# 16 — Data Architecture

**Principle:** Postgres is the system of record for RE:WORK. SAP remains the enterprise system of record for workforce objects we did not copy as master.

**No Neo4j.** Adjacency tables + optional pgvector cover the graph we need. Neo4j would add ops cost without a query we cannot express in SQL for this prototype.

---

## 1. Relational model (minimum)

```
candidates
  id, display_name, location, work_modes[], languages[],
  sap_user_id null, created_at

candidate_evidence
  id, candidate_id, type, summary, source_ref, occurred_on,
  provenance, reliability, confidence, raw_uri null

skills
  id (text pk), label, description, sap_attribute_id null, embedding vector null

skill_edges
  from_id, to_id, rel, weight

candidate_skills
  id, candidate_id, skill_id, kind, proficiency, confidence,
  recency, context, sap_attribute_id null

candidate_skill_evidence
  candidate_skill_id, evidence_id

jobs
  id, title, raw_text, sap_requisition_id null, provenance, version

job_tasks
  id, job_id, text, on_site_likelihood, importance

job_task_skills
  job_task_id, skill_id, min_proficiency, importance

job_requirements
  id, job_id, text, class, review_tag, strength, why_relevant, why_proxy, confidence

role_outcomes
  id, job_id, text

capability_gaps
  id, run_id, skill_id null, requirement_id null, type, severity, notes, confidence

barrier_assessments
  id, run_id, requirement_id, counterfactual, recommendation, confidence, human_review_required

market_signals
  id, skill_id, window, demand_index, trend, opportunity_count, provenance, notes

learning_items
  id, title, hours, sap_learning_item_id null, source, provenance

learning_paths
  id, run_id, target_job_id, total_weeks, status, no_viable_path

learning_path_items
  path_id, learning_item_id, target_skill_id, why, start_prof, target_prof,
  exercise, proof_id, weeks, progress

proof_assessments
  id, skill_id, task_key, rubric_json, version

proof_results
  id, assessment_id, candidate_id, run_id, scores_json, total, result, evaluator, human_override

opportunities
  id, job_id, location, work_modes[], language, source, sap_opportunity_id null, provenance

match_recommendations
  id, run_id, opportunity_id, readiness_state, coverage, payload_json

recommendation_evidence
  recommendation_id, ref_type, ref_id

runs
  id, status, mode, state_json, parent_run_id, demo_scenario_id

human_reviews / decisions
  id, run_id, actor_id, actor_role, action, comment, patches_json, created_at

outcomes
  id, run_id, kind, payload_json  -- later: hired, completed_path, etc.

audit_events
  id, run_id, node, input_hash, output_json, confidence, latency_ms,
  model_id, prompt_version, error, fallback, created_at
```

Names can be snake_case in Postgres; this list is the conceptual minimum requested.

---

## 2. Graph model (in Postgres)

- Skill adjacency: `skill_edges`
- Person–skill–evidence: join tables
- Job–task–skill: join tables

No separate graph DB.

---

## 3. Vector model (optional, useful)

`skills.embedding` + pgvector for **alias / JD phrase → skill_id** candidates.  
Final skill assignment still must pass allowlist + agent validation.

Do **not** rank people with resume embeddings as the matcher.

---

## 4. Document blobs

Resumes: object storage or DB bytea for prototype. Parsed text stored with provenance. P0: paste text, skip file storage if time-constrained.

---

## 5. SAP sync

Tables hold **copies** with `sap_*_id` and `provenance`. Live adapter overwrites copies; never pretend copies are masters.

Direction P0: **read-only** from SAP (or simulated). Write-back: export JSON for humans, not OData upsert.

---

## 6. Why not Neo4j

Queries are bounded (one candidate, one job, tens of opportunities). SQL shortest-path of length 1–2 on `skill_edges` is enough. Neo4j would be “impressive” and unused — forbidden by the brief’s own anti-overengineering rule.
