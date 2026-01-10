"""Utility functions for formatting and display."""

from typing import Optional

from jiralite.domain.models import Issue, User


# Default issue type icon mapping
ISSUE_TYPE_ICONS = {
    "objective": "🟨",
    "epic": "🟪",
    "bug": "🟥",
    "task": "🟦",
    "story": "🟩",
    "sub-task": "⬜",
}


def get_issue_icon(issue_type_name: str) -> str:
    """Get the icon for an issue type.

    Args:
        issue_type_name: Name of the issue type

    Returns:
        Icon character
    """
    normalized = issue_type_name.lower().strip()
    return ISSUE_TYPE_ICONS.get(normalized, "⬛")


def format_issue_line(
    issue: Issue, show_assignee: bool = True, max_width: int = 80
) -> str:
    """Format an issue for display in the list view.

    Args:
        issue: Issue to format
        show_assignee: Whether to show assignee
        max_width: Maximum line width

    Returns:
        Formatted issue line
    """
    icon = get_issue_icon(issue.issue_type.name)

    # Fixed column widths for alignment
    key_width = 12
    status_width = 15
    
    # Format key and status with padding
    key_col = f"{issue.key:<{key_width}}"
    status_col = f"{issue.status:<{status_width}}"
    
    # Build assignee text
    assignee_text = ""
    if show_assignee and issue.assignee:
        assignee_text = f" ({issue.assignee.display_name})"

    # Calculate available space for summary
    # icon + space + key_col + space + status_col + space + summary + assignee
    # 2 (icon + space) + key_width + 1 (space) + status_width + 1 (space)
    prefix_len = 2 + key_width + 1 + status_width + 1
    available = max_width - prefix_len - len(assignee_text)

    if available <= 0:
        return f"{icon} {key_col} {status_col}".strip()

    # Truncate summary if needed
    summary = issue.summary
    if len(summary) > available:
        summary = summary[: available - 1] + "…"

    return f"{icon} {key_col} {status_col} {summary}{assignee_text}"
    if len(summary) > available:
        summary = summary[: available - 1] + "…"

    return f"{icon} {key_col}{status_col}{summary}{assignee_text}"


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text with ellipsis if too long.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"


def format_assignee(assignee: Optional[User]) -> str:
    """Format assignee for display.

    Args:
        assignee: User instance or None

    Returns:
        Formatted assignee string
    """
    if not assignee:
        return "Unassigned"
    return assignee.display_name
