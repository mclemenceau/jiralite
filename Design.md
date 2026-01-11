---
title: "Jira TUI CLI Design"
source: "https://chatgpt.com/c/6962805b-363c-8328-8e40-553191e5ae1e"
author:
  - "[[ChatGPT]]"
published:
created: 2026-01-10
description: "ChatGPT is your AI chatbot for everyday use. Chat with the most advanced AI to explore ideas, solve problems, and learn faster."
tags:
  - "clippings"
---
JiraLite is a fast, keyboard-first Jira TUI designed for Linux terminal users who  
want to interact with Jira without the cost, latency, and distraction of the web  
UI.

Default workflow:  
launch → view assigned issues → select an issue → perform a quick action  
(edit, comment, transition) → quit.

Primary goal: dramatically reduce friction, memory usage, and context switching  
while preserving Jira’s essential workflows.

---

## Goals

### User goals

- Instant startup with minimal memory footprint
- Immediate visibility of assigned issues
- Full keyboard navigation (arrow keys and vim-style)
- Perform common actions in seconds:
	- Edit summary and description
	- Add comments
	- Change issue status with mandatory rationale
	- View issue history (comments and changelog)
- Comfortable usage within an 80-column terminal
- Visually scannable issue list using icons or emojis per Jira issue type
- Flexible list view that can be extended with additional fields when needed

### Non-goals (v1)

- Jira administration (projects, workflows, screens)
- Advanced bulk editing
- Offline-first workflows

---

## UX / Interaction Model

### Start behavior

- Running `jiralite` with no arguments shows issues assigned to the current user.
- Default query logic:
	- Assigned to current user
	- Not resolved OR resolved within the last 14 days
	- Ordered by most recently updated

Illustrative default JQL logic (not hardcoded):

- assignee = currentUser()
- AND (resolution = EMPTY OR resolved >= -14d)
- ORDER BY updated DESC

### Arguments

- `jiralite --jql "<JQL>"`  
	Override the default query
- `jiralite --project ABC`  
	Convenience helper that expands into JQL
- `jiralite --fields key,summary,assignee,status`  
	Extend the default list view with additional fields
- `jiralite --me`  
	Print resolved Jira identity and exit
- `jiralite --help`
- `jiralite --version`

---

## Main Screen (Issue List)

The main screen is designed to fit comfortably within 80 columns and optimized  
for fast visual scanning.

### Default fields

By default, each issue line displays:

- Issue type icon
- Issue key
- Issue summary
- Assignee, unless the assignee is the current user

If the active JQL assigns issues to the current user, the assignee column is  
hidden by default to reduce visual noise.

### Issue line format

Each issue line begins with an icon representing the Jira issue type, followed by  
the issue key and a truncated summary.

When displayed, the assignee appears at the end of the line.

Example visual layouts:

- 🟩 ABC-128 Add support for multi-project search (John D.)
- 🟦 ABC-131 Update README with authentication examples (Alice M.)

### Default issue type icons

The icon mapping uses colored squares for visual clarity. Default mappings:

- Objective → 🟨
- Epic → 🟪
- Bug → 🟥
- Task → 🟦
- Story → 🟩
- Sub-task → ⬜
- Unknown or custom → ⬛

Icons are intentionally simple Unicode characters to avoid font compatibility  
issues.

### Extensible list fields

The list view is designed to be extensible via the `--fields` parameter.

- Additional fields can be enabled via command-line arguments
- Status is always displayed unless explicitly overridden
- Fields are displayed in the order specified
- Fields are truncated to preserve the 80-column layout
- Unknown or unsupported fields are silently ignored

**Usage:**
```bash
jiralite --fields priority,labels
jiralite --fields assignee,reporter,updated
```

**Supported fields:**
- `status` (default, always shown)
- `priority`
- `assignee`
- `reporter`
- `labels`
- `fix_versions`
- `components`
- `created`
- `updated`

**Display format:**
Each field is truncated to a maximum width to ensure readability:
- status: 15 characters
- priority: 10 characters
- assignee/reporter: 15 characters
- labels/fix_versions/components: 20 characters (comma-separated)
- dates: YYYY-MM-DD format

The default view shows only icon, key, status, and summary to preserve 
readability and performance.

### Key bindings

- Up / Down or j / k  
	Move selection
- Enter or Space  
	Open issue modal
- e  
	Edit summary and description
- c  
	Add comment
- s  
	Change status (comment required)
- h  
	View history
- o
    Open selected issue in the default web browser using xdg-open
    Notes:
        The URL is built from the configured Jira base URL plus the issue key.
        If base URL is missing or invalid, show an actionable error message.
- ? or F1  
	Help
- q  
	Quit

---

## Issue Modal

The issue modal uses a split layout optimized for readability.

### Center panel (approximately 2/3 width)

- Summary
- Description (scrollable, wrapped to 80 columns)

### Right panel (approximately 1/3 width)

- Issue type (with icon)
- Status
- Assignee
- Fix versions
- Labels
- Priority
- Components

### Behavior

- Clear visual separation between panels
- Tab cycles through editable fields
- Read-only fields are visually distinct

- o
    Open this issue in the default web browser using xdg-open
    This provides the same escape hatch from inside the modal.

---

## Performance Strategy

- UI renders immediately with placeholders
- Jira data loads asynchronously
- Issue details fetched only when required
- Jira API calls explicitly request required fields only
- In-memory cache scoped to a single run
- Optional short-lived disk cache as a future enhancement

---

## Technical Architecture

### Language and runtime

- Python 3.11 or newer
- Async I/O throughout

### TUI framework

- textual

### Layering

- ui/  
	Screens, widgets, modals
- services/  
	Jira operations and workflows
- domain/  
	Typed domain models (issues, comments, transitions)
- config/  
	Authentication and configuration
- util/  
	Shared helpers (formatting, logging, time)

---

## Repository Layout

- jiralite/
	- **main**.py
	- app.py
	- cli.py
	- config/
	- domain/
	- services/
	- ui/
	- util/
- tests/
- Design.md
- Agent.md

---

## Testing Strategy

- pytest and pytest-cov
- HTTP calls mocked using respx
- Unit tests:
	- 100% coverage target for domain/
	- 100% coverage target for services/
- UI smoke tests:
	- Application startup
	- Default list rendering
	- Field extension via command-line arguments
	- Key bindings and modal invocation

---

## Coding Standards

- Maximum line length: 80 characters
- Formatting: black with line length 80
- Linting: flake8
- Imports: isort
- Typing: mypy
- Prefer small, focused files with a single responsibility

---

## Milestones

### v0.1

- Configuration and authentication
- Issue list with icons and default fields
- Optional assignee column
- Issue details modal (read-only)
- Add comment
- Help modal
- History modal (comments and changelog)
- Status transition with mandatory comment

### v0.2

- Edit summary and description

### v0.3

- Caching improvements
- Search and filter
- Advanced list field customization
- Polished error handling and UX

---

## Open Decisions

- Jira API v2 vs v3 (configurable)
- User-defined default field presets