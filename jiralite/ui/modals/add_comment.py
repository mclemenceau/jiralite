"""Add comment modal screen for JiraLite."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, TextArea

from jiralite.domain.models import Issue


class AddCommentModal(ModalScreen[str]):
    """Modal screen for adding a comment to an issue."""

    CSS = """
    AddCommentModal {
        align: center middle;
    }

    AddCommentModal > Container {
        width: 70;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    AddCommentModal Label {
        width: 100%;
        margin-bottom: 1;
    }

    AddCommentModal TextArea {
        width: 100%;
        height: 15;
        margin-bottom: 1;
    }

    AddCommentModal .button-bar {
        width: 100%;
        height: auto;
        align: center middle;
    }

    AddCommentModal Button {
        margin: 0 1;
    }
    """

    def __init__(self, issue: Issue, **kwargs) -> None:
        """Initialize the add comment modal.

        Args:
            issue: Issue to comment on
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.issue = issue

    def compose(self) -> ComposeResult:
        """Compose the add comment layout."""
        with Container():
            yield Label(f"Add Comment to {self.issue.key}")
            yield TextArea(id="comment_text")
            with Horizontal(classes="button-bar"):
                yield Button("Submit", id="submit", variant="primary")
                yield Button("Cancel", id="cancel")

    @on(Button.Pressed, "#submit")
    def submit_comment(self) -> None:
        """Submit the comment."""
        text_area = self.query_one("#comment_text", TextArea)
        comment_text = text_area.text.strip()

        if comment_text:
            self.dismiss(comment_text)
        else:
            # Show error or just close
            self.dismiss(None)

    @on(Button.Pressed, "#cancel")
    def cancel_comment(self) -> None:
        """Cancel adding comment."""
        self.dismiss(None)

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        if event.key == "escape":
            self.dismiss(None)
