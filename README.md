# pytest-configurex

[![Build Status](https://github.com/dsayling/pytest-configurex/actions/workflows/main.yml/badge.svg)](https://github.com/dsayling/pytest-configurex/actions/workflows/main.yml)
[![Python versions](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

Configure pytest with .env files and pydantic-settings for flexible, type-safe test configuration.

---

This [pytest](https://github.com/pytest-dev/pytest) plugin was generated with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with [@hackebrot](https://github.com/hackebrot)'s [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin) template.

## Features

- **Environment-based configuration**: Load test settings from `.env.pytest` files
- **Type-safe settings**: Built on pydantic-settings for validation and type checking
- **Pytest integration**: Automatically applies settings to pytest configuration
- **Custom settings**: Extend `PytestSettings` to add your own configuration fields
- **Fixture access**: Access settings in tests via the `configurex` fixture
- **Priority-based**: Standard pytest CLI args override .env files, which override defaults
- **Flexible discovery**: Searches for `.env.pytest`, then `.env`, then environment variables
- **Built-in support**: Verbosity, logging, markers, coverage (pytest-cov), and parallel execution (pytest-xdist)
- **No custom CLI**: Uses standard pytest options (`-vv`, `--log-level`, `-m`, etc.) - no new options to learn

## Requirements

- Python 3.10+
- pytest 8.3.4+
- pydantic-settings 2.0+
- python-dotenv 1.0.0+

## Installation

> **Note**: This package has not yet been published to PyPI.

For now, you can install "pytest-configurex" directly from the GitHub repository:

```bash
# Using pip
pip install git+https://github.com/dsayling/pytest-configurex.git

# Using uv
uv add git+https://github.com/dsayling/pytest-configurex.git
```

Or for development, clone the repository and install in editable mode:

```bash
git clone https://github.com/dsayling/pytest-configurex.git
cd pytest-configurex
pip install -e .
```

## Usage

Quick start:

1. Create a `.env.pytest` file with default settings:

```bash
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_MARKERS=not slow
```

2. Run pytest - settings are automatically applied:

```bash
pytest  # Uses settings from .env.pytest
```

3. Override settings with standard pytest CLI options:

```bash
pytest -vv                    # Override verbosity
pytest --log-level=DEBUG      # Override log level
pytest -m unit                # Override markers
```

4. Access settings in your tests:

```python
def test_something(configurex):
    assert configurex.verbosity == 2
    assert configurex.log_level == "INFO"
```

**Priority order:** Standard pytest CLI > `.env.pytest` > defaults

For detailed documentation and advanced usage, see [USAGE.md](https://github.com/dsayling/pytest-configurex/blob/main/USAGE.md).

## Performance

pytest-configurex is designed to have minimal overhead. Performance benchmarks show:

- **Configuration loading time**: ~321ms per test run (using `.env.pytest`)
- **Overhead vs vanilla pytest**: Negligible (~-4.4% in benchmarks, within margin of error)
- **Fastest method**: `.env.pytest` file

See [PERFORMANCE.md](https://github.com/dsayling/pytest-configurex/blob/main/PERFORMANCE.md) for detailed benchmark results.

### Running Performance Tests

To run performance benchmarks on your system:

```bash
# Install performance testing dependencies
pip install pyperf

# Run benchmarks and generate reports
python3 performance_tests/run_performance_tests.py
```

This generates:
- `PERFORMANCE.md` - Human-readable report with analysis
- `performance_results_summary.json` - Machine-readable summary data

## Contributing

Contributions are very welcome. Tests can be run with [pytest](https://github.com/pytest-dev/pytest), please ensure the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license, "pytest-configurex" is free and open source software.

## Issues

If you encounter any problems, please [file an issue](https://github.com/dsayling/pytest-configurex/issues) along with a detailed description.
