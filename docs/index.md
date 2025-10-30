# pytest-configurex Documentation

**Configure pytest with .env files and pydantic-settings for flexible, type-safe test configuration.**

[![PyPI version](https://img.shields.io/pypi/v/pytest-configurex.svg)](https://pypi.org/project/pytest-configurex)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-configurex.svg)](https://pypi.org/project/pytest-configurex)
[![Build Status](https://github.com/dsayling/pytest-configurex/actions/workflows/main.yml/badge.svg)](https://github.com/dsayling/pytest-configurex/actions/workflows/main.yml)

---

## Overview

pytest-configurex is a pytest plugin that makes test configuration simple, flexible, and type-safe. It leverages `.env` files and pydantic-settings to provide a powerful configuration system for your pytest test suite.

### Why pytest-configurex?

- **Centralized Configuration**: Keep all test settings in `.env.pytest` files
- **Type Safety**: Built on pydantic-settings for validation and type checking
- **Team Consistency**: Share test configurations across your team via version control
- **Environment Flexibility**: Different configs for dev, CI, staging, production
- **Zero Boilerplate**: Automatic discovery and application of settings
- **Extensible**: Easily add custom configuration fields

---

## Quick Start

### Installation

Install via pip or uv:

```bash
pip install pytest-configurex
# or
uv add pytest-configurex
```

### Basic Usage

1. **Create a `.env.pytest` file** in your project root:

```bash
# .env.pytest
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_LOG_CLI=true
X_MARKERS=not slow
```

2. **Run pytest** - settings are automatically loaded:

```bash
pytest
```

3. **Access settings in your tests** via the `configurex` fixture:

```python
def test_something(configurex):
    assert configurex.verbosity == 2
    assert configurex.log_level == "INFO"
    print(f"Current config: {configurex}")
```

That's it! No additional setup required.

---

## Features

### Core Features

- **Environment-based configuration**: Load test settings from `.env.pytest` files
- **Type-safe settings**: Built on pydantic-settings for validation and type checking
- **Pytest integration**: Automatically applies settings to pytest configuration
- **Custom settings**: Extend `PytestSettings` to add your own configuration fields
- **Fixture access**: Access settings in tests via the `configurex` fixture
- **Priority-based**: CLI args override .env files, which override defaults
- **Flexible discovery**: Searches for `.env.pytest`, then `.env`, then environment variables

### Built-in Settings Support

pytest-configurex provides out-of-the-box support for common pytest options:

#### Verbosity
```bash
X_VERBOSITY=2  # 0=quiet, 1=-v, 2=-vv, 3=-vvv
```

#### Logging
```bash
X_LOG_LEVEL=INFO        # DEBUG, INFO, WARNING, ERROR, CRITICAL
X_LOG_CLI=true          # Enable live logging to console
X_LOG_FILE=pytest.log   # Write logs to file
```

#### Test Selection
```bash
X_MARKERS=slow          # Only run tests marked with @pytest.mark.slow
X_MARKERS=not slow      # Skip slow tests
```

#### Coverage (requires pytest-cov)
```bash
X_COVERAGE_ENABLED=true
X_COVERAGE_SOURCE=src
X_COVERAGE_REPORT=term-missing
```

#### Parallel Execution (requires pytest-xdist)
```bash
X_XDIST_NUMPROCESSES=4      # Run tests in parallel with 4 processes
X_XDIST_DIST=loadscope      # Distribution mode
```

---

## Configuration Priority

Settings are applied in the following order (highest to lowest priority):

1. **Standard pytest CLI arguments** - e.g., `-vv`, `--log-level=DEBUG`, `-m unit`
2. **`.env.pytest` file** or **custom Settings class**
3. **Default values**

This means you can override file-based settings with standard pytest CLI options for one-off test runs.

---

## Custom Settings

Extend `PytestSettings` to add your own configuration fields:

```python
# conftest.py
from pytest_configurex import PytestSettings

class MyProjectSettings(PytestSettings):
    """Custom settings for my project."""

    api_base_url: str = "http://localhost:8000"
    api_timeout: int = 30
    enable_debug_mode: bool = False

    def apply_to_pytest(self, config):
        """Override to add custom logic."""
        super().apply_to_pytest(config)

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

Use in tests:

```python
def test_api_call(configurex):
    # configurex is automatically your custom MyProjectSettings instance
    assert configurex.api_base_url == "https://api.example.com"
    assert configurex.api_timeout == 60
```

---

## Examples

The [examples directory](https://github.com/dsayling/pytest-configurex/tree/main/examples) contains complete working examples:

### Environment-Based Configuration
- **[env_based_config](https://github.com/dsayling/pytest-configurex/tree/main/examples/env_based_config)** - Multiple environments (dev, staging, production)

### Test Type Configuration
- **[test_type_config](https://github.com/dsayling/pytest-configurex/tree/main/examples/test_type_config)** - Different configs for unit, integration, e2e tests

### CI/CD Integration
- **[github_actions](https://github.com/dsayling/pytest-configurex/tree/main/examples/github_actions)** - GitHub Actions workflow examples

### Task Runners
- **[task_runners](https://github.com/dsayling/pytest-configurex/tree/main/examples/task_runners)** - Integration with poethepoet, make, and just

---

## Documentation

For comprehensive documentation and advanced usage:

- **[USAGE.md](https://github.com/dsayling/pytest-configurex/blob/main/USAGE.md)** - Complete usage guide with all features
- **[README.md](https://github.com/dsayling/pytest-configurex/blob/main/README.md)** - Package overview

---

## Requirements

- Python 3.10+
- pytest 8.3.4+
- pydantic-settings 2.0+
- python-dotenv 1.0.0+

---

## Contributing

Contributions are very welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for your changes
5. Run the test suite: `pytest`
6. Run linting: `ruff check && ruff format`
7. Submit a pull request

Please ensure test coverage stays at or improves from current levels.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/dsayling/pytest-configurex/issues)
- **Repository**: [GitHub](https://github.com/dsayling/pytest-configurex)
- **PyPI**: [pytest-configurex](https://pypi.org/project/pytest-configurex)

---

## License

Distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license, pytest-configurex is free and open source software.

---

## Credits

This pytest plugin was generated with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with [@hackebrot](https://github.com/hackebrot)'s [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin) template.
