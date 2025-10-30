# pytest-configurex Examples

Practical examples showing how to use pytest-configurex in different scenarios.

## Overview

| Example | Description | Best For |
|---------|-------------|----------|
| [env_based_config](env_based_config/) | Different configs for dev/staging/prod | Multi-environment deployments |
| [test_type_config](test_type_config/) | Different configs for unit/integration/e2e | Test pyramid approach |
| [github_actions](github_actions/) | CI/CD workflows | GitHub-based projects |
| [task_runners](task_runners/) | poe and just integration | Local development automation |

## Quick Start

### 1. Environment-Based Configuration

Use different settings for different environments:

```bash
cd examples/env_based_config
cp .env.pytest.dev .env.pytest
pytest  # Runs with dev settings (verbose, debug logging)
```

**When to use**: Multiple deployment environments (dev/staging/production)

**See**: [env_based_config/README.md](env_based_config/README.md)

### 2. Test Type Configuration

Use different settings for different test types:

```bash
cd examples/test_type_config
cp .env.pytest.unit .env.pytest
pytest  # Runs unit tests only, parallel, with coverage
```

**When to use**: Test pyramid with unit/integration/e2e tests

**See**: [test_type_config/README.md](test_type_config/README.md)

### 3. GitHub Actions

CI/CD workflows for GitHub:

```yaml
- name: Run unit tests
  run: |
    export X_MARKERS="unit and not slow"
    export X_XDIST_NUMPROCESSES=auto
    pytest
```

**When to use**: GitHub-based CI/CD pipelines

**See**: [github_actions/](github_actions/)

### 4. Task Runners (poe / just)

Automate testing with task runners:

```bash
# Using poe (poethepoet)
poe test-unit

# Using just
just test-unit
```

**When to use**: Local development workflows, automation

**See**: [task_runners/README.md](task_runners/README.md)

## Configuration Strategies

### Strategy 1: Environment Variables (Fastest)

Best for CI/CD and simple cases:

```bash
export X_VERBOSITY=2
export X_MARKERS="unit and not slow"
export X_XDIST_NUMPROCESSES=auto
pytest
```

**Pros**:
- ✅ No file management
- ✅ Works anywhere
- ✅ Easy to override
- ✅ Fastest (no file I/O)

**Cons**:
- ❌ Verbose for many options
- ❌ Harder to share configs
- ❌ Must set in each shell

### Strategy 2: .env Files

Best for local development:

```bash
# .env.pytest
X_VERBOSITY=2
X_MARKERS=unit and not slow
X_XDIST_NUMPROCESSES=auto
```

```bash
pytest  # Automatically loads .env.pytest
```

**Pros**:
- ✅ Shareable configs
- ✅ Easy to switch (copy different .env files)
- ✅ Gitignored for local customization

**Cons**:
- ❌ File I/O overhead (~20ms)
- ❌ Need to manage multiple files
- ❌ Can be forgotten in git

### Strategy 3: CLI Arguments

Best for explicit control:

```bash
pytest \
  --configurex-verbosity=2 \
  --configurex-markers="unit and not slow" \
  --configurex-xdist-n=auto
```

**Pros**:
- ✅ Most explicit
- ✅ Overrides everything
- ✅ Self-documenting

**Cons**:
- ❌ Very verbose
- ❌ Harder to reuse
- ❌ Long command lines

### Strategy 4: Custom Settings Class

Best for complex configurations:

```python
# conftest.py
from pytest_configurex import PytestSettings

class MyProjectSettings(PytestSettings):
    api_url: str = "http://localhost:8000"
    database_url: str = "postgresql://localhost/test"

    def apply_to_pytest(self, config):
        super().apply_to_pytest(config)
        # Custom logic here
```

```ini
# pytest.ini (for performance, use explicit registration)
[pytest]
configurex_settings_class = conftest.MyProjectSettings
```

**Pros**:
- ✅ Type-safe configuration
- ✅ Extensible and customizable
- ✅ Add custom fields
- ✅ Validation via Pydantic

**Cons**:
- ❌ More complex setup
- ❌ Auto-discovery adds ~157ms overhead (use explicit registration!)

## Recommended Patterns

### Pattern 1: Fast Feedback Loop (Development)

