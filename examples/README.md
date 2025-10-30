# pytest-configurex Examples

This directory contains examples showing how to use pytest-configurex.

## Quick Start

### 1. Basic Usage

Create a `.env` file in your project root:

```bash
# .env
LOG_LEVEL=DEBUG
TIMEOUT=30
```

Use the `configurex` fixture in your tests:

```python
def test_with_configurex(configurex):
    log_level = configurex.get("log_level")
    assert log_level == "DEBUG"
```

### 2. Configuration Precedence

pytest-configurex merges configuration from three sources with the following precedence:

**CLI > .env > pytest.ini**

Example:

```bash
# .env
LOG_LEVEL=INFO
```

```ini
; pytest.ini
[pytest]
log_level = WARNING
```

```bash
# Command line wins
$ pytest --log-level=DEBUG
# configurex["log_level"] == "DEBUG"

# .env wins over ini
$ pytest
# configurex["log_level"] == "INFO"
```

## Advanced Usage

### Plugin Registration

External plugins or your `conftest.py` can register custom mappings:

```python
# conftest.py
def pytest_configurex_register(registry):
    """Register custom environment variable mappings."""
    registry.register(
        field="database_url",
        cli_flag="--database-url",
        ini_key="database_url"
    )
```

Then use in `.env`:

```bash
DATABASE_URL=postgresql://localhost/testdb
```

And access in tests:

```python
def test_database(configurex):
    db_url = configurex.get("database_url")
    # Use db_url...
```

### pytest-cov Integration

```python
# conftest.py
def pytest_configurex_register(registry):
    registry.register("coverage_source", "--cov", ini_key="cov")
    registry.register("coverage_report", "--cov-report")
```

```bash
# .env
COVERAGE_SOURCE=src
COVERAGE_REPORT=html
```

Now you can run `pytest` without CLI arguments and coverage will be configured from `.env`.

### pytest-xdist Integration

```python
# conftest.py
def pytest_configurex_register(registry):
    registry.register("num_workers", "-n", ini_key="numprocesses")
```

```bash
# .env
NUM_WORKERS=4
```

Run parallel tests without `-n 4` flag.

## File Structure

```
examples/
├── README.md                 # This file
├── .env.example             # Example .env file
├── conftest_example.py      # Example plugin registration
└── pytest.ini.example       # Example pytest.ini
```

## Best Practices

### 1. Use .env for Environment-Specific Values

```bash
# .env.development
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://localhost/dev_db

# .env.ci
LOG_LEVEL=INFO
DATABASE_URL=postgresql://ci-db/test_db
```

### 2. Use pytest.ini for Project Defaults

```ini
[pytest]
log_level = INFO
timeout = 60
testpaths = tests
```

### 3. Use CLI for One-Off Overrides

```bash
# Override just for this run
pytest --log-level=DEBUG --timeout=120
```

### 4. Custom Fields for Application Config

```python
# conftest.py
def pytest_configurex_register(registry):
    registry.register("api_base_url", "--api-url")
    registry.register("test_user_email", "--test-email")

@pytest.fixture
def api_client(configurex):
    base_url = configurex.get("api_base_url", "http://localhost:8000")
    return APIClient(base_url)
```

```bash
# .env
API_BASE_URL=https://staging.example.com
TEST_USER_EMAIL=test@staging.example.com
```

## Real-World Examples

### Example 1: Multi-Environment Testing

```python
# conftest.py
def pytest_configurex_register(registry):
    registry.register("test_env", "--env")
    registry.register("api_url", "--api-url")
    registry.register("db_url", "--database-url")

@pytest.fixture(scope="session")
def test_environment(configurex):
    return configurex.get("test_env", "local")

@pytest.fixture
def api_client(configurex):
    url = configurex.get("api_url")
    return APIClient(url)
```

```bash
# .env.local
TEST_ENV=local
API_URL=http://localhost:8000
DB_URL=postgresql://localhost/test

# .env.staging
TEST_ENV=staging
API_URL=https://staging.example.com
DB_URL=postgresql://staging-db/test
```

### Example 2: Feature Flags

```python
# conftest.py
def pytest_configurex_register(registry):
    registry.register("enable_experimental", "--experimental")
    registry.register("skip_slow_tests", "--skip-slow")

@pytest.fixture(autouse=True)
def skip_slow_tests(request, configurex):
    if configurex.get("skip_slow_tests") == "true":
        if request.node.get_closest_marker("slow"):
            pytest.skip("Skipping slow test")
```

```bash
# .env
SKIP_SLOW_TESTS=true
ENABLE_EXPERIMENTAL=false
```

### Example 3: Dynamic Test Data

```python
# conftest.py
def pytest_configurex_register(registry):
    registry.register("test_data_path", "--test-data")
    registry.register("fixtures_path", "--fixtures")

@pytest.fixture
def test_data(configurex):
    path = configurex.get("test_data_path", "tests/data")
    return load_test_data(path)
```

```bash
# .env
TEST_DATA_PATH=/shared/test-data
FIXTURES_PATH=/shared/fixtures
```

## Troubleshooting

### Configuration not being loaded

1. Check that `.env` file is in the pytest rootdir
2. Verify field names match (case-insensitive)
3. Ensure custom fields are registered via `pytest_configurex_register`

### Values not being merged correctly

Check precedence: CLI arguments always win, then .env, then pytest.ini

### Help

Run `pytest --help` to see all registered configurex options:

```bash
pytest --help
# Look for "configurex:" section
```

## See Also

- [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [pytest configuration](https://docs.pytest.org/en/stable/reference/customize.html)
- [pytest plugins](https://docs.pytest.org/en/stable/how-to/plugins.html)
