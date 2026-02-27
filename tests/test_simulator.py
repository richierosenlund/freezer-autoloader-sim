"""Unit tests for the simulator"""

import unittest
from src.models.simulator import FreezerAutoloaderSimulator, PattyBelt
from src.models.cartridge import Cartridge


class TestCartridge(unittest.TestCase):
    """Test cartridge functionality"""
    
    def setUp(self):
        self.cartridge = Cartridge(1, "W", 30)
    
    def test_dispense_success(self):
        """Test successful patty dispensing"""
        result = self.cartridge.dispense(5)
        self.assertTrue(result)
        self.assertEqual(self.cartridge.patties_in_stack, 25)
        self.assertEqual(self.cartridge.dispense_queue, 5)
    
    def test_dispense_insufficient_stock(self):
        """Test dispensing with insufficient stock"""
        result = self.cartridge.dispense(35)
        self.assertFalse(result)
        self.assertEqual(self.cartridge.patties_in_stack, 30)
    
    def test_reload(self):
        """Test cartridge reload and type switching"""
        # normal reload
        self.cartridge.dispense(10)
        self.cartridge.reload()
        self.assertEqual(self.cartridge.patties_in_stack, 30)
        # reload as opposite type should change stack to correct size
        self.cartridge.reload('WJ')
        self.assertEqual(self.cartridge.patty_type, 'WJ')
        self.assertEqual(self.cartridge.patties_in_stack, 43)
        # switch back to W
        self.cartridge.reload('W')
        self.assertEqual(self.cartridge.patty_type, 'W')
        self.assertEqual(self.cartridge.patties_in_stack, 39)


