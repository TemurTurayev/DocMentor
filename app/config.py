"""
Application configuration.
"""

import os
from pathlib import Path

# Base configuration
APP_NAME = "DocMentor"
VERSION = "0.1.0"

# Storage paths
BASE_PATH = Path.home() / ".docmentor"
PRIVATE_STORAGE = BASE_PATH / "private"
PUBLIC_STORAGE = BASE_PATH / "public"
TEMP_STORAGE = BASE_PATH / "temp"

# Models
MODEL_NAME = "distilbert-base-multilingual-cased"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# UI Configuration
MAX_FILE_SIZE = 200  # MB
SUPPORTED_FORMATS = ["pdf"]
DEFAULT_MODE = "private"

# Initialize storage directories
for path in [PRIVATE_STORAGE, PUBLIC_STORAGE, TEMP_STORAGE]:
    path.mkdir(parents=True, exist_ok=True)