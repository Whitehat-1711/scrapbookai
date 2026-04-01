# Start Blogy backend Server
# This script starts the FastAPI backend with uvicorn

Set-Location (Split-Path -Parent -Path $MyInvocation.MyCommand.Definition)

Write-Host "Starting Blogy backend Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Recommended: Conda environment 'blogy' should be activated" -ForegroundColor Yellow
Write-Host ""

# Set PYTHONPATH to current directory
$env:PYTHONPATH = Get-Location

# Run uvicorn
python -m uvicorn backend.core.main:app --reload --host 0.0.0.0 --port 8000

Write-Host "backend server stopped."
