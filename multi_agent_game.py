"""
Multi-agent training system for Snake game
Allows multiple agents to train simultaneously on the same board
"""
import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple
from snake_game import Direction, Point, BLOCK_SIZE

class MultiAgentSnakeGame:
    """
    Snake game supporting multiple agents training simultaneously
    Each snake is independent and can collide with walls, itself, or other snakes
    """
    
    def __init__(self, w=640, h=480, num_agents=2):
        self.w = w
        self.h = h
        self.num_agents = num_agents
        
        # Display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption(f'Snake Game - Multi-Agent Training ({num_agents} agents)')
        self.clock = pygame.time.Clock()
        
        # Colors for different agents
        self.agent_colors = [
            ((0, 0, 255), (0, 100, 255)),      # Blue
            ((0, 255, 0), (100, 255, 100)),    # Green
            ((255, 165, 0), (255, 200, 100)),  # Orange
            ((255, 0, 255), (255, 100, 255))   # Magenta
        ]
        
        self.reset()
        
    def reset(self):
        """Reset all agents and game state"""
        self.frame_iteration = 0
        
        # Initialize each agent
        self.agents_data = []
        
        # Pre-defined safe starting positions for up to 4 agents
        safe_positions = [
            (BLOCK_SIZE * 5, BLOCK_SIZE * 5, Direction.RIGHT),    # Top-left
            (self.w - BLOCK_SIZE * 8, self.h - BLOCK_SIZE * 5, Direction.LEFT),  # Bottom-right
            (self.w - BLOCK_SIZE * 8, BLOCK_SIZE * 5, Direction.DOWN),   # Top-right
            (BLOCK_SIZE * 5, self.h - BLOCK_SIZE * 5, Direction.UP)      # Bottom-left
        ]
        
        for i in range(self.num_agents):
            if i < len(safe_positions):
                start_x, start_y, direction = safe_positions[i]
            else:
                # Random position for additional agents
                start_x = random.randint(5, (self.w // BLOCK_SIZE) - 5) * BLOCK_SIZE
                start_y = random.randint(5, (self.h // BLOCK_SIZE) - 5) * BLOCK_SIZE
                direction = random.choice([Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN])
            
            head = Point(start_x, start_y)
            
            # Create snake with 3 segments
            if direction == Direction.RIGHT:
                snake = [head, Point(head.x-BLOCK_SIZE, head.y), Point(head.x-2*BLOCK_SIZE, head.y)]
            elif direction == Direction.LEFT:
                snake = [head, Point(head.x+BLOCK_SIZE, head.y), Point(head.x+2*BLOCK_SIZE, head.y)]
            elif direction == Direction.UP:
                snake = [head, Point(head.x, head.y+BLOCK_SIZE), Point(head.x, head.y+2*BLOCK_SIZE)]
            else:  # DOWN
                snake = [head, Point(head.x, head.y-BLOCK_SIZE), Point(head.x, head.y-2*BLOCK_SIZE)]
            
            agent_data = {
                'snake': snake,
                'direction': direction,
                'score': 0,
                'alive': True,
                'food': None
            }
            self.agents_data.append(agent_data)
        
        # Place food for each agent
        for i in range(self.num_agents):
            self._place_food(i)
    
    def _place_food(self, agent_idx):
        """Place food for specific agent"""
        while True:
            x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
            y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
            food = Point(x, y)
            
            # Check if food overlaps with any snake
            valid = True
            for agent_data in self.agents_data:
                if food in agent_data['snake']:
                    valid = False
                    break
            
            if valid:
                self.agents_data[agent_idx]['food'] = food
                break
    
    def play_step(self, actions):
        """
        Execute one game step for all agents
        Args:
            actions: list of actions for each agent [straight, right, left]
        Returns:
            rewards: list of rewards for each agent
            dones: list of booleans indicating if each agent is done
            scores: list of scores for each agent
        """
        self.frame_iteration += 1
        
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        rewards = []
        dones = []
        scores = []
        
        # Move each agent and check outcomes
        for i, (agent_data, action) in enumerate(zip(self.agents_data, actions)):
            if not agent_data['alive']:
                rewards.append(0)
                dones.append(True)
                scores.append(agent_data['score'])
                continue
            
            # Move agent
            self._move(i, action)
            agent_data['snake'].insert(0, agent_data['snake'][0])  # Insert new head
            
            # Check collision
            reward = 0
            done = False
            
            if self._is_collision(i) or self.frame_iteration > 100 * len(agent_data['snake']) * self.num_agents:
                agent_data['alive'] = False
                reward = -10
                done = True
            # Check if ate food
            elif agent_data['snake'][0] == agent_data['food']:
                agent_data['score'] += 1
                reward = 10
                self._place_food(i)
            else:
                # Remove tail if didn't eat
                agent_data['snake'].pop()
            
            rewards.append(reward)
            dones.append(done)
            scores.append(agent_data['score'])
        
        # Update UI
        self._update_ui()
        self.clock.tick(20)  # Slower for multi-agent visualization
        
        return rewards, dones, scores
    
    def _is_collision(self, agent_idx):
        """Check if agent has collision"""
        agent_data = self.agents_data[agent_idx]
        head = agent_data['snake'][0]
        
        # Check boundary collision
        if head.x > self.w - BLOCK_SIZE or head.x < 0 or head.y > self.h - BLOCK_SIZE or head.y < 0:
            return True
        
        # Check self collision
        if head in agent_data['snake'][1:]:
            return True
        
        # Check collision with other snakes
        for i, other_data in enumerate(self.agents_data):
            if i != agent_idx and other_data['alive']:
                if head in other_data['snake']:
                    return True
        
        return False
    
    def _move(self, agent_idx, action):
        """Move the agent based on action"""
        agent_data = self.agents_data[agent_idx]
        
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(agent_data['direction'])
        
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # No change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # Right turn
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # Left turn
        
        agent_data['direction'] = new_dir
        
        head = agent_data['snake'][0]
        x = head.x
        y = head.y
        
        if new_dir == Direction.RIGHT:
            x += BLOCK_SIZE
        elif new_dir == Direction.LEFT:
            x -= BLOCK_SIZE
        elif new_dir == Direction.DOWN:
            y += BLOCK_SIZE
        elif new_dir == Direction.UP:
            y -= BLOCK_SIZE
        
        agent_data['snake'][0] = Point(x, y)
    
    def get_state(self, agent_idx):
        """Get state for specific agent"""
        agent_data = self.agents_data[agent_idx]
        head = agent_data['snake'][0]
        
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)
        
        dir_l = agent_data['direction'] == Direction.LEFT
        dir_r = agent_data['direction'] == Direction.RIGHT
        dir_u = agent_data['direction'] == Direction.UP
        dir_d = agent_data['direction'] == Direction.DOWN
        
        # Create temporary agent data to check collision
        state = [
            # Danger straight
            (dir_r and self._would_collide(agent_idx, point_r)) or 
            (dir_l and self._would_collide(agent_idx, point_l)) or 
            (dir_u and self._would_collide(agent_idx, point_u)) or 
            (dir_d and self._would_collide(agent_idx, point_d)),
            
            # Danger right
            (dir_u and self._would_collide(agent_idx, point_r)) or 
            (dir_d and self._would_collide(agent_idx, point_l)) or 
            (dir_l and self._would_collide(agent_idx, point_u)) or 
            (dir_r and self._would_collide(agent_idx, point_d)),
            
            # Danger left
            (dir_d and self._would_collide(agent_idx, point_r)) or 
            (dir_u and self._would_collide(agent_idx, point_l)) or 
            (dir_r and self._would_collide(agent_idx, point_u)) or 
            (dir_l and self._would_collide(agent_idx, point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location
            agent_data['food'].x < head.x,  # food left
            agent_data['food'].x > head.x,  # food right
            agent_data['food'].y < head.y,  # food up
            agent_data['food'].y > head.y   # food down
        ]
        
        return np.array(state, dtype=int)
    
    def _would_collide(self, agent_idx, point):
        """Check if point would cause collision"""
        # Check boundary
        if point.x > self.w - BLOCK_SIZE or point.x < 0 or point.y > self.h - BLOCK_SIZE or point.y < 0:
            return True
        
        # Check self collision
        if point in self.agents_data[agent_idx]['snake'][1:]:
            return True
        
        # Check collision with other snakes
        for i, other_data in enumerate(self.agents_data):
            if i != agent_idx and other_data['alive']:
                if point in other_data['snake']:
                    return True
        
        return False
    
    def _update_ui(self):
        """Update the game display"""
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (200, 0, 0)
        
        self.display.fill(BLACK)
        
        # Draw all snakes
        for i, agent_data in enumerate(self.agents_data):
            if agent_data['alive']:
                color1, color2 = self.agent_colors[i % len(self.agent_colors)]
                
                for pt in agent_data['snake']:
                    pygame.draw.rect(self.display, color1, 
                                   pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.display, color2, 
                                   pygame.Rect(pt.x+4, pt.y+4, 12, 12))
                
                # Draw food
                pygame.draw.rect(self.display, RED, 
                               pygame.Rect(agent_data['food'].x, agent_data['food'].y, 
                                         BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw scores
        font = pygame.font.Font(None, 24)
        y_offset = 10
        for i, agent_data in enumerate(self.agents_data):
            color = self.agent_colors[i % len(self.agent_colors)][0]
            status = "Alive" if agent_data['alive'] else "Dead"
            text = font.render(f"Agent {i+1}: {agent_data['score']} ({status})", True, color)
            self.display.blit(text, [10, y_offset])
            y_offset += 25
        
        pygame.display.flip()
    
    def all_done(self):
        """Check if all agents are done"""
        return all(not agent_data['alive'] for agent_data in self.agents_data)
    
    def get_alive_count(self):
        """Get number of alive agents"""
        return sum(1 for agent_data in self.agents_data if agent_data['alive'])
