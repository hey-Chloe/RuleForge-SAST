"""DeepSeek-compatible AI client for fix suggestions.

保留 OpenRouterClient 类名，以兼容项目现有导入。
API Key 优先从 DEEPSEEK_API_KEY 读取；
若未设置，则兼容读取原有的 OPENROUTER_API_KEY。
"""

from __future__ import annotations

import json
import os
from urllib.parse import urlparse

import httpx


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_MAX_OUTPUT_TOKENS = 1200
DEFAULT_MAX_CODE_CHARS = 4000


class AIConfigurationError(RuntimeError):
    """AI 服务配置不正确时抛出。"""


class AIUpstreamError(RuntimeError):
    """上游 AI 服务请求失败时抛出。"""


def _strip_markdown_fence(content: str) -> str:
    """安全去除模型返回内容外围的 Markdown 代码块。

    支持 ```json 与 ``` 两种围栏，允许围栏前有空白。
    若内容不是代码块，原样返回；不猜测或补全残缺 JSON。
    """
    stripped = content.strip()
    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()
    if len(lines) < 2:
        return stripped

    # 第一行可能是 ``` 或 ```json（允许带语言标识）。
    first = lines[0].strip()
    if not first.startswith("```"):
        return stripped

    # 找到闭合围栏（最后一行）。
    if not lines[-1].strip().startswith("```"):
        return stripped

    return "\n".join(lines[1:-1]).strip()


class OpenRouterClient:

    """调用 DeepSeek 的 OpenAI 兼容聊天补全接口。

    为了兼容项目中已有的导入，暂时保留 OpenRouterClient 类名。
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        normalized_key = api_key.strip()
        normalized_base_url = base_url.strip().rstrip("/")
        normalized_model = model.strip()

        parsed_url = urlparse(normalized_base_url)

        if not normalized_key:
            raise AIConfigurationError(
                "AI suggestion service is not configured"
            )

        if (
            parsed_url.scheme not in {"http", "https"}
            or not parsed_url.netloc
        ):
            raise AIConfigurationError(
                "AI suggestion service is not configured"
            )

        if not normalized_model:
            raise AIConfigurationError(
                "AI suggestion service is not configured"
            )

        if timeout_seconds <= 0:
            raise AIConfigurationError(
                "AI request timeout must be greater than 0"
            )

        if max_output_tokens <= 0:
            raise AIConfigurationError(
                "AI max output tokens must be greater than 0"
            )

        self._api_key = normalized_key
        self._base_url = normalized_base_url
        self._model = normalized_model
        self._timeout = httpx.Timeout(timeout_seconds)
        self._max_output_tokens = max_output_tokens
        self._transport = transport

    @classmethod
    def from_environment(cls) -> "OpenRouterClient":
        """从环境变量创建客户端。"""

        api_key = (
            os.getenv("DEEPSEEK_API_KEY", "").strip()
            or os.getenv("OPENROUTER_API_KEY", "").strip()
        )

        return cls(
            api_key=api_key,
            base_url=os.getenv(
                "AI_BASE_URL",
                DEFAULT_BASE_URL,
            ),
            model=os.getenv(
                "AI_MODEL",
                DEFAULT_MODEL,
            ),
            timeout_seconds=float(
                os.getenv(
                    "AI_REQUEST_TIMEOUT_SECONDS",
                    str(DEFAULT_TIMEOUT_SECONDS),
                )
            ),
            max_output_tokens=int(
                os.getenv(
                    "AI_MAX_OUTPUT_TOKENS",
                    str(DEFAULT_MAX_OUTPUT_TOKENS),
                )
            ),
        )

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict,
    ) -> tuple[str, dict]:
        """调用模型并返回 `(content, usage)`。

        content 是模型返回的 JSON 字符串。
        usage 仅包含 token、费用等元数据，不包含密钥。
        """

        schema_text = json.dumps(
            response_schema,
            ensure_ascii=False,
            indent=2,
        )

        enhanced_system_prompt = (
            f"{system_prompt}\n\n"
            "你必须只返回一个合法的 JSON 对象。\n"
            "不要使用 Markdown 代码块，不要添加解释或其他文字。\n"
            "返回结果必须符合下面的 JSON Schema：\n"
            f"{schema_text}"
        )

        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": "system",
                    "content": enhanced_system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "max_tokens": self._max_output_tokens,
            "stream": False,
            "response_format": {
                "type": "json_object",
            },
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
            raise AIUpstreamError(
                "AI provider request timed out"
            ) from exc

        except httpx.RequestError as exc:
            raise AIUpstreamError(
                f"AI provider request failed: {exc}"
            ) from exc

        if response.status_code != 200:
            try:
                error_data = response.json()
                error_detail = json.dumps(
                    error_data,
                    ensure_ascii=False,
                )
            except ValueError:
                error_detail = response.text.strip()

            if len(error_detail) > 1000:
                error_detail = error_detail[:1000] + "..."

            raise AIUpstreamError(
                "AI provider returned HTTP "
                f"{response.status_code}: {error_detail}"
            )

        try:
            response_data = response.json()

            choice = response_data["choices"][0]
            content = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
            usage = response_data.get("usage") or {}

        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise AIUpstreamError(
                "AI provider returned an invalid response"
            ) from exc

        if not isinstance(content, str) or not content.strip():
            raise AIUpstreamError(
                "AI provider returned empty content"
            )

        if not isinstance(usage, dict):
            usage = {}

        content = content.strip()

        # 检查上游 finish_reason：若为 length，说明响应因达到
        # max_tokens 上限被截断，返回明确提示，不尝试补全残缺 JSON。
        if finish_reason == "length":
            raise AIUpstreamError(
                "AI 响应被截断，请重试"
            )

        # 有些模型即使被要求只输出 JSON，
        # 仍可能擅自套上 Markdown 代码块。
        content = _strip_markdown_fence(content)

        # 提前检查是否为合法 JSON，
        # 避免后续只看到含糊的解析错误。
        # 不向前端暴露原始模型内容，只返回简洁提示。
        try:
            json.loads(content)
        except json.JSONDecodeError as exc:
            raise AIUpstreamError(
                "AI provider returned invalid JSON"
            ) from exc

        return content, usage


