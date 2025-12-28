"""Tests for discovery module functions."""

import sys
import textwrap
from pathlib import Path
from unittest.mock import Mock

import pytest

from pytest_configurex.discovery import (
    _autodiscover_from_conftest,
    _find_settings_subclasses,
    _load_conftest_module,
    discover_settings_class,
    get_settings_class_from_ini,
)
from pytest_configurex.settings import PytestSettings


class TestLoadConftestModule:
    """Tests for _load_conftest_module function."""

    def test_load_valid_conftest(self, tmp_path):
        """Test loading a valid conftest.py module."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                test_value = 42

                def test_function():
                    return "test"
                """
            )
        )

        module = _load_conftest_module(conftest_path)
        assert hasattr(module, "test_value")
        assert module.test_value == 42
        assert hasattr(module, "test_function")
        assert callable(module.test_function)

    def test_load_conftest_with_syntax_error(self, tmp_path):
        """Test that syntax errors raise ImportError."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text("invalid python syntax @#$%")

        with pytest.raises(ImportError):
            _load_conftest_module(conftest_path)

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading a non-existent file."""
        conftest_path = tmp_path / "nonexistent.py"

        with pytest.raises(ImportError):
            _load_conftest_module(conftest_path)

    def test_conftest_module_cleanup(self, tmp_path):
        """Test that conftest module is cleaned up from sys.modules."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text("test_var = 'cleanup_test'")

        # Module should be cleaned up after loading
        _load_conftest_module(conftest_path)
        assert "conftest" not in sys.modules

    def test_load_conftest_with_imports(self, tmp_path):
        """Test loading conftest that imports standard libraries."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                import os
                from pathlib import Path

                test_value = Path("test")
                """
            )
        )

        module = _load_conftest_module(conftest_path)
        assert hasattr(module, "test_value")
        assert isinstance(module.test_value, Path)


class TestFindSettingsSubclasses:
    """Tests for _find_settings_subclasses function."""

    def test_find_single_subclass(self, tmp_path):
        """Test finding a single PytestSettings subclass."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class CustomSettings(PytestSettings):
                    custom_field: str = "test"
                """
            )
        )

        module = _load_conftest_module(conftest_path)
        subclasses = _find_settings_subclasses(module)

        assert len(subclasses) == 1
        assert subclasses[0].__name__ == "CustomSettings"
        assert issubclass(subclasses[0], PytestSettings)

    def test_find_multiple_subclasses(self, tmp_path):
        """Test finding multiple PytestSettings subclasses."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class CustomSettings1(PytestSettings):
                    field1: str = "test1"

                class CustomSettings2(PytestSettings):
                    field2: str = "test2"
                """
            )
        )

        module = _load_conftest_module(conftest_path)
        subclasses = _find_settings_subclasses(module)

        assert len(subclasses) == 2
        names = {cls.__name__ for cls in subclasses}
        assert names == {"CustomSettings1", "CustomSettings2"}

    def test_ignore_imported_subclasses(self, tmp_path):
        """Test that imported PytestSettings subclasses are ignored."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                # This should be found (defined here)
                class LocalSettings(PytestSettings):
                    local: str = "local"
                """
            )
        )

        module = _load_conftest_module(conftest_path)
        subclasses = _find_settings_subclasses(module)

        # Should only find LocalSettings, not imported PytestSettings
        assert len(subclasses) == 1
        assert subclasses[0].__name__ == "LocalSettings"

    def test_find_no_subclasses(self, tmp_path):
        """Test finding no PytestSettings subclasses."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                # No PytestSettings subclasses defined
                test_value = 42

                class RegularClass:
                    pass
                """
            )
        )

        module = _load_conftest_module(conftest_path)
        subclasses = _find_settings_subclasses(module)

        assert len(subclasses) == 0

    def test_ignore_base_pytestsettings(self, tmp_path):
        """Test that PytestSettings itself is not included."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings
                """
            )
        )

        module = _load_conftest_module(conftest_path)
        subclasses = _find_settings_subclasses(module)

        # Should not include PytestSettings itself
        assert len(subclasses) == 0


class TestAutodiscoverFromConftest:
    """Tests for _autodiscover_from_conftest function."""

    def test_autodiscover_with_custom_settings(self, tmp_path):
        """Test auto-discovery finds custom settings class."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class CustomSettings(PytestSettings):
                    custom_field: str = "discovered"
                """
            )
        )

        config = Mock()
        config.rootdir = tmp_path

        discovered = _autodiscover_from_conftest(config)
        assert discovered is not None
        assert discovered.__name__ == "CustomSettings"

    def test_autodiscover_no_conftest(self, tmp_path):
        """Test auto-discovery returns None when conftest.py doesn't exist."""
        config = Mock()
        config.rootdir = tmp_path

        discovered = _autodiscover_from_conftest(config)
        assert discovered is None

    def test_autodiscover_empty_conftest(self, tmp_path):
        """Test auto-discovery returns None when conftest.py has no custom settings."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text("# Empty conftest")

        config = Mock()
        config.rootdir = tmp_path

        discovered = _autodiscover_from_conftest(config)
        assert discovered is None

    def test_autodiscover_multiple_settings_returns_first(self, tmp_path):
        """Test that autodiscovery returns first settings class when multiple exist."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class FirstSettings(PytestSettings):
                    pass

                class SecondSettings(PytestSettings):
                    pass
                """
            )
        )

        config = Mock()
        config.rootdir = tmp_path

        discovered = _autodiscover_from_conftest(config)
        assert discovered is not None
        # Should return one of them (order depends on inspect.getmembers)
        assert discovered.__name__ in {"FirstSettings", "SecondSettings"}

    def test_autodiscover_handles_errors(self, tmp_path):
        """Test that autodiscovery handles errors gracefully."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text("invalid syntax @#$%")

        config = Mock()
        config.rootdir = tmp_path
        config.warn = Mock()

        discovered = _autodiscover_from_conftest(config)
        assert discovered is None
        assert config.warn.called


