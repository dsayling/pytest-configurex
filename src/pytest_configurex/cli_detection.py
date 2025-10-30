"""Utilities for detecting explicitly set CLI options."""

from typing import Any


def has_cli_option(config: Any, *patterns: str) -> bool:
    """
    Check if any CLI option pattern was explicitly passed.

    Args:
        config: Pytest config object
        patterns: Option patterns to check (e.g., '-v', '--verbose')

    Returns:
        True if any pattern found in invocation args

    Examples:
        >>> has_cli_option(config, '-v', '--verbose')
        >>> has_cli_option(config, '--log-level')
        >>> has_cli_option(config, '-m', '--markers')
    """
    args = config.invocation_params.args
    for arg in args:
        for pattern in patterns:
            # Match exact arg or arg with = value
            if arg == pattern or arg.startswith(pattern + "="):
                return True
    return False
