"""Core settings module for pytest-configurex."""

import os
from pathlib import Path
from typing import Any, Optional

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
    log_level: Optional[str] = Field(
        default=None,
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). "
        "Maps to --log-cli-level and --log-file-level.",
    )

    log_cli: bool = Field(
        default=False,
        description="Enable live logging to console. Maps to --log-cli.",
    )

    log_file: Optional[str] = Field(
        default=None,
        description="Path to log file. Maps to --log-file.",
    )

    # Test selection
    markers: Optional[str] = Field(
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

    coverage_report: Optional[str] = Field(
        default=None,
        description="Coverage report type (term, term-missing, html, xml). Maps to --cov-report.",
    )

    # xdist options (pytest-xdist)
    xdist_numprocesses: Optional[int] = Field(
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
    def load_settings(cls, config_root: Optional[Path] = None) -> "PytestSettings":
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
        Apply settings to pytest config object.

        This method is called during pytest_configure hook.
        Override this in subclasses to customize behavior.

        Args:
            config: Pytest config object
        """
        # Store reference to settings in config for fixture access
        config._configurex_settings = self

        # Apply verbosity
        if self.verbosity > 0:
            config.option.verbose = self.verbosity

        # Apply logging settings
        if self.log_level:
            if hasattr(config.option, "log_cli_level"):
                config.option.log_cli_level = self.log_level
            if hasattr(config.option, "log_file_level"):
                config.option.log_file_level = self.log_level

        if self.log_cli:
            if hasattr(config.option, "log_cli"):
                config.option.log_cli = True

        if self.log_file:
            if hasattr(config.option, "log_file"):
                config.option.log_file = self.log_file

        # Apply marker expression
        if self.markers:
            if hasattr(config.option, "markexpr"):
                config.option.markexpr = self.markers

        # Apply coverage settings
        if self.coverage_enabled:
            if hasattr(config.option, "cov_source"):
                if not config.option.cov_source:
                    config.option.cov_source = [self.coverage_source]

        if self.coverage_report:
            if hasattr(config.option, "cov_report"):
                config.option.cov_report = {self.coverage_report: None}

        # Apply xdist settings
        if self.xdist_numprocesses:
            if hasattr(config.option, "numprocesses"):
                config.option.numprocesses = self.xdist_numprocesses

        if hasattr(config.option, "dist"):
            config.option.dist = self.xdist_dist

    def get_cli_args(self) -> list[str]:
        """
        Generate equivalent CLI arguments from settings.

        This is useful for debugging or generating command strings.

        Returns:
            List of CLI argument strings
        """
        args = []

        # Verbosity
        if self.verbosity > 0:
            args.append("-" + "v" * self.verbosity)

        # Logging
        if self.log_level:
            args.append(f"--log-cli-level={self.log_level}")
            args.append(f"--log-file-level={self.log_level}")

        if self.log_cli:
            args.append("--log-cli")

        if self.log_file:
            args.append(f"--log-file={self.log_file}")

        # Markers
        if self.markers:
            args.append(f"-m={self.markers}")

        # Coverage
        if self.coverage_enabled:
            args.append(f"--cov={self.coverage_source}")

        if self.coverage_report:
            args.append(f"--cov-report={self.coverage_report}")

        # xdist
        if self.xdist_numprocesses:
            args.append(f"-n={self.xdist_numprocesses}")

        if hasattr(self, "xdist_dist") and self.xdist_dist != "load":
            args.append(f"--dist={self.xdist_dist}")

        return args

    def __repr__(self) -> str:
        """String representation showing key settings."""
        return (
            f"PytestSettings(verbosity={self.verbosity}, "
            f"log_level={self.log_level!r}, "
            f"markers={self.markers!r})"
        )
