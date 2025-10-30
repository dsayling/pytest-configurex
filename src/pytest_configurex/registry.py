"""Registry for mapping environment variables to pytest CLI flags and ini options."""

from typing import Iterator


class ConfigurexRegistry:
    """Registry for mapping settings fields to pytest CLI/ini options.

    The registry maintains mappings between:
    - Settings model field names (e.g., "log_level")
    - CLI flags (e.g., "--log-level")
    - pytest.ini keys (e.g., "log_level")

    This allows plugins to register their own mappings dynamically.
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._map: dict[str, dict[str, str | None]] = {}

    def register(
        self,
        field: str,
        cli_flag: str,
        ini_key: str | None = None,
    ) -> None:
        """Register a mapping from settings field to CLI flag and/or ini key.

        Args:
            field: The field name in the ConfigurexSettings model
            cli_flag: The CLI flag (e.g., "--log-level")
            ini_key: Optional pytest.ini key (e.g., "log_level")

        Example:
            >>> registry.register("log_level", "--log-level", ini_key="log_level")
        """
        self._map[field] = {
            "cli": cli_flag,
            "ini": ini_key,
        }

    def resolve(self, field: str) -> dict[str, str | None] | None:
        """Resolve a field to its CLI/ini mapping.

        Args:
            field: The field name to resolve

        Returns:
            Dictionary with "cli" and "ini" keys, or None if not found
        """
        return self._map.get(field)

    def items(self) -> Iterator[tuple[str, dict[str, str | None]]]:
        """Iterate over all registered mappings.

        Yields:
            Tuples of (field_name, mapping_dict)
        """
        return iter(self._map.items())

    def get_all_cli_flags(self) -> list[str]:
        """Get all registered CLI flags.

        Returns:
            List of CLI flags
        """
        return [meta["cli"] for meta in self._map.values() if meta["cli"]]

    def get_field_for_cli(self, cli_flag: str) -> str | None:
        """Get the field name for a given CLI flag.

        Args:
            cli_flag: The CLI flag to look up

        Returns:
            The field name, or None if not found
        """
        for field, meta in self._map.items():
            if meta["cli"] == cli_flag:
                return field
        return None


# Global registry instance
registry = ConfigurexRegistry()

# Register built-in mappings
# Note: We use configurex-specific option names to avoid conflicts with existing pytest options
registry.register("log_level", "--configurex-log-level", ini_key="configurex_log_level")
registry.register("timeout", "--configurex-timeout", ini_key="configurex_timeout")
registry.register("addopts", "--configurex-addopts", ini_key="configurex_addopts")
