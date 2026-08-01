import unittest
from pathlib import Path

from backend.engine.semgrep_runner import scan


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = PROJECT_ROOT / "rules"
TESTCASES_DIR = PROJECT_ROOT / "testcase" / "rules"


class PythonRulesBatchTwoTests(unittest.TestCase):
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

    def test_pickle_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "python-pickle.yaml",
            TESTCASES_DIR / "python-unsafe-pickle" / "vulnerable.py",
            "python-unsafe-pickle",
            "deserialization",
            "CWE-502",
            2,
        )

    def test_pickle_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "python-pickle.yaml",
            TESTCASES_DIR / "python-unsafe-pickle" / "safe.py",
        )

    def test_subprocess_shell_true_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "python-subprocess-shell.yaml",
            TESTCASES_DIR / "python-subprocess-shell-true" / "vulnerable.py",
            "python-subprocess-shell-true",
            "command-execution",
            "CWE-78",
            4,
        )

    def test_subprocess_shell_true_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "python-subprocess-shell.yaml",
            TESTCASES_DIR / "python-subprocess-shell-true" / "safe.py",
        )


if __name__ == "__main__":
    unittest.main()
