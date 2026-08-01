import unittest
from pathlib import Path

from backend.engine.semgrep_runner import scan


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = PROJECT_ROOT / "rules"
TESTCASES_DIR = PROJECT_ROOT / "testcase" / "rules"


class PhpTaintRulesBatchFiveTests(unittest.TestCase):
    def assert_dangerous_sample(
        self,
        rule_file,
        sample_file,
        expected_rule_id,
        expected_category,
        expected_cwe,
        expected_description,
        expected_findings,
    ):
        result = scan(str(sample_file), str(rule_file))
        vulnerabilities = result["vulnerabilities"]

        self.assertEqual(len(vulnerabilities), expected_findings)
        for vulnerability in vulnerabilities:
            self.assertTrue(vulnerability["rule"].endswith(expected_rule_id))
            self.assertEqual(vulnerability["category"], expected_category)
            self.assertEqual(vulnerability["severity"], "HIGH")
            self.assertEqual(vulnerability["cwe"], expected_cwe)
            self.assertEqual(vulnerability["description"], expected_description)
            self.assertIsInstance(vulnerability["fix"], list)
            self.assertTrue(vulnerability["fix"])

    def assert_safe_sample(self, rule_file, sample_file):
        result = scan(str(sample_file), str(rule_file))

        self.assertEqual(result["vulnerabilities"], [])

    def test_ssrf_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "php-ssrf.yaml",
            TESTCASES_DIR / "php-ssrf-user-controlled-url" / "vulnerable.php",
            "php-ssrf-user-controlled-url",
            "ssrf",
            "CWE-918",
            "用户可控 URL 进入网络请求，可能导致 SSRF",
            3,
        )

    def test_ssrf_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "php-ssrf.yaml",
            TESTCASES_DIR / "php-ssrf-user-controlled-url" / "safe.php",
        )

    def test_reflected_xss_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "php-xss.yaml",
            TESTCASES_DIR / "php-reflected-xss" / "vulnerable.php",
            "php-reflected-xss",
            "xss",
            "CWE-79",
            "用户可控输入直接输出到 HTML，可能导致反射型 XSS",
            3,
        )

    def test_reflected_xss_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "php-xss.yaml",
            TESTCASES_DIR / "php-reflected-xss" / "safe.php",
        )

    def test_upload_name_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "php-file-upload.yaml",
            TESTCASES_DIR / "php-user-controlled-upload-name" / "vulnerable.php",
            "php-user-controlled-upload-name",
            "file-upload",
            "CWE-434",
            "用户可控上传文件名用于存储路径，可能导致危险文件上传",
            1,
        )

    def test_upload_name_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "php-file-upload.yaml",
            TESTCASES_DIR / "php-user-controlled-upload-name" / "safe.php",
        )


if __name__ == "__main__":
    unittest.main()
