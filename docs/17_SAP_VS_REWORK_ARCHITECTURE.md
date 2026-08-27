# 17 — SAP vs RE:WORK Architecture

```
+----------------------------- SAP --------------------------------+
|  Enterprise workforce data                                       |
|  Employee / candidate / role context                             |
|  Skills foundation (TIH / Growth Portfolio)                      |
|  Learning ecosystem                                              |
|  Opportunity / recruiting ecosystem                              |
|  Enterprise workflows, identity, permissions                     |
+-------------------------------+----------------------------------+
                                |  Adapter
                                |  (BTP Destination in production)
                                v
+--------------------------- RE:WORK ------------------------------+
|  Capability reasoning & evidence synthesis                       |
|  Job decomposition & requirement classification                  |
|  Gap vs proxy diagnosis                                          |
|  Counterfactual barrier analysis                                 |
|  Pathway + proof orchestration                                   |
|  Inclusive matching (deterministic)                              |
|  Explainability & audit                                          |
|  Human decision capture                                          |
+------------------------------------------------------------------+
```

---

## 1. Ownership

| Data / decision | Owner |
|---|---|
| Legal employee record | SAP EC |
| Requisition master | SAP Recruiting |
| Canonical attribute id | TIH (when mapped) |
| Course catalog master | SF Learning / Learning Hub |
| Internal opportunity master | Opportunity Marketplace |
| Evidence graph, proofs, diagnoses | **RE:WORK** |
| Rank formula, readiness | **RE:WORK** |
| Hire / reject / offer | **Human in SAP process** — RE:WORK never owns |

---

## 2. Runtime (prototype)

```
[Next.js UI]
    |
    | REST
    v
[FastAPI]
    |
    +-- LangGraph orchestrator
    +-- SAP Adapter (Simulated | Live)
    +-- Postgres (Supabase or Docker)
    +-- LLM Provider (Gemini | optional AI Core)
```

Production sketch (not claimed as deployed):

```
[Fiori / our UI]
    -> App Router / XSUAA
    -> CAP or FastAPI on BTP
    -> Destination -> SuccessFactors
    -> Generative AI Hub
```

---

## 3. Failure isolation

If SAP is down: RE:WORK still runs on user-provided docs + last cached copy, with degraded banner.  
If LLM is down: demo fixtures; live mode fails the run.  
If RE:WORK is down: SAP hiring continues unchanged (extension, not core HR).

---

## 4. What we will say on stage

“SuccessFactors holds the workforce objects. RE:WORK is the reasoning extension you would deploy beside it on BTP. Today the tenant switch is simulated; the contracts are real.”

If a live GET works by finale, replace the second sentence with the entity we actually read.
