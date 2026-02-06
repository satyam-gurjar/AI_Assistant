import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QComboBox, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QTimer, Slot
from PySide6.QtGui import QColor, QPalette, QPixmap

logger = logging.getLogger(__name__)

# ==========================================================
# STYLES
# ==========================================================
PANEL = """
QFrame {
    background-color: #0b0b0b;
    border: 1px solid #151515;
    border-radius: 10px;
}
"""

SECTION_TITLE = "color:#6f6f6f;font-size:9pt;font-weight:bold;"
TEXT_MUTED = "color:#8a8a8a;font-size:9pt;"
TEXT_ACCENT = "color:#4c6fff;font-weight:bold;"

# ==========================================================
# CHAT
# ==========================================================
class MessageBubble(QFrame):
    def __init__(self, sender, text):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(3)

        sender_lbl = QLabel(sender.upper())
        sender_lbl.setStyleSheet("color:#4c6fff;font-size:8pt;font-weight:bold;")

        msg_lbl = QLabel(text)
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("color:#ddd;font-size:10pt;")

        layout.addWidget(sender_lbl)
        layout.addWidget(msg_lbl)


class ChatPanel(QFrame):
    message_sent = Signal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet(PANEL)

        layout = QVBoxLayout(self)

        title = QLabel("CHAT")
        title.setStyleSheet(SECTION_TITLE)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border:none;")

        self.container = QWidget()
        self.msg_layout = QVBoxLayout(self.container)
        self.msg_layout.addStretch()
        self.scroll.setWidget(self.container)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message...")
        self.input.setStyleSheet("""
            QLineEdit {
                background:#111;
                border:1px solid #1c1c1c;
                border-radius:6px;
                padding:8px;
                color:#eee;
            }
        """)

        send = QPushButton("SEND")
        send.setStyleSheet("""
            QPushButton {
                background:#4c6fff;
                color:white;
                border-radius:6px;
                padding:8px 14px;
                font-weight:bold;
            }
        """)

        send.clicked.connect(self._send)
        self.input.returnPressed.connect(self._send)

        input_row = QHBoxLayout()
        input_row.addWidget(self.input)
        input_row.addWidget(send)

        layout.addWidget(title)
        layout.addWidget(self.scroll, 1)
        layout.addLayout(input_row)

    def _send(self):
        text = self.input.text().strip()
        if text:
            self.message_sent.emit(text)
            self.input.clear()

    def add_message(self, sender, text):
        self.msg_layout.insertWidget(
            self.msg_layout.count() - 1,
            MessageBubble(sender, text)
        )
        self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()
        )

# ==========================================================
# STATUS
# ==========================================================
class StatusIndicator(QWidget):
    def __init__(self, label):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(label)
        self.label.setStyleSheet(TEXT_MUTED)

        self.value = QLabel("DISCONNECTED")
        self.value.setStyleSheet("color:#ff5252;font-weight:bold;")

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.value)

    def set_connected(self, ok):
        self.value.setText("CONNECTED" if ok else "DISCONNECTED")
        self.value.setStyleSheet(
            "color:#4c6fff;font-weight:bold;" if ok
            else "color:#ff5252;font-weight:bold;"
        )

