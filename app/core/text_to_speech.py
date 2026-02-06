"""
Text-to-Speech Module
Converts assistant responses to speech
"""
import pyttsx3
from typing import Optional
import threading
import queue


class TextToSpeech:
    """Handles text-to-speech conversion using pyttsx3"""
    
    def __init__(self):
        self.engine: Optional[pyttsx3.Engine] = None
        self.enabled = True
        self.speaking = False
        self.speech_queue = queue.Queue()
        self.worker_thread = None
        self._initialize_engine()
        
    def _initialize_engine(self):
        """Initialize the TTS engine with settings"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure voice settings
            self.engine.setProperty('rate', 175)  # Speed of speech (default: 200)
            self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Try to set a better voice (female voice if available)
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find a female voice
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice if no female voice found
                    self.engine.setProperty('voice', voices[0].id)
                    
            print(f"✓ TTS engine initialized successfully")
            
        except Exception as e:
            print(f"✗ Failed to initialize TTS engine: {e}")
            self.engine = None
            
    def speak(self, text: str):
        """
        Speak the given text
        Uses a queue and worker thread to avoid blocking
        """
        if not self.enabled or not self.engine or not text:
            return
            
        # Clean the text
        text = text.strip()
        if not text:
            return
            
        # Add to queue
        self.speech_queue.put(text)
        
        # Start worker thread if not running
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.worker_thread.start()
            
    def _speech_worker(self):
        """Worker thread that processes speech queue"""
        while not self.speech_queue.empty():
            try:
                text = self.speech_queue.get(timeout=0.1)
                self._speak_sync(text)
            except queue.Empty:
                break
            except Exception as e:
                print(f"✗ TTS worker error: {e}")
                
    def _speak_sync(self, text: str):
        """Synchronously speak text (blocking)"""
        if not self.engine:
            return
            
        try:
            self.speaking = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.speaking = False
        except Exception as e:
            print(f"✗ TTS speak error: {e}")
            self.speaking = False
            
    def stop(self):
        """Stop speaking immediately"""
        if self.engine:
            try:
                self.engine.stop()
                self.speaking = False
                # Clear the queue
                while not self.speech_queue.empty():
                    try:
                        self.speech_queue.get_nowait()
                    except queue.Empty:
                        break
            except Exception as e:
                print(f"✗ TTS stop error: {e}")
                
    def toggle(self) -> bool:
        """Toggle TTS on/off, returns new state"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop()
        return self.enabled
        
    def set_enabled(self, enabled: bool):
        """Enable or disable TTS"""
        self.enabled = enabled
        if not enabled:
            self.stop()
            
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.speaking
        
    def set_rate(self, rate: int):
        """Set speech rate (words per minute, default: 200)"""
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except Exception as e:
                print(f"✗ Failed to set rate: {e}")
                
    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0)"""
        if self.engine:
            try:
                volume = max(0.0, min(1.0, volume))  # Clamp to 0.0-1.0
                self.engine.setProperty('volume', volume)
            except Exception as e:
                print(f"✗ Failed to set volume: {e}")
                
    def cleanup(self):
        """Clean up resources"""
        self.stop()
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
