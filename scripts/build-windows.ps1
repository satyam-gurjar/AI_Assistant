# Build script for Windows
# Builds AI Assistant application for Windows distribution

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Building AI Assistant for Windows" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force build }
if (Test-Path "dist") { Remove-Item -Recurse -Force dist }

# Build with PyInstaller
Write-Host "Building executable..." -ForegroundColor Yellow
pyinstaller AIAssistant.production.spec

# Create distribution package
Write-Host "Creating distribution package..." -ForegroundColor Yellow
Set-Location dist
Compress-Archive -Path AIAssistant.exe -DestinationPath AIAssistant-windows-x64.zip -Force
Set-Location ..

# Copy .env.example to dist
Copy-Item .env.example dist\.env.example

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Package: dist\AIAssistant-windows-x64.zip" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "1. Extract the zip file" -ForegroundColor Cyan
Write-Host "2. Copy .env.example to .env and configure your API" -ForegroundColor Cyan
Write-Host "3. Run: AIAssistant.exe" -ForegroundColor Cyan
