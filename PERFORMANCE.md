# pytest-configurex Performance Report

Generated: 2025-12-29 16:11:02

## Overview

This report shows the performance characteristics of different configuration loading methods in pytest-configurex.

## Results

| Configuration Method | Mean Time (seconds) | Min Time (seconds) | Max Time (seconds) | Runs |
|---------------------|--------------------:|-------------------:|-------------------:|-----:|
| Environment Vars | 0.301756 | 0.296864 | 0.307579 | 20 |
| Env | 0.301972 | 0.298379 | 0.310919 | 20 |
| Env Pytest | 0.303883 | 0.296536 | 0.321595 | 20 |
| Cli Only | 0.304178 | 0.298393 | 0.311322 | 20 |

## Configuration Methods Tested

1. **Env Pytest**: Loading configuration from `.env.pytest` file
2. **Env**: Loading configuration from `.env` file (fallback)
3. **Environment Vars**: Loading configuration from environment variables
4. **CLI Only**: Traditional pytest command line (no configurex plugin)

## Performance Analysis

- **Overhead of pytest-configurex**: ~-0.10%
- **Absolute overhead**: ~-0.29ms per test run

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
