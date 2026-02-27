"""Broiler UI Panel widget"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class BroilerPanel(QWidget):
    """Broiler UI panel for requesting patties"""
    
    # Signals
    request_whopper = pyqtSignal(int)
    request_whopper_jr = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Broiler UI")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title)
        
        # Request Whopper section
        whopper_group = QGroupBox("Request Whopper Patty")
        whopper_layout = QHBoxLayout()
        
        self.whopper_spin = QSpinBox()
        self.whopper_spin.setMinimum(1)
        self.whopper_spin.setMaximum(10)
        self.whopper_spin.setValue(1)
        self.whopper_spin.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #155E75;
                border-radius: 3px;
                padding: 4px;
                width: 50px;
            }
        """)
        
        whopper_btn = QPushButton("+")
        whopper_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 16px;
                width: 40px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        whopper_btn.clicked.connect(
            lambda: self.request_whopper.emit(self.whopper_spin.value())
        )
        
        whopper_layout.addWidget(self.whopper_spin)
        whopper_layout.addWidget(whopper_btn)
        whopper_layout.addStretch()
        whopper_group.setLayout(whopper_layout)
        whopper_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 2px solid #10B981;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        layout.addWidget(whopper_group)
        
        # Request Whopper JR section
        whopper_jr_group = QGroupBox("Request Whopper JR Patty")
        whopper_jr_layout = QHBoxLayout()
        
        self.whopper_jr_spin = QSpinBox()
        self.whopper_jr_spin.setMinimum(1)
        self.whopper_jr_spin.setMaximum(10)
        self.whopper_jr_spin.setValue(1)
        self.whopper_jr_spin.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #155E75;
                border-radius: 3px;
                padding: 4px;
                width: 50px;
            }
        """)
        
        whopper_jr_btn = QPushButton("+")
        whopper_jr_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 16px;
                width: 40px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        whopper_jr_btn.clicked.connect(
            lambda: self.request_whopper_jr.emit(self.whopper_jr_spin.value())
        )
        
        whopper_jr_layout.addWidget(self.whopper_jr_spin)
        whopper_jr_layout.addWidget(whopper_jr_btn)
        whopper_jr_layout.addStretch()
        whopper_jr_group.setLayout(whopper_jr_layout)
        whopper_jr_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 2px solid #10B981;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)
        layout.addWidget(whopper_jr_group)
        
        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #155E75; border-radius: 5px; padding: 15px;")