class TestGetSettingsClassFromIni:
    """Tests for get_settings_class_from_ini function."""

    def test_get_settings_with_dot_notation(self, tmp_path):
        """Test getting settings class with module.Class notation."""
        # Create a module with a settings class
        settings_module = tmp_path / "my_settings.py"
        settings_module.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class MySettings(PytestSettings):
                    custom: str = "test"
                """
            )
        )

        config = Mock()
        config.getini.return_value = "my_settings.MySettings"
        config.rootdir = str(tmp_path)

        try:
            settings_class = get_settings_class_from_ini(config)
            assert settings_class is not None
            assert settings_class.__name__ == "MySettings"
        finally:
            # Clean up sys.modules to avoid pollution
            if "my_settings" in sys.modules:
                del sys.modules["my_settings"]

    def test_get_settings_with_colon_notation(self, tmp_path):
        """Test getting settings class with module:Class notation."""
        settings_module = tmp_path / "my_settings.py"
        settings_module.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class MySettings(PytestSettings):
                    custom: str = "test"
                """
            )
        )

        config = Mock()
        config.getini.return_value = "my_settings:MySettings"
        config.rootdir = str(tmp_path)

        try:
            settings_class = get_settings_class_from_ini(config)
            assert settings_class is not None
            assert settings_class.__name__ == "MySettings"
        finally:
            # Clean up sys.modules to avoid pollution
            if "my_settings" in sys.modules:
                del sys.modules["my_settings"]

    def test_get_settings_returns_none_when_not_configured(self):
        """Test that None is returned when no class path is configured."""
        config = Mock()
        config.getini.return_value = ""

        settings_class = get_settings_class_from_ini(config)
        assert settings_class is None

    def test_get_settings_invalid_format_raises(self):
        """Test that invalid format raises ImportError."""
        config = Mock()
        config.getini.return_value = "invalid_format"
        config.rootdir = "/tmp"

        with pytest.raises(ImportError):
            get_settings_class_from_ini(config)

    def test_get_settings_nonexistent_module_raises(self):
        """Test that nonexistent module raises ImportError."""
        config = Mock()
        config.getini.return_value = "nonexistent.module.Class"
        config.rootdir = "/tmp"

        with pytest.raises(ImportError):
            get_settings_class_from_ini(config)

    def test_get_settings_not_subclass_raises(self, tmp_path):
        """Test that non-PytestSettings class raises ImportError."""
        settings_module = tmp_path / "invalid_settings.py"
        settings_module.write_text(
            textwrap.dedent(
                """
                class NotASettings:
                    pass
                """
            )
        )

        config = Mock()
        config.getini.return_value = "invalid_settings.NotASettings"
        config.rootdir = str(tmp_path)

        try:
            with pytest.raises(ImportError):
                get_settings_class_from_ini(config)
        finally:
            # Clean up sys.modules to avoid pollution
            if "invalid_settings" in sys.modules:
                del sys.modules["invalid_settings"]


