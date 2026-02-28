# SprintSync

> Lean internal tool for engineers: log work, track time, and get AI-powered planning help.  
> Built as the CodeStratLabs hiring challenge reference implementation.

[![CI](https://github.com/YOUR_USERNAME/sprintsync/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/sprintsync/actions)

---

## 🎥 Demo Video

[Loom walkthrough — 5 min](https://drive.google.com/file/d/1neCTI4XO-xQwtD3tM95Iaf2HQOK6q8Ix/view?usp=drivesdk)  
Covers: product demo → architecture → code tour → deploy.

## 🌐 Live App

[https://sprintsync.onrender.com](https://sprintsync.onrender.com)

Demo credentials:
- `alice / alice123` (regular user)
- `admin / admin123` (admin)

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│               SprintSync                    │
│                                             │
│  React SPA (Vite)  ←→  FastAPI backend      │
│                         │                   │
│                    ┌────┴────┐              │
│                    │ SQLite  │ (dev)        │
│                    │Postgres │ (prod)       │
│                    └─────────┘              │
│                                             │
│  AI: OpenAI gpt-4o-mini  (+ stub fallback) or coustom model│
│  Auth: JWT (python-jose + bcrypt)           │
│  Logging: structlog JSON → stdout           │
│  Metrics: /metrics (Prometheus-style JSON)  │
└─────────────────────────────────────────────┘
```

**Key design decisions:**

- **FastAPI** chosen for: automatic OpenAPI/Swagger docs, async support for AI calls, Pydantic validation, minimal boilerplate.
- **SQLite in dev / Postgres in prod** via a single `DATABASE_URL` env var — no code changes needed.
- **AI stub pattern**: `USE_AI_STUB=true` returns deterministic JSON. The same code path is used in tests and CI, ensuring the integration test doesn't depend on external APIs.
- **Status state machine**: `STATUS_TRANSITIONS` dict in the model layer enforces valid transitions (backlog → in_progress → review → done). Invalid transitions return a descriptive 400 with allowed next states.
- **Middleware logging**: every request logs `method, path, userId, latency_ms` as structured JSON. Stack traces appear on errors. `/metrics` exposes in-memory counters.

---

## Project Structure

```
sprintsync/
├── backend/
│   ├── main.py              # FastAPI app, middleware, startup
│   ├── config.py            # Pydantic settings (env vars)
│   ├── database.py          # SQLAlchemy engine + session
│   ├── seed.py              # Demo data seeder
│   ├── models/
│   │   ├── user.py          # User model (isAdmin)
│   │   └── task.py          # Task model + STATUS_TRANSITIONS
│   ├── routers/
│   │   ├── auth.py          # /auth/register, /auth/token
│   │   ├── users.py         # CRUD /users
│   │   ├── tasks.py         # CRUD /tasks + /transition
│   │   ├── ai.py            # /ai/suggest (description | daily_plan)
│   │   └── stats.py         # /stats/top-users, /stats/cycle-time
│   ├── services/
│   │   ├── auth.py          # JWT, password hashing, get_current_user
│   │   ├── ai.py            # OpenAI calls + deterministic stub
│   │   └── logging.py       # structlog config, metrics, middleware
│   ├── tests/
│   │   ├── conftest.py      # Fixtures, in-memory DB override
│   │   ├── test_unit.py     # 2+ happy path unit tests
│   │   └── test_integration.py # /ai/suggest stub integration test
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Full React SPA (list + kanban views)
│   │   └── api.js           # API client with token management
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── .github/workflows/ci.yml # GitHub Actions: lint → test → docker build
├── Dockerfile               # Multi-stage: Node (frontend) + Python
├── docker-compose.yml       # App + Postgres
├── docker-compose.dev.yml   # App + SQLite (simpler local dev)
├── render.yaml              # One-click Render deploy
├── estimates.csv            # Time estimates vs actuals
└── README.md
```

---

## Quick Start

### Local dev (Python + Node, no Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env if needed (defaults use SQLite, stub AI)
uvicorn main:app --reload
# → http://localhost:8000 (API + Swagger at /docs)

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

### Docker (recommended)

```bash
cp .env.example .env
# Optionally add OPENAI_API_KEY=sk-...
docker-compose up --build
# → http://localhost:8000
```

---

## API Reference

Full interactive docs at `/docs` (Swagger) or `/redoc`.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Register new user |
| POST | `/auth/token` | — | Login → JWT |
| GET | `/users/me` | JWT | Current user profile |
| GET | `/users/` | Admin | List all users |
| GET | `/tasks/` | JWT | List tasks (own, or all if admin) |
| POST | `/tasks/` | JWT | Create task |
| PATCH | `/tasks/{id}` | JWT | Update task fields |
| POST | `/tasks/{id}/transition` | JWT | Status transition |
| DELETE | `/tasks/{id}` | JWT | Delete task |
| POST | `/ai/suggest?mode=description&title=...` | JWT | AI task description |
| POST | `/ai/suggest?mode=daily_plan` | JWT | AI daily plan |
| GET | `/stats/top-users` | JWT | Top 5 users by minutes |
| GET | `/stats/cycle-time` | JWT | Avg minutes per status |
| GET | `/metrics` | — | Prometheus-style JSON metrics |
| GET | `/health` | — | Health check |

---

## Testing

```bash
cd backend
# All tests (uses in-memory SQLite + AI stub, no external services needed)
pytest tests/ -v

# Expected output:
# tests/test_unit.py::TestAuth::test_register_and_login PASSED
# tests/test_unit.py::TestAuth::test_login_wrong_password PASSED
# tests/test_unit.py::TestAuth::test_get_me PASSED
# tests/test_unit.py::TestTasks::test_create_and_list_tasks PASSED
# tests/test_unit.py::TestTasks::test_status_transition_happy_path PASSED
# tests/test_unit.py::TestTasks::test_invalid_status_transition PASSED
# tests/test_unit.py::TestTasks::test_update_task PASSED
# tests/test_unit.py::TestTasks::test_delete_task PASSED
# tests/test_integration.py::TestAISuggestIntegration::test_suggest_description_stub PASSED
# tests/test_integration.py::TestAISuggestIntegration::test_suggest_daily_plan_stub PASSED
# tests/test_integration.py::TestAISuggestIntegration::test_suggest_description_missing_title PASSED
# tests/test_integration.py::TestAISuggestIntegration::test_suggest_unauthenticated PASSED
```

---

## Deployment (Render)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Point to this repo — Render reads `render.yaml` automatically
4. Set `OPENAI_API_KEY` in Render dashboard (optional; stub works without it)
5. Deploy — first run seeds demo data automatically

---

## Observability

**Structured logs** (stdout, JSON):
```json
{"level": "info", "logger": "sprintsync", "timestamp": "2026-02-24T10:00:00Z",
 "event": "request", "method": "POST", "path": "/tasks/", "status_code": 201,
 "latency_ms": 12.4, "user_id": 2}
```

**Metrics** (`GET /metrics`):
```json
{
  "requests_total": 142,
  "requests_by_status_200": 130,
  "requests_by_status_201": 8,
  "requests_by_status_401": 4,
  "latency_ms_total": 1840.2
}
```

---

## Stretch Features Implemented

- ✅ **React SPA** — List view + Kanban board, task CRUD, AI assist, auth
- ✅ **CI pipeline** — GitHub Actions: test → docker build on every push
- ✅ `/stats/top-users` — Top 5 by logged minutes
- ✅ `/stats/cycle-time` — Average minutes per task status
- ✅ `render.yaml` — One-click Render deployment blueprint

---

## Time Log

See `estimates.csv` for task-by-task estimates vs actuals.

---

*Built with FastAPI · React · SQLAlchemy · structlog · OpenAI · Docker*
