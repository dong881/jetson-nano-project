"""
Snake Game with API interface for RL agents
"""
import pygame
import random
import numpy as np
from enum import Enum
from collections import namedtuple
import time

pygame.init()
font = pygame.font.Font(None, 36)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# RGB colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

BLOCK_SIZE = 20
SPEED = 15

class SnakeGameAI:
    """
    Snake game with both human playable mode and API for RL agents
    """
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # Display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake Game - RL Training')
        self.clock = pygame.time.Clock()
        self.reset()
        self.high_score = 0
        
    def reset(self):
        """Reset the game to initial state"""
        # Init game state
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        
    def _place_food(self):
        """Place food randomly on the board"""
        x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
            
    def play_step(self, action):
        """
        Execute one game step
        Args:
            action: [straight, right, left] - one-hot encoded action
        Returns:
            reward: reward for the action
            game_over: boolean indicating if game is over
            score: current score
        """
        self.frame_iteration += 1
        
        # 1. Collect user input (for human mode)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        # 2. Move
        self._move(action)  # Update the head
        self.snake.insert(0, self.head)
        
        # 3. Check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score
            
        # 4. Place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. Update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        
        # 6. Return game over and score
        return reward, game_over, self.score
    
    def is_collision(self, pt=None):
        """Check if there's a collision with walls or self"""
        if pt is None:
            pt = self.head
        # Hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # Hits itself
        if pt in self.snake[1:]:
            return True
        
        return False
        
    def _update_ui(self):
        """Update the game display"""
        self.display.fill(BLACK)
        
        # Draw snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        # Draw food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw score
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        
        # Draw high score
        text = font.render("High Score: " + str(self.high_score), True, WHITE)
        self.display.blit(text, [0, 30])
        
        pygame.display.flip()
        
    def _move(self, action):
        """
        Move the snake based on action
        Args:
            action: [straight, right, left]
        """
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # No change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # Right turn
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # Left turn
            
        self.direction = new_dir
        
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
    
    def get_state(self):
        """
        Get current game state for RL agent
        Returns:
            numpy array with 11 values representing the state
        """
        head = self.snake[0]
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)
        
        dir_l = self.direction == Direction.LEFT
        dir_r = self.direction == Direction.RIGHT
        dir_u = self.direction == Direction.UP
        dir_d = self.direction == Direction.DOWN
        
        state = [
            # Danger straight
            (dir_r and self.is_collision(point_r)) or 
            (dir_l and self.is_collision(point_l)) or 
            (dir_u and self.is_collision(point_u)) or 
            (dir_d and self.is_collision(point_d)),
            
            # Danger right
            (dir_u and self.is_collision(point_r)) or 
            (dir_d and self.is_collision(point_l)) or 
            (dir_l and self.is_collision(point_u)) or 
            (dir_r and self.is_collision(point_d)),
            
            # Danger left
            (dir_d and self.is_collision(point_r)) or 
            (dir_u and self.is_collision(point_l)) or 
            (dir_r and self.is_collision(point_u)) or 
            (dir_l and self.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location
            self.food.x < self.head.x,  # food left
            self.food.x > self.head.x,  # food right
            self.food.y < self.head.y,  # food up
            self.food.y > self.head.y   # food down
        ]
        
        return np.array(state, dtype=int)
    
    def update_high_score(self):
        """Update high score if current score is higher"""
        if self.score > self.high_score:
            self.high_score = self.score


class SnakeGameHuman:
    """
    Snake game for human players with keyboard controls
    """
    
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # Display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake Game - Human Play')
        self.clock = pygame.time.Clock()
        self.reset()
        self.high_score = 0
        
    def reset(self):
        """Reset the game to initial state"""
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0
        self.food = None
        self._place_food()
        
    def _place_food(self):
        """Place food randomly on the board"""
        x = random.randint(0, (self.w-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
            
    def play_step(self):
        """
        Execute one game step for human player
        Returns:
            game_over: boolean indicating if game is over
            score: current score
        """
        # 1. Collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
                    
        # 2. Move
        self._move(self.direction)
        self.snake.insert(0, self.head)
        
        # 3. Check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. Place new food or just move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. Update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        
        # 6. Return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        """Check if there's a collision with walls or self"""
        # Hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        # Hits itself
        if self.head in self.snake[1:]:
            return True
        return False
        
    def _update_ui(self):
        """Update the game display"""
        self.display.fill(BLACK)
        
        # Draw snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
            
        # Draw food
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        # Draw score
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        
        # Draw high score
        text = font.render("High Score: " + str(self.high_score), True, WHITE)
        self.display.blit(text, [0, 30])
        
        pygame.display.flip()
        
    def _move(self, direction):
        """Move the snake in the given direction"""
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
    
    def update_high_score(self):
        """Update high score if current score is higher"""
        if self.score > self.high_score:
            self.high_score = self.score


if __name__ == '__main__':
    game = SnakeGameHuman()
    
    # Game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over:
            game.update_high_score()
            print(f'Game Over! Score: {score}, High Score: {game.high_score}')
            game.reset()
