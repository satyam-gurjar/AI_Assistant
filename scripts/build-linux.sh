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

# Create distribution directory
echo "Creating distribution directory..."
mkdir -p dist/AIAssistant-linux-x64

# Copy executable to distribution directory
cp dist/AIAssistant dist/AIAssistant-linux-x64/

# Copy .env.example to distribution directory
cp .env.example dist/AIAssistant-linux-x64/.env.example

# Create README in dist
cat > dist/AIAssistant-linux-x64/README.txt << 'EOF'
AI Assistant - Linux x64
========================

Setup Instructions:
1. Copy .env.example to .env
2. Edit .env and set your API_BASE_URL
3. Run: ./AIAssistant

Configuration:
Edit .env file to customize:
- API_BASE_URL: Your AI server URL
- API_KEY: Your API key (if required)
- TTS_RATE: Speech rate (default: 150)
- TTS_VOLUME: Speech volume (default: 0.9)

For more information, visit:
https://github.com/yourusername/yourrepo
EOF

# Create distribution package
echo "Creating tarball..."
cd dist
tar -czf AIAssistant-linux-x64.tar.gz AIAssistant-linux-x64
cd ..

echo "=========================================="
echo "Build complete!"
echo "Package: dist/AIAssistant-linux-x64.tar.gz"
echo "=========================================="
echo ""
echo "To run the application:"
echo "1. Extract the tar.gz file"
echo "2. Copy .env.example to .env and configure your API"
echo "3. Run: ./AIAssistant"
