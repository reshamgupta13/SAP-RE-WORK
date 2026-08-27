# 21 — Tech Stack Decision

Local machine: Node 22, Python 3.13, Docker, Git. Empty repo. No SAP env. Supabase CLI not installed; Supabase MCP org exists (all projects INACTIVE, unrelated).

---

## 1. Classification

| Layer | Choice | Class | Notes |
|---|---|---|---|
| Frontend | Next.js + TypeScript + Tailwind + shadcn/ui | **Required** | Fits enterprise UI speed |
| Charts | Recharts | **Useful** | Pathway/market small charts |
| Backend | FastAPI + Python | **Required** | Agents live here |
| Orchestration | LangGraph | **Required** (or equivalent FSM) | Explicit state |
| LLM | Gemini (or hackathon-permitted); interface for SAP GenAI Hub | **Required** | Hub **optional** until entitled |
| DB | PostgreSQL | **Required** | Docker local or new Supabase |
| Auth | Supabase Auth | **Optional** | P0 demo lock + local, no auth |
| Vector | pgvector | **Useful** | Skill aliasing; not matcher |
| Graph DB | Neo4j | **Unnecessary** | See data doc |
| PDF parse | PyMuPDF / python-docx | **Useful** | P1; P0 paste text |
| SAP | Adapter + simulated payloads; live OData if verified | **Required architecture / optional live** | |
| Deploy | Vercel (UI) + Railway/Render/Fly (API) | **Useful** | Or local + hotspot at finale |
| Observability SaaS | — | **Unnecessary** P0 | Postgres audit table |
| CrewAI / AutoGen | — | **Unnecessary** | Duplicate orchestration |
| Redis | — | **Optional** | Skip P0 |
| Kafka | — | **Unnecessary** | |

---

## 2. Why this and not BTP-first

BTP is the **correct production home**. We have **[NOT VERIFIED]** subaccount. Building only on BTP risks zero demo. FastAPI locally with a Destination-shaped adapter is the honest split.

If BTP appears on day 1, still keep FastAPI/LangGraph; deploy as a BTP app if time (P2).

---

## 3. LLM pinning

- One model for extractors; temperature 0 in demo
- Do not mix models mid-run
- Keys in `.env` never committed

---

## 4. Python 3.13 risk

Pin `langgraph`, `langchain-*`, `pydantic` v2 early. If a package lacks 3.13 wheels, use 3.12 in a venv — **do not** rewrite the architecture.

---

## 5. Monorepo sketch (after approval)

```
/apps/web          Next.js
/apps/api          FastAPI
/packages/schemas  Shared JSON schemas (or OpenAPI from FastAPI)
/docs
/fixtures
```

Not created in this phase.
