"""Example conftest.py showing how to register custom configurex mappings.

This example shows how external plugins or user conftest.py files can
register their own environment variable to CLI/ini mappings.
"""


def pytest_configurex_register(registry):
    """Register custom configurex mappings.

    This hook is called during pytest_configure, allowing you to add
    your own mappings between environment variables and pytest options.

    Args:
        registry: The ConfigurexRegistry instance
    """
    # Example: pytest-cov integration
    # This allows you to set COVERAGE_SOURCE=src in .env
    # instead of always using --cov=src on command line
    registry.register(
        field="coverage_source",
        cli_flag="--cov",
        ini_key="cov",
    )

    registry.register(
        field="coverage_report",
        cli_flag="--cov-report",
        ini_key="cov_report",
    )

    # Example: pytest-xdist integration
    # Allows NUM_WORKERS=4 in .env for parallel test execution
    registry.register(
        field="num_workers",
        cli_flag="-n",
        ini_key="numprocesses",
    )

    # Example: Custom test markers
    registry.register(
        field="test_marker",
        cli_flag="-m",
        ini_key="markers",
    )

    # Example: Custom verbosity level
    registry.register(
        field="verbosity",
        cli_flag="-v",
        ini_key="verbosity_level",
    )

    # Example: Custom database URL for integration tests
    # No CLI/ini mapping needed, just .env
    registry.register(
        field="database_url",
        cli_flag="--database-url",
        ini_key=None,  # Only available via .env or CLI
    )


# Example usage in tests:
def test_example_with_configurex(configurex):
    """Example test showing how to access merged configuration."""
    # Get coverage source (from CLI, .env, or pytest.ini)
    cov_source = configurex.get("coverage_source")
    if cov_source:
        print(f"Coverage enabled for: {cov_source}")

    # Get number of workers for parallel execution
    num_workers = configurex.get("num_workers")
    if num_workers:
        print(f"Running with {num_workers} workers")

    # Get custom database URL
    db_url = configurex.get("database_url")
    if db_url:
        print(f"Using database: {db_url}")
