@echo off
setlocal
cd /d "%~dp0"
set PYTHONPATH=%~dp0

echo =================================================================
echo   AWS Cloud FinOps & Autonomous Cost Governance Engine
echo =================================================================

if "%1"=="test" (
    echo [*] Executing Test Suite...
    python -m pytest tests/ -v
    goto :eof
)

if "%1"=="dashboard" (
    echo [*] Opening Dashboard...
    start index.html
    goto :eof
)

if "%1"=="park" (
    echo [*] Executing Auto-Parking Cycle...
    python -m src.cli park --action %2
    goto :eof
)

echo [*] Running FinOps Sweep (Dry-Run Mode)...
python -m src.cli scan --dry-run
