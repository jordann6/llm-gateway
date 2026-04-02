"""CloudWatch custom metrics for the LLM Gateway."""

import logging
from datetime import datetime, timezone

from app.core import settings
from app.core.aws import cloudwatch

logger = logging.getLogger(__name__)

NAMESPACE = settings.CLOUDWATCH_NAMESPACE


def _put_metric(
    metric_name: str,
    value: float,
    unit: str,
    dimensions: list[dict] | None = None,
) -> None:
    """Publish a single metric to CloudWatch."""
    try:
        metric_data = {
            "MetricName": metric_name,
            "Value": value,
            "Unit": unit,
            "Timestamp": datetime.now(timezone.utc),
        }
        if dimensions:
            metric_data["Dimensions"] = dimensions

        cloudwatch.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[metric_data],
        )
    except Exception as e:
        logger.warning(f"Failed to publish metric {metric_name}: {e}")


def emit_request_latency(latency_ms: float) -> None:
    """Emit request latency metric."""
    _put_metric("RequestLatencyMs", latency_ms, "Milliseconds")


def emit_token_usage(
    provider: str, input_tokens: int, output_tokens: int
) -> None:
    """Emit token usage metrics by provider."""
    dims = [{"Name": "Provider", "Value": provider}]
    _put_metric("InputTokens", float(input_tokens), "Count", dims)
    _put_metric("OutputTokens", float(output_tokens), "Count", dims)


def emit_estimated_cost(provider: str, cost_cents: float) -> None:
    """Emit estimated cost metric by provider."""
    dims = [{"Name": "Provider", "Value": provider}]
    _put_metric("EstimatedCostCents", cost_cents, "None", dims)


def emit_cache_event(hit: bool) -> None:
    """Emit cache hit or miss metric."""
    if hit:
        _put_metric("CacheHit", 1.0, "Count")
    else:
        _put_metric("CacheMiss", 1.0, "Count")


def emit_provider_error(provider: str) -> None:
    """Emit provider error metric."""
    dims = [{"Name": "Provider", "Value": provider}]
    _put_metric("ProviderError", 1.0, "Count", dims)


def emit_eval_score(provider: str, score: float) -> None:
    """Emit eval quality score metric."""
    dims = [{"Name": "Provider", "Value": provider}]
    _put_metric("EvalScore", score, "None", dims)


def emit_feedback(positive: bool) -> None:
    """Emit feedback signal metric."""
    if positive:
        _put_metric("FeedbackPositive", 1.0, "Count")
    else:
        _put_metric("FeedbackNegative", 1.0, "Count")
