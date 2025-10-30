"""Main pytest plugin hooks for pytest-configurex."""

import pytest

from pytest_pytest_configurex.discovery import load_settings_for_config


def pytest_addoption(parser):
    """Register CLI options for configurex settings."""
    group = parser.getgroup("configurex", "pytest-configurex configuration")

    # Verbosity
    group.addoption(
        "--configurex-verbosity",
        action="store",
        type=int,
        dest="configurex_verbosity",
        default=None,
        help="Verbosity level (0-3). Maps to -v flags.",
    )

    # Logging
    group.addoption(
        "--configurex-log-level",
        action="store",
        dest="configurex_log_level",
        default=None,
        help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )

    group.addoption(
        "--configurex-log-cli",
        action="store_true",
        dest="configurex_log_cli",
        default=None,
        help="Enable live logging to console.",
    )

    group.addoption(
        "--configurex-log-file",
        action="store",
        dest="configurex_log_file",
        default=None,
        help="Path to log file.",
    )

    # Markers
    group.addoption(
        "--configurex-markers",
        action="store",
        dest="configurex_markers",
        default=None,
        help="Marker expression to filter tests.",
    )

    # Coverage
    group.addoption(
        "--configurex-coverage",
        action="store_true",
        dest="configurex_coverage",
        default=None,
        help="Enable coverage reporting.",
    )

    group.addoption(
        "--configurex-coverage-source",
        action="store",
        dest="configurex_coverage_source",
        default=None,
        help="Coverage source path.",
    )

    group.addoption(
        "--configurex-coverage-report",
        action="store",
        dest="configurex_coverage_report",
        default=None,
        help="Coverage report type (term, term-missing, html, xml).",
    )

    # xdist
    group.addoption(
        "--configurex-xdist-n",
        action="store",
        type=int,
        dest="configurex_xdist_n",
        default=None,
        help="Number of parallel processes for xdist.",
    )

    group.addoption(
        "--configurex-xdist-dist",
        action="store",
        dest="configurex_xdist_dist",
        default=None,
        help="Distribution mode for xdist (load, loadscope, etc).",
    )


def pytest_configure(config):
    """
    Load and apply configurex settings.

    Priority order:
    1. CLI options (--configurex-*)
    2. .env.pytest / custom Settings class
    3. Default values

    CLI options override settings from .env files.
    """
    # Load settings (auto-discovers custom class from conftest.py)
    settings = load_settings_for_config(config)

    # Override settings with CLI options if provided
    # This implements the priority system: CLI > env > defaults

    if config.option.configurex_verbosity is not None:
        settings.verbosity = config.option.configurex_verbosity

    if config.option.configurex_log_level is not None:
        settings.log_level = config.option.configurex_log_level

    if config.option.configurex_log_cli is not None:
        settings.log_cli = config.option.configurex_log_cli

    if config.option.configurex_log_file is not None:
        settings.log_file = config.option.configurex_log_file

    if config.option.configurex_markers is not None:
        settings.markers = config.option.configurex_markers

    if config.option.configurex_coverage is not None:
        settings.coverage_enabled = config.option.configurex_coverage

    if config.option.configurex_coverage_source is not None:
        settings.coverage_source = config.option.configurex_coverage_source

    if config.option.configurex_coverage_report is not None:
        settings.coverage_report = config.option.configurex_coverage_report

    if config.option.configurex_xdist_n is not None:
        settings.xdist_numprocesses = config.option.configurex_xdist_n

    if config.option.configurex_xdist_dist is not None:
        settings.xdist_dist = config.option.configurex_xdist_dist

    # Apply settings to pytest config
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
