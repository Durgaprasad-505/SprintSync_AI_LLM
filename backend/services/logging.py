"""Structured JSON logging via structlog."""
import logging
import sys
import time
import traceback
from collections import defaultdict
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# ── Configure structlog ──────────────────────────────────────────────────────
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = structlog.get_logger("sprintsync")

# ── Metrics counters (in-memory, Prometheus-style) ───────────────────────────
_metrics: dict = defaultdict(int)


def record_request(method: str, path: str, status_code: int, latency_ms: float) -> None:
    _metrics["requests_total"] += 1
    _metrics[f"requests_by_status_{status_code}"] += 1
    _metrics["latency_ms_total"] += latency_ms


def get_metrics() -> dict:
    return dict(_metrics)


# ── Request logging middleware ────────────────────────────────────────────────
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.perf_counter()
        user_id = None

        try:
            from jose import jwt as _jwt
            from config import settings
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1]
                payload = _jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_id = payload.get("sub")
        except Exception:
            pass

        try:
            response = await call_next(request)
            latency_ms = (time.perf_counter() - start) * 1000
            record_request(request.method, request.url.path, response.status_code, latency_ms)
            logger.info(
                "request",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                latency_ms=round(latency_ms, 2),
                user_id=user_id,
            )
            return response
        except Exception as exc:
            latency_ms = (time.perf_counter() - start) * 1000
            record_request(request.method, request.url.path, 500, latency_ms)
            logger.error(
                "unhandled_exception",
                method=request.method,
                path=request.url.path,
                latency_ms=round(latency_ms, 2),
                user_id=user_id,
                exc_info=True,
                stack_trace=traceback.format_exc(),
            )
            raise
