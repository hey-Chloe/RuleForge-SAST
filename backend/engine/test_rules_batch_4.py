import unittest
from pathlib import Path

from backend.engine.semgrep_runner import scan


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = PROJECT_ROOT / "rules"
TESTCASES_DIR = PROJECT_ROOT / "testcase" / "rules"


class JavaRulesBatchFourTests(unittest.TestCase):
    def assert_dangerous_sample(
        self,
        rule_file,
        sample_file,
        expected_rule_id,
        expected_category,
        expected_cwe,
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
            self.assertIsInstance(vulnerability["fix"], list)
            self.assertTrue(vulnerability["fix"])

    def assert_safe_sample(self, rule_file, sample_file):
        result = scan(str(sample_file), str(rule_file))

        self.assertEqual(result["vulnerabilities"], [])

    def test_deserialization_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "java-deserialization.yaml",
            TESTCASES_DIR / "java-unsafe-deserialization" / "vulnerable.java",
            "java-unsafe-deserialization",
            "deserialization",
            "CWE-502",
            1,
        )

    def test_deserialization_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "java-deserialization.yaml",
            TESTCASES_DIR / "java-unsafe-deserialization" / "safe.java",
        )

    def test_command_execution_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "java-command-execution.yaml",
            TESTCASES_DIR / "java-command-execution" / "vulnerable.java",
            "java-command-execution",
            "command-execution",
            "CWE-78",
            1,
        )

    def test_command_execution_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "java-command-execution.yaml",
            TESTCASES_DIR / "java-command-execution" / "safe.java",
        )

    def test_sql_injection_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "java-sqli.yaml",
            TESTCASES_DIR / "java-sql-injection" / "vulnerable.java",
            "java-sql-injection",
            "sql-injection",
            "CWE-89",
            3,
        )

    def test_sql_injection_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "java-sqli.yaml",
            TESTCASES_DIR / "java-sql-injection" / "safe.java",
        )


if __name__ == "__main__":
    unittest.main()
