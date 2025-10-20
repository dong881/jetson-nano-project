# Testing Instructions for Jetson Nano

This document provides step-by-step instructions for testing the libcudnn.so.8 fix on your Jetson Nano.

## Prerequisites

Before testing, ensure you have:

1. **Jetson Nano with JetPack 4.6.x** installed
   - Verify: `dpkg -l | grep nvidia`
   - Should show CUDA 10.2 packages

2. **Docker and Docker Compose** installed
   - Verify: `docker --version` and `docker compose version`

3. **nvidia-container-runtime** installed
   - Verify: `docker info | grep -i runtime`
   - Should show: `Runtimes: nvidia runc`

4. **CuDNN installed on host** (comes with JetPack)
   - Verify: `find /usr -name "libcudnn.so*" 2>/dev/null`
   - Should find files like `/usr/lib/aarch64-linux-gnu/libcudnn.so.8.x.x.x`

## Testing Steps

### 1. Pull the Latest Changes

```bash
cd ~/jetson-nano-project
git fetch origin
git checkout copilot/fix-docker-compose-issues
git pull origin copilot/fix-docker-compose-issues
```

### 2. Clean Previous Docker Builds

```bash
# Stop any running containers
docker compose down

# Remove old images (optional but recommended)
docker image prune -a

# Remove build cache (optional but recommended)
docker builder prune -a
```

### 3. Allow X11 Connections

```bash
xhost +local:docker
```

### 4. Build the Docker Image

```bash
docker compose build --no-cache
```

**Expected output:**
- Build should complete without errors
- You should see the removal of conflicting libraries during the build

### 5. Start the Container

```bash
docker compose up
```

**Expected output:**

```
[+] Running 1/1
 ✔ Container jetson-nano-project-snake-game-1  Created
Attaching to jetson-nano-project-snake-game-1
jetson-nano-project-snake-game-1  | ========================================
jetson-nano-project-snake-game-1  | CUDA Library Configuration Check
jetson-nano-project-snake-game-1  | ========================================
jetson-nano-project-snake-game-1  | LD_LIBRARY_PATH: /usr/local/lib:/usr/local/cuda/lib64:...
jetson-nano-project-snake-game-1  |
jetson-nano-project-snake-game-1  | Searching for CUDA libraries...
jetson-nano-project-snake-game-1  | Found libcurand in: /usr/local/cuda/lib64
jetson-nano-project-snake-game-1  | ...
jetson-nano-project-snake-game-1  | ✓ CUDA libraries found
jetson-nano-project-snake-game-1  |
jetson-nano-project-snake-game-1  | Checking for missing CUDA library symlinks...
jetson-nano-project-snake-game-1  | Creating symlink: /usr/local/lib/libcurand.so.10 -> ...
jetson-nano-project-snake-game-1  | Creating symlink: /usr/local/lib/libcublas.so.10 -> ...
jetson-nano-project-snake-game-1  | ✓ CUDA symlinks check complete
jetson-nano-project-snake-game-1  |
jetson-nano-project-snake-game-1  | ========================================
jetson-nano-project-snake-game-1  | Starting Snake Game Application
jetson-nano-project-snake-game-1  | ========================================
jetson-nano-project-snake-game-1  |
jetson-nano-project-snake-game-1  | pygame 2.1.2 (SDL 2.0.16, Python 3.6.9)
jetson-nano-project-snake-game-1  | Hello from the pygame community. https://www.pygame.org/contribute.html
```

**What you should NOT see:**
- ❌ `OSError: /usr/lib/aarch64-linux-gnu/libcudnn.so.8: file too short`
- ❌ `jetson-nano-project-snake-game-1 exited with code 1`

### 6. Verify CUDA and CuDNN Inside Container

Open a new terminal and run:

```bash
docker compose exec snake-game python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CuDNN version: {torch.backends.cudnn.version()}')"
```

**Expected output:**
```
CUDA available: True
CuDNN version: 8204
```
(The exact CuDNN version number may vary depending on your JetPack version)

### 7. Test the Application

The Snake Game window should appear on your display. Test:

1. **Human Mode** (default):
   - Use arrow keys to control the snake
   - Try to eat apples
   - Verify the game works smoothly

2. **Training Mode**:
   - Click "Switch to Training" button
   - Verify AI starts training
   - Check that training statistics update
   - Observe GPU usage: `sudo tegrastats` in another terminal

### 8. Check CUDA Acceleration

In another terminal:

```bash
# Monitor GPU usage while training
sudo tegrastats

# You should see GPU usage increase when in training mode
```

### 9. Stop the Container

```bash
# Press Ctrl+C in the terminal running docker compose
# Or in another terminal:
docker compose down
```

## Success Criteria

✅ **The fix is successful if:**

1. Container builds without errors
2. Container starts without "file too short" error
3. Application window appears
4. PyTorch reports CUDA is available
5. CuDNN version is displayed (not an error)
6. Game runs smoothly in both human and training modes
7. GPU usage increases during training (visible in tegrastats)

## Troubleshooting

If you encounter issues, check:

1. **Container logs**:
   ```bash
   docker compose logs
   ```

2. **Library files on host**:
   ```bash
   ls -la /usr/lib/aarch64-linux-gnu/libcudnn*
   ls -la /usr/local/cuda/lib64/
   ```

3. **nvidia-container-runtime**:
   ```bash
   docker info | grep -i runtime
   docker run --rm --runtime nvidia nvcr.io/nvidia/l4t-base:r32.7.1 nvidia-smi
   ```

4. **JetPack version**:
   ```bash
   dpkg -l | grep nvidia-jetpack
   ```

## Reporting Results

After testing, please report:

1. ✅ Success or ❌ Failure
2. Any error messages encountered
3. Output of diagnostic commands above
4. Screenshots of the application running (if successful)

## Additional Verification

For extra confidence, you can also:

1. **Check symlinks created**:
   ```bash
   docker compose exec snake-game ls -la /usr/local/lib/
   ```
   Should show symlinks like `libcurand.so.10`, `libcudnn.so.8`, etc.

2. **Verify LD_LIBRARY_PATH**:
   ```bash
   docker compose exec snake-game printenv LD_LIBRARY_PATH
   ```
   Should start with `/usr/local/lib:`

3. **Test with ldd**:
   ```bash
   docker compose exec snake-game python3 -c "import torch; import torch.backends.cudnn"
   ```
   Should load without errors

## Clean Up (After Testing)

If you want to clean up after testing:

```bash
# Stop and remove containers
docker compose down

# Remove the image (optional)
docker image rm jetson-nano-project-snake-game

# Remove unused images and cache
docker system prune -a
```

## Next Steps

If testing is successful:
1. The PR can be merged to main branch
2. Update CHANGELOG.md with the fix
3. Create a new release/tag if appropriate

If testing fails:
1. Collect the diagnostic information listed above
2. Open an issue or comment on the PR with details
3. We'll investigate and provide additional fixes
