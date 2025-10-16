"""
Screenshot generator for Snake Game UI
This creates a visual demonstration of the game interface
"""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from snake_game import SnakeGameAI, BLOCK_SIZE, Direction, Point
import sys

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
GREEN = (0, 255, 0)
DARK_GRAY = (64, 64, 64)

def create_ui_screenshot():
    """Create a screenshot showing the complete UI"""
    
    pygame.init()
    
    # Create full UI screen
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    GAME_WIDTH = 640
    GAME_HEIGHT = 480
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Snake Game - UI Demo')
    
    # Create a game with some progress
    game = SnakeGameAI(GAME_WIDTH, GAME_HEIGHT)
    
    # Add some segments to the snake to make it look active
    game.snake = [
        Point(320, 240),
        Point(300, 240),
        Point(280, 240),
        Point(260, 240),
        Point(240, 240),
    ]
    game.head = game.snake[0]
    game.score = 4
    game.high_score = 15
    
    # Place food
    game.food = Point(400, 300)
    
    # Draw the game
    game._update_ui()
    
    # Draw the complete UI
    screen.fill(BLACK)
    screen.blit(game.display, (0, 0))
    
    # Draw stats panel
    panel_x = GAME_WIDTH
    panel_width = SCREEN_WIDTH - GAME_WIDTH
    
    # Panel background
    pygame.draw.rect(screen, DARK_GRAY, (panel_x, 0, panel_width, SCREEN_HEIGHT))
    
    # Fonts
    FONT_SMALL = pygame.font.Font(None, 24)
    FONT_MEDIUM = pygame.font.Font(None, 32)
    
    # Mode buttons (human mode)
    pygame.draw.rect(screen, GREEN, (panel_x + 20, 20, 140, 40))
    pygame.draw.rect(screen, WHITE, (panel_x + 20, 20, 140, 40), 2)
    text = FONT_SMALL.render("Switch to Training", True, BLACK)
    screen.blit(text, (panel_x + 25, 30))
    
    # Reset button
    pygame.draw.rect(screen, BLUE1, (panel_x + 20, 80, 140, 40))
    pygame.draw.rect(screen, WHITE, (panel_x + 20, 80, 140, 40), 2)
    text = FONT_SMALL.render("Reset Game", True, WHITE)
    screen.blit(text, (panel_x + 35, 90))
    
    # Mode indicator
    text = FONT_MEDIUM.render("Mode: HUMAN", True, WHITE)
    screen.blit(text, (panel_x + 10, 200))
    
    # Stats
    text = FONT_SMALL.render(f"Score: {game.score}", True, WHITE)
    screen.blit(text, (panel_x + 10, 250))
    
    text = FONT_SMALL.render(f"High: {game.high_score}", True, WHITE)
    screen.blit(text, (panel_x + 10, 275))
    
    # Instructions
    text = FONT_SMALL.render("Arrow Keys to Move", True, WHITE)
    screen.blit(text, (panel_x + 10, 400))
    
    # Title at bottom
    text = FONT_SMALL.render("Snake Game with RL", True, GREEN)
    screen.blit(text, (panel_x + 15, 550))
    
    # Update display
    pygame.display.flip()
    
    # Save screenshot
    pygame.image.save(screen, "ui_screenshot.png")
    print("Screenshot saved to ui_screenshot.png")
    
    # Also create a training mode screenshot
    screen.fill(BLACK)
    screen.blit(game.display, (0, 0))
    pygame.draw.rect(screen, DARK_GRAY, (panel_x, 0, panel_width, SCREEN_HEIGHT))
    
    # Training mode button
    pygame.draw.rect(screen, RED, (panel_x + 20, 20, 140, 40))
    pygame.draw.rect(screen, WHITE, (panel_x + 20, 20, 140, 40), 2)
    text = FONT_SMALL.render("Switch to Human", True, WHITE)
    screen.blit(text, (panel_x + 25, 30))
    
    # Reset button
    pygame.draw.rect(screen, BLUE1, (panel_x + 20, 80, 140, 40))
    pygame.draw.rect(screen, WHITE, (panel_x + 20, 80, 140, 40), 2)
    text = FONT_SMALL.render("Reset Game", True, WHITE)
    screen.blit(text, (panel_x + 35, 90))
    
    # Save button
    pygame.draw.rect(screen, (128, 128, 128), (panel_x + 20, 140, 140, 40))
    pygame.draw.rect(screen, WHITE, (panel_x + 20, 140, 140, 40), 2)
    text = FONT_SMALL.render("Save Model", True, WHITE)
    screen.blit(text, (panel_x + 35, 150))
    
    # Mode indicator
    text = FONT_MEDIUM.render("Mode: TRAINING", True, WHITE)
    screen.blit(text, (panel_x + 10, 200))
    
    # Stats
    text = FONT_SMALL.render(f"Score: {game.score}", True, WHITE)
    screen.blit(text, (panel_x + 10, 250))
    
    text = FONT_SMALL.render(f"Record: {game.high_score}", True, WHITE)
    screen.blit(text, (panel_x + 10, 275))
    
    text = FONT_SMALL.render("Games: 42", True, WHITE)
    screen.blit(text, (panel_x + 10, 300))
    
    # Instructions
    text = FONT_SMALL.render("AI Training...", True, GREEN)
    screen.blit(text, (panel_x + 10, 400))
    
    # Title at bottom
    text = FONT_SMALL.render("Snake Game with RL", True, GREEN)
    screen.blit(text, (panel_x + 15, 550))
    
    pygame.display.flip()
    pygame.image.save(screen, "ui_screenshot_training.png")
    print("Training mode screenshot saved to ui_screenshot_training.png")
    
    pygame.quit()


if __name__ == '__main__':
    create_ui_screenshot()
