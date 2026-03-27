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
        # requests are still allocated stock-first, then belts dispatch per cartridge
        result = self.simulator.request_patties("W", 5)
        self.assertTrue(result)
        queues = self.simulator.get_dispense_queues()
        # one patty immediately dispatched from the highest-stock W cartridge
        self.assertEqual(queues["W"], 4)
        # simulate time passing so that another patty can be released
        import time
        from unittest.mock import patch
        base = time.time()
        with patch('src.models.simulator.time.time') as mock_time:
            mock_time.return_value = base + 11
            self.simulator.update()
        info = self.simulator.get_belt_info()
        total = info[1]["patty_count"] + info[2]["patty_count"]
        self.assertEqual(total, 2)
    
    def test_request_no_stock(self):
        """Test requesting with no stock"""
        # cartridges 0 and 1 (ids 1 & 2) are both W; drain them both
        self.simulator.cartridges[0].patties_in_stack = 0
        self.simulator.cartridges[1].patties_in_stack = 0

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
        """Ensure a 10 second gap is enforced per cartridge belt."""
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
            self.assertEqual(state['w_belt']['patty_count'], 0)
            self.assertEqual(state['belts'][2]['patty_count'], 1)
            mock_time.return_value = base + 11
            sim.request_patties('W', 2)
            state = sim.update()
            self.assertEqual(state['w_belt']['patty_count'], 0)
            self.assertEqual(state['belts'][2]['patty_count'], 2)

    def test_get_dispense_queues_reflects_cartridges(self):
        """Global queue is just the sum of all cartridge queues."""
        sim = FreezerAutoloaderSimulator()
        # cartridges index 0 (id 1) and index 1 (id 2) are both W by default
        sim.cartridges[0].dispense(3)
        sim.cartridges[1].dispense(2)
        queues = sim.get_dispense_queues()
        self.assertEqual(queues['W'], 5)
        self.assertEqual(queues['WJ'], 0)

    def test_belt_assignment_and_type_changes(self):
        """Verify each cartridge has its own belt and belt types can change."""
        sim = FreezerAutoloaderSimulator()
        # Default: belts 1&2 are W, belts 3&4 are WJ
        self.assertEqual(sim.belt1.patty_type, 'W')
        self.assertEqual(sim.belt2.patty_type, 'W')
        self.assertEqual(sim.belt3.patty_type, 'WJ')
        self.assertEqual(sim.belt4.patty_type, 'WJ')

        # W request should succeed immediately (carts 1&2 have W, belts 1&2 are W)
        self.assertTrue(sim.request_patties('W', 1))
        # WJ request should succeed immediately (carts 3&4 have WJ, belts 3&4 are WJ)
        self.assertTrue(sim.request_patties('WJ', 1))

        # Change belt 3 away from WJ; cart 3 can no longer feed
        # but cart 4 / belt 4 still can
        sim.set_belt_type(3, 'W')
        self.assertTrue(sim.request_patties('WJ', 1))

        # Change belt 4 away from WJ too; now no WJ belt is available
        sim.set_belt_type(4, 'W')
        self.assertFalse(sim.request_patties('WJ', 1))

        # Restore belt 4 to WJ; requests should succeed again
        sim.set_belt_type(4, 'WJ')
        self.assertTrue(sim.request_patties('WJ', 1))
        # the previous WJ dispense just happened so this one stays queued
        total_wj_queued = sum(c.dispense_queue for c in sim.cartridges if c.patty_type == 'WJ')
        self.assertGreater(total_wj_queued, 0)
        from unittest.mock import patch
        # use a far-future time so all queued patties can drain one-by-one
        with patch('src.models.simulator.time.time') as mock_time:
            future = 9_999_999_999.0
            for _ in range(total_wj_queued):
                mock_time.return_value = future
                sim.update()
                future += 6.0
        total_wj_queued = sum(c.dispense_queue for c in sim.cartridges if c.patty_type == 'WJ')
        self.assertEqual(total_wj_queued, 0)

    def test_request_wj_uses_belts3_and_4(self):
        """WJ requests should succeed using belts 3 & 4 (default WJ configuration)."""
        sim = FreezerAutoloaderSimulator()
        # cartridges 3&4 and belts 3&4 default to WJ
        self.assertTrue(sim.request_patties('WJ', 2))
        self.assertIsNone(sim.last_error)
        # stock-first allocation means one patty dispatches immediately, one remains queued
        self.assertEqual(sim.get_dispense_queues()['WJ'], 1)

    def test_request_distributes_to_highest_stocked_cartridges(self):
        """Requests should be split across eligible cartridges with the highest stock first."""
        sim = FreezerAutoloaderSimulator()
        sim.reload_cartridge(3, 'WJ')
        sim.reload_cartridge(4, 'WJ')
        sim.set_belt_type(2, 'WJ')
        sim.cartridges[2].patties_in_stack = 3
        sim.cartridges[3].patties_in_stack = 5

        self.assertTrue(sim.request_patties('WJ', 7))
        self.assertEqual(sim.cartridges[3].patties_in_stack, 0)
        self.assertEqual(sim.cartridges[2].patties_in_stack, 1)
        self.assertEqual(sim.get_dispense_queues()['WJ'], 5)

    def test_request_wj_patty_dispenses_on_belt3_or_4(self):
        """WJ requests use belts 3 & 4 (default config); W belts are not touched."""
        sim = FreezerAutoloaderSimulator()
        from unittest.mock import patch

        # Belts 3&4 default to WJ; request should succeed immediately
        self.assertEqual(sim.belt3.patty_type, 'WJ')
        self.assertEqual(sim.belt4.patty_type, 'WJ')
        with patch('src.models.simulator.time.time') as mock_time:
            mock_time.return_value = 100.0
            self.assertTrue(sim.request_patties('WJ', 1))
            # Request two more; one is dispatched immediately and one remains queued
            mock_time.return_value = 200.0
            self.assertTrue(sim.request_patties('WJ', 2))

        # First patty is immediately dispatched; no remaining queue
        self.assertEqual(sim.cartridges[2].dispense_queue + sim.cartridges[3].dispense_queue, 1)
        # W belts untouched
        self.assertEqual(sim.belt1.get_patty_count(), 0)
        self.assertEqual(sim.belt2.get_patty_count(), 0)
        self.assertEqual(sim.belt3.get_patty_count() + sim.belt4.get_patty_count(), 2)

    def test_parallel_belt_dispatch_uses_multiple_cartridges(self):
        """Queued patties on different cartridges should start on their belts simultaneously."""
        from unittest.mock import patch

        sim = FreezerAutoloaderSimulator()
        sim.cartridges[0].dispense(2)
        sim.cartridges[1].dispense(2)
        with patch('src.models.simulator.time.time') as mock_time:
            mock_time.return_value = 100.0
            sim._process_queues()
            self.assertEqual(sim.belt1.get_patty_count(), 1)
            self.assertEqual(sim.belt2.get_patty_count(), 1)
            self.assertEqual(sim.get_dispense_queues()['W'], 2)

            mock_time.return_value = 111.0
            sim.update()
            self.assertEqual(sim.belt1.get_patty_count(), 2)
            self.assertEqual(sim.belt2.get_patty_count(), 2)
            self.assertEqual(sim.get_dispense_queues()['W'], 0)


if __name__ == "__main__":
    unittest.main()