"""Tests for Jira service layer."""

import pytest
import respx
from httpx import Response

from jiralite.domain.exceptions import (
    AuthenticationError,
    IssueNotFoundError,
    JiraAPIError,
)
from jiralite.services import JiraClient, build_default_jql


def test_build_default_jql():
    """Test default JQL builder."""
    jql = build_default_jql(14)
    assert "assignee IN (currentUser())" in jql
    assert "resolved >= -14d" in jql
    assert "ORDER BY updated DESC" in jql


def test_build_default_jql_custom_days():
    """Test default JQL builder with custom days."""
    jql = build_default_jql(30)
    assert "resolved >= -30d" in jql


@pytest.mark.asyncio
@respx.mock
async def test_get_current_user(sample_config):
    """Test getting current user."""
    respx.get("https://example.atlassian.net/rest/api/3/myself").mock(
        return_value=Response(
            200,
            json={
                "accountId": "123",
                "displayName": "John Doe",
                "emailAddress": "john@example.com",
            },
        )
    )

    async with JiraClient(sample_config) as client:
        user = await client.get_current_user()
        assert user.account_id == "123"
        assert user.display_name == "John Doe"
        assert user.email == "john@example.com"


@pytest.mark.asyncio
@respx.mock
async def test_get_current_user_auth_error(sample_config):
    """Test authentication error when getting current user."""
    respx.get("https://example.atlassian.net/rest/api/3/myself").mock(
        return_value=Response(401, json={"errorMessages": ["Unauthorized"]})
    )

    async with JiraClient(sample_config) as client:
        with pytest.raises(AuthenticationError):
            await client.get_current_user()


@pytest.mark.asyncio
@respx.mock
async def test_search_issues(sample_config):
    """Test searching for issues."""
    respx.get("https://example.atlassian.net/rest/api/3/search/jql").mock(
        return_value=Response(
            200,
            json={
                "issues": [
                    {
                        "key": "ABC-123",
                        "fields": {
                            "summary": "Test issue",
                            "issuetype": {
                                "id": "1",
                                "name": "Bug",
                            },
                            "status": {"name": "Open"},
                            "assignee": None,
                            "reporter": None,
                            "description": "Test",
                            "labels": [],
                            "fixVersions": [],
                            "components": [],
                        },
                    }
                ]
            },
        )
    )

    async with JiraClient(sample_config) as client:
        issues = await client.search_issues("project = ABC")
        assert len(issues) == 1
        assert issues[0].key == "ABC-123"
        assert issues[0].summary == "Test issue"


@pytest.mark.asyncio
@respx.mock
async def test_get_issue_not_found(sample_config):
    """Test getting a non-existent issue."""
    respx.get("https://example.atlassian.net/rest/api/3/issue/ABC-999").mock(
        return_value=Response(404, json={"errorMessages": ["Not found"]})
    )

    async with JiraClient(sample_config) as client:
        with pytest.raises(IssueNotFoundError):
            await client.get_issue("ABC-999")


@pytest.mark.asyncio
@respx.mock
async def test_add_comment(sample_config):
    """Test adding a comment to an issue."""
    respx.post(
        "https://example.atlassian.net/rest/api/3/issue/ABC-123/comment"
    ).mock(
        return_value=Response(
            201,
            json={
                "id": "456",
                "author": {
                    "accountId": "123",
                    "displayName": "John Doe",
                },
                "body": "Test comment",
                "created": "2024-01-10T12:00:00.000+0000",
            },
        )
    )

    async with JiraClient(sample_config) as client:
        comment = await client.add_comment("ABC-123", "Test comment")
        assert comment.id == "456"
        assert comment.body == "Test comment"
