"""Tests for configuration."""

from jiralite.config.settings import JiraConfig


def test_jira_config_creation():
    """Test creating a JiraConfig instance."""
    config = JiraConfig(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )
    assert config.base_url == "https://example.atlassian.net"
    assert config.email == "test@example.com"
    assert config.api_token == "test-token"
    assert config.default_jql_days == 14


def test_jira_config_custom_days():
    """Test creating a JiraConfig with custom default_jql_days."""
    config = JiraConfig(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
        default_jql_days=30,
    )
    assert config.default_jql_days == 30


def test_jira_config_immutable():
    """Test that JiraConfig is immutable."""
    config = JiraConfig(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token",
    )
    try:
        config.base_url = "https://new-url.atlassian.net"
        assert False, "Should not be able to modify frozen dataclass"
    except AttributeError:
        pass  # Expected
