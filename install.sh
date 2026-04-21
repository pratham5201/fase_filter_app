#!/bin/bash
# Face Filter App - Quick Install Script for Ubuntu

echo "=========================================="
echo "Face Filter App - Installation Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python installation..."
python3 --version

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Install it with: sudo apt install python3 python3-pip"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip
echo "✓ Pip upgraded"

# Install requirements
echo ""
echo "Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Installation completed successfully!"
    echo "=========================================="
    echo ""
    echo "To run the application:"
    echo "  1. Activate the environment: source venv/bin/activate"
    echo "  2. Run the app: python3 main.py"
    echo ""
    echo "Or simply run: ./run.sh"
    echo ""
else
    echo ""
    echo "✗ Installation failed!"
    echo "Please check the error messages above"
    exit 1
fi
