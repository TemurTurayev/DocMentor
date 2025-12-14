"""Modes initialization."""

from .base_mode import BaseMode
from .local_mode import LocalMode
from .cloud_mode import CloudMode
from .hybrid_mode import HybridMode

# Backwards compatibility aliases
PrivateMode = LocalMode
PublicMode = CloudMode

__all__ = ['BaseMode', 'LocalMode', 'CloudMode', 'HybridMode', 'PrivateMode', 'PublicMode']