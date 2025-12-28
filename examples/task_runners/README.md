# Task Runner Examples

Simple examples of running pytest with task runners.

## poethepoet (poe)

Add to your `pyproject.toml`:

```toml
# Basic test commands
[tool.poe.tasks.test]
cmd = "pytest"
help = "Run all tests"

[tool.poe.tasks.test-unit]
cmd = "pytest"
env.X_MARKERS = "unit"
help = "Run unit tests only"

[tool.poe.tasks.test-integration]
cmd = "pytest"
env.X_MARKERS = "integration"
help = "Run integration tests"

[tool.poe.tasks.test-cov]
cmd = "pytest"
env.X_COVERAGE_ENABLED = "true"
help = "Run tests with coverage"

# Parallel execution
[tool.poe.tasks.test-parallel]
cmd = "pytest"
env.X_XDIST_NUMPROCESSES = "auto"
help = "Run tests in parallel"

[tool.poe.tasks.test-unit-parallel]
cmd = "pytest"
env.X_MARKERS = "unit"
env.X_XDIST_NUMPROCESSES = "auto"
help = "Run unit tests in parallel"

# Fast feedback for TDD
[tool.poe.tasks.test-fast]
cmd = "pytest"
env.X_MARKERS = "unit and not slow"
env.X_VERBOSITY = "2"
help = "Fast tests for TDD"

[tool.poe.tasks.watch]
cmd = "ptw"
env.X_MARKERS = "unit and not slow"
help = "Watch mode for TDD"

# Composed tasks (using ref to call other tasks)
[tool.poe.tasks.test-all]
sequence = ["test-unit", "test-integration"]
help = "Run all test suites"

[tool.poe.tasks.test-quick]
ref = "test-unit-parallel"
help = "Quick parallel unit tests"

[tool.poe.tasks.ci]
sequence = ["lint", "test-all", "test-cov"]
help = "Full CI test suite"

# Environment switching
[tool.poe.tasks.test-staging]
shell = "cp .env.pytest.staging .env.pytest && pytest"
help = "Run tests with staging config"

# Maximum verbosity for debugging
[tool.poe.tasks.test-verbose]
cmd = "pytest"
env.X_VERBOSITY = "3"
env.X_LOG_LEVEL = "DEBUG"
help = "Run tests with maximum verbosity"
```

Run:
```bash
# List all available tasks with help text
poe

# Run specific tasks
poe test-unit              # Unit tests only
poe test-quick             # Fast parallel unit tests (refs test-unit-parallel)
poe test-all               # Runs unit + integration (sequence)
poe ci                     # Full CI suite: lint + test-all + coverage
poe watch                  # TDD watch mode
poe test-verbose           # Maximum verbosity
```

## just

Create a `justfile`:

```just
# Run all tests
test:
    pytest

# Run unit tests only
test-unit:
    export X_MARKERS="unit"
    pytest

# Run integration tests
test-integration:
    export X_MARKERS="integration"
    pytest

# Run with coverage
test-cov:
    export X_COVERAGE_ENABLED=true
    pytest

# Run tests in parallel
test-parallel:
    export X_XDIST_NUMPROCESSES=auto
    pytest

# Fast TDD mode
test-fast:
    #!/usr/bin/env bash
    export X_MARKERS="unit and not slow"
    export X_VERBOSITY=2
    pytest
```

Run:
```bash
just test-unit
just test-cov
just test-fast
```

## Common Patterns

### TDD with watch mode

**poe:**
```toml
[tool.poe.tasks.watch]
cmd = "ptw"
env.X_MARKERS = "unit and not slow"
```

**just:**
```just
watch:
    export X_MARKERS="unit and not slow"
    ptw
```

### CI checks

**poe:**
```toml
[tool.poe.tasks.ci]
sequence = ["lint", "test"]
```

**just:**
```just
ci: lint test
    @echo "✅ All checks passed"
```

### Environment switching

**poe:**
```toml
[tool.poe.tasks.test-staging]
shell = "cp .env.pytest.staging .env.pytest && pytest"
```

**just:**
```just
test-staging:
    cp .env.pytest.staging .env.pytest
    pytest
```
