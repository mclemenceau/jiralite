"""Issue detail modal screen for JiraLite."""

import webbrowser
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from jiralite.domain.models import Issue
from jiralite.util import format_assignee, get_issue_icon


class IssueDetailModal(ModalScreen):
    """Modal screen showing issue details."""

    CSS = """
    IssueDetailModal {
        align: center middle;
    }

    #detail-container {
        width: 90%;
        height: 90%;
        background: $surface;
        border: thick $primary;
    }

    #header {
        width: 100%;
        height: auto;
        background: $boost;
        padding: 1;
        border-bottom: solid $primary;
    }

    #content-area {
        width: 100%;
        height: 1fr;
    }

    #description-panel {
        width: 65%;
        height: 100%;
        border-right: solid $primary;
    }

    #metadata-panel {
        width: 35%;
        height: 100%;
    }

    #description-scroll {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    #metadata-scroll {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    .section-title {
        color: $text-muted;
        text-style: bold;
        margin-bottom: 1;
    }

    .field-label {
        color: $text-muted;
        text-style: bold;
        margin-top: 1;
    }

    .field-value {
        margin-bottom: 1;
    }

    #button-bar {
        width: 100%;
        height: auto;
        dock: bottom;
        background: $boost;
        padding: 0 1;
        border-top: solid $primary;
        align: center middle;
    }
    """

    def __init__(self, issue: Issue, base_url: str, **kwargs: Any) -> None:
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
        with Container(id="detail-container"):
            # Header
            with Container(id="header"):
                icon = get_issue_icon(self.issue.issue_type.name)
                yield Label(f"{icon} {self.issue.key}: {self.issue.summary}")

            # Split panel content
            with Horizontal(id="content-area"):
                # Left: Description
                with Container(id="description-panel"):
                    with VerticalScroll(id="description-scroll"):
                        yield Label("Description", classes="section-title")
                        desc = (
                            self.issue.description or "No description provided"
                        )
                        yield Static(desc)

                # Right: Metadata
                with Container(id="metadata-panel"):
                    with VerticalScroll(id="metadata-scroll"):
                        yield Label("Type", classes="field-label")
                        yield Label(
                            self.issue.issue_type.name,
                            classes="field-value",
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
                            yield Label(
                                self.issue.priority, classes="field-value"
                            )

                        if self.issue.fix_versions:
                            yield Label("Fix Versions", classes="field-label")
                            yield Label(
                                ", ".join(self.issue.fix_versions),
                                classes="field-value",
                            )

                        if self.issue.labels:
                            yield Label("Labels", classes="field-label")
                            yield Label(
                                ", ".join(self.issue.labels),
                                classes="field-value",
                            )

                        if self.issue.components:
                            yield Label("Components", classes="field-label")
                            yield Label(
                                ", ".join(self.issue.components),
                                classes="field-value",
                            )

            # Buttons
            with Horizontal(id="button-bar"):
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

    def on_key(self, event: Any) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.app.pop_screen()
        elif event.key == "o":
            self.open_browser()
