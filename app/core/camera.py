"""
Camera Module

Handles webcam access and display.
Provides real-time camera feed in the UI.
"""

import logging
import cv2
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage, QPixmap
import numpy as np

logger = logging.getLogger(__name__)


class CameraThread(QThread):
    """
    Background thread for camera capture.
    
    WHAT IT DOES:
    - Opens webcam (camera 0)
    - Captures frames continuously
    - Emits frames as QImage signals
    - Handles camera errors
    """
    
    # Signal emitted with each camera frame
    frame_ready = Signal(QImage)
    
    # Signal emitted on error
    error_occurred = Signal(str)
    
    def __init__(self, camera_index=0):
        """
        Initialize camera thread.
        
        Args:
            camera_index: Camera device index (0 = default camera)
        """
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.capture = None
        
    def run(self):
        """
        Main thread loop - captures and emits frames.
        
        FLOW:
        1. Open camera
        2. Loop: Capture frame → Convert to QImage → Emit
        3. Close camera on stop
        """
        try:
            # STEP 1: Open camera
            logger.info(f"Opening camera {self.camera_index}...")
            self.capture = cv2.VideoCapture(self.camera_index)
            
            if not self.capture.isOpened():
                logger.error("Failed to open camera")
                self.error_occurred.emit("Could not open camera. Check if camera is available.")
                return
            
            # Set camera properties for better quality
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info("Camera opened successfully")
            self.running = True
            
            # STEP 2: Main capture loop
            while self.running:
                ret, frame = self.capture.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    continue
                
                # Convert BGR (OpenCV) to RGB (Qt)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Get frame dimensions
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                
                # Convert to QImage
                qt_image = QImage(
                    rgb_frame.data,
                    w, h,
                    bytes_per_line,
                    QImage.Format_RGB888
                )
                
                # Emit frame
                self.frame_ready.emit(qt_image)
                
                # Small delay to control frame rate
                self.msleep(33)  # ~30 FPS
            
        except Exception as e:
            logger.error(f"Camera error: {e}")
            self.error_occurred.emit(f"Camera error: {str(e)}")
            
        finally:
            # STEP 3: Cleanup
            self.stop()
    
    def stop(self):
        """
        Stop camera capture and release resources.
        
        WHAT IT DOES:
        - Stops the capture loop
        - Releases camera
        - Logs shutdown
        """
        logger.info("Stopping camera...")
        self.running = False
        
        if self.capture:
            self.capture.release()
            self.capture = None
        
        logger.info("Camera stopped")


class CameraManager:
    """
    Manages camera thread and provides easy interface.
    
    USAGE:
    manager = CameraManager()
    manager.frame_ready.connect(update_display)
    manager.start_camera()
    ...
    manager.stop_camera()
    """
    
    def __init__(self):
        """Initialize camera manager."""
        self.camera_thread = None
        self.is_running = False
        logger.info("CameraManager initialized")
    
    def start_camera(self, camera_index=0):
        """
        Start camera capture.
        
        Args:
            camera_index: Camera device index (0 = default)
            
        Returns:
            CameraThread: The camera thread object
        """
        if self.is_running:
            logger.warning("Camera already running")
            return self.camera_thread
        
        logger.info("Starting camera...")
        self.camera_thread = CameraThread(camera_index)
        self.camera_thread.start()
        self.is_running = True
        
        return self.camera_thread
    
    def stop_camera(self):
        """
        Stop camera capture.
        
        WHAT IT DOES:
        - Stops camera thread
        - Waits for thread to finish
        - Cleans up resources
        """
        if not self.is_running or not self.camera_thread:
            return
        
        logger.info("Stopping camera...")
        self.camera_thread.stop()
        self.camera_thread.wait(2000)  # Wait up to 2 seconds
        self.camera_thread = None
        self.is_running = False
        logger.info("Camera stopped")
    
    def is_camera_running(self):
        """Check if camera is currently running."""
        return self.is_running
