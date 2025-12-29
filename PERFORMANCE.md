# pytest-configurex Performance Report

Generated: 2025-12-29 16:45:45

## Overview

This report shows the performance characteristics of different configuration loading methods in pytest-configurex.

## Results

| Configuration Method | Mean Time (seconds) | Min Time (seconds) | Max Time (seconds) | Runs |
|---------------------|--------------------:|-------------------:|-------------------:|-----:|
| Env Pytest | 0.291265 | 0.287391 | 0.305098 | 21 |
| Env | 0.291691 | 0.285022 | 0.297374 | 21 |
| Cli Only | 0.293319 | 0.287854 | 0.307835 | 21 |
| Environment Vars | 0.293549 | 0.286965 | 0.313807 | 21 |

## Configuration Methods Tested

1. **Env Pytest**: Loading configuration from `.env.pytest` file
2. **Env**: Loading configuration from `.env` file (fallback)
3. **Environment Vars**: Loading configuration from environment variables
4. **CLI Only**: Traditional pytest command line (no configurex plugin)

## Performance Analysis

- **Overhead of pytest-configurex**: ~-0.70%
- **Absolute overhead**: ~-2.05ms per test run

- **Fastest method**: Env Pytest

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
