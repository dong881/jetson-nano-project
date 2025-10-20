# Fix Summary: CUDA Library Issues

## Problems Fixed

### 1. Original Issue: libcurand.so.10 Missing
The application was failing with:
```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
jetson-nano-project-snake-game-1 exited with code 1
```

### 2. New Issue: libcudnn.so.8 File Too Short
After the initial fix, the application was failing with:
```
OSError: /usr/lib/aarch64-linux-gnu/libcudnn.so.8: file too short
jetson-nano-project-snake-game-1 exited with code 1
```

## Root Causes

### Issue 1: Missing CUDA Library Symlinks
PyTorch requires CUDA libraries with specific version symlinks (e.g., `libcurand.so.10`), but the host CUDA installation only provides libraries with more specific versions (e.g., `libcurand.so.10.0` or `libcurand.so.10.0.326`). The intermediate version symlinks that PyTorch expects are missing.

Additionally, since `/usr/local/cuda` is mounted as read-only from the host, the container cannot create these symlinks in the mounted directory.

### Issue 2: Corrupted CuDNN Library in Container
The base Docker image contains a broken or corrupted `libcudnn.so.8` file/symlink in `/usr/lib/aarch64-linux-gnu/`. When PyTorch tries to load this library, it fails with "file too short" error. This conflicts with the nvidia-container-runtime which tries to mount the proper CuDNN library from the host.

## Solutions Implemented

### 1. Dockerfile Changes
- **Updated** `ENV LD_LIBRARY_PATH` to include `/usr/local/lib` at the beginning:
  ```dockerfile
  ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/local/cuda/lib64:/usr/local/cuda/lib:/usr/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH
  ```
  This allows runtime-created symlinks in `/usr/local/lib` to be found first.

- **Added** removal of `libcudnn.so*` files from the container image:
  ```dockerfile
  RUN rm -f /usr/lib/aarch64-linux-gnu/libcudnn.so* \
      /usr/lib/libcudnn.so* \
      ...
  ```
  This prevents conflicts with the nvidia-container-runtime which mounts the correct CuDNN from the host.

### 2. check_cuda.sh Changes
- **Added** `create_cuda_symlinks()` function that:
  - Creates `/usr/local/lib` directory (writable location)
  - Searches for CUDA libraries in multiple locations including:
    - `/usr/local/cuda/lib64`
    - `/usr/local/cuda-10.2/targets/aarch64-linux/lib`
    - `/usr/lib/aarch64-linux-gnu`
    - `/usr/local/cuda/lib`
  - Creates missing version symlinks (e.g., `libcurand.so.10 -> libcurand.so.10.0.326`)
  - Handles multiple CUDA libraries: libcurand, libcublas, libcublasLt, libcudnn, libcufft, libcusparse, libcusolver
  - Updates LD_LIBRARY_PATH if needed
- **Integrated** symlink creation into the startup diagnostics

### 3. How It Works
1. Container build removes corrupted/conflicting NVIDIA libraries (including libcudnn.so*)
2. nvidia-container-runtime mounts proper NVIDIA libraries from host at runtime
3. Container starts and check_cuda.sh runs
4. Script finds CUDA libraries in multiple locations (including host-mounted `/usr/local/cuda` and runtime-mounted `/usr/lib/aarch64-linux-gnu`)
5. Script creates missing symlinks in writable `/usr/local/lib` (e.g., `libcurand.so.10 -> /usr/local/cuda/lib64/libcurand.so.10.0.326`, `libcudnn.so.8 -> /usr/lib/aarch64-linux-gnu/libcudnn.so.8.x.x.x`)
6. PyTorch can now find all required CUDA libraries via the symlinks
7. Application starts successfully

## How to Deploy

### On Your Jetson Nano:

1. **Pull the latest changes**:
   ```bash
   git pull origin copilot/fix-errors-in-docker-compose
   ```

2. **Build and run**:
   ```bash
   xhost +local:docker
   docker compose down
   docker compose build --no-cache
   docker compose up
   ```

## Expected Output

