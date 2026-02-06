# AI Assistant - Desktop Application

A cross-platform AI Assistant desktop application built with Python and PySide6.

## Features

- 🎙️ Voice input and text-to-speech output
- 💬 Interactive chat interface
- 🔌 Configurable API backend via .env file
- 🎨 Modern dark theme UI
- 📹 Camera integration (optional)
- 🖥️ Cross-platform (Windows, Linux, macOS)

## Quick Start

### Download Pre-built Application

Download the latest release for your platform:

- **Windows**: [AIAssistant-windows-x64.zip](https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-windows-x64.zip)
- **Linux**: [AIAssistant-linux-x64.tar.gz](https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-linux-x64.tar.gz)
- **macOS**: [AIAssistant-macos-x64.zip](https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-macos-x64.zip)

### Setup

1. Extract the downloaded archive
2. Copy `.env.example` to `.env`
3. Edit `.env` and configure your API server:
   ```env
   API_BASE_URL=https://your-api-server.com/api
   API_KEY=your_api_key_here
   ```
4. Run the application:
   - **Windows**: Double-click `AIAssistant.exe`
   - **Linux**: `./AIAssistant`
   - **macOS**: Open `AIAssistant.app`

## Configuration

All settings are managed through the `.env` file:

```env
# Your AI API server URL
API_BASE_URL=http://localhost:5000/api

# API Authentication (optional)
API_KEY=your_key_here
API_SECRET=your_secret_here

# Application Settings
DEBUG_MODE=false
API_TIMEOUT=30

# Voice Settings
TTS_RATE=150
TTS_VOLUME=0.9
```

**To change your API server**: Just edit the `.env` file and restart the application. No code changes needed!

## Development

### Requirements

- Python 3.9+
- pip

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your API settings
nano .env  # or use your favorite editor

# Run the application
python app/main.py
```

### Build from Source

#### Linux
```bash
chmod +x scripts/build-linux.sh
./scripts/build-linux.sh
```

#### Windows
```powershell
powershell -ExecutionPolicy Bypass -File scripts/build-windows.ps1
```

#### macOS
```bash
chmod +x scripts/build-macos.sh
./scripts/build-macos.sh
```

The built application will be in the `dist/` directory.

## CI/CD

This project uses GitHub Actions for automated builds and releases.

### Creating a Release

1. Update version in `.env.example` and commit changes
2. Create and push a version tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. GitHub Actions will automatically:
   - Build for Windows, Linux, and macOS
   - Create a GitHub Release
   - Upload downloadable packages

### Download Links

After creating a release, users can download from:
```
https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-windows-x64.zip
https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-linux-x64.tar.gz
https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-macos-x64.zip
```

## Project Structure

```
client/
├── app/
│   ├── main.py              # Application entry point
│   ├── controllers/         # Business logic
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration (reads .env)
│   │   ├── api_client.py   # API communication
│   │   └── ...
│   └── ui/                 # User interface
├── scripts/                # Build scripts
│   ├── build-linux.sh
│   ├── build-windows.ps1
│   └── build-macos.sh
├── .github/
│   └── workflows/
│       └── release.yml     # CI/CD pipeline
├── .env                    # Your local configuration (not in git)
├── .env.example           # Configuration template
├── requirements.txt       # Python dependencies
└── AIAssistant.production.spec  # PyInstaller config
```

## Troubleshooting

### API Connection Issues

1. Check your `.env` file has correct `API_BASE_URL`
2. Verify your API server is running
3. Check firewall settings
4. Enable `DEBUG_MODE=true` in `.env` for detailed logs

### Build Issues

**Linux**: Install required system packages:
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

**macOS**: Install portaudio:
```bash
brew install portaudio
```

**Windows**: PyAudio may require Microsoft C++ Build Tools

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Need help?** Open an issue on GitHub or check the documentation.
