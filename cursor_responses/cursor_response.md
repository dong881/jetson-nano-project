# CUDA Library Error Fix for Jetson Nano Snake Game

## Problem Summary

The Docker container was failing to start the Snake Game application with the following error:

```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
```

This error occurred when PyTorch tried to load CUDA libraries at import time.

## Root Cause Analysis

The issue had two main causes:

1. **Missing CUDA Volume Mounts**: The `docker-compose.yml` file was not mounting the host's CUDA libraries into the container. The Jetson Nano has CUDA installed via JetPack on the host, but these libraries were not accessible inside the Docker container.

2. **Insufficient Diagnostics**: The `check_cuda.sh` script was detecting that CUDA libraries were missing but wasn't attempting to create necessary symlinks or providing detailed enough diagnostics to understand why.

## Changes Made

### 1. Updated docker-compose.yml

Added CUDA library volume mounts to make host CUDA libraries accessible inside the container:

```yaml
volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix:ro
  # Mount CUDA libraries from host Jetson Nano
  - /usr/local/cuda:/usr/local/cuda:ro
  - /usr/local/cuda-10.2:/usr/local/cuda-10.2:ro
  # Mount model and high score data
  - ./model:/app/model
  - ./high_score.txt:/app/high_score.txt
```

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
