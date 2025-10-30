"""Tests for pytest-configurex plugin."""

import textwrap


def test_help_message(pytester):
    """Test that configurex options appear in help."""
    result = pytester.runpytest("--help")
    result.stdout.fnmatch_lines(
        [
            "*configurex*",
            "*--configurex-verbosity*",
            "*--configurex-log-level*",
            "*--configurex-markers*",
        ]
    )


def test_configurex_fixture_available(pytester):
    """Test that the configurex fixture is automatically available."""
    pytester.makepyfile(
        """
        def test_configurex_fixture(configurex):
            assert configurex is not None
            assert hasattr(configurex, 'verbosity')
            assert hasattr(configurex, 'log_level')
            assert hasattr(configurex, 'markers')
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_configurex_fixture PASSED*"])
    assert result.ret == 0


def test_env_pytest_file_loading(pytester):
    """Test loading settings from .env.pytest file."""
    # Create .env.pytest file
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=2
        X_LOG_LEVEL=INFO
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_env_loaded(configurex):
            assert configurex.verbosity == 2
            assert configurex.log_level == "INFO"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_env_loaded PASSED*"])
    assert result.ret == 0


def test_env_fallback(pytester):
    """Test fallback to .env when .env.pytest doesn't exist."""
    # Create only .env file (not .env.pytest)
    env_file = pytester.path / ".env"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=1
        X_LOG_LEVEL=DEBUG
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_env_fallback(configurex):
            assert configurex.verbosity == 1
            assert configurex.log_level == "DEBUG"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_env_fallback PASSED*"])
    assert result.ret == 0


def test_cli_overrides_env(pytester):
    """Test that CLI options override .env.pytest settings."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=1
        X_LOG_LEVEL=DEBUG
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_cli_override(configurex):
            assert configurex.verbosity == 3
            assert configurex.log_level == "ERROR"
    """
    )

    result = pytester.runpytest("--configurex-verbosity=3", "--configurex-log-level=ERROR", "-v")
    result.stdout.fnmatch_lines(["*::test_cli_override PASSED*"])
    assert result.ret == 0


def test_default_values(pytester):
    """Test default values when no .env file exists."""
    pytester.makepyfile(
        """
        def test_defaults(configurex):
            assert configurex.verbosity == 0
            assert configurex.log_level is None
            assert configurex.markers is None
            assert configurex.log_cli is False
            assert configurex.coverage_enabled is False
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_defaults PASSED*"])
    assert result.ret == 0


def test_custom_settings_class_discovery(pytester):
    """Test auto-discovery of custom PytestSettings class in conftest.py."""
    # Create conftest.py with custom settings class
    pytester.makeconftest(
        """
        from pytest_configurex import PytestSettings

        class CustomSettings(PytestSettings):
            custom_field: str = "custom_value"

            def apply_to_pytest(self, config):
                super().apply_to_pytest(config)
                # Custom logic can go here
    """
    )

    pytester.makepyfile(
        """
        def test_custom_settings(configurex):
            assert hasattr(configurex, 'custom_field')
            assert configurex.custom_field == "custom_value"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_custom_settings PASSED*"])
    assert result.ret == 0


def test_custom_settings_with_env(pytester):
    """Test custom settings class with .env.pytest file."""
    pytester.makeconftest(
        """
        from pytest_configurex import PytestSettings

        class CustomSettings(PytestSettings):
            custom_field: str = "default"
    """
    )

    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
X_VERBOSITY=2
        X_CUSTOM_FIELD=from_env
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_custom_with_env(configurex):
            assert configurex.verbosity == 2
            assert configurex.custom_field == "from_env"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_custom_with_env PASSED*"])
    assert result.ret == 0


def test_verbosity_mapping(pytester):
    """Test that verbosity setting maps to pytest verbosity."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
X_VERBOSITY=2
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_verbose(configurex, request):
            # Check that verbosity was applied
            assert request.config.option.verbose == 2
    """
    )

    result = pytester.runpytest()
    assert result.ret == 0


def test_markers_mapping(pytester):
    """Test that markers setting maps to pytest marker expression."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
X_MARKERS=slow
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.slow
        def test_slow(configurex):
            assert configurex.markers == "slow"

        def test_fast(configurex):
            assert False, "Should not run"
    """
    )

    result = pytester.runpytest("-v")
    # Only slow test should run
    result.stdout.fnmatch_lines(["*::test_slow PASSED*"])
    assert "test_fast" not in result.stdout.str()
    assert result.ret == 0


