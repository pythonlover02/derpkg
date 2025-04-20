#!/usr/bin/env python3

from .base import BasePackageManager
from .colors import Colors

class YayManager(BasePackageManager):
    """Yay AUR helper for Arch Linux."""
    
    def __init__(self):
        super().__init__()
        self.commands = {
            "search": ["yay", "-Ss"],
            "install": ["yay", "-S"],
            "update": ["yay", "-Syu"],
            "remove": ["yay", "-Rs"]
        }
    
    def is_available(self):
        """Check if yay is available on the system."""
        return self.cmd_exists("yay")
    
    def search(self, packages):
        """Search for packages using yay."""
        return self.commands["search"] + packages
    
    def install(self, packages):
        """Install packages using yay."""
        return self.commands["install"] + packages
    
    def update(self):
        """Update all packages using yay."""
        return self.commands["update"]
    
    def remove(self, packages):
        """Remove packages using yay."""
        return self.commands["remove"] + packages
    
    def format_search_results(self, output):
        """Format yay search results according to the required format."""
        lines = output.strip().split('\n')
        
        results = []
        
        for line in lines:
            if not line.startswith(' '):  # This is a package line, not a description
                # For yay, the format is: repo/package version user-score (Installed: date)
                
                # First, extract repo/package
                repo_pkg_parts = line.split(' ', 1)
                if len(repo_pkg_parts) < 2:
                    continue
                    
                repo_pkg = repo_pkg_parts[0]  # format: repo/package
                rest_of_line = repo_pkg_parts[1]
                
                # Extract version (first word after repo/package)
                version_parts = rest_of_line.split(' ', 1)
                if len(version_parts) < 1:
                    continue
                    
                version = version_parts[0]
                
                # Check if package is installed
                is_installed = "(Installed:" in line or "[installed]" in line
                
                # Split repo/package
                if '/' in repo_pkg:
                    repo, pkg = repo_pkg.split('/', 1)
                else:
                    repo, pkg = '', repo_pkg
                
                # Format with colors according to required format
                if is_installed:
                    print(f"{Colors.BOLD}{pkg}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{repo}{Colors.ENDC} {Colors.RED}-i{Colors.ENDC}")
                else:
                    print(f"{Colors.BOLD}{pkg}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{repo}{Colors.ENDC}")
        
        return results 