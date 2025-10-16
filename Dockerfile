# Dockerfile for Jetson Nano with CUDA support
FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3

# Set UTF-8 locale environment variables to prevent Unicode encoding errors
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

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
# Upgrade pip to latest version to ensure better package compatibility
RUN pip3 install --upgrade pip

# Install pygame and numpy with --prefer-binary flag to use wheel packages
# This avoids compilation issues and Unicode encoding errors during extraction
RUN pip3 install --no-cache-dir --prefer-binary pygame numpy

# Copy project files
COPY . .

# Create model directory
RUN mkdir -p model

# Remove conflicting NVIDIA libraries to fix runtime mount errors
# This is a workaround for the "file exists" error when using nvidia runtime on Jetson
# The nvidia-container-runtime will mount these libraries from the host
RUN rm -f /usr/lib/aarch64-linux-gnu/libcuda.so* \
    /usr/lib/aarch64-linux-gnu/libnvidia-*.so* \
    /usr/lib/aarch64-linux-gnu/libvisionworks*.so* \
    /usr/lib/aarch64-linux-gnu/libcudnn*.so* \
    /usr/lib/aarch64-linux-gnu/libnvcaffe_parser*.so* \
    /usr/lib/aarch64-linux-gnu/libnvinfer*.so* \
    /usr/lib/aarch64-linux-gnu/libnvonnxparser*.so* \
    /usr/lib/aarch64-linux-gnu/libnvparsers*.so* \
    2>/dev/null || true

# Set display environment variable (for X11 forwarding)
ENV DISPLAY=:0

# Run the main application
CMD ["python3", "main.py"]