### On Successful Startup:
```
======================================== 
CUDA Library Configuration Check
========================================
LD_LIBRARY_PATH: /usr/local/lib:/usr/local/cuda/lib64:/usr/local/cuda/lib:/usr/lib/aarch64-linux-gnu:...

Searching for CUDA libraries...
Found libcurand in: /usr/local/cuda/lib64
lrwxrwxrwx 1 root root  17 ... libcurand.so -> libcurand.so.10.0
lrwxrwxrwx 1 root root  21 ... libcurand.so.10.0 -> libcurand.so.10.0.326
-rw-r--r-- 1 root root 61M ... libcurand.so.10.0.326
✓ CUDA libraries found

Checking for missing CUDA library symlinks...
Creating symlink: /usr/local/lib/libcurand.so.10 -> /usr/local/cuda/lib64/libcurand.so.10.0.326
Creating symlink: /usr/local/lib/libcublas.so.10 -> /usr/local/cuda/lib64/libcublas.so.10.0.167
✓ CUDA symlinks check complete

========================================
Starting Snake Game Application
========================================

pygame 2.1.2 (SDL 2.0.16, Python 3.6.9)
Hello from the pygame community. https://www.pygame.org/contribute.html
[Game window opens successfully]
```

### If CUDA Libraries Not Found:
The startup script will show a warning:
```
⚠ WARNING: libcurand not found in expected locations

This error typically means:
  1. JetPack is not installed on your Jetson Nano
  2. The /usr/local/cuda volume mount is not working
  3. nvidia-container-runtime is not properly configured

Please check:
  - JetPack 4.6.x is installed on the host
  - /usr/local/cuda exists on the host
  - nvidia-container-runtime is installed and working

Continuing anyway - the application may fail...
```

## Troubleshooting

### If the error still occurs:

1. **Check CUDA installation on your Jetson Nano**:
   ```bash
   ls /usr/local/cuda/lib64/libcurand.so*
   ```
   
   If this doesn't exist, you need to install JetPack 4.6.x

2. **Verify symlinks were created**:
   ```bash
   docker compose up
   # Look for "Creating symlink: /usr/local/lib/libcurand.so.10 -> ..." in output
   ```

3. **Check nvidia-container-runtime**:
   ```bash
   docker info | grep -i runtime
   # Should show: Runtimes: nvidia runc
   ```

4. **Check Docker logs**:
   ```bash
   docker compose logs
   ```

5. **See detailed troubleshooting**:
   Refer to `TROUBLESHOOTING.md` for comprehensive solutions

## Files Changed

### Modified:
- `Dockerfile` - Added `/usr/local/lib` to LD_LIBRARY_PATH and removed libcudnn.so* files
- `check_cuda.sh` - Added automatic CUDA symlink creation with expanded search locations
- `TROUBLESHOOTING.md` - Enhanced documentation with symlink and libcudnn fix details
- `FIX_SUMMARY.md` - This file (updated)

## Why This Fix Works

1. **Writable Location for Symlinks**: `/usr/local/lib` is writable, allowing symlink creation at runtime
2. **Automatic Detection**: Script finds actual library files regardless of their exact version
3. **Handles Multiple Libraries**: Creates symlinks for all CUDA libraries PyTorch might need
4. **Non-Intrusive**: Doesn't modify the read-only mounted CUDA directory from host
5. **LD_LIBRARY_PATH Priority**: `/usr/local/lib` is first in path, so symlinks are found before other locations

## Technical Details

### Why PyTorch Looks for libcurand.so.10
PyTorch is compiled against specific CUDA library versions. When it tries to load CUDA libraries, it uses the version it was compiled with (CUDA 10.x). The dynamic linker looks for:
1. `libcurand.so.10` (minor version specific)
2. `libcurand.so` (generic version)

If the host only has `libcurand.so.10.0` or `libcurand.so.10.0.326`, the linker can't find `libcurand.so.10` unless there's a symlink.

### Why Read-Only Mount
The `/usr/local/cuda` directory is mounted read-only (`ro`) from the host to:
- Prevent accidental modifications to the host's CUDA installation
- Ensure container doesn't interfere with host system
- Follow security best practices for container volumes

### Solution Pattern
This fix follows a common pattern for handling library version mismatches in containers:
1. Mount libraries from host (read-only for safety)
2. Create version-specific symlinks in a writable container location
3. Ensure writable location is in LD_LIBRARY_PATH before read-only locations

## Prevention for Future

- Always include intermediate version symlinks in library distributions
- Test container startup with actual library loading, not just file existence checks
- Document library version dependencies clearly
- Provide runtime diagnostics that explain issues and show what's being done to fix them

## Next Steps

After successful deployment:
1. Verify the game runs correctly in human mode
2. Test the training mode to ensure CUDA acceleration works
3. Check PyTorch CUDA availability:
   ```python
   import torch
   print(torch.cuda.is_available())  # Should be True
   print(torch.cuda.get_device_name(0))  # Should show GPU name
   ```

If issues persist, please:
1. Run `docker compose logs` and share the full startup output
2. Check if symlinks were created: `docker compose exec snake-game ls -la /usr/local/lib/`
3. Open a GitHub issue with the diagnostic information
