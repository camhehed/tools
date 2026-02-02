#!/bin/bash
# Quick start script for Stock Market Simulation Game

echo "Stock Market Simulation Game - Quick Start"
echo "=========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"
echo ""

# Check if we're in the stock_game directory
if [ ! -f "main.py" ]; then
    echo "Error: Please run this script from the stock_game directory"
    echo "Usage: cd stock_game && bash quickstart.sh"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Check for tkinter
echo "Checking for Tkinter..."
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "Warning: Tkinter is not installed!"
    echo "Please install it using one of these commands:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo "  macOS/Windows: Should be included with Python"
    echo ""
    exit 1
fi

echo ""
echo "All dependencies are installed!"
echo ""
echo "Starting Stock Market Simulation Game..."
echo "=========================================="
echo ""

# Run the game
python3 main.py
