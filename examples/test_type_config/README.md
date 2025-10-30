# Test Type Configuration Example

This example shows how to configure pytest differently for different types of tests (unit, integration, e2e).

## Files

- `.env.pytest.unit` - Unit tests (fast, parallel, high coverage)
- `.env.pytest.integration` - Integration tests (medium speed, external services)
- `.env.pytest.e2e` - End-to-end tests (slow, sequential, full system)

## Test Type Philosophy

### Unit Tests
- **Speed**: Very fast (< 1s per test)
- **Scope**: Single function/class
- **Dependencies**: Mocked/stubbed
- **Parallelization**: Yes (auto)
- **Coverage**: High priority
- **Markers**: `@pytest.mark.unit`

### Integration Tests
- **Speed**: Medium (1-10s per test)
- **Scope**: Multiple components
- **Dependencies**: Real services (DB, Redis, etc.)
- **Parallelization**: Limited (may need isolation)
- **Coverage**: Medium priority
- **Markers**: `@pytest.mark.integration`

### E2E Tests
- **Speed**: Slow (10s-60s+ per test)
- **Scope**: Full application flow
- **Dependencies**: Complete system
- **Parallelization**: No (sequential)
- **Coverage**: Low priority (focuses on correctness)
- **Markers**: `@pytest.mark.e2e`

## Usage

### Running Specific Test Types

```bash
# Unit tests only (fast feedback loop)
cp .env.pytest.unit .env.pytest
pytest

# Integration tests
cp .env.pytest.integration .env.pytest
pytest

# E2E tests
cp .env.pytest.e2e .env.pytest
pytest
```

### Using Makefiles

```makefile
.PHONY: test-unit test-integration test-e2e test-all

test-unit:
\tcp .env.pytest.unit .env.pytest
\tpytest

test-integration:
\tcp .env.pytest.integration .env.pytest
\tpytest

test-e2e:
\tcp .env.pytest.e2e .env.pytest
\tpytest

test-all: test-unit test-integration test-e2e
```

Then:
```bash
make test-unit
make test-integration
make test-e2e
make test-all
```

### Using Task Runners

#### poethepoet (poe)

```toml
# pyproject.toml
[tool.poe.tasks]
test-unit = "pytest -m unit"
test-integration = "pytest -m integration"
test-e2e = "pytest -m e2e"
test-fast = "pytest -m 'unit and not slow'"
test-all = ["test-unit", "test-integration", "test-e2e"]
```

With env files:
```toml
[tool.poe.tasks.test-unit]
cmd = "pytest"
env_file = ".env.pytest.unit"

[tool.poe.tasks.test-integration]
cmd = "pytest"
env_file = ".env.pytest.integration"

[tool.poe.tasks.test-e2e]
cmd = "pytest"
env_file = ".env.pytest.e2e"
```

Run with:
```bash
poe test-unit
poe test-integration
poe test-e2e
```

#### just

```just
# justfile
test-unit:
    cp .env.pytest.unit .env.pytest
    pytest

test-integration:
    cp .env.pytest.integration .env.pytest
    pytest

test-e2e:
    cp .env.pytest.e2e .env.pytest
    pytest

test-all: test-unit test-integration test-e2e
```

Run with:
```bash
just test-unit
just test-integration
just test-e2e
just test-all
```

## Configuration Comparison

| Setting | Unit | Integration | E2E |
|---------|------|-------------|-----|
| Verbosity | 2 (-vv) | 1 (-v) | 1 (-v) |
| Log Level | DEBUG | INFO | INFO |
| Markers | `unit and not slow` | `integration` | `e2e` |
| Coverage | ✅ term-missing | ✅ HTML | ❌ |
| Parallel | ✅ auto | ⚠️ limited | ❌ sequential |
| Log File | ❌ | ❌ | ✅ e2e_tests.log |

## Marking Tests

```python
import pytest

# Unit test - fast, no external dependencies
@pytest.mark.unit
def test_calculate_total():
    assert calculate_total([1, 2, 3]) == 6

# Integration test - uses database
@pytest.mark.integration
def test_user_repository(db_session):
    repo = UserRepository(db_session)
    user = repo.create(name="Alice")
    assert repo.get(user.id).name == "Alice"

# E2E test - full application flow
@pytest.mark.e2e
def test_user_signup_flow(browser):
    browser.visit("/signup")
    browser.fill("username", "alice")
    browser.fill("password", "secret")
    browser.click("submit")
    assert browser.is_text_present("Welcome, alice!")

# Mark as slow even if it's a unit test
@pytest.mark.unit
@pytest.mark.slow
def test_complex_calculation():
    assert fibonacci(100) == 354224848179261915075
```

