"""Help modal screen for JiraLite."""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Label, Markdown


class HelpModal(ModalScreen):
    """Modal screen showing keyboard shortcuts and help."""

    CSS = """
    HelpModal {
        align: center middle;
    }

    HelpModal > Container {
        width: 70;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    HelpModal Label {
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
    }

    HelpModal VerticalScroll {
        width: 100%;
        height: auto;
        max-height: 30;
    }
    """

    HELP_TEXT = """
# JiraLite Help

## Navigation
- **Up/Down** or **j/k** — Move selection
- **Enter** or **Space** — Open issue details
- **Tab** — Cycle through fields

## Actions
- **e** — Edit summary and description
- **c** — Add comment
- **s** — Change status (comment required)
- **h** — View issue history
- **o** — Open issue in web browser

## General
- **?** or **F1** — Show this help
- **q** or **Esc** — Quit / Close modal

## Tips
- All modals can be closed with **Esc**
- The issue list auto-refreshes
- Use **Tab** to navigate between fields in modals
"""

    def compose(self) -> ComposeResult:
        """Compose the help modal layout."""
        with Container():
            yield Label("JiraLite — Keyboard Shortcuts")
            with VerticalScroll():
                yield Markdown(self.HELP_TEXT)
            yield Label("Press any key to close", classes="dim")

    def on_key(self, event) -> None:
        """Close modal on any key press."""
        self.app.pop_screen()
