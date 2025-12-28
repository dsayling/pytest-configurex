# GitHub Actions Examples

Example CI/CD workflows for using pytest-configurex in GitHub Actions.

## Available Workflows

### [test-fast.yml](.github/workflows/test-fast.yml) - Fast PR Checks

**Runs on**: Pull requests and pushes to main/develop

**What it does**:
- Runs unit tests across Python 3.9-3.12
- Uses parallel execution (xdist)
- Generates coverage reports
- Fast feedback for PRs (~2-5 minutes)

**Configuration method**: Environment variables (fastest)

### [test-full.yml](.github/workflows/test-full.yml) - Complete Test Suite

**Runs on**: Nightly schedule (2 AM UTC) or manual trigger

**What it does**:
- Runs unit, integration, and E2E tests
- Sets up services (PostgreSQL, Redis)
- Comprehensive coverage across all test types
- Slower but thorough (~10-20 minutes)

**Configuration method**: Environment variables with service dependencies

### [test-matrix.yml](.github/workflows/test-matrix.yml) - Multi-OS Matrix

**Runs on**: Pushes to main and pull requests

**What it does**:
- Tests across multiple OS (Ubuntu, macOS, Windows)
- Tests across Python versions (3.9, 3.12)
- Tests different test types (unit, integration)
- Matrix excludes integration tests on Windows (example)

**Configuration method**: Environment variables with directory-based test selection

## Configuration Methods

### Method 1: Environment Variables (Recommended) ⭐

**Fastest** - No file I/O overhead

```yaml
- name: Run tests
  run: |
    export X_VERBOSITY=1
    export X_COVERAGE_ENABLED=true
    export X_COVERAGE_REPORT=xml
    export X_XDIST_NUMPROCESSES=auto
    uv run pytest
```

**Pros**:
- ✅ Fastest (no file operations)
- ✅ Explicit and clear
- ✅ Easy to see what's configured
- ✅ No file dependencies

**Cons**:
- ❌ More verbose
- ❌ Repeated across jobs

### Method 2: Test Directory Selection (Recommended for type filtering)

**Most reliable** - No marker dependencies

```yaml
- name: Run unit tests
  run: |
    export X_VERBOSITY=1
    export X_XDIST_NUMPROCESSES=auto
    uv run pytest tests/unit/

- name: Run integration tests
  run: |
    export X_VERBOSITY=1
    uv run pytest tests/integration/
```

**Pros**:
- ✅ Works without markers
- ✅ Clear separation of test types
- ✅ Easy to understand
- ✅ Directory structure is self-documenting

**Cons**:
- ❌ Requires organized test directories

### Method 3: .env Files (Optional)

**Useful** if you have complex configs committed to repo

```yaml
- name: Run tests
  run: |
    cp .env.pytest.ci .env.pytest
    uv run pytest
```

**Pros**:
- ✅ Reusable across local and CI
- ✅ Can version control configs
- ✅ Less duplication

**Cons**:
- ❌ Slower (~20ms file I/O)
- ❌ Requires committing .env files
- ❌ Need to manage multiple files

### Method 4: pytest Markers (Use with caution)

**Advanced** - Only use if tests are properly marked

```yaml
- name: Run unit tests
  run: |
    # WARNING: Only works if tests have @pytest.mark.unit decorator!
    uv run pytest -m "unit and not slow"
```

**Pros**:
- ✅ Flexible filtering
- ✅ Can combine markers
- ✅ Works across directory structure

**Cons**:
- ❌ Requires all tests to be marked
- ❌ Will run 0 tests if markers missing
- ❌ Easy to misconfigure

## Common Pitfalls

### ❌ Pitfall 1: Using markers without marking tests

```yaml
# This will run 0 tests if tests aren't marked!
export X_MARKERS="unit and not slow"
pytest
```

**Solution**: Use directory-based selection or ensure all tests are marked:

```python
# tests/unit/test_example.py
import pytest

@pytest.mark.unit
def test_something():
    assert True
```

### ❌ Pitfall 2: Not specifying test paths

```yaml
# Might run too many or too few tests
pytest
```

**Solution**: Be explicit about what to run:

