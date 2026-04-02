"""LLM provider base class and provider registry."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderResponse:
    """Standardized response from any LLM provider."""

    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: float


class LLMProvider(ABC):
    """Base class for LLM providers."""

    name: str
    model: str

    # Cost per 1M tokens in cents
    input_cost_per_million: float
    output_cost_per_million: float

    @abstractmethod
    async def complete(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> ProviderResponse:
        """Send a completion request to the provider."""
        ...

    def estimate_cost_cents(
        self, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate estimated cost in cents."""
        input_cost = (input_tokens / 1_000_000) * self.input_cost_per_million
        output_cost = (
            output_tokens / 1_000_000
        ) * self.output_cost_per_million
        return round(input_cost + output_cost, 6)

    @abstractmethod
    async def health_check(self) -> str:
        """Return health status string."""
        ...
