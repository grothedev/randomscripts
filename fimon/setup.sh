#!/bin/bash

# File Monitor Setup Script

echo "Setting up File Monitor..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

# Install required Python packages
echo "Installing required packages..."
pip3 install -r requirements.txt

# Make the script executable
chmod +x file_monitor.py

# Create a sample config if it doesn't exist
if [ ! -f "config.ini" ]; then
    echo "Creating sample configuration file..."
    python3 file_monitor.py --config config.ini --create-config
    echo ""
    echo "Configuration file created at: config.ini"
    echo "Please edit this file with your specific settings before running the monitor."
else
    echo "Configuration file already exists: config.ini"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the file monitor:"
echo "  python3 file_monitor.py -c config.ini"
echo ""
echo "Make sure to edit config.ini with your specific settings first."
