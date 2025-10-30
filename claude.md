# pytest-configurex Development Guide

## Project Overview
A pytest plugin that uses pydantic-settings to configure pytest via `.env` files and environment variables with an `X_` prefix.

## Package Manager
This project uses **uv** for Python package management.

## Development Setup

### Install Dependencies
```bash
uv sync
```

### Install Development Dependencies
```bash
uv pip install -e ".[dev]"
```

## Code Quality

### Linting and Formatting
This project uses **ruff** for both linting and formatting.

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Lint and auto-fix
uv run ruff check --fix .
```

### Pre-commit (if configured)
```bash
uv run pre-commit run --all-files
```

## Testing

### Run All Tests
```bash
uv run pytest
```

### Run Tests with Verbosity
```bash
uv run pytest -v
```

### Run Tests with Coverage
```bash
uv run pytest --cov=pytest_pytest_configurex --cov-report=term-missing
```

### Run Specific Test
```bash
uv run pytest tests/test_pytest_configurex.py::test_name -v
```

## Project Structure

```
pytest-configurex/
├── src/
│   └── pytest_pytest_configurex/
│       ├── __init__.py
│       ├── plugin.py          # Main plugin hooks
│       ├── settings.py        # Pydantic settings classes
│       └── discovery.py       # Auto-discovery logic
├── tests/
│   ├── conftest.py
│   └── test_pytest_configurex.py
├── pyproject.toml
└── README.rst
```

## Key Implementation Details

### Environment Variable Prefix
All environment variables use the `X_` prefix:
- `X_VERBOSITY=2`
- `X_LOG_LEVEL=INFO`
- `X_MARKERS=slow`

### Configuration Priority
1. **Highest**: Pytest CLI options (e.g., `--verbosity=2`)
2. **Medium**: `.env.pytest` or custom Pydantic settings class
3. **Lowest**: Default values or pytest.ini

### Configuration File Discovery
1. Look for `.env.pytest` first
2. Fallback to `.env` if `.env.pytest` doesn't exist
3. Use defaults if neither exists

### Custom Settings Class
Users can subclass `PytestSettings` in their `conftest.py`:

```python
from pytest_configurex import PytestSettings

class MySettings(PytestSettings):
    custom_field: str = "default"

    def apply_to_pytest(self, config):
        super().apply_to_pytest(config)
        # Custom logic
```

### Fixture
The `configurex` fixture is automatically available in all tests and provides access to the settings instance.

## Testing Requirements

### All Tests Must Pass
Before committing code, ensure all tests pass:
```bash
uv run pytest
```

### Test Coverage
- Write tests for all new functionality
- Maintain high test coverage
- Use `pytester` fixture for plugin testing

### Test Categories
1. **Settings Loading**: Test .env.pytest, .env fallback, defaults
2. **Priority System**: Test CLI > env > defaults
3. **Auto-Discovery**: Test custom Settings class discovery
4. **Field Mappings**: Test all field → pytest option mappings
5. **Fixture**: Test `configurex` fixture availability and values

## Dependencies

### Core
- `pytest>=8.3.4`
- `pydantic-settings>=2.0`
- `python-dotenv`

### Development
- `ruff` - Linting and formatting
- `pytest-cov` - Coverage reporting
- `pytester` - Pytest plugin testing

## Entry Point
The plugin is registered via `pyproject.toml`:
```toml
[project.entry-points.pytest11]
configurex = "pytest_pytest_configurex.plugin"
```

## Common Commands

```bash
# Install deps
uv sync

# Format code
uv run ruff format .

# Lint code
uv run ruff check --fix .

# Run tests
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=pytest_pytest_configurex

# Build package
uv build

# Install locally for testing
uv pip install -e .
```

## Notes
- Always run tests before committing
- Ensure ruff passes on all code
- Update tests when adding new features
- Keep this document updated with any workflow changes