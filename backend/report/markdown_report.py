"""Generate standalone Markdown security reports."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any


_RISK_ORDER = {
    "CRITICAL": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
    "INFO": 4,
    "UNKNOWN": 5,
}


def _display(value: Any, default: str) -> str:
    if value is None or value == "":
        return default
    return str(value)


def _normalize_fix(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.strip()]
    return []


def _extract_vulnerabilities(value: Any) -> list:
    if isinstance(value, Mapping) and "vulnerabilities" in value:
        value = value.get("vulnerabilities", [])

    if value is None:
        return []
    if isinstance(value, Mapping):
        return [value]

    try:
        return list(value)
    except TypeError:
        return []


def generate_markdown_report(
    vulnerabilities: Any,
    output_path: str = "security_report.md",
) -> Path:
    """Write vulnerabilities grouped by severity to a UTF-8 Markdown file."""
    groups: dict[str, list[Mapping]] = {}

    for vulnerability in _extract_vulnerabilities(vulnerabilities):
        if not isinstance(vulnerability, Mapping):
            continue

        severity = _display(vulnerability.get("severity"), "UNKNOWN").upper()
        groups.setdefault(severity, []).append(vulnerability)

    lines = ["# Security Report", ""]

    for severity in sorted(
        groups,
        key=lambda value: (_RISK_ORDER.get(value, len(_RISK_ORDER)), value),
    ):
        lines.extend([f"## {severity} Risk", ""])

        for index, vulnerability in enumerate(groups[severity]):
            if index:
                lines.extend(["---", ""])

            rule = vulnerability.get("rule") or vulnerability.get("id")
            fixes = _normalize_fix(vulnerability.get("fix"))

            lines.extend(
                [
                    "漏洞:",
                    "",
                    _display(rule, "N/A"),
                    "",
                    "CWE:",
                    "",
                    _display(vulnerability.get("cwe"), "N/A"),
                    "",
                    "类型:",
                    "",
                    _display(vulnerability.get("category"), "unknown"),
                    "",
                    "文件:",
                    "",
                    _display(vulnerability.get("file"), "N/A"),
                    "",
                    "行:",
                    "",
                    _display(vulnerability.get("line"), "N/A"),
                    "",
                    "描述:",
                    "",
                    _display(vulnerability.get("description"), "暂无描述"),
                    "",
                    "修复建议:",
                    "",
                ]
            )
            lines.extend(f"- {fix}" for fix in fixes)
            if not fixes:
                lines.append("- 暂无修复建议")
            lines.append("")

    report_path = Path(output_path)
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return report_path

