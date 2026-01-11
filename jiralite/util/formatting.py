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
    issue: Issue,
    show_assignee: bool = True,
    max_width: int = 80,
    additional_fields: Optional[list[str]] = None,
) -> str:
    """Format an issue for display in the list view.

    Args:
        issue: Issue to format
        show_assignee: Whether to show assignee
        max_width: Maximum line width
        additional_fields: Additional fields to display

    Returns:
        Formatted issue line
    """
    icon = get_issue_icon(issue.issue_type.name)
    fields = additional_fields or []

    # Fixed column widths for alignment
    key_width = 12

    # Format key with padding
    key_col = f"{issue.key:<{key_width}}"

    # Build additional field columns
    field_parts = []

    # Always include status unless explicitly excluded
    if "status" not in fields:
        fields = ["status"] + fields

    for field_name in fields:
        field_value = _get_field_value(issue, field_name)
        if field_value:
            field_parts.append(field_value)

    # Build assignee text
    assignee_text = ""
    if show_assignee and "assignee" not in fields and issue.assignee:
        assignee_text = f" ({issue.assignee.display_name})"

    # Join field parts with spacing
    fields_text = " ".join(field_parts) if field_parts else ""

    # Calculate available space for summary
    # icon + space + key_col + space + fields + space + summary + assignee
    prefix_len = 2 + key_width + 1
    if fields_text:
        prefix_len += len(fields_text) + 1

    available = max_width - prefix_len - len(assignee_text)

    if available <= 0:
        base = f"{icon} {key_col}"
        if fields_text:
            base += f" {fields_text}"
        return base.strip()

    # Truncate summary if needed
    summary = issue.summary
    if len(summary) > available:
        summary = summary[: available - 1] + "…"

    result = f"{icon} {key_col}"
    if fields_text:
        result += f" {fields_text}"
    result += f" {summary}{assignee_text}"
    return result


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


def _get_field_value(issue: Issue, field_name: str) -> str:
    """Get formatted value for a field.

    Args:
        issue: Issue instance
        field_name: Name of the field to retrieve

    Returns:
        Formatted field value or empty string
    """
    field_map = {
        "status": lambda: issue.status[:15],
        "priority": lambda: issue.priority[:10] if issue.priority else "",
        "assignee": lambda: (
            issue.assignee.display_name[:15] if issue.assignee else "Unassigned"
        ),
        "reporter": lambda: (
            issue.reporter.display_name[:15] if issue.reporter else ""
        ),
        "labels": lambda: (",".join(issue.labels)[:20] if issue.labels else ""),
        "fix_versions": lambda: (
            ",".join(issue.fix_versions)[:20] if issue.fix_versions else ""
        ),
        "components": lambda: (
            ",".join(issue.components)[:20] if issue.components else ""
        ),
        "created": lambda: (
            issue.created.strftime("%Y-%m-%d") if issue.created else ""
        ),
        "updated": lambda: (
            issue.updated.strftime("%Y-%m-%d") if issue.updated else ""
        ),
    }

    getter = field_map.get(field_name)
    if getter:
        return getter()
    return ""


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
