"""pytest-configurex: A unified configuration layer for pytest.

This plugin provides:
- Loading of .env files with typed models via pydantic-settings
- Merging with pytest CLI and ini values
- Plugin registration system for custom mappings (.env ’ CLI/ini options)
"""

from .core import get_env_file_path, load_env, merge_layers
from .models import ConfigurexSettings
from .registry import ConfigurexRegistry, registry

__version__ = "0.0.1"

__all__ = [
    "ConfigurexSettings",
    "ConfigurexRegistry",
    "registry",
    "load_env",
    "merge_layers",
    "get_env_file_path",
]
