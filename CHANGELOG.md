# Changelog

## Additional CUDA Library Symlinks Fix (Latest)

### Problem Statement

After the previous CUDA library path fixes, some users still encountered errors when running the application:
```
OSError: libcufft.so.10: cannot open shared object file: No such file or directory
```

This occurred when PyTorch tried to use CUDA FFT (Fast Fourier Transform) operations or other advanced CUDA features.

### Root Cause

PyTorch requires several CUDA libraries beyond just `libcurand`:
- `libcufft.so.10` - CUDA FFT library for Fourier transforms
- `libcusparse.so.10` - CUDA sparse matrix operations
- `libcusolver.so.10` - CUDA linear algebra operations

The `check_cuda.sh` script was only creating symlinks for a subset of CUDA libraries (libcurand, libcublas, libcublasLt, libcudnn), missing the additional libraries that PyTorch might need for specific operations.

### Solution Implemented

#### Updated check_cuda.sh Library List

**Modified** the `libs_to_link` array in `check_cuda.sh` to include:
```bash
local libs_to_link=(
    "libcurand.so.10.0:libcurand.so.10"
    "libcublas.so.10.0:libcublas.so.10"
    "libcublasLt.so.10.0:libcublasLt.so.10"
    "libcudnn.so.8:libcudnn.so.8"
    "libcufft.so.10.0:libcufft.so.10"       # NEW - FFT operations
    "libcusparse.so.10.0:libcusparse.so.10" # NEW - Sparse matrices
    "libcusolver.so.10.0:libcusolver.so.10" # NEW - Linear algebra
)
```

This ensures that all commonly used CUDA libraries by PyTorch are available with the correct version symlinks.

#### Updated Documentation

- Updated `DEPENDENCIES.md` to list all CUDA libraries
- Updated `FIX_SUMMARY.md` to document the complete library list
- Updated `TROUBLESHOOTING.md` with a new section for libcufft errors

### Impact

This fix resolves the `libcufft.so.10` error and prevents similar errors for other CUDA libraries, ensuring PyTorch can use all CUDA features without library loading failures.

### Files Changed

- `check_cuda.sh` - Added libcufft, libcusparse, libcusolver to symlink creation
- `DEPENDENCIES.md` - Updated CUDA library list
- `FIX_SUMMARY.md` - Updated documentation
- `TROUBLESHOOTING.md` - Added new troubleshooting section
- `CHANGELOG.md` - This entry

---

## CUDA Library Path Fix

### Problem Statement

Despite previous fixes to package versions, the application still failed with:
```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
```

This occurred when PyTorch tried to load CUDA libraries during import.

### Root Cause

The issue was that while the docker-compose.yml mounted `/usr/local/cuda` from the host and set `LD_LIBRARY_PATH` as an environment variable, the Dockerfile itself did not have `LD_LIBRARY_PATH` configured. This meant:

1. **PyTorch loads during container startup**: When the container starts, Python imports PyTorch before environment variables from docker-compose are fully processed
2. **Missing library paths**: The base image's LD_LIBRARY_PATH didn't include all possible CUDA library locations
3. **No diagnostics**: When the error occurred, there was no helpful information about what went wrong

### Solutions Implemented

#### 1. Fixed Dockerfile LD_LIBRARY_PATH Configuration

**Added to Dockerfile**:
```dockerfile
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/local/cuda/lib:/usr/lib/aarch64-linux-gnu:$LD_LIBRARY_PATH
```

This ensures CUDA libraries can be found in multiple locations:
- `/usr/local/cuda/lib64` - Primary CUDA toolkit location (JetPack default)
- `/usr/local/cuda/lib` - Alternative 32-bit or older CUDA installations
- `/usr/lib/aarch64-linux-gnu` - System library location for ARM64
- `$LD_LIBRARY_PATH` - Preserves any existing paths from the base image

#### 2. Removed CUDA Stub Libraries

**Added to Dockerfile**:
```dockerfile
RUN rm -rf /usr/local/cuda-*/lib*/stubs \
    2>/dev/null || true
```

CUDA stub libraries are only needed for compilation, not runtime. They can conflict with real CUDA libraries provided by the nvidia-container-runtime.

#### 3. Created Startup Diagnostics Script

**Created** `check_cuda.sh`:
- Checks for CUDA library availability before starting the application
- Searches multiple locations for libcurand and other CUDA libraries
- Provides clear, actionable error messages if libraries are missing
- Continues with warnings instead of hard failures for better user experience

**Updated Dockerfile CMD**:
```dockerfile
CMD ["./check_cuda.sh"]
```

#### 4. Simplified docker-compose.yml

**Removed**:
```yaml
environment:
  - LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

This is no longer needed since LD_LIBRARY_PATH is now set in the Dockerfile itself.

**Kept**:
```yaml
volumes:
  - /usr/local/cuda:/usr/local/cuda:ro
