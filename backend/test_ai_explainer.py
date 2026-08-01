import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx


BACKEND_DIRECTORY = Path(__file__).resolve().parent
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from services.ai_explainer import AIInputError, explain_vulnerability
from services.deepseek_client import (
    AIConfigurationError,
    AIUpstreamError,
    DeepSeekClient,
)


VULNERABILITY = {
    "rule": "php-dangerous-eval",
    "severity": "CRITICAL",
    "cwe": "CWE-95",
    "category": "code-execution",
    "language": "php",
    "description": "不安全的 PHP eval 代码执行",
    "fix": ["避免将用户可控输入传入 eval"],
}

VALID_EXPLANATION = {
    "summary": "用户可控内容进入 eval 会造成高风险代码执行。",
    "root_cause": "应用将未经安全解析的数据交给动态代码执行函数。",
    "attack_impact": "可能破坏应用数据和服务完整性。",
    "recommendations": ["移除 eval", "使用受约束的数据解析方式"],
    "confidence": "high",
}


def _completion_response(content: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={"choices": [{"message": {"content": content}}]},
    )


class AIExplainerTests(unittest.IsolatedAsyncioTestCase):
    def _client(self, handler) -> DeepSeekClient:
        return DeepSeekClient(
            api_key="test-placeholder-not-a-real-key",
            transport=httpx.MockTransport(handler),
        )

    async def test_valid_json_explanation(self):
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/chat/completions")
            return _completion_response(json.dumps(VALID_EXPLANATION, ensure_ascii=False))

        result = await explain_vulnerability(VULNERABILITY, self._client(handler))

        self.assertEqual(result, VALID_EXPLANATION)

    async def test_markdown_wrapped_json_explanation(self):
        def handler(request: httpx.Request) -> httpx.Response:
            content = "```json\n" + json.dumps(VALID_EXPLANATION, ensure_ascii=False) + "\n```"
            return _completion_response(content)

        result = await explain_vulnerability(VULNERABILITY, self._client(handler))

        self.assertEqual(result, VALID_EXPLANATION)

    async def test_invalid_model_json_returns_safe_fallback(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return _completion_response("not valid json")

        result = await explain_vulnerability(VULNERABILITY, self._client(handler))

        self.assertEqual(result["confidence"], "low")
        self.assertEqual(result["summary"], VULNERABILITY["description"])
        self.assertEqual(result["recommendations"], VULNERABILITY["fix"])
        self.assertEqual(
            set(result),
            {
                "summary",
                "root_cause",
                "attack_impact",
                "recommendations",
                "confidence",
            },
        )

    async def test_incomplete_model_json_returns_safe_fallback(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return _completion_response('{"summary": "字段不完整"}')

        result = await explain_vulnerability(VULNERABILITY, self._client(handler))

        self.assertEqual(result["confidence"], "low")
        self.assertEqual(result["summary"], VULNERABILITY["description"])

    async def test_missing_api_key_is_configuration_error(self):
        with patch.dict(
            os.environ,
            {"AI_PROVIDER": "deepseek", "DEEPSEEK_API_KEY": ""},
            clear=False,
        ):
            with self.assertRaisesRegex(
                AIConfigurationError,
                "AI explanation service is not configured",
            ):
                await explain_vulnerability(VULNERABILITY)

    async def test_upstream_timeout_is_safe_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("simulated timeout", request=request)

        with self.assertRaisesRegex(AIUpstreamError, "timed out"):
            await explain_vulnerability(VULNERABILITY, self._client(handler))

    async def test_upstream_http_error_is_safe_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(429, json={"error": "upstream details"})

        with self.assertRaisesRegex(AIUpstreamError, "HTTP 429") as context:
            await explain_vulnerability(VULNERABILITY, self._client(handler))
        self.assertNotIn("upstream details", str(context.exception))

    async def test_invalid_upstream_json_is_safe_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, content=b"not-json")

        with self.assertRaisesRegex(AIUpstreamError, "invalid response"):
            await explain_vulnerability(VULNERABILITY, self._client(handler))

    async def test_rejects_non_vulnerability_fields(self):
        with self.assertRaisesRegex(AIInputError, "unsupported fields"):
            await explain_vulnerability(
                {**VULNERABILITY, "shell_command": "not accepted"},
                self._client(lambda request: _completion_response("{}")),
            )


if __name__ == "__main__":
    unittest.main()
