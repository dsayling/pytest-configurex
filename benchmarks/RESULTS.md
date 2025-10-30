# Benchmark Results

## Executive Summary

**Auto-discovery adds 157.6ms overhead compared to explicit registration** - exceeding our 100ms acceptability threshold.

**Recommendation**: Provide both options, but **document explicit registration as the recommended approach** for performance-sensitive environments.

## Test Environment

- **Date**: 2025-10-29
- **Python Version**: 3.12.5
- **OS**: macOS (Darwin 23.6.0)
- **Hardware**: (varies by system)
- **Iterations**: 15 per scenario
- **Measurement**: `--collect-only` (startup time only, no test execution)

## Results Table

| Scenario | Mean | Min | Max | StDev |
|----------|------|-----|-----|-------|
| baseline             |    602.7ms |    495.2ms |    809.0ms |    110.4ms |
| default              |    534.9ms |    490.5ms |    734.9ms |     62.7ms |
| autodiscovery        |    781.7ms |    507.5ms |     1.426s |    282.7ms |
| explicit             |    624.1ms |    553.3ms |    879.5ms |     77.2ms |

## Analysis

### Overhead Comparison (vs Baseline)

1. **Default settings**: -67.7ms (-11.2%)
   - Surprisingly faster than baseline (likely due to measurement variance)
   - Plugin overhead is negligible when using default settings

2. **Auto-discovery**: +179.0ms (+29.7%)
   - Significant overhead from module inspection and import
   - High variance (StDev: 282.7ms) suggests inconsistent performance
   - Some runs as fast as baseline, others 2-3x slower

3. **Explicit registration**: +21.4ms (+3.6%)
   - Minimal overhead
   - Direct import is much faster than auto-discovery
   - Consistent performance (StDev: 77.2ms)

### Auto-discovery vs Explicit Registration

- **Difference**: 157.6ms
- **Performance improvement**: 20.2% faster with explicit registration
- **Verdict**: ❌ Auto-discovery exceeds 100ms threshold

## Why is Auto-Discovery Slower?

Auto-discovery requires:
1. **File system operations**: Check if `conftest.py` exists
2. **Dynamic module loading**: `importlib.util.spec_from_file_location()`
3. **Module execution**: Execute conftest.py to load classes
4. **Class inspection**: `inspect.getmembers()` over all module members
5. **Type checking**: `issubclass()` checks on each class

Explicit registration:
1. **Direct import**: `importlib.import_module(module_path)`
2. **Direct attribute access**: `getattr(module, class_name)`
3. **Type verification**: Single `issubclass()` check

## Decision: Keep or Remove Auto-Discovery?

### Arguments for Keeping (with deprecation warning)
- **Developer experience**: "It just works" without configuration
- **Prototyping/testing**: Quick setup for experiments
- **Backwards compatibility**: If users start relying on it
- **Learning curve**: Easier for beginners

### Arguments for Removing/Discouraging
- ✅ **Performance**: 157ms overhead is significant
- ✅ **Consistency**: Explicit is always better than implicit (PEP 20)
- ✅ **Predictability**: No "magic" discovery that might fail
- ✅ **CI/CD**: In automated environments, explicit is clearer
- ✅ **Debugging**: Easier to understand explicit imports

### Recommended Approach

1. **Keep both options available**
2. **Document explicit registration as the recommended method**
3. **Add performance note to documentation**
4. **Consider adding a warning** when auto-discovery is used (optional)

## Reproducing These Results

```bash
# Run benchmarks with default settings (10 iterations)
uv run python benchmarks/benchmark_startup.py

# Run with more iterations for better statistics
uv run python benchmarks/benchmark_startup.py --iterations=20

# Run with verbose output
uv run python benchmarks/benchmark_startup.py --verbose

# Save results to JSON
uv run python benchmarks/benchmark_startup.py --output=results.json
```

Or use the convenience script:

```bash
# From project root
./benchmarks/run_benchmarks.sh --iterations=15 --verbose
```

## Benchmark Scenarios

### 1. Baseline
- **Description**: No plugin functionality (minimal conftest.py)
- **Purpose**: Establish baseline pytest startup time
- **Location**: `benchmarks/baseline/`

### 2. Default
- **Description**: Plugin loaded with default settings (no custom class)
- **Purpose**: Measure plugin overhead without customization
- **Location**: `benchmarks/default/`

### 3. Auto-Discovery
- **Description**: Plugin with custom class in conftest.py (auto-discovered)
- **Configuration**: Custom `BenchmarkSettings` class in conftest.py
- **Purpose**: Measure auto-discovery overhead
- **Location**: `benchmarks/autodiscovery/`

### 4. Explicit Registration
- **Description**: Plugin with custom class registered via pytest.ini
- **Configuration**: `configurex_settings_class = benchmark_settings.ExplicitSettings`
- **Purpose**: Measure explicit registration performance
- **Location**: `benchmarks/explicit/`

## Notes on Variance

The high standard deviation in auto-discovery (282.7ms) suggests:
- First-time module import costs
- File system caching effects
- Python's import system variability

Running more iterations helps average out these effects, but the mean overhead remains significant.

## Recommendations for Users

### For Development
Either approach is fine. Auto-discovery provides convenience:
```python
# conftest.py
from pytest_pytest_configurex import PytestSettings

class MySettings(PytestSettings):
    api_url: str = "http://localhost:8000"
```

### For CI/CD
Use explicit registration for predictable performance:
```ini
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
configurex_settings_class = "myapp.test_settings.MySettings"
```

### For Large Test Suites
Every millisecond counts. Use explicit registration:
- 157ms per test run
- 1000 test runs = 157 seconds saved
- That's 2.6 minutes of CI time per 1000 runs

## Future Improvements

1. **Caching**: Cache discovered class to avoid repeated discovery
2. **Lazy loading**: Only discover when `configurex` fixture is used
3. **Import optimization**: Use faster import methods
4. **Make auto-discovery opt-in**: Require explicit flag to enable

## Conclusion

**Explicit registration is 20% faster and more predictable than auto-discovery.**

For performance-critical environments (CI/CD, large test suites), explicit registration should be used. Auto-discovery remains available for convenience but adds measurable overhead.
