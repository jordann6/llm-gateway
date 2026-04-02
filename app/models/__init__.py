"""Pydantic models for the LLM Gateway API."""

from pydantic import BaseModel, Field
from enum import Enum


class RoutingStrategy(str, Enum):
    COST = "cost"
    LATENCY = "latency"
    QUALITY = "quality"


class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class GatewayRequest(BaseModel):
    """Incoming request to the LLM Gateway."""

    prompt: str = Field(..., min_length=1, max_length=50000)
    strategy: RoutingStrategy = RoutingStrategy.COST
    provider: Provider | None = None
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    client_id: str = Field(default="default")
    use_cache: bool = True


class GatewayResponse(BaseModel):
    """Response from the LLM Gateway."""

    request_id: str
    provider: str
    model: str
    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    estimated_cost_cents: float
    cached: bool
    strategy_used: str


class FeedbackRequest(BaseModel):
    """User feedback on a response."""

    request_id: str
    rating: str = Field(..., pattern="^(positive|negative)$")
    comment: str | None = None


class EvalResult(BaseModel):
    """Result of an LLM as judge evaluation."""

    eval_id: str
    request_id: str
    provider: str
    score: float = Field(..., ge=1.0, le=5.0)
    reasoning: str
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    providers: dict[str, str]
