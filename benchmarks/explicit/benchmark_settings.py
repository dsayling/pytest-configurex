"""Settings module for explicit registration benchmark."""

from pytest_pytest_configurex import PytestSettings


class ExplicitSettings(PytestSettings):
    """Custom settings class for benchmarking explicit registration."""

    custom_field: str = "explicit_value"
    another_field: int = 99
