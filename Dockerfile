# Dockerfile for Jetson Nano with CUDA support
FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pygame \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
# Note: PyTorch is already included in the base image for Jetson Nano
RUN pip3 install --no-cache-dir pygame numpy

# Copy project files
COPY . .

# Create model directory
RUN mkdir -p model

# Set display environment variable (for X11 forwarding)
ENV DISPLAY=:0

# Run the main application
CMD ["python3", "main.py"]
