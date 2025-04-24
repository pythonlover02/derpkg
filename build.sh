#!/bin/bash

# Check if virtual environment exists, if not create it
if [ ! -d "py_env" ]; then
    echo "Creating Python virtual environment..."
    python -m venv py_env
    
    # Activate virtual environment and install requirements
    source py_env/bin/activate
    pip install -r requirements.txt
else
    # Just activate the existing virtual environment
    source py_env/bin/activate
    pip update
fi

# Create release directory if it doesn't exist
mkdir -p release

# Run PyInstaller on the derpkg.py file
pyinstaller --onefile src/derpkg.py

# Copy the executable to the release folder
cp dist/derpkg release/

# Remove build artifacts
rm -rf dist build __pycache__ derpkg.spec

echo "Build completed successfully. Executable is in the release folder."

# Deactivate virtual environment
deactivate
