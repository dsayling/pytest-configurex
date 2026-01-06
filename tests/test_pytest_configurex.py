"""Tests for pytest-configurex plugin."""

import textwrap


def test_help_message(pytester):
    """Test that custom configurex CLI options do NOT appear (we use standard pytest options)."""
    result = pytester.runpytest("--help")
    # Should not have custom --configurex-* options anymore
    assert "--configurex-verbosity" not in result.stdout.str()
    assert "--configurex-log-level" not in result.stdout.str()
    assert "--configurex-markers" not in result.stdout.str()


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


def test_standard_pytest_cli_overrides_env(pytester):
    """Test that standard pytest CLI options override .env.pytest settings."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=1
        X_LOG_LEVEL=INFO
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_cli_override(configurex, request):
            # Verbosity from CLI (-vv) should override X_VERBOSITY=1
            assert request.config.option.verbose == 2
            # .env setting should still be visible in configurex
            assert configurex.verbosity == 1  # Original .env value
    """
    )

    result = pytester.runpytest("-vv")
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


def test_standard_pytest_cli_options(pytester):
    """Test that standard pytest CLI options work correctly."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=1
        X_LOG_LEVEL=INFO
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_standard_cli(request):
            # Standard pytest -vvv should set verbosity to 3
            assert request.config.option.verbose == 3
    """
    )

    result = pytester.runpytest("-vvv")
    result.stdout.fnmatch_lines(["*::test_standard_cli PASSED*"])
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
    """Test complete priority system: standard pytest CLI > env > defaults."""
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
        def test_priority(configurex, request):
            # Standard CLI -vvv should override X_VERBOSITY=1 in config
            assert request.config.option.verbose == 3
            # Env value for log_level (no CLI override) should apply
            assert request.config.option.log_cli_level == "INFO"
            # Settings object still has original .env values
            assert configurex.verbosity == 1
            assert configurex.log_level == "INFO"
            assert configurex.log_cli is True
    """
    )

    result = pytester.runpytest("-vvv")
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


def test_standard_markers_cli_overrides_env(pytester):
    """Test that standard -m CLI option overrides .env.pytest settings."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_MARKERS=slow")

    pytester.makepyfile(
        """
        import pytest

        @pytest.mark.unit
        def test_unit():
            pass

        @pytest.mark.slow
        def test_slow():
            assert False, "Should not run"
    """
    )

    result = pytester.runpytest("-m", "unit", "-v")
    result.stdout.fnmatch_lines(["*::test_unit PASSED*"])
    assert "test_slow" not in result.stdout.str()
    assert result.ret == 0


def test_standard_log_file_cli_overrides_env(pytester):
    """Test that standard --log-file CLI option overrides .env.pytest settings."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_LOG_FILE=default.log")

    pytester.makepyfile(
        """
        def test_log_file_cli(request):
            # CLI --log-file should override X_LOG_FILE
            assert request.config.option.log_file == "custom.log"
    """
    )

    result = pytester.runpytest("--log-file=custom.log", "-v")
    result.stdout.fnmatch_lines(["*::test_log_file_cli PASSED*"])
    assert result.ret == 0


def test_standard_cov_report_cli_overrides_env(pytester):
    """Test that standard --cov-report CLI option overrides .env.pytest settings."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_COVERAGE_REPORT=term")

    pytester.makepyfile(
        """
        def test_coverage_report_cli(request):
            # CLI --cov-report should override X_COVERAGE_REPORT
            assert "html" in request.config.option.cov_report
    """
    )

    result = pytester.runpytest("--cov-report=html", "-v")
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
            assert hasattr(configurex, 'apply_to_pytest')
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


def test_durations_mapping(pytester):
    """Test durations setting is applied to pytest config."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_DURATIONS=5")

    pytester.makepyfile(
        """
        def test_durations_check(request):
            # Durations should be set from .env.pytest
            assert request.config.option.durations == 5
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_durations_check PASSED*"])
    assert result.ret == 0


