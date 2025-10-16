"""
Alternative RL algorithms: PPO and A3C
"""
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
from collections import deque
import os

class PPO_Net(nn.Module):
    """
    Actor-Critic network for PPO
    """
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        # Shared layers
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        
        # Actor head (policy)
        self.actor = nn.Linear(hidden_size, output_size)
        
        # Critic head (value)
        self.critic = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        
        action_probs = F.softmax(self.actor(x), dim=-1)
        state_value = self.critic(x)
        
        return action_probs, state_value
    
    def save(self, file_name='ppo_model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
            
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class PPOAgent:
    """
    Proximal Policy Optimization Agent
    """
    def __init__(self, lr=0.0003, gamma=0.99, eps_clip=0.2, k_epochs=4):
        self.n_games = 0
        self.gamma = gamma
        self.eps_clip = eps_clip
        self.k_epochs = k_epochs
        
        self.model = PPO_Net(11, 256, 3)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        
        # Memory for batch updates
        self.memory = {
            'states': [],
            'actions': [],
            'log_probs': [],
            'rewards': [],
            'is_terminals': []
        }
    
    def get_state(self, game):
        """Get the current game state"""
        return game.get_state()
    
    def get_action(self, state, training=True):
        """Get action using policy network"""
        state_tensor = torch.tensor(state, dtype=torch.float)
        
        with torch.no_grad():
            action_probs, _ = self.model(state_tensor)
        
        if training:
            # Sample from probability distribution
            dist = Categorical(action_probs)
            action_idx = dist.sample()
            log_prob = dist.log_prob(action_idx)
            
            # Store log prob for training
            self.memory['log_probs'].append(log_prob)
        else:
            # Greedy action
            action_idx = torch.argmax(action_probs)
        
        # Convert to one-hot
        action = [0, 0, 0]
        action[action_idx.item()] = 1
        
        return action
    
    def remember(self, state, action, reward, done):
        """Store experience"""
        self.memory['states'].append(state)
        self.memory['actions'].append(action.index(1))  # Store action index
        self.memory['rewards'].append(reward)
        self.memory['is_terminals'].append(done)
    
    def train(self):
        """Train using PPO algorithm"""
        if len(self.memory['states']) == 0:
            return
        
        # Convert lists to tensors
        old_states = torch.tensor(np.array(self.memory['states']), dtype=torch.float)
        old_actions = torch.tensor(self.memory['actions'], dtype=torch.long)
        old_log_probs = torch.stack(self.memory['log_probs'])
        
        # Calculate returns
        returns = []
        discounted_reward = 0
        for reward, is_terminal in zip(reversed(self.memory['rewards']), 
                                       reversed(self.memory['is_terminals'])):
            if is_terminal:
                discounted_reward = 0
            discounted_reward = reward + (self.gamma * discounted_reward)
            returns.insert(0, discounted_reward)
        
        returns = torch.tensor(returns, dtype=torch.float)
        returns = (returns - returns.mean()) / (returns.std() + 1e-7)
        
        # PPO update for k epochs
        for _ in range(self.k_epochs):
            # Get current action probabilities and values
            action_probs, state_values = self.model(old_states)
            state_values = state_values.squeeze()
            
            # Get log probs for taken actions
            dist = Categorical(action_probs)
            new_log_probs = dist.log_prob(old_actions)
            entropy = dist.entropy()
            
            # Calculate ratios
            ratios = torch.exp(new_log_probs - old_log_probs.detach())
            
            # Calculate advantages
            advantages = returns - state_values.detach()
            
            # Calculate surrogate losses
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            
            # Calculate total loss
            actor_loss = -torch.min(surr1, surr2).mean()
            critic_loss = F.mse_loss(state_values, returns)
            entropy_loss = -entropy.mean()
            
            loss = actor_loss + 0.5 * critic_loss + 0.01 * entropy_loss
            
            # Optimize
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
        
        # Clear memory
        self.memory = {
            'states': [],
            'actions': [],
            'log_probs': [],
            'rewards': [],
            'is_terminals': []
        }
    
    def save_model(self, filename='ppo_model.pth'):
        """Save the current model"""
        self.model.save(filename)
    
    def load_model(self, filename='ppo_model.pth'):
        """Load a saved model"""
        model_path = f'./model/{filename}'
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path))
            print(f"Model loaded from {model_path}")
        else:
            print(f"No model found at {model_path}")


class A3CNet(nn.Module):
    """
    Actor-Critic network for A3C (simplified single-thread version)
    """
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        
        # Actor head
        self.actor = nn.Linear(hidden_size, output_size)
        
        # Critic head
        self.critic = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        
        action_probs = F.softmax(self.actor(x), dim=-1)
        state_value = self.critic(x)
        
        return action_probs, state_value
    
    def save(self, file_name='a3c_model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
            
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class A3CAgent:
    """
    Advantage Actor-Critic (A3C) Agent - Simplified single-thread version
    """
    def __init__(self, lr=0.001, gamma=0.99):
        self.n_games = 0
        self.gamma = gamma
        
        self.model = A3CNet(11, 256, 3)
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        
        # Temporary memory for current episode
        self.episode_memory = {
            'states': [],
            'actions': [],
            'rewards': [],
            'log_probs': [],
            'values': []
        }
    
    def get_state(self, game):
        """Get the current game state"""
        return game.get_state()
    
    def get_action(self, state, training=True):
        """Get action using policy network"""
        state_tensor = torch.tensor(state, dtype=torch.float)
        
        action_probs, state_value = self.model(state_tensor)
        
        if training:
            dist = Categorical(action_probs)
            action_idx = dist.sample()
            log_prob = dist.log_prob(action_idx)
            
            # Store for training
            self.episode_memory['log_probs'].append(log_prob)
            self.episode_memory['values'].append(state_value)
        else:
            action_idx = torch.argmax(action_probs)
        
        # Convert to one-hot
        action = [0, 0, 0]
        action[action_idx.item()] = 1
        
        return action
    
    def remember(self, state, action, reward, done):
        """Store experience for current episode"""
        self.episode_memory['states'].append(state)
        self.episode_memory['actions'].append(action.index(1))
        self.episode_memory['rewards'].append(reward)
    
    def train_on_episode(self):
        """Train on completed episode"""
        if len(self.episode_memory['states']) == 0:
            return
        
        # Calculate returns
        returns = []
        R = 0
        for reward in reversed(self.episode_memory['rewards']):
            R = reward + self.gamma * R
            returns.insert(0, R)
        
        returns = torch.tensor(returns, dtype=torch.float)
        
        # Stack tensors
        log_probs = torch.stack(self.episode_memory['log_probs'])
        values = torch.stack(self.episode_memory['values']).squeeze()
        
        # Calculate advantages
        advantages = returns - values.detach()
        
        # Calculate losses
        actor_loss = -(log_probs * advantages).mean()
        critic_loss = advantages.pow(2).mean()
        
        loss = actor_loss + 0.5 * critic_loss
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Clear episode memory
        self.episode_memory = {
            'states': [],
            'actions': [],
            'rewards': [],
            'log_probs': [],
            'values': []
        }
    
    def save_model(self, filename='a3c_model.pth'):
        """Save the current model"""
        self.model.save(filename)
    
    def load_model(self, filename='a3c_model.pth'):
        """Load a saved model"""
        model_path = f'./model/{filename}'
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path))
            print(f"Model loaded from {model_path}")
        else:
            print(f"No model found at {model_path}")
