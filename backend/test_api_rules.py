import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


BACKEND_DIRECTORY = Path(__file__).resolve().parent
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from api import app
from services.rule_catalog import RuleCatalogError


class RulesApiTests(unittest.TestCase):
    def test_get_rules_returns_current_catalog(self):
        with TestClient(app) as client:
            response = client.get("/rules")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("rules", payload)
        self.assertIsInstance(payload["rules"], list)
        self.assertEqual(len(payload["rules"]), 18)

        rule = next(
            item for item in payload["rules"]
            if item["id"] == "php-dangerous-unserialize"
        )
        self.assertEqual(rule["severity"], "HIGH")
        self.assertEqual(rule["cwe"], "CWE-502")
        self.assertEqual(rule["source_file"], "php-unserialize.yaml")

    @patch("api.load_rule_catalog", side_effect=RuleCatalogError("catalog unavailable"))
    def test_get_rules_returns_clear_error_without_traceback(self, _load_rule_catalog):
        with TestClient(app) as client:
            response = client.get("/rules")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {"detail": "Unable to load local rule catalog: catalog unavailable"},
        )
        self.assertNotIn("Traceback", response.text)


if __name__ == "__main__":
    unittest.main()
