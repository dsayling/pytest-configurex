"""Core settings module for pytest-configurex."""

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@dataclass
class PytestFieldMapping:
    """
    Metadata for mapping a Pydantic field to pytest configuration options.

    This dataclass defines how a settings field should be applied to pytest's
    config object, including CLI detection, value transformation, and conditional
    application logic.

    Attributes:
        pytest_options: Tuple of pytest config.option attribute names to set.
                       Can specify multiple targets (e.g., both log_cli_level and log_file_level).
        cli_flags: Tuple of CLI flags that, if present, prevent this setting from applying.
                  Respects pytest's CLI priority.
        apply_when: Condition for when to apply the setting based on field value:
                   - "always": Always apply regardless of value
                   - "if_truthy": Only apply if value is truthy (e.g., non-zero, non-empty)
                   - "if_not_none": Only apply if value is not None
        transform: Optional function to transform the value before setting.
                  Useful for type conversions (e.g., str → list, str → dict).
        requires: Name of another field that must be truthy for this field to apply.
                 Enables conditional dependencies (e.g., coverage_source requires coverage_enabled).
    """

    pytest_options: tuple[str, ...]
    cli_flags: tuple[str, ...]
    apply_when: Literal["always", "if_truthy", "if_not_none"] = "if_not_none"
    transform: Callable[[Any], Any] | None = None
    requires: str | None = None


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
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("verbose",),
                cli_flags=("-v", "-vv", "-vvv", "--verbose"),
                apply_when="if_truthy",
            )
        },
    )

    # Logging configuration
    log_level: str | None = Field(
        default=None,
        description="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). "
        "Maps to --log-cli-level and --log-file-level.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("log_cli_level", "log_file_level"),
                cli_flags=("--log-level", "--log-cli-level", "--log-file-level"),
            )
        },
    )

    log_cli: bool = Field(
        default=False,
        description="Enable live logging to console. Maps to --log-cli.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("log_cli",),
                cli_flags=("--log-cli",),
                apply_when="if_truthy",
            )
        },
    )

    log_file: str | None = Field(
        default=None,
        description="Path to log file. Maps to --log-file.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("log_file",),
                cli_flags=("--log-file",),
            )
        },
    )

    # Test selection
    markers: str | None = Field(
        default=None,
        description="Marker expression to filter tests. Maps to -m.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("markexpr",),
                cli_flags=("-m", "--markers"),
            )
        },
    )

    # Coverage options (pytest-cov)
    coverage_enabled: bool = Field(
        default=False,
        description="Enable coverage reporting. Maps to --cov.",
    )

    coverage_source: str = Field(
        default=".",
        description="Coverage source path. Used with --cov.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("cov_source",),
                cli_flags=("--cov",),
                transform=lambda x: [x] if x else [],
                requires="coverage_enabled",
            )
        },
    )

    coverage_report: str | None = Field(
        default=None,
        description="Coverage report type (term, term-missing, html, xml). Maps to --cov-report.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("cov_report",),
                cli_flags=("--cov-report",),
                transform=lambda x: {x: None},
            )
        },
    )

    # xdist options (pytest-xdist)
    xdist_numprocesses: int | None = Field(
        default=None,
        ge=1,
        description="Number of parallel processes. Maps to -n.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("numprocesses",),
                cli_flags=("-n", "--numprocesses"),
            )
        },
    )

    xdist_dist: str = Field(
        default="load",
        description="Distribution mode for xdist (load, loadscope, etc). Maps to --dist.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("dist",),
                cli_flags=("--dist",),
            )
        },
    )

    # Reporting: durations
    durations: int | None = Field(
        default=None,
        ge=0,
        description="Show N slowest setup/test durations (N=0 for all). Maps to --durations.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("durations",),
                cli_flags=("--durations",),
            )
        },
    )

    durations_min: float | None = Field(
        default=None,
        ge=0.0,
        description="Minimal duration in seconds for inclusion in slowest list. Maps to --durations-min.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("durations_min",),
                cli_flags=("--durations-min",),
            )
        },
    )

    # Reporting: summary options
    no_header: bool = Field(
        default=False,
        description="Disable header. Maps to --no-header.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("no_header",),
                cli_flags=("--no-header",),
                apply_when="if_truthy",
            )
        },
    )

    no_summary: bool = Field(
        default=False,
        description="Disable summary. Maps to --no-summary.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("no_summary",),
                cli_flags=("--no-summary",),
                apply_when="if_truthy",
            )
        },
    )

    no_fold_skipped: bool = Field(
        default=False,
        description="Do not fold skipped tests in short summary. Maps to --no-fold-skipped.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("no_fold_skipped",),
                cli_flags=("--no-fold-skipped",),
                apply_when="if_truthy",
            )
        },
    )

    force_short_summary: bool = Field(
        default=False,
        description="Force condensed summary output regardless of verbosity level. Maps to --force-short-summary.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("force_short_summary",),
                cli_flags=("--force-short-summary",),
                apply_when="if_truthy",
            )
        },
    )

    # Reporting: test summary info
    reportchars: str | None = Field(
        default=None,
        description="Show extra test summary info as specified by chars. Maps to -r.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("reportchars",),
                cli_flags=("-r",),
            )
        },
    )

    disable_warnings: bool = Field(
        default=False,
        description="Disable warnings summary. Maps to --disable-warnings.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("disable_warnings",),
                cli_flags=("--disable-warnings", "--disable-pytest-warnings"),
                apply_when="if_truthy",
            )
        },
    )

    # Reporting: traceback options
    showlocals: bool = Field(
        default=False,
        description="Show locals in tracebacks. Maps to --showlocals.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("showlocals",),
                cli_flags=("-l", "--showlocals", "--no-showlocals"),
                apply_when="if_truthy",
            )
        },
    )

    tbstyle: str | None = Field(
        default=None,
        description="Traceback print mode (auto/long/short/line/native/no). Maps to --tb.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("tbstyle",),
                cli_flags=("--tb",),
            )
        },
    )

    show_capture: str | None = Field(
        default=None,
        description="Controls how captured stdout/stderr/log is shown on failed tests. Maps to --show-capture.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("showcapture",),
                cli_flags=("--show-capture",),
            )
        },
    )

    full_trace: bool = Field(
        default=False,
        description="Don't cut any tracebacks (default is to cut). Maps to --full-trace.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("fulltrace",),
                cli_flags=("--full-trace",),
                apply_when="if_truthy",
            )
        },
    )

    # Reporting: output options
    color: str | None = Field(
        default=None,
        description="Color terminal output (yes/no/auto). Maps to --color.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("color",),
                cli_flags=("--color",),
            )
        },
    )

    code_highlight: str | None = Field(
        default=None,
        description="Whether code should be highlighted (yes/no). Maps to --code-highlight.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("code_highlight",),
                cli_flags=("--code-highlight",),
            )
        },
    )

    pastebin: str | None = Field(
        default=None,
        description="Send failed|all info to bpaste.net pastebin service. Maps to --pastebin.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("pastebin",),
                cli_flags=("--pastebin",),
            )
        },
    )

    # Reporting: junit-xml
    junit_xml: str | None = Field(
        default=None,
        description="Create junit-xml style report file at given path. Maps to --junitxml.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("xmlpath",),
                cli_flags=("--junitxml", "--junit-xml"),
            )
        },
    )

    junit_prefix: str | None = Field(
        default=None,
        description="Prepend prefix to classnames in junit-xml output. Maps to --junitprefix.",
        json_schema_extra={
            "pytest_mapping": PytestFieldMapping(
                pytest_options=("junitprefix",),
                cli_flags=("--junitprefix", "--junit-prefix"),
            )
        },
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

    def apply_to_pytest(self, config: Any) -> None:  # noqa: C901 # complexity is acceptable
        """
        Apply settings to pytest config object using field metadata.

        This method uses a metadata-driven approach to apply settings. Each field
        with a "pytest_mapping" in its json_schema_extra will be automatically
        applied to the pytest config based on its mapping configuration.

        Standard pytest CLI options take precedence over .env settings.
        This method is called during pytest_configure hook.
        Override this in subclasses to customize behavior or add additional logic.

        Args:
            config: Pytest config object
        """
        from pytest_configurex.cli_detection import has_cli_option

        # Store reference to settings in config for fixture access
        config._configurex_settings = self

        # Iterate through all fields and apply based on metadata
        for field_name, field_info in self.model_fields.items():
            # Extract mapping metadata
            mapping: PytestFieldMapping | None = None
            if field_info.json_schema_extra:
                mapping = field_info.json_schema_extra.get("pytest_mapping")

            if not mapping:
                continue

            # 1. Check CLI priority - skip if CLI option was provided
            if mapping.cli_flags and has_cli_option(config, *mapping.cli_flags):
                continue

            # 2. Check requirements - skip if required field is not truthy
            if mapping.requires:
                required_value = getattr(self, mapping.requires, None)
                if not required_value:
                    continue

            # 3. Get field value and check apply condition
            value = getattr(self, field_name)
            if mapping.apply_when == "if_truthy" and not value:
                continue
            if mapping.apply_when == "if_not_none" and value is None:
                continue

            # 4. Transform value if transformer is provided
            if mapping.transform:
                value = mapping.transform(value)

            # 5. Apply to all target pytest options
            for pytest_option in mapping.pytest_options:
                if hasattr(config.option, pytest_option):
                    # Special handling for coverage_source: only set if target is empty
                    # This preserves the original behavior of checking "if not config.option.cov_source"
                    if pytest_option == "cov_source":
                        current = getattr(config.option, pytest_option)
                        if current:
                            continue

                    setattr(config.option, pytest_option, value)

    def __repr__(self) -> str:
        """String representation showing key settings."""
        return (
            f"PytestSettings(verbosity={self.verbosity}, "
            f"log_level={self.log_level!r}, "
            f"markers={self.markers!r})"
        )
