# pytest-configurex Performance Report

Generated: 2025-12-29 15:50:55

## Overview

This report shows the performance characteristics of different configuration loading methods in pytest-configurex.

## Results

| Configuration Method | Mean Time (seconds) | Min Time (seconds) | Max Time (seconds) | Runs |
|---------------------|--------------------:|-------------------:|-------------------:|-----:|
| Env Pytest | 0.320996 | 0.310732 | 0.341375 | 20 |
| Env | 0.330890 | 0.312761 | 0.421061 | 20 |
| Environment Vars | 0.334830 | 0.307198 | 0.399020 | 20 |
| Cli Only | 0.335586 | 0.308477 | 0.405773 | 20 |

## Configuration Methods Tested

1. **Env Pytest**: Loading configuration from `.env.pytest` file
2. **Env**: Loading configuration from `.env` file (fallback)
3. **Environment Vars**: Loading configuration from environment variables
4. **CLI Only**: Traditional pytest command line (no configurex plugin)

## Performance Analysis

- **Overhead of pytest-configurex**: ~-4.35%
- **Absolute overhead**: ~-14.59ms per test run

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
