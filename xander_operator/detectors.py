#!/usr/bin/env python3
"""
Detectors — Safety and input validation pre-checks for tasks.

These modules examine tasks before execution to flag potential issues.
"""

import re
from typing import Dict, List, Any
from urllib.parse import urlparse

def validate_task(task: Dict[str, Any]) -> List[str]:
    """
    Run all input validation detectors on a task.
    Returns a list of issue descriptions (empty if all good).
    """
    issues = []
    issues.extend(_validate_task_structure(task))
    issues.extend(_validate_url(task.get("url")))
    issues.extend(_validate_selectors(task.get("selectors", {})))
    issues.extend(_validate_values(task.get("values", {})))
    return issues

def _validate_task_structure(task: Dict[str, Any]) -> List[str]:
    issues = []
    if not task.get("id"):
        issues.append("Missing task id")
    if not task.get("type"):
        issues.append("Missing task type")
    if not task.get("task"):
        issues.append("Missing task description")
    return issues

def _validate_url(url: Any) -> List[str]:
    issues = []
    if not url:
        return issues
    if not isinstance(url, str):
        issues.append("URL must be a string")
        return issues
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            issues.append(f"URL scheme '{parsed.scheme}' not allowed (only http/https)")
        # Block localhost and private IP ranges
        host = parsed.hostname
        if host:
            if host in ("localhost", "127.0.0.1", "0.0.0.0"):
                issues.append("URL points to localhost — blocked for safety")
            if re.match(r"^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[0-1])\.)", host):
                issues.append("URL points to private IP range — blocked")
    except Exception:
        issues.append("URL parsing failed")
    return issues

def _validate_selectors(selectors: Dict[str, str]) -> List[str]:
    issues = []
    if not isinstance(selectors, dict):
        issues.append("Selectors must be a dict")
        return issues
    for key, sel in selectors.items():
        if not isinstance(sel, str) or not sel.strip():
            issues.append(f"Selector for '{key}' is empty")
    return issues

def _validate_values(values: Dict[str, str]) -> List[str]:
    issues = []
    if not isinstance(values, dict):
        issues.append("Values must be a dict")
        return issues
    # Basic heuristic: disallow overly long values that may be misstructured
    for key, val in values.items():
        if isinstance(val, str) and len(val) > 1000:
            issues.append(f"Value for '{key}' exceeds 1000 characters")
    return issues

def safety_check(task: Dict[str, Any]) -> List[str]:
    """
    Evaluate a task for potential safety concerns beyond basic validation.
    Returns warnings that may be configurable to block or require extra approval.
    """
    warnings = []
    url = task.get("url", "")
    task_type = task.get("type", "")
    desc = task.get("task", "").lower()

    # Detect potentially sensitive actions
    if task_type == "fill":
        # Check for password fields
        selectors = task.get("selectors", {})
        for name in selectors.keys():
            if "password" in name.lower():
                warnings.append("Form includes a password field — requires explicit approval")
        # Check for financial/payment identifiers
        if any(kw in desc for kw in ("pay", "credit", "billing", "donation")):
            warnings.append("Task description suggests financial transaction — extra caution")

    # Block obvious dangerous URLs
    if url:
        if url.startswith("file://"):
            warnings.append("file:// URLs are blocked")
        if "javascript:" in url.lower():
            warnings.append("javascript: URLs are blocked")

    return warnings
