"""Gateway API routes."""

import logging
import uuid

from fastapi import APIRouter, HTTPException

from app.models import (
    GatewayRequest,
    GatewayResponse,
    FeedbackRequest,
)
from app.core.router import select_provider
from app.core.cache import compute_prompt_hash, get_cached_response, put_cached_response
from app.core.request_logger import log_request
from app.observability import (
    emit_request_latency,
    emit_token_usage,
    emit_estimated_cost,
    emit_cache_event,
    emit_provider_error,
    emit_feedback,
)
from app.eval import maybe_evaluate

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/v1/complete", response_model=GatewayResponse)
async def complete(request: GatewayRequest):
    """Route a completion request through the gateway.

    1. Check cache (if enabled)
    2. Select provider based on strategy
    3. Send request to provider
    4. Log request, emit metrics, cache response
    5. Optionally trigger eval pipeline
    """
    request_id = str(uuid.uuid4())
    provider = select_provider(request.strategy, request.provider)

    # Cache check
    if request.use_cache:
        prompt_hash = compute_prompt_hash(
            request.prompt,
            provider.name,
            provider.model,
            request.max_tokens,
            request.temperature,
        )
        cached = get_cached_response(prompt_hash)
        if cached:
            emit_cache_event(hit=True)
            log_request(
                request_id=request_id,
                client_id=request.client_id,
                prompt=request.prompt,
                provider=cached["provider"],
                model=cached["model"],
                strategy=request.strategy.value,
                content=cached["content"],
                input_tokens=int(cached["input_tokens"]),
                output_tokens=int(cached["output_tokens"]),
                latency_ms=0.0,
                estimated_cost_cents=0.0,
                cached=True,
            )
            return GatewayResponse(
                request_id=request_id,
                provider=cached["provider"],
                model=cached["model"],
                content=cached["content"],
                input_tokens=int(cached["input_tokens"]),
                output_tokens=int(cached["output_tokens"]),
                latency_ms=0.0,
                estimated_cost_cents=0.0,
                cached=True,
                strategy_used=request.strategy.value,
            )
        emit_cache_event(hit=False)

    # Call the provider
    try:
        result = await provider.complete(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
    except Exception as e:
        emit_provider_error(provider.name)
        logger.error(f"Provider {provider.name} failed: {e}")
        log_request(
            request_id=request_id,
            client_id=request.client_id,
            prompt=request.prompt,
            provider=provider.name,
            model=provider.model,
            strategy=request.strategy.value,
            content="",
            input_tokens=0,
            output_tokens=0,
            latency_ms=0.0,
            estimated_cost_cents=0.0,
            cached=False,
            error=str(e),
        )
        raise HTTPException(
            status_code=502,
            detail=f"Provider {provider.name} error: {str(e)}",
        )

    cost_cents = provider.estimate_cost_cents(
        result.input_tokens, result.output_tokens
    )

    # Emit metrics
    emit_request_latency(result.latency_ms)
    emit_token_usage(result.provider, result.input_tokens, result.output_tokens)
    emit_estimated_cost(result.provider, cost_cents)

    # Log request
    log_request(
        request_id=request_id,
        client_id=request.client_id,
        prompt=request.prompt,
        provider=result.provider,
        model=result.model,
        strategy=request.strategy.value,
        content=result.content,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        estimated_cost_cents=cost_cents,
        cached=False,
    )

    # Cache the response
    if request.use_cache:
        put_cached_response(
            prompt_hash=prompt_hash,
            provider=result.provider,
            model=result.model,
            content=result.content,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            estimated_cost_cents=cost_cents,
        )

    # Async eval (fire and forget)
    await maybe_evaluate(
        request_id=request_id,
        provider=result.provider,
        prompt=request.prompt,
        response_content=result.content,
    )

    return GatewayResponse(
        request_id=request_id,
        provider=result.provider,
        model=result.model,
        content=result.content,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        estimated_cost_cents=cost_cents,
        cached=False,
        strategy_used=request.strategy.value,
    )


@router.post("/v1/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback on a gateway response."""
    is_positive = feedback.rating == "positive"
    emit_feedback(is_positive)
    logger.info(
        f"Feedback for {feedback.request_id}: {feedback.rating}"
    )
    return {"status": "recorded", "request_id": feedback.request_id}
