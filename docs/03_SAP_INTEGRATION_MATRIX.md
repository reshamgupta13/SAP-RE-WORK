# 03 — SAP Integration Matrix

**Rule:** Never claim a feature or API is available in *our* landscape until verified from (1) our SAP environment, (2) official SAP documentation, or (3) hackathon-provided documentation.

**Current landscape from this workspace:** no tenant, no BTP subaccount, no destinations, no credentials.  
**Live status for every row’s access column:** **[NOT VERIFIED]** unless stated otherwise.

**Public documentation status** is called out separately so we can design honest adapters.

Verification labels: `[VERIFIED LIVE]` `[VERIFIED API]` `[AVAILABLE IN LANDSCAPE]` `[SIMULATED FOR PROTOTYPE]` `[NOT VERIFIED]`

---

## How RE:WORK will use SAP without lying

1. Define a **SAP Adapter** with stable internal DTOs.
2. Implement `SimulatedSuccessFactorsAdapter` using **documented entity names and field semantics**.
3. Implement `LiveSuccessFactorsAdapter` as a thin OData/REST client behind the same interface — empty until credentials exist.
4. UI provenance badges on every SAP-sourced object.
5. Production-path docs for Integration Center / TIH file flows where APIs are weak.

Finale judges should hear: *“SAP is the system of record. We are not calling a customer tenant from this laptop today. Here is the adapter, here are the official entities, here is the live switch.”*

If the team later obtains a Learning Hub practice system or BTP trial, only the adapter implementation changes.

---

## Matrix

### 1. SAP SuccessFactors Employee Central (people)

| Column | Content |
|---|---|
| **SAP capability** | Employee Central person / employment master |
| **What SAP already provides** | System of record for employee identity, employment, org assignment, location, job info |
| **Data available to RE:WORK** | Person ID, employment status, location, job classification, FTE, manager — **if connected** |
| **What RE:WORK does with it** | Anchor internal-mobility profiles; never invent employment history |
| **What SAP does not solve here** | Heterogeneous non-employee evidence; returner profiles who are **candidates**, not employees |
| **RE:WORK innovation** | Merge EC (if present) with external evidence pack without letting EC knockout fields dominate capability reasoning |
| **Prototype method** | Adapter DTO `SapEmployeeContext`. Simulated JSON for demo employee; live CompoundEmployee SOAP or OData User/EmpJob if tenant appears |
| **Status** | Product/API: **[VERIFIED API]** CompoundEmployee SOAP and EC OData are documented. Access: **[NOT VERIFIED]**. Prototype data: **[SIMULATED FOR PROTOTYPE]** |
| **Evidence required** | Tenant URL, API user, permission to query the demo person, sample payload |
| **Overclaim risk** | **High** if we show an “Employee Central” panel with simulated data and no badge |

### 2. SAP SuccessFactors Recruiting (requisitions, applications)

| Column | Content |
|---|---|
| **SAP capability** | Job requisitions, applications, operator roles |
| **What SAP already provides** | Requisition as workflow object; candidate applications; filters; (if enabled) job profile clone onto requisition |
| **Data available to RE:WORK** | Title, location, description, status, job role association — **if connected** |
| **What RE:WORK does with it** | Job Decomposition input; match target; write-back of **recommendations** only via human-approved export (prototype: do not upsert SAP) |
| **What SAP does not solve here** | Task-level decomposition; proxy classification; counterfactuals; proof-of-skill as first-class evidence |
| **RE:WORK innovation** | Typed requirement analysis on top of requisition text + structured fields |
| **Prototype method** | `JobRequisition`-shaped DTO. Documented OData entity `JobRequisition` exists. Job profile *sections* are **not** generally upsertable via OData (SAP KBA 3658100) |
| **Status** | `JobRequisition` OData: **[VERIFIED API]**. Job profile section update via OData: **documented limitation**. Access: **[NOT VERIFIED]**. Demo: **[SIMULATED FOR PROTOTYPE]** |
| **Evidence required** | OData dictionary screenshot from *our* tenant (entities vary by template) |
| **Overclaim risk** | **High** if we say “we update Job Profiles via API” — public KBA says section update is not supported |

### 3. Talent Intelligence Hub (attributes library)

