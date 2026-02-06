"""
Voice Agent Controller

Handles voice input, API calls, and UI updates for the voice agent interface.
"""

import logging
from typing import Optional

from PySide6.QtCore import QObject, Signal, QThread, Slot

from app.core.api_client import APIClient, APIResponse, APIStatus
from app.core.config import Config
from app.core.voice_input import VoiceInputHandler
from app.core.text_to_speech import TextToSpeech


logger = logging.getLogger(__name__)


class APIWorker(QThread):
    """Worker thread for async API calls."""
    
    response_received = Signal(APIResponse)
    error_occurred = Signal(str)
    
    def __init__(self, api_client: APIClient, message: str, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.message = message
    
    def run(self):
        """Execute API call in background thread."""
        try:
            logger.info("Making API call in background thread...")
            response = self.api_client.send_chat_message(self.message)
            self.response_received.emit(response)
        except Exception as e:
            logger.exception(f"Error in API worker: {e}")
            self.error_occurred.emit(str(e))


class VoiceAgentController(QObject):
    """
    Controller for voice agent interface.
    
    Manages:
    - Voice input capture
    - Speech-to-text conversion
    - API communication
    - UI updates
    """
    
    def __init__(self, window, parent=None):
        super().__init__(parent)
        
        self.window = window
        self.api_client = APIClient()
        
        # Voice input handler
        self.voice_handler = VoiceInputHandler()
        
        # Text-to-speech handler
        self.tts = TextToSpeech()
        
        # Current API worker
        self.current_worker: Optional[APIWorker] = None
        
        # Connect signals
        self._connect_signals()
        
        # Check initial connection
        self._check_connection()
        
        # Show initial greeting
        self.window.add_agent_message("Hey, how can I help you today?")
        
        logger.info("VoiceAgentController initialized")
        
    def _connect_signals(self):
        """Connect all signals from UI and voice handler."""
        
        # Voice button signals
        self.window.voice_input_started.connect(self._on_voice_start)
        self.window.voice_input_stopped.connect(self._on_voice_stop)
        self.window.stop_all_requested.connect(self._on_stop_all)
        
        # Text chat signal
        self.window.text_message_sent.connect(self._on_text_message)
        
        # Disconnect button signal
        self.window.disconnect_requested.connect(self._on_disconnect_requested)
        
        # TTS toggle signal
        self.window.tts_toggled.connect(self._on_tts_toggle)
        
        # Voice handler signals
        if self.voice_handler.is_available():
            self.voice_handler.transcription_ready.connect(self._on_transcription_ready)
            self.voice_handler.error_occurred.connect(self._on_voice_error)
            self.voice_handler.listening_started.connect(self._on_listening_started)
        else:
            logger.warning("Voice input not available")
            self.window.show_error("Voice input not available. Install: pip install SpeechRecognition PyAudio")
        
        logger.debug("Signals connected")
        
    @Slot()
    def _on_voice_start(self):
        """Handle voice input start."""
        logger.info("Voice input started by user")
        
        if not self.voice_handler.is_available():
            self.window.show_error("Voice input not available")
            return
            
        # Start recording
        self.voice_handler.start_recording()
        
    @Slot()
    def _on_voice_stop(self):
        """Handle voice input stop."""
        logger.info("Voice input stopped by user")
        
        if not self.voice_handler.is_available():
            return
            
        # Stop recording (transcription will be emitted via signal)
        self.voice_handler.stop_recording()
        
    @Slot()
    def _on_listening_started(self):
        """
        Handle when voice handler starts listening for speech.
        
        INTERRUPTION LOGIC:
        - If TTS is currently speaking, stop it
        - This allows user to interrupt the assistant
        """
        if self.tts.is_speaking():
            logger.info("User speaking - interrupting TTS")
            self.tts.stop()
    
    @Slot(str)
    def _on_transcription_ready(self, text: str):
        """Handle transcribed text from voice input."""
        logger.info(f"Transcription ready: {text}")
        
        if not text or not text.strip():
            logger.warning("Empty transcription")
            return
            
        # Display user message
        self.window.add_user_message(text)
        
        # Send to API
        self._send_to_api(text)
        
    @Slot(str)
    def _on_voice_error(self, error_message: str):
        """Handle voice input error."""
        logger.error(f"Voice error: {error_message}")
        self.window.show_error(error_message)
    
    @Slot(str)
    def _on_text_message(self, text: str):
        """Handle text message from chat panel."""
        logger.info(f"Text message from chat: {text}")
        
        if not text or not text.strip():
            logger.warning("Empty message")
            return
        
        # Display user message
        self.window.add_user_message(text)
        
        # Send to API
        self._send_to_api(text)
        
    def _send_to_api(self, message: str):
        """Send message to API asynchronously."""
        logger.info(f"Sending message to API: {message[:50]}...")
        
        # Create worker thread
        self.current_worker = APIWorker(self.api_client, message)
        
        # Connect signals
        self.current_worker.response_received.connect(self._handle_api_response)
        self.current_worker.error_occurred.connect(self._handle_api_error)
        self.current_worker.finished.connect(self._cleanup_worker)
        
        # Start worker
        self.current_worker.start()
        
    @Slot(APIResponse)
    def _handle_api_response(self, response: APIResponse):
        """Handle API response."""
        logger.info(f"Received API response: {response.status}")
        
        if response.is_success():
            # Extract AI reply (server returns 'response' field)
            ai_reply = response.data.get("response", response.data.get("reply", "No response"))
            self.window.add_agent_message(ai_reply)
            
            # Speak the response
            self.tts.speak(ai_reply)
            
            # Update status
            self.window.set_agent_connected(True)
            
        else:
            # Handle error
            self._handle_error_response(response)
            
    def _handle_error_response(self, response: APIResponse):
        """Handle API error response."""
        logger.warning(f"API error: {response.status}")
        
        if response.status == APIStatus.TIMEOUT:
            error_msg = "Request timed out"
        elif response.status == APIStatus.CONNECTION_ERROR:
            error_msg = "Cannot connect to server"
        elif response.status == APIStatus.AUTHENTICATION_ERROR:
            error_msg = "Authentication failed"
        else:
            error_msg = response.error or "Unknown error"
            
            # Check for specific OpenAI errors
            if "429" in str(error_msg) or "quota" in str(error_msg).lower():
                error_msg = "⚠️ OpenAI Quota Exceeded\n\nYour API key has run out of credits or exceeded the quota.\n\nFix this:\n1. Go to platform.openai.com/account/billing\n2. Add payment method or check usage\n3. Ensure billing is enabled for your API key"
            elif "401" in str(error_msg) or "invalid" in str(error_msg).lower():
                error_msg = "⚠️ Invalid API Key\n\nYour OpenAI API key is invalid or expired.\n\nFix this:\n1. Go to platform.openai.com/api-keys\n2. Generate a new API key\n3. Update Server/.env file"
            
        self.window.show_error(error_msg)
        self.window.set_agent_connected(False)
        
    @Slot(str)
    def _handle_api_error(self, error_message: str):
        """Handle unexpected API error."""
        logger.error(f"API error: {error_message}")
        self.window.show_error(error_message)
        self.window.set_agent_connected(False)
        
    def _cleanup_worker(self):
        """Clean up finished worker thread."""
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
            
    def _check_connection(self):
        """Check API connection status."""
        logger.info("Checking API connection...")
        
        # Try to check health
        try:
            response = self.api_client.check_health()
            if response.is_success():
                self.window.set_room_connected(True)
                self.window.set_agent_connected(True)
                logger.info("API connected")
            else:
                self.window.set_room_connected(False)
                self.window.set_agent_connected(False)
                logger.warning("API not connected")
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            self.window.set_room_connected(False)
            self.window.set_agent_connected(False)
            
    @Slot(bool)
    def _on_tts_toggle(self, enabled: bool):
        """Handle TTS toggle button."""
        logger.info(f"TTS toggled: {enabled}")
        self.tts.set_enabled(enabled)
        if not enabled:
            self.tts.stop()
    
    @Slot()
    def _on_stop_all(self):
        """Handle stop button - stops both voice input and TTS."""
        logger.info("Stop all requested")
        
        # Stop voice input
        if self.voice_handler.is_available():
            self.voice_handler.stop_recording()
        
        # Stop TTS immediately
        self.tts.stop()
    
    def _on_disconnect_requested(self):
        """
        Handle disconnect button click.
        
        WHAT IT DOES:
        - Stops voice input
        - Disconnects from server
        - Updates UI status
        - Shows disconnected message
        """
        logger.info("Disconnect requested by user")
        
        # Stop voice input if active
        if self.voice_handler.is_available():
            self.voice_handler.stop_recording()
        
        # Stop TTS if speaking
        self.tts.stop()
        
        # Stop any running API call
        if self.current_worker and self.current_worker.isRunning():
            logger.info("Stopping active API call...")
            self.current_worker.wait(1000)
        
        # Update UI
        self.window.set_room_connected(False)
        self.window.set_agent_connected(False)
        self.window.add_agent_message("Disconnected. Refresh to reconnect.")
        
        logger.info("Disconnected successfully")
            
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up VoiceAgentController...")
        
        # Stop voice input
        if self.voice_handler.is_available():
            self.voice_handler.stop_recording()
        
        # Stop and cleanup TTS
        self.tts.cleanup()
        
        # Wait for worker
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.wait(1000)
            
        # Close API client
        self.api_client.close()
        
        logger.info("Cleanup completed")
