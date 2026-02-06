# Deployment Guide

## Step-by-Step Deployment to GitHub with CI/CD

### 1. Initialize Git Repository (if not already done)

```bash
cd /home/satya/client
git init
git add .
git commit -m "Initial commit: Production-ready AI Assistant with CI/CD"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `ai-assistant-desktop`)
3. **DO NOT** initialize with README, .gitignore, or license
4. Copy the repository URL

### 3. Push to GitHub

```bash
# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 4. Create Your First Release

```bash
# Tag your first version
git tag v1.0.0

# Push the tag to trigger CI/CD
git push origin v1.0.0
```

### 5. What Happens Next

GitHub Actions will automatically:
1. Build application for Windows, Linux, and macOS
2. Create executables for each platform
3. Create a GitHub Release with all packages
4. Generate downloadable links

**Build progress**: Go to your repo → Actions tab to watch the build

**Download links** (after build completes):
- `https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-windows-x64.zip`
- `https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-linux-x64.tar.gz`
- `https://github.com/YOUR_USERNAME/YOUR_REPO/releases/latest/download/AIAssistant-macos-x64.zip`

### 6. Updating Your Application

When you want to release a new version:

```bash
# Make your changes
git add .
git commit -m "Your changes description"
git push origin main

# Create a new version tag
git tag v1.0.1
git push origin v1.0.1
```

The CI/CD pipeline will automatically build and publish the new release!

## Changing API Server Configuration

### For Users (After Deployment)

Users only need to edit the `.env` file next to the executable:

1. Extract the application
2. Copy `.env.example` to `.env`
3. Edit `.env`:
   ```env
   API_BASE_URL=https://your-new-api-server.com/api
   API_KEY=your_new_key
   ```
4. Restart the application

**No recompilation needed!**

### For Development

Edit `/home/satya/client/.env`:
```env
API_BASE_URL=http://localhost:5000/api
```

Run: `python app/main.py`

## Troubleshooting CI/CD

### Build Fails on GitHub Actions

1. Check Actions tab for error logs
2. Common issues:
   - Missing dependencies → Update `requirements.txt`
   - Build script permissions → Scripts should be executable
   - PyInstaller issues → Check `AIAssistant.production.spec`

### Manual Build Test (Local)

Before pushing to GitHub, test build locally:

```bash
# Linux
./scripts/build-linux.sh

# Check dist/ folder for output
ls -lh dist/
```

### Release Not Created

- Ensure you pushed a tag starting with `v` (e.g., `v1.0.0`)
- Check GitHub Actions completed successfully
- Verify you have write permissions on the repository

## Project Files Summary

### Created/Modified Files

- **`.env`** - Your local configuration (NOT in git)
- **`.env.example`** - Configuration template (in git)
- **`.gitignore`** - Ignore sensitive files
- **`app/core/config.py`** - Updated to read from .env
- **`AIAssistant.production.spec`** - PyInstaller configuration
- **`scripts/build-*.sh|ps1`** - Build scripts for each platform
- **`.github/workflows/release.yml`** - CI/CD pipeline

### Removed Files

- `main.spec` - Old spec file
- `setup.sh`, `build.sh`, `run.sh`, `launch.sh` - Old build scripts

## Next Steps

1. Push your code to GitHub
2. Create first release: `git tag v1.0.0 && git push origin v1.0.0`
3. Wait for GitHub Actions to complete (5-15 minutes)
4. Share download links with users
5. When you change API server in the future:
   - For users: Just edit `.env` file
   - For code updates: Edit `.env.example` and create new release

**Your application is now production-ready and automatically builds for all platforms!**
