# Snake Game with Reinforcement Learning

A complete Snake game implementation with both human playable mode and Reinforcement Learning (RL) training capabilities, optimized for Jetson Nano with CUDA support.

## Features

- **Dual Mode System**: 
  - Human Play Mode: Control the snake with arrow keys
  - Training Mode: Watch the AI learn to play automatically
- **Deep Q-Network (DQN)** implementation with PyTorch
- **Real-time Training Visualization**: Watch the AI play and improve live
- **Model Persistence**: Automatic saving and loading of trained models
- **CUDA Acceleration**: Optimized for Jetson Nano GPU

## Quick Start

### Prerequisites

- **For Jetson Nano**: JetPack 4.6.x with CUDA 10.2
- **For Development**: Python 3.6+, PyTorch, PyGame

### Docker Installation (Recommended for Jetson Nano)

1. **Verify your Jetson Nano setup (Recommended)**:
```bash
chmod +x verify_jetson_setup.sh
./verify_jetson_setup.sh
```
This will check if all prerequisites are properly configured.

2. **Allow X11 connections**:
```bash
xhost +local:docker
```

3. **Build and run**:
```bash
docker compose build
docker compose up
```

The container will perform CUDA library checks on startup and provide helpful diagnostics if issues are detected.

### Standard Installation

```bash
# Clone repository
git clone https://github.com/dong881/jetson-nano-project.git
cd jetson-nano-project

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Usage

### Human Play Mode

1. Launch with `python main.py`
2. Use **Arrow Keys** to control the snake
3. Eat apples to grow and score points
4. Avoid walls and self-collision

### Training Mode (RL)

1. Click **"Switch to Training"** button
2. Watch the AI learn to play automatically
3. Model saves automatically on new records
4. Click **"Save Model"** to manually save progress

## Requirements

### Python Package Dependencies

- **pygame 2.1.2**: Game interface (Python 3.6 compatible)
- **PyTorch 1.10**: Deep learning (pre-installed in Docker base image with CUDA 10.2)
- **numpy 1.19.5**: Numerical operations (Python 3.6 compatible)

**Important**: The Docker image uses `nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.10-py3` which includes:
- Python 3.6.9
- PyTorch 1.10 with CUDA 10.2 support
- Pre-configured for Jetson Nano

### System Requirements (Jetson Nano)

- JetPack 4.6.x (includes CUDA 10.2)
- Docker with NVIDIA Container Runtime
- At least 2GB available RAM

## Project Structure

```
jetson-nano-project/
├── main.py                    # Main UI with mode switching
├── snake_game.py              # Game logic (Human & AI modes)
├── agent.py                   # RL Agent implementation
├── model.py                   # Neural network and trainer
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image for Jetson Nano
├── docker-compose.yml         # Docker Compose configuration
├── check_cuda.sh              # CUDA library startup diagnostics
├── verify_jetson_setup.sh     # Pre-deployment verification script
├── README.md                  # Main documentation (this file)
├── QUICKSTART.md              # Quick start guide (EN/中文)
├── TROUBLESHOOTING.md         # Troubleshooting guide
├── DOCKER_FIX_EXPLANATION.md  # Detailed libcudnn.so.8 fix explanation
└── DEPENDENCIES.md            # Dependency compatibility guide
```

## Documentation

- **[README.md](README.md)** (this file) - Main project documentation
- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide in English and Chinese
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Detailed troubleshooting for common issues
- **[DOCKER_FIX_EXPLANATION.md](DOCKER_FIX_EXPLANATION.md)** - Technical explanation of the libcudnn.so.8 fix
- **[DEPENDENCIES.md](DEPENDENCIES.md)** - Package version compatibility and requirements

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions to common issues:
- CUDA library errors (libcurand.so.10, libcudnn.so.8)
- Docker build and runtime issues
- Display and X11 forwarding problems
- Package compatibility issues

For a detailed explanation of the libcudnn.so.8 "file too short" fix, see [DOCKER_FIX_EXPLANATION.md](DOCKER_FIX_EXPLANATION.md).

## Performance

On Jetson Nano:
- Training speed: ~60 FPS
- Inference speed: Real-time (60+ FPS)
- Model size: ~500KB
- Memory usage: ~500MB during training

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.