def test_log_level_mapping(pytester):
    """Test that log_level setting is applied."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
X_LOG_LEVEL=INFO
        X_LOG_CLI=true
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        import logging

        def test_logging(configurex):
            assert configurex.log_level == "INFO"
            assert configurex.log_cli is True
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_logging PASSED*"])
    assert result.ret == 0


def test_coverage_settings(pytester):
    """Test coverage-related settings."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
X_COVERAGE_ENABLED=true
        X_COVERAGE_SOURCE=src
        X_COVERAGE_REPORT=term
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_coverage_settings(configurex):
            assert configurex.coverage_enabled is True
            assert configurex.coverage_source == "src"
            assert configurex.coverage_report == "term"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_coverage_settings PASSED*"])
    assert result.ret == 0


def test_xdist_settings(pytester):
    """Test xdist-related settings."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
X_XDIST_NUMPROCESSES=4
        X_XDIST_DIST=loadscope
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_xdist_settings(configurex):
            assert configurex.xdist_numprocesses == 4
            assert configurex.xdist_dist == "loadscope"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_xdist_settings PASSED*"])
    assert result.ret == 0


def test_get_cli_args(pytester):
    """Test the get_cli_args method."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=2
        X_LOG_LEVEL=INFO
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_get_cli_args(configurex):
            args = configurex.get_cli_args()
            assert "-vv" in args
            assert "--log-cli-level=INFO" in args
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_get_cli_args PASSED*"])
    assert result.ret == 0


def test_multiple_cli_options(pytester):
    """Test multiple CLI options together."""
    pytester.makepyfile(
        """
        def test_multiple_cli(configurex):
            assert configurex.verbosity == 3
            assert configurex.log_level == "DEBUG"
            assert configurex.log_cli is True
            assert configurex.coverage_enabled is True
    """
    )

    result = pytester.runpytest(
        "--configurex-verbosity=3",
        "--configurex-log-level=DEBUG",
        "--configurex-log-cli",
        "--configurex-coverage",
        "-v",
    )
    result.stdout.fnmatch_lines(["*::test_multiple_cli PASSED*"])
    assert result.ret == 0


def test_env_prefix_case_insensitive(pytester):
    """Test that environment variable prefix is case insensitive."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
x_verbosity=1
        X_LOG_LEVEL=warning
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_case_insensitive(configurex):
            assert configurex.verbosity == 1
            assert configurex.log_level.upper() == "WARNING"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_case_insensitive PASSED*"])
    assert result.ret == 0


def test_repr_method(pytester):
    """Test the __repr__ method of PytestSettings."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
X_VERBOSITY=2
        X_LOG_LEVEL=INFO
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_repr(configurex):
            repr_str = repr(configurex)
            assert "PytestSettings" in repr_str
            assert "verbosity=2" in repr_str
            assert "log_level='INFO'" in repr_str or 'log_level="INFO"' in repr_str
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_repr PASSED*"])
    assert result.ret == 0


def test_priority_system_complete(pytester):
    """Test complete priority system: CLI > env > defaults."""
    # Set env value
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=1
        X_LOG_LEVEL=INFO
        X_LOG_CLI=true
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_priority(configurex):
            # CLI overrides env for verbosity
            assert configurex.verbosity == 3
            # Env value for log_level (no CLI override)
            assert configurex.log_level == "INFO"
            # Env value for log_cli (no CLI override)
            assert configurex.log_cli is True
            # Default for markers (no env or CLI)
            assert configurex.markers is None
    """
    )

    result = pytester.runpytest("--configurex-verbosity=3", "-v")
    result.stdout.fnmatch_lines(["*::test_priority PASSED*"])
    assert result.ret == 0


def test_log_file_setting(pytester):
    """Test log_file setting."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_LOG_FILE=test.log
        X_LOG_LEVEL=INFO
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_log_file(configurex):
            assert configurex.log_file == "test.log"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_log_file PASSED*"])
    assert result.ret == 0


