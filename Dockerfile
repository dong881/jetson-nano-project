# Dockerfile for Jetson Nano with CUDA support
FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3

# Set working directory
WORKDIR /app

# Remove problematic Kitware repository to fix GPG key error
# This comprehensively removes all Kitware repository references that may cause GPG key errors
RUN rm -f /etc/apt/sources.list.d/kitware.list* && \
    find /etc/apt/sources.list.d/ -type f -name '*kitware*' -delete && \
    sed -i '/kitware/d' /etc/apt/sources.list 2>/dev/null || true && \
    apt-key del 16FAAD7AF99A65E2 2>/dev/null || true

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
