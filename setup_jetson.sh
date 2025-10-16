#!/bin/bash

# Setup script for Jetson Nano
# This script prepares the environment for running Snake Game with RL

echo "=========================================="
echo "Jetson Nano Setup for Snake Game with RL"
echo "=========================================="
echo ""

# Update system
echo "Updating system packages..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-pygame \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev

# Install Python packages
echo "Installing Python packages..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create model directory
mkdir -p model

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To run the game:"
echo "  ./run.sh"
echo ""
echo "Or directly:"
echo "  python3 main.py"
echo ""
echo "For Docker deployment:"
echo "  xhost +local:docker"
echo "  docker compose build"
echo "  docker compose up"
echo ""
