import sys
import unittest
from pathlib import Path


BACKEND_DIRECTORY = Path(__file__).resolve().parent
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from services.rule_catalog import load_rule_catalog


class RuleCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = load_rule_catalog()

    def test_discovers_all_current_rules(self):
        self.assertEqual(len(self.rules), 18)

    def test_php_unserialize_has_complete_metadata(self):
        rule = next(
            item for item in self.rules
            if item["id"] == "php-dangerous-unserialize"
        )

        self.assertEqual(rule["languages"], ["php"])
        self.assertEqual(rule["message"], "Dangerous unserialize usage")
        self.assertEqual(rule["semgrep_severity"], "ERROR")
        self.assertEqual(rule["category"], "deserialization")
        self.assertEqual(rule["severity"], "HIGH")
        self.assertEqual(rule["cwe"], "CWE-502")
        self.assertEqual(rule["description"], "不安全反序列化漏洞")
        self.assertTrue(rule["fix"])
        self.assertEqual(rule["source_file"], "php-unserialize.yaml")

    def test_legacy_rule_uses_safe_metadata_defaults(self):
        rule = next(item for item in self.rules if item["id"] == "hardcoded-secret")

        self.assertEqual(rule["category"], "unknown")
        self.assertEqual(rule["severity"], "WARNING")
        self.assertEqual(rule["cwe"], "N/A")
        self.assertEqual(rule["description"], "Possible hardcoded secret.")
        self.assertEqual(rule["fix"], [])
        self.assertEqual(rule["source_file"], "hardcoded-secrets.yaml")


if __name__ == "__main__":
    unittest.main()
