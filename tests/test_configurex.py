"""Tests for pytest-configurex plugin."""

import pytest


def test_configurex_fixture_exists(pytester):
    """Verify that the configurex fixture is available."""
    pytester.makepyfile(
        """
        def test_fixture(configurex):
            assert isinstance(configurex, dict)
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_fixture PASSED*"])
    assert result.ret == 0


def test_env_file_loading(pytester):
    """Test that .env file values are loaded into configurex."""
    # Create a .env file
    pytester.path.joinpath(".env").write_text(
        "LOG_LEVEL=DEBUG\nTIMEOUT=30\n",
        encoding="utf-8",
    )

    pytester.makepyfile(
        """
        def test_env_values(configurex):
            assert configurex.get("log_level") == "DEBUG"
            assert configurex.get("timeout") == 30
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_env_values PASSED*"])
    assert result.ret == 0


def test_cli_overrides_env(pytester):
    """Test that CLI arguments override .env values."""
    # Create a .env file
    pytester.path.joinpath(".env").write_text(
        "LOG_LEVEL=INFO\n",
        encoding="utf-8",
    )

    pytester.makepyfile(
        """
        def test_cli_override(configurex):
            # CLI should override env
            assert configurex.get("log_level") == "DEBUG"
        """
    )

    result = pytester.runpytest("--log-level=DEBUG", "-v")
    result.stdout.fnmatch_lines(["*::test_cli_override PASSED*"])
    assert result.ret == 0


def test_ini_configuration(pytester):
    """Test that pytest.ini values are loaded."""
    pytester.makeini(
        """
        [pytest]
        log_level = WARNING
        timeout = 60
        """
    )

    pytester.makepyfile(
        """
        def test_ini_values(configurex):
            assert configurex.get("log_level") == "WARNING"
            assert configurex.get("timeout") == "60"
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_ini_values PASSED*"])
    assert result.ret == 0


def test_precedence_cli_over_env_over_ini(pytester):
    """Test the full precedence chain: CLI > env > ini."""
    # Set up all three sources
    pytester.makeini(
        """
        [pytest]
        log_level = ERROR
        """
    )

    pytester.path.joinpath(".env").write_text(
        "LOG_LEVEL=WARNING\n",
        encoding="utf-8",
    )

    pytester.makepyfile(
        """
        def test_cli_wins(configurex):
            # CLI should win
            assert configurex.get("log_level") == "DEBUG"
        """
    )

    result = pytester.runpytest("--log-level=DEBUG", "-v")
    result.stdout.fnmatch_lines(["*::test_cli_wins PASSED*"])
    assert result.ret == 0


def test_precedence_env_over_ini(pytester):
    """Test that env overrides ini when no CLI arg is given."""
    pytester.makeini(
        """
        [pytest]
        log_level = ERROR
        """
    )

    pytester.path.joinpath(".env").write_text(
        "LOG_LEVEL=WARNING\n",
        encoding="utf-8",
    )

    pytester.makepyfile(
        """
        def test_env_wins(configurex):
            # Env should override ini
            assert configurex.get("log_level") == "WARNING"
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_env_wins PASSED*"])
    assert result.ret == 0


def test_extra_env_fields(pytester):
    """Test that extra fields from .env are included."""
    pytester.path.joinpath(".env").write_text(
        "CUSTOM_FIELD=custom_value\nANOTHER_FIELD=123\n",
        encoding="utf-8",
    )

    pytester.makepyfile(
        """
        def test_extra_fields(configurex):
            assert configurex.get("custom_field") == "custom_value"
            assert configurex.get("another_field") == "123"
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_extra_fields PASSED*"])
    assert result.ret == 0


def test_help_message(pytester):
    """Test that configurex options appear in help."""
    result = pytester.runpytest("--help")

    result.stdout.fnmatch_lines([
        "*configurex*",
        "*--log-level*",
        "*--timeout*",
        "*--addopts*",
    ])
    assert result.ret == 0


def test_plugin_registration(pytester):
    """Test that external plugins can register their own mappings."""
    # Create a conftest that registers a custom mapping
    pytester.makeconftest(
        """
        def pytest_configurex_register(registry):
            registry.register("custom_option", "--custom", ini_key="custom")
        """
    )

    pytester.makeini(
        """
        [pytest]
        custom = ini_value
        """
    )

    pytester.makepyfile(
        """
        def test_custom_option(configurex):
            assert configurex.get("custom_option") == "ini_value"
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_custom_option PASSED*"])
    assert result.ret == 0


def test_plugin_registration_with_env(pytester):
    """Test external plugin registration with .env file."""
    pytester.makeconftest(
        """
        def pytest_configurex_register(registry):
            registry.register("coverage_source", "--cov", ini_key="cov")
        """
    )

    pytester.path.joinpath(".env").write_text(
        "COVERAGE_SOURCE=src\n",
        encoding="utf-8",
    )

    pytester.makepyfile(
        """
        def test_coverage_from_env(configurex):
            assert configurex.get("coverage_source") == "src"
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_coverage_from_env PASSED*"])
    assert result.ret == 0


def test_no_env_file(pytester):
    """Test that plugin works without .env file."""
    pytester.makepyfile(
        """
        def test_no_env(configurex):
            # Should still work, just empty or with ini/cli values
            assert isinstance(configurex, dict)
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_no_env PASSED*"])
    assert result.ret == 0


def test_empty_env_file(pytester):
    """Test that plugin handles empty .env file."""
    pytester.path.joinpath(".env").write_text("", encoding="utf-8")

    pytester.makepyfile(
        """
        def test_empty_env(configurex):
            assert isinstance(configurex, dict)
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_empty_env PASSED*"])
    assert result.ret == 0


def test_case_insensitive_env_vars(pytester):
    """Test that environment variables are case-insensitive."""
    pytester.path.joinpath(".env").write_text(
        "log_level=DEBUG\nLOG_LEVEL=INFO\n",
        encoding="utf-8",
    )

    pytester.makepyfile(
        """
        def test_case_insensitive(configurex):
            # Should handle case-insensitive env vars
            log_level = configurex.get("log_level")
            assert log_level in ["DEBUG", "INFO"]
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_case_insensitive PASSED*"])
    assert result.ret == 0


def test_dump_config_method(pytester):
    """Test ConfigurexSettings.dump_config method."""
    pytester.makepyfile(
        """
        from pytest_configurex.models import ConfigurexSettings

        def test_dump_config():
            settings = ConfigurexSettings(log_level="DEBUG", timeout=30)

            # Test normal dump
            config = settings.dump_config()
            assert config["log_level"] == "DEBUG"
            assert config["timeout"] == 30

            # Test CLI format
            cli_config = settings.dump_config(as_cli=True)
            assert cli_config["log-level"] == "DEBUG"
            assert cli_config["timeout"] == "30"

            # Test exclude none
            settings_with_none = ConfigurexSettings(log_level="DEBUG")
            config_no_none = settings_with_none.dump_config(include_none=False)
            assert "timeout" not in config_no_none or config_no_none["timeout"] is None
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_dump_config PASSED*"])
    assert result.ret == 0


def test_registry_methods(pytester):
    """Test ConfigurexRegistry methods."""
    pytester.makepyfile(
        """
        from pytest_configurex.registry import ConfigurexRegistry

        def test_registry():
            registry = ConfigurexRegistry()

            # Test register and resolve
            registry.register("test_field", "--test", ini_key="test_ini")
            resolved = registry.resolve("test_field")
            assert resolved["cli"] == "--test"
            assert resolved["ini"] == "test_ini"

            # Test get_all_cli_flags
            flags = registry.get_all_cli_flags()
            assert "--test" in flags

            # Test get_field_for_cli
            field = registry.get_field_for_cli("--test")
            assert field == "test_field"

            # Test items
            items = list(registry.items())
            assert len(items) >= 1
        """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_registry PASSED*"])
    assert result.ret == 0