| Column | Content |
|---|---|
| **SAP capability** | Canonical attributes (skills, competencies, etc.) across SuccessFactors |
| **What SAP already provides** | Skills foundation; governance of incoming skills; mapping into recruiting, learning, performance |
| **Data available to RE:WORK** | Attribute IDs, names, types — **if export/API exists in tenant** |
| **What RE:WORK does with it** | Align capability IDs to TIH attributes when mapping is provided; do not fork a competing skills taxonomy in production |
| **What SAP does not solve here** | Community blogs (2H2024 and later discussion) state **no simple third-party API for Attributes Library** as of that timeframe; workaround is custom MDF or Integration Center. 1H2026 TIH highlights add governance UI and certificate attribute type — **not verified as a public REST API for us** |
| **RE:WORK innovation** | Evidence-rich capability instances *referencing* TIH IDs when known; heterogeneous evidence SAP does not ingest |
| **Prototype method** | Local `Skill` table with optional `sap_attribute_id`. Seed a small TIH-like library for demo |
| **Status** | Product: **[VERIFIED API]** (product exists). Public third-party Attributes Library API: **treat as incomplete / Integration Center**. Access: **[NOT VERIFIED]**. Demo: **[SIMULATED FOR PROTOTYPE]** |
| **Evidence required** | Business Accelerator Hub ICD templates actually imported in a tenant we control; or a documented API changelog newer than our last check |
| **Overclaim risk** | **Critical.** Do not say “we call Talent Intelligence Hub live.” |

### 4. Growth Portfolio

| Column | Content |
|---|---|
| **SAP capability** | Per-person attributes, proficiency, passionate-about, expected ratings, timeline from other modules |
| **What SAP already provides** | Employee-facing skills portfolio; updates from Opportunity Marketplace, performance, learning (when configured) |
| **Data available to RE:WORK** | Proficiency snapshots — typically via **Integration Center import/export templates**, not a documented rich public CRUD API |
| **What RE:WORK does with it** | Prior for Candidate Intelligence; recency of SAP ratings vs new proof-of-skill |
| **What SAP does not solve here** | Returner who is not in the tenant; proof artifacts; barrier reasoning |
| **RE:WORK innovation** | Treat Growth Portfolio as **one evidence source among many**, with source weight and date |
| **Prototype method** | `SapGrowthPortfolioSnapshot` DTO; simulated for Ananya if treated as internal mobility; empty + user-provided resume if external candidate |
| **Status** | Product: **[VERIFIED API]** (product + ICD templates documented). Live: **[NOT VERIFIED]**. Demo: **[SIMULATED FOR PROTOTYPE]** |
| **Evidence required** | Export file from Integration Center or confirmed OData/MDF entities in-tenant |
| **Overclaim risk** | **High** |

### 5. SuccessFactors Learning

| Column | Content |
|---|---|
| **SAP capability** | Catalog, assignments, completion, curricula |
| **What SAP already provides** | LMS of record; OData/public learning APIs and microservices (user assignment, curriculum, history) documented in SAP Help (e.g. Learning web services guide) |
| **Data available to RE:WORK** | Item IDs, titles, assignment status, completion — **if connected** |
| **What RE:WORK does with it** | Map pathway `LearningItem` to LMS item IDs; later write assignment **only** with human approval |
| **What SAP does not solve here** | Selecting items from a *task-level gap* + attaching a work-sample proof; challenging requisition proxies that ignore completion |
| **RE:WORK innovation** | Pathway = gap + item + exercise + proof + readiness update |
| **Prototype method** | Map demo pathway to **named** courses. Prefer real SAP Learning Hub, student edition course titles **if the team supplies the catalog names they can see**. Until then, labeled synthetic catalog |
| **Status** | Learning APIs: **[VERIFIED API]**. Our tenant: **[NOT VERIFIED]**. Learning Hub student edition access for this team: **[NOT VERIFIED]**. Demo catalog: **[SYNTHETIC]** unless team pastes real item names |
| **Evidence required** | Learning Hub login proof; or LMS OAuth client; list of 10 real item titles for the demo path |
| **Overclaim risk** | **High** if we invent “SAP official completion rates” |

### 6. Opportunity Marketplace

| Column | Content |
|---|---|
| **SAP capability** | Internal gigs, assignments, career exploration, recommendations into Growth Portfolio |
| **What SAP already provides** | Opportunity objects; assignment completion can update Growth Portfolio (documented product behavior) |
| **Data available to RE:WORK** | Open opportunities, required attributes — **if API/export available** |
| **What RE:WORK does with it** | Target set for inclusive matching; prefer SAP opportunities for internal persona |
| **What SAP does not solve here** | Barrier audit of opportunity wording; proof-of-skill gate; external candidate market |
| **RE:WORK innovation** | Match states including pathway-fit; explainability; HR review |
| **Prototype method** | `Opportunity` table with `source=sap_omm | synthetic`. No live OMM API verified for this project |
| **Status** | Product behavior: **[VERIFIED API]** (help/learning content). Public API for third-party matching: **[NOT VERIFIED]**. Demo: **[SIMULATED FOR PROTOTYPE]** |
| **Evidence required** | API docs from *our* landscape or Integration Center extract |
| **Overclaim risk** | **High** |