# ==========================================================
# MAIN WINDOW
# ==========================================================
class VoiceAgentWindow(QMainWindow):

    voice_input_started = Signal()
    voice_input_stopped = Signal()
    text_message_sent = Signal(str)
    disconnect_requested = Signal()
    tts_toggled = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ARIS - Local Voice Assistant & Agent")
        self.resize(1440, 900)
        
        self.is_recording = False
        self.is_connected = False
        self.camera_manager = None

        self._build_ui()
        self._apply_theme()

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()
        
        # Start camera automatically
        self._start_camera()

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------
    def _header(self):
        bar = QFrame()
        bar.setFixedHeight(50)
        bar.setStyleSheet("background:#000;border-bottom:1px solid #151515;")

        layout = QHBoxLayout(bar)

        title = QLabel("ARIS - Local Voice Assistant & Agent")
        title.setStyleSheet("color:#7aa2ff;font-size:14pt;font-weight:bold;")

        # Store disconnect button as instance variable
        self.disconnect_btn = QPushButton("Disconnected")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background:#666;
                color:white;
                border-radius:6px;
                padding:6px 14px;
            }
        """)
        self.disconnect_btn.clicked.connect(self._on_disconnect_clicked)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.disconnect_btn)
        return bar

    # --------------------------------------------------
    # UI BUILD
    # --------------------------------------------------
    def _build_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)

        root_layout.addWidget(self._header())

        body = QHBoxLayout()
        root_layout.addLayout(body, 1)

        # ================= LEFT SIDE =================
        left = QVBoxLayout()

        # VIDEO (FULL HEIGHT)
        video = QFrame()
        video.setStyleSheet(PANEL)
        v = QVBoxLayout(video)
        v.addWidget(QLabel("VIDEO"))

        self.video_label = QLabel("Waiting for video track")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("color:#666;")
        v.addWidget(self.video_label, 1)

        # CHAT BELOW VIDEO
        self.chat = ChatPanel()
        self.chat.message_sent.connect(self.text_message_sent.emit)

        left.addWidget(video, 5)
        left.addWidget(self.chat, 3)

        # ================= RIGHT SIDE =================
        right = QVBoxLayout()

        settings = self._info_card("SETTINGS", [
            ("Room", "aris-room"),
            ("Participant", "user-7378")
        ])

        status = QFrame()
        status.setStyleSheet(PANEL)
        s = QVBoxLayout(status)
        s.addWidget(QLabel("STATUS"))
        self.room_status = StatusIndicator("Room connected")
        self.agent_status = StatusIndicator("Agent connected")
        s.addWidget(self.room_status)
        s.addWidget(self.agent_status)

        camera = QFrame()
        camera.setStyleSheet(PANEL)
        c = QVBoxLayout(camera)
        c.addWidget(QLabel("CAMERA"))
        self.camera_preview = QLabel()
        self.camera_preview.setFixedHeight(320)  # Increased from 140
        self.camera_preview.setStyleSheet("background:#000;border-radius:8px;color:#666;")
        self.camera_preview.setAlignment(Qt.AlignCenter)
        self.camera_preview.setText("Camera Preview\n(Camera access coming soon)")
        c.addWidget(self.camera_preview)

        clock = self._clock_card()
        
        # Voice Control Buttons
        voice_frame = QFrame()
        voice_frame.setStyleSheet(PANEL)
        voice_layout = QVBoxLayout(voice_frame)
        
        voice_title_layout = QHBoxLayout()
        voice_title = QLabel("VOICE CONTROL")
        voice_title.setStyleSheet(SECTION_TITLE)
        voice_title_layout.addWidget(voice_title)
        
        # Listening indicator
        self.listening_indicator = QLabel("⚫ Ready")
        self.listening_indicator.setStyleSheet("color:#666;font-size:9pt;")
        voice_title_layout.addStretch()
        voice_title_layout.addWidget(self.listening_indicator)
        voice_layout.addLayout(voice_title_layout)
        
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ START LISTENING")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background:#4c6fff;
                color:white;
                border-radius:6px;
                font-size:11pt;
                font-weight:bold;
            }
            QPushButton:disabled {
                background:#333;
                color:#666;
            }
        """)
        self.start_btn.clicked.connect(self._on_start_voice)
        
        self.stop_btn = QPushButton("■ STOP")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background:#ff5252;
                color:white;
                border-radius:6px;
                font-size:11pt;
                font-weight:bold;
            }
            QPushButton:disabled {
                background:#333;
                color:#666;
            }
        """)
        self.stop_btn.clicked.connect(self._on_stop_voice)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        voice_layout.addLayout(btn_layout)
        
        # TTS Toggle Button
        tts_layout = QHBoxLayout()
        tts_label = QLabel("🔊 Voice Output:")
        tts_label.setStyleSheet("color:#8a8a8a;font-size:10pt;")
        
        self.tts_btn = QPushButton("ON")
        self.tts_btn.setCheckable(True)
        self.tts_btn.setChecked(True)  # Enabled by default
        self.tts_btn.setFixedSize(60, 30)
        self.tts_btn.setStyleSheet("""
            QPushButton {
                background:#4c6fff;
                color:white;
                border-radius:6px;
                font-weight:bold;
            }
            QPushButton:checked {
                background:#4c6fff;
            }
            QPushButton:!checked {
                background:#333;
                color:#666;
            }
        """)
        self.tts_btn.clicked.connect(self._on_tts_toggle)
        
        tts_layout.addWidget(tts_label)
        tts_layout.addStretch()
        tts_layout.addWidget(self.tts_btn)
        voice_layout.addLayout(tts_layout)

        right.addWidget(settings)
        right.addWidget(status)
        right.addWidget(camera)
        right.addWidget(voice_frame)
        right.addWidget(clock)
        right.addStretch()

        body.addLayout(left, 3)
        body.addLayout(right, 1)

        self.setCentralWidget(root)

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------
    def _info_card(self, title, rows):
        frame = QFrame()
        frame.setStyleSheet(PANEL)
        l = QVBoxLayout(frame)
        l.addWidget(QLabel(title))
        for k, v in rows:
            r = QHBoxLayout()
            r.addWidget(QLabel(k))
            val = QLabel(v)
            val.setStyleSheet(TEXT_ACCENT)
            r.addStretch()
            r.addWidget(val)
            l.addLayout(r)
        return frame

    def _clock_card(self):
        frame = QFrame()
        frame.setStyleSheet(PANEL)
        l = QVBoxLayout(frame)

        self.time_label = QLabel()
        self.time_label.setStyleSheet("font-size:22pt;font-weight:bold;")

        self.date_label = QLabel()
        self.date_label.setStyleSheet(TEXT_MUTED)

        self.weather_label = QLabel("--°C\nLoading location...")
        self.weather_label.setStyleSheet("color:#aaa;")

        l.addWidget(self.time_label)
        l.addWidget(self.date_label)
        l.addSpacing(6)
        l.addWidget(self.weather_label)
        return frame

    # --------------------------------------------------
    def _update_clock(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        self.date_label.setText(now.strftime("%A, %B %d, %Y"))

    def _apply_theme(self):
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#000"))
        pal.setColor(QPalette.WindowText, QColor("#eee"))
        self.setPalette(pal)

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------
    def add_user_message(self, text):
        self.chat.add_message("User", text)

    def add_agent_message(self, text):
        self.chat.add_message("Agent", text)

    def set_room_connected(self, ok):
        self.room_status.set_connected(ok)

    def set_agent_connected(self, ok):
        self.agent_status.set_connected(ok)
        self.is_connected = ok
        self._update_connection_button(ok)
    
    def _update_connection_button(self, connected):
        """Update disconnect button appearance based on connection state"""
        if connected:
            self.disconnect_btn.setText("Disconnect")
            self.disconnect_btn.setStyleSheet("""
                QPushButton {
                    background:#ff5252;
                    color:white;
                    border-radius:6px;
                    padding:6px 14px;
                }
                QPushButton:hover {
                    background:#ff6b6b;
                }
            """)
        else:
            self.disconnect_btn.setText("Disconnected")
            self.disconnect_btn.setStyleSheet("""
                QPushButton {
                    background:#666;
                    color:#aaa;
                    border-radius:6px;
                    padding:6px 14px;
                }
            """)
    
    def update_weather(self, temp: str, condition: str, location: str):
        """Update weather display with dynamic data"""
        self.weather_label.setText(f"{temp} • {condition}\n{location}")
    
    def show_error(self, message: str):
        """Show error message in chat"""
        self.add_agent_message(f"Error: {message}")
    
    # --------------------------------------------------
    # VOICE CONTROL
    # --------------------------------------------------
    def _on_start_voice(self):
        """Handle Start button click - begins continuous listening"""
        self.is_recording = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.listening_indicator.setText("🔴 Listening...")
        self.listening_indicator.setStyleSheet("color:#ff5252;font-size:9pt;font-weight:bold;")
        self.voice_input_started.emit()
        self.add_agent_message("Listening continuously... Speak anytime!")
        logger.info("Continuous voice listening started")
    
    def _on_stop_voice(self):
        """Handle Stop button click - ends continuous listening"""
        self.is_recording = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.listening_indicator.setText("⚫ Ready")
        self.listening_indicator.setStyleSheet("color:#666;font-size:9pt;")
        self.voice_input_stopped.emit()
        self.add_agent_message("Listening stopped.")
        logger.info("Continuous voice listening stopped")
    
    def _on_tts_toggle(self):
        """Handle TTS toggle button"""
        enabled = self.tts_btn.isChecked()
        self.tts_btn.setText("ON" if enabled else "OFF")
        self.tts_toggled.emit(enabled)
        logger.info(f"TTS {'enabled' if enabled else 'disabled'}")
    
    # --------------------------------------------------
    # CLEANUP
    # --------------------------------------------------
    def closeEvent(self, event):
        """Cleanup resources on close"""
        self.clock_timer.stop()
        self._stop_camera()
        super().closeEvent(event)
    
    # --------------------------------------------------
    # CAMERA METHODS
    # --------------------------------------------------
    def _start_camera(self):
        """Start camera capture and display"""
        try:
            from app.core.camera import CameraManager
            
            self.camera_manager = CameraManager()
            camera_thread = self.camera_manager.start_camera()
            
            if camera_thread:
                camera_thread.frame_ready.connect(self._update_camera_frame)
                camera_thread.error_occurred.connect(self._on_camera_error)
                logger.info("Camera started successfully")
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            self.camera_preview.setText(f"Camera Error\n{str(e)}")
    
    def _stop_camera(self):
        """Stop camera capture"""
        if self.camera_manager:
            self.camera_manager.stop_camera()
            self.camera_manager = None
            logger.info("Camera stopped")
    
    @Slot(object)
    def _update_camera_frame(self, qimage):
        """Update camera preview with new frame"""
        # Scale image to fit preview while maintaining aspect ratio
        scaled_pixmap = QPixmap.fromImage(qimage).scaled(
            self.camera_preview.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_preview.setPixmap(scaled_pixmap)
    
    @Slot(str)
    def _on_camera_error(self, error_msg):
        """Handle camera errors"""
        logger.error(f"Camera error: {error_msg}")
        self.camera_preview.setText(f"Camera Error\n{error_msg}")
    
    # --------------------------------------------------
    # DISCONNECT BUTTON HANDLER
    # --------------------------------------------------
    def _on_disconnect_clicked(self):
        """Handle disconnect button click"""
        if self.is_connected:
            # User wants to disconnect
            logger.info("User requested disconnect")
            self.disconnect_requested.emit()
            self._update_connection_button(False)
        else:
            # Already disconnected, do nothing or show message
            logger.info("Already disconnected")
