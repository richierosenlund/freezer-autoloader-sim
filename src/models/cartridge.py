"""Cartridge model for patty storage"""

class Cartridge:
    """Represents a single cartridge that holds patties"""
    
    def __init__(self, cartridge_id: int, patty_type: str, initial_stack: int):
        """
        Initialize a cartridge.
        
        Args:
            cartridge_id: Unique identifier (1-4)
            patty_type: Type of patty ("W" or "WJ")
            initial_stack: Initial number of patties in stack
        """
        self.id = cartridge_id
        self.patty_type = patty_type
        self.patties_in_stack = initial_stack
        self.initial_stack = initial_stack
        self.dispense_queue = 0
        # assign a physical belt based on cartridge id: 1&2 -> belt 1, 3&4 -> belt 2
        self.belt_id = 1 if cartridge_id in (1, 2) else 2
    
    def dispense(self, count: int) -> bool:
        """
        Attempt to dispense patties from this cartridge.
        
        Args:
            count: Number of patties to dispense
            
        Returns:
            True if successful, False if insufficient stock
        """
        if self.patties_in_stack >= count:
            self.patties_in_stack -= count
            self.dispense_queue += count
            return True
        return False
    
    def reload(self, patty_type: str = None):
        """Reload the cartridge.

        If ``patty_type`` is provided, change the cartridge's type and set the
        initial stack appropriate to that type (39 for W, 43 for WJ) before
        reloading.  Otherwise just refill to the existing initial stack.
        """
        if patty_type is not None:
            self.patty_type = patty_type
            self.initial_stack = 39 if patty_type == "W" else 43
        self.patties_in_stack = self.initial_stack
    
    def reset_stack_counter(self):
        """Reset the stack counter and reload"""
        self.reload()
    
    def get_info(self) -> dict:
        """Get current cartridge status"""
        return {
            "id": self.id,
            "type": self.patty_type,
            "patties_in_stack": self.patties_in_stack,
            "dispense_queue": self.dispense_queue,
            "belt_id": self.belt_id,
        }