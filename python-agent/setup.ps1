# Setup script for Python Agent Console

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Python Agent Console Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if we're in the correct directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "✗ requirements.txt not found. Please run this script from the python-agent directory." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists, skipping..." -ForegroundColor Gray
} else {
    python -m venv venv
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check if .env exists
Write-Host ""
if (Test-Path ".env") {
    Write-Host "✓ Configuration file (.env) already exists" -ForegroundColor Green
} else {
    Write-Host "⚠ Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created. Please update with your settings." -ForegroundColor Green
}

# Check Azure CLI authentication
Write-Host ""
Write-Host "Checking Azure CLI authentication..." -ForegroundColor Yellow
try {
    $azAccount = az account show 2>&1 | ConvertFrom-Json
    Write-Host "✓ Authenticated as: $($azAccount.user.name)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Not authenticated with Azure CLI. Run 'az login' if needed." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Ensure .env file has correct settings" -ForegroundColor White
Write-Host "  2. Run: python agent_console.py" -ForegroundColor White
Write-Host ""
Write-Host "Examples:" -ForegroundColor Cyan
Write-Host "  python agent_console.py                           # Interactive mode" -ForegroundColor Gray
Write-Host '  python agent_console.py "What is Azure?"          # Single message' -ForegroundColor Gray
Write-Host ""
