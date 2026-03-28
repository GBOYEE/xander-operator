"""Tests for detectors module."""
import pytest  # noqa: F401
from xander_operator.detectors import validate_task, safety_check

def test_validate_task_missing_fields():
    task = {}
    issues = validate_task(task)
    assert "Missing task id" in issues
    assert "Missing task type" in issues
    assert "Missing task description" in issues

def test_validate_task_invalid_url_scheme():
    task = {"id": "1", "type": "browse", "url": "ftp://example.com"}
    issues = validate_task(task)
    assert any("scheme" in issue.lower() for issue in issues)

def test_validate_task_localhost_url():
    task = {"id": "1", "type": "browse", "url": "http://localhost"}
    issues = validate_task(task)
    assert any("localhost" in issue.lower() for issue in issues)

def test_validate_task_private_ip():
    task = {"id": "1", "type": "browse", "url": "http://192.168.0.1"}
    issues = validate_task(task)
    assert any("private ip" in issue.lower() for issue in issues)

def test_validate_task_good():
    task = {"id": "123", "type": "browse", "url": "https://example.com", "task": "Test browse"}
    issues = validate_task(task)
    assert len(issues) == 0

def test_validate_task_selectors_empty():
    task = {"id": "1", "type": "fill", "url": "https://example.com", "selectors": {"field": ""}}
    issues = validate_task(task)
    assert any("empty" in issue.lower() for issue in issues)

def test_safety_check_password_field():
    task = {"id": "1", "type": "fill", "url": "https://example.com", "selectors": {"password_field": "#pass"}, "values": {}}
    warnings = safety_check(task)
    assert any("password" in w.lower() for w in warnings)

def test_safety_check_file_url():
    task = {"id": "1", "type": "browse", "url": "file:///etc/passwd"}
    warnings = safety_check(task)
    assert any("file://" in w.lower() for w in warnings)

def test_safety_check_javascript_url():
    task = {"id": "1", "type": "browse", "url": "javascript:alert(1)"}
    warnings = safety_check(task)
    assert any("javascript:" in w.lower() for w in warnings)
