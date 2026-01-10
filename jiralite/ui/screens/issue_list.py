"""Main issue list screen for JiraLite."""

import webbrowser

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, ListItem, ListView

from jiralite.config import JiraConfig
from jiralite.domain.models import Issue
from jiralite.services import JiraClient
from jiralite.ui.modals import (
    AddCommentModal,
    HelpModal,
    IssueDetailModal,
    TransitionModal,
)
from jiralite.util import format_issue_line, get_logger

logger = get_logger("ui.issue_list")


class IssueListItem(ListItem):
    """Custom list item for displaying an issue."""

    def __init__(self, issue: Issue, show_assignee: bool = True) -> None:
        """Initialize issue list item.

        Args:
            issue: Issue to display
            show_assignee: Whether to show assignee
        """
        super().__init__()
        self.issue = issue
        self.show_assignee = show_assignee
        self._label: Label | None = None

    def compose(self) -> ComposeResult:
        """Compose the list item."""
        # Start with 80 columns, will update on mount
        line = format_issue_line(
            self.issue, show_assignee=self.show_assignee, max_width=80
        )
        self._label = Label(line)
        yield self._label

    def on_resize(self) -> None:
        """Update label when widget is resized."""
        if self._label is not None and self.size.width > 0:
            max_width = max(80, self.size.width)
            line = format_issue_line(
                self.issue,
                show_assignee=self.show_assignee,
                max_width=max_width,
            )
            self._label.update(line)


