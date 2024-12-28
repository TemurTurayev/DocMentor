from enum import Enum
from typing import Optional
import json
import os

class Mode(Enum):
    PRIVATE = "private"
    PUBLIC = "public"

class ModeManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.current_mode: Mode = self.load_mode()
    
    def load_mode(self) -> Mode:
        """Load mode from config or return default"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                return Mode(config.get("mode", Mode.PRIVATE.value))
        return Mode.PRIVATE
    
    def save_mode(self) -> None:
        """Save current mode to config"""
        with open(self.config_path, 'w') as f:
            json.dump({"mode": self.current_mode.value}, f)
    
    def switch_mode(self, mode: Mode) -> None:
        """Switch to specified mode"""
        self.current_mode = mode
        self.save_mode()
    
    def get_current_mode(self) -> Mode:
        """Get current mode"""
        return self.current_mode