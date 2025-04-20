#!/usr/bin/env python3

from .base import BasePackageManager
from .colors import Colors

class ZypperManager(BasePackageManager):
    """Zypper package manager for openSUSE."""
    
    def __init__(self):
        super().__init__()
        self.commands = {
            "search": ["zypper", "search", "-s"],
            "install": ["zypper", "install"],
            "update": ["zypper", "dup"],
            "remove": ["zypper", "remove", "--clean-deps"]
        }
    
    def is_available(self):
        """Check if zypper is available on the system."""
        return self.cmd_exists("zypper")
    
    def search(self, packages):
        """Search for packages using zypper."""
        return self.commands["search"] + packages
    
    def install(self, packages):
        """Install packages using zypper."""
        return self.commands["install"] + packages
    
    def update(self):
        """Update all packages using zypper."""
        return self.commands["update"]
    
    def remove(self, packages):
        """Remove packages using zypper."""
        return self.commands["remove"] + packages
    
    def format_search_results(self, output):
        """Format zypper search results."""
        lines = output.strip().split('\n')
        
        for line in lines:
            # Skip empty or header lines
            if not line.strip() or line.startswith('-') or 'Status' in line:
                continue
            
            # Split by |
            parts = [part.strip() for part in line.split('|')]
            
            if len(parts) >= 6:
                status = parts[0]
                pkg_name = parts[1]
                pkg_type = parts[2]
                version = parts[3]
                arch = parts[4]
                repo = parts[5]
                
                # Check if package is installed (status contains 'i')
                is_installed = 'i' in status
                
                # Format with colors
                if is_installed:
                    print(f"{Colors.BOLD}{pkg_name}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{repo}{Colors.ENDC} {Colors.RED}-i{Colors.ENDC}")
                else:
                    print(f"{Colors.BOLD}{pkg_name}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{repo}{Colors.ENDC}")
        
        return [] 