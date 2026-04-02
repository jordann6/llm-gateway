"""Request logging to DynamoDB."""

import logging
import time
from datetime import datetime, timezone
from decimal import Decimal

from app.core import settings
from app.core.aws import dynamodb

logger = logging.getLogger(__name__)

table = dynamodb.Table(settings.DYNAMODB_REQUEST_LOG_TABLE)


def log_request(
    request_id: str,
    client_id: str,
    prompt: str,
    provider: str,
    model: str,
    strategy: str,
    content: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: float,
    estimated_cost_cents: float,
    cached: bool,
    error: str | None = None,
) -> None:
    """Write a request log entry to DynamoDB."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        expires_at = int(time.time()) + settings.REQUEST_LOG_TTL_SECONDS

        item = {
            "request_id": request_id,
            "timestamp": now,
            "client_id": client_id,
            "prompt_preview": prompt[:200],
            "provider": provider,
            "model": model,
            "strategy": strategy,
            "response_preview": content[:200],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": Decimal(str(latency_ms)),
            "estimated_cost_cents": Decimal(str(estimated_cost_cents)),
            "cached": cached,
            "expires_at": expires_at,
        }

        if error:
            item["error"] = error

        table.put_item(Item=item)
        logger.info(f"Logged request {request_id}")
    except Exception as e:
        logger.error(f"Failed to log request {request_id}: {e}")
