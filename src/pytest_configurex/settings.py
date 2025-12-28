"""Core settings module for pytest-configurex."""

from pathlib import Path
from typing import Any

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
        env_file=None,  # Handled via _env_file parameter in load_settings
        env_file_encoding="utf-8",
        extra="allow",  # Allow extra fields from environment variables
        case_sensitive=False,
    )
    # Note: Extra/custom fields work from environment variables but not from .env files
    # when using _env_file parameter. This is a pydantic-settings limitation.

    @classmethod
    def load_settings(cls, config_root: Path | None = None) -> "PytestSettings":
        """
        Load settings with proper .env file fallback.

        Priority:
        1. Environment variables with X_ prefix (highest)
        2. .env.pytest file
        3. .env file (fallback)
        4. Default values

        Args:
            config_root: Root directory to search for .env files. Defaults to cwd.

        Returns:
            PytestSettings instance
        """
        if config_root is None:
            config_root = Path.cwd()

        # Pydantic-settings loads files in order, with later files overriding earlier ones
        # List .env first, then .env.pytest so .env.pytest takes precedence
        # Environment variables automatically take precedence over all files
        env_files = [
            config_root / ".env",
            config_root / ".env.pytest",
        ]

        return cls(_env_file=env_files, _env_file_encoding="utf-8")

    def _apply_verbosity(self, config: Any) -> None:
        """Apply verbosity setting if not overridden by CLI."""
        from pytest_configurex.cli_detection import has_cli_option

        if self.verbosity > 0 and not has_cli_option(config, "-v", "-vv", "-vvv", "--verbose"):
            config.option.verbose = self.verbosity

    def _apply_logging_settings(self, config: Any) -> None:
        """Apply logging-related settings if not overridden by CLI."""
        from pytest_configurex.cli_detection import has_cli_option

        # Log level
        if self.log_level and not has_cli_option(
            config, "--log-level", "--log-cli-level", "--log-file-level"
        ):
            if hasattr(config.option, "log_cli_level"):
                config.option.log_cli_level = self.log_level
            if hasattr(config.option, "log_file_level"):
                config.option.log_file_level = self.log_level

        # Log CLI
        if self.log_cli and not has_cli_option(config, "--log-cli"):
            if hasattr(config.option, "log_cli"):
                config.option.log_cli = True

        # Log file
        if self.log_file and not has_cli_option(config, "--log-file"):
            if hasattr(config.option, "log_file"):
                config.option.log_file = self.log_file

    def _apply_marker_settings(self, config: Any) -> None:
        """Apply marker expression setting if not overridden by CLI."""
        from pytest_configurex.cli_detection import has_cli_option

        if self.markers and not has_cli_option(config, "-m", "--markers"):
            if hasattr(config.option, "markexpr"):
                config.option.markexpr = self.markers

    def _apply_coverage_settings(self, config: Any) -> None:
        """Apply coverage-related settings if not overridden by CLI."""
        from pytest_configurex.cli_detection import has_cli_option

        # Coverage enabled
        if self.coverage_enabled and not has_cli_option(config, "--cov"):
            if hasattr(config.option, "cov_source"):
                if not config.option.cov_source:
                    config.option.cov_source = [self.coverage_source]

        # Coverage report
        if self.coverage_report and not has_cli_option(config, "--cov-report"):
            if hasattr(config.option, "cov_report"):
                config.option.cov_report = {self.coverage_report: None}

    def _apply_xdist_settings(self, config: Any) -> None:
        """Apply xdist-related settings if not overridden by CLI."""
        from pytest_configurex.cli_detection import has_cli_option

        # Number of processes
        if self.xdist_numprocesses and not has_cli_option(config, "-n", "--numprocesses"):
            if hasattr(config.option, "numprocesses"):
                config.option.numprocesses = self.xdist_numprocesses

        # Distribution mode
        if self.xdist_dist and not has_cli_option(config, "--dist"):
            if hasattr(config.option, "dist"):
                config.option.dist = self.xdist_dist

    def apply_to_pytest(self, config: Any) -> None:
        """
        Apply settings to pytest config object, respecting CLI priority.

        Standard pytest CLI options take precedence over .env settings.
        This method is called during pytest_configure hook.
        Override this in subclasses to customize behavior.

        Args:
            config: Pytest config object
        """
        # Store reference to settings in config for fixture access
        config._configurex_settings = self

        # Apply all settings categories
        self._apply_verbosity(config)
        self._apply_logging_settings(config)
        self._apply_marker_settings(config)
        self._apply_coverage_settings(config)
        self._apply_xdist_settings(config)

    def __repr__(self) -> str:
        """String representation showing key settings."""
        return (
            f"PytestSettings(verbosity={self.verbosity}, "
            f"log_level={self.log_level!r}, "
            f"markers={self.markers!r})"
        )
