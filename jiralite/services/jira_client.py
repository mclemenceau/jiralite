"""Jira API client and service layer."""

import base64
from datetime import datetime
from typing import Any, Optional

import httpx

from jiralite.config import JiraConfig
from jiralite.domain.exceptions import (
    AuthenticationError,
    IssueNotFoundError,
    JiraAPIError,
)
from jiralite.domain.models import (
    ChangelogEntry,
    Comment,
    Issue,
    IssueType,
    Transition,
    User,
)


class JiraClient:
    """Async Jira API client."""

    def __init__(self, config: JiraConfig) -> None:
        """Initialize the Jira client.

        Args:
            config: Jira configuration
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "JiraClient":
        """Enter async context manager."""
        auth_string = f"{self.config.email}:{self.config.api_token}"
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")

        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()

    def _handle_error(self, response: httpx.Response) -> None:
        """Convert HTTP errors to domain exceptions.

        Args:
            response: HTTP response

        Raises:
            AuthenticationError: For 401 responses
            IssueNotFoundError: For 404 responses
            JiraAPIError: For other errors
        """
        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed. Check email and API token."
            )
        elif response.status_code == 404:
            raise IssueNotFoundError("Issue not found", status_code=404)
        else:
            try:
                error_data = response.json()
                message = error_data.get(
                    "errorMessages", [str(response.status_code)]
                )
                if isinstance(message, list):
                    message = "; ".join(message)
            except Exception:
                message = f"HTTP {response.status_code}"

            raise JiraAPIError(message, status_code=response.status_code)

    async def get_current_user(self) -> User:
        """Get the current authenticated user.

        Returns:
            User instance

        Raises:
            AuthenticationError: If authentication fails
            JiraAPIError: If the API call fails
        """
        assert self._client is not None
        response = await self._client.get("/rest/api/3/myself")

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        return User(
            account_id=data["accountId"],
            display_name=data["displayName"],
            email=data.get("emailAddress"),
        )

    async def search_issues(
        self, jql: str, fields: Optional[list[str]] = None
    ) -> list[Issue]:
        """Search for issues using JQL.

        Args:
            jql: JQL query string
            fields: Optional list of field names to retrieve

        Returns:
            List of Issue instances

        Raises:
            JiraAPIError: If the API call fails
        """
        if fields is None:
            fields = [
                "key",
                "summary",
                "issuetype",
                "status",
                "assignee",
                "reporter",
                "description",
                "priority",
                "labels",
                "fixVersions",
                "components",
                "created",
                "updated",
            ]

        params = {
            "jql": jql,
            "fields": ",".join(fields),
            "maxResults": 100,
        }

        assert self._client is not None
        response = await self._client.get(
            "/rest/api/3/search/jql", params=params  # type: ignore[arg-type]
        )

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        issues = []

        for issue_data in data.get("issues", []):
            issues.append(self._parse_issue(issue_data))

        return issues

    async def get_issue(self, key: str) -> Issue:
        """Get a single issue by key.

        Args:
            key: Issue key (e.g., 'ABC-123')

        Returns:
            Issue instance

        Raises:
            IssueNotFoundError: If issue doesn't exist
            JiraAPIError: If the API call fails
        """
        fields = [
            "key",
            "summary",
            "issuetype",
            "status",
            "assignee",
            "reporter",
            "description",
            "priority",
            "labels",
            "fixVersions",
            "components",
            "created",
            "updated",
        ]

        params = {"fields": ",".join(fields)}

        assert self._client is not None
        response = await self._client.get(
            f"/rest/api/3/issue/{key}", params=params  # type: ignore[arg-type]
        )

        if response.status_code != 200:
            self._handle_error(response)

        return self._parse_issue(response.json())

    async def get_comments(self, key: str) -> list[Comment]:
        """Get comments for an issue.

        Args:
            key: Issue key

        Returns:
            List of Comment instances

        Raises:
            JiraAPIError: If the API call fails
        """
        assert self._client is not None
        response = await self._client.get(f"/rest/api/3/issue/{key}/comment")

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        comments = []

        for comment_data in data.get("comments", []):
            comments.append(self._parse_comment(comment_data))

        return comments

    async def add_comment(self, key: str, body: str) -> Comment:
        """Add a comment to an issue.

        Args:
            key: Issue key
            body: Comment text

        Returns:
            Created Comment instance

        Raises:
            JiraAPIError: If the API call fails
        """
        # Convert plain text to Atlassian Document Format (ADF)
        adf_body = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": body}],
                }
            ],
        }

        payload = {"body": adf_body}

        assert self._client is not None
        response = await self._client.post(
            f"/rest/api/3/issue/{key}/comment", json=payload
        )

        if response.status_code not in (200, 201):
            self._handle_error(response)

        return self._parse_comment(response.json())

    async def get_transitions(self, key: str) -> list[Transition]:
        """Get available transitions for an issue.

        Args:
            key: Issue key

        Returns:
            List of Transition instances

        Raises:
            JiraAPIError: If the API call fails
        """
        assert self._client is not None
        response = await self._client.get(
            f"/rest/api/3/issue/{key}/transitions"
        )

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        transitions = []

        for trans_data in data.get("transitions", []):
            transitions.append(
                Transition(
                    id=trans_data["id"],
                    name=trans_data["name"],
                    to_status=trans_data["to"]["name"],
                )
            )

        return transitions

    async def get_changelog(self, key: str) -> list["ChangelogEntry"]:
        """Get changelog for an issue.

        Args:
            key: Issue key

        Returns:
            List of ChangelogEntry instances

        Raises:
            JiraAPIError: If the API call fails
        """
        assert self._client is not None
        response = await self._client.get(
            f"/rest/api/3/issue/{key}?expand=changelog"
        )

        if response.status_code != 200:
            self._handle_error(response)

        data = response.json()
        changelog_entries = []

        changelog = data.get("changelog", {})
        histories = changelog.get("histories", [])

        for history in histories:
            author = self._parse_user(history.get("author"))
            created = self._parse_datetime(history.get("created"))

            for item in history.get("items", []):
                changelog_entries.append(
                    ChangelogEntry(
                        timestamp=created or datetime.now(),
                        author=author
                        or User(account_id="", display_name="Unknown"),
                        field=item.get("field", ""),
                        from_value=item.get("fromString"),
                        to_value=item.get("toString"),
                    )
                )

        return changelog_entries

    async def transition_issue(self, key: str, transition_id: str) -> None:
        """Perform a status transition on an issue.

        Args:
            key: Issue key
            transition_id: Transition ID

        Raises:
            JiraAPIError: If the API call fails
        """
        payload: dict[str, Any] = {"transition": {"id": transition_id}}

        assert self._client is not None
        response = await self._client.post(
            f"/rest/api/3/issue/{key}/transitions", json=payload
        )

        if response.status_code != 204:
            self._handle_error(response)

    def _parse_user(self, data: Optional[dict]) -> Optional[User]:
        """Parse user data from API response.

        Args:
            data: User data dict

        Returns:
            User instance or None
        """
        if not data:
            return None

        return User(
            account_id=data.get("accountId", ""),
            display_name=data.get("displayName", "Unknown"),
            email=data.get("emailAddress"),
        )

    def _parse_issue_type(self, data: dict) -> IssueType:
        """Parse issue type data from API response.

        Args:
            data: Issue type data dict

        Returns:
            IssueType instance
        """
        return IssueType(
            id=data.get("id", ""),
            name=data.get("name", "Unknown"),
            icon_url=data.get("iconUrl"),
        )

    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string.

        Args:
            value: ISO datetime string

        Returns:
            datetime instance or None
        """
        if not value:
            return None

        try:
            # Jira uses format: 2024-01-10T12:34:56.789+0000
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None

    def _extract_text_from_adf(self, adf: dict | str | None) -> str | None:
        """Extract plain text from Atlassian Document Format.

        Args:
            adf: ADF dict, plain string, or None

        Returns:
            Plain text or None
        """
        if adf is None:
            return None

        # Handle plain strings (from older API versions)
        if isinstance(adf, str):
            return adf

        # Handle ADF dict
        if not isinstance(adf, dict):
            return None

        # Recursively extract text from ADF nodes
        text_parts: list[str] = []

        def extract_node(node: Any) -> None:
            """Recursively extract text from ADF node."""
            if isinstance(node, dict):
                # Text nodes have a 'text' field
                if "text" in node:
                    text_parts.append(node["text"])

                # Process child content
                if "content" in node:
                    for child in node["content"]:
                        extract_node(child)

                # Add line breaks for paragraphs and hard breaks
                node_type = node.get("type", "")
                if node_type == "paragraph" and text_parts:
                    text_parts.append("\n")
                elif node_type == "hardBreak":
                    text_parts.append("\n")
            elif isinstance(node, list):
                for item in node:
                    extract_node(item)

        extract_node(adf)

        # Join and clean up text
        text = "".join(text_parts).strip()
        return text if text else None

    def _parse_issue(self, data: dict) -> Issue:
        """Parse issue data from API response.

        Args:
            data: Issue data dict

        Returns:
            Issue instance
        """
        fields = data.get("fields", {})

        # Parse labels
        labels = tuple(fields.get("labels", []))

        # Parse fix versions
        fix_versions = tuple(v["name"] for v in fields.get("fixVersions", []))

        # Parse components
        components = tuple(c["name"] for c in fields.get("components", []))

        return Issue(
            key=data.get("key", ""),
            summary=fields.get("summary", ""),
            issue_type=self._parse_issue_type(fields.get("issuetype", {})),
            status=fields.get("status", {}).get("name", "Unknown"),
            assignee=self._parse_user(fields.get("assignee")),
            reporter=self._parse_user(fields.get("reporter")),
            description=self._extract_text_from_adf(fields.get("description")),
            priority=fields.get("priority", {}).get("name"),
            labels=labels,
            fix_versions=fix_versions,
            components=components,
            created=self._parse_datetime(fields.get("created")),
            updated=self._parse_datetime(fields.get("updated")),
        )

    def _parse_comment(self, data: dict) -> Comment:
        """Parse comment data from API response.

        Args:
            data: Comment data dict

        Returns:
            Comment instance
        """
        author = self._parse_user(data.get("author"))

        return Comment(
            id=data.get("id", ""),
            author=author or User(account_id="", display_name="Unknown"),
            body=self._extract_text_from_adf(data.get("body")) or "",
            created=self._parse_datetime(data.get("created")) or datetime.now(),
            updated=self._parse_datetime(data.get("updated")),
        )


def build_default_jql(days: int = 14) -> str:
    """Build the default JQL query.

    Args:
        days: Number of days to look back for resolved issues

    Returns:
        JQL query string
    """
    return (
        f"(assignee IN (currentUser()) AND "
        f'statusCategory IN ("To Do","In Progress")) OR '
        f"(assignee IN (currentUser()) AND "
        f"statusCategory IN (Done) AND resolved >= -{days}d) "
        f"ORDER BY updated DESC"
    )
