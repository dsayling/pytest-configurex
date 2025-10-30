#!/bin/bash
# Run pytest-configurex startup performance benchmarks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Running pytest-configurex benchmarks..."
echo "Project root: $PROJECT_ROOT"
echo ""

# Ensure we're in the project root
cd "$PROJECT_ROOT"

# Run the benchmark script with uv
uv run python benchmarks/benchmark_startup.py "$@"