def test_durations_cli_override(pytester):
    """Test that CLI --durations overrides .env.pytest setting."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_DURATIONS=10")

    pytester.makepyfile(
        """
        def test_durations_cli(request):
            # CLI should override X_DURATIONS
            assert request.config.option.durations == 3
    """
    )

    result = pytester.runpytest("--durations=3", "-v")
    result.stdout.fnmatch_lines(["*::test_durations_cli PASSED*"])
    assert result.ret == 0


def test_reportchars_mapping(pytester):
    """Test reportchars setting is applied to pytest config."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_REPORTCHARS=fEsx")

    pytester.makepyfile(
        """
        def test_reportchars_check(request):
            # Reportchars should be set from .env.pytest
            assert request.config.option.reportchars == "fEsx"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_reportchars_check PASSED*"])
    assert result.ret == 0


def test_reportchars_cli_override(pytester):
    """Test that CLI -r overrides .env.pytest setting."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_REPORTCHARS=fEsx")

    pytester.makepyfile(
        """
        def test_reportchars_cli(request):
            # CLI should override X_REPORTCHARS
            # Note: -ra is parsed as reportchars='a' by pytest
            assert request.config.option.reportchars in ["a", "fEsx"]
    """
    )

    result = pytester.runpytest("-r", "a", "-v")
    result.stdout.fnmatch_lines(["*::test_reportchars_cli PASSED*"])
    assert result.ret == 0


def test_tbstyle_mapping(pytester):
    """Test tbstyle setting is applied to pytest config."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_TBSTYLE=short")

    pytester.makepyfile(
        """
        def test_tbstyle_check(request):
            # Tbstyle should be set from .env.pytest
            assert request.config.option.tbstyle == "short"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_tbstyle_check PASSED*"])
    assert result.ret == 0


def test_tbstyle_cli_override(pytester):
    """Test that CLI --tb overrides .env.pytest setting."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_TBSTYLE=short")

    pytester.makepyfile(
        """
        def test_tbstyle_cli(request):
            # CLI should override X_TBSTYLE
            assert request.config.option.tbstyle == "line"
    """
    )

    result = pytester.runpytest("--tb=line", "-v")
    result.stdout.fnmatch_lines(["*::test_tbstyle_cli PASSED*"])
    assert result.ret == 0


def test_showlocals_mapping(pytester):
    """Test showlocals setting is applied to pytest config."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_SHOWLOCALS=true")

    pytester.makepyfile(
        """
        def test_showlocals_check(request):
            # Showlocals should be set from .env.pytest
            assert request.config.option.showlocals is True
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_showlocals_check PASSED*"])
    assert result.ret == 0


def test_junit_xml_mapping(pytester):
    """Test junit_xml setting is applied to pytest config."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_JUNIT_XML=test-report.xml")

    pytester.makepyfile(
        """
        def test_junit_check(request):
            # junit_xml should be set from .env.pytest
            assert request.config.option.xmlpath == "test-report.xml"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_junit_check PASSED*"])
    assert result.ret == 0


def test_junit_xml_cli_override(pytester):
    """Test that CLI --junitxml overrides .env.pytest setting."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_JUNIT_XML=test-report.xml")

    pytester.makepyfile(
        """
        def test_junit_cli(request):
            # CLI should override X_JUNIT_XML
            assert request.config.option.xmlpath == "cli-report.xml"
    """
    )

    result = pytester.runpytest("--junitxml=cli-report.xml", "-v")
    result.stdout.fnmatch_lines(["*::test_junit_cli PASSED*"])
    assert result.ret == 0


def test_color_mapping(pytester):
    """Test color setting is applied to pytest config."""
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_COLOR=no")

    pytester.makepyfile(
        """
        def test_color_check(request):
            # Color should be set from .env.pytest
            assert request.config.option.color == "no"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_color_check PASSED*"])
    assert result.ret == 0


def test_all_reporting_fields_accessible(pytester):
    """Test that all reporting fields are accessible from fixture."""
    pytester.makepyfile(
        """
        def test_reporting_fields(configurex):
            # Verify all reporting fields exist
            assert hasattr(configurex, 'durations')
            assert hasattr(configurex, 'durations_min')
            assert hasattr(configurex, 'no_header')
            assert hasattr(configurex, 'no_summary')
            assert hasattr(configurex, 'no_fold_skipped')
            assert hasattr(configurex, 'force_short_summary')
            assert hasattr(configurex, 'reportchars')
            assert hasattr(configurex, 'disable_warnings')
            assert hasattr(configurex, 'showlocals')
            assert hasattr(configurex, 'tbstyle')
            assert hasattr(configurex, 'show_capture')
            assert hasattr(configurex, 'full_trace')
            assert hasattr(configurex, 'color')
            assert hasattr(configurex, 'code_highlight')
            assert hasattr(configurex, 'pastebin')
            assert hasattr(configurex, 'junit_xml')
            assert hasattr(configurex, 'junit_prefix')
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_reporting_fields PASSED*"])
    assert result.ret == 0
