#!/usr/bin/env python3

import subprocess
import shutil
import os

class BasePackageManager:
    """Base class for package managers."""
    
    def __init__(self):
        self.commands = {}
        
    def is_available(self):
        """Check if this package manager is available on the system."""
        return False
        
    def search(self, packages):
        """Search for packages."""
        raise NotImplementedError("Search method not implemented")
        
    def install(self, packages):
        """Install packages."""
        raise NotImplementedError("Install method not implemented")
        
    def update(self):
        """Update all packages."""
        raise NotImplementedError("Update method not implemented")
        
    def remove(self, packages):
        """Remove packages."""
        raise NotImplementedError("Remove method not implemented")
        
    def format_search_results(self, output):
        """Format search results."""
        raise NotImplementedError("Format search results method not implemented")
    
    def cmd_exists(self, cmd):
        """Check if a command exists and is callable."""
        try:
            # Use shutil.which first as it's more reliable
            if shutil.which(cmd) is not None:
                return True
            
            # Check common binary paths that might not be in PATH when using sudo
            common_paths = [
                "/usr/bin",
                "/usr/local/bin",
                "/bin",
                "/sbin",
                "/usr/sbin",
                "/usr/local/sbin"
            ]
            
            for path in common_paths:
                cmd_path = os.path.join(path, cmd)
                if os.path.exists(cmd_path) and os.access(cmd_path, os.X_OK):
                    return True
                
            # Fallback to which command
            return subprocess.call(["which", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        except Exception:
            return False 