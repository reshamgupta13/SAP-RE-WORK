# 00 — Project Reconnaissance

**Project:** RE:WORK  
**Date:** 2026-08-28  
**Mode:** Discovery only. No application code created or modified.  
**Workspace:** `c:\Users\shria\Desktop\rework`

---

## 1. Repository state

The workspace is **empty and uninitialized**.

| Check | Result |
|---|---|
| Files in workspace (including hidden) | **0** |
| Git repository | **No** (`.git` absent) |
| `package.json` / `pyproject.toml` / `requirements.txt` | **Absent** |
| Frontend | **Absent** |
| Backend | **Absent** |
| Agent code | **Absent** |
| API routes | **Absent** |
| Database schema / migrations | **Absent** |
| Environment files (`.env*`) | **Absent** |
| Tests | **Absent** |
| Deployment config | **Absent** |
| Docs (before this phase) | **Absent** |
| Assets / demo data | **Absent** |
| Hackathon briefing files in repo | **Absent** |

This is a **greenfield** repository. There is nothing to preserve, merge, or overwrite.

---

## 2. Local toolchain (verified on this machine)

| Tool | Status | Notes |
|---|---|---|
| Node.js | **Verified** `v22.14.0` | Suitable for Next.js |
| npm | **Verified** `10.9.2` | |
| Python | **Verified** `3.13.12` | Suitable for FastAPI / LangGraph |
| Git | **Verified** `2.46.1` | Repo not initialized |
| Docker | **Verified** `29.2.0` | Available if needed for local Postgres |
| npx | **Verified** `10.9.2` | |
| Supabase CLI | **Not installed** | MCP access to user's org exists; CLI is not on PATH |
| `upsk` CLI | **Not on PATH** | Config folder exists at `%USERPROFILE%\.upsk`; not required for this project |
| SAP CLI / BTP CLI / `cf` | **Not observed** | Not in PATH snapshot |
| SAP-related environment variables | **None** | No `SAP_*`, `SUCCESSFACTORS_*`, `BTP_*`, `GEMINI_*`, `OPENAI_*`, `SUPABASE_*` in process env |

---

## 3. Adjacent systems observed (not RE:WORK)

Supabase MCP is authenticated against the user's organization. Existing projects:

| Project | Region | Status | Relevance |
|---|---|---|---|
| `civicseva` | ap-south-1 | INACTIVE | Unrelated. Do not reuse. |
| `SoundWave` | ap-south-1 | INACTIVE | Unrelated. Do not reuse. |
| `acdyon-pathway-engine` | ap-south-1 | INACTIVE | Name suggests a prior pathway concept. **Not verified as reusable.** Treat as unrelated unless the team explicitly confirms otherwise. |
| `synapsoul-command` | ap-south-1 | INACTIVE | Unrelated. Do not reuse. |
| `shriansh1625's Project` | ap-northeast-1 | INACTIVE | Unrelated. Do not reuse. |

**Decision:** Do not attach RE:WORK to an existing inactive project. Create a new Supabase project only after the MASTER BUILD PLAN is approved.

---

## 4. Hackathon materials (external, not in repo)

Official North Region brief was retrieved from SAP Events (public page, not a private tenant document):

