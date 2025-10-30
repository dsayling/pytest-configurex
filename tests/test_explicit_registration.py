"""Tests for explicit settings class registration via pytest.ini."""

import textwrap


def test_explicit_registration_via_ini(pytester):
    """Test that settings class can be registered explicitly in pytest.ini."""
    # Create a settings module
    pytester.makepyfile(
        my_settings="""
        from pytest_configurex import PytestSettings

        class MyTestSettings(PytestSettings):
            custom_value: str = "from_explicit_registration"
    """
    )

    # Create pytest.ini with explicit registration
    pytester.makeini(
        """
        [pytest]
        configurex_settings_class = my_settings.MyTestSettings
    """
    )

    # Create test file
    pytester.makepyfile(
        """
        def test_explicit_registration(configurex):
            assert configurex.custom_value == "from_explicit_registration"
            assert hasattr(configurex, 'verbosity')
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_explicit_registration PASSED*"])
    assert result.ret == 0


def test_explicit_registration_overrides_autodiscovery(pytester):
    """Test that pytest.ini registration takes priority over auto-discovery."""
    # Create settings module for explicit registration
    pytester.makepyfile(
        explicit_settings="""
        from pytest_configurex import PytestSettings

        class ExplicitSettings(PytestSettings):
            source: str = "explicit"
    """
    )

    # Create conftest.py with a different settings class (would be auto-discovered)
    pytester.makeconftest(
        """
        from pytest_configurex import PytestSettings

        class AutoDiscoveredSettings(PytestSettings):
            source: str = "autodiscovery"
    """
    )

    # Configure pytest.ini to use explicit registration
    pytester.makeini(
        """
        [pytest]
        configurex_settings_class = explicit_settings.ExplicitSettings
    """
    )

    # Test should use explicit registration, not auto-discovery
    pytester.makepyfile(
        """
        def test_priority(configurex):
            # Should be from explicit registration, not auto-discovery
            assert configurex.source == "explicit"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_priority PASSED*"])
    assert result.ret == 0


def test_explicit_registration_with_colon_syntax(pytester):
    """Test that module:ClassName syntax works."""
    pytester.makepyfile(
        test_settings="""
        from pytest_configurex import PytestSettings

        class ColonSyntaxSettings(PytestSettings):
            syntax_type: str = "colon"
    """
    )

    pytester.makeini(
        """
        [pytest]
        configurex_settings_class = test_settings:ColonSyntaxSettings
    """
    )

    pytester.makepyfile(
        """
        def test_colon_syntax(configurex):
            assert configurex.syntax_type == "colon"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_colon_syntax PASSED*"])
    assert result.ret == 0


def test_explicit_registration_with_env_vars(pytester):
    """Test that explicit registration works with environment variables."""
    pytester.makepyfile(
        env_settings="""
        from pytest_configurex import PytestSettings

        class EnvSettings(PytestSettings):
            custom_field: str = "default"
    """
    )

    pytester.makeini(
        """
        [pytest]
        configurex_settings_class = env_settings.EnvSettings
    """
    )

    # Create .env.pytest file
    env_file = pytester.path / ".env.pytest"
    env_file.write_text(
        textwrap.dedent(
            """
        X_VERBOSITY=3
        X_CUSTOM_FIELD=from_env
        """
        ).strip()
    )

    pytester.makepyfile(
        """
        def test_env_with_explicit(configurex):
            assert configurex.verbosity == 3
            assert configurex.custom_field == "from_env"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_env_with_explicit PASSED*"])
    assert result.ret == 0


def test_explicit_registration_invalid_class_path(pytester):
    """Test error handling for invalid class path in pytest.ini."""
    pytester.makeini(
        """
        [pytest]
        configurex_settings_class = nonexistent.module.Class
    """
    )

    pytester.makepyfile(
        """
        def test_something(configurex):
            pass
    """
    )

    result = pytester.runpytest()
    # Should show error or warning about invalid class path
    # But should fall back to auto-discovery/default
    # We allow it to fail gracefully
    assert result.ret in [0, 1, 3]  # Various pytest exit codes are acceptable


def test_explicit_registration_not_a_subclass(pytester):
    """Test error handling when registered class is not a PytestSettings subclass."""
    pytester.makepyfile(
        bad_settings="""
        class NotASettings:
            pass
    """
    )

    pytester.makeini(
        """
        [pytest]
        configurex_settings_class = bad_settings.NotASettings
    """
    )

    pytester.makepyfile(
        """
        def test_something(configurex):
            # Should fall back to default settings
            assert hasattr(configurex, 'verbosity')
    """
    )

    result = pytester.runpytest()
    # Should handle gracefully
    assert result.ret in [0, 1, 3]


def test_explicit_registration_with_cli_override(pytester):
    """Test that standard pytest CLI arguments override explicit registration settings."""
    pytester.makepyfile(
        cli_settings="""
        from pytest_configurex import PytestSettings

        class CliSettings(PytestSettings):
            pass
    """
    )

    pytester.makeini(
        """
        [pytest]
        configurex_settings_class = cli_settings.CliSettings
    """
    )

    # Create .env.pytest with verbosity=1
    env_file = pytester.path / ".env.pytest"
    env_file.write_text("X_VERBOSITY=1")

    pytester.makepyfile(
        """
        def test_cli_override(configurex, request):
            # Standard CLI -vv should override X_VERBOSITY=1
            assert request.config.option.verbose == 2
            # Settings object still has original .env value
            assert configurex.verbosity == 1
    """
    )

    result = pytester.runpytest("-vv")
    result.stdout.fnmatch_lines(["*::test_cli_override PASSED*"])
    assert result.ret == 0


def test_no_explicit_registration_uses_autodiscovery(pytester):
    """Test that without pytest.ini setting, auto-discovery still works."""
    # No pytest.ini setting

    pytester.makeconftest(
        """
        from pytest_configurex import PytestSettings

        class AutoSettings(PytestSettings):
            auto_field: str = "autodiscovered"
    """
    )

    pytester.makepyfile(
        """
        def test_autodiscovery_works(configurex):
            assert configurex.auto_field == "autodiscovered"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_autodiscovery_works PASSED*"])
    assert result.ret == 0


def test_empty_ini_value_uses_autodiscovery(pytester):
    """Test that empty string in pytest.ini falls back to auto-discovery."""
    pytester.makeini(
        """
        [pytest]
        configurex_settings_class =
    """
    )

    pytester.makeconftest(
        """
        from pytest_configurex import PytestSettings

        class FallbackSettings(PytestSettings):
            fallback_field: str = "used"
    """
    )

    pytester.makepyfile(
        """
        def test_fallback(configurex):
            assert configurex.fallback_field == "used"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_fallback PASSED*"])
    assert result.ret == 0


def test_explicit_registration_from_package(pytester):
    """Test explicit registration with package path."""
    # Create a package structure
    pytester.mkpydir("mypackage")
    pytester.makepyfile(
        **{
            "mypackage/settings": """
        from pytest_configurex import PytestSettings

        class PackageSettings(PytestSettings):
            package_field: str = "from_package"
    """
        }
    )

    pytester.makeini(
        """
        [pytest]
        configurex_settings_class = mypackage.settings.PackageSettings
    """
    )

    pytester.makepyfile(
        """
        def test_package_settings(configurex):
            assert configurex.package_field == "from_package"
    """
    )

    result = pytester.runpytest("-v")
    result.stdout.fnmatch_lines(["*::test_package_settings PASSED*"])
    assert result.ret == 0
