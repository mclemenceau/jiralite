"""Domain models for JiraLite.

All models are frozen, slotted dataclasses to ensure immutability
and minimal memory footprint.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True, slots=True)
class User:
    """Represents a Jira user."""

    account_id: str
    display_name: str
    email: Optional[str] = None


@dataclass(frozen=True, slots=True)
class IssueType:
    """Represents a Jira issue type."""

    id: str
    name: str
    icon_url: Optional[str] = None


@dataclass(frozen=True, slots=True)
class Issue:
    """Represents a Jira issue."""

    key: str
    summary: str
    issue_type: IssueType
    status: str
    assignee: Optional[User] = None
    reporter: Optional[User] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    labels: tuple[str, ...] = ()
    fix_versions: tuple[str, ...] = ()
    components: tuple[str, ...] = ()
    created: Optional[datetime] = None
    updated: Optional[datetime] = None


@dataclass(frozen=True, slots=True)
class Comment:
    """Represents a Jira comment."""

    id: str
    author: User
    body: str
    created: datetime
    updated: Optional[datetime] = None


@dataclass(frozen=True, slots=True)
class Transition:
    """Represents a Jira status transition."""

    id: str
    name: str
    to_status: str


@dataclass(frozen=True, slots=True)
class ChangelogEntry:
    """Represents a Jira changelog entry."""

    timestamp: datetime
    author: User
    field: str
    from_value: Optional[str] = None
    to_value: Optional[str] = None
