#!/bin/bash

# Create release directory if it doesn't exist
mkdir -p release

# Run PyInstaller on the derpkg.py file
pyinstaller --onefile src/derpkg.py

# Copy the executable to the release folder
cp dist/derpkg release/

# Remove build artifacts
rm -rf dist build __pycache__ derpkg.spec

echo "Build completed successfully. Executable is in the release folder."
