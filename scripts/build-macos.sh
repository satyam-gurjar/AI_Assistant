#!/bin/bash
# Build script for macOS
# Builds AI Assistant application for macOS distribution

set -e  # Exit on error

echo "=========================================="
echo "Building AI Assistant for macOS"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build with PyInstaller
echo "Building application..."
pyinstaller AIAssistant.production.spec

# Create distribution package
echo "Creating distribution package..."
cd dist
# For macOS, we can create a DMG or just zip the .app bundle
if [ -d "AIAssistant.app" ]; then
    zip -r AIAssistant-macos-x64.zip AIAssistant.app
else
    # If not .app bundle, zip the executable
    zip AIAssistant-macos-x64.zip AIAssistant
fi
cd ..

# Copy .env.example to dist
cp .env.example dist/.env.example

echo "=========================================="
echo "Build complete!"
echo "Package: dist/AIAssistant-macos-x64.zip"
echo "=========================================="
echo ""
echo "To run the application:"
echo "1. Extract the zip file"
echo "2. Copy .env.example to .env and configure your API"
echo "3. Open AIAssistant.app (or run ./AIAssistant)"