### 7. Job Profile Builder (families, roles, competencies)

| Column | Content |
|---|---|
| **SAP capability** | Structured job profiles (successor to JDM) |
| **What SAP already provides** | Role-task-competency structure **when customers actually fill it** |
| **Data available to RE:WORK** | Role competencies — often via import/export / MDF, not full OData upsert of profile sections |
| **What RE:WORK does with it** | Gold input to Job Decomposition when present; else decompose JD text and mark lower confidence |
| **What SAP does not solve here** | Most noisy requisitions are unstructured text. JPB does not run counterfactuals |
| **RE:WORK innovation** | Decomposition even when JPB is empty; classify proxies in free text |
| **Prototype method** | Optional `sap_job_profile` JSON. Demo role seeded as JPB-like structured profile **and** a messy JD to show the difference |
| **Status** | Product: **[VERIFIED API]**. OData update of job profile sections: **documented as not supported**. Access: **[NOT VERIFIED]** |
| **Evidence required** | Whether “Use Job Profiles in Requisitions” is on in tenant |
| **Overclaim risk** | Medium (overstating how complete customer JPB data is) |

### 8. SAP BTP (runtime, destinations, identity)

| Column | Content |
|---|---|
| **SAP capability** | Extension platform: Destination service, XSUAA, connectivity, CAP, Cloud Foundry / Kyma |
| **What SAP already provides** | Secure connectivity pattern from extension apps to SuccessFactors |
| **Data available to RE:WORK** | None by itself — it is plumbing |
| **What RE:WORK does with it** | **Production home** for the adapter and possibly the orchestrator |
| **What SAP does not solve here** | The reasoning algorithms |
| **RE:WORK innovation** | Intelligence layer portable to BTP |
| **Prototype method** | Document destination-based architecture. **Do not fake a BTP deploy.** Local FastAPI is acceptable if the adapter contract matches BTP-style destinations |
| **Status** | Architecture: **[VERIFIED API]** (Architecture Center: pro-code agents, Destinations). Our subaccount: **[NOT VERIFIED]** |
| **Evidence required** | Subaccount GUID, destination name `successfactors`, SSO method |
| **Overclaim risk** | **Critical** if slides say “running on BTP” and it is localhost |

### 9. SAP Integration Suite

| Column | Content |
|---|---|
| **SAP capability** | iFlows, OData/SFTP, Integration Center adjacent patterns |
| **What SAP already provides** | The realistic path to TIH/Growth Portfolio **file** integration |
| **Data available to RE:WORK** | Batch attribute and portfolio extracts |
| **What RE:WORK does with it** | Nightly ingest in production design; out of scope for P0 runtime |
| **What SAP does not solve here** | Interactive demo loop |
| **RE:WORK innovation** | Consume extracts into capability graph |
| **Prototype method** | Show a sample **ICD-shaped CSV/JSON** in `/docs` or demo fixtures labeled `[SYNTHETIC]` |
| **Status** | Product: **[VERIFIED API]**. Access: **[NOT VERIFIED]** |
| **Evidence required** | Tenant Integration Center job or BTP iFlow |
| **Overclaim risk** | Medium |

### 10. SAP Generative AI Hub / AI Core

| Column | Content |
|---|---|
| **SAP capability** | Governed foundation-model access for BTP apps |
| **What SAP already provides** | Enterprise LLM proxy, grounding, lifecycle |
| **Data available to RE:WORK** | Model completions |
| **What RE:WORK does with it** | Optional LLM backend instead of direct Gemini |
| **What SAP does not solve here** | Our graphs, scores, governance |
| **RE:WORK innovation** | Same agents, swappable LLM provider |
| **Prototype method** | `LLMProvider` interface: `GeminiProvider` | `SapGenAiHubProvider` |
| **Status** | Product: **[VERIFIED API]** (Architecture Center). Entitlement: **[NOT VERIFIED]**. P0 likely Gemini or other permitted model: **[NOT VERIFIED]** which models the hackathon allows |
| **Evidence required** | AI Core resource group, model deployment name |
| **Overclaim risk** | High if we imply SAP-hosted inference without entitlement |

