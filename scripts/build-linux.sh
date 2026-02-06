#!/bin/bash
# Build script for Linux
# Builds AI Assistant application for Linux distribution

set -e  # Exit on error

echo "=========================================="
echo "Building AI Assistant for Linux"
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
echo "Building executable..."
pyinstaller AIAssistant.spec

# Copy .env.example to dist
cp .env.example dist/.env.example

echo "=========================================="
echo "Build complete!"
echo "Executable: dist/AIAssistant"
echo "=========================================="
echo ""
echo "To run the application:"
echo "1. Extract the tar.gz file"
echo "2. Copy .env.example to .env and configure your API"
echo "3. Run: ./AIAssistant"
