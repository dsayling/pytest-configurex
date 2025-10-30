"""Conftest with custom settings class for auto-discovery benchmark."""

from pytest_pytest_configurex import PytestSettings


class BenchmarkSettings(PytestSettings):
    """Custom settings class for benchmarking auto-discovery."""

    custom_field: str = "benchmark_value"
    another_field: int = 42
