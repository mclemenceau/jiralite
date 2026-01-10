"""Issue detail modal screen for JiraLite."""

import webbrowser

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from jiralite.domain.models import Issue
from jiralite.util import format_assignee, get_issue_icon


class IssueDetailModal(ModalScreen):
    """Modal screen showing issue details in split-panel layout."""

    CSS = """
    IssueDetailModal {
        align: center middle;
    }

    IssueDetailModal > Container {
        width: 90%;
        height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    .detail-header {
        width: 100%;
        height: auto;
        padding: 1;
        background: $boost;
    }

    .detail-content {
        width: 100%;
        height: 1fr;
    }

    .detail-main {
        width: 2fr;
        height: 100%;
        padding: 1;
    }

    .detail-sidebar {
        width: 1fr;
        height: 100%;
        padding: 1;
        background: $panel;
    }

    .field-label {
        color: $text-muted;
        text-style: bold;
    }

    .field-value {
        margin-bottom: 1;
    }

    .description-scroll {
        width: 100%;
        height: 1fr;
        border: solid $primary;
        padding: 1;
        margin-top: 1;
    }

    .button-bar {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }
    """

    def __init__(self, issue: Issue, base_url: str, **kwargs) -> None:
        """Initialize the issue detail modal.

        Args:
            issue: Issue to display
            base_url: Jira base URL
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.issue = issue
        self.base_url = base_url

    def compose(self) -> ComposeResult:
        """Compose the issue detail layout."""
        with Container():
            # Header
            with Container(classes="detail-header"):
                icon = get_issue_icon(self.issue.issue_type.name)
                yield Label(f"{icon} {self.issue.key}: {self.issue.summary}")

            # Main content area (split panel)
            with Horizontal(classes="detail-content"):
                # Left panel: description
                with Container(classes="detail-main"):
                    yield Label("Description", classes="field-label")
                    with VerticalScroll(classes="description-scroll"):
                        desc = self.issue.description or "No description"
                        yield Static(desc)

                # Right panel: metadata
                with Container(classes="detail-sidebar"):
                    yield Label("Type", classes="field-label")
                    yield Label(
                        self.issue.issue_type.name, classes="field-value"
                    )

                    yield Label("Status", classes="field-label")
                    yield Label(self.issue.status, classes="field-value")

                    yield Label("Assignee", classes="field-label")
                    yield Label(
                        format_assignee(self.issue.assignee),
                        classes="field-value",
                    )

                    if self.issue.priority:
                        yield Label("Priority", classes="field-label")
                        yield Label(self.issue.priority, classes="field-value")

                    if self.issue.fix_versions:
                        yield Label("Fix Versions", classes="field-label")
                        yield Label(
                            ", ".join(self.issue.fix_versions),
                            classes="field-value",
                        )

                    if self.issue.labels:
                        yield Label("Labels", classes="field-label")
                        yield Label(
                            ", ".join(self.issue.labels), classes="field-value"
                        )

                    if self.issue.components:
                        yield Label("Components", classes="field-label")
                        yield Label(
                            ", ".join(self.issue.components),
                            classes="field-value",
                        )

            # Button bar
            with Horizontal(classes="button-bar"):
                yield Button("Close (Esc)", id="close", variant="primary")
                yield Button("Open in Browser (o)", id="open_browser")

    @on(Button.Pressed, "#close")
    def close_modal(self) -> None:
        """Close the modal."""
        self.app.pop_screen()

    @on(Button.Pressed, "#open_browser")
    def open_browser(self) -> None:
        """Open issue in web browser."""
        url = f"{self.base_url}/browse/{self.issue.key}"
        webbrowser.open(url)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "o":
            self.open_browser()
