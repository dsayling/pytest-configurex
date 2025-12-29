#!/usr/bin/env python3
"""
Run performance tests and generate reports in both markdown and JSON formats.

This script:
1. Runs the performance benchmarks using pyperf
2. Parses the results
3. Generates a markdown report
4. Generates a JSON report
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_performance_benchmarks():
    """Run performance benchmarks and return results as JSON."""
    print("Running performance benchmarks...")
    print("This may take several minutes...\n")
    
    # Run benchmarks and save to JSON
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).parent / "measure_performance.py"),
            "-o", "performance_results.json",
            "--quiet"
        ],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        print(f"Error running benchmarks: {result.stderr}")
        sys.exit(1)
    
    # Read results
    results_file = Path("performance_results.json")
    if not results_file.exists():
        print("Error: Results file not created")
        sys.exit(1)
    
    with open(results_file) as f:
        data = json.load(f)
    
    return data


def parse_benchmark_results(data):
    """Parse pyperf benchmark results."""
    benchmarks = data.get("benchmarks", [])
    
    results = {}
    for bench in benchmarks:
        name = bench.get("metadata", {}).get("name", "unknown")
        runs = bench.get("runs", [])
        
        if runs:
            # Get values from runs
            values = [run.get("values", [None])[0] for run in runs if run.get("values")]
            if values:
                mean = sum(values) / len(values)
                results[name] = {
                    "mean": mean,
                    "min": min(values),
                    "max": max(values),
                    "runs": len(values),
                    "values": values
                }
    
    return results


def generate_markdown_report(results, output_file="PERFORMANCE.md"):
    """Generate a markdown report from benchmark results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# pytest-configurex Performance Report

Generated: {timestamp}

## Overview

This report shows the performance characteristics of different configuration loading methods in pytest-configurex.

## Results

| Configuration Method | Mean Time (seconds) | Min Time (seconds) | Max Time (seconds) | Runs |
|---------------------|--------------------:|-------------------:|-------------------:|-----:|
"""
    
    # Sort by mean time
    sorted_results = sorted(results.items(), key=lambda x: x[1]["mean"])
    
    for name, data in sorted_results:
        display_name = name.replace("_", " ").replace("load from ", "").title()
        report += f"| {display_name} | {data['mean']:.6f} | {data['min']:.6f} | {data['max']:.6f} | {data['runs']} |\n"
    
    report += """
## Configuration Methods Tested

1. **Env Pytest**: Loading configuration from `.env.pytest` file
2. **Env**: Loading configuration from `.env` file (fallback)
3. **Environment Vars**: Loading configuration from environment variables
4. **CLI Only**: Traditional pytest command line (no configurex plugin)

## Performance Analysis

"""
    
    # Calculate performance comparison
    if "load_from_env_pytest" in results and "load_from_cli_only" in results:
        env_pytest_time = results["load_from_env_pytest"]["mean"]
        cli_only_time = results["load_from_cli_only"]["mean"]
        overhead = ((env_pytest_time - cli_only_time) / cli_only_time) * 100
        
        report += f"- **Overhead of pytest-configurex**: ~{overhead:.2f}%\n"
        report += f"- **Absolute overhead**: ~{(env_pytest_time - cli_only_time) * 1000:.2f}ms per test run\n\n"
    
    # Find fastest method
    if sorted_results:
        fastest = sorted_results[0]
        report += f"- **Fastest method**: {fastest[0].replace('_', ' ').replace('load from ', '').title()}\n"
    
    report += """
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
"""
    
    # Write report
    output_path = Path(output_file)
    output_path.write_text(report)
    print(f"\nMarkdown report generated: {output_path}")
    
    return report


def generate_json_report(results, output_file="performance_results_summary.json"):
    """Generate a JSON report from benchmark results."""
    timestamp = datetime.now().isoformat()
    
    report_data = {
        "timestamp": timestamp,
        "benchmarks": {}
    }
    
    for name, data in results.items():
        report_data["benchmarks"][name] = {
            "mean_seconds": data["mean"],
            "min_seconds": data["min"],
            "max_seconds": data["max"],
            "runs": data["runs"],
            "mean_milliseconds": data["mean"] * 1000,
        }
    
    # Calculate overhead if applicable
    if "load_from_env_pytest" in results and "load_from_cli_only" in results:
        env_pytest_time = results["load_from_env_pytest"]["mean"]
        cli_only_time = results["load_from_cli_only"]["mean"]
        overhead_pct = ((env_pytest_time - cli_only_time) / cli_only_time) * 100
        overhead_ms = (env_pytest_time - cli_only_time) * 1000
        
        report_data["analysis"] = {
            "overhead_percentage": round(overhead_pct, 2),
            "overhead_milliseconds": round(overhead_ms, 2),
            "fastest_method": min(results.items(), key=lambda x: x[1]["mean"])[0]
        }
    
    # Write report
    output_path = Path(output_file)
    with open(output_path, "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"JSON report generated: {output_path}")
    
    return report_data


def main():
    """Main function to run tests and generate reports."""
    print("pytest-configurex Performance Testing")
    print("=" * 50)
    print()
    
    # Run benchmarks
    data = run_performance_benchmarks()
    
    # Parse results
    results = parse_benchmark_results(data)
    
    if not results:
        print("Error: No benchmark results found")
        sys.exit(1)
    
    # Generate reports
    generate_markdown_report(results)
    generate_json_report(results)
    
    print("\n" + "=" * 50)
    print("Performance testing complete!")
    print("Reports generated:")
    print("  - PERFORMANCE.md")
    print("  - performance_results_summary.json")


if __name__ == "__main__":
    main()