## TDD Workflow

For test-driven development, use the pyramid:

```
     /\     E2E (few, slow)
    /  \
   /    \   Integration (some, medium)
  /      \
 /________\ Unit (many, fast)
```

### Fast Feedback Loop

```bash
# 1. Start with unit tests during development
cp .env.pytest.unit .env.pytest
pytest --watch  # or use pytest-watch

# 2. Periodically run integration tests
cp .env.pytest.integration .env.pytest
pytest

# 3. Run E2E before commits/PRs
cp .env.pytest.e2e .env.pytest
pytest
```

## CI/CD Strategy

### PR Checks (Fast)

```yaml
# .github/workflows/pr.yml
- name: Unit Tests
  run: |
    cp .env.pytest.unit .env.pytest
    pytest
```

### Nightly Builds (Comprehensive)

```yaml
# .github/workflows/nightly.yml
- name: All Tests
  run: |
    cp .env.pytest.unit .env.pytest && pytest
    cp .env.pytest.integration .env.pytest && pytest
    cp .env.pytest.e2e .env.pytest && pytest
```

### Deployment Pipeline

```yaml
deploy-staging:
  steps:
    - name: Integration Tests
      run: |
        cp .env.pytest.integration .env.pytest
        pytest

deploy-production:
  needs: deploy-staging
  steps:
    - name: Smoke Tests (E2E subset)
      run: |
        cp .env.pytest.e2e .env.pytest
        pytest -m "e2e and smoke"
```

## Best Practices

1. **Test Pyramid**: More unit tests, fewer integration tests, minimal E2E
2. **Mark Everything**: Always mark tests with appropriate markers
3. **Separate Concerns**: Don't mix test types in the same file
4. **Fast Defaults**: Make unit tests the default (`make test` = unit tests)
5. **Parallel When Possible**: Use xdist for unit tests, be careful with integration
6. **Coverage Where It Matters**: Unit tests need coverage, E2E doesn't

## Example Project Structure

```
my-project/
├── .env.pytest.unit
├── .env.pytest.integration
├── .env.pytest.e2e
├── pytest.ini
├── Makefile or justfile
├── pyproject.toml (with poe tasks)
└── tests/
    ├── unit/           # Fast, isolated tests
    │   ├── test_models.py
    │   └── test_utils.py
    ├── integration/    # Tests with real dependencies
    │   ├── test_database.py
    │   └── test_api.py
    └── e2e/           # Full system tests
        ├── test_user_flow.py
        └── test_checkout.py
```

## Common Patterns

### Skip Integration Tests Without Dependencies

```python
@pytest.mark.integration
@pytest.mark.skipif(not has_database(), reason="Database not available")
def test_with_real_db(db):
    ...
```

### Conditional E2E Tests

```python
@pytest.mark.e2e
@pytest.mark.skipif(os.getenv("CI") is None, reason="E2E only in CI")
def test_full_deployment():
    ...
```

### Combining Markers

```python
# Fast unit test
@pytest.mark.unit
def test_fast():
    ...

# Slow unit test (run less frequently)
@pytest.mark.unit
@pytest.mark.slow
def test_expensive_calculation():
    ...

# Use: X_MARKERS="unit and not slow" for fast unit tests only
```

## Troubleshooting

### Tests not running

Check markers are registered in `pytest.ini`:

```ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (medium speed, external deps)
    e2e: End-to-end tests (slow, full system)
    slow: Tests that take a long time
    smoke: Critical path tests for production
```

### Parallel tests failing

Some integration/e2e tests may not be parallel-safe:
- Shared database state
- File system conflicts
- Port collisions

Solution: Set `X_XDIST_NUMPROCESSES=1` or remove xdist config for those test types.

### Coverage too low

Unit tests should have high coverage (>80%). If low:
- Add more unit tests
- Don't rely on integration tests for coverage
- Use `pytest --cov-report=html` to find gaps