- Source: [Hackfest 2026 — North Region](https://events.sap.com/in-hackfest-2026/en_us/home.html)
- Status of this source: **[VERIFIED PUBLIC BRIEF]**
- Theme selected: **Theme 2 — Inclusive Workforce**
- Finale requirement (quoted from brief): teams must **design, develop and demonstrate a functional prototype leveraging SAP technologies**
- Required career orchestrator capabilities named in the brief:
  - Skills Discovery
  - Market Intelligence
  - Learning Pathways
  - Inclusive Matching
  - Bias Audit
  - Human-in-the-loop
- Named demo persona: **28-year-old woman returning to work after a 3-year caregiving break in Lucknow**
- Mandatory participation platform: **SAP Learning Hub, student edition**
- Finale date (North): **3 September 2026** at Chandigarh University
- Prototype window after shortlisting: **27 August – 2 September 2026**

Additional brief agents named by SAP that we must account for in design (not all must be separate LLM agents):

- Employer Readiness Agent
- Bias Audit Agent

**Not found in repo:** private judge rubrics, provided SuccessFactors tenant credentials, BTP subaccount details, Integration Suite keys, or a college-issued landscape document.

---

## 5. What already exists

| Item | Exists? | Reusable? |
|---|---|---|
| Application code | No | N/A |
| Design system | No | N/A |
| Demo fixtures | No | N/A |
| SAP adapter | No | N/A |
| Product idea / thesis (this prompt) | Yes, in conversation | **Yes — this is the product brief** |
| Official theme constraints | Yes, public SAP Events page | **Yes — treat as source of truth for judging expectations** |
| Official SAP product documentation | Public Help Portal / Community / Architecture Center | **Yes — for capability claims and API existence, not for live access** |

---

## 6. What is reusable

Nothing in this repository.

Reusable **outside** the repo, with caution:

1. **Official SAP entity concepts** (Job Requisition, Growth Portfolio attributes, Learning items, Employee Central person data). Use as *schema inspiration*, not as proof of live access.
2. **Local toolchain** (Node 22, Python 3.13, Docker, Git).
3. **Supabase MCP** for a future new project, if the team chooses Supabase.
4. **Hackfest persona and agent list** from the official brief.

---

## 7. What is broken

Nothing is broken because nothing has been built.

The only “broken” condition is **missing foundation**:

- no git history
- no package managers initialized
- no secrets management
- no SAP connectivity
- no demo dataset

---

## 8. What is missing (ordered by dependence)

1. Git repository and branch strategy
2. Product specification (this docs set)
3. Canonical data model and provenance labels
4. SAP adapter contract (live vs simulated)
5. Orchestrator state machine
6. Seed/demo corpus for the Lucknow returner persona plus adjacent personas
7. LLM provider decision and keys
8. Database
9. Frontend application
10. Evaluation harness
11. Deployment

---

## 9. What should NOT be rebuilt

Once we start, do **not** rebuild:

- SAP SuccessFactors itself (skills library, employee master, LMS, opportunity marketplace UI)
- A generic job board
- A generic chatbot career coach
- A resume-vs-JD cosine-similarity matcher as the core product
- A graph database for its own sake
- Ten independent chat agents
- A live market-data crawler
- Autonomous hire/reject decisioning

Use SAP as the **system of record**. Build the **reasoning layer** only.

---

## 10. Recommended starting point (after plan approval)

Do **not** start with UI chrome or dummy REST stubs that invent SAP endpoints.

Start in this order:

1. Canonical schemas + provenance enum (`LIVE | SIMULATED | SYNTHETIC | MOCKED | USER-PROVIDED`)
2. SAP-shaped adapter interface with a **simulated SuccessFactors backend** that uses documented entity names
3. LangGraph orchestrator with explicit state
4. One vertical slice: Lucknow returner → target role → diagnosis → pathway → match → human review
5. UI only after the slice returns inspectable artifacts

---

## 11. Risks

| Risk | Severity | Why it matters |
|---|---|---|
| No SAP tenant / credentials | **Critical** | Finale requires “leveraging SAP technologies.” Logo-only integration will be challenged. |
| Overclaiming TIH/Joule live features | **Critical** | Talent Intelligence Hub does not currently expose a simple public Attributes Library API for third-party apps. See `03_SAP_INTEGRATION_MATRIX.md`. |
| Time: ~5 days to finale | **Critical** | 27 Aug–2 Sep build window. Scope must collapse to one demo-quality loop. |
| Empty repo / no git | High | Easy to lose work; initialize only after plan approval if the team wants git. |
| Hallucinated market statistics | High | Judges will ask for sources. Synthetic market data must be labeled. |
| Discriminatory “inclusion scoring” | High | Protected characteristics must not become ranking advantages. |
| Python 3.13 + LangGraph package lag | Medium | Pin versions early; 3.13 is new. |
| Inactive unrelated Supabase projects | Low | Temptation to reuse the wrong project. |
| LLM non-determinism in live demo | High | Demo mode must be fixture-backed and reproducible. |

---

## 12. Unknowns requiring verification (blocked until the team provides evidence)

These remain **[NOT VERIFIED]** until the team produces screenshots, URLs, credentials (in a secret store), or official landscape docs:

1. Do we have a **SuccessFactors** tenant (customer, partner, or Learning Hub practice system)?
2. Do we have **SAP BTP** subaccount + Destinations + XSUAA?
3. Do we have **SAP Integration Suite** / Cloud Integration?
4. Do we have **Generative AI Hub / AI Core** entitlements?
5. Do we have **Joule** / Joule Studio access?
6. What does **SAP Learning Hub, student edition** actually give this team (courses only vs cloud practice systems vs SuccessFactors sandbox)?
7. Is there a college-provided **API collection** or Postman file?
8. Which LLM is permitted (Gemini, AI Core models, both)?
9. Team size and skill split (hackathon rule: 4–5 students)?
10. Is `acdyon-pathway-engine` a prior attempt at this idea, or a different product?
11. Will judges have internet access to a deployed URL, or is local demo required?
12. Are we allowed to use non-SAP LLMs if we still consume SAP-shaped data?

---

## 13. Verification legend used across all docs

| Label | Meaning |
|---|---|
| **[VERIFIED LIVE]** | We successfully called it from this project’s environment. |
| **[VERIFIED API]** | Official SAP documentation confirms the API/product exists. We have **not** called it from this repo. |
| **[AVAILABLE IN LANDSCAPE]** | Present in a tenant/subaccount we can see. Not yet wired. |
| **[SIMULATED FOR PROTOTYPE]** | Realistic payload and entity names; not a live system call. |
| **[SYNTHETIC]** | Created for demo; not from a customer system. |
| **[NOT VERIFIED]** | Existence, access, or fit is unconfirmed. |

**Current SAP access from this workspace: [NOT VERIFIED] for every live product.**  
**Current SAP API existence from public docs: [VERIFIED API] for several SuccessFactors / BTP / Learning products — see matrix.**

---

## 14. Conclusion

RE:WORK is a **blank-slate finale prototype**. The idea is strong and aligned with the official Inclusive Workforce brief. The repository contains no code to salvage. The highest-leverage work in this phase is the specification set in `/docs`, not scaffolding.

No application code has been changed.
