"""
Chat Controller Module for AI Assistant Application

This is the CONTROLLER layer in MVC architecture.
Handles all business logic and coordinates between UI and API.

Responsibilities:
- Handle user message submissions
- Make async API calls (prevent UI freezing)
- Update UI with responses
- Manage connection status
- Error handling and recovery

The controller sits between:
- UI (MainWindow) - displays information
- API Client - communicates with backend
"""

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal, QThread, Slot
from PySide6.QtWidgets import QApplication

from app.core.api_client import APIClient, APIResponse, APIStatus
from app.core.config import Config


# Configure logging for this module
logger = logging.getLogger(__name__)


class APIWorker(QThread):
    """
    Worker thread for making API calls asynchronously.
    
    This prevents the UI from freezing during API requests.
    Runs in a separate thread and emits signals when done.
    
    Qt best practice: Never block the main UI thread with network calls.
    
    Signals:
        response_received: Emitted when API call completes (APIResponse)
        error_occurred: Emitted if an error occurs (str: error_message)
    """
    
    # Signal emitted when API response is received
    response_received = Signal(APIResponse)
    
    # Signal emitted if an error occurs
    error_occurred = Signal(str)
    
    def __init__(self, api_client: APIClient, message: str, parent=None):
        """
        Initialize the API worker thread.
        
        Args:
            api_client: APIClient instance to use for requests
            message: User message to send to API
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.api_client = api_client
        self.message = message
        
        logger.debug(f"APIWorker created for message: {message[:50]}...")
    
    def run(self):
        """
        Execute the API call in the background thread.
        
        This method runs in a separate thread (not the UI thread).
        When finished, emits response_received signal with the result.
        
        Note: This method should NOT interact with UI directly.
        Use signals to communicate with the main thread.
        """
        try:
            logger.info("Making API call in background thread...")
            
            # Make the API call
            # This may take several seconds, but won't block the UI
            response = self.api_client.send_chat_message(self.message)
            
            # Emit signal with response
            # The main thread (controller) will receive this
            self.response_received.emit(response)
            
            logger.debug("API call completed, signal emitted")
        
        except Exception as e:
            # Catch any unexpected errors
            logger.exception(f"Error in API worker thread: {e}")
            self.error_occurred.emit(f"Unexpected error: {str(e)}")


class HealthCheckWorker(QThread):
    """
    Worker thread for checking API health asynchronously.
    
    Runs periodic health checks in the background to update
    connection status without blocking the UI.
    
    Signals:
        health_status: Emitted with health check result (bool: is_healthy)
    """
    
    # Signal emitted with health check result
    health_status = Signal(bool)
    
    def __init__(self, api_client: APIClient, parent=None):
        """
        Initialize the health check worker.
        
        Args:
            api_client: APIClient instance to use for health checks
            parent: Parent QObject
        """
        super().__init__(parent)
        self.api_client = api_client
    
    def run(self):
        """
        Execute the health check in background thread.
        
        Makes a quick API call to check if backend is responsive.
        """
        try:
            logger.debug("Checking API health...")
            
            # Make health check request
            response = self.api_client.check_health()
            
            # Emit result
            is_healthy = response.is_success()
            self.health_status.emit(is_healthy)
            
            logger.debug(f"Health check result: {'healthy' if is_healthy else 'unhealthy'}")
        
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.health_status.emit(False)


class ChatController(QObject):
    """
    Main controller for chat functionality.
    
    This is the CONTROLLER in MVC architecture.
    Coordinates between the UI (View) and backend API (Model).
    
    Responsibilities:
    1. Listen to UI signals (user actions)
    2. Validate user input
    3. Make API calls asynchronously
    4. Update UI with results
    5. Handle errors gracefully
    6. Manage connection status
    
    The controller does NOT:
    - Contain UI code (that's in MainWindow)
    - Make direct HTTP calls (that's in APIClient)
    - Store application config (that's in Config)
    """
    
    def __init__(self, main_window, parent=None):
        """
        Initialize the chat controller.
        
        Args:
            main_window: MainWindow instance (the UI)
            parent: Parent QObject
        """
        super().__init__(parent)
        
        # Store reference to UI window
        self.main_window = main_window
        
        # Create API client for backend communication
        self.api_client = APIClient()
        
        # Track current API worker (for async calls)
        self.current_worker: Optional[APIWorker] = None
        
        # Track health check worker
        self.health_worker: Optional[HealthCheckWorker] = None
        
        # Connect UI signals to controller methods
        self._connect_signals()
        
        # Check initial connection status
        self._check_connection()
        
        logger.info("ChatController initialized")
    
    def _connect_signals(self):
        """
        Connect UI signals to controller methods.
        
        Sets up event handlers for user actions.
        When user interacts with UI, these methods are called.
        """
        # Connect message_sent signal from UI
        # When user clicks Send, this calls handle_message_sent
        self.main_window.message_sent.connect(self.handle_message_sent)
        
        logger.debug("UI signals connected to controller")
    
    @Slot(str)
    def handle_message_sent(self, message: str):
        """
        Handle user message submission.
        
        Called when user sends a message via UI.
        This is the main entry point for message processing.
        
        Flow:
        1. Validate message
        2. Display user message in UI
        3. Disable input (prevent spam)
        4. Make async API call
        5. Wait for response (in background)
        6. Display AI response
        7. Re-enable input
        
        Args:
            message: User's message text
        """
        logger.info(f"Handling user message: {message[:50]}...")
        
        # Validate message
        if not message or not message.strip():
            logger.warning("Empty message received, ignoring")
            return
        
        if len(message) > Config.MAX_MESSAGE_LENGTH:
            error_msg = f"Message too long. Maximum {Config.MAX_MESSAGE_LENGTH} characters."
            self.main_window.show_error(error_msg)
            logger.warning(error_msg)
            return
        
        # Display user message in chat
        self.main_window.add_user_message(message)
        
        # Disable input while processing
        # Prevents user from sending multiple messages at once
        self.main_window.set_input_enabled(False)
        
        # Update status
        self.main_window.set_status("Sending...", Config.TEXT_SECONDARY)
        
        # Create worker thread for API call
        # This prevents UI from freezing during network request
        self.current_worker = APIWorker(self.api_client, message)
        
        # Connect worker signals to handler methods
        self.current_worker.response_received.connect(self._handle_api_response)
        self.current_worker.error_occurred.connect(self._handle_api_error)
        
        # When thread finishes, clean it up
        self.current_worker.finished.connect(self._cleanup_worker)
        
        # Start the background thread
        # The API call happens in background, UI remains responsive
        self.current_worker.start()
        
        logger.debug("API worker thread started")
    
    @Slot(APIResponse)
    def _handle_api_response(self, response: APIResponse):
        """
        Handle API response from worker thread.
        
        Called when API call completes (success or failure).
        Updates UI based on response status.
        
        Args:
            response: APIResponse object from API client
        """
        logger.info(f"Received API response: {response.status}")
        
        # Re-enable input
        self.main_window.set_input_enabled(True)
        
        if response.is_success():
            # Success: Extract AI reply and display it
            ai_reply = response.data.get("reply", "No response from AI")
            self.main_window.add_ai_message(ai_reply)
            
            # Update status
            self.main_window.set_status("Connected", Config.SUCCESS_COLOR)
            
            logger.info("AI response displayed successfully")
        
        else:
            # Error: Show error message to user
            self._handle_error_response(response)
    
    def _handle_error_response(self, response: APIResponse):
        """
        Handle error responses from API.
        
        Provides user-friendly error messages based on error type.
        
        Args:
            response: APIResponse object with error status
        """
        logger.warning(f"API error: {response.status} - {response.error}")
        
        # Determine appropriate error message based on status
        if response.status == APIStatus.TIMEOUT:
            error_msg = "Request timed out. Please try again."
            status_msg = "Timeout"
            
        elif response.status == APIStatus.CONNECTION_ERROR:
            error_msg = "Cannot connect to server. Please check your connection."
            status_msg = "Disconnected"
            
        elif response.status == APIStatus.AUTHENTICATION_ERROR:
            error_msg = "Authentication failed. Please check your API key in config.py"
            status_msg = "Auth Error"
            
        elif response.status == APIStatus.INVALID_RESPONSE:
            error_msg = "Server returned invalid response."
            status_msg = "Invalid Response"
            
        else:
            # Generic error
            error_msg = response.error or "An error occurred. Please try again."
            status_msg = "Error"
        
        # Show error in UI
        self.main_window.show_error(error_msg)
        self.main_window.set_status(status_msg, Config.ERROR_COLOR)
    
    @Slot(str)
    def _handle_api_error(self, error_message: str):
        """
        Handle unexpected errors from worker thread.
        
        Called if worker thread encounters an unexpected exception.
        
        Args:
            error_message: Error description
        """
        logger.error(f"API worker error: {error_message}")
        
        # Re-enable input
        self.main_window.set_input_enabled(True)
        
        # Show error
        self.main_window.show_error(error_message)
        self.main_window.set_status("Error", Config.ERROR_COLOR)
    
    def _cleanup_worker(self):
        """
        Clean up finished worker thread.
        
        Called automatically when worker thread finishes.
        Prevents memory leaks by properly deleting thread objects.
        """
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
            logger.debug("Worker thread cleaned up")
    
    def _check_connection(self):
        """
        Check API connection status.
        
        Makes a health check request to verify backend is accessible.
        Updates UI status bar with result.
        
        This runs asynchronously to avoid blocking UI.
        """
        logger.info("Checking API connection...")
        
        # Update status
        self.main_window.set_status("Connecting...", Config.TEXT_SECONDARY)
        
        # Create health check worker
        self.health_worker = HealthCheckWorker(self.api_client)
        
        # Connect signal
        self.health_worker.health_status.connect(self._handle_health_status)
        self.health_worker.finished.connect(self._cleanup_health_worker)
        
        # Start health check
        self.health_worker.start()
    
    @Slot(bool)
    def _handle_health_status(self, is_healthy: bool):
        """
        Handle health check result.
        
        Updates UI status bar based on health check result.
        
        Args:
            is_healthy: True if API is healthy, False otherwise
        """
        if is_healthy:
            self.main_window.set_status("Connected", Config.SUCCESS_COLOR)
            logger.info("API connection healthy")
        else:
            self.main_window.set_status("Disconnected", Config.ERROR_COLOR)
            logger.warning("API connection unhealthy")
    
    def _cleanup_health_worker(self):
        """Clean up health check worker thread."""
        if self.health_worker:
            self.health_worker.deleteLater()
            self.health_worker = None
    
    def cleanup(self):
        """
        Clean up controller resources.
        
        Call this when closing the application to properly
        release resources and close connections.
        """
        logger.info("Cleaning up ChatController...")
        
        # Wait for any running workers to finish
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.wait(1000)  # Wait max 1 second
        
        if self.health_worker and self.health_worker.isRunning():
            self.health_worker.wait(1000)
        
        # Close API client
        self.api_client.close()
        
        logger.info("ChatController cleanup completed")


# ========== USAGE NOTES ==========
"""
This is the CONTROLLER layer in MVC architecture.

The ChatController:
1. Listens to UI signals (user actions)
2. Validates input
3. Makes API calls (asynchronously)
4. Updates UI with results
5. Handles errors

Key design patterns used:

1. MVC Architecture:
   - Model: APIClient (data/backend)
   - View: MainWindow (UI)
   - Controller: ChatController (this file)

2. Signal-Slot Pattern (Qt):
   - UI emits signals
   - Controller has slots that handle signals
   - Decoupled communication

3. Worker Thread Pattern:
   - API calls run in background threads
   - UI stays responsive
   - No freezing during network operations

4. Separation of Concerns:
   - UI code in main_window.py
   - API code in api_client.py
   - Logic code here
   - Each component has single responsibility

To use:
    from app.controllers.chat_controller import ChatController
    from app.ui.main_window import MainWindow
    
    window = MainWindow()
    controller = ChatController(window)
    window.show()
"""
