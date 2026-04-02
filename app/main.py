"""LLM Gateway & Observability Platform.

A FastAPI proxy that routes requests across OpenAI and Anthropic,
caches responses in DynamoDB, emits CloudWatch metrics, and runs
an automated eval pipeline.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import settings
from app.core.router import get_providers
from app.models import HealthResponse
from app.routers import router as gateway_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info(
        f"LLM Gateway starting on port {settings.PORT} "
        f"region={settings.AWS_REGION}"
    )
    logger.info(f"Request log table: {settings.DYNAMODB_REQUEST_LOG_TABLE}")
    logger.info(f"Cache table: {settings.DYNAMODB_CACHE_TABLE}")
    logger.info(f"Eval table: {settings.DYNAMODB_EVAL_TABLE}")
    logger.info(f"CloudWatch namespace: {settings.CLOUDWATCH_NAMESPACE}")
    yield
    logger.info("LLM Gateway shutting down")


app = FastAPI(
    title="LLM Gateway",
    description="Multi provider LLM proxy with routing, caching, and observability",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(gateway_router)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint for ECS container health checks."""
    providers = get_providers()
    provider_status = {}
    for name, provider in providers.items():
        status = await provider.health_check()
        provider_status[name] = status

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        providers=provider_status,
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "LLM Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
