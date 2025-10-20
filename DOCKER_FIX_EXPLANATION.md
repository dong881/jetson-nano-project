# Docker Compose libcudnn.so.8 Fix - Detailed Explanation

## Issue Description

When running `sudo docker compose up`, the container was failing with:

```
OSError: /usr/lib/aarch64-linux-gnu/libcudnn.so.8: file too short
jetson-nano-project-snake-game-1 exited with code 1
```

This error occurred after PyTorch had been successfully initializing CUDA libraries, indicating that the CUDA setup was working, but specifically the CuDNN library was causing problems.

## What is libcudnn.so.8?

**CuDNN (CUDA Deep Neural Network library)** is NVIDIA's GPU-accelerated library of primitives for deep neural networks. PyTorch uses CuDNN to accelerate:
- Convolution operations
- Pooling operations
- Normalization layers
- Activation functions
- RNN/LSTM operations

Version 8 is the major version of CuDNN that's compatible with CUDA 10.2 on Jetson Nano.

## Root Cause Analysis

The error "file too short" is a specific error that occurs when:

1. **The file exists but is corrupted or empty** - The base Docker image (`nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3`) contains a CuDNN library file or symlink at `/usr/lib/aarch64-linux-gnu/libcudnn.so.8`

2. **The file is a broken symlink** - It might be pointing to a non-existent file or a file that was removed during the Docker image build process

3. **Conflict with nvidia-container-runtime** - The nvidia-container-runtime (specified by `runtime: nvidia` in docker-compose.yml) tries to mount the correct CuDNN library from the Jetson Nano host system into the container, but encounters a conflict because a file with the same name already exists in the container

## The Fix

### Changes Made to Dockerfile

We added removal of `libcudnn.so*` files from the container image:

```dockerfile
RUN rm -f /usr/lib/aarch64-linux-gnu/libcudnn.so* \
    /usr/lib/libcudnn.so* \
    ...
```

This is added at lines 56 and 64 in the Dockerfile.

**Why this works:**
- Removes the corrupted/broken CuDNN files from the container
- Allows nvidia-container-runtime to properly mount CuDNN from the host without conflicts
- The host's CuDNN (from JetPack installation) becomes the only CuDNN available in the container

### Changes Made to check_cuda.sh

We expanded the search locations for CUDA libraries to include:

```bash
local cuda_dirs=(
    "/usr/local/cuda/lib64"
    "/usr/local/cuda-10.2/targets/aarch64-linux/lib"
    "/usr/lib/aarch64-linux-gnu"      # Added
    "/usr/local/cuda/lib"              # Added
)
```

**Why this is important:**
- After nvidia-container-runtime mounts CuDNN, it might be in `/usr/lib/aarch64-linux-gnu/`
- The script can now find CuDNN and create symlinks if needed
- Provides better diagnostics about library locations

## How the Complete Solution Works

### Build Time (Dockerfile execution)
1. Base image is pulled with PyTorch 1.10 pre-installed
2. Container is built with system dependencies
3. **Corrupted/conflicting CuDNN files are removed** from `/usr/lib/aarch64-linux-gnu/` and `/usr/lib/`
4. LD_LIBRARY_PATH is configured to look in `/usr/local/lib` first

### Runtime (Container startup)
1. Docker Compose starts the container with `runtime: nvidia`
2. **nvidia-container-runtime mounts NVIDIA libraries from the host**, including:
   - CuDNN from JetPack installation (typically version 8.x.x)
   - Other NVIDIA libraries (libcuda, libnvidia-*, etc.)
3. **check_cuda.sh runs** as the container entrypoint:
   - Searches for CUDA libraries in multiple locations
   - Creates symlinks in `/usr/local/lib` for version compatibility
   - For example: `libcudnn.so.8 -> /usr/lib/aarch64-linux-gnu/libcudnn.so.8.x.x.x`
4. **PyTorch initializes** and successfully loads CuDNN:
   - Looks for `libcudnn.so.8`
   - Finds it either directly (from nvidia-container-runtime mount) or via symlink
   - Successfully loads the library

### Application Execution
1. `main.py` imports PyTorch
2. PyTorch loads CUDA and CuDNN libraries successfully
3. Application starts without errors

## Why We Don't Install CuDNN in the Container

You might wonder: "Why not just install the correct version of CuDNN in the container?"

**Reasons:**
1. **Version Matching**: The CuDNN version must exactly match the CUDA version and PyTorch expectations. The host JetPack installation already has the correct version.

2. **ARM Architecture**: Finding and installing the correct ARM64 (aarch64) version of CuDNN for CUDA 10.2 is difficult, as NVIDIA primarily distributes x86_64 versions.

3. **Container Size**: CuDNN libraries are large (~600MB). Using the host's libraries keeps the container smaller.

4. **Consistency**: Using the same libraries as the host ensures consistent behavior between Docker and non-Docker environments.

