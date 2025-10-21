# CUDA Library Fix for Snake Game Docker Container

## Problem Analysis

The Docker container was failing with the error:
```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
=======
# CUDA Library Error Fix for Jetson Nano Snake Game

## Problem Summary

The Docker container was failing to start the Snake Game application with the following error:


```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
```

This error occurred when PyTorch tried to load CUDA libraries at import time.

## Root Cause Analysis

This error occurs because PyTorch cannot find the required CUDA libraries (`libcurand.so.10`, `libcufft.so.10`, `libcublas.so.10`, etc.) that are needed for GPU acceleration.

## Root Cause

The issue was in the `docker-compose.yml` configuration. The container was missing the crucial volume mount for CUDA libraries from the host system. While the Dockerfile and `check_cuda.sh` script were properly configured to handle CUDA libraries, the Docker Compose file wasn't mounting the host's CUDA installation into the container.

## Solution Applied

I've fixed the `docker-compose.yml` file by adding the missing CUDA volume mount:

```yaml
volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix:ro
  # Mount CUDA libraries from host (required for PyTorch CUDA support)
  - /usr/local/cuda:/usr/local/cuda:ro
=======
The issue had two main causes:

1. **Missing CUDA Volume Mounts**: The `docker-compose.yml` file was not mounting the host's CUDA libraries into the container. The Jetson Nano has CUDA installed via JetPack on the host, but these libraries were not accessible inside the Docker container.

2. **Insufficient Diagnostics**: The `check_cuda.sh` script was detecting that CUDA libraries were missing but wasn't attempting to create necessary symlinks or providing detailed enough diagnostics to understand why.

## Changes Made

### 1. Updated docker-compose.yml

Added CUDA library volume mounts to make host CUDA libraries accessible inside the container:

```yaml
volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix:ro
# Mount model and high score data
  - ./model:/app/model
  - ./high_score.txt:/app/high_score.txt
  
  
  
```

## How This Fixes the Problem

1. **CUDA Library Access**: The `/usr/local/cuda:/usr/local/cuda:ro` volume mount makes the host's CUDA installation (from JetPack) available inside the container
2. **Library Discovery**: The `check_cuda.sh` script can now find the CUDA libraries in `/usr/local/cuda/lib64/` and create necessary symlinks
3. **PyTorch Compatibility**: PyTorch can now load the required CUDA libraries (`libcurand.so.10`, `libcufft.so.10`, etc.) for GPU acceleration

## Instructions to Apply the Fix

Run these commands on your Jetson Nano:

```bash
# Stop any running containers
sudo docker compose down

# Rebuild the container with the updated configuration
sudo docker compose build --no-cache

# Start the container with the fix
sudo docker compose up
```

## Expected Results

After applying this fix, you should see:

1. **CUDA Library Detection**: The startup script will show:
   ```
   ✓ CUDA libraries found
   Creating symlink: /usr/local/lib/libcurand.so.10 -> /usr/local/cuda/lib64/libcurand.so.10.0.326
   Creating symlink: /usr/local/lib/libcufft.so.10 -> /usr/local/cuda/lib64/libcufft.so.10.0.326
   ```

2. **Successful Application Start**: The Snake Game should start without the `libcurand.so.10` error:
   ```
   Starting Snake Game Application
   ========================================
   pygame 2.1.2 (SDL 2.0.16, Python 3.6.9)
   Hello from the pygame community. https://www.pygame.org/contribute.html
   [Game window opens successfully]
   ```

## Verification

To verify CUDA is working properly, you can test inside the container:

```bash
# Run container interactively
sudo docker compose run --rm snake-game /bin/bash

# Inside container, test PyTorch CUDA
python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

Expected output: `CUDA available: True`

## Technical Details

- **Host CUDA Location**: `/usr/local/cuda` (standard JetPack installation path)
- **Container Mount**: Read-only mount to prevent conflicts
- **Library Path**: The `LD_LIBRARY_PATH` in the Dockerfile includes `/usr/local/cuda/lib64` for library discovery
- **Symlink Creation**: The `check_cuda.sh` script creates version compatibility symlinks in `/usr/local/lib`

This fix ensures that the Docker container has access to all necessary CUDA libraries while maintaining compatibility with the Jetson Nano's JetPack installation.
=======
**Why this works**: The nvidia-container-runtime needs access to the host's CUDA libraries. By mounting `/usr/local/cuda` and `/usr/local/cuda-10.2` from the host, PyTorch can find the required CUDA libraries (`libcurand.so.10`, `libcublas.so.10`, etc.).

### 2. Enhanced check_cuda.sh Script

Updated the CUDA check script to:

- **Better diagnostics**: Now checks if CUDA directories are actually mounted and lists their contents
- **Always create symlinks**: Previously only created symlinks if libraries were found; now always attempts to create them, which may fix missing libraries
- **More detailed error messages**: Shows exactly what's missing and where to look

Key changes:
- Added check for CUDA directory existence
- Added directory listing to help diagnose mount issues
- Moved symlink creation outside of conditional - now runs regardless of initial library detection

## How to Test

1. **Verify JetPack is installed on your Jetson Nano host**:
   ```bash
   ls -la /usr/local/cuda
   ```
   You should see CUDA installation directories.

2. **Stop any running containers**:
   ```bash
   sudo docker compose down
   ```

3. **Rebuild and start the container**:
   ```bash
   sudo docker compose up --build
   ```

4. **Expected output**: 
   - The check script should now find CUDA libraries in the mounted directories
   - It will create necessary symlinks for PyTorch compatibility
   - The application should start without the `libcurand.so.10` error

## Additional Notes

### Prerequisites
- **JetPack 4.6.x** must be installed on the Jetson Nano host
- **nvidia-container-runtime** must be properly configured
- **Docker runtime** must be set to `nvidia` (already configured in docker-compose.yml)

### What if it still fails?

If you still see CUDA library errors after these changes:

1. **Verify JetPack installation**:
   ```bash
   dpkg -l | grep cuda
   ```

2. **Check nvidia-container-runtime**:
   ```bash
   sudo docker run --rm --runtime=nvidia nvcr.io/nvidia/l4t-base:r32.7.1 nvidia-smi
   ```

3. **Check the enhanced diagnostics** in the container output - it will now show:
   - Whether CUDA directories are mounted
   - Contents of CUDA directories
   - Which specific libraries are missing
   - Which symlinks were created

4. **Manual library verification** inside the container:
   ```bash
   sudo docker compose run --rm snake-game /bin/bash
   ls -la /usr/local/cuda/lib64/
   ls -la /usr/local/cuda-10.2/targets/aarch64-linux/lib/
   ```

### Why PyTorch needs these libraries

PyTorch 1.10 (included in the base image) requires specific CUDA 10.2 libraries:
- `libcudart.so.10.2` - CUDA Runtime
- `libcurand.so.10` - CUDA Random Number Generation
- `libcublas.so.10` - CUDA Basic Linear Algebra
- `libcufft.so.10` - CUDA Fast Fourier Transform
- `libcudnn.so.8` - CUDA Deep Neural Network library

The script now creates symlinks for version compatibility between what PyTorch expects and what's available on the Jetson Nano.

## Summary

The fix ensures that CUDA libraries from the Jetson Nano host are properly mounted into the Docker container, allowing PyTorch to access GPU acceleration. The enhanced diagnostic script helps identify and fix any remaining library compatibility issues automatically.
