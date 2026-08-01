import unittest
from pathlib import Path

from backend.engine.semgrep_runner import scan


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = PROJECT_ROOT / "rules"
TESTCASES_DIR = PROJECT_ROOT / "testcase" / "rules"


class EvalRulesBatchOneTests(unittest.TestCase):
    def assert_dangerous_sample(self, rule_file, sample_file, expected_rule_id):
        result = scan(str(sample_file), str(rule_file))
        vulnerabilities = result["vulnerabilities"]

        self.assertEqual(len(vulnerabilities), 1)
        vulnerability = vulnerabilities[0]
        self.assertTrue(vulnerability["rule"].endswith(expected_rule_id))
        self.assertEqual(vulnerability["severity"], "CRITICAL")
        self.assertEqual(vulnerability["cwe"], "CWE-95")
        self.assertEqual(vulnerability["category"], "code-execution")
        self.assertIsInstance(vulnerability["fix"], list)
        self.assertTrue(vulnerability["fix"])

    def assert_safe_sample(self, rule_file, sample_file):
        result = scan(str(sample_file), str(rule_file))

        self.assertEqual(result["vulnerabilities"], [])

    def test_php_eval_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "php-eval.yaml",
            TESTCASES_DIR / "php-dangerous-eval" / "vulnerable.php",
            "php-dangerous-eval",
        )

    def test_php_eval_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "php-eval.yaml",
            TESTCASES_DIR / "php-dangerous-eval" / "safe.php",
        )

    def test_python_eval_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "python-eval.yaml",
            TESTCASES_DIR / "python-dangerous-eval" / "vulnerable.py",
            "python-dangerous-eval",
        )

    def test_python_eval_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "python-eval.yaml",
            TESTCASES_DIR / "python-dangerous-eval" / "safe.py",
        )


if __name__ == "__main__":
    unittest.main()
