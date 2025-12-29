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

import os
import subprocess
import sys
import tempfile
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


def measure_env_pytest_loading():
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
        
        # Run pytest once - pyperf will handle timing and loops
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=tmpdir,
            capture_output=True,
            env=os.environ.copy(),
        )
        if result.returncode != 0:
            raise RuntimeError(f"pytest failed: {result.stderr.decode()}")


def measure_env_loading():
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
        
        # Run pytest once - pyperf will handle timing and loops
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=tmpdir,
            capture_output=True,
            env=os.environ.copy(),
        )
        if result.returncode != 0:
            raise RuntimeError(f"pytest failed: {result.stderr.decode()}")


def measure_environment_variables_loading():
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
        
        # Run pytest once - pyperf will handle timing and loops
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=tmpdir,
            capture_output=True,
            env=env,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pytest failed: {result.stderr.decode()}")


def measure_cli_only_loading():
    """Measure time to load configuration via traditional pytest CLI (no configurex)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test file
        create_test_file(tmpdir_path)
        
        # Run pytest once with CLI options - pyperf will handle timing and loops
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


def main():
    """Run all performance benchmarks."""
    runner = pyperf.Runner()
    
    # Run benchmarks - pyperf.Runner handles timing, loops, and statistical analysis
    runner.bench_func("load_from_env_pytest", measure_env_pytest_loading)
    runner.bench_func("load_from_env", measure_env_loading)
    runner.bench_func("load_from_environment_vars", measure_environment_variables_loading)
    runner.bench_func("load_from_cli_only", measure_cli_only_loading)


if __name__ == "__main__":
    main()
