"""SprintSync — FastAPI backend entry point."""
import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings
from database import init_db
from routers import auth_router, users_router, tasks_router, ai_router, stats_router
from services.logging import LoggingMiddleware, get_metrics, logger

# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="SprintSync",
    description=(
        "Lean internal tool for engineers: log work, track time, "
        "and get AI-powered planning help."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(ai_router)
app.include_router(stats_router)


# ── Observability ─────────────────────────────────────────────────────────────
@app.get("/metrics", tags=["observability"])
def metrics():
    """Prometheus-style JSON metrics."""
    return get_metrics()


@app.get("/health", tags=["observability"])
def health():
    return {"status": "ok", "service": settings.APP_NAME}


# ── Serve React SPA (if built) ────────────────────────────────────────────────
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        index = os.path.join(FRONTEND_DIST, "index.html")
        return FileResponse(index)


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()
    # Auto-seed in development
    try:
        from seed import seed
        seed()
    except Exception as exc:
        logger.warning("seed_skipped", reason=str(exc))
    logger.info("startup", app=settings.APP_NAME)
