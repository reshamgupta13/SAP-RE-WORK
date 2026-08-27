# RE:WORK

**AI-Powered Inclusive Workforce Recomposition Engine**

SAP Hackfest 2026 — Inclusive Workforce theme.

RE:WORK is an **intervention intelligence layer** that reasons across workforce capability, evidence, job requirements, barriers, learning, proof, opportunity, and employer readiness to determine the **smallest evidence-backed pathway** that can make an opportunity viable.

It is **not** a job recommender, ATS, or chatbot.

## Architecture

```
SAP (system of record)          RE:WORK (reasoning layer)
─────────────────────          ─────────────────────────
Workforce context              Evidence synthesis
Skills / attributes            Capability diagnosis
Learning ecosystem             Counterfactual analysis
Opportunity ecosystem          Pathway + proof-of-skill
                               Intervention simulation
                               Explainability + human governance
```

**Canonical case:** `case-ananya-finale` — single source of truth for the demo.

## Quick start

### Backend

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000/control-room](http://localhost:3000/control-room)

### Environment

Copy `backend/.env.example` to `backend/.env`.

| Variable | Default | Description |
|----------|---------|-------------|
| `DEMO_MODE` | `true` | Deterministic fallback, no external APIs |
| `SAP_MODE` | `SIMULATED` | `LIVE` only with verified credentials |
| `PERSISTENCE_MODE` | `memory` | `postgres` optional |

## DEMO_FALLBACK

With `DEMO_MODE=true`, the full Ananya case runs without:

- LLM API keys
- SAP tenant
- PostgreSQL
- External market APIs

Engine mode: `DEMO_FALLBACK`

## SAP integration

- **Default:** `SimulatedSAPProvider` — fixture-backed, labeled `SIMULATED`
- **Live:** Set `SAP_MODE=LIVE` + `SAP_API_URL`, `SAP_CLIENT_ID`, `SAP_CLIENT_SECRET`
- Health: `GET /api/sap/health`
- Context: `GET /api/sap/context`

**No live SAP capability is claimed without a verified successful connection.**

Read-only live integration is the default posture; write-back is disabled until explicitly validated.

## Source modes

Every object displays provenance:

| Mode | Meaning |
|------|---------|
| `SIMULATED` | SAP-shaped demo data |
| `SYNTHETIC` | RE:WORK fixture data |
| `USER_PROVIDED` | Candidate-uploaded evidence |
| `LIVE` | Verified SAP connection only |

RE:WORK-derived scores (e.g. capability fit) are **never** labeled as SAP data.

## Tests

```bash
cd backend
pytest
```

## Golden replay

```bash
python scripts/golden_replay.py
# → artifacts/golden/finale_ananya_replay.json
```

## Benchmark (22 executable scenarios)

```bash
python scripts/benchmark_eval.py
# → artifacts/evaluation/final_benchmark_report.json
```

## Demo health check

```bash
python scripts/demo_health_check.py
# → artifacts/demo_health_check.json (PASS/FAIL)
```

## Key APIs

| Endpoint | Purpose |
|----------|---------|
| `GET /api/cases/{id}/control-room` | Full Control Room payload |
| `GET /api/cases/{id}/export` | Case export (redacted) |
| `POST /api/cases/{id}/execute` | Run case pipeline |
| `GET /api/sap/health` | SAP connectivity status |

## Known limitations

- Live SAP requires tenant-specific endpoint verification
- 21 benchmark scenarios use diagnosis-level execution (finale uses full pipeline)
- Postgres persistence optional
- No resume upload in current build

## Documentation

- [Final demo script](docs/FINAL_FINALE_DEMO_SCRIPT.md)
- [Judge Q&A](docs/JUDGE_QA.md)
- [Engineering readiness](docs/FINAL_ENGINEERING_READINESS.md)
