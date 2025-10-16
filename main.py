"""
Main UI for Snake Game with Human/Training Mode Switch
Enhanced with multiple features: difficulty levels, leaderboard, 
policy visualization, and multiple RL algorithms
"""
import pygame
import sys
import os
import threading
import time
from snake_game import SnakeGameAI, SnakeGameHuman, BLOCK_SIZE, Direction, Point
from agent import Agent
from advanced_agents import PPOAgent, A3CAgent
from leaderboard import Leaderboard
from policy_visualizer import PolicyVisualizer
from config import DIFFICULTY_LEVELS, REWARD_PARAMS, DEFAULT_DIFFICULTY, DEFAULT_REWARD_PROFILE
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
SCREEN_WIDTH = 1000  # Increased to accommodate more UI elements
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
    Main UI for Snake Game with mode switching and enhanced features
    """
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Snake Game - Human Play & RL Training (Enhanced)')
        self.clock = pygame.time.Clock()
        
        # Game mode: 'human' or 'training'
        self.mode = 'human'
        self.switching_mode = False
        
        # Difficulty and algorithm settings
        self.difficulty = DEFAULT_DIFFICULTY
        self.reward_profile = DEFAULT_REWARD_PROFILE
        self.algorithm = 'DQN'  # DQN, PPO, A3C
        
        # Games
        self.human_game = None
        self.ai_game = None
        self.agent = None
        
        # Leaderboard
        self.leaderboard = Leaderboard()
        self.show_leaderboard = False
        
        # Policy visualizer
        self.policy_viz = PolicyVisualizer()
        self.show_policy_viz = True
        
        # Training stats
        self.training_games = 0
        self.training_record = 0
        self.training_running = False
        self.training_thread = None
        
        # UI Elements
        panel_x = GAME_WIDTH + 20
        button_width = 160
        button_height = 35
        y_pos = 20
        
        self.mode_button = Button(panel_x, y_pos, button_width, button_height, 
                                   "Switch to Training", GREEN, BLACK)
        y_pos += 45
        self.reset_button = Button(panel_x, y_pos, button_width, button_height, 
                                    "Reset Game", BLUE, WHITE)
        y_pos += 45
        self.save_button = Button(panel_x, y_pos, button_width, button_height, 
                                   "Save Model", GRAY, WHITE)
        y_pos += 45
        
        # New buttons for enhanced features
        self.difficulty_button = Button(panel_x, y_pos, button_width, button_height,
                                        f"Difficulty: {self.difficulty}", (128, 128, 255), WHITE)
        y_pos += 45
        self.algorithm_button = Button(panel_x, y_pos, button_width, button_height,
                                       f"Algorithm: {self.algorithm}", (255, 128, 0), BLACK)
        y_pos += 45
        self.leaderboard_button = Button(panel_x, y_pos, button_width, button_height,
                                         "Toggle Leaderboard", (255, 215, 0), BLACK)
        y_pos += 45
        self.viz_button = Button(panel_x, y_pos, button_width, button_height,
                                 "Toggle Policy Viz", (200, 100, 200), WHITE)
        
        # High scores
        self.high_score_file = 'high_score.txt'
        self.high_score = self.load_high_score()
        
        self.initialize_game()
        
    def initialize_game(self):
        """Initialize the appropriate game based on mode"""
        if self.mode == 'human':
            self.human_game = SnakeGameHuman(GAME_WIDTH, GAME_HEIGHT, difficulty=self.difficulty)
            self.human_game.high_score = self.high_score
        else:
            self.ai_game = SnakeGameAI(GAME_WIDTH, GAME_HEIGHT, 
                                       difficulty=self.difficulty, 
                                       reward_profile=self.reward_profile)
            
            # Initialize agent based on selected algorithm
            if self.algorithm == 'DQN':
                self.agent = Agent()
            elif self.algorithm == 'PPO':
                self.agent = PPOAgent()
            elif self.algorithm == 'A3C':
                self.agent = A3CAgent()
            
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
        if self.algorithm == 'DQN':
            model_path = './model/model.pth'
        elif self.algorithm == 'PPO':
            model_path = './model/ppo_model.pth'
        else:  # A3C
            model_path = './model/a3c_model.pth'
        
        if os.path.exists(model_path):
            try:
                self.agent.model.load_state_dict(torch.load(model_path))
                print(f"{self.algorithm} model loaded successfully")
            except Exception as e:
                print(f"Error loading model: {e}")
    
    def save_model(self):
        """Save the current model"""
        if self.agent:
            if self.algorithm == 'DQN':
                self.agent.save_model()
            elif self.algorithm == 'PPO':
                self.agent.save_model('ppo_model.pth')
            else:  # A3C
                self.agent.save_model('a3c_model.pth')
            print(f"{self.algorithm} model saved successfully")
    
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
            # Add to leaderboard
            if self.human_game.score > 0:
                self.leaderboard.add_score(self.human_game.score, 'human', self.difficulty)
            self.human_game.reset()
        elif self.mode == 'training' and self.ai_game:
            self.ai_game.update_high_score()
            if self.ai_game.high_score > self.high_score:
                self.high_score = self.ai_game.high_score
                self.save_high_score()
            # Add to leaderboard
            if self.ai_game.score > 0:
                self.leaderboard.add_score(self.ai_game.score, self.algorithm, self.difficulty)
            self.ai_game.reset()
    
    def cycle_difficulty(self):
        """Cycle through difficulty levels"""
        difficulties = ['easy', 'medium', 'hard']
        current_idx = difficulties.index(self.difficulty)
        self.difficulty = difficulties[(current_idx + 1) % len(difficulties)]
        self.difficulty_button.text = f"Difficulty: {self.difficulty}"
        # Reinitialize game with new difficulty
        self.initialize_game()
    
    def cycle_algorithm(self):
        """Cycle through RL algorithms"""
        algorithms = ['DQN', 'PPO', 'A3C']
        current_idx = algorithms.index(self.algorithm)
        self.algorithm = algorithms[(current_idx + 1) % len(algorithms)]
        self.algorithm_button.text = f"Algorithm: {self.algorithm}"
        # Only reinitialize if in training mode
        if self.mode == 'training':
            self.initialize_game()
    
    def toggle_leaderboard(self):
        """Toggle leaderboard display"""
        self.show_leaderboard = not self.show_leaderboard
    
    def toggle_policy_viz(self):
        """Toggle policy visualization"""
        self.show_policy_viz = not self.show_policy_viz
    
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
        self.difficulty_button.draw(self.screen)
        self.algorithm_button.draw(self.screen)
        self.leaderboard_button.draw(self.screen)
        self.viz_button.draw(self.screen)
        if self.mode == 'training':
            self.save_button.draw(self.screen)
        
        # Draw policy visualization if enabled and in training mode
        if self.show_policy_viz and self.mode == 'training' and self.agent and self.ai_game:
            self.policy_viz.draw_q_values(self.screen, self.agent, self.ai_game, 
                                          panel_x + 10, 430)
        
        # Draw leaderboard if enabled
        if self.show_leaderboard:
            self.draw_leaderboard()
    
    def draw_leaderboard(self):
        """Draw leaderboard overlay"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((400, 500))
        overlay.set_alpha(230)
        overlay.fill((30, 30, 30))
        overlay_x = (SCREEN_WIDTH - 400) // 2
        overlay_y = (SCREEN_HEIGHT - 500) // 2
        self.screen.blit(overlay, (overlay_x, overlay_y))
        
        # Draw border
        pygame.draw.rect(self.screen, (255, 255, 0), 
                        (overlay_x, overlay_y, 400, 500), 3)
        
        # Title
        title = FONT_LARGE.render("LEADERBOARD", True, (255, 255, 0))
        title_rect = title.get_rect(center=(overlay_x + 200, overlay_y + 30))
        self.screen.blit(title, title_rect)
        
        # Get top scores
        top_scores = self.leaderboard.get_top_scores(10)
        
        y = overlay_y + 80
        for i, entry in enumerate(top_scores):
            # Rank
            rank_text = f"{i+1}."
            rank_surface = FONT_MEDIUM.render(rank_text, True, WHITE)
            self.screen.blit(rank_surface, (overlay_x + 20, y))
            
            # Score
            score_text = f"{entry['score']}"
            score_surface = FONT_MEDIUM.render(score_text, True, (0, 255, 0))
            self.screen.blit(score_surface, (overlay_x + 60, y))
            
            # Mode/Algorithm and Difficulty
            mode_text = f"{entry.get('mode', 'N/A')} ({entry.get('difficulty', 'N/A')})"
            mode_surface = FONT_SMALL.render(mode_text, True, (200, 200, 200))
            self.screen.blit(mode_surface, (overlay_x + 150, y + 5))
            
            y += 40
        
        # Instructions
        inst_text = "Press 'L' to close"
        inst_surface = FONT_SMALL.render(inst_text, True, (150, 150, 150))
        inst_rect = inst_surface.get_rect(center=(overlay_x + 200, overlay_y + 470))
        self.screen.blit(inst_surface, inst_rect)
    
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
        
        # Algorithm-specific training
        if self.algorithm == 'DQN':
            # Train short memory
            self.agent.train_short_memory(state_old, final_move, reward, state_new, done)
            # Remember
            self.agent.remember(state_old, final_move, reward, state_new, done)
            
            if done:
                # Train long memory (experience replay)
                self.ai_game.reset()
                self.agent.n_games += 1
                self.agent.train_long_memory()
        
        elif self.algorithm == 'PPO':
            # Remember experience
            self.agent.remember(state_old, final_move, reward, done)
            
            if done:
                # Train on episode
                self.agent.train()
                self.ai_game.reset()
                self.agent.n_games += 1
        
        elif self.algorithm == 'A3C':
            # Remember experience
            self.agent.remember(state_old, final_move, reward, done)
            
            if done:
                # Train on episode
                self.agent.train_on_episode()
                self.ai_game.reset()
                self.agent.n_games += 1
        
        if done:
            self.training_games = self.agent.n_games
            
            if score > self.training_record:
                self.training_record = score
                self.save_model()
            
            if score > self.high_score:
                self.high_score = score
                self.save_high_score()
            
            # Add to leaderboard
            if score > 0:
                self.leaderboard.add_score(score, self.algorithm, self.difficulty)
    
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
                    elif self.difficulty_button.is_clicked(pos):
                        self.cycle_difficulty()
                    elif self.algorithm_button.is_clicked(pos):
                        self.cycle_algorithm()
                    elif self.leaderboard_button.is_clicked(pos):
                        self.toggle_leaderboard()
                    elif self.viz_button.is_clicked(pos):
                        self.toggle_policy_viz()
                    elif self.mode == 'training' and self.save_button.is_clicked(pos):
                        self.save_model()
                
                if event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    self.mode_button.update_hover(pos)
                    self.reset_button.update_hover(pos)
                    self.difficulty_button.update_hover(pos)
                    self.algorithm_button.update_hover(pos)
                    self.leaderboard_button.update_hover(pos)
                    self.viz_button.update_hover(pos)
                    if self.mode == 'training':
                        self.save_button.update_hover(pos)
                
                # Keyboard shortcuts
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_l:
                        self.toggle_leaderboard()
                    elif event.key == pygame.K_d:
                        self.cycle_difficulty()
                    elif event.key == pygame.K_a:
                        self.cycle_algorithm()
                    elif event.key == pygame.K_v:
                        self.toggle_policy_viz()
            
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
                    # Add to leaderboard
                    if score > 0:
                        self.leaderboard.add_score(score, 'human', self.difficulty)
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