class TestDiscoverSettingsClass:
    """Tests for discover_settings_class function."""

    def test_discover_uses_ini_first(self, tmp_path):
        """Test that ini configuration has priority over autodiscovery."""
        # Create conftest with settings
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class ConftestSettings(PytestSettings):
                    source: str = "conftest"
                """
            )
        )

        # Create ini-configured settings
        ini_module = tmp_path / "ini_settings.py"
        ini_module.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class IniSettings(PytestSettings):
                    source: str = "ini"
                """
            )
        )

        config = Mock()
        config.getini.return_value = "ini_settings.IniSettings"
        config.rootdir = str(tmp_path)

        try:
            discovered = discover_settings_class(config)
            # Should use ini settings, not conftest
            assert discovered.__name__ == "IniSettings"
        finally:
            # Clean up sys.modules to avoid pollution
            if "ini_settings" in sys.modules:
                del sys.modules["ini_settings"]

    def test_discover_uses_autodiscovery_when_no_ini(self, tmp_path):
        """Test that autodiscovery is used when ini is not configured."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class ConftestSettings(PytestSettings):
                    source: str = "conftest"
                """
            )
        )

        config = Mock()
        config.getini.return_value = ""
        config.rootdir = tmp_path

        discovered = discover_settings_class(config)
        assert discovered.__name__ == "ConftestSettings"

    def test_discover_returns_default_when_nothing_found(self, tmp_path):
        """Test that default PytestSettings is returned when nothing is found."""
        config = Mock()
        config.getini.return_value = ""
        config.rootdir = tmp_path

        discovered = discover_settings_class(config)
        assert discovered is PytestSettings

    def test_discover_falls_back_on_ini_error(self, tmp_path):
        """Test that discovery falls back to autodiscovery on ini error."""
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text(
            textwrap.dedent(
                """
                from pytest_configurex.settings import PytestSettings

                class ConftestSettings(PytestSettings):
                    source: str = "fallback"
                """
            )
        )

        config = Mock()
        config.getini.return_value = "nonexistent.Settings"
        config.rootdir = tmp_path
        config.warn = Mock()

        discovered = discover_settings_class(config)
        # Should fall back to conftest autodiscovery
        assert discovered.__name__ == "ConftestSettings"
        assert config.warn.called


class TestDiscoveryIntegration:
    """Integration tests using pytester."""

    def test_custom_settings_discovery_integration(self, pytester):
        """Test full discovery flow with pytester."""
        pytester.makeconftest(
            """
            from pytest_configurex import PytestSettings

            class IntegrationSettings(PytestSettings):
                integration_field: str = "integration_test"
            """
        )

        pytester.makepyfile(
            """
            def test_integration(configurex):
                assert hasattr(configurex, 'integration_field')
                assert configurex.integration_field == "integration_test"
            """
        )

        result = pytester.runpytest("-v")
        result.stdout.fnmatch_lines(["*::test_integration PASSED*"])
        assert result.ret == 0

    def test_ini_settings_override_integration(self, pytester):
        """Test that ini settings override conftest autodiscovery."""
        # Create conftest settings
        pytester.makeconftest(
            """
            from pytest_configurex import PytestSettings

            class ConftestSettings(PytestSettings):
                source: str = "conftest"
            """
        )

        # Create ini settings module
        pytester.makepyfile(
            ini_settings="""
            from pytest_configurex import PytestSettings

            class IniSettings(PytestSettings):
                source: str = "ini"
            """
        )

        # Configure pytest.ini
        pytester.makeini(
            """
            [pytest]
            configurex_settings_class = ini_settings.IniSettings
            """
        )

        pytester.makepyfile(
            """
            def test_ini_priority(configurex):
                assert configurex.source == "ini"
            """
        )

        result = pytester.runpytest("-v")
        result.stdout.fnmatch_lines(["*::test_ini_priority PASSED*"])
        assert result.ret == 0
