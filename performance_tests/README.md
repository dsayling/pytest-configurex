# Performance Tests

This directory contains performance benchmarks for pytest-configurex that measure the overhead of different configuration loading methods.

## What's Tested

The performance tests measure the time it takes to load configuration via:

1. **`.env.pytest` file** - Primary configuration method
2. **`.env` file** - Fallback configuration method
3. **Environment variables** - Direct environment variable configuration
4. **CLI only** - Traditional pytest command line (baseline, no configurex)

## Running Performance Tests

### Prerequisites

Install required dependencies:

```bash
pip install pyperf
```

Note: `psutil` is automatically installed as a dependency of `pyperf`.

### Run Full Test Suite with Reports

Generate both markdown and JSON reports:

```bash
python3 performance_tests/run_performance_tests.py
```

This will:
- Run all benchmarks with multiple iterations
- Generate `PERFORMANCE.md` with formatted results
- Generate `performance_results_summary.json` with machine-readable data
- Take several minutes to complete

### Run Raw Benchmarks Only

For more detailed pyperf output:

```bash
python3 performance_tests/measure_performance.py
```

Options:
```bash
# Save results to JSON file
python3 performance_tests/measure_performance.py -o results.json

# Run with specific number of processes
python3 performance_tests/measure_performance.py --processes 4

# Quiet mode
python3 performance_tests/measure_performance.py --quiet
```

## Understanding Results

### Output Files

- **`PERFORMANCE.md`** - Human-readable report with tables and analysis
- **`performance_results_summary.json`** - Machine-readable summary data
- **`performance_results.json`** - Full pyperf benchmark data

### Metrics

- **Mean Time**: Average time across all runs
- **Min/Max Time**: Best and worst case timing
- **Runs**: Number of benchmark iterations
- **Overhead**: Additional time compared to vanilla pytest

## Example Output

```
| Configuration Method | Mean Time (seconds) | Min Time (seconds) | Max Time (seconds) | Runs |
|---------------------|--------------------:|-------------------:|-------------------:|-----:|
| CLI Only            | 0.234561           | 0.230123           | 0.245678           | 50   |
| Env Pytest          | 0.245678           | 0.240123           | 0.256789           | 50   |
```

## Notes

- Tests use `pytest --collect-only` to isolate configuration loading time
- Multiple runs ensure statistical significance
- Results vary based on system performance
- Cold starts may show higher times
