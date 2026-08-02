import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


BACKEND_DIRECTORY = Path(__file__).resolve().parent
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

from api import app


class ScanRuleSelectionApiTests(unittest.TestCase):
    """Verify route selection only; mocked scans do not prove Semgrep execution."""

    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    @patch("api.scan", return_value={"vulnerabilities": []})
    def test_missing_rule_id_uses_compatible_default(self, scan):
        response = self.client.post(
            "/scan",
            data={"scan_mode": "single"},
            files={"file": ("test.php", b"<?php echo 'test';", "application/x-php")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["vulnerabilities"], [])
        self.assertEqual(
            response.json()["scan"],
            {
                "mode": "single",
                "language": "php",
                "rule_count": 1,
                "rule_id": "php-dangerous-unserialize",
                "source_file": "php-unserialize.yaml",
            },
        )
        self.assertEqual(Path(scan.call_args.args[1][0]).name, "php-unserialize.yaml")


    @patch(
        "api.scan",
        return_value={
            "vulnerabilities": [
                {
                    "id": "C.Users.Li.RuleForgeSAST.RuleForge-SAST.rules.php-dangerous-eval",
                    "rule": "C.Users.Li.RuleForgeSAST.RuleForge-SAST.rules.php-dangerous-eval",
                    "file": "temp.php",
                    "line": 1,
                    "category": "code-execution",
                    "severity": "CRITICAL",
                    "cwe": "CWE-95",
                    "description": "不安全的 PHP eval 代码执行",
                    "fix": ["避免执行用户可控代码", "使用安全的解析方式"],
                    "message": "Dangerous PHP eval usage",
                }
            ]
        },
    )
    def test_valid_php_rule_maps_to_catalog_yaml(self, scan):
        response = self.client.post(
            "/scan",
            data={"rule_id": "php-dangerous-eval", "scan_mode": "single"},
            files={"file": ("vulnerable.php", b"<?php eval($input);", "application/x-php")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["scan"]["rule_id"], "php-dangerous-eval")
        self.assertEqual(response.json()["scan"]["source_file"], "php-eval.yaml")
        self.assertEqual(Path(scan.call_args.args[1][0]).name, "php-eval.yaml")


        finding = response.json()["vulnerabilities"][0]
        self.assertEqual(finding["id"], "php-dangerous-eval")
        self.assertEqual(finding["rule"], "php-dangerous-eval")
        self.assertEqual(finding["file"], "vulnerable.php")
        self.assertEqual(finding["line"], 1)

        self.assertEqual(finding["category"], "code-execution")
        self.assertEqual(finding["severity"], "CRITICAL")
        self.assertEqual(finding["cwe"], "CWE-95")
        self.assertEqual(finding["description"], "不安全的 PHP eval 代码执行")
        self.assertEqual(
            finding["fix"],
            ["避免将用户可控输入传入 eval", "使用 json_decode 等安全的数据解析方式替代动态代码执行"],
        )
        self.assertEqual(finding["message"], "Dangerous PHP eval usage")

        self.assertNotIn("C.Users", response.text)
        self.assertNotIn("RuleForge-SAST", response.text)
        self.assertNotIn(str(BACKEND_DIRECTORY.parent), response.text)

    @patch("api.scan")
    def test_unknown_rule_id_returns_400_without_scanning(self, scan):
        response = self.client.post(
            "/scan",
            data={"rule_id": "php-rule-does-not-exist", "scan_mode": "single"},
            files={"file": ("test.php", b"<?php", "application/x-php")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown rule_id", response.json()["detail"])
        scan.assert_not_called()

    @patch("api.scan")
    def test_python_and_java_rules_return_400_without_scanning(self, scan):
        for rule_id in ("python-dangerous-eval", "java-command-execution"):
            with self.subTest(rule_id=rule_id):
                response = self.client.post(
                    "/scan",
                    data={"rule_id": rule_id, "scan_mode": "single"},
                    files={"file": ("test.php", b"<?php", "application/x-php")},
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn("does not support PHP scans", response.json()["detail"])

        scan.assert_not_called()

    @patch("api.scan")
    def test_path_traversal_rule_id_returns_400_without_scanning(self, scan):
        response = self.client.post(
            "/scan",
            data={"rule_id": "../../rules/php-eval.yaml", "scan_mode": "single"},
            files={"file": ("test.php", b"<?php", "application/x-php")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown rule_id", response.json()["detail"])
        self.assertNotIn(str(BACKEND_DIRECTORY.parent), response.text)
        self.assertNotIn("Traceback", response.text)
        scan.assert_not_called()

    @patch("api.scan", return_value={"vulnerabilities": []})
    def test_all_mode_uses_all_rules_for_language(self, scan):
        response = self.client.post(
            "/scan",
            data={"scan_mode": "all"},
            files={"file": ("vuln.py", b"eval(x)", "text/x-python")},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["scan"]["mode"], "all")
        self.assertEqual(response.json()["scan"]["language"], "python")
        self.assertEqual(response.json()["scan"]["rule_count"], 3)
        rule_paths = scan.call_args.args[1]
        self.assertEqual(len(rule_paths), 3)
        self.assertTrue(all(path.endswith(".yaml") for path in rule_paths))

    @patch("api.scan")
    def test_invalid_scan_mode_returns_400(self, scan):
        response = self.client.post(
            "/scan",
            data={"scan_mode": "bogus"},
            files={"file": ("test.php", b"<?php", "application/x-php")},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("scan_mode", response.json()["detail"])
        scan.assert_not_called()



if __name__ == "__main__":
    unittest.main()
