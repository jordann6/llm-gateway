"""OpenAI provider implementation using httpx."""

import time
import logging
import httpx
from app.providers import LLMProvider, ProviderResponse
from app.core import settings

logger = logging.getLogger(__name__)

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4o-mini provider."""

    name = "openai"
    model = "gpt-4o-mini"
    input_cost_per_million = 15.0  # cents
    output_cost_per_million = 60.0  # cents

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def complete(
        self, prompt: str, max_tokens: int, temperature: float
    ) -> ProviderResponse:
        """Send completion request to OpenAI."""
        start = time.monotonic()

        response = await self.client.post(
            OPENAI_API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
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
            content=data["choices"][0]["message"]["content"],
            model=data["model"],
            provider=self.name,
            input_tokens=data["usage"]["prompt_tokens"],
            output_tokens=data["usage"]["completion_tokens"],
            latency_ms=round(elapsed_ms, 2),
        )

    async def health_check(self) -> str:
        """Check if OpenAI API key is configured."""
        if self.api_key and self.api_key != "placeholder":
            return "configured"
        return "no_api_key"
