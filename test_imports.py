#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
Run this before building to catch missing dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all critical imports."""
    
    errors = []
    
    print("Testing imports...")
    print("=" * 60)
    
    # Test core Python modules
    try:
        import os
        import sys
        import logging
        from pathlib import Path
        print("✓ Core Python modules")
    except ImportError as e:
        errors.append(f"Core modules: {e}")
        print(f"✗ Core Python modules: {e}")
    
    # Test PySide6
    try:
        from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
        from PySide6.QtCore import Qt, Signal, QThread
        from PySide6.QtGui import QColor, QPalette
        print("✓ PySide6 (Qt)")
    except ImportError as e:
        errors.append(f"PySide6: {e}")
        print(f"✗ PySide6: {e}")
    
    # Test dotenv
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        errors.append(f"python-dotenv: {e}")
        print(f"✗ python-dotenv: {e}")
    
    # Test requests
    try:
        import requests
        import certifi
        import urllib3
        print("✓ requests, certifi, urllib3")
    except ImportError as e:
        errors.append(f"HTTP libraries: {e}")
        print(f"✗ HTTP libraries: {e}")
    
    # Test speech recognition (optional)
    try:
        import speech_recognition as sr
        print("✓ speech_recognition")
    except ImportError as e:
        print(f"⚠ speech_recognition: {e} (optional, voice input won't work)")
    
    # Test PyAudio (optional)
    try:
        import pyaudio
        print("✓ PyAudio")
    except ImportError as e:
        print(f"⚠ PyAudio: {e} (optional, voice input won't work)")
    
    # Test pyttsx3 (optional)
    try:
        import pyttsx3
        print("✓ pyttsx3")
    except ImportError as e:
        print(f"⚠ pyttsx3: {e} (optional, text-to-speech won't work)")
    
    # Test OpenCV (optional)
    try:
        import cv2
        print("✓ opencv-python")
    except ImportError as e:
        print(f"⚠ opencv-python: {e} (optional, camera won't work)")
    
    # Test NumPy (optional)
    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"⚠ numpy: {e} (optional, may affect camera/audio processing)")
    
    print("=" * 60)
    
    # Test application imports
    print("\nTesting application modules...")
    print("=" * 60)
    
    try:
        from app.core.config import Config
        print("✓ app.core.config")
    except ImportError as e:
        errors.append(f"app.core.config: {e}")
        print(f"✗ app.core.config: {e}")
    
    try:
        from app.core.api_client import APIClient
        print("✓ app.core.api_client")
    except ImportError as e:
        errors.append(f"app.core.api_client: {e}")
        print(f"✗ app.core.api_client: {e}")
    
    try:
        from app.core.voice_input import VoiceInputHandler
        print("✓ app.core.voice_input")
    except ImportError as e:
        errors.append(f"app.core.voice_input: {e}")
        print(f"✗ app.core.voice_input: {e}")
    
    try:
        from app.core.text_to_speech import TextToSpeech
        print("✓ app.core.text_to_speech")
    except ImportError as e:
        errors.append(f"app.core.text_to_speech: {e}")
        print(f"✗ app.core.text_to_speech: {e}")
    
    try:
        from app.core.camera import CameraManager
        print("✓ app.core.camera")
    except ImportError as e:
        errors.append(f"app.core.camera: {e}")
        print(f"✗ app.core.camera: {e}")
    
    try:
        from app.ui.voice_agent_window import VoiceAgentWindow
        print("✓ app.ui.voice_agent_window")
    except ImportError as e:
        errors.append(f"app.ui.voice_agent_window: {e}")
        print(f"✗ app.ui.voice_agent_window: {e}")
    
    try:
        from app.controllers.voice_agent_controller import VoiceAgentController
        print("✓ app.controllers.voice_agent_controller")
    except ImportError as e:
        errors.append(f"app.controllers.voice_agent_controller: {e}")
        print(f"✗ app.controllers.voice_agent_controller: {e}")
    
    print("=" * 60)
    
    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ FAILED: {len(errors)} critical imports failed")
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("✅ SUCCESS: All critical imports working!")
        print("\nYou can now build the application:")
        print("  - Windows: scripts/build-windows.ps1")
        print("  - Linux: scripts/build-linux.sh")
        print("  - macOS: scripts/build-macos.sh")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
