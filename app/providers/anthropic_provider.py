"""Anthropic provider implementation using httpx."""

import time
import logging
import httpx
from app.providers import LLMProvider, ProviderResponse
from app.core import settings

logger = logging.getLogger(__name__)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude Haiku 4.5 provider."""

    name = "anthropic"
    model = "claude-haiku-4-5-20251001"
    input_cost_per_million = 100.0  # cents
    output_cost_per_million = 500.0  # cents

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def complete(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> ProviderResponse:
        """Send completion request to Anthropic."""
        start = time.monotonic()

        response = await self.client.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
        )
        response.raise_for_status()

        elapsed_ms = (time.monotonic() - start) * 1000
        data = response.json()

        return ProviderResponse(
            content=data["content"][0]["text"],
            model=data["model"],
            provider=self.name,
            input_tokens=data["usage"]["input_tokens"],
            output_tokens=data["usage"]["output_tokens"],
            latency_ms=round(elapsed_ms, 2),
        )

    async def health_check(self) -> str:
        """Check if Anthropic API key is configured."""
        if self.api_key and self.api_key != "placeholder":
            return "configured"
        return "no_api_key"
