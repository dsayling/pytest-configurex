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
    pattern_set = set(patterns)
    pattern_prefixes = tuple(pattern + "=" for pattern in patterns)

    return any(arg in pattern_set or arg.startswith(pattern_prefixes) for arg in args)
