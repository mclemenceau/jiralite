"""History modal screen for JiraLite."""

from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from jiralite.domain.models import ChangelogEntry, Comment


class HistoryModal(ModalScreen):
    """Modal screen showing issue history (comments and changelog)."""

    CSS = """
    HistoryModal {
        align: center middle;
    }

    HistoryModal > Container {
        width: 90%;
        height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }

    .history-header {
        width: 100%;
        height: auto;
        padding: 1;
        background: $boost;
        text-align: center;
    }

    .history-scroll {
        width: 100%;
        height: 1fr;
        padding: 1;
        margin-top: 1;
    }

    .history-entry {
        width: 100%;
        margin-bottom: 2;
        padding: 1;
        background: $panel;
        border-left: thick $accent;
    }

    .history-meta {
        color: $text-muted;
        text-style: italic;
        margin-bottom: 1;
    }

    .changelog-item {
        width: 100%;
        margin-bottom: 1;
        padding: 1;
        background: $surface;
    }

    .button-bar {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }
    """

    def __init__(
        self,
        issue_key: str,
        comments: list[Comment],
        changelog: list[ChangelogEntry],
        **kwargs: Any,
    ) -> None:
        """Initialize the history modal.

        Args:
            issue_key: Issue key for display
            comments: List of comments
            changelog: List of changelog entries
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.issue_key = issue_key
        self.comments = comments
        self.changelog = changelog

    def compose(self) -> ComposeResult:
        """Compose the history layout."""
        with Container():
            # Header
            with Container(classes="history-header"):
                yield Label(f"History for {self.issue_key}")

            # Scrollable content area
            with VerticalScroll(classes="history-scroll"):
                # Merge and sort comments and changelog by timestamp
                all_entries = self._merge_history()

                if not all_entries:
                    yield Static("No history available")
                else:
                    for entry in all_entries:
                        if isinstance(entry, Comment):
                            yield from self._render_comment(entry)
                        else:
                            yield from self._render_changelog(entry)

            # Button bar
            with Container(classes="button-bar"):
                yield Button("Close (Esc)", id="close", variant="primary")

    def _merge_history(
        self,
    ) -> list[Comment | ChangelogEntry]:
        """Merge and sort comments and changelog by timestamp.

        Returns:
            Sorted list of comments and changelog entries
        """
        all_entries: list[Comment | ChangelogEntry] = []
        all_entries.extend(self.comments)
        all_entries.extend(self.changelog)

        # Sort by timestamp (most recent last)
        all_entries.sort(
            key=lambda e: (
                e.timestamp if isinstance(e, ChangelogEntry) else e.created
            )
        )

        return all_entries

    def _render_comment(self, comment: Comment) -> ComposeResult:
        """Render a comment entry.

        Args:
            comment: Comment to render

        Yields:
            Textual widgets for the comment
        """
        with Container(classes="history-entry"):
            timestamp = comment.created.strftime("%Y-%m-%d %H:%M:%S")
            meta = f"💬 {comment.author.display_name} · {timestamp}"
            yield Label(meta, classes="history-meta")
            yield Static(comment.body)

    def _render_changelog(self, entry: ChangelogEntry) -> ComposeResult:
        """Render a changelog entry.

        Args:
            entry: Changelog entry to render

        Yields:
            Textual widgets for the changelog entry
        """
        with Container(classes="changelog-item"):
            timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            meta = f"📝 {entry.author.display_name} · {timestamp}"
            yield Label(meta, classes="history-meta")

            from_val = entry.from_value or "(empty)"
            to_val = entry.to_value or "(empty)"
            change_text = f"{entry.field}: {from_val} → {to_val}"
            yield Static(change_text)

    @on(Button.Pressed, "#close")
    def close_modal(self) -> None:
        """Close the modal."""
        self.app.pop_screen()

    def on_key(self, event: Any) -> None:
        """Handle keyboard shortcuts.

        Args:
            event: Key event
        """
        if event.key == "escape":
            self.app.pop_screen()
