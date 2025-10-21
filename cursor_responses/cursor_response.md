# CUDA Library Fix for Snake Game Docker Container

## Problem Analysis

The Docker container was failing with the error:
```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
```

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