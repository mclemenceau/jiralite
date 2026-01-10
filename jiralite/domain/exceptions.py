"""Domain-level exceptions for JiraLite."""

from typing import Optional


class JiraLiteException(Exception):
    """Base exception for all JiraLite errors."""

    pass


class AuthenticationError(JiraLiteException):
    """Raised when authentication fails."""

    pass


class ConfigurationError(JiraLiteException):
    """Raised when configuration is invalid or missing."""

    pass


class JiraAPIError(JiraLiteException):
    """Raised when Jira API returns an error."""

    def __init__(
        self, message: str, status_code: Optional[int] = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class IssueNotFoundError(JiraAPIError):
    """Raised when an issue cannot be found."""

    pass