5. **nvidia-container-runtime Design**: This is exactly what nvidia-container-runtime is designed for - sharing GPU libraries from the host.

## Verification Steps

After applying this fix, you should see:

1. **During container startup**, check_cuda.sh output shows:
   ```
   Checking for missing CUDA library symlinks...
   Creating symlink: /usr/local/lib/libcurand.so.10 -> /usr/local/cuda/lib64/libcurand.so.10.0.326
   Creating symlink: /usr/local/lib/libcublas.so.10 -> /usr/local/cuda-10.2/targets/aarch64-linux/lib/libcublas.so.10.0
   ...
   ✓ CUDA symlinks check complete
   ```

2. **Application starts successfully**:
   ```
   Starting Snake Game Application
   ========================================
   
   pygame 2.1.2 (SDL 2.0.16, Python 3.6.9)
   Hello from the pygame community. https://www.pygame.org/contribute.html
   [Game window opens]
   ```

3. **No "file too short" errors**

## Testing CUDA and CuDNN

To verify CUDA and CuDNN are working inside the container:

```bash
# Run the container interactively
docker compose run --rm snake-game /bin/bash

# Inside the container, test PyTorch CUDA
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CuDNN version: {torch.backends.cudnn.version()}')"

# Expected output:
# CUDA available: True
# CuDNN version: 8xxx (e.g., 8204 for CuDNN 8.2.4)
```

## Troubleshooting

### If the error still occurs:

1. **Check JetPack installation on the host**:
   ```bash
   # On Jetson Nano (outside container)
   find /usr -name "libcudnn.so*" 2>/dev/null
   ```
   
   Should show files like:
   ```
   /usr/lib/aarch64-linux-gnu/libcudnn.so.8.2.4
   /usr/lib/aarch64-linux-gnu/libcudnn.so.8
   ```

2. **Verify nvidia-container-runtime**:
   ```bash
   docker info | grep -i runtime
   # Should show: Runtimes: nvidia runc
   ```

3. **Check Docker logs**:
   ```bash
   docker compose logs snake-game
   ```

4. **Rebuild without cache**:
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up
   ```

### If CuDNN is not found on the host:

You need to install JetPack 4.6.x on your Jetson Nano, which includes:
- CUDA 10.2
- CuDNN 8.x
- TensorRT
- Other NVIDIA libraries

Download from: https://developer.nvidia.com/embedded/jetpack

## Related Documentation

- **TROUBLESHOOTING.md**: Comprehensive troubleshooting guide for all common issues
- **FIX_SUMMARY.md**: Summary of all fixes applied to the project
- **DEPENDENCIES.md**: Package version compatibility information
- **QUICKSTART.md**: Quick start guide for running the project

## Technical Details

### Error Message Breakdown

```
OSError: /usr/lib/aarch64-linux-gnu/libcudnn.so.8: file too short
```

- **OSError**: Operating System error (file/library loading error)
- **Path**: `/usr/lib/aarch64-linux-gnu/` - Standard location for ARM64 libraries
- **Library**: `libcudnn.so.8` - CuDNN version 8 shared library
- **"file too short"**: The file exists but has zero or very few bytes (corrupted/broken)

### Why "file too short" specifically?

When the dynamic linker tries to load a shared library:
1. It opens the file
2. Reads the ELF header (first few bytes)
3. If the file is too small to contain a valid ELF header, it returns "file too short"

This usually means:
- Empty file (0 bytes)
- Broken symlink pointing to a non-existent file
- Corrupted file that was partially deleted

### Library Loading Order

With our fix, the library loading order is:

1. **LD_LIBRARY_PATH priority**: `/usr/local/lib` (for symlinks) comes first
2. **Standard paths**: `/usr/local/cuda/lib64`, `/usr/lib/aarch64-linux-gnu`, etc.
3. **Fallback**: System default library paths

This ensures symlinks are found first, then actual libraries from nvidia-container-runtime or CUDA mount.

## Benefits of This Fix

1. ✅ **Solves the immediate problem**: Container starts successfully
2. ✅ **Robust**: Works with different CuDNN versions on different Jetson Nano setups
3. ✅ **Minimal changes**: Only adds library removal and search locations
4. ✅ **Well documented**: Clear explanation of what was changed and why
5. ✅ **Diagnostic friendly**: check_cuda.sh provides helpful output for debugging
6. ✅ **Future-proof**: Will work with JetPack updates as long as the same patterns are followed

## Summary

The fix is simple but effective:
- **Remove conflicting CuDNN files from container** → Let nvidia-container-runtime provide the correct ones
- **Expand search locations in check_cuda.sh** → Find libraries wherever they are mounted
- **Create symlinks as needed** → Ensure version compatibility

This allows PyTorch to successfully load CuDNN and run CUDA-accelerated deep learning operations on the Jetson Nano.