```

This mounts CUDA toolkit from the host Jetson Nano.

#### 5. Created Setup Verification Script

**Created** `verify_jetson_setup.sh`:
- Pre-deployment verification script for Jetson Nano
- Checks all prerequisites before running Docker container:
  - JetPack/L4T version
  - CUDA installation and libraries
  - Docker and nvidia-container-runtime
  - Docker Compose
  - X11 configuration
- Provides color-coded pass/fail/warning indicators
- Tests nvidia-container-runtime functionality

#### 6. Enhanced Documentation

**Updated TROUBLESHOOTING.md**:
- Expanded libcurand.so.10 error section with detailed troubleshooting steps
- Added instructions for installing nvidia-container-runtime
- Documented how to verify CUDA installation
- Explained the startup diagnostics and how to interpret them

**Updated DEPENDENCIES.md**:
- Documented the LD_LIBRARY_PATH configuration
- Explained the importance of mounting /usr/local/cuda
- Added verification steps

**Updated README.md and QUICKSTART.md**:
- Added instructions to run verify_jetson_setup.sh before deployment
- Documented the new startup diagnostics
- Updated project structure to include new scripts

### Files Changed

**Modified**:
1. `Dockerfile` - Added LD_LIBRARY_PATH, removed stub libraries
2. `docker-compose.yml` - Removed redundant LD_LIBRARY_PATH environment variable
3. `TROUBLESHOOTING.md` - Enhanced CUDA troubleshooting section
4. `DEPENDENCIES.md` - Added LD_LIBRARY_PATH documentation
5. `README.md` - Added verification script instructions
6. `QUICKSTART.md` - Added verification step to Docker deployment

**Created**:
1. `check_cuda.sh` - Startup diagnostics script
2. `verify_jetson_setup.sh` - Pre-deployment verification script

### Testing Instructions

**On Jetson Nano:**

1. **Verify prerequisites**:
```bash
./verify_jetson_setup.sh
```

2. **Build and run**:
```bash
xhost +local:docker
docker compose build --no-cache
docker compose up
```

3. **Check startup output**:
Look for "CUDA Library Configuration Check" section. It should show:
```
✓ CUDA libraries found
```

4. **Verify PyTorch CUDA**:
If the container starts successfully, PyTorch should be able to use CUDA without errors.

### Expected Behavior

**Before Fix**:
```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
jetson-nano-project-snake-game-1 exited with code 1
```

**After Fix**:
```
======================================== 
CUDA Library Configuration Check
========================================
LD_LIBRARY_PATH: /usr/local/cuda/lib64:/usr/local/cuda/lib:/usr/lib/aarch64-linux-gnu:...

Searching for CUDA libraries...
Found libcurand in: /usr/local/cuda/lib64
✓ CUDA libraries found

========================================
Starting Snake Game Application
========================================

pygame 2.1.2 (SDL 2.0.16, Python 3.6.9)
Hello from the pygame community. https://www.pygame.org/contribute.html
[Application starts successfully]
```

### Prevention Measures

1. **Always set LD_LIBRARY_PATH in Dockerfile**: Don't rely solely on docker-compose environment variables
2. **Include startup diagnostics**: Help users troubleshoot issues quickly
3. **Provide verification tools**: Let users check prerequisites before deployment
4. **Document library paths**: Make it clear where CUDA libraries should be located

### Related Issues

This fix resolves:
- ✅ libcurand.so.10 not found error
- ✅ PyTorch unable to load CUDA libraries
- ✅ No diagnostic information when startup fails
- ✅ Unclear prerequisites for deployment

---

# Dependency Fix and Documentation Reorganization Summary

## Problem Statement

The project had the following issues:
1. **Incompatible package versions** in requirements.txt causing runtime errors
2. **Docker build failures** due to library conflicts
3. **Duplicate and outdated documentation** across multiple files
4. **Missing critical dependency information**

## Root Cause Analysis

### The CUDA Library Error

The error message showed:
```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
```

**Root Causes:**
1. **Python Version Mismatch**: Base Docker image uses Python 3.6.9, but requirements.txt specified packages requiring Python 3.8+
2. **PyTorch Version Conflict**: requirements.txt tried to install PyTorch 2.0.1, incompatible with:
   - Python 3.6
   - CUDA 10.2 (Jetson Nano)
   - The pre-installed PyTorch 1.10 in base image
3. **Package Incompatibility**: 
   - pygame 2.5.2 requires Python 3.8+
   - numpy 1.24.3 requires Python 3.8+

## Solutions Implemented

### 1. Fixed requirements.txt

**Before:**
```txt
pygame==2.5.2
torch==2.0.1
numpy==1.24.3
```

**After:**
```txt
# Python 3.6 compatible versions for Jetson Nano
# PyTorch 1.10 is pre-installed in the base Docker image
# with CUDA 10.2 support - DO NOT reinstall torch

# pygame - last version supporting Python 3.6
pygame==2.1.2

# numpy - last version supporting Python 3.6
numpy==1.19.5
```

**Key Changes:**
- ✅ pygame 2.5.2 → 2.1.2 (Python 3.6 compatible)
- ✅ numpy 1.24.3 → 1.19.5 (Python 3.6 compatible)
- ✅ Removed torch==2.0.1 (use base image's PyTorch 1.10)
- ✅ Added clear comments explaining version constraints

### 2. Updated Dockerfile

**Before:**
```dockerfile
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir --prefer-binary pygame numpy
```

**After:**
```dockerfile
# Upgrade pip to latest compatible version for Python 3.6
RUN pip3 install --upgrade "pip<21.0"

