import unittest
from pathlib import Path

from backend.engine.semgrep_runner import scan


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = PROJECT_ROOT / "rules"
TESTCASES_DIR = PROJECT_ROOT / "testcase" / "rules"


class PhpRulesBatchThreeTests(unittest.TestCase):
    def assert_dangerous_sample(
        self,
        rule_file,
        sample_file,
        expected_rule_id,
        expected_category,
        expected_severity,
        expected_cwe,
        expected_findings,
    ):
        result = scan(str(sample_file), str(rule_file))
        vulnerabilities = result["vulnerabilities"]

        self.assertEqual(len(vulnerabilities), expected_findings)
        for vulnerability in vulnerabilities:
            self.assertTrue(vulnerability["rule"].endswith(expected_rule_id))
            self.assertEqual(vulnerability["category"], expected_category)
            self.assertEqual(vulnerability["severity"], expected_severity)
            self.assertEqual(vulnerability["cwe"], expected_cwe)
            self.assertIsInstance(vulnerability["fix"], list)
            self.assertTrue(vulnerability["fix"])

    def assert_safe_sample(self, rule_file, sample_file):
        result = scan(str(sample_file), str(rule_file))

        self.assertEqual(result["vulnerabilities"], [])

    def test_weak_hash_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "php-weak-hash.yaml",
            TESTCASES_DIR / "php-weak-hash" / "vulnerable.php",
            "php-weak-hash",
            "weak-crypto",
            "MEDIUM",
            "CWE-328",
            2,
        )

    def test_weak_hash_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "php-weak-hash.yaml",
            TESTCASES_DIR / "php-weak-hash" / "safe.php",
        )

    def test_weak_randomness_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "php-weak-randomness.yaml",
            TESTCASES_DIR / "php-weak-randomness" / "vulnerable.php",
            "php-weak-randomness",
            "weak-randomness",
            "MEDIUM",
            "CWE-330",
            2,
        )

    def test_weak_randomness_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "php-weak-randomness.yaml",
            TESTCASES_DIR / "php-weak-randomness" / "safe.php",
        )

    def test_xxe_entity_loader_vulnerable_sample(self):
        self.assert_dangerous_sample(
            RULES_DIR / "php-xxe.yaml",
            TESTCASES_DIR / "php-xxe-entity-loader-disabled" / "vulnerable.php",
            "php-xxe-entity-loader-disabled",
            "xxe",
            "HIGH",
            "CWE-611",
            1,
        )

    def test_xxe_entity_loader_safe_sample(self):
        self.assert_safe_sample(
            RULES_DIR / "php-xxe.yaml",
            TESTCASES_DIR / "php-xxe-entity-loader-disabled" / "safe.php",
        )


if __name__ == "__main__":
    unittest.main()
