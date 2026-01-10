# JiraLite

Fast, keyboard-first Jira TUI for Linux terminal users.

## Overview

JiraLite is a terminal user interface (TUI) for Jira that provides:

- **Instant startup** with minimal memory footprint
- **Keyboard-first navigation** (arrow keys and vim-style bindings)
- **Visual issue identification** using emoji icons
- **Common workflows** in seconds: view, comment, transition
- **80-column friendly** display for comfortable terminal usage

## Features (v0.1)

- ✅ View issues assigned to you
- ✅ Customizable JQL queries
- ✅ Issue details modal with split-panel layout
- ✅ Add comments to issues
- ✅ Open issues in web browser
- ✅ Comprehensive keyboard shortcuts
- ✅ Help modal with all key bindings

## Installation

### Requirements

- Python 3.11 or newer
- Linux (other Unix-like systems may work)
- Jira Cloud instance with API access

### Install from source

```bash
git clone https://github.com/yourusername/jiralite.git
cd jiralite
pip install -e ".[dev]"
```

## Configuration

Create a configuration file at `~/.config/jiralite/config.toml`:

```toml
[jira]
base_url = "https://your-domain.atlassian.net"
email = "your-email@example.com"
api_token = "your-api-token"
default_jql_days = 14  # Optional, defaults to 14
```

### Getting a Jira API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "JiraLite")
4. Copy the token and paste it into your config file

## Usage

### Basic usage

Launch JiraLite to see your assigned issues:

```bash
jiralite
```

### Command-line options

```bash
# Use custom JQL query
jiralite --jql "project = ABC AND status = Open"

# Filter by project
jiralite --project ABC

# Show additional fields in list view
jiralite --fields status,priority,labels

# Print current user info and exit
jiralite --me

# Enable debug logging
jiralite --debug

# Show version
jiralite --version
```

## Keyboard Shortcuts

### Navigation
- **Up/Down** or **j/k** — Move selection
- **Enter** or **Space** — Open issue details
- **Tab** — Cycle through fields

### Actions
- **e** — Edit summary and description (coming in v0.2)
- **c** — Add comment
- **s** — Change status (coming in v0.2)
- **h** — View issue history (coming in v0.2)
- **o** — Open issue in web browser
- **r** — Refresh issue list

### General
- **?** or **F1** — Show help
- **q** or **Esc** — Quit / Close modal

## Default Behavior

By default, JiraLite shows:

- Issues assigned to you
- Not resolved OR resolved within the last 14 days
- Ordered by most recently updated
- Assignee column hidden if all issues are assigned to you

This is equivalent to the JQL query:
```
assignee = currentUser() AND 
(resolution = EMPTY OR resolved >= -14d) 
ORDER BY updated DESC
```

## Issue Type Icons

JiraLite uses colored square emojis to quickly identify issue types:

- 🟨 Objective
- 🟪 Epic
- 🟥 Bug
- 🟦 Task
- 🟩 Story
- ⬜ Sub-task
- ⬛ Unknown/Custom

## Development

### Setup development environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=jiralite --cov-report=html

# Format code
black jiralite tests
isort jiralite tests

# Lint code
flake8 jiralite tests

# Type check
mypy jiralite
```

### Project Structure

```
jiralite/
├── jiralite/
│   ├── config/       # Configuration loading
│   ├── domain/       # Domain models and exceptions
│   ├── services/     # Jira API client
│   ├── ui/           # TUI screens and modals
│   │   ├── modals/   # Modal screens
│   │   └── screens/  # Main screens
│   ├── util/         # Utilities (logging, formatting)
│   ├── app.py        # Main application
│   ├── cli.py        # CLI entry point
│   └── __main__.py   # Python module entry point
├── tests/            # Test suite
├── Design.md         # Design documentation
├── Agent.md          # Agent instructions
└── pyproject.toml    # Project metadata
```

## Roadmap

### v0.2 (Planned)
- Edit summary and description
- Status transition with mandatory comment
- History modal (comments and changelog)

### v0.3 (Planned)
- Caching improvements
- Advanced search and filtering
- Custom field presets
- Enhanced error handling

## Contributing

Contributions are welcome! Please:

1. Follow the design principles in `Design.md`
2. Adhere to coding standards in `Agent.md`
3. Add tests for new functionality
4. Ensure all tests pass and code is formatted
5. Keep line length to 80 characters

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/jiralite/issues
- Documentation: See `Design.md` and `Agent.md`

## Credits

Built with:
- [Textual](https://textual.textualize.io/) - TUI framework
- [httpx](https://www.python-httpx.org/) - HTTP client
- [pytest](https://pytest.org/) - Testing framework