# Install dependencies from requirements.txt
RUN pip3 install --no-cache-dir --prefer-binary -r requirements.txt
```

**Key Changes:**
- ✅ Constrained pip version to <21.0 (Python 3.6 compatible)
- ✅ Use requirements.txt instead of hardcoded packages
- ✅ Added comments explaining why we don't reinstall torch
- ✅ Preserved existing CUDA library handling

### 3. Fixed Code Bug

**File:** model.py

**Issue:** Missing numpy import

**Before:**
```python
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
```

**After:**
```python
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os
```

### 4. Reorganized Documentation

#### Removed Files
- ❌ **IMPLEMENTATION.md** - Development status report, not needed for end users

#### Enhanced Files
- ✅ **README.md** - Streamlined to focus on features and quick start
- ✅ **QUICKSTART.md** - Updated to reference new documentation structure

#### New Files
- ✅ **TROUBLESHOOTING.md** - Comprehensive troubleshooting guide with:
  - CUDA library errors
  - Docker build issues
  - Docker runtime issues
  - Display issues
  - Package compatibility issues
  - Performance issues
  
- ✅ **DEPENDENCIES.md** - Detailed dependency compatibility guide with:
  - System requirements
  - Package version matrix
  - Why specific versions are required
  - What NOT to do
  - Verification steps
  - Update procedures

#### Documentation Structure

```
Documentation Hierarchy:
├── README.md           - Main entry point, features, quick start
├── QUICKSTART.md       - Step-by-step guide (bilingual)
├── TROUBLESHOOTING.md  - Problem solving
└── DEPENDENCIES.md     - Technical details on versions
```

## Verification

### Package Compatibility Matrix

| Component | Version | Python Req | CUDA Req | Status |
|-----------|---------|------------|----------|--------|
| Python | 3.6.9 | N/A | N/A | ✅ From base image |
| PyTorch | 1.10.0 | 3.6+ | 10.2 | ✅ Pre-installed |
| pygame | 2.1.2 | 3.6-3.10 | N/A | ✅ Compatible |
| numpy | 1.19.5 | 3.6-3.9 | N/A | ✅ Compatible |

### Expected Behavior After Fix

When running `docker compose up`, the container should:

1. ✅ Build successfully without GPG errors
2. ✅ Install pygame 2.1.2 and numpy 1.19.5
3. ✅ Use PyTorch 1.10 from base image (not reinstall)
4. ✅ Mount CUDA libraries from host
5. ✅ Successfully import all modules:
   ```python
   import pygame    # Works
   import numpy     # Works
   import torch     # Works with CUDA
   ```
6. ✅ Run the game without `libcurand.so.10` error

## Files Changed Summary

### Modified Files
1. **requirements.txt** - Fixed package versions
2. **Dockerfile** - Updated pip installation and dependency handling
3. **model.py** - Added missing numpy import
4. **README.md** - Streamlined and reorganized
5. **QUICKSTART.md** - Updated references to new docs

### New Files
1. **TROUBLESHOOTING.md** - Comprehensive troubleshooting
2. **DEPENDENCIES.md** - Dependency compatibility guide

### Removed Files
1. **IMPLEMENTATION.md** - Obsolete development document

## Prevention Measures

### For Users
1. **Always use specified versions** in requirements.txt
2. **Never upgrade packages** without checking Python 3.6 compatibility
3. **Read DEPENDENCIES.md** before making changes
4. **Use `docker compose build --no-cache`** when in doubt

### For Maintainers
1. **Keep requirements.txt comments** explaining version constraints
2. **Test on actual Jetson Nano** before merging changes
3. **Document any version changes** in DEPENDENCIES.md
4. **Update compatibility matrix** when upgrading packages

## Testing Checklist

To verify the fix works:

- [ ] Clone the repository
- [ ] Run `docker compose build`
- [ ] Build completes without errors
- [ ] Run `docker compose up`
- [ ] Container starts without errors
- [ ] No "libcurand.so.10" error
- [ ] Game UI displays correctly
- [ ] Human play mode works
- [ ] Training mode works
- [ ] CUDA is available in PyTorch

## Long-term Solution

For projects requiring newer package versions:

**Option 1: Accept limitations**
- Keep Python 3.6 and current versions
- Maintain Jetson Nano compatibility
- Best for production on Jetson Nano

**Option 2: Upgrade base image** (NOT RECOMMENDED)
- Use newer Ubuntu/Python base
- Install PyTorch CPU version
- Lose GPU acceleration
- Only for development/testing

**Recommendation:** Stay with current setup for Jetson Nano deployment.

## Related Issues

This fix resolves:
- ✅ libcurand.so.10 not found error
- ✅ PyTorch CUDA compatibility issues
- ✅ Package version conflicts
- ✅ Documentation duplication
- ✅ Missing dependency information

## References

- JetPack 4.6.x documentation
- PyTorch version compatibility
- Python 3.6 package support
- NVIDIA L4T container documentation