class IssueListScreen(Screen):
    """Main screen showing list of issues."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("?", "help", "Help"),
        ("c", "add_comment", "Add Comment"),
        ("s", "transition", "Change Status"),
        ("h", "show_history", "History"),
        ("o", "open_browser", "Open in Browser"),
        ("r", "refresh", "Refresh"),
    ]

    CSS = """
    IssueListScreen {
        background: $background;
    }

    IssueListScreen Container {
        width: 100%;
        height: 100%;
    }

    IssueListScreen ListView {
        width: 100%;
        height: 1fr;
        background: $surface;
    }

    IssueListScreen .loading {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: $text-muted;
    }

    IssueListScreen .error {
        width: 100%;
        height: 100%;
        content-align: center middle;
        color: $error;
    }
    """

    def __init__(
        self,
        config: JiraConfig,
        jql: str,
        additional_fields: list[str] = None,
        **kwargs,
    ) -> None:
        """Initialize the issue list screen.

        Args:
            config: Jira configuration
            jql: JQL query to execute
            additional_fields: Additional fields to display
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.config = config
        self.jql = jql
        self.additional_fields = additional_fields or []
        self.issues: list[Issue] = []
        self.current_user_id: str = ""

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()
        with Container():
            yield Label("Loading issues...", classes="loading")
        yield Footer()

    def on_mount(self) -> None:
        """Load issues when screen is mounted."""
        self.load_issues()

    @work(exclusive=True)
    async def load_issues(self) -> None:
        """Load issues from Jira API."""
        try:
            async with JiraClient(self.config) as client:
                # Get current user
                user = await client.get_current_user()
                self.current_user_id = user.account_id

                # Search issues
                self.issues = await client.search_issues(self.jql)

                # Update UI
                self.refresh_issue_list()

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.exception(f"Failed to load issues: {error_msg}")
            self.show_error(error_msg)

    def refresh_issue_list(self) -> None:
        """Refresh the issue list display."""
        # Clear current content
        container = self.query_one(Container)
        container.remove_children()

        if not self.issues:
            container.mount(Label("No issues found", classes="loading"))
            return

        # Determine if we should show assignee
        # Hide assignee if all issues are assigned to current user
        show_assignee = any(
            issue.assignee is None
            or issue.assignee.account_id != self.current_user_id
            for issue in self.issues
        )

        # Create and mount list view first
        list_view = ListView()
        container.mount(list_view)

        # Then populate it with items
        for issue in self.issues:
            list_view.append(IssueListItem(issue, show_assignee=show_assignee))

        list_view.focus()

    def show_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message to display
        """
        # Log to console for easy copying
        logger.error(f"Error displayed to user: {message}")

        container = self.query_one(Container)
        container.remove_children()
        container.mount(Label(f"Error: {message}", classes="error"))

    def get_selected_issue(self) -> Issue | None:
        """Get the currently selected issue.

        Returns:
            Selected Issue or None
        """
        try:
            list_view = self.query_one(ListView)
            if list_view.index is not None:
                item = list_view.highlighted_child
                if isinstance(item, IssueListItem):
                    return item.issue
        except Exception:
            pass
        return None

    @on(ListView.Selected)
    def show_issue_detail(self, event: ListView.Selected) -> None:
        """Show issue detail modal when item is selected."""
        if isinstance(event.item, IssueListItem):
            modal = IssueDetailModal(event.item.issue, self.config.base_url)
            self.app.push_screen(modal)

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_help(self) -> None:
        """Show help modal."""
        self.app.push_screen(HelpModal())

    def action_add_comment(self) -> None:
        """Add comment to selected issue."""
        issue = self.get_selected_issue()
        if not issue:
            return

        def handle_comment(comment_text: str | None) -> None:
            if comment_text:
                self.submit_comment(issue, comment_text)

        self.app.push_screen(AddCommentModal(issue), handle_comment)

    def action_transition(self) -> None:
        """Transition selected issue to a new status."""
        issue = self.get_selected_issue()
        if not issue:
            return

        # Load transitions and show modal
        self.load_and_show_transitions(issue)

    @work(exclusive=True)
    async def load_and_show_transitions(self, issue: Issue) -> None:
        """Load available transitions and show transition modal.

        Args:
            issue: Issue to transition
        """
        try:
            async with JiraClient(self.config) as client:
                transitions = await client.get_transitions(issue.key)

                if not transitions:
                    self.notify(
                        f"No transitions available for {issue.key}",
                        severity="warning",
                    )
                    return

                def handle_transition(result: tuple[str, str] | None) -> None:
                    if result:
                        transition_id, comment = result
                        self.submit_transition(issue, transition_id, comment)

                self.app.push_screen(
                    TransitionModal(issue, transitions), handle_transition
                )

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.exception(f"Failed to load transitions: {error_msg}")
            self.notify(f"Error: {error_msg}", severity="error")

    @work(exclusive=True)
    async def submit_transition(
        self, issue: Issue, transition_id: str, comment: str
    ) -> None:
        """Submit status transition to Jira.

        Args:
            issue: Issue to transition
            transition_id: ID of the transition
            comment: Comment text (mandatory)
        """
        try:
            async with JiraClient(self.config) as client:
                await client.transition_issue(issue.key, transition_id, comment)
                self.notify(f"Status changed for {issue.key}")
                # Refresh to show updated status
                self.load_issues()
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.exception(f"Failed to transition issue: {error_msg}")
            self.notify(f"Error: {error_msg}", severity="error")

    @work(exclusive=True)
    async def submit_comment(self, issue: Issue, comment_text: str) -> None:
        """Submit comment to Jira.

        Args:
            issue: Issue to comment on
            comment_text: Comment text
        """
        try:
            async with JiraClient(self.config) as client:
                await client.add_comment(issue.key, comment_text)
                self.notify(f"Comment added to {issue.key}")
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            logger.exception(f"Failed to add comment: {error_msg}")
            self.notify(f"Error: {error_msg}", severity="error")

    def action_show_history(self) -> None:
        """Show issue history (placeholder for v0.2)."""
        self.notify("History view coming in v0.2")

    def action_open_browser(self) -> None:
        """Open selected issue in web browser."""
        issue = self.get_selected_issue()
        if issue:
            url = f"{self.config.base_url}/browse/{issue.key}"
            webbrowser.open(url)

    def action_refresh(self) -> None:
        """Refresh the issue list."""
        self.load_issues()
