#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR"

echo "================================================================="
echo "  AWS Cloud FinOps & Autonomous Cost Governance Engine"
echo "================================================================="

if [ "$1" == "test" ]; then
    echo "[*] Executing Test Suite (Pytest + Moto)..."
    python3 -m pytest tests/ -v
    exit 0
fi

if [ "$1" == "dashboard" ]; then
    echo "[*] Opening Dashboard..."
    if command -v xdg-open &> /dev/null; then
        xdg-open index.html
    elif command -v open &> /dev/null; then
        open index.html
    fi
    exit 0
fi

if [ "$1" == "park" ]; then
    echo "[*] Executing Auto-Parking Cycle..."
    python3 -m src.cli park --action "${2:-stop}"
    exit 0
fi

echo "[*] Running FinOps Sweep (Dry-Run Mode)..."
python3 -m src.cli scan --dry-run
