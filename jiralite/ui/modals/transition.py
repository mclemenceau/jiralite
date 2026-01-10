"""Transition modal screen for JiraLite."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListItem, ListView, TextArea

from jiralite.domain.models import Issue, Transition


class TransitionListItem(ListItem):
    """Custom list item for displaying a transition."""

    def __init__(self, transition: Transition) -> None:
        """Initialize transition list item.

        Args:
            transition: Transition to display
        """
        super().__init__()
        self.transition = transition

    def compose(self) -> ComposeResult:
        """Compose the list item."""
        yield Label(
            f"{self.transition.name} → {self.transition.to_status}"
        )


class TransitionModal(ModalScreen[tuple[str, str] | None]):
    """Modal screen for transitioning an issue with mandatory comment."""

    CSS = """
    TransitionModal {
        align: center middle;
    }

    TransitionModal > Container {
        width: 70;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    TransitionModal Label {
        width: 100%;
        margin-bottom: 1;
    }

    TransitionModal ListView {
        width: 100%;
        height: 10;
        margin-bottom: 1;
    }

    TransitionModal TextArea {
        width: 100%;
        height: 10;
        margin-bottom: 1;
    }

    TransitionModal .button-bar {
        width: 100%;
        height: auto;
        align: center middle;
    }

    TransitionModal Button {
        margin: 0 1;
    }
    """

    def __init__(
        self, issue: Issue, transitions: list[Transition], **kwargs
    ) -> None:
        """Initialize the transition modal.

        Args:
            issue: Issue to transition
            transitions: Available transitions
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.issue = issue
        self.transitions = transitions
        self.selected_transition: Transition | None = None

    def compose(self) -> ComposeResult:
        """Compose the transition layout."""
        with Container():
            yield Label(
                f"Change Status for {self.issue.key} "
                f"(Current: {self.issue.status})"
            )
            yield Label("Select new status:")
            yield ListView(
                *[
                    TransitionListItem(t)
                    for t in self.transitions
                ],
                id="transition_list"
            )
            yield Label("Comment (required):")
            yield TextArea(id="comment_text")
            with Horizontal(classes="button-bar"):
                yield Button("Submit", id="submit", variant="primary")
                yield Button("Cancel", id="cancel")

    @on(ListView.Selected, "#transition_list")
    def transition_selected(
        self, event: ListView.Selected
    ) -> None:
        """Handle transition selection."""
        if isinstance(event.item, TransitionListItem):
            self.selected_transition = event.item.transition

    @on(Button.Pressed, "#submit")
    def submit_transition(self) -> None:
        """Submit the transition."""
        if not self.selected_transition:
            # No transition selected, cannot proceed
            return

        text_area = self.query_one("#comment_text", TextArea)
        comment_text = text_area.text.strip()

        if not comment_text:
            # Comment is mandatory, cannot proceed
            return

        self.dismiss((self.selected_transition.id, comment_text))

    @on(Button.Pressed, "#cancel")
    def cancel_transition(self) -> None:
        """Cancel the transition."""
        self.dismiss(None)
