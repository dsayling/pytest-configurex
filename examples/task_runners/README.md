# Task Runner Examples

Examples of using pytest-configurex with popular task runners.

## Available Task Runners

### [poethepoet (poe)](https://github.com/nat-n/poethepoet)
Configuration in `pyproject.toml`, Python-centric, great for Python projects.

### [just](https://github.com/casey/just)
Simple command runner with a `justfile`, language-agnostic, Make-like syntax.

## Quick Comparison

| Feature | poe (poet the poet) | just |
|---------|-------------------|------|
| **Config File** | pyproject.toml | justfile |
| **Language** | Python | Rust (any language tasks) |
| **Syntax** | TOML | Make-like |
| **Best For** | Python projects | Any project |
| **Dependencies** | pip install poethepoet | Binary install |
| **IDE Support** | VSCode, PyCharm | VSCode |

## Using poe (poethepoet)

### Installation

```bash
# With pip
pip install poethepoet

# With uv
uv add --dev poethepoet
```

### Configuration

See [pyproject.toml](./pyproject.toml) for full configuration.

Key sections:
```toml
[tool.poe.tasks]
test-unit = {cmd = "pytest", env = {X_MARKERS = "unit"}}
test-integration = {cmd = "pytest", env = {X_MARKERS = "integration"}}
```

### Usage

```bash
# Run unit tests
poe test-unit

# Run with coverage
poe test-cov

# Run all CI checks
poe ci

# List all tasks
poe
```

### Advantages

- ✅ Integrated with pyproject.toml (no extra files)
- ✅ Environment variables configured inline
- ✅ Task sequences and dependencies
- ✅ Cross-platform (pure Python)
- ✅ IDE integration (VSCode, PyCharm)

### Disadvantages

- ❌ Python-specific
- ❌ Less flexible than shell scripts
- ❌ Requires installation (extra dependency)

## Using just

### Installation

```bash
# macOS
brew install just

# Linux
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash

# Windows (with scoop)
scoop install just
```

See [just installation guide](https://github.com/casey/just#installation) for more options.

### Configuration

See [justfile](./justfile) for full configuration.

Key recipes:
```just
test-unit:
    export X_MARKERS="unit"
    uv run pytest

test-integration:
    export X_MARKERS="integration"
    uv run pytest
```

### Usage

```bash
# Run default (test-unit)
just

# Run unit tests
just test-unit

# Run with coverage
just test-cov

# Run all CI checks
just ci

# List all recipes
just --list
```

### Advantages

- ✅ Simple, Make-like syntax
- ✅ Language-agnostic
- ✅ Powerful shell integration
- ✅ Fast execution (Rust binary)
- ✅ No Python dependency

### Disadvantages

- ❌ Separate justfile needed
- ❌ Less IDE support than poe
- ❌ Requires binary installation

## Which Should You Use?

### Use **poe** if:
- Working on a Python project
- Want everything in pyproject.toml
- Need IDE task integration
- Want cross-platform without shell scripting

### Use **just** if:
- Need complex shell operations
- Want language-agnostic task runner
- Already use Make but want modern syntax
- Need very fast task execution

### Use **both** if:
- poe for Python tasks
- just for system/deployment tasks
- Best of both worlds!

## Common Recipes

### Fast Feedback Loop (TDD)

**poe:**
```toml
[tool.poe.tasks.tdd]
cmd = "ptw"  # pytest-watch
env.X_MARKERS = "unit and not slow"
env.X_VERBOSITY = "1"
```

**just:**
```just
tdd:
    export X_MARKERS="unit and not slow"
    uv run ptw
```

### CI Simulation

**poe:**
```toml
[tool.poe.tasks.ci]
sequence = ["lint", "test-unit", "test-integration"]
```

**just:**
```just
ci: lint test-unit test-integration
    @echo "✅ All CI checks passed!"
```

### Environment Switching

**poe:**
```toml
[tool.poe.tasks.test-dev]
shell = "cp .env.pytest.dev .env.pytest && pytest"
```

**just:**
```just
test-dev:
    cp .env.pytest.dev .env.pytest
    pytest
```

## Integration with pytest-configurex

Both task runners work great with pytest-configurex:

### Method 1: Environment Variables (poe)
```toml
[tool.poe.tasks.test-fast]
cmd = "pytest"
env.X_MARKERS = "unit and not slow"
env.X_VERBOSITY = "2"
env.X_XDIST_NUMPROCESSES = "auto"
```

### Method 2: Environment Variables (just)
```just
test-fast:
    #!/usr/bin/env bash
    export X_MARKERS="unit and not slow"
    export X_VERBOSITY=2
    export X_XDIST_NUMPROCESSES=auto
    pytest
```

### Method 3: .env Files
```bash
# Both poe and just
cp .env.pytest.fast .env.pytest && pytest
```

### Method 4: CLI Arguments
```bash
# Most explicit (and fastest with explicit registration)
pytest --configurex-markers="unit" --configurex-verbosity=2
```

## Example Workflows

### Development Workflow

```bash
# 1. Start development
just init-config dev  # or: cp .env.pytest.dev .env.pytest

# 2. TDD with watch mode
poe tdd  # or: just watch

# 3. Before commit
just ci  # or: poe ci
```

### CI/CD Workflow

```bash
# GitHub Actions
- run: poe ci

# GitLab CI
script:
  - just ci
```

### Multi-Environment Testing

```bash
# Development
poe test-dev  # or: just test-dev

# Staging
poe test-staging  # or: just test-staging

# Production smoke tests
poe test-prod  # or: just test-prod
```

## Tips

### poe Tips

1. **List all tasks**: Run `poe` without arguments
2. **Task help**: Add `help = "Description"` to tasks
3. **Shell tasks**: Use `shell = "command"` for complex commands
4. **Sequences**: Chain tasks with `sequence = ["task1", "task2"]`
5. **Scripts**: Call Python functions with `script = "module:function"`

### just Tips

1. **List recipes**: `just --list` or `just -l`
2. **Default recipe**: First recipe runs with `just`
3. **Private recipes**: Prefix with `_` (e.g., `_internal`)
4. **Shell choice**: Use shebang `#!/usr/bin/env bash` for bash features
5. **Variables**: `cores="auto"` allows `just test-parallel 4`

## Complete Example Project

```
my-project/
├── pyproject.toml          # Contains poe tasks
├── justfile                # Contains just recipes
├── .env.pytest             # Current config (gitignored)
├── .env.pytest.dev         # Development config
├── .env.pytest.staging     # Staging config
├── .env.pytest.production  # Production config
├── src/
│   └── myapp/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

### Quick Setup

```bash
# 1. Initialize project
uv init

# 2. Add pytest-configurex
uv add pytest-configurex

# 3. Add task runner (choose one or both)
uv add --dev poethepoet  # for poe
brew install just        # for just

# 4. Copy example configs
cp examples/task_runners/pyproject.toml .
cp examples/task_runners/justfile .

# 5. Create env files
cp .env.pytest.dev.example .env.pytest.dev
cp .env.pytest.staging.example .env.pytest.staging
cp .env.pytest.production.example .env.pytest.production

# 6. Initialize for development
cp .env.pytest.dev .env.pytest

# 7. Run tests!
poe test-unit  # or: just test-unit
```

## See Also

- [poe documentation](https://poethepoet.natn.io/)
- [just documentation](https://just.systems/)
- [pytest-configurex USAGE.md](../../USAGE.md)
- [GitHub Actions examples](../github_actions/)
