"""Tests for formatting utilities."""

from jiralite.domain.models import Issue, IssueType, User
from jiralite.util.formatting import (
    format_assignee,
    format_issue_line,
    get_issue_icon,
    truncate_text,
)


def test_get_issue_icon():
    """Test issue type icon mapping."""
    assert get_issue_icon("Objective") == "🟨"
    assert get_issue_icon("Epic") == "🟪"
    assert get_issue_icon("Bug") == "🟥"
    assert get_issue_icon("Task") == "🟦"
    assert get_issue_icon("Story") == "🟩"
    assert get_issue_icon("Sub-task") == "⬜"
    assert get_issue_icon("Unknown Type") == "⬛"


def test_get_issue_icon_case_insensitive():
    """Test that icon lookup is case-insensitive."""
    assert get_issue_icon("bug") == "🟥"
    assert get_issue_icon("BUG") == "🟥"
    assert get_issue_icon("Bug") == "🟥"


def test_format_assignee_with_user():
    """Test formatting assignee with a user."""
    user = User(
        account_id="123",
        display_name="John Doe",
    )
    assert format_assignee(user) == "John Doe"


def test_format_assignee_without_user():
    """Test formatting assignee without a user."""
    assert format_assignee(None) == "Unassigned"


def test_truncate_text_no_truncation():
    """Test truncating text that doesn't need truncation."""
    text = "Short text"
    assert truncate_text(text, 20) == "Short text"


def test_truncate_text_with_truncation():
    """Test truncating long text."""
    text = "This is a very long text that needs truncation"
    result = truncate_text(text, 20)
    assert len(result) == 20
    assert result.endswith("…")


def test_format_issue_line_with_assignee(sample_issue):
    """Test formatting issue line with assignee shown."""
    line = format_issue_line(sample_issue, show_assignee=True)
    assert "🟥" in line  # Bug icon (red square)
    assert "ABC-123" in line
    assert "(John Doe)" in line


def test_format_issue_line_without_assignee(sample_issue):
    """Test formatting issue line without assignee shown."""
    line = format_issue_line(sample_issue, show_assignee=False)
    assert "🟥" in line  # Bug icon (red square)
    assert "ABC-123" in line
    assert "(John Doe)" not in line


def test_format_issue_line_truncates_summary():
    """Test that long summaries are truncated."""
    issue_type = IssueType(id="1", name="Bug")
    issue = Issue(
        key="ABC-123",
        summary="X" * 200,  # Very long summary
        issue_type=issue_type,
        status="Open",
    )
    line = format_issue_line(issue, show_assignee=False, max_width=80)
    assert len(line) <= 80
    assert "…" in line


def test_format_issue_line_very_small_width():
    """Test formatting with very small max_width."""
    user = User(account_id="123", display_name="Very Long Name")
    issue_type = IssueType(id="1", name="Bug")
    issue = Issue(
        key="ABC-123",
        summary="Test summary",
        issue_type=issue_type,
        status="Open",
        assignee=user,
    )
    # Small width that leaves no room for summary
    line = format_issue_line(issue, show_assignee=True, max_width=20)
    assert "🟥" in line
    assert "ABC-123" in line
