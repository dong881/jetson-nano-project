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
# Note: PyTorch 1.10 is already included in the base image for Jetson Nano with CUDA 10.2 support
# DO NOT reinstall torch as it will break CUDA compatibility
# Upgrade pip to latest compatible version for Python 3.6
RUN pip3 install --upgrade "pip<21.0"

# Install dependencies from requirements.txt
# Using --no-cache-dir to reduce image size and --prefer-binary to avoid compilation issues
RUN pip3 install --no-cache-dir --prefer-binary -r requirements.txt

# Copy project files
COPY . .

# Make the CUDA check script executable
RUN chmod +x check_cuda.sh

# Create model directory
RUN mkdir -p model

# Remove conflicting NVIDIA libraries to fix runtime mount errors
# This is a workaround for the "file exists" error when using nvidia runtime on Jetson
# The nvidia-container-runtime will mount these libraries from the host
# Note: We keep CUDA runtime libraries (libcudart, libcurand, libcublas, etc.) that PyTorch needs
RUN rm -f /usr/lib/aarch64-linux-gnu/libcuda.so* \
    /usr/lib/aarch64-linux-gnu/libnvidia-*.so* \
    /usr/lib/aarch64-linux-gnu/libcudnn.so* \
    /usr/lib/aarch64-linux-gnu/libvisionworks*.so* \
    /usr/lib/aarch64-linux-gnu/libnvcaffe_parser*.so* \
    /usr/lib/aarch64-linux-gnu/libnvinfer*.so* \
    /usr/lib/aarch64-linux-gnu/libnvonnxparser*.so* \
    /usr/lib/aarch64-linux-gnu/libnvparsers*.so* \
    /usr/lib/libcuda.so* \
    /usr/lib/libnvidia-*.so* \
    /usr/lib/libcudnn.so* \
    /usr/lib/libvisionworks*.so* \
    /usr/lib/libnvcaffe_parser*.so* \
    /usr/lib/libnvinfer*.so* \
    /usr/lib/libnvonnxparser*.so* \
    /usr/lib/libnvparsers*.so* \
    2>/dev/null || true

# Also remove any CUDA stub libraries that might conflict with host CUDA
# The real CUDA libraries will be provided by the nvidia-container-runtime
RUN rm -rf /usr/local/cuda-*/lib*/stubs \
    2>/dev/null || true

# Set CUDA library path to ensure PyTorch can find CUDA libraries
# This is critical for PyTorch to work with CUDA on Jetson Nano
# The base image may already have LD_LIBRARY_PATH set, so we prepend our path
# /usr/local/lib is included for runtime-created symlinks
ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/local/cuda/lib64:/usr/local/cuda/lib:/usr/lib/aarch64-linux-gnu:/usr/local/cuda-10.2/targets/aarch64-linux/lib:$LD_LIBRARY_PATH

# Create initial CUDA library symlinks in the image
# This ensures that even if the host mount fails, we have some CUDA libraries available
RUN mkdir -p /usr/local/lib && \
    find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "libcufft.so*" -exec ln -sf {} /usr/local/lib/libcufft.so.10 \; 2>/dev/null || true && \
    find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "libcurand.so*" -exec ln -sf {} /usr/local/lib/libcurand.so.10 \; 2>/dev/null || true && \
    find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "libcublas.so*" -exec ln -sf {} /usr/local/lib/libcublas.so.10 \; 2>/dev/null || true

# Set display environment variable (for X11 forwarding)
ENV DISPLAY=:0

# Run the CUDA check script which then starts the main application
CMD ["./check_cuda.sh"]
