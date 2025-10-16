# Snake Game with Reinforcement Learning

A complete Snake game implementation with both human playable mode and Reinforcement Learning (RL) training capabilities, optimized for Jetson Nano with CUDA support.

## Features

### Game Features
- **Complete UI with PyGame**: Full graphical interface with smooth gameplay
- **Dual Mode System**: 
  - Human Play Mode: Control the snake with arrow keys
  - Training Mode: Watch the AI learn to play automatically
- **Game Rules**:
  - Boundary walls that end the game on collision
  - Apple spawning system - snake grows by 1 segment per apple
  - Score tracking with persistent high score
  - Self-collision detection for game over
- **Score System**:
  - Current score display
  - High score tracking across sessions
  - Training statistics (games played, record score)

### API Interface for RL
- **State API**: Get 11-dimensional state vector representing game state
- **Action API**: Perform actions (straight, turn right, turn left)
- **Reset API**: Reset game to initial state
- **Reward System**: +10 for food, -10 for death, 0 otherwise

### Reinforcement Learning
- **Deep Q-Network (DQN)** implementation
- **Experience Replay Buffer**: Stores up to 100,000 experiences
- **Neural Network Architecture**:
  - Input: 11 state features
  - Hidden: 256 neurons (2 layers)
  - Output: 3 actions
- **Training Features**:
  - Epsilon-greedy exploration strategy
  - Batch training with replay memory
  - Automatic model saving on new records
  - Model persistence across sessions
- **Real-time Training Visualization**: Watch the AI play and improve live

### UI Features
- **Mode Switch Button**: Toggle between Human/Training modes
- **Progress Saving**: Automatic model save when switching modes
- **Statistics Panel**: 
  - Current score
  - High score / Record
  - Games played (in training mode)
  - Mode indicator
- **Reset Button**: Start a new game
- **Save Model Button**: Manually save training progress

## Requirements

- Python 3.7+
- PyGame 2.5.2
- PyTorch 2.0.1
- NumPy 1.24.3
- CUDA-capable device (for Jetson Nano)

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/dong881/jetson-nano-project.git
cd jetson-nano-project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the game:
```bash
python main.py
```

### Docker Installation (Recommended for Jetson Nano)

This project includes a Dockerfile optimized for Jetson Nano with CUDA support. The docker-compose.yml is configured to:
- Use NVIDIA Container Runtime for GPU access
- Mount CUDA libraries from the host system to avoid library conflicts
- Mount aarch64 libraries which may contain CUDA files on Jetson Nano
- Set proper environment variables for CUDA library paths

1. **Prerequisites**:
   - Jetson Nano with JetPack installed (includes CUDA)
   - Docker installed
   - NVIDIA Container Runtime installed

2. **Allow X11 connections** (for display):
```bash
xhost +local:docker
```

3. **Build and run with Docker Compose**:
```bash
# Build the Docker image
docker compose build

# Run the container
docker compose up
```

**To rebuild and replace an old image** (recommended to save disk space):
```bash
# Remove old containers and images
docker compose down
docker compose build --no-cache

# Run the new container
docker compose up
```

**To clean up unused Docker images** (saves disk space):
```bash
# Remove all stopped containers and unused images
docker system prune -a

# Or specifically remove old images of this project
docker rmi $(docker images -q snake-game)
```

Or build and run manually:
```bash
# Build the image
docker build -t snake-rl .

# Run the container with CUDA support
docker run --runtime nvidia \
  -e DISPLAY=$DISPLAY \
  -e LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH} \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v /usr/local/cuda:/usr/local/cuda:ro \
  -v /usr/lib/aarch64-linux-gnu:/usr/lib/aarch64-linux-gnu:ro \
  -v $(pwd)/model:/app/model \
  -v $(pwd)/high_score.txt:/app/high_score.txt \
  --network host \
  snake-rl
```

## Usage

### Human Play Mode

1. Launch the application: `python main.py`
2. The game starts in Human Play mode by default
3. Use **Arrow Keys** to control the snake:
   - ↑ Up
   - ↓ Down
   - ← Left
   - → Right
4. Try to eat the red apples and avoid hitting walls or yourself
5. Your score increases by 1 for each apple eaten
6. Game resets automatically on game over

### Training Mode (RL)

1. Click the **"Switch to Training"** button
2. The AI will start training automatically
3. Watch the snake learn to play in real-time
4. Training statistics are displayed in the right panel:
   - Current score
   - Record score
   - Number of games played
5. The model is automatically saved when it achieves a new record
6. Click **"Save Model"** to manually save progress
7. Switch back to Human mode anytime (progress is saved)

### API Usage for Custom RL Agents

```python
from snake_game import SnakeGameAI
from agent import Agent

# Initialize game and agent
game = SnakeGameAI()
agent = Agent()

# Training loop
while True:
    # Get current state
    state = agent.get_state(game)
    
    # Get action from agent
    action = agent.get_action(state)
    
    # Perform action
    reward, game_over, score = game.play_step(action)
    
    # Train agent
    agent.train_short_memory(state, action, reward, next_state, game_over)
    
    if game_over:
        game.reset()
        agent.train_long_memory()
```

## Project Structure

```
jetson-nano-project/
├── main.py              # Main UI with mode switching
├── snake_game.py        # Game logic (Human & AI modes)
├── agent.py             # RL Agent implementation
├── model.py             # Neural network and trainer
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker image for Jetson Nano
├── docker-compose.yml  # Docker Compose configuration
├── model/              # Saved models directory (created automatically)
└── high_score.txt      # Persistent high score (created automatically)
```