def test_get_cli_args_comprehensive(pytester):
    """Test get_cli_args with all options."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=3
        X_LOG_LEVEL=DEBUG
        X_LOG_CLI=true
        X_LOG_FILE=pytest.log
        X_MARKERS=not slow
        X_COVERAGE_ENABLED=true
        X_COVERAGE_SOURCE=src
        X_COVERAGE_REPORT=term-missing
        X_XDIST_NUMPROCESSES=4
        X_XDIST_DIST=loadscope
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_get_cli_args_all(configurex):
            args = configurex.get_cli_args()
            assert "-vvv" in args
            assert "--log-cli-level=DEBUG" in args
            assert "--log-file-level=DEBUG" in args
            assert "--log-cli" in args
            assert "--log-file=pytest.log" in args
            assert "-m=not slow" in args
            assert "--cov=src" in args
            assert "--cov-report=term-missing" in args
            assert "-n=4" in args
            assert "--dist=loadscope" in args
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_get_cli_args_all PASSED*"])
    assert result.ret == 0


def test_get_cli_args_minimal(pytester):
    """Test get_cli_args with minimal/default settings."""
    pytester.makepyfile(
        """
        def test_get_cli_args_minimal(configurex):
            args = configurex.get_cli_args()
            # With default settings, most args should not be present
            assert "-v" not in args
            # xdist_dist defaults to "load", which should not add --dist arg
            assert all("--dist=" not in arg for arg in args)
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_get_cli_args_minimal PASSED*"])
    assert result.ret == 0


def test_xdist_dist_default(pytester):
    """Test that default xdist_dist value doesn't generate CLI arg."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_XDIST_NUMPROCESSES=2
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_xdist_default_dist(configurex):
            args = configurex.get_cli_args()
            # Should have -n but not --dist when dist is default "load"
            assert "-n=2" in args
            assert configurex.xdist_dist == "load"
            # --dist=load should not be in args (it's the default)
            assert all("--dist=" not in arg for arg in args)
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_xdist_default_dist PASSED*"])
    assert result.ret == 0


def test_cli_markers_option(pytester):
    """Test --configurex-markers CLI option."""
    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.unit
        def test_unit(configurex):
            assert configurex.markers == "unit"

        @pytest.mark.integration
        def test_integration(configurex):
            assert False, "Should not run"
    """
    )

    result = pytester.runpytest("--configurex-markers=unit", "-v")
    result.stdout.fnmatch_lines(["*::test_unit PASSED*"])
    assert "test_integration" not in result.stdout.str()
    assert result.ret == 0


def test_cli_log_file_option(pytester):
    """Test --configurex-log-file CLI option."""
    pytester.makepyfile(
        """
        def test_log_file_cli(configurex):
            assert configurex.log_file == "custom.log"
    """
    )

    result = pytester.runpytest("--configurex-log-file=custom.log", "-v")
    result.stdout.fnmatch_lines(["*::test_log_file_cli PASSED*"])
    assert result.ret == 0


def test_cli_coverage_report_option(pytester):
    """Test --configurex-coverage-report CLI option."""
    pytester.makepyfile(
        """
        def test_coverage_report_cli(configurex):
            assert configurex.coverage_report == "html"
    """
    )

    result = pytester.runpytest("--configurex-coverage-report=html", "-v")
    result.stdout.fnmatch_lines(["*::test_coverage_report_cli PASSED*"])
    assert result.ret == 0


def test_settings_repr_string(pytester):
    """Test that repr returns a valid string representation."""
    pytester.makepyfile(
        """
        def test_repr_string(configurex):
            repr_str = repr(configurex)
            # Should be a string
            assert isinstance(repr_str, str)
            # Should contain class name
            assert "Settings" in repr_str
            # Should contain key attributes
            assert "verbosity" in repr_str
            assert "log_level" in repr_str
            assert "markers" in repr_str
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_repr_string PASSED*"])
    assert result.ret == 0


def test_all_settings_fields_accessible(pytester):
    """Test that all settings fields are accessible from fixture."""
    pytester.makepyfile(
        """
        def test_all_fields(configurex):
            # Verify all expected fields exist
            assert hasattr(configurex, 'verbosity')
            assert hasattr(configurex, 'log_level')
            assert hasattr(configurex, 'log_cli')
            assert hasattr(configurex, 'log_file')
            assert hasattr(configurex, 'markers')
            assert hasattr(configurex, 'coverage_enabled')
            assert hasattr(configurex, 'coverage_source')
            assert hasattr(configurex, 'coverage_report')
            assert hasattr(configurex, 'xdist_numprocesses')
            assert hasattr(configurex, 'xdist_dist')

            # Verify methods exist
            assert hasattr(configurex, 'get_cli_args')
            assert hasattr(configurex, 'apply_to_pytest')
            assert callable(configurex.get_cli_args)
            assert callable(configurex.apply_to_pytest)
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_all_fields PASSED*"])
    assert result.ret == 0


def test_coverage_source_default(pytester):
    """Test coverage_source default value."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_COVERAGE_ENABLED=true
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_coverage_default(configurex):
            # coverage_source should default to "."
            assert configurex.coverage_enabled is True
            assert configurex.coverage_source == "."
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_coverage_default PASSED*"])
    assert result.ret == 0
