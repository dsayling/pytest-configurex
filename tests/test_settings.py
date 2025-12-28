"""Tests for settings module."""

import textwrap
from unittest.mock import Mock

from pytest_configurex.settings import PytestSettings


class TestLoadSettings:
    """Tests for load_settings classmethod."""

    def test_load_from_env_pytest_file(self, tmp_path):
        """Test loading settings from .env.pytest file."""
        env_file = tmp_path / ".env.pytest"
        env_file.write_text(
            textwrap.dedent(
                """
                X_VERBOSITY=2
                X_LOG_LEVEL=INFO
                X_MARKERS=slow
                """
            ).strip()
        )

        settings = PytestSettings.load_settings(config_root=tmp_path)

        assert settings.verbosity == 2
        assert settings.log_level == "INFO"
        assert settings.markers == "slow"

    def test_fallback_to_env_file(self, tmp_path):
        """Test fallback to .env when .env.pytest doesn't exist."""
        env_file = tmp_path / ".env"
        env_file.write_text(
            textwrap.dedent(
                """
                X_VERBOSITY=1
                X_LOG_LEVEL=DEBUG
                """
            ).strip()
        )

        settings = PytestSettings.load_settings(config_root=tmp_path)

        assert settings.verbosity == 1
        assert settings.log_level == "DEBUG"

    def test_env_pytest_takes_precedence_over_env(self, tmp_path):
        """Test that .env.pytest takes precedence over .env."""
        env_pytest = tmp_path / ".env.pytest"
        env_pytest.write_text("X_VERBOSITY=3")

        env_default = tmp_path / ".env"
        env_default.write_text("X_VERBOSITY=1")

        settings = PytestSettings.load_settings(config_root=tmp_path)

        assert settings.verbosity == 3

    def test_environment_variables_take_precedence(self, tmp_path, monkeypatch):
        """Test that environment variables override .env files."""
        env_file = tmp_path / ".env.pytest"
        env_file.write_text("X_VERBOSITY=1")

        monkeypatch.setenv("X_VERBOSITY", "3")

        settings = PytestSettings.load_settings(config_root=tmp_path)

        assert settings.verbosity == 3

    def test_default_values_when_no_env_file(self, tmp_path):
        """Test default values are used when no env file exists."""
        settings = PytestSettings.load_settings(config_root=tmp_path)

        assert settings.verbosity == 0
        assert settings.log_level is None
        assert settings.markers is None
        assert settings.log_cli is False
        assert settings.coverage_enabled is False

    def test_case_insensitive_env_vars(self, tmp_path):
        """Test that environment variables are case insensitive."""
        env_file = tmp_path / ".env.pytest"
        env_file.write_text(
            textwrap.dedent(
                """
                x_verbosity=2
                X_LOG_LEVEL=warning
                """
            ).strip()
        )

        settings = PytestSettings.load_settings(config_root=tmp_path)

        assert settings.verbosity == 2
        assert settings.log_level.upper() == "WARNING"

    def test_all_defined_fields_loaded(self, tmp_path):
        """Test that all defined fields are loaded from .env.pytest."""
        env_file = tmp_path / ".env.pytest"
        env_file.write_text(
            textwrap.dedent(
                """
                X_VERBOSITY=2
                X_LOG_LEVEL=INFO
                X_LOG_CLI=true
                X_LOG_FILE=test.log
                X_MARKERS=slow
                X_COVERAGE_ENABLED=true
                X_COVERAGE_SOURCE=src
                X_COVERAGE_REPORT=html
                X_XDIST_NUMPROCESSES=4
                X_XDIST_DIST=loadscope
                """
            ).strip()
        )

        settings = PytestSettings.load_settings(config_root=tmp_path)

        assert settings.verbosity == 2
        assert settings.log_level == "INFO"
        assert settings.log_cli is True
        assert settings.log_file == "test.log"
        assert settings.markers == "slow"
        assert settings.coverage_enabled is True
        assert settings.coverage_source == "src"
        assert settings.coverage_report == "html"
        assert settings.xdist_numprocesses == 4
        assert settings.xdist_dist == "loadscope"

    def test_load_settings_with_no_config_root(self, monkeypatch):
        """Test loading settings defaults to current working directory."""
        # This test just ensures it doesn't crash when config_root is None
        settings = PytestSettings.load_settings()
        assert isinstance(settings, PytestSettings)


