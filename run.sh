#!/bin/bash
set -e

echo "==> [1/3] Running Go engine..."
cd /workspace/engine && ./scanner

echo "==> [2/3] Running Python OWASP checks..."
cd /workspace/checks && python3 checks.py

echo "==> [3/3] Running Rust reporter..."
cd /workspace/reporter && ./target/release/reporter

echo ""
echo "[✓] Pipeline complete. report.html generated."