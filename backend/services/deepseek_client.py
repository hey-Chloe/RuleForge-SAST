"""Minimal DeepSeek client for defensive AI explanations."""

from __future__ import annotations

import os
from urllib.parse import urlparse

import httpx


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT_SECONDS = 15.0


class AIConfigurationError(RuntimeError):
    """Raised when the configured AI provider cannot be used."""


class AIUpstreamError(RuntimeError):
    """Raised when the upstream AI provider fails safely."""


class DeepSeekClient:
    """Call DeepSeek's OpenAI-compatible chat completion endpoint."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        normalized_key = api_key.strip()
        normalized_base_url = base_url.strip().rstrip("/")
        normalized_model = model.strip()
        parsed_url = urlparse(normalized_base_url)

        if not normalized_key:
            raise AIConfigurationError("AI explanation service is not configured")
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise AIConfigurationError("AI explanation service is not configured")
        if not normalized_model:
            raise AIConfigurationError("AI explanation service is not configured")

        self._api_key = normalized_key
        self._base_url = normalized_base_url
        self._model = normalized_model
        self._timeout = httpx.Timeout(timeout_seconds)
        self._transport = transport

    @classmethod
    def from_environment(cls) -> "DeepSeekClient":
        provider = os.getenv("AI_PROVIDER", "deepseek").strip().lower()
        if provider != "deepseek":
            raise AIConfigurationError("AI explanation service is not configured")

        return cls(
            api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            base_url=os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL),
            model=os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL),
        )

    async def explain(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": 800,
            "stream": False,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
        except httpx.TimeoutException as exc:
            raise AIUpstreamError("AI provider request timed out") from exc
        except httpx.RequestError as exc:
            raise AIUpstreamError("AI provider request failed") from exc

        if response.status_code != 200:
            raise AIUpstreamError(
                f"AI provider returned HTTP {response.status_code}"
            )

        try:
            response_data = response.json()
            content = response_data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIUpstreamError("AI provider returned an invalid response") from exc

        if not isinstance(content, str) or not content.strip():
            raise AIUpstreamError("AI provider returned an invalid response")
        return content