class TestApplyVerbosity:
    """Tests for _apply_verbosity method."""

    def test_apply_verbosity_when_not_set_in_cli(self):
        """Test verbosity is applied when not set via CLI."""
        settings = PytestSettings(verbosity=2)
        config = Mock()
        config.option.verbose = 0
        config.invocation_params.args = []

        settings._apply_verbosity(config)

        assert config.option.verbose == 2

    def test_skip_verbosity_when_set_in_cli(self):
        """Test verbosity is not applied when set via CLI."""
        settings = PytestSettings(verbosity=2)
        config = Mock()
        config.option.verbose = 3
        config.invocation_params.args = ["-vvv"]

        settings._apply_verbosity(config)

        # Should remain unchanged
        assert config.option.verbose == 3

    def test_skip_verbosity_when_zero(self):
        """Test verbosity is not applied when it's zero."""
        settings = PytestSettings(verbosity=0)
        config = Mock()
        config.option.verbose = 0
        config.invocation_params.args = []

        settings._apply_verbosity(config)

        assert config.option.verbose == 0


class TestApplyLoggingSettings:
    """Tests for _apply_logging_settings method."""

    def test_apply_log_level(self):
        """Test log level is applied when not set via CLI."""
        settings = PytestSettings(log_level="INFO")
        config = Mock()
        config.option.log_cli_level = None
        config.option.log_file_level = None
        config.invocation_params.args = []

        settings._apply_logging_settings(config)

        assert config.option.log_cli_level == "INFO"
        assert config.option.log_file_level == "INFO"

    def test_apply_log_cli(self):
        """Test log_cli is applied when not set via CLI."""
        settings = PytestSettings(log_cli=True)
        config = Mock()
        config.option.log_cli = False
        config.invocation_params.args = []

        settings._apply_logging_settings(config)

        assert config.option.log_cli is True

    def test_apply_log_file(self):
        """Test log_file is applied when not set via CLI."""
        settings = PytestSettings(log_file="test.log")
        config = Mock()
        config.option.log_file = None
        config.invocation_params.args = []

        settings._apply_logging_settings(config)

        assert config.option.log_file == "test.log"

    def test_skip_log_level_when_cli_set(self):
        """Test log level is not applied when set via CLI."""
        settings = PytestSettings(log_level="INFO")
        config = Mock()
        config.option.log_cli_level = "DEBUG"
        config.invocation_params.args = ["--log-cli-level=DEBUG"]

        settings._apply_logging_settings(config)

        assert config.option.log_cli_level == "DEBUG"


class TestApplyMarkerSettings:
    """Tests for _apply_marker_settings method."""

    def test_apply_markers(self):
        """Test markers are applied when not set via CLI."""
        settings = PytestSettings(markers="slow")
        config = Mock()
        config.option.markexpr = None
        config.invocation_params.args = []

        settings._apply_marker_settings(config)

        assert config.option.markexpr == "slow"

    def test_skip_markers_when_cli_set(self):
        """Test markers are not applied when set via CLI."""
        settings = PytestSettings(markers="slow")
        config = Mock()
        config.option.markexpr = "fast"
        config.invocation_params.args = ["-m", "fast"]

        settings._apply_marker_settings(config)

        assert config.option.markexpr == "fast"


