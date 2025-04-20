#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
import time
import shutil

# Import our package manager modules
from pm import (
    Colors,
    BasePackageManager,
    PacmanManager,
    AptManager,
    ZypperManager,
    FlatpakManager,
    YayManager
)


class Display:
    @staticmethod
    def get_terminal_width():
        """Get terminal width for proper formatting."""
        try:
            return shutil.get_terminal_size().columns
        except Exception:
            return 80
    
    @staticmethod
    def print_header(text):
        """Print a formatted header."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    
    @staticmethod
    def print_step(text):
        """Print a step in the process."""
        print(f"\n{Colors.BLUE}{Colors.BOLD}> {text}:{Colors.ENDC}")
    
    @staticmethod
    def print_success(text, add_newline=True):
        """Print a success message."""
        newline = "\n" if add_newline else ""
        print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}{newline}")
    
    @staticmethod
    def print_warning(text, add_newline=True):
        """Print a warning message."""
        newline = "\n" if add_newline else ""
        print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}{newline}")
    
    @staticmethod
    def print_error(text, add_newline=True):
        """Print an error message."""
        newline = "\n" if add_newline else ""
        print(f"{Colors.RED}✗ {text}{Colors.ENDC}{newline}")
    
    @staticmethod
    def print_table(headers, rows):
        """Print a formatted table."""
        if not rows:
            return
            
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):  # Ensure we don't go beyond our header columns
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Cap column widths to avoid extremely wide columns
        max_width = Display.get_terminal_width() // len(headers) - 3  # Allow for separators
        col_widths = [min(width, max_width) for width in col_widths]
        
        # Print headers
        header_line = ' | '.join(h.ljust(col_widths[i]) if i < len(col_widths) else h 
                              for i, h in enumerate(headers))
        print(f"{Colors.BOLD}{header_line}{Colors.ENDC}")
        print('-' * len(header_line))
        
        # Print rows
        for row in rows:
            formatted_row = []
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    # Truncate cell content if it's too long
                    cell_str = str(cell)
                    if len(cell_str) > col_widths[i]:
                        cell_str = cell_str[:col_widths[i]-3] + "..."
                    formatted_row.append(cell_str.ljust(col_widths[i]))
                else:
                    formatted_row.append(str(cell))
            
            print(' | '.join(formatted_row))


class PackageManager:
    def __init__(self):
        # Initialize individual package managers
        self.package_managers = {
            "pacman": PacmanManager(),
            "apt": AptManager(),
            "zypper": ZypperManager(),
            "flatpak": FlatpakManager(),
            "yay": YayManager()
        }
        
        # Detect available package managers
        self.available_managers = self._detect_package_managers()
        # System managers are those that aren't flatpak or yay
        self.system_managers = {k: v for k, v in self.available_managers.items() 
                               if k not in ["flatpak", "yay"]}
        
        # Create a lowercase mapping of package manager names for case-insensitive matching
        self.lowercase_managers = {name.lower(): name for name in self.available_managers.keys()}
        
    def _detect_package_managers(self):
        """Detect which package managers are available on the system."""
        available = {}
        
        for name, manager in self.package_managers.items():
            if manager.is_available():
                available[name] = manager.commands
                
        return available
    
    def _validate_packages(self, packages):
        """Validate that packages are provided and properly formatted."""
        if not packages:
            Display.print_error("No packages specified")
            return False
            
        for pkg in packages:
            if not isinstance(pkg, str) or not pkg.strip():
                Display.print_error(f"Invalid package name: {pkg}")
                return False
        
        return True
    
    def _ask_manager_preference(self, action_type="install", manager="flatpak"):
        """Ask user if they prefer to use alternative package manager instead of native package manager."""
        if manager not in self.available_managers:
            return False
        
        if not self.system_managers:
            # If only alternative manager is available, use it without asking
            return True
            
        try:
            if manager == "flatpak":
                if action_type == "install":
                    prompt = f"{Colors.YELLOW}Install from Flatpak instead of native package manager? (y/N): {Colors.ENDC}"
                elif action_type == "remove":
                    prompt = f"{Colors.YELLOW}Remove from Flatpak instead of native package manager? (y/N): {Colors.ENDC}"
                elif action_type == "search":
                    prompt = f"{Colors.YELLOW}Include Flatpak in the search process? (y/N): {Colors.ENDC}"
                else:  # update
                    prompt = f"{Colors.YELLOW}Include Flatpak in the update process? (y/N): {Colors.ENDC}"
            elif manager == "yay":
                if action_type == "install":
                    prompt = f"{Colors.YELLOW}Install using Yay instead of native package manager? (y/N): {Colors.ENDC}"
                elif action_type == "remove":
                    prompt = f"{Colors.YELLOW}Remove using Yay instead of native package manager? (y/N): {Colors.ENDC}"
                elif action_type == "search":
                    prompt = f"{Colors.YELLOW}Include Yay in the search process? (y/N): {Colors.ENDC}"
                else:  # update
                    prompt = f"{Colors.YELLOW}Include Yay in the update process? (y/N): {Colors.ENDC}"
            else:
                # Default prompt for unknown managers
                prompt = f"{Colors.YELLOW}Use {manager} for this operation? (y/N): {Colors.ENDC}"
                
            # Default to No for all operations
            response = input(prompt).lower().strip()
            return response in ('y', 'yes')
                
        except (KeyboardInterrupt, EOFError):
            print()  # Add newline after ^C
            Display.print_warning("Operation cancelled by user")
            return False
    
    def _ask_flatpak_preference(self, action_type="install"):
        """Legacy method for backward compatibility."""
        return self._ask_manager_preference(action_type, "flatpak")
    
    def _run_command(self, cmd, packages=None):
        """Run a command with given packages."""
        command = cmd.copy()
        if packages:
            command.extend(packages)
        
        # Check if we need to add sudo
        needs_sudo = "flatpak" not in command[0] and "yay" not in command[0]
        
        display_cmd = command.copy()
        if needs_sudo:
            display_cmd = ["sudo"] + display_cmd
        
        Display.print_step(f"Running: {' '.join(display_cmd)}")
        try:
            # For interactive commands (like flatpak install without -y), use call instead of run
            if "flatpak" in command[0] and "install" in command:
                result = subprocess.call(command)
                if result == 0:
                    Display.print_success(f"Command completed successfully")
                    return True
                else:
                    Display.print_error(f"Command failed with exit code {result}")
                    return False
            else:
                # If needs sudo, prepend it to the command
                exec_cmd = command
                if needs_sudo:
                    exec_cmd = ["sudo"] + command
                
                result = subprocess.run(exec_cmd, check=True, text=True, capture_output=True)
                
                # Format output for different package managers
                if result.stdout.strip():
                    # Special handling for flatpak search output
                    if "flatpak" in command[0] and "search" in command:
                        # Flatpak search produces tab-delimited output
                        try:
                            lines = result.stdout.strip().split('\n')
                            # Skip empty lines
                            lines = [line for line in lines if line.strip()]
                            
                            if lines:
                                headers = ["Name", "Description", "Application ID", "Version", "Branch", "Origin"]
                                rows = []
                                
                                for line in lines:
                                    parts = line.split('\t')
                                    if len(parts) >= 6:
                                        # Standard flatpak output format
                                        rows.append(parts[:6])
                                    elif len(parts) >= 2:
                                        # Some versions might have different format
                                        # Try to extract what we can
                                        name = parts[0]
                                        description = parts[1] if len(parts) > 1 else ""
                                        app_id = ""
                                        version = ""
                                        branch = ""
                                        origin = ""
                                        
                                        # Try to extract app ID if present in output
                                        for part in parts:
                                            if '.' in part and len(part.split('.')) >= 3:
                                                app_id = part
                                                break
                                        
                                        rows.append([name, description, app_id, version, branch, origin])
                                
                                # Only print the table if we have rows
                                if rows:
                                    Display.print_table(headers, rows)
                                else:
                                    # If parsing failed, print original
                                    print(result.stdout)
                            else:
                                # Empty result
                                print(result.stdout)
                        except Exception as e:
                            # Fallback to printing the raw output if parsing fails
                            print(result.stdout)
                    else:
                        # For other package managers, just print the output as is
                        print(result.stdout)
                
                Display.print_success(f"Command completed successfully")
                return True
        except subprocess.CalledProcessError as e:
            Display.print_error(f"Command failed with exit code {e.returncode}")
            if e.stderr:
                print(f"{Colors.RED}{e.stderr}{Colors.ENDC}")
            return False
        except Exception as e:
            Display.print_error(f"Unexpected error: {str(e)}")
            return False
    
    # Helper method to convert source to proper case if it exists
    def _normalize_source(self, source):
        """Convert source string to proper case if it exists in available managers."""
        if not source:
            return None
        
        # Check lowercase version against our mapping
        lowercase_source = source.lower()
        if lowercase_source in self.lowercase_managers:
            return self.lowercase_managers[lowercase_source]
        
        return source  # Return original if not found
    
    def search(self, packages, source=None):
        """Search for packages in specified or all available package managers."""
        Display.print_header("Package Search")
        
        if not self._validate_packages(packages):
            return
        
        # Normalize source to proper case
        source = self._normalize_source(source)
            
        # Ask if user wants to include flatpak/yay in search
        use_flatpak = (source == "flatpak" or 
                      (source is None and "flatpak" in self.available_managers and 
                       self._ask_manager_preference("search", "flatpak")))
                       
        use_yay = (source == "yay" or 
                  (source is None and "yay" in self.available_managers and 
                   self._ask_manager_preference("search", "yay")))
        
        results = []
        
        # Get list of installed flatpak packages if we're going to search flatpak
        installed_flatpaks = []
        if use_flatpak and "flatpak" in self.available_managers:
            try:
                flatpak_manager = self.package_managers["flatpak"]
                installed_flatpaks = flatpak_manager.get_installed_flatpaks()
            except Exception as e:
                Display.print_warning(f"Failed to get list of installed flatpaks: {str(e)}")
        
        if source and source in self.available_managers:
            # Search in specific package manager
            self._search_in_manager(source, packages, installed_flatpaks)
        else:
            # Use system package managers
            for manager in self.system_managers:
                self._search_in_manager(manager, packages, installed_flatpaks)
            
            # Also use yay if requested
            if use_yay and "yay" in self.available_managers:
                self._search_in_manager("yay", packages, installed_flatpaks)
                
            # Also use flatpak if requested
            if use_flatpak and "flatpak" in self.available_managers:
                self._search_in_manager("flatpak", packages, installed_flatpaks)
    
    def _search_in_manager(self, manager, packages, installed_flatpaks):
        """Search for packages in a specific package manager and display formatted results."""
        Display.print_step(f"Searching for {', '.join(packages)} using {manager}")
        
        cmd = self.available_managers[manager]["search"]
        
        try:
            # Add sudo if needed (not for flatpak or yay)
            needs_sudo = manager not in ["flatpak", "yay"]
            full_cmd = cmd + packages
            if needs_sudo:
                full_cmd = ["sudo"] + full_cmd
                
            result = subprocess.run(full_cmd, check=False, text=True, capture_output=True)
            
            if result.returncode != 0:
                Display.print_error(f"Search failed with exit code {result.returncode}")
                if result.stderr:
                    print(f"{Colors.RED}{result.stderr.strip()}{Colors.ENDC}")
                return
                
            if not result.stdout.strip():
                Display.print_warning(f"No packages found")
                return
                
            # Process and display formatted results based on package manager
            if manager == "pacman":
                self.package_managers[manager].format_search_results(result.stdout)
            elif manager == "apt":
                self.package_managers[manager].format_search_results(result.stdout)
            elif manager == "flatpak":
                self.package_managers[manager].format_search_results(result.stdout, installed_flatpaks)
            elif manager == "zypper":
                self.package_managers[manager].format_search_results(result.stdout)
            elif manager == "yay":
                self.package_managers[manager].format_search_results(result.stdout)
            else:
                # For other package managers, just print the raw output for now
                print(result.stdout)
                
            Display.print_success(f"Search completed", add_newline=False)
            
        except Exception as e:
            Display.print_error(f"Unexpected error during search: {str(e)}")
    
    def install(self, packages, source=None):
        """Install packages using specified or all available package managers."""
        Display.print_header("Package Installation")
        
        if not self._validate_packages(packages):
            return
        
        # Normalize source to proper case
        source = self._normalize_source(source)
            
        # If source is specified, use that
        if source:
            if source not in self.available_managers:
                Display.print_error(f"Package manager '{source}' not found or not available")
                return
                
            cmd = self.available_managers[source]["install"]
            Display.print_step(f"Installing {', '.join(packages)} using {source}")
            
            # For flatpak, use with flathub by default
            if source == "flatpak":
                # Pass directly to flatpak, no sudo needed
                flatpak_cmd = ["flatpak", "install", "flathub"] + packages
                return_code = subprocess.call(flatpak_cmd)
                if return_code == 0:
                    Display.print_success(f"Package installation completed", add_newline=False)
                else:
                    Display.print_error(f"Package installation failed with code {return_code}", add_newline=False)
            else:
                # Pass to the package manager with sudo if needed
                full_cmd = cmd + packages
                if source != "yay":  # yay doesn't need sudo
                    full_cmd = ["sudo"] + full_cmd
                
                return_code = subprocess.call(full_cmd)
                if return_code == 0:
                    Display.print_success(f"Package installation completed", add_newline=False)
                else:
                    Display.print_error(f"Package installation failed with code {return_code}", add_newline=False)
        else:
            # Ask if user wants to use alternative package managers
            use_flatpak = "flatpak" in self.available_managers and self._ask_manager_preference("install", "flatpak")
            use_yay = "yay" in self.available_managers and self._ask_manager_preference("install", "yay")
            
            if use_flatpak:
                Display.print_step(f"Installing {', '.join(packages)} using flatpak")
                # Pass directly to flatpak
                flatpak_cmd = ["flatpak", "install", "flathub"] + packages
                return_code = subprocess.call(flatpak_cmd)
                if return_code == 0:
                    Display.print_success(f"Package installation completed", add_newline=False)
                else:
                    Display.print_error(f"Package installation failed with code {return_code}", add_newline=False)
            elif use_yay:
                Display.print_step(f"Installing {', '.join(packages)} using yay")
                cmd = self.available_managers["yay"]["install"]
                full_cmd = cmd + packages
                return_code = subprocess.call(full_cmd)
                if return_code == 0:
                    Display.print_success(f"Package installation completed", add_newline=False)
                else:
                    Display.print_error(f"Package installation failed with code {return_code}", add_newline=False)
            else:
                # Use first available system package manager
                if self.system_managers:
                    manager = next(iter(self.system_managers))
                    cmd = self.available_managers[manager]["install"]
                    Display.print_step(f"Installing {', '.join(packages)} using {manager}")
                    # Pass directly to the package manager with sudo
                    full_cmd = cmd + packages
                    full_cmd = ["sudo"] + full_cmd
                    return_code = subprocess.call(full_cmd)
                    if return_code == 0:
                        Display.print_success(f"Package installation completed", add_newline=False)
                    else:
                        Display.print_error(f"Package installation failed with code {return_code}", add_newline=False)
                else:
                    Display.print_warning("No native package managers available", add_newline=False)
    
    def update(self):
        """Update all packages from all available package managers."""
        Display.print_header("System Update")
        
        # Ask if user wants to include alternative package managers in updates
        include_flatpak = "flatpak" in self.available_managers and self._ask_manager_preference("update", "flatpak")
        include_yay = "yay" in self.available_managers and self._ask_manager_preference("update", "yay")
        
        # Update system package managers
        for manager in self.system_managers:
            cmd = self.available_managers[manager]["update"]
            Display.print_step(f"Updating packages using {manager}")
            # Add sudo for system package managers
            full_cmd = ["sudo"] + cmd
            return_code = subprocess.call(full_cmd)
            if return_code == 0:
                Display.print_success(f"{manager.capitalize()} update completed")
            else:
                Display.print_error(f"{manager.capitalize()} update failed with code {return_code}")
            
            # Add a small delay between package managers to avoid overwhelming output
            time.sleep(0.5)
        
        # Update yay if requested
        if include_yay and "yay" in self.available_managers:
            cmd = self.available_managers["yay"]["update"]
            Display.print_step("Updating packages using Yay")
            # No sudo needed for yay
            return_code = subprocess.call(cmd)
            if return_code == 0:
                Display.print_success(f"Yay update completed")
            else:
                Display.print_error(f"Yay update failed with code {return_code}")
            
            # Add a small delay between package managers
            time.sleep(0.5)
            
        # Update flatpak if requested
        if include_flatpak and "flatpak" in self.available_managers:
            cmd = self.available_managers["flatpak"]["update"]
            Display.print_step("Updating Flatpak applications")
            # No sudo needed for flatpak
            return_code = subprocess.call(cmd)
            if return_code == 0:
                Display.print_success(f"Flatpak update completed", add_newline=False)
            else:
                Display.print_error(f"Flatpak update failed with code {return_code}", add_newline=False)
    
    def remove(self, packages, source=None):
        """Remove packages using specified or all available package managers."""
        Display.print_header("Package Removal")
        
        if not self._validate_packages(packages):
            return
        
        # Normalize source to proper case
        source = self._normalize_source(source)
            
        # If source is specified, use that
        if source:
            if source not in self.available_managers:
                Display.print_error(f"Package manager '{source}' not found or not available")
                return
                
            cmd = self.available_managers[source]["remove"]
            Display.print_step(f"Removing {', '.join(packages)} using {source}")
            
            # For flatpak, handle separately
            if source == "flatpak":
                # Pass directly to flatpak, no sudo needed
                flatpak_cmd = ["flatpak", "uninstall"] + packages
                return_code = subprocess.call(flatpak_cmd)
                if return_code == 0:
                    Display.print_success(f"Package removal completed")
                    # Cleanup after successful removal
                    Display.print_step("Cleaning up unused Flatpak runtimes")
                    cleanup_cmd = self.available_managers[source]["cleanup"]
                    cleanup_return_code = subprocess.call(cleanup_cmd)
                    if cleanup_return_code == 0:
                        Display.print_success(f"Cleanup completed", add_newline=False)
                    else:
                        Display.print_error(f"Cleanup failed with code {cleanup_return_code}", add_newline=False)
                else:
                    Display.print_error(f"Package removal failed with code {return_code}", add_newline=False)
            else:
                # Pass to package manager with sudo if needed
                full_cmd = cmd + packages
                if source != "yay":  # yay doesn't need sudo
                    full_cmd = ["sudo"] + full_cmd
                    
                return_code = subprocess.call(full_cmd)
                if return_code == 0:
                    Display.print_success(f"Package removal completed", add_newline=False)
                else:
                    Display.print_error(f"Package removal failed with code {return_code}", add_newline=False)
        else:
            # Ask if user wants to use alternative package managers
            use_flatpak = "flatpak" in self.available_managers and self._ask_manager_preference("remove", "flatpak")
            use_yay = "yay" in self.available_managers and self._ask_manager_preference("remove", "yay")
            
            if use_flatpak:
                Display.print_step(f"Removing {', '.join(packages)} from flatpak")
                # Pass directly to flatpak, no sudo needed
                flatpak_cmd = ["flatpak", "uninstall"] + packages
                return_code = subprocess.call(flatpak_cmd)
                if return_code == 0:
                    Display.print_success(f"Package removal completed")
                    # Cleanup after successful removal
                    Display.print_step("Cleaning up unused Flatpak runtimes")
                    cleanup_cmd = self.available_managers["flatpak"]["cleanup"]
                    cleanup_return_code = subprocess.call(cleanup_cmd)
                    if cleanup_return_code == 0:
                        Display.print_success(f"Cleanup completed", add_newline=False)
                    else:
                        Display.print_error(f"Cleanup failed with code {cleanup_return_code}", add_newline=False)
                else:
                    Display.print_error(f"Package removal failed with code {return_code}", add_newline=False)
            elif use_yay:
                Display.print_step(f"Removing {', '.join(packages)} using yay")
                cmd = self.available_managers["yay"]["remove"]
                full_cmd = cmd + packages
                # No sudo needed for yay
                return_code = subprocess.call(full_cmd)
                if return_code == 0:
                    Display.print_success(f"Package removal completed", add_newline=False)
                else:
                    Display.print_error(f"Package removal failed with code {return_code}", add_newline=False)
            else:
                # Use first available system package manager
                if self.system_managers:
                    manager = next(iter(self.system_managers))
                    cmd = self.available_managers[manager]["remove"]
                    Display.print_step(f"Removing {', '.join(packages)} using {manager}")
                    # Pass to package manager with sudo
                    full_cmd = cmd + packages
                    full_cmd = ["sudo"] + full_cmd
                    return_code = subprocess.call(full_cmd)
                    if return_code == 0:
                        Display.print_success(f"Package removal completed", add_newline=False)
                    else:
                        Display.print_error(f"Package removal failed with code {return_code}", add_newline=False)
                else:
                    Display.print_warning("No native package managers available", add_newline=False)
                    
    def list_available_managers(self):
        """Display available package managers."""
        Display.print_header("Available Package Managers")
        
        if not self.available_managers:
            Display.print_warning("No package managers detected on this system", add_newline=False)
            return
        
        Display.print_step("System Package Managers:")
        if self.system_managers:
            for manager in self.system_managers:
                Display.print_success(manager.capitalize(), add_newline=False)
        else:
            Display.print_warning("No native package managers detected", add_newline=False)
            
        Display.print_step("Alternative Package Managers:")
        if "flatpak" in self.available_managers:
            Display.print_success("Flatpak", add_newline=False)
        else:
            Display.print_warning("Flatpak not detected", add_newline=False)
            
        if "yay" in self.available_managers:
            Display.print_success("Yay", add_newline=False)
        else:
            Display.print_warning("Yay not detected", add_newline=False)


def is_running_as_sudo():
    """Check if the program is running with sudo/root privileges."""
    return 'SUDO_USER' in os.environ or os.geteuid() == 0


def main():
    try:
        # Exit if running with sudo
        if is_running_as_sudo():
            Display.print_error("This program should not be run with sudo privileges.")
            Display.print_error("Sudo will be called automatically when needed.")
            return 1
        
        # Custom usage formatter to match desired format
        custom_usage = "derpkg (-h | -u | -i | -r | -s | -l) [-so SOURCE] <packages ...>"
        
        parser = argparse.ArgumentParser(
            description="Unified package manager interface",
            usage=custom_usage,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""Examples:
  derpkg -s firefox                # Search for firefox (will ask which package managers to use)
  derpkg -i firefox                # Install firefox (will ask which package manager to use)
  derpkg -i firefox -so apt        # Install firefox using apt (case insensitive)
  derpkg -i firefox -so Flatpak    # Install firefox using Flatpak (case insensitive)
  derpkg -u                        # Update all packages (will ask which package managers to use on the Update)
  derpkg -r firefox                # Remove firefox (will ask from which package manager to remove)
  derpkg -r firefox -so pacman     # Remove firefox specifically from pacman
  derpkg -l                        # List available package managers on your system
  derpkg -s lutris -so flatpak     # Search for lutris only in flatpak
  derpkg -i neofetch -so yay       # Install neofetch using yay AUR helper"""
        )
        
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-u", "--update", action="store_true", help="Update all packages")
        group.add_argument("-i", "--install", action="store_true", help="Install packages")
        group.add_argument("-r", "--remove", action="store_true", help="Remove packages")
        group.add_argument("-s", "--search", action="store_true", help="Search for packages")
        group.add_argument("-l", "--list", action="store_true", help="List available package managers")
        
        parser.add_argument("-so", "--source", help="Specify package manager source, if no source is indicated derpkg will ask before doing the task which one/s to use")
        parser.add_argument("packages", nargs="*", help="Packages to operate on")
        
        args = parser.parse_args()
        
        # Create package manager instance
        pkg_manager = PackageManager()
        
        # Normalize source to proper case and validate if provided
        if args.source:
            normalized_source = pkg_manager._normalize_source(args.source)
            if normalized_source not in pkg_manager.available_managers:
                Display.print_error(f"Package manager '{args.source}' not found or not available")
                Display.print_step("Available package managers:")
                for manager in pkg_manager.available_managers.keys():
                    print(f"  - {manager}")
                return 1
            args.source = normalized_source
        
        # Execute requested operation
        if args.update:
            pkg_manager.update()
        elif args.install:
            if not args.packages:
                Display.print_error("No packages specified for installation")
                return 1
            pkg_manager.install(args.packages, args.source)
        elif args.remove:
            if not args.packages:
                Display.print_error("No packages specified for removal")
                return 1
            pkg_manager.remove(args.packages, args.source)
        elif args.search:
            if not args.packages:
                Display.print_error("No packages specified for search")
                return 1
            pkg_manager.search(args.packages, args.source)
        elif args.list:
            pkg_manager.list_available_managers()

        # Add a blank line after all operations are done
        print()

        return 0
        
    except KeyboardInterrupt:
        print()  # Add newline after ^C
        Display.print_warning("Operation cancelled by user")
        return 130
    except Exception as e:
        Display.print_error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

