#!/usr/bin/env python3

from .base import BasePackageManager
from .colors import Colors

class PacmanManager(BasePackageManager):
    """Pacman package manager for Arch Linux."""
    
    def __init__(self):
        super().__init__()
        self.commands = {
            "search": ["pacman", "-Ss"],
            "install": ["pacman", "-S"],
            "update": ["pacman", "-Syu"],
            "remove": ["pacman", "-Rs"]
        }
    
    def is_available(self):
        """Check if pacman is available on the system."""
        return self.cmd_exists("pacman")
    
    def search(self, packages):
        """Search for packages using pacman."""
        return self.commands["search"] + packages
    
    def install(self, packages):
        """Install packages using pacman."""
        return self.commands["install"] + packages
    
    def update(self):
        """Update all packages using pacman."""
        return self.commands["update"]
    
    def remove(self, packages):
        """Remove packages using pacman."""
        return self.commands["remove"] + packages
    
    def format_search_results(self, output):
        """Format pacman search results."""
        lines = output.strip().split('\n')
        
        current_pkg = None
        results = []
        
        for line in lines:
            if not line.startswith(' '):  # This is a package line, not a description
                parts = line.split(' ')
                
                if len(parts) >= 2:
                    repo_pkg = parts[0]  # format: repo/package
                    version = parts[1]
                    
                    # Check if package is installed
                    is_installed = '[installed]' in line
                    
                    # Split repo/package
                    if '/' in repo_pkg:
                        repo, pkg = repo_pkg.split('/', 1)
                    else:
                        repo, pkg = '', repo_pkg
                    
                    # Format with colors
                    if is_installed:
                        print(f"{Colors.BOLD}{pkg}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{repo}{Colors.ENDC} {Colors.RED}-i{Colors.ENDC}")
                    else:
                        print(f"{Colors.BOLD}{pkg}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{repo}{Colors.ENDC}")
        
        return results 