```bash
# .env.pytest (local development)
X_VERBOSITY=2
X_LOG_CLI=true
X_LOG_LEVEL=DEBUG
X_MARKERS=unit and not slow
X_XDIST_NUMPROCESSES=auto
X_COVERAGE_ENABLED=true
```

Use with watch mode:
```bash
pytest-watch  # or: poe tdd  # or: just watch
```

### Pattern 2: CI/CD Pipeline

```yaml
# GitHub Actions
env:
  X_VERBOSITY: 1
  X_MARKERS: "not slow"
  X_COVERAGE_ENABLED: true
  X_COVERAGE_REPORT: xml
  X_XDIST_NUMPROCESSES: auto

run: pytest
```

### Pattern 3: Multi-Environment Testing

```bash
# Makefile or justfile
test-dev:
\tcp .env.pytest.dev .env.pytest && pytest

test-staging:
\tcp .env.pytest.staging .env.pytest && pytest

test-prod:
\tcp .env.pytest.production .env.pytest && pytest
```

## Performance Considerations

See [benchmarks/RESULTS.md](../benchmarks/RESULTS.md) for detailed performance analysis.

**Key Findings**:
- **Auto-discovery**: Adds ~157ms overhead
- **Explicit registration**: Adds ~21ms overhead
- **Environment variables**: Fastest (no file I/O)
- **.env files**: Adds ~20ms overhead

**Recommendation**: Use explicit registration in pytest.ini for best performance:

```ini
[pytest]
configurex_settings_class = myapp.test_settings.MyTestSettings
```

## Common Recipes

### Recipe: Quick Test Feedback

For TDD with instant feedback:

```bash
# .env.pytest
X_MARKERS=unit and not slow
X_VERBOSITY=1
X_XDIST_NUMPROCESSES=auto
```

### Recipe: Comprehensive CI

For thorough CI testing:

```bash
# Run all test types
pytest -m unit && \
pytest -m integration && \
pytest -m e2e
```

### Recipe: Pre-Commit Hook

For fast pre-commit validation:

```bash
#!/bin/bash
# .git/hooks/pre-commit
export X_MARKERS="unit and not slow"
export X_VERBOSITY=0
pytest --exitfirst
```

### Recipe: Debugging Failing Tests

For investigating failures:

```bash
export X_VERBOSITY=3
export X_LOG_CLI=true
export X_LOG_LEVEL=DEBUG
pytest -x  # Stop on first failure
```

## Troubleshooting

### Q: Which .env file is being loaded?

Add a test:
```python
def test_config(configurex):
    print(f"Settings: {configurex}")
    print(f"CLI args: {configurex.get_cli_args()}")
```

### Q: Environment variables not working?

Check the prefix:
```bash
# ❌ Wrong
export VERBOSITY=2

# ✅ Correct
export X_VERBOSITY=2
```

### Q: Auto-discovery is slow?

Use explicit registration in pytest.ini:
```ini
[pytest]
configurex_settings_class = myapp.test_settings.MyTestSettings
```

This improves startup time by ~157ms.

### Q: How to see current configuration?

```python
def test_show_config(configurex):
    print(repr(configurex))
    # Shows: PytestSettings(verbosity=2, log_level='INFO', ...)
```

## Best Practices

1. **Commit .env.pytest.* files**: These are config templates
2. **Gitignore .env.pytest**: Let developers customize locally
3. **Use explicit registration**: For performance (pytest.ini)
4. **Environment variables in CI**: More reliable than files
5. **Task runners for automation**: poe or just for common workflows
6. **Test pyramid**: More unit tests, fewer e2e tests
7. **Parallel unit tests**: Use `X_XDIST_NUMPROCESSES=auto`
8. **Sequential integration tests**: Avoid parallel when tests have state

## See Also

- [Main Usage Guide](../USAGE.md)
- [Benchmark Results](../benchmarks/RESULTS.md)
- [GitHub Repository](https://github.com/dsayling/pytest-configurex)

## Contributing Examples

Have a useful pattern? Add it to this directory:

1. Create a new directory under `examples/`
2. Add README.md explaining the pattern
3. Include example files (.env.pytest, conftest.py, etc.)
4. Update this README with a link
5. Submit a PR!
