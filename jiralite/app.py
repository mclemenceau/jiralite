"""Main JiraLite application."""

import sys
from typing import Any, Optional

from textual.app import App

from jiralite.config import JiraConfig
from jiralite.ui.screens import IssueListScreen
from jiralite.util import get_logger

logger = get_logger("app")


class JiraLiteApp(App):
    """JiraLite TUI application."""

    CSS = """
    Screen {
        background: $background;
    }
    """

    TITLE = "JiraLite"
    SUB_TITLE = "Fast, keyboard-first Jira TUI"

    def __init__(
        self,
        config: JiraConfig,
        jql: str,
        additional_fields: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the application.

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

    def on_mount(self) -> None:
        """Mount the main issue list screen."""
        screen = IssueListScreen(
            config=self.config,
            jql=self.jql,
            additional_fields=self.additional_fields,
        )
        self.push_screen(screen)

    def on_exception(self, event: Any) -> None:
        """Handle unhandled exceptions.

        Log to console for debugging while also showing in UI.
        """
        logger.exception(
            f"Unhandled exception in app: {type(event.exception).__name__}: "
            f"{event.exception}"
        )
        # Print to stderr for immediate visibility
        print(
            f"\n{'='*60}\n"
            f"ERROR: {type(event.exception).__name__}: {event.exception}\n"
            f"Check the log above for full traceback.\n"
            f"{'='*60}\n",
            file=sys.stderr,
        )
