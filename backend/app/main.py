from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from slowapi.errors import RateLimitExceeded

try:
    from slowapi.extension import _rate_limit_exceeded_handler
except ImportError:
    from slowapi import _rate_limit_exceeded_handler
from starlette.responses import Response

from app.api.v1 import admin, analytics, auth, brand, platforms, replies, reviews
from app.core.config import settings
from app.core.database import init_db
from app.core.dependencies import limiter
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment="production" if not settings.DEBUG else "development",
    )

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up AutoReply AI backend...")
    try:
        await init_db()
        logger.info("Database tables initialized")
    except Exception as exc:
        logger.warning("Database initialization deferred: %s", exc)
    try:
        redis_conn = await get_redis()
        if redis_conn:
            logger.info("Redis connected")
        else:
            logger.warning("Redis not available")
    except Exception as exc:
        logger.warning("Redis connection failed: %s", exc)
    yield
    logger.info("Shutting down...")
    from app.core.database import engine as db_engine
    await db_engine.dispose()
    try:
        from app.core.redis import close_redis
        await close_redis()
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next: Any) -> Response:
    method = request.method
    path = request.url.path
    start = time.time()
    try:
        response = await call_next(request)
        status = response.status_code
        REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()
        REQUEST_DURATION.labels(method=method, endpoint=path).observe(time.time() - start)
        return response
    except Exception as exc:
        REQUEST_COUNT.labels(method=method, endpoint=path, status=500).inc()
        REQUEST_DURATION.labels(method=method, endpoint=path).observe(time.time() - start)
        raise


app.include_router(auth.router)
app.include_router(reviews.router)
app.include_router(replies.router)
app.include_router(brand.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(platforms.router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    if settings.SENTRY_DSN:
        sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )
