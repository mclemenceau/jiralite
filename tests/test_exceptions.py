"""Tests for domain exceptions."""

from jiralite.domain.exceptions import (
    AuthenticationError,
    ConfigurationError,
    IssueNotFoundError,
    JiraAPIError,
    JiraLiteException,
)


def test_jiralite_exception():
    """Test base JiraLiteException."""
    error = JiraLiteException("Test error")
    assert str(error) == "Test error"


def test_configuration_error():
    """Test ConfigurationError."""
    error = ConfigurationError("Config missing")
    assert str(error) == "Config missing"
    assert isinstance(error, JiraLiteException)


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError("Invalid credentials")
    assert str(error) == "Invalid credentials"
    assert isinstance(error, JiraLiteException)


def test_jira_api_error():
    """Test JiraAPIError."""
    error = JiraAPIError("API failed")
    assert str(error) == "API failed"
    assert isinstance(error, JiraLiteException)


def test_jira_api_error_with_status():
    """Test JiraAPIError with status code."""
    error = JiraAPIError("API failed", status_code=404)
    assert str(error) == "API failed"
    assert error.status_code == 404


def test_issue_not_found_error():
    """Test IssueNotFoundError."""
    error = IssueNotFoundError("Issue not found")
    assert str(error) == "Issue not found"
    assert isinstance(error, JiraAPIError)
