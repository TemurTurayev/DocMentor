"""
Local mode implementation for DocMentor.
This is a new filename for what was previously private_mode.py.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union, Any

from .base_mode import BaseMode
from .private_mode import PrivateMode

logger = logging.getLogger(__name__)

# For backwards compatibility, use PrivateMode as LocalMode
# In the future, this class should replace PrivateMode with enhanced functionality
LocalMode = PrivateMode

# Usage example:
# local_mode = LocalMode(storage_path="path/to/storage", model_name="model_name")
