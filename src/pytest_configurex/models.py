"""Pydantic settings models for pytest-configurex."""

from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurexSettings(BaseSettings):
    """Base settings model for pytest-configurex.

    This model loads configuration from .env files and allows extra fields
    for dynamic plugin-registered settings.

    Built-in fields map to common pytest options:
    - log_level: Sets the logging level
    - timeout: Sets a global timeout for tests
    - addopts: Additional pytest command-line options

    Plugins can add their own fields dynamically through the extra="allow" config.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        case_sensitive=False,
    )

    # Built-in settings that map to common pytest options
    log_level: str | None = None
    timeout: int | None = None
    addopts: str | None = None

    def dump_config(self, *, include_none: bool = False, as_cli: bool = False) -> dict[str, Any]:
        """Dump configuration as a dictionary.

        Args:
            include_none: If True, include fields with None values
            as_cli: If True, format keys for CLI usage (replace _ with -)

        Returns:
            Dictionary of configuration values
        """
        data = self.model_dump(exclude_none=not include_none)

        # Include any extra fields added dynamically
        if hasattr(self, "__pydantic_extra__") and self.__pydantic_extra__:
            data.update(self.__pydantic_extra__)

        if as_cli:
            # Convert to CLI format: underscore to dash, values to strings
            return {k.replace("_", "-"): str(v) for k, v in data.items()}

        return data
