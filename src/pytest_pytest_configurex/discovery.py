"""Auto-discovery logic for custom PytestSettings classes."""

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Optional, Type

from pytest_pytest_configurex.settings import PytestSettings


def discover_settings_class(config) -> Type[PytestSettings]:
    """
    Auto-discover custom PytestSettings class from conftest.py.

    Searches for a subclass of PytestSettings in the conftest.py file
    located in the pytest root directory.

    Priority:
    1. Look for any class that subclasses PytestSettings (excluding PytestSettings itself)
    2. If multiple found, use the first one discovered
    3. If none found, return the default PytestSettings class

    Args:
        config: Pytest config object

    Returns:
        Type[PytestSettings]: Custom settings class or default PytestSettings
    """
    # Get the pytest root directory
    rootdir = Path(config.rootdir)
    conftest_path = rootdir / "conftest.py"

    # If conftest.py doesn't exist, return default
    if not conftest_path.exists():
        return PytestSettings

    try:
        # Load conftest.py as a module
        spec = importlib.util.spec_from_file_location("conftest", conftest_path)
        if spec is None or spec.loader is None:
            return PytestSettings

        conftest_module = importlib.util.module_from_spec(spec)

        # Temporarily add to sys.modules to handle relative imports
        sys.modules["conftest"] = conftest_module

        try:
            spec.loader.exec_module(conftest_module)
        finally:
            # Clean up sys.modules
            if "conftest" in sys.modules:
                del sys.modules["conftest"]

        # Search for PytestSettings subclasses
        custom_classes = []
        for _name, obj in inspect.getmembers(conftest_module, inspect.isclass):
            # Check if it's a subclass of PytestSettings but not PytestSettings itself
            if (
                issubclass(obj, PytestSettings)
                and obj is not PytestSettings
                and obj.__module__ == "conftest"  # Ensure it's defined in conftest, not imported
            ):
                custom_classes.append(obj)

        # If we found custom classes, use the first one
        if custom_classes:
            custom_class = custom_classes[0]
            # Log discovery for debugging
            if hasattr(config, "hook") and hasattr(config.hook, "pytest_configure"):
                # Use pytest's terminal writer if available
                if hasattr(config, "_configured") and not config._configured:
                    pass  # Don't log during early configuration
            return custom_class

        # No custom class found, return default
        return PytestSettings

    except Exception as e:
        # If anything goes wrong, log the error and return default
        if hasattr(config, "warn"):
            config.warn(
                "C1",
                f"Failed to discover custom PytestSettings class from conftest.py: {e}",
                fslocation=str(conftest_path),
            )
        # Return default on any error
        return PytestSettings


def load_settings_for_config(
    config, settings_class: Optional[Type[PytestSettings]] = None
) -> PytestSettings:
    """
    Load settings instance for pytest config.

    Args:
        config: Pytest config object
        settings_class: Optional custom settings class. If None, will auto-discover.

    Returns:
        PytestSettings instance
    """
    # Discover or use provided class
    if settings_class is None:
        settings_class = discover_settings_class(config)

    # Get root directory for .env file discovery
    rootdir = Path(config.rootdir)

    # Load settings
    try:
        settings = settings_class.load_settings(config_root=rootdir)
        return settings
    except Exception as e:
        # Log error and return default instance
        if hasattr(config, "warn"):
            config.warn(
                "C1",
                f"Failed to load settings from {settings_class.__name__}: {e}. "
                f"Using default settings.",
            )
        # Return default settings instance on error
        return PytestSettings.load_settings(config_root=rootdir)
