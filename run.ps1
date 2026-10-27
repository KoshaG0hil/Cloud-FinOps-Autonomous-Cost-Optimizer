# ==============================================================================
# Cloud-FinOps-Autonomous-Cost-Optimizer One-Click Runner (PowerShell)
# ==============================================================================

param (
    [string]$Command = "scan",
    [switch]$Live = $false,
    [switch]$Test = $false,
    [switch]$Dashboard = $false,
    [string]$Action = "stop"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
$env:PYTHONPATH = $ScriptDir

Write-Host "=================================================================" -ForegroundColor Green
Write-Host "  AWS Cloud FinOps & Autonomous Cost Governance Engine" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

if ($Test) {
    Write-Host "`n[*] Executing Test Suite (Pytest + Moto)..." -ForegroundColor Yellow
    python -m pytest tests/ -v
    exit $LASTEXITCODE
}

if ($Dashboard) {
    Write-Host "`n[*] Launching Live FinOps Dashboard in web browser..." -ForegroundColor Green
    Start-Process "$ScriptDir\index.html"
    exit 0
}

if ($Command -eq "park") {
    Write-Host "`n[*] Executing Scheduled Auto-Parking Cycle ($Action)..." -ForegroundColor Yellow
    if ($Live) {
        python -m src.cli park --action $Action
    } else {
        python -m src.cli park --action $Action --dry-run
    }
    exit $LASTEXITCODE
}

Write-Host "`n[*] Running Infrastructure FinOps Sweep..." -ForegroundColor Yellow
if ($Live) {
    python -m src.cli scan --live
} else {
    python -m src.cli scan --dry-run
}
