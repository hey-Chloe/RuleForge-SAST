import unittest

from backend.rules.metadata_parser import parse_metadata


class MetadataParserTests(unittest.TestCase):
    def test_parse_complete_metadata(self):
        result = {
            "check_id": "php-dangerous-unserialize",
            "extra": {
                "severity": "ERROR",
                "message": "Semgrep fallback message",
                "metadata": {
                    "rule_id": "PHP-UNSERIALIZE-001",
                    "category": "deserialization",
                    "severity": "HIGH",
                    "cwe": "CWE-502",
                    "description": "不安全反序列化漏洞",
                    "fix": [
                        "避免用户可控输入进入 unserialize",
                        "使用安全序列化方式",
                    ],
                },
            },
        }

        self.assertEqual(
            parse_metadata(result),
            {
                "rule_id": "PHP-UNSERIALIZE-001",
                "category": "deserialization",
                "severity": "HIGH",
                "cwe": "CWE-502",
                "description": "不安全反序列化漏洞",
                "fix": [
                    "避免用户可控输入进入 unserialize",
                    "使用安全序列化方式",
                ],
            },
        )

    def test_parse_missing_metadata_uses_safe_defaults(self):
        result = {
            "check_id": "php-dangerous-unserialize",
            "extra": {
                "severity": "ERROR",
                "message": "Dangerous unserialize usage",
            },
        }

        self.assertEqual(
            parse_metadata(result),
            {
                "rule_id": "php-dangerous-unserialize",
                "category": "unknown",
                "severity": "ERROR",
                "cwe": "N/A",
                "description": "Dangerous unserialize usage",
                "fix": [],
            },
        )

    def test_parse_string_fix_converts_it_to_list(self):
        result = {
            "check_id": "php-dangerous-unserialize",
            "extra": {
                "metadata": {
                    "fix": "避免用户可控输入进入 unserialize",
                },
            },
        }

        parsed = parse_metadata(result)

        self.assertEqual(parsed["fix"], ["避免用户可控输入进入 unserialize"])
        self.assertIsInstance(parsed["fix"], list)
        self.assertEqual(parsed["severity"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
