"""
pytest-configurex: Configure pytest via .env files using pydantic-settings.

This plugin allows you to configure pytest using .env.pytest files and
environment variables with the X_ prefix.

Basic usage:
    Create a .env.pytest file:
        X_VERBOSITY=2
        X_LOG_LEVEL=INFO
        X_MARKERS=not slow

    The settings will be automatically loaded and applied to pytest.

Advanced usage:
    Subclass PytestSettings in your conftest.py:

        from pytest_configurex import PytestSettings

        class MySettings(PytestSettings):
            custom_field: str = "default"

            def apply_to_pytest(self, config):
                super().apply_to_pytest(config)
                # Custom logic here

    Access settings in tests via the configurex fixture:

        def test_something(configurex):
            assert configurex.verbosity == 2
"""

from pytest_configurex.settings import PytestSettings

__version__ = "0.0.1"
__all__ = ["PytestSettings"]
