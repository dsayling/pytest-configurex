"""Core settings module for pytest-configurex."""

import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PytestSettings(BaseSettings):
    """
    Pydantic settings class for pytest configuration.

    This class loads settings from .env.pytest (or .env as fallback) and
    environment variables with the X_ prefix.

    Fields can be customized by subclassing this class in your conftest.py.
    """

    # Verbosity: maps to -v, -vv, -vvv
    verbosity: int = Field(
        default=0,
        ge=0,
        le=3,
        description="Verbosity level (0-3). Maps to -v flags.",
    )

    # Logging configuration
    log_level: str | None = Field(
        default=None,
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). "
        "Maps to --log-cli-level and --log-file-level.",
    )

    log_cli: bool = Field(
        default=False,
        description="Enable live logging to console. Maps to --log-cli.",
    )

    log_file: str | None = Field(
        default=None,
        description="Path to log file. Maps to --log-file.",
    )

    # Test selection
    markers: str | None = Field(
        default=None,
        description="Marker expression to filter tests. Maps to -m.",
    )

    # Coverage options (pytest-cov)
    coverage_enabled: bool = Field(
        default=False,
        description="Enable coverage reporting. Maps to --cov.",
    )

    coverage_source: str = Field(
        default=".",
        description="Coverage source path. Used with --cov.",
    )

    coverage_report: str | None = Field(
        default=None,
        description="Coverage report type (term, term-missing, html, xml). Maps to --cov-report.",
    )

    # xdist options (pytest-xdist)
    xdist_numprocesses: int | None = Field(
        default=None,
        ge=1,
        description="Number of parallel processes. Maps to -n.",
    )

    xdist_dist: str = Field(
        default="load",
        description="Distribution mode for xdist (load, loadscope, etc). Maps to --dist.",
    )

    model_config = SettingsConfigDict(
        env_prefix="X_",
        env_file=None,  # We'll handle this manually in load_settings
        env_file_encoding="utf-8",
        extra="allow",  # Allow extra fields for user extensions
        case_sensitive=False,
    )

    @classmethod
    def load_settings(cls, config_root: Path | None = None) -> "PytestSettings":
        """
        Load settings with proper .env file fallback.

        Priority:
        1. .env.pytest
        2. .env (fallback)
        3. Environment variables with X_ prefix
        4. Default values

        Args:
            config_root: Root directory to search for .env files. Defaults to cwd.

        Returns:
            PytestSettings instance
        """
        if config_root is None:
            config_root = Path.cwd()

        env_pytest = config_root / ".env.pytest"
        env_default = config_root / ".env"

        # Determine which env file to use
        env_file = None
        if env_pytest.exists():
            env_file = env_pytest
        elif env_default.exists():
            env_file = env_default

        # Load env file values and temporarily set them in the environment
        # This allows pydantic-settings to pick them up
        env_vars_to_restore = {}
        env_vars_to_delete = []

        if env_file:
            # Load values from env file
            env_values = dotenv_values(env_file)

            # Temporarily set these in the environment
            for key, value in env_values.items():
                if value is not None:  # dotenv_values can return None for empty values
                    # Store original value if it exists
                    if key in os.environ:
                        env_vars_to_restore[key] = os.environ[key]
                    else:
                        env_vars_to_delete.append(key)
                    # Set the new value from .env file
                    # But only if it's not already set (env vars take precedence over .env)
                    if key not in os.environ:
                        os.environ[key] = value

        try:
            # Create instance - pydantic-settings will now read from environment
            return cls()
        finally:
            # Restore original environment
            for key in env_vars_to_delete:
                if key in os.environ:
                    del os.environ[key]
            for key, value in env_vars_to_restore.items():
                os.environ[key] = value

    def apply_to_pytest(self, config: Any) -> None:
        """
        Apply settings to pytest config object, respecting CLI priority.

        Standard pytest CLI options take precedence over .env settings.
        This method is called during pytest_configure hook.
        Override this in subclasses to customize behavior.

        Args:
            config: Pytest config object
        """
        from pytest_configurex.cli_detection import has_cli_option

        # Store reference to settings in config for fixture access
        config._configurex_settings = self

        # Apply verbosity - only if not set via CLI (-v, -vv, -vvv, --verbose)
        if self.verbosity > 0 and not has_cli_option(config, "-v", "-vv", "-vvv", "--verbose"):
            config.option.verbose = self.verbosity

        # Apply log level - only if not set via CLI
        if self.log_level and not has_cli_option(
            config, "--log-level", "--log-cli-level", "--log-file-level"
        ):
            if hasattr(config.option, "log_cli_level"):
                config.option.log_cli_level = self.log_level
            if hasattr(config.option, "log_file_level"):
                config.option.log_file_level = self.log_level

        # Apply log CLI - only if not set via CLI
        if self.log_cli and not has_cli_option(config, "--log-cli"):
            if hasattr(config.option, "log_cli"):
                config.option.log_cli = True

        # Apply log file - only if not set via CLI
        if self.log_file and not has_cli_option(config, "--log-file"):
            if hasattr(config.option, "log_file"):
                config.option.log_file = self.log_file

        # Apply marker expression - only if not set via CLI
        if self.markers and not has_cli_option(config, "-m", "--markers"):
            if hasattr(config.option, "markexpr"):
                config.option.markexpr = self.markers

        # Apply coverage settings - only if not set via CLI
        if self.coverage_enabled and not has_cli_option(config, "--cov"):
            if hasattr(config.option, "cov_source"):
                if not config.option.cov_source:
                    config.option.cov_source = [self.coverage_source]

        # Apply coverage report - only if not set via CLI
        if self.coverage_report and not has_cli_option(config, "--cov-report"):
            if hasattr(config.option, "cov_report"):
                config.option.cov_report = {self.coverage_report: None}

        # Apply xdist numprocesses - only if not set via CLI
        if self.xdist_numprocesses and not has_cli_option(config, "-n", "--numprocesses"):
            if hasattr(config.option, "numprocesses"):
                config.option.numprocesses = self.xdist_numprocesses

        # Apply xdist dist - only if not set via CLI
        if self.xdist_dist and not has_cli_option(config, "--dist"):
            if hasattr(config.option, "dist"):
                config.option.dist = self.xdist_dist

    def __repr__(self) -> str:
        """String representation showing key settings."""
        return (
            f"PytestSettings(verbosity={self.verbosity}, "
            f"log_level={self.log_level!r}, "
            f"markers={self.markers!r})"
        )
