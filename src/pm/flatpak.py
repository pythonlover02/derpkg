#!/usr/bin/env python3

import subprocess
from .base import BasePackageManager
from .colors import Colors

class FlatpakManager(BasePackageManager):
    """Flatpak package manager."""
    
    def __init__(self):
        super().__init__()
        self.commands = {
            "search": ["flatpak", "search"],
            "install": ["flatpak", "install", "flathub"],
            "update": ["flatpak", "update"],
            "remove": ["flatpak", "uninstall"],
            "cleanup": ["flatpak", "uninstall", "--unused"]
        }
    
    def is_available(self):
        """Check if flatpak is available on the system."""
        return self.cmd_exists("flatpak")
    
    def search(self, packages):
        """Search for packages using flatpak."""
        return self.commands["search"] + packages
    
    def install(self, packages):
        """Install packages using flatpak."""
        return self.commands["install"] + packages
    
    def update(self):
        """Update all packages using flatpak."""
        return self.commands["update"]
    
    def remove(self, packages):
        """Remove packages using flatpak."""
        return self.commands["remove"] + packages
    
    def cleanup(self):
        """Clean up unused runtimes."""
        return self.commands["cleanup"]
    
    def get_installed_flatpaks(self):
        """Get list of installed flatpak applications."""
        installed_flatpaks = []
        try:
            flatpak_list = subprocess.run(["flatpak", "list"], check=True, text=True, capture_output=True)
            if flatpak_list.stdout:
                # Parse the output to get application IDs of installed flatpaks
                for line in flatpak_list.stdout.strip().split('\n'):
                    parts = line.split('\t')
                    if len(parts) >= 3:  # Name, Application ID, Version fields
                        installed_flatpaks.append(parts[1])  # Application ID
        except Exception:
            pass
        
        return installed_flatpaks
    
    def format_search_results(self, output, installed_flatpaks=None):
        """Format flatpak search results."""
        if installed_flatpaks is None:
            installed_flatpaks = self.get_installed_flatpaks()
            
        lines = output.strip().split('\n')
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
                
            parts = line.split('\t')
            
            if len(parts) >= 5:  # Name, Description, Application ID, Version, Branch, Remote
                name = parts[0]
                app_id = parts[2] if len(parts) > 2 else ""
                version = parts[3] if len(parts) > 3 else ""
                branch = parts[4] if len(parts) > 4 else ""
                remote = parts[5] if len(parts) > 5 else ""
                
                # Check if this flatpak is installed
                is_installed = app_id in installed_flatpaks
                
                # Format with colors
                if is_installed:
                    print(f"{Colors.BOLD}{name}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{remote}/{branch}{Colors.ENDC} {Colors.RED}-i{Colors.ENDC}")
                else:
                    print(f"{Colors.BOLD}{name}{Colors.ENDC} {Colors.GREEN}{version}{Colors.ENDC} {Colors.YELLOW}{remote}/{branch}{Colors.ENDC}")
            elif len(parts) == 1 and parts[0].strip():
                # Fallback for unexpected format
                print(parts[0])
        
        return [] 