"""
Deep Q-Learning Agent for Snake Game
"""
import torch
import random
import numpy as np
import os
from collections import deque
from snake_game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer

# Check CUDA availability and handle cuDNN version issues
def check_cuda_availability():
    """Check if CUDA is available and working properly"""
    try:
        if torch.cuda.is_available():
            # Try to create a simple tensor to test CUDA functionality
            test_tensor = torch.tensor([1.0]).cuda()
            return True
    except Exception as e:
        print(f"CUDA test failed: {e}")
        print("Falling back to CPU mode")
        return False
    return False

# Set device based on CUDA availability
DEVICE = torch.device('cuda' if check_cuda_availability() else 'cpu')
print(f"Using device: {DEVICE}")

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    """
    Reinforcement Learning Agent using Deep Q-Learning
    """
    
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # Randomness
        self.gamma = 0.9  # Discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        
    def get_state(self, game):
        """Get the current game state"""
        return game.get_state()
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in memory"""
        self.memory.append((state, action, reward, next_state, done))  # popleft if MAX_MEMORY is reached
    
    def train_long_memory(self):
        """Train on a batch of experiences from memory"""
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)  # list of tuples
        else:
            mini_sample = self.memory
            
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    
    def train_short_memory(self, state, action, reward, next_state, done):
        """Train on a single experience"""
        self.trainer.train_step(state, action, reward, next_state, done)
    
    def get_action(self, state):
        """
        Get action based on current state
        Uses epsilon-greedy strategy for exploration vs exploitation
        """
        # Random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float).to(DEVICE)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            
        return final_move
    
    def save_model(self, filename='model.pth'):
        """Save the current model"""
        self.model.save(filename)
        
    def load_model(self, filename='model.pth'):
        """Load a saved model"""
        model_path = f'./model/{filename}'
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=DEVICE))
            print(f"Model loaded from {model_path}")
        else:
            print(f"No model found at {model_path}")


def train():
    """Training loop for the agent"""
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    
    while True:
        # Get old state
        state_old = agent.get_state(game)
        
        # Get move
        final_move = agent.get_action(state_old)
        
        # Perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)
        
        # Train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        # Remember
        agent.remember(state_old, final_move, reward, state_new, done)
        
        if done:
            # Train long memory (experience replay), plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            
            if score > record:
                record = score
                agent.save_model()
                
            print('Game', agent.n_games, 'Score', score, 'Record:', record)
            
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)


if __name__ == '__main__':
    train()
