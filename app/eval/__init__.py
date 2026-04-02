"""Eval pipeline: LLM as judge for response quality scoring."""

import logging
import random
import re
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from app.core import settings
from app.core.aws import dynamodb
from app.providers.openai_provider import OpenAIProvider
from app.observability import emit_eval_score

logger = logging.getLogger(__name__)

eval_table = dynamodb.Table(settings.DYNAMODB_EVAL_TABLE)

JUDGE_PROMPT_TEMPLATE = """You are an expert LLM output quality evaluator. Rate the following response on a scale of 1 to 5 based on accuracy, helpfulness, clarity, and completeness.

User Prompt: {prompt}

LLM Response: {response}

Respond with ONLY a JSON object in this exact format (no markdown, no extra text):
{{"score": <number 1-5>, "reasoning": "<brief explanation>"}}"""


async def maybe_evaluate(
    request_id: str,
    provider: str,
    prompt: str,
    response_content: str,
) -> None:
    """Probabilistically evaluate a response using LLM as judge.

    Samples at the configured rate to avoid evaluating every request.
    Uses OpenAI as the judge to avoid self evaluation bias when
    the original provider is also OpenAI (in production you would
    use a different judge, but for a portfolio demo this is fine).
    """
    if random.random() > settings.EVAL_SAMPLE_RATE:
        return

    try:
        judge = OpenAIProvider()
        judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
            prompt=prompt[:500],
            response=response_content[:1000],
        )

        result = await judge.complete(
            prompt=judge_prompt,
            max_tokens=256,
            temperature=0.0,
        )

        score, reasoning = _parse_eval_response(result.content)

        if score is None:
            logger.warning(f"Could not parse eval response for {request_id}")
            return

        eval_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        eval_table.put_item(
            Item={
                "eval_id": eval_id,
                "timestamp": now,
                "request_id": request_id,
                "provider": provider,
                "score": Decimal(str(score)),
                "reasoning": reasoning,
                "judge_model": judge.model,
                "judge_input_tokens": result.input_tokens,
                "judge_output_tokens": result.output_tokens,
                "expires_at": int(
                    datetime.now(timezone.utc).timestamp()
                ) + 2592000,  # 30 days
            }
        )

        emit_eval_score(provider, score)
        logger.info(
            f"Eval for {request_id}: provider={provider} score={score}"
        )

    except Exception as e:
        logger.error(f"Eval failed for {request_id}: {e}")


def _parse_eval_response(content: str) -> tuple[float | None, str]:
    """Extract score and reasoning from the judge response."""
    try:
        import json

        cleaned = content.strip()
        # Handle potential markdown code blocks
        if cleaned.startswith("```"):
            cleaned = re.sub(r"```json?\s*", "", cleaned)
            cleaned = re.sub(r"```\s*$", "", cleaned)

        parsed = json.loads(cleaned)
        score = float(parsed.get("score", 0))
        reasoning = parsed.get("reasoning", "")

        if 1.0 <= score <= 5.0:
            return score, reasoning
        return None, ""
    except (json.JSONDecodeError, ValueError, KeyError):
        return None, ""
