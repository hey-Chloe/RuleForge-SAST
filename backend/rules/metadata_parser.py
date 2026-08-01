"""Parse normalized metadata from a single Semgrep result."""

from typing import Any


def _non_empty_string(value: Any, default: str) -> str:
    """Return a non-empty string or a safe default."""
    if isinstance(value, str) and value.strip():
        return value
    return default


def _normalize_fix(value: Any) -> list:
    """Normalize remediation guidance to a list of non-empty strings."""
    if isinstance(value, str):
        return [value] if value.strip() else []

    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.strip()]

    return []


def parse_metadata(result: Any) -> dict:
    """Extract vulnerability metadata from one Semgrep JSON result."""
    if not isinstance(result, dict):
        result = {}

    extra = result.get("extra")
    if not isinstance(extra, dict):
        extra = {}

    metadata = extra.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    check_id = _non_empty_string(result.get("check_id"), "unknown")
    extra_severity = _non_empty_string(extra.get("severity"), "UNKNOWN")
    message = _non_empty_string(extra.get("message"), "")

    return {
        "rule_id": _non_empty_string(metadata.get("rule_id"), check_id),
        "category": _non_empty_string(metadata.get("category"), "unknown"),
        "severity": _non_empty_string(metadata.get("severity"), extra_severity),
        "cwe": _non_empty_string(metadata.get("cwe"), "N/A"),
        "description": _non_empty_string(metadata.get("description"), message),
        "fix": _normalize_fix(metadata.get("fix")),
    }

