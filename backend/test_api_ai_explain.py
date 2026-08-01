import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


BACKEND_DIRECTORY = Path(__file__).resolve().parent
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from api import app
from services.deepseek_client import AIUpstreamError


VULNERABILITY = {
    "rule": "php-dangerous-eval",
    "severity": "CRITICAL",
    "cwe": "CWE-95",
    "category": "code-execution",
    "language": "php",
    "description": "不安全的 PHP eval 代码执行",
    "fix": ["避免将用户可控输入传入 eval"],
}

EXPLANATION = {
    "summary": "动态执行用户可控内容可能导致代码执行。",
    "root_cause": "不可信数据进入动态执行函数。",
    "attack_impact": "可能影响应用的机密性、完整性和可用性。",
    "recommendations": ["移除 eval", "使用安全解析方式"],
    "confidence": "high",
}


class AIExplainApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    @patch("api.explain_vulnerability", new_callable=AsyncMock)
    def test_success(self, explain):
        explain.return_value = EXPLANATION

        response = self.client.post("/ai/explain", json=VULNERABILITY)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EXPLANATION)
        explain.assert_awaited_once_with(VULNERABILITY)

    def test_invalid_input_returns_400(self):
        response = self.client.post(
            "/ai/explain",
            json={"rule": "php-dangerous-eval"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("missing required", response.json()["detail"])

    def test_missing_configuration_returns_503(self):
        with patch.dict(
            os.environ,
            {"AI_PROVIDER": "deepseek", "DEEPSEEK_API_KEY": ""},
            clear=False,
        ):
            response = self.client.post("/ai/explain", json=VULNERABILITY)

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json()["detail"],
            "AI explanation service is not configured",
        )

    @patch("api.explain_vulnerability", new_callable=AsyncMock)
    def test_timeout_returns_502(self, explain):
        explain.side_effect = AIUpstreamError("AI provider request timed out")

        response = self.client.post("/ai/explain", json=VULNERABILITY)

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "AI provider request timed out")

    @patch("api.explain_vulnerability", new_callable=AsyncMock)
    def test_upstream_http_error_returns_502(self, explain):
        explain.side_effect = AIUpstreamError("AI provider returned HTTP 429")

        response = self.client.post("/ai/explain", json=VULNERABILITY)

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "AI provider returned HTTP 429")
        self.assertNotIn("Traceback", response.text)


if __name__ == "__main__":
    unittest.main()
