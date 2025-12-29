# pytest-configurex Performance Report

Generated: 2025-12-29 16:53:22

## Overview

This report shows the performance characteristics of different configuration loading methods in pytest-configurex.

## Results

| Configuration Method | Mean Time (seconds) | Min Time (seconds) | Max Time (seconds) | Runs |
|---------------------|--------------------:|-------------------:|-------------------:|-----:|
| Environment Vars | 0.291917 | 0.286151 | 0.298007 | 21 |
| Env Pytest | 0.292231 | 0.287700 | 0.299170 | 21 |
| Env | 0.292843 | 0.287331 | 0.301084 | 21 |
| Cli Only | 0.293464 | 0.286739 | 0.304688 | 21 |

## Configuration Methods Tested

1. **Env Pytest**: Loading configuration from `.env.pytest` file
2. **Env**: Loading configuration from `.env` file (fallback)
3. **Environment Vars**: Loading configuration from environment variables
4. **CLI Only**: Traditional pytest command line (no configurex plugin)

## Performance Analysis

- **Overhead of pytest-configurex**: ~-0.42%
- **Absolute overhead**: ~-1.23ms per test run

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
