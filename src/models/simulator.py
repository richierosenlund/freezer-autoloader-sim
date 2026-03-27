"""Main simulator engine for the freezer autoloader"""

import time
from typing import List, Tuple
from src.models.cartridge import Cartridge
from src.utils.constants import (
    CARTRIDGE_CONFIGS,
    BELT_SPEED_W,
    BELT_SPEED_WJ,
    DISPENSE_DELAY_SECONDS_W,
    DISPENSE_DELAY_SECONDS_WJ,
)

# mapping from patty type to belt speed constant
BELT_SPEED_MAP = {"W": BELT_SPEED_W, "WJ": BELT_SPEED_WJ}
DISPENSE_DELAY_MAP = {
    "W": DISPENSE_DELAY_SECONDS_W,
    "WJ": DISPENSE_DELAY_SECONDS_WJ,
}


class PattyBelt:
    """Represents an animated belt with patties"""
    
    def __init__(self, patty_type: str, belt_speed: float):
        """
        Initialize a patty belt.
        
        Args:
            patty_type: "W" or "WJ"
            belt_speed: Time in seconds for patty to traverse belt
        """
        self.patty_type = patty_type
        self.belt_speed = belt_speed
        self.patties_on_belt: List[Tuple[float, str]] = []  # (start_time, type)
        self.start_time = time.time()
    
    def add_patty(self):
        """Add a patty to the belt"""
        self.patties_on_belt.append((time.time(), self.patty_type))
    
    def add_patty_with_type(self, patty_type: str):
        """Add a patty to the belt with a specific type label.
        
        Args:
            patty_type: Custom type label for the patty (e.g., "LTO")
        """
        self.patties_on_belt.append((time.time(), patty_type))
    
    def update(self) -> Tuple[List[Tuple[float, float]], float]:
        """
        Update belt animation state.
        
        Returns:
            Tuple of (patty_positions, time_remaining)
            patty_positions: List of (position_percent, patty_id)
            time_remaining: Seconds until belt clears
        """
        current_time = time.time()
        positions = []
        remaining_patties = []
        
        for patty_time, patty_type in self.patties_on_belt:
            elapsed = current_time - patty_time
            position = (elapsed / self.belt_speed) * 100
            
            if position <= 100:
                positions.append((position, patty_type))
                remaining_patties.append((patty_time, patty_type))
        
        self.patties_on_belt = remaining_patties
        
        # Calculate time remaining until last patty clears
        if remaining_patties:
            last_patty_time = remaining_patties[-1][0]
            time_remaining = (last_patty_time + self.belt_speed) - current_time
            time_remaining = max(0, time_remaining)
        else:
            time_remaining = 0
        
        return positions, time_remaining
    
    def get_patty_count(self) -> int:
        """Get number of patties currently on belt"""
        return len(self.patties_on_belt)

    def has_active_type(self, patty_type: str) -> bool:
        """Return True when a patty type is still moving toward the end of the belt."""
        current_time = time.time()
        for patty_time, current_type in self.patties_on_belt:
            if current_type != patty_type:
                continue
            elapsed = current_time - patty_time
            position = (elapsed / self.belt_speed) * 100
            # "Reached the end" is treated as position >= 100.
            if position < 100:
                return True
        return False


