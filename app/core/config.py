"""
Configuration Module for AI Assistant Application

Production-ready configuration that loads all settings from .env file.
To change API server: Edit .env file and restart the application.

IMPORTANT: All configuration is now managed through the .env file.
Never hardcode sensitive data in this file.
"""

import os
import sys
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Determine the correct directory for .env file
# When running as compiled executable, use the executable's directory
# When running as script, use the project root
if getattr(sys, 'frozen', False):
    # Running as compiled executable (PyInstaller)
    # sys._MEIPASS is the temp folder where PyInstaller extracts files
    # But we want the actual executable directory for user's .env file
    ENV_DIR = Path(sys.executable).parent
    # Also check sys._MEIPASS for bundled .env.example
    if hasattr(sys, '_MEIPASS'):
        # If .env doesn't exist in executable dir, check bundled location
        if not (ENV_DIR / ".env").exists():
            bundled_env = Path(sys._MEIPASS) / ".env"
            if bundled_env.exists():
                # Use bundled .env as fallback (but prefer user's .env)
                pass
else:
    # Running as script - go up to project root
    ENV_DIR = Path(__file__).parent.parent.parent

# Load environment variables from .env file
load_dotenv(dotenv_path=ENV_DIR / ".env")


class Config:
    """
    Central configuration class for the AI Assistant application.
    Settings can be customized via .env file (optional).
    Default values are hardcoded for immediate use.
    """
    
    # ========== API CONFIGURATION ==========
    # Your backend AI API server URL
    # Default: http://localhost:5000/api (can be changed in .env file)
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:5000/api")
    
    # Specific API endpoints (relative to API_BASE_URL)
    CHAT_ENDPOINT: str = "/chat"
    HEALTH_ENDPOINT: str = "/health"
    
    # ========== AUTHENTICATION ==========
    # API credentials (loaded from .env)
    API_KEY: Optional[str] = os.getenv("API_KEY", None)
    API_SECRET: Optional[str] = os.getenv("API_SECRET", None)
    
    # Authentication header configuration
    AUTH_HEADER_NAME: str = "Authorization"
    AUTH_TYPE: str = "Bearer"
    
    # ========== TIMEOUT SETTINGS ==========
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    CONNECTION_TIMEOUT: int = int(os.getenv("CONNECTION_TIMEOUT", "10"))
    
    # ========== UI CONFIGURATION ==========
    APP_NAME: str = os.getenv("APP_NAME", "AI Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    WINDOW_WIDTH: int = 1000
    WINDOW_HEIGHT: int = 700
    WINDOW_MIN_WIDTH: int = 800
    WINDOW_MIN_HEIGHT: int = 600
    
    # ========== LOGGING CONFIGURATION ==========
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    # Use the same directory as the executable/script for logs
    LOG_DIR: Path = ENV_DIR / "logs"
    LOG_FILE: str = "ai_assistant.log"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ========== CHAT CONFIGURATION ==========
    MAX_MESSAGE_LENGTH: int = 5000
    MAX_CHAT_HISTORY: int = 100
    
    # ========== VOICE SETTINGS ==========
    TTS_RATE: int = int(os.getenv("TTS_RATE", "150"))
    TTS_VOLUME: float = float(os.getenv("TTS_VOLUME", "0.9"))
    
    # ========== THEME CONFIGURATION ==========
    DARK_BACKGROUND: str = "#1e1e1e"
    DARK_SURFACE: str = "#2d2d2d"
    DARK_ACCENT: str = "#007acc"
    TEXT_PRIMARY: str = "#e0e0e0"
    TEXT_SECONDARY: str = "#a0a0a0"
    USER_MESSAGE_BG: str = "#007acc"
    AI_MESSAGE_BG: str = "#2d2d2d"
    ERROR_COLOR: str = "#f44336"
    SUCCESS_COLOR: str = "#4caf50"
    
    @classmethod
    def get_full_chat_url(cls) -> str:
        """
        Construct the full chat API URL.
        
        Returns:
            str: Complete URL for chat endpoint
            
        Example:
            "http://localhost:8000/api/v1/chat"
        """
        return f"{cls.API_BASE_URL}{cls.CHAT_ENDPOINT}"
    
    @classmethod
    def get_full_health_url(cls) -> str:
        """
        Construct the full health check API URL.
        
        Returns:
            str: Complete URL for health endpoint
            
        Example:
            "http://localhost:8000/api/v1/health"
        """
        return f"{cls.API_BASE_URL}{cls.HEALTH_ENDPOINT}"
    
    @classmethod
    def get_auth_header(cls) -> dict:
        """
        Generate authentication header for API requests.
        
        Returns:
            dict: Headers dictionary with authorization
            
        Example:
            {"Authorization": "Bearer your_api_key_here"}
        """
        if cls.API_KEY:
            return {
                cls.AUTH_HEADER_NAME: f"{cls.AUTH_TYPE} {cls.API_KEY}"
            }
        return {}
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration settings.
        
        Checks if all required configuration is present and valid.
        Useful for startup validation.
        
        Returns:
            tuple[bool, list[str]]: (is_valid, list_of_errors)
            
        Example:
            valid, errors = Config.validate_config()
            if not valid:
                print("Config errors:", errors)
        """
        errors = []
        
        # Check if API base URL is set
        if not cls.API_BASE_URL:
            errors.append("API_BASE_URL is not configured")
        
        # Check if API URL is valid format
        if not cls.API_BASE_URL.startswith(("http://", "https://")):
            errors.append("API_BASE_URL must start with http:// or https://")
        
        # Warning if API key is not set (may be optional depending on backend)
        if not cls.API_KEY:
            errors.append("API_KEY is not set (may be required for authentication)")
        
        return len(errors) == 0, errors


# Create a default config instance
config = Config()

