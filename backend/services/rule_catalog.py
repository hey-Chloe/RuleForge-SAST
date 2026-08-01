"""Read and normalize the local Semgrep rule catalog."""

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RULES_DIRECTORY = PROJECT_ROOT / "rules"


class RuleCatalogError(RuntimeError):
    """Raised when the local rule catalog cannot be read safely."""


def _non_empty_string(value: Any, default: str) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return default


def _normalize_languages(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.strip()]
    return []


def _normalize_fix(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.strip()]
    return []


def _normalize_rule(rule: dict[str, Any], source_file: str) -> dict[str, Any]:
    metadata = rule.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    message = _non_empty_string(rule.get("message"), "")
    semgrep_severity = _non_empty_string(rule.get("severity"), "UNKNOWN")

    return {
        "id": _non_empty_string(rule.get("id"), ""),
        "languages": _normalize_languages(rule.get("languages")),
        "message": message,
        "semgrep_severity": semgrep_severity,
        "category": _non_empty_string(metadata.get("category"), "unknown"),
        "severity": _non_empty_string(metadata.get("severity"), semgrep_severity),
        "cwe": _non_empty_string(metadata.get("cwe"), "N/A"),
        "description": _non_empty_string(metadata.get("description"), message),
        "fix": _normalize_fix(metadata.get("fix")),
        "source_file": source_file,
    }


def load_rule_catalog() -> list[dict[str, Any]]:
    """Load every .yaml/.yml rule beneath the fixed project rules directory."""
    if not RULES_DIRECTORY.is_dir():
        raise RuleCatalogError("Local rule directory is unavailable")

    try:
        rule_files = sorted(
            path
            for path in RULES_DIRECTORY.iterdir()
            if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}
        )
    except OSError as exc:
        raise RuleCatalogError("Unable to enumerate local rule directory") from exc

    catalog: list[dict[str, Any]] = []
    for rule_file in rule_files:
        try:
            document = yaml.safe_load(rule_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise RuleCatalogError(f"Failed to read {rule_file.name}: {exc}") from exc

        if not isinstance(document, dict):
            raise RuleCatalogError(f"Invalid rule document in {rule_file.name}")

        rules = document.get("rules")
        if not isinstance(rules, list):
            raise RuleCatalogError(f"Missing rules list in {rule_file.name}")

        for rule in rules:
            if not isinstance(rule, dict):
                raise RuleCatalogError(f"Invalid rule entry in {rule_file.name}")
            catalog.append(_normalize_rule(rule, rule_file.name))

    return catalog
