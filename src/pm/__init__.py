"""
Package managers module for derpkg.
"""

from .colors import Colors
from .base import BasePackageManager
from .pacman import PacmanManager
from .apt import AptManager
from .zypper import ZypperManager
from .flatpak import FlatpakManager
from .yay import YayManager

__all__ = [
    'Colors',
    'BasePackageManager',
    'PacmanManager',
    'AptManager',
    'ZypperManager',
    'FlatpakManager',
    'YayManager',
] 