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

# Timeout for subprocess calls (in seconds)
SUBPROCESS_TIMEOUT = 30


class BenchmarkContext:
    """Context for running benchmarks with pre-created test files."""
    
    def __init__(self):
        self.tmpdir = None
        self.tmpdir_path = None
    
    def setup(self):
        """Set up temporary directory and test file (non-performance critical)."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir_path = Path(self.tmpdir.name)
        
        # Create test file
        test_file = self.tmpdir_path / "test_sample.py"
        test_file.write_text("""
def test_dummy():
    assert True
""")
    
    def cleanup(self):
        """Clean up temporary directory."""
        if self.tmpdir:
            self.tmpdir.cleanup()


def measure_env_pytest_loading(context):
    """Measure time to load configuration from .env.pytest file."""
    # Create .env.pytest file
    env_file = context.tmpdir_path / ".env.pytest"
    env_file.write_text("""
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_MARKERS=not slow
X_LOG_CLI=true
X_COVERAGE_ENABLED=true
X_COVERAGE_SOURCE=src
""")
    
    # Run pytest once - pyperf will handle timing and loops
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=context.tmpdir_path,
        capture_output=True,
        env=os.environ.copy(),
        timeout=SUBPROCESS_TIMEOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pytest failed: {result.stderr.decode()}")


def measure_env_loading(context):
    """Measure time to load configuration from .env file."""
    # Create .env file (not .env.pytest)
    env_file = context.tmpdir_path / ".env"
    env_file.write_text("""
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_MARKERS=not slow
""")
    
    # Run pytest once - pyperf will handle timing and loops
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=context.tmpdir_path,
        capture_output=True,
        env=os.environ.copy(),
        timeout=SUBPROCESS_TIMEOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pytest failed: {result.stderr.decode()}")


def measure_environment_variables_loading(context):
    """Measure time to load configuration from environment variables."""
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
        cwd=context.tmpdir_path,
        capture_output=True,
        env=env,
        timeout=SUBPROCESS_TIMEOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pytest failed: {result.stderr.decode()}")


def measure_cli_only_loading(context):
    """Measure time to load configuration via traditional pytest CLI (no configurex)."""
    # Run pytest once with CLI options - pyperf will handle timing and loops
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "--collect-only", "-q",
            "-vv",
            "--log-level=INFO",
            "-m", "not slow"
        ],
        cwd=context.tmpdir_path,
        capture_output=True,
        env=os.environ.copy(),
        timeout=SUBPROCESS_TIMEOUT,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pytest failed: {result.stderr.decode()}")


def main():
    """Run all performance benchmarks."""
    runner = pyperf.Runner()
    
    # Set up context with test file (non-performance critical setup)
    context = BenchmarkContext()
    context.setup()
    
    try:
        # Run benchmarks - pyperf.Runner handles timing, loops, and statistical analysis
        runner.bench_func("load_from_env_pytest", measure_env_pytest_loading, context)
        runner.bench_func("load_from_env", measure_env_loading, context)
        runner.bench_func("load_from_environment_vars", measure_environment_variables_loading, context)
        runner.bench_func("load_from_cli_only", measure_cli_only_loading, context)
    finally:
        # Clean up
        context.cleanup()


if __name__ == "__main__":
    main()
