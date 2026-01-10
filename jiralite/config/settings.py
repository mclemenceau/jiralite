"""Configuration management for JiraLite."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        raise ImportError(
            "tomli is required for Python < 3.11. "
            "Install with: pip install tomli"
        )

from jiralite.domain.exceptions import (
    AuthenticationError,
    ConfigurationError,
)


@dataclass(frozen=True, slots=True)
class JiraConfig:
    """Jira connection configuration."""

    base_url: str
    email: str
    api_token: str
    default_jql_days: int = 14


def get_config_path() -> Path:
    """Get the path to the configuration file.

    Searches in order:
    1. JIRALITE_CONFIG environment variable
    2. ~/.config/jiralite/config.toml
    3. ~/.jiralite.toml
    """
    # Check environment variable
    if env_path := os.getenv("JIRALITE_CONFIG"):
        return Path(env_path)

    # Check XDG config directory
    xdg_config = Path.home() / ".config" / "jiralite" / "config.toml"
    if xdg_config.exists():
        return xdg_config

    # Check home directory
    home_config = Path.home() / ".jiralite.toml"
    if home_config.exists():
        return home_config

    # Default to XDG location
    return xdg_config


def load_config() -> JiraConfig:
    """Load configuration from TOML file.

    Returns:
        JiraConfig instance

    Raises:
        ConfigurationError: If config file is missing or invalid
        AuthenticationError: If credentials are missing
    """
    config_path = get_config_path()

    if not config_path.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_path}\n"
            f"Create a config file at {config_path} with:\n"
            f"  [jira]\n"
            f"  base_url = 'https://your-domain.atlassian.net'\n"
            f"  email = 'your-email@example.com'\n"
            f"  api_token = 'your-api-token'\n"
        )

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        raise ConfigurationError(
            f"Failed to parse config file {config_path}: {e}"
        )

    # Validate required fields
    jira_config = data.get("jira", {})

    base_url = jira_config.get("base_url", "").rstrip("/")
    email = jira_config.get("email", "")
    api_token = jira_config.get("api_token", "")

    if not base_url:
        raise ConfigurationError("Missing 'base_url' in [jira] section")
    if not email:
        raise AuthenticationError("Missing 'email' in [jira] section")
    if not api_token:
        raise AuthenticationError("Missing 'api_token' in [jira] section")

    # Optional fields
    default_jql_days = jira_config.get("default_jql_days", 14)

    return JiraConfig(
        base_url=base_url,
        email=email,
        api_token=api_token,
        default_jql_days=default_jql_days,
    )
