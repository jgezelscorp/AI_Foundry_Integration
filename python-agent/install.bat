@echo off
echo.
echo =====================================
echo Python Agent Console - Quick Setup
echo =====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

echo Installing dependencies...
pip install azure-ai-projects azure-identity python-dotenv --quiet

if errorlevel 1 (
    echo Error: Failed to install dependencies
    exit /b 1
)

echo.
echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo You can now run:
echo   python agent_console.py
echo.
echo Or send a single message:
echo   python agent_console.py "What is Azure AI Foundry?"
echo.

pause
