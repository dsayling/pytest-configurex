#!/usr/bin/env python3
"""
Performance tests for pytest-configurex.

This script measures the time it takes to load configuration via different methods:
1. Loading from .env.pytest file
2. Loading from .env file
3. Loading from environment variables
4. Traditional pytest command line (no configurex)

Uses pyperf for accurate timing measurements with multiple runs.
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pyperf


def create_test_file(tmpdir: Path) -> Path:
    """Create a minimal test file for pytest to run."""
    test_file = tmpdir / "test_sample.py"
    test_file.write_text("""
def test_dummy():
    assert True
""")
    return test_file


def measure_env_pytest_loading(loops: int) -> float:
    """Measure time to load configuration from .env.pytest file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create .env.pytest file
        env_file = tmpdir_path / ".env.pytest"
        env_file.write_text("""
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_MARKERS=not slow
X_LOG_CLI=true
X_COVERAGE_ENABLED=true
X_COVERAGE_SOURCE=src
""")
        
        # Create test file
        create_test_file(tmpdir_path)
        
        # Measure time
        t0 = pyperf.perf_counter()
        for _ in range(loops):
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                cwd=tmpdir,
                capture_output=True,
                env=os.environ.copy(),
            )
            if result.returncode != 0:
                raise RuntimeError(f"pytest failed: {result.stderr.decode()}")
        
        return pyperf.perf_counter() - t0


def measure_env_loading(loops: int) -> float:
    """Measure time to load configuration from .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create .env file (not .env.pytest)
        env_file = tmpdir_path / ".env"
        env_file.write_text("""
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_MARKERS=not slow
""")
        
        # Create test file
        create_test_file(tmpdir_path)
        
        # Measure time
        t0 = pyperf.perf_counter()
        for _ in range(loops):
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                cwd=tmpdir,
                capture_output=True,
                env=os.environ.copy(),
            )
            if result.returncode != 0:
                raise RuntimeError(f"pytest failed: {result.stderr.decode()}")
        
        return pyperf.perf_counter() - t0


def measure_environment_variables_loading(loops: int) -> float:
    """Measure time to load configuration from environment variables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test file
        create_test_file(tmpdir_path)
        
        # Set environment variables
        env = os.environ.copy()
        env.update({
            "X_VERBOSITY": "2",
            "X_LOG_LEVEL": "INFO",
            "X_MARKERS": "not slow",
        })
        
        # Measure time
        t0 = pyperf.perf_counter()
        for _ in range(loops):
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                cwd=tmpdir,
                capture_output=True,
                env=env,
            )
            if result.returncode != 0:
                raise RuntimeError(f"pytest failed: {result.stderr.decode()}")
        
        return pyperf.perf_counter() - t0


def measure_cli_only_loading(loops: int) -> float:
    """Measure time to load configuration via traditional pytest CLI (no configurex)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test file
        create_test_file(tmpdir_path)
        
        # Measure time with CLI options
        t0 = pyperf.perf_counter()
        for _ in range(loops):
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    "--collect-only", "-q",
                    "-vv",
                    "--log-level=INFO",
                    "-m", "not slow"
                ],
                cwd=tmpdir,
                capture_output=True,
                env=os.environ.copy(),
            )
            if result.returncode != 0:
                raise RuntimeError(f"pytest failed: {result.stderr.decode()}")
        
        return pyperf.perf_counter() - t0


def main():
    """Run all performance benchmarks."""
    runner = pyperf.Runner()
    
    print("Running performance tests for pytest-configurex...")
    print("This will take a few minutes...\n")
    
    # Run benchmarks
    runner.bench_time_func("load_from_env_pytest", measure_env_pytest_loading)
    runner.bench_time_func("load_from_env", measure_env_loading)
    runner.bench_time_func("load_from_environment_vars", measure_environment_variables_loading)
    runner.bench_time_func("load_from_cli_only", measure_cli_only_loading)


if __name__ == "__main__":
    main()
