"""
Main Window UI Module for AI Assistant Application

This module contains the main window UI components using PySide6 (Qt).
Implements a dark-themed, modern chat interface with:
- Chat message display area
- Text input box
- Send button
- Status bar for connection status

This is the VIEW layer in MVC architecture.
UI logic only - no business logic here.
"""

from typing import List, Tuple
import logging

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QScrollArea,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor, QColor, QPalette

from app.core.config import Config


# Configure logging for this module
logger = logging.getLogger(__name__)


class MessageWidget(QFrame):
    """
    Custom widget for displaying a single chat message.
    
    Creates a styled message bubble that distinguishes between
    user messages and AI responses.
    
    Attributes:
        is_user: Boolean indicating if message is from user
        message_text: The actual message content
    """
    
    def __init__(self, message: str, is_user: bool, parent=None):
        """
        Initialize a message bubble widget.
        
        Args:
            message: The message text to display
            is_user: True if message from user, False if from AI
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.is_user = is_user
        self.message_text = message
        
        # Set up the message bubble UI
        self._setup_ui()
    
    def _setup_ui(self):
        """
        Set up the message bubble appearance.
        
        Creates a styled frame with appropriate colors
        based on message sender (user vs AI).
        """
        # Create layout for message content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)  # Padding inside bubble
        
        # Create label for message text
        message_label = QLabel(self.message_text)
        message_label.setWordWrap(True)  # Allow text to wrap to multiple lines
        message_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse  # Allow users to select and copy text
        )
        
        # Set font
        font = QFont()
        font.setPointSize(10)
        message_label.setFont(font)
        
        # Add label to layout
        layout.addWidget(message_label)
        
        # Style the message bubble based on sender
        if self.is_user:
            # User messages: Blue background, align right
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {Config.USER_MESSAGE_BG};
                    color: {Config.TEXT_PRIMARY};
                    border-radius: 12px;
                    padding: 8px;
                }}
                QLabel {{
                    color: {Config.TEXT_PRIMARY};
                }}
            """)
        else:
            # AI messages: Gray background, align left
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {Config.AI_MESSAGE_BG};
                    color: {Config.TEXT_PRIMARY};
                    border-radius: 12px;
                    padding: 8px;
                    border: 1px solid #3d3d3d;
                }}
                QLabel {{
                    color: {Config.TEXT_PRIMARY};
                }}
            """)
        
        # Set size policy to allow proper sizing
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)


class ChatArea(QWidget):
    """
    Chat display area widget.
    
    Manages the scrollable area where all chat messages are displayed.
    Handles adding new messages and auto-scrolling.
    
    This widget contains all message bubbles in a vertical layout.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the chat display area.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # List to keep track of all message widgets
        self.messages: List[MessageWidget] = []
        
        # Set up the chat area UI
        self._setup_ui()
    
    def _setup_ui(self):
        """
        Set up the chat area layout and scroll functionality.
        
        Creates a scrollable area with a vertical layout
        for stacking message bubbles.
        """
        # Main layout for this widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create scroll area for messages
        # This allows scrolling when messages exceed visible area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow content to resize
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # No horizontal scroll
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Vertical scroll when needed
        
        # Style the scroll area
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {Config.DARK_BACKGROUND};
            }}
            QScrollBar:vertical {{
                background-color: {Config.DARK_BACKGROUND};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #666666;
            }}
        """)
        
        # Create container widget for messages
        self.messages_container = QWidget()
        
        # Create vertical layout for stacking messages
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(15, 15, 15, 15)  # Outer padding
        self.messages_layout.setSpacing(12)  # Space between messages
        self.messages_layout.addStretch()  # Push messages to top initially
        
        # Set container as scroll area's widget
        self.scroll_area.setWidget(self.messages_container)
        
        # Add scroll area to main layout
        main_layout.addWidget(self.scroll_area)
    
    def add_message(self, message: str, is_user: bool):
        """
        Add a new message to the chat area.
        
        Creates a message bubble and adds it to the layout.
        Automatically scrolls to show the new message.
        
        Args:
            message: The message text to display
            is_user: True if message from user, False if from AI
        """
        # Create message widget
        message_widget = MessageWidget(message, is_user)
        
        # Add to list
        self.messages.append(message_widget)
        
        # Insert before the stretch (keeps messages at top)
        # Count - 1 because stretch is last item
        self.messages_layout.insertWidget(
            self.messages_layout.count() - 1,
            message_widget,
            alignment=Qt.AlignRight if is_user else Qt.AlignLeft
        )
        
        # Scroll to bottom to show new message
        # Use QTimer to ensure layout is updated first
        QTimer.singleShot(100, self._scroll_to_bottom)
        
        logger.debug(f"Added {'user' if is_user else 'AI'} message: {message[:50]}...")
    
    def _scroll_to_bottom(self):
        """
        Scroll the chat area to the bottom.
        
        Called automatically after adding a new message
        to ensure the latest message is visible.
        """
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_messages(self):
        """
        Clear all messages from the chat area.
        
        Removes all message widgets and resets the display.
        """
        # Remove all message widgets
        for message_widget in self.messages:
            self.messages_layout.removeWidget(message_widget)
            message_widget.deleteLater()
        
        # Clear the list
        self.messages.clear()
        
        logger.info("Chat area cleared")


class MainWindow(QMainWindow):
    """
    Main application window.
    
    This is the primary UI window containing:
    - Chat display area
    - Message input box
    - Send button
    - Status bar
    
    Emits signals when user takes actions (sending messages).
    The controller listens to these signals.
    
    Signals:
        message_sent: Emitted when user sends a message (str: message_text)
    """
    
    # Qt signal emitted when user sends a message
    # The controller will connect to this signal
    message_sent = Signal(str)
    
    def __init__(self):
        """
        Initialize the main window.
        
        Sets up the entire UI including all widgets and layouts.
        """
        super().__init__()
        
        logger.info("Initializing MainWindow")
        
        # Set up the UI
        self._setup_ui()
        
        # Apply dark theme
        self._apply_theme()
    
    def _setup_ui(self):
        """
        Set up the main window UI components.
        
        Creates all widgets, layouts, and arranges them properly.
        This is called once during initialization.
        """
        # Set window properties
        self.setWindowTitle(Config.APP_NAME)
        self.setGeometry(100, 100, Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)
        self.setMinimumSize(Config.WINDOW_MIN_WIDTH, Config.WINDOW_MIN_HEIGHT)
        
        # Create central widget (required for QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create chat area (where messages are displayed)
        self.chat_area = ChatArea()
        main_layout.addWidget(self.chat_area, stretch=1)  # Takes most space
        
        # Create input area (text box + send button)
        input_area = self._create_input_area()
        main_layout.addWidget(input_area)
        
        # Create status bar at bottom
        self._create_status_bar()
        
        logger.debug("UI setup completed")
    
    def _create_input_area(self) -> QWidget:
        """
        Create the message input area.
        
        Contains:
        - Text input box for typing messages
        - Send button
        
        Returns:
            QWidget: Widget containing input components
        """
        # Container widget for input area
        input_widget = QWidget()
        input_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {Config.DARK_SURFACE};
                border-top: 1px solid #3d3d3d;
            }}
        """)
        
        # Horizontal layout for text box + button
        layout = QHBoxLayout(input_widget)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Create text input box
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Type your message here...")
        self.input_box.setMaximumHeight(100)  # Limit height
        self.input_box.setMinimumHeight(40)
        
        # Set font for input box
        font = QFont()
        font.setPointSize(10)
        self.input_box.setFont(font)
        
        # Style the input box
        self.input_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Config.DARK_BACKGROUND};
                color: {Config.TEXT_PRIMARY};
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 8px;
            }}
            QTextEdit:focus {{
                border: 1px solid {Config.DARK_ACCENT};
            }}
        """)
        
        # Create send button
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumSize(80, 40)
        self.send_button.setCursor(Qt.PointingHandCursor)  # Hand cursor on hover
        
        # Style the send button
        self.send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Config.DARK_ACCENT};
                color: {Config.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #0086d6;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #888888;
            }}
        """)
        
        # Connect button click to send method
        self.send_button.clicked.connect(self._on_send_clicked)
        
        # Add widgets to layout
        layout.addWidget(self.input_box, stretch=1)  # Text box takes most space
        layout.addWidget(self.send_button)
        
        return input_widget
    
    def _create_status_bar(self):
        """
        Create and configure the status bar.
        
        The status bar shows connection status at the bottom
        of the window (Connected / Disconnected / Connecting...).
        """
        # Qt status bar (built into QMainWindow)
        self.status_bar = self.statusBar()
        
        # Create status label
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {Config.TEXT_SECONDARY};
                padding: 5px;
            }}
        """)
        
        # Add label to status bar
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Style the status bar
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {Config.DARK_SURFACE};
                color: {Config.TEXT_SECONDARY};
                border-top: 1px solid #3d3d3d;
            }}
        """)
    
    def _apply_theme(self):
        """
        Apply dark theme to the entire application.
        
        Sets the color palette for the window and all child widgets.
        This creates a consistent dark theme throughout the app.
        """
        # Get application palette
        palette = self.palette()
        
        # Set color roles for dark theme
        palette.setColor(QPalette.Window, QColor(Config.DARK_BACKGROUND))
        palette.setColor(QPalette.WindowText, QColor(Config.TEXT_PRIMARY))
        palette.setColor(QPalette.Base, QColor(Config.DARK_SURFACE))
        palette.setColor(QPalette.AlternateBase, QColor(Config.DARK_BACKGROUND))
        palette.setColor(QPalette.Text, QColor(Config.TEXT_PRIMARY))
        palette.setColor(QPalette.Button, QColor(Config.DARK_SURFACE))
        palette.setColor(QPalette.ButtonText, QColor(Config.TEXT_PRIMARY))
        palette.setColor(QPalette.Highlight, QColor(Config.DARK_ACCENT))
        palette.setColor(QPalette.HighlightedText, QColor(Config.TEXT_PRIMARY))
        
        # Apply palette to window
        self.setPalette(palette)
        
        logger.debug("Dark theme applied")
    
    def _on_send_clicked(self):
        """
        Handle send button click event.
        
        Called when user clicks the Send button.
        Extracts message text and emits signal for controller to handle.
        """
        # Get message text from input box
        message = self.input_box.toPlainText().strip()
        
        # Check if message is not empty
        if message:
            # Check message length
            if len(message) > Config.MAX_MESSAGE_LENGTH:
                self.show_error(
                    f"Message too long. Maximum {Config.MAX_MESSAGE_LENGTH} characters."
                )
                return
            
            # Clear input box
            self.input_box.clear()
            
            # Emit signal with message
            # The controller will handle this
            self.message_sent.emit(message)
            
            logger.debug(f"Message sent signal emitted: {message[:50]}...")
    
    # ========== PUBLIC METHODS (Called by Controller) ==========
    
    def add_user_message(self, message: str):
        """
        Add a user message to the chat.
        
        Called by the controller after user sends a message.
        
        Args:
            message: User's message text
        """
        self.chat_area.add_message(message, is_user=True)
    
    def add_ai_message(self, message: str):
        """
        Add an AI response to the chat.
        
        Called by the controller after receiving API response.
        
        Args:
            message: AI's response text
        """
        self.chat_area.add_message(message, is_user=False)
    
    def set_status(self, status: str, color: str = None):
        """
        Update the status bar text.
        
        Called by the controller to show connection status.
        
        Args:
            status: Status text to display
            color: Optional color for the status text
        """
        self.status_label.setText(status)
        
        if color:
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    padding: 5px;
                }}
            """)
        
        logger.debug(f"Status updated: {status}")
    
    def set_input_enabled(self, enabled: bool):
        """
        Enable or disable the input area.
        
        Used to prevent user input while processing a message.
        
        Args:
            enabled: True to enable input, False to disable
        """
        self.input_box.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
    
    def show_error(self, error_message: str):
        """
        Display an error message to the user.
        
        Shows error as an AI message in red color.
        
        Args:
            error_message: Error message to display
        """
        # Create error message widget
        error_widget = MessageWidget(f"❌ Error: {error_message}", is_user=False)
        
        # Override styling to show error color
        error_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {Config.ERROR_COLOR};
                color: white;
                border-radius: 12px;
                padding: 8px;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
        # Add to chat
        self.chat_area.messages_layout.insertWidget(
            self.chat_area.messages_layout.count() - 1,
            error_widget,
            alignment=Qt.AlignLeft
        )
        
        # Scroll to show error
        QTimer.singleShot(100, self.chat_area._scroll_to_bottom)
        
        logger.warning(f"Error displayed: {error_message}")


# ========== USAGE NOTES ==========
"""
This is the VIEW layer in MVC architecture.

The MainWindow:
1. Displays the UI
2. Emits signals when user interacts (message_sent signal)
3. Provides methods for the controller to update the UI

The controller will:
1. Connect to the message_sent signal
2. Call add_user_message(), add_ai_message(), etc. to update UI
3. Handle all business logic

This separation keeps UI code clean and testable.
"""