class TestSimulator(unittest.TestCase):
    """Test simulator functionality"""
    
    def setUp(self):
        self.simulator = FreezerAutoloaderSimulator()
    
    def test_request_whopper(self):
        """Test requesting Whopper patties with default belt configuration."""
        # both belts start configured for W; cartridges 1&3 can queue
        result = self.simulator.request_patties("W", 5)
        self.assertTrue(result)
        queues = self.simulator.get_dispense_queues()
        # one patty immediately dispatched, remaining 4 in queues
        self.assertEqual(queues["W"], 4)
        # simulate time passing so that another patty can be released
        import time
        from unittest.mock import patch
        base = time.time()
        with patch('src.models.simulator.time.time') as mock_time:
            mock_time.return_value = base + 6
            state = self.simulator.update()
        info = self.simulator.get_belt_info()
        total = info[1]["patty_count"] + info[2]["patty_count"]
        self.assertEqual(total, 2)
    
    def test_request_no_stock(self):
        """Test requesting with no stock"""
        # Drain first cartridge
        self.simulator.cartridges[0].dispense(30)
        self.simulator.cartridges[2].dispense(30)
        
        result = self.simulator.request_patties("W", 5)
        self.assertFalse(result)
        self.assertIsNotNone(self.simulator.last_error)

    def test_simulator_reload_changes_type_and_stack(self):
        """Ensure simulator-level reload_cartridge accepts a type."""
        self.simulator.reload_cartridge(1, "WJ")
        info = self.simulator.get_cartridge_info(1)
        self.assertEqual(info["type"], "WJ")
        self.assertEqual(info["patties_in_stack"], 43)
        self.simulator.reload_cartridge(1, "W")
        info = self.simulator.get_cartridge_info(1)
        self.assertEqual(info["type"], "W")
        self.assertEqual(info["patties_in_stack"], 39)
    
    def test_dispense_delay(self):
        """Ensure a 5 second gap is enforced between patties on a belt."""
        from unittest.mock import patch

        sim = FreezerAutoloaderSimulator()
        # start with a deterministic time
        base = 100.0
        with patch('src.models.simulator.time.time') as mock_time:
            mock_time.return_value = base
            sim.request_patties('W', 2)
            self.assertEqual(sim.get_dispense_queues()['W'], 1)
            mock_time.return_value = base + 3
            state = sim.update()
            self.assertEqual(state['w_belt']['patty_count'], 1)
            mock_time.return_value = base + 6
            state = sim.update()
            self.assertEqual(state['w_belt']['patty_count'], 2)

    def test_get_dispense_queues_reflects_cartridges(self):
        """Global queue is just the sum of all cartridge queues."""
        sim = FreezerAutoloaderSimulator()
        sim.cartridges[0].dispense(3)
        sim.cartridges[1].dispense(2)
        queues = sim.get_dispense_queues()
        self.assertEqual(queues['W'], 3)
        self.assertEqual(queues['WJ'], 2)

    def test_belt_assignment_and_type_changes(self):
        """Verify cartridges are tied to belts and belts can change type."""
        sim = FreezerAutoloaderSimulator()
        # default both belts to W
        self.assertTrue(sim.set_belt_type(1, 'W'))
        self.assertTrue(sim.set_belt_type(2, 'W'))
        # request WJ should fail because no belt is set for WJ
        self.assertFalse(sim.request_patties('WJ', 1))
        # change belt1 to WJ so cartridge 2 (belt1) can queue
        sim.set_belt_type(1, 'WJ')
        self.assertTrue(sim.request_patties('WJ', 1))
        # the patty will have been immediately dispatched, so cartridge queue is 0
        self.assertEqual(sim.cartridges[1].dispense_queue, 0)
        # now revert belt1 back to W; no belt is set for WJ so next request fails
        sim.set_belt_type(1, 'W')
        self.assertFalse(sim.request_patties('WJ', 1))
        # set belt2 to WJ and ensure cartridge 4 (on belt2) is used
        sim.set_belt_type(2, 'WJ')
        self.assertTrue(sim.request_patties('WJ', 1))
        # because the previous WJ dispense just occurred, next one will remain queued
        self.assertEqual(sim.cartridges[3].dispense_queue, 1)
        # advance time and call update to flush it
        import time
        from unittest.mock import patch
        base = time.time()
        with patch('src.models.simulator.time.time') as mock_time:
            mock_time.return_value = base + 6
            sim.update()
        self.assertEqual(sim.cartridges[3].dispense_queue, 0)

    def test_request_wj_patty_dispenses_on_belt2(self):
        """Test requesting WJ patties dispenses on belt 2 when cart 4 has WJ and belt 2 is set to WJ."""
        sim = FreezerAutoloaderSimulator()
        # Initial state: cartridge 4 (index 3) has WJ patties
        self.assertEqual(sim.cartridges[3].patty_type, 'WJ')
        # Initially belt 2 is set to W
        self.assertEqual(sim.belt2.patty_type, 'W')
        # requesting WJ should fail because no belt is set for WJ
        self.assertFalse(sim.request_patties('WJ', 1))
        # Now set belt 2 to WJ (the speed at which WJ patties run)
        sim.set_belt_type(2, 'WJ')
        self.assertEqual(sim.belt2.patty_type, 'WJ')
        # Now request WJ should succeed and dispense from cart 4 (belt 2)
        self.assertTrue(sim.request_patties('WJ', 1))
        # The first patty is immediately dispatched to the belt, not queued
        self.assertEqual(sim.cartridges[3].dispense_queue, 0)
        # Verify cartridge 2 (belt1, WJ) was not used
        self.assertEqual(sim.cartridges[1].dispense_queue, 0)
        # Verify the patty is on belt 2
        self.assertEqual(sim.belt2.get_patty_count(), 1)
        # Verify no patties on belt 1
        self.assertEqual(sim.belt1.get_patty_count(), 0)
        # Request another patty
        self.assertTrue(sim.request_patties('WJ', 1))
        # This one stays queued until 5 seconds have passed
        self.assertEqual(sim.cartridges[3].dispense_queue, 1)
        # Advance time and process queue to move patty from queue to belt
        import time
        from unittest.mock import patch
        base = time.time()
        with patch('src.models.simulator.time.time') as mock_time:
            mock_time.return_value = base + 6
            sim.update()
        # Verify the second patty is now on belt 2
        self.assertEqual(sim.cartridges[3].dispense_queue, 0)
        self.assertEqual(sim.belt2.get_patty_count(), 2)


if __name__ == "__main__":
    unittest.main()