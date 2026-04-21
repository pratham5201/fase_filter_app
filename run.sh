#!/bin/bash
# Face Filter App - Run Script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run: chmod +x install.sh && ./install.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the app
python3 main.py
