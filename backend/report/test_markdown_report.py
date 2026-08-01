import tempfile
import unittest
from pathlib import Path

from backend.models.vulnerability import Vulnerability
from backend.report.markdown_report import generate_markdown_report


class MarkdownReportTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.output_path = Path(self.temp_directory.name) / "security_report.md"

    def tearDown(self):
        self.temp_directory.cleanup()

    def read_report(self) -> str:
        return self.output_path.read_text(encoding="utf-8")

    def test_generates_report_from_vulnerability_list(self):
        vulnerability = Vulnerability(
            id="php-dangerous-unserialize",
            rule="rules.php-dangerous-unserialize",
            file="test.php",
            line=3,
            category="deserialization",
            severity="HIGH",
            cwe="CWE-502",
            description="不安全反序列化漏洞",
            fix=[
                "避免用户可控输入进入 unserialize",
                "使用安全序列化方式",
            ],
        )

        generated_path = generate_markdown_report([vulnerability], self.output_path)
        report = self.read_report()

        self.assertEqual(generated_path, self.output_path)
        self.assertIn("# Security Report", report)
        self.assertIn("## HIGH Risk", report)
        self.assertIn("rules.php-dangerous-unserialize", report)
        self.assertIn("CWE-502", report)
        self.assertIn("deserialization", report)
        self.assertIn("不安全反序列化漏洞", report)
        self.assertIn("- 避免用户可控输入进入 unserialize", report)
        self.assertIn("- 使用安全序列化方式", report)

    def test_generates_report_from_plain_dict_list_with_defaults(self):
        vulnerabilities = [
            {
                "rule": "legacy-rule",
                "file": "legacy.php",
                "line": 8,
                "category": "unknown",
            }
        ]

        generate_markdown_report(vulnerabilities, self.output_path)
        report = self.read_report()

        self.assertIn("## UNKNOWN Risk", report)
        self.assertIn("CWE:\n\nN/A", report)
        self.assertIn("描述:\n\n暂无描述", report)
        self.assertIn("- 暂无修复建议", report)

    def test_generates_report_from_scan_result(self):
        scan_result = {
            "vulnerabilities": [
                {
                    "id": "finding-1",
                    "rule": "scan-rule",
                    "file": "scan.php",
                    "line": 11,
                    "category": "deserialization",
                    "severity": "HIGH",
                    "cwe": "CWE-502",
                    "description": "扫描结果描述",
                    "fix": ["扫描结果修复建议"],
                }
            ]
        }

        generate_markdown_report(scan_result, self.output_path)
        report = self.read_report()

        self.assertIn("scan-rule", report)
        self.assertIn("scan.php", report)
        self.assertIn("扫描结果描述", report)
        self.assertIn("- 扫描结果修复建议", report)


if __name__ == "__main__":
    unittest.main()
