"""Hook specifications for pytest-configurex.

This module defines hooks that other pytest plugins can implement
to extend configurex functionality.
"""

import pytest


@pytest.hookspec
def pytest_configurex_register(registry):
    """Hook for plugins to register additional Configurex mappings.

    This hook is called during pytest_configure, allowing other plugins
    to register their own environment variable to CLI/ini mappings.

    Args:
        registry: The ConfigurexRegistry instance

    Example:
        In your plugin or conftest.py:

        >>> def pytest_configurex_register(registry):
        ...     registry.register("coverage_source", "--cov", ini_key="cov")
        ...     registry.register("coverage_report", "--cov-report")
    """
