#!/bin/bash
# Verification script for Jetson Nano CUDA setup
# Run this on your Jetson Nano to verify the setup before running the Docker container

echo "========================================"
echo "Jetson Nano CUDA Setup Verification"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓ $1${NC}"
}

check_fail() {
    echo -e "${RED}✗ $1${NC}"
}

check_warn() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Track if all checks pass
ALL_PASS=true

echo "1. Checking JetPack/L4T version..."
if [ -f /etc/nv_tegra_release ]; then
    L4T_VERSION=$(cat /etc/nv_tegra_release)
    echo "   $L4T_VERSION"
    if echo "$L4T_VERSION" | grep -q "R32"; then
        check_pass "L4T R32 (JetPack 4.x) detected"
    else
        check_warn "L4T version might not be compatible"
        ALL_PASS=false
    fi
else
    check_fail "Cannot detect L4T version - is this a Jetson Nano?"
    ALL_PASS=false
fi
echo ""

echo "2. Checking CUDA installation..."
if [ -d "/usr/local/cuda" ]; then
    check_pass "/usr/local/cuda directory exists"
    
    # Check CUDA version
    if [ -f "/usr/local/cuda/version.txt" ]; then
        CUDA_VERSION=$(cat /usr/local/cuda/version.txt)
        echo "   $CUDA_VERSION"
        if echo "$CUDA_VERSION" | grep -q "10.2"; then
            check_pass "CUDA 10.2 detected (correct for JetPack 4.6)"
        else
            check_warn "CUDA version might not match expected 10.2"
        fi
    fi
else
    check_fail "/usr/local/cuda not found - JetPack might not be installed"
    ALL_PASS=false
fi
echo ""

echo "3. Checking CUDA libraries..."
if [ -d "/usr/local/cuda/lib64" ]; then
    check_pass "/usr/local/cuda/lib64 exists"
    
    # Check for specific libraries PyTorch needs
    REQUIRED_LIBS=(
        "libcudart.so"
        "libcurand.so"
        "libcublas.so"
        "libcusparse.so"
        "libcusolver.so"
    )
    
    for lib in "${REQUIRED_LIBS[@]}"; do
        if ls /usr/local/cuda/lib64/${lib}* &> /dev/null; then
            check_pass "Found $lib"
        else
            check_fail "$lib not found"
            ALL_PASS=false
        fi
    done
else
    check_fail "/usr/local/cuda/lib64 not found"
    ALL_PASS=false
fi
echo ""

echo "4. Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    check_pass "Docker installed: $DOCKER_VERSION"
else
    check_fail "Docker not installed"
    ALL_PASS=false
fi
echo ""

echo "5. Checking nvidia-container-runtime..."
if docker info 2>&1 | grep -q "nvidia"; then
    check_pass "nvidia-container-runtime is configured"
else
    check_fail "nvidia-container-runtime not found"
    echo "   Install with: sudo apt-get install nvidia-docker2"
    ALL_PASS=false
fi
echo ""

echo "6. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    check_pass "Docker Compose installed: $COMPOSE_VERSION"
elif docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    check_pass "Docker Compose (plugin) installed: $COMPOSE_VERSION"
else
    check_fail "Docker Compose not installed"
    ALL_PASS=false
fi
echo ""

echo "7. Checking X11 configuration..."
if [ -n "$DISPLAY" ]; then
    check_pass "DISPLAY environment variable set: $DISPLAY"
else
    check_warn "DISPLAY not set - you may need to set it for GUI"
    echo "   Run: export DISPLAY=:0"
fi

if [ -d "/tmp/.X11-unix" ]; then
    check_pass "/tmp/.X11-unix directory exists"
else
    check_warn "/tmp/.X11-unix not found - X11 might not be running"
fi
echo ""

echo "8. Testing nvidia-container-runtime..."
if docker info 2>&1 | grep -q "nvidia"; then
    echo "   Running test container..."
    if timeout 10 docker run --rm --runtime nvidia nvcr.io/nvidia/l4t-base:r32.7.1 nvidia-smi &> /dev/null; then
        check_pass "nvidia-container-runtime test passed"
    else
        check_warn "nvidia-container-runtime test failed or timed out"
        echo "   This might be normal if the image needs to be pulled"
    fi
fi
echo ""

echo "========================================"
if [ "$ALL_PASS" = true ]; then
    echo -e "${GREEN}All critical checks passed!${NC}"
    echo ""
    echo "You can now run:"
    echo "  xhost +local:docker"
    echo "  docker compose up"
else
    echo -e "${RED}Some checks failed!${NC}"
    echo ""
    echo "Please fix the issues above before running the container."
    echo "See TROUBLESHOOTING.md for detailed solutions."
fi
echo "========================================"
