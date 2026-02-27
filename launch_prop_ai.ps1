# Automated setup and launch script for Prop.AI (2.0)
# This script checks for Python, creates/activates .venv, installs requirements, starts backend, and runs the dashboard.

$ErrorActionPreference = 'Stop'

Write-Host "Checking Python installation..."
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python not found. Please install Python 3.8+ from https://www.python.org/downloads/ and ensure it is in your PATH."
    exit 1
}

Write-Host "Checking for .venv..."
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment (.venv)..."
    python -m venv .venv
}

Write-Host "Activating .venv..."
& ".venv/Scripts/Activate.ps1"

Write-Host "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Starting FastAPI backend..."
Start-Process -NoNewWindow -FilePath python -ArgumentList "-m uvicorn app.api.main:app --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 5

Write-Host "Launching unified dashboard script..."
python run_dashboard.py
