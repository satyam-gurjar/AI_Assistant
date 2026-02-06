"""
Voice Input Handler - Continuous Listening Mode

Manages speech recognition with continuous listening.
Automatically detects when user stops speaking and processes the transcription.
"""

import logging
import threading
from typing import Optional

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    logging.warning("speech_recognition not installed. Voice input will not work.")

from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class VoiceInputHandler(QObject):
    """
    Handles voice input using speech recognition with continuous listening.
    
    NEW BEHAVIOR:
    - Click START once → Continuously listens
    - Detects silence (1.5 seconds) → Auto-processes and emits transcription
    - Keeps listening after each response
    - Click STOP to end the session
    
    Signals:
        transcription_ready: Emitted when speech is converted to text (str)
        error_occurred: Emitted when an error occurs (str)
        listening_started: Emitted when actively listening
    """
    
    # Signals
    transcription_ready = Signal(str)
    error_occurred = Signal(str)
    listening_started = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Check if speech_recognition is available
        if sr is None:
            logger.error("speech_recognition module not available")
            self.recognizer = None
            self.microphone = None
            return
            
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Configure recognizer for continuous listening
        self.recognizer.energy_threshold = 300  # Minimum audio energy to consider for recording
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.5  # Seconds of silence to mark end of phrase
        self.recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking audio
        
        # Recording state
        self.is_recording = False  # For backwards compatibility
        self.is_active = False  # Overall session active
        self.stop_listening = None  # Function to stop background listening
        self.listen_thread: Optional[threading.Thread] = None
        
        # Adjust for ambient noise on startup
        try:
            with self.microphone as source:
                logger.info("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Microphone ready for continuous voice input")
        except Exception as e:
            logger.error(f"Failed to initialize microphone: {e}")
            self.microphone = None
            
    def is_available(self) -> bool:
        """Check if voice input is available."""
        return self.recognizer is not None and self.microphone is not None
    
    def start_recording(self):
        """
        Start continuous listening session.
        Will keep listening until stop_recording() is called.
        """
        if not self.is_available():
            error_msg = "Voice input not available. Please install: pip install SpeechRecognition PyAudio"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return
            
        if self.is_active:
            logger.warning("Already in active listening session")
            return
            
        self.is_active = True
        self.is_recording = True  # For backwards compatibility
        
        # Start continuous listening in background thread
        self.listen_thread = threading.Thread(target=self._continuous_listen, daemon=True)
        self.listen_thread.start()
        
        logger.info("Started continuous listening session")
    
    def stop_recording(self):
        """Stop the continuous listening session."""
        if not self.is_active:
            return
            
        self.is_active = False
        self.is_recording = False  # For backwards compatibility
        
        # Stop background listening if active
        if self.stop_listening:
            self.stop_listening(wait_for_stop=False)
            self.stop_listening = None
            
        logger.info("Stopped continuous listening session")
    
    def _continuous_listen(self):
        """
        Continuous listening loop.
        Automatically detects speech, waits for silence, then processes.
        """
        try:
            with self.microphone as source:
                logger.info("🎤 Continuous listening active - speak anytime...")
                
                while self.is_active:
                    try:
                        # Emit signal that we're ready to listen
                        self.listening_started.emit()
                        
                        logger.info("👂 Listening for speech...")
                        
                        # Listen for audio with pause detection
                        # pause_threshold is set in __init__ (1.5 seconds)
                        audio = self.recognizer.listen(
                            source,
                            timeout=None,  # Wait indefinitely for speech
                            phrase_time_limit=30  # Max 30 seconds per phrase
                        )
                        
                        if not self.is_active:
                            logger.info("Session ended")
                            break
                        
                        logger.info("🔄 Processing speech...")
                        
                        # Recognize speech using Google Speech Recognition
                        text = self.recognizer.recognize_google(audio)
                        
                        if text and text.strip():
                            logger.info(f"✅ Transcribed: {text}")
                            self.transcription_ready.emit(text)
                        else:
                            logger.debug("Empty transcription")
                            
                    except sr.UnknownValueError:
                        # Could not understand audio - just continue listening
                        logger.debug("Could not understand audio, continuing...")
                        continue
                        
                    except sr.RequestError as e:
                        error_msg = f"Speech recognition service error: {e}"
                        logger.error(error_msg)
                        self.error_occurred.emit(error_msg)
                        # Continue listening despite error
                        continue
                        
                    except Exception as e:
                        if self.is_active:  # Only log if not intentionally stopped
                            logger.error(f"Error in continuous listening: {e}")
                        continue
                        
        except Exception as e:
            error_msg = f"Voice recording error: {e}"
            logger.exception(error_msg)
            self.error_occurred.emit(error_msg)
            
        finally:
            self.is_active = False
            self.is_recording = False
            logger.info("Continuous listening ended")


# ========== USAGE NOTES ==========
"""
Voice Input Requirements:

1. Install dependencies:
   pip install SpeechRecognition PyAudio

2. PyAudio installation issues:
   
   On Linux (Ubuntu/Debian):
   sudo apt-get install portaudio19-dev python3-pyaudio
   pip install PyAudio
   
   On macOS:
   brew install portaudio
   pip install PyAudio
   
   On Windows:
   pip install pipwin
   pipwin install pyaudio
   
3. Usage:
   handler = VoiceInputHandler()
   handler.transcription_ready.connect(on_text_ready)
   handler.start_recording()  # Start listening
   # User speaks...
   handler.stop_recording()   # Stop and transcribe

4. Alternative engines:
   - Google (default): Free, requires internet
   - Sphinx: Offline, less accurate
   - Wit.ai: Free API key required
   - Azure: Paid, very accurate
   
5. Microphone permissions:
   - Ensure app has microphone access
   - On macOS: System Preferences > Security > Microphone
   - On Windows: Settings > Privacy > Microphone
"""
