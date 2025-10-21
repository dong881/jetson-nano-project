#!/bin/bash
# Check CUDA libraries are available before starting the application

echo "========================================"
echo "CUDA Library Configuration Check"
echo "========================================"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
echo ""

# Function to check for CUDA libraries in various locations
find_cuda_libs() {
    local locations=(
        "/usr/local/cuda/lib64"
        "/usr/local/cuda/lib"
        "/usr/lib/aarch64-linux-gnu"
        "/usr/local/cuda-10.2/lib64"
        "/usr/local/cuda-10.2/targets/aarch64-linux/lib"
    )
    
    local found_any=false
    local required_libs=("libcurand" "libcufft" "libcublas" "libcudart")
    
    for loc in "${locations[@]}"; do
        if [ -d "$loc" ]; then
            local found_in_loc=false
            for lib in "${required_libs[@]}"; do
                if ls "$loc"/${lib}.so* &> /dev/null; then
                    if [ "$found_in_loc" = false ]; then
                        echo "Found CUDA libraries in: $loc"
                        found_in_loc=true
                        found_any=true
                    fi
                    ls -lh "$loc"/${lib}.so* | head -1
                fi
            done
        fi
    done
    
    if [ "$found_any" = true ]; then
        return 0
    else
        return 1
    fi
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
        "libcurand.so.10:libcurand.so.10"
        "libcublas.so.10:libcublas.so.10"
        "libcublasLt.so.10:libcublasLt.so.10"
        "libcudnn.so.8:libcudnn.so.8"
        "libcufft.so.10:libcufft.so.10"
        "libcusparse.so.10:libcusparse.so.10"
        "libcusolver.so.10:libcusolver.so.10"
        "libcudart.so.10.0:libcudart.so.10.2"
    )
    
    for cuda_dir in "${cuda_dirs[@]}"; do
        if [ -d "$cuda_dir" ]; then
            for lib_pair in "${libs_to_link[@]}"; do
                IFS=':' read -r source_lib target_lib <<< "$lib_pair"
                
                # Find the source library with flexible version matching
                local source_path
                # First try to find the exact library name
                source_path=$(find "$cuda_dir" -name "$source_lib" -type f -o -name "$source_lib" -type l 2>/dev/null | head -1)
                
                # If not found, try to find any version of the library
                if [ -z "$source_path" ]; then
                    local base_lib_name=$(echo "$source_lib" | sed 's/\.so\..*$/\.so/')
                    source_path=$(find "$cuda_dir" -name "${base_lib_name}.*" -type f 2>/dev/null | head -1)
                fi
                
                # If still not found, try to find any file starting with the library name
                if [ -z "$source_path" ]; then
                    source_path=$(find "$cuda_dir" -name "${source_lib}*" -type f 2>/dev/null | head -1)
                fi

                # For cuDNN, ensure we only link to v8 artifacts
                if [ "$source_lib" = "libcudnn.so.8" ] && [ -n "$source_path" ]; then
                    if [[ "$source_path" != *"libcudnn.so.8"* ]]; then
                        echo "Warning: Found $source_path for libcudnn.so.8 but it is not v8; skipping"
                        source_path=""
                    fi
                fi

                if [ -n "$source_path" ] && [ ! -e "$link_dir/$target_lib" ]; then
                    echo "Creating symlink: $link_dir/$target_lib -> $source_path"
                    ln -sf "$source_path" "$link_dir/$target_lib"
                elif [ -z "$source_path" ]; then
                    echo "Warning: Could not find $source_lib in $cuda_dir"
                fi
            done
        fi
    done
    
    # Add our link directory to LD_LIBRARY_PATH if not already there
    if [[ ":$LD_LIBRARY_PATH:" != *":$link_dir:"* ]]; then
        export LD_LIBRARY_PATH="$link_dir:$LD_LIBRARY_PATH"
        echo "Updated LD_LIBRARY_PATH to include $link_dir"
    fi
    
    # Fallback: Create symlinks from any available CUDA library versions
    echo ""
    echo "Creating fallback symlinks for missing libraries..."
    local fallback_libs=(
        "libcufft.so.10"
        "libcurand.so.10" 
        "libcublas.so.10"
        "libcusparse.so.10"
        "libcusolver.so.10"
        "libcudart.so.10.2"
    )
    
    for target_lib in "${fallback_libs[@]}"; do
        if [ ! -e "$link_dir/$target_lib" ]; then
            local found_lib=""
            if [[ "$target_lib" == "libcudart.so.10.2" ]]; then
                # Prefer exact CUDA 10.2 runtime if present
                found_lib=$(find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "libcudart.so.10.2*" -type f 2>/dev/null | head -1)
            fi

            if [ -z "$found_lib" ]; then
                # Generic fallback for other libraries (keeps the same major version)
                local base_name=$(echo "$target_lib" | sed 's/\.so\..*$/\.so/')
                found_lib=$(find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "${base_name}.*" -type f 2>/dev/null | head -1)
            fi
            
            if [ -n "$found_lib" ]; then
                echo "Creating fallback symlink: $link_dir/$target_lib -> $found_lib"
                ln -sf "$found_lib" "$link_dir/$target_lib"
            fi
        fi
    done
    
    echo "✓ CUDA symlinks check complete"

    # Ensure cuDNN 8 is present (do not alias to v7)
    echo ""
    echo "Checking for cuDNN 8..."
    local cudnn8_found=false
    if [ -e "$link_dir/libcudnn.so.8" ]; then
        cudnn8_found=true
    else
        # Try to locate a real cuDNN 8 on the system and link it
        local cudnn8_path
        cudnn8_path=$(find /usr/lib/aarch64-linux-gnu /usr/local/cuda* -maxdepth 3 -name "libcudnn.so.8*" -type f 2>/dev/null | head -1)
        if [ -n "$cudnn8_path" ]; then
            echo "Creating symlink: $link_dir/libcudnn.so.8 -> $cudnn8_path"
            ln -sf "$cudnn8_path" "$link_dir/libcudnn.so.8"
            cudnn8_found=true
        fi
    fi

    if [ "$cudnn8_found" = true ]; then
        echo "✓ libcudnn.so.8 is available"
    else
        echo "✗ libcudnn.so.8 not found. PyTorch 1.10 requires cuDNN 8."
        echo "  Upgrade JetPack to 4.6.x (L4T r32.7.x) or install libcudnn8 on the host."
    fi

    # Special handling for PyTorch 1.10 CUDA 10.2 compatibility
    # PyTorch 1.10 expects libcudart.so.10.2 but Jetson Nano has libcudart.so.10.0
    echo ""
    echo "Creating PyTorch 1.10 CUDA compatibility symlinks..."
    local pytorch_cuda_libs=(
        "libcudart.so.10.0:libcudart.so.10.2"
        "libcublas.so.10.0:libcublas.so.10.2"
        "libcufft.so.10.0:libcufft.so.10.2"
        "libcurand.so.10.0:libcurand.so.10.2"
        "libcusparse.so.10.0:libcusparse.so.10.2"
        "libcusolver.so.10.0:libcusolver.so.10.2"
    )
    
    for lib_pair in "${pytorch_cuda_libs[@]}"; do
        IFS=':' read -r source_lib target_lib <<< "$lib_pair"
        
        # Find the source library - try exact match first, then flexible matching
        local source_path
        source_path=$(find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "$source_lib" -type f 2>/dev/null | head -1)
        
        # If not found, try to find any version of the library
        if [ -z "$source_path" ]; then
            local base_lib_name=$(echo "$source_lib" | sed 's/\.so\..*$/.so/')
            source_path=$(find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "${base_lib_name}.*" -type f 2>/dev/null | head -1)
        fi
        
        # If still not found, try to find any file starting with the library name
        if [ -z "$source_path" ]; then
            source_path=$(find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "${source_lib}*" -type f 2>/dev/null | head -1)
        fi
        
        if [ -n "$source_path" ] && [ ! -e "$link_dir/$target_lib" ]; then
            echo "Creating PyTorch compatibility symlink: $link_dir/$target_lib -> $source_path"
            ln -sf "$source_path" "$link_dir/$target_lib"
        elif [ -z "$source_path" ]; then
            echo "Warning: Could not find $source_lib for PyTorch compatibility"
        fi
    done
    
    # Special handling for cuDNN version mismatch
    # PyTorch 1.10 expects libcudnn.so.8 but Jetson Nano has libcudnn.so.7.6.3
    echo ""
    echo "Handling cuDNN version compatibility..."
    
    # Check if we have cuDNN 8.x available
    local cudnn8_path
    cudnn8_path=$(find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "libcudnn.so.8*" -type f 2>/dev/null | head -1)
    
    if [ -n "$cudnn8_path" ]; then
        echo "Found cuDNN 8.x: $cudnn8_path"
        if [ ! -e "$link_dir/libcudnn.so.8" ]; then
            echo "Creating cuDNN 8 symlink: $link_dir/libcudnn.so.8 -> $cudnn8_path"
            ln -sf "$cudnn8_path" "$link_dir/libcudnn.so.8"
        fi
    else
        echo "Warning: cuDNN 8.x not found, PyTorch may fail with CUDA"
        echo "Available cuDNN versions:"
        find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "libcudnn.so*" -type f 2>/dev/null | head -5
        
        # Try to create a compatibility symlink from cuDNN 7.x to 8.x
        # This is a workaround that may or may not work depending on API compatibility
        local cudnn7_path
        cudnn7_path=$(find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "libcudnn.so.7*" -type f 2>/dev/null | head -1)
        
        if [ -n "$cudnn7_path" ]; then
            echo "Attempting cuDNN 7.x to 8.x compatibility symlink (may not work):"
            echo "Creating symlink: $link_dir/libcudnn.so.8 -> $cudnn7_path"
            ln -sf "$cudnn7_path" "$link_dir/libcudnn.so.8"
            echo "Note: This is a compatibility workaround and may cause runtime errors"
        else
            echo "Error: No cuDNN libraries found at all"
        fi
    fi
    
    # Verify critical libraries are accessible
    echo ""
    echo "Verifying critical CUDA libraries..."
    local critical_libs=("libcufft.so.10" "libcurand.so.10" "libcublas.so.10" "libcudart.so.10.2")
    local all_found=true
    
    for lib in "${critical_libs[@]}"; do
        if [ -e "$link_dir/$lib" ] || ldconfig -p | grep -q "$lib"; then
            echo "✓ $lib is accessible"
        else
            echo "✗ $lib is missing"
            all_found=false
        fi
    done
    
    # Check cuDNN specifically
    if [ -e "$link_dir/libcudnn.so.8" ]; then
        echo "✓ libcudnn.so.8 is accessible"
    else
        echo "✗ libcudnn.so.8 is missing"
        all_found=false
    fi
    
    if [ "$all_found" = false ]; then
        echo ""
        echo "⚠ WARNING: Some critical CUDA libraries are missing"
        echo "This may cause PyTorch to fail with CUDA errors"
        echo ""
        echo "The application will attempt to fall back to CPU mode if CUDA fails"
    fi
}

# Check if CUDA libraries are accessible
echo "Searching for CUDA libraries..."
if find_cuda_libs; then
    echo "✓ CUDA libraries found"
    # Create any missing symlinks that PyTorch might need
    create_cuda_symlinks
else
    echo ""
    echo "⚠ WARNING: CUDA libraries not found in expected locations"
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
