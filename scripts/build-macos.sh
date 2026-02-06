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
pyinstaller AIAssistant.spec

# Create distribution directory
echo "Creating distribution directory..."
mkdir -p dist/AIAssistant-macos-x64

# For macOS, we can create a DMG or just zip the .app bundle
if [ -d "dist/AIAssistant.app" ]; then
    # Copy .app bundle to distribution directory
    cp -r dist/AIAssistant.app dist/AIAssistant-macos-x64/
else
    # If not .app bundle, copy the executable
    cp dist/AIAssistant dist/AIAssistant-macos-x64/
fi

# Copy .env.example to distribution directory
cp .env.example dist/AIAssistant-macos-x64/.env.example

# Create README in dist
cat > dist/AIAssistant-macos-x64/README.txt << 'EOF'
AI Assistant - macOS x64
========================

Setup Instructions:
1. Copy .env.example to .env
2. Edit .env and set your API_BASE_URL
3. Open AIAssistant.app (or run ./AIAssistant)

Configuration:
Edit .env file to customize:
- API_BASE_URL: Your AI server URL
- API_KEY: Your API key (if required)
- TTS_RATE: Speech rate (default: 150)
- TTS_VOLUME: Speech volume (default: 0.9)

Note: On first run, you may need to right-click and select "Open"
to bypass macOS security warnings.

For more information, visit:
https://github.com/yourusername/yourrepo
EOF

# Create distribution package
echo "Creating zip file..."
cd dist
zip -r AIAssistant-macos-x64.zip AIAssistant-macos-x64
cd ..

echo "=========================================="
echo "Build complete!"
echo "Package: dist/AIAssistant-macos-x64.zip"
echo "=========================================="
echo ""
echo "To run the application:"
echo "1. Extract the zip file"
echo "2. Copy .env.example to .env and configure your API"
echo "3. Open AIAssistant.app (or run ./AIAssistant)"
