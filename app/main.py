"""
Main Entry Point for AI Assistant Desktop Application

This file is the application's entry point.
It only handles:
1. Logging setup
2. Application initialization
3. Window and controller creation
4. Event loop startup
5. Cleanup on exit

All other logic is in separate modules (MVC architecture).

Usage:
    python main.py
    
Or after building:
    ./AIAssistant.exe (Windows)
    ./AIAssistant (Linux/Mac)
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from app.core.config import Config
from app.ui.voice_agent_window import VoiceAgentWindow
from app.controllers.voice_agent_controller import VoiceAgentController


def setup_logging():
    """
    Configure application logging.
    
    Sets up logging to both console and file.
    Logs are saved to logs/ai_assistant.log
    
    Log levels:
    - DEBUG: Detailed information for debugging
    - INFO: General information about app state
    - WARNING: Warning messages
    - ERROR: Error messages
    - CRITICAL: Critical errors
    """
    # Create logs directory if it doesn't exist
    Config.LOG_DIR.mkdir(exist_ok=True)
    
    # Determine log level based on debug mode
    log_level = logging.DEBUG if Config.DEBUG_MODE else logging.INFO
    
    # Configure logging format
    # Shows timestamp, level, module name, and message
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Create formatters and handlers
    formatter = logging.Formatter(log_format, date_format)
    
    # Console handler (prints to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # File handler (writes to log file)
    log_file_path = Config.LOG_DIR / Config.LOG_FILE
    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Log startup message
    logging.info("=" * 60)
    logging.info(f"{Config.APP_NAME} v{Config.APP_VERSION} - Starting")
    logging.info("=" * 60)
    logging.info(f"Log file: {log_file_path}")
    logging.info(f"Debug mode: {Config.DEBUG_MODE}")
    logging.info(f"API Base URL: {Config.API_BASE_URL}")


def validate_configuration():
    """
    Validate application configuration.
    
    Checks if all required settings are properly configured.
    Logs warnings for any configuration issues.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    logger.info("Validating configuration...")
    
    # Validate using Config class method
    is_valid, errors = Config.validate_config()
    
    if not is_valid:
        logger.warning("Configuration validation found issues:")
        for error in errors:
            logger.warning(f"  - {error}")
    else:
        logger.info("Configuration validation passed")
    
    return is_valid


def setup_qt_settings():
    """
    Configure Qt application settings.
    
    Sets application-wide Qt properties and attributes.
    """
    # Enable high DPI scaling (for 4K monitors, etc.)
    # This makes the UI look crisp on high-resolution displays
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def check_env_file():
    """
    Check if .env file exists (optional info only).
    App works without .env using hardcoded defaults.
    
    Returns:
        bool: True always (doesn't block startup)
    """
    # This function kept for future use but doesn't block startup
    # App works with hardcoded defaults from config.py
    return True


def main():
    """
    Main application function.
    
    This is the entry point that:
    1. Checks for .env file
    2. Sets up logging
    3. Validates configuration
    4. Creates Qt application
    5. Creates main window and controller
    6. Shows the window
    7. Starts the event loop
    8. Cleans up on exit
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    try:
        # Note: .env file is now OPTIONAL
        # App works with hardcoded defaults, .env only for customization
        # Just set up logging with defaults
        setup_logging()
        
        logger = logging.getLogger(__name__)
        
        # Validate configuration
        validate_configuration()
        
        # Configure Qt settings
        setup_qt_settings()
        
        # Create Qt application
        # This is required for all Qt applications
        # sys.argv is passed to handle command-line arguments
        logger.info("Creating Qt application...")
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName(Config.APP_NAME)
        app.setApplicationVersion(Config.APP_VERSION)
        app.setOrganizationName("YourOrganization")  # Change this
        
        # Create main window (the UI)
        logger.info("Creating voice agent window...")
        window = VoiceAgentWindow()
        
        # Create controller (the business logic)
        # Controller connects UI and API
        logger.info("Creating voice agent controller...")
        controller = VoiceAgentController(window)
        
        # Show the window
        logger.info("Showing main window...")
        window.show()
        
        # Start the Qt event loop
        # This runs until user closes the application
        # All UI events (clicks, keyboard, etc.) are processed here
        logger.info("Application started successfully")
        logger.info("=" * 60)
        
        # Run the event loop and capture exit code
        exit_code = app.exec()
        
        # Application is closing
        logger.info("=" * 60)
        logger.info("Application shutting down...")
        
        # Clean up resources
        controller.cleanup()
        
        logger.info(f"Application exited with code {exit_code}")
        logger.info("=" * 60)
        
        return exit_code
    
    except Exception as e:
        # Catch any unexpected errors during startup
        # Try to log it if logger exists, otherwise print to stderr
        try:
            logger = logging.getLogger(__name__)
            logger.exception(f"Fatal error during application startup: {e}")
        except:
            import sys
            print(f"FATAL ERROR: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
        
        # Show error dialog to user
        try:
            app = QApplication.instance() or QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Application Error")
            msg.setText("AI Assistant failed to start!")
            msg.setInformativeText(f"Error: {str(e)}\n\nCheck logs/ai_assistant.log for details.")
            msg.exec()
        except:
            pass
        
        return 1


if __name__ == "__main__":
    """
    Script entry point.
    
    When running: python main.py
    This block executes the main() function.
    """
    # Run main function and exit with its return code
    sys.exit(main())


# ========== NOTES ==========
"""
Application Architecture:

1. main.py (this file):
   - Entry point
   - Logging setup
   - Application lifecycle management
   
2. app/core/config.py:
   - Configuration settings
   - API URLs, timeouts, etc.
   
3. app/core/api_client.py:
   - HTTP client for REST API calls
   - Error handling
   
4. app/ui/main_window.py:
   - UI components
   - View layer (MVC)
   
5. app/controllers/chat_controller.py:
   - Business logic
   - Controller layer (MVC)
   - Connects UI and API

Flow:
User -> UI -> Controller -> API Client -> Backend API
                ↓              ↓
            Updates UI    Returns data

Best Practices Used:
- MVC architecture (separation of concerns)
- Async operations (non-blocking UI)
- Comprehensive error handling
- Detailed logging
- Configuration management
- Type hints (Python 3.11+)
- PEP8 style guide

Building Executable:
See README.md for PyInstaller instructions to create:
- AIAssistant.exe (Windows)
- AIAssistant (Linux/Mac)
"""
