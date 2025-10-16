#!/bin/bash

# Quick Start Script for Snake Game with RL

echo "=========================================="
echo "Snake Game with Reinforcement Learning"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "Error: pip3 is not installed. Please install pip3."
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing required packages..."
    pip3 install -r requirements.txt
else
    echo "Dependencies are already installed."
fi

echo ""
echo "Starting Snake Game..."
echo "- Use Arrow Keys to play in Human mode"
echo "- Click 'Switch to Training' to watch AI learn"
echo "- Click 'Reset Game' to restart"
echo ""

python3 main.py
