"""Routing logic to select the best provider based on strategy."""

import logging
from app.models import RoutingStrategy, Provider
from app.providers import LLMProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider

logger = logging.getLogger(__name__)

# Provider registry
_providers: dict[str, LLMProvider] = {}


def get_providers() -> dict[str, LLMProvider]:
    """Lazy initialize and return provider registry."""
    global _providers
    if not _providers:
        _providers = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
        }
    return _providers


# Strategy rankings (lower index = preferred)
COST_RANKING = ["openai", "anthropic"]
LATENCY_RANKING = ["openai", "anthropic"]
QUALITY_RANKING = ["anthropic", "openai"]


def select_provider(
    strategy: RoutingStrategy,
    preferred_provider: Provider | None = None,
) -> LLMProvider:
    """Select a provider based on routing strategy.

    If a specific provider is requested, use that directly.
    Otherwise, pick the top ranked provider for the strategy.
    """
    providers = get_providers()

    if preferred_provider:
        provider_name = preferred_provider.value
        if provider_name in providers:
            logger.info(f"Using explicitly requested provider: {provider_name}")
            return providers[provider_name]

    if strategy == RoutingStrategy.COST:
        ranking = COST_RANKING
    elif strategy == RoutingStrategy.LATENCY:
        ranking = LATENCY_RANKING
    else:
        ranking = QUALITY_RANKING

    selected = ranking[0]
    logger.info(
        f"Strategy '{strategy.value}' selected provider: {selected}"
    )
    return providers[selected]
