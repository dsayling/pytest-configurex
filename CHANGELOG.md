# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-01-XX

### Added

#### Core Features
- Environment-based pytest configuration using `.env.pytest` files
- Type-safe settings powered by pydantic-settings
- Automatic settings discovery (`.env.pytest` → `.env` → environment variables)
- `configurex` fixture for accessing settings in tests
- Support for custom settings classes by extending `PytestSettings`

#### Built-in Settings Support
- **Verbosity**: Control pytest verbosity levels (0-3)
- **Logging**: Configure log level, CLI logging, and log files
- **Test Selection**: Filter tests using pytest markers
- **Coverage**: Integration with pytest-cov (coverage reporting)
- **Parallel Execution**: Integration with pytest-xdist (parallel test runs)

#### Configuration Priority
- CLI arguments (highest priority)
- `.env.pytest` file or custom Settings class
- Default values (lowest priority)

#### Developer Tools
- Comprehensive test suite with 28+ tests
- Code quality tools: ruff for linting and formatting
- Pre-commit hooks for automated checks
- CI/CD via GitHub Actions (Python 3.10, 3.11, 3.12, 3.13)
- Type hints throughout codebase

#### Documentation
- Comprehensive USAGE.md with examples
- Multiple example configurations:
  - Environment-based config
  - Test type configurations
  - GitHub Actions integration
  - Task runner integration (poethepoet)
- README with quick start guide
- Inline code documentation

### Technical Details

#### Plugin Architecture
- Automatic discovery of Settings classes in conftest.py
- Hook into pytest configuration phase
- CLI option registration
- Settings validation and application

#### Supported Python Versions
- Python 3.10+
- Tested on CPython and PyPy

#### Dependencies
- pytest >= 8.3.4
- pydantic-settings >= 2.0
- python-dotenv >= 1.0.0

### Initial Release Notes

This is the first public release of pytest-configurex. The plugin provides a flexible, type-safe way to configure pytest using `.env` files and pydantic-settings. It's designed to:

1. Simplify test configuration management
2. Support multiple environments (dev, staging, production)
3. Enable team-wide consistent test settings
4. Provide type safety and validation for test configuration
5. Integrate seamlessly with existing pytest workflows

The plugin is production-ready for basic use cases but marked as version 0.0.1 to signal active development and potential API changes based on user feedback.

### Known Limitations

- Settings must use `X_` prefix for environment variables
- Some advanced pytest options not yet supported
- Documentation could be expanded with more examples

### Future Considerations

- Additional pytest option support
- Enhanced documentation and tutorials
- Performance optimizations for large test suites
- Integration examples with popular frameworks

---

[0.0.1]: https://github.com/dsayling/pytest-configurex/releases/tag/v0.0.1
