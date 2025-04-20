#!/usr/bin/env python3

from .base import BasePackageManager
from .colors import Colors

class AptManager(BasePackageManager):
    """Apt package manager for Debian/Ubuntu."""
    
    def __init__(self):
        super().__init__()
        self.commands = {
            "search": ["apt", "search"],
            "install": ["apt", "install"],
            "update": ["bash", "-c", "apt update && apt upgrade"],
            "remove": ["apt", "autoremove", "--purge"]
        }
    
    def is_available(self):
        """Check if apt is available on the system."""
        return self.cmd_exists("apt")
    
    def search(self, packages):
        """Search for packages using apt."""
        return self.commands["search"] + packages
    
    def install(self, packages):
        """Install packages using apt."""
        return self.commands["install"] + packages
    
    def update(self):
        """Update all packages using apt."""
        return self.commands["update"]
    
    def remove(self, packages):
        """Remove packages using apt."""
        return self.commands["remove"] + packages
    
    def format_search_results(self, output):
        """Format apt search results."""
        lines = output.strip().split('\n')
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            # Skip lines that don't look like package entries
            if line.startswith(' ') or ':' in line[:10] or '/' not in line and not line[0].isalnum():
                continue
                
            parts = line.split(' ', 1)
            
            if len(parts) >= 1:
                # Format: package/repo version architecture [installed,automatic]
                pkg_repo = parts[0].strip()  # format: package/repo
                
                if '/' in pkg_repo:
                    pkg, repo = pkg_repo.split('/', 1)
                else:
                    pkg, repo = pkg_repo, ''
                
                # Extract version and check if installed
                remaining = parts[1].strip() if len(parts) > 1 else ''
                remaining_parts = remaining.split(' ')
                
                # Extract version (first part after package/repo)
                version = remaining_parts[0] if remaining_parts else ''
                
                # Check if package is installed
                is_installed = '[installed' in remaining
                
                # Format with colors
                if is_installed:
                    print(f"{Colors.BOLD}{pkg}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{repo}{Colors.ENDC} {Colors.RED}-i{Colors.ENDC}")
                else:
                    print(f"{Colors.BOLD}{pkg}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{repo}{Colors.ENDC}")
        
        return [] 