# Agent Instructions — JiraLite
You are contributing to JiraLite, a fast, keyboard-first Jira TUI for Linux  
terminal users.

Primary objectives:

- Instant startup
- Low memory usage
- Efficient Jira workflows
- Clear, scannable UI within 80 columns
- Visual issue identification using icons or emojis

When in doubt, follow Design.md.

---

## Hard Requirements

### Style and formatting

- Maximum line length: 80 characters
- Formatting:
	- Use black with line length 80
- Linting:
	- flake8 must pass with zero warnings
- Imports:
	- Use isort with Black-compatible settings

### Type safety

- Type hints are mandatory for all public functions
- Domain models must use frozen, slotted dataclasses
- Avoid use of Any unless explicitly justified

### Dependency boundaries

- ui/ must not perform HTTP calls
- services/ must not import UI code
- domain/ must be framework-agnostic

### Testing

- All new behavior requires tests
- Unit tests must not call real Jira APIs
- HTTP interactions mocked using respx
- Coverage targets:
	- domain/: 100%
	- services/: 100%

### Performance

- Minimize Jira API calls
- Always request explicit fields
- Lazy-load issue details
- Reuse a single async HTTP client
- Avoid storing full JSON payloads

### Security

- Never log secrets or tokens
- Redact authorization headers in logs
- Do not persist credentials unless explicitly configured

---

## Preferred Libraries

- TUI: textual
- HTTP: httpx (async)
- Config: tomllib
- Testing: pytest, respx, pytest-cov
- Linting: flake8
- Formatting: black, isort
- Typing: mypy

---

## Error Handling

- Convert HTTP errors into domain-level exceptions
- Services raise domain exceptions
- UI layer catches and displays actionable messages
- Authentication errors must clearly explain how to fix configuration

---

## Async Rules

- UI event handlers may be async
- No blocking I/O in UI code
- Use background tasks for long-running operations

---

## Logging

- Use Python logging
- Central configuration in util/logging.py
- Default level: INFO
- \--debug enables DEBUG
- Never log tokens or authorization headers

---

## Code Checklist

Before committing:

1. Correct module placement
2. Fully typed functions
3. Tests added
4. 80-column compliance
5. No unnecessary dependencies
6. Minimal Jira API calls
7. Secrets protected

---

## Default JQL Builder

Implement a helper that builds the default JQL based on:

- Issues assigned to the current user
- Completed issues only if resolved within N days
- Default N equals 14 and is configurable

Do not hardcode workflow names or project keys.

---

## UI Key Bindings (Required)

Navigation:

- Up / Down
- j / k

Actions:

- Space: open issue
- e: edit summary and description
- c: add comment
- s: status transition with mandatory comment
- h: history
- o: open issue in web browser (xdg-open)

Help and exit:

- ? or F1: help
- q: quit

Any new binding requires updating the help modal.

---

## Definition of Done

A feature is complete when:

- UI behaves as designed
- Services and domain logic are implemented
- Tests cover success and failure cases
- flake8 passes cleanly
- Code is formatted with Black at 80 columns
- Help and shortcut documentation is updated

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
## Design Documentation Synchronization (Mandatory)

All user-visible features, behaviors, or workflows introduced into JiraLite  
MUST be reflected in Design.md.

This includes, but is not limited to:

- New commands or CLI arguments
- New screens, modals, or UI flows
- New key bindings or shortcuts
- New configuration options
- Changes to default behavior or assumptions
- New performance or caching strategies
- New visual elements (icons, layout changes, indicators)

### Required workflow when adding a feature

When implementing a new feature, the following steps are mandatory:

1. Identify the relevant section(s) in Design.md  
	Examples:
	- UX / Interaction Model
	- Main Screen
	- Issue Modal
	- Performance Strategy
	- Milestones
	- Open Decisions
2. Update Design.md to describe:
	- What the feature does
	- How the user interacts with it
	- Any new defaults or assumptions
	- Any new shortcuts, flags, or configuration
3. Ensure the documentation matches the implemented behavior exactly  
	Design.md must not describe features that do not exist, and code must not  
	implement features that are undocumented.

### Acceptance criteria

A feature is NOT considered complete unless:

- Design.md has been updated accordingly
- The documentation change is part of the same commit or pull request
- The documented behavior matches the actual UI and CLI behavior

### Enforcement guidance for agents

If you are about to introduce or modify functionality and Design.md has not been  
updated:

- Pause implementation
- Update Design.md first
- Then continue with code changes

If unsure where a feature belongs in Design.md:

- Add it to the most relevant existing section
- Or create a clearly named new subsection

Documentation drift is considered a bug.