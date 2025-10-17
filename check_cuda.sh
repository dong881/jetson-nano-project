#!/bin/bash
# Check CUDA libraries are available before starting the application

echo "========================================"
echo "CUDA Library Configuration Check"
echo "========================================"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
echo ""

# Function to check for libcurand in various locations
find_libcurand() {
    local locations=(
        "/usr/local/cuda/lib64"
        "/usr/local/cuda/lib"
        "/usr/lib/aarch64-linux-gnu"
        "/usr/local/cuda-10.2/lib64"
    )
    
    for loc in "${locations[@]}"; do
        if [ -d "$loc" ]; then
            if ls "$loc"/libcurand.so* &> /dev/null; then
                echo "Found libcurand in: $loc"
                ls -lh "$loc"/libcurand.so* | head -3
                return 0
            fi
        fi
    done
    return 1
}

# Check if CUDA libraries are accessible
echo "Searching for CUDA libraries..."
if find_libcurand; then
    echo "✓ CUDA libraries found"
else
    echo ""
    echo "⚠ WARNING: libcurand not found in expected locations"
    echo ""
    echo "This error typically means:"
    echo "  1. JetPack is not installed on your Jetson Nano"
    echo "  2. The /usr/local/cuda volume mount is not working"
    echo "  3. nvidia-container-runtime is not properly configured"
    echo ""
    echo "Please check:"
    echo "  - JetPack 4.6.x is installed on the host"
    echo "  - /usr/local/cuda exists on the host"
    echo "  - nvidia-container-runtime is installed and working"
    echo ""
    echo "Continuing anyway - the application may fail..."
fi

echo ""
echo "========================================"
echo "Starting Snake Game Application"
echo "========================================"
echo ""

# Run the main application
exec python3 main.py