## Game State Representation

The RL agent receives an 11-dimensional state vector:
1. Danger straight ahead (boolean)
2. Danger to the right (boolean)
3. Danger to the left (boolean)
4. Moving left (boolean)
5. Moving right (boolean)
6. Moving up (boolean)
7. Moving down (boolean)
8. Food is to the left (boolean)
9. Food is to the right (boolean)
10. Food is above (boolean)
11. Food is below (boolean)

## Action Space

The agent can perform 3 actions:
- `[1, 0, 0]`: Continue straight
- `[0, 1, 0]`: Turn right
- `[0, 0, 1]`: Turn left

## Training Details

### Hyperparameters
- Learning Rate: 0.001
- Gamma (Discount Factor): 0.9
- Epsilon (Initial): 80 - n_games
- Batch Size: 1000
- Memory Size: 100,000
- Hidden Layer Size: 256

### Reward System
- +10: Eating an apple
- -10: Game over (collision)
- 0: Normal move

### Training Strategy
- **Epsilon-Greedy**: Balances exploration vs exploitation
- **Experience Replay**: Learns from past experiences
- **Target Network**: Stabilizes learning
- **Automatic Checkpointing**: Saves best models

## Jetson Nano Optimization

The project is optimized for Jetson Nano with:
- CUDA-accelerated PyTorch operations
- Efficient neural network architecture
- Docker image based on NVIDIA L4T PyTorch
- GPU memory management
- Real-time inference capabilities

## Troubleshooting

### CUDA Library Error (libcurand.so.10)
If you encounter an error like:
```
OSError: libcurand.so.10: cannot open shared object file: No such file or directory
```

This error occurs when the Docker container cannot find CUDA libraries from the host system. The issue has been fixed by:

1. **Mounting CUDA libraries from host**: The `docker-compose.yml` now includes a volume mount for `/usr/local/cuda` directory
2. **Setting LD_LIBRARY_PATH**: The environment variable `LD_LIBRARY_PATH` is set to include CUDA library paths
3. **Preserving essential CUDA libraries**: The Dockerfile preserves CUDA runtime libraries (libcudnn, libcurand, libcublas, etc.) that PyTorch requires

**Solution steps:**

1. **Verify CUDA is installed on your Jetson Nano** (comes with JetPack):
```bash
ls /usr/local/cuda/lib64/libcurand.so.10
```

2. **Ensure you're using the latest docker-compose.yml** with CUDA volume mounts:
```yaml
volumes:
  - /usr/local/cuda:/usr/local/cuda:ro
  - /usr/lib/aarch64-linux-gnu:/usr/lib/aarch64-linux-gnu:ro
environment:
  - LD_LIBRARY_PATH=/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
```

The `/usr/lib/aarch64-linux-gnu` mount is important for Jetson Nano as some CUDA libraries may be located there.

3. **Rebuild without cache**:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

4. **Verify NVIDIA Container Runtime is properly installed**:
```bash
# Check if nvidia runtime is available
docker info | grep -i runtime

# Test NVIDIA runtime
docker run --rm --runtime nvidia nvcr.io/nvidia/l4t-base:r32.7.1 nvidia-smi
```

If the issue persists, ensure that:
- JetPack is fully installed on your Jetson Nano
- CUDA version matches the PyTorch version in the base image (CUDA 10.2 for L4T PyTorch r32.7.1)
- The host CUDA libraries are accessible and not corrupted

### Docker Build GPG Key Error
If you encounter a GPG key verification error during Docker build:
```
E: The repository 'https://apt.kitware.com/ubuntu bionic InRelease' is not signed.
```

This has been fixed in the latest Dockerfile by comprehensively removing all Kitware repository references. If you still encounter this issue:

1. Make sure you're using the latest version of the Dockerfile
2. Try rebuilding without cache:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

### Display Issues with Docker
If you get display errors:
```bash
xhost +local:docker
export DISPLAY=:0
```

### NVIDIA Docker Runtime Library Conflict
If you encounter an error like:
```
nvidia-container-cli: mount error: file creation failed: /var/lib/docker/overlay2/.../merged/usr/lib/libvisionworks.so: file exists
```

This issue has been fixed in the latest Dockerfile. The error occurs when the NVIDIA container runtime tries to mount libraries that already exist in the container image. The fix removes conflicting NVIDIA libraries during the build process, allowing the runtime to mount fresh copies from the host. **Note:** This is safe because the nvidia-container-runtime will provide these libraries from the host system at runtime, ensuring full GPU functionality is maintained.

If you still encounter this issue:
1. Make sure you're using the latest version of the Dockerfile
2. Rebuild without cache:
```bash
docker compose down
docker compose build --no-cache
docker compose up
```

### CUDA Not Available
Check NVIDIA runtime:
```bash
docker run --runtime nvidia nvidia/cuda:11.0-base nvidia-smi
```

### PyGame Display Error
For headless systems, you might need to set up a virtual display:
```bash
sudo apt-get install xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

## Performance

- Training speed: ~60 FPS on Jetson Nano
- Inference speed: Real-time (60+ FPS)
- Model size: ~500KB
- Memory usage: ~500MB during training

## Future Enhancements

- [ ] Multiple difficulty levels
- [ ] Different RL algorithms (PPO, A3C)
- [ ] Leaderboard system
- [ ] Multi-agent training
- [ ] Custom reward shaping
- [ ] Visualization of learned policy

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- PyGame community for the game framework
- PyTorch team for the deep learning framework
- NVIDIA for Jetson Nano support