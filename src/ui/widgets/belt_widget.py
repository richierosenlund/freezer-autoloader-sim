"""Animated belt widget for displaying patty movement"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import QSize
from src.utils.constants import (
    BELT_WIDTH, BELT_HEIGHT, PATTY_WIDTH, PATTY_HEIGHT,
    UPDATE_INTERVAL_MS
)


class BeltAnimationWidget(QWidget):
    """Widget that displays animated belt with patties"""
    
    def __init__(self, patty_type: str, parent=None):
        """
        Initialize belt widget.
        
        Args:
            patty_type: "W" or "WJ"
        """
        super().__init__(parent)
        self.patty_type = patty_type
        self.patty_positions = []
        self.time_remaining = 0
        
        self.setMinimumSize(BELT_WIDTH + 60, 150)
        self.setStyleSheet("background-color: #0F172A;")
        
        # Timer for animation updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(UPDATE_INTERVAL_MS)
    
    def update_belt_state(self, positions: list, time_remaining: float):
        """
        Update the belt with new patty positions.
        
        Args:
            positions: List of (position_percent, patty_type)
            time_remaining: Seconds until belt clears
        """
        self.patty_positions = positions
        self.time_remaining = time_remaining
        self.update()

    def set_patty_type(self, patty_type: str):
        """Change the belt's configured patty type for new patties."""
        self.patty_type = patty_type
    
    def paintEvent(self, event):
        """Draw the belt and patties"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw belt frame
        belt_y = 30
        self.draw_belt(painter, belt_y)
        
        # Draw patties
        for position_percent, patty_type in self.patty_positions:
            self.draw_patty(painter, position_percent, belt_y, patty_type)
        
        # Draw time remaining
        self.draw_time_remaining(painter)
    
    def draw_belt(self, painter: QPainter, y: int):
        """Draw the conveyor belt"""
        # Belt background
        belt_rect = QRect(30, y, BELT_WIDTH, BELT_HEIGHT)
        painter.fillRect(belt_rect, QColor("#2D3E50"))
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.drawRect(belt_rect)
        
        # Draw rollers (circles at ends)
        roller_diameter = BELT_HEIGHT
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawEllipse(20 - roller_diameter // 2, y - 5, roller_diameter, roller_diameter)
        painter.drawEllipse(30 + BELT_WIDTH - roller_diameter // 2, y - 5, roller_diameter, roller_diameter)
        
        # Draw roller details
        painter.setPen(QPen(QColor("#666666"), 1))
        for offset in [-20, -10, 0, 10, 20]:
            painter.drawLine(25 + offset, y - 5, 25 + offset, y + roller_diameter - 5)
        
        for offset in [-20, -10, 0, 10, 20]:
            painter.drawLine(30 + BELT_WIDTH - 5 + offset, y - 5, 30 + BELT_WIDTH - 5 + offset, y + roller_diameter - 5)
    
    def draw_patty(self, painter: QPainter, position_percent: float, belt_y: int, patty_type: str):
        """Draw a single patty on the belt"""
        # Convert position percent to pixel position
        pixel_position = 30 + (position_percent / 100.0) * BELT_WIDTH
        patty_x = pixel_position - PATTY_WIDTH // 2
        patty_y = belt_y + (BELT_HEIGHT - PATTY_HEIGHT) // 2

        # Draw patty as a filled ellipse (round patty)
        patty_color = QColor("#8B4513") if patty_type == "W" else QColor("#A0522D")
        painter.setBrush(patty_color)
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        painter.drawEllipse(int(patty_x), int(patty_y), PATTY_WIDTH, PATTY_HEIGHT)

        # Draw patty label
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        font = QFont()
        font.setPixelSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            int(patty_x), int(patty_y),
            PATTY_WIDTH, PATTY_HEIGHT,
            Qt.AlignCenter,
            patty_type
        )
        painter.setBrush(Qt.NoBrush)
    
    def draw_time_remaining(self, painter: QPainter):
        """Draw time remaining text"""
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        font = QFont()
        font.setPixelSize(11)
        painter.setFont(font)
        
        time_text = f"Time remaining: {self.time_remaining:.1f}s"
        painter.drawText(30, 120, time_text)