```yaml
pytest tests/unit/          # Clear and explicit
pytest -k "test_user"       # Pattern matching
pytest tests/unit tests/integration  # Multiple directories
```

### ❌ Pitfall 3: Forgetting services for integration tests

```yaml
# Integration tests fail because DB is missing
pytest tests/integration/
```

**Solution**: Set up required services:

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: postgres
```

## Project Structure Assumption

These workflows assume a structure like:

```
my-project/
├── .github/
│   └── workflows/
│       ├── test-fast.yml
│       ├── test-full.yml
│       └── test-matrix.yml
├── tests/
│   ├── unit/              # Fast, isolated tests
│   ├── integration/       # Tests with external deps
│   └── e2e/              # Full system tests
├── src/
│   └── myapp/
└── pyproject.toml
```

**If your structure is different**, adjust the `pytest` paths:

```yaml
# If tests are in root:
pytest test_*.py

# If tests are nested:
pytest app/tests/

# If mixed structure:
pytest tests/ integration_tests/
```

## Customization Guide

### Change Python Versions

```yaml
matrix:
  python-version: ["3.9", "3.10", "3.11", "3.12"]  # Current
  python-version: ["3.11", "3.12"]                 # Latest only
  python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]  # Wider support
```

### Change Test Paths

```yaml
# Change this:
uv run pytest tests/unit/

# To your structure:
uv run pytest unit_tests/
uv run pytest src/tests/unit/
uv run pytest test_*.py
```

### Add More Services

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: postgres

  redis:
    image: redis:7

  rabbitmq:
    image: rabbitmq:3-management
```

### Change OS Matrix

```yaml
matrix:
  os: [ubuntu-latest, macos-latest, windows-latest]  # All
  os: [ubuntu-latest]                                # Linux only
  os: [ubuntu-latest, macos-latest]                  # No Windows
```

## Performance Tips

### 1. Use Parallel Execution

```yaml
export X_XDIST_NUMPROCESSES=auto  # Use all available cores
export X_XDIST_NUMPROCESSES=4     # Fixed number of workers
```

### 2. Cache Dependencies

```yaml
- name: Cache uv
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/pyproject.toml') }}
```

### 3. Fast Fail Strategy

```yaml
strategy:
  fail-fast: true  # Stop all jobs if one fails (faster feedback)
  fail-fast: false # Continue all jobs (see all failures)
```

### 4. Use Explicit Registration (Performance)

```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
configurex_settings_class = "myapp.test_settings.MyTestSettings"
```

This saves ~157ms per test run (see [../../benchmarks/RESULTS.md](../../benchmarks/RESULTS.md))

## Secrets and Environment Variables

### Setting Secrets

```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

### Using pytest-configurex with Secrets

```yaml
env:
  # Don't put secrets in X_ prefixed vars (they might get logged)
  DATABASE_URL: ${{ secrets.DATABASE_URL }}

  # Use X_ vars for non-sensitive config
  X_VERBOSITY: 1
  X_LOG_LEVEL: INFO
```

## Troubleshooting

### Tests not running

**Symptom**: "collected 0 items"

**Causes**:
1. Wrong test path
2. Using markers without marking tests
3. Incorrect file naming (must be `test_*.py`)

**Solutions**:
```yaml
# Be explicit about paths
pytest tests/

# Check pytest discovery
pytest --collect-only

# Use verbose mode
pytest -v
```

### Services not available

**Symptom**: Connection refused errors

**Cause**: Service not configured or not healthy

**Solution**:
```yaml
services:
  postgres:
    image: postgres:15
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

### Slow CI runs

**Symptom**: Jobs take >10 minutes

**Solutions**:
1. Use `X_XDIST_NUMPROCESSES=auto` for parallel tests
2. Split into unit (fast) and integration (slow) jobs
3. Cache dependencies
4. Use fail-fast strategy
5. Run slow tests only on main branch

## Examples in Action

See these repos using pytest-configurex in GitHub Actions:

- (Add your repo here by submitting a PR!)

## See Also

- [Task Runner Examples](../task_runners/) - Local automation with poe/just
- [Test Type Config Examples](../test_type_config/) - Unit/integration/e2e configs
- [Benchmark Results](../../benchmarks/RESULTS.md) - Performance analysis