### 11. Joule / Joule Studio / SuccessFactors Joule Agents

| Column | Content |
|---|---|
| **SAP capability** | Copilot; Career and Talent Development Agent; HR Service; People Intelligence; etc. (H1 2026 narrative in hackfest brief) |
| **What SAP already provides** | In-product agents for SF customers who are entitled |
| **Data available to RE:WORK** | None unless A2A / Agent Gateway is set up |
| **What RE:WORK does with it** | **Do not rebuild Joule.** Optionally, later expose RE:WORK as an A2A skill |
| **What SAP does not solve here** | The inclusive recomposition loop as specified in this repo |
| **RE:WORK innovation** | Complementary reasoning product, not a Joule clone |
| **Prototype method** | Out of P0. Architecture note only |
| **Status** | Product narrative: **[VERIFIED API]** as SAP public messaging. Our Joule: **[NOT VERIFIED]**. A2A from this app: **[NOT VERIFIED]** |
| **Evidence required** | Joule Studio project, Agent Gateway URL |
| **Overclaim risk** | **Critical.** Judges know Joule. Do not put a Joule logo on a Gemini chat. |

### 12. People Intelligence / SAP Business Data Cloud

| Column | Content |
|---|---|
| **SAP capability** | Unified people/skills/business analytics |
| **What SAP already provides** | Insights products for customers |
| **Data available to RE:WORK** | Not available to us |
| **What RE:WORK does with it** | Nothing in prototype |
| **Status** | **[NOT VERIFIED]** / not in MVP |
| **Overclaim risk** | **Critical** if mentioned as integrated |

### 13. Smart Recruiters / Winston (acquisition narrative)

| Column | Content |
|---|---|
| **SAP capability** | Talent acquisition suite + AI agent Winston (hackfest brief) |
| **What RE:WORK does** | Out of scope. Do not integrate or impersonate |
| **Status** | **[NOT VERIFIED]** access. Product mentioned in brief only |
| **Overclaim risk** | **Critical** |

### 14. SAP Learning Hub, student edition (hackathon-mandated)

| Column | Content |
|---|---|
| **SAP capability** | Student learning + (gated) cloud practice systems |
| **What SAP already provides** | Courses, possibly practice landscapes for entitled students |
| **Data available to RE:WORK** | Course names, completion of *team members’* learning — not customer HR data |
| **What RE:WORK does with it** | (a) Team enablement; (b) map demo learning items to **real course titles** the team can show on Learning Hub; (c) if a **SuccessFactors practice system** is included in *this team’s* entitlement, that becomes the preferred live adapter target |
| **What SAP does not solve here** | Practice systems are training data, not the customer’s inclusive-hiring process |
| **RE:WORK innovation** | Use practice data honestly as `[LIVE]` *training-system* data, never as a named enterprise’s HR data |
| **Prototype method** | Screenshot-backed catalog mapping; optional live OData if practice SF is confirmed |
| **Status** | Platform exists: **[VERIFIED API]** (public student edition). **This team’s login and practice-system contents:** **[NOT VERIFIED]** |
| **Evidence required** | Learning Hub user, list of entitled practice systems, whether SuccessFactors is among them |
| **Overclaim risk** | Medium — claiming practice data is a customer deployment |

---

## SAP-critical vs SAP-optional for the prototype

| Must appear in demo | Nice if verified in time | Do not mention as integrated |
|---|---|---|
| Adapter contract + SAP-shaped workforce context panel | One live OData GET (requisition or user) | Joule, Winston, Business Data Cloud, “live TIH API” |
| Provenance badges | Real Learning Hub course titles | Fake destinations |
| Honest spoken line: simulated vs live | BTP destination screenshot | |

---

## Fallback if no SAP API is ever available

Still “leverage SAP technologies” in a judge-defensible way:

1. **Semantic alignment:** DTOs named and fielded after documented SuccessFactors entities.
2. **Integration architecture:** Destination-style adapter, Integration Center sample extract, write-back as human-approved export.
3. **Learning Hub:** real course mapping if the team provides titles.
4. **Narrative accuracy:** “This is the extension layer SAP BTP is for; we could not bind a tenant in time; here is the switch.”

This is weaker than a live GET, but stronger than a logo. **A single live read beats ten simulated modules.** Obtaining practice-system access is the highest-priority external dependency.
