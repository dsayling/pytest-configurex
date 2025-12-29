# pytest-configurex Performance Report

Generated: 2025-12-29 17:04:16

## Overview

This report shows the performance characteristics of different configuration loading methods in pytest-configurex.

## Results

| Configuration Method | Mean Time (seconds) | Min Time (seconds) | Max Time (seconds) | Runs |
|---------------------|--------------------:|-------------------:|-------------------:|-----:|
| Environment Vars | 0.335347 | 0.311810 | 0.388058 | 21 |
| Env Pytest | 0.339845 | 0.311607 | 0.382994 | 21 |
| Env | 0.341115 | 0.317971 | 0.380111 | 21 |
| Cli Only | 0.343254 | 0.317662 | 0.396473 | 21 |

## Configuration Methods Tested

1. **Env Pytest**: Loading configuration from `.env.pytest` file
2. **Env**: Loading configuration from `.env` file (fallback)
3. **Environment Vars**: Loading configuration from environment variables
4. **CLI Only**: Traditional pytest command line (no configurex plugin)

## Performance Analysis

- **Overhead of pytest-configurex**: ~-0.99%
- **Absolute overhead**: ~-3.41ms per test run

- **Fastest method**: Environment Vars

## Notes

- All measurements use `pytest --collect-only` to isolate configuration loading time
- Each benchmark is run multiple times to get accurate averages
- Times shown are for a single pytest invocation with configuration loading
- Results may vary depending on system performance and load

## How to Run

To regenerate this report:

```bash
python3 performance_tests/run_performance_tests.py
```

Or run the raw benchmarks:

```bash
python3 performance_tests/measure_performance.py
```
