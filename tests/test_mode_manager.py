import unittest
from core.modes.mode_manager import ModeManager, Mode
import os
import json

class TestModeManager(unittest.TestCase):
    def setUp(self):
        self.test_config = "test_config.json"
        self.manager = ModeManager(self.test_config)
    
    def tearDown(self):
        if os.path.exists(self.test_config):
            os.remove(self.test_config)
    
    def test_default_mode(self):
        """Test default mode is private"""
        self.assertEqual(self.manager.get_current_mode(), Mode.PRIVATE)
    
    def test_mode_switch(self):
        """Test mode switching"""
        self.manager.switch_mode(Mode.PUBLIC)
        self.assertEqual(self.manager.get_current_mode(), Mode.PUBLIC)
        
        # Check if mode persists after reload
        new_manager = ModeManager(self.test_config)
        self.assertEqual(new_manager.get_current_mode(), Mode.PUBLIC)

if __name__ == '__main__':
    unittest.main()