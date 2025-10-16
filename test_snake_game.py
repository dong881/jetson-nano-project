"""
Unit tests for Snake Game
"""
import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from snake_game import SnakeGameAI, Direction, Point


class TestSnakeGame(unittest.TestCase):
    """Test cases for Snake Game"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Use smaller window for testing
        self.game = SnakeGameAI(w=200, h=200)
    
    def test_initialization(self):
        """Test game initializes correctly"""
        self.assertIsNotNone(self.game)
        self.assertEqual(len(self.game.snake), 3)
        self.assertEqual(self.game.score, 0)
        self.assertIsNotNone(self.game.food)
    
    def test_collision_with_boundary(self):
        """Test collision detection with boundaries"""
        # Test collision with right boundary
        point_right = Point(self.game.w, self.game.h/2)
        self.assertTrue(self.game.is_collision(point_right))
        
        # Test collision with left boundary
        point_left = Point(-20, self.game.h/2)
        self.assertTrue(self.game.is_collision(point_left))
        
        # Test collision with top boundary
        point_top = Point(self.game.w/2, -20)
        self.assertTrue(self.game.is_collision(point_top))
        
        # Test collision with bottom boundary
        point_bottom = Point(self.game.w/2, self.game.h)
        self.assertTrue(self.game.is_collision(point_bottom))
    
    def test_collision_with_self(self):
        """Test collision detection with snake body"""
        # Add a point to the snake that overlaps with existing body
        self.game.snake.insert(0, self.game.snake[1])
        self.assertTrue(self.game.is_collision(self.game.snake[0]))
    
    def test_movement(self):
        """Test snake movement"""
        initial_head = self.game.head
        
        # Move straight
        action = [1, 0, 0]
        self.game.play_step(action)
        
        # Head should have moved
        self.assertNotEqual(initial_head, self.game.head)
    
    def test_score_increment(self):
        """Test score increments when eating food"""
        initial_score = self.game.score
        
        # Place food at next position
        if self.game.direction == Direction.RIGHT:
            self.game.food = Point(self.game.head.x + 20, self.game.head.y)
        elif self.game.direction == Direction.LEFT:
            self.game.food = Point(self.game.head.x - 20, self.game.head.y)
        elif self.game.direction == Direction.UP:
            self.game.food = Point(self.game.head.x, self.game.head.y - 20)
        else:  # DOWN
            self.game.food = Point(self.game.head.x, self.game.head.y + 20)
        
        # Move straight to eat food
        action = [1, 0, 0]
        reward, game_over, score = self.game.play_step(action)
        
        # Score should increase and we should get positive reward
        self.assertEqual(score, initial_score + 1)
        self.assertEqual(reward, 10)
    
    def test_get_state(self):
        """Test state representation"""
        state = self.game.get_state()
        
        # State should be 11-dimensional
        self.assertEqual(len(state), 11)
        
        # All values should be 0 or 1
        for value in state:
            self.assertIn(value, [0, 1])
    
    def test_reset(self):
        """Test game reset"""
        # Play a few steps
        for _ in range(5):
            self.game.play_step([1, 0, 0])
        
        # Reset game
        self.game.reset()
        
        # Game should be back to initial state
        self.assertEqual(len(self.game.snake), 3)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.frame_iteration, 0)


class TestGameAPI(unittest.TestCase):
    """Test API interface for RL agents"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.game = SnakeGameAI(w=200, h=200)
    
    def test_action_interface(self):
        """Test action API accepts correct format"""
        # Test all three actions
        actions = [
            [1, 0, 0],  # Straight
            [0, 1, 0],  # Right
            [0, 0, 1],  # Left
        ]
        
        for action in actions:
            reward, game_over, score = self.game.play_step(action)
            self.assertIsInstance(reward, (int, float))
            self.assertIsInstance(game_over, bool)
            self.assertIsInstance(score, int)
    
    def test_state_api(self):
        """Test state API returns correct format"""
        state = self.game.get_state()
        
        # Should return numpy array
        self.assertEqual(state.shape, (11,))
    
    def test_reset_api(self):
        """Test reset API"""
        # Modify game state
        self.game.score = 10
        self.game.frame_iteration = 100
        
        # Reset
        self.game.reset()
        
        # Should be back to initial state
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.frame_iteration, 0)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
