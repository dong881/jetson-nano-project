# Troubleshooting Guide

This guide provides detailed solutions to common issues when running the Snake Game with RL on Jetson Nano.

## Table of Contents

- [CUDA Library Errors](#cuda-library-errors)
- [Docker Build Issues](#docker-build-issues)
- [Docker Runtime Issues](#docker-runtime-issues)
- [Display Issues](#display-issues)
- [Package Compatibility Issues](#package-compatibility-issues)
- [Performance Issues](#performance-issues)

---

## CUDA Library Errors

### libcurand.so.10: cannot open shared object file

**Error Message:**
```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
```

**Cause:**
PyTorch is looking for `libcurand.so.10` but the host CUDA installation only has `libcurand.so.10.0` or `libcurand.so.10.0.326` with incomplete symlinks. This happens when:
1. The host CUDA installation is missing intermediate version symlinks
2. CUDA libraries are mounted read-only, preventing symlink creation in the mounted directory
3. JetPack is not fully installed or has been partially updated

**Solution:**

The latest version of the project includes an automatic fix in the `check_cuda.sh` startup script that creates the necessary symlinks at runtime.

**1. Verify JetPack is installed on your Jetson Nano**

JetPack includes CUDA 10.2 which is required. Check if CUDA is installed:

```bash
# Check if CUDA directory exists
ls /usr/local/cuda/lib64/libcurand.so*

# Check JetPack version
dpkg -l | grep nvidia

# Expected: cuda-10-2, cuda-toolkit-10-2, etc.
```

If CUDA is not installed, you need to install JetPack 4.6.x on your Jetson Nano.

### libcufft.so.10 / libcusparse.so.10 / libcusolver.so.10: cannot open shared object file

**Error Message:**
```
OSError: libcufft.so.10: cannot open shared object file: No such file or directory
```
(or similar errors for libcusparse.so.10, libcusolver.so.10)

**Cause:**
PyTorch requires various CUDA libraries beyond just libcurand. Depending on the operations used, it may need:
- `libcufft.so.10` (CUDA FFT library for Fourier transforms)
- `libcusparse.so.10` (CUDA sparse matrix operations)
- `libcusolver.so.10` (CUDA linear algebra operations)

The host CUDA installation has these libraries with specific versions (e.g., `libcufft.so.10.0.326`), but the intermediate version symlinks (e.g., `libcufft.so.10`) are missing.

**Solution:**

The latest version of the project (v2.0+) includes automatic creation of these symlinks in the `check_cuda.sh` startup script. The script now creates symlinks for all commonly needed CUDA libraries:
- libcurand.so.10
- libcublas.so.10
- libcublasLt.so.10
- libcudnn.so.8
- libcufft.so.10
- libcusparse.so.10
- libcusolver.so.10

**To apply the fix:**

1. **Update to the latest version**:
   ```bash
   git pull origin main
   ```

2. **Rebuild and restart**:
   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up
   ```

3. **Verify the symlinks are created**:
   When the container starts, you should see output like:
   ```
   Creating symlink: /usr/local/lib/libcufft.so.10 -> /usr/local/cuda/lib64/libcufft.so.10.0.326
   Creating symlink: /usr/local/lib/libcusparse.so.10 -> /usr/local/cuda/lib64/libcusparse.so.10.0.326
   Creating symlink: /usr/local/lib/libcusolver.so.10 -> /usr/local/cuda/lib64/libcusolver.so.10.0.326
   ```

**2. Verify nvidia-container-runtime is installed**

```bash
# Check if nvidia runtime is available
docker info | grep -i runtime

# Should show: Runtimes: nvidia runc

# Test NVIDIA runtime
docker run --rm --runtime nvidia nvcr.io/nvidia/l4t-base:r32.7.1 nvidia-smi
```

If nvidia-container-runtime is not installed, install it:

```bash
# Install nvidia-container-runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

**3. Rebuild with the latest configuration**

The latest Dockerfile and check_cuda.sh script have been updated to automatically create missing CUDA library symlinks:

```bash
# Clean rebuild
docker compose down
docker compose build --no-cache
docker compose up
```

**4. Check the startup diagnostics**

When the container starts, it will now show CUDA library diagnostics and create missing symlinks:

```bash
docker compose up
# Look for "CUDA Library Configuration Check" in the output
# It will show if libraries are found and if symlinks were created
```

**What the fix does:**

The updated configuration:
- Sets `LD_LIBRARY_PATH` to include `/usr/local/lib` for runtime-created symlinks
- Automatically detects missing CUDA library version symlinks
- Creates symlinks like `libcurand.so.10 -> libcurand.so.10.0.326` in `/usr/local/lib`
- Mounts `/usr/local/cuda` from the host (where JetPack installs CUDA)
- Uses nvidia-container-runtime to inject GPU drivers
- Includes a startup script that checks for CUDA libraries and provides helpful error messages

**If the problem persists:**

1. **Check CUDA location on your Jetson Nano:**
   ```bash
   # On the Jetson Nano host (not in Docker)
   find /usr -name "libcurand.so*" 2>/dev/null
   ```

2. **Verify the symlinks were created:**
   ```bash
   docker compose up
   # Look for messages like "Creating symlink: /usr/local/lib/libcurand.so.10 -> ..."
   ```

3. **If CUDA is in a different location**, update docker-compose.yml:
   ```yaml
   volumes:
     - /your/cuda/path:/usr/local/cuda:ro
   ```

4. **Check Docker logs for more details:**
   ```bash
   docker compose logs
   ```

---

## Docker Build Issues

### GPG Key Verification Error

**Error Message:**
```
E: The repository 'https://apt.kitware.com/ubuntu bionic InRelease' is not signed.
```

**Cause:**
The Kitware APT repository has GPG key issues that can break the Docker build process.

**Solution:**

The latest Dockerfile comprehensively removes all Kitware repository references. If you still encounter this issue:

1. **Ensure you're using the latest version of the Dockerfile**

2. **Rebuild without cache**:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

3. **If the issue persists**, manually remove Kitware references:
```bash
# On your Jetson Nano (not in container)
sudo rm -f /etc/apt/sources.list.d/kitware.list*
sudo find /etc/apt/sources.list.d/ -type f -name '*kitware*' -delete
sudo sed -i '/kitware/d' /etc/apt/sources.list
sudo apt-key del 16FAAD7AF99A65E2
sudo apt-get update
```

---

## Docker Runtime Issues

### Read-Only File System Error

**Error Message:**
```
nvidia-container-cli: mount error: file creation failed: /var/lib/docker/overlay2/.../merged/usr/lib/aarch64-linux-gnu/libcuda.so.1.1: read-only file system: unknown
```

**Cause:**
The nvidia-container-runtime tries to inject NVIDIA libraries into a directory that is mounted as read-only from the host.

**Solution:**

1. **Remove the read-only mount of `/usr/lib/aarch64-linux-gnu`** from docker-compose.yml (should NOT be present in the latest version)

2. **Ensure your docker-compose.yml looks like this**:
```yaml
volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix:ro
  - /usr/local/cuda:/usr/local/cuda:ro
  - ./model:/app/model
  - ./high_score.txt:/app/high_score.txt
# NOTE: Do NOT mount /usr/lib/aarch64-linux-gnu
```

3. **Rebuild and restart**:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

### File Exists Error

**Error Message:**
```
nvidia-container-cli: mount error: file creation failed: /var/lib/docker/overlay2/.../merged/usr/lib/libvisionworks.so: file exists
```

**Cause:**
The NVIDIA container runtime tries to mount libraries that already exist in the container image.

**Solution:**

The latest Dockerfile removes conflicting NVIDIA libraries during the build process. This is safe because nvidia-container-runtime will provide these libraries from the host system at runtime.

1. **Ensure you're using the latest version of the Dockerfile**

2. **Rebuild without cache**:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

3. **Verify the Dockerfile contains**:
```dockerfile
# Remove conflicting NVIDIA libraries
RUN rm -f /usr/lib/aarch64-linux-gnu/libcuda.so* \
    /usr/lib/aarch64-linux-gnu/libnvidia-*.so* \
    /usr/lib/aarch64-linux-gnu/libvisionworks*.so* \
    # ... etc
```

---

## Display Issues

### X11 Connection Errors

**Error Message:**
```
No protocol specified
cannot connect to X server :0
```

**Cause:**
Docker container doesn't have permission to access the X11 display server.

**Solution:**

1. **Allow X11 connections from Docker**:
```bash
xhost +local:docker
```

2. **Set DISPLAY environment variable**:
```bash
export DISPLAY=:0
```

3. **Verify X11 socket is mounted** in docker-compose.yml:
```yaml
volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix:ro
environment:
  - DISPLAY=${DISPLAY}
```

### Headless Environment (No Display)

**Scenario:**
Running on a headless system or via SSH without X11 forwarding.

**Solution:**

Set up a virtual display using Xvfb:

```bash
# Install Xvfb
sudo apt-get install xvfb

# Start virtual display
Xvfb :99 -screen 0 1024x768x24 &

# Set DISPLAY variable
export DISPLAY=:99

# Run your application
python main.py
```

For testing without display:
```bash
export SDL_VIDEODRIVER=dummy
python test_snake_game.py
```

---

## Package Compatibility Issues

### Python Version Mismatch

**Issue:**
Error installing packages due to Python version incompatibility.

**Cause:**
The Docker base image uses Python 3.6.9, but some packages require newer Python versions.

**Solution:**

The requirements.txt has been updated with Python 3.6 compatible versions:

```txt
# Python 3.6 compatible versions
pygame==2.1.2    # Last version supporting Python 3.6
numpy==1.19.5    # Last version supporting Python 3.6
# PyTorch 1.10 pre-installed in base image
```

**Do NOT upgrade** to these versions (incompatible with Python 3.6):
- ❌ pygame 2.5.2 (requires Python 3.8+)
- ❌ torch 2.0.1 (requires Python 3.8+)
- ❌ numpy 1.24.3 (requires Python 3.8+)

### PyTorch Version Mismatch

**Issue:**
Attempting to install PyTorch 2.x on Jetson Nano causes errors.

**Cause:**
Jetson Nano with JetPack 4.6.x uses CUDA 10.2, which is only compatible with PyTorch 1.10 or earlier.

**Solution:**

**DO NOT** install PyTorch via pip in the Dockerfile or requirements.txt. The base Docker image `nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3` already includes:
- PyTorch 1.10 (built for CUDA 10.2)
- Python 3.6.9
- All necessary CUDA libraries

If you accidentally installed the wrong version:
```bash
# Remove incorrect PyTorch
pip3 uninstall torch

# Use the base image's PyTorch (already installed)
# No need to reinstall
```

### Pip Upgrade Issues

**Issue:**
Latest pip version may not work correctly with Python 3.6.

**Solution:**

Use pip version < 21.0 for Python 3.6 compatibility:
```bash
pip3 install --upgrade "pip<21.0"
```

---

## Performance Issues

### Low FPS / Laggy Training

**Possible Causes:**
1. CUDA not being used (running on CPU)
2. Insufficient memory
3. Thermal throttling

**Solutions:**

1. **Verify CUDA is available**:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device: {torch.cuda.get_device_name(0)}")
```

2. **Check memory usage**:
```bash
# Monitor GPU memory
tegrastats

# Monitor system memory
free -h
```

3. **Reduce batch size** if memory is low (in `agent.py`):
```python
BATCH_SIZE = 500  # Reduce from 1000
```

4. **Enable fan** (if thermal throttling):
```bash
# Set fan to maximum
sudo jetson_clocks
sudo sh -c 'echo 255 > /sys/devices/pwm-fan/target_pwm'
```

### High Memory Usage

**Solution:**

1. **Reduce memory buffer size** in `agent.py`:
```python
MAX_MEMORY = 50_000  # Reduce from 100,000
```

2. **Close other applications**:
```bash
# Kill unnecessary processes
sudo systemctl stop nvargus-daemon
```

---

## Additional Resources

### Useful Commands

**Check CUDA installation:**
```bash
nvcc --version
ls /usr/local/cuda/lib64/
```

**Check Docker setup:**
```bash
docker info
docker ps
docker logs <container_id>
```

**Monitor Jetson Nano:**
```bash
tegrastats
jtop  # Install with: sudo pip3 install jetson-stats
```

**Clean up Docker:**
```bash
# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Clean everything
docker system prune -a
```

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/dong881/jetson-nano-project/issues)
2. Create a new issue with:
   - Error message (full stack trace)
   - Your system info (JetPack version, Docker version)
   - Steps to reproduce
   - docker-compose.yml and Dockerfile content

---

## Version Compatibility Matrix

| Component | Version | Python | CUDA | Notes |
|-----------|---------|--------|------|-------|
| JetPack | 4.6.x | 3.6.9 | 10.2 | Required for Jetson Nano |
| PyTorch | 1.10 | 3.6+ | 10.2 | Pre-installed in base image |
| pygame | 2.1.2 | 3.6+ | N/A | Last version for Python 3.6 |
| numpy | 1.19.5 | 3.6+ | N/A | Last version for Python 3.6 |
| Docker | 19.03+ | N/A | N/A | With nvidia-container-runtime |

**Important:** Do not mix versions from different rows. Use the exact versions specified for Jetson Nano compatibility.
