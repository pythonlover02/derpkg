#!/bin/bash

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Check if the release directory exists
if [ ! -d "release" ]; then
  echo "Release directory not found. Run build.sh first."
  exit 1
fi

# Check if the executable exists
if [ ! -f "release/derpkg" ]; then
  echo "Executable not found in release directory. Run build.sh first."
  exit 1
fi

# Copy the executable to /usr/local/bin/
cp release/derpkg /usr/local/bin/

# Make it executable
chmod +x /usr/local/bin/derpkg

echo "Installation completed successfully. You can now run 'derpkg' from anywhere."
