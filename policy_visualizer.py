"""
Visualization of learned policy for RL agent
"""
import pygame
import torch
import numpy as np

class PolicyVisualizer:
    """Visualizes the AI's decision-making process"""
    
    def __init__(self):
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 24)
    
    def draw_q_values(self, screen, agent, game, x, y):
        """Draw Q-values for current state"""
        if not agent or not game:
            return
        
        try:
            # Get current state
            state = agent.get_state(game)
            state_tensor = torch.tensor(state, dtype=torch.float)
            
            # Get Q-values
            with torch.no_grad():
                q_values = agent.model(state_tensor)
            
            # Action labels
            actions = ['Straight', 'Right', 'Left']
            colors = [(0, 255, 0), (255, 255, 0), (255, 128, 0)]
            
            # Draw title
            title = self.font_medium.render("Q-Values:", True, (255, 255, 255))
            screen.blit(title, (x, y))
            y += 30
            
            # Draw each Q-value
            max_q_idx = torch.argmax(q_values).item()
            for i, (action, color) in enumerate(zip(actions, colors)):
                q_val = q_values[i].item()
                
                # Highlight the chosen action
                if i == max_q_idx:
                    text_color = (255, 255, 0)  # Yellow for selected
                    prefix = "► "
                else:
                    text_color = (200, 200, 200)
                    prefix = "  "
                
                text = f"{prefix}{action}: {q_val:.2f}"
                surface = self.font_small.render(text, True, text_color)
                screen.blit(surface, (x, y))
                
                # Draw bar
                bar_width = max(0, min(100, int(abs(q_val) * 5)))
                bar_color = color if q_val >= 0 else (255, 0, 0)
                pygame.draw.rect(screen, bar_color, (x + 120, y + 5, bar_width, 12))
                
                y += 25
                
        except Exception as e:
            # Silently fail if visualization can't be drawn
            pass
    
    def draw_state_info(self, screen, game, x, y):
        """Draw current state information"""
        if not game:
            return
        
        try:
            state = game.get_state()
            
            # Draw title
            title = self.font_medium.render("State Info:", True, (255, 255, 255))
            screen.blit(title, (x, y))
            y += 30
            
            # Danger indicators
            dangers = {
                'Danger Straight': state[0],
                'Danger Right': state[1],
                'Danger Left': state[2]
            }
            
            for label, value in dangers.items():
                color = (255, 0, 0) if value else (0, 255, 0)
                text = f"{label}: {'YES' if value else 'NO'}"
                surface = self.font_small.render(text, True, color)
                screen.blit(surface, (x, y))
                y += 22
            
            y += 5
            
            # Food direction
            food_dirs = []
            if state[7]:
                food_dirs.append('Left')
            if state[8]:
                food_dirs.append('Right')
            if state[9]:
                food_dirs.append('Up')
            if state[10]:
                food_dirs.append('Down')
            
            food_text = "Food: " + (', '.join(food_dirs) if food_dirs else 'None')
            surface = self.font_small.render(food_text, True, (0, 255, 255))
            screen.blit(surface, (x, y))
            
        except Exception as e:
            # Silently fail if visualization can't be drawn
            pass
    
    def draw_exploration_info(self, screen, agent, x, y):
        """Draw exploration vs exploitation info"""
        if not agent:
            return
        
        try:
            # Calculate epsilon
            epsilon = max(0, 80 - agent.n_games)
            exploration_rate = min(100, epsilon / 200 * 100)
            
            # Draw title
            title = self.font_medium.render("Exploration:", True, (255, 255, 255))
            screen.blit(title, (x, y))
            y += 30
            
            # Draw rate
            text = f"Rate: {exploration_rate:.1f}%"
            surface = self.font_small.render(text, True, (255, 255, 255))
            screen.blit(surface, (x, y))
            y += 5
            
            # Draw bar
            bar_width = int(exploration_rate)
            pygame.draw.rect(screen, (100, 100, 100), (x, y + 20, 100, 12))
            pygame.draw.rect(screen, (0, 200, 255), (x, y + 20, bar_width, 12))
            
        except Exception as e:
            # Silently fail if visualization can't be drawn
            pass
