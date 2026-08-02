import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from backend.engine.semgrep_runner import scan
from backend.models.vulnerability import Vulnerability


class SemgrepRunnerTests(unittest.TestCase):
    @patch("backend.engine.semgrep_runner.subprocess.run")
    def test_scan_builds_vulnerabilities_with_and_without_metadata(self, run):
        semgrep_output = {
            "results": [
                {
                    "check_id": "php-dangerous-unserialize",
                    "path": os.path.join("src", "vulnerable.php"),
                    "start": {"line": 7},
                    "extra": {
                        "message": "Dangerous unserialize usage",
                        "severity": "ERROR",
                        "metadata": {
                            "category": "deserialization",
                            "severity": "HIGH",
                            "cwe": "CWE-502",
                            "description": "不安全反序列化漏洞",
                            "fix": ["避免用户可控输入进入 unserialize"],
                        },
                    },
                },
                {
                    "check_id": "legacy-rule",
                    "path": os.path.join("legacy", "old.php"),
                    "start": {"line": 12},
                    "extra": {
                        "message": "Legacy vulnerability",
                        "severity": "WARNING",
                    },
                },
            ]
        }
        run.return_value = SimpleNamespace(
            returncode=0,
            stdout=json.dumps(semgrep_output, ensure_ascii=False),
            stderr="",
        )

        result = scan("source", "rules.yml")

        self.assertEqual(
            run.call_args.args[0],
            ["semgrep", "scan", "--config", "rules.yml", "source", "--json"],
        )
        self.assertTrue(run.call_args.kwargs["capture_output"])
        self.assertTrue(run.call_args.kwargs["text"])
        self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")
        self.assertEqual(
            run.call_args.kwargs["env"]["PYTHONUTF8"],
            os.environ.get("PYTHONUTF8", "1"),
        )
        self.assertEqual(len(result["vulnerabilities"]), 2)

        item = result["vulnerabilities"][0]
        self.assertIsInstance(item, Vulnerability)
        self.assertEqual(item["rule"], "php-dangerous-unserialize")
        self.assertEqual(item["file"], "vulnerable.php")
        self.assertEqual(item["line"], 7)
        self.assertEqual(item.get("message"), "Dangerous unserialize usage")
        self.assertEqual(item["severity"], "HIGH")
        self.assertEqual(item["cwe"], "CWE-502")
        self.assertEqual(item["category"], "deserialization")

        legacy_item = result["vulnerabilities"][1]
        self.assertEqual(legacy_item["rule"], "legacy-rule")
        self.assertEqual(legacy_item["severity"], "WARNING")
        self.assertEqual(legacy_item["cwe"], "N/A")
        self.assertEqual(legacy_item["category"], "unknown")
        self.assertEqual(legacy_item["description"], "Legacy vulnerability")
        self.assertEqual(legacy_item["fix"], [])

        encoded = json.dumps(result, ensure_ascii=False)
        self.assertIn("不安全反序列化漏洞", encoded)

    @patch("backend.engine.semgrep_runner.subprocess.run")
    def test_scan_extracts_code_snippet_from_lines(self, run):
        semgrep_output = {
            "results": [
                {
                    "check_id": "php-dangerous-eval",
                    "path": os.path.join("src", "vulnerable.php"),
                    "start": {"line": 3},
                    "extra": {
                        "message": "Dangerous eval usage",
                        "lines": "eval($input);",
                    },
                },
                {
                    "check_id": "php-dangerous-unserialize",
                    "path": os.path.join("src", "vulnerable.php"),
                    "start": {"line": 7},
                    "extra": {
                        "message": "Dangerous unserialize usage",
                        "lines": ["$user = unserialize(", "    $_GET['cmd'],", ");"],
                    },
                },
            ]
        }
        run.return_value = SimpleNamespace(
            returncode=0,
            stdout=json.dumps(semgrep_output, ensure_ascii=False),
            stderr="",
        )

        result = scan("source", "rules.yml")

        self.assertEqual(
            result["vulnerabilities"][0]["code_snippet"],
            "eval($input);",
        )
        self.assertEqual(
            result["vulnerabilities"][1]["code_snippet"],
            "$user = unserialize(\n    $_GET['cmd'],\n);",
        )

    @patch("backend.engine.semgrep_runner.subprocess.run")
    def test_scan_falls_back_to_fixed_lines_for_code_snippet(self, run):
        semgrep_output = {
            "results": [
                {
                    "check_id": "php-dangerous-unserialize",
                    "path": os.path.join("src", "vulnerable.php"),
                    "start": {"line": 7},
                    "extra": {
                        "message": "Dangerous unserialize usage",
                        "fixed_lines": "unserialize($input, ['allowed_classes' => false]);",
                    },
                },
            ]
        }
        run.return_value = SimpleNamespace(
            returncode=0,
            stdout=json.dumps(semgrep_output, ensure_ascii=False),
            stderr="",
        )

        result = scan("source", "rules.yml")

        self.assertEqual(
            result["vulnerabilities"][0]["code_snippet"],
            "unserialize($input, ['allowed_classes' => false]);",
        )

    @patch("backend.engine.semgrep_runner.subprocess.run")
    def test_scan_returns_empty_code_snippet_without_lines(self, run):
        # 没有 lines 和 fixed_lines 时返回空字符串，且不使用 message 作为代码片段。
        semgrep_output = {
            "results": [
                {
                    "check_id": "php-dangerous-eval",
                    "path": os.path.join("src", "vulnerable.php"),
                    "start": {"line": 3},
                    "extra": {
                        "message": "Dangerous eval usage",
                    },
                },
            ]
        }
        run.return_value = SimpleNamespace(
            returncode=0,
            stdout=json.dumps(semgrep_output, ensure_ascii=False),
            stderr="",
        )

        result = scan("source", "rules.yml")

        self.assertEqual(result["vulnerabilities"][0]["code_snippet"], "")

    @patch("backend.engine.semgrep_runner.subprocess.run")
    def test_scan_sets_python_utf8_when_not_configured(self, run):

        run.return_value = SimpleNamespace(returncode=0, stdout='{"results": []}', stderr="")

        with patch.dict(os.environ, {}, clear=True):
            scan("source", "rules.yml")

        self.assertEqual(run.call_args.kwargs["env"], {"PYTHONUTF8": "1"})

    @patch("backend.engine.semgrep_runner.subprocess.run")
    def test_scan_preserves_configured_python_utf8(self, run):
        run.return_value = SimpleNamespace(returncode=0, stdout='{"results": []}', stderr="")

        with patch.dict(os.environ, {"PYTHONUTF8": "0"}, clear=True):
            scan("source", "rules.yml")

        self.assertEqual(run.call_args.kwargs["env"], {"PYTHONUTF8": "0"})


if __name__ == "__main__":
    unittest.main()
