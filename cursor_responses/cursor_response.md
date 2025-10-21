# CUDA Runtime Library Error Fix

## Problem
The Docker container was failing with the error:
```
OSError: libcudart.so.10.2: cannot open shared object file: No such file or directory
```

This occurred because:
- PyTorch 1.10 (in the base Docker image) expects CUDA 10.2 libraries
- The Jetson Nano host system has CUDA 10.0 libraries
- The container was creating symlinks for version 10.0 libraries, but PyTorch was looking for version 10.2

## Solution
I implemented a comprehensive fix to create PyTorch 1.10 compatibility symlinks:

### 1. Updated `check_cuda.sh`
- Added PyTorch 1.10 CUDA compatibility symlink creation
- Enhanced library finding logic with flexible matching (exact match → version match → prefix match)
- Added creation of `libcudart.so.10.2` and other CUDA 10.2 symlinks pointing to available CUDA 10.0 libraries
- Updated verification to check for `libcudart.so.10.2`

### 2. Updated `Dockerfile`
- Added creation of `libcudart.so.10.2` symlink during build process
- This ensures compatibility even if host mount fails

### 3. Key Changes Made

#### In `check_cuda.sh`:
```bash
# Added PyTorch 1.10 compatibility symlinks
pytorch_cuda_libs=(
    "libcudart.so.10.0:libcudart.so.10.2"
    "libcublas.so.10.0:libcublas.so.10.2"
    "libcufft.so.10.0:libcufft.so.10.2"
    "libcurand.so.10.0:libcurand.so.10.2"
    "libcusparse.so.10.0:libcusparse.so.10.2"
    "libcusolver.so.10.0:libcusolver.so.10.2"
)
```

#### In `Dockerfile`:
```dockerfile
# Added libcudart.so.10.2 symlink creation
find /usr/local/cuda* /usr/lib/aarch64-linux-gnu -name "libcudart.so*" -exec ln -sf {} /usr/local/lib/libcudart.so.10.2 \; 2>/dev/null || true
```

## Testing
- Created and tested a mock environment that simulates the Jetson Nano CUDA library structure
- Verified that the symlink creation logic correctly creates `libcudart.so.10.2` pointing to `libcudart.so.10.0.326`
- Confirmed all PyTorch 1.10 compatibility symlinks are created successfully

## Expected Result
The Docker container should now start successfully without the `libcudart.so.10.2` error, as PyTorch will find the required CUDA 10.2 libraries through the compatibility symlinks.

## Files Modified
1. `check_cuda.sh` - Enhanced CUDA library detection and symlink creation
2. `Dockerfile` - Added PyTorch compatibility symlink creation during build

The fix maintains backward compatibility while ensuring PyTorch 1.10 can find the CUDA libraries it expects.

---

## libcudnn.so.8 ImportError Fix (Jetson Docker)

### Problem
Container failed at import time with:

```
ImportError: /usr/local/lib/libcudnn.so.8: version `libcudnn.so.8' not found
```

This occurred because a runtime symlink incorrectly pointed `libcudnn.so.8` to a cuDNN 7.x file.

### Changes Made
- Hardened `check_cuda.sh` to strictly link `libcudnn.so.8` only to real cuDNN 8 artifacts and reject v7 paths.
- Added a post-check to ensure `libcudnn.so.8` exists; if missing, it searches known locations and links it, otherwise prints a clear remediation message (upgrade/install cuDNN 8 on host).
- Removed the host `/usr/local/cuda` bind from `docker-compose.yml` to avoid mismatched host CUDA libraries overshadowing the container/base image expectations.

### How to Rebuild/Run
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

### Verify Inside Container
```bash
docker compose run --rm snake-game bash -lc "python3 -c 'import torch; print(torch.cuda.is_available()); print(torch.backends.cudnn.version())'"
```
Expected: `True` and an 8xxx cuDNN version.

### If It Still Fails
- On the Jetson host (outside Docker), confirm cuDNN 8 exists:
```bash
find /usr -name "libcudnn.so.8*" 2>/dev/null
```
If not found, upgrade to JetPack 4.6.x (L4T r32.7.x) or install `libcudnn8`.
