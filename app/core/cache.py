"""DynamoDB prompt cache with TTL."""

import hashlib
import json
import logging
import time
from decimal import Decimal
from typing import Any

from app.core import settings
from app.core.aws import dynamodb

logger = logging.getLogger(__name__)

table = dynamodb.Table(settings.DYNAMODB_CACHE_TABLE)


def compute_prompt_hash(
    prompt: str, provider: str, model: str, max_tokens: int, temperature: float
) -> str:
    """Create a deterministic hash for cache lookup."""
    key = json.dumps(
        {
            "prompt": prompt,
            "provider": provider,
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        sort_keys=True,
    )
    return hashlib.sha256(key.encode()).hexdigest()


def get_cached_response(prompt_hash: str) -> dict[str, Any] | None:
    """Look up a cached response by prompt hash."""
    try:
        response = table.get_item(Key={"prompt_hash": prompt_hash})
        item = response.get("Item")
        if item:
            logger.info(f"Cache hit for hash {prompt_hash[:12]}...")
            return item
        return None
    except Exception as e:
        logger.warning(f"Cache lookup failed: {e}")
        return None


def put_cached_response(
    prompt_hash: str,
    provider: str,
    model: str,
    content: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: float,
    estimated_cost_cents: float,
) -> None:
    """Store a response in the cache with TTL."""
    try:
        expires_at = int(time.time()) + settings.CACHE_TTL_SECONDS
        table.put_item(
            Item={
                "prompt_hash": prompt_hash,
                "provider": provider,
                "model": model,
                "content": content,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": Decimal(str(latency_ms)),
                "estimated_cost_cents": Decimal(str(estimated_cost_cents)),
                "expires_at": expires_at,
                "cached_at": int(time.time()),
            }
        )
        logger.info(f"Cached response for hash {prompt_hash[:12]}...")
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")
