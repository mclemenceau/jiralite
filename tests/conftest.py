"""Test configuration and fixtures."""

import pytest

from jiralite.config import JiraConfig
from jiralite.domain.models import Issue, IssueType, User


@pytest.fixture
def sample_config() -> JiraConfig:
    """Provide a sample Jira configuration."""
    return JiraConfig(
        base_url="https://example.atlassian.net",
        email="test@example.com",
        api_token="test-token-123",
        default_jql_days=14,
    )


@pytest.fixture
def sample_user() -> User:
    """Provide a sample user."""
    return User(
        account_id="123456",
        display_name="John Doe",
        email="john@example.com",
    )


@pytest.fixture
def sample_issue_type() -> IssueType:
    """Provide a sample issue type."""
    return IssueType(
        id="1",
        name="Bug",
        icon_url="https://example.com/icon.png",
    )


@pytest.fixture
def sample_issue(sample_issue_type: IssueType, sample_user: User) -> Issue:
    """Provide a sample issue."""
    return Issue(
        key="ABC-123",
        summary="Fix critical bug in authentication",
        issue_type=sample_issue_type,
        status="In Progress",
        assignee=sample_user,
        reporter=sample_user,
        description="This is a critical bug that needs fixing.",
        priority="High",
        labels=("bug", "security"),
        fix_versions=("1.0.0",),
        components=("Auth",),
    )
