# pytest-configurex Benchmarks

Performance benchmarks for measuring plugin startup overhead.

## Quick Start

```bash
# From project root
./benchmarks/run_benchmarks.sh
```

Or with Python directly:

```bash
uv run python benchmarks/benchmark_startup.py --iterations=15 --verbose
```

## What's Being Measured

These benchmarks measure **pytest startup time** (collection phase) with different plugin configurations:

1. **Baseline**: Minimal pytest without custom settings
2. **Default**: Plugin with default PytestSettings
3. **Auto-discovery**: Plugin auto-discovers custom class from conftest.py
4. **Explicit**: Plugin loads custom class from pytest.ini configuration

## Results Summary

See [RESULTS.md](RESULTS.md) for detailed analysis.

**TL;DR**: Explicit registration is ~157ms faster than auto-discovery (20% improvement).

## Directory Structure

```
benchmarks/
├── README.md                    # This file
├── RESULTS.md                   # Detailed benchmark results
├── benchmark_startup.py         # Main benchmark script
├── run_benchmarks.sh           # Convenience wrapper script
├── baseline/                    # Scenario 1: No custom settings
│   ├── conftest.py
│   └── test_simple.py
├── default/                     # Scenario 2: Default settings
│   └── test_simple.py
├── autodiscovery/              # Scenario 3: Auto-discovered class
│   ├── conftest.py
│   └── test_simple.py
└── explicit/                    # Scenario 4: Explicit registration
    ├── benchmark_settings.py
    ├── pytest.ini
    └── test_simple.py
```

## Running Benchmarks

### Basic Usage

```bash
# Default: 10 iterations
uv run python benchmarks/benchmark_startup.py

# More iterations for better accuracy
uv run python benchmarks/benchmark_startup.py --iterations=20

# Verbose output (shows per-scenario details)
uv run python benchmarks/benchmark_startup.py --verbose

# Save results to JSON
uv run python benchmarks/benchmark_startup.py --output=results.json
```

### Using the Wrapper Script

```bash
# Simple run
./benchmarks/run_benchmarks.sh

# With arguments
./benchmarks/run_benchmarks.sh --iterations=20 --verbose
```

## Interpreting Results

The benchmark outputs a markdown table with timing data:

```
| Scenario      | Mean    | Min     | Max     | StDev   |
|---------------|---------|---------|---------|---------|
| baseline      | 602.7ms | 495.2ms | 809.0ms | 110.4ms |
| autodiscovery | 781.7ms | 507.5ms | 1.426s  | 282.7ms |
| explicit      | 624.1ms | 553.3ms | 879.5ms | 77.2ms  |
```

### Key Metrics

- **Mean**: Average time across all iterations
- **Min**: Fastest run (best case)
- **Max**: Slowest run (worst case)
- **StDev**: Standard deviation (consistency indicator)

Lower is better. Low StDev = consistent performance.

### Overhead Analysis

The script calculates overhead vs baseline:

```
Auto-discovery overhead: 179.0ms (29.7%)
Explicit registration overhead: 21.4ms (3.6%)
```

And compares the two approaches:

```
Auto-discovery vs Explicit
Difference: 157.6ms
Winner: Explicit registration is 157.6ms faster (20.2% improvement)
```

### Decision Criteria

The script returns exit code 1 if auto-discovery overhead exceeds 100ms:

```
### Decision Criteria
Auto-discovery overhead: 157.62ms
❌ Auto-discovery adds >100ms overhead - consider explicit registration
```

## Adding New Scenarios

To add a new benchmark scenario:

1. Create a new directory under `benchmarks/`
2. Add test files and configuration
3. Run the benchmark script (it auto-discovers scenarios)

Example:

```bash
mkdir benchmarks/cached_discovery
# Add your test files
uv run python benchmarks/benchmark_startup.py
```

## Performance Tips

### For Accurate Results

1. **Close other applications** to minimize system noise
2. **Run multiple iterations** (--iterations=20 or more)
3. **Run multiple times** and compare results for consistency
4. **Warm up the system** by running once before timing

### For Fair Comparison

- All scenarios use the same test count (3 tests per scenario)
- Tests use `--collect-only` to measure startup, not execution
- Same environment for all scenarios (same Python, packages, etc.)

## Troubleshooting

### ImportError in explicit scenario

If you see import errors in the explicit scenario:

```bash
# Make sure you're running from project root
cd /path/to/pytest-configurex
uv run python benchmarks/benchmark_startup.py
```

### Inconsistent Results

High variance is normal due to:
- File system caching
- Python import caching
- OS scheduling
- Background processes

Run more iterations to get a stable average:

```bash
uv run python benchmarks/benchmark_startup.py --iterations=30
```

### Baseline Seems Slow

The "baseline" includes:
- Python startup
- pytest collection
- The plugin (it's installed!)

For true baseline, you'd need to uninstall the plugin, which we don't do here. Instead, we compare relative overhead between scenarios.

## What These Numbers Mean

### 157ms overhead seems small?

Consider:
- This is **per test run**, not per test
- Running tests 100 times = 15.7 seconds
- Running tests 1000 times in CI = 2.6 minutes
- For large test suites with frequent runs, it adds up

### When to Care

**Care about performance if:**
- Running tests frequently in watch mode
- Large CI/CD pipeline with many test runs
- Tight feedback loops (TDD)
- Slow test environments already

**Don't care if:**
- Running tests infrequently
- Test execution time >> startup time
- Developer convenience > raw speed
- Small test suite

## Contributing

To improve the benchmarks:

1. Add more realistic scenarios
2. Test with larger conftest.py files
3. Measure memory usage
4. Profile with cProfile for hotspots
5. Test on different OS/Python versions

## See Also

- [RESULTS.md](RESULTS.md) - Detailed analysis and recommendations
- [../USAGE.md](../USAGE.md) - Plugin usage documentation
- [pytest benchmarking guide](https://docs.pytest.org/en/stable/how-to/benchmarking.html)
