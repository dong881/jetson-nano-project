# Enhanced Features Guide

This guide explains how to use the new features added to the Snake Game with RL.

## Quick Start

Run the enhanced game:
```bash
python main.py
```

## New Features Overview

### 1. Multiple Difficulty Levels

The game now supports three difficulty levels:

- **Easy**: Slower speed (10 FPS), larger board (800x600)
- **Medium**: Default speed (15 FPS), standard board (640x480)
- **Hard**: Faster speed (25 FPS), smaller board (480x360)

**How to change difficulty:**
- Click the "Difficulty" button in the UI
- Press `D` key to cycle through levels
- Difficulty applies to both Human and Training modes

### 2. Advanced RL Algorithms

Choose from three reinforcement learning algorithms:

- **DQN** (Deep Q-Network): The original algorithm with experience replay
- **PPO** (Proximal Policy Optimization): Policy gradient method with clipped objective
- **A3C** (Advantage Actor-Critic): Actor-critic method for stable learning

**How to switch algorithms:**
- Click the "Algorithm" button in the UI
- Press `A` key to cycle through algorithms
- Each algorithm has its own saved model

### 3. Leaderboard System

Track the top 10 scores across all sessions:

**How to use:**
- Click "Toggle Leaderboard" button or press `L` key
- Leaderboard shows:
  - Rank (1-10)
  - Score
  - Mode (human/DQN/PPO/A3C)
  - Difficulty level
- Scores are automatically saved to `leaderboard.json`
- High scores are added automatically when games end

### 4. Multi-Agent Training

Train multiple AI agents simultaneously:

**How to use:**
```bash
# Train 2 agents for 10 episodes
python multi_agent_demo.py 2 10

# Train 4 agents for 20 episodes
python multi_agent_demo.py 4 20
```

**Features:**
- Agents compete for food on the same board
- Agents can collide with each other
- Each agent has its own snake and food
- Different colored snakes for each agent
- Training statistics displayed in real-time

### 5. Custom Reward Shaping

Four reward profiles are available:

**Default:**
- Food: +10
- Death: -10
- Step: 0
- Closer to food: 0

**Encouraging:**
- Food: +20
- Death: -5
- Step: 0
- Closer to food: +0.1

**Strict:**
- Food: +10
- Death: -20
- Step: -0.01
- Closer to food: 0

**Shaped:**
- Food: +10
- Death: -10
- Step: 0
- Closer to food: +0.5

**How to customize:**
Edit `config.py` to create your own reward profile:
```python
REWARD_PARAMS['my_profile'] = {
    'food_reward': 15,
    'death_penalty': -15,
    'step_penalty': -0.02,
    'closer_to_food_reward': 0.3,
    'description': 'My custom reward profile'
}

# Update the default profile
DEFAULT_REWARD_PROFILE = 'my_profile'
```

### 6. Policy Visualization

See what the AI is thinking in real-time:

**How to use:**
- Available only in Training mode
- Click "Toggle Policy Viz" or press `V` key
- Shows:
  - Q-values for each action (Straight, Right, Left)
  - Current selected action (highlighted)
  - State information (dangers, food direction)
  - Exploration rate

**Understanding the display:**
- Higher Q-value = AI thinks action is better
- Yellow highlight = Action AI will take
- Green bars = Positive Q-values
- Red bars = Negative Q-values

## Keyboard Shortcuts

- `L` - Toggle leaderboard display
- `D` - Cycle through difficulty levels
- `A` - Cycle through RL algorithms
- `V` - Toggle policy visualization
- Arrow Keys - Control snake in Human mode

## Tips for Training

1. **Start with Easy difficulty** to let agents learn basics
2. **Use DQN first** as it's the most stable algorithm
3. **Try shaped rewards** to speed up early learning
4. **Watch policy visualization** to understand what AI learned
5. **Check leaderboard** to compare algorithm performance

## File Storage

The system creates these files:

- `leaderboard.json` - Top scores database
- `high_score.txt` - Overall high score
- `model/model.pth` - DQN model weights
- `model/ppo_model.pth` - PPO model weights
- `model/a3c_model.pth` - A3C model weights
- `model/multi_agent_*.pth` - Multi-agent model weights

## Advanced Usage

### Comparing Algorithms

1. Train DQN on Medium difficulty for 100 games
2. Save the model
3. Switch to PPO and train for 100 games
4. Switch to A3C and train for 100 games
5. Check leaderboard to compare performance

### Custom Training Loop

You can create custom training scripts using the new classes:

```python
from snake_game import SnakeGameAI
from advanced_agents import PPOAgent

# Create game with custom settings
game = SnakeGameAI(640, 480, 
                   difficulty='hard',
                   reward_profile='shaped')

# Create PPO agent
agent = PPOAgent(lr=0.0005)

# Training loop
for episode in range(100):
    game.reset()
    while True:
        state = agent.get_state(game)
        action = agent.get_action(state)
        reward, done, score = game.play_step(action)
        
        agent.remember(state, action, reward, done)
        
        if done:
            agent.train()
            break
```

## Troubleshooting

**Q: Leaderboard not showing scores?**
A: Make sure games are ending properly and scores are > 0

**Q: Policy visualization not appearing?**
A: Only works in Training mode. Switch to Training mode first.

**Q: Multi-agent training crashes?**
A: Try with 2 agents first. Ensure pygame display is working.

**Q: Algorithm performance differs?**
A: Each algorithm has different learning characteristics. PPO and A3C may need more episodes.

## Performance Notes

- DQN: Fastest training, most stable
- PPO: Slower, but better final performance
- A3C: Medium speed, good for continuous learning
- Multi-agent: Much slower due to multiple agents

Adjust game speed in config.py if training is too slow.
