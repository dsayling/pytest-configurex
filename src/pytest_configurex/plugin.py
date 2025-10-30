"""Main pytest plugin integration for pytest-configurex."""

import pytest

from .core import get_env_file_path, load_env, merge_layers
from .registry import registry


def pytest_addhooks(pluginmanager):
    """Register custom hooks for configurex."""
    from . import hookspec

    pluginmanager.add_hookspecs(hookspec)


def pytest_addoption(parser):
    """Add command-line options and ini settings for all registered fields."""
    group = parser.getgroup("configurex", "pytest-configurex configuration")

    # Add options for all registered fields
    for field, meta in registry.items():
        cli_flag = meta["cli"]
        ini_key = meta["ini"]

        # Determine help text based on field name
        help_text = f"Configurex option: {field}"
        if ini_key:
            help_text += f" (ini: {ini_key})"

        # Add CLI option
        group.addoption(
            cli_flag,
            action="store",
            dest=cli_flag.lstrip("-").replace("-", "_"),
            help=help_text,
        )

        # Add ini setting if specified
        if ini_key:
            parser.addini(
                ini_key,
                help=help_text,
                type="string",
            )


def pytest_configure(config):
    """Configure pytest with merged settings from env, CLI, and ini.

    This hook:
    1. Calls pytest_configurex_register to let other plugins register mappings
    2. Loads settings from .env file
    3. Merges with CLI and ini values
    4. Stores result in config._configurex for access via fixture
    """
    # Allow external plugins to register their mappings
    config.pluginmanager.hook.pytest_configurex_register(registry=registry)

    # Find and load .env file
    env_file = get_env_file_path(config)
    env_settings = load_env(env_file)

    # Merge all configuration layers
    merged = merge_layers(env_settings, config, registry)

    # Store in config for access via fixture
    config._configurex = merged  # type: ignore[attr-defined]


@pytest.fixture(scope="session")
def configurex(pytestconfig):
    """Fixture to access merged configurex settings.

    Returns a dictionary with all merged configuration values
    from .env, CLI, and pytest.ini, with proper precedence.

    Example:
        >>> def test_something(configurex):
        ...     log_level = configurex.get("log_level")
        ...     assert log_level == "DEBUG"
    """
    return getattr(pytestconfig, "_configurex", {})
