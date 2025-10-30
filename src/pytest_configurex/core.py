"""Core configuration loading and merging logic for pytest-configurex."""

from pathlib import Path
from typing import Any

from pytest import Config

from .models import ConfigurexSettings
from .registry import ConfigurexRegistry


def load_env(env_file: str | Path | None = None) -> ConfigurexSettings:
    """Load environment settings from .env file.

    Args:
        env_file: Path to .env file. If None, uses default ".env"

    Returns:
        ConfigurexSettings instance with loaded values
    """
    if env_file is None:
        return ConfigurexSettings()

    # Convert to Path and check if it exists
    env_path = Path(env_file)
    if not env_path.exists():
        # If file doesn't exist, return empty settings
        return ConfigurexSettings(_env_file=None)

    return ConfigurexSettings(_env_file=str(env_path))


def merge_layers(
    env_settings: ConfigurexSettings,
    config: Config,
    registry: ConfigurexRegistry,
) -> dict[str, Any]:
    """Merge configuration from multiple sources with proper precedence.

    Precedence order (highest to lowest):
    1. CLI arguments (--flag values)
    2. Environment variables (.env file)
    3. pytest.ini settings

    Args:
        env_settings: Settings loaded from .env file
        config: pytest Config object
        registry: Registry with field mappings

    Returns:
        Dictionary of merged configuration values
    """
    merged: dict[str, Any] = {}

    for field, meta in registry.items():
        cli_flag = meta["cli"]
        ini_key = meta["ini"]

        # Get CLI value - convert flag to option name
        # e.g., "--log-level" -> "log_level"
        cli_opt = cli_flag.lstrip("-").replace("-", "_")
        cli_val = None

        try:
            cli_val = config.getoption(cli_opt, None)
        except (ValueError, AttributeError):
            # Option might not be registered or accessible
            pass

        # Get ini value
        ini_val = None
        if ini_key:
            try:
                ini_val = config.getini(ini_key)
                # Empty string means not set in ini
                if ini_val == "" or ini_val == []:
                    ini_val = None
            except (ValueError, KeyError):
                # ini key might not be registered
                pass

        # Get env value
        env_val = getattr(env_settings, field, None)

        # Apply precedence: CLI > env > ini
        final_val = cli_val or env_val or ini_val

        if final_val is not None:
            merged[field] = final_val

    # Also include any extra fields from env_settings that aren't in registry
    if hasattr(env_settings, "__pydantic_extra__") and env_settings.__pydantic_extra__:
        for key, value in env_settings.__pydantic_extra__.items():
            if key not in merged and value is not None:
                merged[key] = value

    return merged


def get_env_file_path(config: Config) -> Path | None:
    """Determine the .env file path to use.

    Looks for .env file in the following order:
    1. pytest rootdir
    2. Current working directory

    Args:
        config: pytest Config object

    Returns:
        Path to .env file if found, None otherwise
    """
    # Try rootdir first
    rootdir = Path(config.rootpath if hasattr(config, "rootpath") else config.rootdir)
    env_file = rootdir / ".env"

    if env_file.exists():
        return env_file

    # Try current directory
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        return env_file

    return None
