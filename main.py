"""
Main UI for Snake Game with Human/Training Mode Switch
"""
import pygame
import sys
import os
import threading
import time
from snake_game import SnakeGameAI, SnakeGameHuman, BLOCK_SIZE, Direction, Point
from agent import Agent
import torch

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (64, 64, 64)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_WIDTH = 640
GAME_HEIGHT = 480

# Fonts
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_LARGE = pygame.font.Font(None, 48)


class Button:
    """Simple button class"""
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.color if not self.is_hovered else (min(self.color[0]+30, 255), 
                                                          min(self.color[1]+30, 255), 
                                                          min(self.color[2]+30, 255))
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        text_surface = FONT_SMALL.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
    
    def update_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)


class SnakeGameUI:
    """
    Main UI for Snake Game with mode switching
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake Game - Human Play & RL Training')
        self.clock = pygame.time.Clock()
        
        # Game mode: 'human' or 'training'
        self.mode = 'human'
        self.switching_mode = False
        
        # Games
        self.human_game = None
        self.ai_game = None
        self.agent = None
        
        # Training stats
        self.training_games = 0
        self.training_record = 0
        self.training_running = False
        self.training_thread = None
        
        # UI Elements
        self.mode_button = Button(GAME_WIDTH + 20, 20, 140, 40, "Switch to Training", GREEN, BLACK)
        self.reset_button = Button(GAME_WIDTH + 20, 80, 140, 40, "Reset Game", BLUE, WHITE)
        self.save_button = Button(GAME_WIDTH + 20, 140, 140, 40, "Save Model", GRAY, WHITE)
        
        # High scores
        self.high_score_file = 'high_score.txt'
        self.high_score = self.load_high_score()
        
        self.initialize_game()
        
    def initialize_game(self):
        """Initialize the appropriate game based on mode"""
        if self.mode == 'human':
            self.human_game = SnakeGameHuman(GAME_WIDTH, GAME_HEIGHT)
            self.human_game.high_score = self.high_score
        else:
            self.ai_game = SnakeGameAI(GAME_WIDTH, GAME_HEIGHT)
            self.agent = Agent()
            self.ai_game.high_score = self.high_score
            # Try to load existing model
            self.load_model()
    
    def load_high_score(self):
        """Load high score from file"""
        if os.path.exists(self.high_score_file):
            try:
                with open(self.high_score_file, 'r') as f:
                    return int(f.read().strip())
            except:
                return 0
        return 0
    
    def save_high_score(self):
        """Save high score to file"""
        with open(self.high_score_file, 'w') as f:
            f.write(str(self.high_score))
    
    def load_model(self):
        """Load the trained model if available"""
        model_path = './model/model.pth'
        if os.path.exists(model_path):
            try:
                self.agent.model.load_state_dict(torch.load(model_path))
                print("Model loaded successfully")
            except Exception as e:
                print(f"Error loading model: {e}")
    
    def save_model(self):
        """Save the current model"""
        if self.agent:
            self.agent.save_model()
            print("Model saved successfully")
    
    def switch_mode(self):
        """Switch between human and training mode"""
        self.switching_mode = True
        
        # Save current high score
        if self.mode == 'human' and self.human_game:
            if self.human_game.score > self.high_score:
                self.high_score = self.human_game.score
                self.save_high_score()
        elif self.mode == 'training' and self.ai_game:
            if self.ai_game.score > self.high_score:
                self.high_score = self.ai_game.score
                self.save_high_score()
        
        # Save model if in training mode
        if self.mode == 'training':
            self.save_model()
            self.training_running = False
        
        # Switch mode
        self.mode = 'training' if self.mode == 'human' else 'human'
        
        # Update button text
        if self.mode == 'human':
            self.mode_button.text = "Switch to Training"
            self.mode_button.color = GREEN
        else:
            self.mode_button.text = "Switch to Human"
            self.mode_button.color = RED
        
        # Reinitialize game
        self.initialize_game()
        self.switching_mode = False
    
    def reset_game(self):
        """Reset the current game"""
        if self.mode == 'human' and self.human_game:
            self.human_game.update_high_score()
            if self.human_game.high_score > self.high_score:
                self.high_score = self.human_game.high_score
                self.save_high_score()
            self.human_game.reset()
        elif self.mode == 'training' and self.ai_game:
            self.ai_game.update_high_score()
            if self.ai_game.high_score > self.high_score:
                self.high_score = self.ai_game.high_score
                self.save_high_score()
            self.ai_game.reset()
    
    def draw_stats_panel(self):
        """Draw the statistics panel on the right side"""
        panel_x = GAME_WIDTH
        panel_width = SCREEN_WIDTH - GAME_WIDTH
        
        # Panel background
        pygame.draw.rect(self.screen, DARK_GRAY, (panel_x, 0, panel_width, SCREEN_HEIGHT))
        
        # Mode indicator
        mode_text = f"Mode: {self.mode.upper()}"
        text_surface = FONT_MEDIUM.render(mode_text, True, WHITE)
        self.screen.blit(text_surface, (panel_x + 10, 200))
        
        # Stats
        if self.mode == 'human' and self.human_game:
            score_text = f"Score: {self.human_game.score}"
            high_score_text = f"High: {self.high_score}"
        elif self.mode == 'training' and self.ai_game:
            score_text = f"Score: {self.ai_game.score}"
            high_score_text = f"Record: {self.training_record}"
            games_text = f"Games: {self.training_games}"
            games_surface = FONT_SMALL.render(games_text, True, WHITE)
            self.screen.blit(games_surface, (panel_x + 10, 300))
        
        score_surface = FONT_SMALL.render(score_text, True, WHITE)
        high_surface = FONT_SMALL.render(high_score_text, True, WHITE)
        
        self.screen.blit(score_surface, (panel_x + 10, 250))
        self.screen.blit(high_surface, (panel_x + 10, 275))
        
        # Instructions
        if self.mode == 'human':
            inst_text = "Arrow Keys to Move"
            inst_surface = FONT_SMALL.render(inst_text, True, WHITE)
            self.screen.blit(inst_surface, (panel_x + 10, 400))
        else:
            inst_text = "AI Training..."
            inst_surface = FONT_SMALL.render(inst_text, True, GREEN)
            self.screen.blit(inst_surface, (panel_x + 10, 400))
        
        # Buttons
        self.mode_button.draw(self.screen)
        self.reset_button.draw(self.screen)
        if self.mode == 'training':
            self.save_button.draw(self.screen)
    
    def train_step(self):
        """Execute one training step"""
        if not self.agent or not self.ai_game:
            return
        
        # Get old state
        state_old = self.agent.get_state(self.ai_game)
        
        # Get move
        final_move = self.agent.get_action(state_old)
        
        # Perform move and get new state
        reward, done, score = self.ai_game.play_step(final_move)
        state_new = self.agent.get_state(self.ai_game)
        
        # Train short memory
        self.agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        # Remember
        self.agent.remember(state_old, final_move, reward, state_new, done)
        
        if done:
            # Train long memory (experience replay)
            self.ai_game.reset()
            self.agent.n_games += 1
            self.agent.train_long_memory()
            
            self.training_games = self.agent.n_games
            
            if score > self.training_record:
                self.training_record = score
                self.agent.save_model()
            
            if score > self.high_score:
                self.high_score = score
                self.save_high_score()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.mode_button.is_clicked(pos):
                        self.switch_mode()
                    elif self.reset_button.is_clicked(pos):
                        self.reset_game()
                    elif self.mode == 'training' and self.save_button.is_clicked(pos):
                        self.save_model()
                
                if event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    self.mode_button.update_hover(pos)
                    self.reset_button.update_hover(pos)
                    if self.mode == 'training':
                        self.save_button.update_hover(pos)
            
            # Clear screen
            self.screen.fill(BLACK)
            
            # Game logic
            if self.mode == 'human' and self.human_game:
                game_over, score = self.human_game.play_step()
                if game_over:
                    self.human_game.update_high_score()
                    if self.human_game.high_score > self.high_score:
                        self.high_score = self.human_game.high_score
                        self.save_high_score()
                    # Show game over message
                    time.sleep(1)
                    self.human_game.reset()
                
                # Copy game display to main screen
                self.screen.blit(self.human_game.display, (0, 0))
                
            elif self.mode == 'training' and self.ai_game and self.agent:
                # Run training step
                self.train_step()
                
                # Copy game display to main screen
                self.screen.blit(self.ai_game.display, (0, 0))
            
            # Draw stats panel
            self.draw_stats_panel()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        # Cleanup
        if self.mode == 'training':
            self.save_model()
        self.save_high_score()
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    game_ui = SnakeGameUI()
    game_ui.run()
