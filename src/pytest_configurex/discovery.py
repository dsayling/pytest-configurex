"""Auto-discovery logic for custom PytestSettings classes."""

import importlib
import importlib.util
import inspect
import sys
from pathlib import Path

from pytest_configurex.settings import PytestSettings


def get_settings_class_from_ini(config) -> type[PytestSettings] | None:
    """
    Get settings class from pytest.ini configuration.

    Checks for 'configurex_settings_class' option in pytest.ini.
    If found, imports and returns the specified class.

    Args:
        config: Pytest config object

    Returns:
        Type[PytestSettings] or None if not configured

    Raises:
        ImportError: If the specified class cannot be imported
        AttributeError: If the specified class path is invalid
    """
    # Get the configurex_settings_class from pytest.ini
    class_path = config.getini("configurex_settings_class")

    if not class_path:
        return None

    # Parse the class path (e.g., "myapp.settings.MySettings")
    try:
        if ":" in class_path:
            # Support both "module.path:ClassName" and "module.path.ClassName"
            module_path, class_name = class_path.rsplit(":", 1)
        elif "." in class_path:
            # Assume last part is the class name
            module_path, class_name = class_path.rsplit(".", 1)
        else:
            raise ValueError(
                f"Invalid class path format: {class_path}. "
                f"Expected 'module.path.ClassName' or 'module.path:ClassName'"
            )

        # Add the pytest rootdir to sys.path if not already there
        # This allows importing test modules
        rootdir = str(config.rootdir)
        if rootdir not in sys.path:
            sys.path.insert(0, rootdir)

        try:
            # Import the module
            module = importlib.import_module(module_path)
        finally:
            # Clean up sys.path if we added it
            if rootdir in sys.path and sys.path[0] == rootdir:
                sys.path.remove(rootdir)

        # Get the class from the module
        settings_class = getattr(module, class_name)

        # Verify it's a subclass of PytestSettings
        if not issubclass(settings_class, PytestSettings):
            raise TypeError(
                f"Class {class_path} is not a subclass of PytestSettings. "
                f"Please ensure your custom settings class inherits from PytestSettings."
            )

        return settings_class

    except (ImportError, AttributeError, ValueError, TypeError) as e:
        # Re-raise with more context
        raise ImportError(
            f"Failed to import settings class from pytest.ini: {class_path}. Error: {e}"
        ) from e


def _load_conftest_module(conftest_path: Path):
    """
    Load conftest.py as a module.

    Args:
        conftest_path: Path to conftest.py file

    Returns:
        Loaded module or None if loading fails

    Raises:
        ImportError: If module spec cannot be created or module cannot be loaded
    """
    spec = importlib.util.spec_from_file_location("conftest", conftest_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create module spec for {conftest_path}")

    conftest_module = importlib.util.module_from_spec(spec)

    # Temporarily add to sys.modules to handle relative imports
    sys.modules["conftest"] = conftest_module

    try:
        try:
            spec.loader.exec_module(conftest_module)
            return conftest_module
        except (SyntaxError, FileNotFoundError) as e:
            raise ImportError(f"Failed to load module from {conftest_path}: {e}") from e
    finally:
        # Clean up sys.modules
        if "conftest" in sys.modules:
            del sys.modules["conftest"]


def _find_settings_subclasses(module) -> list[type[PytestSettings]]:
    """
    Find all PytestSettings subclasses defined in the given module.

    Args:
        module: Python module to search

    Returns:
        List of PytestSettings subclasses found in the module
    """
    custom_classes = []
    for _name, obj in inspect.getmembers(module, inspect.isclass):
        # Check if it's a subclass of PytestSettings but not PytestSettings itself
        if (
            issubclass(obj, PytestSettings)
            and obj is not PytestSettings
            and obj.__module__ == module.__name__  # Ensure it's defined in module, not imported
        ):
            custom_classes.append(obj)
    return custom_classes


def _autodiscover_from_conftest(config) -> type[PytestSettings] | None:
    """
    Auto-discover PytestSettings subclass from conftest.py.

    Args:
        config: Pytest config object

    Returns:
        First PytestSettings subclass found, or None if not found or on error
    """
    rootdir = Path(config.rootdir)
    conftest_path = rootdir / "conftest.py"

    # If conftest.py doesn't exist, return None
    if not conftest_path.exists():
        return None

    try:
        conftest_module = _load_conftest_module(conftest_path)
        custom_classes = _find_settings_subclasses(conftest_module)

        # Return the first custom class if found
        return custom_classes[0] if custom_classes else None

    except Exception as e:
        # If anything goes wrong, log the error and return None
        if hasattr(config, "warn"):
            config.warn(
                "C1",
                f"Failed to discover custom PytestSettings class from conftest.py: {e}",
                fslocation=str(conftest_path),
            )
        return None


def discover_settings_class(config) -> type[PytestSettings]:
    """
    Discover custom PytestSettings class.

    Priority:
    1. Check pytest.ini for 'configurex_settings_class' (explicit registration)
    2. Auto-discover from conftest.py (looks for PytestSettings subclass)
    3. Return default PytestSettings class

    Args:
        config: Pytest config object

    Returns:
        Type[PytestSettings]: Custom settings class or default PytestSettings
    """
    # PRIORITY 1: Check pytest.ini for explicit registration
    try:
        ini_class = get_settings_class_from_ini(config)
        if ini_class is not None:
            return ini_class
    except ImportError as e:
        # Log error but continue to auto-discovery fallback
        if hasattr(config, "warn"):
            config.warn("C1", str(e))

    # PRIORITY 2: Auto-discover from conftest.py
    discovered_class = _autodiscover_from_conftest(config)
    if discovered_class is not None:
        return discovered_class

    # PRIORITY 3: Return default
    return PytestSettings


def load_settings_for_config(
    config, settings_class: type[PytestSettings] | None = None
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
