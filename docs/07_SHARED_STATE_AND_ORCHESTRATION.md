# 07 — Shared State and Orchestration

**Choice:** LangGraph (or equivalent explicit state machine).  
**Anti-pattern:** Independent chatbots with copy-pasted context.

---

## 1. Canonical state object

One JSON document per `run_id`. Agents read/write slices. Unknown keys are rejected.

```json
{
  "run_id": "uuid",
  "status": "created|running|awaiting_human|completed|failed|cancelled",
  "mode": "live|demo",
  "provenance_policy": "strict",
  "actor": {"id": "", "role": "candidate|hr|system"},

  "sap_context": {
    "employee": null,
    "growth_portfolio": null,
    "learning_history": null,
    "requisition": null,
    "provenance": "SIMULATED",
    "fetched_at": null
  },

  "candidate_profile": null,
  "job_profile": null,
  "skill_graph": { "nodes": [], "edges": [] },
  "evidence_set": [],
  "capability_assessment": null,
  "requirement_analysis": null,
  "barrier_assessment": null,
  "capability_gaps": [],
  "market_signals": [],
  "learning_path": null,
  "proof_of_skill": null,
  "opportunity_set": [],
  "recommendations": [],
  "explainability": null,
  "bias_audit": null,
  "human_decision": null,
  "outcome": null,

  "confidence": {
    "discover": null,
    "decompose": null,
    "diagnose": null,
    "pathway": null,
    "match": null,
    "inherited": null
  },

  "errors": [],
  "audit_event_ids": []
}
```

`skill_graph` is the working copy of capabilities + transfer edges. Persisted also relationally (see `16_DATA_ARCHITECTURE.md`).

---

## 2. State transitions

```
created
  -> load_context
  -> discover
  -> decompose          (decompose may run parallel to discover)
  -> diagnose           (requires both)
  -> pathway
  -> match
  -> explain
  -> bias_snapshot
  -> awaiting_human
  -> completed | (modify -> diagnose or match)

failed from any node after retries
cancelled by user
```

**Parallelism:** `discover` and `decompose` are independent. Join at `diagnose`.

**Re-entry:** If HR edits `requirement_analysis`, invalidate `barrier_assessment` onward and resume at `diagnose`.

**Proof side-path:** `awaiting_human` or `completed` can spawn `proof_run` which patches `capability_assessment` and may re-enter at `diagnose` or `match` only (not full rediscovery unless evidence is new documents).

---

## 3. Handoffs

| From | To | Payload contract | Validation |
|---|---|---|---|
| load_context | discover, decompose | sap_context + raw docs + job raw | provenance enum; ids present |
| discover | diagnose | capability_assessment, evidence_set | each capability has skill_id in catalog |
| decompose | diagnose | job_profile.requirements[], tasks[] | class enum |
| diagnose | pathway, match | gaps[], barriers[] | types enum; blocking vs trainable |
| pathway | match | learning_path or no_viable_path | items ↔ gap ids |
| match | explain | recommendations[] | readiness enum; scores 0–1 |
| explain | human | explainability block | claims reference artifact ids |
| human | persist | human_decision | action enum; actor role hr for employment actions |

---

## 4. Validation layer

After every node:

1. JSON Schema validate slice
2. Referential integrity (evidence_ids exist)
3. Provenance labels present
4. No `protected_attribute_*` keys
5. Confidence in [0,1]
6. `mode=demo` may load fixture if `DEMO_LOCK=true` (deterministic demo)

Invalid output: **do not** keep LLM prose. Mark node failed or run repair prompt once (`repair_count <= 1`).

---

## 5. Retry behavior

| Error | Retry | Fallback |
|---|---|---|
| LLM timeout / 429 | 2 exponential | DEMO_MODE fixture if `mode=demo`; else fail |
| Schema invalid | 1 repair prompt | fail |
| SAP adapter error | 1 | continue degraded, banner, provenance SIMULATED/USER-PROVIDED |
| Parser error | 0 | ask for paste text |

Retries are orchestrator-owned, not inside agents.

---

## 6. Confidence propagation

```
inherited = min(non-null of: discover, decompose, diagnose)
pathway.effective = min(pathway, inherited)
match.effective = min(match, inherited)
```

Matching **rank** does not use LLM confidence as a hidden boost. Confidence is displayed and used for **escalation** (low → force human, disable “approve without comment” if we add that guard).

---

## 7. Explainability references

Every UI claim uses `ref`: `{ "type": "evidence|requirement|gap|barrier|market|learning|match_subscore", "id": "..." }`.

Narrator must only cite existing refs. Store `explainability.claims[]` as structured rows, plus `prose` as optional.

---

## 8. Human intervention points

| Point | Blocking? | Roles |
|---|---|---|
| After discover (correct capabilities) | P1 optional | candidate, hr |
| After decompose (employer readiness) | Optional path | hr |
| After recommendations | **Yes for employment-affecting persist** | hr |
| Proof grading override | Yes to flip ready_now | hiring manager / hr |
| Appeal | P2 | candidate → hr |

LangGraph `interrupt_before=["record_decision"]` (or equivalent).

---

## 9. Idempotency and concurrency

- `run_id` is the lock. One writer.
- Re-run creates a **new** `run_id` linked via `parent_run_id` so audit stays append-only.
- Demo lock: `demo_scenario_id=ananya_lucknow_v1` pins fixtures and model temperature 0.

---

## 10. Observability (required in design; P0 minimum persist)

Per node:

- agent / node name
- input (store hash + truncated body)
- output (full JSON in DB)
- confidence
- evidence refs
- latency_ms
- error
- fallback (`none|repair|fixture|degraded_sap`)
- model_id, prompt_version
- human override flag when decision recorded

P0: Postgres `audit_events`. P2: OpenTelemetry traces.

---

## 11. DEMO_MODE vs LIVE

| | DEMO | LIVE |
|---|---|---|
| LLM | temperature 0; optional fixture skip of LLM | normal |
| SAP | simulated adapter | live adapter if configured |
| Market | synthetic table | still synthetic unless feed verified |
| UI | “DEMO DATA” chrome | badges per field |

Never mix unlabeled.

---

## 12. Why LangGraph

We need cycles (HR edit → re-diagnose), interrupts (human), and explicit state. A DAG of HTTP micro-agents will not demo reliably in five days. Crew-style multi-chat is harder to audit.

If LangGraph packaging fights Python 3.13, equivalent: a FastAPI state machine with the same JSON and node functions. **Do not change the state contract.**
