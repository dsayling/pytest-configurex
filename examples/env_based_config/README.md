# Environment-Based Configuration Example

This example shows how to use different pytest configurations for different environments (dev, staging, production).

## Files

- `.env.pytest.dev` - Development environment (verbose, debug logging, skip slow tests)
- `.env.pytest.staging` - Staging environment (info logging, all tests, XML coverage)
- `.env.pytest.production` - Production environment (quiet, warnings only, smoke tests only)
- `run_tests.sh` - Helper script to run tests with specific environment

## Usage

### Option 1: Copy the appropriate .env file

```bash
# For development
cp .env.pytest.dev .env.pytest
pytest

# For staging
cp .env.pytest.staging .env.pytest
pytest

# For production
cp .env.pytest.production .env.pytest
pytest
```

### Option 2: Use symbolic links

```bash
# Set up for development
ln -sf .env.pytest.dev .env.pytest
pytest

# Switch to staging
ln -sf .env.pytest.staging .env.pytest
pytest
```

### Option 3: Use environment variable to select config

```bash
# In your shell script or CI/CD
ENV=dev pytest        # Uses .env.pytest.dev
ENV=staging pytest    # Uses .env.pytest.staging
ENV=production pytest # Uses .env.pytest.production
```

This requires a small wrapper script (see `run_tests.sh`).

### Option 4: Use pytest.ini for explicit control

```ini
# pytest.ini
[pytest]
# Override which env file to use via CLI
# pytest --override-ini="env_file=.env.pytest.staging"
```

## Configuration Comparison

| Setting | Dev | Staging | Production |
|---------|-----|---------|------------|
| Verbosity | 2 (-vv) | 1 (-v) | 0 (quiet) |
| Log Level | DEBUG | INFO | WARNING |
| Log to Console | ✅ | ✅ | ❌ |
| Markers | `not slow` | (all) | `smoke` |
| Coverage | ✅ term-missing | ✅ XML | ❌ |

## CI/CD Integration

### GitHub Actions

```yaml
- name: Run tests in staging mode
  run: |
    cp .env.pytest.staging .env.pytest
    pytest
```

### GitLab CI

```yaml
test:staging:
  script:
    - cp .env.pytest.staging .env.pytest
    - pytest
```

### Using with poe (poethepoet)

```toml
[tool.poe.tasks]
test-dev = {cmd = "pytest", env = {PYTEST_ENV_FILE = ".env.pytest.dev"}}
test-staging = {cmd = "pytest", env = {PYTEST_ENV_FILE = ".env.pytest.staging"}}
test-prod = {cmd = "pytest", env = {PYTEST_ENV_FILE = ".env.pytest.production"}}
```

Then run:
```bash
poe test-dev
poe test-staging
poe test-prod
```

## Best Practices

1. **Commit the .env.pytest.* files** - They're configuration, not secrets
2. **Don't commit .env.pytest** - Add it to .gitignore, let users choose
3. **Use .env.pytest.example** - Show all available options
4. **Environment-specific settings** - Keep env-specific values in these files
5. **Secrets in environment variables** - Use actual env vars for API keys, etc.

## Example Project Structure

```
my-project/
├── .env.pytest.dev
├── .env.pytest.staging
├── .env.pytest.production
├── .env.pytest         # Gitignored, symlink or copy of above
├── .gitignore          # Contains .env.pytest
├── pytest.ini
├── conftest.py
├── src/
│   └── myapp/
└── tests/
    ├── test_unit.py
    ├── test_integration.py (marked with @pytest.mark.slow)
    └── test_smoke.py (marked with @pytest.mark.smoke)
```

## Troubleshooting

### Wrong config being loaded

Make sure you:
1. Have copied/linked the correct .env.pytest file
2. Don't have conflicting environment variables set
3. Check `pytest --help` to see which configurex options are active

### Environment variables not working

Remember the `X_` prefix:
```bash
# ❌ Wrong
export VERBOSITY=2

# ✅ Correct
export X_VERBOSITY=2
```

### Markers not filtering correctly

Make sure tests are marked:
```python
import pytest

@pytest.mark.slow
def test_slow_operation():
    ...

@pytest.mark.smoke
def test_critical_path():
    ...
```

Then use `X_MARKERS=slow` or `X_MARKERS="not slow"` in your .env.pytest file.
