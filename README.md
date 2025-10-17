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

1. **Allow X11 connections**:
```bash
xhost +local:docker
```

2. **Build and run**:
```bash
docker compose build
docker compose up
```

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
├── main.py              # Main UI with mode switching
├── snake_game.py        # Game logic (Human & AI modes)
├── agent.py             # RL Agent implementation
├── model.py             # Neural network and trainer
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image for Jetson Nano
├── docker-compose.yml   # Docker Compose configuration
├── QUICKSTART.md        # Quick start guide (EN/中文)
└── TROUBLESHOOTING.md   # Troubleshooting guide
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions to common issues:
- CUDA library errors (libcurand.so.10)
- Docker build and runtime issues
- Display and X11 forwarding problems
- Package compatibility issues

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