class TestApplyCoverageSettings:
    """Tests for _apply_coverage_settings method."""

    def test_apply_coverage_enabled(self):
        """Test coverage is applied when not set via CLI."""
        settings = PytestSettings(coverage_enabled=True, coverage_source="src")
        config = Mock()
        config.option.cov_source = []
        config.invocation_params.args = []

        settings._apply_coverage_settings(config)

        assert config.option.cov_source == ["src"]

    def test_apply_coverage_report(self):
        """Test coverage report is applied when not set via CLI."""
        settings = PytestSettings(coverage_report="html")
        config = Mock()
        config.option.cov_report = {}
        config.invocation_params.args = []

        settings._apply_coverage_settings(config)

        assert config.option.cov_report == {"html": None}

    def test_skip_coverage_when_cli_set(self):
        """Test coverage is not applied when set via CLI."""
        settings = PytestSettings(coverage_enabled=True, coverage_source="src")
        config = Mock()
        config.option.cov_source = ["tests"]
        config.invocation_params.args = ["--cov=tests"]

        settings._apply_coverage_settings(config)

        assert config.option.cov_source == ["tests"]


class TestApplyXdistSettings:
    """Tests for _apply_xdist_settings method."""

    def test_apply_xdist_numprocesses(self):
        """Test xdist numprocesses is applied when not set via CLI."""
        settings = PytestSettings(xdist_numprocesses=4)
        config = Mock()
        config.option.numprocesses = None
        config.invocation_params.args = []

        settings._apply_xdist_settings(config)

        assert config.option.numprocesses == 4

    def test_apply_xdist_dist(self):
        """Test xdist dist mode is applied when not set via CLI."""
        settings = PytestSettings(xdist_dist="loadscope")
        config = Mock()
        config.option.dist = "load"
        config.invocation_params.args = []

        settings._apply_xdist_settings(config)

        assert config.option.dist == "loadscope"

    def test_skip_xdist_when_cli_set(self):
        """Test xdist settings are not applied when set via CLI."""
        settings = PytestSettings(xdist_numprocesses=4)
        config = Mock()
        config.option.numprocesses = 2
        config.invocation_params.args = ["-n", "2"]

        settings._apply_xdist_settings(config)

        assert config.option.numprocesses == 2


class TestApplyToPytest:
    """Tests for apply_to_pytest method."""

    def test_stores_settings_reference(self):
        """Test that settings reference is stored in config."""
        settings = PytestSettings()
        config = Mock()
        config.option.verbose = 0
        config.invocation_params.args = []

        settings.apply_to_pytest(config)

        assert hasattr(config, "_configurex_settings")
        assert config._configurex_settings is settings

    def test_applies_all_settings(self):
        """Test that all settings are applied."""
        settings = PytestSettings(
            verbosity=2,
            log_level="INFO",
            markers="slow",
            coverage_enabled=True,
            xdist_numprocesses=4,
        )
        config = Mock()
        config.option.verbose = 0
        config.option.log_cli_level = None
        config.option.log_file_level = None
        config.option.markexpr = None
        config.option.cov_source = []
        config.option.numprocesses = None
        config.invocation_params.args = []

        settings.apply_to_pytest(config)

        assert config.option.verbose == 2
        assert config.option.log_cli_level == "INFO"
        assert config.option.markexpr == "slow"
        assert config.option.cov_source == ["."]
        assert config.option.numprocesses == 4

    def test_handles_missing_attributes_gracefully(self):
        """Test that missing config attributes don't cause errors."""
        settings = PytestSettings(log_level="INFO", coverage_enabled=True)
        config = Mock()
        config.option.verbose = 0
        config.invocation_params.args = []
        # Remove optional attributes
        delattr(config.option, "log_cli_level")
        delattr(config.option, "cov_source")

        # Should not raise
        settings.apply_to_pytest(config)


class TestPytestSettingsRepr:
    """Tests for __repr__ method."""

    def test_repr_format(self):
        """Test repr returns expected format."""
        settings = PytestSettings(verbosity=2, log_level="INFO", markers="slow")

        repr_str = repr(settings)

        assert "PytestSettings" in repr_str
        assert "verbosity=2" in repr_str
        assert "log_level='INFO'" in repr_str or 'log_level="INFO"' in repr_str
        assert "markers='slow'" in repr_str or 'markers="slow"' in repr_str
