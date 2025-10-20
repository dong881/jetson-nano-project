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

# Function to create missing CUDA library symlinks
create_cuda_symlinks() {
    echo ""
    echo "Checking for missing CUDA library symlinks..."
    
    # Create a writable directory for symlinks if needed
    local link_dir="/usr/local/lib"
    mkdir -p "$link_dir"
    
    # Check common CUDA library locations
    local cuda_dirs=(
        "/usr/local/cuda/lib64"
        "/usr/local/cuda-10.2/targets/aarch64-linux/lib"
        "/usr/lib/aarch64-linux-gnu"
        "/usr/local/cuda/lib"
    )
    
    local libs_to_link=(
        "libcurand.so.10.0:libcurand.so.10"
        "libcublas.so.10.0:libcublas.so.10"
        "libcublasLt.so.10.0:libcublasLt.so.10"
        "libcudnn.so.8:libcudnn.so.8"
        "libcufft.so.10.0:libcufft.so.10"
        "libcusparse.so.10.0:libcusparse.so.10"
        "libcusolver.so.10.0:libcusolver.so.10"
    )
    
    for cuda_dir in "${cuda_dirs[@]}"; do
        if [ -d "$cuda_dir" ]; then
            for lib_pair in "${libs_to_link[@]}"; do
                IFS=':' read -r source_lib target_lib <<< "$lib_pair"
                
                # Find the source library
                local source_path
                source_path=$(find "$cuda_dir" -name "$source_lib*" -type f -o -name "$source_lib" -type l 2>/dev/null | head -1)
                
                if [ -n "$source_path" ] && [ ! -e "$link_dir/$target_lib" ]; then
                    echo "Creating symlink: $link_dir/$target_lib -> $source_path"
                    ln -sf "$source_path" "$link_dir/$target_lib"
                fi
            done
        fi
    done
    
    # Add our link directory to LD_LIBRARY_PATH if not already there
    if [[ ":$LD_LIBRARY_PATH:" != *":$link_dir:"* ]]; then
        export LD_LIBRARY_PATH="$link_dir:$LD_LIBRARY_PATH"
        echo "Updated LD_LIBRARY_PATH to include $link_dir"
    fi
    
    echo "✓ CUDA symlinks check complete"
}

# Check if CUDA libraries are accessible
echo "Searching for CUDA libraries..."
if find_libcurand; then
    echo "✓ CUDA libraries found"
    # Create any missing symlinks that PyTorch might need
    create_cuda_symlinks
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
