# RE:WORK Deployment Guide

Deploy **frontend → Vercel**, **backend → Render**. Secrets stay server-side on Render only.

## Repository layout

| Path | Role |
|------|------|
| `frontend/` | Next.js 15 app (Vercel root directory) |
| `backend/` | FastAPI + LangGraph API (Render root directory) |
| `fixtures/` | Static demo/learning catalog data (required at runtime) |
| `render.yaml` | Optional Render Blueprint (repo root) |

Structure: **monorepo** with separate frontend and backend directories.

---

## 1. Local development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
cp .env.example .env            # fill LLM_API_KEY if using Groq
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verify: `curl http://localhost:8000/health` → `{"status":"ok"}`

### Frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

`frontend/.env.local`:

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Open http://localhost:3000

---

## 2. GitHub

Push the full monorepo to GitHub. Both Vercel and Render connect to the same repository.

**Never commit:** `.env`, `.env.local`, API keys, SAP passwords.

---

## 3. Render (backend)

### Create service

1. [Render Dashboard](https://dashboard.render.com) → **New → Web Service**
2. Connect your GitHub repo
3. Settings:

| Setting | Value |
|---------|-------|
| **Root Directory** | `backend` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Health Check Path** | `/health` |

Or use **New → Blueprint** with the repo’s `render.yaml`.

### Required environment variables (Render)

| Variable | Secret? | Example / notes |
|----------|---------|-----------------|
| `ENVIRONMENT` | No | `production` |
| `CORS_ORIGINS` | No | `https://your-app.vercel.app` (comma-separated for preview URLs) |
| `DEMO_MODE` | No | `true` |
| `SAP_MODE` | No | `SIMULATED` (use `LIVE` only with verified OData) |
| `PERSISTENCE_MODE` | No | `memory` |
| `SAP_PROTOTYPE_FALLBACK` | No | `true` |
| `FIXTURES_DIR` | No | `../fixtures` |
| `LLM_PROVIDER` | No | `groq` |
| `LLM_MODEL` | No | `openai/gpt-oss-120b` |
| `LLM_API_KEY` | **Yes** | Groq API key |
| `LLM_TIMEOUT_SECONDS` | No | `60` (long-running diagnose pipeline) |

### Optional — live SAP (Student page / OData)

Only if `SAP_MODE=LIVE` and OData is verified:

| Variable | Secret? |
|----------|---------|
| `SAP_ODATA_BASE_URL` | No |
| `SAP_AUTH_MODE` | No (`BASIC`) |
| `SAP_USERNAME` | **Yes** |
| `SAP_PASSWORD` | **Yes** |
| `SAP_ENTITY_SKILL` | No |

### Optional — PostgreSQL persistence

If you add a Render Postgres instance:

| Variable | Secret? |
|----------|---------|
| `PERSISTENCE_MODE` | `postgres` |
| `DATABASE_URL` | **Yes** (from Render Postgres) |

**Note:** Default `memory` persistence means cases reset when the Render instance restarts. This is fine for hackfest demos; document it honestly.

### Verify backend

```bash
curl https://<your-render-service>.onrender.com/health
curl https://<your-render-service>.onrender.com/api/catalog/health
```

---

## 4. Vercel (frontend)

### Create project

1. [Vercel Dashboard](https://vercel.com) → **Add New → Project**
2. Import the same GitHub repo
3. Settings:

| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` |
| **Framework** | Next.js (auto-detected) |
| **Build Command** | `npm run build` |
| **Output** | default (Next.js) |

### Required environment variable (Vercel)

| Variable | Secret? | Value |
|----------|---------|-------|
| `NEXT_PUBLIC_API_BASE_URL` | No (public URL) | `https://<your-render-service>.onrender.com` |

**Set this before the first production build.** No trailing slash.

Redeploy after changing env vars.

### Verify frontend

1. Open `https://<your-app>.vercel.app`
2. Workspace → candidates/jobs load from Render
3. Diagnose pairing → Control Room pipeline
4. Targeted Learning → generate plan
5. Student → skill CRUD (requires live SAP credentials on Render if not simulated)

---

## 5. CORS

Backend reads `CORS_ORIGINS` (comma-separated). Example:

```
CORS_ORIGINS=https://rework.vercel.app,https://rework-git-main-yourteam.vercel.app
```

Development defaults to `localhost:3000` when `ENVIRONMENT=development`.

Production **must** set `CORS_ORIGINS` — wildcard `*` is not used.

---

## 6. Health checks

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Render liveness — `{"status":"ok"}` |
| `GET /health/ready` | Fixtures + config sanity |
| `GET /api/health` | API router health (includes sap_mode) |

Health checks do **not** call LLM or SAP.

---

## 7. Architecture

```
Browser → Vercel (Next.js) → HTTPS → Render (FastAPI) → LangGraph → Groq LLM
                                              ↓
                                         SAPProvider (SIMULATED or LIVE OData)
```

Secrets (`LLM_API_KEY`, `SAP_PASSWORD`, `DATABASE_URL`) exist **only on Render**.

---

## 8. Updating production

1. Push to `main` on GitHub
2. Render and Vercel auto-deploy (if enabled)
3. After backend URL changes, update `NEXT_PUBLIC_API_BASE_URL` on Vercel
4. After frontend URL changes, update `CORS_ORIGINS` on Render

---

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| CORS error in browser | Set `CORS_ORIGINS` on Render to exact Vercel URL (https, no trailing slash) |
| `NEXT_PUBLIC_API_BASE_URL is not configured` | Add env var on Vercel, redeploy |
| Workspace empty / network error | Confirm Render service is running; check `/api/catalog/health` |
| Diagnose hangs then fails | Set `LLM_API_KEY` on Render; increase `LLM_TIMEOUT_SECONDS` |
| Targeted learning uses fallback only | `LLM_API_KEY` missing — deterministic fallback still works |
| Student SAP errors | Requires `SAP_MODE=LIVE` + OData credentials on Render |
| Cases disappear after restart | Expected with `PERSISTENCE_MODE=memory` |
| Render cold start slow | Free tier spins down; first request may take 30–60s |

---

## 10. Security checklist

- [ ] No secrets in Git
- [ ] No secrets in `NEXT_PUBLIC_*` variables
- [ ] `CORS_ORIGINS` restricted to your Vercel domain(s)
- [ ] `.env` gitignored (already configured)
- [ ] Rotate any key that was ever committed or pasted in chat
