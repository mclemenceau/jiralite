"""Command-line interface for JiraLite."""

import argparse
import asyncio
import sys
from typing import Optional

from jiralite.config import load_config
from jiralite.domain.exceptions import (
    AuthenticationError,
    ConfigurationError,
    JiraLiteException,
)
from jiralite.services import JiraClient, build_default_jql
from jiralite.util import get_logger, setup_logging

logger = get_logger("cli")


async def print_current_user() -> int:
    """Print current user information and exit.

    Returns:
        Exit code
    """
    try:
        config = load_config()
        async with JiraClient(config) as client:
            user = await client.get_current_user()
            print(f"Account ID: {user.account_id}")
            print(f"Display Name: {user.display_name}")
            if user.email:
                print(f"Email: {user.email}")
            return 0
    except (ConfigurationError, AuthenticationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Optional argument list (for testing)

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="jiralite",
        description="Fast, keyboard-first Jira TUI for Linux",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    parser.add_argument(
        "--jql",
        type=str,
        help="Override default JQL query",
    )

    parser.add_argument(
        "--project",
        type=str,
        help="Filter by project key (convenience for JQL)",
    )

    parser.add_argument(
        "--fields",
        type=str,
        help=(
            "Comma-separated list of additional fields to display. "
            "Available fields: status, priority, assignee, reporter, "
            "labels, fix_versions, components, created, updated, description"
        ),
    )

    parser.add_argument(
        "--me",
        action="store_true",
        help="Print current user information and exit",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    return parser.parse_args(args)


def build_jql_from_args(
    args: argparse.Namespace, default_days: int = 14
) -> str:
    """Build JQL query from command-line arguments.

    Args:
        args: Parsed arguments
        default_days: Default number of days for resolved issues

    Returns:
        JQL query string
    """
    if args.jql:
        return str(args.jql)

    if args.project:
        return (
            f"project = {args.project} AND "
            f"((assignee IN (currentUser()) AND "
            f'statusCategory IN ("To Do","In Progress")) OR '
            f"(assignee IN (currentUser()) AND "
            f"statusCategory IN (Done) AND "
            f"resolved >= -{default_days}d)) "
            f"ORDER BY updated DESC"
        )

    return build_default_jql(default_days)


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for CLI.

    Args:
        argv: Optional argument list (for testing)

    Returns:
        Exit code
    """
    args = parse_args(argv)
    setup_logging(debug=args.debug)

    # Handle --me flag
    if args.me:
        return asyncio.run(print_current_user())

    # Import TUI components only if needed
    try:
        from jiralite.app import JiraLiteApp

        # Build JQL query
        config = load_config()
        jql = build_jql_from_args(args, config.default_jql_days)

        # Parse additional fields
        additional_fields = []
        if args.fields:
            additional_fields = [f.strip() for f in args.fields.split(",")]

        # Run the TUI
        app = JiraLiteApp(
            config=config, jql=jql, additional_fields=additional_fields
        )
        app.run()
        return 0

    except (ConfigurationError, AuthenticationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except JiraLiteException as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