class FreezerAutoloaderSimulator:
    """Main simulation engine"""
    
    def __init__(self):
        """Initialize the simulator"""
        self.cartridges: List[Cartridge] = []
        # one physical belt per cartridge; belts 1&2 default to W, 3&4 to WJ
        self.belt1 = PattyBelt("W", BELT_SPEED_W)
        self.belt2 = PattyBelt("W", BELT_SPEED_W)
        self.belt3 = PattyBelt("WJ", BELT_SPEED_WJ)
        self.belt4 = PattyBelt("WJ", BELT_SPEED_WJ)
        # keep legacy names for compatibility
        self.w_belt = self.belt1
        self.wj_belt = self.belt3
        self.last_error = None

        # timestamps for enforcing minimum delay between dispenses per cartridge
        self.last_dispense_time = {cart_id: 0.0 for cart_id in CARTRIDGE_CONFIGS}
        
        # LTO (Load To Order) state for cartridge 4
        self.lto_mode = False
        self.lto_load_qty = 0
        self.lto_loads_remaining = 0
        self.lto_waiting_for_wj_clear = False
        self.lto_timer_start = None
        
        # Initialize cartridges
        for cart_id, config in CARTRIDGE_CONFIGS.items():
            cartridge = Cartridge(
                cart_id,
                config["type"],
                config["initial_stack"]
            )
            self.cartridges.append(cartridge)
    
    def _belt_for(self, cart_id: int) -> "PattyBelt":
        """Return the belt object assigned to a given cartridge id."""
        return {1: self.belt1, 2: self.belt2, 3: self.belt3, 4: self.belt4}[cart_id]

    def request_patties(self, patty_type: str, count: int = 1) -> bool:
        """
        Request patties to be dispensed.
        
        Patties are queued only in cartridges whose belt is currently configured
        to handle that patty type.  This enforces the physical association
        between cartridges and belts.
        """
        matching_cartridges = [
            c for c in self.cartridges
            if c.patty_type == patty_type
            and self._belt_for(c.id).patty_type == patty_type
        ]
        if not matching_cartridges:
            self.last_error = f"No cartridges available for type {patty_type} on matching belt"
            return False

        total_available = sum(cartridge.patties_in_stack for cartridge in matching_cartridges)
        if total_available < count:
            self.last_error = (
                f"{patty_type}hoppers request - no {patty_type} patties currently loaded"
            )
            return False

        remaining = count
        for cartridge in sorted(
            matching_cartridges,
            key=lambda cartridge: (-cartridge.patties_in_stack, cartridge.id),
        ):
            if remaining <= 0:
                break
            dispense_count = min(remaining, cartridge.patties_in_stack)
            if dispense_count <= 0:
                continue
            cartridge.dispense(dispense_count)
            remaining -= dispense_count

        self.last_error = None
        self._process_queues()
        return True
    
    def reload_cartridge(self, cartridge_id: int, patty_type: str = None) -> bool:
        """
        Reload a specific cartridge, optionally changing its type.

        Args:
            cartridge_id: ID of cartridge to reload (1-4)
            patty_type: if provided, switch the cartridge to this type ("W"/"WJ").

        Returns:
            True if successful
        """
        for cartridge in self.cartridges:
            if cartridge.id == cartridge_id:
                cartridge.reload(patty_type)
                return True
        return False
    
    def reset_stack_counter(self, cartridge_id: int) -> bool:
        """
        Reset the stack counter for a cartridge.
        
        Args:
            cartridge_id: ID of cartridge (1-4)
            
        Returns:
            True if successful
        """
        for cartridge in self.cartridges:
            if cartridge.id == cartridge_id:
                cartridge.reset_stack_counter()
                return True
        return False
    
    def get_cartridge_info(self, cartridge_id: int) -> dict:
        """Get information about a specific cartridge"""
        for cartridge in self.cartridges:
            if cartridge.id == cartridge_id:
                return cartridge.get_info()
        return {}
    
    def get_all_cartridges_info(self) -> List[dict]:
        """Get information about all cartridges"""
        return [c.get_info() for c in self.cartridges]

    def set_belt_type(self, belt_id: int, patty_type: str) -> bool:
        """Change the current patty type (speed) of a belt.

        Args:
            belt_id: 1, 2, 3, or 4
            patty_type: "W" or "WJ"

        Returns:
            True if the belt was set, False for invalid arguments.
        """
        if patty_type not in BELT_SPEED_MAP or belt_id not in (1, 2, 3, 4):
            return False
        belt = self._belt_for(belt_id)
        belt.patty_type = patty_type
        belt.belt_speed = BELT_SPEED_MAP[patty_type]
        return True

    def get_belt_info(self) -> dict:
        """Return current state of all four belts."""
        return {
            i: {
                "patty_type": self._belt_for(i).patty_type,
                "patty_count": self._belt_for(i).get_patty_count(),
            }
            for i in (1, 2, 3, 4)
        }
    
    def update(self) -> dict:
        """
        Update simulation state.
        
        This method is called on every timer tick by the UI.  Before returning
        the current state we attempt to process any cartridge queues and move
        patties onto the belts observing the configured dispense delay requirement.
        
        Returns:
            Dictionary with current state
        """
        # Update LTO state (check timer expiry, belt clearance, etc)
        self.update_lto_state()
        
        # move queued patties onto each cartridge belt independently
        self._process_queues()

        belts_state = {}
        for i in (1, 2, 3, 4):
            belt = self._belt_for(i)
            positions, time_remaining = belt.update()
            belts_state[i] = {
                "positions": positions,
                "time_remaining": time_remaining,
                "patty_count": belt.get_patty_count(),
            }

        # legacy keys kept for any code still using them
        return {
            "w_belt": belts_state[1],
            "wj_belt": belts_state[3],
            "belts": belts_state,
            "cartridges": self.get_all_cartridges_info(),
            "last_error": self.last_error,
        }
    
    def get_dispense_queues(self) -> dict:
        """Get current dispense queues"""
        w_queue = sum(c.dispense_queue for c in self.cartridges if c.patty_type == "W")
        wj_queue = sum(c.dispense_queue for c in self.cartridges if c.patty_type == "WJ")
        
        return {"W": w_queue, "WJ": wj_queue}



    def _process_queues(self) -> None:
        """Move queued patties onto belts respecting the configured delay per cartridge."""
        current_time = time.time()

        for cart in self.cartridges:
            if cart.dispense_queue <= 0:
                continue
            
            # Skip cart 4 if LTO mode is active
            if self.lto_mode and cart.id == 4:
                continue

            belt = self._belt_for(cart.id)
            if belt.patty_type != cart.patty_type:
                continue

            last_time = self.last_dispense_time[cart.id]
            dispense_delay = DISPENSE_DELAY_MAP[belt.patty_type]
            if current_time < last_time + dispense_delay:
                continue

            cart.dispense_queue -= 1
            belt.add_patty()
            self.last_dispense_time[cart.id] = current_time
    
    def initiate_lto(self, load_qty: int) -> bool:
        """Initiate LTO (Load To Order) mode for cartridge 4.
        
        Args:
            load_qty: Number of LTO items to load
            
        Returns:
            True if LTO mode initiated successfully
        """
        if self.lto_mode:
            return False  # Already in LTO mode
        
        self.lto_mode = True
        self.lto_load_qty = load_qty
        self.lto_loads_remaining = load_qty
        # First load is blocked only until any pre-existing WJ patties reach belt end.
        self.lto_waiting_for_wj_clear = self.belt4.has_active_type("WJ")
        self.lto_timer_start = None
        return True
    
    def load_lto_item(self) -> bool:
        """Load a single LTO item onto belt 4.
        
        Returns:
            True if item loaded successfully, False if no loads remaining
        """
        if not self.lto_mode or self.lto_loads_remaining <= 0 or self.lto_waiting_for_wj_clear:
            return False
        
        # Add LTO patty to belt 4 with "LTO" type label
        self.belt4.add_patty_with_type("LTO")
        self.lto_loads_remaining -= 1
        return True
    
    def finish_lto(self) -> bool:
        """Finish LTO mode and start the finish timer.
        
        Returns:
            True if timer started successfully
        """
        if not self.lto_mode or self.lto_loads_remaining > 0:
            return False  # Can only finish when all loads are done
        
        self.lto_timer_start = time.time()
        return True
    
    def update_lto_state(self) -> None:
        """Update LTO state including checking belt clearance and timer expiry."""
        if not self.lto_mode:
            return
        
        current_time = time.time()
        
        # If timer is running, check if it has expired
        if self.lto_timer_start is not None:
            elapsed = current_time - self.lto_timer_start
            if elapsed >= BELT_SPEED_WJ:
                # Timer expired, reset LTO mode
                self.lto_mode = False
                self.lto_waiting_for_wj_clear = False
                self.lto_timer_start = None

        # During Initiate phase, wait only for pre-existing WJ patties on belt 4 to clear.
        if self.lto_waiting_for_wj_clear and not self.belt4.has_active_type("WJ"):
            self.lto_waiting_for_wj_clear = False
    
    def get_lto_status(self) -> dict:
        """Get current LTO status for UI updates.
        
        Returns:
            Dictionary with LTO state information
        """
        belt4_clear = self.belt4.get_patty_count() == 0
        # Allow rapid LTO loads after Initiate gate opens; no per-load belt clear wait.
        load_btn_enabled = (
            self.lto_mode
            and not self.lto_waiting_for_wj_clear
            and self.lto_loads_remaining > 0
            and self.lto_timer_start is None
        )
        finish_btn_enabled = self.lto_mode and self.lto_loads_remaining == 0 and self.lto_timer_start is None
        
        timer_remaining = 0.0
        if self.lto_timer_start is not None:
            current_time = time.time()
            elapsed = current_time - self.lto_timer_start
            timer_remaining = max(0.0, BELT_SPEED_WJ - elapsed)
        
        return {
            "lto_mode": self.lto_mode,
            "belt4_clear": belt4_clear,
            "waiting_for_wj_clear": self.lto_waiting_for_wj_clear,
            "load_btn_enabled": load_btn_enabled,
            "finish_btn_enabled": finish_btn_enabled,
            "loads_remaining": self.lto_loads_remaining,
            "timer_remaining": timer_remaining,
        }
