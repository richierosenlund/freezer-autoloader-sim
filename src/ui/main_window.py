"""Main application window"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QScrollArea, QComboBox
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from src.models.simulator import FreezerAutoloaderSimulator
from src.ui.widgets.broiler_panel import BroilerPanel
from src.ui.widgets.autoloader_panel import AutoloaderPanel
from src.ui.widgets.belt_widget import BeltAnimationWidget


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.simulator = FreezerAutoloaderSimulator()
        self.init_ui()
        self.setup_timers()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Freezer Autoloader Simulator")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("background-color: #0F172A;")
        
        # Main container
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Left side: Broiler and Autoloader panels
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        # Broiler Panel
        self.broiler_panel = BroilerPanel()
        self.broiler_panel.request_whopper.connect(self.on_request_whopper)
        self.broiler_panel.request_whopper_jr.connect(self.on_request_whopper_jr)
        left_layout.addWidget(self.broiler_panel)
        
        # Autoloader Panel
        self.autoloader_panel = AutoloaderPanel()
        self.autoloader_panel.reload_cartridge.connect(self.on_reload_cartridge)
        self.autoloader_panel.reset_stack_counter.connect(self.on_reset_stack)
        left_layout.addWidget(self.autoloader_panel)
        
        # Right side: Belt animations and Error box
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # Whopper belt
        whopper_belt_group = QGroupBox("Whopper Belt")
        whopper_belt_layout = QVBoxLayout()
        # selector to change belt type
        self.belt1_selector = QComboBox()
        self.belt1_selector.addItems(["W", "WJ"])
        self.belt1_selector.setCurrentText("W")
        self.belt1_selector.currentTextChanged.connect(lambda t: self.set_belt_type(1, t))
        whopper_belt_layout.addWidget(self.belt1_selector)
        self.w_belt_widget = BeltAnimationWidget("W")
        whopper_belt_layout.addWidget(self.w_belt_widget)
        whopper_belt_group.setLayout(whopper_belt_layout)
        whopper_belt_group.setStyleSheet("""
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
        right_layout.addWidget(whopper_belt_group)
        
        # Whopper JR belt
        whopper_jr_belt_group = QGroupBox("Whopper JR Belt")
        whopper_jr_belt_layout = QVBoxLayout()
        self.belt2_selector = QComboBox()
        self.belt2_selector.addItems(["W", "WJ"])
        self.belt2_selector.setCurrentText("W")
        self.belt2_selector.currentTextChanged.connect(lambda t: self.set_belt_type(2, t))
        whopper_jr_belt_layout.addWidget(self.belt2_selector)
        self.wj_belt_widget = BeltAnimationWidget("WJ")
        whopper_jr_belt_layout.addWidget(self.wj_belt_widget)
        whopper_jr_belt_group.setLayout(whopper_jr_belt_layout)
        whopper_jr_belt_group.setStyleSheet("""
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
        right_layout.addWidget(whopper_jr_belt_group)
        
        # Error box
        error_group = QGroupBox("ERRORS")
        error_layout = QVBoxLayout()
        self.error_label = QLabel("No errors")
        self.error_label.setStyleSheet("""
            color: #10B981;
            font-weight: bold;
            padding: 10px;
        """)
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignTop)
        error_layout.addWidget(self.error_label)
        error_group.setLayout(error_layout)
        error_group.setStyleSheet("""
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
        error_group.setMaximumHeight(120)
        right_layout.addWidget(error_group)
        
        # Add left and right to main
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def setup_timers(self):
        """Setup update timers"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_simulation)
        self.update_timer.start(50)  # 50ms update rate
    
    def update_simulation(self):
        """Update simulation state"""
        state = self.simulator.update()
        
        # Update belt displays
        self.w_belt_widget.update_belt_state(
            state["w_belt"]["positions"],
            state["w_belt"]["time_remaining"]
        )
        self.wj_belt_widget.update_belt_state(
            state["wj_belt"]["positions"],
            state["wj_belt"]["time_remaining"]
        )
        
        # Update cartridge info
        for info in state["cartridges"]:
            self.autoloader_panel.update_cartridge(info["id"], info)
        
        # Update queues
        queues = self.simulator.get_dispense_queues()
        self.autoloader_panel.update_queues(queues["W"], queues["WJ"])
        
        # Update error display
        if state["last_error"]:
            self.error_label.setText(f"- {state['last_error']}")
            self.error_label.setStyleSheet("""
                color: #EF4444;
                font-weight: bold;
                padding: 10px;
            """)
        else:
            self.error_label.setText("No errors")
            self.error_label.setStyleSheet("""
                color: #10B981;
                font-weight: bold;
                padding: 10px;
            """)
    
    def on_request_whopper(self, count: int):
        """Handle whopper patty request"""
        self.simulator.request_patties("W", count)
    
    def on_request_whopper_jr(self, count: int):
        """Handle whopper JR patty request"""
        self.simulator.request_patties("WJ", count)

    def set_belt_type(self, belt_id: int, patty_type: str):
        """Helper called by UI selectors to change belt configuration"""
        self.simulator.set_belt_type(belt_id, patty_type)
        # update corresponding widget
        widget = self.w_belt_widget if belt_id == 1 else self.wj_belt_widget
        widget.patty_type = patty_type
    
    def on_reload_cartridge(self, cart_id: int, patty_type: str):
        """Handle cartridge reload with explicit type"""
        self.simulator.reload_cartridge(cart_id, patty_type)
    
    def on_reset_stack(self, cart_id: int):
        """Handle stack counter reset"""
        self.simulator.reset_stack_counter(cart_id)