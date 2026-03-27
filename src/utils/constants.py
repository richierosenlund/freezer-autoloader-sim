"""Application constants and configuration"""

# Cartridge Configuration
CARTRIDGE_CONFIGS = {
    1: {"type": "W", "initial_stack": 25},
    2: {"type": "W", "initial_stack": 25},
    3: {"type": "WJ", "initial_stack": 15},
    4: {"type": "WJ", "initial_stack": 15},
}

# Belt Configuration
BELT_SPEED_W = 120.0  # seconds for W patty to traverse belt
BELT_SPEED_WJ = 90.0  # seconds for WJ patty to traverse belt
BELT_WIDTH = 800  # pixels
BELT_HEIGHT = 80  # pixels
PATTY_WIDTH = 40  # pixels
PATTY_HEIGHT = 40  # pixels

# Animation
ANIMATION_FPS = 60
UPDATE_INTERVAL_MS = int(1000 / ANIMATION_FPS)
DISPENSE_DELAY_SECONDS_W = 10.0
DISPENSE_DELAY_SECONDS_WJ = 8.0

# UI Colors
COLOR_DARK_TEAL = "#155E75"
COLOR_LIGHT_TEAL = "#0369A1"
COLOR_WHITE = "#FFFFFF"
COLOR_GREEN = "#10B981"
COLOR_RED = "#EF4444"
COLOR_DARK_BG = "#0F172A"

# Font sizes
FONT_HEADER = 14
FONT_LABEL = 11
FONT_VALUE = 12