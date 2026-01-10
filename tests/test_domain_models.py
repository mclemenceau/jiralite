"""Tests for domain models."""

from datetime import datetime

import pytest

from jiralite.domain.models import Comment, Issue, IssueType, Transition, User


def test_user_creation():
    """Test User model creation."""
    user = User(
        account_id="123",
        display_name="John Doe",
        email="john@example.com",
    )
    assert user.account_id == "123"
    assert user.display_name == "John Doe"
    assert user.email == "john@example.com"


def test_user_immutable():
    """Test that User is immutable."""
    user = User(account_id="123", display_name="John Doe")
    with pytest.raises(AttributeError):
        user.display_name = "Jane Doe"


def test_issue_type_creation():
    """Test IssueType model creation."""
    issue_type = IssueType(
        id="1",
        name="Bug",
        icon_url="https://example.com/icon.png",
    )
    assert issue_type.id == "1"
    assert issue_type.name == "Bug"
    assert issue_type.icon_url == "https://example.com/icon.png"


def test_issue_creation(sample_issue_type, sample_user):
    """Test Issue model creation."""
    issue = Issue(
        key="ABC-123",
        summary="Test issue",
        issue_type=sample_issue_type,
        status="Open",
        assignee=sample_user,
        description="Test description",
        labels=("test", "example"),
    )
    assert issue.key == "ABC-123"
    assert issue.summary == "Test issue"
    assert issue.status == "Open"
    assert issue.labels == ("test", "example")


def test_comment_creation(sample_user):
    """Test Comment model creation."""
    now = datetime.now()
    comment = Comment(
        id="456",
        author=sample_user,
        body="This is a test comment",
        created=now,
    )
    assert comment.id == "456"
    assert comment.author == sample_user
    assert comment.body == "This is a test comment"
    assert comment.created == now


def test_transition_creation():
    """Test Transition model creation."""
    transition = Transition(
        id="11",
        name="Done",
        to_status="Done",
    )
    assert transition.id == "11"
    assert transition.name == "Done"
    assert transition.to_status == "Done"
