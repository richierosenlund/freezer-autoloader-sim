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
    lto_initiate = pyqtSignal()
    lto_load = pyqtSignal()
    lto_finish = pyqtSignal()
    
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
        
        # LTO (Load To Order) section for cartridge 4
        lto_group = QGroupBox("Load To Order (Cart 4)")
        lto_layout = QVBoxLayout()
        
        # LTO load qty
        lto_qty_layout = QHBoxLayout()
        lto_qty_label = QLabel("LTO load qty:")
        lto_qty_label.setStyleSheet("color: #FFFFFF;")
        self.lto_qty_spin = QSpinBox()
        self.lto_qty_spin.setMinimum(1)
        self.lto_qty_spin.setMaximum(20)
        self.lto_qty_spin.setValue(5)
        self.lto_qty_spin.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #155E75;
                border-radius: 3px;
                padding: 4px;
                width: 50px;
            }
        """)
        lto_qty_layout.addWidget(lto_qty_label)
        lto_qty_layout.addWidget(self.lto_qty_spin)
        lto_qty_layout.addStretch()
        lto_layout.addLayout(lto_qty_layout)

        # LTO status row: remaining count on left, finish timer on right
        lto_status_layout = QHBoxLayout()
        self.lto_remaining_label = QLabel("LTO remaining: 0")
        self.lto_remaining_label.setStyleSheet("color: #E5E7EB; font-weight: bold;")

        self.lto_finish_timer_label = QLabel("")
        self.lto_finish_timer_label.setStyleSheet("color: #C4B5FD; font-size: 11px;")
        self.lto_finish_timer_label.setVisible(False)
        self.lto_finish_timer_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        lto_status_layout.addWidget(self.lto_remaining_label)
        lto_status_layout.addStretch()
        lto_status_layout.addWidget(self.lto_finish_timer_label)
        lto_layout.addLayout(lto_status_layout)
        
        # LTO buttons
        lto_buttons_layout = QHBoxLayout()
        
        self.lto_initiate_btn = QPushButton("Initiate LTO 4")
        self.lto_initiate_btn.setStyleSheet("""
            QPushButton {
                background-color: #F59E0B;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #D97706;
            }
            QPushButton:pressed {
                background-color: #B45309;
            }
            QPushButton:disabled {
                background-color: #6B7280;
                color: #9CA3AF;
            }
        """)
        self.lto_initiate_btn.clicked.connect(self._on_lto_initiate)
        
        self.lto_load_btn = QPushButton("Load LTO")
        self.lto_load_btn.setEnabled(False)
        self.lto_load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #6B7280;
                color: #9CA3AF;
            }
        """)
        self.lto_load_btn.clicked.connect(self._on_lto_load)
        
        self.lto_finish_btn = QPushButton("Finished Loading")
        self.lto_finish_btn.setEnabled(False)
        self.lto_finish_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B5CF6;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7C3AED;
            }
            QPushButton:pressed {
                background-color: #6D28D9;
            }
            QPushButton:disabled {
                background-color: #6B7280;
                color: #9CA3AF;
            }
        """)
        self.lto_finish_btn.clicked.connect(self._on_lto_finish)
        
        lto_buttons_layout.addWidget(self.lto_initiate_btn)
        lto_buttons_layout.addWidget(self.lto_load_btn)
        lto_buttons_layout.addWidget(self.lto_finish_btn)
        lto_buttons_layout.addStretch()
        lto_layout.addLayout(lto_buttons_layout)
        
        lto_group.setLayout(lto_layout)
        lto_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 2px solid #8B5CF6;
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
        layout.addWidget(lto_group)
        
        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #155E75; border-radius: 5px; padding: 15px;")
    
    def _on_lto_initiate(self):
        """Handle LTO Initiate button click"""
        self.lto_initiate.emit()
    
    def _on_lto_load(self):
        """Handle LTO Load button click"""
        self.lto_load.emit()
    
    def _on_lto_finish(self):
        """Handle LTO Finish button click"""
        self.lto_finish.emit()

    def set_lto_remaining(self, remaining: int):
        """Update LTO remaining countdown display."""
        self.lto_remaining_label.setText(f"LTO remaining: {remaining}")

    def set_lto_finish_timer(self, timer_remaining: float):
        """Show/clear the finish timer status line during LTO finish phase."""
        if timer_remaining > 0:
            seconds = max(1, int(timer_remaining + 0.999))
            self.lto_finish_timer_label.setText(f"LTO finish timer: {seconds}s")
            self.lto_finish_timer_label.setVisible(True)
        else:
            self.lto_finish_timer_label.clear()
            self.lto_finish_timer_label.setVisible(False)