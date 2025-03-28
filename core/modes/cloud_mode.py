"""
Cloud mode implementation for DocMentor.
This is a new filename for what was previously public_mode.py.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union, Any

from .base_mode import BaseMode
from .public_mode import PublicMode

logger = logging.getLogger(__name__)

# For backwards compatibility, use PublicMode as CloudMode
# In the future, this class should replace PublicMode with enhanced functionality
CloudMode = PublicMode

# Usage example:
# cloud_mode = CloudMode(
#     storage_path="path/to/storage", 
#     cloud_endpoint="https://cloud.endpoint", 
#     api_key="your_api_key",
#     model_name="model_name"
# )
