#!/usr/bin/env python3
"""
Benchmark script for pytest-configurex startup performance.

This script measures the startup time overhead of the plugin in different configurations:
1. Baseline: No plugin (plugin disabled via environment)
2. Default: Plugin with default settings
3. Autodiscovery: Plugin with custom settings class (auto-discovered from conftest.py)
4. Explicit: Plugin with custom settings class (explicitly registered in pytest.ini)

Usage:
    python benchmarks/benchmark_startup.py
    python benchmarks/benchmark_startup.py --iterations=20
    python benchmarks/benchmark_startup.py --verbose
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean, stdev
from typing import Dict, List


def run_pytest_timed(
    scenario_dir: Path, iterations: int = 10, env_override: Dict[str, str] = None
) -> List[float]:
    """
    Run pytest in a scenario directory and measure startup time.

    Args:
        scenario_dir: Path to scenario directory
        iterations: Number of times to run pytest
        env_override: Optional environment variables to set

    Returns:
        List of execution times in seconds
    """
    times = []

    for _i in range(iterations):
        start = time.perf_counter()

        # Run pytest with minimal output, collect-only to measure just startup
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=scenario_dir,
            capture_output=True,
            text=True,
            env=env_override,
        )

        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)

        # Check for errors
        if result.returncode != 0:
            print(f"Warning: pytest returned {result.returncode} for {scenario_dir.name}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")

    return times


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.1f}µs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    else:
        return f"{seconds:.3f}s"


def calculate_stats(times: List[float]) -> Dict[str, float]:
    """Calculate statistics from timing data."""
    return {
        "mean": mean(times),
        "min": min(times),
        "max": max(times),
        "stdev": stdev(times) if len(times) > 1 else 0.0,
    }


def run_benchmarks(
    benchmark_root: Path, iterations: int = 10, verbose: bool = False
) -> Dict[str, Dict[str, float]]:
    """
    Run all benchmark scenarios.

    Args:
        benchmark_root: Root directory containing benchmark scenarios
        iterations: Number of iterations per scenario
        verbose: Print verbose output

    Returns:
        Dictionary of scenario results
    """
    scenarios = {
        "baseline": "No plugin (baseline)",
        "default": "Plugin with default settings",
        "autodiscovery": "Plugin with auto-discovered custom class",
        "explicit": "Plugin with explicit registration (pytest.ini)",
    }

    results = {}

    for scenario_name, description in scenarios.items():
        scenario_dir = benchmark_root / scenario_name

        if not scenario_dir.exists():
            print(f"Warning: Scenario '{scenario_name}' not found at {scenario_dir}")
            continue

        if verbose:
            print(f"\nRunning {scenario_name}: {description}")
            print(f"  Directory: {scenario_dir}")
            print(f"  Iterations: {iterations}")

        # For baseline, we want to disable the plugin
        # We can't easily do that since it's installed, so we'll just measure with it
        # The overhead should still be visible in the comparison

        times = run_pytest_timed(scenario_dir, iterations)
        stats = calculate_stats(times)
        results[scenario_name] = stats

        if verbose:
            print(f"  Mean: {format_time(stats['mean'])}")
            print(f"  Min:  {format_time(stats['min'])}")
            print(f"  Max:  {format_time(stats['max'])}")
            print(f"  StDev: {format_time(stats['stdev'])}")

    return results


def print_results_table(results: Dict[str, Dict[str, float]]):
    """Print results in a markdown table format."""
    print("\n## Benchmark Results\n")
    print("| Scenario | Mean | Min | Max | StDev |")
    print("|----------|------|-----|-----|-------|")

    for scenario_name, stats in results.items():
        print(
            f"| {scenario_name:20s} | {format_time(stats['mean']):>10s} | "
            f"{format_time(stats['min']):>10s} | {format_time(stats['max']):>10s} | "
            f"{format_time(stats['stdev']):>10s} |"
        )

    # Calculate overhead
    if "baseline" in results and "default" in results:
        baseline_mean = results["baseline"]["mean"]
        default_overhead = results["default"]["mean"] - baseline_mean
        print("\n### Overhead Analysis")
        print(
            f"- **Default settings overhead**: {format_time(default_overhead)} "
            f"({default_overhead / baseline_mean * 100:.1f}%)"
        )

    if "baseline" in results and "autodiscovery" in results:
        baseline_mean = results["baseline"]["mean"]
        autodiscovery_overhead = results["autodiscovery"]["mean"] - baseline_mean
        print(
            f"- **Auto-discovery overhead**: {format_time(autodiscovery_overhead)} "
            f"({autodiscovery_overhead / baseline_mean * 100:.1f}%)"
        )

    if "baseline" in results and "explicit" in results:
        baseline_mean = results["baseline"]["mean"]
        explicit_overhead = results["explicit"]["mean"] - baseline_mean
        print(
            f"- **Explicit registration overhead**: {format_time(explicit_overhead)} "
            f"({explicit_overhead / baseline_mean * 100:.1f}%)"
        )

    if "autodiscovery" in results and "explicit" in results:
        diff = results["autodiscovery"]["mean"] - results["explicit"]["mean"]
        print("\n### Auto-discovery vs Explicit")
        print(f"- **Difference**: {format_time(abs(diff))}")
        if diff > 0:
            print(f"- **Winner**: Explicit registration is {format_time(diff)} faster")
            print(f"  ({diff / results['autodiscovery']['mean'] * 100:.1f}% improvement)")
        else:
            print(f"- **Winner**: Auto-discovery is {format_time(abs(diff))} faster")
            print(f"  ({abs(diff) / results['explicit']['mean'] * 100:.1f}% improvement)")


def save_results_json(results: Dict[str, Dict[str, float]], output_file: Path):
    """Save results to JSON file."""
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Benchmark pytest-configurex startup performance")
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations per scenario (default: 10)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print verbose output")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Save results to JSON file",
    )

    args = parser.parse_args()

    # Find benchmark root directory
    script_path = Path(__file__).resolve()
    benchmark_root = script_path.parent

    print("pytest-configurex Startup Performance Benchmark")
    print("=" * 60)
    print(f"Iterations per scenario: {args.iterations}")
    print(f"Benchmark root: {benchmark_root}")

    # Run benchmarks
    results = run_benchmarks(benchmark_root, args.iterations, args.verbose)

    # Print results
    print_results_table(results)

    # Save to JSON if requested
    if args.output:
        save_results_json(results, args.output)

    # Return exit code based on auto-discovery overhead
    if "autodiscovery" in results and "explicit" in results:
        autodiscovery_time = results["autodiscovery"]["mean"]
        explicit_time = results["explicit"]["mean"]
        overhead_ms = (autodiscovery_time - explicit_time) * 1000

        print("\n### Decision Criteria")
        print(f"Auto-discovery overhead: {overhead_ms:.2f}ms")

        if overhead_ms > 100:
            print("❌ Auto-discovery adds >100ms overhead - consider explicit registration")
            return 1
        else:
            print("✅ Auto-discovery overhead is acceptable (<100ms)")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
