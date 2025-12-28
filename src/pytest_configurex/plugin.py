"""Main pytest plugin hooks for pytest-configurex."""

import pytest

from pytest_configurex.discovery import load_settings_for_config


def pytest_addoption(parser):
    """Register ini options for configurex settings."""
    # Register ini option for explicit settings class registration
    parser.addini(
        "configurex_settings_class",
        help="Explicit path to custom PytestSettings class (e.g., 'myapp.settings.MySettings')",
        type="string",
        default=None,
    )


def pytest_configure(config):
    """
    Load and apply configurex settings.

    Priority order:
    1. Standard pytest CLI options (e.g., -vv, --log-level=DEBUG, -m unit)
    2. .env.pytest file / custom Settings class
    3. Default values

    Standard pytest CLI options override settings from .env files.
    """
    # Load settings (auto-discovers custom class from conftest.py)
    settings = load_settings_for_config(config)

    # Apply settings to pytest config
    # The apply_to_pytest method checks for CLI options and respects priority
    settings.apply_to_pytest(config)


@pytest.fixture
def configurex(request):
    """
    Fixture providing access to configurex settings.

    Returns:
        PytestSettings: The loaded settings instance

    Example:
        def test_something(configurex):
            assert configurex.verbosity == 2
            assert configurex.log_level == "INFO"
    """
    return request.config._configurex_settings
