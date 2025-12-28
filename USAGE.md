# pytest-configurex Usage Guide

## Quick Start

### 1. Install the plugin

```bash
uv add pytest-configurex
# or
pip install pytest-configurex
```

### 2. Create a `.env.pytest` file

```bash
# .env.pytest
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_LOG_CLI=true
```

### 3. Run pytest

The settings will be automatically loaded:

```bash
pytest
```

## Configuration Priority

Settings are applied in the following order (highest to lowest):

1. **Standard pytest CLI arguments** (e.g., `-vv`, `--log-level=DEBUG`, `-m unit`)
2. **`.env.pytest` file** or **custom Settings class**
3. **Default values**

## Environment Variable Prefix

All environment variables must use the `X_` prefix:

```bash
X_VERBOSITY=2          # Maps to -vv
X_LOG_LEVEL=DEBUG      # Maps to --log-cli-level=DEBUG
X_MARKERS=not slow     # Maps to -m "not slow"
```

## Configuration File Discovery

The plugin searches for configuration files in this order:

1. `.env.pytest` (preferred)
2. `.env` (fallback)
3. Environment variables only (if no file exists)

## Available Settings

### Verbosity
```bash
X_VERBOSITY=2  # 0=quiet, 1=-v, 2=-vv, 3=-vvv
```

### Logging
```bash
X_LOG_LEVEL=INFO       # DEBUG, INFO, WARNING, ERROR, CRITICAL
X_LOG_CLI=true         # Enable live logging to console
X_LOG_FILE=pytest.log  # Write logs to file
```

### Test Selection
```bash
X_MARKERS=slow         # Only run tests marked with @pytest.mark.slow
X_MARKERS=not slow     # Skip slow tests
```

### Coverage (requires pytest-cov)
```bash
X_COVERAGE_ENABLED=true
X_COVERAGE_SOURCE=src
X_COVERAGE_REPORT=term-missing  # term, term-missing, html, xml
```

### xdist (requires pytest-xdist)
```bash
X_XDIST_NUMPROCESSES=4     # Run tests in parallel with 4 processes
X_XDIST_DIST=loadscope     # Distribution mode: load, loadscope, etc.
```

## Using the `configurex` Fixture

Access settings in your tests via the `configurex` fixture:

```python
def test_something(configurex):
    assert configurex.verbosity == 2
    assert configurex.log_level == "INFO"
    print(f"Settings: {configurex}")
```

## Custom Settings Class

Create a custom settings class in your `conftest.py` to add your own fields:

```python
# conftest.py
from pytest_configurex import PytestSettings

class MyProjectSettings(PytestSettings):
    """Custom settings for my project."""

    # Add custom fields
    api_base_url: str = "http://localhost:8000"
    api_timeout: int = 30
    enable_debug_mode: bool = False

    def apply_to_pytest(self, config):
        """Override to add custom logic."""
        # Call parent to apply standard settings
        super().apply_to_pytest(config)

        # Add custom initialization
        if self.enable_debug_mode:
            print(f"Debug mode enabled! API URL: {self.api_base_url}")
```

Then in your `.env.pytest`:

```bash
# Standard settings
X_VERBOSITY=2
X_LOG_LEVEL=DEBUG

# Custom settings
X_API_BASE_URL=https://api.example.com
X_API_TIMEOUT=60
X_ENABLE_DEBUG_MODE=true
```

Use custom settings in tests:

```python
def test_api_call(configurex):
    """configurex is automatically your custom MyProjectSettings instance."""
    assert configurex.api_base_url == "https://api.example.com"
    assert configurex.api_timeout == 60
    assert configurex.enable_debug_mode is True
```

## Overriding Settings with Standard Pytest CLI

You can override any .env setting using standard pytest CLI options:

```bash
# Override verbosity with standard pytest options
pytest -vv              # Verbosity level 2
pytest -vvv             # Verbosity level 3

# Override log level with standard pytest options
pytest --log-level=DEBUG
pytest --log-cli-level=DEBUG

# Override markers with standard pytest options
pytest -m "slow and integration"
pytest -m unit

# Override multiple settings
pytest -vv --log-level=INFO --log-cli

# Enable coverage with pytest-cov options
pytest --cov=src --cov-report=html

# Run in parallel with pytest-xdist options
pytest -n 4
pytest -n auto --dist=loadscope
```

**Note:** Standard pytest CLI options take priority over `.env.pytest` settings.

## Example Project Structure

```
my-project/
├── .env.pytest          # Plugin configuration
├── conftest.py          # Optional custom settings class
├── src/
│   └── myapp/
│       └── __init__.py
└── tests/
    ├── test_unit.py
    └── test_integration.py
```

## Tips

1. **Keep sensitive data out of .env.pytest**: Use environment variables for secrets
2. **Use .env for defaults**: Let `.env` be your fallback for local development
3. **Commit .env.pytest.example**: Show teammates what settings are available
4. **Use markers wisely**: Don't set `X_MARKERS` globally if you want all tests to run by default
5. **Override in CI**: Use CLI arguments in CI pipelines to override local settings

## Debugging

To see what settings are loaded:

```python
def test_debug_settings(configurex):
    print(configurex)  # Shows: PytestSettings(verbosity=2, log_level='INFO', ...)
    print(configurex.get_cli_args())  # Shows equivalent CLI arguments
```

## Common Patterns

### Development Environment
```bash
# .env.pytest
X_VERBOSITY=2
X_LOG_CLI=true
X_LOG_LEVEL=DEBUG
X_MARKERS=not slow
```

### CI Environment
```bash
pytest -v --cov=src --cov-report=xml
```

### Fast Test Run
```bash
# .env.pytest
X_MARKERS=not slow
X_XDIST_NUMPROCESSES=auto
```

### Debugging Specific Tests
```bash
pytest -vvv --log-level=DEBUG tests/test_specific.py
```
