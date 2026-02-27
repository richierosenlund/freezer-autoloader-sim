"""Freezer Autoloader Panel widget"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QSpinBox, QComboBox, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class AutoloaderPanel(QWidget):
    """Freezer Autoloader panel"""
    
    # Signals
    reload_cartridge = pyqtSignal(int, str)  # cartridge id and type
    reset_stack_counter = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cartridge_widgets = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Freezer Auto-loader")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title)
        
        # Top row: Dispense queues
        queue_layout = QHBoxLayout()
        
        # Whopper queue
        whopper_queue_group = QGroupBox("Whopper Patty\ndispense queue")
        whopper_queue_layout = QVBoxLayout()
        self.whopper_queue_label = QLabel("0")
        self.whopper_queue_label.setStyleSheet("""
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #155E75;
            border-radius: 3px;
            padding: 10px;
            font-weight: bold;
            font-size: 14px;
            text-align: center;
            min-width: 50px;
        """)
        self.whopper_queue_label.setAlignment(Qt.AlignCenter)
        whopper_queue_layout.addWidget(self.whopper_queue_label)
        whopper_queue_group.setLayout(whopper_queue_layout)
        queue_layout.addWidget(whopper_queue_group)
        
        # Whopper JR queue
        whopper_jr_queue_group = QGroupBox("Whopper JR\nPatty dispense\nqueue")
        whopper_jr_queue_layout = QVBoxLayout()
        self.whopper_jr_queue_label = QLabel("0")
        self.whopper_jr_queue_label.setStyleSheet("""
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #155E75;
            border-radius: 3px;
            padding: 10px;
            font-weight: bold;
            font-size: 14px;
            text-align: center;
            min-width: 50px;
        """)
        self.whopper_jr_queue_label.setAlignment(Qt.AlignCenter)
        whopper_jr_queue_layout.addWidget(self.whopper_jr_queue_label)
        whopper_jr_queue_group.setLayout(whopper_jr_queue_layout)
        queue_layout.addWidget(whopper_jr_queue_group)
        
        queue_layout.addStretch()
        layout.addLayout(queue_layout)
        
        # Cartridges grid
        cartridges_group = QGroupBox("Cartridges")
        cartridges_layout = QGridLayout()
        cartridges_layout.setSpacing(10)
        
        # Create 4 cartridge rows
        for cart_id in range(1, 5):
            self.create_cartridge_row(cartridges_layout, cart_id)
        
        cartridges_group.setLayout(cartridges_layout)
        cartridges_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 2px solid #155E75;
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
        layout.addWidget(cartridges_group)
        
        layout.addStretch()
        self.setLayout(layout)
        self.setStyleSheet("background-color: #155E75; border-radius: 5px; padding: 15px;")
    
    def create_cartridge_row(self, parent_layout: QGridLayout, cart_id: int):
        """Create a single cartridge row"""
        row = cart_id - 1
        
        # Reload buttons
        reload_w_btn = QPushButton("W")
        reload_w_btn.setMaximumWidth(40)
        reload_w_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #155E75;
                border-radius: 3px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        reload_w_btn.clicked.connect(lambda _, cid=cart_id: self.reload_cartridge.emit(cid, "W"))
        
        reload_wj_btn = QPushButton("WJ")
        reload_wj_btn.setMaximumWidth(40)
        reload_wj_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #155E75;
                border-radius: 3px;
                padding: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        reload_wj_btn.clicked.connect(lambda _, cid=cart_id: self.reload_cartridge.emit(cid, "WJ"))
        
        reload_layout = QHBoxLayout()
        reload_layout.addWidget(reload_w_btn)
        reload_layout.addWidget(reload_wj_btn)
        reload_layout.setContentsMargins(0, 0, 0, 0)
        reload_group = QGroupBox(f"Reload\nCartridge {cart_id}")
        reload_group.setLayout(reload_layout)
        reload_group.setMaximumHeight(80)
        reload_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                border-radius: 3px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 5px;
                padding: 0 2px 0 2px;
            }
        """)
        
        # Current type display
        current_type_label = QLabel("W")
        current_type_label.setStyleSheet("""
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #155E75;
            border-radius: 3px;
            padding: 4px;
            font-weight: bold;
            text-align: center;
            min-height: 20px;
        """)
        current_type_label.setAlignment(Qt.AlignCenter)
        if cart_id % 2 == 0:
            current_type_label.setText("WJ")
        
        current_type_group = QGroupBox("Current\nType")
        current_type_layout = QVBoxLayout()
        current_type_layout.addWidget(current_type_label)
        current_type_layout.setContentsMargins(5, 5, 5, 5)
        current_type_group.setLayout(current_type_layout)
        current_type_group.setMaximumHeight(80)
        current_type_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                border-radius: 3px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 5px;
                padding: 0 2px 0 2px;
            }
        """)
        
        # Dispense queue
        queue_label = QLabel("30")
        queue_label.setStyleSheet("""
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #155E75;
            border-radius: 3px;
            padding: 4px;
            font-weight: bold;
            text-align: center;
            min-height: 20px;
        """)
        queue_label.setAlignment(Qt.AlignCenter)
        
        queue_group = QGroupBox("Cartridge\nDispense\nqueue")
        queue_layout = QVBoxLayout()
        queue_layout.addWidget(queue_label)
        queue_layout.setContentsMargins(5, 5, 5, 5)
        queue_group.setLayout(queue_layout)
        queue_group.setMaximumHeight(80)
        queue_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                border-radius: 3px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 5px;
                padding: 0 2px 0 2px;
            }
        """)
        
        # Patties in stack
        stack_label = QLabel("30")
        stack_label.setStyleSheet("""
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #155E75;
            border-radius: 3px;
            padding: 4px;
            font-weight: bold;
            text-align: center;
            min-height: 20px;
        """)
        stack_label.setAlignment(Qt.AlignCenter)
        
        stack_layout = QVBoxLayout()
        stack_layout.addWidget(stack_label)
        stack_layout.setContentsMargins(5, 5, 5, 5)
        stack_layout.setSpacing(3)
        
        stack_group = QGroupBox("Patties\nin stack")
        stack_group.setLayout(stack_layout)
        stack_group.setMaximumHeight(80)
        stack_group.setStyleSheet("""
            QGroupBox {
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
                border-radius: 3px;
                margin-top: 5px;
                padding-top: 5px;
                font-size: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 5px;
                padding: 0 2px 0 2px;
            }
        """)
        
        # Add to layout
        parent_layout.addWidget(reload_group, row, 0)
        parent_layout.addWidget(current_type_group, row, 1)
        parent_layout.addWidget(queue_group, row, 2)
        parent_layout.addWidget(stack_group, row, 3)
        
        # Store references for updates
        self.cartridge_widgets[cart_id] = {
            "current_type": current_type_label,
            "queue": queue_label,
            "stack": stack_label,
        }
    
    def update_cartridge(self, cart_id: int, info: dict):
        """Update display for a cartridge"""
        if cart_id in self.cartridge_widgets:
            widgets = self.cartridge_widgets[cart_id]
            widgets["current_type"].setText(info["type"])
            widgets["queue"].setText(str(info["dispense_queue"]))
            widgets["stack"].setText(str(info["patties_in_stack"]))
    
    def update_queues(self, w_queue: int, wj_queue: int):
        """Update the dispense queue displays"""
        self.whopper_queue_label.setText(str(w_queue))
        self.whopper_jr_queue_label.setText(str(wj_queue))