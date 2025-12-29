#!/usr/bin/env python3
"""
Performance tests for pytest-configurex.

This script measures the time it takes to load configuration via different methods:
1. Loading from .env.pytest file
2. Loading from .env file
3. Loading from environment variables
4. Traditional pytest command line (no configurex)

Uses pyperf's bench_func with proper setup/teardown isolation.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pyperf

# Timeout for subprocess calls (in seconds)
SUBPROCESS_TIMEOUT = 30


def benchmark_env_pytest_loading():
    """Benchmark loading configuration from .env.pytest file."""
    # Setup (not timed): Create temporary directory, test file, and .env.pytest
    tmpdir = tempfile.TemporaryDirectory()
    tmpdir_path = Path(tmpdir.name)
    
    test_file = tmpdir_path / "test_sample.py"
    test_file.write_text("""
def test_dummy():
    assert True
""")
    
    env_file = tmpdir_path / ".env.pytest"
    env_file.write_text("""
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_MARKERS=not slow
X_LOG_CLI=true
X_COVERAGE_ENABLED=true
X_COVERAGE_SOURCE=src
""")
    
    def run_pytest():
        """This function is timed - only pytest execution."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=tmpdir_path,
            capture_output=True,
            env=os.environ.copy(),
            timeout=SUBPROCESS_TIMEOUT,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pytest failed: {result.stderr.decode()}")
    
    return run_pytest, tmpdir


def benchmark_env_loading():
    """Benchmark loading configuration from .env file."""
    # Setup (not timed): Create temporary directory, test file, and .env
    tmpdir = tempfile.TemporaryDirectory()
    tmpdir_path = Path(tmpdir.name)
    
    test_file = tmpdir_path / "test_sample.py"
    test_file.write_text("""
def test_dummy():
    assert True
""")
    
    env_file = tmpdir_path / ".env"
    env_file.write_text("""
X_VERBOSITY=2
X_LOG_LEVEL=INFO
X_MARKERS=not slow
""")
    
    def run_pytest():
        """This function is timed - only pytest execution."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=tmpdir_path,
            capture_output=True,
            env=os.environ.copy(),
            timeout=SUBPROCESS_TIMEOUT,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pytest failed: {result.stderr.decode()}")
    
    return run_pytest, tmpdir


def benchmark_environment_variables_loading():
    """Benchmark loading configuration from environment variables."""
    # Setup (not timed): Create temporary directory, test file, and env vars
    tmpdir = tempfile.TemporaryDirectory()
    tmpdir_path = Path(tmpdir.name)
    
    test_file = tmpdir_path / "test_sample.py"
    test_file.write_text("""
def test_dummy():
    assert True
""")
    
    env = os.environ.copy()
    env.update({
        "X_VERBOSITY": "2",
        "X_LOG_LEVEL": "INFO",
        "X_MARKERS": "not slow",
    })
    
    def run_pytest():
        """This function is timed - only pytest execution."""
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=tmpdir_path,
            capture_output=True,
            env=env,
            timeout=SUBPROCESS_TIMEOUT,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pytest failed: {result.stderr.decode()}")
    
    return run_pytest, tmpdir


def benchmark_cli_only_loading():
    """Benchmark traditional pytest CLI (no configurex)."""
    # Setup (not timed): Create temporary directory and test file
    tmpdir = tempfile.TemporaryDirectory()
    tmpdir_path = Path(tmpdir.name)
    
    test_file = tmpdir_path / "test_sample.py"
    test_file.write_text("""
def test_dummy():
    assert True
""")
    
    def run_pytest():
        """This function is timed - only pytest execution."""
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "--collect-only", "-q",
                "-vv",
                "--log-level=INFO",
                "-m", "not slow"
            ],
            cwd=tmpdir_path,
            capture_output=True,
            env=os.environ.copy(),
            timeout=SUBPROCESS_TIMEOUT,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pytest failed: {result.stderr.decode()}")
    
    return run_pytest, tmpdir


def main():
    """Run all performance benchmarks."""
    runner = pyperf.Runner()
    
    # Benchmark 1: .env.pytest loading
    run_pytest_1, tmpdir_1 = benchmark_env_pytest_loading()
    try:
        runner.bench_func("load_from_env_pytest", run_pytest_1)
    finally:
        tmpdir_1.cleanup()
    
    # Benchmark 2: .env loading
    run_pytest_2, tmpdir_2 = benchmark_env_loading()
    try:
        runner.bench_func("load_from_env", run_pytest_2)
    finally:
        tmpdir_2.cleanup()
    
    # Benchmark 3: environment variables loading
    run_pytest_3, tmpdir_3 = benchmark_environment_variables_loading()
    try:
        runner.bench_func("load_from_environment_vars", run_pytest_3)
    finally:
        tmpdir_3.cleanup()
    
    # Benchmark 4: CLI only (traditional pytest)
    run_pytest_4, tmpdir_4 = benchmark_cli_only_loading()
    try:
        runner.bench_func("load_from_cli_only", run_pytest_4)
    finally:
        tmpdir_4.cleanup()


if __name__ == "__main__":
    main()
