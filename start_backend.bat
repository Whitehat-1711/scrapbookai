@echo off
REM Start Blogy backend Server
REM This script starts the FastAPI backend with uvicorn

cd /d "%~dp0"

echo Starting Blogy backend Server...
echo.
echo Recommended: Conda environment 'blogy' should be activated
echo.

REM Option: set PYTHONPATH to current directory
set PYTHONPATH=%cd%

REM Run uvicorn
python -m uvicorn backend.core.main:app --reload --host 0.0.0.0 --port 8000

pause
