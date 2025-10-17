# Dependency Compatibility Guide

This document explains the package version requirements and compatibility for the Snake Game with RL project on Jetson Nano.

## Overview

The project is designed to run on **Jetson Nano with JetPack 4.6.x**, which provides specific versions of system components that determine our package compatibility.

## System Requirements

### Hardware
- **Jetson Nano** (4GB recommended)
- At least 2GB available RAM
- Display (or X11 forwarding capability)

### Software
- **JetPack 4.6.x** (provides CUDA 10.2)
- **Docker** 19.03 or higher
- **NVIDIA Container Runtime**

## Docker Base Image

We use the official NVIDIA L4T PyTorch image:

```dockerfile
FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3
```

This image provides:
- **Python 3.6.9**
- **PyTorch 1.10.0** (pre-built for CUDA 10.2)
- **CUDA 10.2** (compatible with Jetson Nano)
- **cuDNN 8.2.1**
- All necessary CUDA libraries (libcurand, libcublas, etc.)

## Python Package Dependencies

### Critical Version Constraints

All package versions are constrained by **Python 3.6** compatibility:

| Package | Version | Reason |
|---------|---------|--------|
| pygame | 2.1.2 | Last version supporting Python 3.6 |
| numpy | 1.19.5 | Last version supporting Python 3.6 |
| PyTorch | 1.10.0 | Pre-installed, CUDA 10.2 compatible |

### Why These Specific Versions?

#### Python 3.6.9
- **Provided by**: JetPack 4.6.x base system
- **Cannot upgrade**: System Python tied to JetPack
- **Constraint**: Many modern packages require Python 3.8+

#### PyTorch 1.10.0
- **Source**: Pre-installed in Docker base image
- **CUDA version**: Built for CUDA 10.2 (Jetson Nano's CUDA)
- **Why not 2.0+**: Requires Python 3.8+ and CUDA 11+
- **DO NOT REINSTALL**: Installing via pip breaks CUDA compatibility

#### pygame 2.1.2
- **Latest for Python 3.6**: Version 2.2+ requires Python 3.8+
- **Tested**: Fully functional for our game UI
- **SDL version**: Compatible with system libraries

#### numpy 1.19.5
- **Latest for Python 3.6**: Version 1.20+ requires Python 3.8+
- **PyTorch compatible**: Works with PyTorch 1.10
- **Tested**: All array operations work correctly

## What NOT To Do

### ❌ Do NOT Install These Versions

These versions will FAIL on Jetson Nano with JetPack 4.6.x:

```txt
# ❌ WRONG - These require Python 3.8+
pygame==2.5.2
torch==2.0.1
numpy==1.24.3
```

### ❌ Do NOT Reinstall PyTorch

```dockerfile
# ❌ WRONG - This breaks CUDA compatibility
RUN pip3 install torch
```

PyTorch is already installed in the base image with correct CUDA bindings. Reinstalling via pip will:
1. Install CPU-only version or wrong CUDA version
2. Break CUDA library linkage
3. Cause `libcurand.so.10` errors

### ❌ Do NOT Upgrade pip Beyond 21.0

```bash
# ❌ WRONG - Latest pip drops Python 3.6 support
pip3 install --upgrade pip

# ✅ CORRECT - Use pip compatible with Python 3.6
pip3 install --upgrade "pip<21.0"
```

## Dependency Installation Order

The Dockerfile installs dependencies in this specific order:

```dockerfile
# 1. Update package lists (after removing problematic repos)
RUN apt-get update && apt-get install -y <system-packages>

# 2. Upgrade pip to last Python 3.6 compatible version
RUN pip3 install --upgrade "pip<21.0"

# 3. Install Python packages from requirements.txt
RUN pip3 install --no-cache-dir --prefer-binary -r requirements.txt

# NOTE: PyTorch is NOT installed here - it's already in the base image
```

## Verification Steps

After building the Docker image, verify the installation:

```bash
# Enter the container
docker run -it <image-name> /bin/bash

# Check Python version
python3 --version
# Expected: Python 3.6.9

# Check PyTorch
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"
# Expected: PyTorch: 1.10.0+, CUDA: True

# Check pygame
python3 -c "import pygame; print(f'pygame: {pygame.version.ver}')"
# Expected: pygame: 2.1.2

# Check numpy
python3 -c "import numpy; print(f'numpy: {numpy.__version__}')"
# Expected: numpy: 1.19.5

# Test CUDA libraries
python3 -c "import torch; print(torch.cuda.get_device_name(0))"
# Expected: GPU device name (e.g., "NVIDIA Tegra X1")
```

## Common Issues and Solutions

### Issue: libcurand.so.10 not found

**Cause**: CUDA libraries not mounted from host

**Solution**: Ensure docker-compose.yml has:
```yaml
volumes:
  - /usr/local/cuda:/usr/local/cuda:ro
environment:
  - LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

### Issue: pygame version mismatch

**Cause**: Attempting to install pygame 2.2+

**Solution**: Use pygame 2.1.2 (specified in requirements.txt)

### Issue: numpy import error

**Cause**: Attempting to install numpy 1.20+

**Solution**: Use numpy 1.19.5 (specified in requirements.txt)

### Issue: PyTorch CUDA not available

**Cause**: PyTorch reinstalled via pip, breaking CUDA bindings

**Solution**: 
1. Use base image's PyTorch (do not reinstall)
2. Ensure nvidia runtime is used: `docker run --runtime nvidia`

## Testing Compatibility

Run the test suite to verify all dependencies work:

```bash
# Set dummy video driver (for headless testing)
export SDL_VIDEODRIVER=dummy

# Run tests
python3 test_snake_game.py

# Expected: All tests pass
```

## Updating Dependencies

### When to Update

Only update if:
1. A security vulnerability is discovered
2. A critical bug is fixed in a newer version
3. The new version maintains Python 3.6 compatibility

### How to Update Safely

1. **Check Python compatibility**:
   ```bash
   pip3 index versions <package-name>
   # Look for versions compatible with Python 3.6
   ```

2. **Test in container**:
   ```dockerfile
   # Temporarily modify requirements.txt
   RUN pip3 install <package>==<new-version>
   ```

3. **Verify functionality**:
   ```bash
   python3 test_snake_game.py
   python3 main.py  # Manual testing
   ```

4. **Update requirements.txt** only after verification

## Alternative: Upgrading to Python 3.8+

If you need newer package versions, you must:

1. **Use a different base image** (not L4T for Jetson Nano)
2. **Accept CPU-only PyTorch** (no GPU acceleration)
3. **Lose Jetson Nano optimization**

This is NOT recommended for production on Jetson Nano.

## Reference Links

- [JetPack 4.6 Release Notes](https://developer.nvidia.com/embedded/jetpack-archive)
- [L4T PyTorch Container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-pytorch)
- [PyTorch Compatibility Matrix](https://github.com/pytorch/pytorch/blob/master/RELEASE.md)
- [Python Version Support Policy](https://devguide.python.org/versions/)

## Summary

**The golden rule**: Use the exact versions specified in `requirements.txt`. These versions are:

- **Tested** on Jetson Nano with JetPack 4.6.x
- **Python 3.6 compatible**
- **CUDA 10.2 compatible**
- **Mutually compatible** with each other

Any deviation from these versions may result in:
- Import errors
- CUDA compatibility issues
- Runtime crashes
- Performance degradation

**When in doubt**: Use `docker compose build --no-cache` to rebuild from scratch with the verified versions.
