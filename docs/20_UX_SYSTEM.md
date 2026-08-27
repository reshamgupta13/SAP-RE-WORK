# 20 — UX System

**Feel:** enterprise intelligence platform, not student CRUD, not chatbot-first.

---

## 1. Surfaces

| Surface | Purpose | Primary user |
|---|---|---|
| **A. Candidate / Employee** | Timeline, capability graph, pathway, proofs, matches, “why” | Candidate |
| **B. HR / Recruiter** | Requisition hygiene, diagnosis, recommendations, approve/modify/reject | HR |
| **C. Career Orchestrator / Control Room** | Node status, latencies, confidence, replay, DEMO/LIVE | Operator / demo |
| **D. SAP Integration / System Context** | Adapter status, entity payloads, provenance | Architect judges |
| **E. Evidence / Explainability** | WHAT/WHY/EVIDENCE/CONFIDENCE/ALTERNATIVES/DECISION | Both; legal-minded judges |

A and B are two projections of the same `run_id`. Never two databases of truth.

---

## 2. UX principles

- **Progressive disclosure:** summary → typed diagnosis → evidence drawer
- **Clear status:** node pipeline with running/done/failed
- **Confidence visible:** on every major artifact
- **Explainable:** click any match → refs
- **No noisy chatbot-first:** optional “ask about this run” later; P0 is panels
- **Capability graph:** readable nodes (skill, proficiency, source), not a hairball
- **Pathway visualization:** timeline of weeks, gap → item → proof
- **Obvious human approval:** sticky action bar in HR view
- **Evidence traceability:** every chip opens source
- **Provenance badges:** LIVE / SIMULATED / SYNTHETIC / MOCKED / USER-PROVIDED — never silent

---

## 3. Layout (desktop-first; finale is a projector)

**Control Room (demo home):** left rail pipeline; center diagnosis + wow contrast; right SAP context + confidence.

**Candidate:** top identity + constraints; graph; pathway; opportunities as cards with readiness tags.

**HR:** split JD (annotated requirements) | candidate diagnosis | actions.

**Explainability:** full-width drawer.

Mobile: not P0.

---

## 4. Visual language

- Neutral enterprise (slate / white). One accent for “action required”
- Readiness colors: now / proof / pathway / not_ready — consistent
- Do not use rainbow “AI” gradients
- “Traditional vs RE:WORK” contrast card — designed, not a meme

---

## 5. Empty, error, degraded

- SAP degraded banner
- LLM fail → Replay golden
- `not_ready` is a designed state, not a red error crash
- Missing evidence: ask to paste resume, do not invent

---

## 6. Copy rules

- No “biased JD” as a verdict
- No “you should hire”
- No fake precision (“92.37% culture fit”)
- Coverage may be shown as a computed 0–1 with formula link

---

## 7. Accessibility

WCAG-minded: contrast, keyboard on approve actions, do not encode meaning in color only (readiness has text labels).
