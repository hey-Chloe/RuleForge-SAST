import json
import os
import sqlite3
import sys
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient


BACKEND_DIRECTORY = Path(__file__).resolve().parent
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from api import app
from database.ai_usage import DATABASE_PATH
from services.ai_suggest import (
    DAILY_BUDGET_USD,
    DAILY_REQUEST_LIMIT,
    build_request_hash,
)
from services.openrouter_client import OpenRouterClient


SUGGESTION = {
    "summary": "动态执行用户可控内容可能导致代码执行。",
    "risk": "攻击者可执行任意代码，影响机密性、完整性和可用性。",
    "root_cause": "不可信数据进入动态执行函数。",
    "suggested_code": "if (is_allowed($input)) { /* 安全处理 */ }",
    "steps": ["移除 eval", "使用安全解析方式"],
    "caveats": ["AI 建议，尚未经过 Semgrep 修复验证"],
}

USAGE = {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "cost": 0.001,
}


def _mock_transport(
    content: str,
    usage: dict | None = None,
    finish_reason: str = "stop",
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"content": content},
                        "finish_reason": finish_reason,
                    }
                ],
                "usage": usage or USAGE,
            },
        )

    return httpx.MockTransport(handler)


def _make_client(
    content: str,
    usage: dict | None = None,
    finish_reason: str = "stop",
) -> OpenRouterClient:
    return OpenRouterClient(
        api_key="test-key",
        transport=_mock_transport(content, usage, finish_reason),
    )



def _vulnerability(client_id: str) -> dict:
    return {
        "client_id": client_id,
        "filename": "test.php",
        "language": "php",
        "rule_id": "php-dangerous-eval",
        "severity": "CRITICAL",
        "cwe": "CWE-95",
        "category": "code-execution",
        "description": "不安全的 PHP eval 代码执行",
        "code_snippet": "eval($_GET['cmd']);",
        "rule_fix": ["避免将用户可控输入传入 eval"],
    }


class AISuggestApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # 每个测试使用独立 client_id，避免共享数据库导致额度/预算相互干扰。
        self.client_id = "test-" + uuid.uuid4().hex[:16]
        # 清空 AI 用量与缓存表，避免跨测试的缓存/额度状态泄漏。
        connection = sqlite3.connect(str(DATABASE_PATH))
        try:
            connection.execute("DELETE FROM ai_usage")
            connection.execute("DELETE FROM ai_suggestion_cache")
            connection.commit()
        finally:
            connection.close()

    def tearDown(self):
        self.client.close()


    def test_missing_api_key_returns_503(self):
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": ""},
            clear=False,
        ):
            response = self.client.post(
                "/ai/suggest-fix", json=_vulnerability(self.client_id)
            )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["detail"],
            "AI suggestion service is not configured",
        )

    def test_normal_structured_response(self):
        client = _make_client(json.dumps(SUGGESTION, ensure_ascii=False))
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key"},
            clear=False,
        ):
            with patch("services.ai_suggest.OpenRouterClient.from_environment", return_value=client):
                response = self.client.post(
                    "/ai/suggest-fix", json=_vulnerability(self.client_id)
                )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["suggestion"], SUGGESTION)
        self.assertFalse(body["cached"])
        self.assertIn("remaining_requests", body)
        self.assertIn("used_budget_usd", body)
        self.assertEqual(body["daily_budget_usd"], DAILY_BUDGET_USD)

    def test_invalid_json_returns_502(self):
        client = _make_client("not-json-at-all")
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key"},
            clear=False,
        ):
            with patch("services.ai_suggest.OpenRouterClient.from_environment", return_value=client):
                response = self.client.post(
                    "/ai/suggest-fix", json=_vulnerability(self.client_id)
                )

        self.assertEqual(response.status_code, 502)
        # 不向前端暴露原始模型内容，只返回简洁提示。
        self.assertIn("invalid JSON", response.json()["detail"])
        self.assertNotIn("not-json-at-all", response.json()["detail"])

    def test_truncated_response_returns_502(self):
        # finish_reason=length 表示响应因达到 max_tokens 被截断。
        client = _make_client(
            '{"summary": "被截断的响应',
            finish_reason="length",
        )
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key"},
            clear=False,
        ):
            with patch("services.ai_suggest.OpenRouterClient.from_environment", return_value=client):
                response = self.client.post(
                    "/ai/suggest-fix", json=_vulnerability(self.client_id)
                )

        self.assertEqual(response.status_code, 502)
        self.assertIn("被截断", response.json()["detail"])
        # 不暴露残缺的原始 JSON。
        self.assertNotIn("被截断的响应", response.json()["detail"])

    def test_markdown_json_response_parses(self):
        # 模型擅自套上 ```json 代码块，应被安全去除后正常解析。
        markdown_content = (
            "```json\n"
            + json.dumps(SUGGESTION, ensure_ascii=False)
            + "\n```"
        )
        client = _make_client(markdown_content)
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key"},
            clear=False,
        ):
            with patch("services.ai_suggest.OpenRouterClient.from_environment", return_value=client):
                response = self.client.post(
                    "/ai/suggest-fix", json=_vulnerability(self.client_id)
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["suggestion"], SUGGESTION)

    def test_cache_hit_does_not_call_model(self):

        # 第一次调用生成缓存。
        client = _make_client(json.dumps(SUGGESTION, ensure_ascii=False))
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key"},
            clear=False,
        ):
            with patch("services.ai_suggest.OpenRouterClient.from_environment", return_value=client):
                first = self.client.post(
                    "/ai/suggest-fix", json=_vulnerability(self.client_id)
                )
        self.assertEqual(first.status_code, 200)
        self.assertFalse(first.json()["cached"])

        # 第二次相同请求应命中缓存，不再调用模型。
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key"},
            clear=False,
        ):
            with patch(
                "services.ai_suggest.OpenRouterClient.from_environment",
                side_effect=AssertionError("model should not be called"),
            ):
                second = self.client.post(
                    "/ai/suggest-fix", json=_vulnerability(self.client_id)
                )

        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.json()["cached"])
        self.assertEqual(second.json()["suggestion"], SUGGESTION)

    def test_daily_request_limit_exceeded(self):
        client = _make_client(json.dumps(SUGGESTION, ensure_ascii=False))
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key"},
            clear=False,
        ):
            with patch("services.ai_suggest.OpenRouterClient.from_environment", return_value=client):
                # 用尽每日请求次数。每次使用不同代码片段，避免命中缓存。
                for i in range(DAILY_REQUEST_LIMIT):
                    payload = _vulnerability(self.client_id)
                    payload["code_snippet"] = f"eval($_GET['cmd{i}']);"
                    self.client.post("/ai/suggest-fix", json=payload)
                # 下一次（新代码片段）应返回 429。
                payload = _vulnerability(self.client_id)
                payload["code_snippet"] = "eval($_GET['final']);"
                response = self.client.post("/ai/suggest-fix", json=payload)

        self.assertEqual(response.status_code, 429)
        self.assertIn("已达上限", response.json()["detail"])

    def test_daily_budget_exceeded(self):
        client = _make_client(
            json.dumps(SUGGESTION, ensure_ascii=False),
            usage={"prompt_tokens": 1, "completion_tokens": 1, "cost": DAILY_BUDGET_USD},
        )
        with patch.dict(
            os.environ,
            {"OPENROUTER_API_KEY": "test-key"},
            clear=False,
        ):
            with patch("services.ai_suggest.OpenRouterClient.from_environment", return_value=client):
                # 第一次调用即达到预算上限。
                self.client.post(
                    "/ai/suggest-fix", json=_vulnerability(self.client_id)
                )
                # 下一次（新代码片段，避免命中缓存）应返回 429。
                payload = _vulnerability(self.client_id)
                payload["code_snippet"] = "eval($_GET['other']);"
                response = self.client.post("/ai/suggest-fix", json=payload)

        self.assertEqual(response.status_code, 429)
        self.assertIn("费用额度已用尽", response.json()["detail"])


    def test_code_snippet_too_long(self):
        payload = _vulnerability(self.client_id)
        payload["code_snippet"] = "x" * 5000
        response = self.client.post("/ai/suggest-fix", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("超过最大长度", response.json()["detail"])

    def test_missing_client_id_returns_400(self):
        payload = _vulnerability(self.client_id)
        del payload["client_id"]
        response = self.client.post("/ai/suggest-fix", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("client_id", response.json()["detail"])

    def test_invalid_client_id_returns_400(self):
        payload = _vulnerability(self.client_id)
        payload["client_id"] = "bad id!"
        response = self.client.post("/ai/suggest-fix", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn("client_id", response.json()["detail"])

    def test_request_hash_is_stable(self):
        h1 = build_request_hash(
            rule_id="php-dangerous-eval",
            language="php",
            code_snippet="eval($_GET['cmd']);",
            model="openai/gpt-4o-mini",
        )
        h2 = build_request_hash(
            rule_id="php-dangerous-eval",
            language="php",
            code_snippet="eval($_GET['cmd']);",
            model="openai/gpt-4o-mini",
        )
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)


if __name__ == "__main__":
    unittest.main()
