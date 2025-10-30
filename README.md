# pytest-configurex

[![PyPI version](https://img.shields.io/pypi/v/pytest-configurex.svg)](https://pypi.org/project/pytest-configurex)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-configurex.svg)](https://pypi.org/project/pytest-configurex)
[![Build Status](https://github.com/dsayling/pytest-configurex/actions/workflows/main.yml/badge.svg)](https://github.com/dsayling/pytest-configurex/actions/workflows/main.yml)

Configure pytest with .env files and pydantic-settings for flexible, type-safe test configuration.

---

This [pytest](https://github.com/pytest-dev/pytest) plugin was generated with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with [@hackebrot](https://github.com/hackebrot)'s [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin) template.

## Features

- **Environment-based configuration**: Load test settings from `.env.pytest` files
- **Type-safe settings**: Built on pydantic-settings for validation and type checking
- **Pytest integration**: Automatically applies settings to pytest configuration
- **Custom settings**: Extend `PytestSettings` to add your own configuration fields
- **Fixture access**: Access settings in tests via the `configurex` fixture
- **Priority-based**: CLI args override .env files, which override defaults
- **Flexible discovery**: Searches for `.env.pytest`, then `.env`, then environment variables
- **Built-in support**: Verbosity, logging, markers, coverage (pytest-cov), and parallel execution (pytest-xdist)

## Requirements

- Python 3.10+
- pytest 8.3.4+
- pydantic-settings 2.0+
- python-dotenv 1.0.0+

## Installation

You can install "pytest-configurex" via [pip](https://pypi.org/project/pip/) from [PyPI](https://pypi.org/project):

```bash
pip install pytest-configurex
```

## Usage

Quick start:

1. Create a `.env.pytest` file:

```bash
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_MARKERS=not slow
```

2. Run pytest - settings are automatically loaded:

```bash
pytest
```

3. Access settings in your tests:

```python
def test_something(configurex):
    assert configurex.verbosity == 2
    assert configurex.log_level == "INFO"
```

For detailed documentation and advanced usage, see [USAGE.md](https://github.com/dsayling/pytest-configurex/blob/main/USAGE.md).

## Contributing

Contributions are very welcome. Tests can be run with [pytest](https://github.com/pytest-dev/pytest), please ensure the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT](https://opensource.org/licenses/MIT) license, "pytest-configurex" is free and open source software.

## Issues

If you encounter any problems, please [file an issue](https://github.com/dsayling/pytest-configurex/issues) along with a detailed description.
